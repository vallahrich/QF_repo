---
aliases:
- The maximum-likelihood quantum amplitude estimation algorithm provides the best
  tradeoff between accuracy and circuit depth among quantum solutions for integral
  estimation
- maximum likelihood quantum amplitude
authors:
- Marco Maronese
- Massimiliano Incudini
- Luca Asproni
- Enrico Prati
auto_detected: true
classification: ''
contradiction_flags: []
doi: 10.1109/QCE57702.2023.00069
evaluation_type: simulator
evidence_type: ''
has_quantitative_results: true
idea_tags:
- idea:quantum-advantage
- idea:near-term-feasibility
- idea:hybrid-approach
journal_or_venue: 2023 IEEE International Conference on Quantum Computing and Engineering
  (QCE)
methodology_tags:
- amplitude-estimation
- hybrid-quantum-classical
- qft-phase-estimation
paper_type: ''
quantum_advantage_claim: speculative
related_papers: []
relevance_phase1: high
relevance_phase3: high
source_type: conference-paper
source_type_confidence: high
step1_date: '2026-04-14T11:32:18.903814'
step1_model: gpt-5-mini
step2_date: '2026-04-14T11:32:18.903814'
step2_model: gpt-5-mini
step3_date: '2026-04-14T11:32:18.903814'
step3_model: gpt-5-mini
step4_date: '2026-04-14T11:32:18.903814'
step4_model: gpt-5-mini
step5_date: '2026-04-14T11:32:18.903814'
step5_model: gpt-5-mini
step6_date: '2026-04-14T11:32:18.903814'
step6_model: gpt-5-mini
steps_completed:
- 1
- 2
- 3
- 4
- 5
- 6
tags:
- topic/simulation-monte-carlo
- method/amplitude-estimation
- method/hybrid-quantum-classical
- method/qft-phase-estimation
- idea/quantum-advantage
- idea/near-term-feasibility
- idea/hybrid-approach
title: The maximum-likelihood quantum amplitude estimation algorithm provides the
  best tradeoff between accuracy and circuit depth among quantum solutions for integral
  estimation
topic_tags:
- simulation-monte-carlo
year: '2023'
zotero_key: ''
---

## Abstract summary
This conference paper compares standard Quantum Amplitude Estimation (QAE) with NISQ-friendly variants — Maximum Likelihood Amplitude Estimation (MLAE) and Iterative QAE (IQAE) — and a classical Metropolis-Hastings Monte Carlo benchmark for a 1D integral estimation task. Through Qiskit Aer simulations (3 qubits) the authors evaluate error scaling, circuit depth, and execution time, concluding that MLAE offers the best tradeoff between required circuit depth and estimation precision for near-term quantum hardware.
## Methodology
The study implements and benchmarks multiple quantum amplitude estimation (QAE) variants and a classical Monte Carlo baseline on a synthetic 1D numerical-integration task. The target integral is I = (1/bmax) ∫_0^{bmax} sin^2 x dx, discretized and encoded on a small quantum register (n = 3 qubits in the experiments). Quantum circuits: state-preparation P (uniform) realized with Hadamard gates and observable-encoding R realized with controlled-Y rotations on an ancilla. Algorithms compared are the original (phase-estimation-based) QAE, a Maximum-Likelihood Amplitude Estimation (MLAE / MLQAE) hybrid, an Iterative QAE (IQAE) hybrid, and a classical Metropolis-Hastings Monte Carlo (MHMC) baseline. All quantum experiments were run on the Qiskit Aer local simulator; each data point is an average over 10 runs with different simulator seeds. For MLAE and IQAE the authors sampled 100 shots per circuit; IQAE experiments used a 90% confidence level. Measured outcomes are estimation error (absolute error of integral estimate), maximum circuit depth required, and execution time on the local simulator. Error vs sample-count scaling was obtained by fitting a power-law x^-α to the measured error as a function of number of samples/oracle queries, and comparisons of depth and runtime across methods were performed to evaluate NISQ viability.

**Algorithms used:** Quantum Amplitude Estimation (QAE) - standard (phase-estimation based), Maximum Likelihood Amplitude Estimation (MLAE / MLQAE), Iterative Quantum Amplitude Estimation (IQAE), Metropolis-Hastings Monte Carlo (MHMC) - classical baseline
**Frameworks:** Qiskit (Aer local simulator)

