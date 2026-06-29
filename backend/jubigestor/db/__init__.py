import logging

from pgvector.psycopg import register_vector_async
from psycopg_pool import AsyncConnectionPool

from jubigestor.config import settings

logger = logging.getLogger(__name__)

_pool: AsyncConnectionPool | None = None


async def _configure(conn) -> None:
    """Se corre por cada conexion del pool: habilita el tipo `vector` en psycopg."""
    try:
        await register_vector_async(conn)
    except Exception:
        # La extension `vector` puede no existir todavia (antes de `make db-init`).
        logger.warning(
            "No pude registrar el tipo 'vector'. ¿Corriste 'make db-init'?"
        )


def get_pool() -> AsyncConnectionPool:
    """Devuelve el pool de conexiones (lo crea perezosamente)."""
    global _pool
    if _pool is None:
        if not settings.database_url:
            raise RuntimeError(
                "DATABASE_URL no configurada. Levantá la DB (make db-up) "
                "y poné DATABASE_URL en el .env."
            )
        _pool = AsyncConnectionPool(
            settings.database_url,
            open=False,
            configure=_configure,
            min_size=1,
            max_size=5,
        )
    return _pool


async def open_pool() -> None:
    """Abre el pool si hay DB configurada. Si no, no hace nada (la app sigue viva)."""
    if not settings.database_url:
        logger.warning("Sin DATABASE_URL: el chat funciona, pero sin RAG.")
        return
    pool = get_pool()
    await pool.open()
    await pool.wait()


async def close_pool() -> None:
    global _pool
    if _pool is not None:
        await _pool.close()
        _pool = None
