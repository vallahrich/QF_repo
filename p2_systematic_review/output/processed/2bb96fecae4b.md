---
aliases:
- Portfolio rebalancing experiments using the Quantum Alternating Operator Ansatz
- Portfolio rebalancing experiments using
authors:
- Mark Hodson
- Brendan Ruck
- Hugh (Hui Chuan) Ong
- David Garvin
- Stefan Dulman
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
journal_or_venue: arXiv preprint (arXiv:1911.05296)
methodology_tags:
- variational-nisq
- hybrid-quantum-classical
paper_type: ''
quantum_advantage_claim: speculative
related_papers: []
relevance_phase1: high
relevance_phase3: high
source_type: preprint
source_type_confidence: high
step1_date: '2026-04-14T09:54:05.648812'
step1_model: gpt-5-mini
step2_date: '2026-04-14T09:54:05.648812'
step2_model: gpt-5-mini
step3_date: '2026-04-14T09:54:05.648812'
step3_model: gpt-5-mini
step4_date: '2026-04-14T09:54:05.648812'
step4_model: gpt-5-mini
step5_date: '2026-04-14T09:54:05.648812'
step5_model: gpt-5-mini
step6_date: '2026-04-14T09:54:05.648812'
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
title: Portfolio rebalancing experiments using the Quantum Alternating Operator Ansatz
topic_tags:
- portfolio-optimization
year: '2019'
zotero_key: ''
---

## Abstract summary
This preprint implements and evaluates a discrete portfolio rebalancing use case on an idealized gate-model quantum simulator, modeling discrete lots, non-linear trading costs, and an investment constraint. The authors design a novel two-spin encoding and hard-constraint parity mixers for the Quantum Alternating Operator Ansatz, compare it to the original QAOA with penalty-based soft constraints, and report that the constrained approach can identify near-optimal portfolios (within ~5% of adjusted returns) and optimal risk for an eight-stock example.
## Methodology
The authors formulate a discrete portfolio rebalancing optimization as a constrained combinatorial problem over N assets with ternary decisions per asset (long, short, flat) encoded using two binary/spin variables per asset. They derive spin-system expressions for a Markowitz-style risk-return objective and a non-linear fixed trading-cost term, and implement the investment constraint both as a soft quadratic penalty and as a hard constraint realized by entangled parity-ring mixers (a Quantum Alternating Operator Ansatz construction) with a feasible entangled initial state. Experiments are conducted on an idealized (noise-free) gate-model quantum simulator: (i) brute-force enumeration of the full 2^(2N) spin space to obtain baselines and verify feasibility counts; (ii) QAOA (original Quantum Approximate Optimization Algorithm with soft penalty) runs and (iii) QAOA with the Quantum Alternating Operator Ansatz (hard constraint mixers) runs. The outer classical variational optimization loop is run (Nelder–Mead cited as the classical optimizer), the circuit depth parameter p is varied, and performance metrics (expectation value of the cost operator, feasibility probability, cumulative cost distributions, adjusted returns, average portfolio risk, and number of trades) are compared to brute-force optima. They also investigate practical issues such as cost-function scaling (annualizing returns to avoid vanishingly small cost amplitudes) and set penalty coefficients by ensuring the penalty exceeds the unconstrained objective range.

**Algorithms used:** Quantum Approximate Optimization Algorithm (QAOA), Quantum Alternating Operator Ansatz (QAOA with hard-constraint/ parity mixers), Brute-force enumeration (baseline), Nelder–Mead (classical optimizer for variational loop)
**Frameworks:** Idealized gate-model quantum simulator (unnamed; cited reference [13])

**Experimental setup:** Noise-free, idealized gate-model quantum simulator. Simulations run with full state-vector expectation-value evaluation (no QPU noise or decoherence modeled). Initial-state choices: uniform |+>^N for soft-penalty QAOA; entangled Bell/pair parity initial state for hard-constraint QAOA. Circuit depth p varied (p = 1..4).

**Dataset:** Daily closing returns for ASX.20 equities for calendar year 2017 (252 trading days across 20 stocks). Experiments use an 8-stock subset selected from ASX.20 (AMP, ANZ, BHP, BXB, CBA, CSL, IAG, MQG).
## Experiment details
### Input
{'source': 'ASX.20 daily returns for 2017 (public/market price series; referenced as ASX.20 dataset in paper)', 'raw_size': '20 stocks × 252 trading days', 'subset_used': 'N = 8 stocks: AMP, ANZ, BHP, BXB, CBA, CSL, IAG, MQG', 'preprocessing': "Compute per-asset daily mean returns (µ_i) and covariance matrix (σ_ij). In some experiments inputs were annualized by multiplying µ and σ by 250 to improve QAOA parameter scaling. Normalization applied to objective terms (paper refers to 'normalized' returns/covariance and normalized trading cost T)."}

