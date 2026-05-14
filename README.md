# Quantum Finance — Submission Supplementary Repository

Companion repository to the MSc thesis *Quantum Computing in Financial Services* (Copenhagen Business School, 2026), authored by Aleix Telesforo (@TelesforoAleix) and Vincent Wallerich (@vallahrich).

This repository is the **self-contained supplementary archive** submitted alongside the thesis. It carries the full audit trail, configurations, prompts, derived artifacts, and reproduction tooling for every claim made in the manuscript. Everything an examiner needs to verify the thesis claims is in this tree — no external archive is required.

The repository is **frozen** as a hand-in artifact. Headline numbers, taxonomies, cohorts, and audit ledgers are pinned by [`FREEZE.md`](FREEZE.md) at the root and per-folder `FREEZE.md` files.

## Examiner Quickstart

Three commands from the unzipped archive root. Requires **Python 3.12 or 3.13** and PowerShell (`pwsh`). No LLM credentials, no quantum hardware, no Azure account.

```powershell
python -m venv .venv ; .\.venv\Scripts\Activate.ps1
pip install -r requirements-verify.txt
pwsh .\verify.ps1 ; python -m pytest
```

Expected on a clean archive:

- `verify.ps1` ends with `All verification checks passed.` and prints the JSON reports path under `tools/verify/reports/`.
- `pytest` ends with `798 passed, 24 skipped` (counts may differ slightly across Python patch versions).

If anything fails, see [`REPRODUCIBILITY.md`](REPRODUCIBILITY.md) and [`tools/verify/reports/known_drift_2026-05.md`](tools/verify/reports/known_drift_2026-05.md).

## Start Here

| File | Purpose |
|---|---|
| [`FREEZE.md`](FREEZE.md) | Top-level frozen status and headline numbers. |
| [`FAIR_USE.md`](FAIR_USE.md) | Fair-use rationale: which materials are excluded (copyrighted source PDFs and full-text transcripts), which are shipped, and how to obtain originals via DOI. |
| [`REPRODUCIBILITY.md`](REPRODUCIBILITY.md) | Toolchain, setup commands, per-phase reproduction entry points, and LLM-call posture. |
| [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) | Map of the hand-in repository structure. |
| [`docs/PIPELINE.md`](docs/PIPELINE.md) | Phase-by-phase research pipeline overview. |
| [`docs/PROJECT_STATE.yaml`](docs/PROJECT_STATE.yaml) | Compact machine-readable project state and cross-phase contracts. |
| [`docs/PROJECT_TIMELINE.md`](docs/PROJECT_TIMELINE.md) | Chronology grounded in real artifacts. |
| [`docs/AUDIT_INDEX.md`](docs/AUDIT_INDEX.md) | Audit and log navigation. |
| [`docs/ARTIFACT_CLAIM_LEDGER.md`](docs/ARTIFACT_CLAIM_LEDGER.md) | Per-claim source files, allowed wording, and verification commands. **The single highest-value reference for examiners.** |
| [`docs/ai-prompt-iteration-stats.md`](docs/ai-prompt-iteration-stats.md) | Quantitative LLM prompt-iteration and review-acceptance evidence. |

## LLM Audit Trail

Raw LLM call logs from both researchers' execution sessions are merged at [`audit/logs/`](audit/logs/). See [`audit/README.md`](audit/README.md) for the navigation entry point and per-phase pointers; the full file-pattern catalog is in [`audit/logs/README.md`](audit/logs/README.md), and the schema-and-questions index is [`docs/AUDIT_INDEX.md`](docs/AUDIT_INDEX.md). Each phase that invoked an LLM also keeps stage-local call logs (e.g., `p3_thematic_synthesis/s4_thematic_coding/<silo>/themes/*.raw_response.txt` and `*_calls.jsonl` files). Together these constitute the complete AI-use audit trail referenced in the manuscript's AI Use Declaration appendix.

## Phase-Local Provenance Files

| File | Why it is here |
|---|---|
| [`p2_systematic_review/output/audit/manual_extraction_targets.txt`](p2_systematic_review/output/audit/manual_extraction_targets.txt) | Manual extraction target list used in the same P2/P4 triage chain; referenced by [`p4_experiments/canonical/cohort.json`](p4_experiments/canonical/cohort.json). |
| [`p2_systematic_review/output/audit/triage_classification.json`](p2_systematic_review/output/audit/triage_classification.json) | Post-classification quantitative triage ledger. |

These are retained for traceability; current claims are controlled by the freeze files and canonical outputs listed above.

## Phase 3 Evidence

The Phase 3 thematic synthesis spine is included as `p3_thematic_synthesis/s1_silo_scoping/` through `p3_thematic_synthesis/s5_cross_silo/` plus the `s6_silo_framing/` descriptive sibling. Each active silo carries its codes, themes, and reviewed-disposition logs (S4); the cross-silo synthesis (S5) and per-silo descriptive briefs (S6) are present in their final form.

## What Is Not in This Repository

The following materials were deliberately excluded from this submission. See [`FAIR_USE.md`](FAIR_USE.md) for the full rationale.

- **Source PDFs and full-text transcripts of corpus papers** — copyrighted; obtain via DOI from the bridge file at [`shared/bridge/paper_id_bridge.csv`](shared/bridge/paper_id_bridge.csv).
- **Reference PDFs of the Phase 3 quantum-advantage frameworks** (Rønnow, Beverland, Dalzell, Hoefler, Babbush, Chakrabarti, Stilck França) — see [`p3_thematic_synthesis/s3_quantum_advantage/REFERENCE_PDFS_EXCLUDED.md`](p3_thematic_synthesis/s3_quantum_advantage/REFERENCE_PDFS_EXCLUDED.md) for citations.
- **The thesis manuscript itself** — submitted as the primary deliverable on Digital Exam, not as part of this supplementary archive.
- **Personal review notes, work-in-progress audits, internal review matrices, and design-iteration scaffolding** — not part of the validation surface; the canonical evidence (claim ledger, freeze files, audit reports) covers what those notes were tracking.
- **Operational caches and bytecode** (`__pycache__/`, vector stores, API caches) — regenerable.

## Verification

These checks use existing artifacts only; they do not rerun LLM extraction, classification, or expensive experiment jobs.

Requires **Python 3.12 or 3.13**.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements-verify.txt

pwsh .\verify.ps1
python -m pytest
```

`requirements-verify.txt` is the minimal pinned dependency set for the verifier and test surface. For full Phase 4 reproduction (heavy), use [`p4_experiments/canonical/requirements.lock`](p4_experiments/canonical/requirements.lock) instead. See [`REPRODUCIBILITY.md`](REPRODUCIBILITY.md) for both paths.

For Phase 4 reproduction, see [`p4_experiments/canonical/REPRODUCE.md`](p4_experiments/canonical/REPRODUCE.md). Expensive paths support `--dry-run` for plan-only inspection.
