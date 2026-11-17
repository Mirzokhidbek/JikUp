from dataclasses import dataclass

from app.collectors.normalize import INTRO, split_sections

MAX_CHARS = 800
TITLE_SECTION = "title"
SECTION_LABELS = {INTRO: "회사소개"}


@dataclass(frozen=True)
class Chunk:
    index: int
    section: str
    content: str


def _split_line(line: str, max_chars: int) -> list[str]:
    parts: list[str] = []
    while len(line) > max_chars:
        cut = line.rfind(" ", 0, max_chars)
        cut = cut if cut > 0 else max_chars
        parts.append(line[:cut].strip())
        line = line[cut:].strip()
    return [*parts, line] if line else parts


def split_long(body: str, max_chars: int = MAX_CHARS) -> list[str]:
    pieces: list[str] = []
    current: list[str] = []
    size = 0
    for line in (p for raw in body.splitlines() for p in _split_line(raw, max_chars)):
        if current and size + len(line) > max_chars:
            pieces.append("\n".join(current))
            current, size = [], 0
        current.append(line)
        size += len(line) + 1
    if current:
        pieces.append("\n".join(current))
    return pieces


def build_header(title: str, company: str | None, location: str | None) -> str:
    header = f"[{company}] {title}" if company else title
    return f"{header} ({location})" if location else header


def chunk_job(
    title: str, company: str | None, location: str | None, description_clean: str
) -> list[Chunk]:
    header = build_header(title, company, location)
    chunks = [Chunk(0, TITLE_SECTION, header)]
    for section, body in split_sections(description_clean).items():
        label = SECTION_LABELS.get(section, section)
        for piece in split_long(body):
            chunks.append(Chunk(len(chunks), section, f"{header} | {label}\n{piece}"))
    return chunks
