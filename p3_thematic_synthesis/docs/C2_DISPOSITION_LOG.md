# C2 Analytical Theme Disposition Log

> **Status note (2026-05-10): historical 2026-04-28 disposition record.** Retained as provenance for the C2 grounding-check dispositions applied to B2 analytical themes; not the current authority. Current truth: [../FREEZE.md](../FREEZE.md) and [../../docs/PROJECT_STATE.yaml](../../docs/PROJECT_STATE.yaml).

Status date: 2026-04-28.

Source: `docs/C2_GROUNDING_REPORT.md`, v2 grounding check.

Rule for manuscript use: no analytical theme with C2 verdict `unsupported` may
enter Chapter 6 as an interpretive claim unless it is revised, demoted, or
dropped here first. `partially_grounded` themes may be retained only with
narrowed wording that matches the sampled evidence.

## Summary

- Analytical themes checked: 45
- Grounded: 2
- Partially grounded: 32
- Unsupported: 11
- Flagged paper instances: 158

## Required Disposition Workflow

For each unsupported theme, choose exactly one disposition:

- `revise`: keep as analytical theme after rewriting the claim to match the
  supporting memos.
- `demote`: retain as a descriptive observation, not an analytical claim.
- `drop`: remove from Chapter 6 and downstream cross-silo synthesis.

## Pending Dispositions By Silo

| Silo | Unsupported themes | Disposition status |
|---|---:|---|
| trading_execution | 2 | pending researcher decision |
| credit_lending | 1 | pending researcher decision |
| fraud_detection | 1 | pending researcher decision |
| derivative_pricing | 2 | pending researcher decision |
| risk_management | 3 | pending researcher decision |
| simulation_monte_carlo | 1 | pending researcher decision |
| portfolio_optimization | 1 | pending researcher decision |
| quantum_ml_finance | 0 | no unsupported analytical themes in v2 |

## Notes For Revision

- Partially grounded themes should have causal or generalizing language narrowed
  before manuscript use.
- Silos with high empty-memo rates need an explicit data-coverage limitation.
- This log should be updated with theme IDs after the researcher reviews each
  silo-level `c2_grounding_check.json` file.