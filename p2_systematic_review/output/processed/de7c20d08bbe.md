---
aliases:
- Novel Quantum Circuit Designs of Random Injection and Payoff Computation for Financial
  Risk Assessment
- Novel Quantum Circuit Designs
authors:
- Yu-Ting Kao
- Yeong-Jar Chang
- Ying-Wei Tseng
auto_detected: true
classification: ''
contradiction_flags:
- contradiction:scalability
- contradiction:classical-vs-quantum
doi: ''
evaluation_type: simulator
evidence_type: ''
has_quantitative_results: true
idea_tags:
- idea:quantum-advantage
- idea:near-term-feasibility
- idea:hybrid-approach
journal_or_venue: SNUG Taiwan Conference (proceedings) / Conference paper
methodology_tags:
- amplitude-estimation
- hybrid-quantum-classical
- error-mitigation
paper_type: ''
quantum_advantage_claim: speculative
related_papers: []
relevance_phase1: high
relevance_phase3: high
source_type: conference-paper
source_type_confidence: medium
step1_date: unknown_pre_2026-05-02
step1_model: gpt-5-mini
step2_date: unknown_pre_2026-05-02
step2_model: gpt-5-mini
step3_date: unknown_pre_2026-05-02
step3_model: gpt-5-mini
step4_date: unknown_pre_2026-05-02
step4_model: gpt-5-mini
step5_date: unknown_pre_2026-05-02
step5_model: gpt-5-mini
step6_date: unknown_pre_2026-05-02
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
- topic/risk-management
- method/amplitude-estimation
- method/hybrid-quantum-classical
- method/error-mitigation
- idea/quantum-advantage
- idea/near-term-feasibility
- idea/hybrid-approach
- contradiction/scalability
- contradiction/classical-vs-quantum
title: Novel Quantum Circuit Designs of Random Injection and Payoff Computation for
  Financial Risk Assessment
topic_tags:
- derivative-pricing
- simulation-monte-carlo
- risk-management
year: '2025'
zotero_key: ''
---

## Abstract summary
The paper introduces two quantum-circuit components—one for injecting randomness across massively parallel threads and one for directly computing option payoffs—enabling purely quantum preprocessing and conditional averaging without classical partitioning. The authors integrate these designs with Quantum Amplitude Estimation to claim quadratic speedup, demonstrate a Qiskit implementation with experimental verification of randomness and payoff correctness, and argue the approach is scalable to very large thread counts for financial risk assessment.
## Methodology
The paper proposes two integrated quantum-circuit components for financial risk assessment: (1) a novel Random Injection mechanism that injects discrete random bits into massively-parallel thread-level quantum computations, and (2) a Payoff Computation circuit that performs threshold filtering and weighted averaging entirely in-quantum using a Mixed-Signal Switch style control. The Random Injection method is shown analytically to be equivalent in expectation to deterministic grid-sampling over the random parameter, and is combined with Quantum Amplitude Estimation (QAE) so that the deterministic QAE estimate corresponds to the expected value of the randomized massive parallel function. The Payoff circuit encodes price as 5-bit registers (ABCDE → values 0–31), uses digital control on the high bits (AB==11 for price≥24) to route a lower-bit mean (LM) into a payoff register (PF) only for prices above the strike, and computes weighted averages inside the quantum circuit (formulas given for PF and LM). Experiments are implemented in IBM Qiskit, using simulated Monte Carlo-style inputs (5-bit price representation) and measurements (histograms) to validate both the randomness distribution from the Random Injection and the correctness/accuracy of the in-circuit payoff computation, including calibration comparisons against classical baselines and Taylor-series-derived calibration.

**Algorithms used:** Quantum Amplitude Estimation (QAE), Random Injection (proposed randomized gate injection technique), In-circuit Payoff Computation using Mixed-Signal Switch control, Quantum Monte Carlo (conceptual/comparative usage)
**Frameworks:** Qiskit

**Experimental setup:** Implemented and evaluated using IBM Qiskit. Experiments reported with 8 parallel logical threads (n=3), expanded to 16 outputs after random injection, and 1,600 measurement shots. Price encoding used 5 qubits (5-bit price ABCDE representing 0–31). QAE-related discussion mentions m=32 quantum operations as comparable to classical 1024 samples.

**Dataset:** Synthetic Monte Carlo-style stock-price samples encoded as 5-bit integers (0–31). Experiments used 1,600 measurement shots to produce empirical histograms / probability distributions of price outcomes; certain experiments produced only 16 non-zero price outcomes out of 32 possible states.
## Experiment details
### Input
{'source': 'Synthetic Monte Carlo simulation (generated within the experimental setup)', 'size': '1,600 measurement shots / iterations', 'representation': '5-bit binary encoding of price (bits A,B,C,D,E representing values 0..31)', 'preprocessing': 'Optional pre-shifting of inputs to accommodate different strikes (paper describes shifting inputs by subtracting a constant so the fixed circuit threshold at decimal 24 corresponds to other strike prices). No external dataset or market data used.'}

