from collections import defaultdict
from collections.abc import Sequence
from dataclasses import dataclass
from functools import lru_cache

from sqlalchemy import ColumnElement, exists, func, or_, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Job, JobChunk, JobSkill, Skill
from app.nlp.korean import tokenize
from app.nlp.skills import load_dictionary
from app.rag.embed import Embedder
from app.rag.query_parser import ParsedQuery

CANDIDATES = 50
RRF_K = 60
EF_SEARCH = 100


@dataclass(frozen=True)
class RetrievedJob:
    job_id: int
    score: float
    chunk_id: int
    section: str
    content: str


@lru_cache(maxsize=1)
def _skill_terms() -> dict[str, tuple[str, ...]]:
    return {entry.name: entry.terms for entry in load_dictionary()}


def job_filters(query: ParsedQuery) -> list[ColumnElement[bool]]:
    filters: list[ColumnElement[bool]] = [Job.is_active.is_(True)]
    if query.city:
        filters.append(Job.location_city == query.city)
    if query.experience_max is not None:
        filters.append(
            or_(Job.experience_min.is_(None), Job.experience_min <= query.experience_max)
        )
    if query.employment_type:
        filters.append(Job.employment_type == query.employment_type)
    if query.skills:
        filters.append(
            exists()
            .where(JobSkill.job_id == Job.id, JobSkill.skill_id == Skill.id)
            .where(Skill.canonical_name.in_(query.skills))
        )
    return filters


def keyword_terms(query: ParsedQuery) -> list[str]:
    terms = set(tokenize(query.semantic_query))
    for skill in query.skills:
        for term in _skill_terms().get(skill, (skill,)):
            terms.update(tokenize(term))
    return sorted(terms)


def rrf_merge(rankings: Sequence[Sequence[int]], k: int = RRF_K) -> dict[int, float]:
    scores: dict[int, float] = defaultdict(float)
    for ranking in rankings:
        for rank, item in enumerate(ranking, start=1):
            scores[item] += 1 / (k + rank)
    return dict(scores)


async def _vector_ranking(
    session: AsyncSession, query: ParsedQuery, embedder: Embedder
) -> list[tuple[int, int]]:
    [vector] = await embedder.embed([query.semantic_query], "RETRIEVAL_QUERY")
    await session.execute(text(f"SET LOCAL hnsw.ef_search = {EF_SEARCH}"))
    await session.execute(text("SET LOCAL hnsw.iterative_scan = relaxed_order"))
    rows = await session.execute(
        select(JobChunk.id, JobChunk.job_id)
        .join(Job, Job.id == JobChunk.job_id)
        .where(*job_filters(query), JobChunk.embedding.is_not(None))
        .order_by(JobChunk.embedding.cosine_distance(vector))
        .limit(CANDIDATES)
    )
    return [(chunk_id, job_id) for chunk_id, job_id in rows.all()]


async def _keyword_ranking(session: AsyncSession, query: ParsedQuery) -> list[tuple[int, int]]:
    terms = keyword_terms(query)
    if not terms:
        return []
    tsquery = func.websearch_to_tsquery("simple", " OR ".join(terms))
    rows = await session.execute(
        select(JobChunk.id, JobChunk.job_id)
        .join(Job, Job.id == JobChunk.job_id)
        .where(*job_filters(query), JobChunk.search_tokens.op("@@")(tsquery))
        .order_by(func.ts_rank_cd(JobChunk.search_tokens, tsquery).desc(), JobChunk.id)
        .limit(CANDIDATES)
    )
    return [(chunk_id, job_id) for chunk_id, job_id in rows.all()]


async def retrieve(
    session: AsyncSession, query: ParsedQuery, embedder: Embedder | None, limit: int = 10
) -> list[RetrievedJob]:
    rankings = [await _keyword_ranking(session, query)]
    if embedder is not None:
        rankings.append(await _vector_ranking(session, query, embedder))

    job_of = {chunk_id: job_id for ranking in rankings for chunk_id, job_id in ranking}
    chunk_scores = rrf_merge([[chunk_id for chunk_id, _ in ranking] for ranking in rankings])
    best: dict[int, tuple[float, int]] = {}
    for chunk_id, score in chunk_scores.items():
        job_id = job_of[chunk_id]
        if job_id not in best or score > best[job_id][0]:
            best[job_id] = (score, chunk_id)
    top = sorted(best.items(), key=lambda item: (-item[1][0], item[0]))[:limit]
    if not top:
        return []

    chunk_ids = [chunk_id for _, (_, chunk_id) in top]
    rows = await session.execute(
        select(JobChunk.id, JobChunk.section, JobChunk.content).where(JobChunk.id.in_(chunk_ids))
    )
    chunks = {chunk_id: (section, content) for chunk_id, section, content in rows.all()}
    return [
        RetrievedJob(job_id, score, chunk_id, *chunks[chunk_id])
        for job_id, (score, chunk_id) in top
    ]
