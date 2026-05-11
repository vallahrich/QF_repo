"""Phase 9 - Statistical analysis pipeline (H1, H2, H3, H4 + sensitivity).

Reads ``p4_experiments/common/output/results/*.json`` and produces:

  - ``stats_report.json``   : per-hypothesis test result + effect size + 95% CI.
  - ``oracle_tax_table.json``: per-label per-cell tau ratios.
  - ``sensitivity_grid.json``: H4 across tau-thresholds and +/-10x baseline perturbations.

Hypotheses (per PRE_REGISTRATION sec 3, immutable after sign-off):
  H1: median oracle tax > 10x at every (profile, eps) cell.
       Test: per-axis one-sided Wilcoxon signed-rank; H0: median <= 1.
       Accept iff p<0.05 AND Cliff's delta>0.33 AND bootstrap 95% CI
       on median strictly above 1.
  H2: oracle tax distribution differs by silo.
       Test: Kruskal-Wallis omnibus + per-pair Mann-Whitney with
       Holm-Bonferroni; >=1 surviving pair with rank-biserial>0.33.
  H3: oracle tax differs by hardware profile.
       Test: Friedman (blocked by label) + Kendall's W >= 0.10.
  H4: strict-H4 subset = labels satisfying ALL 5 criteria at the H4
       anchor cell (maj_e6_floquet, eps=1e-4, full). Predicted: empty.

Sub-cohorts (per sec 6.4):
    Faithful (F)            : headline H4 (13 current labels).
  Faithful + LLM-resolved : sensitivity (none promoted in canonical pipeline; identical to F).
    Full N=71               : appendix.

Sensitivity grid:
  tau in {3, 10, 30, 100}; baseline +/-10x; SEED in {SEED, +1, +2, +3}.

Schema: see stats_report.schema.json (TODO Phase 9 cleanup).

Note: this script will refuse to compute statistics on an incomplete
result set. Run audit_phase8.py first to confirm all expected records are present.
"""

from __future__ import annotations

import json
import math
import re
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
CANON = ROOT / "p4_experiments" / "canonical"
COHORT = CANON / "cohort.json"
RESULTS = ROOT / "p4_experiments" / "common" / "output" / "results"
REPORTS = CANON / "reports"
ORACLE_TAX_TABLE = REPORTS / "oracle_tax_table.json"
STATS_REPORT = REPORTS / "stats_report.json"
SENSITIVITY = REPORTS / "sensitivity_grid.json"
EVIDENCE_REPORT = REPORTS / "evidence_report.json"
PHASE8D_DIR = CANON / "outputs" / "phase08d_qae_hhl_scout"
PHASE8D_SUMMARY = PHASE8D_DIR / "summary.json"
PHASE8D_STATUS = PHASE8D_DIR / "phase8d_status.json"
VINCENT_REVIEW_DIR = ROOT / "p4_experiments" / "experiments" / "review" / "phase8_faithfulness_review" / "vincent"

PROFILES = [
    "sc_e3_surface", "sc_e4_surface",
    "ti_e3_surface", "ti_e4_surface",
    "maj_e6_surface", "maj_e6_floquet",
]
EPSILONS = [1e-3, 1e-4, 1e-6]
MODES = ["bare", "full"]
EXPECTED_PER_LABEL = len(PROFILES) * len(EPSILONS) * len(MODES)
RESOURCE_AXES = ["logical_qubits", "t_count", "t_depth", "runtime_seconds"]

H4_ANCHOR_PROFILE = "maj_e6_floquet"
H4_ANCHOR_EPS = 1e-4
H4_TAU_GRID = [3, 10, 30, 100]

STRICT_TIER = "paper-faithful-strict"
TEMPLATE_TIER = "paper-family-template"
PROXY_TIER = "proxy"
FAITHFULNESS_TIER_DEFINITIONS = {
    STRICT_TIER: (
        "Paper-exact headline tier: circuit label/source match the cohort entry, "
        "the implementation does not self-disclaim paper faithfulness, and the "
        "faithfulness review has no material drift. No current label is promoted "
        "to this tier without an explicit implementation audit."
    ),
    TEMPLATE_TIER: (
        "Family/scale-faithful template tier: the label remains headline-eligible "
        "for the preregistered S2-backed F/P analysis, but the measured circuit is "
        "a template or family proxy rather than a paper-exact implementation."
    ),
    PROXY_TIER: (
        "Proxy-declared labels outside the reviewed Faithful set; appendix-only "
        "for H4 exploratory lead generation."
    ),
}

# Canonical SEED (PRE_REGISTRATION sec 2.6) and the SEED-robustness grid
# promised in the module docstring (line 28) and PRE_REGISTRATION sec 6.5.
# Only the H1 bootstrap CI is RNG-driven; H3 (Friedman/Kendall's W) and
# H4 (deterministic threshold checks) are seed-invariant by construction.
SEED = 0x50414D50
SEED_GRID = [SEED, SEED + 1, SEED + 2, SEED + 3]
P3_H2_SCOPE_AMENDMENT = "2026-04-28 active P3 problem-domain silos only"


def _p3_scope_disposition(cohort: dict) -> dict:
    disposition = cohort.get("_p3_scope_disposition") or {}
    in_scope_silos = set(disposition.get("in_scope_silos_in_cohort") or [])
    zero_label_silos = set(disposition.get("in_scope_silos_with_zero_labels") or [])
    out_of_scope_silos = set((disposition.get("out_of_scope_silos_in_cohort") or {}).keys())
    active_p3_silos = in_scope_silos | zero_label_silos
    if not active_p3_silos:
        active_p3_silos = {
            entry.get("silo")
            for entry in (cohort.get("labels") or {}).values()
            if entry.get("silo") and entry.get("silo") not in out_of_scope_silos
        }
    return {
        "active_p3_silos": active_p3_silos,
        "in_scope_silos_in_cohort": in_scope_silos,
        "zero_label_silos": zero_label_silos,
        "out_of_scope_silos": out_of_scope_silos,
    }


def _scope_payload(scope: dict, excluded_by_scope: dict[str, list[str]]) -> dict:
    return {
        "scope_rule": P3_H2_SCOPE_AMENDMENT,
        "scope_source": "cohort._p3_scope_disposition checked against shared/config/silo_inclusion.json by audit_phase03.K3",
        "active_p3_silos": sorted(scope["active_p3_silos"]),
        "in_scope_silos_with_zero_labels": sorted(scope["zero_label_silos"]),
        "out_of_scope_silos_excluded": sorted(scope["out_of_scope_silos"]),
        "out_of_scope_observations_excluded": {
            silo_name: sorted(labels)
            for silo_name, labels in sorted(excluded_by_scope.items())
        },
        "n_excluded_out_of_p3_scope": sum(len(labels) for labels in excluded_by_scope.values()),
    }


def _load_records() -> list[dict]:
    if not RESULTS.exists():
        return []
    out = []
    for p in RESULTS.glob("*.json"):
        try:
            out.append(json.loads(p.read_text(encoding="utf-8")))
        except Exception:
            continue
    return out


def _expected_filename(label: str, profile: str, eps: float, mode: str) -> str:
    return f"{label}_{profile}_eps{eps:.0e}_{mode}.json"


def _ensure_phase8_complete(cohort: dict) -> None:
    """Refuse to run Phase 9 on partial Phase 8 output."""
    p8 = (cohort.get("_phase_status") or {}).get("phase8") or {}
    labels = sorted(cohort["labels"].keys())
    expected = {
        _expected_filename(label, profile, eps, mode)
        for label in labels
        for profile in PROFILES
        for eps in EPSILONS
        for mode in MODES
    }
    found = {path.name for path in RESULTS.glob("*.json")} if RESULTS.exists() else set()
    missing = sorted(expected - found)
    extra = sorted(found - expected)
    if p8.get("status") != "complete" or missing or extra:
        raise SystemExit(
            "Phase 9 requires finalized complete Phase 8 results. "
            f"phase8.status={p8.get('status')!r}; "
            f"records={len(found)}/{len(expected)}; "
            f"missing={len(missing)}; extra={len(extra)}. "
            "After the VMs finish, run Sync-Results.ps1 -CleanDestination "
            "and audit_phase8.py first."
        )


def _index(records: list[dict]) -> dict:
    """label -> profile -> eps -> mode -> measured."""
    idx: dict = defaultdict(lambda: defaultdict(lambda: defaultdict(dict)))
    for r in records:
        lid = r.get("label")
        prof = r.get("hardware_profile")
        eps = r.get("epsilon")
        mode = r.get("accounting_mode")
        if not all([lid, prof, eps, mode]):
            continue
        idx[lid][prof][eps][mode] = r
    return idx


def _oracle_tax(idx: dict, faithful_only: set[str] | None = None) -> dict:
    """Build per-cell tau_full_vs_bare for each resource axis."""
    table: dict = {}
    for lid, byprof in idx.items():
        if faithful_only is not None and lid not in faithful_only:
            continue
        table[lid] = {}
        for prof, byeps in byprof.items():
            for eps, bymode in byeps.items():
                bare = (bymode.get("bare") or {}).get("measured") or {}
                full = (bymode.get("full") or {}).get("measured") or {}
                if bare.get("status") == "engine_failure" or full.get("status") == "engine_failure":
                    continue
                key = f"{prof}|{eps:.0e}"
                taus = {}
                for axis in RESOURCE_AXES:
                    b = bare.get(axis)
                    f = full.get(axis)
                    if isinstance(b, (int, float)) and isinstance(f, (int, float)) and b > 0:
                        taus[axis] = f / b
                if taus:
                    table[lid][key] = taus
    return table


def _resolve_baseline_paper_named(cohort: dict, lid: str) -> float | None:
    """Default baseline resolver: paper-named classical wall-clock from Phase 8b."""
    cb = (cohort["labels"].get(lid) or {}).get("classical_baseline") or {}
    c_wc = cb.get("wall_clock_seconds")
    return c_wc if isinstance(c_wc, (int, float)) else None


def _resolve_baseline_strongest_of_top3(cohort: dict, lid: str) -> float | None:
    """Sensitivity baseline resolver: strongest-of-3 silo-default classical
    wall-clock from Phase 8c (min over rank1/rank2/rank3 medians).

    This is the *harder* test for quantum advantage: even if the paper's
    chosen classical baseline is slow, can the quantum approach still beat
    the best silo-default classical method?
    """
    alt = (cohort.get("classical_alternatives_top3") or {}).get(lid) or {}
    candidates = [
        v.get("wall_clock_seconds_median")
        for v in alt.values()
        if isinstance(v, dict) and isinstance(v.get("wall_clock_seconds_median"), (int, float))
    ]
    return float(min(candidates)) if candidates else None


def _faithfulness_tier(entry: dict) -> str:
    tier = entry.get("faithfulness_tier")
    if isinstance(tier, str) and tier:
        return tier
    if entry.get("fidelity") == "P" or entry.get("paper_fidelity") == "proxy":
        return PROXY_TIER
    if entry.get("paper_fidelity") == STRICT_TIER:
        return STRICT_TIER
    return TEMPLATE_TIER


def _faithfulness_tier_sets(cohort: dict) -> dict[str, set[str]]:
    tiers: dict[str, set[str]] = {STRICT_TIER: set(), TEMPLATE_TIER: set(), PROXY_TIER: set()}
    for label, entry in cohort["labels"].items():
        tiers.setdefault(_faithfulness_tier(entry), set()).add(label)
    return tiers


def _faithfulness_tier_summary(cohort: dict) -> dict:
    tiers = _faithfulness_tier_sets(cohort)
    paper_fidelity_counts: dict[str, int] = {}
    review_verdict_counts: dict[str, int] = {}
    for entry in cohort["labels"].values():
        pf = entry.get("paper_fidelity", "<missing>")
        paper_fidelity_counts[pf] = paper_fidelity_counts.get(pf, 0) + 1
        verdict = entry.get("faithfulness_review_verdict")
        if verdict:
            review_verdict_counts[verdict] = review_verdict_counts.get(verdict, 0) + 1
    return {
        "definitions": FAITHFULNESS_TIER_DEFINITIONS,
        "counts": {tier: len(labels) for tier, labels in sorted(tiers.items())},
        "labels_by_tier": {tier: sorted(labels) for tier, labels in sorted(tiers.items())},
        "paper_fidelity_counts": dict(sorted(paper_fidelity_counts.items())),
        "faithfulness_review_verdict_counts": dict(sorted(review_verdict_counts.items())),
        "strict_tier_empty_is_evidence": len(tiers.get(STRICT_TIER, set())) == 0,
        "interpretation_note": (
            "The legacy F/P split is retained for preregistered H1-H4 continuity. "
            "The faithfulness_tier layer prevents the word Faithful from implying "
            "paper-exact implementation when the measured circuit is a template."
        ),
    }


