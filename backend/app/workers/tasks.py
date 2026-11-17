import logging
from dataclasses import asdict
from typing import Any

import httpx
from google import genai

from app.collectors.saramin import collect_saramin as fetch_saramin
from app.collectors.seed import SOURCE as SEED_SOURCE
from app.collectors.seed import load_seed
from app.core.config import get_settings
from app.core.db import SessionLocal
from app.rag.embed import GeminiEmbedder
from app.services.indexing import chunk_pending_jobs, embed_pending_chunks
from app.services.ingest import run_collection

log = logging.getLogger(__name__)

HTTP_TIMEOUT_S = 30
INDEX_JOB_ID = "index_jobs"


async def _queue_indexing(ctx: dict[str, Any]) -> None:
    await ctx["redis"].enqueue_job("index_jobs", _job_id=INDEX_JOB_ID)


async def collect_seed(ctx: dict[str, Any]) -> dict[str, int]:
    async with SessionLocal() as session:
        stats = await run_collection(session, SEED_SOURCE, load_seed())
    await _queue_indexing(ctx)
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
    await _queue_indexing(ctx)
    return asdict(stats)


async def index_jobs(ctx: dict[str, Any]) -> dict[str, int]:
    settings = get_settings()
    async with SessionLocal() as session:
        chunked = await chunk_pending_jobs(session)
        api_key = settings.gemini_api_key.get_secret_value()
        if not api_key:
            log.info("embedding skipped: GEMINI_API_KEY is not set")
            return {"chunked": chunked, "embedded": 0}
        embedder = GeminiEmbedder(genai.Client(api_key=api_key), settings.gemini_embed_model)
        embedded = await embed_pending_chunks(session, embedder)
    log.info("index_jobs finished: chunked=%d embedded=%d", chunked, embedded)
    return {"chunked": chunked, "embedded": embedded}
