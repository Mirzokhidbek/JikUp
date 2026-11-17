from pydantic import BaseModel, Field

from app.rag.query_parser import ParsedQuery
from app.schemas.job import JobSummary


class SearchRequest(BaseModel):
    query: str = Field(min_length=1, max_length=500)
    limit: int = Field(default=10, ge=1, le=20)


class SearchHit(BaseModel):
    job: JobSummary
    score: float
    section: str
    snippet: str
    exact: bool = True


class SearchResponse(BaseModel):
    filters: ParsedQuery
    relaxed: list[str]
    items: list[SearchHit]
