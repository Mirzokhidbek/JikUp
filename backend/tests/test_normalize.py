import pytest

from app.collectors.normalize import (
    clean_html,
    content_hash,
    normalize_company_name,
    parse_experience,
    parse_location,
    split_sections,
)


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("<p>Python 개발</p><br/>FastAPI", "Python 개발\nFastAPI"),
        ("<ul><li>API 설계</li><li>운영</li></ul>", "API 설계\n운영"),
        ("서울 &gt; 강남구 &amp; 판교", "서울 > 강남구 & 판교"),
        ("🚀 채용  중   입니다 ✨", "채용 중 입니다"),
        ("경력 3 < 5 이고 7 > 2", "경력 3 < 5 이고 7 > 2"),
        ("&lt;b&gt;굵게&lt;/b&gt;", "굵게"),
        ("", ""),
        (None, ""),
    ],
)
def test_clean_html(raw: str | None, expected: str) -> None:
    assert clean_html(raw) == expected


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("신입", (0, 0)),
        ("경력 3년 이상", (3, None)),
        ("3년↑", (3, None)),
        ("1~3년", (1, 3)),
        ("경력 1-3년", (1, 3)),
        ("경력 2～5년", (2, 5)),
        ("신입·경력", (0, None)),
        ("신입 및 경력 3년 이상", (0, None)),
        ("10년 이하", (0, 10)),
        ("3년 미만", (0, 2)),
        ("경력무관", (None, None)),
        ("경력 무관", (None, None)),
        ("경력", (1, None)),
        ("경력 5년", (5, None)),
        ("", (None, None)),
        ("협의", (None, None)),
    ],
)
def test_parse_experience(raw: str, expected: tuple[int | None, int | None]) -> None:
    assert parse_experience(raw) == expected


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("서울 강남구", ("서울", "강남구")),
        ("서울 &gt; 강남구", ("서울", "강남구")),
        ("서울특별시 강남구", ("서울", "강남구")),
        ("경기도 성남시 분당구", ("경기", "성남시")),
        ("부산광역시", ("부산", None)),
        ("서울 강남구, 경기 성남시", ("서울", "강남구")),
        ("전국", ("전국", None)),
        ("", (None, None)),
    ],
)
def test_parse_location(raw: str, expected: tuple[str | None, str | None]) -> None:
    assert parse_location(raw) == expected


def test_split_sections_standard_headings() -> None:
    text = "\n".join(
        ["회사 소개 문장", "[주요업무]", "API 개발", "■ 자격요건", "Python 3년"]
        + ["우대사항", "AWS 경험", "복리후생", "식대"]
    )
    assert split_sections(text) == {
        "intro": "회사 소개 문장",
        "주요업무": "API 개발",
        "자격요건": "Python 3년",
        "우대사항": "AWS 경험",
        "복지": "식대",
    }


def test_split_sections_synonyms_and_inline_heading() -> None:
    text = "담당업무: 모델 서빙\n필수요건 :\nPyTorch\n혜택 및 복지\n재택근무"
    assert split_sections(text) == {
        "주요업무": "모델 서빙",
        "자격요건": "PyTorch",
        "복지": "재택근무",
    }


def test_split_sections_without_headings_is_intro() -> None:
    assert split_sections("그냥 설명만 있습니다") == {"intro": "그냥 설명만 있습니다"}


def test_split_sections_keeps_colon_lines_that_are_not_headings() -> None:
    assert split_sections("근무시간: 10시~19시") == {"intro": "근무시간: 10시~19시"}


@pytest.mark.parametrize("raw", ["(주)카카오", "㈜카카오", "주식회사 카카오", "카카오 ", "KAKAO"])
def test_normalize_company_name(raw: str) -> None:
    assert normalize_company_name(raw) in {"카카오", "kakao"}


def test_content_hash_ignores_company_suffix_and_detects_changes() -> None:
    base = content_hash("백엔드 개발자", "(주)카카오", "설명")
    assert base == content_hash(" 백엔드 개발자 ", "카카오", "설명")
    assert base != content_hash("백엔드 개발자", "카카오", "다른 설명")
    assert len(base) == 64


@pytest.mark.parametrize(
    ("heading", "section"),
    [
        ("■ 필수사항", "자격요건"),
        ("필수 조건", "자격요건"),
        ("[지원요건]", "자격요건"),
        ("우대 요건", "우대사항"),
        ("주요 역할", "주요업무"),
        ("혜택", "복지"),
    ],
)
def test_split_sections_heading_variants(heading: str, section: str) -> None:
    assert split_sections(f"{heading}\n내용") == {section: "내용"}
