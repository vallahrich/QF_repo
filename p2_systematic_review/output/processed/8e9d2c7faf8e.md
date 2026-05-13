---
aliases:
- Classically-Boosted Quantum Optimization Algorithm
- Classically Boosted Quantum Optimization
authors:
- Guoming Wang
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
journal_or_venue: arXiv preprint (arXiv:2203.13936)
methodology_tags:
- quantum-walks
- hybrid-quantum-classical
- variational-nisq
paper_type: ''
quantum_advantage_claim: speculative
related_papers: []
relevance_phase1: high
relevance_phase3: high
source_type: preprint
source_type_confidence: high
step1_date: '2026-04-14T11:05:04.387796'
step1_model: gpt-5-mini
step2_date: '2026-04-14T11:05:04.387796'
step2_model: gpt-5-mini
step3_date: '2026-04-14T11:05:04.387796'
step3_model: gpt-5-mini
step4_date: '2026-04-14T11:05:04.387796'
step4_model: gpt-5-mini
step5_date: '2026-04-14T11:05:04.387796'
step5_model: gpt-5-mini
step6_date: '2026-04-14T11:05:04.387796'
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
- method/quantum-walks
- method/hybrid-quantum-classical
- method/variational-nisq
- idea/quantum-advantage
- idea/near-term-feasibility
- idea/hybrid-approach
title: Classically-Boosted Quantum Optimization Algorithm
topic_tags:
- portfolio-optimization
year: '2022'
zotero_key: ''
---

## Abstract summary
This paper introduces the Classically-Boosted Quantum Optimization Algorithm (CBQOA), a hybrid approach that uses a classical algorithm to produce a seed solution and then applies a continuous-time quantum walk (CTQW) to prepare a superposition over nearby feasible solutions, followed by amplitude-amplification-like layers to boost high-quality solutions. CBQOA is designed to handle many constrained and unconstrained combinatorial optimization problems without penalty terms, confines evolution to the feasible subspace, does not require indexing of feasible solutions, and is demonstrated empirically on Max 3SAT and Max Bisection where it outperforms prior approaches.
## Methodology
The paper introduces the Classically-Boosted Quantum Optimization Algorithm (CBQOA), a hybrid quantum-classical variational procedure for combinatorial optimization. The methodology is: (1) run an efficient classical approximation algorithm to produce a feasible seed solution z; (2) construct a weighted undirected graph over the full bitstring space via a set of poly(n) efficiently-computable local, involutory permutations τ_i; (3) form an adjacency matrix A = sum_i w_i H_i where H_i encodes τ_i and weights w_i = sigmoid(θ [f(z)-f(τ_i(z))]) depend on a tunable bias parameter θ; (4) prepare an initial feasible-state superposition |ψ> = e^{i A t} |z> by implementing a continuous-time quantum walk (CTQW) on this graph (using exact circuits where possible or Trotterization otherwise); (5) run a p-layer variational circuit that alternately applies phase separators e^{-i γ_j H_f} (H_f encodes the cost function) and mixing operators e^{-i β_j |ψ><ψ|}, noting the latter is implemented as e^{i A t} e^{-i β |z><z|} e^{-i A t}; (6) tune parameters (t, θ) for the CTQW and then the variational parameters (⃗β,⃗γ) by minimizing Conditional Value at Risk (CVaR) of the objective under the output distribution (α chosen, experiments used α=0.5); (7) accelerate classical simulation by discretizing objective values into M buckets and exploiting a reduced M-dimensional representation to compute resulting probability distributions efficiently. The method was applied and evaluated in classical simulations on synthetic hard instances of Max 3SAT and Max Bisection comparing CBQOA to classical seeds and GM-QAOA baselines.

