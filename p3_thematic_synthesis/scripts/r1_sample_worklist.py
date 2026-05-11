"""R1 propagation-prioritised stratified sampler — 10% per-silo worklist.

Closes GL10_AUDIT.md G-02 step 1 (propagation-prioritised redesign).

Per silo:
  1. Eligible pool E = papers in the silo roster whose propagation_count >= 1,
     where propagation_count counts memberships across that silo's B1 DTs
     and B2 (DTs + ATs) — papers that actually feed at least one theme.
  2. Stratify E into three tiers by L3 severity_max:
        Tier A: any L3 problem with severity == "major"
        Tier B: any L3 problem (none major) with severity == "minor"
        Tier C: L3 record exists with no problems, OR no L3 record at all
  3. Walk A -> B -> C and draw the silo's target N. Within each tier sort by
     (propagation_count desc, paper_id asc) for determinism.
  4. If |E| < N, top up the shortfall from propagation_count == 0 papers
     (also tier-ordered, then propagation desc, paper_id asc); record the
     top-up count in the worklist metadata.

Targets are preserved at the existing per-silo numbers:
  CL=7, DP=15, FD=11, PO=25, QML=31, RM=17, SMC=22, TE=5  (total 133)

After the per-silo draws, a corpus-wide top-up pass adds every major-flagged
paper with corpus_propagation_count >= HIGH_PROP_THRESHOLD that is not already
in any silo's worklist. Each top-up paper is assigned to the silo where its
per-silo propagation_count is highest (paper_id-asc tiebreak). These rows carry
sampling_tier == "topup_high_prop" and are appended to that silo's worklist
without displacing the per-silo draws.

Inputs (per silo):
  p3_thematic_synthesis/s4_thematic_coding/{silo}/reviewed/_disposition.json
    -> "papers_in_silo": authoritative roster (post-projection per silo).
  p3_thematic_synthesis/s4_thematic_coding/{silo}/themes/b1_batch_*.json
  p3_thematic_synthesis/s4_thematic_coding/{silo}/themes/b2_silo_themes.json
    -> theme membership for propagation_count.
  p3_thematic_synthesis/s4_thematic_coding/papers/{paper_id}_l3.json
    -> L3 problems[].severity for tier assignment.

Output (per silo):
  p3_thematic_synthesis/s4_thematic_coding/{silo}/reviewed/r1_review_worklist.jsonl
    one JSON object per line:
      {paper_id, silo, has_l3, l3_problem_count, l3_severity_max,
       propagation_count, sampling_tier in {"A","B","C","topup"},
       status: "pending"}

Determinism: no RNG. The walk is tier-ordered, then sorted within tier by
(propagation_count desc, paper_id asc). Idempotent: overwrites the worklist;
rows preserve sampling-walk order so the diff is stable.

Existing r1_review.jsonl files are empty across all 8 silos — no verdict
migration is needed.
"""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
S4 = REPO / "p3_thematic_synthesis" / "s4_thematic_coding"
PAPERS_DIR = S4 / "papers"

# Per-silo R1 targets — preserved from the prior 10% (floor=5) sampler.
TARGETS = {
    "credit_lending": 7,
    "derivative_pricing": 15,
    "fraud_detection": 11,
    "portfolio_optimization": 25,
    "quantum_ml_finance": 31,
    "risk_management": 17,
    "simulation_monte_carlo": 22,
    "trading_execution": 5,
}
SILOS = list(TARGETS.keys())

# Corpus-wide top-up: every major-flagged paper feeding >= this many themes
# (summed across all silos and across B1+B2) gets a researcher review even if
# the per-silo draws missed it.
HIGH_PROP_THRESHOLD = 10


# ─── Inputs ──────────────────────────────────────────────────────────

def load_roster(silo: str) -> list[str]:
    disp = json.loads((S4 / silo / "reviewed" / "_disposition.json").read_text(encoding="utf-8"))
    return sorted(disp["papers_in_silo"])


def load_propagation_counts(silo: str) -> Counter:
    """Count {paper_id -> #themes that include it} across B1 (DTs) + B2 (DTs+ATs)."""
    counts: Counter = Counter()
    themes_dir = S4 / silo / "themes"

    for b1 in sorted(themes_dir.glob("b1_batch_*.json")):
        data = json.loads(b1.read_text(encoding="utf-8"))
        for t in data.get("themes", []) or []:
            for pid in t.get("supporting_papers", []) or []:
                counts[pid] += 1

    b2_path = themes_dir / "b2_silo_themes.json"
    if b2_path.is_file():
        data = json.loads(b2_path.read_text(encoding="utf-8"))
        out = data.get("output", {}) or {}
        for t in (out.get("descriptive_themes", []) or []):
            for pid in t.get("supporting_papers", []) or []:
                counts[pid] += 1
        for t in (out.get("analytical_themes", []) or []):
            for pid in t.get("supporting_papers", []) or []:
                counts[pid] += 1

    return counts


