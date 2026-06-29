"""Aplica el esquema SQL a la base. Idempotente. Uso: make db-init"""

import asyncio
from pathlib import Path

import psycopg

from jubigestor.config import settings

SCHEMA = Path(__file__).resolve().parent.parent / "jubigestor" / "db" / "schema.sql"


async def main() -> None:
    if not settings.database_url:
        raise SystemExit("DATABASE_URL no configurada. Levantá la DB (make db-up).")

    statements = [s.strip() for s in SCHEMA.read_text().split(";") if s.strip()]
    async with await psycopg.AsyncConnection.connect(
        settings.database_url, autocommit=True
    ) as conn:
        for stmt in statements:
            await conn.execute(stmt)

    print(f"✅ Esquema aplicado ({len(statements)} sentencias).")


if __name__ == "__main__":
    asyncio.run(main())
