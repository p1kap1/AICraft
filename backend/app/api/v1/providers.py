"""模型服务商 API"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.others import Provider
from app.schemas.common import ApiResponse

router = APIRouter(prefix="/api/providers", tags=["providers"])


@router.post("")
def create_provider(
    name: str = "",
    provider_type: str = "openai",
    base_url: str = "",
    api_key: str = "",
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    provider = Provider(
        name=name,
        provider_type=provider_type,
        base_url=base_url,
        api_key=api_key,
        user_id=user.id,
    )
    db.add(provider)
    db.commit()
    db.refresh(provider)
    return ApiResponse(data={"id": provider.id, "name": provider.name})


@router.get("/user")
def list_providers(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    providers = db.query(Provider).filter(Provider.user_id == user.id).all()
    return [
        {
            "id": p.id,
            "name": p.name,
            "provider_type": p.provider_type,
            "base_url": p.base_url,
            "enabled": p.enabled,
        }
        for p in providers
    ]


@router.delete("/{provider_id}")
def delete_provider(provider_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    provider = db.query(Provider).filter(Provider.id == provider_id, Provider.user_id == user.id).first()
    if not provider:
        raise HTTPException(404, "服务商不存在")
    db.delete(provider)
    db.commit()
    return ApiResponse(message="已删除")
