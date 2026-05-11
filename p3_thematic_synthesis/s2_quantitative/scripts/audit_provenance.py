"""Audit provenance coverage across the P3 extraction corpus.

Reports what fraction of key fields used in quantum advantage assessment
are paper-reported vs. inferred/derived/bridged, addressing examiner
concerns about data provenance (CR-4, CR-5).

Usage:
    python -m p3_thematic_synthesis.s2_quantitative.scripts.audit_provenance
    python -m p3_thematic_synthesis.s2_quantitative.scripts.audit_provenance --verbose
"""

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

_QUANT_ROOT = Path(__file__).resolve().parents[1]
_PROJECT_ROOT = Path(__file__).resolve().parents[3]

EXTRACTIONS_DIR = _QUANT_ROOT / "output" / "extractions"
DERIVED_PATH = (
    _PROJECT_ROOT / "p3_thematic_synthesis" / "s3_quantum_advantage"
    / "derived_fields" / "enriched" / "derived_fields.json"
)

# Fields critical for quantum advantage assessment
CRITICAL_FIELDS = [
    "hardware_type",
    "num_qubits",
    "circuit_depth",
    "speedup_order",
    "quantum_complexity",
    "classical_complexity",
    "advantage_status",
]


def load_derived_lookup() -> dict:
    """Load derived fields enrichment and return lookup by paper_id_experiment_id."""
    if not DERIVED_PATH.exists():
        return {}
    data = json.loads(DERIVED_PATH.read_text(encoding="utf-8"))
    lookup = {}
    for e in data.get("enriched_experiments", []):
        key = f"{e.get('paper_id', '')}_{e.get('experiment_id', '')}"
        lookup[key] = e
    return lookup


def classify_field_source(exp: dict, field: str, derived_entry: dict | None) -> str:
    """Determine the provenance of a critical field for one experiment.

    Returns one of: paper_reported, paper_inferred, derived, bridged,
    missing, or null (field exists but is null/empty).
    """
    prov = exp.get("provenance") or {}

    # Check if the field has explicit provenance tagging
    if field in prov:
        tag = prov[field]
        if tag:
            return tag  # paper_reported, paper_inferred, derived, etc.

    # Check if field was bridged
    bridged = prov.get("bridged_fields") or []
    for b in bridged:
        if b.startswith(f"{field}") or f".{field}" in b:
            return "bridged"

    # Check derived fields
    if derived_entry:
        derived_list = derived_entry.get("derived_field_list") or []
        cd = derived_entry.get("complexity_derived") or {}
        rd = derived_entry.get("resources_derived") or {}
        if field in derived_list:
            return "derived"
        if cd.get(f"{field}_derived"):
            return "derived"
        if rd.get(f"{field}_derived"):
            return "derived"

    # Fall back to checking if the value exists in the extraction
    val = _get_field_value(exp, field)
    if val is None:
        return "missing"

    # No provenance tag but value exists — assume paper_reported (pre-provenance corpus)
    return "untagged"


def _get_field_value(exp: dict, field: str):
    """Get the value of a critical field from an experiment dict."""
    if field == "hardware_type":
        return (exp.get("hardware") or {}).get("type")
    elif field == "num_qubits":
        return (exp.get("quantum_resources") or {}).get("num_qubits")
    elif field == "circuit_depth":
        return (exp.get("quantum_resources") or {}).get("circuit_depth")
    elif field == "speedup_order":
        return (exp.get("complexity_analysis") or {}).get("speedup_order")
    elif field == "quantum_complexity":
        return (exp.get("complexity_analysis") or {}).get("quantum_complexity")
    elif field == "classical_complexity":
        return (exp.get("complexity_analysis") or {}).get("classical_complexity")
    elif field == "advantage_status":
        return (exp.get("advantage_assessment") or {}).get("advantage_status")
    return None


def main():
    parser = argparse.ArgumentParser(description="Audit provenance coverage")
    parser.add_argument("--verbose", action="store_true", help="Show per-paper details")
    args = parser.parse_args()

    files = sorted(EXTRACTIONS_DIR.glob("*.json"))
    if not files:
        print(f"No extraction files found in {EXTRACTIONS_DIR}", file=sys.stderr)
        return

    derived_lookup = load_derived_lookup()

    # Per-field counters
    field_sources: dict[str, Counter] = {f: Counter() for f in CRITICAL_FIELDS}
    total_experiments = 0
    papers_with_provenance = 0
    papers_without_provenance = 0

    # Bridge usage stats
    bridge_counts = Counter()

    for path in files:
        data = json.loads(path.read_text(encoding="utf-8"))
        paper_id = data.get("paper_id", path.stem)
        paper_has_prov = False

        for exp in data.get("experiments") or []:
            total_experiments += 1
            eid = exp.get("experiment_id", "?")
            derived_key = f"{paper_id}_{eid}"
            derived_entry = derived_lookup.get(derived_key)

            prov = exp.get("provenance") or {}
            if prov:
                paper_has_prov = True

            # Count bridged fields
            for b in (prov.get("bridged_fields") or []):
                field_name = b.split("←")[0] if "←" in b else b
                bridge_counts[field_name] += 1

            for field in CRITICAL_FIELDS:
                source = classify_field_source(exp, field, derived_entry)
                field_sources[field][source] += 1

        if paper_has_prov:
            papers_with_provenance += 1
        else:
            papers_without_provenance += 1

    # Report
    print(f"\n{'='*70}")
    print(f"PROVENANCE AUDIT — {len(files)} papers, {total_experiments} experiments")
    print(f"{'='*70}")

    print(f"\nPapers with provenance tags:    {papers_with_provenance}")
    print(f"Papers without provenance tags:  {papers_without_provenance}")
    print(f"  (pre-provenance corpus — will be tagged on next extraction run)")

    print(f"\n{'-'*70}")
    print(f"{'Field':<25} {'Reported':>8} {'Inferred':>8} {'Derived':>8} {'Bridged':>8} {'Untagged':>8} {'Missing':>8}")
    print(f"{'-'*70}")

    for field in CRITICAL_FIELDS:
        c = field_sources[field]
        reported = c.get("paper_reported", 0)
        inferred = c.get("paper_inferred", 0)
        derived = c.get("derived", 0)
        bridged = c.get("bridged", 0)
        untagged = c.get("untagged", 0)
        missing = c.get("missing", 0) + c.get("null", 0)
        print(f"{field:<25} {reported:>8} {inferred:>8} {derived:>8} {bridged:>8} {untagged:>8} {missing:>8}")

    total = total_experiments
    print(f"{'-'*70}")
    print(f"{'Total experiments':<25} {total:>8}")

    # Provenance quality summary
    print(f"\n{'-'*70}")
    print("PROVENANCE QUALITY SUMMARY")
    print(f"{'-'*70}")

    for field in CRITICAL_FIELDS:
        c = field_sources[field]
        populated = total - c.get("missing", 0) - c.get("null", 0)
        reported = c.get("paper_reported", 0)
        pct_reported = (reported / populated * 100) if populated > 0 else 0
        pct_populated = (populated / total * 100) if total > 0 else 0
        print(f"  {field:<25} populated: {pct_populated:5.1f}%  paper_reported: {pct_reported:5.1f}%")

    if bridge_counts:
        print(f"\n{'-'*70}")
        print("TOP BRIDGED FIELDS (most frequently copied from other locations)")
        print(f"{'-'*70}")
        for field_name, count in bridge_counts.most_common(15):
            print(f"  {field_name:<55} {count:>6}")

    print()


if __name__ == "__main__":
    main()
