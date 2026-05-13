---
aliases:
- Performance Comparison of QAOA Mixers for Ternary Portfolio Optimization
- Performance Comparison QAOA Mixers
authors:
- Shintaro Yamamura
- Satoshi Watanabe
- Masaya Kunimi
- Kazuhiro Saito
- Tetsuro Nikuni
auto_detected: true
classification: ''
contradiction_flags:
- contradiction:classical-vs-quantum
- contradiction:scalability
doi: ''
evaluation_type: simulator
evidence_type: ''
has_quantitative_results: true
idea_tags:
- idea:quantum-advantage
- idea:near-term-feasibility
- idea:hybrid-approach
journal_or_venue: arXiv (quant-ph), preprint arXiv:2602.21562
methodology_tags:
- variational-nisq
- hybrid-quantum-classical
paper_type: ''
quantum_advantage_claim: not-applicable
related_papers: []
relevance_phase1: high
relevance_phase3: high
source_type: preprint
source_type_confidence: high
step1_date: '2026-04-14T09:47:50.759817'
step1_model: gpt-5-mini
step2_date: '2026-04-14T09:47:50.759817'
step2_model: gpt-5-mini
step3_date: '2026-04-14T09:47:50.759817'
step3_model: gpt-5-mini
step4_date: '2026-04-14T09:47:50.759817'
step4_model: gpt-5-mini
step5_date: '2026-04-14T09:47:50.759817'
step5_model: gpt-5-mini
step6_date: '2026-04-14T09:47:50.759817'
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
- method/variational-nisq
- method/hybrid-quantum-classical
- idea/quantum-advantage
- idea/near-term-feasibility
- idea/hybrid-approach
- contradiction/classical-vs-quantum
- contradiction/scalability
title: Performance Comparison of QAOA Mixers for Ternary Portfolio Optimization
topic_tags:
- portfolio-optimization
year: '2026'
zotero_key: ''
---

## Abstract summary
The authors implement QAOA for a ternary portfolio optimization (long, no position, short) and compare five mixer designs (Standard, XY Ring, XY Parity Ring, XY Full, and QAMPA) using simulations on DAX30-based instances (N=5,8). They evaluate performance under ideal and depolarizing-noise conditions and find XY-based mixers (especially XY Full and QAMPA) outperform the Standard Mixer in noiseless settings, but their advantage decreases with realistic noise due to larger circuit depth and fragile Dicke-state initialization; the optimal mixer depends on circuit depth and noise strength.
## Methodology
The study implements and evaluates the Quantum Approximate Optimization Algorithm (QAOA) for a ternary portfolio optimization problem (asset states: long, no-position, short). Each asset is encoded using two qubits (x+ , x-), with zi = x+ - x-. The cost function is the mean-variance objective (risk term from covariance matrix and expected return term), with an equality constraint on the sum of zi enforced either as a soft penalty (Standard Mixer) or exactly by restricting dynamics to the feasible subspace (XY-based Mixers). The authors compare five mixer/unitary ansatz variants: Standard Mixer, XY Ring, XY Parity Ring, XY Full, and QAMPA. For XY Mixers the initial state is a Dicke state (fixed Hamming weight) prepared deterministically using a Split-and-Cyclic-Shift style construction; for the Standard Mixer the initial state is the uniform |+> state and a penalty term A is selected via an iterative procedure (Algorithm 1). QAOA layers p ∈ {1,3,5,7} are tested; parameter initialization uses a grid search for p=1 and several interpolation/extrapolation heuristics from lower-depth optima for p>1, and classical optimizers (SLSQP with exact statevector evaluations, Nelder–Mead with sampled Qasm, COBYLA for noisy density-matrix runs) are used. Simulations are performed with Qiskit simulators (Statevector, Qasm, DensityMatrix). Noise robustness is assessed by applying a single-qubit depolarizing channel after every one- and two-qubit gate, scanning noise strength η ∈ [0,0.01] (step 0.001). Evaluation metrics are the approximation ratio r (normalized cost relative to feasible min/max) and the optimal-solution probability P. Experiments use historical DAX30 data (via yfinance) to estimate daily returns and annualized expected returns and covariances. Multiple random problem instances are generated (20 instances for N=5,B=2 and 10 instances for N=8,B=4) and results are reported as averages with standard deviations across instances.

**Algorithms used:** QAOA
**Frameworks:** Qiskit, yfinance

