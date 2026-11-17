"""Operational commands. Usage: python -m app.cli seed"""

import argparse
import asyncio

from app.collectors.seed import SOURCE, load_seed
from app.core.config import get_settings
from app.core.db import SessionLocal, engine
from app.core.llm import get_embedder
from app.core.logging import setup_logging
from app.services.indexing import chunk_pending_jobs, embed_pending_chunks
from app.services.ingest import run_collection


async def seed() -> None:
    async with SessionLocal() as session:
        stats = await run_collection(session, SOURCE, load_seed())
        chunked = await chunk_pending_jobs(session)
        embedder = get_embedder()
        embedded = await embed_pending_chunks(session, embedder) if embedder else 0
    await engine.dispose()
    print(f"seed: {stats.inserted} new, {stats.updated} updated, {stats.unchanged} unchanged")
    print(f"index: {chunked} chunks created, {embedded} embedded")
    if embedder is None:
        print("GEMINI_API_KEY is not set: semantic search, chat and copilot stay off.")


def main() -> None:
    parser = argparse.ArgumentParser(prog="python -m app.cli")
    parser.add_argument("command", choices=["seed"])
    parser.parse_args()
    setup_logging(get_settings().log_level)
    asyncio.run(seed())


if __name__ == "__main__":
    main()
