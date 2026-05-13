---
aliases:
- Exponential qubit reduction in optimization for financial transaction settlement
- Exponential qubit reduction optimization
authors:
- Elias X. Huber
- Benjamin Y.L. Tan
- Paul R. Griffin
- Dimitris G. Angelakis
auto_detected: true
classification: ''
contradiction_flags: []
doi: 10.1140/epjqt/s40507-024-00262-w
evaluation_type: real-hardware
evidence_type: ''
has_quantitative_results: true
idea_tags:
- idea:quantum-advantage
- idea:near-term-feasibility
- idea:hybrid-approach
journal_or_venue: EPJ Quantum Technology
methodology_tags:
- variational-nisq
- quantum-ml
- hybrid-quantum-classical
paper_type: ''
quantum_advantage_claim: speculative
related_papers:
- 2021_Tan_QubitEfficientEncoding
relevance_phase1: high
relevance_phase3: high
source_type: peer-reviewed-empirical
source_type_confidence: high
step1_date: '2026-04-14T12:00:48.397632'
step1_model: gpt-5-mini
step2_date: '2026-04-14T12:00:48.397632'
step2_model: gpt-5-mini
step3_date: '2026-04-14T12:00:48.397632'
step3_model: gpt-5-mini
step4_date: '2026-04-14T12:00:48.397632'
step4_model: gpt-5-mini
step5_date: '2026-04-14T12:00:48.397632'
step5_model: gpt-5-mini
step6_date: '2026-04-14T12:00:48.397632'
step6_model: gpt-5-mini
steps_completed:
- 1
- 2
- 3
- 4
- 5
- 6
tags:
- topic/trading-execution
- method/variational-nisq
- method/quantum-ml
- method/hybrid-quantum-classical
- idea/quantum-advantage
- idea/near-term-feasibility
- idea/hybrid-approach
title: Exponential qubit reduction in optimization for financial transaction settlement
topic_tags:
- trading-execution
year: '2024'
zotero_key: ''
---

## Abstract summary
The authors extend a qubit-efficient encoding for QUBO problems with linear inequality constraints and apply it to financial transaction settlement instances derived from exchange data. They introduce a simplified qubit-scaling scheme, a new register-preserving variational ansatz that leverages symmetries to reduce sampling overhead and improve stability, and methods for handling slack variables and variance reduction; benchmarks show competitive performance versus QAOA for 16-transaction problems and demonstrations up to 128 transactions on real quantum hardware.
## Methodology
The authors extend a qubit-efficient encoding (Tan et al., 2021) and apply it to the financial transaction settlement problem constructed from anonymized exchange data. They transform the constrained binary settlement formulation into a mixed-binary optimization (MBO) by introducing continuous slack variables and a quadratic penalty (penalty parameter λ) and then obtain a QUBO for fixed slack variables. To reduce qubit requirements they use a binary-addressing (ancilla + register) encoding: a set-covering A partitions bit positions into subsets of size na (ancilla bits) indexed by nr = ceil(log2(|A|)) register qubits. Two variational circuit ansätze are considered: (i) a hardware-efficient ansatz (RY rotations + entangling CNOT layers) and (ii) a register-preserving ansatz composed of conditional RY rotations and register basis permutations designed to maintain uniform sampling across registers. A greedy sampling algorithm reconstructs full bit-vectors from multiple measurements of ancilla+register states; marginal probability estimators ˆpi and ˆpij are computed from the measurement outcomes and used to build a cost estimator for training. Circuit parameters are optimized classically using either COBYLA (gradient-free) or gradient descent with gradients computed by the parameter-shift rule; slack variables are updated analytically via a rectified expression (equation (22)) eliminating an outer numerical loop for s. Experiments include training and evaluation on simulators (PennyLane) and real QPUs (IBM and IonQ) for problem sizes up to 128 transactions. Benchmarks compare the qubit-efficient approaches (different na) and ansätze against standard QAOA and a uniform-random baseline. Key meta-parameters (shots, depth, penalty λ, regularization η, optimizer details) are reported and sensitivity explored.

