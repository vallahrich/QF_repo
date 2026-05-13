# Project Timeline

This document is a narrative summary of the project's research timeline. Every event is taken from artifacts in this repository: per-phase `FREEZE.md` records, `docs/PROJECT_STATE.yaml`, the SLR amendments log, and the Phase 4 pre-registration. When a sentence here diverges from a phase `FREEZE.md`, the phase freeze wins.

---

## At a glance

| Window | Phase | Key milestone | Source artifact |
|---|---|---|---|
| 2026-03-09 → 2026-03-30 | SLR protocol & search | 12 protocol amendments (A1–A12); search and screening pipeline finalised on `gpt-5-mini` | [p2_systematic_review/s1_slr/01_protocol/amendments_log.csv](../p2_systematic_review/s1_slr/01_protocol/amendments_log.csv) |
| → 2026-04-11 | Phase 1 — Framework synthesis | Scoping/framework taxonomy frozen: downstream 8 active PD silos × 11 SA codes | [p1_framework_synthesis/FREEZE.md](../p1_framework_synthesis/FREEZE.md), [p1_framework_synthesis/audit-trail.md](../p1_framework_synthesis/audit-trail.md), [shared/config/unified_taxonomy.json](../shared/config/unified_taxonomy.json) |
| → 2026-04-14 | Phase 2 — SLR & classification | 6,232 → 3,010 → 875 → 777 papers; active downstream subset 755 after 22 retro-exclusions | [p2_systematic_review/FREEZE.md](../p2_systematic_review/FREEZE.md), [p2_systematic_review/output/processed/](../p2_systematic_review/output/processed/) |
| 2026-04-17 | Phase 3 — first freeze (superseded) | 459-paper s2 quantitative corpus and triangulation layer frozen for Phase 4 consumption; superseded by the 2026-04-22 A1-v2 rerun | `PROJECT_STATE.yaml` decisions log; [corpus_lineage.json](../p3_thematic_synthesis/s2_quantitative/output/audit/corpus_lineage.json) checkpoint `s3_freeze_2026_04_17_historical` |
| 2026-04-19 | Phase 3 — restructure | 7-step thematic process with 5 safeguard layers; 8 active silos; PD-10 merged into PD-03; PD-08 excluded | `PROJECT_STATE.yaml` decisions log |
| 2026-04-22 | Phase 3 — A1 v2 production rerun | A1 prompt v2 production rerun produced the active 501-file / 1,046-experiment s2 corpus (`run_timestamp` 07:57Z → 10:58Z); s4 campaign launched same day 15:07Z | [p3_thematic_synthesis/s4_thematic_coding/campaign_manifest.json](../p3_thematic_synthesis/s4_thematic_coding/campaign_manifest.json), per-file `extraction_metadata.run_timestamp` in [s2_quantitative/output/extractions/](../p3_thematic_synthesis/s2_quantitative/output/extractions/) |
| 2026-04-22 | Phase 3 — L3 full coverage aggregated | L3 adversarial check at 654/654 = 100% coverage; aggregation written 18:58Z to `L3_SUMMARY.md` + `output/l3_summary.json` | [p3_thematic_synthesis/s4_thematic_coding/L3_SUMMARY.md](../p3_thematic_synthesis/s4_thematic_coding/L3_SUMMARY.md), [p3_thematic_synthesis/s4_thematic_coding/output/l3_summary.json](../p3_thematic_synthesis/s4_thematic_coding/output/l3_summary.json) |
| 2026-04-23 → 2026-04-25 | Phase 3 — R1 stratified review | 153/1,291 = 11.85% per-paper coverage across 8 silos in 3 working windows per day (+02:00); per-silo `_disposition.json` + aggregate `r1_review_summary.json` | per-silo [`s4_thematic_coding/<silo>/reviewed/r1_review.jsonl`](../p3_thematic_synthesis/s4_thematic_coding/), [r1_review_summary.json](../p3_thematic_synthesis/s4_thematic_coding/r1_review_summary.json) |
| 2026-04-26 | Phase 3 — B1/B2/c2 themes | B1 batched themes 09:00–10:00 UTC + B2 silo themes 10:00–11:00 UTC + c2 grounding-check meta 11:00–11:30 UTC across 8 silos | per-silo [`s4_thematic_coding/<silo>/themes/`](../p3_thematic_synthesis/s4_thematic_coding/) |
| 2026-04-26 | Phase 3 — finance framing | s6 sub-pipeline added (629/657 papers, 8/8 silos); first call 13:01Z | [p3_thematic_synthesis/s6_silo_framing/](../p3_thematic_synthesis/s6_silo_framing/) |
| 2026-04-26 | Phase 4 — canonical architecture | core/ + experiments/ + canonical/{reports,outputs,release}/ boundaries finalised | [p4_experiments/docs/ARCHITECTURE.md](../p4_experiments/docs/ARCHITECTURE.md) |
| 2026-05-02 | Phase 3 — active baseline freeze | Filtered active-silo triangulation outputs frozen as the live baseline | [p3_thematic_synthesis/s3_quantum_advantage/combined/output/](../p3_thematic_synthesis/s3_quantum_advantage/combined/output/) |
| 2026-05-12 | Phase 4 — cosmetic figure regeneration | Re-rendered `h_figures_sidecar.json` (07 figures) and `p4_hoefler_crossover.json` (3 figures) for visual tweaks; data, source inputs, and numerical claims unchanged | [p4_experiments/canonical/DECISIONS_LOG.md](../p4_experiments/canonical/DECISIONS_LOG.md) 2026-05-12 entry; [`figures/h_figures_sidecar.json`](../p4_experiments/canonical/outputs/figures/h_figures_sidecar.json), [`figures/p4_hoefler_crossover.json`](../p4_experiments/canonical/outputs/figures/p4_hoefler_crossover.json) |

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

