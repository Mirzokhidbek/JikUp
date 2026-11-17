from dataclasses import replace

import pytest
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.collectors.base import RawJob
from app.models import CollectionRun, Company, Job, JobSkill, Skill
from app.services.ingest import IngestStats, run_collection
from app.services.skills_sync import sync_skills

JOBS = [
    RawJob(
        source="seed",
        source_job_id="1",
        url="",
        title="백엔드 개발자",
        company="(주)가상랩",
        description_html="[주요업무]<br>API 개발<br>■ 자격요건<br>파이썬 3년<br>우대사항<br>AWS",
        location="서울특별시 강남구",
        experience_text="경력 3년 이상",
    ),
    RawJob(
        source="seed",
        source_job_id="2",
        url="",
        title="프론트엔드 개발자",
        company="가상랩",
        description_html="자격요건\nReact, TypeScript",
        location="경기 성남시",
        experience_text="신입",
    ),
    RawJob(
        source="seed",
        source_job_id="3",
        url="",
        title="데이터 엔지니어",
        company="데이터웍스",
        description_html="Airflow 운영",
        experience_range=(1, 3),
    ),
]


async def count(session: AsyncSession, model: type) -> int:
    return (await session.execute(select(func.count()).select_from(model))).scalar_one()


async def test_first_run_inserts_and_extracts(db_session: AsyncSession) -> None:
    stats = await run_collection(db_session, "seed", JOBS)
    assert stats == IngestStats(fetched=3, inserted=3)
    assert await count(db_session, Company) == 2

    job = (await db_session.execute(select(Job).where(Job.source_job_id == "1"))).scalar_one()
    assert (job.location_city, job.location_district) == ("서울", "강남구")
    assert (job.experience_min, job.experience_max) == (3, None)

    rows = await db_session.execute(
        select(Skill.canonical_name, JobSkill.is_required)
        .join(JobSkill, JobSkill.skill_id == Skill.id)
        .where(JobSkill.job_id == job.id)
    )
    assert dict(rows.all()) == {"Python": True, "AWS": False}

    third = (await db_session.execute(select(Job).where(Job.source_job_id == "3"))).scalar_one()
    assert (third.experience_min, third.experience_max) == (1, 3)


async def test_rerun_without_changes_is_unchanged(db_session: AsyncSession) -> None:
    await run_collection(db_session, "seed", JOBS)
    stats = await run_collection(db_session, "seed", JOBS)
    assert stats == IngestStats(fetched=3, unchanged=3)
    assert await count(db_session, Job) == 3


async def test_changed_posting_is_updated_and_skills_replaced(db_session: AsyncSession) -> None:
    await run_collection(db_session, "seed", JOBS)
    changed = [replace(JOBS[0], description_html="자격요건\nGo, Kubernetes"), *JOBS[1:]]
    stats = await run_collection(db_session, "seed", changed)
    assert stats == IngestStats(fetched=3, updated=1, unchanged=2)

    names = await db_session.execute(
        select(Skill.canonical_name)
        .join(JobSkill, JobSkill.skill_id == Skill.id)
        .join(Job, Job.id == JobSkill.job_id)
        .where(Job.source_job_id == "1")
    )
    assert set(names.scalars()) == {"Go", "Kubernetes"}


async def test_closed_posting_only_flips_active(db_session: AsyncSession) -> None:
    await run_collection(db_session, "seed", JOBS)
    stats = await run_collection(db_session, "seed", [replace(JOBS[0], is_active=False)])
    assert stats == IngestStats(fetched=1, updated=1)
    job = (await db_session.execute(select(Job).where(Job.source_job_id == "1"))).scalar_one()
    assert job.is_active is False


async def test_bad_record_is_counted_and_others_saved(db_session: AsyncSession) -> None:
    broken = replace(JOBS[1], title=None)  # type: ignore[arg-type]
    stats = await run_collection(db_session, "seed", [JOBS[0], broken, JOBS[2]])
    assert stats == IngestStats(fetched=3, inserted=2, errors=1)
    assert await count(db_session, Job) == 2

    run = (await db_session.execute(select(CollectionRun))).scalar_one()
    assert (run.fetched, run.inserted, run.errors) == (3, 2, 1)
    assert run.finished_at is not None


async def test_source_failure_is_recorded_and_raised(db_session: AsyncSession) -> None:
    async def failing() -> object:
        yield JOBS[0]
        raise RuntimeError("source down")

    with pytest.raises(RuntimeError):
        await run_collection(db_session, "seed", failing())  # type: ignore[arg-type]
    run = (await db_session.execute(select(CollectionRun))).scalar_one()
    assert (run.fetched, run.inserted, run.errors) == (1, 1, 1)


async def test_sync_skills_is_idempotent(db_session: AsyncSession) -> None:
    first = await sync_skills(db_session)
    second = await sync_skills(db_session)
    assert first == second
    assert await count(db_session, Skill) == len(first) == 158
