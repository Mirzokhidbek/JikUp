from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.analytics import queries
from app.analytics.schemas import (
    Bucket,
    CooccurrenceReport,
    Overview,
    SkillsReport,
    TrendReport,
)
from app.core.db import get_session
from app.nlp.skills import get_matcher

CACHE_SECONDS = 300

router = APIRouter(prefix="/analytics", tags=["analytics"])
Session = Annotated[AsyncSession, Depends(get_session)]
Days = Annotated[int | None, Query(ge=7, le=365)]


def cached(response: Response) -> None:
    # private: these routes need a session, so shared caches must not reuse the response.
    response.headers["Cache-Control"] = f"private, max-age={CACHE_SECONDS}"


Cached = Depends(cached)


def canonical(skill: str) -> str:
    found = get_matcher().extract(skill)
    if len(found) != 1:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT, f"Unknown skill: {skill}")
    return found.pop()


@router.get("/overview", dependencies=[Cached])
async def get_overview(session: Session) -> Overview:
    return await queries.overview(session)


@router.get("/skills", dependencies=[Cached])
async def get_skills(
    session: Session,
    days: Days = None,
    category: Annotated[str | None, Query(max_length=30)] = None,
    limit: Annotated[int, Query(ge=1, le=50)] = 15,
) -> SkillsReport:
    return await queries.skills_report(session, days, category, limit)


@router.get("/trends", dependencies=[Cached])
async def get_trends(
    session: Session,
    skills: Annotated[str | None, Query(max_length=200)] = None,
    weeks: Annotated[int, Query(ge=2, le=52)] = 12,
) -> TrendReport:
    names = [canonical(s) for s in (skills or "").split(",") if s.strip()][:5]
    return await queries.trend_report(session, names, weeks)


@router.get("/experience", dependencies=[Cached])
async def get_experience(session: Session, days: Days = None) -> list[Bucket]:
    return await queries.experience_report(session, days)


@router.get("/cities", dependencies=[Cached])
async def get_cities(
    session: Session, days: Days = None, limit: Annotated[int, Query(ge=1, le=17)] = 8
) -> list[Bucket]:
    return await queries.city_report(session, days, limit)


@router.get("/cooccurrence", dependencies=[Cached])
async def get_cooccurrence(
    session: Session,
    skill: Annotated[str, Query(min_length=1, max_length=50)],
    limit: Annotated[int, Query(ge=1, le=30)] = 10,
) -> CooccurrenceReport:
    return await queries.cooccurrence_report(session, canonical(skill), limit)
