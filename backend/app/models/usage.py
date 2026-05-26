import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, ForeignKey, func, Integer, Float
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base

class UsageRecord(Base):
    __tablename__ = "usage_records"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"))
    agent_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    model: Mapped[str] = mapped_column(String(100))
    prompt_tokens: Mapped[int] = mapped_column(Integer, default=0)
    completion_tokens: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