def load_l3(paper_id: str) -> dict:
    """Return {has_l3, problem_count, severity_max in {'major','minor','none'}}."""
    p = PAPERS_DIR / f"{paper_id}_l3.json"
    if not p.exists():
        return {"has_l3": False, "problem_count": 0, "severity_max": "none"}
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return {"has_l3": True, "problem_count": 0, "severity_max": "none"}

    problems = data.get("problems", []) or []
    severities = {(pr.get("severity") or "").lower() for pr in problems}
    if "major" in severities:
        sev = "major"
    elif "minor" in severities:
        sev = "minor"
    else:
        sev = "none"
    return {
        "has_l3": True,
        "problem_count": int(data.get("problem_count", len(problems)) or 0),
        "severity_max": sev,
    }


# ─── Per-silo sampler ────────────────────────────────────────────────

def sample_silo(silo: str) -> dict:
    roster = load_roster(silo)
    target = min(TARGETS[silo], len(roster))
    propagation = load_propagation_counts(silo)

    rows_by_pid: dict[str, dict] = {}
    for pid in roster:
        l3 = load_l3(pid)
        rows_by_pid[pid] = {
            "paper_id": pid,
            "silo": silo,
            "has_l3": l3["has_l3"],
            "l3_problem_count": l3["problem_count"],
            "l3_severity_max": l3["severity_max"],
            "propagation_count": int(propagation.get(pid, 0)),
        }

    eligible = [r for r in rows_by_pid.values() if r["propagation_count"] >= 1]
    non_propagating = [r for r in rows_by_pid.values() if r["propagation_count"] == 0]

    def _sort_key(r: dict) -> tuple:
        return (-r["propagation_count"], r["paper_id"])

    tier_a = sorted([r for r in eligible if r["l3_severity_max"] == "major"], key=_sort_key)
    tier_b = sorted([r for r in eligible if r["l3_severity_max"] == "minor"], key=_sort_key)
    tier_c = sorted([r for r in eligible if r["l3_severity_max"] == "none"],  key=_sort_key)

    selected: list[dict] = []
    for tier_label, tier in (("A", tier_a), ("B", tier_b), ("C", tier_c)):
        if len(selected) >= target:
            break
        room = target - len(selected)
        for r in tier[:room]:
            sel = dict(r)
            sel["sampling_tier"] = tier_label
            sel["status"] = "pending"
            selected.append(sel)

    shortfall = target - len(selected)
    topup_pool = sorted(non_propagating, key=_sort_key) if shortfall > 0 else []
    for r in topup_pool[:shortfall]:
        sel = dict(r)
        sel["sampling_tier"] = "topup"
        sel["status"] = "pending"
        selected.append(sel)

    tier_counts = Counter(r["sampling_tier"] for r in selected)
    return {
        "silo": silo,
        "roster_size": len(roster),
        "target": target,
        "selected_rows": selected,
        "rows_by_pid": rows_by_pid,
        "propagation": propagation,
        "eligible_pool": len(eligible),
        "non_propagating": len(non_propagating),
        "tier_available": {"A": len(tier_a), "B": len(tier_b), "C": len(tier_c)},
        "tier_selected": {
            "A": tier_counts.get("A", 0),
            "B": tier_counts.get("B", 0),
            "C": tier_counts.get("C", 0),
            "topup": tier_counts.get("topup", 0),
        },
        "shortfall_topup": tier_counts.get("topup", 0),
    }


def write_worklist(silo: str, rows: list[dict]) -> Path:
    out = S4 / silo / "reviewed" / "r1_review_worklist.jsonl"
    with out.open("w", encoding="utf-8", newline="\n") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    return out


def build_corpus_propagation(per_silo_props: dict[str, Counter]) -> tuple[Counter, dict[str, str]]:
    """Aggregate corpus-wide propagation counts across all silos.
    Returns (corpus_count, primary_silo_for_paper) where primary_silo is the
    silo with the highest per-silo prop count (paper_id ascending tiebreak)."""
    corpus = Counter()
    silo_count: dict[str, dict[str, int]] = {}  # pid -> {silo: count}
    for silo, c in per_silo_props.items():
        for pid, n in c.items():
            corpus[pid] += n
            silo_count.setdefault(pid, {})[silo] = n
    primary: dict[str, str] = {}
    for pid, sc in silo_count.items():
        # Highest per-silo count, silo name ascending tiebreak.
        primary[pid] = sorted(sc.items(), key=lambda kv: (-kv[1], kv[0]))[0][0]
    return corpus, primary