**Experimental setup:** Local Qiskit Aer simulator. Quantum register size: n = 3 qubits (plus ancilla qubit for amplitude encoding as used in the circuits). Each plotted data point is averaged over 10 independent simulator runs with different seeds. MLAE and IQAE runs used 100 shots per circuit; IQAE used a 90% confidence interval for its iterative routine. State preparation P implemented with Hadamard gates; function encoding R implemented with controlled-Y rotations on ancilla.
## Experiment details
### Input
Synthetic 1D integral of f(x) = sin^2((x + 1/2) * bmax / 2^n) with uniform probability p(x) = 1/2^n. Discretization uses 2^n sample points; experiments used n = 3 (8 discrete points). No external/pre-existing dataset or financial data was used; inputs are generated analytically and encoded into the quantum circuits via Hadamard and controlled-Y rotations.

### Process
1) Define target integral and discretize it via n-qubit encoding. 2) Build quantum circuits: P (uniform superposition via Hadamards) and R (controlled-Y rotations to encode f(x) on ancilla). 3) For each algorithm: - Standard QAE: run phase-estimation style circuit (standalone in experiments) and measure ancilla to estimate amplitude. - MLQAE: run Grover-like circuits Q^k A for k = 0..M, collect counts (hk, Nk) and perform a classical maximum-likelihood fit over combined likelihood L(h, θ) to estimate θ and hence a = sin^2 θ. - IQAE: run iterative routine (FindNextK) selecting k per iteration, collect Nshots measurements per circuit to estimate probabilities, update confidence interval [θ_l, θ_u], repeat until target accuracy reached (experiments used a 90% confidence level). - MHMC: classical Metropolis-Hastings sampling of the integrand used as the classical baseline. 4) Repeat each experimental condition 10 times with different simulator seeds and average results. 5) Measure estimation error, maximum circuit depth for circuits run by each algorithm, and execution time on the simulator. 6) Fit error vs number-of-samples to a power-law x^-α and report slopes and comparisons across methods.

### Output
Outputs reported: absolute estimation error of the integral (plotted vs number of samples/oracle queries), maximum circuit depth required by each method, and wall-clock execution time on the local simulator (plotted vs error and vs number of samples). Error-scaling fits produced power-law exponents α (measured values reported): MLQAE ≈ 0.974 ± 0.058, standard QAE ≈ 1.267 ± 0.206, IQAE ≈ 0.971 ± 0.092, MHMC ≈ 0.485 ± 0.051 (note: MHMC result computed excluding a 10-sample outlier as reported). The classical baseline was Metropolis-Hastings Monte Carlo.

### Parameters
- qubits_total: 3
- discretization_points: 8
- shots_per_circuit: 100
- simulator_runs_per_point: 10
- IQAE_confidence_level: 90%
- algorithms_compared: ['QAE_standard', 'MLQAE', 'IQAE', 'MHMC']
- fitting_model: error vs samples fitted to power-law x^-α

### Hardware
{'simulator': 'Qiskit Aer (local simulator)', 'qpu_model': None, 'cloud_provider': 'IBM / Qiskit (local execution)'}

