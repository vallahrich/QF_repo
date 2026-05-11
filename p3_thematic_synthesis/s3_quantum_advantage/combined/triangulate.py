"""Triangulation layer: 4-core + 1 optional-veto layered consensus.

Layer design
============
1. Benchmark validity      — Rønnow 2014
2. Practicality / crossover — Hoefler 2023 + Babbush 2021 (merged, single score)
3. Full-stack resource      — Beverland 2022
4. Finance-domain realism   — Chakrabarti 2021 (pricing/risk/MC) OR Dalzell 2023 (optimization)
5. Optional NISQ veto       — Stilck França 2021 (only for variational/NISQ; caps but cannot upgrade)

Reads results/*.json from every active framework assessor, merges them into
the 4-core layers, and produces:
  - triangulation_matrix.json:  one row per experiment, one column per layer + consensus
  - consensus_summary.json:     by-silo and by-algorithm rollups
  - disagreement_cases.json:    top-N experiments where layers conflict

Usage:
    python -m p3_thematic_synthesis.s3_quantum_advantage.combined.triangulate
"""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path

_MODULE_ROOT = Path(__file__).resolve().parent
_QA_ROOT = _MODULE_ROOT.parent
OUTPUT_DIR = _MODULE_ROOT / "output"

# ---------------------------------------------------------------------------
# Active assessor framework IDs (emit results/*.json independently)
# ---------------------------------------------------------------------------
ACTIVE_FRAMEWORKS = [
    "ronnow_2014",
    "hoefler_2023",
    "babbush_2021",
    "beverland_inspired_2022",  # honest relabel 2026-05-02 (was "beverland_2022")
    "chakrabarti_2021",
    "dalzell_2023",
    "stilck_franca_2021",
]

# ---------------------------------------------------------------------------
# Layer definitions
# ---------------------------------------------------------------------------
CORE_LAYERS = [
    "benchmark_validity",       # Rønnow
    "practicality_crossover",   # Hoefler + Babbush merged
    "fullstack_resource",       # Beverland
    "finance_domain_realism",   # Chakrabarti OR Dalzell
]
OPTIONAL_VETO_LAYER = "nisq_veto"  # Stilck França

# Silos where Chakrabarti applies (pricing/risk/MC/insurance)
_CHAKRABARTI_SILOS = {
    "derivative-pricing", "risk-management",
    "simulation-monte-carlo", "insurance-actuarial",
    # PD-code aliases
    "PD-02", "PD-03", "PD-09", "PD-10",
}
# Silos where Dalzell applies (portfolio/optimization)
_DALZELL_SILOS = {
    "portfolio-optimization", "trading-execution",
    "credit-lending", "quantum-ml-finance",
    "PD-01", "PD-06", "PD-07", "PD-04",
}

_VERDICT_SCORE = {
    "viable": 4,
    "likely_viable": 3,
    "potentially_viable": 2,
    "conditional": 1,
    "fails": 0,
    "not_applicable": None,  # excluded from consensus
    "insufficient_data": None,
}


# ---------------------------------------------------------------------------
# Discovery & loading
# ---------------------------------------------------------------------------

def _find_result_files() -> dict[str, Path]:
    """Discover all results/*.json files across framework folders."""
    found = {}
    for subdir in _QA_ROOT.iterdir():
        if not subdir.is_dir():
            continue
        results_dir = subdir / "results"
        if results_dir.is_dir():
            for f in results_dir.glob("*_results.json"):
                data = json.loads(f.read_text(encoding="utf-8"))
                fw = data.get("framework")
                if fw and fw in ACTIVE_FRAMEWORKS:
                    found[fw] = f
    return found


def _load_all_verdicts(result_files: dict[str, Path]) -> dict[str, dict[str, dict]]:
    """Return {framework: {(paper_id|exp_id): verdict_record}}."""
    all_verdicts: dict[str, dict[str, dict]] = {}
    for fw, path in result_files.items():
        data = json.loads(path.read_text(encoding="utf-8"))
        by_key: dict[str, dict] = {}
        for exp in data.get("experiments", []):
            key = f"{exp['paper_id']}|{exp['experiment_id']}"
            by_key[key] = exp
        all_verdicts[fw] = by_key
    return all_verdicts


# ---------------------------------------------------------------------------
# Layer merging
# ---------------------------------------------------------------------------

