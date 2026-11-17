from pgvector.sqlalchemy import Vector
from sqlalchemy import ForeignKey, Index, UniqueConstraint
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
        Index(
            "ix_job_chunks_content_trgm",
            "content",
            postgresql_using="gin",
            postgresql_ops={"content": "gin_trgm_ops"},
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    job_id: Mapped[int] = mapped_column(ForeignKey("jobs.id", ondelete="CASCADE"))
    chunk_index: Mapped[int]
    section: Mapped[str]
    content: Mapped[str]
    embedding: Mapped[list[float] | None] = mapped_column(Vector(EMBED_DIM))
