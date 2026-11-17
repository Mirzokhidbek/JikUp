from pgvector.sqlalchemy import Vector
from sqlalchemy import ForeignKey, Index, UniqueConstraint, text
from sqlalchemy.dialects.postgresql import TSVECTOR
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base

EMBED_DIM = 1536


class JobChunk(Base):
    __tablename__ = "job_chunks"
    __table_args__ = (
        UniqueConstraint("job_id", "chunk_index", name="uq_job_chunks_job_chunk"),
        Index(
            "ix_job_chunks_embedding_hnsw",
            "embedding",
            postgresql_using="hnsw",
            postgresql_with={"m": 16, "ef_construction": 64},
            postgresql_ops={"embedding": "vector_cosine_ops"},
        ),
        Index("ix_job_chunks_search_tokens", "search_tokens", postgresql_using="gin"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    job_id: Mapped[int] = mapped_column(ForeignKey("jobs.id", ondelete="CASCADE"))
    chunk_index: Mapped[int]
    section: Mapped[str]
    content: Mapped[str]
    search_tokens: Mapped[str] = mapped_column(TSVECTOR, server_default=text("''::tsvector"))
    embedding: Mapped[list[float] | None] = mapped_column(Vector(EMBED_DIM))
