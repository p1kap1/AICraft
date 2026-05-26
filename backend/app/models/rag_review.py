from datetime import datetime
from sqlalchemy import String, DateTime, ForeignKey, func, Text, Integer
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base

class RagReview(Base):
    __tablename__ = "rag_reviews"
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    kb_id: Mapped[str] = mapped_column(String(36), ForeignKey("knowledge_bases.id"))
    reviewer_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"))
    status: Mapped[str] = mapped_column(String(20), default="pending")  # pending/approved/rejected
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
