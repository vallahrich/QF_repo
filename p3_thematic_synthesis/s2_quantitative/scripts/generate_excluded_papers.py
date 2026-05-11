"""Generate current P3 quantitative corpus exclusion lineage artifacts.

Reconciles P2 processed records, shared extracted text, and active S2
quantitative extractions to produce an auditable record of every P2 paper that
does NOT end up as a current P3 quantitative extraction:

  - no_quantitative_results: P2 set has_quantitative_results=false
  - survey / editorial / meta_analysis / book_chapter / commentary:
        P2 source_type matches SKIP_SOURCE_TYPES
  - scope_out: methodology_tags include quantum-annealing-qubo (SA-01)
        or any other scope-out tag (gate-based thesis only)
  - missing_from_p2: the paper is in extracted_text but has no P2 file
The script writes the current exclusion CSV plus compact JSON/Markdown lineage
reports that distinguish historical checkpoints from the active corpus.

Usage:
    python -m p3_thematic_synthesis.s2_quantitative.scripts.generate_excluded_papers
"""
from __future__ import annotations

import csv
import json
import sys
from collections import Counter
from datetime import date
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_QUANT_ROOT = Path(__file__).resolve().parents[1]
_PROJECT_ROOT = Path(__file__).resolve().parents[3]

TEXT_DIR = _PROJECT_ROOT / "shared" / "extracted_text" / "text"
P2_DIR = _PROJECT_ROOT / "p2_systematic_review" / "output" / "processed"
BRIDGE_CSV = _PROJECT_ROOT / "shared" / "bridge" / "paper_id_bridge.csv"
OUTPUT_CSV = _PROJECT_ROOT / "shared" / "bridge" / "excluded_papers.csv"
EXTRACTIONS_DIR = _QUANT_ROOT / "output" / "extractions"
AUDIT_DIR = _QUANT_ROOT / "output" / "audit"
OUTPUT_JSON = AUDIT_DIR / "corpus_lineage.json"
OUTPUT_MD = AUDIT_DIR / "corpus_lineage.md"
HISTORICAL_EXCLUDED_CSV = AUDIT_DIR / "excluded_papers_historical_2026-04-17.csv"
SCOPE_AUDIT = AUDIT_DIR / "raw_scope_audit.json"
EXPECTED_HISTORICAL_EXCLUSION_ROWS = 318

HISTORICAL_CHECKPOINTS = [
    {
        "checkpoint_id": "pre_q0_audit_historical",
        "paper_count": 643,
        "experiment_count": 1957,
        "source": "p3_thematic_synthesis/AUDIT_REPORT.md",
        "interpretation": "Historical pre-repair audit state; includes annealing/QUBO leakage and is not the active corpus.",
    },
    {
        "checkpoint_id": "s3_freeze_2026_04_17_historical",
        "paper_count": 459,
        "experiment_count": 1185,
        "source": "p3_thematic_synthesis/s3_quantum_advantage/FROZEN.md",
        "interpretation": "Historical S3 freeze state from 2026-04-17; superseded by the active S2 directory.",
    },
]

SKIP_SOURCE_TYPES = {
    "survey": "survey",
    "editorial": "editorial",
    "meta-analysis": "meta_analysis",
    "book-chapter": "book_chapter",
    "commentary": "commentary",
}

SCOPE_OUT_METHODOLOGY_TAGS = {
    "quantum-annealing-qubo",
    "SA-01",
    "quantum-annealing",
    "annealing",
    "qubo",
    "d-wave",
}


def _paper_id_from_bridge_row(row: dict[str, str]) -> str:
    return row.get("slr_id") or row.get("slr_paper_id") or row.get("paper_id") or ""


