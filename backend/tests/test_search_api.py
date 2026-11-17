import json
from collections.abc import AsyncIterator
from types import SimpleNamespace
from typing import Any

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_session
from app.core.llm import get_embedder, get_llm_client
from app.main import app
from app.rag.answer import build_prompt
from app.rag.query_parser import ParsedQuery
from app.schemas.search import SearchResponse
from app.services.indexing import chunk_pending_jobs, embed_pending_chunks
from app.services.ingest import run_collection
from tests.test_retriever import JOBS, TopicEmbedder


class FakeModels:
    def __init__(self, parsed: ParsedQuery, tokens: list[str], fail_stream: bool = False):
        self.parsed = parsed
        self.tokens = tokens
        self.fail_stream = fail_stream
        self.answer_prompts: list[str] = []
        self.answer_configs: list[Any] = []

    async def generate_content(self, *, model: str, contents: str, config: Any) -> Any:
        return SimpleNamespace(parsed=self.parsed)

    async def generate_content_stream(
        self, *, model: str, contents: str, config: Any
    ) -> AsyncIterator[Any]:
        self.answer_prompts.append(contents)
        self.answer_configs.append(config)

        async def chunks() -> AsyncIterator[Any]:
            for token in self.tokens:
                yield SimpleNamespace(text=token)
            if self.fail_stream:
                raise RuntimeError("stream broke")

        return chunks()


@pytest.fixture
async def setup(db_session: AsyncSession) -> AsyncIterator[Any]:
    await run_collection(db_session, "seed", JOBS)
    await chunk_pending_jobs(db_session)
    await embed_pending_chunks(db_session, TopicEmbedder())

    async def session_override() -> AsyncIterator[AsyncSession]:
        yield db_session

    state: dict[str, Any] = {}

    def use(models: FakeModels) -> AsyncClient:
        state["models"] = models
        app.dependency_overrides[get_llm_client] = lambda: SimpleNamespace(
            aio=SimpleNamespace(models=models)
        )
        return AsyncClient(transport=ASGITransport(app=app), base_url="http://test")

    app.dependency_overrides[get_session] = session_override
    app.dependency_overrides[get_embedder] = TopicEmbedder
    yield use
    app.dependency_overrides.clear()


def parse_sse(body: str) -> list[tuple[str, Any]]:
    events = []
    for block in body.strip().split("\n\n"):
        lines = dict(line.split(": ", 1) for line in block.splitlines())
        events.append((lines["event"], json.loads(lines["data"])))
    return events


async def test_search_returns_filters_and_hits(setup: Any) -> None:
    models = FakeModels(ParsedQuery(semantic_query="머신러닝", city="서울", language="uz"), [])
    async with setup(models) as client:
        res = await client.post("/search", json={"query": "Seulda ML ishlari"})
    body = res.json()
    assert res.status_code == 200
    assert body["filters"]["city"] == "서울" and body["relaxed"] == []
    assert body["items"][0]["job"]["title"] == "머신러닝 엔지니어"
    assert all(item["job"]["location_city"] == "서울" for item in body["items"])
    assert "| 자격요건" not in body["items"][0]["snippet"]


async def test_filters_are_relaxed_when_nothing_matches(setup: Any) -> None:
    parsed = ParsedQuery(semantic_query="머신러닝", city="부산", experience_max=0)
    async with setup(FakeModels(parsed, [])) as client:
        body = (await client.post("/search", json={"query": "q"})).json()
    assert body["relaxed"] == ["experience_max"]
    assert body["items"][0]["job"]["title"] == "머신러닝 연구원"


async def test_chat_streams_events_in_order(setup: Any) -> None:
    models = FakeModels(
        ParsedQuery(semantic_query="결제", language="ko"), ["추천 ", "공고 [job:", "4]"]
    )
    async with setup(models) as client:
        res = await client.post("/chat", json={"query": "결제 개발자"})
    assert res.headers["content-type"].startswith("text/event-stream")
    events = parse_sse(res.text)
    assert [name for name, _ in events] == ["filters", "sources", "token", "token", "token", "done"]
    assert "".join(data for name, data in events if name == "token") == "추천 공고 [job:4]"
    assert events[1][1][0]["job"]["title"] == "결제 백엔드 개발자"
    assert "Korean" in models.answer_prompts[0]
    assert models.answer_configs[0].thinking_config.thinking_level == "LOW"


async def test_chat_reports_stream_failure(setup: Any) -> None:
    models = FakeModels(ParsedQuery(semantic_query="결제"), ["부분"], fail_stream=True)
    async with setup(models) as client:
        events = parse_sse((await client.post("/chat", json={"query": "x"})).text)
    assert [name for name, _ in events][-3:] == ["token", "error", "done"]


async def test_invalid_request_is_rejected(setup: Any) -> None:
    async with setup(FakeModels(ParsedQuery(semantic_query="x"), [])) as client:
        assert (await client.post("/search", json={"query": ""})).status_code == 422
        assert (await client.post("/chat", json={"query": "x" * 501})).status_code == 422


async def test_llm_not_configured() -> None:
    app.dependency_overrides[get_llm_client] = lambda: None
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        assert (await client.post("/search", json={"query": "x"})).status_code == 503
    app.dependency_overrides.clear()


def test_prompt_mentions_relaxed_filters_and_language() -> None:
    result = SearchResponse(
        filters=ParsedQuery(semantic_query="x", language="uz"), relaxed=["city"], items=[]
    )
    prompt = build_prompt("savol", result)
    assert "Uzbek" in prompt and "city" in prompt and "(none)" in prompt


async def test_few_skill_matches_are_filled_with_close_matches(setup: Any) -> None:
    parsed = ParsedQuery(semantic_query="결제", city="서울", skills=["Go"])
    async with setup(FakeModels(parsed, [])) as client:
        body = (await client.post("/search", json={"query": "q", "limit": 5})).json()
    assert body["relaxed"] == []
    assert body["items"][0]["job"]["title"] == "결제 백엔드 개발자"
    assert body["items"][0]["exact"] is True
    rest = body["items"][1:]
    assert rest and all(item["exact"] is False for item in rest)
    assert all(item["job"]["location_city"] == "서울" for item in body["items"])
