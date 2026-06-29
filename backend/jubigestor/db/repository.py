"""Acceso a datos: documentos y chunks. SQL crudo sobre psycopg (async)."""

from collections.abc import Sequence
from datetime import date
from uuid import UUID

from psycopg.rows import dict_row

from jubigestor.db import get_pool

# (chunk_index, content, embedding)
ChunkInput = tuple[int, str, Sequence[float]]


def _vector(embedding: Sequence[float]) -> str:
    """Formatea el embedding como literal de pgvector: '[0.1,0.2,...]'.

    Se combina con un cast `%s::vector` en el SQL. Asi el operador `<=>` recibe
    un `vector` y no un `double precision[]` (que no tiene operador de distancia).
    """
    return "[" + ",".join(map(str, embedding)) + "]"


async def upsert_document(
    *, title: str, source_url: str, published_at: date | None = None
) -> UUID:
    """Crea o actualiza un documento (idempotente por source_url). Devuelve su id."""
    pool = get_pool()
    async with pool.connection() as conn, conn.cursor() as cur:
        await cur.execute(
            """
            INSERT INTO documents (title, source_url, published_at, updated_at)
            VALUES (%s, %s, %s, now())
            ON CONFLICT (source_url) DO UPDATE
               SET title = EXCLUDED.title,
                   published_at = EXCLUDED.published_at,
                   updated_at = now()
            RETURNING id
            """,
            (title, source_url, published_at),
        )
        row = await cur.fetchone()
        return row[0]


async def replace_chunks(document_id: UUID, chunks: Sequence[ChunkInput]) -> int:
    """Reemplaza TODOS los chunks de un documento (borra + inserta, en una transaccion)."""
    pool = get_pool()
    async with pool.connection() as conn, conn.cursor() as cur:
        await cur.execute("DELETE FROM chunks WHERE document_id = %s", (document_id,))
        await cur.executemany(
            """
            INSERT INTO chunks (document_id, chunk_index, content, embedding)
            VALUES (%s, %s, %s, %s::vector)
            """,
            [(document_id, idx, content, _vector(emb)) for idx, content, emb in chunks],
        )
        return len(chunks)


async def search_similar_chunks(
    embedding: Sequence[float], *, limit: int = 5
) -> list[dict]:
    """Devuelve los `limit` chunks mas parecidos al embedding, con su cita (JOIN a documents)."""
    pool = get_pool()
    async with pool.connection() as conn, conn.cursor(row_factory=dict_row) as cur:
        await cur.execute(
            """
            SELECT c.content,
                   c.chunk_index,
                   d.title,
                   d.source_url,
                   d.published_at,
                   c.embedding <=> %s::vector AS distance
            FROM chunks c
            JOIN documents d ON d.id = c.document_id
            ORDER BY c.embedding <=> %s::vector
            LIMIT %s
            """,
            (_vector(embedding), _vector(embedding), limit),
        )
        return await cur.fetchall()
