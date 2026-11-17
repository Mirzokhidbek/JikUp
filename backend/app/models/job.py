from datetime import datetime

from sqlalchemy import ForeignKey, Index, UniqueConstraint, true
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class Job(TimestampMixin, Base):
    __tablename__ = "jobs"
    __table_args__ = (
        UniqueConstraint("source", "source_job_id", name="uq_jobs_source_job"),
        Index("ix_jobs_experience", "experience_min", "experience_max"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    source: Mapped[str]
    source_job_id: Mapped[str]
    url: Mapped[str]
    title: Mapped[str]
    company_id: Mapped[int | None] = mapped_column(
        ForeignKey("companies.id", ondelete="SET NULL"), index=True
    )
    location_city: Mapped[str | None] = mapped_column(index=True)
    location_district: Mapped[str | None]
    experience_min: Mapped[int | None]
    experience_max: Mapped[int | None]
    employment_type: Mapped[str | None]
    salary_text: Mapped[str | None]
    description_raw: Mapped[str]
    description_clean: Mapped[str]
    posted_at: Mapped[datetime | None] = mapped_column(index=True)
    deadline_at: Mapped[datetime | None]
    content_hash: Mapped[str] = mapped_column(index=True)
    is_active: Mapped[bool] = mapped_column(server_default=true(), index=True)