### Process
{'encoding': 'Two-spin encoding per asset: decision variables x+ (long) and x- (short), converted to spins s+ and s-. Position zi = x+ - x-. Degenerate both-long-and-short state penalized by trading-cost encoding.', 'objective_terms': 'CRR(s) (spin-form Markowitz risk-return), CTC(s) (piecewise spin-form trading cost conditional on previous position), plus PINV(s) soft quadratic penalty for investment constraint when using soft formulation.', 'constraint_realizations': 'Soft: add quadratic penalty PINV(s) to cost operator. Hard: implement two parity-ring mixers (one for long spins, one for short spins) with entanglement (Bell pairs) to ensure feasible subspace and prepare a feasible initial entangled state as per Eq.(21).', 'algorithms_and_sequence': ['Compute baseline via brute-force enumeration (2^(2N) states; for N=8: 65536 states, 1820 feasible) to obtain min/max C(s) and feasible-optimal solutions.', 'For soft-constraint QAOA: build cost Hamiltonian Csoft(s)=CRR+CTC+PINV; mixing Hamiltonian is standard transverse-field B = sum σx_i; initial state |+>^N; run variational loop.', 'For hard-constraint QAOA (Alternating Operator Ansatz): build cost Hamiltonian Chard(s)=CRR+CTC; mixing operators are parity-ring XY mixers applied separately to long and short spin subsets; prepare entangled feasible initial state; run variational loop constrained to feasible subspace.', 'Classical outer-loop optimizer (Nelder–Mead noted) optimizes circuit parameters {β, γ} for given depth p; p varied (p = 1..4).', 'Repeat runs with different random seeds (20 seeded runs reported) to gather statistics.'], 'parameter_experiments': 'Investigated penalty coefficient A choices (computed from range of unconstrained C(s)), impact of scaling (daily vs annualized inputs), trading cost T values (0 and 0.015), and risk-return tradeoff λ in {0.0, 0.9, 1.0}.'}

### Output
{'outputs_collected': ['Expectation values ⟨ψ1|C|ψ1⟩ for cost operators (used to guide classical optimizer)', 'Probability of measuring feasible solutions (feasibility rate)', 'Cumulative distribution of cost values across measured solutions', 'Adjusted portfolio returns (µ · z − CTC(z)) over multi-period rebalancing', 'Average portfolio risk (sqrt(z^T σ z)) over multi-period rebalancing', 'Number of trades over multi-period rebalancing', 'Comparison against brute-force optimal solutions (baselines) including feasibility and distance to optimal (e.g., within 5% adjusted returns)'], 'metrics_reported': ['Feasibility probability', 'Cumulative probability over cost values', 'Adjusted returns (net of trading costs)', 'Average portfolio risk', 'Number of trades'], 'baselines': 'Brute-force enumeration of full state space and feasible subspace; random uniform draws over all states and over feasible states used as additional baselines.'}

### Parameters
- num_assets: 8
- qubits: 16
- search_space_size: 65536
- feasible_count: 1820
- depth_p_values: [1, 2, 3, 4]
- classical_optimizer: Nelder–Mead (used for variational parameter optimization; artifact from optimizer discussed)
- random_runs: 20
- penalty_A_values_used: {'daily_returns_experiment': 0.03, 'annualized_returns_experiment': 0.75, 'multi-period_experiment': 2.5, 'selection_rule': 'A > max(C_unconstrained) - min(C_unconstrained)'}
- risk_return_lambda_values: [0.0, 0.9, 1.0]
- trading_cost_T_values: [0.0, 0.015]
- target_investment_D: 4
- shots: None
- noise_model: none (idealized/noiseless simulator)

### Hardware
{'simulator': 'Idealized gate-model quantum simulator (unnamed; cited as an idealized simulator and reference [13])', 'qpu_model': None, 'cloud_provider': None, 'noise': 'none (noise-free simulation)', 'notes': 'No specific simulator framework (e.g., Qiskit, Cirq) or executable environment was named in the paper; reference [13] (CBA simulator press article) is given as context.'}

