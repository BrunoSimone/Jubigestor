"""Simple in-memory, per-IP rate limiting (sliding window).

Good enough for a single-instance deployment (Render free) with no extra
dependencies. Migrate to Redis if this ever scales to multiple instances.
"""

import time
from collections import defaultdict, deque

from fastapi import HTTPException, Request

from jubigestor.config import settings

# IP -> monotonic timestamps of the requests inside the window.
_hits: dict[str, deque[float]] = defaultdict(deque)


def _client_ip(request: Request) -> str:
    # Behind a proxy (Render), the real IP comes in X-Forwarded-For.
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


async def rate_limit(request: Request) -> None:
    """FastAPI dependency: raises 429 when the IP exceeds the limit."""
    now = time.monotonic()
    window = settings.rate_limit_window_seconds
    limit = settings.rate_limit_requests

    bucket = _hits[_client_ip(request)]
    # Drop hits that fell outside the window.
    while bucket and bucket[0] <= now - window:
        bucket.popleft()

    if len(bucket) >= limit:
        retry_after = int(window - (now - bucket[0])) + 1
        raise HTTPException(
            status_code=429,
            # User-facing message (shown in the chat).
            detail="Demasiadas consultas seguidas. Esperá unos segundos e intentá de nuevo.",
            headers={"Retry-After": str(retry_after)},
        )

    bucket.append(now)
