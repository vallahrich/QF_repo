---
aliases:
- Quantum Architecture Search for Quantum Monte Carlo Integration via Conditional
  Parameterized Circuits with Application to Finance
- Quantum Architecture Search Quantum
authors:
- Mark-Oliver Wolf
- Tom Ewen
- Ivica Turkalj
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
journal_or_venue: arXiv preprint arXiv:2304.08793
methodology_tags:
- variational-nisq
- amplitude-estimation
- quantum-ml
- hybrid-quantum-classical
paper_type: ''
quantum_advantage_claim: theoretical
related_papers: []
relevance_phase1: high
relevance_phase3: high
source_type: preprint
source_type_confidence: high
step1_date: '2026-04-14T11:29:48.948216'
step1_model: gpt-5-mini
step2_date: '2026-04-14T11:29:48.948216'
step2_model: gpt-5-mini
step3_date: '2026-04-14T11:29:48.948216'
step3_model: gpt-5-mini
step4_date: '2026-04-14T11:29:48.948216'
step4_model: gpt-5-mini
step5_date: '2026-04-14T11:29:48.948216'
step5_model: gpt-5-mini
step6_date: '2026-04-14T11:29:48.948216'
step6_model: gpt-5-mini
steps_completed:
- 1
- 2
- 3
- 4
- 5
- 6
tags:
- topic/derivative-pricing
- topic/simulation-monte-carlo
- method/variational-nisq
- method/amplitude-estimation
- method/quantum-ml
- method/hybrid-quantum-classical
- idea/quantum-advantage
- idea/near-term-feasibility
- idea/hybrid-approach
title: Quantum Architecture Search for Quantum Monte Carlo Integration via Conditional
  Parameterized Circuits with Application to Finance
topic_tags:
- derivative-pricing
- simulation-monte-carlo
year: '2023'
zotero_key: ''
---

## Abstract summary
The paper introduces a method to reduce quantum resource costs for quantum Monte Carlo integration by pretraining parameterized quantum circuits (PQCs) classically and converting them into conditional PQCs (CPQCs) suitable for amplitude estimation. A genetic optimization approach (variable ansatzes) is used to automatically design shallow, hardware-aware PQCs, and the method is applied to pricing European vanilla and basket options, demonstrating substantial reductions in gate counts and depth at the expense of classical pretraining.
## Methodology
The authors develop a method to implement state-dependent functions for Quantum Monte Carlo Integration by (1) training parameterized quantum circuits (PQCs) to approximate payoff functions (variational quantum algorithms), and (2) transforming these PQCs into conditional parameterized quantum circuits (CPQCs) by replacing data-encoding rotation gates with controlled versions so the PQC can be evaluated on superpositions of computational basis states. To find efficient shallow PQCs they use an automated architecture-search style procedure that combines a variable-ansatz approach with genetic-style optimization: iterative mutation (adding randomly sampled encoding or parameterized blocks), local parameter optimization (gradient-based using Pennylane automatic differentiation), removal of noncontributing gates under a small tolerated cost increase, and population-based selection across generations. Encoding blocks are restricted to single-qubit rotations (RX, RY, RZ) to enable efficient construction of controlled encodings that scale linearly in the number of control qubits. The CPQC is then compared to a quantum-arithmetic baseline (qiskit finance implementation) using metrics such as CNOT counts and circuit depth after decomposition. The approach is applied to synthetic option pricing tasks (European vanilla calls and basket options with fixed and variable weights) and empirical results include trained PQC architectures, their CPQC counterparts, function-approximation plots and resource comparisons. The authors report training hyperparameters (population size, generations, iterations), acceptance and gate-removal criteria, and runtime on a classical machine.

**Algorithms used:** Variational Quantum Algorithm (VQA), Variable Ansatz (VAns) style structure search, Genetic-style optimization / Quantum Architecture Search, Conditional Parameterized Quantum Circuits (CPQC) construction, Quantum Amplitude Estimation (AE) (as target application / context)
**Frameworks:** PennyLane, Qiskit (used for baseline / comparison)

