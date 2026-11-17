from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_session
from app.schemas.job import JobDetail, JobPage
from app.services.job_queries import JobFilters, get_job, list_jobs

router = APIRouter(prefix="/jobs", tags=["jobs"])

Session = Annotated[AsyncSession, Depends(get_session)]


@router.get("")
async def search_jobs(
    session: Session,
    city: Annotated[str | None, Query(max_length=20)] = None,
    skill: Annotated[list[str], Query(max_length=10)] = [],  # noqa: B006
    exp_max: Annotated[int | None, Query(ge=0, le=50)] = None,
    employment_type: Annotated[str | None, Query(max_length=20)] = None,
    source: Annotated[str | None, Query(max_length=20)] = None,
    q: Annotated[str | None, Query(min_length=1, max_length=100)] = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    offset: Annotated[int, Query(ge=0, le=10_000)] = 0,
) -> JobPage:
    filters = JobFilters(
        city=city,
        skills=tuple(s[:50] for s in skill),
        exp_max=exp_max,
        employment_type=employment_type,
        source=source,
        q=q,
    )
    return await list_jobs(session, filters, limit=limit, offset=offset)


@router.get("/{job_id}")
async def read_job(job_id: int, session: Session) -> JobDetail:
    job = await get_job(session, job_id)
    if job is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Job not found")
    return job
