"""缓存层 - Redis + 本地兜底"""
import json, time, hashlib
from app.core.config import settings

# 尝试连接 Redis，失败就用本地字典兜底
_cache_store: dict = {}

try:
    import redis
    _redis = redis.Redis.from_url(settings.REDIS_URL or "redis://localhost:6379", decode_responses=True)
    _redis.ping()
    _use_redis = True
except:
    _use_redis = False


def get_cache(key: str) -> str | None:
    if _use_redis:
        return _redis.get(key)
    val = _cache_store.get(key)
    if val:
        exp_time, data = val
        if time.time() < exp_time:
            return data
        del _cache_store[key]
    return None


def set_cache(key: str, value: str, ttl: int = 300):
    if _use_redis:
        _redis.setex(key, ttl, value)
    else:
        _cache_store[key] = (time.time() + ttl, value)


def tool_cache_key(tool_name: str, args: dict) -> str:
    h = hashlib.md5(json.dumps(args, sort_keys=True).encode()).hexdigest()
    return f"tool:{tool_name}:{h}"
