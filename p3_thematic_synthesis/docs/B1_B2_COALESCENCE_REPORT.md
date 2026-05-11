# B1/B2 Coalescence Report

> **Status note (2026-05-10): generated 2026-04-22 pipeline-run report.** Retained as provenance for the B1/B2 coalescence outputs at generation time; not the current authority. Current truth: [../FREEZE.md](../FREEZE.md) and [../../docs/PROJECT_STATE.yaml](../../docs/PROJECT_STATE.yaml).

**Generated**: 2026-04-22 (autonomous pipeline run)

## 1. Per-silo summary

| Silo | Papers | B1 themes | B2 descriptive | B2 analytical | B1 model | Sanitization |
|------|-------:|----------:|---------------:|--------------:|----------|--------------|
| Trading & Execution | 43 | 11 | 10 | 4 | `claude-opus-4.6` | — |
| Credit & Lending | 63 | 12 | 8 | 4 | `claude-opus-4.6-1m` | — |
| Fraud Detection | 105 | 15 | 9 | 5 | `claude-opus-4.6-1m` | — |
| Derivative Pricing | 144 | 20 | 14 | 6 | `claude-opus-4.6-1m` | — |
| Risk Management | 165 | 18 | 11 | 6 | `claude-opus-4.6-1m` | 1 edits / 0 dropped |
| Simulation & Monte Carlo | 218 | 20 | 16 | 7 | `claude-opus-4.6-1m` | — |
| Portfolio Optimization | 251 | 19 | 13 | 6 | `claude-opus-4.6-1m` | 2 edits / 0 dropped |
| Quantum ML in Finance | 313 | 24 | 14 | 7 | `claude-opus-4.6-1m` | — |
| **Total** | **1302** (654 unique; multi-silo papers counted once per silo) | **139** | **95** | **45** | — | — |

## 2. Model routing

| Model | Used for | Rationale |
|-------|----------|-----------|
| `claude-opus-4.6` (200K) | trading_execution, credit_lending (B1); all B2 | Pilot + prompts ≤ 200K tokens |
| `claude-opus-4.6-1m` (1M) | fraud_detection, derivative_pricing, risk_management, simulation_monte_carlo, portfolio_optimization, quantum_ml_finance (B1) | Single-batch synthesis on payloads 217–634K tokens. Same underlying model; only context window differs. |

## 3. Validation outcomes

- **L-B1** (hard, structural): all 8 silos passed. 3 silos required code-ID sanitization (invalid code IDs stripped; no themes dropped):
  - risk_management: 1 theme had 2 confabulated code IDs (C-046, C-047) for paper 95a7b64bceac.
  - portfolio_optimization: 2 themes had 2 papers with all-invalid code IDs; those papers removed.
- **L-B2** (hard, structural + cross-referential): all 8 silos passed on first run. 0 sanitization needed.
- **Hallucination rate** (silo level): 3/139 themes had any code-ID confabulation = 2.2%. All caught and corrected by L-B1.

## 4. Audit-trail artifacts (per silo)

Located at `s4_thematic_coding/<silo>/themes/`:
- `b1_batch_01.prompt.txt`: rendered B1 prompt (reproducible from code_memo_index.json + silo memos)
- `b1_batch_01.meta.json`: hashes, model, file references
- `b1_batch_01.raw_response.txt`: exact LLM response text
- `b1_batch_01.json`: parsed + validated + sanitized themes
- `b1_batch_01.sanitize_log.json`: per-theme sanitization record (when applicable)
- `b1_manifest.jsonl`: append-only manifest of all B1 runs
- `b2.prompt.txt`, `b2.meta.json`, `b2.raw_response.txt`, `b2_silo_themes.json`, `b2_manifest.jsonl`: same pattern for B2

Global: `p3_thematic_synthesis/logs/b1_calls.jsonl` and `b2_calls.jsonl` — full-content call logs (CBS GenAI Pillar 3).

## 5. Next steps

1. **Researcher quality review (R2)**: score each silo against `docs/B1_B2_QUALITY_RUBRIC.md` (mean ≥ 4.0, no criterion < 3). Spot-check 2–3 counter-evidence citations per silo.
2. **Cross-silo synthesis (stage C)**: compare analytical themes across silos to surface meta-patterns for the thesis Discussion chapter.
3. **Manuscript integration**: author 8 silo sections (Chapter 6) using these themes as the analytical spine.