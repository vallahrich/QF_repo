"""Generate Chapter 7 regime-backbone artifacts (T5, H3 6-row body table, and
appendix detail tables) at the canonical H4 anchor (eps=1e-4).

Outputs (under p4_experiments/canonical/outputs/manuscript_artifacts/):
  - table_h_regime_backbone.tex      (T5: H1-H4 x R1/R2 backbone)
  - table_h3_profile_regime_body.tex (H3 6-row profile x regime body table)
  - table_h_regime_appendix_detail.tex (full per-(H, profile, regime) detail)

Reads existing canonical CSVs only; no pipeline re-run.
"""
from __future__ import annotations

import csv
import json
import statistics as st
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / "p4_experiments/canonical/outputs/manuscript_artifacts"
RESULTS = ROOT / "p4_experiments/common/output/results"

ANCHOR_PROFILE = "maj_e6_floquet"
ANCHOR_EPS = 1e-4

PROFILE_DISPLAY = {
    "maj_e6_floquet": r"\hwid{maj\_e6\_floquet}",
    "maj_e6_surface": r"\hwid{maj\_e6\_surface}",
    "sc_e3_surface": r"\hwid{sc\_e3\_surface}",
    "sc_e4_surface": r"\hwid{sc\_e4\_surface}",
    "ti_e3_surface": r"\hwid{ti\_e3\_surface}",
    "ti_e4_surface": r"\hwid{ti\_e4\_surface}",
}
PROFILE_ORDER = [
    "maj_e6_floquet",
    "maj_e6_surface",
    "sc_e3_surface",
    "sc_e4_surface",
    "ti_e4_surface",
    "ti_e3_surface",
]


