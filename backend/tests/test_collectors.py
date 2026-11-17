import json
from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import httpx
import pytest
from tenacity import wait_none

from app.collectors.saramin import PAGE_SIZE, SaraminError, collect_saramin, parse_job
from app.collectors.seed import load_seed

ACCESS_KEY = "secret-test-key"

SAMPLE_JOB: dict[str, Any] = {
    "id": "48210001",
    "url": "https://www.saramin.co.kr/zf_user/jobs/relay/view?rec_idx=48210001",
    "active": 1,
    "company": {"detail": {"name": "(주)테스트랩"}},
    "position": {
        "title": "Python 백엔드 개발자",
        "location": {"name": "서울 &gt; 강남구"},
        "job-type": {"name": "정규직"},
        "job-code": {"name": "백엔드/서버개발, Python"},
        "experience-level": {"code": 2, "min": 3, "max": 0, "name": "경력 3년↑"},
    },
    "keyword": "FastAPI, AWS",
    "salary": {"name": "회사내규에 따름"},
    "posting-timestamp": "1794873600",
    "expiration-timestamp": "1797465599",
}


def page(count: int) -> dict[str, Any]:
    jobs = [{**SAMPLE_JOB, "id": str(i)} for i in range(count)]
    return {"jobs": {"count": count, "start": 0, "total": str(count), "job": jobs}}


def client_for(handler: Callable[[httpx.Request], httpx.Response]) -> httpx.AsyncClient:
    return httpx.AsyncClient(transport=httpx.MockTransport(handler))


async def collect(client: httpx.AsyncClient, max_pages: int = 5) -> list[Any]:
    jobs = collect_saramin(client, ACCESS_KEY, max_pages=max_pages, delay_s=0, wait=wait_none())
    return [job async for job in jobs]


def test_parse_job_maps_fields() -> None:
    job = parse_job(SAMPLE_JOB)
    assert job.source == "saramin"
    assert job.source_job_id == "48210001"
    assert job.company == "(주)테스트랩"
    assert job.location == "서울 &gt; 강남구"
    assert job.experience_range == (3, None)
    assert job.description_html == "백엔드/서버개발, Python\nFastAPI, AWS"
    assert job.posted_at == datetime(2026, 11, 17, tzinfo=UTC)
    assert job.is_active


@pytest.mark.parametrize(
    ("level", "expected"),
    [
        ({"code": 0, "name": "경력무관"}, (None, None)),
        ({"code": 1, "name": "신입"}, (0, 0)),
        ({"code": 3, "name": "신입/경력"}, (0, None)),
        ({"code": 2, "min": 1, "max": 3}, (1, 3)),
        ({"name": "협의"}, None),
    ],
)
def test_parse_job_experience_codes(
    level: dict[str, Any], expected: tuple[int | None, int | None] | None
) -> None:
    item = {**SAMPLE_JOB, "position": {**SAMPLE_JOB["position"], "experience-level": level}}
    assert parse_job(item).experience_range == expected


async def test_collect_stops_on_short_page() -> None:
    pages = iter([page(PAGE_SIZE), page(3)])
    starts: list[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        starts.append(request.url.params["start"])
        return httpx.Response(200, json=next(pages))

    async with client_for(handler) as client:
        jobs = await collect(client)
    assert len(jobs) == PAGE_SIZE + 3
    assert starts == ["0", "1"]


async def test_collect_respects_max_pages() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json=page(PAGE_SIZE))

    async with client_for(handler) as client:
        jobs = await collect(client, max_pages=2)
    assert len(jobs) == 2 * PAGE_SIZE


async def test_collect_retries_server_errors() -> None:
    responses = iter([httpx.Response(503), httpx.Response(429), httpx.Response(200, json=page(1))])

    async with client_for(lambda _: next(responses)) as client:
        jobs = await collect(client)
    assert len(jobs) == 1


async def test_client_error_is_not_retried_and_hides_key() -> None:
    calls = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        return httpx.Response(401)

    async with client_for(handler) as client:
        with pytest.raises(SaraminError) as exc_info:
            await collect(client)
    assert calls == 1
    assert exc_info.value.status == 401
    assert ACCESS_KEY not in str(exc_info.value)
    assert exc_info.value.__cause__ is None


async def test_unexpected_body_raises() -> None:
    async with client_for(lambda _: httpx.Response(200, json={"code": 3})) as client:
        with pytest.raises(SaraminError, match="code=3"):
            await collect(client)


def test_load_seed(tmp_path: Path) -> None:
    record = {
        "id": "seed-0001",
        "title": "데이터 엔지니어",
        "company": "가상데이터",
        "location": "경기 성남시",
        "experience": "1~3년",
        "employment_type": "정규직",
        "salary": "회사내규에 따름",
        "description": "[주요업무]\nAirflow 운영",
        "posted_at": "2026-11-10T00:00:00+00:00",
        "deadline_at": "2026-12-10T00:00:00+00:00",
    }
    path = tmp_path / "seed.jsonl"
    path.write_text(json.dumps(record, ensure_ascii=False) + "\n\n", encoding="utf-8")
    jobs = list(load_seed(path))
    assert len(jobs) == 1
    assert jobs[0].source == "seed"
    assert jobs[0].experience_text == "1~3년"
    assert jobs[0].posted_at == datetime(2026, 11, 10, tzinfo=UTC)