**Experimental setup:** Simulated experiments using Qiskit Statevector (exact), Qasm (shot-based) and DensityMatrix (noisy) simulators. QAOA depths p in {1,3,5,7}. Shot counts: 3000 (Qasm N=5 runs), 10000 (Qasm N=8 runs), 8192 (DensityMatrix noisy runs), 20000 shots used for feasibility (Dicke) measurement statistics. Depolarizing channel applied after every 1- and 2-qubit gate with η varied from 0 to 0.01 in steps of 0.001. Classical optimizers: SLSQP (Statevector), Nelder–Mead (Qasm), COBYLA (DensityMatrix noisy).

**Dataset:** Historical daily adjusted closing prices for constituents of the German DAX30 index, retrieved from Yahoo Finance via the yfinance Python library, covering 2016-01-01 to 2020-12-31. Specific stocks used for noise experiments: LIN.DE, BAYN.DE, VNA.DE, MTX.DE, MUV2.DE.
## Experiment details
### Input
{'source': 'Yahoo Finance via yfinance', 'time_span': '2016-01-01 to 2020-12-31 (5 years)', 'assets': 'DAX30 constituents (subsets used per experiment: N=5 and N=8 cases; for noise study a 5-asset set listed above)', 'instances': '20 random portfolios for N=5,B=2; 10 random portfolios for N=8,B=4', 'preprocessing': 'Drop dates with missing data; compute daily simple returns rt,i; empirical average daily return rbar_i; annualize expected returns via geometric compounding assuming 252 trading days; estimate daily covariance via unbiased sample covariance and annualize by multiplying by 252.'}

### Process
1) Formulate ternary portfolio optimization: cost F(z) = q * risk (covariance) - (1-q) * expected return, with q=1/3 and equality constraint sum_i zi = B. 2) Encode each asset as two qubits (x+ , x-), map zi to (Z- - Z+)/2 and construct cost Hamiltonian and cost unitary UF(γ). Scale factor λ = 4N for Standard Mixer and λ = 2N(2N-1) for XY/QAMPA. 3) Prepare initial state: uniform |+>^{2N} for Standard; Dicke state |D_{2N}^{N+B}> (then X gates on short qubits) for XY-based mixers using a deterministic SCS-based construction. 4) Implement mixer unitaries: Standard (single-qubit X rotations), XY Ring, XY Parity Ring, XY Full (pairwise XY rotations across adjacency or all pairs), and QAMPA (combined mixer-phase two-qubit blocks synthesized via KAK decomposition). 5) For Standard Mixer include penalty term A*(sum zi - B)^2 with A determined by Algorithm 1. 6) Build p-layer QAOA circuits (p ∈ {1,3,5,7}) and optimize parameters (γ, β): initial grid search for p=1, parameter extrapolation heuristics for p>1. 7) Classical optimization: SLSQP with Statevector; Nelder–Mead with Qasm; COBYLA for noisy DensityMatrix. 8) Simulate: evaluate expectation ⟨F⟩, sample output distributions (shots), compute metrics (approximation ratio r and optimal probability P). 9) Noise study: apply depolarizing channel after each gate, sweep η ∈ {0,0.001,...,0.01}, repeat simulations and report averaged metrics across instances.

### Output
Outputs are averaged approximation ratio r (normalized relative to feasible min/max) and optimal-solution probability P reported as functions of QAOA depth p, mixer type, and noise strength η. Comparisons are made across five mixer variants. Baselines include the Standard Mixer (with penalty) and the XY-family mixers constrained to the feasible subspace. Results include averages and standard deviations across multiple random problem instances and shot-noise/noise-model conditions.

### Parameters
- encoding: 2 qubits per asset (x+, x-); zi = x+ - x-
- q_tradeoff: 0.3333333333
- N_values: [5, 8]
- constraints: {'B_for_N5': 2, 'B_for_N8': 4}
- qubits: {'N=5': 10, 'N=8': 16}
- QAOA_depths_p: [1, 3, 5, 7]
- parameter_initialization: grid search for p=1; interpolation/extrapolation heuristics from lower p for p>1
- classical_optimizers: {'Statevector': 'SLSQP', 'Qasm': 'Nelder–Mead', 'DensityMatrix (noisy)': 'COBYLA'}
- shots: {'Qasm_N=5': 3000, 'Qasm_N=8': 10000, 'DensityMatrix_noise_runs': 8192, 'Dicke_feasibility_measurement': 20000}
- noise_model: Depolarizing channel applied after every 1- and 2-qubit gate; E(rho)=eta*I/2^{2N} + (1-eta) rho
- noise_strengths: eta in {0, 0.001, 0.002, ..., 0.01}
- lambda_scaling: {'Standard': '4N', 'XY_and_QAMPA': '2N(2N-1)'}
- penalty_method: Quadratic penalty A*(sum zi - B)^2 with A chosen by iterative Algorithm 1 to separate infeasible minima
- number_of_random_instances: {'N=5': 20, 'N=8': 10}

