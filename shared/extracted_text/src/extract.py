#!/usr/bin/env python3
"""Extract text from SLR PDFs to Markdown using PyMuPDF.

Uses direct text extraction for born-digital PDFs (instant).
Flags scanned/image-only PDFs (< 500 chars) for OCR with ocr_extract.py.

PDFs are read from:  p2_systematic_review/s1_slr/05_full_texts/pdfs/
Output goes to:      shared/extracted_text/text/

Usage:
    python extract.py                   # extract all PDFs
    python extract.py --limit 10        # extract first 10 only
    python extract.py --skip-existing   # skip already-extracted
"""

from __future__ import annotations

import argparse
import csv
import re
import time
from datetime import datetime
from pathlib import Path

import fitz  # PyMuPDF — pip install PyMuPDF

# Paths (relative to project root)
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent  # shared/extracted_text/src -> project root
PDF_DIR = PROJECT_ROOT / "p2_systematic_review" / "s1_slr" / "05_full_texts" / "pdfs"
OUT_DIR = SCRIPT_DIR.parent / "text"
LOG_PATH = SCRIPT_DIR.parent / "extraction_log.csv"

MIN_CHAR_THRESHOLD = 500

LOG_COLUMNS = [
    "paper_id", "pdf_file", "md_file",
    "page_count", "char_count", "status", "error", "timestamp",
]


def paper_id_from_filename(filename: str) -> str:
    """Extract paper ID (first segment before underscore)."""
    return filename.split("_", 1)[0]


def load_log(log_path: Path) -> dict[str, dict[str, str]]:
    existing: dict[str, dict[str, str]] = {}
    if log_path.exists():
        with open(log_path, encoding="utf-8", newline="") as f:
            for row in csv.DictReader(f):
                existing[row["paper_id"]] = row
    return existing


def save_log(log_path: Path, rows: dict[str, dict[str, str]]) -> None:
    lines = [",".join(LOG_COLUMNS)]
    for pid in sorted(rows):
        row = rows[pid]
        def _esc(v: str) -> str:
            v = str(v)
            if any(c in v for c in (",", '"', "\n")):
                return '"' + v.replace('"', '""') + '"'
            return v
        lines.append(",".join(_esc(row.get(c, "")) for c in LOG_COLUMNS))
    log_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def clean_text(text: str) -> str:
    """Normalize whitespace and remove excessive blank lines."""
    text = re.sub(r'[ \t]+', ' ', text)
    text = re.sub(r'\n{4,}', '\n\n\n', text)
    text = text.replace("\x00", "")
    return text.strip()


def extract_pdf_text(pdf_path: Path) -> tuple[str, int]:
    """Extract text from a PDF using PyMuPDF. Returns (text, page_count)."""
    doc = fitz.open(str(pdf_path))
    page_count = len(doc)
    pages = [page.get_text("text") for page in doc]
    doc.close()
    return clean_text("\n\n".join(pages)), page_count


def remove_header_pollution(text: str, threshold: int = 8) -> str:
    """Remove lines repeated more than `threshold` times (headers/footers)."""
    from collections import Counter
    lines = text.split("\n")
    counts = Counter(l.strip() for l in lines if len(l.strip()) > 15)
    repeated = {line for line, count in counts.items() if count > threshold}
    if not repeated:
        return text
    cleaned = [l for l in lines if l.strip() not in repeated]
    return re.sub(r'\n{4,}', '\n\n\n', "\n".join(cleaned))


def main():
    parser = argparse.ArgumentParser(description="Extract text from SLR PDFs")
    parser.add_argument("--limit", type=int, help="Max PDFs to process")
    parser.add_argument("--skip-existing", action="store_true",
                        help="Skip papers already in the log with status=success")
    args = parser.parse_args()

    if not PDF_DIR.exists():
        print(f"ERROR: PDF directory not found: {PDF_DIR}")
        print(f"  Expected: p2_systematic_review/s1_slr/05_full_texts/pdfs/")
        return

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    pdfs = sorted(PDF_DIR.glob("*.pdf"))
    if args.limit:
        pdfs = pdfs[:args.limit]

    existing = load_log(LOG_PATH) if args.skip_existing else {}
    done_count = sum(1 for r in existing.values() if r.get("status") == "success")

    print(f"{'='*60}")
    print(f"  PDF source:  {PDF_DIR}")
    print(f"  Output:      {OUT_DIR}")
    print(f"  PDFs found:  {len(pdfs)}")
    if args.skip_existing:
        print(f"  Already done: {done_count}")
    print(f"{'='*60}\n")

    t_start = time.time()
    extracted = flagged = errors = 0
    log_rows = load_log(LOG_PATH)

    for i, pdf_path in enumerate(pdfs):
        paper_id = paper_id_from_filename(pdf_path.name)

        if args.skip_existing and paper_id in existing and existing[paper_id].get("status") == "success":
            continue

        stem = pdf_path.stem
        md_name = f"{stem}.md"
        md_path = OUT_DIR / md_name

        row = {
            "paper_id": paper_id,
            "pdf_file": pdf_path.name,
            "md_file": md_name,
            "page_count": 0,
            "char_count": 0,
            "status": "error",
            "error": "",
            "timestamp": datetime.now().isoformat(timespec="seconds"),
        }

        try:
            text, page_count = extract_pdf_text(pdf_path)
            text = remove_header_pollution(text)
            row["page_count"] = page_count
            row["char_count"] = len(text)

            if len(text) < MIN_CHAR_THRESHOLD:
                row["status"] = "flagged"
                row["error"] = f"char_count={len(text)} < {MIN_CHAR_THRESHOLD} (scanned PDF, run ocr_extract.py)"
                flagged += 1
            else:
                md_path.write_text(text, encoding="utf-8")
                row["status"] = "success"
                extracted += 1

        except Exception as e:
            row["status"] = "error"
            row["error"] = str(e)[:200]
            errors += 1

        log_rows[paper_id] = row
        total = done_count + extracted + flagged + errors
        elapsed = time.time() - t_start
        print(f"  [{total}/{len(pdfs)}] {row['status']:7s} "
              f"{row['char_count']:>6} chars  {pdf_path.name[:60]}  ({elapsed:.1f}s)")

    save_log(LOG_PATH, log_rows)
    elapsed = time.time() - t_start

    print(f"\n{'='*60}")
    print(f"  Done in {elapsed:.1f}s")
    print(f"  Extracted: {extracted}  |  Flagged (need OCR): {flagged}  |  Errors: {errors}")
    if flagged > 0:
        print(f"  Run:  python ocr_extract.py  to OCR flagged papers")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
