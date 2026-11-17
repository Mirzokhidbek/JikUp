import uuid
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from types import SimpleNamespace
from typing import Any

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.agent import get_session_factory
from app.core.auth import CurrentUser, current_user
from app.core.db import get_session
from app.core.llm import get_llm_client
from app.main import app
from app.models import Job
from app.resumes.parser import ParsedResume
from app.services.ingest import run_collection
from app.services.resumes import create_resume
from tests.conftest import TEST_USER_ID
from tests.test_agent_loop import LETTER, PREP, call, turn
from tests.test_retriever import JOBS
from tests.test_search_api import parse_sse


class FakeModels:
    def __init__(self, agent_turns: list[Any], fail_writing: bool = False) -> None:
        self.agent_turns = agent_turns
        self.fail_writing = fail_writing

    async def generate_content(self, *, model: str, contents: Any, config: Any) -> Any:
        if config.tools:
            return self.agent_turns.pop(0) if self.agent_turns else turn(text="요약")
        if self.fail_writing:
            return SimpleNamespace(parsed=None)
        schema = config.response_schema
        return SimpleNamespace(parsed=LETTER if schema.__name__ == "CoverLetter" else PREP)


@pytest.fixture
async def ctx(db_session: AsyncSession) -> AsyncIterator[dict[str, Any]]:
    await run_collection(db_session, "seed", JOBS)
    job_id = (await db_session.execute(select(Job.id).limit(1))).scalar_one()
    resume = await create_resume(
        db_session, TEST_USER_ID, "r.pdf", "text", ParsedResume(skills=["Python"])
    )
    state: dict[str, Any] = {"job_id": job_id, "resume_id": str(resume.id)}

    async def session_override() -> AsyncIterator[AsyncSession]:
        yield db_session

    @asynccontextmanager
    async def factory() -> AsyncIterator[AsyncSession]:
        yield db_session

    def use(models: FakeModels) -> AsyncClient:
        app.dependency_overrides[get_llm_client] = lambda: SimpleNamespace(
            aio=SimpleNamespace(models=models)
        )
        return AsyncClient(transport=ASGITransport(app=app), base_url="http://test")

    app.dependency_overrides[get_session] = session_override
    app.dependency_overrides[get_session_factory] = lambda: factory
    state["use"] = use
    yield state
    app.dependency_overrides.clear()


async def test_run_streams_steps_and_saves_result(ctx: dict[str, Any]) -> None:
    models = FakeModels(
        [
            turn(call("get_resume"), call("get_job")),
            turn(call("compute_skill_gap")),
            turn(call("draft_cover_letter")),
            turn(call("generate_interview_questions")),
        ]
    )
    body = {"resume_id": ctx["resume_id"], "job_id": ctx["job_id"], "language": "uz"}
    async with ctx["use"](models) as client:
        events = parse_sse((await client.post("/agent/run", json=body)).text)
        names = [name for name, _ in events]
        assert names[0] == "run" and names[-2:] == ["result", "done"]
        assert [data["tool"] for name, data in events if name == "step"] == [
            "get_resume",
            "get_job",
            "compute_skill_gap",
            "draft_cover_letter",
            "generate_interview_questions",
        ]
        result = events[-2][1]
        assert result["summary"] == "요약" and len(result["interview"]["questions"]) == 10

        run = (await client.get(f"/agent/runs/{events[0][1]['run_id']}")).json()
        assert run["status"] == "completed" and len(run["steps"]) == 5
        assert run["result"]["cover_letter"]["motivation"] == "a"


async def test_failed_run_is_recorded(ctx: dict[str, Any]) -> None:
    body = {"resume_id": ctx["resume_id"], "job_id": ctx["job_id"]}
    async with ctx["use"](FakeModels([], fail_writing=True)) as client:
        events = parse_sse((await client.post("/agent/run", json=body)).text)
        assert [name for name, _ in events][-2:] == ["error", "done"]
        run = (await client.get(f"/agent/runs/{events[0][1]['run_id']}")).json()
        assert run["status"] == "failed" and run["result"] == {"error": "RuntimeError"}


async def test_missing_resume_or_job_is_404(ctx: dict[str, Any]) -> None:
    async with ctx["use"](FakeModels([])) as client:
        unknown = {"resume_id": str(uuid.uuid4()), "job_id": ctx["job_id"]}
        assert (await client.post("/agent/run", json=unknown)).status_code == 404
        no_job = {"resume_id": ctx["resume_id"], "job_id": 999999}
        assert (await client.post("/agent/run", json=no_job)).status_code == 404
        assert (await client.get(f"/agent/runs/{uuid.uuid4()}")).status_code == 404
        bad = {"resume_id": ctx["resume_id"], "job_id": ctx["job_id"], "language": "de"}
        assert (await client.post("/agent/run", json=bad)).status_code == 422


async def test_runs_are_private(ctx: dict[str, Any]) -> None:
    body = {"resume_id": ctx["resume_id"], "job_id": ctx["job_id"]}
    async with ctx["use"](FakeModels([], fail_writing=True)) as client:
        run_id = parse_sse((await client.post("/agent/run", json=body)).text)[0][1]["run_id"]
        app.dependency_overrides[current_user] = lambda: CurrentUser(uuid.uuid4(), "x@example.com")
        assert (await client.get(f"/agent/runs/{run_id}")).status_code == 404
        assert (await client.post("/agent/run", json=body)).status_code == 404