## Phase 1 — Framework synthesis (complete 2026-04-11)

- Scoping/framework synthesis of the exploratory literature, with LLM-assisted extraction and researcher-curated normalization.
- Outputs: conceptual framework (10 PD × 11 SA codes with mapping matrix), classification codebook, audit trail (4 entries documenting LLM proposal vs researcher decision divergences).
- Boundary decisions documented in the Phase 1 freeze/audit trail: PD-10 was later retracted/merged into PD-03, PD-08 is excluded from active Phase 3/P4 scope, and PD-11 forecasting-prediction is registered as merged into PD-04.
- Design principle: LLM as analytical assistant, not analytical authority — researcher retains epistemic authority on every code.
- Source: [p1_framework_synthesis/audit-trail.md](../p1_framework_synthesis/audit-trail.md), [p1_framework_synthesis/s4_outputs/](../p1_framework_synthesis/s4_outputs/).

## Phase 2 — Systematic review and classification (complete 2026-04-14)

- 777 papers processed through the 6-step LLM extraction pipeline using gpt-5-mini on Azure.
- Active downstream subset is 755 after 22 post-hoc false positives were retro-excluded as off-scope.
- Outputs: structured Markdown per paper with frontmatter `topic_tags` and `methodology_tags`, PRISMA flow diagram, and audit records.
- Source: [p2_systematic_review/output/processed/](../p2_systematic_review/output/processed/). PRISMA flow diagram and other SLR figures are reproducible via [p2_systematic_review/s1_slr/generate_figures.py](../p2_systematic_review/s1_slr/generate_figures.py) and [p2_systematic_review/s1_slr/generate_workflow_figure.py](../p2_systematic_review/s1_slr/generate_workflow_figure.py).

## Phase 3 — Thematic synthesis (frozen as scoped; key milestones April-May 2026)

The thematic-synthesis pipeline went through three documented restructurings:

