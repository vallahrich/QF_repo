---
name: genai-compliance
description: "Validate compliance with CBS generative-AI guidelines and academic integrity norms for LLM-assisted research. Use when: writing the AI declaration appendix, auditing LLM-assisted pipeline steps, verifying audit trails, preparing for examiner questions on AI bias/reliability, or before thesis submission. Ensures every use of GenAI in the thesis is transparent, reproducible, and defensible."
argument-hint: "Pass 'full' for complete compliance audit, 'declaration' for the AI-use appendix check, 'audit-trail' for provenance verification, 'reproducibility' for prompt/model logging, or a phase name for phase-specific review"
---

# GenAI Compliance — Responsible Use & Disclosure

Validate that every use of generative AI in this thesis is **disclosed, auditable, reproducible, and defensible** under CBS academic integrity rules and examiner scrutiny. This skill is the transparency conscience of the project: it verifies that the LLM's role is correctly framed and documented, not silently embedded.

## When to Use

- Drafting or reviewing the **AI Use Declaration** appendix
- Auditing any pipeline step that calls an LLM (P1 extraction, P2 classification, P3 thematic coding, P4 circuit drafting)
- Before thesis submission — full compliance sweep
- Pre-defence preparation — anticipating examiner questions on AI bias, reliability, and reproducibility
- When adding a new LLM-assisted step — checking it meets compliance criteria before deployment
- Reviewing the methodology chapter's treatment of LLM use

## Canonical References

1. **CBS thesis guidelines** on generative-AI use (declaration, disclosure, academic integrity).
2. **`docs/METHODOLOGY_DESIGN.md`** — Section on LLM integration principles.
3. **`p1_framework_synthesis/audit-trail.md`** — Reference template for LLM-proposal-vs-researcher-decision documentation.
4. **Project principle**: *LLM as analytical assistant, not analytical authority. Researcher makes all final decisions.*

## Compliance Pillars

Every LLM use must satisfy **five pillars**. Flag any violation as ❌ Broken; partial satisfaction as ⚠️ Drift.

### Pillar 1 — Declaration
The AI Use Declaration in `manuscript/04_Appendix/` must:
- State **which** GenAI tools were used (model name + provider + version/date).
- State **where** they were used (which phase, which step, which task).
- State **how** they were used (extraction, proposal generation, drafting, code assistance).
- State **what the researcher did** to validate / override the output.
- Be signed and dated by both authors.

Red flag: Declaration says "AI was used to assist with writing" without specifying model, scope, or validation procedure.

### Pillar 2 — Role Framing ("Assistant, Not Authority")
In the thesis text and code comments, the LLM must be framed as:
- Producing **candidate** outputs (extractions, groupings, drafts).
- Subject to **researcher review** before any output enters the analytical record.
- Never making **final categorisation, inclusion, exclusion, or interpretive** decisions unilaterally.

Red flag: Any claim of the form "the LLM classified X" without a corresponding "the researcher verified/corrected X".

### Pillar 3 — Audit Trail (Provenance)
Every LLM-assisted step must leave a record allowing a third party to reconstruct:
- **Input**: what text/data was sent to the model.
- **Prompt**: the exact prompt template used (committed to the repo, not ephemeral).
- **Output**: the raw model response (logged, not just the post-processed version).
- **Decision**: what the researcher accepted, modified, or rejected — with rationale.

Expected artifacts:
- `p1_framework_synthesis/audit-trail.md` — Phase 1 proposals vs. decisions.
- `p2_systematic_review/s2_classification/prompts/` — all prompts version-controlled.
- `logs/*_llm_client.jsonl` — raw LLM call logs (request/response pairs).
- `logs/*_phase*_extraction.jsonl` — phase-level processing logs.

Red flag: A step produces outputs but no logs exist, or logs omit the prompt / raw response.

### Pillar 4 — Reproducibility
For any LLM call to be reproducible (to the extent possible given model non-determinism):
- **Model identity** must be pinned: provider + model name + version/date.
- **Prompt template** must be committed and referenced by path in the methodology.
- **Sampling parameters** must be recorded: temperature, top_p, seed (where supported), max_tokens.
- **Cached vs. fresh** calls must be distinguishable in logs.
- **Model non-determinism** must be acknowledged in the methodology chapter (Section on limitations).

Red flag: Methodology refers to "GPT-4" or "Claude" without a version, or no temperature/seed is recorded.

### Pillar 5 — Validation & Bias Mitigation
Every LLM-assisted analytical step must include at least one of:
- **Human spot-check sample** with documented accuracy rate.
- **Inter-rater reliability** measure (if two researchers code overlapping samples).
- **Adversarial / edge-case testing** documented.
- **Known-answer validation** (e.g., LLM classification vs. ground-truth on pilot papers).
- **Bias audit**: did the researcher actively look for systematic LLM errors (e.g., favouring certain categories, over-fitting to prompt examples)?

Red flag: LLM was used on ~1,500 papers but no validation sample, no error rate, no bias discussion.

## Procedure

### Step 1 — Read State & Declaration

