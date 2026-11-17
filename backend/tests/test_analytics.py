from collections.abc import AsyncIterator
from dataclasses import replace
from datetime import UTC, datetime, timedelta

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.collectors.base import RawJob
from app.core.db import get_session
from app.main import app
from app.services.ingest import run_collection

NOW = datetime.now(UTC)
BASE = RawJob(
    source="seed", source_job_id="0", url="", title="", company="가상랩", description_html=""
)
JOBS = [
    replace(
        BASE,
        source_job_id="1",
        title="AI 엔지니어",
        description_html="자격요건\nPython, PyTorch",
        location="서울 강남구",
        experience_text="신입",
        posted_at=NOW - timedelta(days=1),
    ),
    replace(
        BASE,
        source_job_id="2",
        title="백엔드",
        description_html="자격요건\nPython, Docker",
        location="서울 마포구",
        experience_text="경력 3년 이상",
        posted_at=NOW - timedelta(days=10),
    ),
    replace(
        BASE,
        source="saramin",
        source_job_id="3",
        title="프론트엔드",
        description_html="자격요건\nReact",
        location="부산 해운대구",
        experience_text="경력무관",
        posted_at=NOW - timedelta(days=60),
    ),
    replace(
        BASE,
        source_job_id="4",
        title="마감된 공고",
        description_html="Python",
        location="서울",
        posted_at=NOW - timedelta(days=1),
        is_active=False,
    ),
]


@pytest.fixture
async def client(db_session: AsyncSession) -> AsyncIterator[AsyncClient]:
    await run_collection(db_session, "seed", JOBS)

    async def session_override() -> AsyncIterator[AsyncSession]:
        yield db_session

    app.dependency_overrides[get_session] = session_override
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c
    app.dependency_overrides.clear()


async def test_overview(client: AsyncClient) -> None:
    res = await client.get("/analytics/overview")
    assert res.headers["cache-control"] == "private, max-age=300"
    assert res.json() == {
        "active_jobs": 3,
        "new_this_week": 1,
        "entry_level_share": 33.3,
        "demo_share": 66.7,
        "top_skill": {"name": "Python", "jobs": 2, "share": 66.7},
    }


@pytest.mark.real_auth
async def test_public_stats_need_no_session(client: AsyncClient) -> None:
    assert (await client.get("/analytics/overview")).status_code == 401
    res = await client.get("/public/stats")
    assert res.status_code == 200
    assert res.headers["cache-control"] == "public, max-age=300"
    body = res.json()
    assert {k: body[k] for k in ("active_jobs", "new_this_week", "ai_ml_jobs", "junior_jobs")} == {
        "active_jobs": 3,
        "new_this_week": 1,
        "ai_ml_jobs": 1,
        "junior_jobs": 2,
    }
    assert body["top_skills"][0] == {"name": "Python", "jobs": 2, "share": 66.7}


async def test_skills_period_and_category(client: AsyncClient) -> None:
    body = (await client.get("/analytics/skills")).json()
    assert body["total_jobs"] == 3
    assert body["skills"][0] == {"name": "Python", "jobs": 2, "share": 66.7}
    recent = (await client.get("/analytics/skills", params={"days": 30})).json()
    assert recent["total_jobs"] == 2 and "React" not in [s["name"] for s in recent["skills"]]
    ai = (await client.get("/analytics/skills", params={"category": "AI/ML"})).json()
    assert [s["name"] for s in ai["skills"]] == ["PyTorch"]
    assert "AI/ML" in ai["categories"]


def in_complete_weeks(*ages_days: int, weeks: int = 4) -> int:
    current_week = (NOW - timedelta(days=NOW.weekday())).date()
    first_week = current_week - timedelta(weeks=weeks)
    return sum(first_week <= (NOW - timedelta(days=d)).date() < current_week for d in ages_days)


async def test_trends_cover_complete_weeks_only(client: AsyncClient) -> None:
    body = (
        await client.get("/analytics/trends", params={"skills": "파이썬,react", "weeks": 4})
    ).json()
    current_week = (NOW - timedelta(days=NOW.weekday())).date().isoformat()
    assert len(body["weeks"]) == 4 and current_week not in body["weeks"]
    series = {s["skill"]: s["counts"] for s in body["series"]}
    assert set(series) == {"Python", "React"}
    python_jobs = in_complete_weeks(1, 10)
    assert sum(series["Python"]) == python_jobs and sum(series["React"]) == 0
    assert sum(body["totals"]) == python_jobs


async def test_trends_reject_unknown_skill(client: AsyncClient) -> None:
    assert (await client.get("/analytics/trends", params={"skills": "NoSuch"})).status_code == 422


async def test_experience_and_cities(client: AsyncClient) -> None:
    exp = {b["label"]: b["jobs"] for b in (await client.get("/analytics/experience")).json()}
    assert exp == {"new": 1, "1-3": 1, "4-5": 0, "6+": 0, "any": 1}
    cities = (await client.get("/analytics/cities", params={"limit": 1})).json()
    assert cities == [
        {"label": "서울", "jobs": 2, "share": 66.7},
        {"label": "other", "jobs": 1, "share": 33.3},
    ]


async def test_cooccurrence(client: AsyncClient) -> None:
    body = (await client.get("/analytics/cooccurrence", params={"skill": "python"})).json()
    assert body["skill"] == "Python" and body["jobs"] == 2
    assert {s["name"]: s["share"] for s in body["related"]} == {"Docker": 50.0, "PyTorch": 50.0}
