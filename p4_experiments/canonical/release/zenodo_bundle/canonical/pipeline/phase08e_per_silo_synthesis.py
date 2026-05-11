"""Phase 8e — Per-silo synthesis cards.

Read-only with respect to canonical pipeline data (cohort labels,
result records, stats_report, oracle_tax_table, sensitivity_grid,
key_numbers.json). Writes:

    p4_experiments/canonical/outputs/phase08e_per_silo/<silo_id>.json
    p4_experiments/canonical/outputs/phase08e_per_silo/per_silo_synthesis.json
    p4_experiments/canonical/outputs/phase08e_per_silo/sweep_record.schema.json
    p4_experiments/canonical/outputs/manuscript_artifacts/table_silo_<silo_id>_h4.tex     (6)
        p4_experiments/canonical/outputs/manuscript_artifacts/table_silo_<silo_id>_phase8d.tex (6)

Adds (additive only) cohort['_phase_status']['phase8e'] = {status, completed_utc}.

Idempotent. Single-thread enforced. Canonical SEED constant carried for
provenance only (no RNG calls in this phase).
"""
from __future__ import annotations

import json
import os
import re
import subprocess
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# ---- Single-thread + seed (provenance) ---------------------------------------
for _v in ("OMP_NUM_THREADS", "MKL_NUM_THREADS",
           "OPENBLAS_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ.setdefault(_v, "1")
CANONICAL_SEED = 0x50414D50

# ---- Paths -------------------------------------------------------------------
ROOT = Path(__file__).resolve().parents[3]
CANON = ROOT / "p4_experiments" / "canonical"
COHORT_PATH = CANON / "cohort.json"
REPORTS = CANON / "reports"
STATS_PATH = REPORTS / "stats_report.json"
ORACLE_PATH = REPORTS / "oracle_tax_table.json"
SENSITIVITY_PATH = REPORTS / "sensitivity_grid.json"
OUTPUTS = CANON / "outputs"
KEYNUM_PATH = OUTPUTS / "manuscript_artifacts" / "key_numbers.json"
S8C_DIR = OUTPUTS / "phase08c_alternatives"
PHASE8D_STATUS = OUTPUTS / "phase08d_qae_hhl_scout" / "phase8d_status.json"
RESULTS_DIR = ROOT / "p4_experiments" / "common" / "output" / "results"

OUT_DIR = OUTPUTS / "phase08e_per_silo"
ARTI_DIR = OUTPUTS / "manuscript_artifacts"
SCHEMA_PATH = OUT_DIR / "sweep_record.schema.json"

# ---- Constants ---------------------------------------------------------------
SCHEMA_TAG = "phase8e.1.1"
ANCHOR_PROFILE = "maj_e6_floquet"
ANCHOR_EPSILON = 1e-04
ANCHOR_EPS_FILE = "1e-04"
ANCHOR_MODE = "full"
ALL_PROFILES = ("maj_e6_floquet", "maj_e6_surface",
                "sc_e3_surface", "sc_e4_surface",
                "ti_e3_surface", "ti_e4_surface")
ALL_MODES = ("bare", "full")
# Canonical H4 winner predicate (mirrors stats_report.H4.per_criterion_breakdown.criteria_definitions):
#   C1_tau_runtime_lt_10:  tau_runtime = full_runtime / bare_runtime < 10
#   C2_full_runtime_lt_baseline: full_runtime < classical_baseline_seconds
#   C3_full_t_count_gt_0:  full T-count > 0 (oracle is non-trivial)
#   C4_tau_tdepth_ge_10:   tau_t_depth = full_t_depth / bare_t_depth >= 10
#   C5_baseline_ge_0_01s:  classical_baseline_seconds >= 0.01 (not toy-scale)
TAU_THRESHOLD = 10.0
BASELINE_MIN_SECONDS = 0.01

HONEST_TO_ENT = {"B3": "B3", "B4": "B4", "B5": "B5", "SQ17": "B3"}

SILO_DIR_OVERRIDE = {
    "derivative-pricing": "derivative_pricing",
    "quantum-ml-finance": "quantum_ml_finance",
    "portfolio-optimization": "portfolio_optimization",
    "simulation-monte-carlo": "simulation_monte_carlo",
    "risk-management": "risk_management",
    "fraud-detection": "fraud_detection",
    "insurance-actuarial": "insurance_actuarial",
    "cryptography-security": "cryptography_security",
    "trading-execution": "trading_execution",
    "other": "cross_silo_other",
}

SILO_HUMAN_NAME = {
    "derivative-pricing": "Derivative pricing",
    "quantum-ml-finance": "Quantum ML for finance",
    "portfolio-optimization": "Portfolio optimization",
    "simulation-monte-carlo": "Simulation / Monte Carlo",
    "risk-management": "Risk management",
    "fraud-detection": "Fraud detection",
    "insurance-actuarial": "Insurance / actuarial",
    "cryptography-security": "Cryptography / security",
    "trading-execution": "Trading execution",
    "other": "Cross-silo / other",
}


def _card_kind(n_F: int) -> str:
    if n_F == 0:
        return "f-zero"
    if n_F == 1:
        return "case-study"
    if n_F == 2:
        return "descriptive"
    return "deep"


def _read_json(p: Path) -> Any:
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


def _write_json(p: Path, obj: Any) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, indent=2, sort_keys=False), encoding="utf-8")