**Algorithms used:** CBQOA (Classically-Boosted Quantum Optimization Algorithm), Continuous-Time Quantum Walk (CTQW), Trotterization (for Hamiltonian simulation), Quantum Approximate Optimization Algorithm (QAOA) variants (GM-QAOA referenced), Karloff-Zwick SDP + random hyperplane rounding (seed for Max 3SAT), Feige-Langberg SDP + RPR2 rounding (seed for Max Bisection), Semidefinite Programming (SDP) interior-point solver (referenced), ADAM optimizer (for CVaR minimization / parameter tuning)
**Frameworks:** Orquestra (simulation / experiment platform)

**Experimental setup:** All experiments were classical simulations run in the Orquestra platform. Seeds were produced by solving SDP relaxations (Karloff–Zwick for Max3SAT; Feige–Langberg for Max Bisection) and applying randomized rounding. CTQWs were implemented exactly when A decomposed into single-qubit rotations (Max3SAT) or approximately via first-order Trotter steps (Max Bisection) with N=3. Parameter tuning (t, θ, ⃗β, ⃗γ) performed by iterative CVaR minimization using ADAM. Simulation acceleration used a discretization of objective values into M=1000 buckets and an M-dimensional propagation technique.
## Experiment details
### Input
{'Max3SAT': {'source': 'synthetic random instances', 'n': 16, 'clauses': 200, 'clause_weights': 'uniform in [0,1]', 'instance_selection': "select instances for which KZ rounding over 10,000 trials yields POGS0.7 < 0.05 (deemed 'hard')", 'count': 100}, 'MaxBisection': {'source': 'synthetic random instances (Erdős–Rényi)', 'graph_model': 'G(n=12, p=0.5)', 'edge_weights': 'uniform in [-1,1]', 'instance_selection': "select instances for which Feige–Langberg rounding over 10,000 trials yields POGS0.99 < 0.05 (deemed 'hard')", 'count': 100}, 'preprocessing': 'SDP solves (interior-point), randomized-rounding seed generation; for Max3SAT encoding uses auxiliary variables to express negations; for MaxBisection seeds determine partition T used to construct CTQW permutations.'}

### Process
{'pipeline_steps': ['Generate synthetic instance (Max3SAT or Max Bisection) and assign clause/edge weights.', 'Solve SDP relaxation (Karloff–Zwick or Feige–Langberg) and produce classical seed z via randomized rounding (10,000 trials used for instance selection).', 'Construct permutation set T from problem structure (e.g., single-bit flips for unconstrained problems; swap operations for permutation-invariant or bisection problems).', 'Form adjacency A = sum_i w_i H_i with weights w_i = 1/(1+exp(-θ(f(z)-f(τ_i(z))))).', 'Implement CTQW |ψ> = e^{i A t} |z> (exact where A decomposes into commuting local terms; otherwise approximate via repeated product of localized exponentials with N Trotter steps; experiments used N=3 for Max Bisection).', 'Tune CTQW parameters (t, θ) by minimizing CVaR_α of f over the distribution produced by measurement from |ψ>, with α=0.5 in experiments.', 'Construct variational ansatz: p-layer alternating sequence of phase separators e^{-i γ_j H_f} and mixers e^{-i β_j |ψ><ψ|} where e^{-i β_j |ψ><ψ|} is implemented via conjugation by CTQW operator.', 'Tune variational parameters ⃗β,⃗γ with ADAM minimizing CVaR_α of measured cost; p values tested up to p=3.', 'Evaluate performance metric POGS_x (probability of producing solution with approximation ratio ≥ x) and compare to baselines (seed algorithm, GM-QAOA).'], 'key_iterations': {'seed_rounds_for_selection': 10000, 'CVaR_alpha': 0.5, 'M_for_simulation_acceleration': 1000, 'Trotter_steps_for_MaxBisection_N': 3, 'variational_layers_tested_p': [0, 1, 2, 3]}}

