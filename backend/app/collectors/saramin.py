import asyncio
from collections.abc import AsyncIterator
from datetime import UTC, datetime
from typing import Any

import httpx
from tenacity import (
    AsyncRetrying,
    retry_if_exception,
    stop_after_attempt,
    wait_exponential,
)
from tenacity.wait import wait_base

from app.collectors.base import RawJob

SOURCE = "saramin"
API_URL = "https://oapi.saramin.co.kr/job-search"
PAGE_SIZE = 110
IT_JOB_MID_CODE = "2"
DEFAULT_WAIT = wait_exponential(multiplier=1, max=30)

_EXPERIENCE_BY_CODE: dict[int, tuple[int | None, int | None]] = {
    0: (None, None),
    1: (0, 0),
    3: (0, None),
}


class SaraminError(Exception):
    def __init__(self, message: str, status: int | None = None) -> None:
        super().__init__(message)
        self.status = status


def _is_retryable(exc: BaseException) -> bool:
    if not isinstance(exc, SaraminError):
        return False
    return exc.status is None or exc.status == 429 or exc.status >= 500


async def _get_page(client: httpx.AsyncClient, params: dict[str, str]) -> dict[str, Any]:
    try:
        response = await client.get(API_URL, params=params)
    except httpx.TransportError as exc:
        raise SaraminError(f"transport error: {type(exc).__name__}") from None
    if response.status_code != 200:
        raise SaraminError(f"HTTP {response.status_code}", status=response.status_code)
    data: dict[str, Any] = response.json()
    if "jobs" not in data:
        raise SaraminError(f"unexpected response: code={data.get('code')}", status=200)
    return data


def _timestamp(value: Any) -> datetime | None:
    if value in (None, ""):
        return None
    return datetime.fromtimestamp(int(value), UTC)


def _experience_range(level: dict[str, Any]) -> tuple[int | None, int | None] | None:
    code = level.get("code")
    if code is None:
        return None
    code = int(code)
    if code in _EXPERIENCE_BY_CODE:
        return _EXPERIENCE_BY_CODE[code]
    low, high = level.get("min"), level.get("max")
    return (int(low) if low else 1), (int(high) if high else None)


def parse_job(item: dict[str, Any]) -> RawJob:
    position = item.get("position", {})
    job_codes = position.get("job-code", {}).get("name", "")
    keywords = item.get("keyword", "")
    return RawJob(
        source=SOURCE,
        source_job_id=str(item["id"]),
        url=item.get("url", ""),
        title=position.get("title", ""),
        company=item.get("company", {}).get("detail", {}).get("name", ""),
        description_html="\n".join(part for part in (job_codes, keywords) if part),
        location=position.get("location", {}).get("name"),
        experience_text=position.get("experience-level", {}).get("name"),
        experience_range=_experience_range(position.get("experience-level", {})),
        employment_type=position.get("job-type", {}).get("name"),
        salary_text=item.get("salary", {}).get("name"),
        posted_at=_timestamp(item.get("posting-timestamp")),
        deadline_at=_timestamp(item.get("expiration-timestamp")),
        is_active=str(item.get("active", 1)) == "1",
    )


async def collect_saramin(
    client: httpx.AsyncClient,
    access_key: str,
    max_pages: int,
    delay_s: float = 1.0,
    wait: wait_base = DEFAULT_WAIT,
) -> AsyncIterator[RawJob]:
    for page in range(max_pages):
        params = {
            "access-key": access_key,
            "job_mid_cd": IT_JOB_MID_CODE,
            "start": str(page),
            "count": str(PAGE_SIZE),
            "sort": "pd",
        }
        retrying = AsyncRetrying(
            retry=retry_if_exception(_is_retryable),
            stop=stop_after_attempt(4),
            wait=wait,
            reraise=True,
        )
        data: dict[str, Any] = await retrying(_get_page, client, params)
        items = data["jobs"].get("job", [])
        for item in items:
            yield parse_job(item)
        if len(items) < PAGE_SIZE:
            return
        await asyncio.sleep(delay_s)