**Algorithms used:** QAOA, Variational Quantum Algorithm (VQA) / VQE-style optimization, Qubit-efficient encoding (ancilla+register binary encoding), Register-preserving variational ansatz (conditional RY rotations + register permutations), Hardware-efficient variational ansatz (RY + CNOT layers), Greedy sampling algorithm for reconstructing full bit-vectors, Parameter-shift rule for gradient evaluation, COBYLA (classical optimizer), Gradient descent (classical optimizer)
**Frameworks:** PennyLane, SciPy

**Experimental setup:** Simulations performed with PennyLane (pennylane=0.29.1) and SciPy (scipy=1.10.1). Experiments run on both noise-free simulators and real quantum hardware: IBM Quantum backends (ibm_geneva, ibm_hanoi) and IonQ backends (ionq_harmony, ionq_aria). Problem instances: primarily I=16 transactions (K = 10,12,13 parties) and an instance with I=128 transactions (K=41). Qubit counts varied according to ancilla/register choices (nq = na + ceil(log2(|A|))). Measurements (shots) typically 1e4 or 2e4 per circuit execution; bit-vector sampling drawn from collected shots (e.g., 500–1000 bit-vectors per trained generator reported).

**Dataset:** Anonymized transaction instruction records from a regulated financial exchange. Each instruction includes PARTICIPANT, COUNTERPARTY, INSTRUMENT, QUANTITY (security), CONSIDERATION (currency), and SETTLEMENT_TYPE (DVP or FOP). Authors used only cash and one security (J=2) in experiments.
## Experiment details
### Input
{'source': 'Anonymized transaction data provided by a regulated financial exchange (available from corresponding author upon reasonable request)', 'sizes': [{'I': 16, 'K': [10, 12, 13], 'notes': 'Three sampled settlement problems constructed'}, {'I': 128, 'K': 41, 'notes': 'One larger settlement problem constructed'}], 'preprocessing': 'Constructed each instance by (1) selecting I-R transactions and assigning parties, (2) choosing minimal non-negative balances balk so those I-R transactions are jointly feasible, then (3) adding R random transactions (R = floor(I/4)). Per-party and per-security normalization applied: each party/security scaled by γ_kj = mean(|v_ikj|) over nonzero entries to mitigate scale/unit differences. Slack variables introduced and either optimized analytically (via equation (22)) or alternated in QAOA experiments.'}

### Process
{'pipeline_steps': ['Formulate settlement optimization as max w^T x with linear balance constraints and convert to MBO by adding quadratic slack penalties (penalty parameter λ).', 'For fixed slack s, obtain QUBO matrix Q = A + Diag[b(s)].', 'Choose qubit-efficient covering A (authors use disjoint covering via k-means-inspired clustering on transaction graph) and set ancilla count na and register count nr = ceil(log2(|A|)).', 'Prepare parameterized quantum circuit (either hardware-efficient or register-preserving ansatz) and initialize parameters uniformly at random.', 'Execute PQC on simulator / QPU to collect nshots measurements; use greedy sampling across measurements to reconstruct full bit-vectors; compute marginal estimators ˆpi and ˆpij from measurement outcomes.', 'Compute cost estimator ˆC(θ) (uses marginal probabilities, QUBO coefficients, optimal slack substitution ˆs(θ) = max(0, ...)). Optionally add register-regularization penalty.', 'Optimize circuit parameters θ via classical optimizer (COBYLA or gradient descent using parameter-shift gradients). For QAOA runs alternate slack-variable updates and circuit parameter optimization (authors used 50 alternations with up to 1000 COBYLA iterations per cycle).', 'Post-training, sample many bit-vectors from trained PQC (reusing shots) and compute actual cost and feasibility; compare cost distributions to QAOA and uniform-random baseline; run selected pre-trained circuits on real QPUs for hardware evaluation.'], 'iterations_and_repeats': 'Optimization repeated across multiple random initializations (e.g., 25 runs for qubit-efficient experiments, 10 for QAOA). For QAOA slack alternation: ~50 alternations with up to 1000 COBYLA iterations per alternation.'}

