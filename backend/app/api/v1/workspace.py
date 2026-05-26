"""Agent 工作区 API"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.agent import Agent

router = APIRouter(prefix="/api/workspace", tags=["workspace"])


@router.post("/agents/{agent_id}")
def add_to_workspace(agent_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    agent = db.query(Agent).filter(Agent.id == agent_id).first()
    if not agent:
        raise HTTPException(404, "Agent 不存在")
    # 工作区就是用户的 Agent 列表，这里简化处理
    return {"message": "Agent 已添加到工作区", "agent_id": agent_id}


@router.get("/agents")
def list_workspace(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    agents = db.query(Agent).filter(Agent.user_id == user.id, Agent.deleted_at.is_(None)).all()
    return [{"id": a.id, "name": a.name, "enabled": a.enabled} for a in agents]
