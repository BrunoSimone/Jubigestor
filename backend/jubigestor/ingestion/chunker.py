"""Split text into chunks with the recursive splitter (structure-aware).

It tries to split on paragraphs first, then sentences, then words: cuts land in
natural places instead of breaking sentences in half.
"""

from langchain_text_splitters import RecursiveCharacterTextSplitter

from jubigestor.config import settings

# Preferred split order. For Argentine regulations we can tune custom separators
# (e.g. "\nArtículo", "\nInciso") if retrieval quality is weak.
_SEPARATORS = ["\n\n", "\n", ". ", " ", ""]


def chunk_text(text: str) -> list[str]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
        separators=_SEPARATORS,
        keep_separator=True,
    )
    return [chunk.strip() for chunk in splitter.split_text(text) if chunk.strip()]
