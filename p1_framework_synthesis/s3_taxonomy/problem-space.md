# Problem-Space Taxonomy

_Produced during Phase 1 — Framework Synthesis (LLM-assisted, researcher-curated)_
_Date: 2026-04-11 (header reframed 2026-05-02 freeze) | Method: Cruzes & Dybå (2011) within an Arksey & O'Malley (2005) scoping approach_

> **Active partition (post 2026-05-02):** the **8** active problem domains used downstream are PD-01..PD-09 minus PD-08 (excluded; QKD-dominated) and PD-10 (retracted; sole evidence file misidentified — see [`audit-trail.md`](../audit-trail.md) D-1 / D-2). Both lifecycle states are codified in [`shared/config/unified_taxonomy.json`](../../shared/config/unified_taxonomy.json) and enforced by `tools/verify/v2_consistency.py`. Per-category counts below are the **Phase-1 exploratory corpus counts at framework time**; for the active P3 partition consult [`p3_thematic_synthesis/README.md`](../../p3_thematic_synthesis/README.md).

## Overview

The problem-space taxonomy comprises **10 categories** derived from LLM-assisted extraction over the Phase 1 exploratory corpus, followed by deductive normalisation against an a-priori code vocabulary (`scripts/build_review_data_done.py::PROBLEM_CODE_MAP`). The original framing as "Elo & Kyngäs inductive content analysis" was **not the executed protocol** — see audit-trail D-5.

Each category has a working definition, scope notes for include/exclude decisions, and a list of contributing constituent codes. Category boundaries are imperfect by design — see the multi-tag and overlap policy in [`s4_outputs/codebook.md`](../s4_outputs/codebook.md) for PD-02 ↔ PD-09 and PD-08 ↔ SA-09 disambiguation.

---

## PD-01: Portfolio Optimisation and Asset Allocation

**Definition:** Problems concerning the selection, weighting, and rebalancing of financial assets in a portfolio to maximise return, minimise risk, or satisfy complex constraints. Includes mean-variance optimisation, index tracking, factor investing, and multi-period rebalancing.

**Scope (included):** Portfolio construction, asset allocation, diversification, index tracking, factor models, ESG-constrained portfolios, multi-objective portfolio problems.

**Scope (excluded):** General combinatorial optimisation not applied to portfolios; trading execution (see PD-06).

**Papers contributing:** 19

**Constituent codes:**
- `portfolio-optimization` — 119 entries across 19 papers
- `mean-variance` — 11 entries across 7 papers
- `asset-allocation` — 22 entries across 9 papers
- `markowitz` — 10 entries across 7 papers
- `diversification` — 1 entries across 1 papers
- `index-tracking` — 2 entries across 1 papers
- `factor-investing` — 0 entries across 0 papers
- `combinatorial-optimization` — 14 entries across 7 papers
- `constraint-satisfaction` — 1 entries across 1 papers

**Contributing papers:**
- 2019_Ors_Quantum_Computing_Finance_Overview
- 2020_AdamBouland_Prospects_Challenges_Quantum_Finance
- 2022_Albareti_Structured_Survey_Quantum_Computing
- 2022_Canabarro_Quantum_Finance_Tutorial_Quantum
- 2022_DylanHerman_Survey_Quantum_Computing_Finance
- 2023_Abbas_Quantum_Optimization_Potential_Challenges
- 2023_Herman_Quantum_Computing_Finance
- 2023_Markna_Unveiling_Advanced_Computational_Applications
- 2024_Abbas_Challenges_Opportunities_Quantum_Optimization
- 2024_OmosholaSOwolabi_Quantum_Computing_Applications_Challenges
- 2024_Sotelo_Quantum_Computing_Finance_Intesa
- 2025_Aggarwal_Comprehensive_Review_Convergence_Quantum
- 2025_Helmy_Unveiling_Quantum_Realm_Comprehensive
- 2025_Irfan_Quantum_Finance_Unleashed_Transforming
- 2025_Irfan_Quantum_Future_Finance_Applications
- 2025_Uppaluri_Quantum_Computing_Financial_Systems
- 2026_ArnoldCAlguno_Quantum_Computing_Drives_Innovation
- 2026_AtharvaJain_Quantum_Computing_S_Role
- 2026_MohammadAliTagati_Quantum_Computing_Future_Finance

