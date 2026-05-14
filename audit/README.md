# `audit/` — AI-Use Audit Trail

This folder holds the merged **AI-Use Disclosure Bundle** for the thesis: every
LLM call from both researchers' production sessions, across all four pipeline
phases.

The audit ledger here is the *root-level* aggregate. **Most evidence lives
phase-locally** (e.g. raw responses next to the artefact they produced); see
the cross-references below.

## Folder Map

| Path | Contents |
|---|---|
| [`logs/`](logs/) | Merged LLM-call JSONL + supporting `*.log` files. See [`logs/README.md`](logs/README.md) for file-naming patterns. |

## How To Navigate

1. Start with [`../docs/AUDIT_INDEX.md`](../docs/AUDIT_INDEX.md) — the
   examiner-facing index that maps every log family to the questions it
   answers and the schema it uses.
2. Use [`logs/README.md`](logs/README.md) for file-naming and provenance of
   the root-level bundle (the union of both researchers' execution sessions).
3. For per-phase logs that are not duplicated here (raw responses, prompt
   logs, sweep records), follow the per-phase pointers below.

## Phase-Local Audit Pointers

| Phase | Local audit/log surface |
|---|---|
| P1 | [`../p1_framework_synthesis/audit-trail.md`](../p1_framework_synthesis/audit-trail.md), `../p1_framework_synthesis/s1_extractions/` |
| P2 | [`../p2_systematic_review/processing_log.json`](../p2_systematic_review/processing_log.json), [`../p2_systematic_review/output/audit/`](../p2_systematic_review/output/audit/), [`../p2_systematic_review/s1_slr/03_screening/`](../p2_systematic_review/s1_slr/03_screening/) |
| P3 | [`../p3_thematic_synthesis/AUDIT_REPORT.md`](../p3_thematic_synthesis/AUDIT_REPORT.md), `../p3_thematic_synthesis/s4_thematic_coding/<silo>/themes/*.raw_response.txt`, `../p3_thematic_synthesis/s2_quantitative/output/audit/` |
| P4 | [`../p4_experiments/canonical/reports/audit/`](../p4_experiments/canonical/reports/audit/), [`../p4_experiments/canonical/DECISIONS_LOG.md`](../p4_experiments/canonical/DECISIONS_LOG.md) |

## Compliance

This audit bundle is the evidence base for the thesis's **AI Use Declaration**
(manuscript appendix) under CBS GenAI policy. Every LLM-assisted step in the
pipeline is disclosed, auditable, and reproducible from these files plus the
prompt templates retained under `<phase>/prompts/`.

The verifier (`pwsh ./verify.ps1`) and the test surface (`python -m pytest`)
do **not** call any LLM; they read existing artefacts only.
