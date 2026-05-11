# B1 / B2 Theme Quality Rubric

> **Purpose**: Quality gate for every B1 descriptive-theme batch and every B2
> analytical-theme silo output. Applied after automated L-B1/L-B2 schema
> validation and before researcher review gates.
>
> **Author**: methodology-guard skill (drafted).
> **Approver**: researcher (sign below).
> **Status**: DRAFT — must be committed and signed BEFORE first production call.

---

## Origin & grounding

This rubric operationalises the Phase 3 methodological commitments stated in
`docs/METHODOLOGY_DESIGN.md` and the Phase 3 section of
`p3_thematic_synthesis/docs/PRODUCTION_ARCHITECTURE.md`. Specifically:

- **Thomas & Harden (2008)**: themes must emerge bottom-up from coded
  evidence; analytical themes must go beyond description to interpretation.
- **Cruzes & Dybå (2011)**: thematic synthesis requires visible provenance
  from theme → code → text span.
- **CBS GenAI Pillar 5 (validation/bias)**: every LLM-assisted analytical
  step needs a documented quality check.
- **Phase 3 fresh within-silo coding**: themes must NOT be restatements of
  Phase 1 taxonomy codes (PD-01..PD-10, SA-01..SA-11).

A theme output that scores below the gate on this rubric is treated as a
methodology risk, not merely a stylistic issue. Re-running is cheaper than
defending a weak chapter at oral defence.

---

## Scoring scale

Every criterion is scored on a 1–5 integer scale:

| Score | Meaning |
|:---:|---|
| 5 | Excellent. No concerns. Would survive adversarial examiner questioning. |
| 4 | Good. Minor issues that do not affect defensibility. |
| 3 | Acceptable floor. Some issues but the output is usable after editing. |
| 2 | Poor. Issues that would weaken a thesis section. Rerun recommended. |
| 1 | Unacceptable. Must not feed downstream. Rerun required. |

**Gate (per silo)**: mean over all scored criteria ≥ 4.0 AND no individual
criterion below 3. Fail → revise prompt and rerun that silo's B1 (or B2).

---

## Rubric — five criteria

### C1. Theme coherence  (applies: B1, B2)
*Does each theme have a clear, specific, falsifiable claim that is internally
consistent across its evidence?*

| Score | Indicators |
|:---:|---|
| 5 | Every theme label + description names a specific pattern with a clear scope. No grab-bag themes. |
| 4 | Most themes specific; at most 1 could be split or sharpened. |
| 3 | Several themes are broad but usable. |
| 2 | Multiple themes are umbrella labels covering disparate claims. |
| 1 | Themes are vague ("various methods", "different approaches") and uninformative. |

Examiner question this defends against: *"What does theme X actually claim that a reader could disagree with?"*

### C2. Grounding quality  (applies: B1, B2)
*Do `supporting_papers` and `support_code_ids` actually substantiate the
theme? Is every cited code ID valid (exists in that paper's A1 codes or the
overlay) and relevant to the theme?*

Check procedure (researcher or automated spot-check, 3 themes per silo):
1. Pick a theme; pick 2 of its `supporting_papers`.
2. Pull those papers' `support_code_ids` from the theme.
3. Open the A1 `codes/*.jsonl` and verify each code's text span is relevant.
4. Score by what fraction of spot-checks pass.

| Score | Indicators |
|:---:|---|
| 5 | 100% of spot-checks substantiate the theme. |
| 4 | ≥80% substantiate; 1 weak link but not contradicted. |
| 3 | ≥60% substantiate. |
| 2 | <60% substantiate. |
| 1 | Phantom code IDs or manifestly irrelevant grounding. |

Examiner question this defends against: *"Show me the exact sentence in paper X that supports theme Y."*

### C3. Interpretive depth  (applies: B2 analytical themes only)
*Does each analytical theme add a genuine higher-order interpretation beyond
the descriptive themes it merges? Does it explain WHY or what it MEANS?*

| Score | Indicators |
|:---:|---|
| 5 | Every analytical theme gives a non-obvious interpretation with an explicit `implication`. |
| 4 | Most are interpretive; 1 is a restatement of a descriptive theme with a different label. |
| 3 | Half are genuinely analytical; half are re-labelled descriptives. |
| 2 | Most analytical themes merely rename descriptives. |
| 1 | No genuine analytical move. The output is just a cleaned-up descriptive set. |

