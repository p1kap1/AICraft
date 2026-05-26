from datetime import datetime
from sqlalchemy import String, DateTime, ForeignKey, func, Integer, Float
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base

class UserCredit(Base):
    __tablename__ = "user_credits"
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), primary_key=True)
    balance: Mapped[float] = mapped_column(Float, default=10.0)
    total_used: Mapped[float] = mapped_column(Float, default=0.0)
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

class Order(Base):
    __tablename__ = "orders"
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"))
    amount: Mapped[float] = mapped_column(Float)
    credits: Mapped[float] = mapped_column(Float)
    status: Mapped[str] = mapped_column(String(20), default="paid")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