def _merge_practicality(hoefler_v: str | None, babbush_v: str | None) -> str:
    """Merge Hoefler + Babbush into one practicality_crossover verdict.

    Rule: take the more pessimistic scored verdict (min score).
    This avoids double-counting the same construct from two angles.
    If one is not_applicable/insufficient_data/missing, use the other.
    """
    def _score(v: str | None) -> int | None:
        if v is None or v == "missing":
            return None
        return _VERDICT_SCORE.get(v)

    sh = _score(hoefler_v)
    sb = _score(babbush_v)

    if sh is None and sb is None:
        return "insufficient_data"
    if sh is None:
        return babbush_v  # type: ignore[return-value]
    if sb is None:
        return hoefler_v  # type: ignore[return-value]

    # Both have scores — take the more pessimistic (lower score)
    if sh <= sb:
        return hoefler_v  # type: ignore[return-value]
    return babbush_v  # type: ignore[return-value]


def _select_finance_domain(
    silo: str,
    chakrabarti_v: str | None,
    dalzell_v: str | None,
) -> tuple[str, str]:
    """Select Chakrabarti OR Dalzell based on silo.

    Returns (verdict, source_framework).
    """
    if silo in _CHAKRABARTI_SILOS:
        if chakrabarti_v and chakrabarti_v not in ("missing",):
            return chakrabarti_v, "chakrabarti_2021"
        # Fallback to Dalzell if Chakrabarti didn't run
        if dalzell_v and dalzell_v not in ("missing",):
            return dalzell_v, "dalzell_2023"
        return "insufficient_data", "none"

    if silo in _DALZELL_SILOS:
        if dalzell_v and dalzell_v not in ("missing",):
            return dalzell_v, "dalzell_2023"
        if chakrabarti_v and chakrabarti_v not in ("missing",):
            return chakrabarti_v, "chakrabarti_2021"
        return "insufficient_data", "none"

    # Silo not in either set — check if either framework returned a real verdict
    for v, fw in [(chakrabarti_v, "chakrabarti_2021"), (dalzell_v, "dalzell_2023")]:
        if v and v not in ("missing", "not_applicable"):
            return v, fw

    return "not_applicable", "none"


# Consensus labels ranked by optimism for veto comparison
_CONSENSUS_RANK = {
    "unanimous_viable": 5,
    "low_coverage_viable": 4,
    "majority_viable": 3,
    "split": 2,
    "majority_fails": 1,
    "low_coverage_fails": 0,
    "unanimous_fails": 0,
    "insufficient_data": None,
}

# Map from Stilck verdict to the consensus cap it can impose
_STILCK_CAP = {
    "fails": "unanimous_fails",
    "conditional": "split",
}


def _apply_nisq_veto(current_consensus: str, stilck_v: str | None) -> tuple[str, bool]:
    """Apply Stilck França as an optional veto on the consensus label.

    Can only downgrade the consensus — never upgrade.
    Returns (final_consensus, was_vetoed).
    """
    if stilck_v is None or stilck_v in ("missing", "not_applicable", "insufficient_data"):
        return current_consensus, False

    cap_consensus = _STILCK_CAP.get(stilck_v)
    if cap_consensus is None:
        # Stilck returned viable/potentially_viable — no cap needed
        return current_consensus, False

    current_rank = _CONSENSUS_RANK.get(current_consensus)
    cap_rank = _CONSENSUS_RANK.get(cap_consensus)

    if current_rank is None or cap_rank is None:
        return current_consensus, False

    if current_rank > cap_rank:
        return cap_consensus, True

    return current_consensus, False


# ---------------------------------------------------------------------------
# Consensus
# ---------------------------------------------------------------------------

