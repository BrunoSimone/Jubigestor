"""Prueba el retrieve: embebe una pregunta y muestra los chunks más parecidos.

Sirve para validar la búsqueda semántica antes de conectarla al /api/chat.
Uso: make query Q="¿cómo me jubilo si no tengo aportes?"
"""

import asyncio
import sys

from jubigestor.db import close_pool, open_pool
from jubigestor.db import repository as repo
from jubigestor.llm import get_provider

DEFAULT_QUERY = "¿cómo me jubilo si no tengo 30 años de aportes?"


async def main() -> None:
    query = " ".join(sys.argv[1:]).strip() or DEFAULT_QUERY

    provider = get_provider()
    if provider.name != "gemini":
        raise SystemExit("Sin GEMINI_API_KEY no se puede embeber la consulta.")

    await open_pool()
    (embedding,) = await provider.embed([query], task_type="RETRIEVAL_QUERY")
    results = await repo.search_similar_chunks(embedding, limit=3)
    await close_pool()

    print(f'\nConsulta: "{query}"\n')
    if not results:
        print("(sin resultados — ¿corriste 'make ingest'?)")
        return
    print("Chunks más relevantes (menor distancia = más parecido):\n")
    for i, r in enumerate(results, 1):
        fecha = r["published_at"] or "sin fecha"
        print(f"{i}. [dist {r['distance']:.4f}]  {r['content'][:90]}…")
        print(f"   📄 {r['title']}")
        print(f"   🔗 {r['source_url']}  ·  última actualización: {fecha}\n")


if __name__ == "__main__":
    asyncio.run(main())
