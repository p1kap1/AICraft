from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.platform_provider import PlatformProvider
import uuid

router = APIRouter(prefix="/api/admin/providers", tags=["admin-providers"])

@router.post("")
def add_platform_provider(
    name: str = "", base_url: str = "", api_key: str = "",
    model: str = "", price: float = 0.01,
    user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    if not user.is_admin: raise HTTPException(403, "admin only")
    p = PlatformProvider(id=str(uuid.uuid4()), name=name, base_url=base_url,
        api_key=api_key, model=model, price_per_1k_tokens=price)
    db.add(p); db.commit()
    return {"message": "added", "id": p.id}

@router.get("")
def list_platform_providers(db: Session = Depends(get_db)):
    return [{"id": p.id, "name": p.name, "model": p.model, "price": p.price_per_1k_tokens, "enabled": p.enabled, "base_url": p.base_url} for p in db.query(PlatformProvider).filter(PlatformProvider.enabled == True).all()]

@router.delete("/{pid}")
def delete_provider(pid: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not user.is_admin: raise HTTPException(403)
    p = db.query(PlatformProvider).filter(PlatformProvider.id == pid).first()
    if p: db.delete(p); db.commit()
    return {"message": "deleted"}
