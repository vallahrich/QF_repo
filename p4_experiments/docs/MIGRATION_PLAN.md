# Phase 4 Restructuring Migration Plan

> **Status note (2026-05-11): historical migration plan — all seven waves complete, and the canonical flat wrapper layer has been removed for handoff clarity.** Retained as provenance for the Phase 4 directory restructuring executed before the freeze; not an active task list. Current truth: [../FREEZE.md](../FREEZE.md), [../canonical/PRE_REGISTRATION.md](../canonical/PRE_REGISTRATION.md), and [../../docs/PROJECT_STATE.yaml](../../docs/PROJECT_STATE.yaml).

This plan restructures Phase 4 without breaking the active canonical evidence chain. It is staged because the current pipeline, audits, and release bundle use hard-coded canonical paths.

## Status

Wave 1 is complete. Wave 2 is complete: generated Phase 10 artifacts, H/Hoefler figures, Phase 8c alternatives, finalized Phase 8d QAE/HHL scout results, Phase 8e cards, and Phase 11 release artifacts now live under `canonical/outputs/` or `canonical/release/`. Wave 3 is complete: authoritative phase, audit, and S2 helper implementations now live under `canonical/pipeline/`, `canonical/audits/`, and `canonical/data/`; the older flat module wrappers were removed during the final handoff cleanup. Wave 4 is complete: reusable implementation code now lives under `core/`, and `common/` is retained only for raw result output. Wave 5 is complete: per-paper evidence and review evidence now live under `experiments/`; old root silo imports are preserved by package-level aliases rather than root folders. Wave 6 is complete for the report layer: generated JSON reports now live under `canonical/reports/` and audit JSON outputs under `canonical/reports/audit/`. Wave 7 is complete for the infrastructure layer: Phase 8/8d VM setup, sync, monitor, helper, and legacy bootstrap tooling now lives under `infra/azure/`.

## Non-Negotiable Guardrails

1. Do not move scientific external-compute result directories into `infra/`. Phase 8d is finalized locally under `canonical/outputs/phase08d_qae_hhl_scout/`; only VM setup, sync, monitor, helper, and historical bootstrap material belongs under `infra/`.
2. Do not move `canonical/PRE_REGISTRATION.md` until `cohort.json`, `audit_phase3.py`, prompts, and Phase 11 bundling are updated together.
3. Do not move `common/output/results/` until Phase 8, Phase 9, Phase 10, Phase 11, and audits read the new path.
4. Do not hand-edit `canonical/release/zenodo_bundle/`; rebuild Phase 11 after final path changes.
5. Use compatibility wrappers for moved Python modules.
6. Run the audit ladder after every structural wave.
7. Propose a `docs/PROJECT_STATE.yaml` update after the structural migration is complete; do not edit it without approval.

## Wave 1 - Documentation Layer

Goal: create a professional documentation surface without breaking runtime paths.

Actions:

- Add `p4_experiments/docs/README.md`.
- Add `p4_experiments/docs/ARCHITECTURE.md`.
- Add `p4_experiments/docs/MIGRATION_PLAN.md`.
- Update `p4_experiments/README.md` to point to the docs layer.
- Keep canonical documents in `canonical/` for compatibility.

Validation:

```powershell
python -m p4_experiments.canonical.run_pipeline --dry-run
python -m p4_experiments.canonical.audits.audit_phase03
```

## Wave 2 - Generated Output Boundaries

Goal: separate generated outputs from executable scripts.

Proposed moves:

```text
canonical/figures/ -> thesis/appendix figure files; P4 keeps source CSVs only [handoff cleanup]
canonical/manuscript_artifacts/ -> canonical/outputs/manuscript_artifacts/ [complete]
canonical/s8d_qae_hhl_scout/ -> canonical/outputs/phase08d_qae_hhl_scout/ [complete]
canonical/s8c_classical_alternatives/ -> canonical/outputs/phase08c_alternatives/ [complete]
canonical/s8e_per_silo/ -> canonical/outputs/phase08e_per_silo/ [complete]
canonical/zenodo_bundle* -> canonical/release/ [complete]
```

Required code updates:

- `phase10_manuscript_artifacts.py`
- `phase10_h_figures.py`
- `phase10_hoefler_scaling_figure.py`
- `phase11_zenodo_bundle.py`
- `audit_phase10.py`
- `audit_phase11.py`
- `phase8d_qae_hhl_scout.py`
- `phase8d_select_experiments.py`
- `phase8d_finalize_qae_hhl.py`
- `audit_phase8d.py`
- `phase8e_per_silo_synthesis.py`
- `audit_phase8e.py`
- `README.md` and `REPRODUCE.md`

Validation:

```powershell
python -m p4_experiments.canonical.audits.audit_phase08d
python -m p4_experiments.canonical.audits.audit_phase10
python -m p4_experiments.canonical.pipeline.phase11_zenodo_bundle
python -m p4_experiments.canonical.audits.audit_phase11
```

## Wave 3 - Pipeline and Audit Modules

Goal: make `canonical/` navigable by separating executable phases from audit code.

Status: complete. The target namespaces now contain the authoritative implementations, and flat legacy module paths delegate to those target modules.

Completed moves:

