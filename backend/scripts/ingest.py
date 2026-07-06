"""Ingestion pipeline: load data/corpus/*.md, chunk, embed and store in pgvector.

Requires: DB up (make db-up) + schema (make db-init) + GEMINI_API_KEY.
Usage: make ingest
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
            "Embeddings need GEMINI_API_KEY. Set it in backend/.env."
        )

    docs = load_corpus(CORPUS_DIR)
    if not docs:
        raise SystemExit(f"No .md documents in {CORPUS_DIR}. Add at least one.")

    await open_pool()
    total_chunks = 0
    for doc in docs:
        n = await ingest_document(provider, doc)
        total_chunks += n
        print(f"OK  {doc.title} — {n} chunks  ({doc.source_url})")
    await close_pool()

    print(f"\nIngestion complete: {len(docs)} document(s), {total_chunks} chunks.")


if __name__ == "__main__":
    asyncio.run(main())