### Process
{'steps': ['Prepare quantum circuit in Qiskit with price register (5 qubits), random-injection qubits (2 bits used for r ∈ {0,1,2,3}), and auxiliary registers for LM and PF.', 'Initialize / prepare amplitude distributions corresponding to the Monte Carlo-like price process (superposition over price states).', 'Apply Random Injection gates: inject random bits into all parallel threads so that one random pattern (r==3) flips a target bit (XOR) producing randomized outcomes; analytically show equivalence to deterministic grid-sampling average.', 'Implement Mixed-Signal Switch logic in-circuit: use digital control on the high-order bits (AB==11 corresponding to price≥24) to route LM into PF; otherwise set PF=0.', 'Compute weighted averages within the circuit per provided PF and LM summation formulas (PF = sum_{i=0..7} P[i+24] * (i*m + k); LM aggregates grouped probabilities similarly).', 'Run the circuits in Qiskit with 1,600 shots, collect measurement histograms, convert counts to probabilities (p = |Ci|^2), and compute PF and LM from measured distributions.', 'Compare quantum results against classical baselines (classical computation, original quantum without calibration, quantum with analog calibration, Taylor-series approximation) and report error rates and calibration improvements.'], 'parameters_and_variations': ['Number of logical threads used in reported experiments: 8 (n=3), expanded to 16 after random injection in some runs.', 'Price encoding bits: 5 (ABCDE).', 'Measurement shots: 1,600.', 'QAE discussion: m=32 quantum operations referenced for quadratic speedup comparison.']}

### Output
{'result_format': 'Histograms of measured outcomes (counts per price value), probabilities computed from counts, computed weighted averages PF and LM from the measured probability distribution.', 'metrics_reported': ['Observed change-probability for sign-change event after random injection (expected 0.25; reported average error 9.26% at 1,600 shots).', 'Payoff (PF) and Lower-bit Mean (LM) values computed from measured distributions.', 'Relative error percentages comparing quantum vs classical and pre/post calibration (e.g., PF error reduced from 3.912% to 0.0134% after calibration; LM error reduced from 3.248% to 0.0079%).'], 'baselines': ['Classical Monte Carlo / direct classical computation (used as baseline for accuracy comparisons).', 'Original uncalibrated quantum computation and Taylor-series / analog calibration variants.']}

### Parameters
- price_bits: 5
- initial_threads: 8
- post_injection_outputs: 16
- random_bits_for_injection: 2
- shots: 1600
- QAE_m_operations: 32
- strike_threshold_decimal: 24
- calibration_scaling_factor_reported: 1.57

### Hardware
{'simulator': 'IBM Qiskit (framework); experiments implemented in Qiskit environment', 'qpu_model': None, 'cloud_provider': 'IBM (Qiskit ecosystem)'}

### Reproducibility
The paper states implementation in IBM Qiskit and provides circuit-level descriptions, formulas for PF and LM, and experimental parameters (shots=1600, price_bits=5, threads=8). However, no code repository, circuit source files, input seed data, or Qiskit scripts are provided in the paper. Some implementation details (exact gate sequences, circuit depth, mapping of auxiliary qubits, noise model/simulator backend) are not specified, which limits direct reproducibility without contacting the authors or re-implementing the circuits from the provided high-level description.
## Findings
- [supported] The authors implemented an integrated quantum circuit in Qiskit that combines random-number injection and in-circuit payoff computation, tested on an 8-thread example with 1,600 measurement shots.
- [supported] For a toy XOR example the paper derives and demonstrates the equivalence between Random Injection (stochastic r) and exhaustive Grid Sampling (deterministic r) in expectation, showing identical analytic averages.
- [supported] Empirical random-injection results (1600 shots) produced an average error of 9.26% relative to the expected sign-change probability (0.25) in the reported experiment.
- [supported] The proposed quantum payoff circuit (5-bit price, threshold at decimal 24) can filter values >=24 and compute the weighted average (payoff) entirely inside the quantum circuit without classical preprocessing; this behavior is demonstrated experimentally.
- [supported] The paper reports specific numerical improvements from analog calibration: payoff error reduced from 3.912% to 0.0134%, and low-bit-mean (LM) error reduced from 3.248% to 0.0079%, in the presented experiments.
- [supported] The Mixed-Signal Switch concept (digital control routing based on high bits AB=11) is implemented in the circuit to route and conditionally include only prices >= strike in the payoff computation.
- [speculative] The authors claim that combining Random Injection with Quantum Amplitude Estimation (QAE) yields a convergence rate O(m^-1) (quantum) vs classical Monte Carlo O(m^-1/2), i.e., a quadratic advantage for randomized massive-parallel simulations.
- [speculative] The design is described as scalable to 2^n parallel threads (authors claim scalability to extremely large thread counts such as 2^266 or millions of threads) and as offering a path toward demonstrating quantum supremacy.
- [speculative] The authors assert that their approach simultaneously preserves statistical randomness at the thread level while retaining QAE's quadratic speedup, overcoming an alleged tension between QAE determinism and the need for randomness.
- [supported] The authors report they implemented 23 threads in the current demonstration and claim the architecture generalizes to 2^n threads by construction.
- [speculative] The statement that QAE produces an exact deterministic average equivalent to exhaustive deterministic grid evaluation (without repeated sampling) is presented as a conceptual claim; the paper frames QAE as a deterministic statistical estimator for large-scale random simulations.
- [supported] The paper presents an empirical calibration relationship (scaling factor ~1.57) aligning an analog rotation calibration with a Taylor-series-based mapping, which reduced approximation errors in their experiments.