def _git_commit() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=str(ROOT),
            stderr=subprocess.DEVNULL).decode().strip()
    except Exception:
        return "unknown"


def _record_path(label: str, profile: str, eps_file: str, mode: str) -> Path:
    return RESULTS_DIR / f"{label}_{profile}_eps{eps_file}_{mode}.json"


def _runtime_for(label: str, profile: str, mode: str,
                 eps_file: str = ANCHOR_EPS_FILE) -> float | None:
    rec = _read_json(_record_path(label, profile, eps_file, mode))
    if not rec:
        return None
    rt = (rec.get("measured") or {}).get("runtime_seconds")
    return rt if isinstance(rt, (int, float)) else None


def _anchor_values(label: str) -> dict[str, Any]:
    full = _read_json(_record_path(label, ANCHOR_PROFILE, ANCHOR_EPS_FILE, "full"))
    bare = _read_json(_record_path(label, ANCHOR_PROFILE, ANCHOR_EPS_FILE, "bare"))
    fm = (full or {}).get("measured", {}) or {}
    bm = (bare or {}).get("measured", {}) or {}
    return {
        "logical_qubits": fm.get("logical_qubits"),
        "physical_qubits": fm.get("physical_qubits"),
        "t_count": fm.get("t_count"),
        "t_depth": fm.get("t_depth"),
        "runtime_seconds": fm.get("runtime_seconds"),
        "bare_runtime_seconds": bm.get("runtime_seconds"),
        "bare_t_depth": bm.get("t_depth"),
    }


def _h4_row(label: str, classical_seconds: float | None) -> dict[str, Any]:
    v = _anchor_values(label)
    full_rt = v["runtime_seconds"]
    bare_rt = v["bare_runtime_seconds"]
    full_td = v["t_depth"]
    bare_td = v["bare_t_depth"]
    full_tc = v["t_count"]

    def _num(x):
        return isinstance(x, (int, float)) and x is not None

    tau_runtime = (full_rt / bare_rt) if (_num(full_rt) and _num(bare_rt) and bare_rt > 0) else None
    tau_tdepth = (full_td / bare_td) if (_num(full_td) and _num(bare_td) and bare_td > 0) else None

    c1 = bool(tau_runtime is not None and tau_runtime < TAU_THRESHOLD)
    c2 = bool(_num(full_rt) and _num(classical_seconds) and full_rt < classical_seconds)
    c3 = bool(_num(full_tc) and full_tc > 0)
    c4 = bool(tau_tdepth is not None and tau_tdepth >= TAU_THRESHOLD)
    c5 = bool(_num(classical_seconds) and classical_seconds >= BASELINE_MIN_SECONDS)
    passes = c1 and c2 and c3 and c4 and c5
    return {
        "anchor": {"profile": ANCHOR_PROFILE,
                   "epsilon": ANCHOR_EPSILON, "mode": ANCHOR_MODE},
        "C1_tau_runtime_lt_10": c1,
        "C2_full_runtime_lt_baseline": c2,
        "C3_full_t_count_gt_0": c3,
        "C4_tau_tdepth_ge_10": c4,
        "C5_baseline_ge_0_01s": c5,
        "passes_all_5": passes,
        "values": {**v,
                   "tau_runtime": tau_runtime,
                   "tau_t_depth": tau_tdepth,
                   "classical_baseline_seconds": classical_seconds},
    }


