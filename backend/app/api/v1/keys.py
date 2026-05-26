import secrets
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.apikey import ApiKey
from app.schemas.common import ApiResponse

router = APIRouter(prefix="/api/keys", tags=["api-keys"])

@router.post("")
def create_key(name: str = "", user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    key = ApiKey(name=name, key=f"ak-{secrets.token_urlsafe(24)}", user_id=user.id)
    db.add(key); db.commit(); db.refresh(key)
    return ApiResponse(data={"id": key.id, "name": key.name, "key": key.key})

@router.get("/user")
def list_keys(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return [{"id": k.id, "name": k.name, "key": k.key[:8]+"***", "enabled": k.enabled, "last_used": k.last_used_at} for k in db.query(ApiKey).filter(ApiKey.user_id == user.id).all()]

@router.delete("/{key_id}")
def delete_key(key_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    k = db.query(ApiKey).filter(ApiKey.id == key_id, ApiKey.user_id == user.id).first()
    if not k: raise HTTPException(404, "not found")
    db.delete(k); db.commit()
    return ApiResponse(message="deleted")
