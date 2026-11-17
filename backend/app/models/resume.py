import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import ForeignKey, text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, CreatedAtMixin

RESUME_TTL = "7 days"


class Resume(CreatedAtMixin, Base):
    __tablename__ = "resumes"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, server_default=text("gen_random_uuid()")
    )
    filename: Mapped[str]
    raw_text: Mapped[str]
    parsed: Mapped[dict[str, Any] | None]
    expires_at: Mapped[datetime] = mapped_column(
        server_default=text(f"now() + interval '{RESUME_TTL}'"), index=True
    )


class AgentRun(CreatedAtMixin, Base):
    __tablename__ = "agent_runs"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, server_default=text("gen_random_uuid()")
    )
    resume_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("resumes.id", ondelete="CASCADE"), index=True
    )
    job_id: Mapped[int | None] = mapped_column(ForeignKey("jobs.id", ondelete="SET NULL"))
    status: Mapped[str]
    steps: Mapped[list[dict[str, Any]]] = mapped_column(server_default=text("'[]'::jsonb"))
    result: Mapped[dict[str, Any] | None]
