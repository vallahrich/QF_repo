# Amendment 2026-05-02 — Post-classification scope triage

**Amendment ID:** A-2026-05-02-PostClass-Triage
**Status:** Adopted (retrospective formalisation of 2026-04 triage work)
**Author:** Vincent Wallerich
**Affects protocol section:** §1 Tiered extraction; §4 Boundaries and grey-literature policy

---

## 1. Background

The Phase-2 LLM classification pipeline (`s2_classification/scripts/run_extraction_step.py`,
single-shot per paper, no schema enforcement, no inter-rater check) produced
777 markdown / `_extraction.json` records under
`p2_systematic_review/output/processed/`. A post-hoc spot-check
identified a non-trivial false-positive rate: papers that should not
have entered the corpus on inclusion-criteria grounds were nevertheless
classified with finance-relevant `topic_tags` and `methodology_tags`.

Examples surfaced in the senior review (2026-05-02):

- `001f5dbe487a` — speculative essay on Vedic mathematics tagged
  `portfolio-optimization` and `cryptography-security`.
- `11807719b419` — "Testing quantum theory by generalizing
  noncontextuality" (foundational physics, no finance content).
- `1502fad8d8ac` — "Predictive Maintenance of Machine Health"
  (industrial IoT, no quantum content).
- `0ab110ae249c` — "Coherence-Gated Dimensional Access" (consciousness
  studies; not in any defined scope).

These are the symptoms of two compounding gaps in the classification
prompt design:

- **No "no-applicable-tag" escape hatch.** `prompts/step6_synthesis.txt`
  defines a closed vocabulary and treats an empty list as a degenerate
  case rather than as a first-class out-of-scope signal. The model
  therefore projects the closest available tag onto any paper it cannot
  honestly leave un-tagged.
- **No per-step structured-output enforcement.** Unlike
  `s1_slr/tools/slr_toolkit/llm_screening.py`, which uses
  `SCREENING_RESPONSE_SCHEMA` strict=true, the per-paper extraction
  pipeline regex-parses free-text JSON. A hallucinated `topic_tags`
  value passes silently downstream.

## 2. Triage performed

A post-classification triage pass (ledger retained at
`p2_systematic_review/output/audit/triage_classification.json`,
`process_empty_triage.py`, `triage_empties.py`, `dump_likely.py`,
`exclude_pass2.py`, `verify_excludes.py`) classified 63 candidate-defective
papers. Of these, **22** were confirmed out-of-scope under the protocol:

| Triage class                  | Count | Rationale |
|---|---:|---|
| `NON_FINANCE`                 | 6 | Paper has no financial application content. |
| `NO_QUANTUM_CONTENT`          | 6 | Paper does not use or analyse quantum computing. |
| `OUT_OF_SCOPE`                | 5 | Paper is in scope of QC and finance individually but addresses neither in combination. |
| `NO_QUANT_METRICS`            | 2 | Paper claims relevance but reports no quantitative results (Tier 2/3 ineligible). |
| `TOO_SHORT_abstract_only`     | 3 | PDF contains only the abstract; insufficient for tier-2 extraction. |
| **Total excluded**            | **22** | |

The full list with paper IDs and triage class is in
[`output/audit/excluded_post_classification.csv`](../../../output/audit/excluded_post_classification.csv).

The remaining 41 triaged papers are either `BORDERLINE` (24 — kept,
flagged for downstream sensitivity), `LIKELY_HAS_RESULTS` (17 — kept,
no action needed).

## 3. Amendment

The 22 confirmed-off-scope papers are **excluded retrospectively** from
the Phase-2 included corpus. Their `output/processed/<paper_id>.md`
records are preserved on disk for audit-trail purposes but **must be
treated by all downstream phases (P3, P4, manuscript) as
post-classification exclusions** equivalent to a step-3 (full-text
screening) reject.

The active P3 baseline (501 quantitative extractions) already excludes
these papers — see `shared/bridge/excluded_papers.csv` and
`p3_thematic_synthesis/s2_quantitative/output/audit/corpus_lineage.json`
which document the 777 → 501 lineage. This amendment makes the
exclusion **explicit at the P2 protocol layer** rather than implicit at
the P3 ingest layer.

## 4. Future protocol changes (recommended, not yet adopted)

The two prompt-design gaps that produced the false positives should be
closed before any future re-classification pass:

1. Add an `out-of-scope` enum value to `topic_tags` /
   `methodology_tags`. When step 1 returns `out-of-scope`, downstream
   steps short-circuit and the paper is excluded with a recorded
   reason.
2. Enforce per-step structured outputs in
   `s2_classification/utils/step_runner.py` by passing a JSON schema
   per step (allowed enums for `source_type`, `evaluation_type`,
   `quantum_advantage_claim`; `topic_tags` as
   `array<enum from unified_taxonomy.json>`).

These changes are tracked in the chore/remediation-2026-05 plan as
"Stronger version" items; they are not required for the MDV.

## 5. Reproducibility

Triage scripts have been migrated from the repo root to
`p2_systematic_review/scripts/triage/` (Phase 6 of the
chore/remediation-2026-05 plan). The triage ledger is retained under
`p2_systematic_review/output/audit/triage_classification.json` so it is
phase-local with the P2 audit artifacts. The P4 cohort `_source_pinning`
block references this path and preserves the ledger checksum.