def _hardware_sensitivity_row(label: str) -> dict[str, dict[str, float | None]]:
    out: dict[str, dict[str, float | None]] = {}
    for prof in ALL_PROFILES:
        out[prof] = {m: _runtime_for(label, prof, m) for m in ALL_MODES}
    return out


def _phase8c_top3(label: str) -> dict | None:
    p = S8C_DIR / f"{label}.json"
    rec = _read_json(p)
    if not rec:
        return None
    meas = rec.get("measurements", {}) or {}
    out = {}
    for rank in ("rank1", "rank2", "rank3"):
        if rank not in meas:
            continue
        b = meas[rank]
        out[rank] = {
            "kernel": b.get("kernel"),
            "wall_clock_seconds_median": b.get("wall_clock_seconds_median"),
            "wall_clock_seconds_iqr": b.get("wall_clock_seconds_iqr"),
            "n_repeats_completed": b.get("n_repeats_completed"),
        }
    return out or None


_IMPORT_RE = re.compile(
    r"from\s+p4_experiments\.(?:common|core)\.templates\.(\w+)\s+import")


def _candidate_circuit_paths(label_entry: dict) -> list[Path]:
    # Use only the active cohort circuit paths. Retired release archives are
    # intentionally not searched.
    paths: list[Path] = []
    inv = label_entry.get("circuit_inventory") or {}
    for src in (label_entry.get("circuit_path"), inv.get("circuit_path")):
        if src:
            paths.append(ROOT / src)
    return paths


def _detect_template_ent(label: str, label_entry: dict,
                         instance_cache: dict) -> tuple[str | None, str | None]:
    # Scan ALL existing candidates and pick first one whose imports match a
    # known template; do not bail out on a candidate that exists but has no
    # template imports (paper_id may collide across experiments).
    last_existing_imports: set[str] | None = None
    for p in _candidate_circuit_paths(label_entry):
        if not p.exists():
            continue
        try:
            text = p.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        imports = set(_IMPORT_RE.findall(text))
        if last_existing_imports is None:
            last_existing_imports = imports
        if "ansatz_stretch" in imports:
            return "tmpl_ansatz_stretch", "per-template-not-paper-algorithm"
        if "amplitude_encoding" in imports:
            return "tmpl_amp_encoding", "per-template-not-paper-algorithm"
        if "qae" in imports or "sim_mc_state_prep" in imports or "qgan_qae" in imports:
            return "tmpl_qae_simmc", "per-template-not-paper-algorithm"
        if "hhl" in imports:
            inst = instance_cache.get(label) or {}
            sp = inst.get("sparsity")
            if sp == 3:
                return "tmpl_hhl_sp3", "per-template-not-paper-algorithm"
            if sp == 8:
                return "tmpl_hhl_sp8", "per-template-not-paper-algorithm"
            return None, "hhl-sparsity-ambiguous"
    if last_existing_imports is None:
        return None, "template-mapping-unknown"
    return None, "template-mapping-unknown"


def _phase8d_lookup(label: str, label_entry: dict, fidelity_sub: str,
                    phase8d_status: dict, instance_cache: dict) -> dict | None:
    if not fidelity_sub.startswith("paper-faithful"):
        return None
    return {
        "ent_id_used": None,
        "kind": "qae_hhl_fixed_precision_high_n",
        "k_classical": None,
        "by_profile": {},
        "stage": phase8d_status.get("stage"),
        "appendix_caveat": (
            "Phase 8d is the fixed-precision QAE/HHL high-N scout, "
            "reported separately rather than as a per-label N* table"
        ),
    }


def _bottom_f_zero(silo: str, n_P: int, top_family: str) -> str:
    return (f"Silo {silo} has 0 legacy Faithful entries (n_P={n_P}). "
            f"The proxy cohort suggests {top_family}. "
            "No quantitative quantum-vs-classical claim is made.")


