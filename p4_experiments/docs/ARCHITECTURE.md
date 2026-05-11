# Phase 4 Architecture

Phase 4 is the empirical validation package for the thesis. Its architecture should make it obvious which files are executable code, canonical data, generated outputs, audit evidence, release artifacts, and per-paper experiment evidence.

## Architectural Principles

1. Keep the canonical evidence chain intact: P3 frozen inputs -> P4 cohort -> resource-estimation records -> statistics -> manuscript artifacts -> release bundle.
2. Separate source code from generated outputs.
3. Separate canonical headline evidence from appendix-only exploratory/scaling evidence.
4. Keep pre-registration, audit, and release artifacts traceable from stable paths.
5. Keep one obvious source-of-truth namespace for each layer.

## Current Handoff Layout

The current active layout has the major source and evidence moves completed: VM-backed Phase 8d reruns are finalized, generated outputs are separated from source code, authoritative phase/audit implementations live under structured namespaces, reusable code lives under `core/`, and per-paper evidence lives under `experiments/`.

```text
p4_experiments/
  README.md
  docs/
    README.md
    ARCHITECTURE.md
    MIGRATION_PLAN.md
  canonical/
    README.md
    PRE_REGISTRATION.md
    REPRODUCE.md
    THREATS_TO_VALIDITY.md
    DECISIONS_LOG.md
    run_pipeline.py
    pipeline/
    audits/
    data/
    reports/
      audit/
    cohort.json
    outputs/
      manuscript_artifacts/
      phase08c_alternatives/
      phase08d_qae_hhl_scout/
      phase08e_per_silo/
    release/
      zenodo_bundle/
  common/
    output/
  core/
    qdk_bridge.py
    run_unit.py
    phase8_run_cell.py
    oracle_accounting.py
    circuit_registry.py
    build_p4_shortlist.py
    templates/
    schemas/
    resource_profiles/
  experiments/
    silos/
    review/
  infra/
    azure/
      phase8_6vm_20260425/
      phase8_4vm_legacy_bootstrap/
  prompts/
```

This layout is operationally stable and avoids duplicate canonical entry points. Generated Phase 3/8/9 JSON reports and audit outputs now live under `canonical/reports/`, generated Phase 10 tables and figures live under `canonical/outputs/`, finalized appendix-only Phase 8d data lives under `canonical/outputs/phase08d_qae_hhl_scout/`, VM/Azure setup and sync material lives under `infra/azure/`, executable phase/audit implementations live under `canonical/pipeline/` and `canonical/audits/`, reusable implementation code lives under `core/`, and per-paper evidence lives under `experiments/silos/`. The highest-risk paths are still handled conservatively:

- `canonical/PRE_REGISTRATION.md`: referenced by `cohort.json` and `audits/audit_phase03.py`.
- `common/output/results/`: canonical Phase 8 raw record store.
- `canonical/release/zenodo_bundle*`: generated Phase 11 release snapshot.

## Target Submission Layout

The target architecture after migration is:

```text
p4_experiments/
  README.md
  docs/
    README.md
    ARCHITECTURE.md
    MIGRATION_PLAN.md
    PRE_REGISTRATION.md
    REPRODUCE.md
    THREATS_TO_VALIDITY.md
    DECISIONS_LOG.md
    MANUAL_CITATION_BACKLOG.md

  core/
    __init__.py
    qdk_bridge.py
    run_unit.py
    phase8_run_cell.py
    oracle_accounting.py
    circuit_registry.py
    build_p4_shortlist.py
    templates/
    schemas/
    resource_profiles/

  experiments/
    README.md
    silos/
      derivative_pricing/
      portfolio_optimization/
      quantum_ml_finance/
      simulation_monte_carlo/
      fraud_detection/
      credit_lending/
      trading_execution/
      risk_management/
      cryptography_security/
      other/
    review/
      phase8_faithfulness_review/

  canonical/
    README.md
    run_pipeline.py
    pipeline/
    audits/
    data/
    reports/
    outputs/
    release/

  prompts/
  infra/
```

## Target Folder Semantics

| Folder | Responsibility |
|---|---|
| `docs/` | Human-facing research, reproducibility, architecture, and decision documentation |
| `core/` | Reusable Phase 4 implementation code, shared templates, schemas, and resource profiles |
| `experiments/silos/` | Per-paper circuit implementations, instances, and proxy justifications |
| `experiments/review/` | Researcher review worksheets and adjudication evidence |
| `canonical/pipeline/` | Canonical executable phase scripts |
| `canonical/audits/` | Audit scripts only |
| `canonical/data/` | Checked canonical input state such as `cohort.json` |
| `canonical/reports/` | Generated JSON reports and audit outputs |
| `canonical/outputs/` | Generated scientific outputs, figures, tables, and result layers |
| `canonical/release/` | Hash-stamped Zenodo bundle and release sidecars |
| `infra/` | Azure/VM operational scripts, setup manifests, sync tools, monitor logs, and helper orchestration |

## Direct Execution Rule

Use `python -m p4_experiments.canonical.run_pipeline` for orchestrated rebuilds. For targeted runs, execute modules from the structured namespaces directly: `p4_experiments.canonical.pipeline.*` for phases and `p4_experiments.canonical.audits.*` for audits. The canonical flat wrapper layer has been removed so readers see a single implementation location.

## Submission Standard

A reader should be able to answer these questions from the directory tree alone:

1. Where is the pre-registered empirical contract?
2. Where are the raw resource-estimation records?
3. Where are the statistics and manuscript-ready tables?
4. Where are the scripts that generated them?
5. Where is the release bundle and manifest?
6. Which evidence is headline canonical evidence and which evidence is appendix-only?