**Results summary:** The paper presents an integrated quantum-circuit architecture that injects randomness and computes payoffs wholly within a quantum circuit. The authors implemented prototypes in Qiskit (8-thread example, 1,600 shots; also reference to 23 threads implemented) demonstrating: (1) a random-injection mechanism whose empirical histogram matches expected probabilities with a reported average error of 9.26%; (2) an in-circuit payoff filter/averager for 5-bit encoded prices with threshold 24 that sets PF=0 below threshold and computes weighted averages above threshold; and (3) large reductions in approximation error after analog calibration (payoff error 3.912%→0.0134%, LM 3.248%→0.0079%). The paper also provides theoretical arguments that random-injection expectation equals exhaustive grid sampling and asserts that integrating random injection with QAE yields quadratic convergence and scalable parallelism (2^n threads), claims which are presented as theoretical/speculative paths to quantum advantage and potential quantum supremacy.

**Performance claims:**
- 8 parallel threads implemented in demonstration
- 1,600 measurement shots used in experiments
- Average error for random-injection histogram: 9.26% (with 1,600 shots)
- Payoff (PF) error reduced from 3.912% to 0.0134% after analog calibration (reported)
- Low-Bit Mean (LM) error reduced from 3.248% to 0.0079% after analog calibration (reported)
- Implemented prototype with 23 threads; circuit claimed scalable to 2^n threads
- Illustrative QAE claim: m = 32 quantum operations purportedly match m^2 = 1024 classical Monte Carlo samples (used as an example of quadratic advantage)
## Quantum advantage claim
**Classification:** speculative

The paper asserts a quadratic convergence advantage by combining Random Injection with Quantum Amplitude Estimation (QAE) and claims scalability toward massive parallelism and potential quantum supremacy. However, the work provides limited empirical demonstration of QAE-based speedup (the experiments reported use finite-shot sampling on small instances), so the claims about realized quantum advantage and scalability remain theoretical/speculative rather than demonstrated.
## Limitations
- Quantum Amplitude Estimation (QAE) is deterministic and suppresses measurement randomness; reconciling deterministic QAE with the need for statistical randomness is identified as a core dilemma by the authors.
- Experimental validation is small-scale: the implementation reported used IBM Qiskit with 8 parallel threads (paper also references a current implementation of 23 threads) and 1,600 measurement shots; empirical results show non-negligible error (average error 9.26%) attributed to randomness and finite shots.
- Loading arbitrary probability density functions (PDFs) into quantum states is still a challenging problem and is not solved by the proposed circuitry (author-stated limitation of the field acknowledged in the paper).
- The presented payoff circuit is implemented with a fixed strike-price threshold (24 decimal) and uses input shifting to adapt to other strikes (i.e., requires pre-shifting of inputs rather than a fully general dynamic threshold within the same circuit).
- [inferred] The Mixed-Signal Switch / analog–digital control mechanism central to the payoff circuit relies on nonstandard or less-proven quantum/analog hardware primitives; practical availability and low-level implementation details are not provided.
- [inferred] The equivalence between random injection and exhaustive grid sampling is demonstrated for a discrete uniform random variable (r ∈ {0,1,2,3}); it is unclear if and how the approach generalizes to non-uniform, continuous, high-dimensional, or correlated random variables.
- [inferred] Claims of achieving quadratic speedup and a path toward quantum supremacy are theoretical in the paper and are not empirically demonstrated at scale; device noise, gate errors, state-preparation overhead, and realistic resource constraints may negate the advantage.
- [inferred] Shot noise and statistical errors observed (e.g., 9.26% error with 1,600 shots) indicate the need for larger measurement budgets or improved variance reduction; the paper does not fully characterize shot-scaling requirements for target accuracies.
- [inferred] The paper does not provide quantitative resource estimates (required qubits, circuit depth, gate counts, or fault-tolerance/error-correction requirements) for the large-scale examples (e.g., millions of threads, 2^266-sized state spaces).
- [inferred] Payoff computation experiments are demonstrated for 5-bit price encoding (32 levels); scaling to higher-resolution price representations (more bits) may substantially increase circuit complexity and is not analyzed.
## Open questions
- How can arbitrary and complex PDFs be prepared efficiently and scalably on quantum hardware to feed the proposed random-injection and payoff circuits?
- What are the concrete hardware requirements and implementation details for the Mixed-Signal Switch and analog quantum operations proposed for thresholding and weighted averaging?
- How does realistic device noise (decoherence, gate errors, measurement error) affect the claimed equivalence between random injection and exhaustive grid sampling and the claimed O(m^-1) convergence?
- Can the random-injection technique be generalized to non-uniform, continuous, multi-dimensional, or correlated random variables common in financial risk models?
- What are the practical resource (qubits, gates, depth) and runtime requirements to realize the claimed large-scale scenarios (e.g., million parallel threads or 2^n threads) on near-term or fault-tolerant quantum devices?
- How does state-preparation overhead, and any required classical pre-processing (e.g., input shifting for different strike prices), impact end-to-end speedup compared to classical Monte Carlo?
- What measurement budgets (number of shots) and QAE parameter settings (m) are required in practice to reach industry-relevant accuracies for VaR/CVaR and option pricing?
- How robust is the analog calibration factor (reported 1.57) across different problem instances, and what is the theoretical justification and limits of that calibration?
- Can the approach be implemented and validated on physical quantum hardware (beyond simulator/Qiskit experiments) and produce empirical evidence of quantum speedup for realistic financial workloads?
- How to handle dynamic or multiple strike prices within a single circuit instance without resorting to classical per-instance shifting or repeated circuit compilation?

