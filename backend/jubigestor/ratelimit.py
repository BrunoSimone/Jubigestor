"""Rate limiting simple en memoria, por IP (ventana deslizante).

Para un despliegue de una sola instancia (Render free) alcanza y no agrega
dependencias. Si algún día escalás a varias instancias, migrar a Redis.
"""

import time
from collections import defaultdict, deque

from fastapi import HTTPException, Request

from jubigestor.config import settings

# IP -> timestamps (monotónicos) de las consultas dentro de la ventana.
_hits: dict[str, deque[float]] = defaultdict(deque)


def _client_ip(request: Request) -> str:
    # Detrás de un proxy (Render), la IP real viene en X-Forwarded-For.
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


async def rate_limit(request: Request) -> None:
    """Dependencia de FastAPI: corta con 429 si la IP superó el límite."""
    now = time.monotonic()
    window = settings.rate_limit_window_seconds
    limit = settings.rate_limit_requests

    bucket = _hits[_client_ip(request)]
    # Descarta los hits fuera de la ventana.
    while bucket and bucket[0] <= now - window:
        bucket.popleft()

    if len(bucket) >= limit:
        retry_after = int(window - (now - bucket[0])) + 1
        raise HTTPException(
            status_code=429,
            detail="Demasiadas consultas seguidas. Esperá unos segundos e intentá de nuevo.",
            headers={"Retry-After": str(retry_after)},
        )

    bucket.append(now)
