import json
from collections.abc import Iterator
from datetime import datetime
from pathlib import Path

from app.collectors.base import RawJob

SOURCE = "seed"
SEED_PATH = Path(__file__).resolve().parents[2] / "data" / "seed_jobs.jsonl"


def _date(value: str | None) -> datetime | None:
    return datetime.fromisoformat(value) if value else None


def load_seed(path: Path = SEED_PATH) -> Iterator[RawJob]:
    with path.open(encoding="utf-8") as lines:
        for line in lines:
            if not line.strip():
                continue
            record = json.loads(line)
            yield RawJob(
                source=SOURCE,
                source_job_id=record["id"],
                url="",
                title=record["title"],
                company=record["company"],
                description_html=record["description"],
                location=record.get("location"),
                experience_text=record.get("experience"),
                employment_type=record.get("employment_type"),
                salary_text=record.get("salary"),
                posted_at=_date(record.get("posted_at")),
                deadline_at=_date(record.get("deadline_at")),
            )