**Experimental setup:** All quantum circuit training and evaluation were performed on noiseless classical simulators accessed via Pennylane (gradients computed via automatic differentiation). A classical pretraining workflow was executed on a dual Intel Xeon Gold 6240R system (48 cores). No physical QPU was used; baseline quantum-arithmetic implementations referenced IBM Qiskit finance module for gate counts.

**Dataset:** Synthetic discretizations of underlying asset price(s) used to compute option payoffs. Tasks: European vanilla call (strike 100, asset price range shown in figures ~70–130) and basket options with two underlyings (fixed and variable weight). Data were generated as regular discretizations with 2^n grid points (n equals number of control qubits); exact training set sizes per experiment are not consistently specified in the text.
## Experiment details
### Input
{'source': 'synthetic / simulated', 'type': 'discretized asset prices (uniform grid over chosen range) mapped to payoff labels', 'sizes': 'variable; examples: n=3 (8 points) in illustrative example; experiments conducted up to n=14 control qubits for resource comparisons. For two-asset basket, each underlying was assigned nk = n/2 qubits.', 'preprocessing': 'feature entries mapped to bit-strings via a mapping b(·) (basis encoding). Encodings chosen to be rotation angles (RX/RY/RZ). No other preprocessing described.'}

### Process
{'overview': '1) Define training data X (discretized inputs) and labels Y (payoff values). 2) Initialize a PQC U0(x,θ) in the layered form U(x,θ)=∏_l S_l(x) W_l(θ_l) where S_l are encoding blocks (rotations) and W_l are parameterized blocks. 3) Run genetic/variable-ansatz structure search (Algorithms 1 and 2): within each candidate, iteratively sample a block to add (encoding or param block), optimize parameters θ with a gradient-based optimizer (Pennylane automatic differentiation), compute new cost, accept or reject the structural change according to an acceptance function, and apply a gate-reduction step removing gates that increase cost by less than a threshold. 4) Maintain a population of candidate circuits across generations and select next-generation members with probability proportional to 1/cost^2. 5) After structure learning, construct CPQC by replacing encoding rotations with controlled rotations acting on the control register; this construction is efficient (O(n)) when encodings are rotations. 6) Compare resulting CPQC resource usage (CNOT count and depth) against a quantum-arithmetic baseline (qiskit finance) after gate decomposition.', 'key_steps_and_parameters': {'structure_search_iterations_per_generation': '20 (for the presented call-option experiment)', 'generations': '20 (call-option example)', 'population_size': '48 (call-option example)', 'parameter_optimizer': 'Pennylane Root-mean-squared-propagation (RMSProp) with autodiff gradients', 'acceptance_rule': 'If cost decreased accept; else accept with probability exp(-5*(c_new - c_old)/c_old)', 'gate_removal_threshold': 'Allow removal if increase in cost ≤ 1%', 'encoding_blocks': 'Single-qubit rotations (RX, RY, RZ)', 'selection_weights': 'w_j = (1 / c_j^2) / sum_k (1 / c_k^2)', 'CPQC_construction': 'Replace S_l(x) rotations by control-circuit Λ_l composed of controlled-Rα gates; linear scaling O(n)'}}

### Output
{'formats': ['Trained PQC circuit diagrams (gate sequences and parameters)', 'Constructed CPQC circuit diagrams', 'Function-approximation plots: PQC/CPQC prediction vs true payoff surface', 'Resource comparisons: CNOT gate counts and circuit depth after decomposition (to CNOT and U(θ,φ,λ))', 'Runtime for pretraining on classical hardware'], 'metrics_and_baselines': {'primary_metrics': ['CNOT count (post-decomposition)', 'Circuit depth (post-decomposition)', 'Visual and MSE-based function-approximation quality (cost used during training is MSE)'], 'baseline': 'IBM qiskit finance quantum-arithmetic implementation (bitwise arithmetic approach) used for comparison of gate counts and depth'}, 'representative_results': 'Examples reported include a CPQC CNOT count of 92 and depth 151 for n=14 (two-asset basket scenario). Training runtime reported ~5.5 hours on described CPU machine for the call-option experiment.'}

