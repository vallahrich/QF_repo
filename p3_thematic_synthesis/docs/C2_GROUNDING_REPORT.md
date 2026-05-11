# Stage C2 — Dual-LLM Grounding Check Report

> **Status note (2026-05-10): generated 2026-04-22 grounding-check report.** Retained as provenance for the dual-LLM C2 grounding check; numerical findings are frozen as of generation time. Current truth: [../FREEZE.md](../FREEZE.md) and [../../docs/PROJECT_STATE.yaml](../../docs/PROJECT_STATE.yaml).

Generated: 2026-04-22T21:12:35.876696+00:00
Verifier model: gpt-5.4 (GPT family) — cross-check against Claude Opus 4.6 that produced B2 themes.
Prompt: `prompts/c2_grounding_check_v1.txt`

## Executive summary

- Total analytical themes checked: **45**
- `grounded`: 2 (4%)
- `partially_grounded`: 32 (71%)
- `unsupported`: 11 (24%)
- Flagged paper instances (across all themes): 158

## Interpreting the pattern

The C2 verifier rubric is deliberately strict: `grounded` requires ≥80% of sampled memos to directly support the theme's *interpretation*, not just the descriptive pattern. Analytical themes are abstractions that by design extend beyond what any single memo says, so a majority `partially_grounded` verdict is consistent with a healthy inductive synthesis. The critical signal is:

1. `unsupported` themes — these must be revised or demoted.
2. Silo-level memo coverage — when a silo's memos are sparse, C2 cannot distinguish theme overreach from data starvation.

## Per-silo rollup

| Silo | Themes | Grounded | Partial | Unsupported | Flagged | Empty memo % | Note |
|------|-------:|---------:|--------:|------------:|--------:|-------------:|------|
| TE | 4 | 1 | 1 | 2 | 12 | 33.9% | The TE analytical layer is partly well grounded: the sampled memos robustly supp… |
| CL | 4 | 0 | 3 | 1 | 17 | 28.0% | The credit-lending analytical layer contains real patterns, but most themes exte… |
| FD | 5 | 0 | 4 | 1 | 20 | 34.9% | The FD analytical layer is directionally grounded on experimental constraints, i… |
| DP | 6 | 0 | 4 | 2 | 25 | 27.1% | The derivative-pricing analytical layer is mixed: the memos consistently support… |
| RM | 6 | 0 | 3 | 3 | 18 | 25.5% | The RM analytical layer is anchored in real recurring memo signals around loadin… |
| SMC | 7 | 1 | 5 | 1 | 24 | 28.3% | The SMC analytical layer is mostly grounded at the level of recurring bottleneck… |
| PO | 6 | 0 | 5 | 1 | 20 | 60.1% | The PO analytical layer captures several real patterns, especially the prevalenc… |
| QML | 7 | 0 | 7 | 0 | 22 | 40.6% | The silo's analytical layer is directionally grounded, but every theme stretches… |

> **Memo coverage caveat**: The `Empty memo %` column is the fraction of memos in the silo's `memos/` directory whose `key_points` field is empty. When this is high (≥40%), C2 verdicts may reflect data starvation rather than theme overreach.

## v1 vs v2 delta

`v1` = first C2 run (`render_c2_prompts.py` trimmed to `key_points` only — confounded by papers on 8-dimension schema).
`v2` = this run (`render_c2_prompts.py` with `dimension_texts` fallback; richer evidence, same rubric/prompt).

| Silo | v1 G/P/U | v2 G/P/U | Δ grounded | Δ unsupported |
|------|:--------:|:--------:|:----------:|:-------------:|
| TE | 0/2/2 | 1/1/2 | +1 | +0 |
| CL | 0/2/2 | 0/3/1 | +0 | -1 |
| FD | 1/4/0 | 0/4/1 | -1 | +1 |
| DP | 0/5/1 | 0/4/2 | +0 | +1 |
| RM | 0/3/3 | 0/3/3 | +0 | +0 |
| SMC | 1/5/1 | 1/5/1 | +0 | +0 |
| PO | 0/0/6 | 0/5/1 | +0 | -5 |
| QML | 0/5/2 | 0/7/0 | +0 | -2 |
| **Total** | 2/26/17 | 2/32/11 | +0 | -6 |

**Interpretation.** The rubric is stable: 6 of 8 silos show ≤1 verdict change between runs (expected rubric noise). PO and QML — the two silos with the highest rate of papers on the raw 8-dimension schema — show large upward moves (PO: 6 unsupported → 1; QML: 2 unsupported → 0). This confirms v1 verdicts for PO/QML were confounded by evidence starvation rather than genuine theme overreach, and validates the dim-fallback fix. The v2 run is the methodologically defensible one; v1 raw responses are preserved under `c2_grounding_check.v1.*` for audit.


For every theme:

- **grounded** → retain interpretation as written; cite evidence as-is.
- **partially_grounded** → narrow the chapter-prose claim to what the sampled evidence directly supports; foot-note the C2 caveat where the original theme had stronger causal wording.
- **unsupported** → one of:
    (a) demote to a descriptive observation (no interpretive claim);
    (b) revise the interpretation so that it is recoverable from the supporting memos;
    (c) drop from the chapter if neither (a) nor (b) is feasible.

Silos with high empty-memo rates (PO, QML) additionally get an explicit *data-coverage limitation* footnote in their chapter sections.

## Next actions

1. Researcher inspects each `unsupported` verdict (per-silo JSON under `s4_thematic_coding/<silo>/themes/c2_grounding_check.json`).
2. For each `unsupported` theme, choose disposition (a / b / c) and record in `docs/C2_DISPOSITION_LOG.md`.
3. Chapter 6 silo sections MUST reflect the disposition — no `unsupported` claim survives into prose unless revised.
