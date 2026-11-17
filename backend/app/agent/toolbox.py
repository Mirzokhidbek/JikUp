import uuid
from typing import Any, Protocol

from sqlalchemy.ext.asyncio import AsyncSession

from app.agent.context import load_job, load_resume, skill_gap_for
from app.agent.skill_gap import SkillGap
from app.agent.writing import (
    CoverLetter,
    InterviewPrep,
    draft_cover_letter,
    generate_interview_questions,
    job_text,
)
from app.resumes.parser import ParsedResume
from app.schemas.job import JobDetail


class Toolbox(Protocol):
    gap: SkillGap | None
    cover_letter: CoverLetter | None
    interview: InterviewPrep | None

    async def get_resume(self) -> dict[str, Any]: ...
    async def get_job(self) -> dict[str, Any]: ...
    async def compute_skill_gap(self) -> dict[str, Any]: ...
    async def draft_cover_letter(self, tone: str | None = None) -> dict[str, Any]: ...
    async def generate_interview_questions(self) -> dict[str, Any]: ...


class DatabaseToolbox:
    """Tools bound to one resume and one job, so the model never chooses which data to read."""

    def __init__(
        self,
        session: AsyncSession,
        client: Any,
        model: str,
        resume_id: uuid.UUID,
        job_id: int,
    ) -> None:
        self._session = session
        self._client = client
        self._model = model
        self._resume_id = resume_id
        self._job_id = job_id
        self._resume: ParsedResume | None = None
        self._job: JobDetail | None = None
        self.gap: SkillGap | None = None
        self.cover_letter: CoverLetter | None = None
        self.interview: InterviewPrep | None = None

    async def _load_resume(self) -> ParsedResume:
        if self._resume is None:
            self._resume = await load_resume(self._session, self._resume_id)
        return self._resume

    async def _load_job(self) -> JobDetail:
        if self._job is None:
            self._job = await load_job(self._session, self._job_id)
        return self._job

    async def _ensure_gap(self) -> SkillGap:
        if self.gap is None:
            self.gap = skill_gap_for(await self._load_resume(), await self._load_job())
        return self.gap

    async def get_resume(self) -> dict[str, Any]:
        return (await self._load_resume()).model_dump(exclude={"name"})

    async def get_job(self) -> dict[str, Any]:
        job = await self._load_job()
        skills = {s.name: "required" if s.required else "preferred" for s in job.skills}
        return {"posting": job_text(job), "skills": skills, "experience_min": job.experience_min}

    async def compute_skill_gap(self) -> dict[str, Any]:
        return (await self._ensure_gap()).model_dump()

    async def draft_cover_letter(self, tone: str | None = None) -> dict[str, Any]:
        gap = await self._ensure_gap()
        kwargs = {"tone": tone} if tone else {}
        self.cover_letter = await draft_cover_letter(
            self._client,
            self._model,
            await self._load_resume(),
            await self._load_job(),
            gap,
            **kwargs,
        )
        return {key: len(value) for key, value in self.cover_letter.model_dump().items()}

    async def generate_interview_questions(self) -> dict[str, Any]:
        gap = await self._ensure_gap()
        self.interview = await generate_interview_questions(
            self._client, self._model, await self._load_resume(), await self._load_job(), gap
        )
        return {"questions": [q.question for q in self.interview.questions]}
