"""Test the retrieve step: embed a question and show the closest chunks.

Useful to validate semantic search before wiring it into /api/chat.
Usage: make query Q="¿cómo me jubilo si no tengo aportes?"
"""

import asyncio
import sys

from jubigestor.db import close_pool, open_pool
from jubigestor.db import repository as repo
from jubigestor.llm import get_provider

# Example query in Spanish (representative of real user input).
DEFAULT_QUERY = "¿cómo me jubilo si no tengo 30 años de aportes?"


async def main() -> None:
    query = " ".join(sys.argv[1:]).strip() or DEFAULT_QUERY

    provider = get_provider()
    if provider.name != "gemini":
        raise SystemExit("Embedding the query needs GEMINI_API_KEY.")

    await open_pool()
    (embedding,) = await provider.embed([query], task_type="RETRIEVAL_QUERY")
    results = await repo.search_similar_chunks(embedding, limit=3)
    await close_pool()

    print(f'\nQuery: "{query}"\n')
    if not results:
        print("(no results — did you run 'make ingest'?)")
        return
    print("Most relevant chunks (lower distance = closer):\n")
    for i, r in enumerate(results, 1):
        updated = r["published_at"] or "no date"
        print(f"{i}. [dist {r['distance']:.4f}]  {r['content'][:90]}…")
        print(f"   doc: {r['title']}")
        print(f"   url: {r['source_url']}  ·  last updated: {updated}\n")


if __name__ == "__main__":
    asyncio.run(main())