### Reproducibility
The paper describes datasets (ASX.20 daily returns for 2017) and provides sufficient methodological detail (encodings, Hamiltonians, penalty selection rule, parameters tested, and the 8-stock subset), but does not provide code, parameter files, exact random seeds, or a named simulator implementation. Penalty A selection is specified by a rule but the raw intermediate values (max/min unconstrained C) are not tabulated for each experiment. Therefore full reproduction would require reimplementation of cost Hamiltonians and mixers from the equations in the paper and reconstruction of the exact simulator configuration; direct code and artifact links are not provided.
## Findings
- [supported] Implemented a discrete portfolio rebalancing formulation for N=8 assets using both the original QAOA (soft constraints) and the Quantum Alternating Operator Ansatz (hard constraints) on an idealized gate-model quantum simulator.
- [supported] Designed and implemented a two-spin encoding for long/short/no-hold positions and a conditional spin-system trading-cost function, and validated these encodings by brute-force enumeration and simulation.
- [supported] Developed a hard-constraint mixer based on entangled parity-ring mixers (parity bands and Bell-state entanglement) to enforce the investment constraint; in simulation this hard-constraint QAOA produced only feasible solutions (100% feasible probability).
- [supported] The soft-constraint QAOA (penalty-based) produced feasible solutions with substantially lower probability (reported between ~33% and ~66% in their experiments), validating sensitivity to penalty scaling.
- [supported] Demonstrated that data scaling matters: using annualized returns (multiplying daily mean and covariance by 250) improved mixing behavior and convergence properties in their QAOA simulations.
- [supported] For the 8-stock test problem and multi-period (6-month) rebalancing scenario the hard-constraint (Quantum Alternating Operator Ansatz) formulation found solutions with optimal risk and within ~5% of optimal adjusted returns for p=4 in the idealized simulator.
- [supported] Reported combinatorial problem sizes and baselines: with 16 spin variables (2 per asset) the full search space is 2^16 = 65,536 states; only 1,820 (≈2.78%) satisfy the D=4 investment constraint; brute-force baselines were used for comparison.
- [supported] Observed that deeper QAOA circuits (p=4) outperformed shallower ones (p=2) in their simulated experiments, and that the hard-constraint variant outperformed the penalty-based variant in this setting.
- [speculative] Claim that this application demonstrates potential tractability on NISQ hardware (i.e., could be relevant for near-term quantum devices) — based on idealized, noise-free simulation results rather than experiments on actual NISQ devices.
- [speculative] Suggested that the novel parity-mixer entanglement design is a promising template for other constrained combinatorial problems on gate-model NISQ devices, pending circuit-depth and noise analysis.
- [speculative] Recommended next steps (circuit depth/hardware resource analysis, noise impact simulation, experiments on current NISQ hardware) as necessary to assess end-to-end viability and potential quantum advantage.

**Results summary:** The authors implemented a discrete portfolio rebalancing problem (long/short/flat, fixed trading costs, investment constraint) for an 8-stock instance on an idealized noiseless gate-model quantum simulator, using both a penalty-based QAOA formulation and a hard-constraint Quantum Alternating Operator Ansatz with a novel entangled parity mixer. They validated encodings against brute-force baselines, found the hard-constraint approach produced only feasible solutions in simulation and generally outperformed the soft-constraint variant, and reported that with p=4 the hard-constraint QAOA identified portfolios within ~5% of optimal adjusted returns and achieved optimal risk for the tested small instance. The authors note important practical issues (data/cost scaling, penalty tuning) and characterize their claims as preliminary, recommending hardware/noise/circuit-depth follow-up work.

**Performance claims:**
- Identified portfolios within 5% of the optimal adjusted returns for the 8-stock instance when using the hard-constraint Quantum Alternating Operator Ansatz with p=4 (simulation).
- Hard-constraint QAOA returned feasible solutions with 100% probability in the simulator (for the tested settings).
- Soft-constraint (penalty) QAOA returned feasible solutions with ≈33% to 66% probability in the simulator (reported across runs and p values).
- Problem size enumerations: 16 spin variables (2 per asset), full space 2^16 = 65,536 states; feasible states 1,820 (≈2.78%) for D=4.
- Penalty scaling heuristics used: examples in experiments include A=0.75 (annualized single-run) and A=2.5 (monthly multi-period runs); trading cost used in multi-period experiments T=0.015.
- Upper bound on trades in the 6-month rebalancing scenario (D=4, zero initial holdings) is 28 trades; reported observed trade counts varied with λ (risk-return parameter).
- Deeper circuits (p=4) produced better results than shallower (p=2) in these simulations.
## Quantum advantage claim
**Classification:** speculative