def _compute_layer_consensus(
    layer_verdicts: dict[str, str],
) -> tuple[str, float, str, int, int]:
    """Given {layer_name: verdict_string}, return (consensus_label, disagreement, outlier, layers_scored, layers_total).

    Consensus labels:
      unanimous_viable   -- all scored layers agree >= potentially_viable AND >= 3 layers scored
      majority_viable    -- >50% of scored layers say >= potentially_viable
      split              -- no majority either way
      majority_fails     -- >50% of scored layers say fails
      unanimous_fails    -- all scored layers agree: fails AND >= 3 layers scored
      low_coverage_viable -- all scored layers agree >= potentially_viable but < 3 layers scored
      low_coverage_fails  -- all scored layers agree fails but < 3 layers scored
      insufficient_data  -- all layers returned not_applicable or insufficient_data
    """
    total = len(layer_verdicts)
    scored: list[tuple[str, int]] = []
    for layer, v in layer_verdicts.items():
        s = _VERDICT_SCORE.get(v)
        if s is not None:
            scored.append((layer, s))

    n = len(scored)
    if not scored:
        return "insufficient_data", 0.0, "All layers returned not_applicable or insufficient_data", 0, total

    scores = [s for _, s in scored]
    mean_score = sum(scores) / n

    viable_count = sum(1 for s in scores if s >= 2)
    fails_count = sum(1 for s in scores if s == 0)
    all_same = len(set(scores)) == 1

    if all_same:
        if scores[0] >= 2:
            # Only call it "unanimous" if enough layers actually scored
            label = "unanimous_viable" if n >= 3 else "low_coverage_viable"
        elif scores[0] == 0:
            label = "unanimous_fails" if n >= 3 else "low_coverage_fails"
        elif scores[0] == 1:
            label = "split"  # unanimous conditional -> treat as split
        else:
            label = "split"
    elif viable_count > n / 2:
        label = "majority_viable"
    elif fails_count > n / 2:
        label = "majority_fails"
    else:
        label = "split"

    # Disagreement score: normalised variance
    if n <= 1:
        disagreement = 0.0
    else:
        variance = sum((s - mean_score) ** 2 for s in scores) / n
        max_var = 4.0
        disagreement = min(variance / max_var, 1.0)

    # Outlier
    outlier = ""
    if not all_same and n >= 2:
        deviations = [
            (layer, abs(s - mean_score), layer_verdicts[layer])
            for layer, s in scored
        ]
        deviations.sort(key=lambda x: x[1], reverse=True)
        top = deviations[0]
        outlier = f"{top[0]} is outlier (verdict='{top[2]}', distance={top[1]:.1f} from mean={mean_score:.1f})"

    return label, disagreement, outlier, n, total


# ---------------------------------------------------------------------------
# Matrix building
# ---------------------------------------------------------------------------

