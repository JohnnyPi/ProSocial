import hashlib
import time

from django.core.cache import cache


def is_rate_limited(*, key: str, limit: int, window_seconds: int) -> bool:
    cache_key = f"rate_limit:{key}"
    cache.add(cache_key, 0, timeout=window_seconds)
    try:
        attempts = cache.incr(cache_key)
    except ValueError:
        cache.add(cache_key, 0, timeout=window_seconds)
        attempts = cache.incr(cache_key)
    return attempts > limit


def rate_limit_key(prefix: str, identifier: str) -> str:
    digest = hashlib.sha256(identifier.encode()).hexdigest()[:16]
    return f"{prefix}:{digest}:{int(time.time()) // 3600}"
