"""定时任务 - Agent 自动执行"""
import json
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from openai import OpenAI

from app.core.config import settings
from app.models.task import ScheduledTask
from app.services.tool_registry import get_tool_definitions, execute_tool


def get_client():
    return OpenAI(api_key=settings.OPENAI_API_KEY, base_url=settings.OPENAI_BASE_URL)


def execute_scheduled_task(task_id: str, db: Session):
    """执行一个定时任务"""
    task = db.query(ScheduledTask).filter(ScheduledTask.id == task_id).first()
    if not task or not task.enabled:
        return

    client = get_client()
    messages = [{"role": "user", "content": task.prompt}]

    tools = get_tool_definitions()
    resp = client.chat.completions.create(
        model=settings.DEFAULT_MODEL,
        messages=messages,
        tools=tools,
        tool_choice="auto",
    )

    choice = resp.choices[0]
    result = choice.message.content or "无回复"

    if choice.message.tool_calls:
        for tc in choice.message.tool_calls:
            args = json.loads(tc.function.arguments)
            tr = execute_tool(tc.function.name, args)
            messages.append({"role": "assistant", "content": None,
                "tool_calls": [{"id": tc.id, "type": "function",
                    "function": {"name": tc.function.name, "arguments": tc.function.arguments}}]})
            messages.append({"role": "tool", "tool_call_id": tc.id, "content": tr})
        resp2 = client.chat.completions.create(model=settings.DEFAULT_MODEL, messages=messages)
        result = resp2.choices[0].message.content

    task.last_run_at = datetime.now(timezone.utc)
    db.commit()
    return result