---

## PD-02: Derivative Pricing and Valuation

**Definition:** Problems related to computing the fair value of financial derivatives including options, swaps, and structured products. Encompasses both closed-form and simulation-based pricing methods.

**Scope (included):** European/American/Asian/barrier option pricing, exotic derivatives, interest rate derivatives, credit valuation adjustment (CVA/XVA), Black-Scholes extensions, stochastic volatility models.

**Scope (excluded):** Pure Monte Carlo methodology without a pricing context (see PD-09); generic risk metrics (see PD-03).

**Papers contributing:** 17

**Constituent codes:**
- `derivative-pricing` — 84 entries across 17 papers
- `option-pricing` — 22 entries across 11 papers
- `european-options` — 1 entries across 1 papers
- `american-options` — 6 entries across 4 papers
- `asian-options` — 1 entries across 1 papers
- `barrier-options` — 1 entries across 1 papers
- `exotic-derivatives` — 1 entries across 1 papers
- `black-scholes` — 2 entries across 1 papers
- `interest-rate-derivatives` — 1 entries across 1 papers
- `swaps` — 4 entries across 2 papers
- `cva` — 16 entries across 7 papers
- `xva` — 1 entries across 1 papers

**Contributing papers:**
- 2019_Ors_Quantum_Computing_Finance_Overview
- 2020_AdamBouland_Prospects_Challenges_Quantum_Finance
- 2022_Albareti_Structured_Survey_Quantum_Computing
- 2022_AndrsGmez_Survey_Quantum_Computational_Finance
- 2022_DylanHerman_Survey_Quantum_Computing_Finance
- 2023_Abbas_Quantum_Optimization_Potential_Challenges
- 2023_Herman_Quantum_Computing_Finance
- 2024_Abbas_Challenges_Opportunities_Quantum_Optimization
- 2024_Sotelo_Quantum_Computing_Finance_Intesa
- 2025_Aggarwal_Comprehensive_Review_Convergence_Quantum
- 2025_Helmy_Unveiling_Quantum_Realm_Comprehensive
- 2025_Irfan_Quantum_Finance_Unleashed_Transforming
- 2025_Irfan_Quantum_Future_Finance_Applications
- 2025_Uppaluri_Quantum_Computing_Financial_Systems
- 2026_ArnoldCAlguno_Quantum_Computing_Drives_Innovation
- 2026_AtharvaJain_Quantum_Computing_S_Role
- 2026_MohammadAliTagati_Quantum_Computing_Future_Finance

---

## PD-03: Risk Management and Assessment

**Definition:** Problems involving the measurement, modelling, and mitigation of financial risk. Includes market risk, credit risk, systemic risk, and operational risk quantification.

**Scope (included):** Value-at-Risk (VaR), Conditional VaR (CVaR), stress testing, credit risk modelling, systemic risk analysis, counterparty risk, tail risk estimation, risk aggregation.

**Scope (excluded):** Credit scoring as a classification task (see PD-07); derivative-specific risk measures tied to pricing (see PD-02).

**Papers contributing:** 18

**Constituent codes:**
- `risk-management` — 82 entries across 18 papers
- `value-at-risk` — 30 entries across 11 papers
- `cvar` — 13 entries across 7 papers
- `stress-testing` — 1 entries across 1 papers
- `market-risk` — 1 entries across 1 papers
- `credit-risk` — 19 entries across 11 papers
- `systemic-risk` — 7 entries across 5 papers
- `operational-risk` — 0 entries across 0 papers
- `tail-risk` — 1 entries across 1 papers
- `counterparty-risk` — 3 entries across 2 papers
- `risk-aggregation` — 0 entries across 0 papers
- `risk-analysis` — 25 entries across 14 papers