Examiner question this defends against: *"What is the analytical contribution of Chapter N beyond summarising what papers say?"*

### C4. Counter-evidence validity  (applies: B2 analytical themes only)
*For each analytical theme, is the counter-evidence real, specific, and in-scope? Or is it hallucinated/generic?*

Check procedure (automated L-B2.5 + researcher spot-check):
1. Every `counter_evidence[*].paper_id` is in the silo's paper set (automated).
2. The cited `reason` names a concrete claim of that paper that contests the theme (researcher spot-check: sample 2 per silo).
3. If `no_counter_evidence_reason` is used, it is justified (not a lazy default).

| Score | Indicators |
|:---:|---|
| 5 | All counter-examples in scope + spot-check confirms the claim; any `no_counter_evidence_reason` is plausible. |
| 4 | 1 weak counter-example but no fabrications. |
| 3 | 1 out-of-scope or generic counter-example. |
| 2 | Multiple weak or generic counter-examples. |
| 1 | Fabricated paper_id OR multiple themes using `no_counter_evidence_reason` as a dodge. |

Examiner question this defends against: *"Which papers contradict your theme, and how do you handle that contradiction?"*

### C5. Anti-anchoring  (applies: B1, B2)
*Do the themes emerge inductively from the memos, or are they restatements
of Phase 1 categories (PD-01..10, SA-01..11)?*

Check procedure:
1. **Keyword scan** (automated): theme labels must not contain the silo name
   verbatim as the main descriptor or any PD/SA code or its canonical label.
2. **Semantic crosswalk** (researcher): for each theme, is it a genuine
   emergent pattern, a paraphrase of a Phase 1 category, or a partial overlap?

| Score | Indicators |
|:---:|---|
| 5 | 0 keyword matches; ≤10% of themes marked `partial` on crosswalk; 0 marked `restatement`. |
| 4 | 0 keyword matches; ≤20% marked `partial`; 0 `restatement`. |
| 3 | 0 keyword matches; some `partial` themes but clear inductive content dominates. |
| 2 | Keyword matches present, or >20% `restatement`. |
| 1 | Themes largely mirror the Phase 1 taxonomy for this silo. |

Examiner question this defends against: *"How do you know Phase 3 produced genuinely new insights rather than re-labelling Phase 1?"*

---

## Rubric application procedure

1. **After L-B1 passes** for a silo's full B1 output: researcher scores C1, C2, C5 on the aggregated B1 themes. Time budget: ~20 min per silo.
2. **After L-B2 and L-B2.5 pass** for a silo's B2 output: researcher scores C1, C2, C3, C4, C5 on the B2 output. Time budget: ~30 min per silo.
3. **Scorecard written** to `<silo>/themes/QUALITY_SCORECARD.md` with scores, one-line justification per criterion, overall pass/fail, and disposition (`accept`, `revise_and_rerun`, `escalate`).
4. **On fail**: revise the prompt (document the change as `_v2.txt`), delete the failed output, rerun. Repeat until the gate is met.

**Recording**: every scored output's scorecard is committed to the repo. The methodology chapter cites the aggregate pass rate and median scores in a footnote or appendix table.

---

## Defensibility statement

This rubric, applied before any B2 output feeds R2 chapter writing, gives the
thesis a defensible answer to the question:

> *"How did you ensure the LLM-assisted themes are trustworthy before you
> built a chapter on them?"*

Answer: *"Every theme output was scored against a pre-committed five-criterion
rubric drafted from Thomas & Harden (2008) and Cruzes & Dybå (2011). Outputs
below threshold were not accepted; the prompt was revised and the output
regenerated. All scorecards are committed in the repository."*

---

## Signatures

- Drafted by: methodology-guard skill, 2026-04-22
- **Approved by researcher**: Aleix Telesforo, 2026-04-22 
- Prompt versions at approval: `b1_descriptive_themes_v1.txt`, `b2_analytical_themes_v1.txt`
- Applies to: all B1 batch outputs and all B2 silo outputs from this approval date forward
- Revision policy: any material change to the rubric requires re-signing and, if already-scored outputs exist, re-scoring them under the new version