### Output
{'formats': ['Empirical cumulative distribution functions (ECDF) of normalized costs over generated bit-vectors', 'Training convergence traces (cost vs. optimization steps)', 'Statistics on number of feasible/settled transactions per sampled bit-vector', 'Gradient variance estimates (shot-noise impact) vs circuit depth'], 'metrics_reported': ['Cost (normalized and unnormalized), computed by x^T Q x (or equivalent MBO objective with slack substitution)', 'Distribution of costs across sampled bit-vectors', 'Feasibility fraction (bit-vectors satisfying balance constraints)', 'Comparison against QAOA and uniformly random sampling'], 'baselines': ['Standard QAOA (alternating operator ansatz)', 'Uniform random sampling (random bit-vectors)'], 'key_findings_summary': 'Register-preserving ansatz generally outperformed the hardware-efficient ansatz and QAOA in the tested 16-transaction problems; deeper qubit-efficient circuits improved performance; hardware runs (IonQ and IBMQ) showed degradation due to noise but IonQ (all-to-all connectivity) often outperformed IBM for register-preserving circuits; experiments demonstrated ability to run a 128-transaction instance on real quantum hardware using qubit-efficient encoding.'}

### Parameters
- penalty_lambda: 10
- register_regularization_eta: 1000
- gradient_max_steps: 1500
- gradient_stepsize: 0.00025
- optimizers: ['COBYLA', 'Gradient descent (with parameter-shift gradient)']
- number_of_runs: 25
- parameter_initialization: Uniform random in [0, 2π]
- depth_d: [1, 4]
- ancilla_qubits_na: [1, 4, 8, 16]
- shots_nshots: [10000, 20000]
- R_choice: R = floor(I/4) (number of transactions reserved to make some infeasible)
- QAOA_p_values: Varied up to 10 for comparisons (no significant improvement observed in these experiments)
- qubit_counts_examples: {'I=16, na=1': 'nq = 1 + ceil(log2(16)) = 5.. (examples reported with 5 or 6 depending on encoding)', 'I=16, na=4': 'nq = 4 + ceil(log2(16/4)) = 6', 'I=128, na=16': 'nq = 16 + ceil(log2(128/16)) = 19'}

### Hardware
{'simulator': {'name': 'PennyLane', 'version': '0.29.1'}, 'quantum_processors': [{'provider': 'IBM Quantum', 'models': ['ibm_geneva', 'ibm_hanoi'], 'notes': 'ibm_geneva used in some runs; ibm_hanoi used for larger experiments'}, {'provider': 'IonQ', 'models': ['ionq_harmony', 'ionq_aria'], 'notes': 'ionq_harmony (11 qubits) and ionq_aria (larger device) used; IonQ performance often better for register-preserving ansatz due to all-to-all connectivity'}], 'classical_frameworks': ['SciPy 1.10.1 (COBYLA)', 'PennyLane for circuit simulation and execution'], 'cloud_providers': ['IBM Quantum', 'IonQ', 'Amazon Web Services (acknowledged usage)']}