def _vincent_review_verdicts(cohort: dict) -> dict:
    out: dict[str, dict] = {}
    for label, entry in sorted(cohort["labels"].items()):
        if entry.get("fidelity") != "F":
            continue
        path = VINCENT_REVIEW_DIR / f"{label}.md"
        payload = {
            "review_path": str(path.relative_to(ROOT)).replace("\\", "/"),
            "present": path.exists(),
            "verdict": entry.get("faithfulness_review_verdict"),
        }
        if path.exists():
            text = path.read_text(encoding="utf-8", errors="replace")
            match = re.search(r"\*\*Verdict:\*\*\s*\*\*([^*]+)\*\*", text)
            payload["verdict"] = match.group(1).strip() if match else payload["verdict"]
            payload["review_disclaims_paper_exact"] = "does NOT implement" in text
        out[label] = payload
    counts: dict[str, int] = {}
    for payload in out.values():
        verdict = payload.get("verdict") or "<missing>"
        counts[verdict] = counts.get(verdict, 0) + 1
    return {"counts": dict(sorted(counts.items())), "labels": out}


def _raw_logical_counts(measured: dict) -> dict:
    raw = measured.get("raw_estimate") or {}
    return raw.get("logicalCounts") or {}


def _raw_physical_breakdown(measured: dict) -> dict:
    raw = measured.get("raw_estimate") or {}
    return ((raw.get("physicalCounts") or {}).get("breakdown") or {})


def _qdk_magic_metrics(bare_rec: dict, full_rec: dict) -> dict:
    bare_logical = _raw_logical_counts(bare_rec)
    full_logical = _raw_logical_counts(full_rec)
    bare_breakdown = _raw_physical_breakdown(bare_rec)
    full_breakdown = _raw_physical_breakdown(full_rec)

    def num(value: object) -> float | None:
        return float(value) if isinstance(value, (int, float)) else None

    metrics = {
        "bare_t_count": num(bare_rec.get("t_count")),
        "full_t_count": num(full_rec.get("t_count")),
        "bare_rotation_count": num(bare_logical.get("rotationCount")),
        "full_rotation_count": num(full_logical.get("rotationCount")),
        "bare_rotation_depth": num(bare_logical.get("rotationDepth")),
        "full_rotation_depth": num(full_logical.get("rotationDepth")),
        "bare_num_tstates": num(bare_breakdown.get("numTstates")),
        "full_num_tstates": num(full_breakdown.get("numTstates")),
    }
    for name in ["t_count", "rotation_count", "rotation_depth", "num_tstates"]:
        b = metrics.get(f"bare_{name}")
        f = metrics.get(f"full_{name}")
        metrics[f"delta_{name}"] = (f - b) if b is not None and f is not None else None
    deltas = [
        metrics.get("delta_t_count"),
        metrics.get("delta_rotation_count"),
        metrics.get("delta_rotation_depth"),
        metrics.get("delta_num_tstates"),
    ]
    metrics["qdk_magic_delta_positive"] = any(
        isinstance(value, (int, float)) and value > 0 for value in deltas
    )
    return metrics


def _phase8b_non_exact_baselines(cohort: dict, faithful: set[str]) -> set[str]:
    out: set[str] = set()
    for label in faithful:
        cb = (cohort["labels"].get(label) or {}).get("classical_baseline") or {}
        prov = cb.get("_phase8b_provenance") or {}
        relationship = prov.get("baseline_relationship")
        if relationship and relationship != "paper_named_exact":
            out.add(label)
    return out


def _h4_subset(idx: dict, faithful: set[str], cohort: dict, tau_threshold: float = 10.0,
               baseline_scale: float = 1.0, baseline_resolver=None) -> list[str]:
    """Strict-H4 subset construction at the canonical anchor cell.

    ``baseline_resolver(cohort, lid) -> float | None`` chooses which
    classical wall-clock comparator to use. Defaults to the paper-named
    Phase 8b baseline; the Phase 8c top-3 sensitivity passes
    ``_resolve_baseline_strongest_of_top3``.
    """
    if baseline_resolver is None:
        baseline_resolver = _resolve_baseline_paper_named
    winners = []
    for lid in faithful:
        bare = ((idx.get(lid) or {}).get(H4_ANCHOR_PROFILE) or {}).get(H4_ANCHOR_EPS) or {}
        full_rec = (bare.get("full") or {}).get("measured") or {}
        bare_rec = (bare.get("bare") or {}).get("measured") or {}
        if not full_rec or not bare_rec:
            continue
        if full_rec.get("status") == "engine_failure" or bare_rec.get("status") == "engine_failure":
            continue
        b_rt = bare_rec.get("runtime_seconds")
        f_rt = full_rec.get("runtime_seconds")
        b_td = bare_rec.get("t_depth")
        f_td = full_rec.get("t_depth")
        f_tc = full_rec.get("t_count")
        if not all(isinstance(x, (int, float)) for x in [b_rt, f_rt, b_td, f_td, f_tc]):
            continue
        if b_rt <= 0 or b_td <= 0:
            continue
        tau_runtime = f_rt / b_rt
        tau_tdepth = f_td / b_td

        c_wc = baseline_resolver(cohort, lid)
        if c_wc is None:
            continue  # PHASE_8_PENDING placeholders skip the headline test
        c_wc_eff = c_wc * baseline_scale

        criteria = [
            tau_runtime < tau_threshold,
            f_rt < c_wc_eff,
            f_tc > 0,
            tau_tdepth >= tau_threshold,
            c_wc_eff >= 0.01,
        ]
        if all(criteria):
            winners.append(lid)
    return winners


# Pre-registered names for the 5 H4 criteria (kept in sync with _h4_subset)
H4_CRITERIA_NAMES = (
    "C1_tau_runtime_lt_10",          # tau_runtime < tau_threshold (default 10)
    "C2_full_runtime_lt_baseline",   # full_runtime < classical_baseline
    "C3_full_t_count_gt_0",          # oracle is non-trivial in T-count
    "C4_tau_tdepth_ge_10",           # oracle costs survive in T-depth
    "C5_baseline_ge_0_01s",          # classical baseline non-toy
)


def _h4_per_label_scoreboard(
    idx: dict, faithful: set[str], cohort: dict,
    tau_threshold: float = 10.0, baseline_scale: float = 1.0,
) -> dict:
    """Return per-label PASS/FAIL across the 5 H4 criteria + per-criterion totals.

    This is the 'transparency table' that lets a reviewer audit why a
    Faithful label fails the strict subset (e.g. "SR1 fails on C1
    only"). Pre-registered in PRE_REGISTRATION sec 3.4 and required by
    the audit (academic-rigor pass 2026-04-19).
    """
    per_label: dict[str, dict] = {}
    failure_counts: dict[str, int] = {name: 0 for name in H4_CRITERIA_NAMES}
    excluded_no_data: list[str] = []
    excluded_no_baseline: list[str] = []

    for lid in sorted(faithful):
        bare = ((idx.get(lid) or {}).get(H4_ANCHOR_PROFILE) or {}).get(H4_ANCHOR_EPS) or {}
        full_rec = (bare.get("full") or {}).get("measured") or {}
        bare_rec = (bare.get("bare") or {}).get("measured") or {}
        if (not full_rec or not bare_rec
                or full_rec.get("status") == "engine_failure"
                or bare_rec.get("status") == "engine_failure"):
            excluded_no_data.append(lid)
            continue

        b_rt = bare_rec.get("runtime_seconds")
        f_rt = full_rec.get("runtime_seconds")
        b_td = bare_rec.get("t_depth")
        f_td = full_rec.get("t_depth")
        f_tc = full_rec.get("t_count")
        if not all(isinstance(x, (int, float)) for x in [b_rt, f_rt, b_td, f_td, f_tc]):
            excluded_no_data.append(lid)
            continue
        if b_rt <= 0 or b_td <= 0:
            excluded_no_data.append(lid)
            continue

        cb = (cohort["labels"].get(lid) or {}).get("classical_baseline") or {}
        c_wc = cb.get("wall_clock_seconds")
        if not isinstance(c_wc, (int, float)):
            excluded_no_baseline.append(lid)
            continue
        c_wc_eff = c_wc * baseline_scale

        tau_runtime = f_rt / b_rt
        tau_tdepth = f_td / b_td

        criteria_results = {
            "C1_tau_runtime_lt_10": bool(tau_runtime < tau_threshold),
            "C2_full_runtime_lt_baseline": bool(f_rt < c_wc_eff),
            "C3_full_t_count_gt_0": bool(f_tc > 0),
            "C4_tau_tdepth_ge_10": bool(tau_tdepth >= tau_threshold),
            "C5_baseline_ge_0_01s": bool(c_wc_eff >= 0.01),
        }
        qdk_magic = _qdk_magic_metrics(bare_rec, full_rec)
        for name, passed in criteria_results.items():
            if not passed:
                failure_counts[name] += 1

        per_label[lid] = {
            "metrics": {
                "tau_runtime": float(tau_runtime),
                "full_runtime_seconds": float(f_rt),
                "bare_runtime_seconds": float(b_rt),
                "tau_t_depth": float(tau_tdepth),
                "full_t_count": float(f_tc),
                "classical_baseline_seconds": float(c_wc_eff),
                "qdk_magic": qdk_magic,
            },
            "criteria": criteria_results,
            "criteria_qdk_nontriviality": {
                **criteria_results,
                "C3_qdk_magic_delta_gt_0": bool(qdk_magic.get("qdk_magic_delta_positive")),
            },
            "n_criteria_passed": sum(criteria_results.values()),
            "passes_all": all(criteria_results.values()),
            "failed_criteria": [k for k, v in criteria_results.items() if not v],
        }

    n_evaluated = len(per_label)
    return {
        "tau_threshold": tau_threshold,
        "baseline_scale": baseline_scale,
        "criteria_definitions": {
            "C1_tau_runtime_lt_10": "tau_runtime = full_runtime / bare_runtime < tau_threshold",
            "C2_full_runtime_lt_baseline": "full_runtime < classical_baseline_seconds",
            "C3_full_t_count_gt_0": "full T-count > 0 (oracle is non-trivial)",
            "C4_tau_tdepth_ge_10": "tau_t_depth = full_t_depth / bare_t_depth >= tau_threshold",
            "C5_baseline_ge_0_01s": "classical_baseline_seconds >= 0.01 (not toy-scale)",
        },
        "n_faithful": len(faithful),
        "n_evaluated": n_evaluated,
        "n_excluded_no_re_data": len(excluded_no_data),
        "n_excluded_no_classical_baseline": len(excluded_no_baseline),
        "excluded_no_re_data": excluded_no_data,
        "excluded_no_classical_baseline": excluded_no_baseline,
        "per_criterion_failure_counts": failure_counts,
        "per_criterion_failure_rate": {
            name: (failure_counts[name] / n_evaluated if n_evaluated else None)
            for name in H4_CRITERIA_NAMES
        },
        "per_label": per_label,
    }


