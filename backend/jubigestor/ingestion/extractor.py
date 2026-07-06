"""Extract text from a PDF into a draft .md to REVIEW before ingesting.

PDF extraction is never perfect (columns, tables, OCR), so the result is a draft:
a human reviews the text and fills in the frontmatter (title, source_url) before
running `make ingest`. The draft frontmatter placeholders are in Spanish because
the person curating the corpus works in Spanish.
"""

import re
from pathlib import Path

from pypdf import PdfReader

_DRAFT_FRONTMATTER = """---
title: TODO — completá el título del documento
source_url: TODO — pegá el link oficial (ANSES, etc.)
published_at: TODO — fecha de última actualización AAAA-MM-DD (o borrá esta línea)
---
"""


def _clean(text: str) -> str:
    """Basic cleanup: normalize line breaks, collapse spaces and blank lines."""
    text = text.replace("\r\n", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def extract_pdf_text(pdf_path: Path) -> str:
    """Return the plain text of a PDF, page by page."""
    reader = PdfReader(str(pdf_path))
    pages = [page.extract_text() or "" for page in reader.pages]
    return _clean("\n\n".join(pages))


def build_draft_md(pdf_path: Path) -> str:
    """Build the draft .md content: frontmatter to fill in + extracted text."""
    return f"{_DRAFT_FRONTMATTER}\n{extract_pdf_text(pdf_path)}\n"
