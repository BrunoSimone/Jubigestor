"""Trocea texto en chunks usando el splitter recursivo (respeta la estructura).

Intenta cortar primero por párrafos, luego oraciones, luego palabras: los cortes
caen en lugares naturales y no parten frases por la mitad.
"""

from langchain_text_splitters import RecursiveCharacterTextSplitter

from jubigestor.config import settings

# Orden de preferencia de corte. Para normativa argentina se pueden afinar
# separadores propios (p. ej. "\nArtículo", "\nInciso") si el retrieve sale flojo.
_SEPARATORS = ["\n\n", "\n", ". ", " ", ""]


def chunk_text(text: str) -> list[str]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
        separators=_SEPARATORS,
        keep_separator=True,
    )
    return [chunk.strip() for chunk in splitter.split_text(text) if chunk.strip()]
