#!/usr/bin/env python3
"""Generate Excel review workbook from Phase 1 extraction JSONs.

Creates a workbook with:
- Dashboard sheet: overview of all papers with status columns
- One sheet per paper: extraction data laid out for review with annotation columns

Usage:
    python -m p1_framework_synthesis.scripts.build_review_workbook
    python -m p1_framework_synthesis.scripts.build_review_workbook --output p1_framework_synthesis/s2_coding/review.xlsx
"""

import argparse
import json
import os
import sys
from pathlib import Path

_PROJECT_ROOT = str(Path(__file__).resolve().parents[2])
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

PHASE1_ROOT = str(Path(__file__).resolve().parents[1])
EXTRACTIONS_DIR = os.path.join(PHASE1_ROOT, "s1_extractions")
DEFAULT_OUTPUT = os.path.join(PHASE1_ROOT, "s2_coding", "review_workbook.xlsx")

# Styles
HEADER_FONT = Font(bold=True, size=11, color="FFFFFF")
HEADER_FILL = PatternFill(start_color="2F5496", end_color="2F5496", fill_type="solid")
SECTION_FONT = Font(bold=True, size=11, color="2F5496")
SECTION_FILL = PatternFill(start_color="D6E4F0", end_color="D6E4F0", fill_type="solid")
OK_FILL = PatternFill(start_color="C6EFCE", end_color="C6EFCE", fill_type="solid")
WARN_FILL = PatternFill(start_color="FFEB9C", end_color="FFEB9C", fill_type="solid")
BAD_FILL = PatternFill(start_color="FFC7CE", end_color="FFC7CE", fill_type="solid")
WRAP = Alignment(wrap_text=True, vertical="top")
THIN_BORDER = Border(
    left=Side(style="thin"),
    right=Side(style="thin"),
    top=Side(style="thin"),
    bottom=Side(style="thin"),
)


def _style_header_row(ws, row, max_col):
    """Apply header styling to a row."""
    for col in range(1, max_col + 1):
        cell = ws.cell(row=row, column=col)
        cell.font = HEADER_FONT
        cell.fill = HEADER_FILL
        cell.alignment = Alignment(wrap_text=True, vertical="center")
        cell.border = THIN_BORDER


def _style_section_row(ws, row, max_col, label):
    """Insert a section separator row."""
    ws.cell(row=row, column=1, value=label)
    for col in range(1, max_col + 1):
        cell = ws.cell(row=row, column=col)
        cell.font = SECTION_FONT
        cell.fill = SECTION_FILL
        cell.border = THIN_BORDER


def _auto_width(ws, min_width=10, max_width=50):
    """Set column widths based on content."""
    for col_cells in ws.columns:
        col_letter = get_column_letter(col_cells[0].column)
        lengths = []
        for cell in col_cells:
            if cell.value:
                lines = str(cell.value).split("\n")
                lengths.append(max(len(line) for line in lines))
        if lengths:
            width = min(max(max(lengths) + 2, min_width), max_width)
        else:
            width = min_width
        ws.column_dimensions[col_letter].width = width


def load_extractions() -> list[dict]:
    """Load all extraction JSONs, sorted by filename."""
    results = []
    for fname in sorted(os.listdir(EXTRACTIONS_DIR)):
        if not fname.endswith(".json"):
            continue
        path = os.path.join(EXTRACTIONS_DIR, fname)
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        data["_filename"] = fname.removesuffix(".json")
        results.append(data)
    return results


def _short_name(filename: str, max_len: int = 31) -> str:
    """Create a valid Excel sheet name (max 31 chars, no special chars)."""
    name = filename.replace("_", " ")
    if len(name) > max_len:
        name = name[:max_len - 1] + "…"
    # Excel forbids: \ / * ? : [ ]
    for ch in r"\/*?:[]":
        name = name.replace(ch, "")
    return name