def build_triangulation_matrix(all_verdicts: dict[str, dict[str, dict]]) -> list[dict]:
    """Build one row per experiment with layer verdicts + consensus."""
    all_keys: set[str] = set()
    for by_key in all_verdicts.values():
        all_keys.update(by_key.keys())

    matrix: list[dict] = []
    for key in sorted(all_keys):
        paper_id, exp_id = key.split("|", 1)

        # Get a reference record for metadata
        ref = None
        for fw in ACTIVE_FRAMEWORKS:
            if key in all_verdicts.get(fw, {}):
                ref = all_verdicts[fw][key]
                break
        if ref is None:
            continue

        silo = ref.get("silo", "")
        algo_family = ref.get("algorithm_family", "")

        # Collect raw framework verdicts
        def _get_v(fw: str) -> str | None:
            rec = all_verdicts.get(fw, {}).get(key)
            return rec["verdict"] if rec else None

        ronnow_v = _get_v("ronnow_2014")
        hoefler_v = _get_v("hoefler_2023")
        babbush_v = _get_v("babbush_2021")
        beverland_v = _get_v("beverland_inspired_2022")
        chakrabarti_v = _get_v("chakrabarti_2021")
        dalzell_v = _get_v("dalzell_2023")
        stilck_v = _get_v("stilck_franca_2021")

        # Build layer verdicts
        practicality_v = _merge_practicality(hoefler_v, babbush_v)
        finance_v, finance_source = _select_finance_domain(silo, chakrabarti_v, dalzell_v)

        layer_verdicts = {
            "benchmark_validity": ronnow_v or "missing",
            "practicality_crossover": practicality_v,
            "fullstack_resource": beverland_v or "missing",
            "finance_domain_realism": finance_v,
        }

        # L2 sub-framework disagreement diagnostic (added 2026-05-02): the
        # practicality_crossover layer hides a min-merge across Hoefler 2023
        # and Babbush 2021. This boolean exposes when the two frameworks
        # disagree (different scored verdicts) so downstream consumers can
        # filter or highlight L2 conflicts. True only when BOTH have a
        # scored verdict and the scores differ; False otherwise (including
        # when one or both are not_applicable / insufficient_data / missing).
        sh_score = _VERDICT_SCORE.get(hoefler_v) if hoefler_v not in (None, "missing") else None
        sb_score = _VERDICT_SCORE.get(babbush_v) if babbush_v not in (None, "missing") else None
        l2_merge_disagreement = (
            sh_score is not None and sb_score is not None and sh_score != sb_score
        )

        # Consensus from core layers
        consensus_label, disagreement_score, outlier, layers_scored, layers_total = (
            _compute_layer_consensus(layer_verdicts)
        )

        # Apply optional NISQ veto
        final_consensus, was_vetoed = _apply_nisq_veto(consensus_label, stilck_v)

        row: dict = {
            "paper_id": paper_id,
            "experiment_id": exp_id,
            "silo": silo,
            "algorithm_family": algo_family,
            # Layer verdicts
            "L1_benchmark_validity": layer_verdicts["benchmark_validity"],
            "L2_practicality_crossover": layer_verdicts["practicality_crossover"],
            "L2_merge_disagreement": l2_merge_disagreement,
            "L3_fullstack_resource": layer_verdicts["fullstack_resource"],
            "L4_finance_domain_realism": layer_verdicts["finance_domain_realism"],
            "L4_finance_source": finance_source,
            "L5_nisq_veto": stilck_v or "not_applicable",
            "L5_veto_applied": was_vetoed,
            # Raw framework verdicts (for audit)
            "raw_ronnow_2014": ronnow_v or "missing",
            "raw_hoefler_2023": hoefler_v or "missing",
            "raw_babbush_2021": babbush_v or "missing",
            "raw_beverland_2022": beverland_v or "missing",
            "raw_chakrabarti_2021": chakrabarti_v or "missing",
            "raw_dalzell_2023": dalzell_v or "missing",
            "raw_stilck_franca_2021": stilck_v or "missing",
            # Consensus
            "consensus_verdict": final_consensus,
            "pre_veto_consensus": consensus_label,
            "layers_scored": layers_scored,
            "layers_total": layers_total,
            "disagreement_score": round(disagreement_score, 4),
            "disagreement_reason": outlier,
        }

        matrix.append(row)

    return matrix


def build_consensus_summary(matrix: list[dict]) -> dict:
    """Roll up consensus by silo and by algorithm."""
    by_silo: dict[str, Counter] = defaultdict(Counter)
    by_algo: dict[str, Counter] = defaultdict(Counter)

    for row in matrix:
        by_silo[row["silo"]][row["consensus_verdict"]] += 1
        by_algo[row["algorithm_family"]][row["consensus_verdict"]] += 1

    veto_count = sum(1 for row in matrix if row.get("L5_veto_applied"))

    # NISQ veto eligibility diagnostic:
    # Of the pre-veto-viable rows with a variational/NISQ algorithm,
    # how many carry enough noise+depth data to cap the veto?
    _NISQ_FAMILIES = {
        "qaoa", "vqe", "quantum-annealing", "quantum_annealing",
        "variational-nisq", "variational_nisq", "variational",
        "qnn", "qgan", "qcbm", "hybrid",
        "quantum-ml", "quantum_ml", "qml",
        "quantum-svm", "quantum_svm", "qsvm",
    }
    veto_eligible_rows = [
        row for row in matrix
        if row.get("algorithm_family") in _NISQ_FAMILIES
        and row.get("pre_veto_consensus") in (
            "unanimous_viable", "low_coverage_viable", "majority_viable"
        )
    ]
    veto_diagnostic_counts = Counter(
        row.get("raw_stilck_franca_2021", "missing")
        for row in veto_eligible_rows
    )

    return {
        "layer_design": "4 core + 1 optional veto",
        "core_layers": CORE_LAYERS,
        "optional_veto": OPTIONAL_VETO_LAYER,
        "by_silo": {
            silo: dict(counts.most_common())
            for silo, counts in sorted(by_silo.items())
        },
        "by_algorithm": {
            algo: dict(counts.most_common())
            for algo, counts in sorted(by_algo.items())
        },
        "total_experiments": len(matrix),
        "consensus_distribution": dict(
            Counter(row["consensus_verdict"] for row in matrix).most_common()
        ),
        "nisq_veto_applied_count": veto_count,
        "nisq_veto_diagnostic": {
            "_note": (
                "Rows where veto COULD fire = variational algorithm family AND "
                "pre-veto consensus is viable-leaning. Counts Stilck verdicts on those rows. "
                "If Stilck is 'not_applicable'/'insufficient_data', the veto cannot fire "
                "even though the row is a natural candidate."
            ),
            "eligible_rows": len(veto_eligible_rows),
            "stilck_verdicts_on_eligible_rows": dict(veto_diagnostic_counts.most_common()),
        },
    }


