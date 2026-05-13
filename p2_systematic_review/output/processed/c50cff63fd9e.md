---
aliases:
- 'Bridging Quantum Algorithms and Classical Finance: Portfolio Optimization Using
  QAOA and QUBO Framework'
- Bridging Quantum Algorithms Classical
authors:
- Arnav Aggarwal
- Prerna Agarwal
- Pranav Shrivastava
- Rajneesh Kler
auto_detected: true
classification: ''
contradiction_flags:
- contradiction:scalability
doi: 10.1109/UPWIECON67212.2025.11390104
evaluation_type: simulator
evidence_type: ''
has_quantitative_results: true
idea_tags:
- idea:near-term-feasibility
- idea:hybrid-approach
journal_or_venue: 2025 1st IEEE Uttar Pradesh Section Women in Engineering International
  Conference on Electrical Electronics and Computer Engineering (UPWIECON)
methodology_tags:
- quantum-annealing-qubo
- variational-nisq
- hybrid-quantum-classical
paper_type: ''
quantum_advantage_claim: speculative
related_papers: []
relevance_phase1: high
relevance_phase3: high
source_type: conference-paper
source_type_confidence: high
step1_date: '2026-04-14T11:45:48.664044'
step1_model: gpt-5-mini
step2_date: '2026-04-14T11:45:48.664044'
step2_model: gpt-5-mini
step3_date: '2026-04-14T11:45:48.664044'
step3_model: gpt-5-mini
step4_date: '2026-04-14T11:45:48.664044'
step4_model: gpt-5-mini
step5_date: '2026-04-14T11:45:48.664044'
step5_model: gpt-5-mini
step6_date: '2026-04-14T11:45:48.664044'
step6_model: gpt-5-mini
steps_completed:
- 1
- 2
- 3
- 4
- 5
- 6
tags:
- topic/portfolio-optimization
- method/quantum-annealing-qubo
- method/variational-nisq
- method/hybrid-quantum-classical
- idea/near-term-feasibility
- idea/hybrid-approach
- contradiction/scalability
title: 'Bridging Quantum Algorithms and Classical Finance: Portfolio Optimization
  Using QAOA and QUBO Framework'
topic_tags:
- portfolio-optimization
year: '2025'
zotero_key: ''
---

## Abstract summary
This paper integrates quantum optimization (QAOA) with classical mean–variance portfolio optimization by reformulating asset selection as a QUBO problem using monthly turnover data from the National Stock Exchange of India. The authors construct a QUBO matrix combining expected returns and covariance, solve it with brute-force and quantum-inspired solvers, and report that index-based derivative combinations (Index Futures and Index Options) achieve the best risk‑adjusted performance (Sharpe ≈ 0.286), illustrating the practical potential of hybrid quantum-classical approaches for portfolio selection.
## Methodology
The study converts a classical mean-variance portfolio optimization into a binary Quadratic Unconstrained Binary Optimization (QUBO) problem by replacing continuous asset weights with binary inclusion variables. Monthly turnover data for four NSE equity-derivative instruments (Index Futures, Index Options, Stock Futures, Stock Options) are preprocessed (non-numeric rows removed or imputed), transformed into month-over-month percentage returns, and used to compute expected returns (μ) and the covariance matrix (Σ). A QUBO matrix is constructed that integrates risk (Σ) and expected returns (μ) with a risk-aversion parameter (λ = 0.5), and an equality/penalty constraint is used to enforce a fixed number of selected assets (k, here k=2). The resulting QUBO is solved by (a) classical exhaustive enumeration/brute-force and a classical integer-quadratic solver implemented using CVXPY to obtain exact benchmarks, and (b) a quantum-inspired QAOA implementation via Qiskit (hybrid quantum-classical variational parameter optimization) to minimize the QUBO objective. Results are compared across all 2-asset combinations using metrics such as expected return, portfolio variance, QUBO objective value, and Sharpe ratio to validate the quantum-inspired solver against classical baselines.

**Algorithms used:** Quantum Approximate Optimization Algorithm (QAOA), QUBO formulation (Quadratic Unconstrained Binary Optimization), Classical exhaustive enumeration (brute-force), Classical integer quadratic solver (CVXPY)
**Frameworks:** Qiskit, CVXPY

