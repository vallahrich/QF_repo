# Phase 2 Classification Codebook

_Derived from Phase 1 Framework Synthesis — 2026-04-11_

## Purpose

This codebook provides structured classification codes for deductively tagging papers in Phase 2 (Systematic Identification and Classification). Each paper in the Phase 2 corpus should be tagged with **one or more problem-space categories** and **one or more solution-space categories** from the taxonomies below.

## Instructions for Classifiers

1. Read the paper's abstract, introduction, and methodology sections.
2. Identify which **financial problem(s)** the paper addresses.
3. Assign one or more problem-space codes (PD-01 through PD-10).
4. Identify which **quantum solution approach(es)** the paper uses or proposes.
5. Assign one or more solution-space codes (SA-01 through SA-11).
6. If a paper does not clearly fit any category, flag for manual review.
7. Multi-tagging is expected — many papers span multiple categories.

### Multi-tag and overlap policy (added 2026-05-02 freeze; closes audit-trail D-4)

The taxonomy has three known overlap seams that classifiers must resolve
consistently:

- **PD-02 (Derivative Pricing) vs PD-09 (Simulation / Monte Carlo).**
  Monte Carlo / QAE / QMCI methods *applied to a specific pricing instance*
  (option valuation, CVA/XVA, etc.) get **PD-02 only**. Methods presented as
  general MC machinery without a pricing-specific instance get **PD-09 only**.
  A paper that demonstrates both (e.g. a generic QAE primitive with a worked
  pricing example) gets **PD-02 ∧ PD-09**, but the matrix-aggregation step
  in `scripts/build_taxonomy.py` is responsible for deduplicating the SA-03
  count across the two cells. Cite this rule in any per-paper assignment that
  picks one over the other.

- **SA-02 (Variational / NISQ) vs SA-04 (Quantum ML).** Variational circuits
  used as *trainable classifiers / regressors* (QNN, VQE-as-classifier,
  variational autoencoders) belong to **both SA-02 and SA-04**. Variational
  circuits used purely for *combinatorial optimisation* (QAOA on QUBO,
  VQE on a Hamiltonian ground state) belong to **SA-02 only**. Pure QSVM /
  quantum-kernel methods belong to **SA-04 only**.

- **PD-08 (Cryptography) ↔ SA-09 (Quantum Cryptography).** PD-08 is
  excluded from the active P3 pipeline (QKD-dominated; see banner on the
  PD-08 entry). For any paper where security is the *problem* statement,
  use PD-08 *and* SA-09; for a finance paper that mentions Shor-as-threat
  in passing, use neither. Phase-2 classifiers should err on the side of
  excluding PD-08 unless the paper's primary problem is security.

---

## Problem-Space Codes

| Code | Category | Definition |
|------|----------|------------|
| PD-01 | Portfolio Optimisation and Asset Allocation | Problems concerning the selection, weighting, and rebalancing of financial assets in a portfolio to maximise return, min... |
| PD-02 | Derivative Pricing and Valuation | Problems related to computing the fair value of financial derivatives including options, swaps, and structured products.... |
| PD-03 | Risk Management and Assessment | Problems involving the measurement, modelling, and mitigation of financial risk. Includes market risk, credit risk, syst... |
| PD-04 | Machine Learning and Pattern Recognition in Finance | Applications of quantum-enhanced machine learning techniques to financial data analysis, including classification, regre... |
| PD-05 | Fraud Detection and Anomaly Detection | Problems concerning the identification of fraudulent transactions, money laundering activity, and other financial anomal... |
| PD-06 | Trading and Market Microstructure | Problems related to trade execution, market making, arbitrage, and the design of trading strategies.... |
| PD-07 | Credit Scoring and Lending | Classification and scoring problems in the credit domain, including default prediction and lending decisions.... |
| PD-08 | Cryptography and Financial Security | Security problems arising from quantum computing capabilities, including threats to existing cryptographic systems and q... |
| PD-09 | Simulation and Monte Carlo Methods | General simulation problems in finance, particularly Monte Carlo integration and stochastic process simulation.... |
| PD-10 | Insurance and Actuarial Science | Problems specific to the insurance industry including premium calculation, claims modelling, and underwriting.... |

