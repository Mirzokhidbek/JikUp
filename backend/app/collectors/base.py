from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class RawJob:
    source: str
    source_job_id: str
    url: str
    title: str
    company: str
    description_html: str
    location: str | None = None
    experience_text: str | None = None
    experience_range: tuple[int | None, int | None] | None = None
    employment_type: str | None = None
    salary_text: str | None = None
    posted_at: datetime | None = None
    deadline_at: datetime | None = None
    is_active: bool = True
