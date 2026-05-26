from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.others import Tool
from app.models.market import ToolMarketItem, ToolInstall
import uuid

router = APIRouter(prefix="/api/market", tags=["market"])

@router.post("/publish")
def publish_tool(tool_id: str = "", user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    tool = db.query(Tool).filter(Tool.id == tool_id, Tool.user_id == user.id).first()
    if not tool: raise HTTPException(404, "工具不存在")
    item = ToolMarketItem(id=str(uuid.uuid4()), tool_id=tool.id, name=tool.name, description=tool.description, author_id=user.id)
    db.add(item); db.commit()
    return {"message": "published", "item_id": item.id}

@router.get("/browse")
def browse_market(db: Session = Depends(get_db)):
    items = db.query(ToolMarketItem).filter(ToolMarketItem.status == "published").order_by(ToolMarketItem.downloads.desc()).all()
    return [{"id": i.id, "name": i.name, "description": i.description, "downloads": i.downloads} for i in items]

@router.post("/install/{item_id}")
def install(item_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    item = db.query(ToolMarketItem).filter(ToolMarketItem.id == item_id).first()
    if not item: raise HTTPException(404, "not found")
    existing = db.query(ToolInstall).filter(ToolInstall.market_item_id == item_id, ToolInstall.user_id == user.id).first()
    if not existing:
        # Copy tool to user
        src = db.query(Tool).filter(Tool.id == item.tool_id).first()
        if src:
            new_tool = Tool(id=str(uuid.uuid4()), name=src.name, description=src.description, tool_type=src.tool_type, config=src.config, user_id=user.id)
            db.add(new_tool)
        inst = ToolInstall(id=str(uuid.uuid4()), market_item_id=item_id, user_id=user.id)
        db.add(inst)
        item.downloads += 1
        db.commit()
    return {"message": "installed"}