def _bottom_descriptive(silo: str, n_F: int, labels: list[str],
                        strict_count: int, template_count: int,
                        h4_pass_count: int, baseline_win_count: int,
                        non_toy_baseline_count: int,
                        median_tau: float | None) -> str:
    tau = "n/a" if median_tau is None else f"{median_tau:.3g}"
    return (f"Silo {silo} has n_F={n_F} legacy Faithful entries "
            f"({strict_count} paper-exact strict, {template_count} "
            f"template/family tier): {', '.join(labels)}. Anchor-cell "
            f"all-criteria H4 passes: {h4_pass_count}/{n_F}; full-mode "
            f"runtime beats the available classical baseline (C2) in "
            f"{baseline_win_count}/{n_F}; non-toy baseline support (C5) "
            f"holds in {non_toy_baseline_count}/{n_F}. Median full/bare "
            f"oracle tax across legacy F = {tau}. No silo-level "
            "statistical claim is made because the sample is too small.")


def _bottom_deep(silo: str, n_F: int, n_families: int, p_pass: int,
                 baseline_win_count: int, non_toy_baseline_count: int,
                 strict_count: int, template_count: int,
                 median_runtime: float | None, median_tau: float | None,
                 phase8d_caveat: str) -> str:
    rt = "n/a" if median_runtime is None else f"{median_runtime:.3g}s"
    tau = "n/a" if median_tau is None else f"{median_tau:.3g}"
    return (f"Silo {silo} has n_F={n_F} legacy Faithful entries "
            f"({strict_count} paper-exact strict, {template_count} "
            f"template/family tier) spanning {n_families} algorithm "
            f"families. At the anchor cell, all-criteria H4 passes are "
            f"{p_pass}/{n_F}; full-mode runtime beats the available "
            f"classical baseline (C2) in {baseline_win_count}/{n_F}; "
            f"non-toy baseline support (C5) holds in "
            f"{non_toy_baseline_count}/{n_F}. Median full-mode runtime = "
            f"{rt}. Median full/bare oracle tax = {tau}. This is "
            f"per-silo descriptive evidence, not a silo-level "
            f"statistical test. {phase8d_caveat}")


def _bottom_case(silo: str, label: str, family: str,
                 rt: float | None, cb: float | None, pass_n: int,
         strict_count: int, template_count: int,
         b: float | None, r2: float | None,
         n_star: float | None) -> str:
    rt_s = "n/a" if rt is None else f"{rt:.3g}s"
    cb_s = "n/a" if cb is None else f"{cb:.3g}s"
    ratio = "n/a" if (rt is None or cb is None or cb == 0) else f"{rt/cb:.1f}"
    return (f"Silo {silo} is illustrated by one legacy Faithful label, "
            f"{label} ({family}; {strict_count} paper-exact strict, "
            f"{template_count} template/family tier). "
            f"At the anchor cell: runtime={rt_s}, classical baseline={cb_s}, "
            f"ratio={ratio}. C1-C5 verdict: {pass_n}/5. "
            "No silo-level statistical claim is made from a single label. "
            "Phase 8d is reported separately as a fixed-precision QAE/HHL "
            "high-N scout.")


