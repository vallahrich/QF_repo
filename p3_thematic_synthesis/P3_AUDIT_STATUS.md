# P3 Audit Status

Status date: 2026-05-10. This file consolidates the older Q and QA audit items
from `AUDIT_REPORT.md`, the historical 2026-04-17 `FROZEN.md`, and the current
active S2/S3 state. It is the handoff status for work before manuscript rebuild.
Current claim boundaries are controlled by `FREEZE.md`; this file explains the
audit disposition behind those boundaries.

Status values:

- `closed-active`: implemented in the current active corpus or code path.
- `accepted-risk`: intentionally retained with a claim boundary.
- `deferred`: not blocking the current methodology thesis if disclosed.
- `open-blocker`: must be resolved before strong empirical claims.

## Quantitative Extraction Items

| ID | Item | Status | Evidence / Required action |
|---|---|---|---|
| Q-0 | Scope filter for annealing/QUBO papers | closed-active | `run_extraction.py` has scope-out methodology tags; `scripts/audit_scope.py` writes `output/audit/raw_scope_audit.json`; current audit reports 0 hard family/hardware scope violations. |
| Q-1 | Schema excludes annealing/QUBO/hardware annealers | closed-active | `config/benchmark_schema.json` allows only `gate_based` paper scope and excludes annealer hardware. |
| Q-2 | Prompt scope banners remove annealing target | accepted-risk | Active outputs are scope-clean; prompt files should still be reviewed before any LLM rerun. |
| Q-3 | Validator treats schema/range errors as failed validation | closed-active | Active metadata has 36 failed files and 465 passing files; failures are not marked passing. |
| Q-4 | Extraction temperature fixed at 0 | closed-active | `config/extraction_config.json` has `temperature: 0.0` and seed 42. |
| Q-5 | Classical-only solver deny-list / QBSolv handling | accepted-risk | Needs spot-check in extraction prompts before any new LLM extraction. |
| Q-6 | Stratified inter-variant reliability/kappa | deferred | Current A/B evidence remains insufficient for strong extraction-reliability claims. This is accepted as a disclosed limitation for the freeze: do not make strong extraction-reliability claims unless a future stratified n >= 30 reliability audit is run. |
| Q-7 | Provenance and aggregation bookkeeping | accepted-risk | Current extraction metadata carries validation fields; complete run metadata varies across files. |
| Q-8 | Legacy prompt/script cleanup | deferred | Remove or clearly archive legacy `extract_benchmarks.py` paths before release. |
| Q-9 | Duplicate experiment handling | closed-active | S3 loader suffixes duplicate experiment IDs with `__dupN` to preserve rows. |
| Q-10 | Document corpus exclusion lineage | closed-active | `shared/bridge/excluded_papers.csv` records the current 276 active exclusions; `s2_quantitative/output/audit/corpus_lineage.json` and `.md` explain 777 -> historical 643/459 -> current 501 files / 1046 experiments; `s2_quantitative/output/audit/excluded_papers_historical_2026-04-17.csv` preserves the 318-row historical 459-paper freeze exclusion set. |
| Q-11 | Self-identifying extraction metadata | accepted-risk | Active files include `extraction_metadata`; require a release audit before manuscript claims. |

## Quantum-Advantage Triangulation Items

| ID | Item | Status | Evidence / Required action |
|---|---|---|---|
| QA-0 | Loader guard against scope regressions | closed-active | `_shared/extraction_loader.py` now points to active S2 output, defaults to valid files, and skips annealing/QUBO/annealer rows. |
| QA-1 | Ronnow applicability gate | closed-active | Algorithm-family gate added 2026-05-02 in [`s3_quantum_advantage/ronnow/assess_ronnow.py:_assess_one`](s3_quantum_advantage/ronnow/assess_ronnow.py) (`_RONNOW_APPLICABLE_FAMILIES`); families outside `{qaoa, grover, amplitude-estimation, amplitude-amplification, quantum-annealing, qaoa-annealing}` and not flagged as `benchmark_validity_study` now return `not_applicable` rather than being scored. |
| QA-2 | Stilck Franca scope note | deferred | Keep as limitation unless NISQ claims are strengthened. |
| QA-3 | L4 routing documentation | accepted-risk | Fraud/cryptography coverage gaps must be disclosed in S3 methods. |
| QA-4 | Dalzell orphan thresholds | deferred | Clean threshold file before release if unused thresholds remain. |
| QA-5 | Dalzell portfolio blanket infeasible flag | closed-active | Algorithm-family gate added 2026-05-02 in [`s3_quantum_advantage/dalzell_2023/assess_dalzell.py`](s3_quantum_advantage/dalzell_2023/assess_dalzell.py) (lines ~121-153): the QIPM `is_infeasible` verdict is now scoped to QIPM-tagged experiments; non-QIPM portfolio papers return `not_applicable`. |
| QA-6 | Fixed classical parallelism assumptions | accepted-risk | Keep as framework-level assumption with sensitivity caveat. |
| QA-7 | Consensus arithmetic / schema checks | closed-active | Current filtered consensus summary is reconciled to 936 active rows; raw unfiltered summary remains 1046-row provenance. |
| QA-8 | Confidence-weighted consensus | deferred | Not needed for headline if current 4-core + 1-veto rule is presented as preregistered/scoped. |
| QA-9 | Explicit silo x family routing table | deferred | Useful for methods clarity; not required for current repair pass. |
| QA-10 | Stilck noise inference coverage | accepted-risk | Current NISQ veto coverage is limited; do not make strong NISQ-noise claims. |
| QA-11 | Beverland modelling depth | accepted-risk | Honest relabel applied 2026-05-02: `FRAMEWORK_ID` renamed to `"beverland_inspired_2022"` in [`s3_quantum_advantage/beverland_2022/assess_beverland.py`](s3_quantum_advantage/beverland_2022/assess_beverland.py); fidelity caveat in module docstring. Full Beverland modelling depth (logical-qubit / T-factory stack) deferred to any future re-run. |
| QA-12 | Output payload metadata | accepted-risk | Current outputs are usable, but release metadata should be restamped after reruns. |
| QA-13 | Robust JSON read failures | deferred | Useful hardening; not a current blocker. |
| QA-14 | Threshold indexing summary | deferred | Add to S3 methods docs before final submission. |
| QA-15 | Chakrabarti QAOA 2025 integration | deferred | Treat as forward-work unless QAOA pricing claims become central. |

## Immediate Rule

Any regenerated S3 assessor output should be produced from valid active S2 files
only. If invalid extraction files are included for sensitivity, that run must be
named and reported separately.