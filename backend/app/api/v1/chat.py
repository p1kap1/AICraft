"""对话 API - SSE 流式 + Agent 规划引擎 + 高可用故障转移"""
import json, uuid
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from openai import OpenAI

from app.core.config import settings
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.agent import Agent
from app.models.others import Session, Message
from app.schemas.common import ChatRequest
from app.services.tool_registry import get_tool_definitions, execute_tool
from app.services.rate_limiter import check_rate_limit

router = APIRouter(prefix="/api/chat", tags=["chat"])

PLANNER_SYSTEM_PROMPT = """你是一个 AI Agent，严格按以下四步处理用户指令：

1. 分析意图：理解用户真正想做什么
2. 拆解子任务：把复杂任务分解为可执行的步骤
3. 工具调度：判断是否需要调用工具，如需要则调用
4. 结果汇总：整合执行结果，给出完整回复

不要问"我该怎么帮你"，直接执行。"""


@router.post("/stream")
async def chat_stream(req: ChatRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    allowed, reason = check_rate_limit(user.id)
    if not allowed: raise HTTPException(429, reason)

    if req.session_id:
        session = db.query(Session).filter(Session.id == req.session_id).first()
    else:
        session = Session(id=str(uuid.uuid4()), user_id=user.id, title=req.message[:30])
        db.add(session); db.commit()
        # 异步生成标题
        import threading
        def gen_title():
            try:
                from app.core.database import SessionLocal
                sdb = SessionLocal()
                try:
                    resp = client.chat.completions.create(
                        model=settings.DEFAULT_MODEL,
                        messages=[{"role": "system", "content": "用 10 个字以内概括用户意图，只返回概括结果。"}, {"role": "user", "content": req.message}],
                        max_tokens=20
                    )
                    title = resp.choices[0].message.content.strip()[:20]
                    sdb.query(Session).filter(Session.id == session.id).update({"title": title})
                    sdb.commit()
                finally:
                    sdb.close()
            except:
                pass
        threading.Thread(target=gen_title).start()

    agent = db.query(Agent).filter(Agent.id == req.agent_id).first() if req.agent_id else None

    # 自动选择 Provider
    from app.models.others import Provider
    failover_providers = []

    # 优先用当前用户的默认模型（即使是别人的 Agent，也用你自己配置的 Key）
    if not user.is_admin and user.default_provider_id:
        dp = db.query(Provider).filter(Provider.id == user.default_provider_id, Provider.user_id == user.id).first()
        if dp: failover_providers = [{"api_key": dp.api_key, "base_url": dp.base_url, "model": settings.DEFAULT_MODEL}]
    
    # 没有默认模型 → 看 Agent 的配置
    if not failover_providers:
        if agent and agent.provider_source == "platform" and agent.provider_id:
            from app.services.billing_engine import get_providers_for_model
            failover_providers = get_providers_for_model(agent.provider_id, db)
        elif agent and agent.provider_source == "personal":
            p = db.query(Provider).filter(Provider.id == agent.provider_id, Provider.user_id == user.id).first() if agent.provider_id else None
            if p: failover_providers = [{"api_key": p.api_key, "base_url": p.base_url, "model": settings.DEFAULT_MODEL}]
        elif not user.is_admin:
            raise HTTPException(402, "请先在「设置」里选择默认模型，或创建 Agent 对话")

    if not failover_providers:
        failover_providers = [{"api_key": settings.OPENAI_API_KEY, "base_url": settings.OPENAI_BASE_URL, "model": settings.DEFAULT_MODEL}]

    msg = Message(id=str(uuid.uuid4()), session_id=session.id, role="user", content=req.message)
    db.add(msg); db.commit()

    messages = [{"role": "system", "content": PLANNER_SYSTEM_PROMPT}]
    if agent and agent.system_prompt:
        messages.append({"role": "system", "content": agent.system_prompt})

    history = db.query(Message).filter(Message.session_id == session.id).order_by(Message.created_at.asc()).limit(20).all()
    messages.extend({"role": m.role, "content": m.content} for m in history[:-1])
    messages.append({"role": "user", "content": req.message})

    # 工具：只能通过 Agent 绑定获得
    if agent and agent.tool_ids:
        all_tools = get_tool_definitions(db)
        tools = [t for t in all_tools if any(t.get("function",{}).get("name") == tid for tid in agent.tool_ids)]
    else:
        tools = get_tool_definitions(db) if not agent else []

    # 知识库：Agent 绑定了就检索，结果注入 prompt
    if agent and agent.knowledge_base_ids:
        try:
            from app.services.kb_search import search_knowledge
            kb_results = search_knowledge(req.message, agent.knowledge_base_ids)
            if kb_results:
                kb_text = "\n".join(f"- {s}" for s in kb_results[:5])
                messages.insert(-1, {"role": "system", "content": f"知识库检索结果：\n{kb_text}\n请基于以上信息回答。"})
        except:
            pass

    async def generate():
        full = ""
        try:
            # 故障转移：依次尝试每个 provider
            for attempt, p in enumerate(failover_providers):
                if attempt > 0:
                    yield f"data: {json.dumps({'type': 'system', 'content': '节点故障，自动切换...'})}\n\n"
                try:
                    fc = OpenAI(api_key=p["api_key"], base_url=p["base_url"])
                    model = p.get("model", settings.DEFAULT_MODEL)
                    stream = fc.chat.completions.create(model=model, messages=messages, tools=tools, tool_choice="auto", stream=True)

                    tool_calls_acc = {}
                    for chunk in stream:
                        delta = chunk.choices[0].delta
                        if delta.tool_calls:
                            for tc in delta.tool_calls:
                                idx = tc.index
                                if idx not in tool_calls_acc:
                                    tool_calls_acc[idx] = {"id": tc.id or "", "name": "", "args": ""}
                                if tc.function:
                                    if tc.function.name: tool_calls_acc[idx]["name"] += tc.function.name
                                    if tc.function.arguments: tool_calls_acc[idx]["args"] += tc.function.arguments
                            continue
                        if delta.content:
                            full += delta.content
                            yield f"data: {json.dumps({'type': 'text', 'content': delta.content})}\n\n"

                    if tool_calls_acc:
                        for tc in tool_calls_acc.values():
                            args = json.loads(tc["args"])
                            result = execute_tool(tc["name"], args, db)
                            yield f"data: {json.dumps({'type': 'tool', 'name': tc['name'], 'result': result[:200]})}\n\n"
                            messages.append({"role": "assistant", "content": None, "tool_calls": [{"id": tc["id"], "type": "function", "function": {"name": tc["name"], "arguments": tc["args"]}}]})
                            messages.append({"role": "tool", "tool_call_id": tc["id"], "content": result})
                        stream2 = fc.chat.completions.create(model=model, messages=messages, stream=True)
                        for chunk in stream2:
                            if chunk.choices[0].delta.content:
                                c = chunk.choices[0].delta.content
                                full += c
                                yield f"data: {json.dumps({'type': 'text', 'content': c})}\n\n"

                    yield f"data: {json.dumps({'type': 'done', 'content': full})}\n\n"
                    db.add(Message(id=str(uuid.uuid4()), session_id=session.id, role="assistant", content=full))
                    db.commit()
                    return  # 成功，退出

                except Exception as e:
                    if attempt == len(failover_providers) - 1:
                        raise  # 最后一个也失败了，抛出
                    continue  # 试下一个

        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'content': f'所有节点均失败: {str(e)[:100]}'})}\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Session-Id": session.id})


@router.get("/sessions")
def list_sessions(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return [{"id": s.id, "title": s.title, "created_at": s.created_at.isoformat()} for s in db.query(Session).filter(Session.user_id == user.id).order_by(Session.updated_at.desc()).all()]


@router.delete("/sessions/{session_id}")
def delete_session(session_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    s = db.query(Session).filter(Session.id == session_id, Session.user_id == user.id).first()
    if not s: raise HTTPException(404, "会话不存在")
    # 先删关联消息
    db.query(Message).filter(Message.session_id == session_id).delete()
    db.delete(s); db.commit()
    return {"message": "deleted"}

@router.get("/sessions/{session_id}/messages")
def get_messages(session_id: str, db: Session = Depends(get_db)):
    return [{"id": m.id, "role": m.role, "content": m.content} for m in db.query(Message).filter(Message.session_id == session_id).order_by(Message.created_at.asc()).all()]