def build_dashboard(wb: Workbook, extractions: list[dict]) -> None:
    """Build the Dashboard sheet."""
    ws = wb.active
    ws.title = "Dashboard"

    # Title
    ws.cell(row=1, column=1, value="Phase 1 — Manual Review Dashboard")
    ws.cell(row=1, column=1).font = Font(bold=True, size=14, color="2F5496")
    ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=12)

    # Summary stats
    total = len(extractions)
    total_problems = sum(len(e.get("problem_domains", [])) for e in extractions)
    total_solutions = sum(len(e.get("solution_approaches", [])) for e in extractions)
    total_claims = sum(len(e.get("key_claims", [])) for e in extractions)

    ws.cell(row=3, column=1, value="Papers:")
    ws.cell(row=3, column=2, value=total)
    ws.cell(row=3, column=3, value="Total problems:")
    ws.cell(row=3, column=4, value=total_problems)
    ws.cell(row=3, column=5, value="Total solutions:")
    ws.cell(row=3, column=6, value=total_solutions)
    ws.cell(row=3, column=7, value="Total claims:")
    ws.cell(row=3, column=8, value=total_claims)
    for col in range(1, 9):
        ws.cell(row=3, column=col).font = Font(bold=True, size=10)

    # Headers
    headers = [
        "＃",             # A
        "Sheet",           # B
        "Title",           # C
        "Authors",         # D
        "Year",            # E
        "Type",            # F
        "Problems",        # G
        "Solutions",       # H
        "Mappings",        # I
        "Claims",          # J
        "Quality",         # K
        "Review Status",   # L — reviewer fills
        "Relevance",       # M — reviewer fills
        "Exclusion Reason",# N — reviewer fills
        "Notes",           # O — reviewer fills
    ]
    header_row = 5
    for col, h in enumerate(headers, 1):
        ws.cell(row=header_row, column=col, value=h)
    _style_header_row(ws, header_row, len(headers))

    # Data rows
    for i, ext in enumerate(extractions, 1):
        row = header_row + i
        meta = ext.get("metadata", {})
        quality = ext.get("_extraction_quality", {})
        q_valid = quality.get("valid", True)
        q_reason = quality.get("reason", "")
        sheet_name = _short_name(ext["_filename"])

        ws.cell(row=row, column=1, value=i)
        ws.cell(row=row, column=2, value=sheet_name)
        ws.cell(row=row, column=3, value=meta.get("title", ""))
        authors = meta.get("authors", [])
        ws.cell(row=row, column=4, value=", ".join(authors) if authors else "")
        ws.cell(row=row, column=5, value=meta.get("year", ""))
        ws.cell(row=row, column=6, value=meta.get("document_type", ""))
        ws.cell(row=row, column=7, value=len(ext.get("problem_domains", [])))
        ws.cell(row=row, column=8, value=len(ext.get("solution_approaches", [])))
        ws.cell(row=row, column=9, value=len(ext.get("problem_solution_mappings", [])))
        ws.cell(row=row, column=10, value=len(ext.get("key_claims", [])))

        quality_text = "OK" if q_valid else f"LOW: {q_reason}"
        q_cell = ws.cell(row=row, column=11, value=quality_text)
        q_cell.fill = OK_FILL if q_valid else WARN_FILL

        # Reviewer columns — dropdowns via data validation
        ws.cell(row=row, column=12, value="")  # Review Status
        ws.cell(row=row, column=13, value="")  # Relevance
        ws.cell(row=row, column=14, value="")  # Exclusion Reason
        ws.cell(row=row, column=15, value="")  # Notes

        # Style
        for col in range(1, len(headers) + 1):
            cell = ws.cell(row=row, column=col)
            cell.alignment = WRAP
            cell.border = THIN_BORDER

    # Data validation for reviewer columns
    from openpyxl.worksheet.datavalidation import DataValidation

    dv_status = DataValidation(
        type="list",
        formula1='"not-started,in-progress,verified,needs-recheck,exclude"',
        allow_blank=True,
    )
    dv_status.prompt = "Review status"
    dv_relevance = DataValidation(
        type="list",
        formula1='"high,medium,low"',
        allow_blank=True,
    )
    dv_relevance.prompt = "Relevance for taxonomy building"

    first_data = header_row + 1
    last_data = header_row + len(extractions)
    dv_status.add(f"L{first_data}:L{last_data}")
    dv_relevance.add(f"M{first_data}:M{last_data}")
    ws.add_data_validation(dv_status)
    ws.add_data_validation(dv_relevance)

    # Freeze panes
    ws.freeze_panes = f"A{header_row + 1}"

    # Column widths
    widths = [4, 20, 40, 25, 6, 16, 9, 9, 9, 7, 18, 14, 10, 18, 30]
    for i, w in enumerate(widths, 1):
        ws.column_dimensions[get_column_letter(i)].width = w


