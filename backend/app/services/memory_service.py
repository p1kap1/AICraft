"""长期记忆服务 - 提取 & 检索"""
from sqlalchemy.orm import Session
from sqlalchemy import func
from openai import OpenAI

from app.core.config import settings
from app.models.memory import Memory


def get_client():
    return OpenAI(
        api_key=settings.OPENAI_API_KEY,
        base_url=settings.OPENAI_BASE_URL,
    )


def extract_memories(user_id: str, conversation: str, db: Session) -> list[Memory]:
    """从对话中提取重要事实作为记忆"""
    client = get_client()
    try:
        resp = client.chat.completions.create(
            model=settings.DEFAULT_MODEL,
            messages=[{
                "role": "system",
                "content": "从以下对话中提取关于用户的重要信息。每行一条，用 'fact:' 'preference:' 'context:' 开头分类。只提取有价值的信息，不要废话。"
            }, {
                "role": "user",
                "content": conversation[-2000:]
            }],
            temperature=0.3,
            max_tokens=300,
        )
        text = resp.choices[0].message.content

        memories = []
        for line in text.split("\n"):
            line = line.strip()
            if not line or ":" not in line:
                continue
            category, content = line.split(":", 1)
            category = category.strip()
            content = content.strip()
            if category in ("fact", "preference", "context") and len(content) > 3:
                # 查重
                existing = db.query(Memory).filter(
                    Memory.user_id == user_id,
                    Memory.content == content
                ).first()
                if not existing:
                    mem = Memory(user_id=user_id, content=content, category=category)
                    db.add(mem)
                    memories.append(mem)

        if memories:
            db.commit()
        return memories
    except Exception as e:
        return []


def get_relevant_memories(user_id: str, query: str, db: Session, limit: int = 5) -> list[str]:
    """检索与当前对话相关的记忆"""
    memories = (
        db.query(Memory)
        .filter(Memory.user_id == user_id)
        .order_by(Memory.created_at.desc())
        .limit(limit * 2)
        .all()
    )
    # 简单关键词匹配排序
    scored = []
    for m in memories:
        score = sum(1 for w in query if w in m.content)
        if score > 0:
            scored.append((score, m.content))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [s[1] for s in scored[:limit]]


def format_memories_for_prompt(memories: list[str]) -> str:
    """将记忆格式化为 Prompt"""
    if not memories:
        return ""
    lines = [f"- {m}" for m in memories]
    return "## 关于用户的已知信息\n" + "\n".join(lines)
