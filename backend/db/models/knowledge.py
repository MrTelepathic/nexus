"""Knowledge base and LLM cache models (pgvector)."""

from db.models.base import Base, TenantMixin, UUIDPrimaryKeyMixin
from pgvector.sqlalchemy import Vector
from sqlalchemy import Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column


class KnowledgeBase(Base, UUIDPrimaryKeyMixin, TenantMixin):
    """RAG knowledge base chunks with vector embeddings."""

    __tablename__ = "knowledge_base"

    title: Mapped[str] = mapped_column(String(500), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    source: Mapped[str | None] = mapped_column(String(500), nullable=True)
    embedding = mapped_column(Vector(1536), nullable=True)
    metadata_: Mapped[dict] = mapped_column("metadata", JSONB, default=dict)


class LLMCache(Base, UUIDPrimaryKeyMixin, TenantMixin):
    """Semantic LLM response cache."""

    __tablename__ = "llm_cache"

    query_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    query_embedding = mapped_column(Vector(1536), nullable=True)
    response: Mapped[str] = mapped_column(Text, nullable=False)
    model: Mapped[str] = mapped_column(String(100), nullable=False)
    token_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    hit_count: Mapped[int] = mapped_column(Integer, default=0)
    expires_at: Mapped[str] = mapped_column(nullable=False)
