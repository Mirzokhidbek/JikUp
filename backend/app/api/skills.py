from typing import Annotated

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_session
from app.models import Job, JobSkill, Skill

router = APIRouter(tags=["skills"])


class SkillCount(BaseModel):
    name: str
    category: str
    jobs: int


@router.get("/skills")
async def list_skills(session: Annotated[AsyncSession, Depends(get_session)]) -> list[SkillCount]:
    jobs = func.count(JobSkill.job_id)
    rows = await session.execute(
        select(Skill.canonical_name, Skill.category, jobs)
        .join(JobSkill, JobSkill.skill_id == Skill.id)
        .join(Job, Job.id == JobSkill.job_id)
        .where(Job.is_active.is_(True))
        .group_by(Skill.id)
        .order_by(jobs.desc(), Skill.canonical_name)
    )
    return [SkillCount(name=name, category=category, jobs=n) for name, category, n in rows.all()]