### Reproducibility
Anonymized transaction data samples are available from the corresponding author upon reasonable request (permission by the regulated exchange). Implementation details and numeric hyperparameters are reported (Table 4). Simulator and SciPy versions are stated (PennyLane 0.29.1, SciPy 1.10.1). No public code repository or scripts are provided in the paper; reproduction would require reimplementation of the qubit-efficient mapping, cost estimator, sampling algorithm and register-preserving ansatz as specified in the text. Therefore, data availability is partial (on request) but code is not publicly provided; experimental backends and versions are named which facilitates replication given an independent implementation.
## Findings
- [supported] The authors extend a qubit-efficient encoding scheme to represent QUBO problems with linear inequality constraints using exponentially fewer qubits (encoding cost from O(I) to O(na + log(I/na))).
- [supported] The paper introduces a register-preserving variational ansatz tailored to the qubit-efficient encoding that reduces sampling variance and improves numerical stability in simulations.
- [supported] For 16-transaction settlement instances, the qubit-efficient approaches (hardware-efficient and register-preserving ansätze) produced competitive or better solution-quality distributions compared with standard QAOA in simulation; the register-preserving ansatz performed best overall in the reported benchmarks.
- [supported] The authors demonstrated execution of instances with 128 transactions on real quantum hardware (IonQ and IBMQ), using the qubit-efficient encoding, thereby increasing the largest demonstrated instance size compared to prior reported NISQ runs.
- [supported] Experimental results indicate backend-dependent behavior: ion-trap hardware (IonQ) outperformed the tested IBM superconducting backends for the register-preserving ansatz, attributed to all-to-all connectivity reducing SWAP overhead.
- [supported] Register-preserving circuits show substantially lower shot-noise variance of gradient estimates (empirical evidence presented in simulations), enabling more stable optimization and potential shot reductions.
- [supported] The paper provides an explicit estimator for the cost (including handling slack variables) and shows how to obtain optimal slack variables without an outer optimization loop (closed-form substitution using estimated marginals).
- [speculative] The authors claim the methods are directly applicable to any QUBO with linear inequality constraints; while plausible, only transaction-settlement instances (and related synthetic constructions) were tested.
- [speculative] The authors suggest the register-preserving design and symmetry incorporation may mitigate barren-plateau and optimization issues generally; empirical results support improved stability here, but broader generalization is not proven.
- [supported] The qubit-efficient encoding entails significant sampling overhead (trade-off between qubit reduction and required measurement shots), discussed and evidenced in the paper.
- [supported] The paper demonstrates practical engineering techniques (normalization of heterogeneous units, clustering-derived coverings for register assignment, and greedy sampling postprocessing) to construct and run settlement instances.

**Results summary:** This work extends a previously proposed qubit-efficient encoding and introduces a register-preserving variational ansatz for solving mixed-binary (transaction settlement) optimization instances with exponentially fewer qubits. In simulation on 16-transaction instances the qubit-efficient methods (particularly the register-preserving ansatz) were competitive with or outperformed standard QAOA in terms of solution-quality distributions and showed lower gradient-shot variance. The authors also executed 128-transaction instances on real quantum hardware (IonQ and IBMQ), demonstrating much larger instance sizes than earlier NISQ demonstrations. The approach trades qubit count reduction for increased sampling overhead and requires careful ansatz design and post-processing; the paper presents explicit cost estimators, slack-variable substitution, and practical implementation details.

**Performance claims:**
- 128 transactions were executed on quantum hardware (ionq_aria and ibm_hanoi) using 19 qubits (na=16 ancillas + nr register qubits), demonstrating exponential qubit compression compared to naive encoding.
- 16-transaction instances were solved in simulation using qubit-efficient encodings with as few as 5–6 physical qubits (versus 16 qubits in standard QAOA), and the register-preserving ansatz produced the best empirical solution distributions.
- Shots per experiment reported in benchmarks: 1e4 and 2.4e4 measurement shots were used to collect samples for cost estimation and sampling.
- The register-preserving ansatz showed substantially lower variance in gradient estimators across circuit depths in simulation (visualized in the paper), implying more stable optimization and fewer required shots (no single scalar reduction percentage reported).
- The authors report outperforming QAOA on the tested 16-transaction problems in their simulations; no asymptotic runtime or provable optimality guarantees were claimed.
## Quantum advantage claim
**Classification:** speculative

