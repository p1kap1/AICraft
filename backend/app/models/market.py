from datetime import datetime
from sqlalchemy import String, DateTime, ForeignKey, func, Boolean, Text, Integer
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base

class ToolMarketItem(Base):
    __tablename__ = "tool_market"
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    tool_id: Mapped[str] = mapped_column(String(36), ForeignKey("tools.id"))
    name: Mapped[str] = mapped_column(String(100))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    author_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"))
    downloads: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[str] = mapped_column(String(20), default="published")  # pending/published/rejected
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

class ToolInstall(Base):
    __tablename__ = "tool_installs"
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    market_item_id: Mapped[str] = mapped_column(String(36), ForeignKey("tool_market.id"))
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"))
    installed_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
