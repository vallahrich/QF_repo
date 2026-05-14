# Reproducibility

This document is the entry point for reproducing or verifying any artifact in this repository. It explains the toolchain, the per-phase reproduction surfaces, and the LLM-call posture.

## Toolchain (open-source only)

**Python: 3.12 or 3.13** (the production Phase 4 environment used 3.13.13; the verify-only path was independently confirmed on 3.12.10).

| Component | Pinned version | Source |
|-----------|---------------|--------|
| Python | 3.12 – 3.13 | python.org |
| qiskit | 2.3.0 | PyPI (pip) |
| qiskit-aer | 0.17.2 | PyPI (pip) |
| qsharp | 1.27.0 | PyPI (pip) |
| numpy, scipy, pandas, pytest | latest compatible | PyPI (pip) |

Full pinned set for the heavy Phase 4 pipeline: [`p4_experiments/canonical/requirements.lock`](p4_experiments/canonical/requirements.lock).

No proprietary or paid dependencies are required. No quantum hardware credentials are required (Phase 4 uses Qiskit Aer classical simulation throughout).

## Setup

Two install paths are supported. **Most examiners only need the verify path.**

### Verify-only (lightweight; runs `verify.ps1` and `pytest`)

```powershell
# Fresh Python 3.12 or 3.13 venv
python -m venv .venv
.\.venv\Scripts\Activate.ps1

pip install -r requirements-verify.txt
```

Pinned set: [`requirements-verify.txt`](requirements-verify.txt) — `jsonschema`, `numpy`, `openai`, `openpyxl`, `pandas`, `pytest`, `python-dotenv`, `python-frontmatter`. (`openai` and `python-dotenv` are pulled in transitively by `shared.tools` modules at test-collection time; no LLM call is made during verification.)

### Full Phase 4 reproduction (heavy)

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1

pip install -r p4_experiments/canonical/requirements.lock
```

## Running the verification harness

The `verify.ps1` script runs every `tools/verify/v*.py` validator in numeric order and writes timestamped reports to `tools/verify/reports/`. These validators check schema integrity, cross-phase consistency, label trace coverage, claim-vs-evidence alignment, and bridge hygiene.

```powershell
pwsh .\verify.ps1               # run all
pwsh .\verify.ps1 -Only v1      # run a single validator
python -m pytest                # run the structural tests across phases
```

Exit code is non-zero if any check fails. The validators do not call any LLM and do not regenerate pipeline outputs; they only read existing artifacts.

## Per-phase reproduction documents

Each phase ships a `FREEZE.md` describing the frozen state, plus phase-local READMEs explaining the pipeline. Phase 4 additionally ships dedicated reproducibility documents:

| Phase | Entry point | Purpose |
|-------|-------------|---------|
| Phase 1 (framework synthesis) | [`p1_framework_synthesis/README.md`](p1_framework_synthesis/README.md), [`p1_framework_synthesis/FREEZE.md`](p1_framework_synthesis/FREEZE.md) | Inductive coding pipeline; per-paper extraction JSONs |
| Phase 2 (systematic review) | [`p2_systematic_review/README.md`](p2_systematic_review/README.md), [`p2_systematic_review/FREEZE.md`](p2_systematic_review/FREEZE.md) | PRISMA SLR pipeline; classification step runner |
| Phase 3 (thematic synthesis) | [`p3_thematic_synthesis/README.md`](p3_thematic_synthesis/README.md), [`p3_thematic_synthesis/FREEZE.md`](p3_thematic_synthesis/FREEZE.md), [`p3_thematic_synthesis/AUDIT_REPORT.md`](p3_thematic_synthesis/AUDIT_REPORT.md) | Per-silo coding, themes, cross-silo synthesis, quantum-advantage triangulation |
| Phase 4 (experiments) | [`p4_experiments/canonical/REPRODUCE.md`](p4_experiments/canonical/REPRODUCE.md), [`p4_experiments/canonical/PRE_REGISTRATION.md`](p4_experiments/canonical/PRE_REGISTRATION.md), [`p4_experiments/canonical/DECISIONS_LOG.md`](p4_experiments/canonical/DECISIONS_LOG.md) | 71-label cohort, Phase-8 grid (2,556 records), seeded for deterministic re-run |

## Phase 4 dry-run

The full Phase 4 pipeline takes multi-day local compute (71 labels × 6 hardware profiles × 3 error budgets × 2 accounting modes = 2,556 cells). For inspection without running the grid:

```powershell
python -m p4_experiments.canonical.run_pipeline --dry-run
```

For full re-execution, follow [`p4_experiments/canonical/REPRODUCE.md`](p4_experiments/canonical/REPRODUCE.md).

## LLM calls and credentials

Phases 1, 2, 3, and the LLM-assisted P4 audit prompts use **Azure OpenAI**. Re-running any LLM-calling step requires user-provided credentials in a local `.env` (see `.env.example` for the schema). The repository does not ship credentials.

You do **not** need credentials to verify the existing artifacts. Every LLM call from the production runs is logged in `audit/logs/` and in the per-phase stage-local logs (`*_calls.jsonl`, `*.raw_response.txt`, `*.meta.json`). These cover the full audit trail referenced from the manuscript's AI Use Declaration appendix.

Re-running the LLM steps will not reproduce identical responses byte-for-byte: the Azure OpenAI seed parameter was not passed at production time, so outputs are subject to model non-determinism even at temperature 0. This limitation is disclosed in [`p3_thematic_synthesis/s4_thematic_coding/campaign_manifest.json`](p3_thematic_synthesis/s4_thematic_coding/campaign_manifest.json) and in the manuscript methodology chapter.

## Verifying claims directly

For the highest-density verification path, see [`docs/ARTIFACT_CLAIM_LEDGER.md`](docs/ARTIFACT_CLAIM_LEDGER.md). It maps every numerical claim in the manuscript to its authoritative source file plus the exact `python -m tools.verify.v*` command that recomputes it.