### Reproducibility
The paper reports implementation details (state-preparation with Hadamards, function-encoding with controlled-Y rotations, QAE variants compared, shot counts, number of qubits, number of simulator seeds and averaging) but does not provide code or a public repository link. All experiments were carried out on the Qiskit Aer local simulator; random seeds were varied (10 seeds averaged). No explicit publication of scripts, parameter files, or bmax value is provided; reproducing exact figures would require re-implementing the described circuits and routines with the reported settings.
## Findings
- [speculative] Quantum Amplitude Estimation (QAE) offers a quadratic algorithmic speedup over classical Monte Carlo methods in theory.
- [supported] In Qiskit aer simulations on a 1D integral using n=3 qubits, fitted scaling exponents (error vs number of samples) were: MLQAE: -0.974 ± 0.058, IQAE: -0.971 ± 0.092, standard QAE: -1.267 ± 0.206, classical Metropolis-Hastings MC: -0.485 ± 0.051.
- [supported] The Maximum Likelihood Amplitude Estimation (MLAE) approach provides the best trade-off between circuit depth and estimation precision among the tested quantum algorithms in the simulator experiments.
- [supported] Both hybrid algorithms (MLAE and IQAE) have shallower individual-circuit depths than the canonical QAE, but IQAE can require much deeper single circuits than MLAE for the same estimation error due to concatenated oracle calls.
- [supported] In simulator timing experiments, generating a classical Monte Carlo sample was approximately 4 orders of magnitude faster than one MLQAE sample on the simulated platform; under the simulated timing assumptions, MLQAE would only be faster than classical MC for extremely small target errors (authors estimate ~10^-13 to 10^-11).
- [speculative] With hypothetical faster quantum gate execution (100x–1000x faster than the simulator baseline), the error range where MLQAE could beat classical MC in runtime could shift to roughly 10^-9–10^-6 (authors' back-of-envelope estimates).
- [supported] IQAE supports choosing an arbitrary confidence level and uses an iterative classical subroutine to select Grover-iteration counts, while MLAE builds a global likelihood from multiple k-values and performs classical maximum-likelihood estimation.
- [speculative] The authors conclude that MLAE (maximum likelihood QAE, avoiding phase estimation) is the most promising near-term candidate to first demonstrate an advantage over classical Monte Carlo methods on realistic hardware.
- [speculative] Prior-cited estimates (from other work, cited by the authors) suggest that achieving precision ~10^-3 for practical problems may require ~1000 qubits with long coherence and high-fidelity gates.

**Results summary:** The paper compares standard QAE, MLAE, IQAE, and classical Metropolis-Hastings Monte Carlo on a 1D integral using Qiskit aer simulations (n=3 qubits). Empirical fits indicate near-quadratic scaling for the quantum schemes (slopes ≈ -1) and the expected 1/√M scaling for classical MC. MLAE achieves the best practical trade-off between circuit depth and estimation precision among the tested quantum variants; IQAE can require deeper single circuits despite comparable sample-scaling. In simulated wall-clock terms classical MC is far faster for practically reachable precisions; authors estimate that MLQAE would outperform classical MC only for extremely small target errors under current simulated gate speeds, though that regime could move into more practical ranges if quantum gate speeds improve substantially. The paper concludes MLAE is the best near-term candidate to first show advantage, but this remains conditional on hardware progress.

**Performance claims:**
- MLQAE fitted scaling exponent (error ∝ samples^α): α = -0.974 ± 0.058 (simulator, n=3 qubits).
- IQAE fitted scaling exponent: α = -0.971 ± 0.092 (simulator, n=3 qubits).
- Standard QAE fitted scaling exponent: α = -1.267 ± 0.206 (simulator, n=3 qubits).
- Classical Metropolis-Hastings MC fitted scaling exponent: α = -0.485 ± 0.051 (simulator results; note: result obtained without considering the case with 10 samples).
- Simulator timing: one classical MC sample generation was ~10^4 times faster than one MLQAE sample (on the Qiskit aer simulation platform used by the authors).
- Authors' simulated-runtime estimate: MLQAE might outperform classical MC only for target errors in the approximate range 10^-13 to 10^-11 under their simulator timing; with hypothetical 100x faster gates this shifts to ~10^-9–10^-8, and with 1000x faster gates to ~10^-7–10^-6 (order-of-magnitude estimates presented by the authors).
- Simulations used 3 qubits (n=3) and for MLQAE/IQAE runs the authors used 100 shots per quantum circuit (QAE executed standalone).
## Quantum advantage claim
**Classification:** speculative

The paper reiterates the theoretical quadratic speedup of QAE but does not demonstrate a practical advantage on current hardware; simulator experiments show MLAE as the most promising near-term candidate owing to lower circuit depth for comparable precision, yet any runtime advantage over classical Monte Carlo appears only in extremely small-error regimes or would require significantly faster/less noisy quantum hardware. Consequently, claims of a practical quantum advantage remain speculative.
## Limitations
- Author-stated: The canonical QAE requires fault-tolerant quantum hardware (long coherence times, high-fidelity gates) which is not currently available, preventing practical quadratic speedup.
- Author-stated: QAE circuits involve many controlled oracle queries and a QFT, producing circuit depths unsuitable for NISQ devices due to decoherence and gate errors.
- Author-stated: Current NISQ hardware has low coherence times and gate errors, so QAE has not yet shown advantage in practical cases.
- Author-stated: Simulations and benchmarks in the paper were performed on a Qiskit local simulator (aer) with only 3 qubits and a 1D test integrand (sin^2 x), limiting generality to larger or higher-dimensional problems.
- Author-stated: Some analyses (execution time comparisons) omitted three important factors: device noise, discretization/systematic error from limited qubits, and the potential loss of advantage when error correction is applied.
- Author-stated: Pure MLAE (as described) brings less than a quadratic advantage over classical Monte Carlo (citing Ref. [24]).
- Author-stated: The iterative IQAE can require very long circuits in practice (due to concatenated oracle calls within single circuits), which reduces NISQ feasibility.
- Author-stated: The performance comparisons depend on parameters such as the number of shots (Nshots) and the chosen confidence level α; these affect resource requirements and are not universally fixed.
- [inferred] The benchmarking on a simple low-depth 1D integrand may not reflect algorithmic performance or resource trade-offs for realistic financial integrals or high-dimensional problems.
- [inferred] The simulator-based execution time comparisons may not translate to real quantum hardware performance because they do not model realistic gate times, queueing, or classical-quantum interfacing overheads.
- [inferred] The evaluation does not include realistic noise models or error mitigation strategies, so relative rankings of MLQAE, IQAE, and canonical QAE could change under realistic noise.
- [inferred] The resource and runtime advantage thresholds identified (e.g., ranges of error where MLQAE might beat classical MC) are speculative and sensitive to optimistic assumptions about gate speeds and scaling.
- [inferred] Scalability questions remain about how circuit depth, required qubit counts, and classical post-processing scale for higher precision and higher-dimensional integrals in practice.
- [inferred] The need for repeated runs / many shots to boost confidence (or median-of-means) may substantially increase wall-clock time and classical overhead, potentially offsetting theoretical sample complexity gains.
## Open questions
- How will the presence of realistic device noise and the use of error mitigation or error correction change the practical advantage and relative ranking of QAE variants (canonical QAE, MLAE, IQAE) for integration tasks?
- What are the resource requirements (qubit count, circuit depth, gate fidelities, runtime) for achieving practically relevant precision (e.g., 10^-3) on real financial integration problems, and when will hardware meet those requirements?
- How do MLAE and IQAE scale and perform on higher-dimensional integrals and realistic financial models (e.g., multi-asset option pricing), beyond the 1D sin^2(x) benchmark used here?
- What is the best choice of algorithm parameters (number of shots Nshots, confidence level α, sequence of k in IQAE) to optimize the trade-off between circuit depth, classical overhead, and estimation error in practice?
- Can hybrid or variational variants (e.g., variational quantum amplitude estimation) be improved to regain more of the theoretical quadratic speedup while staying NISQ-friendly?
- To what extent do classical post-processing costs (MLE optimization, iterative decision logic) affect overall wall-clock time and scalability, especially for MLQAE variants that require classical optimization?
- How robust are the MLAE and IQAE methods to discretization/systematic errors that arise from finite qubit registers encoding continuous distributions?
- What are the real-world cross-over points (in error tolerance, problem dimensionality, and hardware performance) where quantum amplitude estimation variants outperform classical Monte Carlo methods on physical devices?

**Future work:**
- Author-suggested: Perform further resource analyses that include device noise models, the effects of finite qubit discretization (systematic errors), and the impact of error correction on algorithmic advantage.
- Author-suggested: Extend benchmarking to more realistic, higher-dimensional integrals (e.g., multidimensional problems relevant to finance) to evaluate scalability and practical performance.
- Author-suggested: Experimental validation on physical quantum hardware (not just simulators) to assess real execution times, noise effects, and feasibility of MLQAE and IQAE.
- Author-suggested: Quantify required qubit counts, coherence times, and gate fidelities needed to achieve target precisions (e.g., 10^-3) for practical applications, following and extending resource estimates like those cited in Ref. [8].
- [inferred] Investigate optimization of algorithm hyperparameters (Nshots, α, choice of k sequence) and classical post-processing routines to reduce wall-clock time and circuit depth.
- [inferred] Study hybrid/variational modifications (e.g., variational quantum amplitude estimation) to improve empirical scaling while maintaining NISQ compatibility.
- [inferred] Develop and benchmark realistic noise-aware simulations and error mitigation strategies to determine practical algorithm rankings under NISQ constraints.
- [inferred] Explore application-specific implementations (financial derivatives pricing, risk metrics) to identify problem instances where QAE variants can realistically provide advantage.
## Key ideas
- #idea:quantum-advantage — In 3-qubit Qiskit Aer simulations, QAE variants produced error-scaling exponents near 1 (MLAE ≈ -0.974, IQAE ≈ -0.971, standard QAE ≈ -1.267) vs classical MHMC ≈ -0.485, supporting potential quadratic improvement in this small-scale benchmark.
- #idea:hybrid-approach — MLAE and IQAE leverage classical postprocessing/iterative routines; MLAE uses a maximum-likelihood fit over collected counts and provides the best observed trade-off between circuit depth and estimation precision.
- #idea:near-term-feasibility — The paper argues MLAE is the most NISQ-friendly among tested methods because it attains good precision with shallower individual circuits; IQAE may require deeper single circuits for comparable error.
- #limitation:qubit-count — Experiments are limited to n = 3 qubits (8 discretization points), so conclusions about performance on realistic, high-dimensional integrals or financial Monte Carlo are limited.
- #limitation:simulation-only — All experiments were performed on a Qiskit Aer local simulator; no noisy-device or real-QPU validation is provided.
- #limitation:no-empirical-validation — No public code or repository is provided and exact experimental parameters (e.g., bmax) are not published, reducing reproducibility.
- #limitation:data-encoding — The study uses controlled-Y rotations for analytic function encoding on a tiny register; the practical cost and scalability of data/function encoding for real-world integrands are not explored.
## Contradictions
<!-- Step 6 output — where this paper contradicts others -->

## Notable quotes
<!-- Researcher-added — verbatim quotes with page references -->

## Researcher notes
<!-- Researcher-added — not LLM generated -->
