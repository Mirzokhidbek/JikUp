from pathlib import Path

import pytest

from app.nlp.skills import (
    SkillEntry,
    SkillMatcher,
    extract_job_skills,
    get_matcher,
    load_dictionary,
)


@pytest.fixture(scope="module")
def matcher() -> SkillMatcher:
    return get_matcher()


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("파이썬을 활용한 개발", {"Python"}),
        ("Python을 사용합니다", {"Python"}),
        ("리액트와 타입스크립트", {"React", "TypeScript"}),
        ("자바스크립트 숙련자", {"JavaScript"}),
        ("자바, 스프링부트", {"Java", "Spring Boot"}),
        ("Spring Boot 기반 MSA", {"Spring Boot", "MSA"}),
        ("C++ 및 C# 경험", {"C++", "C#"}),
        ("Node.js 백엔드", {"Node.js"}),
        ("k8s, 쿠버네티스 운영", {"Kubernetes"}),
        ("pytorch PYTORCH PyTorch", {"PyTorch"}),
        ("Golang 또는 Go 개발", {"Go"}),
        ("we go to the office", set()),
        ("C언어와 R 통계 분석", {"C", "R", "Statistics"}),
        ("RAG 시스템", {"RAG"}),
        ("인터뷰와 코드 리뷰 진행", {"Code Review"}),
        ("", set()),
    ],
)
def test_extract(matcher: SkillMatcher, text: str, expected: set[str]) -> None:
    assert matcher.extract(text) == expected


def test_extract_job_skills_marks_required_and_preferred(matcher: SkillMatcher) -> None:
    sections = {
        "주요업무": "Python 기반 API 개발",
        "자격요건": "Python 3년 이상, Docker 경험",
        "우대사항": "AWS 경험, Docker Compose",
    }
    assert extract_job_skills(matcher, sections) == {
        "Python": True,
        "Docker": True,
        "AWS": False,
    }


def test_real_dictionary_loads() -> None:
    entries = load_dictionary()
    assert len(entries) == len({entry.name for entry in entries})
    assert all(entry.category for entry in entries)


def test_duplicate_alias_is_rejected(tmp_path: Path) -> None:
    path = tmp_path / "dict.yaml"
    path.write_text(
        "A:\n  - {name: Foo, aliases: [shared]}\n  - {name: Bar, aliases: [Shared]}\n",
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="Duplicate skill term"):
        load_dictionary(path)


def test_matcher_accepts_custom_entries() -> None:
    matcher = SkillMatcher([SkillEntry(name="Foo Bar", category="X", aliases=("푸바",))])
    assert matcher.extract("FooBar, foo bar, 푸바를") == {"Foo Bar"}