The paper argues 'potential tractability' on NISQ hardware but presents results only from an idealized, noise-free simulator on a small (8-asset) instance; no experiments on real quantum hardware or on problem sizes where classical methods become infeasible were provided. Therefore any claim toward quantum advantage is speculative pending noise/circuit-depth analysis and hardware validation.
## Limitations
- Results are obtained on an idealized simulator and ignore noise and coherence time limitations of real NISQ hardware (author-stated).
- Demonstration is limited to a small problem (eight-stock portfolio, 16 spins); scalability to larger portfolios is not shown (author-stated).
- Investment constraint in the soft-constraint formulation relies on a penalty scaling coefficient A set by a simple, experimentally chosen bound; choice of A may strongly affect feasibility and performance (author-stated).
- The QAOA cost function and algorithm were sensitive to data scaling (required converting daily returns to annualized returns); performance depends on cost-function scaling (author-stated).
- Hard-constraint formulation’s initial state induces a non-uniform (binomial) probability across parity bands, introducing potential solution bias (author-stated).
- Optimization was performed independently at each rebalancing time-step (no multi-period foresight or dynamic programming), so the multi-period trajectory is approximate (author-stated).
- Simplified trading-cost model (fixed cost per trade) and assumption of equal dollar value per lot; real trading cost structures and heterogeneous lot sizes are not modeled (author-stated / modeling limitation).
- Observed artifacts due to the classical optimizer (Nelder–Mead) — e.g., best performance at lower p possibly an optimizer artifact — indicating classical optimizer choice affects results (author-stated).
- [inferred] The hard-constraint mixer construction requires preparing entangled (Bell) states and parity rings across many qubits; implementing this on NISQ hardware may be challenging due to circuit depth and fidelity constraints.
- [inferred] Preprocessing and input of cost-function coefficients (even for quadratic Ising form) may become computationally expensive as problem size grows; parameter-count and classical precomputation scaling is a concern.
- [inferred] The two-spin encoding permits degenerate states (both long and short selected) that are handled via penalty/CTC encoding; this degeneracy may complicate the energy landscape and optimization.
## Open questions
- How will the proposed QAOA and Quantum Alternating Operator Ansatz formulations perform on real NISQ hardware under realistic noise and decoherence?
- What are the hardware resource requirements (gate counts, circuit depth, connectivity) for the hard-constraint mixer and the overall circuit as problem size grows?
- How can the initial-state bias introduced by the parity/mixed initial state be mitigated while keeping circuits shallow enough for NISQ devices?
- Can more principled or automated methods for selecting penalty scaling A be developed to improve feasibility and optimization robustness?
- Will the approaches scale to larger portfolios (N much greater than 8) while maintaining solution quality and reasonable runtime?
- How does the choice of classical optimizer (and hybrid optimization strategy) impact convergence and final solution quality for increasing p and N?
- How can true multi-period (dynamic) optimization / foresight be incorporated into the formulation instead of independent per-period optimization?
- How sensitive are results to more realistic, heterogeneous trading-cost models and unequal lot sizes, and how should those be encoded?
- How do these gate-model QAOA-based approaches compare empirically (quality, runtime, robustness) to quantum annealing or other quantum and classical heuristics on the same problem instances?
- Can the entangling parity-mixer and the needed Bell-state preparations be implemented efficiently and with sufficient fidelity on current-generation quantum devices?

**Future work:**
- Circuit depth analysis via hardware resource estimation (assess gate counts, depth, connectivity requirements).
- Impact of noise: simulated performance analysis including realistic noise models and decoherence.
- Validation on current-generation NISQ hardware (running the algorithms on actual devices).
- Investigate mitigation of initial-state bias from parity-based initial states in conjunction with circuit depth/coherence constraints.
- Further full-stack investigation to uncover classical pre-processing, optimizer choices, and other system-level parameters critical to scaling and practical performance.
## Key ideas
- #idea:quantum-advantage — QAOA with Quantum Alternating Operator Ansatz (parity/ hard-constraint mixers) recovered near-optimal discrete rebalancing portfolios (within ~5% adjusted returns) on an 8-asset example compared to brute-force optima.
- #idea:hybrid-approach — The variational QAOA loop uses a classical optimizer (Nelder–Mead) to tune circuit parameters, demonstrating a hybrid quantum-classical workflow.
- #idea:near-term-feasibility — The paper designs parity-ring mixers and a two-spin per-asset encoding tailored to constrained combinatorial portfolio problems, aiming at NISQ-style variational implementations.
- #idea:quantum-advantage — Hard-constraint QAOA (feasible-subspace preparation + parity mixers) achieves substantially higher feasibility probabilities and better cost distributions than standard soft-penalty QAOA in the tested instances.
- #idea:hybrid-approach — Practical engineering choices (annualizing returns to avoid vanishing cost amplitudes, penalty coefficient selection) are necessary to make QAOA optimization effective in practice.
- #idea:near-term-feasibility — Empirical exploration of circuit depth p (1..4) and repeated seeded runs (20 seeds) shows improvement with depth on idealized simulator, but only for small-scale (N=8, 16 qubit) problems.
## Contradictions
- contradiction:classical-vs-quantum — The paper reports a quantum approach finding near-optimal portfolios, but the same small N=8 instances are solvable by classical brute-force enumeration used as baseline, so no demonstrated advantage over classical methods at realistic scales.
- contradiction:scalability — Claims about the promise of constrained-QAOA are based on noise-free simulations at 16 qubits; the work does not demonstrate scalability to larger asset universes nor account for hardware noise, contradicting implications of near-term practical scalability.
## Notable quotes
<!-- Researcher-added — verbatim quotes with page references -->

## Researcher notes
<!-- Researcher-added — not LLM generated -->
