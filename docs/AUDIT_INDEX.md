# Audit Index

This index maps each log family in the repository to what it records and what range of events it answers questions about. It is a navigation aid for examiners. Freeze files and checked derived outputs control current research claims; logs and ledgers control provenance for the events they record.

Generated: 2026-05-09. No log file referenced here was modified to produce this index.

---

## How to use this index

Each section names a log family, gives its location, says what schema/format it uses, and explains which kind of question it answers. Use it to locate the right artifact before drilling into details.

For the project-wide chronology, start with [PROJECT_TIMELINE.md](PROJECT_TIMELINE.md). For phase status, start with [PROJECT_STATE.yaml](PROJECT_STATE.yaml) and the per-folder freeze files.

---

## Phase 1 — Framework synthesis

| Artifact | What it records | Schema | Answers |
|---|---|---|---|
| [p1_framework_synthesis/audit-trail.md](../p1_framework_synthesis/audit-trail.md) | LLM proposal vs researcher decision divergences during inductive taxonomy construction | Markdown narrative, 4 entries | "Where did the researcher override the LLM during taxonomy design, and why?" |
| [p1_framework_synthesis/s1_extractions/](../p1_framework_synthesis/s1_extractions/) | Per-paper structured extraction JSONs from the 30 exploratory papers | JSON, one file per paper, includes attributed quotes with page references | "What evidence anchored each PD/SA code?" |
| [p1_framework_synthesis/s4_outputs/](../p1_framework_synthesis/s4_outputs/) | Final framework artifacts: `conceptual-framework.md`, `codebook.md`, mapping matrix | Markdown + JSON | "What is the final taxonomy and what are the operationalised definitions?" |

## Phase 2 — Systematic review (SLR) and classification

### Protocol amendments
| Artifact | What it records | Schema | Answers |
|---|---|---|---|
| [p2_systematic_review/s1_slr/01_protocol/protocol.md](../p2_systematic_review/s1_slr/01_protocol/protocol.md) | Historical/amended SLR protocol text; read with the amendments log and Phase 2 freeze | Markdown | "What did the protocol say at this stage, and how was it later amended?" |
| [p2_systematic_review/s1_slr/01_protocol/amendments_log.csv](../p2_systematic_review/s1_slr/01_protocol/amendments_log.csv) | All 12 numbered amendments (A1–A12) plus deprecation events for raw export folders | CSV: date, version, section, change_description, author | "When and why did the protocol change? Which raw export run is current vs deprecated?" |
| [p2_systematic_review/s1_slr/01_protocol/archive/](../p2_systematic_review/s1_slr/01_protocol/archive/) | Earlier amendment notes preserved for historical reference | Markdown | "What did earlier amendment notes look like before consolidation?" |

### Search and ingestion
| Artifact | What it records | Schema | Answers |
|---|---|---|---|
| [p2_systematic_review/s1_slr/03_screening/asreview_dataset.csv](../p2_systematic_review/s1_slr/03_screening/asreview_dataset.csv) | Deduplicated screening dataset | CSV | "What is the screening universe after deduplication?" |
| [p2_systematic_review/s1_slr/03_screening/asreview_prior_labels.csv](../p2_systematic_review/s1_slr/03_screening/asreview_prior_labels.csv) | Prior labels passed to AI screening | CSV | "What labels seeded the AI screening run?" |

