import json
import logging
from collections.abc import AsyncIterator
from typing import Annotated, Any

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.db import get_session
from app.core.llm import LLM, get_embedder
from app.core.rate_limit import SEARCH, rate_limit
from app.rag.answer import stream_answer
from app.rag.embed import Embedder
from app.rag.search import search
from app.schemas.search import SearchRequest, SearchResponse

router = APIRouter(tags=["search"])
log = logging.getLogger(__name__)

Session = Annotated[AsyncSession, Depends(get_session)]
EmbedderDep = Annotated[Embedder | None, Depends(get_embedder)]


def sse(event: str, data: object) -> str:
    return f"event: {event}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"


async def _run_search(
    session: AsyncSession, client: Any, embedder: Embedder | None, body: SearchRequest
) -> SearchResponse:
    model = get_settings().gemini_parser_model
    return await search(session, client, model, embedder, body.query, body.limit)


@router.post("/search", dependencies=[Depends(rate_limit(SEARCH))])
async def search_jobs(
    body: SearchRequest, session: Session, client: LLM, embedder: EmbedderDep
) -> SearchResponse:
    return await _run_search(session, client, embedder, body)


@router.post("/chat", dependencies=[Depends(rate_limit(SEARCH))])
async def chat(
    body: SearchRequest, session: Session, client: LLM, embedder: EmbedderDep
) -> StreamingResponse:
    result = await _run_search(session, client, embedder, body)
    model = get_settings().gemini_chat_model

    async def events() -> AsyncIterator[str]:
        yield sse("filters", {**result.filters.model_dump(), "relaxed": result.relaxed})
        yield sse("sources", [hit.model_dump(mode="json") for hit in result.items])
        try:
            async for token in stream_answer(client, model, body.query, result):
                yield sse("token", token)
        except Exception as exc:
            log.warning("answer stream failed (%s)", type(exc).__name__)
            yield sse("error", "Answer generation failed")
        yield sse("done", {})

    return StreamingResponse(
        events(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
