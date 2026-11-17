"""chunk search tokens

Revision ID: 0002
Revises: 0001
Create Date: 2026-11-17
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import TSVECTOR

revision: str = "0002"
down_revision: str | None = "0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.drop_index("ix_job_chunks_content_trgm", table_name="job_chunks")
    op.add_column(
        "job_chunks",
        sa.Column(
            "search_tokens", TSVECTOR, server_default=sa.text("''::tsvector"), nullable=False
        ),
    )
    op.create_index(
        "ix_job_chunks_search_tokens", "job_chunks", ["search_tokens"], postgresql_using="gin"
    )


def downgrade() -> None:
    op.drop_index("ix_job_chunks_search_tokens", table_name="job_chunks")
    op.drop_column("job_chunks", "search_tokens")
    op.create_index(
        "ix_job_chunks_content_trgm",
        "job_chunks",
        ["content"],
        postgresql_using="gin",
        postgresql_ops={"content": "gin_trgm_ops"},
    )
