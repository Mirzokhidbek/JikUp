import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel

from app.agent.skill_gap import SkillGap
from app.agent.writing import CoverLetter, InterviewPrep


class AgentRunRequest(BaseModel):
    resume_id: uuid.UUID
    job_id: int
    language: Literal["ko", "en", "uz", "ru"] = "en"


class AgentStep(BaseModel):
    step: int
    tool: str
    ok: bool
    fallback: bool
    summary: str
    ms: int


class AgentResultData(BaseModel):
    gap: SkillGap
    cover_letter: CoverLetter
    interview: InterviewPrep
    summary: str


class AgentErrorData(BaseModel):
    error: str


class AgentRunOut(BaseModel):
    id: uuid.UUID
    resume_id: uuid.UUID
    job_id: int | None
    status: str
    steps: list[AgentStep]
    result: AgentResultData | AgentErrorData | None
    created_at: datetime
