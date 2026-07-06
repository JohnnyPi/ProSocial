import threading

import pytest
from django.core.cache import cache

from apps.common.rate_limit import is_rate_limited


@pytest.fixture(autouse=True)
def clear_cache():
    cache.clear()
    yield
    cache.clear()


@pytest.mark.django_db
def test_rate_limit_blocks_after_limit():
    key = "test-key"
    for _ in range(3):
        assert is_rate_limited(key=key, limit=3, window_seconds=60) is False
    assert is_rate_limited(key=key, limit=3, window_seconds=60) is True


@pytest.mark.django_db
def test_rate_limit_atomic_under_concurrency():
    key = "concurrent-key"
    limit = 5
    successes = []

    def attempt():
        if not is_rate_limited(key=key, limit=limit, window_seconds=60):
            successes.append(1)

    threads = [threading.Thread(target=attempt) for _ in range(10)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    assert len(successes) == limit
