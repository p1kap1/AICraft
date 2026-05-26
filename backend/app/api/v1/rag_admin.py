from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.knowledge import KnowledgeBase
from app.models.rag_review import RagReview
import uuid, datetime as dt

router = APIRouter(prefix="/api/admin/rag", tags=["admin-rag"])

@router.get("/pending")
def pending_rags(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not user.is_admin: raise HTTPException(403)
    reviews = db.query(RagReview).filter(RagReview.status == "pending").all()
    result = []
    for rv in reviews:
        kb = db.query(KnowledgeBase).filter(KnowledgeBase.id == rv.kb_id).first()
        result.append({"review_id": rv.id, "kb_id": rv.kb_id, "kb_name": kb.name if kb else "Unknown", "status": rv.status, "created_at": rv.created_at.isoformat()})
    return result

@router.post("/{review_id}/approve")
def approve_rag(review_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not user.is_admin: raise HTTPException(403)
    rv = db.query(RagReview).filter(RagReview.id == review_id).first()
    if not rv: raise HTTPException(404)
    rv.status = "approved"; rv.reviewed_at = dt.datetime.utcnow()
    db.commit()
    return {"message": "approved"}

@router.post("/{review_id}/reject")
def reject_rag(review_id: str, comment: str = "", user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not user.is_admin: raise HTTPException(403)
    rv = db.query(RagReview).filter(RagReview.id == review_id).first()
    if not rv: raise HTTPException(404)
    rv.status = "rejected"; rv.comment = comment; rv.reviewed_at = dt.datetime.utcnow()
    db.commit()
    return {"message": "rejected"}