1. Read `docs/PROJECT_STATE.yaml` to identify which phases use LLMs.
2. Check whether `manuscript/04_Appendix/` contains an AI Use Declaration. If missing, flag ❌.
3. Read `docs/METHODOLOGY_DESIGN.md` sections on LLM integration.

### Step 2 — Per-Phase LLM Inventory

For each phase that uses LLMs (typically P1, P2, P3), produce a row:

| Phase | Step | Task | Model | Prompt Location | Log Location | Validated? |
|-------|------|------|-------|-----------------|--------------|------------|
| P1 | extraction | structured profile | ? | `p1_.../prompts/` | `logs/2026-04-*_phase1_*.jsonl` | audit-trail.md |
| P2 | s2_classification | 6-step coding | ? | `p2_.../s2_classification/prompts/` | `logs/*_llm_client.jsonl` | spot-check? |
| P3 | problems | thematic coding | ? | ? | ? | ? |

Flag any `?` that cannot be resolved from the repository.

### Step 3 — Pillar-by-Pillar Audit

Iterate the five pillars against each row. For each combination (phase × pillar), record: ✅ / ⚠️ / ❌ with a one-line justification and evidence path.

### Step 4 — Declaration Appendix Check

If the AI Use Declaration exists, verify it contains:
- [ ] Model names + versions + dates
- [ ] Explicit scope per phase (not just "used throughout")
- [ ] Explicit validation procedure per phase
- [ ] Explicit statement that researchers made all final decisions
- [ ] Acknowledgement of non-determinism / limitations
- [ ] Author signatures + dates

### Step 5 — Examiner-Question Readiness

Rehearse answers to the common GenAI examiner questions. For each, confirm the thesis contains a cited answer:

1. *"Which model did you use, and why that one?"* — Methodology §X
2. *"How do you know the LLM didn't bias your taxonomy?"* — Audit trail + Pillar 5 validation
3. *"What's the error rate of the LLM classification?"* — Pilot validation in Methodology or Appendix
4. *"How reproducible is your pipeline?"* — Prompts in repo + model versions + parameters
5. *"Could another researcher replicate your study?"* — Methodology reproducibility statement
6. *"What if the model was deprecated tomorrow?"* — Prompts + logs preserve the record; raw outputs stored

Flag any question that the current thesis cannot answer cleanly.

### Step 6 — Output

Produce a structured report:

```
GenAI Compliance Report — <date>
=================================

Summary: <N> ✅  <N> ⚠️  <N> ❌

Pillar 1 — Declaration:       [status] — [evidence / gap]
Pillar 2 — Role Framing:      [status] — [evidence / gap]
Pillar 3 — Audit Trail:       [status] — [evidence / gap]
Pillar 4 — Reproducibility:   [status] — [evidence / gap]
Pillar 5 — Validation/Bias:   [status] — [evidence / gap]

Per-phase matrix: [...]

Required actions (ranked by severity):
  ❌ 1. ...
  ⚠️ 2. ...
  💡 3. ...

Examiner-question readiness: <ready/at-risk list>
```

## Invariants (Always Check)

1. **No undeclared LLM use.** Every LLM call in the codebase must map to a declared use in the appendix.
2. **No missing prompts.** Every prompt referenced in the methodology must exist as a committed file.
3. **No silent model swaps.** If the model changed mid-project, the methodology must document the switch date, affected outputs, and any re-validation.
4. **No anthropomorphising.** The thesis must not say the LLM "understood", "decided", "judged", or "concluded". Use "produced", "proposed", "generated", "output".
5. **No training-data contamination claims without evidence.** If the thesis asserts the LLM was not trained on the target corpus, this must be justified or framed as a limitation.
6. **Student authorship.** The declaration must confirm that analytical decisions, writing, and interpretation are the researchers' own work, with GenAI limited to assistance roles.

## Common Violations to Catch

- Methodology chapter uses "we classified" when in fact the LLM classified and the researcher spot-checked — fix the framing.
- Prompts are in the repo but not referenced from the methodology — add citations.
- Logs exist but contain only post-processed outputs, not raw responses — document the limitation.
- The AI declaration is a boilerplate sentence rather than a detailed per-phase account.
- No validation sample was taken, or it was taken but the error rate is not reported.
- Model temperature is unset/default and undocumented.
- The thesis reports LLM outputs as findings without the "proposed / verified" two-step framing.

## Cross-Skill Integration

- **methodology-guard**: GenAI compliance complements methodology integrity — a methodologically sound step can still be non-compliant if undeclared.
- **consistency-check**: Compliance depends on cross-phase consistency between declared use, actual use, and log evidence.
- **academic-writer**: When drafting the AI declaration or methodology LLM sections, the academic-writer skill handles prose; this skill handles substance.
- **professor-review**: A professor review of the methodology chapter should surface compliance gaps; use this skill proactively to close them first.

## Escalation

If any ❌ is found in the declaration or audit trail, **do not proceed with thesis submission** until resolved. Missing provenance cannot be reconstructed after the fact and is the single biggest defence vulnerability for an LLM-assisted thesis.
