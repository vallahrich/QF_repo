"""One-shot corpus cleanup for P3 quantitative extractions.

Fixes known data quality issues in the existing 643 extraction files
so they conform to benchmark_schema.json. All changes are logged.

Issues addressed:
  CR-2  paper_metadata.year stored as string → cast to int
  CR-2  complexity_analysis.speedup_order invalid values → map to valid enum
  CR-2  speedup_claims[].type invalid values → map to valid enum
  CR-3  quality_score null → recompute via compute_quality_score()
  MI-5  extraction_metadata missing validation fields → backfill

Usage:
    python -m p3_thematic_synthesis.s2_quantitative.scripts.cleanup_corpus
    python -m p3_thematic_synthesis.s2_quantitative.scripts.cleanup_corpus --dry-run
"""

import argparse
import json
import logging
import sys
from pathlib import Path

_QUANT_ROOT = Path(__file__).resolve().parents[1]
_PROJECT_ROOT = Path(__file__).resolve().parents[3]

_project_root_str = str(_PROJECT_ROOT)
if _project_root_str not in sys.path:
    sys.path.insert(0, _project_root_str)

from p3_thematic_synthesis.s2_quantitative.scripts.validate_benchmarks import (  # noqa: E402
    compute_quality_score,
    normalize_extraction_metrics,
    validate_extraction,
)

OUTPUT_DIR = _QUANT_ROOT / "output" / "extractions"

logging.basicConfig(level=logging.INFO, format="%(levelname)s  %(message)s")
logger = logging.getLogger("cleanup_corpus")

# ── Mappings for invalid enum values ─────────────────────────────────────

# speedup_order: schema allows exponential|cubic|quadratic|polynomial_other|logarithmic|constant|none|null
SPEEDUP_ORDER_FIX = {
    "speculative": "none",
    "theoretical": "none",        # "theoretical" is a speedup_claims.type, not an order
    "polynomial": "polynomial_other",
}

# speedup_claims.type: schema allows asymptotic|empirical|theoretical|projected|none
SPEEDUP_TYPE_FIX = {
    "speculative": "theoretical",  # closest valid category
    "claimed": "empirical",        # a claim without proof class → empirical
}


def fix_year(data: dict) -> list[str]:
    """Cast paper_metadata.year from string to int where possible."""
    changes = []
    pm = data.get("paper_metadata")
    if not pm:
        return changes
    y = pm.get("year")
    if isinstance(y, str):
        if not y.strip():
            pm["year"] = None
            changes.append("year: '' → null")
        else:
            try:
                pm["year"] = int(y)
                changes.append(f"year: '{y}' → {pm['year']}")
            except ValueError:
                import re
                m = re.search(r"(19|20)\d{2}", y)
                if m:
                    pm["year"] = int(m.group())
                    changes.append(f"year: '{y}' → {pm['year']} (extracted)")
                else:
                    pm["year"] = None
                    changes.append(f"year: '{y}' → null (unparseable)")
    return changes


def fix_speedup_order(data: dict) -> list[str]:
    """Fix invalid complexity_analysis.speedup_order values."""
    changes = []
    for exp in data.get("experiments") or []:
        ca = exp.get("complexity_analysis")
        if not ca:
            continue
        so = ca.get("speedup_order")
        if so in SPEEDUP_ORDER_FIX:
            new_val = SPEEDUP_ORDER_FIX[so]
            ca["speedup_order"] = new_val
            eid = exp.get("experiment_id", "?")
            changes.append(f"exp {eid}: speedup_order '{so}' → '{new_val}'")
    return changes


def fix_speedup_claims_type(data: dict) -> list[str]:
    """Fix invalid speedup_claims[].type values."""
    changes = []
    for exp in data.get("experiments") or []:
        for sc in exp.get("speedup_claims") or []:
            st = sc.get("type")
            if st in SPEEDUP_TYPE_FIX:
                new_val = SPEEDUP_TYPE_FIX[st]
                sc["type"] = new_val
                eid = exp.get("experiment_id", "?")
                changes.append(f"exp {eid}: speedup_claims.type '{st}' → '{new_val}'")
    return changes