**Contributing papers:**
- 2019_Ors_Quantum_Computing_Finance_Overview
- 2020_AdamBouland_Prospects_Challenges_Quantum_Finance
- 2022_Albareti_Structured_Survey_Quantum_Computing
- 2022_AndrsGmez_Survey_Quantum_Computational_Finance
- 2022_DylanHerman_Survey_Quantum_Computing_Finance
- 2023_Abbas_Quantum_Optimization_Potential_Challenges
- 2023_Herman_Quantum_Computing_Finance
- 2023_Markna_Unveiling_Advanced_Computational_Applications
- 2024_Abbas_Challenges_Opportunities_Quantum_Optimization
- 2024_Sotelo_Quantum_Computing_Finance_Intesa
- 2025_Aggarwal_Comprehensive_Review_Convergence_Quantum
- 2025_Irfan_Quantum_Finance_Unleashed_Transforming
- 2025_Irfan_Quantum_Future_Finance_Applications
- 2025_Uppaluri_Quantum_Computing_Financial_Systems
- 2026_ArnoldCAlguno_Quantum_Computing_Drives_Innovation
- 2026_AtharvaJain_Quantum_Computing_S_Role
- 2026_MohammadAliTagati_Quantum_Computing_Future_Finance
- 2026_Sarin_Leveraging_Quantum_Computing_Business

---

## PD-04: Machine Learning and Pattern Recognition in Finance

**Definition:** Applications of quantum-enhanced machine learning techniques to financial data analysis, including classification, regression, forecasting, and natural language processing tasks.

**Scope (included):** Time-series forecasting, return prediction, sentiment analysis, financial NLP, clustering of market regimes, pattern recognition, quantum-enhanced classification of financial data.

**Scope (excluded):** ML used purely for fraud detection (see PD-05); generic QML algorithm development without financial application.

**Papers contributing:** 17

**Constituent codes:**
- `machine-learning` — 52 entries across 13 papers
- `classification` — 12 entries across 5 papers
- `forecasting` — 34 entries across 14 papers
- `nlp-sentiment` — 3 entries across 2 papers
- `pattern-recognition` — 5 entries across 3 papers
- `regression` — 11 entries across 6 papers
- `clustering` — 8 entries across 4 papers

**Contributing papers:**
- 2019_Ors_Quantum_Computing_Finance_Overview
- 2020_AdamBouland_Prospects_Challenges_Quantum_Finance
- 2022_Albareti_Structured_Survey_Quantum_Computing
- 2022_AndrsGmez_Survey_Quantum_Computational_Finance
- 2022_DylanHerman_Survey_Quantum_Computing_Finance
- 2023_Herman_Quantum_Computing_Finance
- 2023_Markna_Unveiling_Advanced_Computational_Applications
- 2024_Abbas_Challenges_Opportunities_Quantum_Optimization
- 2024_Sotelo_Quantum_Computing_Finance_Intesa
- 2025_Aggarwal_Comprehensive_Review_Convergence_Quantum
- 2025_Irfan_Quantum_Finance_Unleashed_Transforming
- 2025_Irfan_Quantum_Future_Finance_Applications
- 2025_Uppaluri_Quantum_Computing_Financial_Systems
- 2026_ArnoldCAlguno_Quantum_Computing_Drives_Innovation
- 2026_AtharvaJain_Quantum_Computing_S_Role
- 2026_MohammadAliTagati_Quantum_Computing_Future_Finance
- 2026_Sarin_Leveraging_Quantum_Computing_Business

---

## PD-05: Fraud Detection and Anomaly Detection

**Definition:** Problems concerning the identification of fraudulent transactions, money laundering activity, and other financial anomalies.

**Scope (included):** Anti-money laundering (AML), transaction monitoring, anomaly detection in financial networks, Know-Your-Customer (KYC).

**Scope (excluded):** General anomaly detection outside finance; cybersecurity threats (see PD-08).

**Papers contributing:** 12

**Constituent codes:**
- `fraud-detection` — 30 entries across 12 papers
- `aml` — 2 entries across 2 papers
- `transaction-monitoring` — 0 entries across 0 papers
- `anomaly-detection` — 11 entries across 6 papers