### Hardware
{'simulators': ['Qiskit Statevector Simulator (exact)', 'Qiskit Qasm Simulator (shot-based)', 'Qiskit DensityMatrix Simulator (noisy)'], 'QPU_model': None, 'cloud_provider': None, 'notes': 'All experiments performed via simulators in Qiskit; no physical quantum hardware used.'}

### Reproducibility
{'code_repository': 'https://github.com/Shintaro-Yamamura/QAOA-Ternary-Portfolio', 'available_materials': 'Authors state that source data and simulation data for N=5 and N=8 and noisy runs are available in the GitHub repository.', 'assessment': 'Code and simulation data are provided by the authors; exact simulator versions, random seeds, and some low-level implementation details (e.g., Qiskit version, numerical tolerances) are not specified in the preprint but can likely be recovered from the repository.'}
## Findings
- [supported] In noiseless simulations of ternary portfolio optimization (N=5, B=2 and N=8, B=4), XY-type mixers (XY Ring, XY Parity Ring, XY Full, QAMPA) outperform the Standard Mixer in both approximation ratio and optimal-solution probability.
- [supported] Among XY mixers, the XY Full Mixer and QAMPA converge fastest in noiseless simulations, reaching very high approximation ratios (reported >99% for N=5, B=2) and higher ground-state probabilities (reported P ≃ 0.6 for that instance).
- [supported] XY mixers can be implemented to preserve the investment-constraint subspace exactly (hard constraint) by preparing an initial Dicke-like state supported only on feasible Hamming-weight bitstrings; Standard Mixer requires a penalty term and explores the full Hilbert space.
- [supported] When a realistic depolarizing-noise model is applied (noise channel after each 1- and 2-qubit gate), the advantage of XY mixers degrades and there exist noise-strength thresholds where the Standard Mixer becomes superior; the threshold depends on QAOA depth p.
- [supported] The paper reports specific numerical crossover noise thresholds (η) where the Standard Mixer overtakes XY mixers: (approx.) for approximation ratio r: p=1: η≈0.003; p=3: η≈0.001; p=5: η≈0.0005; p=7: η≈0.0005. For optimal probability P: p=1: η≈0.005; p=3: η≈0.003; p=5: η≈0.001; p=7: η≈0.001.
- [supported] The initial Dicke-state preparation required for XY mixers introduces substantial circuit depth and CNOT count (scales with problem size), whereas the Standard Mixer initial state requires only Hadamards (constant depth, no entangling gates); this overhead makes XY mixers more susceptible to noise.
- [supported] Depolarizing noise rapidly reduces the probability mass in the constraint-satisfying Dicke subspace (measured Pfeasible decreases monotonically with η), explaining why XY mixers lose their advantage under noise.
- [supported] Ternary encoding (two qubits per asset) doubles qubit requirements compared to binary formulations and enlarges the search space (e.g., for N=5, Standard Mixer explores 2^{10}=1024 states while XY mixers restrict to 120 feasible portfolios; for N=8 feasible portfolios = 15,504), making optimization harder for fixed N.
- [supported] Recommendation from simulations: on near-term noisy hardware, shallow/low-overhead mixers (Standard or XY Ring) are preferable; more expressive mixers (XY Full, QAMPA) are advantageous only when noise is sufficiently low or mitigated.
- [speculative] The assertion that QAMPA reduces the number of CNOT gates to approximately three-quarters of the conventional XY Full Mixer is presented as an advantage of QAMPA (cited from prior work); the paper does not present a direct empirical CNOT-count comparison for every case.
- [speculative] The broader implication that mixer choice should be selected based on device noise characteristics and QAOA depth is advocated as a design guideline (informed by the simulations) but generalization to all problem sizes and other noise models is not rigorously proven here.