# ─── Driver ──────────────────────────────────────────────────────────

def main() -> None:
    print("R1 propagation-prioritised stratified sampler")
    print(f"{'silo':<25} {'roster':>6} {'tgt':>4} "
          f"{'pool':>5} {'A_av':>5} {'B_av':>5} {'C_av':>5} | "
          f"{'A':>3} {'B':>3} {'C':>3} {'top':>4}  {'+hi':>4}")

    # Pass 1: per-silo Tier-A->B->C draws (no writes yet).
    silo_state = {s: sample_silo(s) for s in SILOS}

    # Pass 2: corpus-wide high-propagation top-up.
    per_silo_props = {s: silo_state[s]["propagation"] for s in SILOS}
    corpus_prop, primary_silo = build_corpus_propagation(per_silo_props)

    in_worklist: set[str] = set()
    for s in SILOS:
        for r in silo_state[s]["selected_rows"]:
            in_worklist.add(r["paper_id"])

    # Candidates: major-flagged AND corpus_prop >= threshold AND not in any worklist.
    high_prop_topups: list[dict] = []
    for pid, n in corpus_prop.items():
        if n < HIGH_PROP_THRESHOLD:
            continue
        if pid in in_worklist:
            continue
        l3 = load_l3(pid)
        if l3["severity_max"] != "major":
            continue
        silo = primary_silo[pid]
        per_silo_n = per_silo_props[silo].get(pid, 0)
        high_prop_topups.append({
            "paper_id": pid,
            "silo": silo,
            "has_l3": l3["has_l3"],
            "l3_problem_count": l3["problem_count"],
            "l3_severity_max": l3["severity_max"],
            "propagation_count": per_silo_n,
            "corpus_propagation_count": int(n),
            "sampling_tier": "topup_high_prop",
            "status": "pending",
        })
    # Deterministic order: by corpus_prop desc, paper_id asc.
    high_prop_topups.sort(key=lambda r: (-r["corpus_propagation_count"], r["paper_id"]))

    # Append top-ups to their primary silo's selection.
    topups_per_silo: dict[str, int] = {s: 0 for s in SILOS}
    for r in high_prop_topups:
        silo_state[r["silo"]]["selected_rows"].append(r)
        topups_per_silo[r["silo"]] += 1

    # Pass 3: write worklists + print summary.
    total_target = total_sampled = total_pool = total_topup = 0
    for s in SILOS:
        st = silo_state[s]
        out_path = write_worklist(s, st["selected_rows"])
        ta = st["tier_available"]; ts = st["tier_selected"]
        n_hi = topups_per_silo[s]
        n_total = len(st["selected_rows"])
        print(
            f"{s:<25} {st['roster_size']:>6} {st['target']:>4} "
            f"{st['eligible_pool']:>5} {ta['A']:>5} {ta['B']:>5} {ta['C']:>5} | "
            f"{ts['A']:>3} {ts['B']:>3} {ts['C']:>3} {ts['topup']:>4} "
            f"{n_hi:>4}  -> {n_total} rows  {out_path.relative_to(REPO)}"
        )
        total_target += st["target"]
        total_sampled += n_total
        total_pool += st["eligible_pool"]
        total_topup += st["shortfall_topup"]

    corpus_propagating = {pid for pid, n in corpus_prop.items() if n >= 1}
    print()
    print(f"Per-silo target sum (10% floor=5):              {total_target}")
    print(f"Per-silo selected (incl. high-prop top-ups):    {total_sampled}")
    print(f"Eligible pools (summed across silos):           {total_pool}")
    print(f"Shortfall top-ups (propagation_count == 0):     {total_topup}")
    print(f"High-prop top-ups (corpus_prop >= {HIGH_PROP_THRESHOLD}, major):     {len(high_prop_topups)}")
    print(f"Corpus papers propagating to >=1 theme:         {len(corpus_propagating)}")
    print(f"Sample fraction of propagating subset:          "
          f"{100 * total_sampled / max(1, len(corpus_propagating)):.1f}% "
          f"({total_sampled}/{len(corpus_propagating)})")


if __name__ == "__main__":
    main()
