"""Convert a framework paper's PDF to Markdown using PyMuPDF.

Reuses the extraction logic from shared/extracted_text/src/extract.py.
Keeps the PDF alongside the .md so either can be consulted.

Usage:
    python -m p3_thematic_synthesis.s3_quantum_advantage._shared.pdf_to_md \
        <pdf_path> <out_md_path>
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


def _clean(text: str) -> str:
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{4,}", "\n\n\n", text)
    return text.replace("\x00", "").strip()


def _remove_header_pollution(text: str, threshold: int = 8) -> str:
    from collections import Counter
    lines = text.split("\n")
    counts = Counter(l.strip() for l in lines if len(l.strip()) > 15)
    repeated = {line for line, c in counts.items() if c > threshold}
    if not repeated:
        return text
    cleaned = [l for l in lines if l.strip() not in repeated]
    return re.sub(r"\n{4,}", "\n\n\n", "\n".join(cleaned))


def pdf_to_markdown(pdf_path: Path) -> tuple[str, int]:
    try:
        import fitz  # PyMuPDF
    except ImportError as e:
        raise SystemExit(
            "PyMuPDF (fitz) not installed. Install with: pip install PyMuPDF"
        ) from e
    doc = fitz.open(str(pdf_path))
    pages = [page.get_text("text") for page in doc]
    page_count = len(doc)
    doc.close()
    text = _clean("\n\n".join(pages))
    text = _remove_header_pollution(text)
    return text, page_count


def main():
    parser = argparse.ArgumentParser(description="Convert a PDF to Markdown.")
    parser.add_argument("pdf", type=Path)
    parser.add_argument("out", type=Path)
    args = parser.parse_args()

    if not args.pdf.is_file():
        print(f"ERROR: PDF not found: {args.pdf}", file=sys.stderr)
        sys.exit(1)

    text, page_count = pdf_to_markdown(args.pdf)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(text, encoding="utf-8")
    print(f"Wrote {args.out} ({page_count} pages, {len(text):,} chars)")


if __name__ == "__main__":
    main()
