import re
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

import yaml

DICTIONARY_PATH = Path(__file__).resolve().parents[2] / "data" / "skills_dictionary.yaml"
REQUIRED_SECTION = "자격요건"

_HANGUL = re.compile(r"[가-힣]")
_WHITESPACE = re.compile(r"\s+")


@dataclass(frozen=True)
class SkillEntry:
    name: str
    category: str
    aliases: tuple[str, ...] = ()
    case_sensitive: bool = False

    @property
    def terms(self) -> tuple[str, ...]:
        return (self.name, *self.aliases)


def load_dictionary(path: Path = DICTIONARY_PATH) -> list[SkillEntry]:
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    entries = [
        SkillEntry(
            name=item["name"],
            category=category,
            aliases=tuple(item.get("aliases", [])),
            case_sensitive=item.get("case_sensitive", False),
        )
        for category, items in raw.items()
        for item in items
    ]
    owners: dict[str, str] = {}
    for entry in entries:
        for term in entry.terms:
            key = _key(term).lower()
            if key in owners:
                raise ValueError(f"Duplicate skill term {term!r}: {owners[key]} and {entry.name}")
            owners[key] = entry.name
    return entries


def _key(term: str) -> str:
    return _WHITESPACE.sub("", term)


def _pattern(term: str) -> str:
    body = re.escape(term).replace(r"\ ", r"\s*")
    before = r"(?<![가-힣])" if _HANGUL.match(term[0]) else r"(?<![A-Za-z0-9])"
    after = "" if _HANGUL.match(term[-1]) else r"(?![A-Za-z0-9+#])"
    return before + body + after


class SkillMatcher:
    def __init__(self, entries: Iterable[SkillEntry]) -> None:
        self._exact: dict[str, str] = {}
        self._folded: dict[str, str] = {}
        parts: list[tuple[int, str]] = []
        for entry in entries:
            for term in entry.terms:
                pattern = _pattern(term)
                if entry.case_sensitive:
                    self._exact[_key(term)] = entry.name
                else:
                    self._folded[_key(term).lower()] = entry.name
                    pattern = f"(?i:{pattern})"
                parts.append((len(term), pattern))
        parts.sort(key=lambda part: -part[0])
        self._regex = re.compile("|".join(pattern for _, pattern in parts))

    def extract(self, text: str) -> set[str]:
        return {self._resolve(m.group()) for m in self._regex.finditer(text)}

    def _resolve(self, matched: str) -> str:
        key = _key(matched)
        return self._exact.get(key) or self._folded[key.lower()]


def extract_job_skills(matcher: SkillMatcher, sections: Mapping[str, str]) -> dict[str, bool]:
    skills: dict[str, bool] = {}
    for section, body in sections.items():
        required = section == REQUIRED_SECTION
        for name in matcher.extract(body):
            skills[name] = skills.get(name, False) or required
    return skills


@lru_cache
def get_matcher() -> SkillMatcher:
    return SkillMatcher(load_dictionary())