### Detailed Problem-Space Definitions

#### PD-01: Portfolio Optimisation and Asset Allocation

**Definition:** Problems concerning the selection, weighting, and rebalancing of financial assets in a portfolio to maximise return, minimise risk, or satisfy complex constraints. Includes mean-variance optimisation, index tracking, factor investing, and multi-period rebalancing.

**Include:** Portfolio construction, asset allocation, diversification, index tracking, factor models, ESG-constrained portfolios, multi-objective portfolio problems.

**Exclude:** General combinatorial optimisation not applied to portfolios; trading execution (see PD-06).

#### PD-02: Derivative Pricing and Valuation

**Definition:** Problems related to computing the fair value of financial derivatives including options, swaps, and structured products. Encompasses both closed-form and simulation-based pricing methods.

**Include:** European/American/Asian/barrier option pricing, exotic derivatives, interest rate derivatives, credit valuation adjustment (CVA/XVA), Black-Scholes extensions, stochastic volatility models.

**Exclude:** Pure Monte Carlo methodology without a pricing context (see PD-09); generic risk metrics (see PD-03).

#### PD-03: Risk Management and Assessment

**Definition:** Problems involving the measurement, modelling, and mitigation of financial risk. Includes market risk, credit risk, systemic risk, and operational risk quantification.

**Include:** Value-at-Risk (VaR), Conditional VaR (CVaR), stress testing, credit risk modelling, systemic risk analysis, counterparty risk, tail risk estimation, risk aggregation.

**Exclude:** Credit scoring as a classification task (see PD-07); derivative-specific risk measures tied to pricing (see PD-02).

#### PD-04: Machine Learning and Pattern Recognition in Finance

**Definition:** Applications of quantum-enhanced machine learning techniques to financial data analysis, including classification, regression, forecasting, and natural language processing tasks.

**Include:** Time-series forecasting, return prediction, sentiment analysis, financial NLP, clustering of market regimes, pattern recognition, quantum-enhanced classification of financial data.

**Exclude:** ML used purely for fraud detection (see PD-05); generic QML algorithm development without financial application.

#### PD-05: Fraud Detection and Anomaly Detection

**Definition:** Problems concerning the identification of fraudulent transactions, money laundering activity, and other financial anomalies.

**Include:** Anti-money laundering (AML), transaction monitoring, anomaly detection in financial networks, Know-Your-Customer (KYC).

**Exclude:** General anomaly detection outside finance; cybersecurity threats (see PD-08).

#### PD-06: Trading and Market Microstructure

**Definition:** Problems related to trade execution, market making, arbitrage, and the design of trading strategies.

**Include:** Algorithmic trading, optimal execution, arbitrage detection, high-frequency trading, market microstructure, order routing.

**Exclude:** Portfolio-level allocation decisions (see PD-01); return prediction (see PD-04).

#### PD-07: Credit Scoring and Lending

**Definition:** Classification and scoring problems in the credit domain, including default prediction and lending decisions.

**Include:** Credit scoring models, default prediction, loan approval, creditworthiness assessment.

**Exclude:** Credit risk as a risk management aggregate (see PD-03); fraud in lending (see PD-05).

#### PD-08: Cryptography and Financial Security  *(EXCLUDED from active P3 pipeline 2026-04-19; QKD-dominated, out of gate-based scope)*

**Definition:** Security problems arising from quantum computing capabilities, including threats to existing cryptographic systems and quantum-safe alternatives.

**Include:** Quantum key distribution (QKD), post-quantum cryptography, threats to RSA/ECC, cybersecurity in financial infrastructure.

