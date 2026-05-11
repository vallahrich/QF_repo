# P4 - Experiment Replication and Validation

P4 is organized around the S2-backed canonical pipeline in [canonical/](canonical/). The handoff surface is intentionally narrow: use the files below for current work, and treat historical planning material as provenance only.

> ⚠️ **Mixed historical / current content** (banner added 2026-05-02 freeze).
>
> The active 2026-05-02 hardening state uses explicit implementation tiers:
> **0 paper-faithful-strict / 13 paper-family-template / 58 proxy** in the
> active 71-label P3/S3-selected estimator cohort. Treat [FREEZE.md](FREEZE.md) and
> [canonical/PRE_REGISTRATION.md](canonical/PRE_REGISTRATION.md) as the
> controlling status documents for artifact claims.

## Current State

- Cohort: 71 S2-backed labels across 8 silos: 13 family/template labels and 58 proxy-declared labels; strict-tier estimator labels = 0.
- Canonical Phase 8 grid: 71 labels x 6 hardware profiles x 3 error budgets x 2 accounting modes = 2556 cells.
- Phase 8 status: 2519 OK records and 37 documented `engine_failure` records; no missing cells.
- Phase 9 status: H1-H4 statistics plus `canonical/reports/evidence_report.json` are audit-clean; generated report files are in the source archive.
- Phase 10 status: 27 manuscript artifacts, claim-evidence tables, figure CSVs, markdown briefs, and H figures are audit-clean.
- Headline result: no H4 canonical winners in the active family/template + proxy implementation cohort; no strict-tier H4 claim is supported by the current grid.
- Regime boundary: headline inference uses `canonical_s2_backed_label_grid`; `qae_hhl_fixed_precision_high_n` is appendix-only HHL/QAE scaling evidence.

## Main Documents

| Document | Purpose |
|---|---|
| [docs/README.md](docs/README.md) | Documentation index for the Phase 4 package |
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | Handoff architecture and folder responsibilities |
| [docs/MIGRATION_PLAN.md](docs/MIGRATION_PLAN.md) | Historical restructuring provenance; not an active task list |
| [canonical/README.md](canonical/README.md) | Current pipeline map, counts, artifacts, and regeneration order |
| [canonical/PRE_REGISTRATION.md](canonical/PRE_REGISTRATION.md) | Active canonical contract and reporting rules |
| [canonical/REPRODUCE.md](canonical/REPRODUCE.md) | Rebuild and audit commands |
| [canonical/THREATS_TO_VALIDITY.md](canonical/THREATS_TO_VALIDITY.md) | Current limitations and mitigations |
| [canonical/DECISIONS_LOG.md](canonical/DECISIONS_LOG.md) | Dated operator decisions |
| [core/p4_shortlist_summary.md](core/p4_shortlist_summary.md) | Historical shortlist precursor; not the current canonical cohort |

## Current Folders

| Folder | Role |
|---|---|
| [docs/](docs/) | Human-facing architecture and migration documentation |
| [canonical/](canonical/) | Active Phase 3-11 orchestrator, phase/audit/data namespaces, reports, outputs, and release artifacts |
| [common/](common/) | Guarded Phase 8 and Phase 8b/8c raw output stores |
| [core/](core/) | Authoritative shared implementation code, templates, schemas, resource profiles, and shortlist inputs |
| [experiments/](experiments/) | Authoritative per-paper circuit/instance evidence and review evidence |
| [infra/](infra/) | VM/Azure operations namespace, including historical Phase 8/8d setup, sync, monitor, and helper tooling |
| [experiments/review/phase8_faithfulness_review/](experiments/review/phase8_faithfulness_review/) | Vincent review worksheets, observations, and joint triage evidence |
| [experiments/silos/](experiments/silos/) | Per-paper circuits, instances, notes, and proxy justifications by silo |
| Historical root silo imports | Preserved by package aliases in [__init__.py](__init__.py); source folders live under [experiments/silos/](experiments/silos/) |

The current layout keeps one clear source of truth for each layer. Phase implementations live under [canonical/pipeline/](canonical/pipeline/), audit implementations under [canonical/audits/](canonical/audits/), and canonical helper data under [canonical/data/](canonical/data/). Reusable implementation code lives under [core/](core/), and per-paper evidence lives under [experiments/silos/](experiments/silos/). The handoff architecture is documented in [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md); [docs/MIGRATION_PLAN.md](docs/MIGRATION_PLAN.md) is retained only to explain how the current structure was reached.

Generated outputs that matter for the thesis are concentrated in the source archive, with the canonical release tarball retained in this hand-in tree:

- `common/output/results/` - the 2556 canonical Phase 8 result records.
- `common/output/classical_results/` - Phase 8b/8c classical baseline measurements.
- `canonical/reports/` - generated Phase 3/8/9 JSON reports and audit outputs.
- `canonical/outputs/manuscript_artifacts/` - Phase 10 tables, figure source CSVs, key numbers, result briefs, and discussion claim support.
- `canonical/outputs/phase08c_alternatives/` - Phase 8c top-3 classical alternatives.
- `canonical/outputs/phase08d_qae_hhl_scout/` - appendix-only HHL/QAE fixed-precision high-N scout.
- `canonical/outputs/phase08e_per_silo/` - Phase 8e per-silo synthesis cards.

[canonical/release/zenodo_bundle/](canonical/release/zenodo_bundle/) and the tarball next to it are generated Phase 11 release snapshots. Do not hand-edit bundle contents; rebuild Phase 11 when a final hash-stamped release package is needed.

## Pipeline Driver

The active orchestrator is [canonical/run_pipeline.py](canonical/run_pipeline.py). The default pipeline skips external Phase 8d VM compute unless `--include-phase8d` is supplied.

Operational VM setup and sync scripts under `infra/azure/` and generated scientific outputs under `canonical/outputs/` are in the source archive.

```powershell
python -m p4_experiments.canonical.run_pipeline --resume
python -m p4_experiments.canonical.run_pipeline --resume --include-phase8d
```

For documentation, tables, and figures after the current Phase 9/10 work, the source-of-truth files are `canonical/reports/evidence_report.json` and `canonical/outputs/manuscript_artifacts/key_numbers.json` in the source archive.
