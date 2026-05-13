---
aliases:
- 'Quantum Thinking in Finance: A Toy Model of Risk and Superposition'
- Quantum Thinking Finance Toy
authors:
- Valdir Dumba
- Ennis Mawa
auto_detected: true
classification: ''
contradiction_flags: []
doi: ''
evaluation_type: simulator
evidence_type: ''
has_quantitative_results: true
idea_tags:
- idea:quantum-advantage
- idea:near-term-feasibility
- idea:hybrid-approach
journal_or_venue: preprint
methodology_tags:
- quantum-annealing-qubo
- variational-nisq
- hybrid-quantum-classical
paper_type: ''
quantum_advantage_claim: speculative
related_papers: []
relevance_phase1: high
relevance_phase3: high
source_type: preprint
source_type_confidence: high
step1_date: '2026-04-14T12:20:48.042416'
step1_model: gpt-5-mini
step2_date: '2026-04-14T12:20:48.042416'
step2_model: gpt-5-mini
step3_date: '2026-04-14T12:20:48.042416'
step3_model: gpt-5-mini
step4_date: '2026-04-14T12:20:48.042416'
step4_model: gpt-5-mini
step5_date: '2026-04-14T12:20:48.042416'
step5_model: gpt-5-mini
step6_date: '2026-04-14T12:20:48.042416'
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
- idea/quantum-advantage
- idea/near-term-feasibility
- idea/hybrid-approach
title: 'Quantum Thinking in Finance: A Toy Model of Risk and Superposition'
topic_tags:
- portfolio-optimization
year: '2025'
zotero_key: ''
---

## Abstract summary
This preprint proposes a hybrid quantum/classical portfolio optimization algorithm that encodes a mean-variance objective into a QUBO and solves it with QAOA, extending a binary invest/not-invest model to a two-qubit (four-level) investment encoding. The model integrates a mixed-strategy Nash equilibrium to capture strategic interactions among investors, is tested on randomized four-asset portfolios in simulation, and is reported to yield higher simulated annual expected returns and favorable Sharpe ratios versus classical benchmarks while discussing current quantum hardware limitations and future prospects.
## Methodology
The study implements a hybrid quantum/classical portfolio optimization pipeline in which a mean-variance objective is encoded as a QUBO and converted to an Ising Hamiltonian for use with QAOA. Binary decision variables are replaced by 2-qubit encodings per asset to represent four discrete investment levels (don’t invest, low, medium, high) with associated reward weights and fixed percentage allocations of the initial investment (0%, 6%, 12.5%, 25%). Expected returns (μ) and covariance (Σ) are estimated from historical price data (Yahoo Finance) over a five-year window. A mixed-strategy game-theoretic layer (two-player Up/Down payoff matrices) is computed with Nashpy to adjust asset-level strategy probabilities and thus modify expected-return inputs. The resulting quadratic program (with constraints to ensure one level choice per asset) is converted into an Ising Hamiltonian and solved with QAOA (hybrid classical optimizer controlling quantum circuit parameters). A classical optimizer (COBYLA) is used with up to 250 iterations and QAOA uses three layers (p=3). Execution is on a noiseless quantum simulator (described as a “perfect simulated without noise” backend). Outputs include sampled bitstring solutions with values and probabilities, optimal investment tables, covariance heatmaps, and portfolio-growth simulations compared to classical baselines (NASDAQ-100 and S&P 500).

**Algorithms used:** QAOA, QUBO to Ising conversion, COBYLA (classical optimizer), Minimum Eigen Optimizer (Qiskit high-level interface), Mixed-strategy Nash equilibrium computation (Nashpy)
**Frameworks:** Qiskit, Nashpy, pandas, yfinance, NumPy, Matplotlib

**Experimental setup:** Runs used a noiseless (perfect) quantum simulator (Qiskit) rather than a physical QPU. The QAOA circuit applies Hadamard gates for superposition and is optimized in a hybrid loop using COBYLA (max 250 iterations). QAOA depth p=3. A MinimumEigenOptimizer wrapper is used; solutions are sampled and reported as bitstring selections with values and probabilities.