**Exclude:** Non-financial cryptographic applications; quantum computing hardware security.

#### PD-09: Simulation and Monte Carlo Methods

**Definition:** General simulation problems in finance, particularly Monte Carlo integration and stochastic process simulation.

**Include:** Monte Carlo integration, stochastic simulation, path simulation, random walk models, quantum simulation of financial processes.

**Exclude:** Monte Carlo specifically for option pricing (see PD-02); Monte Carlo for VaR estimation (see PD-03).

#### PD-10: Insurance and Actuarial Science  *(RETRACTED 2026-05-02; sole evidence file misidentified — see s1_extractions/_QUARANTINED_2026_AtharvaJain_misidentified.RETRACTION.md; merged into PD-03 in the active P3 silo set)*

**Definition:** Problems specific to the insurance industry including premium calculation, claims modelling, and underwriting.

**Include:** Insurance pricing, actuarial models, underwriting optimisation, claims prediction.

**Exclude:** General risk management not specific to insurance (see PD-03).

---

## Solution-Space Codes

| Code | Category | Definition |
|------|----------|------------|
| SA-01 | Quantum Annealing and QUBO Formulations | Approaches that solve optimisation problems by encoding them as Quadratic Unconstrained Binary Optimisation (QUBO) or Is... |
| SA-02 | Variational and NISQ Algorithms | Gate-based quantum algorithms that use parameterised circuits optimised by a classical outer loop. Designed for near-ter... |
| SA-03 | Quantum Amplitude Estimation and Monte Carlo Integration | Algorithms based on quantum amplitude estimation (QAE) that provide quadratic speedups for Monte Carlo integration tasks... |
| SA-04 | Quantum Machine Learning | Quantum algorithms for machine learning tasks including classification, regression, generative modelling, and dimensiona... |
| SA-05 | Grover's Search and Variants | Algorithms based on Grover's search providing quadratic speedup for unstructured search problems. Includes variants and ... |
| SA-06 | Quantum Linear Systems (HHL and Extensions) | Algorithms for solving linear systems of equations on quantum computers, based on the HHL algorithm and its extensions.... |
| SA-07 | Quantum Walks | Algorithms based on quantum walks on graphs, with applications to search, sampling, and financial network analysis.... |
| SA-08 | Hybrid Quantum-Classical Approaches | Architectural patterns that integrate quantum subroutines within larger classical computation pipelines. Cross-cuts othe... |
| SA-09 | Quantum Cryptography and Post-Quantum Security | Quantum-based security solutions and post-quantum cryptographic protocols relevant to financial infrastructure.... |
| SA-10 | Quantum Fourier Transform and Phase Estimation | Primitive quantum subroutines (QFT, QPE) that underpin many higher-level algorithms. Included as a solution category bec... |
| SA-11 | Error Mitigation and Fault Tolerance | Techniques for managing noise and errors in quantum computations, including error mitigation for NISQ and full error cor... |

### Detailed Solution-Space Definitions

#### SA-01: Quantum Annealing and QUBO Formulations

**Definition:** Approaches that solve optimisation problems by encoding them as Quadratic Unconstrained Binary Optimisation (QUBO) or Ising models and solving via quantum annealing hardware (e.g., D-Wave) or adiabatic quantum computing.

**Include:** Quantum annealing, D-Wave implementations, QUBO formulations, Ising model encodings, simulated annealing benchmarks, adiabatic quantum computing.

**Exclude:** Gate-based variational approaches (see SA-02); classical simulated annealing without quantum comparison.

#### SA-02: Variational and NISQ Algorithms

**Definition:** Gate-based quantum algorithms that use parameterised circuits optimised by a classical outer loop. Designed for near-term noisy intermediate-scale quantum (NISQ) devices.

**Include:** QAOA, VQE, variational quantum algorithms, parameterised circuits, NISQ-specific algorithm design.

**Exclude:** Variational QML models (see SA-04); fault-tolerant algorithms (see SA-03, SA-05, SA-06).