### Output
{'format': 'histograms and empirical distributions over instances', 'metrics_reported': ['POGS_x (probability of good solutions: probability algorithm produces solution with approximation ratio ≥ x)', 'approximation ratio β(z) defined as (E[f(x)] - f(z)) / (E[f(x)] - f(z*))', 'comparison of POGS across algorithms (seed, GM-QAOA, CBQOA at different depths)'], 'baselines': ['Karloff–Zwick classical algorithm (Max3SAT seed)', 'Feige–Langberg classical algorithm (Max Bisection seed)', 'GM-QAOA'], 'observed_outputs': 'Histograms of POGS for thresholds (e.g., 0.7, 0.8 for Max3SAT; 0.99 for Max Bisection) showing CBQOA (p up to 3) improved probabilities versus seeds and GM-QAOA.'}

### Parameters
- Max3SAT: {'n_qubits': 16, 'clauses': 200, 'CTQW_implementation': 'A = sum_i w_i X_i (single-qubit rotations), exact', 'Trotter_steps_N': 1, 'variational_layers_p_tested': [0, 1, 2, 3], 'CVaR_alpha': 0.5, 'M_discretization': 1000, 'optimizer': 'ADAM'}
- MaxBisection: {'n_qubits': 12, 'graph_model': 'Erdos-Renyi G(12,0.5)', 'CTQW_implementation': 'A = (1/2) sum_{a in T} sum_{b in T^c} w_{a,b} (X_a X_b + Y_a Y_b) (XY gates)', 'Trotter_steps_N': 3, 'parallelization': 'reorder terms into R_k slices to implement disjoint XY gates in parallel per slice', 'variational_layers_p_tested': [0, 1, 2, 3], 'CVaR_alpha': 0.5, 'M_discretization': 1000, 'optimizer': 'ADAM'}
- common: {'weight_sigmoid_parameter': 'θ (tuned)', 'CTQW_time_t': 't (tuned)', 'phase_separator_parameters': '⃗γ (tuned)', 'mixer_parameters': '⃗β (tuned)', 'seed_rounds_for_selection': 10000}

### Hardware
{'simulator': 'Orquestra', 'qpu_model': None, 'cloud_provider': None, 'notes': 'All experiments reported are classical simulations executed on Orquestra; no physical QPU was used.'}

### Reproducibility
The paper describes algorithms, parameter choices, instance generation procedures, and many implementation details (SDP relaxations used for seeds, seed rounding counts, discretization parameter M, Trotter step count N, CVaR α, optimizer ADAM). Source code and exact SDP solver configurations are not provided in the preprint. Reproduction is feasible given the methodological description but would require (1) an SDP solver implementing the referenced interior-point method, (2) implementation of the CTQW construction and Trotterization, and (3) access to the Orquestra platform or reimplementation on an alternative simulator. Random seeds and exact instance lists are not supplied, so exact numeric replication would require rerunning instance-selection procedure as described.
## Findings
- [speculative] The paper introduces CBQOA (Classically-Boosted Quantum Optimization Algorithm), a hybrid approach that uses a classical algorithm to produce a seed solution and a continuous-time quantum walk (CTQW) to prepare a problem-dependent initial quantum state which is then processed by an alternating-phase ansatz.
- [speculative] CBQOA is designed so that the quantum evolution remains confined to the feasible subspace for constrained problems (i.e., it only produces feasible solutions without modifying the cost function).
- [speculative] CBQOA does not require efficient indexing of feasible solutions (unlike some prior CTQW-based approaches) and can handle many constrained problems (Max Bisection, Max/Minimum Vertex Cover, Maximum Independent Set, Portfolio Optimization, TSP) under a stated structural assumption (Assumption 3.1).
- [speculative] Under Assumption 3.1 (existence of poly(n) efficiently-computable local involutive permutations partitioning the feasible set), one can construct a weighted graph over bitstrings so that CTQWs on it are efficiently implementable (via Trotterization or small-local unitaries).
- [speculative] Edge weights in the CTQW graph can be chosen adaptively as sigmoid functions of local improvements from the seed (parameter θ), biasing the walk toward promising local moves.
- [supported] The authors implemented classical simulations (Orquestra platform) showing CBQOA (with up to 3 alternating layers) improved over the classical seed algorithms and over GM-QAOA on small, hard benchmark instances of Max 3SAT and Max Bisection.
- [supported] In experiments the classical seed generators were: Karloff–Zwick (KZ) for Max 3SAT and Feige–Langberg (FL) for Max Bisection; CBQOA expanded the seed by preparing a CTQW-based superposition and then applied an amplitude-amplification-like ansatz tuned by CVaR minimization.
- [supported] Experimental setup details: 100 'hard' Max 3SAT instances (n=16 variables, 200 weighted clauses) and 100 'hard' Max Bisection instances (Erdős–Rényi G(12,0.5), edge weights uniform in [-1,1]) were used to compare algorithms via empirical sampling metrics.
- [supported] The parameter-tuning approach used Conditional Value at Risk (CVaR) minimization (α=0.5 in experiments) and the ADAM optimizer to choose CTQW and ansatz parameters; a simulation acceleration technique based on binning objective values into M bins (M=1000) was used.
- [speculative] CBQOA can be implemented with polynomial-depth quantum circuits under the provided constructions (local permutations, local CTQW terms, Trotterization with polynomial N) and mixing operators e^{-iβ|ψ⟩⟨ψ|} implemented via conjugation with the CTQW.
- [speculative] The paper claims CBQOA combines desirable properties (adaptive ansatz construction using classical preprocessing; direct handling of constrained problems without penalties; confinement to feasible subspace; no need for indexing) simultaneously — a contrast to prior QAOA variants.
- [speculative] The authors propose that finding seeds that are near many high-quality solutions (in Hamming/graph distance) is more valuable to CBQOA performance than absolute seed objective, and that improved classical seeding tailored to this goal could further boost CBQOA.

