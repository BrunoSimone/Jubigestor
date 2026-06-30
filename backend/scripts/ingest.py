"""Pipeline de ingesta: carga data/corpus/*.md, los trocea, embebe y guarda en pgvector.

Requiere: DB levantada (make db-up) + esquema (make db-init) + GEMINI_API_KEY.
Uso: make ingest
"""

import asyncio
import logging
from pathlib import Path

from jubigestor.db import close_pool, open_pool
from jubigestor.ingestion.loader import load_corpus
from jubigestor.ingestion.pipeline import ingest_document
from jubigestor.llm import get_provider

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

CORPUS_DIR = Path(__file__).resolve().parent.parent / "data" / "corpus"


async def main() -> None:
    provider = get_provider()
    if provider.name != "gemini":
        raise SystemExit(
            "Sin GEMINI_API_KEY no se pueden generar embeddings. Configurala en backend/.env."
        )

    docs = load_corpus(CORPUS_DIR)
    if not docs:
        raise SystemExit(f"No hay documentos .md en {CORPUS_DIR}. Agregá al menos uno.")

    await open_pool()
    total_chunks = 0
    for doc in docs:
        n = await ingest_document(provider, doc)
        total_chunks += n
        print(f"✅ {doc.title} — {n} chunks  ({doc.source_url})")
    await close_pool()

    print(f"\nIngesta completa: {len(docs)} documento(s), {total_chunks} chunks.")


if __name__ == "__main__":
    asyncio.run(main())
