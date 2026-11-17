import uuid
from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel


class AgentRunRequest(BaseModel):
    resume_id: uuid.UUID
    job_id: int
    language: Literal["ko", "en", "uz", "ru"] = "en"


class AgentRunOut(BaseModel):
    id: uuid.UUID
    resume_id: uuid.UUID
    job_id: int | None
    status: str
    steps: list[dict[str, Any]]
    result: dict[str, Any] | None
    created_at: datetime