def fix_noise_model(data: dict) -> list[str]:
    """Fix malformed noise_model objects (C1).

    Patterns found:
    - noise_model.noise_model is a descriptive string (251 cases) → parse into is_noisy
    - noise_model has dead keys {noise_model: null, noise_parameters: null, mitigation_details: null}
      but no is_noisy (765 cases) → flatten to proper schema fields
    """
    changes = []
    for exp in data.get("experiments") or []:
        nm = exp.get("noise_model")
        if not isinstance(nm, dict):
            continue

        eid = exp.get("experiment_id", "?")
        inner = nm.get("noise_model")

        if isinstance(inner, str) and inner:
            # Parse the descriptive string into structured fields
            lower = inner.lower()
            is_noisy = None
            if any(kw in lower for kw in ("noise-free", "noiseless", "no noise", "statevector",
                                           "no gate noise", "noise_free")):
                is_noisy = False
            elif any(kw in lower for kw in ("noisy", "noise", "decoherence", "real hardware",
                                             "nisq", "shot noise", "depolariz")):
                is_noisy = True

            nm["is_noisy"] = nm.get("is_noisy") if nm.get("is_noisy") is not None else is_noisy
            nm["noise_description"] = inner  # preserve the original text
            del nm["noise_model"]  # remove the malformed key
            changes.append(f"exp {eid}: noise_model flattened (was string: '{inner[:60]}...')")

        elif inner is None and "noise_model" in nm:
            # Dead key: {noise_model: null, noise_parameters: null, ...}
            # Remove the self-referential key
            del nm["noise_model"]

            # Try to infer is_noisy from hardware type if missing
            if nm.get("is_noisy") is None:
                hw_type = (exp.get("hardware") or {}).get("type", "")
                if isinstance(hw_type, str) and hw_type:
                    if "noisy" in hw_type:
                        nm["is_noisy"] = True
                    elif "statevector" in hw_type:
                        nm["is_noisy"] = False
                    elif hw_type.startswith("real_qpu"):
                        nm["is_noisy"] = True

            # Flatten noise_parameters into top-level noise_model fields
            np_data = nm.pop("noise_parameters", None)
            if isinstance(np_data, dict):
                for k, v in np_data.items():
                    if v is not None and k not in nm:
                        nm[k] = v

            changes.append(f"exp {eid}: noise_model dead keys removed")

        exp["noise_model"] = nm
    return changes


def fix_dataset_specification(data: dict) -> list[str]:
    """Fix string dataset_specification values (M5) by wrapping in an object."""
    changes = []
    for exp in data.get("experiments") or []:
        pi = exp.get("problem_instance")
        if not pi:
            continue
        ds = pi.get("dataset_specification")
        if isinstance(ds, str):
            pi["dataset_specification"] = {"description": ds}
            eid = exp.get("experiment_id", "?")
            changes.append(f"exp {eid}: dataset_specification wrapped (was string)")
    return changes


def fix_empty_doi(data: dict) -> list[str]:
    """Fix empty-string doi values (m2) → null."""
    changes = []
    pm = data.get("paper_metadata")
    if pm and pm.get("doi") == "":
        pm["doi"] = None
        changes.append("doi: '' -> null")
    return changes


