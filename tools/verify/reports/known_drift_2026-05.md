# Known Verification Drift — 2026-05-02 baseline

This document inventories the drift that the Phase-5 verification scripts
**intentionally** surface against the current repository state. Every entry
here is a *known* finding. The verification scripts are honest: unaccepted
drift exits non-zero, while accepted exceptions are machine-readable and
reported in JSON. As of the 2026-05-02 hardening pass, `verify.ps1` passes.

The remediation plan does **not** cover fixing the underlying drift —
that requires either re-running expensive jobs (out of scope) or
schema-level decisions outside the chore/remediation-2026-05 branch.

---

## V2 — `tools.verify.v2_consistency`

**Status:** 0 fail / 0 warn at 2026-05-02 after the hardening pass.

### W2.1 — closed: orphan folder `problems/forecasting_prediction/`
- Folder exists under `p3_thematic_synthesis/problems/` but is not
  referenced by `silo_inclusion.json` (neither active nor excluded nor
  cross_cutting).
- Root cause: `forecasting_prediction` was absorbed into PD-04
  `quantum_ml_finance` (`silo_inclusion.json` notes the absorption on
  PD-04 itself, but the legacy folder was kept for traceability).
- Suggested fix (Phase 6, low priority): add a `STATUS.md` marker file
  inside the folder, OR add a third `silo_inclusion.json` array
  (`merged_silos`) that records the absorption explicitly.

---

## V3 — `tools.verify.v3_trace_label`

**Status after 2026-05-02 hardening:** V3 supports explicit accepted
exceptions via [../v3_trace_label_allowlist.json](../v3_trace_label_allowlist.json).
Three DOI-backed bridge rows were repaired in
[../../../shared/bridge/paper_id_bridge.csv](../../../shared/bridge/paper_id_bridge.csv):
`5413b7728054` (`SQ12`), `7cfdb2957f6c` (`SX1`-`SX4`), and
`e922f913e80b` (`SM8`). The remaining bridge-only gaps are accepted only when
they match the allow-list exactly; any new unaccepted V3 break still exits 1 and
fails [../../../verify.ps1](../../../verify.ps1).

### B3.1 — Bridge-only gaps in P4 cohort labels
- Original finding: 35/71 cohort label-links referenced paper IDs missing from
  `paper_id_bridge.csv`.
- Repaired as bridge rows: 6 label-links / 3 unique paper IDs, where P2
  processed frontmatter contained DOI evidence.
- Accepted exceptions: 29 label-links where P2/P3 artifact trace is complete
  but DOI and Zotero key are blank on disk.
- Root cause: the bridge was generated against the SLR-screened corpus
  (Phase 2 `s1_slr/`); papers added to the P3 active baseline through
  manual triage / repair (`p2_systematic_review/output/audit/triage_classification.json`,
  `p2_systematic_review/output/audit/manual_extraction_targets.txt`) bypassed the SLR pipeline and
  therefore were never bridged to DOIs or Zotero keys.
- Accepted-exception rule: a V3 bridge gap may pass only if the label,
  paper_id, experiment_id, reason, source artifact, and claim-use boundary are
  present in `tools/verify/v3_trace_label_allowlist.json`.
- Suggested stronger fix:
  regenerate the bridge against the union of (SLR corpus ∪ active P3
  baseline ∪ active P4 cohort), backfilling DOIs from extraction
  metadata where present.
- Until then: the allow-list is the canonical answer to "which cohort labels
  lack clean DOI/Zotero bridge linkage"; it is a limitation, not a silent pass.

---

## V9 — `tools.verify.v9_bridge`

**Status:** 534 bridge rows, 0 blank DOI, 3 blank Zotero keys, 14 DOI
collisions, 14 Zotero-key collisions, 52 title-string collisions. Always exits
0; the report is the deliverable. The 3 blank Zotero keys are the DOI-backed
rows added from P2 processed frontmatter during the 2026-05-02 V3 repair.

### B9.1 — 14 DOI collisions
- The same DOI (case-normalised) is associated with multiple
  `slr_paper_id`s.
- Example: `10.48550/arxiv.2510.15903` shared by `00c3aaba39ac` and
  `5081ec6b6068`. The two `slr_paper_id`s correspond to the *same*
  arXiv preprint indexed twice — once with `arXiv` casing, once with
  `arxiv` casing — that the SLR ingest pipeline failed to deduplicate.
- Suggested fix (Stronger version Step 10.4): lower-case all DOIs at
  ingest time; collapse duplicate `slr_paper_id`s by adding a
  `canonical_paper_id` column.

### B9.2 — 14 Zotero-key collisions
- Same as B9.1 manifesting on the Zotero side.

### B9.3 — 52 title-string collisions
- Mostly preprint↔published linkage (e.g. arXiv preprint and the later
  Springer/Nature version of the same paper carry identical titles).
- Suggested fix (Stronger version Step 10.4): add a `record_type`
  column (`paper` / `preprint` / `dataset` / `code`) and a
  `canonical_paper_id` column to express preprint↔published
  relationships explicitly.

---

## V6 — informational

V6 captures raw numeric claims from documentation files; it always
exits 0. Use it to spot-check prose claims against on-disk counts:

| On-disk metric                  | Value at 2026-05-02 |
|---|---:|
| `p2_processed_md`               | 777 |
| `p3_s2_extractions_json`        | 501 |
| `p3_s3_matrix_rows`             | 1046 |
| `p4_label_count`                | 71  |

Claims captured by V6's regex are reported *raw* in
`reports/v6_check_doc_claims_<date>.json`. Compare manually against the
table above; do not interpret a mismatch as an error without checking
context (e.g. a doc may correctly state "459 papers (historical)" or
"658 thematically coded").

---

## How to use this document

When `verify.ps1` reports a failure, first look here. If the failure is
already inventoried, no action is required for the MDV. If it is not,
either:
- record it here and proceed, or
- fix the underlying drift.

This file should be updated whenever a new known-drift entry is
accepted or an existing one is closed.
