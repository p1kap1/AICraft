"""Agent API - CRUD + 版本管理"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.agent import Agent, AgentVersion
from app.schemas.common import (
    AgentCreateRequest, AgentResponse, PublishRequest,
    AgentVersionResponse, ApiResponse, AgentUpdate,
)
import uuid, datetime

router = APIRouter(prefix="/api/agents", tags=["agents"])


@router.post("", response_model=ApiResponse)
def create_agent(req: AgentCreateRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    agent = Agent(
        name=req.name, description=req.description, avatar=req.avatar,
        system_prompt=req.system_prompt, welcome_message=req.welcome_message,
        llm_config=req.llm_config, tool_ids=req.tool_ids,
        provider_source=getattr(req, "provider_source", None) or "personal",
        provider_id=getattr(req, "provider_id", None),
        user_id=user.id,
    )
    db.add(agent); db.commit()
    return ApiResponse(data={"id": agent.id, "name": agent.name})


@router.get("/user", response_model=list[AgentResponse])
def list_agents(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(Agent).filter(Agent.user_id == user.id, Agent.deleted_at.is_(None)).order_by(Agent.updated_at.desc()).all()


# /published 必须在 /{agent_id} 前面！否则 FastAPI 会把 "published" 当成 agent_id
@router.get("/published")
def get_published(db: Session = Depends(get_db)):
    versions = db.query(AgentVersion).filter(AgentVersion.publish_status >= 1).order_by(AgentVersion.created_at.desc()).limit(20).all()
    return [{"id": v.id, "agent_id": v.agent_id, "name": db.query(Agent).filter(Agent.id == v.agent_id).first().name if db.query(Agent).filter(Agent.id == v.agent_id).first() else "Unknown", "version_number": v.version_number, "system_prompt": v.system_prompt, "tool_ids": v.tool_ids or [], "knowledge_base_ids": v.knowledge_base_ids or [], "change_log": v.change_log, "created_at": v.created_at.isoformat()} for v in versions]


@router.get("/{agent_id}", response_model=AgentResponse)
def get_agent(agent_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    agent = db.query(Agent).filter(Agent.id == agent_id, Agent.user_id == user.id, Agent.deleted_at.is_(None)).first()
    if not agent: raise HTTPException(404, "Agent 不存在")
    return agent


@router.put("/{agent_id}", response_model=AgentResponse)
def update_agent(agent_id: str, req: AgentUpdate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    agent = db.query(Agent).filter(Agent.id == agent_id, Agent.user_id == user.id, Agent.deleted_at.is_(None)).first()
    if not agent: raise HTTPException(404, "Agent 不存在")
    for key, value in req.model_dump(exclude_unset=True).items():
        setattr(agent, key, value)
    db.commit(); db.refresh(agent)
    return agent


@router.delete("/{agent_id}")
def delete_agent(agent_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    agent = db.query(Agent).filter(Agent.id == agent_id, Agent.user_id == user.id, Agent.deleted_at.is_(None)).first()
    if not agent: raise HTTPException(404, "Agent 不存在")
    agent.deleted_at = datetime.datetime.now(datetime.timezone.utc)
    db.commit()
    return ApiResponse(message="已删除")


@router.post("/{agent_id}/publish", response_model=ApiResponse)
def publish_version(agent_id: str, req: PublishRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    agent = db.query(Agent).filter(Agent.id == agent_id, Agent.user_id == user.id, Agent.deleted_at.is_(None)).first()
    if not agent: raise HTTPException(404, "Agent 不存在")

    version = AgentVersion(
        agent_id=agent.id, version_number=req.version_number,
        system_prompt=agent.system_prompt, welcome_message=agent.welcome_message,
        llm_config=agent.llm_config, tool_ids=agent.tool_ids,
        knowledge_base_ids=agent.knowledge_base_ids,
        change_log=req.change_log, publish_status=2, user_id=user.id,
    )
    db.add(version)
    agent.published_version = req.version_number
    db.commit()
    return ApiResponse(data={"version_id": version.id, "version": req.version_number})


@router.get("/{agent_id}/versions")
def list_versions(agent_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(AgentVersion).filter(AgentVersion.agent_id == agent_id).order_by(AgentVersion.created_at.desc()).all()


@router.post("/{agent_id}/versions/{version_id}/rollback", response_model=ApiResponse)
def rollback_version(agent_id: str, version_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    version = db.query(AgentVersion).filter(AgentVersion.id == version_id, AgentVersion.agent_id == agent_id).first()
    if not version: raise HTTPException(404, "版本不存在")
    agent = db.query(Agent).filter(Agent.id == agent_id, Agent.user_id == user.id).first()
    if not agent: raise HTTPException(404, "Agent 不存在")
    agent.system_prompt = version.system_prompt
    agent.welcome_message = version.welcome_message
    agent.llm_config = version.llm_config
    agent.published_version = version.version_number
    db.commit()
    return ApiResponse(message="已回滚", data={"version": version.version_number})