**Results summary:** The paper presents CBQOA, a hybrid quantum-classical optimization framework that uses a classical approximation algorithm to produce a seed solution, prepares a seed-centered superposition via a continuous-time quantum walk on a problem-dependent graph, and then amplifies high-quality feasible solutions using an alternating-phase ansatz with CVaR-based parameter tuning. Under a structural assumption (existence of local involutive permutations partitioning the feasible set), the CTQW construction and its Trotterized implementation are claimed to be efficient. Classical simulations on small benchmark sets (100 hard Max 3SAT instances with n=16, 200 clauses; 100 hard Max Bisection instances with n=12) show CBQOA (up to 3 layers) improved the probability of finding high-quality solutions relative to the classical seeds (KZ, FL) and to GM-QAOA baselines. The paper emphasizes CBQOA's ability to directly handle constrained problems without penalty terms and to confine evolution to feasible subspaces.

**Performance claims:**
- [supported] Benchmarking used 100 'hard' Max 3SAT instances (n=16 variables, 200 weighted clauses) selected so POGS0.7(KZ) < 0.05 when rounding the SDP solution 10,000 times.
- [supported] Benchmarking used 100 'hard' Max Bisection instances (Erdős–Rényi G(12,0.5), edge weights in [-1,1]) selected so POGS0.99(FL) < 0.05 when running the FL rounding 10,000 times.
- [supported] CBQOA variants (CBQOA_p with p up to 3) empirically outperformed the corresponding GM-QAOA_p and the classical seed generators on those small-instance benchmarks, as measured by probability of 'good' solutions above thresholds (e.g., 0.7/0.8 for Max 3SAT and 0.99 for Max Bisection).
- [supported] Simulation parameters included CVaR minimization with α=0.5, ADAM optimizer for parameter tuning, CTQW Trotterization parameter N=3 for Max Bisection simulations, and binning-based classical simulator acceleration with M=1000.
- [speculative] The paper asserts polynomial implementability of CTQW and mixing unitaries (and overall polynomial circuit depth) under Assumption 3.1 and with O(log n)-local permutations and polynomial Trotter steps.
## Quantum advantage claim
**Classification:** speculative

