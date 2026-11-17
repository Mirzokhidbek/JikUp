from types import SimpleNamespace
from typing import Any

from app.nlp.skills import get_matcher
from app.rag.query_parser import MAX_QUERY_CHARS, ParsedQuery, parse_query, sanitize


class FakeModels:
    def __init__(self, result: Any = None, error: Exception | None = None) -> None:
        self.result = result
        self.error = error
        self.prompts: list[str] = []

    async def generate_content(self, *, model: str, contents: str, config: Any) -> Any:
        self.prompts.append(contents)
        if self.error:
            raise self.error
        return SimpleNamespace(parsed=self.result)


def client(models: FakeModels) -> Any:
    return SimpleNamespace(aio=SimpleNamespace(models=models))


def test_sanitize_normalizes_and_drops_invalid_values() -> None:
    raw = ParsedQuery(
        semantic_query="  AI 엔지니어 ",
        city="Seoul",
        skills=["파이썬", "pytorch", "MadeUpTech"],
        experience_max=99,
        employment_type="freelance",
        language="de",
    )
    assert sanitize(raw, "original", get_matcher()) == ParsedQuery(
        semantic_query="AI 엔지니어", skills=["PyTorch", "Python"], language="en"
    )


def test_sanitize_keeps_valid_values() -> None:
    raw = ParsedQuery(
        semantic_query="",
        city="서울",
        skills=["Python"],
        experience_max=2,
        employment_type="정규직",
        language="uz",
    )
    result = sanitize(raw, "original query", get_matcher())
    assert result.semantic_query == "original query"
    assert (result.city, result.experience_max, result.employment_type) == ("서울", 2, "정규직")
    assert result.language == "uz"


async def test_parse_query_uses_model_output() -> None:
    models = FakeModels(ParsedQuery(semantic_query="백엔드 개발자", city="부산", skills=["Go"]))
    result = await parse_query(client(models), "m", "Busan Go backend")
    assert (result.semantic_query, result.city, result.skills) == ("백엔드 개발자", "부산", ["Go"])
    assert "Busan Go backend" in models.prompts[0]


async def test_parse_query_falls_back_on_error() -> None:
    models = FakeModels(error=RuntimeError("down"))
    result = await parse_query(client(models), "m", "Python React 개발자")
    assert result == ParsedQuery(semantic_query="Python React 개발자", skills=["Python", "React"])


async def test_parse_query_falls_back_without_structured_output() -> None:
    result = await parse_query(client(FakeModels(result=None)), "m", "Kotlin")
    assert result.skills == ["Kotlin"]


async def test_long_query_is_cut() -> None:
    models = FakeModels(ParsedQuery(semantic_query="x"))
    await parse_query(client(models), "m", "가" * (MAX_QUERY_CHARS + 100))
    assert "가" * MAX_QUERY_CHARS in models.prompts[0]
    assert "가" * (MAX_QUERY_CHARS + 1) not in models.prompts[0]


def test_sanitize_adds_skills_named_in_the_query() -> None:
    raw = ParsedQuery(semantic_query="컴퓨터 비전 엔지니어", skills=["PyTorch"])
    result = sanitize(raw, "Computer vision engineer with PyTorch", get_matcher())
    assert result.skills == ["Computer Vision", "PyTorch"]
