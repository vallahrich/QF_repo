# Stage B — L3 propagation audit summary (relevance-aware)

_Generated: 2026-05-06T18:23:20+00:00_  
_Script: `p3_thematic_synthesis/scripts/build_l3_propagation.py`_

## Method

Every AT and DT in the 8 active silos has been annotated in place (in
`b1_batch_*.json` and `b2_silo_themes.json`) with two new fields:

- `l3_flags`: per-paper flag breakdown including the L3-attributed memo
  dimension and a `relevant` bit per flag (whether that dimension is one
  the theme actually relies on).
- `l3_unflagged_support_ratio`: four parallel views of
  `(unflagged_supporting_papers / total_supporting_papers)`.

### The four views

| View | What counts as flagged | Corpus base rate | Use |
|---|---|---|---|
| `any` | Any L3 problem at all | 98.2 % | Saturated; documentation only. |
| `any_major` | Any major-severity problem | 91.7 % | Saturated; documentation only. |
| `relevant` | Any flag whose memo dimension overlaps the theme's relied set (or is unknown). | Theme-specific | Filters out limitation-section nags etc. |
| `relevant_major` | Relevant + major. | Theme-specific | **Recommended primary view for R1 evidence packs.** |

Dimension attribution: each flag's `memo_sentence` is matched against
the per-dimension `text` field of the paper's A2 memo (longest 60-char
window; threshold = 40 chars). Unmatched flags are tagged
`dimension_unknown` and treated *conservatively as relevant*.

### No retain/queue verdict at this layer

The original `unflagged > 0.5 = retained, else queued` rule was designed
when L3 was a 16.5 % sparse sample. Under the new 100 %-coverage mini+v3
safeguard the rule is non-discriminative even on `relevant_major` (the
model's tendency to flag every limitation as `MISSING_LIMITATION` keeps
the base rate high). Per-theme verdicts are therefore deferred to the R1
stratified review, which uses the per-paper `l3_flags` lists as evidence
packs.

## Per-silo evidence

Each row reports the *count of supporting papers* under each view, then
the *count of themes whose every supporting paper is relevant-major-flagged*
(saturated themes — likely highest-priority for R1 attention).

| Silo | ATs | DTs | AT support flagged (any / any-major / relevant / relevant-major) | DT support flagged (any / any-major / relevant / relevant-major) | ATs fully rel-major flagged | DTs fully rel-major flagged |
|---|---:|---:|---|---|---:|---:|
| credit_lending | 4 | 20 | 53 / 51 / 43 / 29 (of 53) | 134 / 130 / 108 / 70 (of 134) | 0 | 1 |
| derivative_pricing | 6 | 34 | 94 / 92 / 79 / 59 (of 94) | 246 / 239 / 200 / 140 (of 246) | 0 | 3 |
| fraud_detection | 5 | 24 | 130 / 127 / 104 / 65 (of 131) | 234 / 228 / 178 / 104 (of 236) | 0 | 0 |
| portfolio_optimization | 6 | 32 | 82 / 69 / 68 / 49 (of 82) | 245 / 211 / 186 / 122 (of 245) | 1 | 3 |
| quantum_ml_finance | 7 | 38 | 74 / 69 / 67 / 37 (of 74) | 336 / 311 / 273 / 153 (of 338) | 0 | 0 |
| risk_management | 6 | 29 | 140 / 133 / 131 / 105 (of 142) | 211 / 197 / 195 / 155 (of 215) | 0 | 4 |
| simulation_monte_carlo | 7 | 36 | 155 / 152 / 147 / 125 (of 155) | 225 / 221 / 215 / 177 (of 225) | 0 | 8 |
| trading_execution | 4 | 21 | 27 / 26 / 24 / 18 (of 27) | 155 / 151 / 125 / 81 (of 155) | 0 | 0 |
| **TOTAL** | **45** | **234** | **755 / 719 / 663 / 487** (of **758**) | **1786 / 1688 / 1480 / 1002** (of **1794**) | **1** | **19** |

**Relevance filter effect**: AT-supporting flagged paper-edges drop from **719** (any-major) to **487** (relevant-major) — a **32.3 %** reduction. DT edges drop from **1688** to **1002** (40.6 % reduction).

## Per-silo manifests

- `p3_thematic_synthesis/s4_thematic_coding/credit_lending/themes/l3_propagation.json`
- `p3_thematic_synthesis/s4_thematic_coding/derivative_pricing/themes/l3_propagation.json`
- `p3_thematic_synthesis/s4_thematic_coding/fraud_detection/themes/l3_propagation.json`
- `p3_thematic_synthesis/s4_thematic_coding/portfolio_optimization/themes/l3_propagation.json`
- `p3_thematic_synthesis/s4_thematic_coding/quantum_ml_finance/themes/l3_propagation.json`
- `p3_thematic_synthesis/s4_thematic_coding/risk_management/themes/l3_propagation.json`
- `p3_thematic_synthesis/s4_thematic_coding/simulation_monte_carlo/themes/l3_propagation.json`
- `p3_thematic_synthesis/s4_thematic_coding/trading_execution/themes/l3_propagation.json`

## Source-file annotations

Each AT and DT in `b1_batch_*.json` and `b2_silo_themes.json` now carries
`l3_flags` (with per-flag dimension + relevance) and
`l3_unflagged_support_ratio` (with the four views above). The original
`theme_id`, `theme_label`, `description`/`interpretation`, `supporting_papers`,
`support_code_ids`, `grounded_in`, `counter_evidence`, and `implication`
fields are unchanged — annotation is strictly additive.
