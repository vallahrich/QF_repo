#!/usr/bin/env python3
"""OCR scanned PDFs that failed text extraction (flagged in extraction_log.csv).

Uses easyocr for born-digital PDFs with scanned pages.
Supports Chinese (ch_sim) and English models.

PDFs are read from:  p2_systematic_review/s1_slr/05_full_texts/pdfs/
Output goes to:      shared/extracted_text/text/

Usage:
    python ocr_extract.py                # OCR all flagged PDFs
    python ocr_extract.py --lang ch_sim  # use Chinese+English model for CJK papers
"""

from __future__ import annotations

import argparse
import csv
import sys
import time
from datetime import datetime
from pathlib import Path

import easyocr
import fitz  # PyMuPDF

sys.stdout.reconfigure(encoding="utf-8")

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent
PDF_DIR = PROJECT_ROOT / "p2_systematic_review" / "s1_slr" / "05_full_texts" / "pdfs"
OUT_DIR = SCRIPT_DIR.parent / "text"
LOG_PATH = SCRIPT_DIR.parent / "extraction_log.csv"

MIN_CHAR_THRESHOLD = 200

LOG_COLUMNS = [
    "paper_id", "pdf_file", "md_file",
    "page_count", "char_count", "status", "error", "timestamp",
]


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


def ocr_pdf(pdf_path: Path, reader: easyocr.Reader) -> tuple[str, int]:
    """OCR a scanned PDF page by page. Returns (text, page_count)."""
    doc = fitz.open(str(pdf_path))
    page_count = len(doc)
    all_text = []
    for page_num, page in enumerate(doc):
        try:
            mat = fitz.Matrix(150 / 72, 150 / 72)
            pix = page.get_pixmap(matrix=mat)
            img_bytes = pix.tobytes("png")
            del pix
            results = reader.readtext(img_bytes, detail=0, paragraph=True)
            del img_bytes
            page_text = "\n".join(results)
            all_text.append(page_text)
            print(f"    page {page_num+1}/{page_count}: {len(page_text)} chars", flush=True)
        except Exception as e:
            print(f"    page {page_num+1}/{page_count}: ERROR - {e}", flush=True)
            all_text.append("")
    doc.close()
    return "\n\n".join(all_text), page_count


def main():
    parser = argparse.ArgumentParser(description="OCR flagged scanned PDFs")
    parser.add_argument("--lang", nargs="+", default=["en"],
                        help="EasyOCR language codes (default: en). Use 'ch_sim en' for Chinese papers")
    parser.add_argument("--paper", type=str, help="Process a specific PDF filename")
    args = parser.parse_args()

    if not PDF_DIR.exists():
        print(f"ERROR: PDF directory not found: {PDF_DIR}")
        return

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    log_rows = load_log(LOG_PATH)

    # Find flagged papers
    if args.paper:
        flagged_files = [args.paper]
    else:
        flagged_files = [
            row["pdf_file"] for row in log_rows.values()
            if row.get("status") == "flagged"
        ]

    if not flagged_files:
        print("No flagged papers to OCR.")
        return

    print(f"Found {len(flagged_files)} papers to OCR")
    print(f"Language model: {args.lang}")
    print(f"Loading easyocr model...")

    reader = easyocr.Reader(args.lang, gpu=False)
    print("Model loaded.\n")

    t_start = time.time()
    success = failed = 0

    for i, pdf_name in enumerate(sorted(flagged_files)):
        pdf_path = PDF_DIR / pdf_name
        if not pdf_path.exists():
            print(f"[{i+1}/{len(flagged_files)}] SKIP: {pdf_name} not found")
            continue

        print(f"[{i+1}/{len(flagged_files)}] {pdf_name[:60]}")

        paper_id = pdf_name.split("_", 1)[0]
        md_name = pdf_path.stem + ".md"
        md_path = OUT_DIR / md_name

        # Skip if already extracted successfully
        if md_path.exists() and md_path.stat().st_size > MIN_CHAR_THRESHOLD:
            print(f"  SKIP: already extracted ({md_path.stat().st_size} bytes)")
            continue

        try:
            t0 = time.time()
            text, page_count = ocr_pdf(pdf_path, reader)
            elapsed = time.time() - t0

            status = "success" if len(text) >= MIN_CHAR_THRESHOLD else "flagged"
            if status == "success":
                md_path.write_text(text, encoding="utf-8")
                success += 1
            else:
                failed += 1

            log_rows[paper_id] = {
                "paper_id": paper_id,
                "pdf_file": pdf_name,
                "md_file": md_name,
                "page_count": str(page_count),
                "char_count": str(len(text)),
                "status": status,
                "error": "" if status == "success" else f"OCR: only {len(text)} chars",
                "timestamp": datetime.now().isoformat(timespec="seconds"),
            }
            print(f"  Done: {len(text)} chars, {page_count} pages, {elapsed:.1f}s -> {status}")

        except Exception as e:
            print(f"  ERROR: {e}")
            failed += 1

    save_log(LOG_PATH, log_rows)
    total_time = time.time() - t_start
    print(f"\n{'='*60}")
    print(f"  OCR Complete: {success} success, {failed} failed in {total_time/60:.1f} min")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
