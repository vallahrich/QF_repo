"""Generate Appendix I.5 Phase 8d scaling table from scout + tail records.

Reads the canonical scout cohort (phase08d_qae_hhl_scout) and the
exploratory tail (phase08d_hhl_tail_exploratory), and emits a single
table summarising fixed-precision HHL/QAE single-circuit runtime,
logical qubits, and T-depth scaling with N. Each row carries a Source
column flagging scout vs tail, and an explicit status (ok / engine
failure with reason).

Output: p4_experiments/canonical/outputs/manuscript_artifacts/
        table_phase8d_scaling.tex

No pipeline re-run; reads existing JSONs only.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / "p4_experiments/canonical/outputs/manuscript_artifacts"
SCOUT = ROOT / "p4_experiments/canonical/outputs/phase08d_qae_hhl_scout/results"
TAIL = ROOT / "p4_experiments/canonical/outputs/phase08d_hhl_tail_exploratory/results"

ENTITY_DISPLAY = {
    "hhl_s1_fixed_m": "HHL s1",
    "hhl_s2_fixed_m": "HHL s2",
    "qae_simmc_fixed_m": "QAE",
}
ENTITY_ORDER = ["hhl_s1_fixed_m", "hhl_s2_fixed_m", "qae_simmc_fixed_m"]
PROFILE_DISPLAY = {
    "maj_e6_floquet": r"\hwid{maj\_e6\_floquet}",
    "maj_e6_surface": r"\hwid{maj\_e6\_surface}",
}
PROFILE_ORDER = ["maj_e6_floquet", "maj_e6_surface"]


def _fmt_runtime(v: float | None) -> str:
    if v is None:
        return "--"
    if v < 0.01 or v >= 1e5:
        return f"{v:.2e}"
    if v < 1:
        return f"{v:.3f}"
    if v < 100:
        return f"{v:.1f}"
    return f"{v:.0f}"


def _fmt_int(v: int | None) -> str:
    if v is None:
        return "--"
    return f"{v:,}"


def _load(path: Path, source: str) -> list[dict]:
    rows = []
    for p in sorted(path.glob("*.json")):
        d = json.loads(p.read_text(encoding="utf-8"))
        m = d.get("measured") or {}
        rows.append({
            "source": source,
            "entity": d.get("entity_id"),
            "profile": d.get("hardware_profile"),
            "n": d.get("n_value"),
            "m": d.get("m_precision_qubits"),
            "status": d.get("status"),
            "reason": d.get("reason"),
            "runtime_s": m.get("runtime_seconds"),
            "log_q": m.get("logical_qubits"),
            "tdepth": m.get("t_depth"),
        })
    return rows


def main() -> None:
    rows = _load(SCOUT, "scout") + _load(TAIL, "tail")

    # Restrict to maj_e6_floquet at m=8 for scout and the highest m available
    # in the tail (m=4, 6). To keep the table compact and the cross-cohort
    # comparison apples-to-apples, we build it per (entity, profile) showing
    # all available (m, N) cells.

    # Display order: entity major, profile minor, m minor, N minor.
    rows.sort(key=lambda r: (
        ENTITY_ORDER.index(r["entity"]) if r["entity"] in ENTITY_ORDER else 99,
        PROFILE_ORDER.index(r["profile"]) if r["profile"] in PROFILE_ORDER else 99,
        r["m"] or 0,
        r["n"] or 0,
    ))

    header = (
        r"\textbf{Source} & \textbf{Entity} & \textbf{Profile} & "
        r"\textbf{$N$} & \textbf{$m$} & \textbf{Status} & "
        r"\textbf{Runtime (s)} & \textbf{Log.\ qubits} & \textbf{$T$-depth} \\"
    )
    caption_short = "Phase 8d HHL/QAE single-circuit scaling"
    caption_long = (
        r"Phase~8d HHL/QAE fixed-precision single-circuit scaling at "
        r"$\varepsilon=10^{-4}$. Source $=$ scout "
        r"(\path{phase08d_qae_hhl_scout}) or tail "
        r"(\path{phase08d_hhl_tail_exploratory}). Status $=$ ok or "
        r"\textit{fail} (estimator engine failure under the run-environment "
        r"configuration). Every Phase~8d OK record is in Regime~2 of the "
        r"chapter's $T$-cost split (full-circuit logical $T$-count $>0$ by "
        r"construction). Phase~8d is appendix-only and not pooled into "
        r"H1--H4."
    )
    label = "tab:app-phase4-phase8d-scaling"
    lines: list[str] = []
    lines.append(r"\begin{longtable}{@{}lllrrlrrr@{}}")
    lines.append(rf"\caption[{caption_short}]{{{caption_long}}}\label{{{label}}} \\")
    lines.append(r"\toprule")
    lines.append(header)
    lines.append(r"\midrule")
    lines.append(r"\endfirsthead")
    lines.append(rf"\caption[]{{{caption_short} (continued).}} \\")
    lines.append(r"\toprule")
    lines.append(header)
    lines.append(r"\midrule")
    lines.append(r"\endhead")
    lines.append(r"\midrule \multicolumn{9}{r}{\textit{(continued on next page)}} \\")
    lines.append(r"\endfoot")
    lines.append(r"\bottomrule")
    lines.append(r"\endlastfoot")

    prev_entity = None
    for r in rows:
        if prev_entity is not None and r["entity"] != prev_entity:
            lines.append(r"\midrule")
        status = r["status"] or "?"
        if status == "engine_failure":
            status_disp = r"\textit{fail}"
        elif status == "ok":
            status_disp = "ok"
        else:
            status_disp = status
        ent = ENTITY_DISPLAY.get(r["entity"], r["entity"] or "?")
        prof = PROFILE_DISPLAY.get(r["profile"], r["profile"] or "?")
        lines.append(
            f"{r['source']} & {ent} & {prof} & {r['n']} & {r['m']} & "
            f"{status_disp} & {_fmt_runtime(r['runtime_s'])} & "
            f"{_fmt_int(r['log_q'])} & {_fmt_int(r['tdepth'])} \\\\"
        )
        prev_entity = r["entity"]

    lines.append(r"\end{longtable}")

    out = ART / "table_phase8d_scaling.tex"
    out.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    print(f"wrote {out.relative_to(ROOT)} ({len(rows)} rows)")


if __name__ == "__main__":
    main()