def _build_card(silo: str, labels_in_silo: list[tuple[str, dict]],
                cohort: dict, oracle: dict, phase8d_status: dict,
                instance_cache: dict) -> dict:
    F = sorted([L for L, e in labels_in_silo
                if e.get("paper_fidelity", "").startswith("paper-faithful")])
    P = sorted([L for L, e in labels_in_silo
                if e.get("paper_fidelity") == "proxy"])
    fid_counter = Counter(e.get("paper_fidelity", "unknown")
                          for _, e in labels_in_silo)
    sub_hist = {k: int(fid_counter.get(k, 0)) for k in
                ("paper-faithful-honest", "paper-faithful-template", "proxy")}
    tier_counter = Counter(e.get("faithfulness_tier", "unknown")
                           for _, e in labels_in_silo)
    tier_hist = {k: int(tier_counter.get(k, 0)) for k in
                 ("paper-faithful-strict", "paper-family-template", "proxy")}
    review_counter = Counter(
        e.get("faithfulness_review_verdict", "unknown")
        for _, e in labels_in_silo
        if e.get("paper_fidelity", "").startswith("paper-faithful")
    )
    review_hist = dict(sorted(review_counter.items()))
    fam_hist = dict(Counter(e.get("algorithm_family", "unknown")
                            for _, e in labels_in_silo))

    n_F, n_P = len(F), len(P)
    strict_count = int(tier_counter.get("paper-faithful-strict", 0))
    template_count = int(tier_counter.get("paper-family-template", 0))
    kind = _card_kind(n_F)
    flag = "f_zero" if n_F == 0 else ("descriptive" if n_F <= 2 else "full")

    label_family = {L: cohort["labels"][L].get("algorithm_family", "unknown")
                    for L in F}

    h4: dict[str, Any] = {}
    p8c: dict[str, Any] = {}
    hw: dict[str, Any] = {}
    p8d: dict[str, Any] = {}
    for L in F:
        e = cohort["labels"][L]
        cb = (e.get("classical_baseline") or {}).get("wall_clock_seconds")
        h4[L] = _h4_row(L, cb)
        top3 = _phase8c_top3(L)
        if top3:
            p8c[L] = top3
        hw[L] = _hardware_sensitivity_row(L)
        p8d[L] = _phase8d_lookup(L, e, e.get("paper_fidelity", ""),
                                 phase8d_status, instance_cache)

    oracle_subset = {}
    table_faithful = oracle.get("table_faithful", {}) or {}
    anchor_key = f"{ANCHOR_PROFILE}|{ANCHOR_EPS_FILE}"
    for L in F:
        cell = (table_faithful.get(L) or {}).get(anchor_key) or {}
        rt = cell.get("runtime_seconds")
        if rt is not None:
            oracle_subset[L] = rt

    if kind == "f-zero":
        top_fam = (Counter(cohort["labels"][L].get("algorithm_family", "unknown")
                           for L in P).most_common(1) or [("none", 0)])[0][0]
        bottom = _bottom_f_zero(silo, n_P, top_fam)
    elif kind == "descriptive":
        h4_pass = sum(1 for L in F if h4[L]["passes_all_5"])
        baseline_wins = sum(1 for L in F if h4[L]["C2_full_runtime_lt_baseline"])
        non_toy_baselines = sum(1 for L in F if h4[L]["C5_baseline_ge_0_01s"])
        taus = sorted(v for v in oracle_subset.values() if v is not None)
        med_tau = taus[len(taus) // 2] if taus else None
        bottom = _bottom_descriptive(
            silo, n_F, F, strict_count, template_count, h4_pass,
            baseline_wins, non_toy_baselines, med_tau)
    elif kind == "deep":
        h4_pass = sum(1 for L in F if h4[L]["passes_all_5"])
        baseline_wins = sum(1 for L in F if h4[L]["C2_full_runtime_lt_baseline"])
        non_toy_baselines = sum(1 for L in F if h4[L]["C5_baseline_ge_0_01s"])
        rts = sorted(h4[L]["values"]["runtime_seconds"] for L in F
                     if isinstance(h4[L]["values"]["runtime_seconds"], (int, float)))
        med_rt = rts[len(rts) // 2] if rts else None
        taus = sorted(v for v in oracle_subset.values() if v is not None)
        med_tau = taus[len(taus) // 2] if taus else None
        n_fams = len(set(label_family.values()))
        caveats = sorted({(p8d[L] or {}).get("appendix_caveat")
                          for L in F if (p8d[L] or {}).get("appendix_caveat")})
        cav_sentence = (f"Phase 8d caveats: {', '.join(caveats)}."
                        if caveats else
                        "Phase 8d: per-paper N* table appendix-only.")
        bottom = _bottom_deep(silo, n_F, n_fams, h4_pass,
                              baseline_wins, non_toy_baselines,
                              strict_count, template_count,
                              med_rt, med_tau, cav_sentence)
    else:  # case-study
        L = F[0]
        v = h4[L]["values"]
        c_keys = ("C1_tau_runtime_lt_10", "C2_full_runtime_lt_baseline",
                  "C3_full_t_count_gt_0", "C4_tau_tdepth_ge_10",
                  "C5_baseline_ge_0_01s")
        pass_n = sum(1 for k in c_keys if h4[L][k])
        prof_block = ((p8d[L] or {}).get("by_profile") or {}).get(ANCHOR_PROFILE) or {}
        bottom = _bottom_case(silo, L, label_family[L],
                              v["runtime_seconds"],
                              v["classical_baseline_seconds"],
                              pass_n, strict_count, template_count,
                              prof_block.get("b"), prof_block.get("r2"),
                              prof_block.get("n_star"))

    claim_scope = {
        "legacy_faithful_count": n_F,
        "paper_exact_strict_count": strict_count,
        "template_family_count": template_count,
        "proxy_count": n_P,
        "headline_interpretation": (
            "Per-silo cards summarize the legacy F/P cohort for context. "
            "They do not convert template/family-faithful labels into "
            "paper-exact implementations, and they do not add a new "
            "silo-level hypothesis test."
        ),
    }

    return {
        "schema": SCHEMA_TAG,
        "silo_id": silo,
        "name": SILO_HUMAN_NAME[silo],
        "card_kind": kind,
        "n_F": n_F, "n_P": n_P,
        "label_list_F": F, "label_list_P": P,
        "paper_fidelity_subhist": sub_hist,
        "faithfulness_tier_histogram": tier_hist,
        "faithfulness_review_verdict_histogram": review_hist,
        "claim_scope": claim_scope,
        "algorithm_family_histogram": fam_hist,
        "label_family_F": label_family,
        "h4_scoreboard": h4,
        "phase8c_top3_classical": p8c,
        "oracle_tax_table_subset": oracle_subset,
        "hardware_sensitivity": hw,
        "phase8d_per_label_n_star": p8d,
        "phase8d_qae_hhl_scout": {
            "track": "qae_hhl_fixed_precision_high_n",
            "stage": phase8d_status.get("stage"),
            "status_path": str(PHASE8D_STATUS.relative_to(ROOT)).replace("\\", "/"),
        },
        "bottom_line_paragraph": bottom,
        "data_completeness_flag": flag,
    }


def _tick(b: bool) -> str:
    return r"\checkmark" if b else r"$\times$"


def _emit_h4_table(silo: str, card: dict) -> str:
    rows = []
    fam_map = card.get("label_family_F", {}) or {}
    for L in card["label_list_F"]:
        h = card["h4_scoreboard"][L]
        v = h["values"]
        rt = "—" if not isinstance(v["runtime_seconds"], (int, float)) \
            else f"{v['runtime_seconds']:.3g}"
        lq = "—" if v["logical_qubits"] is None else f"{v['logical_qubits']}"
        tc = "—" if not isinstance(v["t_count"], (int, float)) \
            else f"{v['t_count']:.3g}"
        fam = (fam_map.get(L) or "—").replace("_", r"\_")
        rows.append(" & ".join([
            L, fam, rt, lq, tc,
            _tick(h["C1_tau_runtime_lt_10"]),
            _tick(h["C2_full_runtime_lt_baseline"]),
            _tick(h["C3_full_t_count_gt_0"]),
            _tick(h["C4_tau_tdepth_ge_10"]),
            _tick(h["C5_baseline_ge_0_01s"]),
            _tick(h["passes_all_5"]),
        ]) + r" \\")
    body = "\n".join(rows) if rows else r"\multicolumn{11}{c}{(no F labels)} \\"
    return (
        r"\begin{tabular}{lllrrrccccccc}" + "\n"
        r"\hline" + "\n"
        r"label & family & runtime (s) & $Q_{\mathrm{log}}$ & $T$-count "
        r"& C1 & C2 & C3 & C4 & C5 & all-5 \\" + "\n"
        r"\hline" + "\n"
        + body + "\n"
        r"\hline" + "\n"
        r"\end{tabular}" + "\n"
    )


def _emit_phase8d_table(silo: str, card: dict) -> str:
    rows = []
    for L in card["label_list_F"]:
        rows.append(" & ".join([
            L,
            "fixed-precision QAE/HHL scout reported separately",
        ]) + r" \\")
    body = "\n".join(rows) if rows else r"\multicolumn{2}{c}{(no faithful labels)} \\" 
    return (
        r"\begin{tabular}{ll}" + "\n"
        r"\hline" + "\n"
        r"label & Phase 8d scope \\" + "\n"
        r"\hline" + "\n"
        + body + "\n"
        r"\hline" + "\n"
        r"\end{tabular}" + "\n"
    )


SCHEMA_DOC = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "Per-silo synthesis card (Phase 8e)",
    "$id": "phase8e.1.1",
    "type": "object",
    "properties": {
        "schema": {"const": SCHEMA_TAG},
        "silo_id": {"type": "string"},
        "name": {"type": "string"},
        "card_kind": {"enum":
                      ["deep", "descriptive", "case-study", "spotlight", "f-zero"]},
        "n_F": {"type": "integer", "minimum": 0},
        "n_P": {"type": "integer", "minimum": 0},
        "label_list_F": {"type": "array", "items": {"type": "string"}},
        "label_list_P": {"type": "array", "items": {"type": "string"}},
        "paper_fidelity_subhist": {"type": "object"},
        "faithfulness_tier_histogram": {"type": "object"},
        "faithfulness_review_verdict_histogram": {"type": "object"},
        "claim_scope": {"type": "object"},
        "algorithm_family_histogram": {"type": "object"},
        "label_family_F": {"type": "object"},
        "h4_scoreboard": {"type": "object"},
        "phase8c_top3_classical": {"type": "object"},
        "oracle_tax_table_subset": {"type": "object"},
        "hardware_sensitivity": {"type": "object"},
        "phase8d_per_label_n_star": {"type": "object"},
        "phase8d_qae_hhl_scout": {"type": "object"},
        "bottom_line_paragraph": {"type": "string"},
        "data_completeness_flag": {"enum": ["full", "descriptive", "f_zero"]},
    },
    "required": ["schema", "silo_id", "card_kind", "n_F", "n_P",
                 "label_list_F", "label_list_P",
                 "faithfulness_tier_histogram", "claim_scope",
                 "bottom_line_paragraph", "data_completeness_flag"],
}


def main() -> int:
    cohort = _read_json(COHORT_PATH)
    oracle = _read_json(ORACLE_PATH) or {}
    phase8d_status = _read_json(PHASE8D_STATUS) or {}

    labels = cohort["labels"]
    by_silo: dict[str, list[tuple[str, dict]]] = {}
    for L, e in labels.items():
        by_silo.setdefault(e["silo"], []).append((L, e))

    expected = sorted(by_silo.keys())
    if not expected:
        raise SystemExit("Phase 8e requires at least one cohort silo")
    missing_names = sorted(set(expected) - set(SILO_HUMAN_NAME))
    if missing_names:
        raise SystemExit(
            "Phase 8e missing human-readable names for silos: "
            f"{missing_names}"
        )

    instance_cache: dict[str, dict] = {}
    for L, e in labels.items():
        ip = e.get("instance_path")
        candidates = []
        if ip:
            candidates.append(ROOT / ip)
        for p in candidates:
            if p.exists():
                try:
                    instance_cache[L] = json.loads(
                        p.read_text(encoding="utf-8"))
                except Exception:
                    pass
                break

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    ARTI_DIR.mkdir(parents=True, exist_ok=True)
    _write_json(SCHEMA_PATH, SCHEMA_DOC)

    rollup = {
        "schema": SCHEMA_TAG,
        "silos": expected,
        "totals": {"n_F": 0, "n_P": 0, "n_labels": 0},
        "by_silo": {},
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "git_commit": _git_commit(),
        "seed": hex(CANONICAL_SEED),
        "phase8d_track": "qae_hhl_fixed_precision_high_n",
        "phase8d_stage": phase8d_status.get("stage"),
    }

    for silo in expected:
        card = _build_card(silo, by_silo[silo], cohort, oracle, phase8d_status,
                           instance_cache)
        _write_json(OUT_DIR / f"{silo}.json", card)
        rollup["totals"]["n_F"] += card["n_F"]
        rollup["totals"]["n_P"] += card["n_P"]
        rollup["totals"]["n_labels"] += card["n_F"] + card["n_P"]
        rollup["by_silo"][silo] = {
            "card_kind": card["card_kind"],
            "n_F": card["n_F"], "n_P": card["n_P"],
            "has_phase8d_data": any(
                (v or {}).get("ent_id_used")
                for v in card["phase8d_per_label_n_star"].values()),
        }
        if card["n_F"] >= 1:
            (ARTI_DIR / f"table_silo_{silo}_h4.tex").write_text(
                _emit_h4_table(silo, card), encoding="utf-8")
            (ARTI_DIR / f"table_silo_{silo}_phase8d.tex").write_text(
                _emit_phase8d_table(silo, card), encoding="utf-8")

    _write_json(OUT_DIR / "per_silo_synthesis.json", rollup)

    ps = cohort.get("_phase_status") or {}
    ps["phase8e"] = {
        "status": "complete",
        "completed_utc": datetime.now(timezone.utc).isoformat(),
        "n_cards": len(expected),
        "totals": rollup["totals"],
    }
    cohort["_phase_status"] = ps
    COHORT_PATH.write_text(json.dumps(cohort, indent=2), encoding="utf-8")

    print(f"[Phase 8e] {len(expected)} silo cards written -> {OUT_DIR}")
    print(f"[Phase 8e] totals: {rollup['totals']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
