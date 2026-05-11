"""Generate sha256 fingerprint manifests for the active P3 baseline.

Writes two manifests so an examiner can verify reproducibility without
re-running the LLM extraction or the QA framework assessors:

  - p3_thematic_synthesis/s2_quantitative/output/audit/active_baseline_fingerprints.json
      sha256 of every active-corpus extraction file (frozen LLM output).

  - p3_thematic_synthesis/s3_quantum_advantage/combined/output/active_baseline_fingerprints.json
      sha256 of every assessor result file + the combined triangulation
      outputs. Every change between active and historical FROZEN.md fingerprints
      should be explainable by either (a) input-corpus regeneration (S2) or
      (b) deterministic post-processing fixes (logged in the diff report).

Run:
    python -m tools.verify.v_make_active_fingerprints

This is read-only; no large LLM jobs and no QDK runs.
"""

from __future__ import annotations

import datetime as _dt
import hashlib
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


def _sha256(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _scan(root: Path, patterns: list[str]) -> list[dict]:
    out: list[dict] = []
    for pat in patterns:
        for p in sorted(root.glob(pat)):
            if p.is_file():
                out.append({
                    "path": str(p.relative_to(REPO_ROOT)).replace("\\", "/"),
                    "size_bytes": p.stat().st_size,
                    "sha256": _sha256(p),
                })
    return out


def main() -> int:
    timestamp = _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")

    # --- S2 active baseline (LLM extractions; frozen content, fresh manifest) ---
    s2_root = REPO_ROOT / "p3_thematic_synthesis" / "s2_quantitative" / "output"
    s2_files = _scan(s2_root / "extractions", ["*.json"])
    s2_manifest = {
        "manifest_kind": "p3_s2_active_baseline",
        "description": (
            "sha256 of every active-corpus quantitative extraction file. "
            "These files are LLM-generated and treated as fixed historical "
            "artefacts; this manifest is the reproducibility anchor for any "
            "downstream consumer (P3 s3 assessors and P4)."
        ),
        "generated_utc": timestamp,
        "file_count": len(s2_files),
        "files": s2_files,
    }
    s2_out = s2_root / "audit" / "active_baseline_fingerprints.json"
    s2_out.parent.mkdir(parents=True, exist_ok=True)
    s2_out.write_text(json.dumps(s2_manifest, indent=2), encoding="utf-8")
    print(f"S2 fingerprints: {len(s2_files)} files -> {s2_out.relative_to(REPO_ROOT)}")

    # --- S3 active baseline (assessor results + triangulation outputs) ---
    s3_root = REPO_ROOT / "p3_thematic_synthesis" / "s3_quantum_advantage"
    s3_files: list[dict] = []
    # Per-framework result files
    for fw_dir in sorted(s3_root.iterdir()):
        if not fw_dir.is_dir() or fw_dir.name.startswith("_"):
            continue
        results = fw_dir / "results"
        if results.is_dir():
            s3_files.extend(_scan(results, ["*_results.json"]))
    # Combined outputs (matrix, summaries, schema)
    combined_out = s3_root / "combined" / "output"
    s3_files.extend(_scan(combined_out, [
        "triangulation_matrix.json",
        "consensus_summary.json",
        "disagreement_cases.json",
    ]))
    s3_files.extend(_scan(s3_root / "combined", ["triangulation_row_schema.json"]))
    # Derived fields (input to assessors)
    s3_files.extend(_scan(s3_root / "derived_fields" / "enriched", ["*.json"]))

    s3_manifest = {
        "manifest_kind": "p3_s3_active_baseline",
        "description": (
            "sha256 of every active P3 quantum-advantage artefact: the seven "
            "assessor result files, the combined triangulation matrix and "
            "summaries, the row schema, and the derived-fields cache. All of "
            "these are deterministic functions of the S2 active baseline "
            "(see active_baseline_fingerprints in s2_quantitative/output/audit/) "
            "plus the assessor code at the current git HEAD."
        ),
        "generated_utc": timestamp,
        "file_count": len(s3_files),
        "files": s3_files,
    }
    s3_out = combined_out / "active_baseline_fingerprints.json"
    s3_out.write_text(json.dumps(s3_manifest, indent=2), encoding="utf-8")
    print(f"S3 fingerprints: {len(s3_files)} files -> {s3_out.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
