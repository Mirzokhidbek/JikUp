import asyncio
import logging
import uuid
from collections.abc import AsyncIterator, Callable
from contextlib import AbstractAsyncContextManager
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.agent.loop import AgentRunner
from app.agent.toolbox import DatabaseToolbox
from app.api.search import sse
from app.core.config import get_settings
from app.core.db import SessionLocal, get_session
from app.core.llm import LLM
from app.core.rate_limit import AGENT_RUN, rate_limit
from app.schemas.agent import AgentRunOut, AgentRunRequest
from app.services.agent_runs import COMPLETED, FAILED, create_run, finish_run, get_run
from app.services.job_queries import get_job
from app.services.resumes import get_resume_row

router = APIRouter(prefix="/agent", tags=["agent"])
log = logging.getLogger(__name__)

SessionFactory = Callable[[], AbstractAsyncContextManager[AsyncSession]]
Session = Annotated[AsyncSession, Depends(get_session)]
_background: set[asyncio.Task[None]] = set()


def get_session_factory() -> SessionFactory:
    return SessionLocal


async def _run_agent(
    factory: SessionFactory,
    client: Any,
    body: AgentRunRequest,
    run_id: uuid.UUID,
    queue: asyncio.Queue[tuple[str, Any] | None],
) -> None:
    async def emit(step: dict[str, Any]) -> None:
        await queue.put(("step", step))

    async with factory() as session:
        model = get_settings().gemini_chat_model
        toolbox = DatabaseToolbox(session, client, model, body.resume_id, body.job_id)
        runner = AgentRunner(client, model, toolbox, emit)
        try:
            result = await runner.run(body.language)
            payload = result.model_dump(mode="json", exclude={"steps"})
            await finish_run(session, run_id, COMPLETED, runner.steps, payload)
            await queue.put(("result", payload))
        except Exception as exc:
            log.warning("agent run failed (%s)", type(exc).__name__)
            await session.rollback()
            await finish_run(session, run_id, FAILED, runner.steps, {"error": type(exc).__name__})
            await queue.put(("error", "The analysis could not be completed"))
        finally:
            await queue.put(None)


@router.post("/run", dependencies=[Depends(rate_limit(AGENT_RUN))])
async def run_agent(
    body: AgentRunRequest,
    session: Session,
    client: LLM,
    factory: Annotated[SessionFactory, Depends(get_session_factory)],
) -> StreamingResponse:
    if await get_resume_row(session, body.resume_id) is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Resume not found")
    if await get_job(session, body.job_id) is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Job not found")
    run_id = await create_run(session, body.resume_id, body.job_id)

    queue: asyncio.Queue[tuple[str, Any] | None] = asyncio.Queue()
    task = asyncio.create_task(_run_agent(factory, client, body, run_id, queue))
    _background.add(task)
    task.add_done_callback(_background.discard)

    async def events() -> AsyncIterator[str]:
        yield sse("run", {"run_id": str(run_id)})
        while (item := await queue.get()) is not None:
            yield sse(*item)
        yield sse("done", {})

    return StreamingResponse(
        events(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@router.get("/runs/{run_id}")
async def read_run(run_id: uuid.UUID, session: Session) -> AgentRunOut:
    run = await get_run(session, run_id)
    if run is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Run not found")
    return run
