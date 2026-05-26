from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.agent import Agent
from app.models.knowledge import KnowledgeBase

router = APIRouter(prefix="/api/binding", tags=["binding"])

@router.post("/agent/{agent_id}/kb/{kb_id}")
def bind_kb(agent_id: str, kb_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    agent = db.query(Agent).filter(Agent.id == agent_id, Agent.user_id == user.id).first()
    kb = db.query(KnowledgeBase).filter(KnowledgeBase.id == kb_id, KnowledgeBase.user_id == user.id).first()
    if not agent or not kb: raise HTTPException(404, "not found")
    ids = agent.knowledge_base_ids or []
    if kb_id not in ids: ids.append(kb_id)
    agent.knowledge_base_ids = ids
    db.commit()
    return {"message": "bound", "kb_ids": ids}

@router.get("/agent/{agent_id}/kbs")
def get_bound_kbs(agent_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    agent = db.query(Agent).filter(Agent.id == agent_id, Agent.user_id == user.id).first()
    if not agent: raise HTTPException(404, "not found")
    ids = agent.knowledge_base_ids or []
    kbs = db.query(KnowledgeBase).filter(KnowledgeBase.id.in_(ids)).all() if ids else []
    return [{"id": k.id, "name": k.name} for k in kbs]