**Results summary:** This preprint implements QAOA for a ternary portfolio optimization (long / no-position / short) using a two-qubit-per-asset encoding and compares five mixer ansätze (Standard, XY Ring, XY Parity Ring, XY Full, QAMPA) through numerical simulations on historical-like instances (DAX constituents) and under a depolarizing noise model. In noiseless statevector simulations, XY mixers—especially XY Full and QAMPA—show markedly better approximation ratios and higher optimal-solution probabilities than the Standard Mixer. However, when depolarizing noise is added after each gate, the performance advantage of XY mixers degrades due to (i) the large gate overhead needed to prepare the Dicke initial state and (ii) the fragility of that Dicke-state subspace to noise. The study quantifies crossover noise strengths (η) at which the Standard Mixer becomes preferable, and concludes that the optimal mixer choice depends on both QAOA depth and hardware noise levels. The work also documents the circuit-cost scaling of Dicke preparation versus trivial Hadamard initialization.

**Performance claims:**
- For N=5, B=2 (noiseless Statevector simulations): XY Full Mixer and QAMPA converge most rapidly, achieving approximation ratio r > 99% and optimal-solution probability P ≃ 0.6.
- For N=5, Standard Mixer explores 2^{10} = 1024 candidate states while XY mixers restrict the search to 120 feasible portfolios (combinatorics for the chosen B).
- For N=8, B=4 the number of feasible ternary portfolios is reported as 15,504; overall performance (r and P) degrades relative to N=5.
- Depolarizing-noise crossover thresholds (approximate η) where Standard Mixer overtakes XY mixers for approximation ratio r: p=1: η≈0.003; p=3: η≈0.001; p=5: η≈0.0005; p=7: η≈0.0005.
- Depolarizing-noise crossover thresholds (approximate η) for optimal probability P: p=1: η≈0.005; p=3: η≈0.003; p=5: η≈0.001; p=7: η≈0.001.
- The Dicke-state preparation circuit depth and CNOT count grow substantially with the number of qubits (authors report roughly linear scaling in depth and large entanglement cost; e.g., with 10 qubits the preparation circuit requires hundreds of gates), whereas Standard Mixer initialization is constant-depth with no CNOTs.
## Quantum advantage claim
**Classification:** not-applicable

The paper conducts a comparative study of QAOA mixer ansätze via classical simulations (statevector, density-matrix, and noisy simulators) for small ternary portfolio instances; it does not claim or demonstrate a computational quantum advantage over classical algorithms. Results are limited to ansatz/mixer performance and noise sensitivity on small problem sizes and do not establish superiority relative to best classical optimization methods.
## Limitations
- Study is based on numerical simulations only (Statevector, Qasm, DensityMatrix simulators) rather than experiments on real quantum hardware.
- Noise model limited to depolarizing channel applied after each gate; other realistic noise sources (e.g., amplitude damping, phase damping, crosstalk, calibration errors) were not considered.
- Problem sizes studied are small (N = 5 and N = 8 assets); scalability to larger, practically relevant portfolios is not demonstrated.
- Ternary encoding requires two qubits per asset, effectively doubling qubit count compared with binary formulations, which increases circuit size and reduces performance.
- XY mixers require preparation of Dicke-type initial states with substantial gate depth and many CNOTs, causing high pre-variational noise overhead and fragility under decoherence.
- Comparisons are limited to the five mixer types considered (Standard, XY Ring, XY Parity Ring, XY Full, QAMPA); other mixer designs and encodings (e.g., qutrits, unary encodings, Grover-Mixers, subspace search variants) were not benchmarked.
- Classical parameter optimization choices (SLSQP for Statevector, Nelder–Mead/COBYLA for Qasm/DensityMatrix) may influence results; sensitivity to optimizer choice and hyperparameters was not systematically explored.
- Constraint enforcement for the Standard Mixer relies on a penalty method with a heuristic procedure to choose the penalty coefficient; robustness to penalty tuning and effect on optimization landscape were not fully characterized.
- Only one financial dataset (DAX constituents over a fixed 5-year window) was used; results may depend on data selection and statistical estimation of returns/covariances.
- Evaluation metrics are limited to approximation ratio and optimal-solution probability; other practical metrics (e.g., out-of-sample performance, transaction costs, risk-adjusted returns) were not considered.
- The study focuses on QAOA and does not integrate or compare advanced algorithmic variants (e.g., Warm-start QAOA, ADAPT-QAOA, R-QAOA) in the ternary portfolio context.
- [inferred] The depolarizing-noise crossover thresholds observed imply very stringent noise requirements for XY Full / QAMPA to be advantageous; the feasibility of achieving such error rates on near-term devices is unclear.
- [inferred] The impact of limited qubit connectivity/topology on the practical implementation of the more connected mixers (XY Full, QAMPA) was not assessed.
- [inferred] Sampling precision (finite shot noise) and measurement budget effects were only partially explored (e.g., shots = 3000 or 10000); sensitivity to lower shot counts typical of near-term hardware was not fully analyzed.
- [inferred] Potential trainability issues such as barren plateaus in the ternary encoding were noted as general concerns but not empirically investigated for these instances.
## Open questions
- How do the relative performances of different mixers scale with problem size (larger N) and larger feasible subspaces?
- What are the practical noise thresholds (for realistic noise types and device architectures) below which expressive XY-based mixers (XY Full, QAMPA) outperform the Standard Mixer?
- How do other, more realistic noise models (amplitude damping, phase damping, crosstalk, non-Markovian noise) affect the observed crossover and mixer robustness?
- Can Dicke-state preparation be made far more noise-resilient or replaced by lower-overhead initializations that still restrict dynamics to feasible subspaces?
- How effective are error mitigation techniques or circuit compilation/optimization strategies at restoring XY Mixer advantages under realistic noise?
- What is the impact of device connectivity constraints and routing overhead on the relative cost and performance of each mixer in hardware implementations?
- How do alternative encodings for ternary variables (e.g., qutrits, unary encodings, more compact embeddings) change qubit requirements, circuit depth, and noise sensitivity?
- Can advanced QAOA variants (warm-starts, ADAPT-QAOA, R-QAOA) improve performance or noise robustness for ternary portfolio optimization compared with the vanilla QAOA mixers studied?
- How sensitive are results to the choice of classical optimizers, initialization heuristics, and parameter transfer strategies between depths?
- How do the reported performance metrics translate to economic/financial utility measures (out-of-sample return, Sharpe ratio, turnover, transaction costs) in realistic trading simulations?
- What are the trade-offs between expressiveness of the ansatz and hardware feasibility (gate counts, depth) for near-term devices?
- To what extent do estimation errors in returns/covariances (finite historical data, nonstationarity) affect QAOA solution utility and algorithmic comparisons?

