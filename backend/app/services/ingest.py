import logging
from collections.abc import AsyncIterable, AsyncIterator, Iterable
from dataclasses import dataclass
from typing import Literal

from sqlalchemy import delete, func, select, update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.collectors.base import RawJob
from app.collectors.normalize import (
    clean_html,
    content_hash,
    normalize_company_name,
    parse_experience,
    parse_location,
    split_sections,
)
from app.models import CollectionRun, Company, Job, JobChunk, JobSkill
from app.nlp.skills import SkillMatcher, extract_job_skills, get_matcher
from app.services.skills_sync import sync_skills

log = logging.getLogger(__name__)

COMMIT_EVERY = 100
Outcome = Literal["inserted", "updated", "unchanged"]
Jobs = Iterable[RawJob] | AsyncIterable[RawJob]


@dataclass
class IngestStats:
    fetched: int = 0
    inserted: int = 0
    updated: int = 0
    unchanged: int = 0
    errors: int = 0


class Ingestor:
    def __init__(self, session: AsyncSession, matcher: SkillMatcher, skill_ids: dict[str, int]):
        self._session = session
        self._matcher = matcher
        self._skill_ids = skill_ids

    async def _company_id(self, name: str) -> int | None:
        key = normalize_company_name(name)
        if not key:
            return None
        stmt = (
            insert(Company)
            .values(name=name.strip(), name_normalized=key)
            .on_conflict_do_update(
                index_elements=[Company.name_normalized], set_={"name": Company.name}
            )
            .returning(Company.id)
        )
        return (await self._session.execute(stmt)).scalar_one()

    async def ingest(self, raw: RawJob) -> Outcome:
        description = clean_html(raw.description_html)
        digest = content_hash(raw.title, raw.company, description)
        existing = (
            await self._session.execute(
                select(Job.id, Job.content_hash, Job.is_active).where(
                    Job.source == raw.source, Job.source_job_id == raw.source_job_id
                )
            )
        ).one_or_none()

        if existing and existing.content_hash == digest:
            if existing.is_active == raw.is_active:
                return "unchanged"
            await self._session.execute(
                update(Job).where(Job.id == existing.id).values(is_active=raw.is_active)
            )
            return "updated"

        city, district = parse_location(raw.location)
        exp_min, exp_max = raw.experience_range or parse_experience(raw.experience_text)
        values = {
            "url": raw.url,
            "title": raw.title.strip(),
            "company_id": await self._company_id(raw.company),
            "location_city": city,
            "location_district": district,
            "experience_min": exp_min,
            "experience_max": exp_max,
            "employment_type": raw.employment_type,
            "salary_text": raw.salary_text,
            "description_raw": raw.description_html,
            "description_clean": description,
            "posted_at": raw.posted_at,
            "deadline_at": raw.deadline_at,
            "content_hash": digest,
            "is_active": raw.is_active,
        }
        stmt = (
            insert(Job)
            .values(source=raw.source, source_job_id=raw.source_job_id, **values)
            .on_conflict_do_update(
                constraint="uq_jobs_source_job", set_={**values, "updated_at": func.now()}
            )
            .returning(Job.id)
        )
        job_id = (await self._session.execute(stmt)).scalar_one()

        if existing:
            await self._session.execute(delete(JobSkill).where(JobSkill.job_id == job_id))
            await self._session.execute(delete(JobChunk).where(JobChunk.job_id == job_id))

        sections = {**split_sections(description), "title": raw.title}
        skills = extract_job_skills(self._matcher, sections)
        if skills:
            await self._session.execute(
                insert(JobSkill).values(
                    [
                        {"job_id": job_id, "skill_id": self._skill_ids[name], "is_required": req}
                        for name, req in skills.items()
                    ]
                )
            )
        return "updated" if existing else "inserted"


async def _iterate(jobs: Jobs) -> AsyncIterator[RawJob]:
    if isinstance(jobs, AsyncIterable):
        async for job in jobs:
            yield job
    else:
        for job in jobs:
            yield job


async def run_collection(
    session: AsyncSession, source: str, jobs: Jobs, matcher: SkillMatcher | None = None
) -> IngestStats:
    skill_ids = await sync_skills(session)
    run_id = (
        await session.execute(
            insert(CollectionRun).values(source=source).returning(CollectionRun.id)
        )
    ).scalar_one()
    await session.commit()

    stats = IngestStats()
    ingestor = Ingestor(session, matcher or get_matcher(), skill_ids)
    try:
        async for raw in _iterate(jobs):
            stats.fetched += 1
            try:
                async with session.begin_nested():
                    outcome = await ingestor.ingest(raw)
                setattr(stats, outcome, getattr(stats, outcome) + 1)
            except Exception as exc:
                stats.errors += 1
                log.warning(
                    "ingest failed: %s/%s (%s)", raw.source, raw.source_job_id, type(exc).__name__
                )
            if stats.fetched % COMMIT_EVERY == 0:
                await session.commit()
    except Exception:
        stats.errors += 1
        raise
    finally:
        await session.commit()
        await session.execute(
            update(CollectionRun)
            .where(CollectionRun.id == run_id)
            .values(
                finished_at=func.now(),
                fetched=stats.fetched,
                inserted=stats.inserted,
                updated=stats.updated,
                errors=stats.errors,
            )
        )
        await session.commit()
        log.info("collection %s finished: %s", source, stats)
    return stats
