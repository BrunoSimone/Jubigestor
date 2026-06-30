"""Carga documentos del corpus (archivos .md con frontmatter) a objetos en memoria.

Cada documento vive en data/corpus/*.md con este formato:

    ---
    title: Moratoria previsional
    source_url: https://www.anses.gob.ar/...
    published_at: 2026-01-15
    ---
    <texto del documento>
"""

from dataclasses import dataclass
from datetime import date
from pathlib import Path


@dataclass(frozen=True)
class SourceDocument:
    title: str
    source_url: str
    published_at: date | None
    content: str


def _parse_frontmatter(text: str) -> tuple[dict[str, str], str]:
    if not text.lstrip().startswith("---"):
        raise ValueError("Falta el frontmatter (--- ... ---) al inicio del archivo.")
    # parts: ['', '<frontmatter>', '<body>']
    parts = text.split("---", 2)
    if len(parts) < 3:
        raise ValueError("Frontmatter mal cerrado: faltan los '---' de cierre.")

    meta: dict[str, str] = {}
    for line in parts[1].strip().splitlines():
        if ":" in line:
            key, _, value = line.partition(":")
            meta[key.strip()] = value.strip()
    return meta, parts[2]


def _parse_date(value: str | None) -> date | None:
    return date.fromisoformat(value) if value else None


def load_corpus(corpus_dir: Path) -> list[SourceDocument]:
    """Lee todos los .md del corpus y los devuelve como SourceDocument."""
    documents: list[SourceDocument] = []
    for path in sorted(corpus_dir.glob("*.md")):
        meta, body = _parse_frontmatter(path.read_text(encoding="utf-8"))
        if "title" not in meta or "source_url" not in meta:
            raise ValueError(f"{path.name}: faltan 'title' o 'source_url' en el frontmatter.")
        documents.append(
            SourceDocument(
                title=meta["title"],
                source_url=meta["source_url"],
                published_at=_parse_date(meta.get("published_at")),
                content=body.strip(),
            )
        )
    return documents
