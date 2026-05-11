"""Export the P3 quantum_advantage triangulation matrix as a P4-ready shortlist.

Joins the frozen triangulation matrix (1185 rows) with the underlying
extraction metadata (paper title / authors / algorithm / resources) and
emits a P4 consumable JSON with:

  - tier_1: the single strongest-evidence rows (unanimous_viable or
            majority_viable with layers_scored >= 3)
  - tier_2: majority_viable rows with partial coverage (layers_scored == 2)
  - tier_3: split rows flagged for manual review (these are the genuinely
            interesting disagreements from disagreement_cases.json)

Running:
    python -m p4_experiments.core.build_p4_shortlist
"""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path

_THIS_FILE = Path(__file__).resolve()
_REPO_ROOT = _THIS_FILE.parents[2]

TRIANGULATION_MATRIX = (
    _REPO_ROOT
    / "p3_thematic_synthesis"
    / "s3_quantum_advantage"
    / "combined"
    / "output"
    / "triangulation_matrix.json"
)
DISAGREEMENT_CASES = (
    _REPO_ROOT
    / "p3_thematic_synthesis"
    / "s3_quantum_advantage"
    / "combined"
    / "output"
    / "disagreement_cases.json"
)
EXTRACTIONS_DIR = (
    _REPO_ROOT
    / "p3_thematic_synthesis"
    / "s2_quantitative"
    / "output"
    / "extractions"
)
DERIVED_FIELDS = (
    _REPO_ROOT
    / "p3_thematic_synthesis"
    / "s3_quantum_advantage"
    / "derived_fields"
    / "enriched"
    / "derived_fields.json"
)

OUTPUT_DIR = _THIS_FILE.parent
SHORTLIST_OUT = OUTPUT_DIR / "p4_shortlist.json"
SUMMARY_OUT = OUTPUT_DIR / "p4_shortlist_summary.md"


# ---------------------------------------------------------------------------
# Loaders
# ---------------------------------------------------------------------------

def _load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _load_extractions() -> dict[str, dict]:
    """Return {paper_id: extraction_dict}."""
    out: dict[str, dict] = {}
    for f in sorted(EXTRACTIONS_DIR.glob("*.json")):
        data = _load_json(f)
        pid = data.get("paper_id", f.stem)
        out[pid] = data
    return out


def _load_derived_by_key() -> dict[str, dict]:
    data = _load_json(DERIVED_FIELDS)
    by_key: dict[str, dict] = {}
    for e in data.get("enriched_experiments", []):
        key = f"{e['paper_id']}|{e['experiment_id']}"
        by_key[key] = e
    return by_key


# ---------------------------------------------------------------------------
# Row enrichment
# ---------------------------------------------------------------------------

def _find_experiment(
    extraction: dict, experiment_id: str
) -> dict | None:
    """Handle __dup suffixes: strip and pick the Nth match."""
    base_id = experiment_id
    dup_idx = 0
    if "__dup" in experiment_id:
        base_id, dup_suffix = experiment_id.split("__dup", 1)
        try:
            dup_idx = int(dup_suffix)
        except ValueError:
            dup_idx = 0
    matches = [
        e for e in (extraction.get("experiments") or [])
        if e.get("experiment_id") == base_id
    ]
    if not matches:
        return None
    return matches[min(dup_idx, len(matches) - 1)]