- **2026-04-17 — first freeze (superseded)**: P3 quantitative corpus and triangulation layer frozen for P4 consumption. Frozen baseline at this point: **459 S2 files / 1,185 experiments** (per [corpus_lineage.json](../p3_thematic_synthesis/s2_quantitative/output/audit/corpus_lineage.json) checkpoint `s3_freeze_2026_04_17_historical`). This freeze was superseded by the 2026-04-22 A1 v2 rerun. Source: `PROJECT_STATE.yaml` decisions log entry 2026-04-17.
- **2026-04-19 — restructuring decision**: Reconciled two divergent design sessions; adopted the 7-step thematic process (A1 → L1 → A2 → L2 → L3 → A3 → R1 within paper; B1 → B2 → R2 within silo; C1 → C2 → C3 across silos) with the 5-layer safeguard architecture (L0 prevention → L1 quote verification → L2 closed-world claim tracing → L3 adversarial error-finding → L4 stratified human audit). PD-10 merged into PD-03; PD-08 excluded; 8 active silos. Source: `PROJECT_STATE.yaml`.
- **2026-04-22 — A1 v2 production rerun (active s2 corpus) + L3 full coverage**: A1 prompt v2 production run produced the **active 501 S2 files / 1,046 experiments** that are the current baseline. Per-file `extraction_metadata.run_timestamp` spans 2026-04-22T07:57:17Z → 10:58:26Z. s4 thematic coding launched the same day (campaign_manifest 2026-04-22T15:07:43Z). Production config: A1=gpt-5.4-mini+v2, A2/L3=gpt-5.1 hybrid initially. 661 papers in scope (3 excluded for corrupted extraction); ~2,631 API calls. **L3 sample (108/654 = 16.5%, gpt-5.1, prompt v2)** completed 17:00 +02:00 and a 17:30 free-text spot-check (~15 papers) approved proceeding to **L3 full coverage** (gpt-5.4-mini, prompt v3) which was aggregated 18:58Z to [`s4_thematic_coding/L3_SUMMARY.md`](../p3_thematic_synthesis/s4_thematic_coding/L3_SUMMARY.md) + [`output/l3_summary.json`](../p3_thematic_synthesis/s4_thematic_coding/output/l3_summary.json). 654/654 coverage; 642 papers (98.2%) flagged with at least one problem; 2,949 total problems.
- **2026-04-23 → 2026-04-25 — R1 stratified review (in-freeze)**: 153/1,291 = 11.85% per-paper coverage across 8 silos in three working windows per day (+02:00). Day 1 Thu 2026-04-23: credit_lending (11) / derivative_pricing (18) / fraud_detection (13). Day 2 Fri 2026-04-24: portfolio_optimization (25) / risk_management (23). Day 3 Sat 2026-04-25: quantum_ml_finance (31) / simulation_monte_carlo (24) / trading_execution (8). Verdicts: approved 69 / approved_with_caveat 81 / requires_revision 2 / flag_for_pull 1. Per-silo `_disposition.json` + aggregate `r1_review_summary.json` written 2026-04-25T23:30 → 2026-04-26T00:30 +02:00.
- **2026-04-26 morning — B1/B2/c2 theme generation**: B1 batched themes (`b1_batch_01.json` per silo) 09:00–10:00 UTC, B2 silo themes (`b2_silo_themes.json` per silo) 10:00–11:00 UTC, c2 grounding-check meta 11:00–11:30 UTC. 8 silos in alphabetical order. C3 cross-silo crosswalk meta is downstream and was generated 2026-05-04 after manuscript Chapter 6 ship-ready.
- **2026-04-26 afternoon — finance framing sub-pipeline added**: s6_silo_framing as a descriptive sibling pipeline to s4 (not downstream). First call 2026-04-26T13:01Z. Two stages: F1 per-paper extraction (gpt-5.4-mini, temperature 0.1) with verbatim-quote substring verification; F2 per-silo aggregation (gpt-5.1) with paper-id verification. Coverage: 629/657 F1-accepted (95.7%); 28 residual failures (4 API errors + 24 parse failures). 8/8 silos completed.
- **2026-05-02 — active baseline freeze**: Quantum-advantage triangulation re-frozen with filtered active-silo outputs as the live baseline. The P3-to-P4 contract is now FROZEN at this baseline.
- **Current freeze boundary**: active S2 corpus is 501 files / 1046 experiments; filtered S3 active-silo matrix is 936 rows with 46 disagreement cases; s4 is complete as scoped with 95 descriptive and 45 analytical themes; s6 is descriptive finance framing, not independent semantic validation.

**P3 process contract:** the design-time within-paper order is **A1/A2 → L3 → R1 → B1/B2**. In the frozen state, this order is honoured: A1/A2 campaign 2026-04-22T15:07Z → L3 full-coverage aggregation 2026-04-22T18:58Z → R1 stratified review 2026-04-23 → 2026-04-25 (3 working windows per day) → B1/B2/c2 themes 2026-04-26T09:00–11:30Z. The wider design-time contract A1 → L1 → A2 → L2 → L3 → A3 → R1 retains A3 (contradiction scan) as a prompt-only deferred step (no `a3_*.json` outputs); see [`p3_thematic_synthesis/FREEZE.md`](../p3_thematic_synthesis/FREEZE.md) GL-10 caveats.

## Phase 4 — Experiment replication and validation (canonical audit clean)

- Toolchain: Qiskit 2.3.0, QDK/qsharp 1.27.0, Azure Quantum Resource Estimator, Python 3.13.13 local venv.
- Cohort: 71 canonical labels selected from the P3/S3 most-viable quantum-advantage layer (paper-faithful strict = 0; family/template = 13; proxy-declared = 58).
- Phase 8 grid: 2,556 expected cells; 2,519 OK records; 37 engine failures; 0 missing.
- **2026-04-26 — canonical architecture finalised**: core/, experiments/, canonical/{reports,outputs,release}/ boundaries set. Source: [p4_experiments/docs/ARCHITECTURE.md](../p4_experiments/docs/ARCHITECTURE.md).
- Source: [p4_experiments/canonical/PRE_REGISTRATION.md](../p4_experiments/canonical/PRE_REGISTRATION.md), [p4_experiments/canonical/REPRODUCE.md](../p4_experiments/canonical/REPRODUCE.md), [p4_experiments/canonical/DECISIONS_LOG.md](../p4_experiments/canonical/DECISIONS_LOG.md).

---

## Document policy

- This timeline is a derived narrative document. The authoritative live status is the freeze set plus [PROJECT_STATE.yaml](PROJECT_STATE.yaml). When a timeline sentence diverges from a phase `FREEZE.md`, the phase freeze wins.
- Dates in this document are taken from existing artifacts. They are not inferred or back-formed.
