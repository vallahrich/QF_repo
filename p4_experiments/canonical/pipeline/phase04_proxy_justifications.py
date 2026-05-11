"""Phase 4 - Generate proxy justifications from S2 quantitative extractions.

For every Proxy-tier (P) label with an on-disk circuit artifact, this script:

  * Detects the generic template imported by circuit.py, if any.
  * Resolves the genuine Phase 3 S2 experiment by paper_id and experiment_id.
  * Reads classification context from phase3_compare.json.
  * Writes proxy_justification.md next to the circuit.
  * Updates cohort.json with the proxy template and justification hash.

Run sequence:
    python -m p4_experiments.canonical.pipeline.phase03_compare
    python -m p4_experiments.canonical.pipeline.phase04_proxy_justifications
    python -m p4_experiments.canonical.audits.audit_phase04
"""

from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from p4_experiments.canonical.data.s2_extraction_index import s2_experiment, s2_extraction_relpath

ROOT = Path(__file__).resolve().parents[3]
CANON = ROOT / "p4_experiments" / "canonical"
COHORT = CANON / "cohort.json"
REPORTS = CANON / "reports"
COMPARE = REPORTS / "phase3_compare.json"
DISPATCH = CANON / "phase3_full_dispatch.json"

DATE = datetime.now(timezone.utc).date().isoformat()
PHASE_TAG = "Phase 4 proxy fallback (template selection + S2 justification)"

TEMPLATE_IMPORT_RE = re.compile(
    r"^\s*from\s+p4_experiments\.(?:common|core)\.templates\.(\w+)\s+import",
    re.M,
)

EXCLUSION_NOTE = (
    "This label is **Proxy-declared (P)**. Per PRE_REGISTRATION section 6.4, "
    "P-tier labels are **excluded from headline H4** and are reported only "
    "in declared proxy sensitivity and Full N appendix sub-cohorts."
)