The paper demonstrates improved empirical performance of CBQOA over specific classical seeds and GM-QAOA on small, classically simulated benchmark instances (supporting potential practical benefits), but it does not prove a general or asymptotic quantum advantage nor demonstrate results on quantum hardware at scale. The claims of efficiency and broad applicability are theoretical contingent on structural assumptions (Assumption 3.1), so any claim of quantum advantage remains speculative.
## Limitations
- Assumption 3.1 is required: existence of a poly(n)-sized set of efficiently-computable, low-locality, order-2 permutations and a partition of F preserved by them. This assumption does not hold for some constrained problems (explicitly noted: Knapsack).
- The CTQW implementation relies on Trotterization (or other Hamiltonian simulation). The Trotter approximation U' explores only a local neighborhood unless the product Nm is large, so exact CTQW behavior may be costly to realize.
- To fully explore all feasible components one must run the CTQW from a seed in each component; complexity depends on k (number of components) which is assumed poly(n) but may be large in practice.
- Edge-weight assignment wi is heuristic (sigmoid of improvement on the seed) and the authors explicitly note this choice may not be optimal.
- The method assumes e^{-i Hf γ} can be implemented efficiently (f decomposes into poly(n) commuting O(log n)-local terms). Problems with high-degree or nonlocal f may violate this.
- Parameter tuning is expensive: many continuous parameters (t, θ, β⃗ , γ⃗ ) must be optimized using iterative classical optimizers; each evaluation requires running the quantum circuit (or classical simulation).
- Classical pre-processing (e.g., solving SDPs for seeds such as Karloff–Zwick or Feige–Langberg) can be computationally heavy (SDP solve times scale as high-degree polynomials) and may dominate runtime.
- Empirical evaluation is limited to small instance sizes (Max 3SAT with n=16, Max Bisection with n=12) using classical simulation; scalability and performance on larger, realistic financial-size instances are untested.
- The CBQOA performance depends on the quality and nature of the classical seed; if the seed is not close (in the graph metric) to many high-quality solutions, the CTQW initial state may have poor overlap with good solutions.
- The Appendix approximation/simulation method requires discretization parameter M scaling as poly(p, b-a, 1/α, 1/ε); in practice this may become large and computationally costly.
- [inferred] The algorithmic depth and gate counts (CTQW layers, Trotter repetitions, XY/ZZ gates, and ancilla usage for e^{-iβ|z⟩⟨z|}) may be large, posing implementation challenges on noisy, near-term quantum hardware.
- [inferred] Sensitivity to noise and decoherence is not analyzed; the algorithm's practical performance on noisy devices is uncertain.
- [inferred] Choosing and tuning the hyperparameter α for CVaR objective is nontrivial and may impact convergence and empirical outcomes.
- [inferred] The local-neighborhood search nature (small t) may fail on landscapes where high-quality solutions are not clustered around good classical seeds.
- [inferred] The need to construct T and the partition (F1..Fk) for a new problem may require problem-specific engineering and is not automated.
## Open questions
- Can one design better classical algorithms that find seeds z which are close (in the CBQOA graph metric) to many high-quality solutions, improving the quantum initialization?
- Is there a principled or better way to assign edge weights wi (instead of the sigmoid of f(z)-f(τi(z))) to improve CTQW exploration and overlap with high-quality solutions?
- Can the parameter tuning process (t, θ, β⃗ , γ⃗ ) be made more efficient by exploiting the CBQOA circuit structure or by developing specialized optimizers, reducing the number of costly quantum evaluations?
- Is it possible to design useful parameter schedules for CBQOA (analogous to schedules in QAOA/adiabatic algorithms) that guarantee or empirically yield strong performance with fewer layers?
- How does CBQOA scale with problem size and depth p on larger instances (particularly those relevant to financial services), and does the empirical advantage observed on small instances persist or grow?
- What is the effect of Trotterization error, finite N, and approximation U' vs the ideal U on final optimization performance in practice, and how to balance N vs circuit depth/noise?
- How robust is CBQOA to realistic hardware noise (gate errors, readout noise, decoherence) and what are its noise thresholds for practical advantage?
- How sensitive is CBQOA to the choice of the CVaR confidence parameter α, and can adaptive or automated selection of α improve outcomes?
- For problems where Assumption 3.1 fails, can CBQOA be adapted (without penalty transforms) or does one necessarily revert to penalty-based unconstrained encodings?
- Can one characterize classes of problems or instances where classical pre-processing leaves little room for quantum improvement (i.e., where the seed is already near-optimal in the graph metric)?
- How to automate construction of the permutation set T and partition (F1..Fk) for new problem domains, minimizing human engineering?
- What are the resource requirements (qubit counts, ancillas, gate depth) for CBQOA on problem sizes of practical interest, and are these achievable on near-term/future hardware?
- Can alternative Hamiltonian simulation techniques (beyond simple Trotterization) reduce circuit depth and improve fidelity of the CTQW for CBQOA?
- How does CBQOA compare empirically to other warm-start or hybrid approaches across a broad benchmark suite (beyond the two tested problems)?
- Could multiple seeds or ensemble seeding strategies yield better coverage of F and improved final solutions, and how to choose such seeds efficiently?

