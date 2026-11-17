from collections.abc import AsyncIterator
from dataclasses import dataclass, replace
from typing import Any

import pytest
from httpx import ASGITransport, AsyncClient
from pydantic import SecretStr
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.admin import get_arq
from app.collectors.base import RawJob
from app.core.config import get_settings
from app.core.db import get_session
from app.main import app
from app.services.ingest import run_collection

BASE = RawJob(
    source="seed",
    source_job_id="0",
    url="",
    title="",
    company="가상랩",
    description_html="",
    location="서울 강남구",
)
JOBS = [
    replace(
        BASE,
        source_job_id="1",
        title="AI 엔지니어",
        description_html="자격요건\nPython, PyTorch",
        experience_text="신입",
    ),
    replace(
        BASE,
        source_job_id="2",
        title="시니어 AI 엔지니어",
        description_html="자격요건\nPython",
        experience_text="경력 5년 이상",
    ),
    replace(
        BASE,
        source_job_id="3",
        title="백엔드 개발자",
        description_html="자격요건\nJava",
        location="부산 해운대구",
        experience_text="경력무관",
    ),
    replace(
        BASE,
        source_job_id="4",
        title="마감된 AI 공고",
        description_html="Python",
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


async def titles(client: AsyncClient, **params: Any) -> list[str]:
    res = await client.get("/jobs", params=params)
    assert res.status_code == 200
    return [item["title"] for item in res.json()["items"]]


async def test_list_returns_only_active_jobs(client: AsyncClient) -> None:
    res = await client.get("/jobs")
    body = res.json()
    assert body["total"] == 3
    assert "마감된 AI 공고" not in [i["title"] for i in body["items"]]


async def test_plan_example_filter(client: AsyncClient) -> None:
    assert await titles(client, city="서울", skill="Python", exp_max=2) == ["AI 엔지니어"]


async def test_skill_alias_and_multiple_skills(client: AsyncClient) -> None:
    assert sorted(await titles(client, skill="파이썬")) == ["AI 엔지니어", "시니어 AI 엔지니어"]
    assert await titles(client, skill=["Python", "pytorch"]) == ["AI 엔지니어"]
    assert await titles(client, skill="NotASkill") == []


async def test_experience_any_is_included(client: AsyncClient) -> None:
    assert sorted(await titles(client, exp_max=0)) == ["AI 엔지니어", "백엔드 개발자"]


async def test_title_search_escapes_wildcards(client: AsyncClient) -> None:
    assert await titles(client, q="백엔드") == ["백엔드 개발자"]
    assert await titles(client, q="%") == []


async def test_pagination(client: AsyncClient) -> None:
    first = (await client.get("/jobs", params={"limit": 2})).json()
    second = (await client.get("/jobs", params={"limit": 2, "offset": 2})).json()
    assert first["total"] == second["total"] == 3
    assert len(first["items"]) == 2 and len(second["items"]) == 1
    assert {i["id"] for i in first["items"]}.isdisjoint(i["id"] for i in second["items"])


async def test_invalid_params_are_rejected(client: AsyncClient) -> None:
    assert (await client.get("/jobs", params={"limit": 500})).status_code == 422
    assert (await client.get("/jobs", params={"exp_max": -1})).status_code == 422


async def test_job_detail_and_404(client: AsyncClient) -> None:
    job_id = (await client.get("/jobs", params={"q": "백엔드"})).json()["items"][0]["id"]
    res = await client.get(f"/jobs/{job_id}")
    body = res.json()
    assert body["company"] == "가상랩"
    assert body["sections"] == {"자격요건": "Java"}
    assert body["skills"] == [{"name": "Java", "required": True}]
    assert (await client.get("/jobs/999999")).status_code == 404


@dataclass
class FakeJob:
    job_id: str


class FakeArq:
    def __init__(self) -> None:
        self.queued: set[str] = set()

    async def enqueue_job(self, name: str, _job_id: str) -> FakeJob | None:
        if _job_id in self.queued:
            return None
        self.queued.add(_job_id)
        return FakeJob(_job_id)


@pytest.fixture
async def admin_client(monkeypatch: pytest.MonkeyPatch) -> AsyncIterator[AsyncClient]:
    monkeypatch.setattr(get_settings(), "admin_token", SecretStr("correct-token"))
    fake = FakeArq()
    app.dependency_overrides[get_arq] = lambda: fake
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c
    app.dependency_overrides.clear()


@pytest.mark.parametrize(
    ("headers", "status"),
    [({}, 401), ({"X-Admin-Token": "wrong"}, 401), ({"X-Admin-Token": "correct-token"}, 202)],
)
async def test_admin_auth(admin_client: AsyncClient, headers: dict[str, str], status: int) -> None:
    res = await admin_client.post("/admin/collect", params={"source": "seed"}, headers=headers)
    assert res.status_code == status


async def test_admin_duplicate_and_bad_source(admin_client: AsyncClient) -> None:
    headers = {"X-Admin-Token": "correct-token"}
    first = await admin_client.post("/admin/collect", params={"source": "seed"}, headers=headers)
    assert first.json() == {"job_id": "collect:seed", "source": "seed"}
    again = await admin_client.post("/admin/collect", params={"source": "seed"}, headers=headers)
    assert again.status_code == 409
    bad = await admin_client.post("/admin/collect", params={"source": "x"}, headers=headers)
    assert bad.status_code == 422


async def test_admin_disabled_without_token(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(get_settings(), "admin_token", SecretStr(""))
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        res = await c.post(
            "/admin/collect", params={"source": "seed"}, headers={"X-Admin-Token": ""}
        )
    assert res.status_code == 503


async def test_skills_counts_active_jobs_only(client: AsyncClient) -> None:
    res = await client.get("/skills")
    counts = {item["name"]: item["jobs"] for item in res.json()}
    assert counts["Python"] == 2
    assert counts["PyTorch"] == 1 and counts["Java"] == 1
    assert res.json()[0]["name"] == "Python"
