import logging

from pgvector.psycopg import register_vector_async
from psycopg_pool import AsyncConnectionPool

from jubigestor.config import settings

logger = logging.getLogger(__name__)

_pool: AsyncConnectionPool | None = None


async def _configure(conn) -> None:
    """Runs for every pooled connection: enables the `vector` type in psycopg."""
    try:
        await register_vector_async(conn)
    except Exception:
        # The `vector` extension may not exist yet (before `make db-init`).
        logger.warning("Could not register the 'vector' type. Did you run 'make db-init'?")


def get_pool() -> AsyncConnectionPool:
    """Return the connection pool (created lazily)."""
    global _pool
    if _pool is None:
        if not settings.database_url:
            raise RuntimeError(
                "DATABASE_URL is not set. Start the DB (make db-up) "
                "and set DATABASE_URL in .env."
            )
        _pool = AsyncConnectionPool(
            settings.database_url,
            open=False,
            configure=_configure,
            # Validate connections on checkout and replace dead ones transparently.
            # Needed because Neon suspends on idle and kills open connections.
            check=AsyncConnectionPool.check_connection,
            min_size=1,
            max_size=5,
        )
    return _pool


async def open_pool() -> None:
    """Open the pool if a DB is configured. Otherwise no-op (the app stays alive)."""
    if not settings.database_url:
        logger.warning("No DATABASE_URL: chat works, but without RAG.")
        return
    pool = get_pool()
    await pool.open()
    await pool.wait()


async def close_pool() -> None:
    global _pool
    if _pool is not None:
        await _pool.close()
        _pool = None
