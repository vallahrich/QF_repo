# Project Timeline

This document is a narrative summary of the project's research and packaging timeline. Every event below is taken from artifacts that already exist in this repository: freeze records, `docs/PROJECT_STATE.yaml`, the SLR amendments log, phase reports under `docs/`, dated snapshot folders, and the Phase 4 pre-registration. No log file, JSONL call record, manifest, snapshot folder name, or commit was modified to produce this document.

Generated: 2026-05-09. Refreshed: 2026-05-10. Source of truth for live phase status is the repository freeze set ([../FREEZE.md](../FREEZE.md) and per-folder `FREEZE.md` files) plus the compact status/contracts in [PROJECT_STATE.yaml](PROJECT_STATE.yaml).

---

## At a glance

| Window | Phase | Key milestone | Source artifact |
|---|---|---|---|
| 2026-03-09 → 2026-03-30 | SLR protocol & search | 12 protocol amendments (A1–A12); search and screening pipeline finalised on `gpt-5-mini` | [p2_systematic_review/s1_slr/01_protocol/amendments_log.csv](../p2_systematic_review/s1_slr/01_protocol/amendments_log.csv) |
| → 2026-04-11 | Phase 1 — Framework synthesis | Scoping/framework taxonomy frozen: downstream 8 active PD silos × 11 SA codes | [p1_framework_synthesis/FREEZE.md](../p1_framework_synthesis/FREEZE.md), [p1_framework_synthesis/audit-trail.md](../p1_framework_synthesis/audit-trail.md), [shared/config/unified_taxonomy.json](../shared/config/unified_taxonomy.json) |
| → 2026-04-14 | Phase 2 — SLR & classification | 6,232 → 3,010 → 875 → 777 papers; active downstream subset 755 after 22 retro-exclusions | [p2_systematic_review/FREEZE.md](../p2_systematic_review/FREEZE.md), [p2_systematic_review/output/processed/](../p2_systematic_review/output/processed/) |
| 2026-04-17 | Phase 3 — first freeze | Quantitative corpus and triangulation layer frozen for Phase 4 consumption | p3_thematic_synthesis/s2_quantitative/output/extractions_preQ0_20260417_095811/ (moved to source archive) |
| 2026-04-19 | Phase 3 — restructure | 7-step thematic process with 5 safeguard layers; 8 active silos; PD-10 merged into PD-03; PD-08 excluded | `PROJECT_STATE.yaml` decisions log |
| 2026-04-22 | Phase 3 — pilot | A1 prompt v2 production rerun; pre-rerun snapshot retained | p3_thematic_synthesis/s2_quantitative/output/extractions_pre_5.3_20260422_095328/ (moved to source archive) |
| 2026-04-26 | Phase 3 — finance framing | s6 sub-pipeline added (629/657 papers, 8/8 silos) | [p3_thematic_synthesis/s6_silo_framing/](../p3_thematic_synthesis/s6_silo_framing/) |
| 2026-04-26 | Phase 4 — canonical architecture | core/ + experiments/ + canonical/{reports,outputs,release}/ boundaries finalised | [p4_experiments/docs/ARCHITECTURE.md](../p4_experiments/docs/ARCHITECTURE.md) |
| 2026-04-28 | Phase 4 — interim revision | Phase 8d HHL tail outputs superseded; pre-revision snapshot retained | p4_experiments/canonical/outputs/phase08d_hhl_tail_exploratory/archive_superseded_20260428/ (moved to source archive) |
| 2026-05-02 | Phase 3 — active baseline freeze | Filtered active-silo triangulation outputs frozen; pre-remediation snapshot retained | p3_thematic_synthesis/s3_quantum_advantage/combined/output/_pre_remediation_snapshot_2026-05-02/ (moved to source archive) |
| 2026-05-04 | Manuscript — Chapter 6 | Ship-ready: 8 silos + intro + cross-silo, ~18k words, 306 cites | Thesis manuscript source outside this clean repository |
| 2026-05-06 | Manuscript — full build | Clean latexmk + biber + pdflatex; 0 undefined citations | `PROJECT_STATE.yaml` `manuscript.last_full_build` |
| 2026-05-09 | Cleanup/submission Phases 1–6 | Detached cleanup copy validated; two derivative packages produced; IP and handoff curation completed | PHASE1_CLEANUP_REPORT.md ... PHASE6_PACKAGE_IP_COMPLIANCE_REPORT.md (moved to source archive) |

---

## March 2026 — SLR protocol design and search

The SLR protocol went through 12 numbered amendments (A1–A12) recorded in [amendments_log.csv](../p2_systematic_review/s1_slr/01_protocol/amendments_log.csv):