**Future work:**
- Develop a better classical algorithm to produce seeds z that are close to many high-quality solutions (improving CBQOA initialization).
- Design more efficient parameter tuning methods for CBQOA that exploit circuit structure to reduce the number of optimizer iterations and expensive quantum evaluations.
- Investigate whether one can design classes of parameter schedules for CBQOA that lead to excellent performance (analogous to schedule design in QAOA/adiabatic algorithms).
- Find improved methods to assign edge weights wi (the authors explicitly leave this as future work).
- Test CBQOA on larger problems and additional problem classes (including larger Max Bisection graphs) to verify conjectures about scaling and performance gaps.
- Further explore hybrid strategies combining classical and quantum components in varied ways to enhance combinatorial optimization performance.
## Key ideas
- #idea:hybrid-approach — CBQOA seeds the quantum routine with a classical approximation (SDP + randomized rounding) and uses a CTQW-based mixing operator to confine evolution to feasible subspace, avoiding penalty terms and indexing of feasible solutions.
- #idea:quantum-advantage — Classical simulations on synthetic Max3SAT (n=16) and Max Bisection (n=12) show CBQOA (p up to 3) yields higher POGS (probability of good solutions) than the classical seeds and GM-QAOA baselines.
- #idea:near-term-feasibility — The approach uses low-depth variational layers (p ≤ 3), Trotterized CTQW when needed, and CVaR-based parameter tuning, presented as a NISQ-friendly hybrid algorithm.
- #limitation:simulation-only — All reported experiments are classical simulations (Orquestra); no runs on real quantum hardware were reported.
- #limitation:no-empirical-validation — The empirical claims of outperforming prior approaches are supported only by simulator results on small synthetic instances (n=12–16) rather than hardware experiments or large-scale benchmarks.
- #limitation:qubit-count — Demonstrations are limited to small qubit counts (16 and 12 qubits), leaving open questions about scaling to problem sizes relevant for financial applications.
- #idea:hybrid-approach — The paper introduces an M-dimensional discretization/simulation acceleration to allow efficient classical simulation of the algorithm's output distribution for parameter tuning and evaluation.
## Contradictions
- The paper asserts an efficient (poly(n) depth) implementable CTQW construction and broad applicability under Assumption 3.1, yet provides only small-scale classical simulations (n<=16) and relies on a strong structural assumption that may not hold for many constrained problems (e.g., knapsack). Thus the claimed scalability/efficiency is unsubstantiated by the presented empirical evidence.
## Notable quotes
<!-- Researcher-added — verbatim quotes with page references -->

## Researcher notes
<!-- Researcher-added — not LLM generated -->