PROXY_METADATA_KEYS = (
    "proxy_template",
    "proxy_template_secondary",
    "proxy_template_detected_from",
    "proxy_justification_path",
    "proxy_justification_sha256",
    "proxy_reason",
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _detect_template(*candidate_paths: Path | None) -> tuple[list[str], Path | None]:
    for path in candidate_paths:
        if path and path.exists():
            text = path.read_text(encoding="utf-8")
            templates = sorted(set(TEMPLATE_IMPORT_RE.findall(text)))
            return templates, path
    return [], None


def _clear_non_p_proxy_artifacts(label_id: str, entry: dict[str, Any]) -> tuple[bool, int]:
    changed = any(key in entry for key in PROXY_METADATA_KEYS)
    removed_files = 0

    candidate_paths: set[Path] = set()
    rel_path = entry.get("proxy_justification_path")
    if rel_path:
        candidate_paths.add(ROOT / rel_path)
    circuit_path_rel = entry.get("circuit_path")
    if circuit_path_rel:
        circuit_dir = (ROOT / circuit_path_rel).parent
        candidate_paths.add(circuit_dir / f"proxy_justification_{label_id}.md")
        candidate_paths.add(circuit_dir / "proxy_justification.md")

    for path in candidate_paths:
        if path.exists() and path.name.startswith("proxy_justification") and path.suffix == ".md":
            path.unlink()
            removed_files += 1
            changed = True

    for key in PROXY_METADATA_KEYS:
        entry.pop(key, None)

    history = entry.get("fidelity_history") or []
    filtered = [item for item in history if "Phase 4" not in (item.get("phase") or "")]
    if len(filtered) != len(history):
        entry["fidelity_history"] = filtered
        changed = True

    return changed, removed_files


def _has_value(value: Any) -> bool:
    if isinstance(value, list):
        return bool(value)
    return value not in (None, "", "NOT_STATED", "not_specified")


def _format_value(value: Any) -> str:
    if isinstance(value, (dict, list)):
        return json.dumps(value, sort_keys=True)
    return str(value)


def _missing_s2_fields(experiment: dict[str, Any]) -> list[str]:
    algorithm = experiment.get("algorithm") or {}
    problem = experiment.get("problem_formulation") or {}
    resources = experiment.get("quantum_resources") or {}
    checks = [
        ("algorithm.family", algorithm.get("family")),
        ("algorithm.variant", algorithm.get("variant")),
        ("problem_formulation.encoding_method", problem.get("encoding_method")),
        ("quantum_resources.num_qubits", resources.get("num_qubits")),
        ("quantum_resources.circuit_depth", resources.get("circuit_depth")),
        ("classical_baselines", experiment.get("classical_baselines")),
    ]
    return [name for name, value in checks if not _has_value(value)]


def _failed_criteria(criteria: dict[str, Any] | None) -> list[str]:
    if not criteria:
        return []
    return [key for key, value in criteria.items() if value is False]


def _stated_s2_block(experiment: dict[str, Any]) -> str:
    algorithm = experiment.get("algorithm") or {}
    problem = experiment.get("problem_formulation") or {}
    resources = experiment.get("quantum_resources") or {}
    implementation = experiment.get("implementation_details") or {}

    fields = [
        ("algorithm.family", algorithm.get("family")),
        ("algorithm.variant", algorithm.get("variant")),
        ("algorithm.ansatz", algorithm.get("ansatz")),
        ("problem_formulation.encoding_method", problem.get("encoding_method")),
        ("problem_formulation.objective_function", problem.get("objective_function")),
        ("problem_formulation.num_ancilla_qubits", problem.get("num_ancilla_qubits")),
        ("quantum_resources.num_qubits", resources.get("num_qubits")),
        ("quantum_resources.circuit_depth", resources.get("circuit_depth")),
        ("quantum_resources.gate_count_total", resources.get("gate_count_total")),
        ("quantum_resources.num_shots", resources.get("num_shots")),
        ("implementation_details.classical_solver", implementation.get("classical_solver")),
        ("implementation_details.classical_preprocessing", implementation.get("classical_preprocessing")),
        ("implementation_details.classical_postprocessing", implementation.get("classical_postprocessing")),
    ]
    lines = [
        f"- `{name}` = `{_format_value(value)}`"
        for name, value in fields
        if _has_value(value)
    ]

    for result in (experiment.get("results") or [])[:5]:
        metric = result.get("metric_name")
        value = result.get("value")
        if _has_value(metric) and _has_value(value):
            unit = result.get("unit") or "unitless"
            lines.append(f"- `results.{metric}` = `{_format_value(value)}` ({unit})")

    return "\n".join(lines) if lines else "_(none)_"


def _baseline_block(label: dict[str, Any], experiment: dict[str, Any]) -> str:
    baselines = experiment.get("classical_baselines") or []
    if baselines:
        lines = []
        for baseline in baselines[:5]:
            method = baseline.get("method_name") or "unnamed_method"
            metric = baseline.get("metric_name")
            value = baseline.get("value")
            unit = baseline.get("unit") or "unitless"
            if _has_value(metric) and _has_value(value):
                lines.append(f"- `{method}`: `{metric}` = `{_format_value(value)}` ({unit})")
            else:
                lines.append(f"- `{method}`")
        return "\n".join(lines)

    cohort_baseline = label.get("classical_baseline") or {}
    if cohort_baseline:
        source = cohort_baseline.get("source") or {}
        return (
            f"- `{cohort_baseline.get('algorithm_label', 'not recorded')}` "
            f"(source.type: `{source.get('type', 'not recorded')}`)"
        )
    return "_(none recorded in S2)_"


def _render_md(
    label_id: str,
    label: dict[str, Any],
    experiment: dict[str, Any],
    compare_entry: dict[str, Any],
    templates: list[str],
) -> str:
    paper_id = label["paper_id"]
    silo = label["silo"]
    family = label.get("algorithm_family") or (experiment.get("algorithm") or {}).get("family")
    paper_title = (label.get("paper_metadata") or {}).get("title", "")
    extraction_path = compare_entry.get("extraction_path") or s2_extraction_relpath(label)

    if templates:
        template_block = "\n".join(
            f"- `p4_experiments.core.templates.{template}`" for template in templates
        )
        template_header = "## Proxy template(s) selected"
    else:
        template_block = (
            "- No generic template import was detected. The label uses a "
            "paper-specific implementation in circuit.py and is retained as a "
            "declared proxy for headline-claim purposes."
        )
        template_header = "## Proxy template selection"

    missing = _missing_s2_fields(experiment)
    missing_block = "\n".join(f"- `{name}`" for name in missing) if missing else "_(none among checked S2 fields)_"

    failed = _failed_criteria(compare_entry.get("criteria"))
    criteria_descriptions = {
        "s2_source_present": "S2 paper file is missing",
        "s2_experiment_id_match": "experiment_id was not found in the S2 paper file",
        "s2_algorithm_family_present": "algorithm family is absent in S2",
        "s2_quantum_resources_present": "S2 reports no quantitative resource fields",
    }
    failed_block = "\n".join(
        f"- `{criterion}` - {criteria_descriptions.get(criterion, criterion)}"
        for criterion in failed
    ) if failed else "_(no S2 source-resolution criteria failed)_"

    rationale = compare_entry.get("rationale", "")
    stated_block = _stated_s2_block(experiment)
    baseline_block = _baseline_block(label, experiment)

    return f"""---
label_id: {label_id}
paper_id: {paper_id}
silo: {silo}
algorithm_family: {family}
fidelity: P
phase: 4
generated_utc: {datetime.now(timezone.utc).isoformat()}
extraction_source: {extraction_path}
classification_method: {compare_entry.get("method", "phase3_s2_cohort_snapshot")}
---

# Proxy justification - `{label_id}`

**Paper.** {paper_title or '(no title in cohort.paper_metadata)'} ({paper_id})

{template_header}

{template_block}

## Why this label is not Faithful

Phase 3 classification context: {rationale}

Failed source-resolution criteria:
{failed_block}

## What S2 states for this experiment

{stated_block}

## S2 fields absent or unresolved

{missing_block}

## Classical baseline

{baseline_block}

## Sub-cohort exclusion

{EXCLUSION_NOTE}

---

_Generated by `p4_experiments/canonical/pipeline/phase04_proxy_justifications.py`._
"""


def main() -> int:
    cohort = json.loads(COHORT.read_text(encoding="utf-8"))
    compare = json.loads(COMPARE.read_text(encoding="utf-8"))
    classifications = compare.get("classifications", {})
    labels = cohort["labels"]
    dispatch = json.loads(DISPATCH.read_text(encoding="utf-8")) if DISPATCH.exists() else []
    v5_paths = {row["label_id"]: row.get("v5_circuit_path") for row in dispatch}

    n_p = 0
    n_with_template = 0
    n_paper_specific = 0
    n_missing_s2 = 0
    template_counts: dict[str, int] = {}
    written: list[str] = []
    n_non_p_cleaned = 0
    n_non_p_proxy_files_removed = 0

    for label_id, entry in labels.items():
        if entry.get("fidelity") != "P":
            changed, removed = _clear_non_p_proxy_artifacts(label_id, entry)
            if changed:
                n_non_p_cleaned += 1
            n_non_p_proxy_files_removed += removed
            continue
        n_p += 1

        circuit_path_rel = entry.get("circuit_path")
        if not circuit_path_rel:
            print(f"[SKIP] {label_id}: no circuit_path")
            continue

        experiment = s2_experiment(entry)
        if experiment is None:
            n_missing_s2 += 1
            print(f"[WARN] {label_id}: no matching S2 experiment; skipping")
            continue

        circuit_path = ROOT / circuit_path_rel
        circuit_dir = circuit_path.parent
        circuit_dir.mkdir(parents=True, exist_ok=True)

        v5_rel = v5_paths.get(label_id)
        v5_full = (ROOT / v5_rel) if v5_rel else None
        templates, detected_from = _detect_template(circuit_path, v5_full)
        if templates:
            n_with_template += 1
            for template in templates:
                template_counts[template] = template_counts.get(template, 0) + 1
        else:
            n_paper_specific += 1
            template_counts["__paper_specific__"] = template_counts.get("__paper_specific__", 0) + 1

        compare_entry = classifications.get(label_id, {})
        md = _render_md(label_id, entry, experiment, compare_entry, templates)
        legacy_path = circuit_dir / "proxy_justification.md"
        if legacy_path.exists():
            legacy_path.unlink()
        out_path = circuit_dir / f"proxy_justification_{label_id}.md"
        out_path.write_text(md, encoding="utf-8")
        rel_path = str(out_path.relative_to(ROOT)).replace("\\", "/")
        sha = _sha256(out_path)

        proxy_template = templates[0] if templates else "paper_specific_no_template"
        entry["proxy_template"] = proxy_template
        if len(templates) > 1:
            entry["proxy_template_secondary"] = templates[1:]
        entry["proxy_justification_path"] = rel_path
        entry["proxy_justification_sha256"] = sha
        if detected_from is not None:
            entry["proxy_template_detected_from"] = str(detected_from.relative_to(ROOT)).replace("\\", "/")

        history = entry.setdefault("fidelity_history", [])
        history = [
            item for item in history
            if not (item.get("date") == DATE and "Phase 4" in (item.get("phase") or ""))
        ]
        failed_criteria = _failed_criteria(compare_entry.get("criteria"))
        history.append({
            "date": DATE,
            "tier": "P",
            "rationale": (
                f"Phase 4 proxy fallback locked in from S2 evidence. Template: {proxy_template}. "
                f"Failed S2 source criteria: {', '.join(failed_criteria) or 'none'}. "
                f"Justification at {rel_path} (sha256: {sha[:16]}...)."
            ),
            "phase": PHASE_TAG,
            "proxy_template": proxy_template,
            "proxy_justification_path": rel_path,
            "proxy_justification_sha256": sha,
        })
        entry["fidelity_history"] = history
        written.append(label_id)

    phase_status = cohort.get("_phase_status", {})
    if not isinstance(phase_status, dict):
        phase_status = {"_legacy": phase_status}
    phase_status["phase4"] = {
        "status": "complete",
        "completed_utc": datetime.now(timezone.utc).isoformat(),
        "P_total": n_p,
        "P_with_generic_template": n_with_template,
        "P_paper_specific_no_template": n_paper_specific,
        "P_missing_s2_experiment": n_missing_s2,
        "template_distribution": template_counts,
        "non_P_proxy_metadata_cleared": n_non_p_cleaned,
        "non_P_proxy_files_removed": n_non_p_proxy_files_removed,
    }
    cohort["_phase_status"] = phase_status

    COHORT.write_text(json.dumps(cohort, indent=2), encoding="utf-8")
    print(f"[Phase 4] proxy_justification.md written for {len(written)} P-tier labels")
    print(f"[Phase 4] template distribution: {template_counts}")
    print(
        f"[Phase 4] non-P proxy cleanup: metadata={n_non_p_cleaned}, "
        f"files_removed={n_non_p_proxy_files_removed}"
    )
    if n_missing_s2:
        print(f"[Phase 4] WARNING: {n_missing_s2} P-tier labels missing S2 experiments")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