**Experimental setup:** QAOA was implemented via Qiskit as a quantum-inspired hybrid optimization (simulation/emulation); a classical CVXPY-based integer quadratic program and brute-force enumeration were used as baselines. No specific quantum hardware model, shot counts, or execution backend details are provided; experiments appear to have been run in simulation/hybrid classical environment.

**Dataset:** Monthly turnover figures (monthly observations) for equity-derivatives traded on the National Stock Exchange (NSE) of India: Index Futures, Index Options, Stock Futures, Stock Options. Time-series were converted to month-over-month percentage returns to compute expected returns and covariance.
## Experiment details
### Input
{'source': 'National Stock Exchange (NSE) monthly turnover data for equity derivatives', 'assets': ['Index Futures', 'Index Options', 'Stock Futures', 'Stock Options'], 'assets_count': 4, 'observations': 'Several monthly observations (not explicitly quantified in paper)', 'preprocessing': 'Non-numeric entries removed; missing values either removed or imputed; monthly returns computed as percentage changes in turnover; then mean expected returns (μ) and covariance matrix (Σ) were computed.'}

### Process
{'steps': ['Preprocess turnover time series (clean non-numeric, impute/remove missing) and compute month-over-month percentage returns.', 'Compute expected returns vector (μ) and covariance matrix (Σ) from monthly returns.', 'Formulate the mean-variance objective as a QUBO by mapping continuous weights to binary inclusion variables and combining Σ and μ with a risk-aversion parameter λ to build the QUBO matrix. Add a penalty/constraint to enforce selection of exactly k assets (k=2 in experiments).', 'Solve the QUBO exactly via brute-force enumeration and via a classical integer-quadratic solver (CVXPY) to obtain benchmark solutions.', 'Solve the QUBO with a quantum-inspired QAOA implementation using Qiskit: prepare parameterized QAOA circuits, iteratively optimize classical parameters to minimize the QUBO objective (hybrid quantum-classical loop), and extract bitstring solutions.', 'Compare and validate solutions across methods using expected return, variance, QUBO objective value, and Sharpe ratio.'], 'parameters_and_notes': 'Risk-aversion λ = 0.5; portfolio cardinality constraint k = 2. QAOA-specific parameters (circuit depth p, number of shots, optimizer type and hyperparameters, number of optimization iterations) are not specified in the paper.'}

### Output
{'output_format': 'Binary selection vectors (bitstrings) indicating chosen assets, expected monthly return, portfolio variance, QUBO objective value and Sharpe ratio for each candidate portfolio.', 'examples': {'best_solution_by_QUBO/CVXPY': {'binary': '[1, 1, 0, 0]', 'selected_assets': ['Index Futures', 'Index Options'], 'expected_monthly_return': 1.2747, 'portfolio_variance': 19.8423, 'qubo_objective': 19.02987, 'sharpe_ratio': 0.286162}}, 'baselines': 'Classical brute-force enumeration and CVXPY-based integer quadratic optimization served as exact baselines for validation of the QAOA implementation.', 'evaluation_metrics': ['Expected return (monthly)', 'Portfolio variance', 'QUBO objective value', 'Sharpe ratio (risk-adjusted return)']}

### Parameters
- risk_aversion_lambda: 0.5
- portfolio_cardinality_k: 2
- number_of_assets: 4
- QAOA_depth_p: None
- QAOA_shots: None
- QAOA_optimizer: None
- classical_solver: CVXPY (integer quadratic programming)
- brute_force: Enumerated all 2-asset combinations (6 combinations)

### Hardware
N/A

