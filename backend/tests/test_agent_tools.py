from types import SimpleNamespace
from typing import Any

import pytest

from app.agent.skill_gap import compute_skill_gap
from app.agent.writing import (
    MIN_QUESTIONS,
    CoverLetter,
    InterviewPrep,
    InterviewQuestion,
    WritingError,
    draft_cover_letter,
    generate_interview_questions,
)
from app.resumes.parser import ParsedResume
from app.schemas.job import JobDetail, JobSkillOut

JOB_SKILLS = {"Python": True, "Docker": True, "Kubernetes": True, "AWS": False, "Go": False}


def test_skill_gap_weights_required_twice() -> None:
    gap = compute_skill_gap(["Python", "Docker", "AWS", "React"], JOB_SKILLS, 2.0, 3)
    assert gap.required_matched == ["Docker", "Python"]
    assert gap.required_missing == ["Kubernetes"]
    assert gap.preferred_matched == ["AWS"]
    assert gap.preferred_missing == ["Go"]
    assert gap.match_percent == round(100 * (2 * 2 + 1) / (2 * 3 + 2))
    assert gap.experience_gap == 1.0


def test_skill_gap_edge_cases() -> None:
    empty = compute_skill_gap(["Python"], {}, None, None)
    assert empty.match_percent is None and empty.experience_gap is None
    full = compute_skill_gap(JOB_SKILLS, JOB_SKILLS, 5.5, 3)
    assert full.match_percent == 100 and full.experience_gap == 0.0
    none = compute_skill_gap([], JOB_SKILLS, 0, 0)
    assert none.match_percent == 0 and none.experience_gap == 0.0


RESUME = ParsedResume(name="Aziz Karimov", skills=["Python", "Docker"], years_experience=2)
JOB = JobDetail(
    id=7,
    source="seed",
    url="",
    title="백엔드 개발자",
    company="가상랩",
    location_city="서울",
    location_district=None,
    experience_min=3,
    experience_max=None,
    employment_type="정규직",
    salary_text=None,
    posted_at=None,
    deadline_at=None,
    skills=[JobSkillOut(name="Kubernetes", required=True)],
    sections={"자격요건": "Kubernetes 운영 경험"},
)
GAP = compute_skill_gap(RESUME.skills, {"Kubernetes": True}, 2, 3)


class FakeModels:
    def __init__(self, result: Any) -> None:
        self.result = result
        self.prompts: list[str] = []

    async def generate_content(self, *, model: str, contents: str, config: Any) -> Any:
        self.prompts.append(contents)
        return SimpleNamespace(parsed=self.result)


def client(models: FakeModels) -> Any:
    return SimpleNamespace(aio=SimpleNamespace(models=models))


LETTER = CoverLetter(motivation=" 지원동기 ", competency="역량", projects="경험", aspiration="포부")


async def test_cover_letter_prompt_has_facts_but_not_name() -> None:
    models = FakeModels(LETTER)
    letter = await draft_cover_letter(client(models), "m", RESUME, JOB, GAP)
    assert letter.motivation == "지원동기"
    prompt = models.prompts[0]
    assert "Aziz" not in prompt
    assert "Kubernetes 운영 경험" in prompt and '"required_missing":["Kubernetes"]' in prompt


async def test_cover_letter_rejects_empty_section() -> None:
    models = FakeModels(LETTER.model_copy(update={"projects": " "}))
    with pytest.raises(WritingError, match="empty section"):
        await draft_cover_letter(client(models), "m", RESUME, JOB, GAP)


def questions(n: int) -> InterviewPrep:
    item = InterviewQuestion(category="technical", question="질문", answer_direction="방향")
    return InterviewPrep(questions=[item] * n)


async def test_interview_questions_need_minimum_count() -> None:
    prep = await generate_interview_questions(
        client(FakeModels(questions(MIN_QUESTIONS))), "m", RESUME, JOB, GAP
    )
    assert len(prep.questions) == MIN_QUESTIONS
    with pytest.raises(WritingError, match="Only 3"):
        await generate_interview_questions(client(FakeModels(questions(3))), "m", RESUME, JOB, GAP)


async def test_missing_structured_output_raises() -> None:
    with pytest.raises(WritingError, match="no CoverLetter"):
        await draft_cover_letter(client(FakeModels(None)), "m", RESUME, JOB, GAP)
