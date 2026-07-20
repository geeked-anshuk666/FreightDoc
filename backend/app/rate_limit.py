"""Small per-process request limiter for the free-tier deployment.

It intentionally is not presented as a distributed DDoS control. Render should
be paired with an edge/WAF before multi-instance production deployment.
"""

from __future__ import annotations

import asyncio
import time
from collections import defaultdict, deque
from collections.abc import Callable

from fastapi import HTTPException, Request, status

from app.config import get_settings


class InMemoryRateLimiter:
    def __init__(self) -> None:
        self._events: dict[str, deque[float]] = defaultdict(deque)
        self._lock = asyncio.Lock()

    async def check(self, key: str, limit: int) -> None:
        now = time.monotonic()
        window = get_settings().rate_limit_window_seconds
        async with self._lock:
            timestamps = self._events[key]
            cutoff = now - window
            while timestamps and timestamps[0] <= cutoff:
                timestamps.popleft()
            if len(timestamps) >= limit:
                retry_after = max(1, int(window - (now - timestamps[0])))
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail={"code": "RATE_LIMITED", "message": "Too many requests. Please try again shortly."},
                    headers={"Retry-After": str(retry_after)},
                )
            timestamps.append(now)


_limiter = InMemoryRateLimiter()


def _client_key(request: Request, bucket: str) -> str:
    client = request.client.host if request.client else "unknown"
    return f"{bucket}:{client}"


def rate_limit(bucket: str, limit: int) -> Callable:
    async def dependency(request: Request) -> None:
        await _limiter.check(_client_key(request, bucket), limit)

    return dependency