def _load_audit() -> dict[str, dict]:
    """label -> {regime, h4_eligible, faithfulness_tier, silo}."""
    out: dict[str, dict] = {}
    with open(ART / "h4_anchor_tcost_label_audit.csv", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            out[r["label"]] = {
                "regime": r["t_count_regime"],
                "h4_eligible": r["h4_eligible"] == "True",
                "tier": r["faithfulness_tier"],
                "silo": r["silo"],
            }
    return out


def _load_runtime_at_eps() -> dict[tuple[str, str, str], float]:
    """(label, profile, accounting_mode) -> runtime_seconds at ANCHOR_EPS."""
    rt: dict[tuple[str, str, str], float] = {}
    for p in sorted(RESULTS.glob("*.json")):
        d = json.loads(p.read_text(encoding="utf-8"))
        if d.get("epsilon") != ANCHOR_EPS:
            continue
        measured = d.get("measured") or {}
        raw = measured.get("raw_estimate") or {}
        if raw.get("status") != "success":
            continue
        s = measured.get("runtime_seconds")
        if s is None:
            continue
        rt[(d["label"], d["hardware_profile"], d["accounting_mode"])] = float(s)
    return rt


def _summary(vals: list[float]) -> tuple[int, float, float, float]:
    n = len(vals)
    return n, st.median(vals), min(vals), max(vals)


def _fmt(x: float) -> str:
    if x == 0:
        return "0"
    if abs(x) < 1e-2 or abs(x) >= 1e5:
        return f"{x:.2e}"
    if abs(x) < 1:
        return f"{x:.3f}"
    if abs(x) < 10:
        return f"{x:.2f}"
    if abs(x) < 1000:
        return f"{x:.1f}"
    return f"{x:.0f}"


def write_t5() -> None:
    audit = _load_audit()
    rt = _load_runtime_at_eps()

    # tau (full/bare) at the anchor profile
    tau_by_pop_regime: dict[str, dict[str, list[float]]] = {
        "ft": defaultdict(list),  # 13-label family-template H4 candidates
        "all": defaultdict(list),  # 71-label active grid
    }
    labels_by_pop_regime: dict[str, dict[str, list[str]]] = {
        "ft": defaultdict(list),
        "all": defaultdict(list),
    }
    for lbl, info in audit.items():
        regime = info["regime"]
        full = rt.get((lbl, ANCHOR_PROFILE, "full"))
        bare = rt.get((lbl, ANCHOR_PROFILE, "bare"))
        if full is None or bare is None:
            continue
        tau = full / bare
        tau_by_pop_regime["all"][regime].append(tau)
        labels_by_pop_regime["all"][regime].append(lbl)
        if info["h4_eligible"]:
            tau_by_pop_regime["ft"][regime].append(tau)
            labels_by_pop_regime["ft"][regime].append(lbl)

    def _row_fragment(pop_key: str, regime: str) -> str:
        vals = tau_by_pop_regime[pop_key][regime]
        if not vals:
            return r"\textit{n/a}"
        n, med, lo, hi = _summary(vals)
        if n == 1:
            return f"$n=1$; $\\tau={_fmt(vals[0])}$"
        return f"$n={n}$; median $\\tau={_fmt(med)}$; range {_fmt(lo)}--{_fmt(hi)}"

    rows: list[tuple[str, str, str, str, str]] = []
    # H1
    rows.append((
        "H1",
        r"R1 (zero-$T$)",
        _row_fragment("ft", "zero_logical_t_count"),
        _row_fragment("all", "zero_logical_t_count"),
        r"$\tau\!\approx\!2$ flat across profiles; below the order-of-magnitude line.",
    ))
    rows.append((
        "H1",
        r"R2 (nonzero-$T$)",
        _row_fragment("ft", "nonzero_logical_t_count"),
        _row_fragment("all", "nonzero_logical_t_count"),
        r"Order-of-magnitude line clearly cleared, but family-template $n=1$ has no test power.",
    ))
    # H2: silo composition
    def _silo_fragment(pop_key: str, regime: str) -> str:
        labs = labels_by_pop_regime[pop_key][regime]
        if not labs:
            return r"\textit{n/a}"
        silos = sorted({audit[l]["silo"] for l in labs})
        return f"$n={len(labs)}$ in {len(silos)} silo" + ("" if len(silos) == 1 else "s")

    rows.append((
        "H2",
        r"R1 (zero-$T$)",
        _silo_fragment("ft", "zero_logical_t_count"),
        _silo_fragment("all", "zero_logical_t_count"),
        r"$\tau$ flat across silos by construction; KW null is structural, not informative.",
    ))
    rows.append((
        "H2",
        r"R2 (nonzero-$T$)",
        _silo_fragment("ft", "nonzero_logical_t_count"),
        _silo_fragment("all", "nonzero_logical_t_count"),
        r"Family-template $n=1$ (\artifact{SD3}); no silo-level test possible.",
    ))
    # H3: tau spread across the 6 profiles within each regime
    def _h3_fragment(pop_key: str, regime: str) -> str:
        labs = set(labels_by_pop_regime[pop_key][regime])
        if not labs:
            return r"\textit{n/a}"
        per_profile_medians = []
        for prof in PROFILE_ORDER:
            vals = []
            for lbl in labs:
                full = rt.get((lbl, prof, "full"))
                bare = rt.get((lbl, prof, "bare"))
                if full is not None and bare is not None:
                    vals.append(full / bare)
            if vals:
                per_profile_medians.append(st.median(vals))
        if not per_profile_medians:
            return r"\textit{n/a}"
        lo = min(per_profile_medians)
        hi = max(per_profile_medians)
        return f"profile median $\\tau$: {_fmt(lo)}--{_fmt(hi)}"

    rows.append((
        "H3",
        r"R1 (zero-$T$)",
        _h3_fragment("ft", "zero_logical_t_count"),
        _h3_fragment("all", "zero_logical_t_count"),
        r"$\tau$ identical across all 6 profiles; ratio is structurally pinned.",
    ))
    rows.append((
        "H3",
        r"R2 (nonzero-$T$)",
        _h3_fragment("ft", "nonzero_logical_t_count"),
        _h3_fragment("all", "nonzero_logical_t_count"),
        r"Ratio varies by profile; absolute runtime varies $\sim\!10^{4}\times$ (Maj fast, TI slowest).",
    ))
    # H4
    rows.append((
        "H4",
        r"R1 (zero-$T$)",
        r"$n=12$; $\tau$ low",
        r"$n=62$; $\tau$ low",
        r"Cannot win: zero $T$-count makes non-triviality (C3, C4) unsatisfiable.",
    ))
    rows.append((
        "H4",
        r"R2 (nonzero-$T$)",
        r"$n=1$ (\artifact{SD3}); $\tau\!\approx\!242$",
        r"$n=9$; $\tau$ 128--698",
        r"Cannot win: $\tau$ is two orders of magnitude over (C1); comparator unbeaten (C2, C5).",
    ))

    lines: list[str] = []
    lines.append(r"\begin{tabularx}{\TableWideWidth}{@{}P{0.7cm}P{1.9cm}P{3.6cm}P{3.6cm}L@{}}")
    lines.append(r"\toprule")
    lines.append(
        r"\textbf{H} & \textbf{Regime} & \textbf{Headline ($n=13$ family-template)} & "
        r"\textbf{Backup ($n=71$ active grid)} & \textbf{Verdict reason} \\"
    )
    lines.append(r"\midrule")
    prev_h = None
    for h, regime, headline, backup, reason in rows:
        if prev_h is not None and h != prev_h:
            lines.append(r"\midrule")
        lines.append(f"{h} & {regime} & {headline} & {backup} & {reason} \\\\")
        prev_h = h
    lines.append(r"\bottomrule")
    lines.append(r"\end{tabularx}")
    out = ART / "table_h_regime_backbone.tex"
    out.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    print(f"wrote {out.relative_to(ROOT)}")


def write_h3_body_table() -> None:
    audit = _load_audit()
    rt = _load_runtime_at_eps()

    # Per-profile per-regime medians (over the 71-label active grid; n unchanged
    # by tier, since tier doesn't affect runtime).
    rows: list[tuple[str, str, str, str, str]] = []
    for prof in PROFILE_ORDER:
        prof_label = PROFILE_DISPLAY[prof]
        r1_taus, r2_taus, r1_abs, r2_abs = [], [], [], []
        for lbl, info in audit.items():
            full = rt.get((lbl, prof, "full"))
            bare = rt.get((lbl, prof, "bare"))
            if full is None or bare is None:
                continue
            tau = full / bare
            if info["regime"] == "zero_logical_t_count":
                r1_taus.append(tau)
                r1_abs.append(full)
            elif info["regime"] == "nonzero_logical_t_count":
                r2_taus.append(tau)
                r2_abs.append(full)
        rows.append((
            prof_label,
            _fmt(st.median(r1_taus)) if r1_taus else "--",
            _fmt(st.median(r2_taus)) if r2_taus else "--",
            _fmt(st.median(r1_abs)) if r1_abs else "--",
            _fmt(st.median(r2_abs)) if r2_abs else "--",
        ))

    lines: list[str] = []
    lines.append(r"\begin{tabular}{@{}lrrrr@{}}")
    lines.append(r"\toprule")
    lines.append(
        r"\textbf{Profile} & \textbf{R1 $\tau$} & \textbf{R2 $\tau$} & "
        r"\textbf{R1 abs.\ runtime (s)} & \textbf{R2 abs.\ runtime (s)} \\"
    )
    lines.append(r"\midrule")
    for prof, r1t, r2t, r1a, r2a in rows:
        lines.append(f"{prof} & {r1t} & {r2t} & {r1a} & {r2a} \\\\")
    lines.append(r"\bottomrule")
    lines.append(r"\end{tabular}")
    out = ART / "table_h3_profile_regime_body.tex"
    out.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    print(f"wrote {out.relative_to(ROOT)}")


def write_appendix_detail() -> None:
    """Full per-(profile, regime) absolute runtime + tau table."""
    audit = _load_audit()
    rt = _load_runtime_at_eps()

    lines: list[str] = []
    lines.append(r"\begin{tabular}{@{}llrrrrrr@{}}")
    lines.append(r"\toprule")
    lines.append(
        r"\textbf{Profile} & \textbf{Regime} & \textbf{$n$} & "
        r"\textbf{med.\ $\tau$} & \textbf{min $\tau$} & \textbf{max $\tau$} & "
        r"\textbf{med.\ abs.\ (s)} & \textbf{max abs.\ (s)} \\"
    )
    lines.append(r"\midrule")

    REGIMES = [
        ("zero_logical_t_count", "R1"),
        ("nonzero_logical_t_count", "R2"),
    ]
    for prof in PROFILE_ORDER:
        prof_label = PROFILE_DISPLAY[prof]
        first = True
        for regime_key, regime_short in REGIMES:
            taus, absvals = [], []
            for lbl, info in audit.items():
                if info["regime"] != regime_key:
                    continue
                full = rt.get((lbl, prof, "full"))
                bare = rt.get((lbl, prof, "bare"))
                if full is None or bare is None:
                    continue
                taus.append(full / bare)
                absvals.append(full)
            if not taus:
                continue
            n, med_t, lo_t, hi_t = _summary(taus)
            _, med_a, _, hi_a = _summary(absvals)
            prof_cell = prof_label if first else ""
            first = False
            lines.append(
                f"{prof_cell} & {regime_short} & {n} & "
                f"{_fmt(med_t)} & {_fmt(lo_t)} & {_fmt(hi_t)} & "
                f"{_fmt(med_a)} & {_fmt(hi_a)} \\\\"
            )
        lines.append(r"\midrule")
    # remove trailing midrule
    while lines and lines[-1] == r"\midrule":
        lines.pop()
    lines.append(r"\bottomrule")
    lines.append(r"\end{tabular}")
    out = ART / "table_h_regime_appendix_detail.tex"
    out.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    print(f"wrote {out.relative_to(ROOT)}")


if __name__ == "__main__":
    write_t5()
    write_h3_body_table()
    write_appendix_detail()