- **2026-03-09 (v1.2 → v2.0)**: Assessment-driven structural revisions: 7th source added (Semantic Scholar), AIS eLibrary removed; Cohen's κ ≥ 0.70 introduced; English-only restriction; 20-field Hoefler extraction codebook; GRADE-adapted certainty-of-evidence framework; OSF registration status recorded as pending.
- **2026-03-09 (v1.3, A2)**: Search strategy adjustments; OpenAlex switched to title/abstract search; tightened Scopus query template.
- **2026-03-10 (A4 → v3.0)**: Screening design changed from single-reviewer with mitigations to two-reviewer calibrate-then-split (50-record calibration round, κ ≥ 0.70 target). Major restructuring positioned the SLR as Phase 1a within an exploratory sequential mixed-methods design (Creswell & Creswell, 2018).
- **2026-03-10 (A5)**: Block 1/Block 2 query refinement to reduce noise; old runs deprecated by `slr_toolkit`.
- **2026-03-13 (A6, A7)**: Block 1/Block 2 expansion; benchmark validation set extended from 10 to 20 known-relevant papers.
- **2026-03-13 (A8 → A9)**: AI-assisted screening layer added (Cochrane/Campbell/JBI/CEE 2025 position); first attempt with ASReview failed to discriminate; switched to LLM-based classification via Azure OpenAI.
- **2026-03-15 (A10)**: LLM screening model trial: gpt-4.1-mini → DeepSeek-V3.2 (failed) → o4-mini → settled on gpt-5-mini.
- **2026-03-17 (A11)**: Production AI-screening run; protocol and counts reconciled to active artifacts: 6,232 ingested → 3,222 duplicates removed → 3,010 unique screened (651 AI-include, 2,359 AI-exclude).
- **2026-03-30 (A12)**: AI-vs-human discrepancy resolution; full merge-screening of 3,142 decisions; 875 unique papers included; AI validation recall = 1.0000 PASS.

Deprecation events for raw exports (run folders matching `2026-03-08`, `2026-03-09`, `2026-03-10-v2`, `2026-03-10-v3`, `2026-03-13-v4`) are recorded by the toolkit in the same file. They are part of the iterative protocol record, not hidden.

## Phase 1 — Framework synthesis (complete 2026-04-11)

- Scoping/framework synthesis of the exploratory literature, with LLM-assisted extraction and researcher-curated normalization. The final freeze explicitly does not claim completion of a strict Elo/Kyngas inductive content-analysis protocol.
- Outputs: conceptual framework (10 PD × 11 SA codes with mapping matrix), classification codebook, audit trail (4 entries documenting LLM proposal vs researcher decision divergences).
- Boundary decisions documented in the Phase 1 freeze/audit trail: PD-10 was later retracted/merged into PD-03, PD-08 is excluded from active Phase 3/P4 scope, and PD-11 forecasting-prediction is registered as merged into PD-04.
- Design principle: LLM as analytical assistant, not analytical authority — researcher retains epistemic authority on every code.
- Source: [p1_framework_synthesis/audit-trail.md](../p1_framework_synthesis/audit-trail.md), [p1_framework_synthesis/s4_outputs/](../p1_framework_synthesis/s4_outputs/).

## Phase 2 — Systematic review and classification (complete 2026-04-14)

- 777 papers processed through the 6-step LLM extraction pipeline using gpt-5-mini on Azure.
- Active downstream subset is 755 after 22 post-hoc false positives were retro-excluded as off-scope.
- Outputs: structured Markdown per paper with frontmatter `topic_tags` and `methodology_tags`, PRISMA flow diagram, and audit records. The earlier root Phase 2 `processing_log.json` test artifact has been removed; the current evidence boundary is the gpt-5-mini processed output plus frozen audit and screening artifacts.
- Source: [p2_systematic_review/output/processed/](../p2_systematic_review/output/processed/). PRISMA flow diagram and other SLR figures are reproducible via [p2_systematic_review/s1_slr/generate_figures.py](../p2_systematic_review/s1_slr/generate_figures.py) and [p2_systematic_review/s1_slr/generate_workflow_figure.py](../p2_systematic_review/s1_slr/generate_workflow_figure.py); the rendered PDF/PNG variants live in the manuscript and are not duplicated in this hand-in tree.

## Phase 3 — Thematic synthesis (frozen as scoped; key milestones April-May 2026)

The thematic-synthesis pipeline went through three documented restructurings. Each iteration kept the prior state on disk as a dated snapshot folder so the evolution is auditable:

- **2026-04-17 — first freeze (`extractions_preQ0_20260417_095811/`)**: P3 quantitative corpus and triangulation layer frozen for P4 consumption. Frozen baseline: 501 S2 files / 1046 experiments. Source: `PROJECT_STATE.yaml` decisions log entry 2026-04-17.
- **2026-04-19 — restructuring decision**: Reconciled two divergent design sessions; adopted the 7-step thematic process (A1 → L1 → A2 → L2 → L3 → A3 → R1 within paper; B1 → B2 → R2 within silo; C1 → C2 → C3 across silos) with the 5-layer safeguard architecture (L0 prevention → L1 quote verification → L2 closed-world claim tracing → L3 adversarial error-finding → L4 stratified human audit). PD-10 merged into PD-03; PD-08 excluded; 8 active silos. Source: `PROJECT_STATE.yaml`.
- **2026-04-22 — pilot/A1 v2 rerun (`extractions_pre_5.3_20260422_095328/`)**: A1 prompt v2 production run; pre-rerun snapshot retained. Production config: A1=gpt-5.4-mini+v2, A2/L3=gpt-5.1 hybrid. 661 papers (3 excluded for corrupted extraction); ~2,631 API calls.
- **2026-04-26 — finance framing sub-pipeline added**: s6_silo_framing as a descriptive sibling pipeline to s4 (not downstream). Two stages: F1 per-paper extraction (gpt-5.4-mini, temperature 0.1) with verbatim-quote substring verification; F2 per-silo aggregation (gpt-5.1) with paper-id verification. Coverage: 629/657 F1-accepted (95.7%); 28 residual failures (4 API errors + 24 parse failures). 8/8 silos completed.
- **2026-05-02 — active baseline freeze (`_pre_remediation_snapshot_2026-05-02/`)**: Quantum-advantage triangulation re-frozen with filtered active-silo outputs as the live baseline; the raw 1046-row outputs are retained for provenance/sensitivity. The P3-to-P4 contract is now FROZEN at this baseline.
- **Current freeze boundary**: active S2 corpus is 501 files / 1046 experiments; filtered S3 active-silo matrix is 936 rows with 46 disagreement cases; s4 is complete as scoped with 95 descriptive and 45 analytical themes; s6 is descriptive finance framing, not independent semantic validation.

**P3 process contract:** the design-time within-paper order is **A1 -> L1 -> A2 -> L2 -> L3 -> A3 -> R1**. In the frozen submission state, A1/L1/A2/L2 and the in-freeze L3 audit sample were executed before thematic synthesis; A3 was retained as a prompt but deferred/not executed; the later full-coverage L3 aggregation/propagation pass and R1 review were GL-10 post-freeze validation closures. Do not cite historical working checklists as evidence that R1 preceded an executed A3 inside the 2026-05-02 freeze.

The L3 archive `s4_thematic_coding/papers_l3_v2_gpt51_archive/` records the pre-v2 L3 (adversarial error-finding layer) outputs preserved when the L3 prompt was upgraded to the gpt-5.1 hybrid configuration.

## Phase 4 — Experiment replication and validation (canonical audit clean)

- Toolchain: Qiskit 2.3.0, QDK/qsharp 1.27.0, Azure Quantum Resource Estimator, Python 3.13.13 local venv.
- Cohort: 71 canonical labels selected from the P3/S3 most-viable quantum-advantage layer (paper-faithful strict = 0; family/template = 13; proxy-declared = 58).
- Phase 8 grid: 2,556 expected cells; 2,519 OK records; 37 engine failures; 0 missing.
- **2026-04-26 — canonical architecture finalised**: core/, experiments/, canonical/{reports,outputs,release}/ boundaries set. Source: [p4_experiments/docs/ARCHITECTURE.md](../p4_experiments/docs/ARCHITECTURE.md).
- **2026-04-28 — Phase 8d revision (`archive_superseded_20260428/`)**: HHL tail exploratory outputs superseded; pre-revision snapshot retained for provenance.
- **Phase 11 release bundle**: `zenodo_bundle.tar.gz` SHA-256 = `3944d4b27e7df90c137e0a7f0a1b029086bc8d2c7307d334fab99efc75e50b77`. Sidecar `.sha256` is the authoritative integrity reference.
- Source: [p4_experiments/canonical/PRE_REGISTRATION.md](../p4_experiments/canonical/PRE_REGISTRATION.md), p4_experiments/canonical/reports/ (moved to source archive), [p4_experiments/canonical/release/](../p4_experiments/canonical/release/).

## Manuscript — May 2026

- **2026-05-04 — Chapter 6 ship-ready**: 8 silo chapters + intro + cross-silo, ~18k words, 306 cites, 45 AT-codes with C2 grounding verdicts. Three commit checkpoints: phase B silo polish (`e3f56f40`), phase C chapter conformance (`c274c7e5`), phase D governance sweep (`0d9d15dc`).
- **2026-05-06 — full clean build**: latexmk + biber + pdflatex pass; 0 undefined citations; PDF size 745 KB; body word count ≈ 42,200. Related Work rewritten to dimension-led structure (Option-beta, 6 sections).
- Outstanding chapter: Chapter 9 Conclusion (~3 pp).

