from datetime import datetime
from sqlalchemy import String, DateTime, ForeignKey, func, Boolean, Integer, Float
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base

class PlatformProvider(Base):
    '''管理员配置的平台级模型，所有用户可用平台余额调用'''
    __tablename__ = "platform_providers"
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    provider_type: Mapped[str] = mapped_column(String(20), default="openai")
    base_url: Mapped[str] = mapped_column(String(500))
    api_key: Mapped[str] = mapped_column(String(500))
    model: Mapped[str] = mapped_column(String(100))
    price_per_1k_tokens: Mapped[float] = mapped_column(Float, default=0.01)  # $0.01 per 1000 tokens
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
