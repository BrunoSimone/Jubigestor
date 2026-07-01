"""RAG: recupera los chunks relevantes y arma el contexto + las citas para el chat."""

import logging

from jubigestor.config import settings
from jubigestor.db import repository as repo
from jubigestor.llm.base import LLMProvider
from jubigestor.schemas.chat import Source

logger = logging.getLogger(__name__)


async def retrieve(
    provider: LLMProvider, message: str
) -> tuple[str | None, list[Source]]:
    """Embebe la pregunta, busca chunks cercanos y devuelve (contexto, fuentes).

    Devuelve (None, []) si no hay chunks lo bastante cercanos o si la búsqueda falla,
    para que el chat siga respondiendo: el system prompt hace que, sin contexto, el
    modelo derive a ANSES en vez de inventar.
    """
    try:
        (query_embedding,) = await provider.embed(
            [message], task_type="RETRIEVAL_QUERY"
        )
        rows = await repo.search_similar_chunks(
            query_embedding, limit=settings.rag_top_k
        )
    except Exception:
        logger.warning("Retrieve falló; respondo sin contexto.", exc_info=True)
        return None, []

    relevant = [r for r in rows if r["distance"] <= settings.rag_max_distance]
    if not relevant:
        return None, []

    context = "\n\n".join(f'[Fuente: {r["title"]}]\n{r["content"]}' for r in relevant)

    sources: list[Source] = []
    seen: set[str] = set()
    for r in relevant:
        if r["source_url"] in seen:
            continue
        seen.add(r["source_url"])
        sources.append(
            Source(
                title=r["title"],
                url=r["source_url"],
                published_at=r["published_at"],
            )
        )
    return context, sources
