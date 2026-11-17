from collections.abc import Sequence
from dataclasses import replace

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.collectors.base import RawJob
from app.models import EMBED_DIM, JobChunk
from app.rag.embed import EmbedTask
from app.services.indexing import chunk_pending_jobs, embed_pending_chunks
from app.services.ingest import run_collection

JOBS = [
    RawJob(
        source="seed",
        source_job_id="1",
        url="",
        title="백엔드 개발자",
        company="가상랩",
        description_html="주요업무\nAPI 개발\n자격요건\n파이썬을 활용한 개발 경험",
        location="서울 강남구",
    ),
    RawJob(
        source="seed",
        source_job_id="2",
        url="",
        title="데이터 엔지니어",
        company="데이터웍스",
        description_html="자격요건\nAirflow 운영",
    ),
]


class FakeEmbedder:
    def __init__(self) -> None:
        self.texts: list[str] = []

    async def embed(self, texts: Sequence[str], task: EmbedTask) -> list[list[float]]:
        assert task == "RETRIEVAL_DOCUMENT"
        self.texts.extend(texts)
        return [[1.0] + [0.0] * (EMBED_DIM - 1) for _ in texts]


async def chunk_count(session: AsyncSession, *where: object) -> int:
    stmt = select(func.count()).select_from(JobChunk).where(*where)  # type: ignore[arg-type]
    return (await session.execute(stmt)).scalar_one()


async def test_chunks_are_created_once_with_search_tokens(db_session: AsyncSession) -> None:
    await run_collection(db_session, "seed", JOBS)
    assert await chunk_pending_jobs(db_session) == 5
    assert await chunk_pending_jobs(db_session) == 0

    query = func.to_tsquery("simple", "파이썬")
    assert await chunk_count(db_session, JobChunk.search_tokens.op("@@")(query)) == 1
    title = (
        await db_session.execute(select(JobChunk.content).where(JobChunk.section == "title"))
    ).scalars()
    assert set(title) == {"[가상랩] 백엔드 개발자 (서울 강남구)", "[데이터웍스] 데이터 엔지니어"}


async def test_only_pending_chunks_are_embedded(db_session: AsyncSession) -> None:
    await run_collection(db_session, "seed", JOBS)
    await chunk_pending_jobs(db_session)
    fake = FakeEmbedder()
    assert await embed_pending_chunks(db_session, fake) == 5
    assert await embed_pending_chunks(db_session, fake) == 0
    assert len(fake.texts) == 5
    assert await chunk_count(db_session, JobChunk.embedding.is_(None)) == 0


async def test_changed_job_is_rechunked(db_session: AsyncSession) -> None:
    await run_collection(db_session, "seed", JOBS)
    await chunk_pending_jobs(db_session)
    await embed_pending_chunks(db_session, FakeEmbedder())

    changed = replace(JOBS[1], description_html="자격요건\nAirflow 운영\n우대사항\nSpark")
    await run_collection(db_session, "seed", [changed])
    assert await chunk_pending_jobs(db_session) == 3
    fake = FakeEmbedder()
    assert await embed_pending_chunks(db_session, fake) == 3
    assert any("Spark" in text for text in fake.texts)