def fix_secondary_silos(data: dict) -> list[str]:
    """Fix non-standard secondary_silos values (m4)."""
    changes = []
    fd = data.get("finance_domain") or {}
    ss = fd.get("secondary_silos")
    if not ss:
        return changes
    VALID = {"portfolio-optimization", "derivative-pricing", "risk-management",
             "quantum-ml-finance", "fraud-detection", "trading-execution",
             "credit-lending", "cryptography-security", "simulation-monte-carlo",
             "insurance-actuarial", "other"}
    fixed = [s.replace("_", "-") for s in ss]
    # Map known non-standard values
    REMAP = {
        "optimization-methods": "portfolio-optimization",
        "benchmarking-advantage": "other",
        "forecasting-prediction": "quantum-ml-finance",
    }
    new_ss = []
    for s in fixed:
        if s in VALID:
            new_ss.append(s)
        elif s in REMAP:
            new_ss.append(REMAP[s])
            changes.append(f"secondary_silo: '{s}' -> '{REMAP[s]}'")
        else:
            new_ss.append("other")
            changes.append(f"secondary_silo: '{s}' -> 'other'")
    fd["secondary_silos"] = new_ss
    return changes


# Valid algorithm families from benchmark_schema.json
_VALID_FAMILIES = {
    "qaoa", "vqe", "amplitude-estimation", "quantum-ml", "quantum-walk",
    "hhl", "hybrid", "grover", "quantum-annealing", "quantum-svm", "qubo",
    "quantum-simulation", "classical-simulation", "other-gate-based", "other",
}

# Map invalid LLM-invented families to valid ones
_FAMILY_FIX = {
    "quantum-cryptography": "other-gate-based",
    "variational-nisq": "vqe",
    "qft-phase-estimation": "amplitude-estimation",
    "error-mitigation": "other",
    "quantum_ml": "quantum-ml",
    "quantum_annealing": "quantum-annealing",
    "quantum_simulation": "quantum-simulation",
    "quantum_walk": "quantum-walk",
    "amplitude_estimation": "amplitude-estimation",
    "quantum_svm": "quantum-svm",
}


def fix_algorithm_family(data: dict) -> list[str]:
    """Fix invalid algorithm.family values."""
    changes = []
    for exp in data.get("experiments") or []:
        algo = exp.get("algorithm") or {}
        fam = algo.get("family")
        if not fam:
            continue
        # Normalize underscores to hyphens
        normalized = fam.replace("_", "-").lower().strip()
        if normalized in _VALID_FAMILIES and normalized != fam:
            algo["family"] = normalized
            eid = exp.get("experiment_id", "?")
            changes.append(f"exp {eid}: family '{fam}' -> '{normalized}'")
        elif fam in _FAMILY_FIX:
            algo["family"] = _FAMILY_FIX[fam]
            eid = exp.get("experiment_id", "?")
            changes.append(f"exp {eid}: family '{fam}' -> '{_FAMILY_FIX[fam]}'")
        elif normalized in _FAMILY_FIX:
            algo["family"] = _FAMILY_FIX[normalized]
            eid = exp.get("experiment_id", "?")
            changes.append(f"exp {eid}: family '{fam}' -> '{_FAMILY_FIX[normalized]}'")
        elif fam not in _VALID_FAMILIES:
            algo["family"] = "other"
            eid = exp.get("experiment_id", "?")
            changes.append(f"exp {eid}: family '{fam}' -> 'other' (unknown)")
    return changes


def fix_quality_and_validation(data: dict) -> list[str]:
    """Recompute quality score and backfill validation metadata."""
    changes = []
    if "extraction_metadata" not in data:
        data["extraction_metadata"] = {}
        changes.append("created extraction_metadata")

    em = data["extraction_metadata"]

    # Normalize metrics first (idempotent)
    normalize_extraction_metrics(data)

    # Run validation
    errors, warnings = validate_extraction(data)
    old_errs = em.get("validation_errors")
    old_passed = em.get("validation_passed")
    em["validation_errors"] = len(errors)
    em["validation_warnings"] = len(warnings)
    em["validation_passed"] = len(errors) == 0
    if errors:
        em["validation_error_details"] = errors
    if warnings:
        em["validation_warning_details"] = warnings

    if old_errs is None:
        changes.append(f"validation: {len(errors)} errors, {len(warnings)} warnings (new)")
    elif old_passed is None:
        changes.append(f"validation_passed: {'true' if len(errors) == 0 else 'false'} (backfilled)")
    elif old_errs != len(errors):
        changes.append(f"validation_errors: {old_errs} -> {len(errors)} (recomputed)")

    # Compute quality score
    old_qs = em.get("quality_score")
    quality = compute_quality_score(data)
    em["quality_score"] = quality["score"]
    em["quality_details"] = quality

    if old_qs is None:
        changes.append(f"quality_score: null → {quality['score']:.2f}")
    elif abs((old_qs or 0) - quality["score"]) > 0.01:
        changes.append(f"quality_score: {old_qs} → {quality['score']:.2f}")

    return changes


