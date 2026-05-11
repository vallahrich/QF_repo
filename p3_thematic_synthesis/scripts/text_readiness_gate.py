"""Text-readiness gate — Step 3.2b.

Assesses text quality for each paper in the thematic scope before A1 coding.
Papers with poor OCR, missing text, or insufficient content are classified
and routed accordingly.

Classification:
  full_text_usable        → normal A1/A2/R1 pipeline
  partial_text_salvageable → A1 with low-confidence flag, shorter memo
  metadata_only           → landscape tables only (P2 frontmatter)
  exclude_ocr_fail        → excluded with log entry

Operates at PER-SILO scope. Reads inclusion lists from Step 3.2.

Outputs to shared/phase3/text_readiness/<silo>.json

Usage:
    python -m p3_thematic_synthesis.scripts.text_readiness_gate
"""

import json
import logging
import os
import re
from pathlib import Path

_PROJECT_ROOT = str(Path(__file__).resolve().parents[2])

INCLUSION_DIR = os.path.join(_PROJECT_ROOT, "shared", "phase3", "inclusion")
TEXT_DIR = os.path.join(_PROJECT_ROOT, "shared", "extracted_text", "text")
OUTPUT_DIR = os.path.join(_PROJECT_ROOT, "shared", "phase3", "text_readiness")

# Thresholds
MIN_FILE_SIZE_KB = 5  # ~1,250 tokens, ~2 pages
MIN_SECTIONS = 3  # must have text from >= 3 of: abstract, intro, methods, results, discussion
CJK_DENSITY_THRESHOLD = 0.05  # < 5% CJK characters

# Section detection patterns (case-insensitive)
SECTION_PATTERNS = [
    r"\babstract\b",
    r"\bintroduction\b",
    r"\bmethod(?:ology|s)?\b",
    r"\bresult(?:s)?\b",
    r"\bdiscussion\b",
    r"\bconclusion(?:s)?\b",
    r"\bexperiment(?:s|al)?\b",
    r"\bbackground\b",
    r"\brelated work\b",
    r"\bevaluation\b",
]

logging.basicConfig(level=logging.INFO, format="%(levelname)s  %(message)s")
logger = logging.getLogger(__name__)


def find_text_file(paper_id: str) -> str | None:
    """Find the extracted text file for a paper_id (files are <id>_<title>.md)."""
    text_dir = Path(TEXT_DIR)
    matches = list(text_dir.glob(f"{paper_id}*.md"))
    if matches:
        return str(matches[0])
    return None


def count_cjk_chars(text: str) -> float:
    """Return fraction of CJK characters in text."""
    if not text:
        return 0.0
    cjk = len(re.findall(r"[\u4e00-\u9fff\u3040-\u309f\u30a0-\u30ff\uac00-\ud7af]", text))
    return cjk / len(text)


def count_sections(text: str) -> int:
    """Count how many distinct section types are present."""
    text_lower = text.lower()
    found = sum(1 for pattern in SECTION_PATTERNS if re.search(pattern, text_lower))
    return found


def assess_paper(paper_id: str) -> dict:
    """Assess text readiness for a single paper."""
    filepath = find_text_file(paper_id)

    if filepath is None:
        return {
            "paper_id": paper_id,
            "status": "exclude_ocr_fail",
            "reason": "no text file found",
            "file_size_kb": 0,
            "sections_found": 0,
            "cjk_density": 0,
        }

    file_size_kb = os.path.getsize(filepath) / 1024

    if file_size_kb < 1:
        return {
            "paper_id": paper_id,
            "status": "exclude_ocr_fail",
            "reason": f"file too small ({file_size_kb:.1f} KB)",
            "file_size_kb": round(file_size_kb, 1),
            "sections_found": 0,
            "cjk_density": 0,
        }

    with open(filepath, encoding="utf-8", errors="replace") as f:
        text = f.read()

    cjk_density = count_cjk_chars(text)
    sections = count_sections(text)

    if cjk_density > CJK_DENSITY_THRESHOLD:
        return {
            "paper_id": paper_id,
            "status": "exclude_ocr_fail",
            "reason": f"CJK density {cjk_density:.1%} > {CJK_DENSITY_THRESHOLD:.0%}",
            "file_size_kb": round(file_size_kb, 1),
            "sections_found": sections,
            "cjk_density": round(cjk_density, 4),
        }

    if file_size_kb < MIN_FILE_SIZE_KB:
        status = "partial_text_salvageable"
        reason = f"below minimum size ({file_size_kb:.1f} KB < {MIN_FILE_SIZE_KB} KB)"
    elif sections < MIN_SECTIONS:
        status = "partial_text_salvageable"
        reason = f"low section diversity ({sections} < {MIN_SECTIONS})"
    else:
        status = "full_text_usable"
        reason = "passes all checks"

    return {
        "paper_id": paper_id,
        "status": status,
        "reason": reason,
        "file_size_kb": round(file_size_kb, 1),
        "sections_found": sections,
        "cjk_density": round(cjk_density, 4),
    }


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    inclusion_dir = Path(INCLUSION_DIR)
    if not inclusion_dir.exists():
        logger.error("Inclusion directory not found: %s", INCLUSION_DIR)
        return

    for inclusion_file in sorted(inclusion_dir.glob("*.json")):
        silo_name = inclusion_file.stem
        with open(inclusion_file, encoding="utf-8") as f:
            inclusion = json.load(f)

        results = []
        status_counts = {}
        for paper in inclusion["papers"]:
            if not paper.get("in_thematic_scope", False):
                continue

            assessment = assess_paper(paper["paper_id"])
            results.append(assessment)

            s = assessment["status"]
            status_counts[s] = status_counts.get(s, 0) + 1

        output = {
            "silo": silo_name,
            "silo_code": inclusion.get("silo_code", ""),
            "total_assessed": len(results),
            "status_distribution": dict(sorted(status_counts.items())),
            "papers": results,
        }

        output_path = os.path.join(OUTPUT_DIR, f"{silo_name}.json")
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(output, f, indent=2, ensure_ascii=False)

        usable = status_counts.get("full_text_usable", 0)
        partial = status_counts.get("partial_text_salvageable", 0)
        meta = status_counts.get("metadata_only", 0)
        excluded = status_counts.get("exclude_ocr_fail", 0)
        logger.info(
            "%-25s  assessed=%3d  usable=%3d  partial=%2d  metadata=%2d  excluded=%2d",
            silo_name, len(results), usable, partial, meta, excluded,
        )

    logger.info("Text readiness assessments written to %s", OUTPUT_DIR)


if __name__ == "__main__":
    main()
