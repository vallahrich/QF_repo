# Stage C3 — Theme-to-Literature Crosswalk (Quality Rubric)

**Purpose.** Position each of our analytical themes against prior review articles in the P2 corpus. The crosswalk strengthens literature positioning (a CBS *Critical* rubric dimension) and exposes where our analysis confirms, extends, or challenges established reviews.

**Status: v1 — pre-committed before the LLM call that produces `s5_cross_silo/c3_crosswalk.json`.**

Signed: 2026-04-22 (single-researcher audit trail anchor).
Prompt file: `p3_thematic_synthesis/prompts/c3_theme_literature_crosswalk_v1.txt`.
Model intended: Claude Opus 4.6 (same model family as B2/C1; justified because this is a positioning task within the single inductive synthesis, not a cross-check).

---

## Inputs

1. **Shortlist of 16 analytical themes** (`s5_cross_silo/crosswalk_shortlist.json`) — 2 grounded + 10 top-partial + 4 silo-balance backfill.
2. **16 review/survey articles** from the P2 corpus (filtered by title keywords: `review | survey | overview | state of the art | taxonomy | landscape | systematic`). For each, we supply the structured sections: abstract summary, findings, quantum advantage claim, limitations, key ideas, contradictions.

## Output schema (per theme)

For each of the 16 themes, the model returns an array `crosswalk` of 2–3 entries. Each entry references ONE prior review by `paper_id` and classifies the relationship as exactly one of:

- `confirms` — the prior review states essentially the same claim (the theme re-observes something the review already surfaces).
- `extends` — the prior review touches the claim but this theme adds specificity, a new domain, or a sharper causal mechanism.
- `contradicts` — the prior review asserts the opposite or reports evidence against this theme's claim.
- `complements` — the prior review addresses a related aspect without direct overlap; the theme and review jointly characterise the landscape.

Plus a `rationale` (2–4 sentences), a `quoted_claim` (≤40 words verbatim from the review section), and a `stance_confidence` (`high`/`medium`/`low`).

## C-series rubric dimensions (self-score by researcher on v2)

| # | Dimension | Target |
|---|-----------|:------:|
| C3-1 | **Coverage**: every shortlisted theme has ≥2 crosswalk entries | 16/16 |
| C3-2 | **Stance discrimination**: not all `complements`; `confirms` / `extends` / `contradicts` each used where warranted | ≥2 of each |
| C3-3 | **Quote fidelity**: every `quoted_claim` is traceable verbatim to the review's extracted section text | 100% |
| C3-4 | **Cross-silo spread**: crosswalk entries drawn from ≥6 distinct review articles (to avoid single-survey dominance) | ≥6 |
| C3-5 | **Defensive flags**: when the review's stance differs from ours, a `contradicts` is used rather than a soft `complements` | present where due |

## Acceptance procedure (L-C3 validator)

A Python validator (`scripts/validate_and_persist_c3.py`) enforces structural constraints:

1. Every shortlisted `theme_id` appears exactly once in the output.
2. Each theme has 2–3 crosswalk entries.
3. Every `review_paper_id` referenced is in the provided review pool (no hallucinated papers).
4. Every `relationship` is one of the 4 allowed values.
5. `quoted_claim` length ≤ 40 words.

Any L-C3 failure blocks persistence and requires re-run. Researcher then scores C3-1 through C3-5 manually.

## Disposition rules (downstream)

- `contradicts` entries flag where our chapter must engage counter-evidence explicitly in prose.
- `confirms` entries enable "prior reviews X and Y observe the same pattern" framing, strengthening literature positioning.
- `extends` entries are the clearest contribution claim — "this thesis extends [review]'s observation by …"
- `complements` entries are valid but weaker; ≥2/3 of total entries should be not-complements.

---

## Methodological notes for the defence

The crosswalk is an explicit positioning exercise. It is not re-coding (P1 taxonomy) nor re-classifying (P2) nor re-theming (B2). It answers the question: "where does this thesis sit relative to the prior literature?" The rubric enforces that the positioning is defensible by quote-traceability (C3-3) and by honest use of the `contradicts` stance where the literature disagrees (C3-5).
