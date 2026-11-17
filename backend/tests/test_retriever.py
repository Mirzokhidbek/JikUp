from collections.abc import Sequence
from dataclasses import replace

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.collectors.base import RawJob
from app.models import EMBED_DIM, Job
from app.rag.embed import EmbedTask
from app.rag.query_parser import ParsedQuery
from app.rag.retriever import keyword_terms, retrieve, rrf_merge
from app.services.indexing import chunk_pending_jobs, embed_pending_chunks
from app.services.ingest import run_collection

TOPICS = ("머신러닝", "프론트엔드", "결제")

BASE = RawJob(
    source="seed", source_job_id="0", url="", title="", company="가상랩", description_html=""
)
JOBS = [
    replace(
        BASE,
        source_job_id="ml-seoul",
        title="머신러닝 엔지니어",
        description_html="자격요건\n파이썬을 활용한 머신러닝 모델 개발",
        location="서울 강남구",
        experience_text="신입",
    ),
    replace(
        BASE,
        source_job_id="ml-busan",
        title="머신러닝 연구원",
        description_html="자격요건\nPyTorch 머신러닝 연구 경력",
        location="부산 해운대구",
        experience_text="경력 5년 이상",
    ),
    replace(
        BASE,
        source_job_id="fe-seoul",
        title="프론트엔드 개발자",
        description_html="자격요건\nReact 프론트엔드 개발",
        location="서울 마포구",
        experience_text="경력무관",
    ),
    replace(
        BASE,
        source_job_id="pay-seoul",
        title="결제 백엔드 개발자",
        description_html="자격요건\nGo 기반 결제 시스템\n우대사항\nJava 경험",
        location="서울 강남구",
        experience_text="1~3년",
    ),
]


class TopicEmbedder:
    """Puts each text on the axis of the first topic word it contains."""

    async def embed(self, texts: Sequence[str], task: EmbedTask) -> list[list[float]]:
        vectors = []
        for text in texts:
            axis = next((i for i, topic in enumerate(TOPICS) if topic in text), len(TOPICS))
            vectors.append([1.0 if i == axis else 0.0 for i in range(EMBED_DIM)])
        return vectors


@pytest.fixture
async def indexed(db_session: AsyncSession) -> AsyncSession:
    await run_collection(db_session, "seed", JOBS)
    await chunk_pending_jobs(db_session)
    await embed_pending_chunks(db_session, TopicEmbedder())
    return db_session


async def source_ids(session: AsyncSession, query: ParsedQuery, semantic: bool = True) -> list[str]:
    results = await retrieve(session, query, TopicEmbedder() if semantic else None)
    names = dict((await session.execute(select(Job.id, Job.source_job_id))).all())
    return [names[r.job_id] for r in results]


def test_rrf_merge_rewards_items_in_both_lists() -> None:
    scores = rrf_merge([[1, 2], [2, 3]], k=60)
    assert max(scores, key=scores.__getitem__) == 2
    assert scores[1] == pytest.approx(1 / 61)


def test_keyword_terms_expand_skill_aliases() -> None:
    terms = keyword_terms(ParsedQuery(semantic_query="모델 개발", skills=["Python"]))
    assert {"모델", "개발", "python", "파이썬", "python3"} <= set(terms)


async def test_semantic_query_ranks_topic_first(indexed: AsyncSession) -> None:
    ids = await source_ids(indexed, ParsedQuery(semantic_query="머신러닝"))
    assert set(ids[:2]) == {"ml-seoul", "ml-busan"}
    assert len(ids) == len(set(ids))


async def test_filters_are_applied(indexed: AsyncSession) -> None:
    query = ParsedQuery(semantic_query="머신러닝", city="서울", experience_max=2)
    ids = await source_ids(indexed, query)
    assert ids[0] == "ml-seoul"
    assert "ml-busan" not in ids


async def test_any_listed_skill_is_enough(indexed: AsyncSession) -> None:
    ids = await source_ids(indexed, ParsedQuery(semantic_query="개발자", skills=["Go", "React"]))
    assert set(ids) == {"pay-seoul", "fe-seoul"}


async def test_keyword_only_finds_korean_spelling_of_skill(indexed: AsyncSession) -> None:
    query = ParsedQuery(semantic_query="", skills=["Python"])
    assert await source_ids(indexed, query, semantic=False) == ["ml-seoul"]


async def test_no_match_returns_empty(indexed: AsyncSession) -> None:
    assert await source_ids(indexed, ParsedQuery(semantic_query="머신러닝", city="제주")) == []
