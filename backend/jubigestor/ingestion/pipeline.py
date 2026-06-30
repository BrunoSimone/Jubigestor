"""Orquesta la ingesta: documento -> upsert -> chunk -> embed -> guardar chunks."""

import logging

from jubigestor.config import settings
from jubigestor.db import repository as repo
from jubigestor.ingestion.chunker import chunk_text
from jubigestor.ingestion.loader import SourceDocument
from jubigestor.llm.base import LLMProvider

logger = logging.getLogger(__name__)


async def _embed_in_batches(provider: LLMProvider, chunks: list[str]) -> list[list[float]]:
    """Embebe en lotes para no pasarnos del límite de la API en documentos grandes."""
    embeddings: list[list[float]] = []
    batch_size = settings.embed_batch_size
    for start in range(0, len(chunks), batch_size):
        batch = chunks[start : start + batch_size]
        embeddings.extend(await provider.embed(batch, task_type="RETRIEVAL_DOCUMENT"))
    return embeddings


async def ingest_document(provider: LLMProvider, doc: SourceDocument) -> int:
    """Procesa un documento completo y devuelve cuántos chunks quedaron guardados."""
    document_id = await repo.upsert_document(
        title=doc.title,
        source_url=doc.source_url,
        published_at=doc.published_at,
    )

    chunks = chunk_text(doc.content)
    if not chunks:
        logger.warning("Documento sin contenido aprovechable: %s", doc.title)
        return 0

    embeddings = await _embed_in_batches(provider, chunks)
    items = [(i, content, emb) for i, (content, emb) in enumerate(zip(chunks, embeddings))]
    return await repo.replace_chunks(document_id, items)
