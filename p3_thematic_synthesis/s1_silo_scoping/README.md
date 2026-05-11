# s1\_silo\_scoping — Corpus Scoping and Silo Registry

**Phase 3, Step 3.1**  
**Status**: ✅ Complete

## Purpose

Defines which application-domain silos are active for Phase 3 thematic synthesis and performs bibliometric scoping of the classified corpus.

## Substeps

| Step | Description | Status |
|------|-------------|--------|
| 3.1.a | Silo scoping — define active silos from P1 taxonomy | ✅ Complete |
| 3.1.b | Bibliometric landscape — corpus-level descriptive statistics | ✅ Complete |

## Active Silos (8)

| Code | Silo | Folder |
|------|------|--------|
| PD-01 | Portfolio Optimization | `portfolio_optimization/` |
| PD-02 | Derivative Pricing | `derivative_pricing/` |
| PD-03 | Risk Management (absorbs PD-10) | `risk_management/` |
| PD-04 | Quantum ML in Finance | `quantum_ml_finance/` |
| PD-05 | Fraud Detection | `fraud_detection/` |
| PD-06 | Trading & Execution | `trading_execution/` |
| PD-07 | Credit & Lending | `credit_lending/` |
| PD-09 | Simulation & Monte Carlo | `simulation_monte_carlo/` |

**Excluded**: PD-08 (Cryptography — QKD-dominated, out of gate-based scope), PD-10 (Insurance — 8 papers, absorbed into PD-03).

## Inputs

- `shared/config/unified_taxonomy.json` — P1 taxonomy codes (PD-01 through PD-10)
- Phase 2 classified papers (777 papers with `topic_tags`)

## Outputs

- `shared/config/silo_inclusion.json` — canonical silo registry (8 active, 2 excluded)
- `shared/phase3/bibliometric/` — 7 JSON files + landscape report

## Downstream Consumers

- **s2\_quantitative** — uses silo lists for per-silo extraction batching
- **s4\_thematic\_coding** — uses silo lists for per-silo coding fan-out
- **manuscript Ch6** — silo ordering follows P1 taxonomy
