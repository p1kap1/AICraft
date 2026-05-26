"""Pydantic 请求/响应模型"""
from pydantic import BaseModel, Field
from datetime import datetime


# ===== 用户 =====
class RegisterRequest(BaseModel):
    email: str | None = None
    phone: str | None = None
    password: str = Field(min_length=6)
    nickname: str = "用户"


class LoginRequest(BaseModel):
    account: str
    password: str


class TokenResponse(BaseModel):
    token: str
    user_id: str
    nickname: str


# ===== Agent =====
class AgentCreate(BaseModel):
    name: str
    description: str | None = None
    avatar: str | None = None
    system_prompt: str | None = None
    welcome_message: str | None = None
    llm_config: dict | None = None
    tool_ids: list[str] | None = None


class AgentUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    avatar: str | None = None
    system_prompt: str | None = None
    welcome_message: str | None = None
    llm_config: dict | None = None
    tool_ids: list[str] | None = None


class AgentResponse(BaseModel):
    id: str
    name: str
    description: str | None
    avatar: str | None
    system_prompt: str | None
    welcome_message: str | None
    llm_config: dict | None
    tool_ids: list | None
    enabled: bool
    published_version: str | None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AgentVersionResponse(BaseModel):
    id: str
    version_number: str
    system_prompt: str | None
    change_log: str | None
    publish_status: int
    created_at: datetime

    class Config:
        from_attributes = True


class PublishRequest(BaseModel):
    version_number: str
    change_log: str | None = None


# ===== 对话 =====
class ChatRequest(BaseModel):
    message: str
    session_id: str | None = None
    agent_id: str | None = None
    provider_id: str | None = None

class AgentCreateRequest(BaseModel):
    name: str = ""
    description: str | None = None
    avatar: str | None = None
    system_prompt: str | None = None
    welcome_message: str | None = None
    llm_config: dict | None = None
    tool_ids: list | None = None
    knowledge_base_ids: list | None = None
    provider_source: str | None = None
    provider_id: str | None = None

class ApiResponse(BaseModel):
    code: int = 200
    message: str = "ok"
    data: dict | list | None = None