### Title/abstract screening
| Artifact | What it records | Schema | Answers |
|---|---|---|---|
| [p2_systematic_review/s1_slr/03_screening/calibration_decisions.csv](../p2_systematic_review/s1_slr/03_screening/calibration_decisions.csv) | Calibration round (50 records, two-reviewer κ ≥ 0.70 target) | CSV | "How did calibration go and what was the inter-rater agreement?" |
| [p2_systematic_review/s1_slr/03_screening/title_abstract_decisions.csv](../p2_systematic_review/s1_slr/03_screening/title_abstract_decisions.csv) | Human title/abstract include/exclude decisions | CSV | "Why was each record included or excluded at title/abstract stage?" |
| [p2_systematic_review/s1_slr/03_screening/ai_screening_decisions.csv](../p2_systematic_review/s1_slr/03_screening/ai_screening_decisions.csv) | AI screening decisions (gpt-5-mini production run) | CSV | "What did the AI predict for each record?" |
| p2_systematic_review/s1_slr/03_screening/llm_screening_prompt_log.jsonl (moved to source archive) | Raw LLM screening prompts and decisions | JSONL | "What prompt and reasoning supported each screening decision?" |
| [p2_systematic_review/s1_slr/03_screening/ai_discrepancy_review.csv](../p2_systematic_review/s1_slr/03_screening/ai_discrepancy_review.csv) | AI vs human disagreement resolution | CSV | "Where did AI and human disagree, and how was it resolved?" |
| [p2_systematic_review/s1_slr/03_screening/fn_audit_sample.csv](../p2_systematic_review/s1_slr/03_screening/fn_audit_sample.csv) | False-negative audit sample (10% of AI excludes) | CSV | "Did the AI miss any genuinely relevant records?" |
| [p2_systematic_review/s1_slr/03_screening/non_english_audit.csv](../p2_systematic_review/s1_slr/03_screening/non_english_audit.csv) | Non-English exclusions per protocol §9 | CSV | "Which records were excluded for language only?" |

### Full-text screening and inclusion
| Artifact | What it records | Schema | Answers |
|---|---|---|---|
| [p2_systematic_review/s1_slr/03_screening/full_text_decisions.csv](../p2_systematic_review/s1_slr/03_screening/full_text_decisions.csv) | Full-text include/exclude decisions | CSV | "Why was each record included or excluded after reading the full text?" |
| [p2_systematic_review/s1_slr/03_screening/included_for_coding.csv](../p2_systematic_review/s1_slr/03_screening/included_for_coding.csv) | Final included set passed forward to extraction | CSV | "Which 875 → 777 papers proceeded to extraction?" |

### Extraction
| Artifact | What it records | Schema | Answers |
|---|---|---|---|
| [p2_systematic_review/output/processed/](../p2_systematic_review/output/processed/) | Final gpt-5-mini structured Markdown per paper (with frontmatter `topic_tags`, `methodology_tags`) and extraction JSON | MD + JSON, one pair per paper | "What was extracted from this specific paper, and what tags does it carry?" |
| [p2_systematic_review/output/audit/](../p2_systematic_review/output/audit/) | Excluded-post-classification audit, including the quantitative triage ledger | CSV + JSON | "Which papers were triaged or excluded after classification, and why?" |
| [shared/extracted_text/extraction_log.csv](../shared/extracted_text/extraction_log.csv) | Per-PDF text-extraction metadata (extractor, page count, OCR fallback) | CSV | "How was the body text extracted for each source PDF?" |

## Phase 3 — Thematic synthesis

### Within-silo audit and freezes
| Artifact | What it records | Schema | Answers |
|---|---|---|---|
| [p3_thematic_synthesis/AUDIT_REPORT.md](../p3_thematic_synthesis/AUDIT_REPORT.md) | Phase 3 audit summary | Markdown | "What is the audited state of Phase 3?" |
| [p3_thematic_synthesis/P3_AUDIT_STATUS.md](../p3_thematic_synthesis/P3_AUDIT_STATUS.md) | Per-silo audit status | Markdown | "Which silos are audit-clean and which are not?" |
| [p3_thematic_synthesis/s2_quantitative/output/audit/corpus_lineage.json](../p3_thematic_synthesis/s2_quantitative/output/audit/corpus_lineage.json) | Lineage of the quantitative corpus across freezes | JSON | "How did the quantitative corpus evolve across the 2026-04-17 and 2026-05-02 freezes?" |
| [p3_thematic_synthesis/s2_quantitative/output/audit/active_baseline_fingerprints.json](../p3_thematic_synthesis/s2_quantitative/output/audit/active_baseline_fingerprints.json) | Hash fingerprints of the active baseline files | JSON | "Has the active baseline drifted since the 2026-05-02 freeze?" |
| [p3_thematic_synthesis/s2_quantitative/output/audit/excluded_papers_historical_2026-04-17.csv](../p3_thematic_synthesis/s2_quantitative/output/audit/excluded_papers_historical_2026-04-17.csv) | Historical exclusion list at the 2026-04-17 freeze | CSV | "Which papers were excluded at the first freeze?" |