def cleanup_file(path: Path, dry_run: bool = False) -> dict:
    """Apply all fixes to a single extraction file. Returns change summary."""
    data = json.loads(path.read_text(encoding="utf-8"))
    paper_id = data.get("paper_id", path.stem)

    all_changes = []
    all_changes.extend(fix_year(data))
    all_changes.extend(fix_speedup_order(data))
    all_changes.extend(fix_speedup_claims_type(data))
    all_changes.extend(fix_noise_model(data))
    all_changes.extend(fix_dataset_specification(data))
    all_changes.extend(fix_empty_doi(data))
    all_changes.extend(fix_secondary_silos(data))
    all_changes.extend(fix_algorithm_family(data))
    # validation must run LAST since other fixes reduce error count
    all_changes.extend(fix_quality_and_validation(data))

    if all_changes and not dry_run:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False, default=str)

    return {"paper_id": paper_id, "changes": all_changes, "n_changes": len(all_changes)}


def main():
    parser = argparse.ArgumentParser(description="Cleanup corpus data quality issues")
    parser.add_argument("--dry-run", action="store_true", help="Report changes without writing")
    args = parser.parse_args()

    files = sorted(OUTPUT_DIR.glob("*.json"))
    if not files:
        logger.error("No extraction files found in %s", OUTPUT_DIR)
        return

    logger.info("Processing %d extraction files%s", len(files), " (DRY RUN)" if args.dry_run else "")

    total_changes = 0
    files_changed = 0
    change_types = {"year": 0, "speedup_order": 0, "speedup_claims.type": 0,
                    "noise_model": 0, "dataset_specification": 0, "doi": 0,
                    "secondary_silo": 0, "quality_score": 0, "validation": 0,
                    "extraction_metadata": 0}

    for path in files:
        result = cleanup_file(path, dry_run=args.dry_run)
        if result["n_changes"] > 0:
            files_changed += 1
            total_changes += result["n_changes"]
            for c in result["changes"]:
                if c.startswith("year:"):
                    change_types["year"] += 1
                elif "speedup_order" in c and "speedup_claims" not in c:
                    change_types["speedup_order"] += 1
                elif "speedup_claims.type" in c:
                    change_types["speedup_claims.type"] += 1
                elif "family" in c:
                    change_types.setdefault("algorithm_family", 0)
                    change_types["algorithm_family"] += 1
                elif "noise_model" in c:
                    change_types["noise_model"] += 1
                elif "dataset_specification" in c:
                    change_types["dataset_specification"] += 1
                elif c.startswith("doi:"):
                    change_types["doi"] += 1
                elif "secondary_silo" in c:
                    change_types["secondary_silo"] += 1
                elif "quality_score" in c:
                    change_types["quality_score"] += 1
                elif "validation" in c:
                    change_types["validation"] += 1
                elif "extraction_metadata" in c:
                    change_types["extraction_metadata"] += 1

            if result["n_changes"] <= 5:
                for c in result["changes"]:
                    logger.info("  %s: %s", result["paper_id"], c)
            else:
                logger.info("  %s: %d changes", result["paper_id"], result["n_changes"])

    logger.info("=" * 60)
    logger.info("Summary: %d files changed, %d total changes", files_changed, total_changes)
    for ct, n in sorted(change_types.items()):
        if n > 0:
            logger.info("  %-25s %d", ct, n)
    if args.dry_run:
        logger.info("DRY RUN — no files were modified")


if __name__ == "__main__":
    main()
