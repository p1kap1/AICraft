"""数据模型 - Agent"""
import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Boolean, DateTime, Text, Integer, ForeignKey, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Agent(Base):
    """Agent 主表 - 存储当前编辑中的配置"""
    __tablename__ = "agents"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String(255))
    avatar: Mapped[str | None] = mapped_column(String(500), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    system_prompt: Mapped[str | None] = mapped_column(Text, nullable=True)
    welcome_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    # 配置 - JSONB
    llm_config: Mapped[dict | None] = mapped_column("model_config", JSONB, nullable=True)
    provider_source: Mapped[str] = mapped_column(String(20), default="personal")  # personal / platform
    provider_id: Mapped[str | None] = mapped_column(String(36), nullable=True)     # 平台 provider ID
    tool_ids: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    knowledge_base_ids: Mapped[list | None] = mapped_column(JSONB, nullable=True)

    # 状态
    published_version: Mapped[str | None] = mapped_column(String(36), nullable=True)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)

    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class AgentVersion(Base):
    """Agent 版本表 - 存储已发布的不可变快照"""
    __tablename__ = "agent_versions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    agent_id: Mapped[str] = mapped_column(String(36), ForeignKey("agents.id"))
    version_number: Mapped[str] = mapped_column(String(20))  # 1.0.0
    system_prompt: Mapped[str | None] = mapped_column(Text, nullable=True)
    welcome_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    llm_config: Mapped[dict | None] = mapped_column("model_config", JSONB, nullable=True)
    tool_ids: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    knowledge_base_ids: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    change_log: Mapped[str | None] = mapped_column(Text, nullable=True)

    # 审核状态: 0=私有 1=待审核 2=已上架 3=拒绝 4=下架
    publish_status: Mapped[int] = mapped_column(Integer, default=0)
    user_id: Mapped[str] = mapped_column(String(36))

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
