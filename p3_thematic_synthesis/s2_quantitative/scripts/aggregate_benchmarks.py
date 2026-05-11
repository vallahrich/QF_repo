"""Aggregate benchmark extractions into per-silo comparison tables.

Reads all extraction JSONs from output/extractions/, groups papers by
their primary finance silo, and produces CSV + markdown comparison tables
in output/tables/.

Usage:
    python -m p3_thematic_synthesis.s2_quantitative.scripts.aggregate_benchmarks
    python -m p3_thematic_synthesis.s2_quantitative.scripts.aggregate_benchmarks --silo portfolio-optimization
"""

import argparse
import csv
import json
import sys
from pathlib import Path

_QUANT_ROOT = Path(__file__).resolve().parents[1]
_PROJECT_ROOT = Path(__file__).resolve().parents[3]

_project_root_str = str(_PROJECT_ROOT)
_p3_str = str(Path(__file__).resolve().parents[2])

# Ensure project root is first on sys.path so our 'shared' package wins
if _project_root_str not in sys.path:
    sys.path.insert(0, _project_root_str)
elif sys.path[0] != _project_root_str:
    sys.path.remove(_project_root_str)
    sys.path.insert(0, _project_root_str)
if _p3_str not in sys.path:
    sys.path.insert(1, _p3_str)

_shared_mod = sys.modules.get("shared")
if _shared_mod is not None:
    _shared_file = getattr(_shared_mod, "__file__", None) or ""
    if _PROJECT_ROOT.as_posix() not in Path(_shared_file).as_posix() if _shared_file else True:
        for _key in [k for k in sys.modules if k == "shared" or k.startswith("shared.")]:
            del sys.modules[_key]

from shared.tools.logger import get_logger  # noqa: E402

logger = get_logger("aggregate_benchmarks")

EXTRACTIONS_DIR = _QUANT_ROOT / "output" / "extractions"
TABLES_DIR = _QUANT_ROOT / "output" / "tables"
SILO_METRICS_PATH = _QUANT_ROOT / "config" / "silo_metrics.json"


def _load_silo_metrics() -> dict:
    """Load per-silo primary metric definitions."""
    with open(SILO_METRICS_PATH, encoding="utf-8") as f:
        return json.load(f)


def _load_extractions(input_dir: Path | None = None) -> list[dict]:
    """Load all extraction JSONs from the directory."""
    directory = input_dir or EXTRACTIONS_DIR
    results: list[dict] = []
    if not directory.is_dir():
        return results
    for path in sorted(directory.glob("*.json")):
        if path.name.startswith("_"):
            continue
        try:
            with open(path, encoding="utf-8") as f:
                results.append(json.load(f))
        except (json.JSONDecodeError, OSError) as exc:
            logger.warning(f"Skipping {path.name}: {exc}")
    return results


def _group_by_silo(extractions: list[dict]) -> dict[str, list[dict]]:
    """Group papers by their primary finance silo."""
    groups: dict[str, list[dict]] = {}
    for ext in extractions:
        silo = (ext.get("finance_domain") or {}).get("primary_silo") or "unclassified"
        groups.setdefault(silo, []).append(ext)
    return groups


def _metric_matches(extracted_name: str, target_name: str) -> bool:
    """Check if an extracted metric name matches a target, with fuzzy matching.

    Handles common variations:
      - exact match (case-insensitive)
      - target is a substring of the extracted name
      - extracted name starts with the target
    """
    e = extracted_name.lower().strip()
    t = target_name.lower().strip()
    if e == t:
        return True
    if t in e:
        return True
    if e.startswith(t):
        return True
    return False


def _find_result(results: list[dict], metric_name: str) -> str:
    """Find a metric value in a results list. Returns formatted string or '—'."""
    for r in results:
        if _metric_matches(r.get("metric_name", ""), metric_name):
            val = r.get("value")
            if val is not None:
                return str(val)
    return "—"


def _find_baseline(baselines: list[dict], metric_name: str) -> tuple[str, str]:
    """Find all baselines for a metric. Returns (method_names, values).

    If multiple baselines match, concatenates them with ' / '.
    """
    matches: list[tuple[str, str]] = []
    for b in baselines:
        if _metric_matches(b.get("metric_name", ""), metric_name):
            method = b.get("method_name", "?")
            val = b.get("value")
            if val is not None:
                matches.append((method, str(val)))
    if not matches:
        return ("—", "—")
    if len(matches) == 1:
        return matches[0]
    # Multiple baselines — show all values with method abbreviations
    methods = " / ".join(m[0][:20] for m in matches)
    values = " / ".join(m[1] for m in matches)
    return (methods, values)


def _speedup_summary(claims: list[dict]) -> str:
    """Summarize speedup claims into a short display string."""
    if not claims:
        return "—"
    parts: list[str] = []
    for c in claims:
        stype = c.get("type", "")
        factor = c.get("factor", "")
        if factor:
            parts.append(f"{factor} ({stype})")
        elif stype and stype != "none":
            parts.append(stype)
    return "; ".join(parts) if parts else "—"


