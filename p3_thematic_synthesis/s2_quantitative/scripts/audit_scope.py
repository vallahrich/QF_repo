"""Audit active S2 extractions for out-of-scope annealing/QUBO rows."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
S2_ROOT = ROOT / "p3_thematic_synthesis" / "s2_quantitative"
DEFAULT_EXTRACTIONS = S2_ROOT / "output" / "extractions"
DEFAULT_OUTPUT = S2_ROOT / "output" / "audit" / "raw_scope_audit.json"

SCOPE_OUT_FAMILIES = {"quantum-annealing", "quantum-annealing-qubo", "qubo"}
SCOPE_OUT_HARDWARE = {"quantum_annealer"}
SCOPE_OUT_TERMS = ("anneal", "qubo", "d-wave", "dwave")


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _norm(value: Any) -> str:
    return str(value or "").strip().lower()


def _scope_flags(exp: dict[str, Any]) -> tuple[list[str], list[str]]:
    hard_reasons: list[str] = []
    review_reasons: list[str] = []
    algorithm = exp.get("algorithm") or {}
    hardware = exp.get("hardware") or {}
    family = _norm(algorithm.get("family"))
    hardware_type = _norm(hardware.get("type"))
    haystack = " ".join(
        _norm(value)
        for value in (
            algorithm.get("name"),
            algorithm.get("family"),
            algorithm.get("variant"),
            hardware.get("type"),
            hardware.get("platform"),
            exp.get("benchmark_task"),
        )
    )
    if family in SCOPE_OUT_FAMILIES:
        hard_reasons.append(f"algorithm.family={family}")
    if hardware_type in SCOPE_OUT_HARDWARE:
        hard_reasons.append(f"hardware.type={hardware_type}")
    for term in SCOPE_OUT_TERMS:
        if term in haystack:
            review_reasons.append(f"scope_term={term}")
    return sorted(set(hard_reasons)), sorted(set(review_reasons))


def audit(extractions: Path) -> dict[str, Any]:
    files = sorted(extractions.glob("*.json"))
    violations = []
    review_hits = []
    validation_failed_files = 0
    warning_count = 0
    experiment_count = 0
    for path in files:
        data = _read_json(path)
        paper_id = data.get("paper_id") or (data.get("paper_metadata") or {}).get("paper_id") or path.stem
        validation = data.get("extraction_metadata") or {}
        if validation.get("validation_passed") is False:
            validation_failed_files += 1
        warning_count += int(validation.get("validation_warnings") or 0)
        for exp in data.get("experiments") or []:
            experiment_count += 1
            hard_reasons, review_reasons = _scope_flags(exp)
            if hard_reasons:
                violations.append({
                    "paper_id": paper_id,
                    "experiment_id": exp.get("experiment_id"),
                    "path": str(path.relative_to(ROOT)).replace("\\", "/"),
                    "reasons": hard_reasons,
                })
            if review_reasons:
                review_hits.append({
                    "paper_id": paper_id,
                    "experiment_id": exp.get("experiment_id"),
                    "path": str(path.relative_to(ROOT)).replace("\\", "/"),
                    "reasons": review_reasons,
                })
    return {
        "schema_version": "s2_scope_audit.1.0",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "extractions_dir": str(extractions.relative_to(ROOT)).replace("\\", "/"),
        "file_count": len(files),
        "experiment_count": experiment_count,
        "validation_failed_files": validation_failed_files,
        "warning_count": warning_count,
        "scope_out_family_terms": sorted(SCOPE_OUT_FAMILIES),
        "scope_out_hardware_terms": sorted(SCOPE_OUT_HARDWARE),
        "scope_out_text_terms": sorted(SCOPE_OUT_TERMS),
        "violation_count": len(violations),
        "violations": violations,
        "review_hit_count": len(review_hits),
        "review_hits": review_hits,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Audit S2 extractions for gate-based scope violations")
    parser.add_argument("--extractions", type=Path, default=DEFAULT_EXTRACTIONS)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--fail-on-violation", action="store_true")
    args = parser.parse_args(argv)
    payload = audit(args.extractions)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {args.output.relative_to(ROOT)}")
    print(
        f"files={payload['file_count']} experiments={payload['experiment_count']} "
        f"violations={payload['violation_count']} validation_failed_files={payload['validation_failed_files']}"
    )
    return 1 if args.fail_on_violation and payload["violation_count"] else 0


if __name__ == "__main__":
    raise SystemExit(main())