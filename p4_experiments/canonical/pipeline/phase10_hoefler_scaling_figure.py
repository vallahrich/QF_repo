"""Phase 10 figure: Hoefler-style crossover-scale plot (time vs N).

Reproduces the work-depth runtime model from Hoefler, Häner & Troyer
(2023), "Disentangling Hype from Practicality", CACM 66(5), 82-87,
doi:10.1145/3571725 (published version of arXiv:2307.00523), and overlays
the P4 cohort's measured wall-clock as a sanity check.

Model
-----
Classical: T_c(N) = N^k · M · t_c   (k > 1 for any quantum speedup)
Quantum  : T_q(N) = N   · M · t_q

with t_c = 1 / r_c, t_q = 1 / r_q the per-op latencies of the chosen
classical chip and the optimistic future fault-tolerant quantum chip.
We use Hoefler's Table 1 numbers for fp16:

  r_c (NVIDIA A100, fp16)            = 195 Top/s    -> t_c = 5.13e-15 s
  r_c (ASIC, A100-tech budget, fp16) = 0.55 Pop/s   -> t_c = 1.82e-15 s
  r_q (10k logical qubits, fp16)     = 10.5 kop/s   -> t_q = 9.52e-5  s

Crossover N* (classical = quantum, fixed M=1, k=2):
  N* = (t_q / t_c)^{1/(k-1)}

Practical-deadline cap (1e6 s ≈ 2 weeks; Hoefler Fig. 1):
  T_q(N) <= 1e6  =>  N <= 1e6 / t_q ≈ 1.05e10  (fp16, 1 op per oracle)

Output
------
This optional renderer can recreate thesis/appendix figure files on demand, but
rendered figures are excluded from the P4 handoff package.
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import matplotlib

matplotlib.use("Agg")  # headless
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[3]
CANON = ROOT / "p4_experiments" / "canonical"
RESULTS = ROOT / "p4_experiments" / "common" / "output" / "results"
OUTPUTS = CANON / "outputs"
FIG_DIR = OUTPUTS / "figures"
FIG_DIR.mkdir(parents=True, exist_ok=True)
DOC_FIG_DIR = ROOT / "docs" / "figures"
DOC_FIG_DIR.mkdir(parents=True, exist_ok=True)
PHASE8D_SUMMARY = OUTPUTS / "phase08d_qae_hhl_scout" / "summary.json"

# --- Hoefler Table 1 constants (per-op latency, seconds) -------------------
# All for fp16, the regime Hoefler reports in the prose (10.5 kop/s).
T_C_GPU_FP16  = 1.0 / 195e12      # A100 GPU
T_C_ASIC_FP16 = 1.0 / 0.55e15     # A100-tech ASIC
T_Q_FT_FP16   = 1.0 / 10.5e3      # 10k logical qubits, 10us cycle
DEADLINE_S    = 1e6               # ≈ 2 weeks (Hoefler "practical" cap)


def _t_classical(N: np.ndarray, k: float, t_c: float, M: float = 1.0) -> np.ndarray:
    return (N ** k) * M * t_c


def _t_quantum(N: np.ndarray, t_q: float, M: float = 1.0) -> np.ndarray:
    return N * M * t_q


def _crossover_N(t_c: float, t_q: float, k: float, M: float = 1.0) -> float:
    """N at which T_c = T_q for fixed M, k>1."""
    if k <= 1:
        return float("nan")
    return (t_q / t_c) ** (1.0 / (k - 1.0))


def _max_N_within_deadline_quantum(t_q: float, deadline_s: float = DEADLINE_S,
                                   M: float = 1.0) -> float:
    return deadline_s / (t_q * M)


def _load_p4_overlay() -> list[dict]:
    """Load the P4 anchor-cell measurements for an overlay of our cohort.

    For each Faithful label, we read the canonical anchor cell
    (qubit_gate_ns_e3 / 1e-3 / full) and produce a (T_count, runtime_s)
    point. T_count is a *proxy* for "operations executed" — not exactly
    Hoefler's M·N (which counts oracle queries × oracle work) but the
    closest measured analog we have.
    """
    # Anchor cell matches Phase 9 H4 anchor:
    #   profile = maj_e6_floquet, epsilon = 1e-3, mode = full.
    from p4_experiments.canonical.pipeline.phase09_stats import (
        H4_ANCHOR_PROFILE, H4_ANCHOR_EPS,
    )
    cohort = json.loads((CANON / "cohort.json").read_text(encoding="utf-8"))
    faithful = {lid for lid, e in cohort["labels"].items()
                if e.get("fidelity") == "F"}
    points = []
    for path in RESULTS.glob("*.json"):
        try:
            rec = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        lid = rec.get("label")
        if lid not in faithful:
            continue
        if rec.get("hardware_profile") != H4_ANCHOR_PROFILE:
            continue
        if abs(float(rec.get("epsilon", 0.0)) - H4_ANCHOR_EPS) > 1e-12:
            continue
        if rec.get("accounting_mode") != "full":
            continue
        m = rec.get("measured") or {}
        if m.get("status") == "engine_failure":
            continue
        tc = m.get("t_count")
        rt = m.get("runtime_seconds")
        if not (isinstance(tc, (int, float)) and isinstance(rt, (int, float))):
            continue
        if tc <= 0 or rt <= 0:
            continue
        points.append({"label": lid, "t_count": float(tc), "runtime_s": float(rt)})
    return points


def _load_phase8d_overlay() -> tuple[list[dict], dict[str, int]]:
    """Load canonical Phase 8d QAE/HHL scout rows for Panel B.

    Phase 8d is appendix-only for claims, but it is directly relevant to this
    Hoefler-style scaling diagram because it is the local high-N scout. We plot
    only rows with QDK estimates (`status == "ok"`) and keep failure counts in
    the sidecar.
    """
    if not PHASE8D_SUMMARY.exists():
        return [], {}
    try:
        summary = json.loads(PHASE8D_SUMMARY.read_text(encoding="utf-8"))
    except Exception:
        return [], {}
    status_counts = {
        str(key): int(value)
        for key, value in (summary.get("by_status") or {}).items()
        if isinstance(value, int)
    }
    points: list[dict] = []
    for row in summary.get("rows") or []:
        if row.get("status") != "ok":
            continue
        n_value = row.get("n_value")
        runtime_s = row.get("runtime_seconds")
        if not (isinstance(n_value, (int, float)) and isinstance(runtime_s, (int, float))):
            continue
        if n_value <= 0 or runtime_s <= 0:
            continue
        points.append({
            "entity_id": row.get("entity_id"),
            "family": row.get("family"),
            "hardware_profile": row.get("hardware_profile"),
            "m_precision_qubits": row.get("m_precision_qubits"),
            "n_value": float(n_value),
            "runtime_s": float(runtime_s),
            "logical_qubits": row.get("logical_qubits"),
            "physical_qubits": row.get("physical_qubits"),
            "t_count": row.get("t_count"),
            "t_depth": row.get("t_depth"),
            "epsilon": row.get("epsilon"),
        })
    return points, status_counts


def make_figure() -> dict:
    # x-axis: N (oracle queries / problem size)
    N = np.logspace(0, 18, 400)

    # Curves
    t_c = T_C_GPU_FP16
    t_q = T_Q_FT_FP16

    classical_k1 = _t_classical(N, 1.0, t_c)  # no speedup baseline
    classical_k2 = _t_classical(N, 2.0, t_c)  # Grover (quadratic)
    classical_k3 = _t_classical(N, 3.0, t_c)  # cubic
    classical_k4 = _t_classical(N, 4.0, t_c)  # quartic
    quantum     = _t_quantum  (N, t_q)

    # Crossover N's for each k
    Nx_k2 = _crossover_N(t_c, t_q, 2.0)
    Nx_k3 = _crossover_N(t_c, t_q, 3.0)
    Nx_k4 = _crossover_N(t_c, t_q, 4.0)

    # Max N the quantum machine can do within 2-week deadline
    Nq_max = _max_N_within_deadline_quantum(t_q)

    # ----- Figure -----
    fig, axes = plt.subplots(1, 2, figsize=(13.5, 5.4))

    # Panel A: time vs N (Hoefler Fig. 1 reproduction)
    ax = axes[0]
    ax.loglog(N, classical_k1, color="#777777", lw=1.5, ls=":",
              label=r"Classical, no speedup $T_c \propto N$")
    ax.loglog(N, classical_k2, color="#1f77b4", lw=2.0, ls="-",
              label=r"Classical $T_c \propto N^2$ (Grover)")
    ax.loglog(N, classical_k3, color="#1f77b4", lw=1.6, ls="--",
              label=r"Classical $T_c \propto N^3$ (cubic)")
    ax.loglog(N, classical_k4, color="#1f77b4", lw=1.2, ls="-.",
              label=r"Classical $T_c \propto N^4$ (quartic)")
    ax.loglog(N, quantum,     color="#d62728", lw=2.4, ls="-",
              label=r"Quantum $T_q \propto N$  (10.5 kop/s, fp16)")

    # 2-week deadline + crossover markers
    ax.axhline(DEADLINE_S, color="black", lw=1.0, ls=(0, (3, 3)))
    ax.text(N[-1], DEADLINE_S * 1.4, "2-week practical deadline ($10^{6}$ s)",
            ha="right", va="bottom", fontsize=8.5)
    ax.axvline(Nq_max, color="#d62728", lw=0.8, ls=":", alpha=0.55)
    ax.text(Nq_max, ax.get_ylim()[0] * 50,
            f"  $N_q^{{\\max}}$ = {Nq_max:.1e}",
            color="#d62728", fontsize=8, rotation=90, va="bottom", ha="left")

    for Nx, label, color in [
        (Nx_k2, r"$N^*_{k=2}$", "#1f77b4"),
        (Nx_k3, r"$N^*_{k=3}$", "#1f77b4"),
        (Nx_k4, r"$N^*_{k=4}$", "#1f77b4"),
    ]:
        if not np.isfinite(Nx):
            continue
        ax.plot([Nx], [_t_quantum(np.array([Nx]), t_q)[0]], "o",
                color=color, ms=6, mec="black", mew=0.6)

    ax.set_xlabel(r"Oracle queries / problem size $N$")
    ax.set_ylabel("Runtime (s)")
    ax.set_title("A. Hoefler–Häner–Troyer (2023) crossover model, fp16\n"
                 "GPU $t_c{=}5.1{\\times}10^{-15}$ s vs FT-quantum "
                 "$t_q{=}9.5{\\times}10^{-5}$ s")
    ax.legend(loc="upper left", fontsize=7.6, framealpha=0.92)
    ax.grid(True, which="both", ls=":", lw=0.4, alpha=0.5)
    ax.set_xlim(1, 1e18)
    ax.set_ylim(1e-15, 1e15)

    # Panel B: P4 cohort overlay — measured (T-count, runtime) for Faithful labels
    ax = axes[1]
    points = _load_p4_overlay()
    phase8d_points, phase8d_status_counts = _load_phase8d_overlay()
    if points:
        xs = np.array([p["t_count"] for p in points])
        ys = np.array([p["runtime_s"] for p in points])
        ax.loglog(xs, ys, "o", color="#2ca02c", ms=7, mec="black", mew=0.6,
                  label=f"P4 Faithful anchor cell (n={len(points)})")
        # Annotate a few extremes
        i_lo = int(np.argmin(ys)); i_hi = int(np.argmax(ys))
        for i in {i_lo, i_hi}:
            ax.annotate(points[i]["label"], (xs[i], ys[i]),
                        fontsize=7.5, xytext=(5, 5), textcoords="offset points")

    if phase8d_points:
        family_colors = {"hhl": "#9467bd", "qae": "#ff7f0e"}
        profile_markers = {"maj_e6_floquet": "s", "maj_e6_surface": "^"}
        families = sorted({p.get("family") for p in phase8d_points}, key=lambda value: str(value))
        profiles = sorted({p.get("hardware_profile") for p in phase8d_points}, key=lambda value: str(value))
        for family in families:
            for profile in profiles:
                group = [
                    p for p in phase8d_points
                    if p.get("family") == family and p.get("hardware_profile") == profile
                ]
                if not group:
                    continue
                xs = np.array([p["n_value"] for p in group])
                ys = np.array([p["runtime_s"] for p in group])
                sizes = np.array([
                    28.0 + 6.0 * max(float(p.get("m_precision_qubits") or 4) - 4.0, 0.0)
                    for p in group
                ])
                family_label = str(family).upper() if family else "unknown"
                profile_label = str(profile).replace("maj_e6_", "") if profile else "unknown"
                ax.scatter(
                    xs,
                    ys,
                    s=sizes,
                    marker=profile_markers.get(profile, "D"),
                    color=family_colors.get(family, "#8c564b"),
                    edgecolors="black",
                    linewidths=0.45,
                    alpha=0.68,
                    label=f"Phase 8d {family_label}, {profile_label}",
                    zorder=4,
                )
        largest = max(phase8d_points, key=lambda p: p["n_value"])
        ax.annotate(
            "Phase 8d scout",
            (largest["n_value"], largest["runtime_s"]),
            fontsize=7.5,
            xytext=(6, -10),
            textcoords="offset points",
        )

    # Reference lines (re-plotted for context, light)
    ax.loglog(N, classical_k2, color="#1f77b4", lw=1.4, ls="-", alpha=0.55,
              label=r"Classical (A100 GPU), $T_c \propto N^2$")
    ax.loglog(N, quantum,     color="#d62728", lw=1.8, ls="-", alpha=0.85,
              label=r"Quantum FT, $T_q \propto N$ (per oracle op)")
    ax.axhline(DEADLINE_S, color="black", lw=1.0, ls=(0, (3, 3)))
    ax.text(N[-1], DEADLINE_S * 1.4, "2-week deadline",
            ha="right", va="bottom", fontsize=8.5)

    ax.set_xlabel(r"$N$  (P4 anchor: T-count; Phase 8d: problem size; Hoefler: oracle queries)", fontsize=8.5)
    ax.set_ylabel("Runtime (s)")
    ax.set_title("B. P4 anchor-cell and Phase 8d scout measurements vs Hoefler band\n"
                 "(Phase 8d plotted as appendix-only high-N scout evidence)")
    ax.legend(loc="upper left", fontsize=7.6, framealpha=0.92)
    ax.grid(True, which="both", ls=":", lw=0.4, alpha=0.5)
    ax.set_xlim(1, 1e18)
    ax.set_ylim(1e-3, 1e15)

    fig.suptitle("Hoefler-style scaling: time vs N  (Phase 10 figure)",
                 fontsize=11.5, y=1.02)
    fig.tight_layout()

    out_png_doc = DOC_FIG_DIR / "p4_hoefler_crossover.png"
    out_pdf_doc = DOC_FIG_DIR / "p4_hoefler_crossover.pdf"
    out_png_can = FIG_DIR    / "p4_hoefler_crossover.png"
    fig.savefig(out_png_doc, dpi=160, bbox_inches="tight")
    fig.savefig(out_pdf_doc, bbox_inches="tight")
    fig.savefig(out_png_can, dpi=160, bbox_inches="tight")
    plt.close(fig)

    # JSON sidecar with the constants and crossover values
    sidecar = {
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "model": (
            "Hoefler, Haner & Troyer (CACM 2023, doi:10.1145/3571725) "
            "work-depth crossover: T_c = N^k * M * t_c, T_q = N * M * t_q. "
            "fp16 constants from Table 1."
        ),
        "constants": {
            "t_c_GPU_fp16_s_per_op":  T_C_GPU_FP16,
            "t_c_ASIC_fp16_s_per_op": T_C_ASIC_FP16,
            "t_q_FT_fp16_s_per_op":   T_Q_FT_FP16,
            "deadline_seconds":       DEADLINE_S,
        },
        "crossover_N_at_M_eq_1": {
            "k=2": _crossover_N(T_C_GPU_FP16, T_Q_FT_FP16, 2.0),
            "k=3": _crossover_N(T_C_GPU_FP16, T_Q_FT_FP16, 3.0),
            "k=4": _crossover_N(T_C_GPU_FP16, T_Q_FT_FP16, 4.0),
        },
        "max_quantum_N_within_deadline": _max_N_within_deadline_quantum(T_Q_FT_FP16),
        "p4_overlay_points": points,
        "phase8d_overlay_points": phase8d_points,
        "phase8d_overlay_status_counts": phase8d_status_counts,
        "outputs": {
            "doc_png":    str(out_png_doc.relative_to(ROOT)).replace("\\", "/"),
            "doc_pdf":    str(out_pdf_doc.relative_to(ROOT)).replace("\\", "/"),
            "canon_png":  str(out_png_can.relative_to(ROOT)).replace("\\", "/"),
        },
    }
    out_json = FIG_DIR / "p4_hoefler_crossover.json"
    out_json.write_text(json.dumps(sidecar, indent=2), encoding="utf-8")
    print(f"[hoefler-fig] PNG -> {out_png_doc.relative_to(ROOT)}")
    print(f"[hoefler-fig] PDF -> {out_pdf_doc.relative_to(ROOT)}")
    print(f"[hoefler-fig] JSON -> {out_json.relative_to(ROOT)}")
    print(f"[hoefler-fig] crossover N (k=2): {sidecar['crossover_N_at_M_eq_1']['k=2']:.3e}")
    print(f"[hoefler-fig] crossover N (k=3): {sidecar['crossover_N_at_M_eq_1']['k=3']:.3e}")
    print(f"[hoefler-fig] crossover N (k=4): {sidecar['crossover_N_at_M_eq_1']['k=4']:.3e}")
    print(f"[hoefler-fig] max N quantum/2wk: {sidecar['max_quantum_N_within_deadline']:.3e}")
    print(f"[hoefler-fig] cohort overlay points: {len(points)}")
    print(f"[hoefler-fig] phase8d overlay points: {len(phase8d_points)}")
    return sidecar


def main(argv: list[str] | None = None) -> int:
    make_figure()
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