## Cleanup/submission Phases 1–6 — 2026-05-09

These phases are *cleanup* phases on a detached copy at `C:\Users\t-vwallerich\OneDrive - Microsoft\Quantum\QF_repo`. They are distinct from the thesis research Phase 4 in `p4_experiments/`.

- **Phase 1 — Cleanup**: reviewer orientation documents created; secret scan run; validation passed (pytest 800/22 skipped, verify.ps1 PASS, taxonomy V2 0 fail / 0 warn). Source: PHASE1_CLEANUP_REPORT.md (moved to source archive).
- **Phase 2 — Packaging design**: package profiles, PDF handling rules, P4 manifest-drift and release-bundle decision records, packaging manifest, reviewer checklist. Source: PHASE2_PACKAGING_REPORT.md (moved to source archive).
- **Phase 3 — Final submission state**: restored 42 cohort S2 files (line-ending-only drift) from the writing repo; re-extracted Phase 11 expanded bundle from the authoritative tarball; `audit_phase11` now 7 PASS / 0 FAIL. Source: PHASE3_FINAL_SUBMISSION_REPORT.md (moved to source archive).
- **Phase 4 — Derived packages**: two derivative packages produced (examiner reproducibility copy + public/archive copy) under `C:\QF_submission_packages\`; 850 source-paper PDFs excluded per package; package validation passed. Source: PHASE4_DERIVED_PACKAGE_REPORT.md (moved to source archive).
- **Phase 5 — Final handoff**: parallel-hashed 20,708 manifest files per package; tarball integrity confirmed via `.sha256` sidecar; hygiene checks passed. Source: PHASE5_FINAL_HANDOFF_REPORT.md (moved to source archive).
- **Phase 6 — IP compliance and handoff curation**: removed verbatim full-text Markdown from `shared/extracted_text/text/` (789 files per package) per the thesis IP statement; subsequent handoff curation removed an additional 4,838 files per package across four classes (non-final archives/snapshots, raw LLM I/O, operational monitor logs, internal package-generation prompt files); final manifest entries 15,083 per package; final verifier PASS, no forbidden paths, no precise secret-token hits. Source: PHASE6_PACKAGE_IP_COMPLIANCE_REPORT.md (moved to source archive).

---

## How iteration is recorded on disk

Real research iterates. This project records iteration explicitly on disk so the trail is auditable rather than rewritten:

| Snapshot/archive folder | What it preserves | When it was created |
|---|---|---|
| p3_thematic_synthesis/s2_quantitative/output/extractions_preQ0_20260417_095811/ (moved to source archive) | Pre-freeze quantitative extractions (P3 first freeze) | 2026-04-17 |
| p3_thematic_synthesis/s2_quantitative/output/extractions_pre_5.3_20260422_095328/ (moved to source archive) | Pre-A1-v2 extractions | 2026-04-22 |
| p3_thematic_synthesis/s4_thematic_coding/papers_l3_v2_gpt51_archive/ (moved to source archive) | Pre-upgrade L3 outputs | (P3 v2 upgrade window) |
| p3_thematic_synthesis/s3_quantum_advantage/combined/output/_pre_remediation_snapshot_2026-05-02/ (moved to source archive) | Pre-remediation triangulation snapshot | 2026-05-02 |
| p4_experiments/canonical/outputs/phase08d_hhl_tail_exploratory/archive_superseded_20260428/ (moved to source archive) | Superseded Phase 8d HHL tail outputs | 2026-04-28 |
| p4_experiments/infra/azure/phase8_4vm_legacy_bootstrap/ (moved to source archive) | Legacy 4-VM Azure bootstrap (superseded by 6-VM run) | (P4 infra revision window) |

These folders are intentionally retained in the source/internal copy as audit evidence. They are excluded from the two derivative submission packages because the packages are reviewer-facing handoffs, not the audit copy. The exclusion is recorded in `EXCLUDED_FILES_MANIFEST.csv` in each package and explained in PHASE6_PACKAGE_IP_COMPLIANCE_REPORT.md (moved to source archive).

---

## Document policy

- This timeline is a derived narrative document. The authoritative live status is the freeze set plus [PROJECT_STATE.yaml](PROJECT_STATE.yaml). When a timeline sentence diverges from a phase `FREEZE.md`, the phase freeze wins.
- Dates in this document are taken from existing artifacts. They are not inferred or back-formed.
- This document is generated by hand as part of the cleanup/submission Phase 6 work and should be regenerated, not edited in place, if the underlying artifact dates change.
