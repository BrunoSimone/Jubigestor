"""Load corpus documents (.md files with frontmatter) into in-memory objects.

Each document lives in data/corpus/*.md with this format:

    ---
    title: Moratoria previsional
    source_url: https://www.anses.gob.ar/...
    published_at: 2026-01-15
    ---
    <document text>
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
        raise ValueError("Missing frontmatter (--- ... ---) at the start of the file.")
    # parts: ['', '<frontmatter>', '<body>']
    parts = text.split("---", 2)
    if len(parts) < 3:
        raise ValueError("Malformed frontmatter: missing the closing '---'.")

    meta: dict[str, str] = {}
    for line in parts[1].strip().splitlines():
        if ":" in line:
            key, _, value = line.partition(":")
            meta[key.strip()] = value.strip()
    return meta, parts[2]


def _parse_date(value: str | None) -> date | None:
    return date.fromisoformat(value) if value else None


def load_corpus(corpus_dir: Path) -> list[SourceDocument]:
    """Read every .md in the corpus and return them as SourceDocument."""
    documents: list[SourceDocument] = []
    for path in sorted(corpus_dir.glob("*.md")):
        meta, body = _parse_frontmatter(path.read_text(encoding="utf-8"))
        if "title" not in meta or "source_url" not in meta:
            raise ValueError(f"{path.name}: missing 'title' or 'source_url' in frontmatter.")
        documents.append(
            SourceDocument(
                title=meta["title"],
                source_url=meta["source_url"],
                published_at=_parse_date(meta.get("published_at")),
                content=body.strip(),
            )
        )
    return documents