**Future work:**
- Provide more detailed analysis and demonstrations of how random injection can achieve quadratic speedup and contribute toward quantum supremacy (authors state intent to introduce more details).
- Scale up experiments to much larger thread counts (e.g., 2^n or million-thread scenarios) to empirically validate scalability claims.
- Extend and apply the proposed random-injection and payoff computation framework to other domains such as physical system modeling, stochastic optimization in machine learning, and cryptographic analysis (mentioned applicability).
- Implement and validate the Mixed-Signal Switch architecture and analog calibration on real quantum hardware to confirm feasibility and quantify hardware requirements.
- Integrate random injection with QAE in large-scale risk-assessment tasks (e.g., VaR/CVaR) and empirically demonstrate the quadratic speedup in end-to-end workflows.
- Refine state-preparation and PDF-loading methods compatible with the proposed circuits to reduce initialization overhead.
## Key ideas
- #idea:quantum-advantage — Authors claim quadratic speedup for expected-value estimation by integrating in-circuit Random Injection and Payoff Computation with Quantum Amplitude Estimation (QAE).
- #idea:hybrid-approach — Entire payoff filtering and weighted averaging are implemented inside the quantum circuit, with classical calibration (scaling/Taylor adjustments) applied post-measurement to dramatically reduce error.
- #idea:near-term-feasibility — Demonstrated Qiskit implementation and measurements (5-bit price encoding, 8 logical threads, 1,600 shots) and analytical equivalence of Random Injection to grid-sampling; authors argue approach scales to large thread counts.
- #limitation:simulation-only — All experimental verification was performed in the Qiskit environment (simulator); no real-QPU runs or noise-modelled hardware experiments reported.
- #limitation:qubit-count — Experiments use very small encodings (5-bit price register, few auxiliary qubits, 8 threads expanded to 16 outputs), raising questions about extension to realistic price precision and problem sizes.
- #limitation:data-encoding — Price is discretized to 5 bits (0..31) and requires input pre-shifting to match fixed circuit thresholds, indicating nontrivial encoding and preprocessing costs for real market data.
- #limitation:noise — Paper does not evaluate or report results under realistic hardware noise models or on noisy quantum hardware; calibration improvements are demonstrated on simulator measurements, not noisy QPUs.
## Contradictions
- Paper asserts scalability and quadratic speedup via QAE for large-thread financial risk assessment, but provides only small-scale simulator experiments (5-bit prices, 8 threads, 1,600 shots) and no QPU or noise-model validation — claiming large-scale speedups without commensurate empirical evidence.
- Paper claims quantum superiority (QAE-based quadratic advantage) while relying on coarse discretization, classical calibration postprocessing (scaling/Taylor corrections) and simulator-based verification; these factors undercut the strength of the quantum-vs-classical advantage claim in practical, noisy, high-precision settings.
## Notable quotes
<!-- Researcher-added — verbatim quotes with page references -->

## Researcher notes
<!-- Researcher-added — not LLM generated -->
