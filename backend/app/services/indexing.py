import logging

from sqlalchemy import exists, func, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Company, Job, JobChunk
from app.nlp.korean import tokenize
from app.rag.chunking import chunk_job
from app.rag.embed import BATCH_SIZE, Embedder

log = logging.getLogger(__name__)


def search_vector(text: str) -> object:
    return func.to_tsvector("simple", " ".join(tokenize(text)))


async def chunk_pending_jobs(session: AsyncSession) -> int:
    has_chunks = exists().where(JobChunk.job_id == Job.id)
    rows = await session.execute(
        select(
            Job.id,
            Job.title,
            Company.name,
            Job.location_city,
            Job.location_district,
            Job.description_clean,
        )
        .outerjoin(Company, Company.id == Job.company_id)
        .where(Job.is_active, ~has_chunks)
        .order_by(Job.id)
    )
    created = 0
    for job_id, title, company, city, district, description in rows.all():
        location = " ".join(part for part in (city, district) if part) or None
        chunks = chunk_job(title, company, location, description)
        await session.execute(
            insert(JobChunk).values(
                [
                    {
                        "job_id": job_id,
                        "chunk_index": chunk.index,
                        "section": chunk.section,
                        "content": chunk.content,
                        "search_tokens": search_vector(chunk.content),
                    }
                    for chunk in chunks
                ]
            )
        )
        created += len(chunks)
    await session.commit()
    return created


async def embed_pending_chunks(session: AsyncSession, embedder: Embedder) -> int:
    embedded = 0
    while True:
        rows = (
            await session.execute(
                select(JobChunk.id, JobChunk.content)
                .where(JobChunk.embedding.is_(None))
                .order_by(JobChunk.id)
                .limit(BATCH_SIZE)
            )
        ).all()
        if not rows:
            return embedded
        vectors = await embedder.embed([content for _, content in rows], "RETRIEVAL_DOCUMENT")
        await session.execute(
            update(JobChunk),
            [
                {"id": chunk_id, "embedding": v}
                for (chunk_id, _), v in zip(rows, vectors, strict=True)
            ],
        )
        await session.commit()
        embedded += len(rows)
        log.info("embedded %d chunks", embedded)
