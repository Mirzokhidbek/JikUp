import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.agent.skill_gap import SkillGap, compute_skill_gap
from app.resumes.parser import ParsedResume
from app.schemas.job import JobDetail
from app.services.job_queries import get_job
from app.services.resumes import get_resume_row


class ContextError(LookupError):
    pass


async def load_job(session: AsyncSession, job_id: int) -> JobDetail:
    job = await get_job(session, job_id)
    if job is None:
        raise ContextError(f"Job {job_id} not found")
    return job


async def load_resume(session: AsyncSession, resume_id: uuid.UUID) -> ParsedResume:
    row = await get_resume_row(session, resume_id)
    if row is None or row.parsed is None:
        raise ContextError("Resume not found")
    return ParsedResume.model_validate(row.parsed)


def skill_gap_for(resume: ParsedResume, job: JobDetail) -> SkillGap:
    return compute_skill_gap(
        resume.skills,
        {skill.name: skill.required for skill in job.skills},
        resume.years_experience,
        job.experience_min,
    )
