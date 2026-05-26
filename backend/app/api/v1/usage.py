from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.usage import UsageRecord

router = APIRouter(prefix="/api/usage", tags=["usage"])

@router.get("/stats")
def get_stats(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    records = db.query(UsageRecord).filter(UsageRecord.user_id == user.id).order_by(UsageRecord.created_at.desc()).limit(50).all()
    total_prompt = sum(r.prompt_tokens for r in records)
    total_completion = sum(r.completion_tokens for r in records)
    return {"total_calls": len(records), "total_prompt_tokens": total_prompt, "total_completion_tokens": total_completion, "total_tokens": total_prompt + total_completion, "recent": [{"model": r.model, "prompt": r.prompt_tokens, "completion": r.completion_tokens, "time": r.created_at.isoformat()} for r in records[:10]]}
