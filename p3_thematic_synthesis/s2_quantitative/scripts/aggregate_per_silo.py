"""
Per-silo aggregator for Phase 3 Stage 2 (benchmark extraction).

Reads all active per-paper extraction JSONs from
p3_thematic_synthesis/s2_quantitative/output/extractions/
and cross-tabs them against filtered S3 consensus verdicts to produce a single
per-silo summary JSON that feeds Chapter 6 silo sections (part iv:
quantitative footprint and quantum-advantage verdict).

Output: p3_thematic_synthesis/s2_quantitative/output/tables/per_silo_summary.json

Usage:
  python -m p3_thematic_synthesis.s2_quantitative.scripts.aggregate_per_silo

Per silo, computes:
- papers_with_experiments
- experiment_count
- algorithm_family_histogram
- qubits_distribution (min / p25 / median / p75 / max / n_reported)
- circuit_depth_distribution (same)
- hardware_type_histogram (simulator / device / not_specified)
- consensus_verdict_distribution (from s3 consensus_summary.filtered.json)
- majority_viable_rate
"""
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from statistics import median, quantiles
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
EXTRACTIONS_DIR = (
    ROOT
    / "p3_thematic_synthesis"
    / "s2_quantitative"
    / "output"
    / "extractions"
)
CONSENSUS_PATH = (
    ROOT
    / "p3_thematic_synthesis"
    / "s3_quantum_advantage"
    / "combined"
    / "output"
    / "consensus_summary.filtered.json"
)
OUT_DIR = ROOT / "p3_thematic_synthesis" / "s2_quantitative" / "output" / "tables"
OUT_PATH = OUT_DIR / "per_silo_summary.json"

# Canonical silo names (s3 uses hyphenated form)
SILOS = [
    "risk-management",
    "fraud-detection",
    "quantum-ml-finance",
    "trading-execution",
    "credit-lending",
    "derivative-pricing",
    "portfolio-optimization",
    "simulation-monte-carlo",
]


def _dist(values: list[float]) -> dict[str, Any]:
    """Return summary statistics for a numeric list; safe for empty/short lists."""
    vals = [v for v in values if v is not None]
    n = len(vals)
    if n == 0:
        return {"n_reported": 0}
    vals_sorted = sorted(vals)
    if n == 1:
        return {
            "n_reported": 1,
            "min": vals_sorted[0],
            "median": vals_sorted[0],
            "max": vals_sorted[0],
        }
    qs = quantiles(vals_sorted, n=4) if n >= 4 else [vals_sorted[0], median(vals_sorted), vals_sorted[-1]]
    return {
        "n_reported": n,
        "min": vals_sorted[0],
        "p25": qs[0],
        "median": median(vals_sorted),
        "p75": qs[-1],
        "max": vals_sorted[-1],
    }


def _silo_of(extraction: dict[str, Any]) -> str | None:
    fd = extraction.get("finance_domain") or {}
    return fd.get("primary_silo")


def _iter_extractions():
    for p in sorted(EXTRACTIONS_DIR.glob("*.json")):
        try:
            yield p, json.loads(p.read_text(encoding="utf-8"))
        except Exception as e:
            print(f"WARN: failed to read {p.name}: {e}")


