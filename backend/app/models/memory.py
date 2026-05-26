"""数据模型 - 长期记忆"""
import uuid
from datetime import datetime, timezone
from sqlalchemy import String, DateTime, Text, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column
from pgvector.sqlalchemy import Vector

from app.core.database import Base


class Memory(Base):
    __tablename__ = "memories"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"))
    content: Mapped[str] = mapped_column(Text)            # 记忆内容，如「用户喜欢简洁回复」
    category: Mapped[str | None] = mapped_column(String(50), default="fact")  # fact / preference / context
    embedding: Mapped[list | None] = mapped_column(Vector(128), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
