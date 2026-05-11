# Quantum Finance — Clean Submission Workspace

This detached cleanup copy has been slimmed for submission review. P2 processed traceability evidence and Phase 3 S1-S5 thesis evidence are present in the hand-in tree; high-volume support evidence, raw/non-final material, and local-only working material were moved to an external source archive, not deleted.

Archive root: `C:\QF_submission_packages\source_internal_archive\QF_repo_supporting_artifacts_20260509`  
Archive manifest: `C:\QF_submission_packages\source_internal_archive\QF_repo_supporting_artifacts_20260509\SOURCE_ARCHIVE_MANIFEST.csv`

## Start Here

| File | Purpose |
|---|---|
| [`FREEZE.md`](FREEZE.md) | Top-level frozen status and headline numbers for the hand-in tree. |
| [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) | Clean map of the hand-in repository structure. |
| [`docs/PIPELINE.md`](docs/PIPELINE.md) | Phase-by-phase research pipeline overview. |
| [`docs/PROJECT_STATE.yaml`](docs/PROJECT_STATE.yaml) | Compact machine-readable project state and cross-phase contracts; per-folder freeze files control artifact counts. |
| [`docs/PROJECT_TIMELINE.md`](docs/PROJECT_TIMELINE.md) | Clean chronology grounded in real artifacts. |
| [`docs/AUDIT_INDEX.md`](docs/AUDIT_INDEX.md) | Audit/log navigation, with source-archive notes for moved evidence. |
| [`docs/METHODOLOGY_DESIGN.md`](docs/METHODOLOGY_DESIGN.md) | Historical methodology scaffold retained for provenance; not the controlling current method. |

## Where Are The Logs?

The root [`logs/`](logs/) folder is a reviewer signpost, not the central storage location for all logs. Canonical logs and audit evidence are kept phase-locally next to the artifacts they document. Start with [`logs/README.md`](logs/README.md) or [`docs/AUDIT_INDEX.md`](docs/AUDIT_INDEX.md) to locate the relevant audit trail.

## Phase-Local Provenance File

| File | Why it is here |
|---|---|
| [`p2_systematic_review/output/audit/manual_extraction_targets.txt`](p2_systematic_review/output/audit/manual_extraction_targets.txt) | Manual extraction target list used in the same P2/P4 triage chain; referenced by [`p4_experiments/canonical/cohort.json`](p4_experiments/canonical/cohort.json). |

This is not a current headline-result file. It is retained for traceability; current claims are controlled by the freeze files and canonical outputs listed above. The post-classification quantitative triage ledger is phase-local at [`p2_systematic_review/output/audit/triage_classification.json`](p2_systematic_review/output/audit/triage_classification.json).

## Phase 3 Evidence

The Phase 3 thematic synthesis spine is included as `p3_thematic_synthesis/s1_silo_scoping/` through `p3_thematic_synthesis/s5_cross_silo/`. The S6 descriptive finance-framing sibling is also present as clean outputs because the freeze and tests expect it. The restored P3 layer keeps final/canonical thesis evidence and leaves source PDFs, full-paper Markdown, raw text, raw model responses, raw request bundles, logs, legacy snapshots, and comparator archives in the external source archive.

## What Was Archived Out Of This Workspace

- Source-paper PDFs and full-text folders.
- Local `.venv`, cache, and operational log folders.
- Internal Copilot/process folders (`.github/`, `review/`, `manuscript/working/`).
- Noisy planning/proofreading docs outside the clean documentation set.
- Raw LLM prompt/request logs and S6 request bundles.
- High-volume generated P4 support evidence plus non-final/raw P2/P3 support evidence useful for deep audit but too noisy or sensitive as loose files.
- Expanded Phase 11 release bundle tree; the canonical `zenodo_bundle.tar.gz` and `.sha256` sidecar remain under `p4_experiments/canonical/release/`.

## Restore Archived Evidence

To restore a moved path, copy it back from the archive root preserving the relative path shown in `SOURCE_ARCHIVE_MANIFEST.csv`. The external archive is local-only and is not intended for public redistribution.

## Verification

These checks use existing artifacts only; they do not rerun LLM extraction, classification, or expensive experiment jobs.

```powershell
pwsh .\verify.ps1
python -m pytest
```

The derivative packages under `C:\QF_submission_packages` are separately curated and manifest-verified.
