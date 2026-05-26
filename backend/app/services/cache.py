"""Redis 缓存工具调用结果"""
import json
import hashlib

# 先用字典模拟 Redis，后续可无痛换成 redis-py
# pip install redis 后改一行即可

_cache: dict[str, tuple[str, float]] = {}
import time


def get_cache(key: str) -> str | None:
    """获取缓存"""
    if key in _cache:
        value, expire_at = _cache[key]
        if time.time() < expire_at:
            return value
        del _cache[key]
    return None


def set_cache(key: str, value: str, ttl: int = 300):
    """写入缓存，默认 5 分钟"""
    _cache[key] = (value, time.time() + ttl)


def tool_cache_key(tool_name: str, args: dict) -> str:
    """生成工具调用的缓存键"""
    raw = f"{tool_name}:{json.dumps(args, sort_keys=True)}"
    return hashlib.md5(raw.encode()).hexdigest()[:16]


# ===== 会话缓存 =====

def cache_session(session_id: str, data: dict, ttl: int = 3600):
    """缓存会话信息"""
    set_cache(f"session:{session_id}", json.dumps(data), ttl)


def get_cached_session(session_id: str) -> dict | None:
    """获取缓存的会话"""
    val = get_cache(f"session:{session_id}")
    return json.loads(val) if val else None