**Dataset:** Historical stock price data retrieved from Yahoo Finance via the yfinance library. The pipeline maintains a pool of 15 stocks spanning ~10 industries and randomly selects 4 assets per run. Time horizon for return/covariance estimation: 5 years.
## Experiment details
### Input
{'source': 'Yahoo Finance via yfinance', 'pool_size': 15, 'assets_per_run': 4, 'time_horizon': '5 years (historical prices)', 'preprocessing': 'Compute asset expected returns (μ) and covariance matrix (Σ) from historical price series; randomly sample 4 assets; apply mixed-strategy adjustments to expected returns using Nashpy payoff matrices; map discrete investment levels to 2-qubit encodings and to fixed portfolio percentages (0%, 6%, 12.5%, 25%).'}

### Process
{'steps': ['Import libraries and set up environment (Qiskit, Nashpy, pandas, yfinance, NumPy, Matplotlib).', 'Acquire market data from Yahoo Finance for a 5-year window and build a pool of 15 stocks.', 'Randomly select 4 assets per experiment run and compute expected returns (μ) and covariance matrix (Σ).', "Set up mixed-strategy game (Up and Down payoff matrices) between Investor (A) and other investor (B) and compute mixed Nash equilibria using Nashpy; use resulting probabilities to adjust assets' expected returns/rewards.", 'Formulate quadratic program (QUBO) with 2-qubit per-asset encoding (one-hot constraint per asset to choose a single investment level) incorporating expected return, covariance (risk term q>0), and reward weights.', 'Convert QUBO to Ising Hamiltonian and build QAOA cost and mixing unitaries; initialize with Hadamard gates.', "Optimize QAOA variational parameters using COBYLA (classical optimizer) wrapped in Qiskit's MinimumEigenOptimizer; QAOA repetitions p=3, optimizer max iterations=250.", 'Execute circuit on a noiseless simulator, sample solutions, and collect bitstrings, objective values and solution probabilities.', 'Post-process results into human-readable investment tables, covariance heatmaps, and portfolio growth simulations; compare to NASDAQ and S&P 500 baselines.'], 'notes': 'Some implementation-level settings (shots, random seeds, exact Qiskit backend name) are not specified in the paper.'}

### Output
{'formats': ['Sampled bitstrings with objective values and sampling probabilities', 'Optimal investment strategy tables (mapping bitstrings to investment levels and amounts)', 'Covariance matrix heatmaps', 'Portfolio growth time-series plots (simulated) and performance metrics'], 'metrics_reported': ['Annual expected return', 'Total return over multi-year windows', 'Sharpe ratio', 'Objective function value (QUBO/Ising energy)'], 'baselines': ['NASDAQ-100 total return', 'S&P 500 total return']}

### Parameters
- num_assets_used: 4
- qubit_encoding: 2 qubits per asset (4 discrete investment levels)
- example_total_qubits: 8
- QAOA_layers_p: 3
- classical_optimizer: COBYLA
- optimizer_max_iterations: 250
- risk_parameter: q (positive scalar; user-specified in mean-variance objective)
- investment_level_percentages: {'dont_invest': '0%', 'invest_low': '6% (IV/16)', 'invest_medium': '12.5% (IV/8)', 'invest_high': '25% (IV/4)'}
- simulator_noise: noiseless (perfect simulator)

### Hardware
{'backend': 'Noiseless perfect quantum simulator (Qiskit)', 'provider': 'Qiskit / IBM software stack (explicit QPU model not used)', 'QPU_model': None, 'notes': 'Paper specifies a perfect noiseless simulated quantum computer; exact Qiskit simulator backend (Aer vs. statevector) and other low-level settings are not stated.'}

