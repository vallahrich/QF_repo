# P2 post-classification triage scripts

These scripts were used in 2026-04 to produce the post-hoc scope-triage
amendment recorded in
[`../../s1_slr/01_protocol/amendments/2026-05-02_post_classification_triage.md`](../../s1_slr/01_protocol/amendments/2026-05-02_post_classification_triage.md).
They lived at the repo root during the triage work itself; they were
relocated here on 2026-05-02 as part of `chore/remediation-2026-05`
(Phase 6) to keep the root clean and to make the post-hoc triage a
**formal, package-scoped protocol amendment** rather than ad-hoc
repo-root debris.

## Scripts

| Script                    | Purpose |
|---|---|
| `dump_likely.py`          | Emit `dump_likely.txt` — candidate "likely has results" rows for triage. |
| `dump_likely.txt`         | Output of `dump_likely.py` (kept for traceability). |
| `triage_empties.py`       | Find papers whose extraction emitted an empty `topic_tags` list (suggesting no-applicable-tag escape). |
| `triage_dump.txt`         | Output of `triage_empties.py`. |
| `process_empty_triage.py` | Apply the triage decisions to flag empty-tag papers. |
| `exclude_pass2.py`        | Second-pass exclusion run over flagged candidates. |
| `verify_excludes.py`      | Sanity-check the exclusion list against the on-disk corpus. |
| `verification_read.txt`   | Output of `verify_excludes.py`. |
| `rerun_ids.txt`           | Input ID list for targeted re-runs of the s2_classification pipeline. |
| `generate_skeletons.py`   | One-shot scaffolding generator for P3 silo folders (used during the P3 restructure). |

## Companion provenance files

The triage ledger is retained at
[`../../output/audit/triage_classification.json`](../../output/audit/triage_classification.json)
with the other Phase 2 audit artifacts. The manual target list is retained at
[`../../output/audit/manual_extraction_targets.txt`](../../output/audit/manual_extraction_targets.txt)
and remains referenced **by sha256** in
[`p4_experiments/canonical/cohort.json::_source_pinning`](../../../p4_experiments/canonical/cohort.json).

## Recommended successor: prompt-level fix

The root cause of the false-positive classifications these scripts
remediated was the closed-vocabulary classification prompt design. A
permanent fix is recorded in the amendment doc as Stronger-version
work: add an `out-of-scope` enum value and enforce per-step structured
outputs in `s2_classification/utils/step_runner.py`.

Until then, **future false-positive rounds should run from this folder
and add their decisions to the amendment**, not from the repo root.
