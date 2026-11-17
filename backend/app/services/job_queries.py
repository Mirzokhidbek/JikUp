from collections import defaultdict
from collections.abc import Sequence
from dataclasses import dataclass, field

from sqlalchemy import Select, exists, false, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.collectors.normalize import split_sections
from app.models import Company, Job, JobSkill, Skill
from app.nlp.skills import get_matcher
from app.schemas.job import JobDetail, JobPage, JobSkillOut, JobSummary


@dataclass(frozen=True)
class JobFilters:
    city: str | None = None
    skills: Sequence[str] = field(default_factory=tuple)
    exp_max: int | None = None
    employment_type: str | None = None
    source: str | None = None
    q: str | None = None


def _filtered_ids(filters: JobFilters) -> Select[int]:
    stmt = select(Job.id).where(Job.is_active)
    if filters.city:
        stmt = stmt.where(Job.location_city == filters.city)
    if filters.exp_max is not None:
        stmt = stmt.where(or_(Job.experience_min.is_(None), Job.experience_min <= filters.exp_max))
    if filters.employment_type:
        stmt = stmt.where(Job.employment_type == filters.employment_type)
    if filters.source:
        stmt = stmt.where(Job.source == filters.source)
    if filters.q:
        stmt = stmt.where(Job.title.icontains(filters.q, autoescape=True))
    matcher = get_matcher()
    for term in filters.skills:
        canonical = matcher.extract(term)
        if not canonical:
            return stmt.where(false())
        for name in canonical:
            stmt = stmt.where(
                exists()
                .where(JobSkill.job_id == Job.id, JobSkill.skill_id == Skill.id)
                .where(Skill.canonical_name == name)
            )
    return stmt


async def _skills_by_job(session: AsyncSession, job_ids: list[int]) -> dict[int, list[JobSkillOut]]:
    rows = await session.execute(
        select(JobSkill.job_id, Skill.canonical_name, JobSkill.is_required)
        .join(Skill, Skill.id == JobSkill.skill_id)
        .where(JobSkill.job_id.in_(job_ids))
        .order_by(JobSkill.is_required.desc(), Skill.canonical_name)
    )
    grouped: dict[int, list[JobSkillOut]] = defaultdict(list)
    for job_id, name, required in rows.all():
        grouped[job_id].append(JobSkillOut(name=name, required=required))
    return grouped


def _summary_fields(job: Job, company: str | None, skills: list[JobSkillOut]) -> dict[str, object]:
    return {
        **{name: getattr(job, name) for name in JobSummary.model_fields if hasattr(Job, name)},
        "company": company,
        "skills": skills,
    }


async def list_jobs(session: AsyncSession, filters: JobFilters, limit: int, offset: int) -> JobPage:
    ids_stmt = _filtered_ids(filters)
    total = (
        await session.execute(select(func.count()).select_from(ids_stmt.subquery()))
    ).scalar_one()
    page_ids = list(
        (
            await session.execute(
                ids_stmt.order_by(Job.posted_at.desc().nulls_last(), Job.id.desc())
                .limit(limit)
                .offset(offset)
            )
        ).scalars()
    )
    return JobPage(total=total, items=await load_summaries(session, page_ids))


async def load_summaries(session: AsyncSession, job_ids: list[int]) -> list[JobSummary]:
    if not job_ids:
        return []
    rows = await session.execute(
        select(Job, Company.name)
        .outerjoin(Company, Company.id == Job.company_id)
        .where(Job.id.in_(job_ids))
    )
    by_id = {job.id: (job, company) for job, company in rows.all()}
    skills = await _skills_by_job(session, job_ids)
    return [
        JobSummary.model_validate(_summary_fields(*by_id[i], skills.get(i, [])))
        for i in job_ids
        if i in by_id
    ]


async def get_job(session: AsyncSession, job_id: int) -> JobDetail | None:
    row = (
        await session.execute(
            select(Job, Company.name)
            .outerjoin(Company, Company.id == Job.company_id)
            .where(Job.id == job_id)
        )
    ).one_or_none()
    if row is None:
        return None
    job, company = row
    skills = (await _skills_by_job(session, [job.id])).get(job.id, [])
    return JobDetail.model_validate(
        {**_summary_fields(job, company, skills), "sections": split_sections(job.description_clean)}
    )