#### SA-03: Quantum Amplitude Estimation and Monte Carlo Integration

**Definition:** Algorithms based on quantum amplitude estimation (QAE) that provide quadratic speedups for Monte Carlo integration tasks. Core primitive for derivative pricing and risk computation.

**Include:** Quantum amplitude estimation, quantum Monte Carlo integration (QMCI), amplitude amplification, quantum counting, quantum sampling.

**Exclude:** Grover search for database tasks (see SA-05); generic circuit constructions.

#### SA-04: Quantum Machine Learning

**Definition:** Quantum algorithms for machine learning tasks including classification, regression, generative modelling, and dimensionality reduction. Includes both gate-based and kernel-based approaches.

**Include:** Quantum neural networks (QNN), quantum SVM (QSVM), quantum kernel methods, quantum Boltzmann machines, quantum GANs, quantum autoencoders, quantum transfer learning, quantum reservoir computing, quantum PCA, quantum feature maps, quantum reinforcement learning.

**Exclude:** Classical ML with quantum data encoding only; variational algorithms for optimisation (see SA-02).

#### SA-05: Grover's Search and Variants

**Definition:** Algorithms based on Grover's search providing quadratic speedup for unstructured search problems. Includes variants and applications to combinatorial search in finance.

**Include:** Grover's algorithm, quantum search, unstructured database search applied to financial problems.

**Exclude:** Amplitude estimation (see SA-03); quantum walk-based search (see SA-07).

#### SA-06: Quantum Linear Systems (HHL and Extensions)

**Definition:** Algorithms for solving linear systems of equations on quantum computers, based on the HHL algorithm and its extensions.

**Include:** HHL algorithm, quantum linear systems algorithms, quantum matrix operations, quantum linear algebra.

**Exclude:** Quantum PCA (see SA-04); classical linear algebra acceleration.

#### SA-07: Quantum Walks

**Definition:** Algorithms based on quantum walks on graphs, with applications to search, sampling, and financial network analysis.

**Include:** Discrete and continuous quantum walks, graph-based quantum algorithms.

**Exclude:** Classical random walks (problem domain, not solution).

#### SA-08: Hybrid Quantum-Classical Approaches

**Definition:** Architectural patterns that integrate quantum subroutines within larger classical computation pipelines. Cross-cuts other solution categories as an integration paradigm.

**Include:** Hybrid QPU-CPU workflows, classical pre/post-processing, quantum-classical feedback loops, divide-and-conquer decomposition.

**Exclude:** Variational algorithms are inherently hybrid but classified under SA-02; this category captures the integration architecture rather than the algorithm.

#### SA-09: Quantum Cryptography and Post-Quantum Security

**Definition:** Quantum-based security solutions and post-quantum cryptographic protocols relevant to financial infrastructure.

**Include:** Quantum key distribution (QKD), post-quantum cryptographic algorithms, Shor's algorithm (as a threat), quantum-safe protocols.

**Exclude:** Cryptographic problems framed as threats to finance (see PD-08); this category covers the solutions/responses.

#### SA-10: Quantum Fourier Transform and Phase Estimation

**Definition:** Primitive quantum subroutines (QFT, QPE) that underpin many higher-level algorithms. Included as a solution category because several papers discuss their direct application to finance.

**Include:** Quantum Fourier transform, quantum phase estimation, applications to period finding and eigenvalue estimation in finance.

**Exclude:** When used only as a subroutine within HHL (see SA-06) or QAE (see SA-03).

#### SA-11: Error Mitigation and Fault Tolerance

**Definition:** Techniques for managing noise and errors in quantum computations, including error mitigation for NISQ and full error correction for fault-tolerant systems.

**Include:** Error mitigation techniques, fault-tolerant quantum computing, quantum error correction, noise-aware algorithm design.

**Exclude:** Hardware-level discussions without algorithmic implication.
