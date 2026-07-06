"""Extract a PDF into a draft .md in the corpus, to review before ingesting.

Usage: make extract PDF=data/sources/moratoria.pdf
       python scripts/extract_pdf.py <path-to-pdf> [output.md]
"""

import sys
from pathlib import Path

from jubigestor.ingestion.extractor import build_draft_md

CORPUS_DIR = Path(__file__).resolve().parent.parent / "data" / "corpus"


def main() -> None:
    if len(sys.argv) < 2 or not sys.argv[1].strip():
        raise SystemExit("Usage: python scripts/extract_pdf.py <path-to-pdf> [output.md]")

    pdf_path = Path(sys.argv[1]).expanduser()
    if not pdf_path.exists():
        raise SystemExit(f"PDF not found: {pdf_path}")

    out_path = Path(sys.argv[2]) if len(sys.argv) > 2 else CORPUS_DIR / f"{pdf_path.stem}.md"
    if out_path.exists():
        raise SystemExit(f"{out_path} already exists. Delete it or pass another output path.")

    out_path.write_text(build_draft_md(pdf_path), encoding="utf-8")
    print(f"OK  draft written to {out_path}")
    print("REVIEW the extracted text and fill in the frontmatter (title, source_url)")
    print("before running 'make ingest'. PDF extraction is never perfect.")


if __name__ == "__main__":
    main()