### Parameters
- control_qubits_range: variable up to at least n=14 tested (examples shown for n=3 and n=14)
- target_qubits: 1 qubit target used in examples (m=1) unless otherwise noted
- population_size: 48
- generations: 20
- structure_iterations_per_generation: 20
- optimizer: RMSProp via Pennylane autodiff
- gate_removal_threshold_percent: 1
- acceptance_probability_factor: -5
- simulator_shots: not specified (analytic/noiseless expectations via autodiff implied)
- gradient_method: automatic differentiation (Pennylane)
- decomposition_basis_for_counts: CNOT and U(θ,φ,λ)

### Hardware
{'classical_training_machine': 'Dual Intel Xeon Gold 6240R system, 48 cores', 'quantum_runtime': 'No QPU used; noiseless classical simulators via Pennylane (backend not explicitly named)', 'baseline_framework': 'Qiskit (IBM qiskit finance module used for baseline comparisons)'}

### Reproducibility
N/A
## Findings
- [speculative] Quantum Amplitude Estimation (AE) offers a theoretical quadratic speed-up over classical Monte Carlo for estimating expectations (cited background).
- [speculative] Proposition 3 (paper): equality of expectations when using a conditional PQC (CPQC) follows from equality of individual encodings; this gives a sufficient condition to replace data-dependent encoding blocks by controlled operations.
- [speculative] For PQCs whose encodings are single-qubit rotations, one can construct CPQCs whose cost (number of elementary gates) grows only linearly in the number of control qubits n (Example 7), i.e., O(n) scaling.
- [supported] The authors implemented genetic/variable-ansatz style structure learning (Algorithms 1 & 2) to automatically find PQC architectures that approximate option payoff functions.
- [supported] In noiseless simulations the pre-trained CPQCs required substantially fewer CNOT gates and smaller circuit depth than a reference bitwise quantum-arithmetic implementation (IBM/qiskit approach) for the tested option pricing tasks (figures 5 and 6).
- [supported] Concrete simulated resource example reported: for a basket option with n = 14 control qubits the CPQC decomposition had CNOT count = 92 and depth = 151 (reported in the text/caption).
- [supported] The classical pretraining used in the experiments required approximately 5.5 hours on a dual Intel Xeon Gold 6240R system (48 cores).
- [speculative] The CPQC approach can 'evade' typical data-loading inefficiencies in quantum machine learning by encoding specific function values as efficiently controlled operators rather than reloading data each time.
- [supported] The learned PQC approximations show smoothing at payoff non-differentiable points (attributed to the PQC/Fourier representation and data re-uploading), an observed effect in simulations.
- [supported] For the variable-weight basket option experiments the trained PQC empirically required encoding the variable weight only once at the circuit start to generalize across weights (observed in simulations).
- [speculative] The tradeoff of an expensive classical pretraining for reduced quantum resources may be advantageous on NISQ devices because small approximation errors could be dominated by gate noise; this is suggested but not experimentally validated on noisy hardware.

**Results summary:** The paper introduces conditional parameterized quantum circuits (CPQCs) and a genetic/variable-ansatz procedure to pretrain PQCs that implement payoff functions for quantum Monte Carlo integration (AE). Theoretically, the authors prove a sufficient condition (Proposition 3) under which encoding blocks can be replaced by control circuits, and show for rotational encodings that CPQC overhead scales linearly in control-qubit count. Empirically (noiseless simulator), they used a genetic search to obtain PQCs for European vanilla and basket options; converting these to CPQCs yielded substantially lower CNOT counts and depths than a reference bitwise quantum-arithmetic implementation, at the expense of a costly classical pretraining (~5.5 hours on a 48-core CPU). The work positions CPQCs as a way to reduce quantum resource requirements for AE subroutines, subject to pretraining and encoding choices.

