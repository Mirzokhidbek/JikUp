"""private resume ids and retention

Revision ID: 0003
Revises: 0002
Create Date: 2026-11-17
"""

from collections.abc import Sequence
from typing import Any

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB, UUID

revision: str = "0003"
down_revision: str | None = "0002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

TS = sa.DateTime(timezone=True)
NOW = sa.text("now()")


def _create(id_type: sa.types.TypeEngine[Any], with_expiry: bool) -> None:
    id_default = sa.text("gen_random_uuid()") if with_expiry else None
    resume_columns = [
        sa.Column("id", id_type, server_default=id_default, nullable=False),
        sa.Column("filename", sa.Text, nullable=False),
        sa.Column("raw_text", sa.Text, nullable=False),
        sa.Column("parsed", JSONB),
        sa.Column("created_at", TS, server_default=NOW, nullable=False),
    ]
    if with_expiry:
        resume_columns.append(
            sa.Column(
                "expires_at",
                TS,
                server_default=sa.text("now() + interval '7 days'"),
                nullable=False,
            )
        )
    op.create_table("resumes", *resume_columns, sa.PrimaryKeyConstraint("id", name="pk_resumes"))
    if with_expiry:
        op.create_index("ix_resumes_expires_at", "resumes", ["expires_at"])

    op.create_table(
        "agent_runs",
        sa.Column("id", id_type, server_default=id_default, nullable=False),
        sa.Column("resume_id", id_type, nullable=False),
        sa.Column("job_id", sa.Integer),
        sa.Column("status", sa.Text, nullable=False),
        sa.Column("steps", JSONB, server_default=sa.text("'[]'::jsonb"), nullable=False),
        sa.Column("result", JSONB),
        sa.Column("created_at", TS, server_default=NOW, nullable=False),
        sa.PrimaryKeyConstraint("id", name="pk_agent_runs"),
        sa.ForeignKeyConstraint(
            ["resume_id"],
            ["resumes.id"],
            name="fk_agent_runs_resume_id_resumes",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["job_id"], ["jobs.id"], name="fk_agent_runs_job_id_jobs", ondelete="SET NULL"
        ),
    )
    op.create_index("ix_agent_runs_resume_id", "agent_runs", ["resume_id"])


def upgrade() -> None:
    op.drop_table("agent_runs")
    op.drop_table("resumes")
    _create(UUID(as_uuid=True), with_expiry=True)


def downgrade() -> None:
    op.drop_table("agent_runs")
    op.drop_table("resumes")
    _create(sa.Integer(), with_expiry=False)
