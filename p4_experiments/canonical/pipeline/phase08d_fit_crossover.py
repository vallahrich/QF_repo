"""Legacy Phase 8d fit + crossover analysis.

Canonical Phase 8d is now the fixed-precision QAE/HHL high-N scout in
``phase8d_qae_hhl_scout.py``. This historical B12 fitter is retained only for
reproducing the deprecated Hoefler N-sweep artifacts and requires
``--legacy-ok`` before it will run.

Reads `s8d_n_sweep/results/*.json` produced by `phase8d_n_sweep.py`,
fits a power law `T_q(N) = a * N^b` to runtime_seconds vs N (log-log
OLS) per (entity, hardware_profile), and computes crossover N* against
the classical baseline `T_c(N) = t_c * N^k` from the canonical Hoefler
model (Phase 10).

Family-default classical k (Track A; documented in DECISIONS_LOG):
    B3, B4, B5                : k = 2 (quantum-svm, AE family)
  tmpl_ansatz_stretch       : k = 2 (defensive default)
  tmpl_amp_encoding         : k = 2
  tmpl_qae_simmc            : k = 2
  tmpl_hhl_sp3, tmpl_hhl_sp8: k = 3 (linear systems)

Outputs (all additive; never mutates locked artefacts):
  s8d_n_sweep/phase8d_crossover.json
    outputs/manuscript_artifacts/table_b12_n_star.tex   (B12.A per-paper + B12.B per-template)
    outputs/manuscript_artifacts/key_numbers_phase8d.json
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[3]
CANON = ROOT / "p4_experiments" / "canonical"
SWEEP = CANON / "s8d_n_sweep"
RESULTS = SWEEP / "results"
OUT_JSON = SWEEP / "phase8d_crossover.json"
ARTI = CANON / "outputs" / "manuscript_artifacts"

from p4_experiments.canonical.pipeline.phase10_hoefler_scaling_figure import (
    T_C_GPU_FP16, T_Q_FT_FP16, DEADLINE_S,
)

FAMILY_DEFAULT_K = {
    "B3": 2, "B4": 2, "B5": 2,
    "tmpl_ansatz_stretch": 2, "tmpl_amp_encoding": 2,
    "tmpl_qae_simmc": 2, "tmpl_hhl_sp3": 3, "tmpl_hhl_sp8": 3,
}


def _collect_points(entity_id: str, profile: str) -> list[tuple[int, float]]:
    pts = []
    if not RESULTS.exists():
        return pts
    for p in sorted(RESULTS.glob(f"{entity_id}__N*__{profile}__eps*.json")):
        rec = json.loads(p.read_text(encoding="utf-8"))
        if rec.get("status") != "ok":
            continue
        n = rec.get("n_value")
        rt = (rec.get("measured") or {}).get("runtime_seconds")
        if isinstance(n, int) and isinstance(rt, (int, float)) and rt > 0:
            pts.append((int(n), float(rt)))
    return sorted(pts)


def _fit_powerlaw(pts: list[tuple[int, float]]) -> dict:
    if len(pts) < 4:
        return {"a": None, "b": None, "r2": None,
                "n_points": len(pts), "fit_status": "insufficient_points"}
    Ns = np.array([p[0] for p in pts], dtype=float)
    ts = np.array([p[1] for p in pts], dtype=float)
    x, y = np.log10(Ns), np.log10(ts)
    b, log_a = np.polyfit(x, y, 1)
    y_hat = b * x + log_a
    ss_res = float(np.sum((y - y_hat) ** 2))
    ss_tot = float(np.sum((y - y.mean()) ** 2))
    r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else None
    status = "ok" if (r2 is not None and r2 >= 0.95) else "low_r2"
    return {"a": float(10 ** log_a), "b": float(b), "r2": r2,
            "n_points": len(pts), "fit_status": status}


def _solve_n_star(a, b, k: float, t_c: float, deadline_s: float) -> dict:
    if a is None or b is None or k <= b:
        return {"n_star": None, "reason": "no_crossover_in_powerlaw_regime",
                "deadline_capped": False, "k_classical_assumed": k}
    n_star = (a / t_c) ** (1.0 / (k - b))
    n_q_deadline = (deadline_s / a) ** (1.0 / b) if b > 0 else float("inf")
    return {"n_star": float(n_star),
            "n_quantum_max_within_deadline": float(n_q_deadline),
            "n_star_within_deadline": bool(n_star <= n_q_deadline),
            "deadline_capped": False,
            "k_classical_assumed": k}


def fit_all() -> dict:
    from p4_experiments.canonical.pipeline.phase08d_n_sweep import (
        PER_PAPER_ENTITIES, PER_TEMPLATE_ENTITIES, PROFILES,
    )
    out = {"per_entity": {}, "constants": {
        "t_c": T_C_GPU_FP16, "t_q": T_Q_FT_FP16, "deadline_s": DEADLINE_S,
    }}
    for ent_id in list(PER_PAPER_ENTITIES) + list(PER_TEMPLATE_ENTITIES):
        per_profile = {}
        for prof in PROFILES:
            pts = _collect_points(ent_id, prof)
            fit = _fit_powerlaw(pts)
            xover = _solve_n_star(fit["a"], fit["b"], FAMILY_DEFAULT_K[ent_id],
                                  T_C_GPU_FP16, DEADLINE_S)
            per_profile[prof] = {"points": pts, "fit": fit, "crossover": xover}
        out["per_entity"][ent_id] = {
            "kind": "per-paper" if ent_id in PER_PAPER_ENTITIES else "per-template",
            "k_classical": FAMILY_DEFAULT_K[ent_id],
            "by_profile": per_profile,
        }
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(out, indent=2), encoding="utf-8")
    return out


def _b12_row(ent, prof, fit, xo, caveat=False) -> str:
    b   = "---" if fit["b"]  is None else f"{fit['b']:.2f}"
    r2  = "---" if fit["r2"] is None else f"{fit['r2']:.3f}"
    nst = "n/a" if xo["n_star"] is None else f"{xo['n_star']:.2e}"
    stat = fit["fit_status"]
    if caveat:
        stat += " *template"
    prof_safe = prof.replace('_', r'\_')
    ent_safe = ent.replace('_', r'\_')
    return rf"{ent_safe} & {prof_safe} & {b} & {r2} & {nst} & {stat} \\"


def emit_b12_table(crossover: dict) -> None:
    lines = [r"\begin{tabular}{llrrrl}", r"\toprule",
             r"Entity & Profile & b (exponent) & R$^2$ & $N^*$ & Status \\",
             r"\midrule",
             r"\multicolumn{6}{l}{\textbf{B12.A --- Per-paper (3 retained builders)}} \\"]
    for ent_id in ["B3", "B4", "B5"]:
        block = crossover["per_entity"].get(ent_id)
        if not block:
            continue
        for prof, pp in block["by_profile"].items():
            lines.append(_b12_row(ent_id, prof, pp["fit"], pp["crossover"]))
    lines.append(r"\midrule")
    lines.append(r"\multicolumn{6}{l}{\textbf{B12.B --- Per-template "
                 r"(\emph{not the paper's algorithm}; family-default $k$)}} \\")
    for ent_id in ["tmpl_ansatz_stretch", "tmpl_amp_encoding",
                   "tmpl_qae_simmc", "tmpl_hhl_sp3", "tmpl_hhl_sp8"]:
        block = crossover["per_entity"].get(ent_id)
        if not block:
            continue
        for prof, pp in block["by_profile"].items():
            lines.append(_b12_row(ent_id, prof, pp["fit"], pp["crossover"], caveat=True))
    lines.append(r"\bottomrule")
    lines.append(r"\end{tabular}")
    ARTI.mkdir(parents=True, exist_ok=True)
    (ARTI / "table_b12_n_star.tex").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--legacy-ok", action="store_true",
                        help="Run the deprecated B12 fitter.")
    args = parser.parse_args(argv)
    if not args.legacy_ok:
        print("[phase8d-fit-legacy] Deprecated path. Canonical Phase 8d is "
              "phase8d_qae_hhl_scout.py + phase8d_finalize_qae_hhl.py. "
              "Pass --legacy-ok only to reproduce historical B12 artifacts.")
        return 2

    crossover = fit_all()
    emit_b12_table(crossover)
    n_promising = sum(
        1 for v in crossover["per_entity"].values()
        for p in v["by_profile"].values()
        if (p["crossover"].get("n_star_within_deadline") is True)
    )
    kn = {
        "n_entities_swept": len(crossover["per_entity"]),
        "n_promising_within_deadline": n_promising,
        "headline_excludes_phase8d": True,
        "appendix_only": True,
    }
    (ARTI / "key_numbers_phase8d.json").write_text(
        json.dumps(kn, indent=2), encoding="utf-8")
    print(f"[phase8d-fit] {len(crossover['per_entity'])} entities; "
          f"{n_promising} cells crossed within deadline")
    print(f"[phase8d-fit] wrote {OUT_JSON}")
    print(f"[phase8d-fit] wrote {ARTI / 'table_b12_n_star.tex'}")
    print(f"[phase8d-fit] wrote {ARTI / 'key_numbers_phase8d.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
