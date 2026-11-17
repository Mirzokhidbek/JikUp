import hashlib
import html
import re
import unicodedata

INTRO = "intro"

_BREAK_TAGS = re.compile(r"<\s*(?:br|li|/p|/li|/div|/h[1-6]|/tr)\b[^>]*>", re.IGNORECASE)
_TAGS = re.compile(r"</?[a-zA-Z][^>]*>")
_EMOJI = re.compile("[\U0001f000-\U0001faff\u2600-\u27bf\ufe0f\u200d]")
_SPACES = re.compile("[ \t\u00a0\u3000]+")

_RANGE = re.compile(r"(\d+)\s*[~\-–]\s*(\d+)\s*년")
_MIN = re.compile(r"(\d+)\s*년\s*(?:이상|↑)")
_MAX = re.compile(r"(\d+)\s*년\s*(이하|미만|↓)")
_YEARS = re.compile(r"(\d+)\s*년")

_CITY_ALIASES = {
    "서울특별시": "서울",
    "서울시": "서울",
    "부산광역시": "부산",
    "대구광역시": "대구",
    "인천광역시": "인천",
    "광주광역시": "광주",
    "대전광역시": "대전",
    "울산광역시": "울산",
    "세종특별자치시": "세종",
    "경기도": "경기",
    "강원도": "강원",
    "강원특별자치도": "강원",
    "충청북도": "충북",
    "충청남도": "충남",
    "전라북도": "전북",
    "전북특별자치도": "전북",
    "전라남도": "전남",
    "경상북도": "경북",
    "경상남도": "경남",
    "제주도": "제주",
    "제주특별자치도": "제주",
}

_SECTION_HEADINGS = {
    "주요업무": "주요업무",
    "담당업무": "주요업무",
    "업무내용": "주요업무",
    "주요역할": "주요업무",
    "자격요건": "자격요건",
    "필수요건": "자격요건",
    "필수사항": "자격요건",
    "필수조건": "자격요건",
    "자격조건": "자격요건",
    "지원자격": "자격요건",
    "지원요건": "자격요건",
    "필요역량": "자격요건",
    "우대사항": "우대사항",
    "우대조건": "우대사항",
    "우대요건": "우대사항",
    "우대역량": "우대사항",
    "복지": "복지",
    "혜택및복지": "복지",
    "복리후생": "복지",
    "혜택": "복지",
}
_HEADING_NOISE = re.compile(r"[\s\[\]【】()<>■□●○▶▷◆◇#*:：\-•·]")
_INLINE_HEADING = re.compile(r"^(.{2,12}?)\s*[:：]\s*(.+)$")

_CORP_MARKERS = re.compile(r"\(주\)|㈜|주식회사|\(유\)|유한회사|\(사\)")


def clean_html(text: str | None) -> str:
    if not text:
        return ""
    text = html.unescape(text)
    text = _BREAK_TAGS.sub("\n", text)
    text = _TAGS.sub("", text)
    text = unicodedata.normalize("NFC", text)
    text = _EMOJI.sub("", text)
    lines = (_SPACES.sub(" ", line).strip() for line in text.splitlines())
    return "\n".join(line for line in lines if line)


def parse_experience(text: str | None) -> tuple[int | None, int | None]:
    if not text:
        return None, None
    t = text.replace("～", "~")
    if "무관" in t:
        return None, None
    has_entry = "신입" in t
    if m := _RANGE.search(t):
        return int(m[1]), int(m[2])
    if m := _MIN.search(t):
        return (0 if has_entry else int(m[1])), None
    if m := _MAX.search(t):
        years = int(m[1])
        return 0, max(years - 1, 0) if m[2] == "미만" else years
    has_career = "경력" in t
    if has_entry:
        return (0, None) if has_career else (0, 0)
    if has_career:
        m = _YEARS.search(t)
        return (int(m[1]) if m else 1), None
    return None, None


def parse_location(text: str | None) -> tuple[str | None, str | None]:
    if not text:
        return None, None
    first = re.split(r"[,/\n]", html.unescape(text))[0]
    parts = [p for p in re.split(r"[\s>]+", first) if p]
    if not parts:
        return None, None
    city = _CITY_ALIASES.get(parts[0], parts[0])
    return city, parts[1] if len(parts) > 1 else None


def _heading(line: str) -> str | None:
    return _SECTION_HEADINGS.get(_HEADING_NOISE.sub("", line))


def split_sections(text: str) -> dict[str, str]:
    sections: dict[str, list[str]] = {}
    current = INTRO
    for line in text.splitlines():
        if heading := _heading(line):
            current = heading
            continue
        if (m := _INLINE_HEADING.match(line)) and (heading := _heading(m[1])):
            current = heading
            line = m[2]
        sections.setdefault(current, []).append(line)
    joined = {name: "\n".join(lines).strip() for name, lines in sections.items()}
    return {name: body for name, body in joined.items() if body}


def normalize_company_name(name: str) -> str:
    return re.sub(r"\s+", "", _CORP_MARKERS.sub("", name)).lower()


def content_hash(title: str, company: str, description_clean: str) -> str:
    payload = "\x1f".join((title.strip(), normalize_company_name(company), description_clean))
    return hashlib.sha256(payload.encode()).hexdigest()
