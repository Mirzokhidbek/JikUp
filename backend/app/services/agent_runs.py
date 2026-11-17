import uuid
from typing import Any

from sqlalchemy import insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import AgentRun, Resume
from app.schemas.agent import AgentRunOut

RUNNING = "running"
COMPLETED = "completed"
FAILED = "failed"


async def create_run(session: AsyncSession, resume_id: uuid.UUID, job_id: int) -> uuid.UUID:
    run_id = (
        await session.execute(
            insert(AgentRun)
            .values(resume_id=resume_id, job_id=job_id, status=RUNNING)
            .returning(AgentRun.id)
        )
    ).scalar_one()
    await session.commit()
    return run_id


async def finish_run(
    session: AsyncSession,
    run_id: uuid.UUID,
    status: str,
    steps: list[dict[str, Any]],
    result: dict[str, Any] | None,
) -> None:
    await session.execute(
        update(AgentRun)
        .where(AgentRun.id == run_id)
        .values(status=status, steps=steps, result=result)
    )
    await session.commit()


async def get_run(session: AsyncSession, run_id: uuid.UUID, owner: uuid.UUID) -> AgentRunOut | None:
    run = (
        await session.execute(
            select(AgentRun)
            .join(Resume, Resume.id == AgentRun.resume_id)
            .where(AgentRun.id == run_id, Resume.user_id == owner)
        )
    ).scalar_one_or_none()
    return AgentRunOut.model_validate(run, from_attributes=True) if run else None