def _enrich_row(
    row: dict,
    extractions: dict[str, dict],
    derived_by_key: dict[str, dict],
) -> dict:
    """Add paper-level and experiment-level context to a triangulation row."""
    pid = row["paper_id"]
    extraction = extractions.get(pid) or {}
    experiment = _find_experiment(extraction, row["experiment_id"]) or {}
    derived = derived_by_key.get(f"{pid}|{row['experiment_id']}") or {}

    paper_meta = extraction.get("paper_metadata") or {}
    algo = experiment.get("algorithm") or {}
    qr = experiment.get("quantum_resources") or {}
    impl = experiment.get("implementation_details") or {}
    hw = experiment.get("hardware") or {}
    adv = experiment.get("advantage_assessment") or {}
    claims = experiment.get("speedup_claims") or []

    return {
        # --- identifiers ---
        "paper_id": pid,
        "experiment_id": row["experiment_id"],
        "silo": row["silo"],
        "algorithm_family": row["algorithm_family"],

        # --- paper metadata ---
        "paper_title": paper_meta.get("title"),
        "paper_authors": paper_meta.get("authors"),
        "paper_year": paper_meta.get("year"),
        "paper_doi": paper_meta.get("doi"),
        "paper_arxiv_id": paper_meta.get("arxiv_id"),

        # --- experiment description ---
        "description": experiment.get("description"),
        "algorithm_name": algo.get("name"),
        "algorithm_variant": algo.get("variant"),

        # --- quantum resources (what P4 needs to replicate) ---
        "num_qubits": qr.get("num_qubits"),
        "circuit_depth": qr.get("circuit_depth"),
        "t_count": qr.get("t_count"),
        "t_depth": qr.get("t_depth"),
        "gate_count_total": qr.get("gate_count_total"),
        "two_qubit_gate_count": qr.get("two_qubit_gate_count"),

        # --- implementation ---
        "hardware_type": hw.get("type"),
        "device_name": hw.get("device_name") or impl.get("hardware_name"),
        "num_shots": qr.get("num_shots") or impl.get("num_shots"),
        "num_layers": impl.get("num_layers") or algo.get("num_layers"),

        # --- claims ---
        "advantage_claim": adv.get("advantage_status"),
        "speedup_type": (claims[0].get("type") if claims else None),
        "speedup_factor": (claims[0].get("factor") if claims else None),

        # --- QA triangulation verdicts ---
        "L1_benchmark_validity": row["L1_benchmark_validity"],
        "L2_practicality_crossover": row["L2_practicality_crossover"],
        "L3_fullstack_resource": row["L3_fullstack_resource"],
        "L4_finance_domain_realism": row["L4_finance_domain_realism"],
        "L4_finance_source": row["L4_finance_source"],
        "L5_nisq_veto": row["L5_nisq_veto"],
        "L5_veto_applied": row["L5_veto_applied"],
        "consensus_verdict": row["consensus_verdict"],
        "pre_veto_consensus": row["pre_veto_consensus"],
        "layers_scored": row["layers_scored"],
        "layers_total": row["layers_total"],
        "disagreement_score": row["disagreement_score"],

        # --- derived complexity (optional) ---
        "derived_speedup_order": (
            (derived.get("complexity_derived") or {}).get("speedup_order")
        ),
        "derived_oracle_M": (
            (derived.get("resources_derived") or {}).get("oracle_complexity_M")
        ),

        # --- replication-readiness flags ---
        "has_circuit_params": bool(qr.get("num_qubits") and (qr.get("circuit_depth") or qr.get("num_layers") or algo.get("num_layers"))),
        "has_resource_estimate": bool(qr.get("t_count") or qr.get("t_depth")),
        "is_real_qpu": str(hw.get("type", "")).startswith("real_qpu") or hw.get("type") == "quantum_annealer",
    }


# ---------------------------------------------------------------------------
# Tiered selection
# ---------------------------------------------------------------------------

def _classify_tier(row: dict) -> str | None:
    """Assign a P4 tier to an enriched row, or return None to exclude."""
    consensus = row["consensus_verdict"]
    scored = row["layers_scored"]

    # Tier 1: strongest positive evidence
    if consensus == "unanimous_viable":
        return "tier_1_unanimous_viable"
    if consensus == "majority_viable" and scored >= 3:
        return "tier_1_majority_viable_full_coverage"

    # Tier 2: majority viable with partial coverage, or low-coverage viable
    if consensus == "majority_viable":
        return "tier_2_majority_viable_partial_coverage"
    if consensus == "low_coverage_viable":
        return "tier_2_low_coverage_viable"

    # Tier 3: interesting disagreements (split with high disagreement_score)
    if consensus == "split" and row["disagreement_score"] >= 0.15:
        return "tier_3_high_disagreement"

    return None


# ---------------------------------------------------------------------------
# Build & write
# ---------------------------------------------------------------------------

def build_shortlist() -> dict:
    matrix = _load_json(TRIANGULATION_MATRIX)
    extractions = _load_extractions()
    derived_by_key = _load_derived_by_key()

    enriched_by_tier: dict[str, list[dict]] = defaultdict(list)

    for row in matrix:
        tier = _classify_tier(row)
        if tier is None:
            continue
        enriched = _enrich_row(row, extractions, derived_by_key)
        enriched["p4_tier"] = tier
        enriched_by_tier[tier].append(enriched)

    # Sort within each tier: real-QPU first, then replication-ready, then
    # descending disagreement score for tier 3.
    def _sort_key(r: dict) -> tuple:
        return (
            0 if r["is_real_qpu"] else 1,
            0 if r["has_circuit_params"] else 1,
            0 if r["has_resource_estimate"] else 1,
            -(r["disagreement_score"] or 0),
        )

    for tier, rows in enriched_by_tier.items():
        rows.sort(key=_sort_key)

    shortlist = {
        "_source": {
            "triangulation_matrix": str(TRIANGULATION_MATRIX.relative_to(_REPO_ROOT)),
            "triangulation_rows": len(matrix),
            "extractions_dir": str(EXTRACTIONS_DIR.relative_to(_REPO_ROOT)),
            "extraction_count": len(extractions),
        },
        "_tier_counts": {
            tier: len(rows) for tier, rows in sorted(enriched_by_tier.items())
        },
        "tiers": {
            tier: rows for tier, rows in sorted(enriched_by_tier.items())
        },
    }
    return shortlist


