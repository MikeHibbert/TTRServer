from __future__ import annotations

import time
from typing import Optional
from redis import Redis


def allow_once_per_minute(redis: Optional[Redis], key: str, max_per_minute: int = 1) -> bool:
    """Simple rate limit using Redis TTL. Returns True if allowed, False otherwise."""
    if redis is None:
        return True  # no rate limiting without Redis
    now_bucket = int(time.time() // 60)
    rl_key = f"rate:{key}:{now_bucket}"
    count = redis.incr(rl_key)
    if count == 1:
        redis.expire(rl_key, 60)
    return count <= max_per_minute