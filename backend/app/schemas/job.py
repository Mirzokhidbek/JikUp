from datetime import datetime

from pydantic import BaseModel


class JobSkillOut(BaseModel):
    name: str
    required: bool


class JobSummary(BaseModel):
    id: int
    source: str
    url: str
    title: str
    company: str | None
    location_city: str | None
    location_district: str | None
    experience_min: int | None
    experience_max: int | None
    employment_type: str | None
    salary_text: str | None
    posted_at: datetime | None
    deadline_at: datetime | None
    skills: list[JobSkillOut]


class JobDetail(JobSummary):
    sections: dict[str, str]


class JobPage(BaseModel):
    total: int
    items: list[JobSummary]
