from datetime import date

from pydantic import BaseModel


class SkillShare(BaseModel):
    name: str
    jobs: int
    share: float


class Overview(BaseModel):
    active_jobs: int
    new_this_week: int
    entry_level_share: float
    demo_share: float
    top_skill: SkillShare | None


class SkillsReport(BaseModel):
    total_jobs: int
    category: str | None
    categories: list[str]
    skills: list[SkillShare]


class TrendSeries(BaseModel):
    skill: str
    counts: list[int]


class TrendReport(BaseModel):
    weeks: list[date]
    totals: list[int]
    series: list[TrendSeries]


class Bucket(BaseModel):
    label: str
    jobs: int
    share: float


class CooccurrenceReport(BaseModel):
    skill: str
    jobs: int
    related: list[SkillShare]
