"""Orchestrates ingestion: document -> upsert -> chunk -> embed -> store chunks."""

import logging

from jubigestor.config import settings
from jubigestor.db import repository as repo
from jubigestor.ingestion.chunker import chunk_text
from jubigestor.ingestion.loader import SourceDocument
from jubigestor.llm.base import LLMProvider

logger = logging.getLogger(__name__)


async def _embed_in_batches(provider: LLMProvider, chunks: list[str]) -> list[list[float]]:
    """Embed in batches to stay under the API limit on large documents."""
    embeddings: list[list[float]] = []
    batch_size = settings.embed_batch_size
    for start in range(0, len(chunks), batch_size):
        batch = chunks[start : start + batch_size]
        embeddings.extend(await provider.embed(batch, task_type="RETRIEVAL_DOCUMENT"))
    return embeddings


async def ingest_document(provider: LLMProvider, doc: SourceDocument) -> int:
    """Process a full document and return how many chunks were stored."""
    document_id = await repo.upsert_document(
        title=doc.title,
        source_url=doc.source_url,
        published_at=doc.published_at,
    )

    chunks = chunk_text(doc.content)
    if not chunks:
        logger.warning("Document with no usable content: %s", doc.title)
        return 0

    embeddings = await _embed_in_batches(provider, chunks)
    items = [(i, content, emb) for i, (content, emb) in enumerate(zip(chunks, embeddings))]
    return await repo.replace_chunks(document_id, items)
