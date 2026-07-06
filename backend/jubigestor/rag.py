"""RAG: retrieve the relevant chunks and build the context + citations for the chat."""

import logging

from jubigestor.config import settings
from jubigestor.db import repository as repo
from jubigestor.llm.base import LLMProvider
from jubigestor.schemas.chat import Source

logger = logging.getLogger(__name__)


async def retrieve(
    provider: LLMProvider, message: str
) -> tuple[str | None, list[Source]]:
    """Embed the question, find nearby chunks and return (context, sources).

    Returns (None, []) when there are no close-enough chunks or the search fails,
    so the chat keeps answering: without context, the system prompt makes the
    model defer to ANSES instead of making things up.
    """
    try:
        (query_embedding,) = await provider.embed(
            [message], task_type="RETRIEVAL_QUERY"
        )
        rows = await repo.search_similar_chunks(
            query_embedding, limit=settings.rag_top_k
        )
    except Exception:
        logger.warning("Retrieve failed; answering without context.", exc_info=True)
        return None, []

    relevant = [r for r in rows if r["distance"] <= settings.rag_max_distance]
    if not relevant:
        return None, []

    # LLM-facing context. The "Fuente" label stays Spanish to match the prompt.
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