### Reproducibility
Authors provide a GitHub repository link with the full Python implementation (data preprocessing, QAOA solver, Nash equilibrium and evaluation). Data source is public (Yahoo Finance via yfinance). However, several low-level details are missing from the manuscript (exact Qiskit backend name, random seeds, number of shots, exact payoff/noise smoothing parameters), which may affect exact reproduction of numerical outputs.
## Findings
- [supported] The authors present a workflow to encode a mean–variance portfolio optimization into a QUBO/Ising Hamiltonian and to solve it with QAOA (hybrid quantum/classical).
- [supported] The paper implements a 2-qubit encoding per asset to represent four discrete investment levels (Don't Invest, Low, Medium, High) and maps those to percentages of initial capital (0%, 6%, 12.5%, 25%).
- [supported] A mixed-strategy Nash equilibrium (game‑theoretic module using Nashpy) is integrated to produce per-asset probability distributions over the four investment levels and to modify expected returns used by the QUBO.
- [supported] The hybrid algorithm (QAOA with p=3, COBYLA classical optimizer with up to 250 iterations) is implemented in Qiskit and run on a noiseless quantum simulator; results, tables and plots are produced and code is published in a GitHub repository.
- [supported] In the authors' noiseless-simulator experiments on randomly selected 4-asset portfolios the hybrid (2-qubit per asset) algorithm produced simulated portfolio growth curves that the authors state often exceed the 5-year returns of NASDAQ-100 and S&P 500 benchmarks in their test cases.
- [supported] The authors report simulated Sharpe ratios above 2 for their hybrid approach in some experiments.
- [speculative] The authors claim that adding qubits (i.e., scaling to many qubits / many assets on less noisy hardware) would enable quantum portfolio optimization to produce 'Annual Expected Returns never even seen in modern history' and to revolutionize portfolio management.
- [speculative] The paper asserts that combining quantum optimization with game-theoretic mixed strategies provides improved adaptability and hedging against market uncertainty compared to classical mean–variance optimization.
- [speculative] The authors suggest that the 2-qubit encoding (4 investment levels) gives better risk-adjusted performance (higher long-run Sharpe) than the simpler 1-qubit invest/not-invest encoding.
- [speculative] The authors assert that QAOA (as used) is a practical route to near-term quantum portfolio optimization under realistic market data when combined with classical preprocessing and optimizers.
- [speculative] The paper states that a future low-noise, large-qubit quantum computer would transform finance sectors (mutual funds, hedge funds, ETFs) and enable large-scale, superior portfolio optimization.
- [supported] The paper provides concrete outputs from runs (e.g., optimal bitstring selections with associated objective values and sampling probabilities) illustrating the algorithm's sampling behavior on their simulator.
- [supported] The authors provide example payoff matrices (Up and Down states) and show how these are used to derive mixed strategies for the game-theoretic component.

**Results summary:** The preprint describes a hybrid classical/quantum pipeline that translates a mean–variance portfolio objective into a QUBO/Ising Hamiltonian, augments expected returns with a mixed‑strategy Nash equilibrium, and solves the optimization with QAOA (p=3) using COBYLA on a noiseless Qiskit simulator. They introduce a 2‑qubit per‑asset encoding to represent four investment levels and produce simulated outputs (covariance matrices, mixed‑strategy probabilities, optimal bitstrings, and portfolio growth plots). In their simulated experiments on randomly selected 4‑asset portfolios the authors report that their hybrid approach often produced higher simulated 5‑year returns than NASDAQ‑100 and S&P 500 benchmarks and achieved Sharpe ratios reported above 2. The work is implementation‑focused (code published) but results are from a noise‑free simulator and the broader claims about transformative real‑world advantage are presented as future prospects rather than demonstrated on real quantum hardware.

**Performance claims:**
- Algorithm configuration: QAOA layers p = 3; classical optimizer COBYLA with max 250 iterations. [supported]
- Investment level mappings: Don't Invest = 0%; Invest Low = 6% (IV/16); Invest Medium = 12.5% (IV/8); Invest High = 25% (IV/4). [supported]
- Reported simulated Sharpe ratio > 2 for the hybrid algorithm in some experimental runs. [supported]
- Reported that NASDAQ produced a 5-year total return of 118.8% and S&P 500 produced 109% (cited external sources). [supported (citation reported by authors)]
- Authors claim their 2-qubit hybrid algorithm produced simulated 5-year returns that 'surpass both Investment Funds' (NASDAQ and S&P 500) on average in many randomized asset selections. [supported (simulation evidence in paper)]
- Appendix example: Optimal selection bitstring [0. 1. 0. 1. 0. 1. 0. 1.] with value 0.0213 and sampling probability 0.0196 from the QAOA solver output. [supported]
- Example 1‑qubit result: Optimal selection [0. 1. 1. 1.] value 0.0018 with sampling probability 0.0639. [supported]
## Quantum advantage claim
**Classification:** speculative

The paper reports simulated instances (noiseless simulator) where the hybrid QAOA + game‑theory pipeline produced higher returns than benchmarks for some randomized 4‑asset portfolios; however these are simulation results on a perfect device with small problem sizes and do not demonstrate a general or hardware-based quantum advantage. The claim that scaling to low-noise, large‑qubit devices will realize transformative, historically unprecedented returns is speculative and not empirically demonstrated.
## Limitations
- Author-stated: Small toy model scale — experiments use very few qubits (1-2 qubits) and only 4 assets per run, limiting realism and generalizability.
- Author-stated: Experiments run on a perfect simulated (noise-free) quantum computer rather than real, noisy hardware.
- Author-stated: Simplified decision model despite extension to 2-qubit (4-level) encoding — investment granularity remains coarse (only four discrete investment levels).
- Author-stated: Game-theory component is simplified — a two-player setting (Investor A vs one other investor/hedge fund), binary market states (Up/Down), and handcrafted payoff matrices.
- Author-stated: Use of a mean–variance objective only (variance as the risk measure), which ignores other risk dimensions (tail risk, CVaR, drawdown etc.).
- Author-stated: Limited QAOA settings reported (three layers, COBYLA optimizer with 250 iterations) — limited exploration of algorithmic/hyperparameter choices.
- Author-stated: Randomized asset selection procedure and limited benchmarking (comparison to indices noted but not a rigorous, controlled benchmark across many trials).
- [inferred] The results rely on historical-estimated expected returns and covariances (5-year window) — exposing the approach to estimation error and nonstationarity.
- [inferred] No transaction costs, slippage, liquidity constraints, market impact, or trading constraints are modeled — results may be optimistic for real trading.
- [inferred] Handcrafted payoff matrices and noise injection in the game-theory model are ad hoc and may not reflect calibrated market interactions.
- [inferred] The mixed-strategy Nash model scales poorly conceptually to many market participants; only two-player interactions are considered.
- [inferred] Lack of rigorous statistical validation or sensitivity analysis (no confidence intervals, no ablation studies, no cross-validation of results reported).
- [inferred] Comparison to broad benchmarks (NASDAQ, S&P 500) is potentially misleading because the portfolio universe, leverage, constraints, and risk profiles differ.
- [inferred] Hardware-implementation challenges (noise, limited connectivity, error rates, readout errors) are not addressed beyond noting they exist; no mitigation strategies tested.
- [inferred] The work does not include operational concerns: latency, real-time data ingestion, rebalancing frequency, or integration with execution systems.
- [inferred] The QUBO-to-Ising/Hamiltonian translation and reward-weight design are described at high level; full reproducibility and numerical stability details appear limited.
- [inferred] The economic plausibility of reward weights and deterministic mapping from bitstrings to portfolio percentages (fixed IV fractions for levels) is simplistic and may not generalize.
## Open questions
- How will the proposed hybrid quantum/classical + game-theory approach scale as the number of qubits and assets increases (hundreds to thousands)?
- What is the expected impact of realistic, noisy quantum hardware on solution quality and stability of QAOA-based portfolio optimization?
- How sensitive are the reported performance gains to choice of hyperparameters (QAOA depth, classical optimizer, risk parameter q, reward weights)?
- How robust are results across different market regimes, rolling windows, and out-of-sample tests (including extreme events)?
- How should payoff matrices and mixed-strategy utilities be calibrated from market data (instead of handcrafted values)?
- Can the mixed-strategy Nash framework be extended to model many interacting market participants (multi-player games) and network effects, and how would that scale computationally?
- How to incorporate realistic market frictions — transaction costs, slippage, liquidity limits, shorting/borrowing costs — into the QUBO formulation?
- How to extend beyond mean–variance objectives to incorporate tail risk measures (CVaR), drawdown control, or investor-specific utility functions in the quantum formulation?
- What is the trade-off between investment discretization (more qubits / finer levels) and computational/measurement complexity on quantum devices?
- How to validate and statistically test whether the algorithmic improvements over classical baselines are significant and persist out-of-sample?
- What is the effect of estimation error in expected returns and covariances on the quantum optimizer’s output, and how can robust estimation be integrated?
- How to integrate quantum optimizer outputs into operational portfolio management (real-time rebalancing, execution, compliance)?
- Which quantum algorithms (beyond QAOA) or hybrid heuristics might perform better for large-scale portfolio optimization?
- What hardware and software advances (noise reduction, error mitigation, connectivity, compiler optimizations) are required before practical deployment in financial services?

**Future work:**
- Investigate hybrid quantum–classical frameworks further (scale up qubit count and asset universe) to evaluate performance at more realistic sizes.
- Comparative risk modeling: extend beyond mean–variance to alternative risk measures and comparative frameworks.
- Study real-time market responsiveness: incorporate dynamic rebalancing and streaming data into the hybrid algorithm.
- Evaluate performance on realistic noisy quantum hardware and explore error mitigation techniques.
- Calibrate and validate game-theoretic payoff matrices from empirical market data and extend to multi-player settings.
- Include transaction costs, liquidity constraints, and other market frictions in the QUBO/Ising formulation.
- Perform robustness and sensitivity analyses (hyperparameters, QAOA depth, optimizer choice, estimation windows) and statistical validation.
- Explore finer-grained investment encodings (more qubits per asset) and study the trade-offs in complexity and solution quality.
- Extend the framework to institutional settings (mutual funds, hedge funds, ETFs) and assess operational integration challenges.
- Compare QAOA with other quantum and classical optimization algorithms at scale to identify the most promising approaches.
## Key ideas
- #idea:hybrid-approach — Mean–variance portfolio optimization is encoded as a QUBO/Ising Hamiltonian and solved with a hybrid QAOA + classical optimizer (COBYLA) pipeline.
- #idea:quantum-advantage — On noiseless simulator experiments with 4-asset instances (2 qubits per asset, 8 qubits total) the QAOA-based solver is reported to produce higher simulated annual expected returns and favorable Sharpe ratios versus market baselines (NASDAQ-100, S&P 500).
- #idea:hybrid-approach — The pipeline integrates a game-theoretic mixed-strategy layer (computed with Nashpy) to adjust expected-return inputs prior to QUBO formulation, combining classical game theory and quantum optimization.
- #idea:near-term-feasibility — Authors discuss current hardware limitations and present the approach as a toy/NISQ-era exploration; they provide a GitHub implementation for reproducibility (though low-level details are missing).
- #idea:quantum-advantage — Uses a multi-level per-asset encoding (2 qubits -> four discrete investment levels) to represent richer allocation options than binary invest/not-invest formulations.
## Contradictions
- The paper claims superior portfolio metrics from the quantum approach but all experiments are on a noiseless simulator for very small (4-asset) toy instances and compare to market indices rather than to classical optimization baselines on the same problem formulation; this undermines the strength of the quantum-advantage claim and is effectively a contradiction between claimed outperformance and limited, simulation-only evidence.
- Reproducibility and realism issues (missing simulator backend details, shots, random seeds, absence of real QPU experiments) contradict implications that the reported results indicate near-term practical superiority on real hardware.
## Notable quotes
<!-- Researcher-added — verbatim quotes with page references -->

## Researcher notes
<!-- Researcher-added — not LLM generated -->
