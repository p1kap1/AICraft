from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.market import ToolMarketItem

router = APIRouter(prefix="/api/admin", tags=["admin"])

@router.get("/tools/pending")
def pending_tools(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not user.is_admin: raise HTTPException(403, "admin only")
    return [{"id": i.id, "name": i.name, "status": i.status} for i in db.query(ToolMarketItem).filter(ToolMarketItem.status.in_(["pending"])).all()]

@router.post("/tools/{item_id}/approve")
def approve_tool(item_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not user.is_admin: raise HTTPException(403)
    item = db.query(ToolMarketItem).filter(ToolMarketItem.id == item_id).first()
    if not item: raise HTTPException(404)
    item.status = "published"; db.commit()
    return {"message": "approved"}