### Reproducibility
N/A
## Findings
- [supported] The authors successfully mapped a classical mean–variance portfolio objective into a QUBO formulation (λ = 0.5) using monthly turnover-derived returns and covariance from NSE derivatives data.
- [supported] A classical exhaustive (brute-force/CVXPY) solver identified the best 2-asset portfolio as [1,1,0,0] (Index Futures + Index Options) with expected monthly return = 1.2747, portfolio variance = 19.8423, QUBO objective = 19.02987 and Sharpe ratio ≈ 0.286162.
- [supported] Stock Options and Stock Futures show the highest expected monthly returns (0.804489 and 0.770428 respectively) and higher individual variances; Index Options show the lowest individual variance (4.592590).
- [supported] The constructed QUBO matrix (provided in the paper) encodes both diagonal (individual asset) and off-diagonal (pairwise interaction) costs, and guides the optimizer to favour lower cumulative Q values (e.g., index-based instruments showed relatively lower pairwise costs).
- [supported] The analysis shows portfolios with the highest raw returns (e.g., Stock Futures + Stock Options) can have poorer risk-adjusted performance (lower Sharpe) due to much higher variance.
- [speculative] The paper states that QAOA (implemented via Qiskit) was used as a quantum-inspired solver on the constructed QUBO, but no detailed QAOA solution outputs, comparison metrics, or experimental data for QAOA are reported in the text.
- [speculative] The authors claim hybrid quantum-classical (QAOA + classical) approaches and quantum-inspired solvers show promise to improve financial decision making and scalability as quantum hardware matures — this is presented as a potential/expected advantage rather than empirically demonstrated in this work.
- [speculative] The paper asserts that the classical brute-force results were used to 'confirm' the quantum-inspired algorithm, but explicit confirming results or performance comparisons for the quantum-inspired/QAOA solver are not presented.
- [speculative] Recommendations and future directions (larger asset universes, multi-period models, transaction costs, deployment on real quantum hardware) are proposed as promising extensions but are forward-looking and not empirically validated here.

**Results summary:** Using monthly turnover data from NSE derivatives, the authors compute expected monthly returns and a covariance matrix, construct a QUBO representation of a mean–variance binary asset-selection problem (λ=0.5), and exhaustively evaluate all two-asset combinations with a classical solver. The best two-asset portfolio (Index Futures + Index Options) yields expected return 1.2747, variance 19.8423 and Sharpe ≈ 0.286. The paper presents the QUBO matrix and comparative metrics for all two-asset portfolios. Although QAOA and a quantum-inspired solver are mentioned (implemented via Qiskit), the paper does not provide explicit QAOA solution results or performance comparisons; claims about quantum-enabled improvement and scalability remain prospective.

**Performance claims:**
- Expected monthly returns per asset: Index Futures = 0.651131, Index Options = 0.623624, Stock Futures = 0.770428, Stock Options = 0.804489.
- Covariance matrix diagonal (variances): Index Futures = 5.471748, Index Options = 4.592590, Stock Futures = 7.958138, Stock Options = 8.244593.
- Top 2-asset portfolio (Index Futures + Index Options): Expected Monthly Return = 1.2747, Portfolio Variance = 19.8423, QUBO Objective = 19.02987, Sharpe Ratio = 0.286162.
- Other 2-asset portfolio metrics (selected examples from TABLE IV): [0,1,1,0] Expected Return = 1.394, Variance = 23.9519, QUBO Obj = 22.98028, Sharpe ≈ 0.284835; [0,0,1,1] Expected Return = 1.5748, Variance = 32.3735, QUBO Obj = 31.1335, Sharpe ≈ 0.276777.
- Example QUBO matrix entries (λ = 0.5 applied): Q_00 (Index Futures,Index Futures) = 5.259762184, Q_01 (Index Futures,Index Options) = 4.685997756, Q_23 (Stock Futures,Stock Options) = 7.775490092, Q_33 (Stock Options,Stock Options) = 7.920992489.
## Quantum advantage claim
**Classification:** speculative