def _h4_subset_qdk_nontriviality(
    idx: dict,
    faithful: set[str],
    cohort: dict,
    tau_threshold: float = 10.0,
    baseline_scale: float = 1.0,
    baseline_resolver=None,
) -> list[str]:
    if baseline_resolver is None:
        baseline_resolver = _resolve_baseline_paper_named
    winners = []
    for lid in faithful:
        bare = ((idx.get(lid) or {}).get(H4_ANCHOR_PROFILE) or {}).get(H4_ANCHOR_EPS) or {}
        full_rec = (bare.get("full") or {}).get("measured") or {}
        bare_rec = (bare.get("bare") or {}).get("measured") or {}
        if not full_rec or not bare_rec:
            continue
        if full_rec.get("status") == "engine_failure" or bare_rec.get("status") == "engine_failure":
            continue
        b_rt = bare_rec.get("runtime_seconds")
        f_rt = full_rec.get("runtime_seconds")
        b_td = bare_rec.get("t_depth")
        f_td = full_rec.get("t_depth")
        if not all(isinstance(x, (int, float)) for x in [b_rt, f_rt, b_td, f_td]):
            continue
        if b_rt <= 0 or b_td <= 0:
            continue
        c_wc = baseline_resolver(cohort, lid)
        if c_wc is None:
            continue
        c_wc_eff = c_wc * baseline_scale
        qdk_magic = _qdk_magic_metrics(bare_rec, full_rec)
        criteria = [
            f_rt / b_rt < tau_threshold,
            f_rt < c_wc_eff,
            bool(qdk_magic.get("qdk_magic_delta_positive")),
            f_td / b_td >= tau_threshold,
            c_wc_eff >= 0.01,
        ]
        if all(criteria):
            winners.append(lid)
    return winners


def _h4_qdk_nontriviality_sensitivity(idx: dict, faithful: set[str], cohort: dict) -> dict:
    scoreboard = _h4_per_label_scoreboard(idx, faithful, cohort, tau_threshold=10.0)
    per_label = {}
    failure_counts = {
        "C1_tau_runtime_lt_10": 0,
        "C2_full_runtime_lt_baseline": 0,
        "C3_qdk_magic_delta_gt_0": 0,
        "C4_tau_tdepth_ge_10": 0,
        "C5_baseline_ge_0_01s": 0,
    }
    for label, payload in (scoreboard.get("per_label") or {}).items():
        criteria = payload.get("criteria_qdk_nontriviality") or {}
        criteria = {
            "C1_tau_runtime_lt_10": criteria.get("C1_tau_runtime_lt_10"),
            "C2_full_runtime_lt_baseline": criteria.get("C2_full_runtime_lt_baseline"),
            "C3_qdk_magic_delta_gt_0": criteria.get("C3_qdk_magic_delta_gt_0"),
            "C4_tau_tdepth_ge_10": criteria.get("C4_tau_tdepth_ge_10"),
            "C5_baseline_ge_0_01s": criteria.get("C5_baseline_ge_0_01s"),
        }
        for name, passed in criteria.items():
            if not passed:
                failure_counts[name] += 1
        per_label[label] = {
            "criteria": criteria,
            "passes_all": all(criteria.values()),
            "failed_criteria": [k for k, v in criteria.items() if not v],
            "metrics": payload.get("metrics") or {},
        }
    winners = sorted(label for label, payload in per_label.items() if payload.get("passes_all"))
    return {
        "description": (
            "Sensitivity replacing C3 full_t_count > 0 with a QDK-aware magic-state "
            "delta check: full mode must increase logical T count, arbitrary rotation "
            "count/depth, or QDK numTstates relative to bare mode. This does not mutate "
            "the preregistered H4 result."
        ),
        "canonical_winners": winners,
        "canonical_winners_count": len(winners),
        "per_criterion_failure_counts": failure_counts,
        "per_label": per_label,
        "direct_subset_recompute": _h4_subset_qdk_nontriviality(idx, faithful, cohort),
    }


def _h4_faithfulness_tier_sensitivity(idx: dict, faithful: set[str], cohort: dict) -> dict:
    tiers = _faithfulness_tier_sets(cohort)
    out: dict[str, dict] = {}
    for tier in [STRICT_TIER, TEMPLATE_TIER]:
        labels = tiers.get(tier, set()) & faithful
        winners = _h4_subset(idx, labels, cohort, tau_threshold=10.0)
        out[tier] = {
            "labels": sorted(labels),
            "subcohort_size": len(labels),
            "canonical_winners": winners,
            "canonical_winners_count": len(winners),
            "per_criterion_breakdown": _h4_per_label_scoreboard(idx, labels, cohort, tau_threshold=10.0),
        }
    return {
        "definitions": FAITHFULNESS_TIER_DEFINITIONS,
        "tiers": out,
        "strict_tier_empty_is_evidence": len(out.get(STRICT_TIER, {}).get("labels") or []) == 0,
    }


def _h4_leave_one_out(idx: dict, faithful: set[str], cohort: dict) -> list[dict]:
    rows = []
    for omitted in sorted(faithful):
        labels = set(faithful) - {omitted}
        winners = _h4_subset(idx, labels, cohort, tau_threshold=10.0)
        winners_qdk = _h4_subset_qdk_nontriviality(idx, labels, cohort, tau_threshold=10.0)
        rows.append({
            "omitted_label": omitted,
            "subcohort_size": len(labels),
            "canonical_winners": winners,
            "canonical_winners_count": len(winners),
            "qdk_nontriviality_winners": winners_qdk,
            "qdk_nontriviality_winners_count": len(winners_qdk),
        })
    return rows


def _try_scipy() -> Any:
    try:
        import scipy.stats as st
        return st
    except ImportError:
        return None


# ---------------------------------------------------------------------------
# Effect-size and bootstrap helpers (added 2026-04-19 academic-rigor pass)
# ---------------------------------------------------------------------------

def _cliffs_delta(xs: list[float], threshold: float = 0.0) -> float:
    """Cliff's delta for one-sample test against a constant ``threshold``.

    delta = (#{x > threshold} - #{x < threshold}) / n. Range [-1, 1].
    Pre-registered acceptance for H1: |delta| > 0.33 (Romano et al.
    'medium' effect; matches Hoefler-style 'meaningful' threshold).
    """
    if not xs:
        return 0.0
    n = len(xs)
    pos = sum(1 for x in xs if x > threshold)
    neg = sum(1 for x in xs if x < threshold)
    return (pos - neg) / n


def _rank_biserial(a: list[float], b: list[float]) -> float:
    """Rank-biserial correlation for Mann-Whitney U.

    rb = 1 - 2 * U / (n_a * n_b). Range [-1, 1]. Sign indicates which
    sample tends to be larger; magnitude indicates separation.
    Pre-registered acceptance for H2 posthocs: |rb| > 0.33.
    """
    import scipy.stats as st  # imported lazily; H2/H3 only run if st is not None
    if not a or not b:
        return 0.0
    u, _ = st.mannwhitneyu(a, b, alternative="two-sided")
    return float(1.0 - 2.0 * u / (len(a) * len(b)))


def _kendalls_w(matrix: list[list[float]]) -> float:
    """Kendall's W (coefficient of concordance) for the Friedman setting.

    matrix[i] = list of k profile values for label i. Returns W in [0, 1].
    Pre-registered acceptance for H3: W >= 0.10.
    Computed as W = 12 * S / (n^2 (k^3 - k)) where S is the sum of
    squared deviations of column rank-sums from their mean, n labels,
    k profiles. Implementation tolerant of ties via average ranks.
    """
    if not matrix or not matrix[0]:
        return 0.0
    import numpy as np
    import scipy.stats as st  # rankdata
    arr = np.array(matrix, dtype=float)            # shape (n_labels, k_profiles)
    n, k = arr.shape
    if n < 2 or k < 2:
        return 0.0
    ranks = np.apply_along_axis(st.rankdata, 1, arr)  # rank within each label row
    Rj = ranks.sum(axis=0)
    Rbar = Rj.mean()
    S = float(((Rj - Rbar) ** 2).sum())
    denom = n * n * (k ** 3 - k) / 12.0
    if denom <= 0:
        return 0.0
    return S / denom


def _bootstrap_median_ci(
    xs: list[float],
    alpha: float = 0.05,
    n_resamples: int = 5000,
    seed: int = SEED,
) -> tuple[float, float]:
    """Percentile bootstrap CI for the median.

    Returns (lo, hi) at 100*(1-alpha)% confidence. n_resamples >= 5000
    is sufficient for stable percentiles at alpha=0.05 with n>=14
    (Efron-Tibshirani 1993, Ch. 13). SEED defaults to the canonical
    pipeline SEED so re-runs are bit-identical.
    """
    import numpy as np
    if len(xs) < 2:
        return (float("nan"), float("nan"))
    rng = np.random.default_rng(seed)
    arr = np.asarray(xs, dtype=float)
    n = len(arr)
    samples = arr[rng.integers(0, n, size=(n_resamples, n))]
    mid = n // 2
    if n % 2:
        medians = np.partition(samples, mid, axis=1)[:, mid]
    else:
        selected = np.partition(samples, (mid - 1, mid), axis=1)
        medians = (selected[:, mid - 1] + selected[:, mid]) / 2.0
    lo = float(np.quantile(medians, alpha / 2))
    hi = float(np.quantile(medians, 1 - alpha / 2))
    return (lo, hi)


def _average_ranks(values: list[float]) -> list[float]:
    order = sorted(range(len(values)), key=lambda i: values[i])
    ranks = [0.0] * len(values)
    rank = 1
    i = 0
    while i < len(order):
        j = i + 1
        while j < len(order) and values[order[j]] == values[order[i]]:
            j += 1
        avg_rank = (rank + rank + (j - i) - 1) / 2.0
        for k in range(i, j):
            ranks[order[k]] = avg_rank
        rank += j - i
        i = j
    return ranks


def _wilcoxon_signed_rank_greater(xs: list[float]) -> tuple[float, float]:
    """Exact one-sample Wilcoxon signed-rank p-value for small H1 samples.

    SciPy's generic ``wilcoxon`` call is unexpectedly slow in this Python
    3.13 environment for the 13-label Faithful vectors. H1 only needs the
    standard one-sided signed-rank statistic W+ and p(W+ >= observed), so
    enumerate the 2^n sign assignments directly. Zero differences are
    dropped, matching SciPy's default ``zero_method='wilcox'`` behavior.
    """
    vals = [float(x) for x in xs if float(x) != 0.0]
    if not vals:
        return (0.0, 1.0)
    ranks = _average_ranks([abs(x) for x in vals])
    w_plus = sum(rank for x, rank in zip(vals, ranks) if x > 0)
    scaled_ranks = [int(round(rank * 2.0)) for rank in ranks]
    observed = int(round(w_plus * 2.0))
    counts = {0: 1}
    for rank in scaled_ranks:
        next_counts = counts.copy()
        for total, count in counts.items():
            next_counts[total + rank] = next_counts.get(total + rank, 0) + count
        counts = next_counts
    total_assignments = 2 ** len(scaled_ranks)
    p_greater = sum(count for total, count in counts.items() if total >= observed) / total_assignments
    return (float(w_plus), float(p_greater))


def _holm_bonferroni(p_values: dict[str, float], alpha: float = 0.05) -> dict[str, dict]:
    """Apply Holm-Bonferroni step-down correction within a family.

    Input: dict of test_id -> raw p-value.
    Output: dict of test_id -> {p_raw, p_adj, reject_at_alpha}.

    Pre-registered for H1 (within-family across 18 cells x 3 axes = 54
    tests) and for H2 posthoc Mann-Whitney pairs.
    """
    items = sorted(p_values.items(), key=lambda kv: kv[1])
    m = len(items)
    out: dict[str, dict] = {}
    prev_adj = 0.0
    for rank, (key, p_raw) in enumerate(items, start=1):
        p_adj = min(1.0, max(prev_adj, (m - rank + 1) * p_raw))
        prev_adj = p_adj
        out[key] = {
            "p_raw": float(p_raw),
            "p_adj_holm": float(p_adj),
            "reject_at_alpha": bool(p_adj < alpha),
        }
    return out


