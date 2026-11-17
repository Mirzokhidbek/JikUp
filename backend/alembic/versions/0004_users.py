"""users and resume ownership

Revision ID: 0004
Revises: 0003
Create Date: 2026-11-17
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import UUID

revision: str = "0004"
down_revision: str | None = "0003"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column(
            "id", UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), nullable=False
        ),
        sa.Column("email", sa.Text, nullable=False),
        sa.Column("password_hash", sa.Text, nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id", name="pk_users"),
        sa.UniqueConstraint("email", name="uq_users_email"),
    )
    # Existing anonymous resumes keep user_id NULL: no owner matches them and the purge
    # job removes them within 7 days.
    op.add_column("resumes", sa.Column("user_id", UUID(as_uuid=True), nullable=True))
    op.create_foreign_key(
        "fk_resumes_user_id_users", "resumes", "users", ["user_id"], ["id"], ondelete="CASCADE"
    )
    op.create_index("ix_resumes_user_id", "resumes", ["user_id"])


def downgrade() -> None:
    op.drop_index("ix_resumes_user_id", table_name="resumes")
    op.drop_constraint("fk_resumes_user_id_users", "resumes", type_="foreignkey")
    op.drop_column("resumes", "user_id")
    op.drop_table("users")
