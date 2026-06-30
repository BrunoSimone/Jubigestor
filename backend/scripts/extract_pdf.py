"""Extrae un PDF a un borrador .md en el corpus, para revisar antes de ingestar.

Uso: make extract PDF=data/sources/moratoria.pdf
     python scripts/extract_pdf.py <ruta-al-pdf> [salida.md]
"""

import sys
from pathlib import Path

from jubigestor.ingestion.extractor import build_draft_md

CORPUS_DIR = Path(__file__).resolve().parent.parent / "data" / "corpus"


def main() -> None:
    if len(sys.argv) < 2 or not sys.argv[1].strip():
        raise SystemExit("Uso: python scripts/extract_pdf.py <ruta-al-pdf> [salida.md]")

    pdf_path = Path(sys.argv[1]).expanduser()
    if not pdf_path.exists():
        raise SystemExit(f"No existe el PDF: {pdf_path}")

    out_path = Path(sys.argv[2]) if len(sys.argv) > 2 else CORPUS_DIR / f"{pdf_path.stem}.md"
    if out_path.exists():
        raise SystemExit(f"Ya existe {out_path}. Borralo o pasá otra ruta de salida.")

    out_path.write_text(build_draft_md(pdf_path), encoding="utf-8")
    print(f"✅ Borrador escrito en {out_path}")
    print("⚠️  REVISÁ el texto extraído y completá el frontmatter (title, source_url)")
    print("    antes de correr 'make ingest'. La extracción de PDF nunca es perfecta.")


if __name__ == "__main__":
    main()
