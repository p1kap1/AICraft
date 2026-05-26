from datetime import datetime
from sqlalchemy import String, DateTime, ForeignKey, func, Float
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base

class Payment(Base):
    __tablename__ = "payments"
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"))
    amount: Mapped[float] = mapped_column(Float)
    method: Mapped[str] = mapped_column(String(20))  # alipay/wechat/stripe
    status: Mapped[str] = mapped_column(String(20), default="pending")  # pending/completed/failed
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
