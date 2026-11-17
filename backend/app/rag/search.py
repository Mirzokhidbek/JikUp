from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.rag.embed import Embedder
from app.rag.query_parser import ParsedQuery, parse_query
from app.rag.retriever import RetrievedJob, retrieve
from app.schemas.search import SearchHit, SearchResponse
from app.services.job_queries import load_summaries

RELAX_ORDER = ("experience_max", "employment_type", "city", "skills")
SNIPPET_CHARS = 300


def _without(query: ParsedQuery, field: str) -> ParsedQuery:
    return query.model_copy(update={field: [] if field == "skills" else None})


async def retrieve_relaxed(
    session: AsyncSession, query: ParsedQuery, embedder: Embedder | None, limit: int
) -> tuple[list[RetrievedJob], list[str], set[int]]:
    """Strict matches first; if there are fewer than `limit`, fill up without the skill filter.

    Returns the results, the filters dropped because nothing matched, and the ids of the
    results that match every remaining filter.
    """
    relaxed: list[str] = []
    current = query
    results = await retrieve(session, current, embedder, limit)
    for field in RELAX_ORDER:
        if results:
            break
        if getattr(current, field) in (None, []):
            continue
        current = _without(current, field)
        relaxed.append(field)
        results = await retrieve(session, current, embedder, limit)
    exact = {r.job_id for r in results}
    if results and len(results) < limit and current.skills:
        extra = await retrieve(session, _without(current, "skills"), embedder, limit)
        results += [r for r in extra if r.job_id not in exact][: limit - len(results)]
    return results, relaxed, exact


def _snippet(content: str) -> str:
    body = content.split("\n", 1)[-1]
    return body[:SNIPPET_CHARS]


async def search(
    session: AsyncSession,
    client: Any,
    parser_model: str,
    embedder: Embedder | None,
    text: str,
    limit: int,
) -> SearchResponse:
    parsed = await parse_query(client, parser_model, text)
    results, relaxed, exact = await retrieve_relaxed(session, parsed, embedder, limit)
    summaries = {s.id: s for s in await load_summaries(session, [r.job_id for r in results])}
    items = [
        SearchHit(
            job=summaries[r.job_id],
            score=r.score,
            section=r.section,
            snippet=_snippet(r.content),
            exact=r.job_id in exact,
        )
        for r in results
        if r.job_id in summaries
    ]
    return SearchResponse(filters=parsed, relaxed=relaxed, items=items)
