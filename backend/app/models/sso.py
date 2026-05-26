from datetime import datetime
from sqlalchemy import String, DateTime, ForeignKey, func, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base

class SsoProvider(Base):
    __tablename__ = "sso_providers"
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    name: Mapped[str] = mapped_column(String(50))
    provider_type: Mapped[str] = mapped_column(String(20))  # github/google/wechat
    client_id: Mapped[str] = mapped_column(String(100))
    client_secret: Mapped[str] = mapped_column(String(200))
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

class SsoSession(Base):
    __tablename__ = "sso_sessions"
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    state: Mapped[str] = mapped_column(String(100), unique=True)
    user_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("users.id"), nullable=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
