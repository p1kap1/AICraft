from sqlalchemy.orm import Session
from openai import OpenAI, APIError, APITimeoutError, RateLimitError
from app.models.billing import UserCredit
from app.models.platform_provider import PlatformProvider
import time, random

def charge_platform_usage(user_id: str, provider_id: str, tokens: int, db: Session) -> dict:
    provider = db.query(PlatformProvider).filter(PlatformProvider.id == provider_id).first()
    if not provider: return {"success": False, "error": "provider not found"}
    cost = (tokens / 1000) * provider.price_per_1k_tokens
    credit = db.query(UserCredit).filter(UserCredit.user_id == user_id).first()
    if not credit: credit = UserCredit(user_id=user_id, balance=0); db.add(credit)
    if credit.balance < cost: return {"success": False, "error": "余额不足", "balance": credit.balance, "cost": cost}
    credit.balance -= cost; credit.total_used += cost; db.commit()
    return {"success": True, "balance": credit.balance, "cost": cost}


def get_available_models(db: Session) -> list[dict]:
    """返回去重后的可用模型列表（用户看到的），同模型多个 Key 只显示一个"""
    providers = db.query(PlatformProvider).filter(PlatformProvider.enabled == True).all()
    seen = {}
    for p in providers:
        if p.model not in seen:
            seen[p.model] = p
    return [{"id": p.id, "name": p.name, "model": p.model, "price": p.price_per_1k_tokens} for p in seen.values()]


def get_providers_for_model(model: str, db: Session) -> list[dict]:
    """获取指定模型的所有 Key（用于故障转移）"""
    providers = db.query(PlatformProvider).filter(PlatformProvider.enabled == True).all()
    matches = [p for p in providers if p.model == model]
    # 随机打乱防止总是第一个 Key 扛所有流量
    random.shuffle(matches)
    return [{"id": p.id, "base_url": p.base_url, "api_key": p.api_key, "model": p.model, "price": p.price_per_1k_tokens} for p in matches]


def call_with_failover(providers: list[dict], messages: list[dict], tools: list[dict] = None):
    """带故障转移的 LLM 调用"""
    last_error = None
    for p in providers:
        try:
            client = OpenAI(api_key=p["api_key"], base_url=p["base_url"], timeout=30)
            kwargs = {"model": p["model"], "messages": messages}
            if tools: kwargs["tools"] = tools; kwargs["tool_choice"] = "auto"
            return client.chat.completions.create(**kwargs), p
        except (RateLimitError, APITimeoutError):
            last_error = f"{p['id'][:8]}: 限流/超时"; time.sleep(1)
        except APIError as e:
            last_error = f"{p['id'][:8]}: APIError({e.status_code})"
        except Exception as e:
            last_error = f"{p['id'][:8]}: {str(e)[:40]}"
    raise Exception(f"所有 Key 均失败: {last_error}")