**Performance claims:**
- Pretraining time: ~5.5 hours on dual Intel Xeon Gold 6240R (48 cores) for the reported experiments.
- Genetic algorithm configuration used in reported experiments: 20 generations, population size 48, 20 structure-optimization iterations per generation (reported in text).
- Reported simulated resource example: for n = 14 control qubits on a basket option, CPQC decomposition had CNOT count = 92 and circuit depth = 151 (figure caption).
- The CPQC construction for rotational encodings uses O(n) elementary gates (theoretical construction, Example 7) compared to the reference quantum-arithmetic weighted-sum operator which scales as O(n log n) gates.
## Quantum advantage claim
**Classification:** theoretical

The paper relies on the known theoretical quadratic advantage of Amplitude Estimation over classical Monte Carlo; it does not experimentally demonstrate end-to-end quantum advantage on hardware. Instead, it presents a theoretical CPQC construction and noiseless-simulator resource comparisons showing reduced circuit depth/CNOT counts versus bitwise quantum-arithmetic methods, indicating a path that could make AE-based advantage more practical but without hardware demonstrations.
## Limitations
- Author-stated: The approach requires a computationally expensive classical pre-training phase (costly pretraining) to produce the reusable CPQCs.
- Author-stated: PQC approximations behave like truncated Fourier series, causing smoothing at non-differentiable points of payoffs (e.g., kink at strike) and limiting fidelity for non-smooth functions.
- Author-stated: The current CPQC construction and proofs are developed for encodings that use simple rotational gates; generalizing to other encoding types is not yet established and may introduce encoding errors.
- Author-stated: Gradients were computed via automatic differentiation on noiseless simulators — the experiments do not account for realistic device noise and were not validated on noisy hardware.
- Author-stated: There is an open concern about justifying approximation error introduced by CPQC substitutions versus the gate-count reduction—i.e., need to study when added approximation error is acceptable relative to hardware noise.
- Author-stated: The paper does not provide a full resource estimation for end-to-end quantum advantage (including AE), only gate counts/depth of the F implementation; broader resource thresholds remain unquantified.
- [inferred] The genetic architecture search (training) can be time- and resource-intensive (e.g., reported ~5.5 hours on a 48-core machine), which may limit scalability or practical retraining frequency.
- [inferred] The experimental evaluation focuses on European vanilla and small-dimension basket options; applicability to higher-dimensional baskets, more complex payoffs, or path-dependent derivatives is untested.
- [inferred] The CPQC method relies on having or assuming an efficient distribution-loading operator P; in practice preparing arbitrary distributions may still be a bottleneck.
- [inferred] The approach assumes the PQC can be turned into an efficient controlled variant; for general encoding structures (beyond rotations) constructing efficient control circuits may be hard or require many gates.
- [inferred] Comparisons focus on gate count and depth in a specific gate decomposition (CNOT and U(θ,φ,λ)); hardware-dependent gate sets and connectivity could change practical advantages.
- [inferred] The invertibility or efficient implementability of the inverse operator F^{-1} — relevant for some Amplitude Estimation variants — is not guaranteed by the presented CPQC constructions.
## Open questions
- How to generalize the conditional PQC construction to encodings other than simple rotational gates, and what approximation errors are introduced in such generalizations?
- At what level of gate-count reduction does the introduced approximation error become acceptable given realistic hardware noise — i.e., how to trade off approximation error vs. noise-induced error?
- Can PQC-based implementations lead to algorithmic shortcuts or further circuit optimizations in full quantum Monte Carlo integration / Amplitude Estimation pipelines?
- Can the CPQC approach ease the implementation of AE variants that have additional constraints on the function operator (e.g., those requiring efficient inverses)?
- How robust are the learned PQCs and resulting CPQCs to realistic noise models and hardware imperfections (including finite-sampling and gate errors)?
- What are the full resource requirements (qubits, total gates, circuit depth, classical precompute) for achieving concrete quantum advantage in derivative pricing when using CPQCs within AE?
- How to adapt and optimize the genetic/QAS procedure to target specific hardware (native gates, connectivity) and noisy conditions effectively?
- Is the CPQC method scalable to high-dimensional underlyings (many assets), path-dependent payoffs, or options with complex features, while maintaining practical gate/depth advantages?
- Can the CPQC framework be extended so that F^{-1} (the inverse of the function unitary) is also efficiently implementable, aiding AE implementations that need reversibility?
- What are the limits of function expressivity for hardware-efficient PQCs trained with genetic methods when approximating non-smooth or highly oscillatory payoff functions?