### Per-paper coding outputs (s4 thematic coding)
| Artifact | What it records | Schema | Answers |
|---|---|---|---|
| `p3_thematic_synthesis/s4_thematic_coding/{silo}/codes/{paper_id}.jsonl` | A1 open-coding output per paper | JSONL, one code per line | "What initial codes were extracted from this paper?" |
| `p3_thematic_synthesis/s4_thematic_coding/{silo}/memos/{paper_id}.json` and `_l3.json` | A2 memo compression and L3 adversarial error-finding outputs | JSON | "How were codes compressed into a memo, and did L3 flag any issues?" |
| `p3_thematic_synthesis/prompts/a3_contradiction_scan.txt` | A3 contradiction-scan prompt retained for traceability; no current `a3_*.json` outputs in the 2026-05-02 freeze | TXT | "Was A3 executed, or deferred?" |
| `p3_thematic_synthesis/s4_thematic_coding/{silo}/reviewed/r1_review.jsonl` | R1 post-freeze reviewer verdicts per paper (GL-10 closure) | JSONL | "What did the human reviewer decide for each paper?" |
| `p3_thematic_synthesis/s4_thematic_coding/{silo}/reviewed/r1_review_worklist.jsonl` | R1 worklist (open items) | JSONL | "Which papers still need R1 review?" |
| `p3_thematic_synthesis/s4_thematic_coding/{silo}/themes/` | B1 batch themes, B2 silo themes, C2 grounding-check, C3 crosswalk, plus the prompt templates used | JSON + prompt `.txt` | "What themes were synthesised per silo and which prompt produced them?" |

### Quantum advantage assessment (s3)
| Artifact | What it records | Schema | Answers |
|---|---|---|---|
| [p3_thematic_synthesis/s3_quantum_advantage/combined/output/triangulation_matrix.json](../p3_thematic_synthesis/s3_quantum_advantage/combined/output/triangulation_matrix.json) | Raw 4-core + 1-veto triangulation matrix | JSON | "What does each rubric say about each experiment?" |
| [p3_thematic_synthesis/s3_quantum_advantage/combined/output/triangulation_matrix.filtered.json](../p3_thematic_synthesis/s3_quantum_advantage/combined/output/triangulation_matrix.filtered.json) | Active-silo filtered baseline (936 active rows) | JSON | "What is the live active-silo baseline that feeds Phase 4?" |
| [p3_thematic_synthesis/s3_quantum_advantage/combined/output/consensus_summary.json](../p3_thematic_synthesis/s3_quantum_advantage/combined/output/consensus_summary.json) and [p3_thematic_synthesis/s3_quantum_advantage/combined/output/consensus_summary.filtered.json](../p3_thematic_synthesis/s3_quantum_advantage/combined/output/consensus_summary.filtered.json) | Consensus rollup, raw and filtered | JSON | "What does the consensus distribution look like overall and per silo?" |
| [p3_thematic_synthesis/s3_quantum_advantage/combined/output/disagreement_cases.json](../p3_thematic_synthesis/s3_quantum_advantage/combined/output/disagreement_cases.json) | Cases where rubrics disagree | JSON | "Which experiments triggered analyst attention?" |
| [p3_thematic_synthesis/s3_quantum_advantage/derived_fields/enriched/derived_fields.json](../p3_thematic_synthesis/s3_quantum_advantage/derived_fields/enriched/derived_fields.json) | Derived per-experiment fields used by Phase 4 | JSON | "What enriched fields does Phase 4 consume?" |
| [p3_thematic_synthesis/s3_quantum_advantage/derived_fields/p4_tau_summary.json](../p3_thematic_synthesis/s3_quantum_advantage/derived_fields/p4_tau_summary.json) | τ summary feeding the Phase 4 oracle-tax analysis | JSON | "What is the per-experiment τ used in Phase 4?" |