The paper discusses leveraging QAOA (via Qiskit) and quantum-inspired solvers and argues these approaches are promising for portfolio optimization. However, the manuscript does not present empirical QAOA results or a demonstrated performance advantage over classical methods; the only concrete solver outputs shown are from classical brute-force/CVXPY. Thus any claim of quantum advantage is prospective/speculative rather than demonstrated.
## Limitations
- Practical implementation restricted to relatively tiny portfolios due to limited qubit capacity of present-day quantum hardware.
- The study relied on simulation and quantum-classical hybrid models (Qiskit) rather than execution on real quantum hardware.
- [inferred] Dataset uses monthly turnover figures (turnover-based returns) rather than direct asset price returns—this proxy may not fully capture investment returns or liquidity effects.
- [inferred] Very small asset universe (4 instruments) and experiments focused on 2-asset combinations; scalability and generalization to larger universes were not demonstrated.
- [inferred] Fixed risk-aversion parameter (λ = 0.5) was used and sensitivity analysis to λ was not reported.
- [inferred] QAOA implementation details (circuit depth p, parameter tuning, convergence behaviour) and performance metrics (runtime, success probability) versus classical solvers are not thoroughly reported.
- [inferred] The QUBO mapping enforces binary inclusion only (no continuous weights), which limits representation of fractional allocations.
- [inferred] Stationarity and estimation error in expected returns and covariance (from historical turnover) were not addressed—robustness to estimation noise is unknown.
- [inferred] Transaction costs, market impact, liquidity constraints, and regulatory/sectoral diversification constraints were not modelled.
- [inferred] Effects of quantum hardware noise, decoherence and real-device errors on solution quality were not evaluated.
## Open questions
- How does the QUBO-QAOA framework scale to larger asset universes and higher-cardinality portfolio constraints?
- Can the approach be executed in real time on actual quantum hardware (e.g., IBM Q or D-Wave), and how will device noise influence solution quality?
- How can transaction costs, market impact, liquidity constraints, sectoral diversification and regulatory constraints be incorporated into the QUBO formulation?
- How can the framework be extended to multi-period (dynamic) portfolio rebalancing using time-evolving QUBO matrices?
- Can quantum machine learning methods be integrated to produce adaptive or self-improving portfolio models?
- How transferable are the findings across different markets (developed vs emerging) with varying volatility and liquidity characteristics?
- Do quantum-enhanced algorithms like QAOA provide practical performance or solution-quality advantages over classical heuristics and solvers for realistic, large-scale financial instances?
- What are the best practices for QAOA parameter selection (depth p, mixers, classical optimizer) for portfolio QUBOs, and how sensitive are results to these choices?
- How sensitive are optimized portfolios to estimation errors in expected returns and covariance; what robustness measures are needed?
- What are the computational and runtime trade-offs between quantum-inspired/hybrid methods and classical optimization as problem size increases?
- How to handle or hybridize binary-selection (QUBO) formulations with continuous-weight portfolio models to capture fractional allocations?

**Future work:**
- Extend the QUBO-QAOA framework to larger asset universes.
- Include multi-objective criteria such as transaction costs, sectoral diversification and regulatory constraints in the model.
- Investigate dynamic portfolio rebalancing using time-evolving QUBO matrices (multi-period decisions).
- Explore real-time implementation on quantum simulators or hardware (e.g., IBM Q or D-Wave).
- Employ quantum machine learning to build adaptive and self-improving portfolio optimisation models.
- Conduct comparative studies across markets (developed vs emerging) to assess transferability under varying volatility and liquidity conditions.
## Key ideas
- #idea:hybrid-approach — Formulated mean–variance portfolio selection as a QUBO and solved it using a QAOA-based hybrid quantum-classical pipeline (Qiskit) validated against exact classical baselines (brute-force and CVXPY).
- #idea:near-term-feasibility — Demonstrated the workflow on real NSE equity-derivative turnover data (4 assets), reporting concrete numerical outputs (expected returns, variance, QUBO objective, Sharpe ≈ 0.286) from the simulated QAOA and classical solvers.
- #idea:hybrid-approach — The study uses classical preprocessing (compute μ and Σ from turnover-derived returns) and a classical optimizer to tune QAOA parameters, illustrating a practical hybrid architecture.
- #limitation:simulation-only — All quantum experiments were performed via Qiskit simulation/emulation; no real quantum hardware runs, shot counts, or noise model details are provided.
- #limitation:no-empirical-validation — There is no empirical validation on a QPU; reported results are compared to classical exact solvers but do not demonstrate quantum advantage on hardware.
- #limitation:data-encoding — The paper maps the portfolio problem to a QUBO (binary inclusion variables) rather than discussing general-purpose amplitude/state encoding of continuous financial data, leaving costs of quantum data loading unaddressed.
## Contradictions
- contradiction:scalability — The paper asserts the practical potential of hybrid quantum-classical approaches but only evaluates a 4-asset, k=2 toy instance solved exactly by brute-force and a classical solver; no QAOA depth, shot, optimizer hyperparameters, or hardware experiments are provided, so claims about scalability to real-world-sized portfolios are unsubstantiated.
## Notable quotes
<!-- Researcher-added — verbatim quotes with page references -->

## Researcher notes
<!-- Researcher-added — not LLM generated -->
