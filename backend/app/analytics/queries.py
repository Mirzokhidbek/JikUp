from collections.abc import Sequence
from datetime import timedelta

from sqlalchemy import ColumnElement, and_, case, distinct, func, literal, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.analytics.schemas import (
    Bucket,
    CooccurrenceReport,
    Overview,
    SkillShare,
    SkillsReport,
    TrendReport,
    TrendSeries,
)
from app.models import Job, JobSkill, Skill

EXPERIENCE_BUCKETS = ("new", "1-3", "4-5", "6+", "any")


def _share(part: int, total: int) -> float:
    return round(100 * part / total, 1) if total else 0.0


def _in_period(days: int | None) -> ColumnElement[bool]:
    active = Job.is_active.is_(True)
    if days is None:
        return active
    return and_(active, Job.posted_at >= func.now() - timedelta(days=days))


async def _count(session: AsyncSession, *where: ColumnElement[bool]) -> int:
    return (await session.execute(select(func.count()).select_from(Job).where(*where))).scalar_one()


async def skill_counts(
    session: AsyncSession, days: int | None, category: str | None, limit: int
) -> list[tuple[str, int]]:
    jobs = func.count(distinct(JobSkill.job_id))
    stmt = (
        select(Skill.canonical_name, jobs)
        .join(JobSkill, JobSkill.skill_id == Skill.id)
        .join(Job, Job.id == JobSkill.job_id)
        .where(_in_period(days))
        .group_by(Skill.canonical_name)
        .order_by(jobs.desc(), Skill.canonical_name)
        .limit(limit)
    )
    if category:
        stmt = stmt.where(Skill.category == category)
    return [(name, n) for name, n in (await session.execute(stmt)).all()]


async def overview(session: AsyncSession) -> Overview:
    total = await _count(session, _in_period(None))
    new = await _count(session, _in_period(7))
    entry = await _count(session, _in_period(None), Job.experience_min == 0)
    demo = await _count(session, _in_period(None), Job.source == "seed")
    top = await skill_counts(session, None, None, 1)
    return Overview(
        active_jobs=total,
        new_this_week=new,
        entry_level_share=_share(entry, total),
        demo_share=_share(demo, total),
        top_skill=SkillShare(name=top[0][0], jobs=top[0][1], share=_share(top[0][1], total))
        if top
        else None,
    )


async def skills_report(
    session: AsyncSession, days: int | None, category: str | None, limit: int
) -> SkillsReport:
    total = await _count(session, _in_period(days))
    counts = await skill_counts(session, days, category, limit)
    categories = (
        await session.execute(select(Skill.category).distinct().order_by(Skill.category))
    ).scalars()
    return SkillsReport(
        total_jobs=total,
        category=category,
        categories=list(categories),
        skills=[SkillShare(name=name, jobs=n, share=_share(n, total)) for name, n in counts],
    )


async def trend_report(session: AsyncSession, skills: Sequence[str], weeks: int) -> TrendReport:
    """Counts for the last `weeks` complete weeks; the current partial week is left out."""
    if not skills:
        skills = [name for name, _ in await skill_counts(session, weeks * 7, None, 5)]
    start = func.date_trunc("week", func.now() - timedelta(weeks=weeks))
    week_list = (
        select(
            func.generate_series(
                start,
                func.date_trunc("week", func.now() - timedelta(weeks=1)),
                timedelta(weeks=1),
            ).label("week")
        )
    ).subquery()
    week = func.date_trunc("week", Job.posted_at)
    totals_stmt = (
        select(week_list.c.week, func.count(Job.id))
        .select_from(week_list)
        .outerjoin(Job, and_(week == week_list.c.week, Job.is_active.is_(True)))
        .group_by(week_list.c.week)
        .order_by(week_list.c.week)
    )
    totals = (await session.execute(totals_stmt)).all()
    per_skill = await session.execute(
        select(Skill.canonical_name, week, func.count(distinct(Job.id)))
        .join(JobSkill, JobSkill.skill_id == Skill.id)
        .join(Job, Job.id == JobSkill.job_id)
        .where(Job.is_active.is_(True), Skill.canonical_name.in_(skills), Job.posted_at >= start)
        .group_by(Skill.canonical_name, week)
    )
    counts = {(name, wk.date()): n for name, wk, n in per_skill.all()}
    week_dates = [wk.date() for wk, _ in totals]
    return TrendReport(
        weeks=week_dates,
        totals=[n for _, n in totals],
        series=[
            TrendSeries(skill=s, counts=[counts.get((s, wk), 0) for wk in week_dates])
            for s in skills
        ],
    )


async def experience_report(session: AsyncSession, days: int | None) -> list[Bucket]:
    bucket = case(
        (Job.experience_min.is_(None), literal("any")),
        (Job.experience_min == 0, literal("new")),
        (Job.experience_min <= 3, literal("1-3")),
        (Job.experience_min <= 5, literal("4-5")),
        else_=literal("6+"),
    )
    rows: dict[str, int] = dict(
        (
            await session.execute(
                select(bucket, func.count()).where(_in_period(days)).group_by(bucket)
            )
        ).all()
    )
    total = sum(rows.values())
    return [
        Bucket(label=b, jobs=rows.get(b, 0), share=_share(rows.get(b, 0), total))
        for b in EXPERIENCE_BUCKETS
    ]


async def city_report(session: AsyncSession, days: int | None, limit: int) -> list[Bucket]:
    city = func.coalesce(Job.location_city, "-")
    rows = (
        await session.execute(
            select(city, func.count())
            .where(_in_period(days))
            .group_by(city)
            .order_by(func.count().desc(), city)
        )
    ).all()
    total = sum(n for _, n in rows)
    top = [Bucket(label=name, jobs=n, share=_share(n, total)) for name, n in rows[:limit]]
    rest = sum(n for _, n in rows[limit:])
    return top + ([Bucket(label="other", jobs=rest, share=_share(rest, total))] if rest else [])


async def cooccurrence_report(session: AsyncSession, skill: str, limit: int) -> CooccurrenceReport:
    base = (
        select(JobSkill.job_id)
        .join(Skill, Skill.id == JobSkill.skill_id)
        .join(Job, Job.id == JobSkill.job_id)
        .where(Skill.canonical_name == skill, Job.is_active.is_(True))
    ).subquery()
    total = (await session.execute(select(func.count()).select_from(base))).scalar_one()
    jobs = func.count(distinct(JobSkill.job_id))
    rows = await session.execute(
        select(Skill.canonical_name, jobs)
        .join(JobSkill, JobSkill.skill_id == Skill.id)
        .where(JobSkill.job_id.in_(select(base.c.job_id)), Skill.canonical_name != skill)
        .group_by(Skill.canonical_name)
        .order_by(jobs.desc(), Skill.canonical_name)
        .limit(limit)
    )
    return CooccurrenceReport(
        skill=skill,
        jobs=total,
        related=[SkillShare(name=name, jobs=n, share=_share(n, total)) for name, n in rows.all()],
    )
