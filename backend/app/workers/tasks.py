import logging
from dataclasses import asdict
from typing import Any

import httpx

from app.collectors.saramin import collect_saramin as fetch_saramin
from app.collectors.seed import SOURCE as SEED_SOURCE
from app.collectors.seed import load_seed
from app.core.config import get_settings
from app.core.db import SessionLocal
from app.services.ingest import run_collection

log = logging.getLogger(__name__)

HTTP_TIMEOUT_S = 30


async def collect_seed(ctx: dict[str, Any]) -> dict[str, int]:
    async with SessionLocal() as session:
        stats = await run_collection(session, SEED_SOURCE, load_seed())
    return asdict(stats)


async def collect_saramin(ctx: dict[str, Any]) -> dict[str, int]:
    settings = get_settings()
    access_key = settings.saramin_access_key.get_secret_value()
    if not access_key:
        log.info("collect_saramin skipped: SARAMIN_ACCESS_KEY is not set")
        return {}
    async with httpx.AsyncClient(timeout=HTTP_TIMEOUT_S) as client, SessionLocal() as session:
        jobs = fetch_saramin(client, access_key, max_pages=settings.saramin_max_pages)
        stats = await run_collection(session, "saramin", jobs)
    return asdict(stats)
