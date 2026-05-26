"""定时任务模型"""
import uuid
from datetime import datetime, timezone
from sqlalchemy import String, DateTime, Text, ForeignKey, func, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class ScheduledTask(Base):
    __tablename__ = "scheduled_tasks"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String(255))
    agent_id: Mapped[str] = mapped_column(String(36), ForeignKey("agents.id"))
    # cron 表达式: "*/5 * * * *" 每5分钟 / "0 9 * * *" 每天9点
    cron_expr: Mapped[str] = mapped_column(String(50), default="0 9 * * *")
    prompt: Mapped[str] = mapped_column(Text)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    last_run_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
