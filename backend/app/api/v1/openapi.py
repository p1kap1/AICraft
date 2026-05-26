"""Agent OpenAPI - 将 Agent 暴露为 REST API，外部系统可直接调用"""
import json
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from openai import OpenAI

from app.core.config import settings
from app.core.database import get_db
from app.models.agent import Agent
from app.models.others import Session, Message
from app.schemas.common import ApiResponse
from app.services.context_manager import ContextManager
from app.services.tool_registry import get_tool_definitions, execute_tool
from app.services.memory_service import extract_memories, get_relevant_memories, format_memories_for_prompt

router = APIRouter(prefix="/api/v1/agent", tags=["openapi"])


@router.post("/{agent_id}/chat")
async def agent_api_chat(
    agent_id: str,
    request: Request,
    db: Session = Depends(get_db),
):
    """
    外部系统调用 Agent 的 REST API
    调用方式：
    POST /api/v1/agent/{agent_id}/chat
    Body: {"message": "你好", "stream": false}
    Header: X-API-Key: your_key（可选）
    """
    agent = db.query(Agent).filter(Agent.id == agent_id, Agent.deleted_at.is_(None)).first()
    if not agent:
        raise HTTPException(404, "Agent 不存在")

    body = await request.json()
    user_message = body.get("message", "")
    stream = body.get("stream", False)

    client = OpenAI(
        api_key=settings.OPENAI_API_KEY,
        base_url=settings.OPENAI_BASE_URL,
    )

    # 构建消息
    messages = []
    if agent.system_prompt:
        messages.append({"role": "system", "content": agent.system_prompt})

    # 注入长期记忆
    from app.models.user import User
    owner = db.query(User).filter(User.id == agent.user_id).first()
    if owner:
        memories = get_relevant_memories(owner.id, user_message, db)
        if memories:
            mem_text = format_memories_for_prompt(memories)
            messages.append({"role": "system", "content": mem_text})

    messages.append({"role": "user", "content": user_message})

    # 工具调用
    tools = get_tool_definitions()
    resp = client.chat.completions.create(
        model=settings.DEFAULT_MODEL,
        messages=messages,
        tools=tools,
        tool_choice="auto",
    )

    choice = resp.choices[0]
    tool_results = []

    if choice.message.tool_calls:
        for tc in choice.message.tool_calls:
            args = json.loads(tc.function.arguments)
            result = execute_tool(tc.function.name, args)
            tool_results.append({
                "tool": tc.function.name,
                "args": args,
                "result": result,
            })
            messages.append({"role": "assistant", "content": None,
                "tool_calls": [{"id": tc.id, "type": "function",
                    "function": {"name": tc.function.name, "arguments": tc.function.arguments}}]})
            messages.append({"role": "tool", "tool_call_id": tc.id, "content": result})

        resp2 = client.chat.completions.create(
            model=settings.DEFAULT_MODEL,
            messages=messages,
        )
        final_answer = resp2.choices[0].message.content
    else:
        final_answer = choice.message.content

    # 异步提取记忆
    import threading
    def extract():
        extract_memories(owner.id if owner else "unknown",
            f"user: {user_message}\nassistant: {final_answer[:500]}", db)
    threading.Thread(target=extract).start()

    return {
        "agent": agent.name,
        "answer": final_answer,
        "tool_calls": tool_results,
    }


@router.get("/{agent_id}/info")
async def agent_api_info(agent_id: str, db: Session = Depends(get_db)):
    """查看 Agent 的 API 信息"""
    agent = db.query(Agent).filter(Agent.id == agent_id, Agent.deleted_at.is_(None)).first()
    if not agent:
        raise HTTPException(404, "Agent 不存在")

    return {
        "agent_id": agent.id,
        "agent_name": agent.name,
        "api_endpoint": f"POST /api/v1/agent/{agent.id}/chat",
        "usage": {
            "method": "POST",
            "body": {"message": "你的问题", "stream": False},
            "response": {"agent": "名称", "answer": "回复", "tool_calls": []},
        },
        "example": f"curl -X POST http://localhost:8000/api/v1/agent/{agent.id}/chat -H 'Content-Type: application/json' -d '{{\"message\":\"你好\"}}'",
    }