def build_disagreement_cases(matrix: list[dict], top_n: int = 50) -> list[dict]:
    """Top-N experiments by disagreement score."""
    ranked = sorted(matrix, key=lambda r: r["disagreement_score"], reverse=True)
    return ranked[:top_n]


# ---------------------------------------------------------------------------
# Schema validation
# ---------------------------------------------------------------------------

SCHEMA_PATH = _MODULE_ROOT / "triangulation_row_schema.json"


def validate_matrix(matrix: list[dict]) -> tuple[int, list[tuple[int, str]]]:
    """Validate every row against triangulation_row_schema.json.

    Returns (n_valid, [(row_idx, error_message), ...]).
    """
    try:
        from jsonschema import Draft202012Validator
    except ImportError:
        print("  (jsonschema not available — skipping row validation)")
        return len(matrix), []

    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema)
    errors: list[tuple[int, str]] = []
    n_valid = 0
    for i, row in enumerate(matrix):
        row_errors = sorted(validator.iter_errors(row), key=lambda e: e.path)
        if row_errors:
            first = row_errors[0]
            errors.append((i, f"{list(first.path)}: {first.message}"))
        else:
            n_valid += 1
    return n_valid, errors


def run_triangulation():
    result_files = _find_result_files()
    print(f"Found {len(result_files)} active framework result files:")
    for fw, path in sorted(result_files.items()):
        print(f"  {fw}: {path.name}")

    if not result_files:
        print("ERROR: No framework results found. Run individual assessors first.")
        return

    all_verdicts = _load_all_verdicts(result_files)

    matrix = build_triangulation_matrix(all_verdicts)
    summary = build_consensus_summary(matrix)
    disagreements = build_disagreement_cases(matrix)

    # Validate every row against the schema
    n_valid, validation_errors = validate_matrix(matrix)
    summary["schema_validation"] = {
        "schema": "triangulation_row_v1.0",
        "total_rows": len(matrix),
        "valid_rows": n_valid,
        "invalid_rows": len(validation_errors),
        "errors_sample": [
            {"row_index": i, "error": msg} for i, msg in validation_errors[:10]
        ],
    }

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    matrix_path = OUTPUT_DIR / "triangulation_matrix.json"
    matrix_path.write_text(json.dumps(matrix, indent=2), encoding="utf-8")

    summary_path = OUTPUT_DIR / "consensus_summary.json"
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    disagree_path = OUTPUT_DIR / "disagreement_cases.json"
    disagree_path.write_text(json.dumps(disagreements, indent=2), encoding="utf-8")

    print(f"\n{'='*60}")
    print(f"  TRIANGULATION — 4 core + 1 veto")
    print(f"  {len(matrix)} experiments × {len(result_files)} assessors → {len(CORE_LAYERS)} layers + veto")
    print(f"{'='*60}")
    print(f"\nConsensus distribution:")
    for label, count in summary["consensus_distribution"].items():
        pct = 100 * count / len(matrix) if matrix else 0
        print(f"  {label}: {count} ({pct:.1f}%)")
    print(f"\nNISQ veto applied: {summary['nisq_veto_applied_count']} experiments")
    sv = summary.get("schema_validation", {})
    print(f"Schema validation: {sv.get('valid_rows', '?')}/{sv.get('total_rows', '?')} rows pass")
    if sv.get("invalid_rows"):
        print(f"  FIRST ERRORS:")
        for err in sv.get("errors_sample", [])[:3]:
            print(f"    row {err['row_index']}: {err['error']}")
    print(f"Disagreement cases: {len(disagreements)} (top-50 by score)")
    print(f"\nOutputs:")
    print(f"  {matrix_path}")
    print(f"  {summary_path}")
    print(f"  {disagree_path}")


def main():
    run_triangulation()


if __name__ == "__main__":
    main()