### Finance framing sub-pipeline (s6)
| Artifact | What it records | Schema | Answers |
|---|---|---|---|
| `p3_thematic_synthesis/s6_silo_framing/extractions/papers/{paper_id}.json` | F1 per-paper finance framing extraction | JSON, includes attributed quotes verified by substring match | "What financial problem framing came from this paper?" |
| `p3_thematic_synthesis/s6_silo_framing/briefs/{silo}/f2_silo_brief.json` | F2 per-silo aggregated brief | JSON, paper-id verified against the F1-accepted set | "What is the silo-level framing presented in Section (0) of the silo chapter?" |

## Phase 4 — Experiments and resource estimation

### Decision trail
| Artifact | What it records | Schema | Answers |
|---|---|---|---|
| [p4_experiments/canonical/PRE_REGISTRATION.md](../p4_experiments/canonical/PRE_REGISTRATION.md) | Canonical empirical contract and reporting rules | Markdown | "What is the pre-registered Phase 4 contract?" |
| [p4_experiments/canonical/DECISIONS_LOG.md](../p4_experiments/canonical/DECISIONS_LOG.md) | Phase 4 design decisions (chronological) | Markdown | "When and why did each Phase 4 design choice happen?" |
| [p4_experiments/canonical/REPRODUCE.md](../p4_experiments/canonical/REPRODUCE.md) | Reproduction recipe | Markdown | "How does an examiner re-run the canonical pipeline?" |

### Cohort and inputs
| Artifact | What it records | Schema | Answers |
|---|---|---|---|
| [p4_experiments/canonical/cohort.json](../p4_experiments/canonical/cohort.json) | Checked 71-label canonical cohort | JSON | "Which experiments are in the canonical cohort?" |
| [p4_experiments/core/p4_shortlist.json](../p4_experiments/core/p4_shortlist.json) | Phase 4 shortlist derived from frozen P3 outputs | JSON | "What is the shortlist that feeds the canonical cohort?" |

### Reports and audits
| Artifact | What it records | Schema | Answers |
|---|---|---|---|
| p4_experiments/canonical/reports/ (moved to source archive) | Generated Phase 3/8/9 reports, evidence report, sensitivity grid | JSON + Markdown | "What does each phase report say?" |
| p4_experiments/canonical/reports/audit/ (moved to source archive) | Per-phase audit JSONs (audit_phase4 … audit_phase11) | JSON | "Did each phase pass its audit, and what failed if not?" |
| p4_experiments/canonical/outputs/manuscript_artifacts/ (moved to source archive) | Phase 10 manuscript tables, figure CSVs, key numbers, briefs, captions | CSV + JSON + Markdown | "Which manuscript tables/figures come from which canonical run?" |
| [p4_experiments/canonical/release/](../p4_experiments/canonical/release/) | Hash-stamped Phase 11 Zenodo bundle, tarball, and `.sha256` sidecar | tar.gz + sidecar | "What is the canonical release bundle and how is its integrity verified?" |

## Cross-cutting verification

| Artifact | What it records | Schema | Answers |
|---|---|---|---|
| [tools/verify/reports/](../tools/verify/reports/) | Cross-phase verifier outputs (v3 trace label, v5 recompute P3, v6 doc claims, v7 algorithm families, v9 bridge), date-stamped per run | JSON, one file per verifier per date | "Did the cross-phase invariants hold on each verifier run?" |
| [shared/bridge/paper_id_bridge.csv](../shared/bridge/paper_id_bridge.csv) | Canonical ID mapping: SLR paper_id ↔ DOI ↔ Zotero item key | CSV | "What is the canonical identifier for this paper across all phases?" |
| [shared/config/unified_taxonomy.json](../shared/config/unified_taxonomy.json) | Single tag registry (PD-01..10, SA-01..11) used across all phases | JSON | "What is the authoritative taxonomy code list?" |

