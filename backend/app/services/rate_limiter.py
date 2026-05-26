"""限流器 - 防止单个用户刷爆额度"""
import time
from collections import defaultdict

# 内存限流：每分钟最多 N 次调用
_rate_limits: dict[str, list[float]] = defaultdict(list)

MAX_CALLS_PER_MINUTE = 30    # 每分钟最多 30 次
MAX_CALLS_PER_HOUR = 500     # 每小时最多 500 次


def check_rate_limit(user_id: str) -> tuple[bool, str]:
    """检查是否超限，返回 (是否放行, 原因)"""
    now = time.time()
    bucket = _rate_limits[user_id]

    # 清理过期记录
    bucket[:] = [t for t in bucket if now - t < 3600]

    # 检查每分钟限制
    recent = [t for t in bucket if now - t < 60]
    if len(recent) >= MAX_CALLS_PER_MINUTE:
        return False, f"每分钟最多 {MAX_CALLS_PER_MINUTE} 次调用"

    # 检查每小时限制
    if len(bucket) >= MAX_CALLS_PER_HOUR:
        return False, f"每小时最多 {MAX_CALLS_PER_HOUR} 次调用"

    # 记录本次调用
    bucket.append(now)
    return True, "ok"


def get_usage(user_id: str) -> dict:
    """获取当前使用情况"""
    now = time.time()
    bucket = _rate_limits.get(user_id, [])
    return {
        "per_minute": len([t for t in bucket if now - t < 60]),
        "per_hour": len([t for t in bucket if now - t < 3600]),
        "limit_per_minute": MAX_CALLS_PER_MINUTE,
        "limit_per_hour": MAX_CALLS_PER_HOUR,
    }