**Contributing papers:**
- 2019_Ors_Quantum_Computing_Finance_Overview
- 2020_AdamBouland_Prospects_Challenges_Quantum_Finance
- 2022_DylanHerman_Survey_Quantum_Computing_Finance
- 2023_Abbas_Quantum_Optimization_Potential_Challenges
- 2023_Herman_Quantum_Computing_Finance
- 2024_Abbas_Challenges_Opportunities_Quantum_Optimization
- 2024_Sotelo_Quantum_Computing_Finance_Intesa
- 2025_Aggarwal_Comprehensive_Review_Convergence_Quantum
- 2025_Irfan_Quantum_Finance_Unleashed_Transforming
- 2025_Irfan_Quantum_Future_Finance_Applications
- 2025_Uppaluri_Quantum_Computing_Financial_Systems
- 2026_AtharvaJain_Quantum_Computing_S_Role

---

## PD-06: Trading and Market Microstructure

**Definition:** Problems related to trade execution, market making, arbitrage, and the design of trading strategies.

**Scope (included):** Algorithmic trading, optimal execution, arbitrage detection, high-frequency trading, market microstructure, order routing.

**Scope (excluded):** Portfolio-level allocation decisions (see PD-01); return prediction (see PD-04).

**Papers contributing:** 7

**Constituent codes:**
- `trading` — 13 entries across 7 papers
- `arbitrage` — 6 entries across 4 papers
- `high-frequency-trading` — 7 entries across 4 papers
- `market-microstructure` — 0 entries across 0 papers
- `order-execution` — 0 entries across 0 papers

**Contributing papers:**
- 2019_Ors_Quantum_Computing_Finance_Overview
- 2020_AdamBouland_Prospects_Challenges_Quantum_Finance
- 2022_DylanHerman_Survey_Quantum_Computing_Finance
- 2025_Aggarwal_Comprehensive_Review_Convergence_Quantum
- 2025_Irfan_Quantum_Finance_Unleashed_Transforming
- 2025_Irfan_Quantum_Future_Finance_Applications
- 2026_AtharvaJain_Quantum_Computing_S_Role

---

## PD-07: Credit Scoring and Lending

**Definition:** Classification and scoring problems in the credit domain, including default prediction and lending decisions.

**Scope (included):** Credit scoring models, default prediction, loan approval, creditworthiness assessment.

**Scope (excluded):** Credit risk as a risk management aggregate (see PD-03); fraud in lending (see PD-05).

**Papers contributing:** 11

**Constituent codes:**
- `credit-scoring` — 14 entries across 8 papers
- `default-prediction` — 0 entries across 0 papers
- `credit-lending` — 6 entries across 6 papers

**Contributing papers:**
- 2019_Ors_Quantum_Computing_Finance_Overview
- 2022_DylanHerman_Survey_Quantum_Computing_Finance
- 2023_Abbas_Quantum_Optimization_Potential_Challenges
- 2023_Herman_Quantum_Computing_Finance
- 2024_Abbas_Challenges_Opportunities_Quantum_Optimization
- 2024_Sotelo_Quantum_Computing_Finance_Intesa
- 2025_Aggarwal_Comprehensive_Review_Convergence_Quantum
- 2025_Irfan_Quantum_Finance_Unleashed_Transforming
- 2025_Irfan_Quantum_Future_Finance_Applications
- 2026_ArnoldCAlguno_Quantum_Computing_Drives_Innovation
- 2026_AtharvaJain_Quantum_Computing_S_Role

---

## PD-08: Cryptography and Financial Security  ⚠️ EXCLUDED FROM ACTIVE PIPELINE (2026-04-19)

> **Status note (added 2026-05-02):** PD-08 is retained in the Phase-1
> taxonomy registry but is **excluded from the active Phase-3 silo set**
> (`shared/config/silo_inclusion.json` `excluded_silos`) on the grounds
> that the literature is QKD-dominated and out of gate-based quantum-
> finance scope. The category remains documented here for traceability;
> it does not feed downstream synthesis.

**Definition:** Security problems arising from quantum computing capabilities, including threats to existing cryptographic systems and quantum-safe alternatives.

**Scope (included):** Quantum key distribution (QKD), post-quantum cryptography, threats to RSA/ECC, cybersecurity in financial infrastructure.

**Scope (excluded):** Non-financial cryptographic applications; quantum computing hardware security.

**Papers contributing:** 9