**Future work:**
- Design mixers and initial states that remain effective even when strict constraint preservation cannot be guaranteed (explicitly mentioned).
- Select mixers and ansatz based on hardware noise characteristics and pursue hardware-aware ansatz design (explicit recommendation).
- Explore noise mitigation and suppression strategies to enable the use of more expressive mixers like XY Full and QAMPA (implied in discussion).
- Develop and test lower-overhead or more noise-robust Dicke/state-preparation circuits, or alternative initializations that restrict to (or bias toward) feasible subspaces (suggested in conclusion).
- Investigate extensions and comparisons with advanced QAOA variants (Warm-start QAOA, R-QAOA, ADAPT-QAOA) in the ternary portfolio context (mentioned as related methods in the paper).
## Key ideas
- #idea:quantum-advantage — In noiseless statevector simulations XY-based mixers (particularly XY Full and QAMPA) achieve higher approximation ratios and optimal-solution probabilities than the Standard Mixer for small ternary portfolio instances (N=5,8).
- #idea:near-term-feasibility — The observed quantum advantage is highly sensitive to realistic noise: depolarizing noise applied after each gate rapidly reduces the benefit of XY-based mixers because of larger circuit depth and fragile deterministic Dicke-state initialization.
- #idea:hybrid-approach — Practical implementation relies on hybrid methods: classical optimizers (SLSQP, Nelder–Mead, COBYLA), grid search and parameter-extrapolation heuristics, and a classical iterative penalty-selection procedure for the Standard Mixer.
- #idea:near-term-feasibility — The optimal mixer choice depends on QAOA depth and noise strength; there is no universally best mixer across depths and noise regimes for the tested problem sizes.
- #idea:quantum-advantage — Constraining dynamics to the feasible subspace (XY-family mixers with Dicke initialisation) can outperform penalty-based approaches when noise is negligible, showing an advantage of problem-tailored mixer design.
## Contradictions
- The paper reports that while XY-based mixers outperform the Standard Mixer in ideal (noise-free) simulations, this advantage largely disappears under realistic depolarizing noise — contradicting any blanket claim that these quantum mixers will outperform classical/penalty approaches on near-term hardware.
- The study shows that larger circuit depth and the complexity of deterministic Dicke-state preparation make XY-based approaches fragile in noisy settings, undermining scalability claims: improved performance at small N in noiseless simulation does not straightforwardly scale to noisy, larger instances.
## Notable quotes
<!-- Researcher-added — verbatim quotes with page references -->

## Researcher notes
<!-- Researcher-added — not LLM generated -->