The paper demonstrates practical qubit-count reduction (exponential encoding) and scales instance size on hardware (128 transactions) beyond prior NISQ demonstrations for this problem class, but does not claim or provide evidence of a provable computational or runtime advantage over the best classical algorithms. Improvements shown are empirical and concern representational/engineering gains (qubit reduction, hardware feasibility) rather than demonstrated quantum speedup or superior classical performance guarantees.
## Limitations
- NISQ hardware limitations: limited number of qubits restricts problem size and connectivity constraints limit implementable QUBO connectivity and increase circuit depth/noise susceptibility (author-stated).
- Sampling overhead: the qubit‑efficient encoding requires many repeated measurements and greedy sampling to reconstruct full bit-vectors, incurring significant shot overhead (author-stated).
- Estimator approximations: marginal probability estimators (ˆpi, ˆpij, ˆμij) are heuristic for general (non-disjoint) coverings and only exact for disjoint coverings; this may bias the cost estimate (author-stated).
- Cost not naturally a Hermitian expectation: after qubit compression the optimization objective is generally not the expectation of a Hermitian observable unless additional constraints (e.g. register-preserving circuits, doubling the Hilbert space) are enforced (author-stated).
- Register‑preserving ansatz restrictions: imposing register-preservation limits the allowed variational gates and may reduce expressivity; constructing NISQ‑friendly yet expressive register-preserving circuits is challenging (author-stated).
- Optimization challenges: alternation between slack-variable updates and variational parameter updates (for QAOA/MBO) leads to a changing landscape and difficulty finding good minima; QAOA in this setting showed poor depth scaling (author-stated).
- Noise and hardware variability: real-device noise and limited connectivity (especially on superconducting devices) degrade performance; device connectivity affects which ansatz performs better (author-stated).
- Numerical instability/division-by-zero: if some registers are rarely sampled (|βr(θ)|^2 ≈ 0), denominators in estimators can cause instability, requiring regularization or register-uniform states (author-stated).
- Shot‑noise impact on gradients: gradient variance due to finite shots is non-trivial, though register-preserving circuits reduced variance empirically (author-stated).
- Need for classical post-processing: many generated bit-vectors violate constraints; projection/post-processing to feasible solutions was not explored and may be necessary (author-stated).
- Resource trade-offs: expressing the cost as a Hermitian observable (to use standard estimation tooling) can require doubling the number of qubits / circuit width (author-stated).
- Lack of classical benchmarking: the paper does not provide direct comparisons to state-of-the-art classical solvers on realistic instances, so classical competitiveness is not demonstrated (author-stated).
- [inferred] Scalability uncertainty: while 128-transaction instances were run, it is not clear how the approach scales in shot-cost, runtime, and optimization difficulty to much larger/industry-scale instances (inferred from discussion of shot and optimization overhead).
- [inferred] Data realism: balances were not available in the provided dataset and were constructed minimally to ensure feasibility; this may limit realism of the tested instances (inferred).
- [inferred] Dependence on covering/clustering: performance depends on the chosen covering (mapping of variables to register/ancilla sets) and clustering heuristic, which may be problem-dependent and suboptimal (inferred).
- [inferred] No optimality guarantees: the hybrid VQA/QAOA heuristics (especially with qubit compression) have no provable guarantees of finding global optima for NP-hard instances (inferred from general VQA/QAOA discussion).
- [inferred] Increased classical post-processing cost: projection/local search (e.g. Hamming-ball search) to obtain feasible solutions adds classical runtime which may grow quickly in worst case (inferred).
## Open questions
- How can register-preserving ansätze be generalized to increase expressivity while remaining NISQ‑friendly and numerically stable?
- What are optimal ancilla-register mappings and coverings (A) for given QUBO instances, and how should they be chosen or learned?
- How to reduce sampling/shot overhead (e.g., via classical shadows, smarter sampling, sample rejection, or reuse) while preserving solution quality?
- Can the heuristic marginal estimators for non-disjoint coverings be improved or made provably accurate? Under what conditions do they remain reliable?
- How to best integrate slack-variable optimization with the variational parameter optimization (simultaneously or via alternatives such as implicit differentiation) without destabilizing the landscape?
- What post-processing/projection methods are most effective to turn infeasible high-quality solutions into feasible near-optimal solutions, and what are their computational costs?
- How does noise sometimes produce better solutions than noise-free simulation in practice (as observed), and under which conditions does noise help or hurt?
- Can the cost objective for non-register-preserving circuits be expressed as a Hermitian observable without prohibitive resource overhead, or are there better formulations?
- How do meta-parameters (depth, penalty λ, regularization η, step-size) scale with problem size, and what are principled tuning strategies?
- How do these qubit‑efficient methods compare against state-of-the-art classical solvers on realistic, large-scale financial settlement instances?
- To what extent can methods like classical shadows be adapted to further reduce measurement complexity for the compressed encoding?
- How to extend the theoretical framework (e.g., theorem 1) to allow different register bases and to retain useful phase information on ancilla states?
- How to adapt QAOA specifically to mixed-binary optimization problems with slack variables in a way that avoids the alternating‑landscape problem?
- What are the trade-offs between doubling Hilbert-space (to express Hermitian cost) vs. alternative strategies in practice on available hardware?

