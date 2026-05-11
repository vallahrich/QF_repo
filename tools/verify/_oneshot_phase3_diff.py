"""One-shot diff for the Phase-3 triangulate rerun (2026-05-02)."""
from __future__ import annotations
import json
import pathlib
from collections import Counter

ROOT = pathlib.Path("p3_thematic_synthesis/s3_quantum_advantage/combined/output")
SNAP = ROOT / "_pre_remediation_snapshot_2026-05-02"

pre = json.loads((SNAP / "triangulation_matrix.json").read_text(encoding="utf-8"))
post = json.loads((ROOT / "triangulation_matrix.json").read_text(encoding="utf-8"))

def idx(m):
    return {(r["paper_id"], r["experiment_id"]): r for r in m}

P, Q = idx(pre), idx(post)

print(f"pre rows:  {len(P)}")
print(f"post rows: {len(Q)}")
print(f"common:    {len(set(P) & set(Q))}")
print(f"pre-only:  {len(set(P) - set(Q))}")
print(f"post-only: {len(set(Q) - set(P))}")

print("\nCONSENSUS DISTRIBUTION SHIFT:")
pre_c = Counter(r["consensus_verdict"] for r in pre)
post_c = Counter(r["consensus_verdict"] for r in post)
labels = sorted(set(list(pre_c) + list(post_c)))
for L in labels:
    p, q = pre_c.get(L, 0), post_c.get(L, 0)
    print(f"  {L:25s}  pre={p:5d}  post={q:5d}  delta={q-p:+5d}")

print("\nPER-SILO viable+ delta:")
def viable_count(rows):
    return Counter(r["silo"] for r in rows
                   if r["consensus_verdict"] in
                      ("unanimous_viable", "low_coverage_viable", "majority_viable"))

pv, qv = viable_count(pre), viable_count(post)
for s in sorted(set(list(pv) + list(qv))):
    p, q = pv.get(s, 0), qv.get(s, 0)
    if p != q:
        print(f"  {s:35s}  pre={p:4d}  post={q:4d}  delta={q-p:+4d}")

changed = sum(
    1 for k in set(P) & set(Q)
    if P[k]["consensus_verdict"] != Q[k]["consensus_verdict"]
)
print(f"\nRows with changed consensus_verdict: {changed} / {len(set(P) & set(Q))}")

print("\nPD-01 portfolio-optimization (Dalzell gate fix focus):")
po_pre = [r for r in pre if r["silo"] in ("PD-01", "portfolio-optimization")]
po_post = [r for r in post if r["silo"] in ("PD-01", "portfolio-optimization")]
print(f"  pre  rows: {len(po_pre):4d}")
print(f"     consensus: {dict(Counter(r['consensus_verdict'] for r in po_pre))}")
print(f"  post rows: {len(po_post):4d}")
print(f"     consensus: {dict(Counter(r['consensus_verdict'] for r in po_post))}")

print("\nL2_merge_disagreement summary (post only):")
l2 = sum(1 for r in post if r.get("L2_merge_disagreement"))
print(f"  rows where Hoefler != Babbush (both scored): {l2} / {len(post)}")

# Persist diff report
report = {
    "rerun_date_utc": "2026-05-02",
    "pre_snapshot_dir": str(SNAP.relative_to(pathlib.Path('.'))),
    "pre_rows": len(P),
    "post_rows": len(Q),
    "common": len(set(P) & set(Q)),
    "pre_only": len(set(P) - set(Q)),
    "post_only": len(set(Q) - set(P)),
    "consensus_distribution_pre": dict(pre_c),
    "consensus_distribution_post": dict(post_c),
    "consensus_distribution_delta": {
        L: post_c.get(L, 0) - pre_c.get(L, 0) for L in labels
    },
    "per_silo_viable_plus_pre": dict(pv),
    "per_silo_viable_plus_post": dict(qv),
    "rows_with_changed_consensus": changed,
    "l2_merge_disagreement_count_post": l2,
    "drivers": {
        "dalzell_algo_gate_fix":
            "Removed silo-wide is_infeasible force-fail for portfolio-optimization "
            "(QA-5). Only QIPM-family experiments now fail; others get not_applicable.",
        "ronnow_family_gate":
            "Restricted Rønnow scope to {qaoa, grover, AE/AA, annealing} or explicit "
            "benchmark_validity_study=true (QA-1). Increased not_applicable from L1.",
        "beverland_relabel":
            "Renamed framework ID to 'beverland_inspired_2022' (QA-11). No verdict "
            "changes from this rename alone.",
        "l2_merge_disagreement_added":
            "New boolean column surfaces hidden Hoefler/Babbush disagreement; does "
            "not change verdicts.",
    },
}
out = ROOT / "_remediation_diff_2026-05-02.json"
out.write_text(json.dumps(report, indent=2), encoding="utf-8")
print(f"\nReport written: {out}")
