# `output/ab_test_results/` — Pipeline selection A/B tests

Side-by-side outputs comparing three candidate classification pipelines on the same 3 sample papers (`29cfef5a271e`, `57294220386e`, `a143717759af`):

- `*_2call.json` — Pipeline A (single 2-call extraction).
- `*_6step.json` — Pipeline B (6 sequential calls, no caching).
- `*_6step_cached.json` — **Pipeline C** (6 steps with cached prefix prompts) — the **production pipeline** used to generate all 777 outputs in [`../processed/`](../processed/).
- `comparison_summary.json` — aggregated comparison metrics that drove the Pipeline C selection.

## Status

Frozen — pipeline selection complete. Retained for reproducibility of the choice.