def write_summary(shortlist: dict) -> None:
    tier_counts = shortlist["_tier_counts"]
    lines: list[str] = []
    lines.append("# P4 Shortlist Summary\n")
    lines.append(
        f"Generated from the frozen P3 triangulation matrix "
        f"({shortlist['_source']['triangulation_rows']} rows).\n"
    )
    lines.append("## Tier counts\n")
    lines.append("| Tier | Count |")
    lines.append("|------|------:|")
    for tier, n in tier_counts.items():
        lines.append(f"| `{tier}` | {n} |")
    total = sum(tier_counts.values())
    lines.append(f"| **Total** | **{total}** |\n")

    # Breakdown by silo and algorithm family per tier
    lines.append("## By silo\n")
    lines.append("| Silo | " + " | ".join(tier_counts.keys()) + " | Total |")
    lines.append("|---|" + "|".join(["---:"] * (len(tier_counts) + 1)) + "|")
    silos = sorted({
        r["silo"] for rows in shortlist["tiers"].values() for r in rows
    })
    for silo in silos:
        row = [silo]
        tot = 0
        for tier in tier_counts.keys():
            n = sum(1 for r in shortlist["tiers"].get(tier, []) if r["silo"] == silo)
            row.append(str(n))
            tot += n
        row.append(f"**{tot}**")
        lines.append("| " + " | ".join(row) + " |")
    lines.append("")

    lines.append("## By algorithm family\n")
    lines.append("| Algorithm | " + " | ".join(tier_counts.keys()) + " | Total |")
    lines.append("|---|" + "|".join(["---:"] * (len(tier_counts) + 1)) + "|")
    algos = sorted({
        r["algorithm_family"] for rows in shortlist["tiers"].values() for r in rows
    })
    for algo in algos:
        row = [algo or "(none)"]
        tot = 0
        for tier in tier_counts.keys():
            n = sum(
                1 for r in shortlist["tiers"].get(tier, [])
                if r["algorithm_family"] == algo
            )
            row.append(str(n))
            tot += n
        row.append(f"**{tot}**")
        lines.append("| " + " | ".join(row) + " |")
    lines.append("")

    # Replication-readiness
    lines.append("## Replication readiness\n")
    all_rows = [r for rows in shortlist["tiers"].values() for r in rows]
    n_total = len(all_rows)
    n_qpu = sum(1 for r in all_rows if r["is_real_qpu"])
    n_params = sum(1 for r in all_rows if r["has_circuit_params"])
    n_res = sum(1 for r in all_rows if r["has_resource_estimate"])
    lines.append(f"- Real-QPU experiments: **{n_qpu}/{n_total}**")
    lines.append(f"- With circuit parameters (qubits + depth/layers): **{n_params}/{n_total}**")
    lines.append(f"- With fault-tolerant resource estimate (T-count/T-depth): **{n_res}/{n_total}**\n")

    lines.append("## Suggested P4 approach\n")
    lines.append(
        "1. **Tier 1** (`tier_1_*`): attempt independent replication via Qiskit simulation "
        "and Azure Quantum Resource Estimator. These are the strongest-evidence rows.\n"
        "2. **Tier 2** (`tier_2_*`): resource-estimate only, no full replication; report "
        "hardware requirements under Beverland scenarios.\n"
        "3. **Tier 3** (`tier_3_high_disagreement`): qualitative case studies — why do "
        "frameworks disagree on these specific experiments?\n"
    )

    SUMMARY_OUT.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    shortlist = build_shortlist()
    SHORTLIST_OUT.write_text(
        json.dumps(shortlist, indent=2, ensure_ascii=False, default=str),
        encoding="utf-8",
    )
    write_summary(shortlist)

    total = sum(shortlist["_tier_counts"].values())
    print(f"\nP4 shortlist written to: {SHORTLIST_OUT.relative_to(_REPO_ROOT)}")
    print(f"  Total shortlisted experiments: {total}")
    for tier, n in shortlist["_tier_counts"].items():
        print(f"  {tier}: {n}")
    print(f"\nMarkdown summary: {SUMMARY_OUT.relative_to(_REPO_ROOT)}")


if __name__ == "__main__":
    main()