def _h1(table: dict, st, seed: int = SEED) -> dict:
    """H1: per-(profile, eps) one-sided Wilcoxon that median log10(tau) > 1.

    Pre-registered acceptance (PRE_REGISTRATION sec 3):
      reject H0 iff p_holm < 0.05 AND Cliff's delta > 0.33
              AND bootstrap 95% CI on median strictly above 1.

    Multiple-comparison correction: Holm-Bonferroni across the entire
    H1 family (18 cells x 3 axes <= 54 tests; skipped tests do not
    enter the family).

    ``seed`` is threaded only into the percentile bootstrap CI (the sole
    RNG-driven quantity in this reduction). Default = canonical SEED so
    re-runs at the default seed remain bit-identical.
    """
    out: dict = {}
    cells: dict = defaultdict(lambda: defaultdict(list))  # cell -> axis -> [tau]
    for lid, by_cell in table.items():
        for cell, taus in by_cell.items():
            for axis, val in taus.items():
                if val > 0:
                    cells[cell][axis].append(val)

    raw_p_values: dict[str, float] = {}
    test_payload: dict[str, dict] = {}

    for cell, by_axis in cells.items():
        out[cell] = {}
        for axis, vals in by_axis.items():
            n = len(vals)
            if n < 5 or st is None:
                out[cell][axis] = {"n": n, "test": "skipped_low_n_or_no_scipy"}
                continue
            try:
                log10_minus_1 = [math.log10(v) - 1 for v in vals]
                stat, p = _wilcoxon_signed_rank_greater(log10_minus_1)
                med_tau = float(sorted(vals)[n // 2])
                cliffs = _cliffs_delta(log10_minus_1, threshold=0.0)
                ci_lo, ci_hi = _bootstrap_median_ci(vals, seed=seed)
                payload = {
                    "n": n,
                    "median_tau": med_tau,
                    "median_log10_tau_minus_1": float(sum(log10_minus_1) / n),
                    "wilcoxon_stat": float(stat),
                    "p_one_sided_greater_raw": float(p),
                    "cliffs_delta_log10_tau_vs_1": float(cliffs),
                    "bootstrap_median_tau_ci95": [ci_lo, ci_hi],
                    "ci_strictly_above_1": bool(ci_lo > 1.0),
                }
                key = f"{cell}@@{axis}"
                raw_p_values[key] = float(p)
                test_payload[key] = payload
                out[cell][axis] = payload
            except Exception as exc:
                out[cell][axis] = {"n": n, "test": f"error:{exc}"}

    # Apply Holm-Bonferroni within the H1 family
    if raw_p_values:
        adjusted = _holm_bonferroni(raw_p_values)
        for key, info in adjusted.items():
            cell, axis = key.split("@@", 1)
            payload = test_payload[key]
            payload["p_one_sided_greater_holm"] = info["p_adj_holm"]
            payload["reject_holm_at_0_05"] = info["reject_at_alpha"]
            # Pre-registered triple-condition acceptance
            payload["accept_h1_triple"] = bool(
                info["reject_at_alpha"]
                and payload.get("cliffs_delta_log10_tau_vs_1", 0.0) > 0.33
                and payload.get("ci_strictly_above_1", False)
            )
            out[cell][axis] = payload

    out["_family_summary"] = {
        "n_tests_in_family": len(raw_p_values),
        "correction": "holm_bonferroni",
        "alpha": 0.05,
        "n_accepted_triple": sum(
            1 for k, p in test_payload.items()
            if out[k.split("@@", 1)[0]][k.split("@@", 1)[1]].get("accept_h1_triple")
        ),
    }
    return out


def _h2(table: dict, cohort: dict, st) -> dict:
    """H2: Kruskal-Wallis omnibus + posthoc Mann-Whitney with Holm.

    Pre-registered (PRE_REGISTRATION sec 3): omnibus Kruskal-Wallis,
    then per-pair Mann-Whitney with Holm-Bonferroni correction; reject
    overall iff at least one pair has p_holm < 0.05 AND
    |rank-biserial| > 0.33.
    """
    if st is None:
        return {"test": "skipped_no_scipy"}
    scope = _p3_scope_disposition(cohort)
    by_silo: dict = defaultdict(list)
    excluded_by_scope: dict[str, list[str]] = defaultdict(list)
    for lid, by_cell in table.items():
        cell = f"{H4_ANCHOR_PROFILE}|{H4_ANCHOR_EPS:.0e}"
        v = (by_cell.get(cell) or {}).get("runtime_seconds")
        if isinstance(v, (int, float)) and v > 0:
            silo = (cohort["labels"].get(lid) or {}).get("silo")
            if silo not in scope["active_p3_silos"]:
                excluded_by_scope[silo or "unknown"].append(lid)
                continue
            by_silo[silo].append(math.log10(v))
    silos = sorted(by_silo)
    samples = [by_silo[s] for s in silos if len(by_silo[s]) >= 2]
    silos_in_test = [s for s in silos if len(by_silo[s]) >= 2]
    if len(samples) < 2:
        return {
            "test": "skipped_insufficient_silos",
            "n_silos": len(samples),
            **_scope_payload(scope, excluded_by_scope),
        }
    stat, p = st.kruskal(*samples)

    # Per-pair Mann-Whitney posthocs with Holm-Bonferroni correction
    pairwise_raw_p: dict[str, float] = {}
    pairwise_payload: dict[str, dict] = {}
    for i, s_i in enumerate(silos_in_test):
        for j in range(i + 1, len(silos_in_test)):
            s_j = silos_in_test[j]
            a, b = by_silo[s_i], by_silo[s_j]
            try:
                u, p_pair = st.mannwhitneyu(a, b, alternative="two-sided")
                rb = _rank_biserial(a, b)
                key = f"{s_i}__vs__{s_j}"
                pairwise_raw_p[key] = float(p_pair)
                pairwise_payload[key] = {
                    "n_a": len(a),
                    "n_b": len(b),
                    "U": float(u),
                    "p_two_sided_raw": float(p_pair),
                    "rank_biserial": float(rb),
                }
            except Exception as exc:
                pairwise_payload[f"{s_i}__vs__{s_j}"] = {"error": str(exc)}

    pairwise_adjusted = _holm_bonferroni(pairwise_raw_p) if pairwise_raw_p else {}
    for key, info in pairwise_adjusted.items():
        pairwise_payload[key]["p_two_sided_holm"] = info["p_adj_holm"]
        pairwise_payload[key]["reject_holm_at_0_05"] = info["reject_at_alpha"]
        pairwise_payload[key]["accept_pair_h2"] = bool(
            info["reject_at_alpha"]
            and abs(pairwise_payload[key].get("rank_biserial", 0.0)) > 0.33
        )

    n_accepted = sum(
        1 for v in pairwise_payload.values() if v.get("accept_pair_h2")
    )
    return {
        "test": "kruskal_wallis_then_mannwhitney_holm",
        "silos_in_test": silos_in_test,
        "n_per_silo": {s: len(by_silo[s]) for s in silos},
        "kw_stat": float(stat),
        "kw_p_value": float(p),
        "pairwise": pairwise_payload,
        "n_pairs": len(pairwise_raw_p),
        "n_pairs_accepted_h2": n_accepted,
        "accept_h2_overall": bool(n_accepted >= 1),
        "correction": "holm_bonferroni",
        **_scope_payload(scope, excluded_by_scope),
        "mixed_effects_sensitivity": _h2_mixed_effects_sensitivity(table, cohort),
    }


def _h2_mixed_effects_sensitivity(table: dict, cohort: dict) -> dict:
    """H2 sensitivity: linear mixed-effects on log10(tau_runtime) pooled
    across all (profile, eps) cells, with silo as fixed effect and label
    as random intercept.

    Why: the canonical H2 above uses a single anchor cell per label
    (n_total ~= |Faithful| ~ 14 rows), which is intentionally close to
    the H4 anchor but limits power. This sensitivity instead pools all
    ~36 cells per label, controlling for within-label correlation via a
    label-level random intercept. Reports the silo fixed-effect Wald
    chi-square and p-value, plus the per-silo coefficient table.

    Statsmodels is an optional dependency; when absent the test is
    flagged as skipped and the canonical KW result still stands.
    Records intra-class correlation (ICC) so the magnitude of
    within-label dependence is visible to readers.
    """
    try:
        import numpy as np  # noqa: F401
        import statsmodels.api as sm
        import statsmodels.formula.api as smf
        import pandas as pd
    except Exception as exc:
        return {
            "test": "skipped_no_statsmodels_or_pandas",
            "reason": f"{type(exc).__name__}: {exc}",
            "note": (
                "Install statsmodels + pandas to enable. The canonical "
                "anchor-cell Kruskal-Wallis result above is unaffected."
            ),
        }

    scope = _p3_scope_disposition(cohort)
    excluded_by_scope: dict[str, list[str]] = defaultdict(list)
    rows: list[dict] = []
    for lid, by_cell in table.items():
        silo = (cohort["labels"].get(lid) or {}).get("silo")
        if not silo:
            continue
        if silo not in scope["active_p3_silos"]:
            excluded_by_scope[silo].append(lid)
            continue
        for cell_key, axes in by_cell.items():
            v = axes.get("runtime_seconds")
            if not isinstance(v, (int, float)) or v <= 0:
                continue
            rows.append({
                "label": lid,
                "silo": silo,
                "cell": cell_key,
                "log10_tau": math.log10(v),
            })
    if len(rows) < 30 or len({r["silo"] for r in rows}) < 2:
        return {
            "test": "skipped_insufficient_data",
            "n_rows": len(rows),
            "n_silos": len({r["silo"] for r in rows}),
            **_scope_payload(scope, excluded_by_scope),
        }

    df = pd.DataFrame(rows)
    # Mixed model: log10_tau ~ C(silo) + (1 | label).
    # ML rather than REML so likelihood-ratio diagnostics are comparable.
    try:
        model = smf.mixedlm("log10_tau ~ C(silo)", df, groups=df["label"])
        fit = model.fit(method="lbfgs", reml=False, disp=False)
    except Exception as exc:
        return {
            "test": "mixedlm_fit_failed",
            "reason": f"{type(exc).__name__}: {exc}",
            "n_rows": len(rows),
        }

    silo_terms = [name for name in fit.params.index if name.startswith("C(silo)")]
    coefs = {
        name: {
            "estimate": float(fit.params[name]),
            "std_err": float(fit.bse[name]),
            "p_value": float(fit.pvalues[name]),
            "reject_at_0_05": bool(float(fit.pvalues[name]) < 0.05),
        }
        for name in silo_terms
    }
    # Joint Wald chi-square test that all silo coefficients are zero.
    try:
        wald = fit.wald_test(" = 0, ".join(silo_terms) + " = 0", scalar=True)
        joint_stat = float(wald.statistic)
        joint_p = float(wald.pvalue)
        joint_df = int(len(silo_terms))
    except Exception:
        joint_stat = float("nan")
        joint_p = float("nan")
        joint_df = len(silo_terms)

    # Intra-class correlation (variance of label random intercept /
    # total variance) -- quantifies the within-label dependence the
    # canonical KW ignores when pooling.
    try:
        var_label = float(fit.cov_re.iloc[0, 0])
        var_resid = float(fit.scale)
        icc = var_label / (var_label + var_resid) if (var_label + var_resid) > 0 else float("nan")
    except Exception:
        var_label = float("nan")
        var_resid = float("nan")
        icc = float("nan")

    return {
        "test": "linear_mixed_effects_silo_fixed_label_random",
        "model_formula": "log10_tau ~ C(silo) + (1 | label)",
        "axis": "runtime_seconds",
        "n_rows": int(len(df)),
        "n_labels": int(df["label"].nunique()),
        "n_silos": int(df["silo"].nunique()),
        "joint_silo_wald_stat": joint_stat,
        "joint_silo_wald_p_value": joint_p,
        "joint_silo_wald_df": joint_df,
        "reject_joint_at_0_05": bool(joint_p < 0.05) if not math.isnan(joint_p) else None,
        "per_silo_coef_vs_reference": coefs,
        "variance_components": {
            "between_label": var_label,
            "residual": var_resid,
            "icc_label": icc,
            "icc_interpretation": (
                "Fraction of total variance attributable to between-label "
                "differences. ICC > 0.3 indicates the canonical pooled "
                "Kruskal-Wallis is materially anti-conservative; this MixedLM "
                "controls for that dependence."
            ),
        },
        **_scope_payload(scope, excluded_by_scope),
        "caveat": (
            "Sensitivity result. Pre-registered headline H2 remains the "
            "active-P3-silo anchor-cell Kruskal-Wallis above "
            "(PRE_REGISTRATION sec 3, amended 2026-04-28). This MixedLM "
            "was added 2026-04-19 and follows the same active-P3 scope."
        ),
    }


def _h3(table: dict, st) -> dict:
    """H3: Friedman across profiles at eps=1e-4 + Kendall's W effect size.

    Pre-registered acceptance (PRE_REGISTRATION sec 3): Friedman p<0.05
    AND Kendall's W >= 0.10 (small-to-medium concordance among profiles).

    Axis choice. The Friedman omnibus is computed on log10(tau_runtime)
    only. The other three resource axes (logical_qubits, t_count,
    t_depth) are profile-invariant *by construction* of the Azure RE
    model: those quantities depend on the algorithm/QIR program and not
    on the QEC code or distillation budget. Reporting them as
    'skipped_low_n' or 'fewer_than_3_complete_blocks' (an earlier shape)
    misled readers into thinking the data was insufficient. We instead
    emit them under ``structural_invariants`` so the reader sees a
    positive statement of why the test was not run.
    """
    if st is None:
        return {"test": "skipped_no_scipy"}
    structural_invariants = {
        "logical_qubits": {
            "axis_invariant_by_construction": True,
            "reason": (
                "Logical qubit count is a property of the QIR program. "
                "Azure RE does not vary it across hardware profiles; "
                "tau = full_logical_qubits / bare_logical_qubits = 1 "
                "identically for every (label, profile, eps) cell. "
                "Friedman degenerates on constant blocks."
            ),
        },
        "t_count": {
            "axis_invariant_by_construction": True,
            "reason": (
                "Logical T-gate count is determined by the input "
                "algorithm and the rotation-synthesis epsilon, not by "
                "the QEC profile. tau is therefore invariant across "
                "profiles within a fixed epsilon."
            ),
        },
        "t_depth": {
            "axis_invariant_by_construction": True,
            "reason": (
                "Logical T-depth is invariant across QEC profiles for "
                "the same reason as t_count: it is fixed by the QIR "
                "program and the rotation-synthesis epsilon."
            ),
        },
    }
    matrix: dict[str, list[float]] = {}  # label -> [tau per profile]
    for lid, by_cell in table.items():
        row = []
        valid = True
        for prof in PROFILES:
            v = (by_cell.get(f"{prof}|1e-04") or {}).get("runtime_seconds")
            if not isinstance(v, (int, float)) or v <= 0:
                valid = False
                break
            row.append(math.log10(v))
        if valid:
            matrix[lid] = row
    if len(matrix) < 5:
        return {
            "test": "skipped_low_n",
            "axis": "runtime_seconds",
            "n_labels_complete": len(matrix),
            "min_required": 5,
            "structural_invariants": structural_invariants,
            "note": (
                "Skip is a coverage condition (need >=5 labels with all 6 "
                "profiles populated at eps=1e-4), not a model issue. "
                "Will activate automatically once Phase 8 fills the missing "
                "trapped-ion bare cells. The other three resource axes are "
                "untestable by construction (see structural_invariants)."
            ),
        }
    rows = list(matrix.values())
    cols = list(zip(*rows))
    stat, p = st.friedmanchisquare(*cols)
    W = _kendalls_w(rows)
    return {
        "test": "friedman_with_kendalls_w",
        "axis": "runtime_seconds",
        "n_labels": len(matrix),
        "profiles": PROFILES,
        "friedman_stat": float(stat),
        "friedman_p_value": float(p),
        "kendalls_w": float(W),
        "accept_h3": bool(p < 0.05 and W >= 0.10),
        "structural_invariants": structural_invariants,
    }


def _h4(idx: dict, faithful: set[str], cohort: dict) -> dict:
    """H4: strict-H4 subset construction at the anchor cell."""
    canonical_winners = _h4_subset(idx, faithful, cohort, tau_threshold=10.0)
    sensitivity_winners = {
        f"tau={t}": _h4_subset(idx, faithful, cohort, tau_threshold=t)
        for t in H4_TAU_GRID
    }
    baseline_winners = {
        "baseline_x10": _h4_subset(idx, faithful, cohort, baseline_scale=10.0),
        "baseline_div10": _h4_subset(idx, faithful, cohort, baseline_scale=0.1),
    }
    scoreboard = _h4_per_label_scoreboard(idx, faithful, cohort, tau_threshold=10.0)
    # SVM sensitivity: H4 with linear-SVM-substitution labels excluded
    # (paper-specified RBF kernels; substitution flagged as MAJOR threat)
    svm_substituted = {"B3", "B4", "SQ5", "SQ17", "SQ18"}
    faithful_no_svm = faithful - svm_substituted
    canonical_winners_no_svm = _h4_subset(idx, faithful_no_svm, cohort, tau_threshold=10.0)
    non_exact_baselines = _phase8b_non_exact_baselines(cohort, faithful)
    faithful_exact_phase8b = faithful - non_exact_baselines
    canonical_winners_exact_phase8b = _h4_subset(
        idx, faithful_exact_phase8b, cohort, tau_threshold=10.0,
    )
    return {
        "anchor_cell": {"profile": H4_ANCHOR_PROFILE, "epsilon": H4_ANCHOR_EPS, "mode": "full"},
        "faithful_subcohort_size": len(faithful),
        "canonical_winners": canonical_winners,
        "canonical_winners_count": len(canonical_winners),
        "sensitivity_tau_winners": {k: len(v) for k, v in sensitivity_winners.items()},
        "sensitivity_tau_winners_detail": sensitivity_winners,
        "sensitivity_baseline_winners": {k: len(v) for k, v in baseline_winners.items()},
        "sensitivity_baseline_winners_detail": baseline_winners,
        "sensitivity_no_svm_substitution": {
            "excluded_labels": sorted(svm_substituted & faithful),
            "faithful_subcohort_size": len(faithful_no_svm),
            "canonical_winners": canonical_winners_no_svm,
            "canonical_winners_count": len(canonical_winners_no_svm),
        },
        "sensitivity_no_non_exact_phase8b_baseline": {
            "description": (
                "H4 with Faithful labels excluded when their Phase 8b measured "
                "classical baseline is a fallback or only one paper-named component, "
                "rather than an exact paper-named implementation. This is the stricter "
                "defensibility check for baseline-substitution risk."
            ),
            "excluded_labels": sorted(non_exact_baselines),
            "faithful_subcohort_size": len(faithful_exact_phase8b),
            "canonical_winners": canonical_winners_exact_phase8b,
            "canonical_winners_count": len(canonical_winners_exact_phase8b),
        },
        "sensitivity_strongest_classical_alt_top3": {
            "description": (
                "H4 with classical baseline replaced by min(rank1,rank2,rank3) "
                "wall-clock from Phase 8c silo-default top-3 kernels (the "
                "strongest classical method per label). Harder test for "
                "quantum advantage. See DECISIONS_LOG 2026-04-19 Phase 8c."
            ),
            "faithful_subcohort_size": len(faithful),
            "canonical_winners": _h4_subset(
                idx, faithful, cohort, tau_threshold=10.0,
                baseline_resolver=_resolve_baseline_strongest_of_top3,
            ),
            "canonical_winners_count": len(_h4_subset(
                idx, faithful, cohort, tau_threshold=10.0,
                baseline_resolver=_resolve_baseline_strongest_of_top3,
            )),
        },
        "faithfulness_tier_sensitivity": _h4_faithfulness_tier_sensitivity(idx, faithful, cohort),
        "qdk_nontriviality_sensitivity": _h4_qdk_nontriviality_sensitivity(idx, faithful, cohort),
        "leave_one_out": _h4_leave_one_out(idx, faithful, cohort),
        "vincent_review_cross_tab": _vincent_review_verdicts(cohort),
        "per_criterion_breakdown": scoreboard,
        "bifurcation_holds": (
            len(canonical_winners) == 0
            and all(len(v) == 0 for v in sensitivity_winners.values())
            and all(len(v) == 0 for v in baseline_winners.values())
        ),
        "proxy_exploratory": _h4_proxy_exploratory(idx, faithful, cohort),
    }


def _h4_proxy_exploratory(idx: dict, faithful: set[str], cohort: dict) -> dict:
    """Exploratory: apply the same five-gate H4 filter to the 79 Proxy labels.

    NOT a falsification of the bifurcation thesis. Proxies use template
    stand-in circuits (generic QFT/QPE/HHL skeletons), so a 'win' here only
    flags a label as a candidate for paper-grade re-extraction in a future
    revision. A 'loss' is corroborating but not dispositive (the proxy may
    understate the paper's true T-count). Reported in the appendix only.
    See DECISIONS_LOG 2026-04-20 H4 proxy exploratory.
    """
    proxies = {lid for lid, e in cohort["labels"].items() if e.get("fidelity") == "P"}
    canonical = _h4_subset(idx, proxies, cohort, tau_threshold=10.0)
    strongest = _h4_subset(
        idx, proxies, cohort, tau_threshold=10.0,
        baseline_resolver=_resolve_baseline_strongest_of_top3,
    )
    scoreboard = _h4_per_label_scoreboard(idx, proxies, cohort, tau_threshold=10.0)
    return {
        "role": "exploratory_lead_generation",
        "warning": (
            "NOT part of the pre-registered H4 test. Proxy circuits are "
            "template stand-ins, not paper-grade reconstructions; their "
            "classical baselines are not commensurable with the proxy "
            "circuit. Use only as a candidate list for future faithful "
            "re-extraction, never as evidence for or against the "
            "bifurcation thesis."
        ),
        "proxy_subcohort_size": len(proxies),
        "canonical_winners": canonical,
        "canonical_winners_count": len(canonical),
        "strongest_classical_alt_top3_winners": strongest,
        "strongest_classical_alt_top3_winners_count": len(strongest),
        "per_criterion_breakdown": scoreboard,
    }


def _seed_grid_sensitivity(
    table_faithful: dict,
    st,
    h1_canonical: dict,
    h3_canonical: dict,
    h4_canonical: dict,
) -> dict:
    """Re-run H1 across SEED_GRID and report seed sensitivity.

    Mechanics: only the H1 percentile bootstrap CI consumes RNG. H3
    (Friedman + Kendall's W) and H4 (deterministic 5-criteria threshold
    check) are seed-invariant by construction; we report the canonical
    value once for each, with ``seed_invariant: true``. For H1 we
    recompute the bootstrap CI at every seed in SEED_GRID and emit
    per-cell/per-axis CI lists alongside the count of cells whose
    ``ci_strictly_above_1`` flag and ``accept_h1_triple`` verdict flip
    relative to the canonical seed. Promised by the module docstring
    (line 28) and PRE_REGISTRATION sec 6.5.
    """
    h1_per_seed: dict[str, dict] = {}
    h1_flip_counts: dict[str, dict] = {}
    canonical_key = f"0x{SEED:08X}"
    for s in SEED_GRID:
        key = f"0x{s:08X}"
        h1_at_seed = h1_canonical if s == SEED else _h1(table_faithful, st, seed=s)
        cis: dict[str, dict[str, dict]] = {}
        for cell, by_axis in h1_at_seed.items():
            if cell == "_family_summary":
                continue
            cis[cell] = {}
            for axis, payload in by_axis.items():
                if not isinstance(payload, dict):
                    continue
                cis[cell][axis] = {
                    "bootstrap_median_tau_ci95": payload.get("bootstrap_median_tau_ci95"),
                    "ci_strictly_above_1": payload.get("ci_strictly_above_1"),
                    "accept_h1_triple": payload.get("accept_h1_triple"),
                }
        h1_per_seed[key] = {
            "seed_int": int(s),
            "n_accepted_triple": (h1_at_seed.get("_family_summary") or {}).get("n_accepted_triple"),
            "per_cell_axis": cis,
        }
        if s != SEED:
            n_flips_strict = 0
            n_flips_triple = 0
            for cell, by_axis in cis.items():
                canon_axes = (h1_canonical.get(cell) or {})
                for axis, payload in by_axis.items():
                    canon = canon_axes.get(axis) or {}
                    if payload.get("ci_strictly_above_1") != canon.get("ci_strictly_above_1"):
                        n_flips_strict += 1
                    if payload.get("accept_h1_triple") != canon.get("accept_h1_triple"):
                        n_flips_triple += 1
            h1_flip_counts[key] = {
                "vs_canonical_seed": canonical_key,
                "n_cells_ci_strictly_above_1_flipped": n_flips_strict,
                "n_cells_accept_h1_triple_flipped": n_flips_triple,
            }

    return {
        "_provenance": {
            "generated_utc": datetime.now(timezone.utc).isoformat(),
            "canonical_seed_int": int(SEED),
            "canonical_seed_hex": canonical_key,
            "seed_grid_int": [int(s) for s in SEED_GRID],
            "seed_grid_hex": [f"0x{s:08X}" for s in SEED_GRID],
            "rationale": (
                "Only the H1 percentile bootstrap CI is RNG-driven; "
                "H3 (Friedman + Kendall's W) and H4 (deterministic "
                "threshold check) are seed-invariant by construction "
                "and reported once with seed_invariant=true."
            ),
            "promised_by": [
                "phase9_stats.py docstring line 28",
                "PRE_REGISTRATION.md sec 6.5",
            ],
        },
        "H1": {
            "seed_invariant": False,
            "rng_use": "percentile bootstrap CI on median tau (n_resamples=5000)",
            "per_seed": h1_per_seed,
            "flip_counts_vs_canonical": h1_flip_counts,
        },
        "H3": {
            "seed_invariant": True,
            "rationale": (
                "Friedman test and Kendall's W are closed-form on "
                "ranks; no RNG. Identical at every seed."
            ),
            "canonical_value": {
                "friedman_p_value": h3_canonical.get("friedman_p_value"),
                "kendalls_w": h3_canonical.get("kendalls_w"),
                "accept_h3": h3_canonical.get("accept_h3"),
            },
        },
        "H4": {
            "seed_invariant": True,
            "rationale": (
                "Deterministic 5-criteria threshold check on Azure RE "
                "outputs; no RNG. Winner count identical at every seed."
            ),
            "canonical_value": {
                "canonical_winners_count": h4_canonical.get("canonical_winners_count"),
                "canonical_winners": h4_canonical.get("canonical_winners"),
                "bifurcation_holds": h4_canonical.get("bifurcation_holds"),
            },
        },
    }


def _median(xs: list[float]) -> float | None:
    if not xs:
        return None
    ys = sorted(float(x) for x in xs)
    mid = len(ys) // 2
    if len(ys) % 2:
        return ys[mid]
    return (ys[mid - 1] + ys[mid]) / 2.0


def _quantile(xs: list[float], q: float) -> float | None:
    if not xs:
        return None
    ys = sorted(float(x) for x in xs)
    if len(ys) == 1:
        return ys[0]
    pos = (len(ys) - 1) * q
    lo = int(math.floor(pos))
    hi = int(math.ceil(pos))
    if lo == hi:
        return ys[lo]
    weight = pos - lo
    return ys[lo] * (1.0 - weight) + ys[hi] * weight


def _distribution_summary(xs: list[float]) -> dict:
    if not xs:
        return {"n": 0, "min": None, "q1": None, "median": None, "q3": None, "max": None}
    ys = sorted(float(x) for x in xs)
    return {
        "n": len(ys),
        "min": ys[0],
        "q1": _quantile(ys, 0.25),
        "median": _median(ys),
        "q3": _quantile(ys, 0.75),
        "max": ys[-1],
    }


def _cell_key(profile: str, eps: float) -> str:
    return f"{profile}|{eps:.0e}"


def _cohort_counts(cohort: dict) -> dict:
    silos: dict[str, dict[str, int]] = {}
    fidelity: dict[str, int] = {}
    faithfulness_tier: dict[str, int] = {}
    for entry in cohort["labels"].values():
        fid = entry.get("fidelity", "?")
        silo = entry.get("silo", "unknown")
        fidelity[fid] = fidelity.get(fid, 0) + 1
        tier = _faithfulness_tier(entry)
        faithfulness_tier[tier] = faithfulness_tier.get(tier, 0) + 1
        bucket = silos.setdefault(silo, {"N": 0, "F": 0, "P": 0})
        bucket["N"] += 1
        bucket[fid] = bucket.get(fid, 0) + 1
    return {
        "n_labels_total": len(cohort.get("labels") or {}),
        "n_labels_faithful": fidelity.get("F", 0),
        "n_labels_proxy": fidelity.get("P", 0),
        "n_silos": len(silos),
        "fidelity_counts": dict(sorted(fidelity.items())),
        "faithfulness_tier_counts": dict(sorted(faithfulness_tier.items())),
        "silo_counts": dict(sorted(silos.items())),
    }


def _read_json_if_exists(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        return {"_parse_error": f"{type(exc).__name__}: {exc}"}


def _phase8d_regime_evidence() -> dict:
    status = _read_json_if_exists(PHASE8D_STATUS)
    summary = _read_json_if_exists(PHASE8D_SUMMARY)
    rows = summary.get("rows") if isinstance(summary.get("rows"), list) else []
    by_family: dict[str, dict] = {}
    by_family_profile: dict[str, dict] = {}
    for row in rows:
        family = row.get("family") or "unknown"
        profile = row.get("hardware_profile") or "unknown"
        status_value = row.get("status") or "unknown"
        bucket = by_family.setdefault(
            family,
            {
                "n_records": 0,
                "by_status": {},
                "entity_ids": set(),
                "n_values": set(),
                "m_precision_qubits": set(),
                "hardware_profiles": set(),
                "runtime_seconds_ok": [],
                "physical_qubits_ok": [],
                "t_depth_ok": [],
                "t_count_ok": [],
            },
        )
        bucket["n_records"] += 1
        bucket["by_status"][status_value] = bucket["by_status"].get(status_value, 0) + 1
        for key, dest in [
            ("entity_id", "entity_ids"),
            ("n_value", "n_values"),
            ("m_precision_qubits", "m_precision_qubits"),
            ("hardware_profile", "hardware_profiles"),
        ]:
            value = row.get(key)
            if value is not None:
                bucket[dest].add(value)
        if status_value == "ok":
            for key, dest in [
                ("runtime_seconds", "runtime_seconds_ok"),
                ("physical_qubits", "physical_qubits_ok"),
                ("t_depth", "t_depth_ok"),
                ("t_count", "t_count_ok"),
            ]:
                value = row.get(key)
                if isinstance(value, (int, float)):
                    bucket[dest].append(float(value))

        combo_key = f"{family}|{profile}"
        combo = by_family_profile.setdefault(combo_key, {"family": family, "hardware_profile": profile, "n_records": 0, "ok": 0, "engine_failure": 0})
        combo["n_records"] += 1
        if status_value == "ok":
            combo["ok"] += 1
        elif status_value == "engine_failure":
            combo["engine_failure"] += 1

    family_rows = []
    for family, bucket in sorted(by_family.items()):
        family_rows.append({
            "family": family,
            "n_records": bucket["n_records"],
            "by_status": dict(sorted(bucket["by_status"].items())),
            "entity_ids": sorted(bucket["entity_ids"]),
            "n_values": sorted(bucket["n_values"]),
            "m_precision_qubits": sorted(bucket["m_precision_qubits"]),
            "hardware_profiles": sorted(bucket["hardware_profiles"]),
            "runtime_seconds_ok_summary": _distribution_summary(bucket["runtime_seconds_ok"]),
            "physical_qubits_ok_summary": _distribution_summary(bucket["physical_qubits_ok"]),
            "t_depth_ok_summary": _distribution_summary(bucket["t_depth_ok"]),
            "t_count_ok_summary": _distribution_summary(bucket["t_count_ok"]),
        })

    return {
        "regime_id": "qae_hhl_fixed_precision_high_n",
        "name": "HHL/QAE fixed-precision high-N scout",
        "role": "appendix_scaling_and_stress_test",
        "source_phase": "8d",
        "present": bool(summary) and "_parse_error" not in summary,
        "included_in_headline_h1_h4": False,
        "appendix_only": status.get("appendix_only", True),
        "headline_excludes_phase8d": status.get("headline_excludes_phase8d", True),
        "separation_rule": (
            "Use for fixed-precision HHL/QAE scaling, resource growth, and engine-limit disclosure. "
            "Do not pool with the S2-backed label grid used by H1-H4."
        ),
        "track": status.get("track") or "qae_hhl_fixed_precision_high_n",
        "stage": status.get("stage"),
        "schema": status.get("schema"),
        "problem_size_decoupled_from_precision": status.get("problem_size_decoupled_from_precision"),
        "selected_entities": status.get("selected_entities") or [],
        "selected_labels": status.get("selected_labels") or [],
        "n_records": summary.get("n_records") or status.get("n_records"),
        "expected_records": status.get("expected_records"),
        "by_status": summary.get("by_status") or status.get("by_status") or {},
        "results_dir": summary.get("results_dir") or status.get("results_dir"),
        "families": family_rows,
        "family_profile_rows": [by_family_profile[key] for key in sorted(by_family_profile)],
        "scaling_rows": [
            {
                "family": row.get("family"),
                "entity_id": row.get("entity_id"),
                "n_value": row.get("n_value"),
                "m_precision_qubits": row.get("m_precision_qubits"),
                "hardware_profile": row.get("hardware_profile"),
                "epsilon": row.get("epsilon"),
                "status": row.get("status"),
                "runtime_seconds": row.get("runtime_seconds"),
                "physical_qubits": row.get("physical_qubits"),
                "t_depth": row.get("t_depth"),
                "t_count": row.get("t_count"),
                "reason": row.get("reason"),
            }
            for row in rows
        ],
    }


def _experiment_regimes_evidence(cohort: dict) -> dict:
    counts = _cohort_counts(cohort)
    phase8d = _phase8d_regime_evidence()
    canonical = {
        "regime_id": "canonical_s2_backed_label_grid",
        "name": "S2-backed canonical label grid",
        "role": "headline_pre_registered_h1_h4",
        "source_phase": "8",
        "included_in_headline_h1_h4": True,
        "appendix_only": False,
        "n_labels_total": counts.get("n_labels_total"),
        "n_labels_faithful": counts.get("n_labels_faithful"),
        "n_labels_proxy": counts.get("n_labels_proxy"),
        "n_silos": counts.get("n_silos"),
        "faithfulness_tier_counts": counts.get("faithfulness_tier_counts"),
        "grid_shape": {
            "profiles": PROFILES,
            "epsilons": EPSILONS,
            "modes": MODES,
            "resource_axes": RESOURCE_AXES,
        },
        "hypotheses": ["H1", "H2", "H3", "H4"],
        "separation_rule": (
            "This is the only regime used for pre-registered H1-H4 inference. "
            "HHL/QAE fixed-precision scout records are not pooled into these tests."
        ),
    }
    return {
        "schema": "experiment_regimes.1.0",
        "regime_boundary": (
            "Phase 9/10 distinguish the S2-backed canonical H1-H4 label grid "
            "from the HHL/QAE fixed-precision high-N scout. The latter is "
            "appendix-only evidence for scaling behavior and estimator limits."
        ),
        "regimes": [canonical, phase8d],
        "headline_regime_id": canonical["regime_id"],
        "appendix_regime_ids": [phase8d["regime_id"]],
    }


def _h1_evidence(stats_report: dict) -> dict:
    h1 = stats_report.get("H1") or {}
    rows: list[dict] = []
    accepted_by_axis = {axis: 0 for axis in RESOURCE_AXES}
    tests_by_axis = {axis: 0 for axis in RESOURCE_AXES}
    runtime_medians: list[float] = []
    for profile in PROFILES:
        for eps in EPSILONS:
            cell = h1.get(_cell_key(profile, eps)) or {}
            for axis in RESOURCE_AXES:
                payload = cell.get(axis) or {}
                median_tau = payload.get("median_tau")
                accept = bool(payload.get("accept_h1_triple"))
                if isinstance(payload.get("n"), int):
                    tests_by_axis[axis] += 1
                if accept:
                    accepted_by_axis[axis] += 1
                if axis == "runtime_seconds" and isinstance(median_tau, (int, float)):
                    runtime_medians.append(float(median_tau))
                rows.append({
                    "profile": profile,
                    "epsilon": eps,
                    "cell": _cell_key(profile, eps),
                    "axis": axis,
                    "n": payload.get("n"),
                    "median_tau": median_tau,
                    "median_log10_tau": (
                        math.log10(median_tau)
                        if isinstance(median_tau, (int, float)) and median_tau > 0 else None
                    ),
                    "bootstrap_median_tau_ci95": payload.get("bootstrap_median_tau_ci95"),
                    "p_one_sided_greater_raw": payload.get("p_one_sided_greater_raw"),
                    "p_one_sided_greater_holm": payload.get("p_one_sided_greater_holm"),
                    "cliffs_delta_log10_tau_vs_1": payload.get("cliffs_delta_log10_tau_vs_1"),
                    "ci_strictly_above_1": payload.get("ci_strictly_above_1"),
                    "reject_holm_at_0_05": payload.get("reject_holm_at_0_05"),
                    "accept_h1_triple": accept,
                    "interpretation": (
                        "supports_order_of_magnitude_tax" if accept
                        else "does_not_support_order_of_magnitude_tax"
                    ),
                })
    return {
        "hypothesis": "H1",
        "claim_role": "Results table and effect-size/uncertainty evidence",
        "threshold_tau": 10.0,
        "family_summary": h1.get("_family_summary") or {},
        "accepted_tests_by_axis": accepted_by_axis,
        "tests_by_axis": tests_by_axis,
        "runtime_median_tau_range": {
            "min": min(runtime_medians) if runtime_medians else None,
            "max": max(runtime_medians) if runtime_medians else None,
        },
        "rows": rows,
    }


def _h2_evidence(table_faithful: dict, cohort: dict, stats_report: dict) -> dict:
    h2 = stats_report.get("H2") or {}
    counts = _cohort_counts(cohort)["silo_counts"]
    scope = _p3_scope_disposition(cohort)
    anchor_cell = f"{H4_ANCHOR_PROFILE}|{H4_ANCHOR_EPS:.0e}"
    by_silo_tau: dict[str, list[float]] = defaultdict(list)
    by_silo_labels: dict[str, list[str]] = defaultdict(list)
    for label, by_cell in table_faithful.items():
        tau = (by_cell.get(anchor_cell) or {}).get("runtime_seconds")
        if isinstance(tau, (int, float)) and tau > 0:
            silo = (cohort["labels"].get(label) or {}).get("silo", "unknown")
            by_silo_tau[silo].append(float(tau))
            by_silo_labels[silo].append(label)

    rows = []
    for silo, silo_counts in sorted(counts.items()):
        taus = by_silo_tau.get(silo, [])
        log_taus = [math.log10(v) for v in taus if v > 0]
        rows.append({
            "silo": silo,
            "p3_scope": "active_p3" if silo in scope["active_p3_silos"] else "out_of_p3_scope",
            "n_labels_total": silo_counts.get("N", 0),
            "n_faithful": silo_counts.get("F", 0),
            "n_proxy": silo_counts.get("P", 0),
            "n_anchor_observations": len(taus),
            "faithful_labels_at_anchor": sorted(by_silo_labels.get(silo, [])),
            "tau_runtime_summary": _distribution_summary(taus),
            "log10_tau_runtime_summary": _distribution_summary(log_taus),
            "included_in_kw": silo in set(h2.get("silos_in_test") or []),
        })

    mixed = h2.get("mixed_effects_sensitivity") or {}
    variance = mixed.get("variance_components") or {}
    return {
        "hypothesis": "H2",
        "claim_role": "Silo-comparison evidence with effective-n disclosure",
        "anchor_cell": anchor_cell,
        "kruskal_wallis": {
            "test": h2.get("test"),
            "scope_rule": h2.get("scope_rule"),
            "active_p3_silos": h2.get("active_p3_silos"),
            "out_of_scope_silos_excluded": h2.get("out_of_scope_silos_excluded"),
            "n_excluded_out_of_p3_scope": h2.get("n_excluded_out_of_p3_scope"),
            "silos_in_test": h2.get("silos_in_test"),
            "n_per_silo": h2.get("n_per_silo"),
            "kw_stat": h2.get("kw_stat"),
            "kw_p_value": h2.get("kw_p_value"),
            "n_pairs": h2.get("n_pairs"),
            "n_pairs_accepted_h2": h2.get("n_pairs_accepted_h2"),
            "accept_h2_overall": h2.get("accept_h2_overall"),
        },
        "mixed_effects_sensitivity": {
            "test": mixed.get("test"),
            "axis": mixed.get("axis"),
            "n_rows": mixed.get("n_rows"),
            "n_labels": mixed.get("n_labels"),
            "n_silos": mixed.get("n_silos"),
            "joint_silo_wald_p_value": mixed.get("joint_silo_wald_p_value"),
            "icc_label": variance.get("icc_label"),
            "reject_joint_at_0_05": mixed.get("reject_joint_at_0_05"),
            "scope_rule": mixed.get("scope_rule"),
            "n_excluded_out_of_p3_scope": mixed.get("n_excluded_out_of_p3_scope"),
        },
        "effective_n_note": (
            "Headline H2 is based on one anchor-cell observation per Faithful label "
            "inside active P3 problem-domain silos only. Rows disclose all cohort "
            "silos, including out-of-P3-scope silos and silos with no Faithful "
            "anchor observation."
        ),
        "rows": rows,
    }


def _h3_evidence(table_faithful: dict, stats_report: dict) -> dict:
    h3 = stats_report.get("H3") or {}
    rows: list[dict] = []
    for profile in PROFILES:
        taus = []
        labels = []
        for label, by_cell in table_faithful.items():
            tau = (by_cell.get(f"{profile}|1e-04") or {}).get("runtime_seconds")
            if isinstance(tau, (int, float)) and tau > 0:
                taus.append(float(tau))
                labels.append(label)
        log_taus = [math.log10(v) for v in taus if v > 0]
        rows.append({
            "profile": profile,
            "epsilon": 1e-4,
            "n_labels": len(taus),
            "labels": sorted(labels),
            "tau_runtime_summary": _distribution_summary(taus),
            "log10_tau_runtime_summary": _distribution_summary(log_taus),
        })
    ordered = sorted(
        rows,
        key=lambda row: (
            row["log10_tau_runtime_summary"].get("median")
            if row["log10_tau_runtime_summary"].get("median") is not None else -math.inf
        ),
        reverse=True,
    )
    return {
        "hypothesis": "H3",
        "claim_role": "Hardware-profile runtime ordering plus structural invariants",
        "test_summary": {
            "test": h3.get("test"),
            "axis": h3.get("axis"),
            "n_labels": h3.get("n_labels"),
            "friedman_stat": h3.get("friedman_stat"),
            "friedman_p_value": h3.get("friedman_p_value"),
            "kendalls_w": h3.get("kendalls_w"),
            "accept_h3": h3.get("accept_h3"),
        },
        "profile_order_by_median_log10_tau": [row["profile"] for row in ordered],
        "rows": rows,
        "structural_invariants": h3.get("structural_invariants") or {},
    }


def _h4_failure_class(criteria: dict) -> str:
    if all(criteria.values()):
        return "strict_winner"
    if not criteria.get("C3_full_t_count_gt_0") and not criteria.get("C4_tau_tdepth_ge_10"):
        return "trivial_oracle_or_no_non_clifford_depth"
    if not criteria.get("C2_full_runtime_lt_baseline") and not criteria.get("C5_baseline_ge_0_01s"):
        return "classical_baseline_too_small_and_not_beaten"
    if not criteria.get("C2_full_runtime_lt_baseline"):
        return "full_runtime_not_below_classical_baseline"
    if not criteria.get("C5_baseline_ge_0_01s"):
        return "classical_baseline_toy_scale"
    if not criteria.get("C1_tau_runtime_lt_10"):
        return "runtime_tax_resource_dominated"
    return "mixed_failure"


def _h4_evidence(cohort: dict, stats_report: dict) -> dict:
    h4 = stats_report.get("H4") or {}
    breakdown = h4.get("per_criterion_breakdown") or {}
    per_label = breakdown.get("per_label") or {}
    criteria_order = list(H4_CRITERIA_NAMES)
    rows: list[dict] = []
    taxonomy_counts: dict[str, int] = {}
    for label, payload in sorted(per_label.items()):
        criteria = payload.get("criteria") or {}
        failure_class = _h4_failure_class(criteria)
        taxonomy_counts[failure_class] = taxonomy_counts.get(failure_class, 0) + 1
        cohort_entry = cohort["labels"].get(label) or {}
        rows.append({
            "label": label,
            "silo": cohort_entry.get("silo"),
            "fidelity": cohort_entry.get("fidelity"),
            "paper_fidelity": cohort_entry.get("paper_fidelity"),
            "faithfulness_tier": _faithfulness_tier(cohort_entry),
            "faithfulness_review_verdict": cohort_entry.get("faithfulness_review_verdict"),
            "n_criteria_passed": payload.get("n_criteria_passed"),
            "passes_all": payload.get("passes_all"),
            "failure_class": failure_class,
            "failed_criteria": payload.get("failed_criteria") or [],
            "criteria": criteria,
            "metrics": payload.get("metrics") or {},
        })

    funnel = []
    current = rows
    for criterion in criteria_order:
        current = [row for row in current if (row.get("criteria") or {}).get(criterion) is True]
        funnel.append({
            "criterion": criterion,
            "n_remaining": len(current),
            "labels_remaining": [row["label"] for row in current],
        })

    near_misses = sorted(
        rows,
        key=lambda row: (-(row.get("n_criteria_passed") or 0), row["label"]),
    )
    return {
        "hypothesis": "H4",
        "claim_role": "Strict-advantage subset and failure-mechanism evidence",
        "anchor_cell": h4.get("anchor_cell"),
        "faithful_subcohort_size": h4.get("faithful_subcohort_size"),
        "canonical_winners": h4.get("canonical_winners"),
        "canonical_winners_count": h4.get("canonical_winners_count"),
        "bifurcation_holds": h4.get("bifurcation_holds"),
        "criteria_definitions": breakdown.get("criteria_definitions") or {},
        "per_criterion_failure_counts": breakdown.get("per_criterion_failure_counts") or {},
        "per_criterion_failure_rate": breakdown.get("per_criterion_failure_rate") or {},
        "failure_taxonomy_counts": dict(sorted(taxonomy_counts.items())),
        "criteria_funnel": funnel,
        "near_misses_by_criteria_passed": near_misses,
        "rows": rows,
        "faithfulness_tier_sensitivity": h4.get("faithfulness_tier_sensitivity"),
        "qdk_nontriviality_sensitivity": h4.get("qdk_nontriviality_sensitivity"),
        "leave_one_out": h4.get("leave_one_out"),
        "vincent_review_cross_tab": h4.get("vincent_review_cross_tab"),
        "sensitivity": {
            "tau_winners": h4.get("sensitivity_tau_winners"),
            "baseline_winners": h4.get("sensitivity_baseline_winners"),
            "no_svm_substitution": h4.get("sensitivity_no_svm_substitution"),
            "no_non_exact_phase8b_baseline": h4.get("sensitivity_no_non_exact_phase8b_baseline"),
            "strongest_classical_alt_top3": h4.get("sensitivity_strongest_classical_alt_top3"),
        },
    }


def _engine_failure_evidence(records: list[dict], faithful: set[str]) -> dict:
    by_profile: dict[str, dict[str, int]] = {}
    by_cell: dict[str, dict[str, int]] = {}
    reasons: dict[str, int] = {}
    h4_anchor_impacted: set[str] = set()
    status_counts = {"ok": 0, "engine_failure": 0, "other": 0}
    for rec in records:
        measured = rec.get("measured") or {}
        status = measured.get("status") or rec.get("status")
        if status == "ok" or status == "success":
            norm_status = "ok"
        elif status == "engine_failure":
            norm_status = "engine_failure"
        elif any(isinstance(measured.get(key), (int, float)) for key in RESOURCE_AXES):
            norm_status = "ok"
        else:
            norm_status = "other"
        status_counts[norm_status] = status_counts.get(norm_status, 0) + 1

        profile = rec.get("hardware_profile", "unknown")
        profile_bucket = by_profile.setdefault(profile, {"total": 0, "ok": 0, "engine_failure": 0, "other": 0})
        profile_bucket["total"] += 1
        profile_bucket[norm_status] = profile_bucket.get(norm_status, 0) + 1

        eps = rec.get("epsilon")
        mode = rec.get("accounting_mode", "unknown")
        cell_key = f"{profile}|{eps:.0e}|{mode}" if isinstance(eps, (int, float)) else f"{profile}|unknown|{mode}"
        cell_bucket = by_cell.setdefault(cell_key, {"total": 0, "ok": 0, "engine_failure": 0, "other": 0})
        cell_bucket["total"] += 1
        cell_bucket[norm_status] = cell_bucket.get(norm_status, 0) + 1

        if norm_status == "engine_failure":
            reason = measured.get("reason") or rec.get("reason") or "unknown"
            reasons[reason] = reasons.get(reason, 0) + 1
            if (rec.get("label") in faithful
                    and rec.get("hardware_profile") == H4_ANCHOR_PROFILE
                    and rec.get("epsilon") == H4_ANCHOR_EPS
                    and rec.get("accounting_mode") in {"bare", "full"}):
                h4_anchor_impacted.add(rec.get("label"))

    return {
        "claim_role": "Completeness, exclusion, and limitations disclosure",
        "total_records": len(records),
        "status_counts": status_counts,
        "engine_failure_rate": (
            status_counts.get("engine_failure", 0) / len(records) if records else None
        ),
        "by_profile": dict(sorted(by_profile.items())),
        "by_profile_epsilon_mode": dict(sorted(by_cell.items())),
        "engine_failure_reasons": dict(sorted(reasons.items(), key=lambda kv: (-kv[1], kv[0]))),
        "h4_anchor_impacted_faithful_labels": sorted(h4_anchor_impacted),
        "h4_anchor_impact_note": (
            "H4 requires both bare and full records at the anchor cell for each Faithful label; "
            "labels listed here would be excluded from H4 due to final engine_failure."
        ),
    }


def _claims_evidence_matrix(evidence: dict) -> list[dict]:
    h1 = evidence["H1"]
    h2 = evidence["H2"]
    h3 = evidence["H3"]
    h4 = evidence["H4"]
    failures = evidence["engine_failures"]
    return [
        {
            "claim_id": "P4-COMPLETE-AUDITABLE",
            "claim": "The canonical P4 resource-estimation grid is complete and suitable for downstream statistical reporting.",
            "scope": "canonical Phase 8 grid",
            "primary_evidence": ["evidence_report.json:engine_failures", "audit_phase8.json", "stats_report.json"],
            "key_numbers": {
                "total_records": failures.get("total_records"),
                "engine_failures": (failures.get("status_counts") or {}).get("engine_failure"),
            },
            "manuscript_use": "Methods/Results completeness paragraph and limitations disclosure",
        },
        {
            "claim_id": "H1-NO-ORDER-MAGNITUDE-ORACLE-TAX",
            "claim": "The legacy Faithful cohort does not support the pre-registered claim that median full-vs-bare oracle tax exceeds 10x across the grid; the observed runtime tau range is consistent with small template/oracle overhead rather than paper-exact oracle scaling.",
            "scope": "Legacy Faithful labels only",
            "primary_evidence": ["table_h1_full_matrix.tex", "figure_h1_heatmap.csv", "stats_report.json:H1"],
            "key_numbers": {
                "accepted_tests_by_axis": h1.get("accepted_tests_by_axis"),
                "runtime_median_tau_range": h1.get("runtime_median_tau_range"),
            },
            "manuscript_use": "Results H1 subsection",
        },
        {
            "claim_id": "H2-NO-ROBUST-SILO-SEPARATION",
            "claim": "Application silo does not explain a statistically robust separation in anchor-cell runtime oracle tax.",
            "scope": "Faithful anchor-cell observations; MixedLM sensitivity across cells",
            "primary_evidence": ["table_h2_silo_effects.tex", "stats_report.json:H2"],
            "key_numbers": {
                "kw_p_value": (h2.get("kruskal_wallis") or {}).get("kw_p_value"),
                "mixedlm_joint_p": (h2.get("mixed_effects_sensitivity") or {}).get("joint_silo_wald_p_value"),
                "icc_label": (h2.get("mixed_effects_sensitivity") or {}).get("icc_label"),
            },
            "manuscript_use": "Results H2 subsection and Discussion methodological caveat",
        },
        {
            "claim_id": "H3-RUNTIME-ONLY-PROFILE-EFFECT",
            "claim": "Hardware profile is meaningful for runtime but non-runtime logical axes are structural invariants under the estimator model.",
            "scope": "Faithful labels with complete profile blocks at epsilon=1e-4",
            "primary_evidence": ["table_h3_profile_ordering.tex", "stats_report.json:H3", "figure_h3_runtime_ecdf.png"],
            "key_numbers": h3.get("test_summary"),
            "manuscript_use": "Results H3 subsection and methods block on structural invariants",
        },
        {
            "claim_id": "H4-EMPTY-STRICT-SUBSET",
            "claim": "No legacy Faithful label satisfies all five strict-H4 criteria. The observed bifurcation is transparent but partly structural under the current template/family-faithful implementations, so it is evidence about this cohort and implementation model rather than a field-wide no-advantage theorem.",
            "scope": "Legacy Faithful labels at maj_e6_floquet, epsilon=1e-4",
            "primary_evidence": ["table_h4_scoreboard.tex", "table_h4_failure_taxonomy.tex", "figure_h4_funnel.csv", "stats_report.json:H4"],
            "key_numbers": {
                "canonical_winners_count": h4.get("canonical_winners_count"),
                "failure_taxonomy_counts": h4.get("failure_taxonomy_counts"),
                "per_criterion_failure_counts": h4.get("per_criterion_failure_counts"),
                "faithfulness_tier_sensitivity": h4.get("faithfulness_tier_sensitivity"),
                "qdk_nontriviality_sensitivity": h4.get("qdk_nontriviality_sensitivity"),
            },
            "manuscript_use": "Headline Results and Discussion contribution",
        },
        {
            "claim_id": "F-TIER-NOT-PAPER-EXACT",
            "claim": "The legacy Faithful set is not equivalent to a paper-exact implementation set; the strict paper-faithful tier is empty under the current audit layer, and the existing H4 headline should be interpreted as a template/family-faithful result.",
            "scope": "S2-backed Faithful labels and Vincent faithfulness reviews",
            "primary_evidence": ["stats_report.json:H4.faithfulness_tier_sensitivity", "evidence_report.json:faithfulness_tiers", "audit_phase4_faithfulness.json"],
            "key_numbers": evidence.get("faithfulness_tiers"),
            "manuscript_use": "Methods faithfulness taxonomy, Results faithfulness-yield paragraph, and limitations framing",
        },
        {
            "claim_id": "PHASE8D-APPENDIX-ONLY",
            "claim": "Fixed-precision QAE/HHL Phase 8d results are a separate appendix-only experiment regime and must not mutate headline H1-H4 claims.",
            "scope": "Phase 8d QAE/HHL scout",
            "primary_evidence": [
                "evidence_report.json:experiment_regimes",
                "table_experiment_regimes.tex",
                "table_phase8d_regime_summary.tex",
                "key_numbers.json:phase8d_qae_hhl",
                "audit_phase8d.json",
            ],
            "key_numbers": {},
            "manuscript_use": "Appendix scaling and limitations after salvage sync completes",
        },
    ]


def _build_evidence_report(
    cohort: dict,
    records: list[dict],
    faithful: set[str],
    table_faithful: dict,
    stats_report: dict,
) -> dict:
    evidence = {
        "schema": "phase9_evidence_report.1.2",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "source_inputs": [
            str(COHORT.relative_to(ROOT)).replace("\\", "/"),
            str(STATS_REPORT.relative_to(ROOT)).replace("\\", "/"),
            str(ORACLE_TAX_TABLE.relative_to(ROOT)).replace("\\", "/"),
            str(SENSITIVITY.relative_to(ROOT)).replace("\\", "/"),
        ],
        "cohort": _cohort_counts(cohort),
        "faithfulness_tiers": _faithfulness_tier_summary(cohort),
        "experiment_regimes": _experiment_regimes_evidence(cohort),
        "H1": _h1_evidence(stats_report),
        "H2": _h2_evidence(table_faithful, cohort, stats_report),
        "H3": _h3_evidence(table_faithful, stats_report),
        "H4": _h4_evidence(cohort, stats_report),
        "engine_failures": _engine_failure_evidence(records, faithful),
    }
    evidence["claims_evidence_matrix"] = _claims_evidence_matrix(evidence)
    return evidence


def main() -> int:
    cohort = json.loads(COHORT.read_text(encoding="utf-8"))
    _ensure_phase8_complete(cohort)
    faithful = {lid for lid, e in cohort["labels"].items() if e.get("fidelity") == "F"}

    records = _load_records()
    print(f"[Phase 9] loaded {len(records)} records from {RESULTS.relative_to(ROOT)}")
    print(f"[Phase 9] Faithful sub-cohort size: {len(faithful)}")

    idx = _index(records)
    table_full = _oracle_tax(idx)
    table_faithful = _oracle_tax(idx, faithful_only=faithful)
    ORACLE_TAX_TABLE.parent.mkdir(parents=True, exist_ok=True)
    ORACLE_TAX_TABLE.write_text(json.dumps({
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "n_labels_full": len(table_full),
        "n_labels_faithful": len(table_faithful),
        "table_faithful": table_faithful,
        "table_full": table_full,
    }, indent=2), encoding="utf-8")
    print(f"[Phase 9] oracle_tax_table.json -> {ORACLE_TAX_TABLE.relative_to(ROOT)}")

    st = _try_scipy()
    h1 = _h1(table_faithful, st)
    h2 = _h2(table_faithful, cohort, st)
    h3 = _h3(table_faithful, st)
    h4 = _h4(idx, faithful, cohort)

    seed_grid_sensitivity = _seed_grid_sensitivity(
        table_faithful, st,
        h1_canonical=h1, h3_canonical=h3, h4_canonical=h4,
    )

    stats_report = {
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "subcohort": f"Faithful ({len(faithful)}/{len(cohort['labels'])} current canonical)",
        "scipy_available": st is not None,
        "H1": h1,
        "H2": h2,
        "H3": h3,
        "H4": h4,
        "seed_grid_sensitivity": seed_grid_sensitivity,
    }
    STATS_REPORT.parent.mkdir(parents=True, exist_ok=True)
    STATS_REPORT.write_text(json.dumps(stats_report, indent=2), encoding="utf-8")
    print(f"[Phase 9] stats_report.json    -> {STATS_REPORT.relative_to(ROOT)}")
    print(f"[Phase 9] seed_grid_sensitivity: SEED_GRID = "
          f"{[hex(s) for s in SEED_GRID]}")

    SENSITIVITY.parent.mkdir(parents=True, exist_ok=True)
    SENSITIVITY.write_text(json.dumps({
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "tau_grid": H4_TAU_GRID,
        "baseline_perturbations": ["baseline_x10", "baseline_div10"],
        "H4_sensitivity": h4,
    }, indent=2), encoding="utf-8")
    print(f"[Phase 9] sensitivity_grid.json -> {SENSITIVITY.relative_to(ROOT)}")

    evidence_report = _build_evidence_report(
        cohort=cohort,
        records=records,
        faithful=faithful,
        table_faithful=table_faithful,
        stats_report=stats_report,
    )
    EVIDENCE_REPORT.parent.mkdir(parents=True, exist_ok=True)
    EVIDENCE_REPORT.write_text(json.dumps(evidence_report, indent=2), encoding="utf-8")
    print(f"[Phase 9] evidence_report.json    -> {EVIDENCE_REPORT.relative_to(ROOT)}")

    # Phase status.
    ps = cohort.get("_phase_status")
    if not isinstance(ps, dict):
        ps = {"_legacy": ps} if ps is not None else {}
    ps["phase9"] = {
        "status": "complete",
        "completed_utc": datetime.now(timezone.utc).isoformat(),
        "n_records_used": len(records),
        "faithful_subcohort_size": len(faithful),
        "h4_canonical_winners_count": h4["canonical_winners_count"],
        "h4_bifurcation_holds": h4["bifurcation_holds"],
        "evidence_report": str(EVIDENCE_REPORT.relative_to(ROOT)).replace("\\", "/"),
    }
    cohort["_phase_status"] = ps
    COHORT.write_text(json.dumps(cohort, indent=2), encoding="utf-8")

    print(f"\n[Phase 9] H4 canonical winners: {h4['canonical_winners_count']} "
          f"({'BIFURCATION HOLDS' if h4['bifurcation_holds'] else 'COUNTER-EXAMPLE'})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
