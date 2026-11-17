import pytest

from app.nlp.korean import tokenize
from app.rag.chunking import MAX_CHARS, build_header, chunk_job, split_long

DESCRIPTION = "회사 소개입니다\n주요업무\nAPI 개발\n자격요건\nPython 3년\n우대사항\nAWS 경험"


def test_chunk_job_one_chunk_per_section_with_context() -> None:
    chunks = chunk_job("백엔드 개발자", "가상랩", "서울 강남구", DESCRIPTION)
    assert [c.section for c in chunks] == ["title", "intro", "주요업무", "자격요건", "우대사항"]
    assert [c.index for c in chunks] == [0, 1, 2, 3, 4]
    assert chunks[0].content == "[가상랩] 백엔드 개발자 (서울 강남구)"
    assert chunks[1].content == "[가상랩] 백엔드 개발자 (서울 강남구) | 회사소개\n회사 소개입니다"
    assert chunks[3].content.endswith("| 자격요건\nPython 3년")


def test_chunk_job_without_sections_or_company() -> None:
    chunks = chunk_job("데이터 분석가", None, None, "")
    assert [(c.section, c.content) for c in chunks] == [("title", "데이터 분석가")]


def test_long_section_is_split_on_line_boundaries() -> None:
    lines = [f"- 업무 항목 {i} " + "가" * 90 for i in range(20)]
    pieces = split_long("\n".join(lines))
    assert len(pieces) > 1
    assert all(len(p) <= MAX_CHARS for p in pieces)
    assert "\n".join(pieces).splitlines() == lines


def test_single_huge_line_is_split_at_spaces() -> None:
    line = " ".join(["단어"] * 1000)
    pieces = split_long(line, max_chars=100)
    assert all(len(p) <= 100 for p in pieces)
    assert " ".join(pieces) == line


def test_build_header_variants() -> None:
    assert build_header("제목", "회사", "부산") == "[회사] 제목 (부산)"
    assert build_header("제목", None, None) == "제목"


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("파이썬을 활용한 백엔드 개발", ["파이썬", "활용", "백엔드", "개발"]),
        ("머신러닝 모델 서빙 경험자 우대", ["머신러닝", "모델", "서빙", "경험자", "우대"]),
        ("프론트엔드와 풀스택 개발자를 찾습니다", ["프론트엔드", "풀스택", "개발자"]),
        ("쿠버네티스(k8s) 운영", ["쿠버네티스", "운영", "k8s"]),
        ("Python과 AWS, C++ 및 C#, Node.js", ["python", "aws", "c++", "c#", "node.js"]),
        ("", []),
    ],
)
def test_tokenize(text: str, expected: list[str]) -> None:
    assert tokenize(text) == expected