**Future work:**
- Explore different ancilla-register mappings and coverings to improve performance and sampling efficiency.
- Investigate additional or alternative variational (register-preserving) ansätze that respect encoding symmetries while improving expressivity.
- Study and refine classical and quantum optimization algorithms and meta-parameter scaling (circuit depth, penalty λ, regularization, learning rates).
- Develop and evaluate classical post-processing methods (e.g., projection within a Hamming ball, heuristics restricted to violated parties and neighbors) to obtain feasible solutions from sampled bit-vectors.
- Extend the register-preserving ansatz class (e.g., change computational bases, keep track of ancilla phases) and study practical constructions for NISQ devices.
- Explore sampling improvements such as sample rejection, hidden layers in the ansatz, and deterministic register sampling to reduce shot requirements.
- Apply classical-shadows or other advanced measurement-reduction techniques to lower shot counts and runtime.
- Compare qubit‑efficient quantum methods to state-of-the-art classical solvers on realistic financial settlement instances to assess practical advantage.
- Investigate implicit differentiation or other techniques to jointly optimize slack variables and variational parameters.
- Analyze and incorporate error-mitigation strategies and Hermitian-expectation tooling (possibly via the doubled-Hilbert approach) for improved estimation on hardware.
- Study how to generalize and provide theoretical guarantees (or bounds) for the heuristic estimators and for performance on non-disjoint coverings.
## Key ideas
- #idea:quantum-advantage — Introduces a qubit-efficient ancilla+register binary encoding that achieves exponential qubit reduction for constrained QUBO formulations applied to transaction settlement.
- #idea:quantum-advantage — Benchmarks show the qubit-efficient variational approach is competitive with standard QAOA on 16-transaction instances and can be executed for a 128-transaction instance on real QPUs.
- #idea:hybrid-approach — Uses a hybrid quantum-classical pipeline: classical preprocessing (cover selection, slack analytic update), classical optimizers (COBYLA, gradient descent) and parameter-shift gradients to train variational circuits.
- #idea:near-term-feasibility — Proposes a register-preserving variational ansatz and greedy sampling to reduce sampling overhead and variance, enabling demonstrations on current IBM and IonQ hardware with realistic shot budgets.
- #limitation:noise — Reports and studies shot-noise and hardware noise impacts (gradient variance, stability) from real QPU runs, indicating noise still affects performance and sampling reliability.
- #limitation:data-encoding — The ancilla+register encoding requires a nontrivial reconstruction (greedy sampling) and marginal estimation pipeline, adding classical postprocessing and sampling complexity.
## Contradictions
<!-- Step 6 output — where this paper contradicts others -->

## Notable quotes
<!-- Researcher-added — verbatim quotes with page references -->

## Researcher notes
<!-- Researcher-added — not LLM generated -->
