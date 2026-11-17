"""initial schema

Revision ID: 0001
Revises:
Create Date: 2026-11-17
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from pgvector.sqlalchemy import Vector
from sqlalchemy.dialects.postgresql import ARRAY, JSONB

revision: str = "0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

EMBED_DIM = 1536
TS = sa.DateTime(timezone=True)
NOW = sa.text("now()")


def _pk(table: str) -> sa.PrimaryKeyConstraint:
    return sa.PrimaryKeyConstraint("id", name=f"pk_{table}")


def _fk(table: str, column: str, target: str, ondelete: str) -> sa.ForeignKeyConstraint:
    return sa.ForeignKeyConstraint(
        [column], [f"{target}.id"], name=f"fk_{table}_{column}_{target}", ondelete=ondelete
    )


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")

    op.create_table(
        "companies",
        sa.Column("id", sa.Integer, nullable=False),
        sa.Column("name", sa.Text, nullable=False),
        sa.Column("name_normalized", sa.Text, nullable=False),
        sa.Column("industry", sa.Text),
        sa.Column("size", sa.Text),
        sa.Column("location", sa.Text),
        _pk("companies"),
        sa.UniqueConstraint("name_normalized", name="uq_companies_name_normalized"),
    )

    op.create_table(
        "jobs",
        sa.Column("id", sa.Integer, nullable=False),
        sa.Column("source", sa.Text, nullable=False),
        sa.Column("source_job_id", sa.Text, nullable=False),
        sa.Column("url", sa.Text, nullable=False),
        sa.Column("title", sa.Text, nullable=False),
        sa.Column("company_id", sa.Integer),
        sa.Column("location_city", sa.Text),
        sa.Column("location_district", sa.Text),
        sa.Column("experience_min", sa.Integer),
        sa.Column("experience_max", sa.Integer),
        sa.Column("employment_type", sa.Text),
        sa.Column("salary_text", sa.Text),
        sa.Column("description_raw", sa.Text, nullable=False),
        sa.Column("description_clean", sa.Text, nullable=False),
        sa.Column("posted_at", TS),
        sa.Column("deadline_at", TS),
        sa.Column("content_hash", sa.Text, nullable=False),
        sa.Column("is_active", sa.Boolean, server_default=sa.true(), nullable=False),
        sa.Column("created_at", TS, server_default=NOW, nullable=False),
        sa.Column("updated_at", TS, server_default=NOW, nullable=False),
        _pk("jobs"),
        _fk("jobs", "company_id", "companies", "SET NULL"),
        sa.UniqueConstraint("source", "source_job_id", name="uq_jobs_source_job"),
    )
    op.create_index("ix_jobs_company_id", "jobs", ["company_id"])
    op.create_index("ix_jobs_location_city", "jobs", ["location_city"])
    op.create_index("ix_jobs_experience", "jobs", ["experience_min", "experience_max"])
    op.create_index("ix_jobs_posted_at", "jobs", ["posted_at"])
    op.create_index("ix_jobs_content_hash", "jobs", ["content_hash"])
    op.create_index("ix_jobs_is_active", "jobs", ["is_active"])

    op.create_table(
        "skills",
        sa.Column("id", sa.Integer, nullable=False),
        sa.Column("canonical_name", sa.Text, nullable=False),
        sa.Column("category", sa.Text, nullable=False),
        sa.Column("aliases", ARRAY(sa.Text), server_default=sa.text("'{}'"), nullable=False),
        _pk("skills"),
        sa.UniqueConstraint("canonical_name", name="uq_skills_canonical_name"),
    )

    op.create_table(
        "job_skills",
        sa.Column("job_id", sa.Integer, nullable=False),
        sa.Column("skill_id", sa.Integer, nullable=False),
        sa.Column("is_required", sa.Boolean, nullable=False),
        sa.PrimaryKeyConstraint("job_id", "skill_id", name="pk_job_skills"),
        _fk("job_skills", "job_id", "jobs", "CASCADE"),
        _fk("job_skills", "skill_id", "skills", "CASCADE"),
    )
    op.create_index("ix_job_skills_skill_id", "job_skills", ["skill_id"])

    op.create_table(
        "job_chunks",
        sa.Column("id", sa.Integer, nullable=False),
        sa.Column("job_id", sa.Integer, nullable=False),
        sa.Column("chunk_index", sa.Integer, nullable=False),
        sa.Column("section", sa.Text, nullable=False),
        sa.Column("content", sa.Text, nullable=False),
        sa.Column("embedding", Vector(EMBED_DIM)),
        _pk("job_chunks"),
        _fk("job_chunks", "job_id", "jobs", "CASCADE"),
        sa.UniqueConstraint("job_id", "chunk_index", name="uq_job_chunks_job_chunk"),
    )
    op.create_index(
        "ix_job_chunks_embedding_hnsw",
        "job_chunks",
        ["embedding"],
        postgresql_using="hnsw",
        postgresql_with={"m": 16, "ef_construction": 64},
        postgresql_ops={"embedding": "vector_cosine_ops"},
    )
    op.create_index(
        "ix_job_chunks_content_trgm",
        "job_chunks",
        ["content"],
        postgresql_using="gin",
        postgresql_ops={"content": "gin_trgm_ops"},
    )

    op.create_table(
        "resumes",
        sa.Column("id", sa.Integer, nullable=False),
        sa.Column("filename", sa.Text, nullable=False),
        sa.Column("raw_text", sa.Text, nullable=False),
        sa.Column("parsed", JSONB),
        sa.Column("created_at", TS, server_default=NOW, nullable=False),
        _pk("resumes"),
    )

    op.create_table(
        "agent_runs",
        sa.Column("id", sa.Integer, nullable=False),
        sa.Column("resume_id", sa.Integer, nullable=False),
        sa.Column("job_id", sa.Integer),
        sa.Column("status", sa.Text, nullable=False),
        sa.Column("steps", JSONB, server_default=sa.text("'[]'::jsonb"), nullable=False),
        sa.Column("result", JSONB),
        sa.Column("created_at", TS, server_default=NOW, nullable=False),
        _pk("agent_runs"),
        _fk("agent_runs", "resume_id", "resumes", "CASCADE"),
        _fk("agent_runs", "job_id", "jobs", "SET NULL"),
    )
    op.create_index("ix_agent_runs_resume_id", "agent_runs", ["resume_id"])

    op.create_table(
        "collection_runs",
        sa.Column("id", sa.Integer, nullable=False),
        sa.Column("source", sa.Text, nullable=False),
        sa.Column("started_at", TS, server_default=NOW, nullable=False),
        sa.Column("finished_at", TS),
        sa.Column("fetched", sa.Integer, server_default=sa.text("0"), nullable=False),
        sa.Column("inserted", sa.Integer, server_default=sa.text("0"), nullable=False),
        sa.Column("updated", sa.Integer, server_default=sa.text("0"), nullable=False),
        sa.Column("errors", sa.Integer, server_default=sa.text("0"), nullable=False),
        _pk("collection_runs"),
    )


def downgrade() -> None:
    for table in (
        "collection_runs",
        "agent_runs",
        "resumes",
        "job_chunks",
        "job_skills",
        "skills",
        "jobs",
        "companies",
    ):
        op.drop_table(table)
    op.execute("DROP EXTENSION IF EXISTS pg_trgm")
    op.execute("DROP EXTENSION IF EXISTS vector")
