"""End-to-end smoke test of the store: insert chunks with real embeddings and search.

Requires: DB up (make db-up) + schema (make db-init) + GEMINI_API_KEY.
Usage: make db-smoke
"""

import asyncio
from datetime import date

from jubigestor.db import close_pool, open_pool
from jubigestor.db import repository as repo
from jubigestor.llm import get_provider

# Spanish fixtures: representative of the real domain content being embedded.
DOCS = [
    "Para acceder a la jubilación ordinaria se requieren 30 años de aportes y la edad "
    "mínima: 60 años las mujeres y 65 los varones.",
    "La moratoria previsional permite regularizar años de aportes faltantes para poder "
    "acceder a la jubilación.",
    "PAMI es la obra social de los jubilados y pensionados; podés afiliarte al jubilarte.",
    "El haber mínimo jubilatorio se actualiza periódicamente según la ley de movilidad.",
]
QUERY = "¿cuántos años de aportes necesito para jubilarme?"


async def main() -> None:
    await open_pool()
    provider = get_provider()
    print(f"Active LLM provider: {provider.name}\n")

    doc_id = await repo.upsert_document(
        title="Test document — ordinary pension",
        source_url="https://www.anses.gob.ar/jubilacion-ordinaria-test",
        published_at=date(2026, 1, 1),
    )

    doc_embeddings = await provider.embed(DOCS, task_type="RETRIEVAL_DOCUMENT")
    items = [(i, text, emb) for i, (text, emb) in enumerate(zip(DOCS, doc_embeddings))]
    n = await repo.replace_chunks(doc_id, items)
    print(f"Inserted {n} chunks (embeddings of {len(doc_embeddings[0])} dims).\n")

    (query_embedding,) = await provider.embed([QUERY], task_type="RETRIEVAL_QUERY")
    results = await repo.search_similar_chunks(query_embedding, limit=3)

    print(f'Query: "{QUERY}"\n')
    print("Results (lower distance = more relevant):")
    for r in results:
        print(f"  [{r['distance']:.4f}] {r['content'][:75]}…")
        print(f"          source: {r['title']} — {r['source_url']}")

    await close_pool()


if __name__ == "__main__":
    asyncio.run(main())