## Cleanup/submission Phases 1–6

| Artifact | What it records | Schema | Answers |
|---|---|---|---|
| PHASE1_CLEANUP_REPORT.md (moved to source archive) | Cleanup boundary check, files created/edited, secret scan, validation results | Markdown | "What did Phase 1 cleanup do, and what passed validation?" |
| PHASE2_PACKAGING_REPORT.md (moved to source archive) | Package profile design, PDF handling rules, P4 manifest-drift and release-bundle decisions | Markdown | "What package profiles were designed and what blockers were documented?" |
| PHASE3_FINAL_SUBMISSION_REPORT.md (moved to source archive) | Restoration of 42 cohort S2 files (line-ending-only drift); Phase 11 re-extraction; final validation | Markdown | "How was the strict P4 dry-run unblocked and the Phase 11 audit cleared?" |
| PHASE4_DERIVED_PACKAGE_REPORT.md (moved to source archive) | Two derivative packages produced; copy/exclusion policy; package validation | Markdown | "What is in each derivative package and what was excluded?" |
| PHASE5_FINAL_HANDOFF_REPORT.md (moved to source archive) | Manifest hashing, hygiene checks, reviewer first steps | Markdown | "Were the packages handoff-ready?" |
| PHASE6_PACKAGE_IP_COMPLIANCE_REPORT.md (moved to source archive) | IP exclusion (verbatim full-text Markdown) and subsequent handoff curation (raw LLM I/O, non-final snapshots, internal prompts, monitor logs); final manifest counts | Markdown | "What did Phase 6 IP and curation do to the derivative packages?" |

Per-package metadata (in each derivative package under `C:\QF_submission_packages\{profile}\`):

| Artifact | What it records |
|---|---|
| `PACKAGE_README.md` | Package purpose, validation quick start, claim boundaries, IP and handoff curation policies |
| `PACKAGE_MANIFEST.json` | Included files with byte sizes and SHA-256 hashes |
| `EXCLUDED_FILES_MANIFEST.csv` | Excluded paths with rule and reason |
| `PDF_EXCLUSION_MANIFEST.csv` | PDF-specific exclusions |
| `VALIDATION_REPORT.md` | Commands run and final validation results, including IP and handoff-curation notes |

---

## Iteration evidence retained on disk (internal copy only)

These dated snapshot/archive folders preserve the pre-rerun state of pipelines that were later re-executed. They live in the source/internal copy as audit evidence and are excluded from the two derivative submission packages per the curation policy recorded in PHASE6_PACKAGE_IP_COMPLIANCE_REPORT.md (moved to source archive; see the archive manifest named in [../README.md](../README.md)):

- p3_thematic_synthesis/s2_quantitative/output/extractions_preQ0_20260417_095811/ (moved to source archive)
- p3_thematic_synthesis/s2_quantitative/output/extractions_pre_5.3_20260422_095328/ (moved to source archive)
- p3_thematic_synthesis/s4_thematic_coding/papers_l3_v2_gpt51_archive/ (moved to source archive)
- p3_thematic_synthesis/s3_quantum_advantage/combined/output/_pre_remediation_snapshot_2026-05-02/ (moved to source archive)
- p4_experiments/canonical/outputs/phase08d_hhl_tail_exploratory/archive_superseded_20260428/ (moved to source archive)
- p4_experiments/infra/azure/phase8_4vm_legacy_bootstrap/ (moved to source archive)

---

## Document policy

- This index is a navigation aid. The underlying logs themselves are the source of truth.
- Paths and counts are taken from the current state of the repository as of 2026-05-10.
- This document is generated by hand and should be regenerated, not edited in place, if the underlying log layout changes.
