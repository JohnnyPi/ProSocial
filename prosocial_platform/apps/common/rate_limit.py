import hashlib
import time

from django.core.cache import cache


def is_rate_limited(*, key: str, limit: int, window_seconds: int) -> bool:
    cache_key = f"rate_limit:{key}"
    attempts = cache.get(cache_key, 0)
    if attempts >= limit:
        return True
    cache.set(cache_key, attempts + 1, timeout=window_seconds)
    return False


def rate_limit_key(prefix: str, identifier: str) -> str:
    digest = hashlib.sha256(identifier.encode()).hexdigest()[:16]
    return f"{prefix}:{digest}:{int(time.time()) // 3600}"