**Future work:**
- Further improvement of the genetic optimization of the PQC (structure learning and QAS enhancements).
- Taking hardware into account during circuit search: using native gates, entangling only physically connected qubits, and optimizing for hardware-specific constraints.
- Modifying the algorithm and cost function to weight approximation error against hardware noise and to optimize for robustness in the presence of noise.
- Adapting the algorithm to ensure the inverse of the function operator F is also efficient, benefiting Amplitude Estimation.
- Researching whether application of PQCs translates to shortcuts or other optimizations for quantum Monte Carlo integration algorithms (e.g., circuit-level optimizations like spin-echo).
- Investigating whether the CPQC approach can make existing AE techniques with additional conditions easier to implement.
- Carrying out a sophisticated resource estimation for quantum advantage that includes the CPQC approach (end-to-end costs and thresholds).
- Generalizing the conditional variant of PQCs for non-rotational encodings and developing more sophisticated control circuits Λ (including quantifying introduced encoding errors).
- Studying at what level of gate-count reduction the additional approximation error is justified compared to noise introduced by quantum gates.
- Investigating extension to pricing more complex instruments (e.g., index options) and exploring CPQC applications for variable-weight baskets and other practical financial products.
## Key ideas
- #idea:quantum-advantage — Classical pretraining of shallow parameterized quantum circuits (PQCs) and conversion to conditional PQCs (CPQCs) yields substantial reductions in CNOT counts and circuit depth versus a quantum-arithmetic (Qiskit finance) baseline for amplitude-estimation-based Monte Carlo option pricing.
- #idea:hybrid-approach — The workflow is hybrid: perform automated classical architecture search and gradient-based parameter training on a classical simulator, then translate trained PQCs into CPQCs (controlled rotations) for use in amplitude estimation.
- #idea:near-term-feasibility — Restricting encoding blocks to single-qubit rotations enables efficient controlled encodings (linear O(n) scaling in control qubits) and produces shallow, hardware-aware circuits aimed at NISQ-era applicability.
- #idea:hybrid-approach — Automated quantum architecture search (variable-ansatz + genetic-style optimization) with gate-pruning finds compact ansätze that trade classical preprocessing/training time for quantum resource savings.
- #idea:quantum-advantage — Representative numeric results reported (e.g., CPQC CNOT count 92 and depth 151 for n=14 in a two-asset basket example) supporting resource savings claims on the tested instances.
- #limitation:simulation-only — All training and evaluation were performed on noiseless classical simulators (PennyLane); no experiments on real quantum hardware were reported.
- #limitation:no-empirical-validation — The approach is not validated on physical QPUs, so the impact of noise and real-device constraints is untested.
- #limitation:qubit-count — Numerical experiments are limited in scale (examples up to n=14 control qubits); scalability to much larger discretizations or many-assets baskets is not demonstrated.
## Contradictions
<!-- Step 6 output — where this paper contradicts others -->

## Notable quotes
<!-- Researcher-added — verbatim quotes with page references -->

## Researcher notes
<!-- Researcher-added — not LLM generated -->
