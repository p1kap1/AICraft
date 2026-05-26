"""工具 API - 注册/发现/调用"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.others import Tool
from app.schemas.common import ApiResponse

router = APIRouter(prefix="/api/tools", tags=["tools"])


@router.post("")
def create_tool(
    name: str = "",
    description: str = "",
    tool_type: str = "function",
    config: dict | None = None,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    tool = Tool(
        name=name,
        description=description,
        tool_type=tool_type,
        config=config or {},
        user_id=user.id,
    )
    db.add(tool)
    db.commit()
    db.refresh(tool)
    return ApiResponse(data={"id": tool.id, "name": tool.name})


@router.get("/user")
def list_tools(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    tools = db.query(Tool).filter(Tool.user_id == user.id).all()
    return [
        {
            "id": t.id,
            "name": t.name,
            "description": t.description,
            "tool_type": t.tool_type,
            "config": t.config,
            "enabled": t.enabled,
        }
        for t in tools
    ]


@router.delete("/{tool_id}")
def delete_tool(tool_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    tool = db.query(Tool).filter(Tool.id == tool_id, Tool.user_id == user.id).first()
    if not tool:
        raise HTTPException(404, "工具不存在")
    db.delete(tool)
    db.commit()
    return ApiResponse(message="已删除")