def main() -> None:
    consensus = json.loads(CONSENSUS_PATH.read_text(encoding="utf-8"))
    by_silo_s3 = consensus.get("by_silo", {})

    acc: dict[str, dict[str, Any]] = {
        s: {
            "papers_with_experiments": set(),
            "experiment_count": 0,
            "algorithm_families": Counter(),
            "num_qubits": [],
            "circuit_depth": [],
            "circuit_depth_transpiled": [],
            "gate_count_total": [],
            "cnot_count": [],
            "t_count": [],
            "num_shots": [],
            "hardware_types": Counter(),
            "hardware_providers": Counter(),
        }
        for s in SILOS
    }

    total_files = 0
    skipped_silo = Counter()
    for path, d in _iter_extractions():
        total_files += 1
        silo = _silo_of(d)
        if silo not in acc:
            skipped_silo[silo or "UNKNOWN"] += 1
            continue
        if not d.get("has_quantitative_results"):
            continue
        experiments = d.get("experiments") or []
        if not experiments:
            continue
        pid = d.get("paper_id") or path.stem
        acc[silo]["papers_with_experiments"].add(pid)
        for e in experiments:
            acc[silo]["experiment_count"] += 1
            algo = (e.get("algorithm") or {}).get("family") or "unspecified"
            acc[silo]["algorithm_families"][algo] += 1
            qr = e.get("quantum_resources") or {}
            for field in (
                "num_qubits",
                "circuit_depth",
                "circuit_depth_transpiled",
                "gate_count_total",
                "cnot_count",
                "t_count",
                "num_shots",
            ):
                v = qr.get(field)
                if isinstance(v, (int, float)) and v > 0:
                    acc[silo][field].append(v)
            hw = e.get("hardware") or {}
            hw_type = hw.get("type") or "not_specified"
            if isinstance(hw_type, list):
                for t in hw_type:
                    acc[silo]["hardware_types"][str(t) or "not_specified"] += 1
            else:
                acc[silo]["hardware_types"][str(hw_type)] += 1
            provider = hw.get("provider")
            if isinstance(provider, list):
                for p in provider:
                    if p:
                        acc[silo]["hardware_providers"][str(p)] += 1
            elif provider:
                acc[silo]["hardware_providers"][str(provider)] += 1

    out: dict[str, Any] = {
        "generated_from": str(EXTRACTIONS_DIR.relative_to(ROOT)),
        "consensus_source": str(CONSENSUS_PATH.relative_to(ROOT)),
        "total_extraction_files_read": total_files,
        "silos_excluded_from_chapter": dict(skipped_silo),
        "chapter_total_experiments": sum(
            acc[s]["experiment_count"] for s in SILOS
        ),
        "by_silo": {},
    }

    for s in SILOS:
        a = acc[s]
        s3 = by_silo_s3.get(s, {})
        total_s3 = sum(s3.values()) if s3 else 0
        maj_viable = s3.get("majority_viable", 0)
        low_cov_viable = s3.get("low_coverage_viable", 0)
        out["by_silo"][s] = {
            "papers_with_experiments": len(a["papers_with_experiments"]),
            "experiment_count_s2": a["experiment_count"],
            "experiment_count_s3_triangulated": total_s3,
            "algorithm_family_histogram": dict(a["algorithm_families"].most_common()),
            "hardware_type_histogram": dict(a["hardware_types"].most_common()),
            "hardware_provider_histogram": dict(a["hardware_providers"].most_common(10)),
            "quantum_resources": {
                "num_qubits": _dist(a["num_qubits"]),
                "circuit_depth": _dist(a["circuit_depth"]),
                "circuit_depth_transpiled": _dist(a["circuit_depth_transpiled"]),
                "gate_count_total": _dist(a["gate_count_total"]),
                "cnot_count": _dist(a["cnot_count"]),
                "t_count": _dist(a["t_count"]),
                "num_shots": _dist(a["num_shots"]),
            },
            "consensus_verdicts": dict(s3),
            "majority_viable_rate": (
                round((maj_viable + low_cov_viable) / total_s3, 4)
                if total_s3
                else None
            ),
            "majority_viable_count": maj_viable,
            "low_coverage_viable_count": low_cov_viable,
        }

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"Wrote {OUT_PATH.relative_to(ROOT)}")
    print(
        f"Processed {total_files} extraction files; "
        f"{out['chapter_total_experiments']} experiments across {len(SILOS)} chapter silos."
    )
    if skipped_silo:
        print(f"Excluded-silo extractions skipped: {dict(skipped_silo)}")


if __name__ == "__main__":
    main()
