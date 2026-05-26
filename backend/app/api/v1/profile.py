from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User

router = APIRouter(prefix="/api/profile", tags=["profile"])

@router.get("")
def get_profile(user: User = Depends(get_current_user)):
    return {"id": user.id, "email": user.email, "phone": user.phone, "nickname": user.nickname, "is_admin": user.is_admin, "default_provider_id": user.default_provider_id, "created_at": user.created_at.isoformat()}

@router.put("")
def update_profile(nickname: str = "", default_provider_id: str = "", user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    u = db.query(User).filter(User.id == user.id).first()
    if not u: return {"message": "user not found"}
    if nickname: u.nickname = nickname
    if default_provider_id: u.default_provider_id = default_provider_id
    db.commit()
    return {"message": "updated", "nickname": u.nickname, "default_provider_id": u.default_provider_id}
