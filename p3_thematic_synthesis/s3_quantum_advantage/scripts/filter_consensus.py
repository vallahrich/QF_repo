"""Filter consensus + matrix + disagreement files to active silos.

The frozen S3 outputs were produced before the 2026-04-19 active-silo
reduction; they still carry `cryptography-security` and `insurance-actuarial`
rows from a pre-exclusion run. This script reads the current
`shared/config/silo_inclusion.json` and emits filtered views for the three
artefacts downstream consumers care about, without re-triangulating:

- ``combined/output/consensus_summary.filtered.json`` (rollup; `by_silo` dict)
- ``combined/output/triangulation_matrix.filtered.json`` (per-experiment rows)
- ``combined/output/disagreement_cases.filtered.json`` (per-experiment rows)

plus a single ``combined/output/consensus_summary.filter_diff.json`` describing
what was dropped from each file.

No LLM calls, no per-paper assessor invocation: pure JSON rollup. Idempotent.

Usage (from the repo root):

    python p3_thematic_synthesis/s3_quantum_advantage/scripts/filter_consensus.py
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
_S3_ROOT = _SCRIPT_DIR.parent
_P3_ROOT = _S3_ROOT.parent
_REPO_ROOT = _P3_ROOT.parent

SILO_INCLUSION = _REPO_ROOT / "shared" / "config" / "silo_inclusion.json"
OUT_DIR = _S3_ROOT / "combined" / "output"
CONSENSUS_PATH = OUT_DIR / "consensus_summary.json"
MATRIX_PATH = OUT_DIR / "triangulation_matrix.json"
DISAGREEMENT_PATH = OUT_DIR / "disagreement_cases.json"
FILTERED_CONSENSUS = OUT_DIR / "consensus_summary.filtered.json"
FILTERED_MATRIX = OUT_DIR / "triangulation_matrix.filtered.json"
FILTERED_DISAGREEMENT = OUT_DIR / "disagreement_cases.filtered.json"
DIFF_PATH = OUT_DIR / "consensus_summary.filter_diff.json"


def _slugs(folder: str) -> set[str]:
    f = folder.strip().lower()
    return {f, f.replace("_", "-")}


def _active_silo_keys() -> set[str]:
    raw = json.loads(SILO_INCLUSION.read_text(encoding="utf-8"))
    keys: set[str] = set()
    for silo in raw.get("active_silos", []):
        keys |= _slugs(silo.get("folder", ""))
    return keys


def _filter_rows(rows: list[dict], active: set[str]) -> tuple[list[dict], dict[str, int]]:
    kept: list[dict] = []
    dropped: dict[str, int] = {}
    for row in rows:
        silo = str(row.get("silo", "")).strip().lower()
        if silo in active:
            kept.append(row)
        else:
            dropped[silo] = dropped.get(silo, 0) + 1
    return kept, dropped


def main() -> None:
    if not CONSENSUS_PATH.is_file():
        print(f"Missing input: {CONSENSUS_PATH}", file=sys.stderr)
        sys.exit(1)

    consensus = json.loads(CONSENSUS_PATH.read_text(encoding="utf-8"))
    active = _active_silo_keys()

    # consensus_summary.json: dict-shaped rollup with by_silo
    by_silo = consensus.get("by_silo", {})
    kept_by_silo: dict[str, dict] = {}
    dropped_by_silo: dict[str, dict] = {}
    for silo_key, payload in by_silo.items():
        if silo_key.lower() in active:
            kept_by_silo[silo_key] = payload
        else:
            dropped_by_silo[silo_key] = payload
    filtered_consensus = dict(consensus)
    filtered_consensus["by_silo"] = kept_by_silo
    filtered_consensus["_filter"] = {
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "source": str(CONSENSUS_PATH.relative_to(_REPO_ROOT)),
        "silo_inclusion": str(SILO_INCLUSION.relative_to(_REPO_ROOT)),
        "active_silo_keys_seen": sorted(kept_by_silo.keys()),
        "dropped_silo_keys": sorted(dropped_by_silo.keys()),
    }
    FILTERED_CONSENSUS.write_text(json.dumps(filtered_consensus, indent=2) + "\n", encoding="utf-8")

    matrix_dropped: dict[str, int] = {}
    matrix_kept_n = 0
    if MATRIX_PATH.is_file():
        matrix = json.loads(MATRIX_PATH.read_text(encoding="utf-8"))
        kept_matrix, matrix_dropped = _filter_rows(matrix, active)
        matrix_kept_n = len(kept_matrix)
        FILTERED_MATRIX.write_text(json.dumps(kept_matrix, indent=2) + "\n", encoding="utf-8")

    disagreement_dropped: dict[str, int] = {}
    disagreement_kept_n = 0
    if DISAGREEMENT_PATH.is_file():
        disagreement = json.loads(DISAGREEMENT_PATH.read_text(encoding="utf-8"))
        kept_dis, disagreement_dropped = _filter_rows(disagreement, active)
        disagreement_kept_n = len(kept_dis)
        FILTERED_DISAGREEMENT.write_text(json.dumps(kept_dis, indent=2) + "\n", encoding="utf-8")

    diff = {
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "kept_silos": sorted(kept_by_silo.keys()),
        "dropped_silos": sorted(dropped_by_silo.keys()),
        "consensus_summary_dropped_row_counts": {
            k: sum(v.values()) if isinstance(v, dict) else 0
            for k, v in dropped_by_silo.items()
        },
        "triangulation_matrix_kept": matrix_kept_n,
        "triangulation_matrix_dropped_row_counts": matrix_dropped,
        "disagreement_cases_kept": disagreement_kept_n,
        "disagreement_cases_dropped_row_counts": disagreement_dropped,
    }
    DIFF_PATH.write_text(json.dumps(diff, indent=2) + "\n", encoding="utf-8")

    print(f"wrote {FILTERED_CONSENSUS.relative_to(_REPO_ROOT)}")
    if MATRIX_PATH.is_file():
        print(f"wrote {FILTERED_MATRIX.relative_to(_REPO_ROOT)} ({matrix_kept_n} rows kept)")
    if DISAGREEMENT_PATH.is_file():
        print(f"wrote {FILTERED_DISAGREEMENT.relative_to(_REPO_ROOT)} ({disagreement_kept_n} rows kept)")
    print(f"wrote {DIFF_PATH.relative_to(_REPO_ROOT)}")
    print(f"  kept silos:    {sorted(kept_by_silo.keys())}")
    print(f"  dropped silos: {sorted(dropped_by_silo.keys())}")
    print(f"  consensus_summary dropped rows: {diff['consensus_summary_dropped_row_counts']}")
    print(f"  triangulation_matrix dropped rows: {matrix_dropped}")
    print(f"  disagreement_cases dropped rows: {disagreement_dropped}")


if __name__ == "__main__":
    main()