def _flatten_experiment(paper: dict, exp: dict) -> dict:
    """Flatten a paper + experiment into a single row dict."""
    meta = paper.get("paper_metadata") or {}
    hw = exp.get("hardware") or {}
    qr = exp.get("quantum_resources") or {}
    algo = exp.get("algorithm") or {}
    pi = exp.get("problem_instance") or {}

    hw_type = hw.get("type") or "not_specified"
    is_qpu = (
        "QPU" if ("real_qpu" in hw_type or hw_type == "quantum_annealer") else "Sim"
    )

    # Build problem size description
    size_parts: list[str] = []
    if pi.get("num_assets"):
        size_parts.append(f"{pi['num_assets']} assets")
    if pi.get("dataset_size"):
        size_parts.append(f"{pi['dataset_size']} samples")
    if pi.get("time_steps"):
        size_parts.append(f"{pi['time_steps']} steps")
    if pi.get("num_features"):
        size_parts.append(f"{pi['num_features']} features")
    problem_size = ", ".join(size_parts) if size_parts else "—"

    return {
        "paper_id": paper.get("paper_id", ""),
        "title": (meta.get("title") or "")[:60],
        "year": meta.get("year", ""),
        "algorithm": algo.get("family", "—"),
        "variant": algo.get("variant") or "",
        "hardware_type": hw_type,
        "sim_or_qpu": is_qpu,
        "provider": hw.get("provider") or "—",
        "device": hw.get("device_name") or "—",
        "num_qubits": qr.get("num_qubits") or "—",
        "circuit_depth": qr.get("circuit_depth") or "—",
        "problem_size": problem_size,
        "speedup": _speedup_summary(exp.get("speedup_claims", [])),
    }


def build_silo_table(
    silo: str, papers: list[dict], silo_metrics: dict
) -> list[dict]:
    """Build a comparison table for a single silo.

    Returns a list of row dicts (one per experiment), sorted by
    year descending, then algorithm, then qubit count descending.
    """
    metrics_config = silo_metrics.get(silo, {})
    primary = metrics_config.get("primary_metrics", [])

    # Classical-only algorithm families to skip in the comparison table.
    # These are baselines, not quantum experiments.
    _CLASSICAL_FAMILIES = {"classical-simulation"}

    rows: list[dict] = []
    for paper in papers:
        if not paper.get("has_quantitative_results"):
            continue
        for exp in paper.get("experiments", []):
            algo_family = (exp.get("algorithm") or {}).get("family", "")
            if algo_family in _CLASSICAL_FAMILIES:
                continue  # Skip purely classical baseline experiments

            row = _flatten_experiment(paper, exp)

            # Append silo-specific primary metrics
            results = exp.get("results", [])
            baselines = exp.get("classical_baselines", [])
            for metric in primary:
                row[f"q_{metric}"] = _find_result(results, metric)
                bl_method, bl_val = _find_baseline(baselines, metric)
                row[f"bl_{metric}"] = bl_val
                row[f"bl_{metric}_method"] = bl_method

            rows.append(row)

    # Sort: year desc → algorithm → num_qubits desc
    def _sort_key(r: dict) -> tuple:
        y = r.get("year") or 0
        q = r.get("num_qubits")
        q_int = int(q) if isinstance(q, (int, float)) else 0
        return (-int(y), r.get("algorithm", ""), -q_int)

    rows.sort(key=_sort_key)
    return rows


def write_csv(rows: list[dict], path: Path) -> None:
    """Write rows to a CSV file."""
    if not rows:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(rows[0].keys())
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_markdown_table(rows: list[dict], path: Path, silo: str) -> None:
    """Write rows as a markdown comparison table."""
    path.parent.mkdir(parents=True, exist_ok=True)

    if not rows:
        path.write_text(
            f"# {silo}\n\nNo quantitative results found.\n", encoding="utf-8"
        )
        return

    # Core display columns
    display_cols = [
        "paper_id", "year", "algorithm", "sim_or_qpu",
        "num_qubits", "circuit_depth", "problem_size", "speedup",
    ]
    # Add silo-specific metric columns (quantum result + baseline)
    extra_cols = [
        k for k in rows[0]
        if k.startswith("q_") or (k.startswith("bl_") and not k.endswith("_method"))
    ]
    cols = display_cols + extra_cols

    lines = [f"# {silo}\n"]
    header = "| " + " | ".join(cols) + " |"
    separator = "| " + " | ".join(["---"] * len(cols)) + " |"
    lines.append(header)
    lines.append(separator)

    for row in rows:
        vals = [str(row.get(c, "—")).replace("|", "\\|") for c in cols]
        lines.append("| " + " | ".join(vals) + " |")

    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def aggregate(
    input_dir: str | None = None,
    output_dir: str | None = None,
    silo_filter: str | None = None,
) -> dict[str, int]:
    """Run full aggregation across all extracted papers.

    Returns a dict mapping silo name to row count.
    """
    extractions = _load_extractions(Path(input_dir) if input_dir else None)
    if not extractions:
        logger.info("No extractions found — nothing to aggregate.")
        return {}

    silo_metrics = _load_silo_metrics()
    grouped = _group_by_silo(extractions)
    out = Path(output_dir) if output_dir else TABLES_DIR

    summary: dict[str, int] = {}
    for silo, papers in sorted(grouped.items()):
        if silo_filter and silo != silo_filter:
            continue

        rows = build_silo_table(silo, papers, silo_metrics)
        write_csv(rows, out / f"{silo}.csv")
        write_markdown_table(rows, out / f"{silo}.md", silo)
        summary[silo] = len(rows)
        logger.info(
            f"Silo {silo}: {len(rows)} experiment rows from {len(papers)} papers"
        )

    return summary


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Aggregate benchmark extractions into comparison tables."
    )
    parser.add_argument(
        "--input-dir", default=None,
        help="Directory containing extraction JSONs.",
    )
    parser.add_argument(
        "--output-dir", default=None,
        help="Directory for output CSV and markdown tables.",
    )
    parser.add_argument(
        "--silo", default=None,
        help="Process only this silo (e.g. portfolio-optimization).",
    )
    args = parser.parse_args()

    summary = aggregate(args.input_dir, args.output_dir, args.silo)
    total = sum(summary.values())
    print(f"Generated tables for {len(summary)} silos, {total} total rows")
    for silo, count in sorted(summary.items()):
        print(f"  {silo}: {count} rows")


if __name__ == "__main__":
    main()