def build_paper_sheet(wb: Workbook, ext: dict) -> None:
    """Build a review sheet for a single paper."""
    sheet_name = _short_name(ext["_filename"])
    ws = wb.create_sheet(title=sheet_name)
    meta = ext.get("metadata", {})

    # Max columns for the data area
    MAX_COL = 8

    # --- Paper header ---
    title = meta.get("title", ext["_filename"])
    ws.cell(row=1, column=1, value=title)
    ws.cell(row=1, column=1).font = Font(bold=True, size=13, color="2F5496")
    ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=MAX_COL)

    authors = ", ".join(meta.get("authors", []))
    year = meta.get("year", "")
    venue = meta.get("venue", "")
    doc_type = meta.get("document_type", "")
    ws.cell(row=2, column=1, value=f"{authors} ({year}) — {venue} [{doc_type}]")
    ws.cell(row=2, column=1).font = Font(italic=True, size=10)
    ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=MAX_COL)

    row = 4

    # --- PROBLEM DOMAINS ---
    _style_section_row(ws, row, MAX_COL, "PROBLEM DOMAINS")
    row += 1
    prob_headers = ["＃", "Problem Label", "Description", "Verbatim Quote", "Location", "Confidence", "Codes (your input)", "Decision"]
    for col, h in enumerate(prob_headers, 1):
        ws.cell(row=row, column=col, value=h)
    _style_header_row(ws, row, len(prob_headers))
    row += 1

    for i, item in enumerate(ext.get("problem_domains", []), 1):
        ws.cell(row=row, column=1, value=i)
        ws.cell(row=row, column=2, value=item.get("problem", ""))
        ws.cell(row=row, column=3, value=item.get("description", ""))
        ws.cell(row=row, column=4, value=item.get("quote", ""))
        ws.cell(row=row, column=5, value=item.get("location", ""))
        ws.cell(row=row, column=6, value=item.get("confidence", ""))
        ws.cell(row=row, column=7, value="")  # Reviewer codes
        ws.cell(row=row, column=8, value="")  # Accept/Edit/Reject/Merge
        for col in range(1, MAX_COL + 1):
            cell = ws.cell(row=row, column=col)
            cell.alignment = WRAP
            cell.border = THIN_BORDER
        row += 1

    # Empty row for manually adding missed problems
    ws.cell(row=row, column=1, value="")
    ws.cell(row=row, column=2, value="(add missed problems here)")
    ws.cell(row=row, column=2).font = Font(italic=True, color="808080")
    row += 2

    # --- SOLUTION APPROACHES ---
    _style_section_row(ws, row, MAX_COL, "SOLUTION APPROACHES")
    row += 1
    sol_headers = ["＃", "Approach Label", "Description", "Verbatim Quote", "Location", "Confidence", "Codes (your input)", "Decision"]
    for col, h in enumerate(sol_headers, 1):
        ws.cell(row=row, column=col, value=h)
    _style_header_row(ws, row, len(sol_headers))
    row += 1

    for i, item in enumerate(ext.get("solution_approaches", []), 1):
        ws.cell(row=row, column=1, value=i)
        ws.cell(row=row, column=2, value=item.get("approach", ""))
        ws.cell(row=row, column=3, value=item.get("description", ""))
        ws.cell(row=row, column=4, value=item.get("quote", ""))
        ws.cell(row=row, column=5, value=item.get("location", ""))
        ws.cell(row=row, column=6, value=item.get("confidence", ""))
        ws.cell(row=row, column=7, value="")
        ws.cell(row=row, column=8, value="")
        for col in range(1, MAX_COL + 1):
            cell = ws.cell(row=row, column=col)
            cell.alignment = WRAP
            cell.border = THIN_BORDER
        row += 1

    ws.cell(row=row, column=2, value="(add missed approaches here)")
    ws.cell(row=row, column=2).font = Font(italic=True, color="808080")
    row += 2

    # --- PROBLEM–SOLUTION MAPPINGS ---
    _style_section_row(ws, row, MAX_COL, "PROBLEM–SOLUTION MAPPINGS")
    row += 1
    map_headers = ["＃", "Problem", "Approach", "Verbatim Quote", "Location", "", "Valid? (Y/N)", "Notes"]
    for col, h in enumerate(map_headers, 1):
        ws.cell(row=row, column=col, value=h)
    _style_header_row(ws, row, len(map_headers))
    row += 1

    for i, item in enumerate(ext.get("problem_solution_mappings", []), 1):
        ws.cell(row=row, column=1, value=i)
        ws.cell(row=row, column=2, value=item.get("problem", ""))
        ws.cell(row=row, column=3, value=item.get("approach", ""))
        ws.cell(row=row, column=4, value=item.get("quote", ""))
        ws.cell(row=row, column=5, value=item.get("location", ""))
        ws.cell(row=row, column=7, value="")  # Valid?
        ws.cell(row=row, column=8, value="")  # Notes
        for col in range(1, MAX_COL + 1):
            cell = ws.cell(row=row, column=col)
            cell.alignment = WRAP
            cell.border = THIN_BORDER
        row += 1

    row += 1

    # --- KEY CLAIMS ---
    _style_section_row(ws, row, MAX_COL, "KEY CLAIMS")
    row += 1
    claim_headers = ["＃", "Claim", "Type", "Verbatim Quote", "Location", "Confidence", "Agree? (Y/N)", "Notes"]
    for col, h in enumerate(claim_headers, 1):
        ws.cell(row=row, column=col, value=h)
    _style_header_row(ws, row, len(claim_headers))
    row += 1

    for i, item in enumerate(ext.get("key_claims", []), 1):
        ws.cell(row=row, column=1, value=i)
        ws.cell(row=row, column=2, value=item.get("claim", ""))
        ws.cell(row=row, column=3, value=item.get("claim_type", ""))
        ws.cell(row=row, column=4, value=item.get("quote", ""))
        ws.cell(row=row, column=5, value=item.get("location", ""))
        ws.cell(row=row, column=6, value=item.get("confidence", ""))
        ws.cell(row=row, column=7, value="")
        ws.cell(row=row, column=8, value="")
        for col in range(1, MAX_COL + 1):
            cell = ws.cell(row=row, column=col)
            cell.alignment = WRAP
            cell.border = THIN_BORDER
        row += 1

    row += 1

    # --- MATURITY INDICATORS ---
    _style_section_row(ws, row, MAX_COL, "MATURITY INDICATORS")
    row += 1
    mat_headers = ["＃", "Indicator", "Verbatim Quote", "Location", "", "", "Correct? (Y/N)", "Notes"]
    for col, h in enumerate(mat_headers, 1):
        ws.cell(row=row, column=col, value=h)
    _style_header_row(ws, row, len(mat_headers))
    row += 1

    for i, item in enumerate(ext.get("maturity_indicators", []), 1):
        ws.cell(row=row, column=1, value=i)
        ws.cell(row=row, column=2, value=item.get("indicator", ""))
        ws.cell(row=row, column=3, value=item.get("quote", ""))
        ws.cell(row=row, column=4, value=item.get("location", ""))
        ws.cell(row=row, column=7, value="")
        ws.cell(row=row, column=8, value="")
        for col in range(1, MAX_COL + 1):
            cell = ws.cell(row=row, column=col)
            cell.alignment = WRAP
            cell.border = THIN_BORDER
        row += 1

    row += 1

    # --- OPEN QUESTIONS ---
    _style_section_row(ws, row, MAX_COL, "OPEN QUESTIONS")
    row += 1
    oq_headers = ["＃", "Question / Future Work", "Verbatim Quote", "Location", "", "", "Keep? (Y/N)", "Notes"]
    for col, h in enumerate(oq_headers, 1):
        ws.cell(row=row, column=col, value=h)
    _style_header_row(ws, row, len(oq_headers))
    row += 1

    for i, item in enumerate(ext.get("open_questions", []), 1):
        ws.cell(row=row, column=1, value=i)
        ws.cell(row=row, column=2, value=item.get("question", ""))
        ws.cell(row=row, column=3, value=item.get("quote", ""))
        ws.cell(row=row, column=4, value=item.get("location", ""))
        ws.cell(row=row, column=7, value="")
        ws.cell(row=row, column=8, value="")
        for col in range(1, MAX_COL + 1):
            cell = ws.cell(row=row, column=col)
            cell.alignment = WRAP
            cell.border = THIN_BORDER
        row += 1

    # Data validation for Decision columns
    from openpyxl.worksheet.datavalidation import DataValidation

    dv_decision = DataValidation(
        type="list",
        formula1='"accept,edit,reject,merge,add"',
        allow_blank=True,
    )
    dv_yn = DataValidation(
        type="list",
        formula1='"Y,N"',
        allow_blank=True,
    )
    ws.add_data_validation(dv_decision)
    ws.add_data_validation(dv_yn)
    # Apply to all Decision/Valid/Agree/Correct/Keep columns (col H=8 and G=7)
    dv_decision.add(f"H1:H{row}")
    dv_yn.add(f"G1:G{row}")

    # Column widths
    widths = [4, 28, 28, 45, 20, 12, 16, 25]
    for i, w in enumerate(widths, 1):
        ws.column_dimensions[get_column_letter(i)].width = w

    # Freeze header area
    ws.freeze_panes = "A4"


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate Excel review workbook from extraction JSONs.",
    )
    parser.add_argument(
        "--output", default=DEFAULT_OUTPUT,
        help=f"Output path (default: {DEFAULT_OUTPUT})",
    )
    args = parser.parse_args()

    extractions = load_extractions()
    if not extractions:
        print("No extraction JSONs found in", EXTRACTIONS_DIR)
        sys.exit(1)

    print(f"Building workbook from {len(extractions)} extractions...")

    wb = Workbook()
    build_dashboard(wb, extractions)

    for ext in extractions:
        build_paper_sheet(wb, ext)

    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    wb.save(args.output)
    print(f"Saved: {args.output}")

    # Stats
    total_rows = sum(
        len(e.get("problem_domains", []))
        + len(e.get("solution_approaches", []))
        + len(e.get("problem_solution_mappings", []))
        + len(e.get("key_claims", []))
        + len(e.get("maturity_indicators", []))
        + len(e.get("open_questions", []))
        for e in extractions
    )
    print(f"Sheets: 1 dashboard + {len(extractions)} papers")
    print(f"Total items to review: {total_rows}")


if __name__ == "__main__":
    main()