def _load_bridge() -> tuple[dict[str, dict], dict[str, int]]:
    if not BRIDGE_CSV.is_file():
        return {}, {}
    out: dict[str, dict] = {}
    counts: Counter[str] = Counter()
    with BRIDGE_CSV.open(encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            sid = _paper_id_from_bridge_row(row)
            if sid:
                counts[sid] += 1
                out[sid] = row
    return out, dict(counts)


def _p2_path(paper_id: str) -> Path | None:
    for name in (f"{paper_id}_extraction.json", f"{paper_id}.json"):
        p = P2_DIR / name
        if p.is_file():
            return p
    return None


def _collect_text_ids() -> set[str]:
    ids: set[str] = set()
    for md in TEXT_DIR.glob("*.md"):
        # Filenames are {paper_id}_title-slug.md; paper_id is the 12-char prefix.
        stem = md.stem
        pid = stem.split("_", 1)[0]
        if pid:
            ids.add(pid)
    return ids


def _collect_p2_ids() -> set[str]:
    return {jp.stem.replace("_extraction", "") for jp in P2_DIR.glob("*.json")}


def _collect_active_extraction_ids() -> set[str]:
    return {jp.stem for jp in EXTRACTIONS_DIR.glob("*.json")}


def _collect_paper_ids() -> list[str]:
    ids: set[str] = set()
    ids.update(_collect_text_ids())
    for jp in P2_DIR.glob("*.json"):
        ids.add(jp.stem.replace("_extraction", ""))
    return sorted(ids)


def _read_p2(paper_id: str) -> dict[str, Any] | None:
    p2 = _p2_path(paper_id)
    if p2 is None:
        return None
    try:
        return json.loads(p2.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


def _classify(paper_id: str) -> tuple[str, str] | None:
    """Return (reason, detail) if excluded, else None (paper is kept)."""
    p2 = _p2_path(paper_id)
    if p2 is None:
        return ("missing_from_p2", "no P2 extraction JSON found")

    try:
        d = json.loads(p2.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        return ("p2_unreadable", str(exc))

    source_type = (d.get("source_type") or "").strip().lower()
    if source_type in SKIP_SOURCE_TYPES:
        return (SKIP_SOURCE_TYPES[source_type], f"source_type={source_type}")

    if not d.get("has_quantitative_results"):
        return ("no_quantitative_results", "P2 flagged no_quantitative_results")

    methodology_tags = [t for t in (d.get("methodology_tags") or []) if t]
    hit = [t for t in methodology_tags if t in SCOPE_OUT_METHODOLOGY_TAGS]
    if hit:
        return ("scope_out", f"methodology_tags={hit}")

    return None  # paper is in scope and should appear in extractions


def _read_csv_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def _read_existing_exclusions() -> list[dict[str, str]]:
    return _read_csv_rows(OUTPUT_CSV)


def _read_historical_exclusions() -> list[dict[str, str]]:
    return _read_csv_rows(HISTORICAL_EXCLUDED_CSV)


def _archive_historical_exclusions(previous_rows: list[dict[str, str]], current_rows: list[dict[str, Any]]) -> bool:
    if not previous_rows:
        return False
    existing_archive = _read_historical_exclusions()
    if len(existing_archive) == EXPECTED_HISTORICAL_EXCLUSION_ROWS:
        return False
    if len(previous_rows) != EXPECTED_HISTORICAL_EXCLUSION_ROWS:
        return False
    previous_ids = {r.get("slr_id", "") for r in previous_rows if r.get("slr_id")}
    current_ids = {r.get("slr_id", "") for r in current_rows if r.get("slr_id")}
    if previous_ids == current_ids:
        return False
    HISTORICAL_EXCLUDED_CSV.parent.mkdir(parents=True, exist_ok=True)
    fields = [field for field in previous_rows[0].keys() if field is not None]
    with HISTORICAL_EXCLUDED_CSV.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        w.writerows(previous_rows)
    return True


def _summarise_active_extractions() -> dict[str, Any]:
    validation_files: Counter[str] = Counter()
    validation_experiments: Counter[str] = Counter()
    total_experiments = 0
    parse_errors: list[str] = []
    for path in sorted(EXTRACTIONS_DIR.glob("*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as exc:
            parse_errors.append(f"{path.name}: {exc}")
            continue
        experiments = data.get("experiments") or []
        total_experiments += len(experiments)
        metadata = data.get("extraction_metadata") or {}
        validation = str(metadata.get("validation_passed"))
        validation_files[validation] += 1
        validation_experiments[validation] += len(experiments)
    return {
        "files": len(list(EXTRACTIONS_DIR.glob("*.json"))),
        "experiments": total_experiments,
        "validation_files": dict(sorted(validation_files.items())),
        "validation_experiments": dict(sorted(validation_experiments.items())),
        "parse_errors": parse_errors,
    }


def _safe_read_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


def _build_lineage(
    rows: list[dict[str, Any]],
    previous_rows: list[dict[str, str]],
    bridge_counts: dict[str, int],
    historical_archive_written: bool,
    historical_archive_rows: list[dict[str, str]],
) -> dict[str, Any]:
    p2_ids = _collect_p2_ids()
    text_ids = _collect_text_ids()
    active_ids = _collect_active_extraction_ids()
    excluded_ids = {r["slr_id"] for r in rows}
    expected_active_ids = p2_ids - excluded_ids
    previous_ids = {r.get("slr_id", "") for r in previous_rows if r.get("slr_id")}
    historical_archive_ids = {r.get("slr_id", "") for r in historical_archive_rows if r.get("slr_id")}
    historical_reference_ids = historical_archive_ids or previous_ids
    duplicate_bridge_ids = sorted(pid for pid, count in bridge_counts.items() if count > 1)
    active_summary = _summarise_active_extractions()
    scope_audit = _safe_read_json(SCOPE_AUDIT) or {}

    current_checkpoint = {
        "checkpoint_id": "current_active_s2_2026_04_28",
        "paper_count": active_summary["files"],
        "experiment_count": active_summary["experiments"],
        "source": "p3_thematic_synthesis/s2_quantitative/output/extractions/",
        "interpretation": "Current active S2 quantitative extraction corpus.",
    }
    return {
        "schema_version": "p3_s2_corpus_lineage.1.0",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "inputs": {
            "p2_processed": str(P2_DIR.relative_to(_PROJECT_ROOT)).replace("\\", "/"),
            "extracted_text": str(TEXT_DIR.relative_to(_PROJECT_ROOT)).replace("\\", "/"),
            "active_s2_extractions": str(EXTRACTIONS_DIR.relative_to(_PROJECT_ROOT)).replace("\\", "/"),
            "paper_id_bridge": str(BRIDGE_CSV.relative_to(_PROJECT_ROOT)).replace("\\", "/"),
            "scope_audit": str(SCOPE_AUDIT.relative_to(_PROJECT_ROOT)).replace("\\", "/"),
        },
        "current_active_lineage": {
            "p2_processed_records": len(p2_ids),
            "extracted_text_files": len(text_ids),
            "current_excluded_papers": len(rows),
            "current_excluded_reason_counts": dict(sorted(Counter(r["exclusion_reason"] for r in rows).items())),
            "active_extraction_files": active_summary["files"],
            "active_experiments": active_summary["experiments"],
            "validation_files": active_summary["validation_files"],
            "validation_experiments": active_summary["validation_experiments"],
            "equation": f"{len(p2_ids)} P2 records - {len(rows)} current exclusions = {active_summary['files']} active extraction files",
        },
        "historical_checkpoints": [*HISTORICAL_CHECKPOINTS, current_checkpoint],
        "historical_previous_exclusion_csv": {
            "rows_before_regeneration": len(previous_rows),
            "reason_counts_before_regeneration": dict(sorted(Counter(r.get("exclusion_reason", "") for r in previous_rows).items())),
            "archive_rows": len(historical_archive_rows),
            "archive_reason_counts": dict(sorted(Counter(r.get("exclusion_reason", "") for r in historical_archive_rows).items())),
            "archive_implied_active_papers": len(p2_ids) - len(historical_archive_rows) if historical_archive_rows else None,
            "overlap_with_current_active_extractions": len(historical_reference_ids & active_ids),
            "ids_in_previous_csv_now_active_sample": sorted(historical_reference_ids & active_ids)[:25],
            "archive_path": str(HISTORICAL_EXCLUDED_CSV.relative_to(_PROJECT_ROOT)).replace("\\", "/") if (HISTORICAL_EXCLUDED_CSV.exists() or historical_archive_written) else None,
        },
        "consistency_checks": {
            "expected_active_matches_extraction_directory": expected_active_ids == active_ids,
            "expected_active_missing_from_extraction_directory": sorted(expected_active_ids - active_ids),
            "active_extractions_not_expected_by_current_filter": sorted(active_ids - expected_active_ids),
            "active_extractions_missing_from_p2": sorted(active_ids - p2_ids),
            "p2_records_missing_text": sorted(p2_ids - text_ids),
            "text_records_missing_p2": sorted(text_ids - p2_ids),
            "active_parse_errors": active_summary["parse_errors"],
            "scope_audit_violation_count": scope_audit.get("violation_count"),
            "scope_audit_validation_failed_files": scope_audit.get("validation_failed_files"),
            "duplicate_paper_ids_in_bridge": duplicate_bridge_ids,
        },
    }


def _lineage_markdown(payload: dict[str, Any]) -> str:
    current = payload["current_active_lineage"]
    checks = payload["consistency_checks"]
    previous = payload["historical_previous_exclusion_csv"]
    lines = [
        "# P3 S2 Corpus Lineage",
        "",
        f"Generated UTC: `{payload['generated_utc']}`",
        "",
        "## Current Active Corpus",
        "",
        f"- P2 processed records: {current['p2_processed_records']}",
        f"- Current exclusion rows: {current['current_excluded_papers']}",
        f"- Active S2 extraction files: {current['active_extraction_files']}",
        f"- Active S2 experiments: {current['active_experiments']}",
        f"- Lineage equation: {current['equation']}",
        f"- Validation files: {current['validation_files']}",
        f"- Validation experiments: {current['validation_experiments']}",
        "",
        "## Current Exclusion Reasons",
        "",
        "| Reason | Papers |",
        "|---|---:|",
    ]
    for reason, count in current["current_excluded_reason_counts"].items():
        lines.append(f"| {reason} | {count} |")
    lines.extend([
        "",
        "## Historical Checkpoints",
        "",
        "| Checkpoint | Papers | Experiments | Interpretation | Source |",
        "|---|---:|---:|---|---|",
    ])
    for checkpoint in payload["historical_checkpoints"]:
        lines.append(
            f"| {checkpoint['checkpoint_id']} | {checkpoint['paper_count']} | "
            f"{checkpoint['experiment_count']} | {checkpoint['interpretation']} | {checkpoint['source']} |"
        )
    lines.extend([
        "",
        "## Previous Exclusion CSV Before Regeneration",
        "",
        f"- Rows in active exclusion CSV before this run: {previous['rows_before_regeneration']}",
        f"- Reason counts in active exclusion CSV before this run: {previous['reason_counts_before_regeneration']}",
        f"- Historical archive rows: {previous['archive_rows']}",
        f"- Historical archive reason counts: {previous['archive_reason_counts']}",
        f"- Historical archive implied active papers: {previous['archive_implied_active_papers']}",
        f"- Previous-excluded IDs now active: {previous['overlap_with_current_active_extractions']}",
        f"- Historical archive: {previous['archive_path']}",
        "",
        "## Consistency Checks",
        "",
        f"- Expected active set matches extraction directory: {checks['expected_active_matches_extraction_directory']}",
        f"- Active extractions missing from P2: {len(checks['active_extractions_missing_from_p2'])}",
        f"- P2 records missing extracted text: {len(checks['p2_records_missing_text'])}",
        f"- Extracted text records missing P2: {len(checks['text_records_missing_p2'])}",
        f"- Scope-audit hard violations: {checks['scope_audit_violation_count']}",
        f"- Scope-audit validation-failed files: {checks['scope_audit_validation_failed_files']}",
        "",
        "Current claim boundary: the 643-paper and 459-paper counts are historical checkpoints, not the active S2 quantitative corpus. The active corpus is the 501-file extraction directory summarized above.",
        "",
    ])
    return "\n".join(lines)


def main() -> int:
    bridge, bridge_counts = _load_bridge()
    paper_ids = _collect_paper_ids()
    previous_rows = _read_existing_exclusions()

    rows: list[dict[str, Any]] = []
    today = date.today().isoformat()
    for pid in paper_ids:
        cls = _classify(pid)
        if cls is None:
            continue
        reason, detail = cls
        br = bridge.get(pid, {})
        p2 = _read_p2(pid) or {}
        rows.append({
            "slr_id": pid,
            "title": br.get("title", "") or p2.get("title", ""),
            "doi": br.get("doi", "") or p2.get("doi", ""),
            "source_type": p2.get("source_type", ""),
            "exclusion_reason": reason,
            "exclusion_detail": detail,
            "date_excluded": today,
        })

    historical_archive_written = _archive_historical_exclusions(previous_rows, rows)
    historical_archive_rows = _read_historical_exclusions()

    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    fields = [
        "slr_id", "title", "doi", "source_type",
        "exclusion_reason", "exclusion_detail", "date_excluded",
    ]
    with OUTPUT_CSV.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in rows:
            w.writerow(r)

    counts: dict[str, int] = {}
    for r in rows:
        counts[r["exclusion_reason"]] = counts.get(r["exclusion_reason"], 0) + 1

    lineage = _build_lineage(rows, previous_rows, bridge_counts, historical_archive_written, historical_archive_rows)
    AUDIT_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_JSON.write_text(json.dumps(lineage, indent=2) + "\n", encoding="utf-8")
    OUTPUT_MD.write_text(_lineage_markdown(lineage), encoding="utf-8")

    print(f"wrote {OUTPUT_CSV} ({len(rows)} papers)")
    for k in sorted(counts):
        print(f"  {k}: {counts[k]}")
    print(f"wrote {OUTPUT_JSON.relative_to(_PROJECT_ROOT)}")
    print(f"wrote {OUTPUT_MD.relative_to(_PROJECT_ROOT)}")
    if historical_archive_written:
        print(f"archived previous CSV to {HISTORICAL_EXCLUDED_CSV.relative_to(_PROJECT_ROOT)}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
