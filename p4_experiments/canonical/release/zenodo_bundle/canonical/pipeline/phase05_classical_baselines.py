"""Phase 5 - Classical baselines for the canonical P4 cohort.

PRE_REGISTRATION audit category J:
> Every label has a classical baseline with
>   `source: {paper_doi, page} OR {default_algorithm, default_source_doi, rationale}`.
> No baseline is marked `pending-citation` at audit time.

For each cohort label this script writes a `classical_baseline` dict. Paper-
stated baselines come from the genuine Phase 3 S2 quantitative extraction,
resolved by paper_id and experiment_id. If S2 does not name a baseline, the
script falls back to the canonical silo default.

The `metric_value` and `wall_clock_seconds` fields stay as PHASE_8_PENDING
placeholders; they are filled by the actual experimental run in Phase 8. Phase
5 is about citing the baseline, not measuring it.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from p4_experiments.canonical.data.s2_extraction_index import (
    s2_experiment,
    s2_extraction_path,
    s2_extraction_relpath,
    s2_extraction_sha256,
)

ROOT = Path(__file__).resolve().parents[3]
CANON = ROOT / "p4_experiments" / "canonical"
COHORT = CANON / "cohort.json"

DATE = datetime.now(timezone.utc).date().isoformat()
PHASE_TAG = "Phase 5 classical-baseline citation"

SILO_DEFAULT: dict[str, dict[str, str]] = {
    "derivative-pricing": {
        "default_algorithm": "Classical Monte Carlo for option pricing (Boyle 1977)",
        "default_source_doi": "10.1016/0304-405X(77)90005-8",
        "rationale": "Boyle 1977 is the canonical classical-MC baseline for derivative pricing across the QF literature; cited by Stamatopoulos et al. 2020, Egger et al. 2020, etc.",
    },
    "quantum-ml-finance": {
        "default_algorithm": "Classical SVM / kernel SVM (Cortes & Vapnik 1995)",
        "default_source_doi": "10.1007/BF00994018",
        "rationale": "Cortes-Vapnik kernel SVM is the canonical classical baseline for QSVM/QNN papers (Havlicek et al. 2019, Schuld 2021).",
    },
    "insurance-actuarial": {
        "default_algorithm": "Classical Monte Carlo for SCR (EIOPA 2014 Solvency II framework)",
        "default_source_doi": "10.2139/ssrn.2531094",
        "rationale": "Solvency II SCR computation under the EIOPA 2014 framework uses classical MC by regulatory mandate; the de-facto baseline for any quantum SCR proposal.",
    },
    "risk-management": {
        "default_algorithm": "Classical Monte Carlo VaR/CVaR (Glasserman 2003)",
        "default_source_doi": "10.1007/978-0-387-21617-1",
        "rationale": "Glasserman 2003 'Monte Carlo Methods in Financial Engineering' is the standard classical-MC reference for VaR/CVaR/credit-risk benchmarks.",
    },
    "fraud-detection": {
        "default_algorithm": "XGBoost (Chen & Guestrin 2016)",
        "default_source_doi": "10.1145/2939672.2939785",
        "rationale": "XGBoost is the canonical classical fraud-detection baseline cited by Q-DTN, QSVM-fraud, and quantum graph-neural-network papers.",
    },
    "portfolio-optimization": {
        "default_algorithm": "Classical convex QP / Markowitz mean-variance (Markowitz 1952)",
        "default_source_doi": "10.2307/2975974",
        "rationale": "Markowitz 1952 mean-variance QP is the canonical classical baseline for portfolio-optimization papers; QAOA/VQE-portfolio papers benchmark against CPLEX/Gurobi solving the same QP.",
    },
    "simulation-monte-carlo": {
        "default_algorithm": "Classical Monte Carlo (Glasserman 2003)",
        "default_source_doi": "10.1007/978-0-387-21617-1",
        "rationale": "Glasserman 2003 is the canonical classical-MC reference for QAE / QMCI papers (Stamatopoulos 2020, Brassard et al. 2002).",
    },
    "trading-execution": {
        "default_algorithm": "Classical Engle-Granger cointegration / matrix-factorization preselection",
        "default_source_doi": "10.2307/1913236",
        "rationale": "Engle-Granger 1987 cointegration test is the canonical classical baseline for statistical-arbitrage papers.",
    },
    "other": {
        "default_algorithm": "Classical Monte Carlo (Glasserman 2003)",
        "default_source_doi": "10.1007/978-0-387-21617-1",
        "rationale": "Generic fallback for cross-silo / methodological papers without a single dominant classical baseline.",
    },
}


def _has_value(value: Any) -> bool:
    return value not in (None, "", "NOT_STATED", "not_specified")


def _paper_baseline_evidence(baselines: list[dict[str, Any]]) -> str | None:
    if not baselines:
        return None
    return json.dumps(baselines[:5], sort_keys=True)


def _normalize_paper_baseline(experiment: dict[str, Any] | None, paper_doi: str | None) -> dict[str, Any] | None:
    if experiment is None:
        return None

    baselines = [
        baseline for baseline in (experiment.get("classical_baselines") or [])
        if _has_value(baseline.get("method_name"))
    ]
    if not baselines:
        return None

    method_names = []
    for baseline in baselines:
        method_name = baseline.get("method_name")
        if method_name not in method_names:
            method_names.append(method_name)
    algorithm_label = " + ".join(method_names[:3])
    if len(method_names) > 3:
        algorithm_label += f" + {len(method_names) - 3} more"

    complexity = (experiment.get("complexity_analysis") or {}).get("classical_complexity")
    return {
        "_status": "PHASE_5_LOCKED",
        "algorithm_label": algorithm_label,
        "reported_complexity": complexity if _has_value(complexity) else None,
        "source": {
            "type": "paper",
            "paper_doi": paper_doi,
            "paper_section": None,
            "rationale": "Classical baseline named in the P3 S2 quantitative extraction.",
        },
        "metric_value": "PHASE_8_PENDING",
        "wall_clock_seconds": "PHASE_8_PENDING",
        "extraction_evidence": _paper_baseline_evidence(baselines),
    }


def _silo_default_baseline(silo: str) -> dict[str, Any]:
    default = SILO_DEFAULT.get(silo, SILO_DEFAULT["other"])
    return {
        "_status": "PHASE_5_LOCKED",
        "algorithm_label": default["default_algorithm"],
        "reported_complexity": None,
        "source": {
            "type": "silo_default",
            "default_algorithm": default["default_algorithm"],
            "default_source_doi": default["default_source_doi"],
            "rationale": default["rationale"],
        },
        "metric_value": "PHASE_8_PENDING",
        "wall_clock_seconds": "PHASE_8_PENDING",
        "extraction_evidence": None,
    }


def main() -> int:
    cohort = json.loads(COHORT.read_text(encoding="utf-8"))
    labels = cohort["labels"]

    n = 0
    n_paper = 0
    n_default = 0
    per_silo_paper: dict[str, int] = {}
    per_silo_default: dict[str, int] = {}

    for label_id, entry in labels.items():
        n += 1
        experiment = s2_experiment(entry)
        ext_path = s2_extraction_path(entry)
        ext_sha = s2_extraction_sha256(entry) if ext_path.exists() else None
        ext_rel = s2_extraction_relpath(entry) if ext_path.exists() else None
        paper_doi = (entry.get("paper_metadata") or {}).get("doi")

        baseline = _normalize_paper_baseline(experiment, paper_doi)
        if baseline is None:
            baseline = _silo_default_baseline(entry["silo"])
            method = "silo_default_fallback"
            n_default += 1
            per_silo_default[entry["silo"]] = per_silo_default.get(entry["silo"], 0) + 1
        else:
            method = "paper_stated_p3_s2_verify"
            n_paper += 1
            per_silo_paper[entry["silo"]] = per_silo_paper.get(entry["silo"], 0) + 1

        if method == "paper_stated_p3_s2_verify":
            baseline["source"]["paper_id"] = entry.get("paper_id")
            baseline["source"]["experiment_id"] = entry.get("experiment_id")
            baseline["source"]["s2_extraction_path"] = ext_rel

        baseline["_phase5_provenance"] = {
            "method": method,
            "extraction_path": ext_rel,
            "extraction_sha256": ext_sha,
            "source_resolution": "paper_id + experiment_id",
            "generator_utc": datetime.now(timezone.utc).isoformat(),
        }

        entry["classical_baseline"] = baseline

        history = entry.setdefault("fidelity_history", [])
        history = [
            item for item in history
            if "Phase 5" not in (item.get("phase") or "")
        ]
        history.append({
            "date": DATE,
            "tier": entry.get("fidelity"),
            "rationale": (
                f"Phase 5 classical baseline locked. method={method}; "
                f"algorithm='{baseline['algorithm_label']}'; "
                f"source.type='{baseline['source']['type']}'."
            ),
            "phase": PHASE_TAG,
            "baseline_method": method,
            "baseline_algorithm": baseline["algorithm_label"],
            "baseline_source_type": baseline["source"]["type"],
        })
        entry["fidelity_history"] = history

    phase_status = cohort.get("_phase_status")
    if not isinstance(phase_status, dict):
        phase_status = {"_legacy": phase_status} if phase_status is not None else {}
    phase_status["phase5"] = {
        "status": "complete",
        "completed_utc": datetime.now(timezone.utc).isoformat(),
        "total_labels": n,
        "paper_stated_baselines": n_paper,
        "silo_default_baselines": n_default,
        "per_silo_paper": per_silo_paper,
        "per_silo_default": per_silo_default,
        "source_resolution": "P3 S2 paper_id + experiment_id",
    }
    cohort["_phase_status"] = phase_status

    COHORT.write_text(json.dumps(cohort, indent=2), encoding="utf-8")
    print(f"[Phase 5] cohort.json updated: {n} labels; paper-stated={n_paper}, silo-default={n_default}")
    print(f"[Phase 5] per-silo paper-stated:  {per_silo_paper}")
    print(f"[Phase 5] per-silo silo-default: {per_silo_default}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