- `canonical/phase*.py` and `canonical/finalize_phase8_results.py` implementation bodies moved into `canonical/pipeline/`.
- `canonical/audit_phase*.py` implementation bodies moved into `canonical/audits/`.
- `canonical/s2_extraction_index.py` implementation moved into `canonical/data/s2_extraction_index.py`.
- Old flat phase, audit, and S2 helper module paths were removed after direct references were migrated to the structured namespaces.
- `run_pipeline.py` dispatches target `pipeline/` and `audits/` scripts while preserving existing audit JSON report names.

Phase 8d has since completed and its finalized local result directory moved under `canonical/outputs/phase08d_qae_hhl_scout/`. Helper/VM operations are historical only and now live under `infra/azure/`; canonical JSON state and release bundles are regenerated through the audit-guarded phase scripts after path moves.

Implemented move pattern:

```text
canonical/phase*.py -> canonical/pipeline/phase*.py [complete]
canonical/finalize_phase8_results.py -> canonical/pipeline/phase08_finalize_results.py [complete]
canonical/audit_phase*.py -> canonical/audits/audit_phase*.py [complete]
canonical/s2_extraction_index.py -> canonical/data/s2_extraction_index.py [complete]
```

Final handoff requirement:

- Use `p4_experiments.canonical.pipeline.*` for direct phase execution.
- Use `p4_experiments.canonical.audits.*` for direct audit execution.
- Rebuild Phase 11 after code/docs changes instead of editing the release bundle by hand.

Validation:

```powershell
python -m p4_experiments.canonical.run_pipeline --dry-run
python -m p4_experiments.canonical.audits.audit_phase03
python -m p4_experiments.canonical.audits.audit_phase05
python -m p4_experiments.canonical.audits.audit_phase11
```

## Wave 4 - Core Library Rename

Goal: rename reusable implementation code from `common/` to `core/` for professional package semantics.

Completed move:

```text
common/*.py -> core/*.py [complete]
common/templates/ -> core/templates/ [complete]
common/schemas/ -> core/schemas/ [complete]
common/re_profiles/ -> core/resource_profiles/ [complete]
common/p4_shortlist* -> core/p4_shortlist* [complete]
common/output/ remains in place [guarded]
```

Final handoff state:

- Reusable implementation code lives under `p4_experiments.core.*`.
- `common/output/results/` and `common/output/classical_results/` remain as guarded raw evidence stores.
- The old `common/*.py`, `common/templates/`, `common/schemas/`, and `common/re_profiles/` compatibility layer has been removed.

Validation:

```powershell
python -m p4_experiments.canonical.run_pipeline --dry-run
python -m p4_experiments.canonical.audits.audit_phase08
python -m p4_experiments.canonical.audits.audit_phase09
```

## Wave 5 - Experiment Evidence Folders

Goal: move per-paper evidence out of the package root.

Completed moves:

```text
derivative_pricing/ -> experiments/silos/derivative_pricing/
portfolio_optimization/ -> experiments/silos/portfolio_optimization/
quantum_ml_finance/ -> experiments/silos/quantum_ml_finance/
simulation_monte_carlo/ -> experiments/silos/simulation_monte_carlo/
fraud_detection/ -> experiments/silos/fraud_detection/
credit_lending/ -> experiments/silos/credit_lending/
trading_execution/ -> experiments/silos/trading_execution/
risk_management/ -> experiments/silos/risk_management/
cryptography_security/ -> experiments/silos/cryptography_security/
cross_silo_other/ -> experiments/silos/other/
insurance_actuarial/ -> experiments/silos/insurance_actuarial/
_phase8_faithfulness_review/ -> experiments/review/phase8_faithfulness_review/
```

Required code updates:

- Circuit discovery/registry paths updated for `experiments/silos/`.
- Proxy justification writers/readers updated and Phase 4 hashes re-stamped through the canonical generator.
- `cohort.json`, `phase3_compare.json`, and Phase 8 result `source_path` values now point at the moved evidence paths.
- Old root silo imports remain compatible through package-level aliases in `p4_experiments/__init__.py`.

Current status: `experiments/silos/` and `experiments/review/` contain the authoritative evidence folders. Root silo folders and `_phase8_faithfulness_review/` have been removed from the active tree.

Validation:

```powershell
python -m p4_experiments.core.build_p4_shortlist
python -m p4_experiments.canonical.audits.audit_phase04
python -m p4_experiments.canonical.audits.audit_phase05
python -m p4_experiments.canonical.run_pipeline --dry-run
```

## Final Acceptance Gate

Run the full canonical audit ladder:

```powershell
$py = "c:/Users/t-vwallerich/OneDrive - Microsoft/Quantum/QF/.venv/Scripts/python.exe"
$audits = @("audit_phase03","audit_phase04","audit_phase05","audit_phase06","audit_phase07","audit_phase08","audit_phase08d","audit_phase08e","audit_phase09","audit_phase10","audit_phase11")
foreach ($audit in $audits) {
  Write-Host "`n=== $audit ==="
  & $py -m "p4_experiments.canonical.audits.$audit"
  if ($LASTEXITCODE -ne 0) { throw "$audit failed" }
}
```

Then update:

- `p4_experiments/README.md`
- `p4_experiments/canonical/README.md`
- `p4_experiments/canonical/REPRODUCE.md`
- `docs/PROJECT_STATE.yaml` after explicit approval