**Constituent codes:**
- `quantum-cryptography` — 48 entries across 9 papers
- `post-quantum` — 9 entries across 5 papers
- `cybersecurity` — 6 entries across 5 papers
- `classical-crypto-vulnerability` — 21 entries across 5 papers

**Contributing papers:**
- 2022_Albareti_Structured_Survey_Quantum_Computing
- 2022_DylanHerman_Survey_Quantum_Computing_Finance
- 2024_Sotelo_Quantum_Computing_Finance_Intesa
- 2025_Aggarwal_Comprehensive_Review_Convergence_Quantum
- 2025_Irfan_Quantum_Finance_Unleashed_Transforming
- 2025_Irfan_Quantum_Future_Finance_Applications
- 2025_Uppaluri_Quantum_Computing_Financial_Systems
- 2026_AtharvaJain_Quantum_Computing_S_Role
- 2026_Sarin_Leveraging_Quantum_Computing_Business

---

## PD-09: Simulation and Monte Carlo Methods

**Definition:** General simulation problems in finance, particularly Monte Carlo integration and stochastic process simulation.

**Scope (included):** Monte Carlo integration, stochastic simulation, path simulation, random walk models, quantum simulation of financial processes.

**Scope (excluded):** Monte Carlo specifically for option pricing (see PD-02); Monte Carlo for VaR estimation (see PD-03).

**Papers contributing:** 14

**Constituent codes:**
- `monte-carlo-simulation` — 53 entries across 14 papers
- `stochastic-simulation` — 2 entries across 2 papers
- `path-simulation` — 0 entries across 0 papers
- `random-walk` — 1 entries across 1 papers
- `quantum-simulation` — 2 entries across 2 papers

**Contributing papers:**
- 2019_Ors_Quantum_Computing_Finance_Overview
- 2020_AdamBouland_Prospects_Challenges_Quantum_Finance
- 2022_Albareti_Structured_Survey_Quantum_Computing
- 2022_AndrsGmez_Survey_Quantum_Computational_Finance
- 2022_Canabarro_Quantum_Finance_Tutorial_Quantum
- 2022_DylanHerman_Survey_Quantum_Computing_Finance
- 2023_Herman_Quantum_Computing_Finance
- 2024_Abbas_Challenges_Opportunities_Quantum_Optimization
- 2025_Aggarwal_Comprehensive_Review_Convergence_Quantum
- 2025_Irfan_Quantum_Finance_Unleashed_Transforming
- 2025_Irfan_Quantum_Future_Finance_Applications
- 2025_Uppaluri_Quantum_Computing_Financial_Systems
- 2026_ArnoldCAlguno_Quantum_Computing_Drives_Innovation
- 2026_AtharvaJain_Quantum_Computing_S_Role

---

## PD-10: Insurance and Actuarial Science  🚫 RETRACTED (2026-05-02)

> **Retraction note (2026-05-02):** the sole evidence file for this
> category, `2026_AtharvaJain_Quantum_Computing_S_Role.json`, was a
> misidentified extraction (the underlying PDF describes 5G/6G quantum
> communication networks, not an insurance/actuarial paper). With the
> source quarantined to
> [`s1_extractions/_QUARANTINED_2026_AtharvaJain_misidentified.RETRACTION.md`](../s1_extractions/_QUARANTINED_2026_AtharvaJain_misidentified.RETRACTION.md),
> PD-10 has no Phase-1 evidence base. The category was already absorbed
> into PD-03 (Risk Management) for the active Phase-3 silo set on
> 2026-04-19; this retraction simply makes the evidence gap visible at
> the source. The descriptive prose below is left in place for audit
> purposes only and **must not be cited as Phase-1 grounding**.

**Definition:** Problems specific to the insurance industry including premium calculation, claims modelling, and underwriting.

**Scope (included):** Insurance pricing, actuarial models, underwriting optimisation, claims prediction.

**Scope (excluded):** General risk management not specific to insurance (see PD-03).

**Papers contributing:** 1

**Constituent codes:**
- `insurance-actuarial` — 2 entries across 1 papers

**Contributing papers:**
- 2026_AtharvaJain_Quantum_Computing_S_Role

---
