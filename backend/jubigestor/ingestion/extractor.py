"""Extrae texto de un PDF a un borrador .md para REVISAR antes de ingestar.

La extracción de PDF nunca es perfecta (columnas, tablas, OCR). Por eso el
resultado es un borrador: el humano revisa el texto y completa el frontmatter
(title, source_url) antes de correr `make ingest`.
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
    """Limpieza básica: normaliza saltos, colapsa espacios y líneas en blanco."""
    text = text.replace("\r\n", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def extract_pdf_text(pdf_path: Path) -> str:
    """Devuelve el texto plano de un PDF, página por página."""
    reader = PdfReader(str(pdf_path))
    pages = [page.extract_text() or "" for page in reader.pages]
    return _clean("\n\n".join(pages))


def build_draft_md(pdf_path: Path) -> str:
    """Arma el contenido del borrador .md: frontmatter a completar + texto extraído."""
    return f"{_DRAFT_FRONTMATTER}\n{extract_pdf_text(pdf_path)}\n"
