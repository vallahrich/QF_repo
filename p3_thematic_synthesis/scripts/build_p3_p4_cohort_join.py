"""Build a compact P3/P4 join artifact without rerunning any pipeline stage.

The output is an audit/navigation aid. It links each P4 cohort label to its
active S2 extraction row, S3 consensus row, B2 themes that cite the same paper,
and any existing Phase 9 H4 per-label metrics.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
P3 = ROOT / "p3_thematic_synthesis"

S2_EXTRACTIONS = P3 / "s2_quantitative" / "output" / "extractions"
S3_MATRIX = P3 / "s3_quantum_advantage" / "combined" / "output" / "triangulation_matrix.json"
S4_THEMES = P3 / "s4_thematic_coding"
P4_COHORT = ROOT / "p4_experiments" / "canonical" / "cohort.json"
P4_STATS = ROOT / "p4_experiments" / "canonical" / "reports" / "stats_report.json"
DEFAULT_OUT = P3 / "output" / "p3_p4_cohort_join.json"

STRICT_TIER = "paper-faithful-strict"
TEMPLATE_TIER = "paper-family-template"
PROXY_TIER = "proxy"


def _read_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def _rel(path: Path) -> str:
    return str(path.relative_to(ROOT)).replace("\\", "/")


def _s2_index() -> dict[tuple[str, str], dict[str, Any]]:
    rows: dict[tuple[str, str], dict[str, Any]] = {}
    for path in sorted(S2_EXTRACTIONS.glob("*.json")):
        data = _read_json(path, {})
        metadata = data.get("paper_metadata") or {}
        extraction_metadata = data.get("extraction_metadata") or {}
        paper_id = data.get("paper_id") or metadata.get("paper_id") or path.stem
        for exp in data.get("experiments") or []:
            experiment_id = exp.get("experiment_id")
            if not experiment_id:
                continue
            algo = exp.get("algorithm") or {}
            hardware = exp.get("hardware") or {}
            rows[(paper_id, experiment_id)] = {
                "path": _rel(path),
                "paper_title": metadata.get("title"),
                "paper_year": metadata.get("year"),
                "validation_passed": extraction_metadata.get("validation_passed"),
                "warning_count": int(extraction_metadata.get("validation_warnings") or 0),
                "algorithm_family": algo.get("family"),
                "algorithm_name": algo.get("name"),
                "hardware_type": hardware.get("type"),
            }
    return rows


def _s3_index() -> dict[tuple[str, str], dict[str, Any]]:
    rows: dict[tuple[str, str], dict[str, Any]] = {}
    data = _read_json(S3_MATRIX, [])
    for row in data if isinstance(data, list) else data.get("rows", []):
        paper_id = row.get("paper_id")
        experiment_id = row.get("experiment_id")
        if not paper_id or not experiment_id:
            continue
        rows[(paper_id, experiment_id)] = {
            "consensus_verdict": row.get("consensus_verdict"),
            "silo": row.get("silo"),
            "algorithm_family": row.get("algorithm_family"),
            "layers_scored": row.get("layers_scored"),
            "layers_total": row.get("layers_total"),
            "disagreement": row.get("disagreement"),
        }
    return rows


def _theme_index() -> dict[str, list[dict[str, Any]]]:
    by_paper: dict[str, list[dict[str, Any]]] = {}
    for path in sorted(S4_THEMES.glob("*/themes/b2_silo_themes.json")):
        data = _read_json(path, {})
        silo = data.get("silo") or path.parents[1].name
        output = data.get("output") or {}
        for kind in ("descriptive_themes", "analytical_themes"):
            for theme in output.get(kind) or []:
                item = {
                    "silo": silo,
                    "theme_kind": kind.replace("_themes", ""),
                    "theme_id": theme.get("theme_id"),
                    "theme_label": theme.get("theme_label"),
                }
                for paper_id in theme.get("supporting_papers") or []:
                    by_paper.setdefault(paper_id, []).append(item)
    return by_paper


def _h4_index() -> dict[str, dict[str, Any]]:
    stats = _read_json(P4_STATS, {})
    h4 = (((stats.get("H4") or {}).get("faithfulness_tier_sensitivity") or {}).get("tiers") or {})
    by_label: dict[str, dict[str, Any]] = {}
    for tier, block in h4.items():
        per_label = (((block or {}).get("per_criterion_breakdown") or {}).get("per_label") or {})
        for label, payload in per_label.items():
            by_label[label] = {"faithfulness_tier": tier, **payload}
    return by_label


def _p3_scope_status(cohort: dict[str, Any], entry: dict[str, Any]) -> str:
    disposition = cohort.get("_p3_scope_disposition") or {}
    silo = entry.get("silo")
    active_silos = set(disposition.get("in_scope_silos_in_cohort") or [])
    active_silos.update(disposition.get("in_scope_silos_with_zero_labels") or [])
    out_of_scope_silos = set((disposition.get("out_of_scope_silos_in_cohort") or {}).keys())
    if silo in active_silos:
        return "active_p3_silo"
    if silo in out_of_scope_silos:
        return "out_of_p3_scope_silo"
    return "p3_scope_not_declared"


def _theme_coverage_status(theme_rows: list[dict[str, Any]]) -> str:
    return "linked_to_b2_themes" if theme_rows else "no_b2_theme_link_for_paper"


def _h4_applicability(entry: dict[str, Any], h4_payload: dict[str, Any] | None) -> str:
    if h4_payload is not None:
        return "evaluated_in_h4"
    if not entry.get("phase8_runnable"):
        return "not_applicable_phase8_not_runnable"
    tier = entry.get("faithfulness_tier") or entry.get("paper_fidelity") or entry.get("fidelity")
    if tier == PROXY_TIER or entry.get("fidelity") == "P":
        return "not_applicable_proxy_tier"
    if tier == STRICT_TIER:
        return "missing_h4_for_strict_tier"
    if tier == TEMPLATE_TIER or entry.get("fidelity") == "F":
        return "missing_h4_for_template_tier"
    return "not_applicable_unknown_tier"


def _paper_exact_claim_eligibility(entry: dict[str, Any]) -> str:
    tier = entry.get("faithfulness_tier")
    if tier == STRICT_TIER:
        return "eligible_paper_exact"
    if tier == TEMPLATE_TIER:
        return "not_paper_exact_template_family_only"
    if tier == PROXY_TIER or entry.get("fidelity") == "P":
        return "not_paper_exact_proxy_only"
    return "not_paper_exact_unknown_tier"


def _why_s3_viable_not_h4(
    s3_payload: dict[str, Any] | None,
    h4_payload: dict[str, Any] | None,
    entry: dict[str, Any],
) -> str | None:
    verdict = (s3_payload or {}).get("consensus_verdict")
    if not verdict or "viable" not in str(verdict):
        return None
    if h4_payload is not None:
        return None
    applicability = _h4_applicability(entry, h4_payload)
    if applicability == "not_applicable_proxy_tier":
        return (
            "S3 viability is a literature/framework assessment. H4 is restricted "
            "to strict/template implementation tiers; this label is proxy-only."
        )
    if applicability == "not_applicable_phase8_not_runnable":
        return "S3 viable, but the P4 circuit was not Phase-8 runnable and therefore has no H4 row."
    if applicability.startswith("missing_h4"):
        return "S3 viable and non-proxy; missing H4 row should be audited."
    return "S3 viable, but H4 applicability is outside the current row scope."


def build_join() -> dict[str, Any]:
    cohort = _read_json(P4_COHORT, {})
    labels = cohort.get("labels") or {}
    s2 = _s2_index()
    s3 = _s3_index()
    themes = _theme_index()
    h4 = _h4_index()
    rows = []
    for label, entry in sorted(labels.items()):
        paper_id = entry.get("paper_id")
        experiment_id = entry.get("experiment_id")
        key = (paper_id, experiment_id)
        s2_payload = s2.get(key)
        s3_payload = s3.get(key)
        theme_rows = themes.get(paper_id, [])
        h4_payload = h4.get(label)
        h4_applicability = _h4_applicability(entry, h4_payload)
        rows.append({
            "label": label,
            "paper_id": paper_id,
            "experiment_id": experiment_id,
            "p3_scope_status": _p3_scope_status(cohort, entry),
            "s4_theme_coverage_status": _theme_coverage_status(theme_rows),
            "p4_h4_applicability": h4_applicability,
            "p4_faithfulness_tier": entry.get("faithfulness_tier"),
            "paper_exact_claim_eligibility": _paper_exact_claim_eligibility(entry),
            "why_s3_viable_not_h4": _why_s3_viable_not_h4(s3_payload, h4_payload, entry),
            "p4": {
                "silo": entry.get("silo"),
                "fidelity": entry.get("fidelity"),
                "faithfulness_tier": entry.get("faithfulness_tier"),
                "paper_fidelity": entry.get("paper_fidelity"),
                "phase8_runnable": entry.get("phase8_runnable"),
                "circuit_path": entry.get("circuit_path"),
            },
            "s2": s2_payload,
            "s3": s3_payload,
            "s4_themes": theme_rows,
            "p4_h4": h4_payload,
        })
    coverage = {
        "p3_scope_status": dict(sorted(Counter(row["p3_scope_status"] for row in rows).items())),
        "s4_theme_coverage_status": dict(sorted(Counter(row["s4_theme_coverage_status"] for row in rows).items())),
        "p4_h4_applicability": dict(sorted(Counter(row["p4_h4_applicability"] for row in rows).items())),
        "paper_exact_claim_eligibility": dict(sorted(Counter(row["paper_exact_claim_eligibility"] for row in rows).items())),
        "s3_viable_without_h4": sum(1 for row in rows if row["why_s3_viable_not_h4"]),
    }
    return {
        "schema_version": "p3_p4_cohort_join.1.1",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "inputs": {
            "p4_cohort": _rel(P4_COHORT),
            "s2_extractions": _rel(S2_EXTRACTIONS),
            "s3_triangulation_matrix": _rel(S3_MATRIX),
            "s4_theme_root": _rel(S4_THEMES),
            "p4_stats_report": _rel(P4_STATS),
        },
        "row_count": len(rows),
        "coverage": coverage,
        "missing": {
            "s2": sum(1 for row in rows if row["s2"] is None),
            "s3": sum(1 for row in rows if row["s3"] is None),
            "p4_h4": sum(1 for row in rows if row["p4_h4"] is None),
        },
        "rows": rows,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build P3/P4 cohort join artifact")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args(argv)
    payload = build_join()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {args.output.relative_to(ROOT)} ({payload['row_count']} rows)")
    print(f"missing: {payload['missing']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())