# Copilot Instructions — Quantum Finance Thesis Repository

This repository is the **clean submission workspace** for the MSc thesis *Quantum Computing in Financial Services* (Copenhagen Business School, 2026), authored by Aleix Telesforo (@TelesforoAleix) and Vallahrich (@vallahrich). It is a **frozen hand-in artifact**, not an active development project. Treat every change with that posture.

## Posture

- **Researcher-authored decisions only.** Copilot is an analytical assistant, never an analytical authority. Do not invent verdicts, scores, themes, classifications, QA assessments, or numerical claims. Surface evidence; let the researcher decide.
- **Frozen repository.** Headline numbers, taxonomies, cohorts, and audit ledgers are pinned by the [`FREEZE.md`](../FREEZE.md) at the root and per-folder `FREEZE.md` files. Do not modify pipeline outputs, freeze numbers, audit logs, or claim ledgers without an explicit researcher request. Flag drift instead of silently fixing it.
- **No re-runs.** Never re-execute LLM extraction (P1), classification (P2), thematic coding / S2 extraction / S3 QA (P3), or Phase-8 resource-estimator jobs (P4). The verifier surface uses existing artifacts only.
- **CBS GenAI compliance.** Every LLM-assisted step must be disclosed, auditable, reproducible, and defensible. See [`.github/genai-compliance/SKILL.md`](genai-compliance/SKILL.md). Do not introduce LLM calls into a code path without an audit-trail story.

## Repository Map

Reader-facing entry points (read these before changing anything):

- [`README.md`](../README.md) — hand-in boundary, archive root, verification commands.
- [`FREEZE.md`](../FREEZE.md) — frozen status table and headline numbers.
- [`docs/ARCHITECTURE.md`](../docs/ARCHITECTURE.md) — repository tree.
- [`docs/PIPELINE.md`](../docs/PIPELINE.md) — phase-by-phase flow.
- [`docs/PROJECT_STATE.yaml`](../docs/PROJECT_STATE.yaml) — machine-readable status and cross-phase contracts.
- [`docs/AUDIT_INDEX.md`](../docs/AUDIT_INDEX.md) — audit/log navigation.
- [`docs/METHODOLOGY_DESIGN.md`](../docs/METHODOLOGY_DESIGN.md) — historical methodology scaffold (provenance only; not the controlling current method).
- [`CONTRIBUTING.md`](../CONTRIBUTING.md) — branch / commit / PR rules.

Pipeline phases (each has its own `README.md` and `FREEZE.md`):

| Phase | Folder | Movement | Output |
|---|---|---|---|
| P1 Framework synthesis | `p1_framework_synthesis/` | Inductive | Problem-domain × solution-approach taxonomy and codebook. |
| P2 Systematic review | `p2_systematic_review/` | Deductive | 777 processed papers; 755 active downstream subset. |
| P3 Thematic synthesis | `p3_thematic_synthesis/` | Inductive within-silo + QA layers | 8 active silos; S1–S6 spine. |
| P4 Experiments | `p4_experiments/` | Empirical | 71-label cohort; 2,556 Phase-8 resource-estimator records. |

Cross-cutting:

- `shared/` — taxonomies, schemas, bridge tables, configs.
- `tools/verify/` — verification gates (V1 schema, V2 consistency, V3 trace-label, V9 bridge).
- `tools/rag/` — retrieval helper (read-only against the frozen corpus).
- `logs/` — reviewer signpost only; canonical logs live phase-locally.

## Skills (Copilot Chat)

The `.github/` subfolders are the **AI-Use Disclosure Bundle** referenced in Chapter 4 §4.7 and the AI Use Declaration appendix. Each is a researcher-invoked workflow scaffold, not an autonomous agent. See [`.github/README.md`](README.md) for classification.

| Skill | Class | Use when |
|---|---|---|
| [`evidence-navigator`](evidence-navigator/SKILL.md) | Retrieval / workflow | Finding pipeline artefacts; read-only retrieval. |
| [`manual-review`](manual-review/SKILL.md) | Retrieval / workflow | PDF manuscript review notes capture → pipeline → fix. |
| [`p3-r1-review`](p3-r1-review/SKILL.md) | Retrieval / workflow | Per-paper R1 triangulation review for P3/s4. |
| [`methodology-guard`](methodology-guard/SKILL.md) | Governance / self-audit | Validating research-design integrity. |
| [`genai-compliance`](genai-compliance/SKILL.md) | Governance / self-audit | Auditing LLM-assisted steps against CBS pillars. |
| [`research-sparring`](research-sparring/SKILL.md) | Analytical sparring | Pre-writing argument development; markdown handoffs only. |

When a user request matches a skill's "When to Use" section, invoke that skill rather than improvising.

## Style and Tooling

- **Language**: Python (see [`pyproject.toml`](../pyproject.toml)). Prefer standard library + already-imported dependencies; do not add new dependencies without asking.
- **Shell**: PowerShell (`pwsh`) on Windows. Use `;` to chain, prefer `Get-ChildItem`/`Test-Path` over POSIX aliases.
- **Tests**: `python -m pytest` from the repo root. Verification entry point: `pwsh .\verify.ps1`.
- **Branching**: never commit to `main`; one branch per feature/fix; PR with squash-merge; no force-push. Branch prefixes: `feature/`, `fix/`, `docs/`, `chore/`. Commit style: imperative (`feat:`, `fix:`, `docs:`, `chore:`).
- **No new top-level folders** without an explicit request.
- **Documentation**: do not add markdown change-logs or summary files unless asked; the freeze files and audit ledgers are the source of truth.

## What to Avoid

- Editing files under `s1_extractions/`, `s2_coding/`, `s2_quantitative/output/`, `s3_quantum_advantage/`, `s4_thematic_coding/`, `s5_cross_silo/`, `p4_experiments/canonical/`, or any `output/` / `audit/` subtree without an explicit researcher request.
- Re-running LLM-backed scripts; "rebuilds" must be the deterministic ones already documented (e.g. `p1_framework_synthesis/scripts/build_review_data_done.py`).
- Touching `.venv/`, `__pycache__/`, `.pytest_cache/`, `tools/rag/.chroma/`, or anything in the external source archive at `C:\QF_submission_packages\source_internal_archive\…`.
- Inventing PD codes, silo names, paper IDs, or numbers. Cross-check against [`shared/config/unified_taxonomy.json`](../shared/config/unified_taxonomy.json), [`shared/config/silo_inclusion.json`](../shared/config/silo_inclusion.json), and the relevant `FREEZE.md`.
- Bypassing the verifier (`--no-verify`, skipping `pytest`) or amending shared history.

## When in Doubt

Ask the researcher. The thesis is under examiner scrutiny: a flagged uncertainty is always preferable to a silent change.
