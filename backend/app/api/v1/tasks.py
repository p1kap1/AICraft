"""定时任务 API"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.task import ScheduledTask
from app.schemas.common import ApiResponse
from app.services.scheduler import execute_scheduled_task

router = APIRouter(prefix="/api/tasks", tags=["tasks"])


@router.post("")
def create_task(
    name: str = "",
    agent_id: str = "",
    cron_expr: str = "0 9 * * *",
    prompt: str = "",
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    task = ScheduledTask(name=name, agent_id=agent_id, cron_expr=cron_expr, prompt=prompt, user_id=user.id)
    db.add(task)
    db.commit()
    db.refresh(task)
    return ApiResponse(data={"id": task.id, "name": task.name})


@router.get("/user")
def list_tasks(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    tasks = db.query(ScheduledTask).filter(ScheduledTask.user_id == user.id).all()
    return [{"id": t.id, "name": t.name, "cron": t.cron_expr, "enabled": t.enabled, "last_run": t.last_run_at} for t in tasks]


@router.post("/{task_id}/run")
def run_task(task_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    task = db.query(ScheduledTask).filter(ScheduledTask.id == task_id, ScheduledTask.user_id == user.id).first()
    if not task:
        raise HTTPException(404, "任务不存在")
    result = execute_scheduled_task(task_id, db)
    return ApiResponse(data={"result": result})


@router.delete("/{task_id}")
def delete_task(task_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    task = db.query(ScheduledTask).filter(ScheduledTask.id == task_id, ScheduledTask.user_id == user.id).first()
    if not task:
        raise HTTPException(404)
    db.delete(task)
    db.commit()
    return ApiResponse(message="已删除")
