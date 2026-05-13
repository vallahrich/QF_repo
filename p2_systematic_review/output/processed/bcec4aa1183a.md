---
aliases:
- A Scalable Quantum Machine Learning Methodology Design for Handling Large-Scale
  Data Classification and Optimization Principle
- Scalable Quantum Machine Learning
authors:
- M.S. Mohamed Mallick
- D. David Neels Ponkumar
- Sivaneasan Bala Krishnan
- Prasun Chakrabarti
- M.S. S. Sasikumar
auto_detected: true
classification: ''
contradiction_flags:
- contradiction:scalability
- contradiction:classical-vs-quantum
doi: 10.1109/ICONSTEM65670.2025.11374683
evaluation_type: real-hardware
evidence_type: ''
has_quantitative_results: true
idea_tags:
- idea:quantum-advantage
- idea:near-term-feasibility
- idea:hybrid-approach
journal_or_venue: Tenth International Conference on Science Technology Engineering
  and Mathematics (ICONSTEM), 2025
methodology_tags:
- variational-nisq
- quantum-ml
- hybrid-quantum-classical
- error-mitigation
paper_type: ''
quantum_advantage_claim: demonstrated
related_papers: []
relevance_phase1: medium
relevance_phase3: high
source_type: conference-paper
source_type_confidence: high
step1_date: '2026-04-14T11:40:33.757288'
step1_model: gpt-5-mini
step2_date: '2026-04-14T11:40:33.757288'
step2_model: gpt-5-mini
step3_date: '2026-04-14T11:40:33.757288'
step3_model: gpt-5-mini
step4_date: '2026-04-14T11:40:33.757288'
step4_model: gpt-5-mini
step5_date: '2026-04-14T11:40:33.757288'
step5_model: gpt-5-mini
step6_date: '2026-04-14T11:40:33.757288'
step6_model: gpt-5-mini
steps_completed:
- 1
- 2
- 3
- 4
- 5
- 6
tags:
- method/variational-nisq
- method/quantum-ml
- method/hybrid-quantum-classical
- method/error-mitigation
- idea/quantum-advantage
- idea/near-term-feasibility
- idea/hybrid-approach
- contradiction/scalability
- contradiction/classical-vs-quantum
title: A Scalable Quantum Machine Learning Methodology Design for Handling Large-Scale
  Data Classification and Optimization Principle
topic_tags: []
year: '2025'
zotero_key: ''
---

## Abstract summary
The paper presents a hybrid, scalable quantum machine learning methodology that combines amplitude encoding, parameterized quantum circuits, entanglement optimization, and classical RMSProp-based variational training, with quantum error mitigation (including zero-noise extrapolation) for NISQ devices. Experiments on 16-qubit processors using Qiskit and PennyLane report a mean classification accuracy of 96.42% (about 5% better than classical baselines), improved fidelity (~0.93) after mitigation, and demonstrated scalability to datasets of up to 10,000 samples with sub-linear time growth.
## Methodology
The paper proposes a hybrid quantum-classical scalable QML framework for large-scale data classification. Classical feature vectors are normalized and encoded into quantum states using amplitude encoding to exploit exponential compression. Parameterized Quantum Circuits (PQCs) act as trainable quantum feature mappers; entanglement layers are adaptively tuned to balance expressiveness and noise sensitivity. A quantum kernel (inner products of quantum states) is used to improve high-dimensional similarity measurement. Training follows a Variational Quantum Algorithm (VQA) loop: measure observables from the PQC, compute a quantum loss, evaluate gradients via the parameter-shift rule, and update parameters with a classical optimizer (RMSProp). Quantum Batch Partitioning (QBP) is used to split large datasets into smaller quantum-encodable batches enabling parallel execution and adaptive qubit utilization. Noise and error mitigation strategies (Quantum Error Mitigation, Zero-Noise Extrapolation and mentions of ICQEM) are applied to improve fidelity on NISQ hardware. The workflow is given as an algorithm: initialize PQC, amplitude-encode inputs, apply U(theta), measure observable O to get fq(x), compute loss Lq(theta), compute gradients and update theta, integrate QEM/ZNE, iterate until convergence, then classify test data with optimized parameters. Experiments report up to 16 qubits, dataset sizes up to 10,000 samples, fidelity improvements from ~0.856 to ~0.927 after mitigation, and mean classification accuracy of 96.42% compared to classical baselines.

**Algorithms used:** Variational Quantum Algorithm (VQA), Quantum kernel methods (state inner-product kernels), Amplitude encoding (quantum feature mapping), Parameter-shift rule for gradient estimation, Hybrid RMSProp optimizer (classical), Zero-Noise Extrapolation (ZNE), Quantum Error Mitigation (QEM), Entanglement-layer adaptive optimization, Quantum Batch Partitioning (QBP)
**Frameworks:** Qiskit, PennyLane

**Experimental setup:** Reported experiments run on 16-qubit NISQ processors using Qiskit and PennyLane frameworks. Datasets of sizes ranging 1,000 to 10,000 samples were processed via amplitude encoding and PQCs. Training used hybrid quantum-classical VQA loops with gradient estimation via parameter-shift and RMSProp optimizer; error mitigation (ZNE/QEM) applied with noise scaling factors up to 2.8. Execution times per trial ~23–28 seconds as reported.
## Experiment details
### Input
{'source': 'not specified in paper', 'size_range': '1,000 to 10,000 samples (experiments reported at increments up to 10,000)', 'preprocessing': 'Normalization of classical feature vectors and amplitude encoding into quantum states; data partitioned into quantum batches via Quantum Batch Partitioning (QBP). No further dataset provenance or feature descriptions provided.'}

### Process
{'pipeline_steps': ['Initialize parameterized quantum circuit (PQC) with random parameters theta_0 and define quantum loss Lq(theta).', 'Normalize classical input x_i and amplitude-encode into quantum state |psi_x>.', 'Apply quantum feature mapping/unitary U(theta) (PQC) including entangling layers; entanglement configuration adaptively tuned based on performance.', 'Measure observable O to compute model output f_q(x) = <psi|O|psi>.', 'Compute loss Lq(theta) as average over dataset (classification loss).', 'Estimate gradients using the parameter-shift rule from measurement statistics.', 'Update parameters using classical optimizer (RMSProp): theta_{t+1} = theta_t - eta * grad.', 'Apply Quantum Error Mitigation and Zero-Noise Extrapolation by running circuits at amplified noise levels and extrapolating to zero-noise.', 'Repeat steps for iterative VQA loop until convergence or max iterations (reported up to 100).', 'Classify unseen test data with optimized PQC parameters.'], 'iterations': 100, 'optimizer': 'RMSProp', 'gradient_method': 'parameter-shift rule', 'noise_mitigation': 'ZNE and QEM with multiple noise-scaling factors'}

### Output
{'metrics_reported': ['Classification accuracy (QML mean 96.42%)', 'Improvement vs classical baselines (approx. +5% average)', 'Execution time per trial (approx. 23–28 s)', 'Qubit utilization percentage (reported 65% to 89%)', 'Fidelity before/after mitigation (avg before ~0.856, after ~0.927)', 'Convergence metrics: quantum loss vs classical loss over iterations, convergence rate (~24.6%)', 'Robustness vs noise levels (accuracy reported across noise p in 0.005–0.05)'], 'baselines': 'Classical neural and kernel-based models (exact architectures not specified), classical accuracy values listed per trial in Table 1', 'output_format': 'Aggregated metrics/tables (accuracy, time, fidelity, qubit utilization) and plots showing scaling and convergence'}

### Parameters
- qubits_used: 8–16 (experiments report adaptive usage; max 16 qubits)
- circuit_depth: constrained (D_c <= D_max) but exact numerical circuit depth not specified
- shots: None
- optimizer: RMSProp (classical)
- iterations: 100
- learning_rate: None
- noise_scaling_factors: [1, 1.2, 1.4, 1.6, 1.8, 2, 2.2, 2.4, 2.6, 2.8]
- fidelity_before_avg: 0.856
- fidelity_after_avg: 0.927
- execution_time_range_seconds: approx. 23.1 to 28.0 s depending on noise/qubit usage
- dataset_sizes_tested: [1000, 2000, 3000, 4000, 5000, 6000, 7000, 8000, 9000, 10000]

### Hardware
{'simulator_name': None, 'qpu_model': '16-qubit NISQ processors (model/vendor not specified)', 'cloud_provider': None, 'frameworks': ['Qiskit', 'PennyLane']}

### Reproducibility
No code repository, dataset links, or explicit circuit descriptions (gate-level circuits, exact PQC templates, shot counts, learning rates) are provided in the paper. While high-level algorithmic steps, iteration counts, noise-scaling factors and some aggregated results are reported, missing low-level experimental details (exact datasets, feature dimensions, PQC layer structure, random seeds, optimizer hyperparameters, number of measurement shots) make exact reproduction difficult.
## Findings
- [supported] The authors implemented a hybrid scalable QML pipeline (amplitude encoding + parameterized quantum circuits + classical RMSProp optimization) and ran experiments using Qiskit and PennyLane on 16-qubit NISQ processors.
- [supported] The proposed QML model achieved a reported mean classification accuracy of 96.42%, outperforming the compared classical baselines by an average ≈5.2 percentage points in the presented trials.
- [supported] Execution times reported for the QML experiments (~23–26 s per trial) are comparable to the classical baselines in the authors' experiments (i.e., similar computation efficiency in their setup).
- [supported] Quantum error mitigation (QEM) and zero-noise extrapolation (ZNE) raised measured fidelity from an average ~0.856 before mitigation to ~0.927 after mitigation (≈8% improvement) in the reported trials.
- [supported] The authors present results showing the approach retains high accuracy under increasing dataset sizes up to 10,000 samples while reporting lower runtime growth than the classical baseline in their experiments (QML time at 10,000 samples = 58.1 s vs classical = 140.8 s).
- [supported] Reported qubit utilization increased with dataset size in the experiments (65% → 89% across 1k→10k samples), indicating adaptive resource use in their implementation.
- [supported] Variational training results in the paper show quantum loss decreasing from 0.231 to 0.131 across 100 iterations with lower gradient variance (0.042 → 0.023), which the authors interpret as steadier/faster convergence under their RMSProp-based optimization.
- [supported] Robustness tests reported accuracy remaining above ~92% even at higher simulated noise levels (e.g., 92.38% at p=0.05) in the authors' experiments.
- [speculative] The paper claims that quantum kernel methods and entanglement-optimized circuits 'drastically' enhance high-dimensional similarity measurement and expressiveness — the paper reports improved accuracy but does not rigorously quantify or isolate the causal contribution of entanglement/configuration choices across baselines.
- [speculative] The authors claim sub-linear scalability due to 'quantum parallelism' (Quantum Batch Partitioning) for large datasets; the presented timing data shows significantly lower growth than the classical baseline in their setup, but the general claim of sub-linear scaling is not proven theoretically and depends on many implementation details.
- [disputed] The paper states amplitude encoding 'allows compression of data exponentially' and implies this is an unqualified efficiency gain. This ignores well-known costs of state preparation (and data-loading) and is therefore a misleading blanket claim when contrasted with standard literature.
- [speculative] The paper projects applicability and benefits of the proposed QML methodology across domains such as bioinformatics, finance, and IoT analytics; these domain-general claims are prospective and not validated in the presented experiments.
- [speculative] The authors suggest that small-scale quantum circuits with few qubits can learn and classify large-scale datasets efficiently in general; this is an aspirational claim supported by their experimental setup but remains dependent on data-loading costs, problem structure, and hardware specifics.

**Results summary:** The conference paper presents a hybrid quantum-classical classification pipeline implemented on 16-qubit NISQ hardware (Qiskit/PennyLane). Empirical results in the paper report a mean QML classification accuracy of 96.42%, about 5 percentage points higher than the classical baselines used by the authors, with similar per-trial execution times (~23–26 s). The authors further report that error mitigation (ZNE/QEM) raised fidelity from ~0.856 to ~0.927, that qubit utilization scaled from 65% to 89% when moving from 1k to 10k samples, and that the QML runtime grew much less steeply than the classical baseline in their experiments (QML: 10.8 s → 58.1 s for 1k→10k samples vs classical: 12.3 s → 140.8 s). Variational training showed reduced quantum loss and lower gradient variance across iterations. The paper also advances broader claims about entanglement/quantum-kernel expressiveness, sub-linear scalability via quantum parallelism, and cross-domain applicability; these are more speculative or depend on assumptions about data-loading and hardware.

**Performance claims:**
- Mean classification accuracy (QML) = 96.42%
- Average improvement over classical baselines ≈ 5.2 percentage points
- Per-trial execution time (QML) ≈ 23–26 s (comparable to classical in their experiments)
- Fidelity before mitigation (avg) ≈ 0.856; fidelity after mitigation (avg) ≈ 0.927 (≈8% improvement)
- Scaling experiment (dataset size → QML time): 1,000 → 10.8 s; 2,000 → 18.9 s; 3,000 → 25.6 s; ...; 10,000 → 58.1 s
- Scaling experiment (dataset size → classical time): 1,000 → 12.3 s; ...; 10,000 → 140.8 s
- Qubit utilization reported from 65% (1k samples) up to 89% (10k samples)
- Variational loss (quantum) decreased from 0.231 to 0.131 over 100 iterations
- Reported convergence rate peak ~24.6% and gradient variance reduced to ~0.023
- Robustness: accuracy 96.42% at noise level p=0.005 (8 qubits used); accuracy 92.38% at noise level p=0.05 (16 qubits used)
## Quantum advantage claim
**Classification:** demonstrated

The paper reports empirical improvements in classification accuracy (~96.4% vs ~91% classical) and reduced runtime growth on the tested datasets/hardware. It attributes gains to quantum feature encoding, quantum kernels/entanglement, and error mitigation. The advantage is demonstrated within the authors' experimental setup (16-qubit NISQ, specific datasets, and implementation choices), but broader claims (e.g., exponential compression via amplitude encoding or universal sub-linear scaling) remain speculative or contested in the wider literature.
## Limitations
- Dependence on NISQ-era hardware: performance constrained by decoherence, gate noise and limited qubit counts (author-stated).
- Need for shallow circuits and hardware-aware ansatzes due to NISQ limitations; deep circuits are not feasible (author-stated).
- Entanglement trade-off: over-entanglement increases noise susceptibility and hurt interpretability; entanglement configuration must be tuned (author-stated).
- Requirement for error mitigation (QEM, ZNE) to achieve high fidelity; mitigation incurs additional circuit executions and overhead (author-stated).
- Resource constraints explicitly captured in optimization (circuit depth and qubit-number bounds) limit model expressivity (author-stated).
- [inferred] Amplitude encoding practicality: preparing amplitude-encoded states for large classical vectors can be costly in terms of gate depth and pre-processing (not detailed).
- [inferred] Scalability claims tested up to 10,000 samples and 16 qubits; generalization of sub-linear time scaling for much larger datasets or real-world deployments is not demonstrated.
- [inferred] Quantum Batch Partitioning implementation assumptions: the approach assumes the ability to encode and run many batches efficiently but practical device-level parallelism / orchestration overheads are not quantified.
- [inferred] Evaluation transparency and reproducibility: dataset details, baselines' configurations, hyperparameters, and code release are not provided, making independent validation difficult.
- [inferred] Potential classical bottlenecks: classical post-processing, feature normalization and optimizer overheads may become limiting factors as dataset sizes grow, but are not analyzed in depth.
- [inferred] Gradient estimation cost and noise sensitivity: parameter-shift gradients scale with number of parameters and are susceptible to shot noise; full cost analysis is absent.
- [inferred] Results may be dependent on simulator vs real hardware differences: while frameworks (Qiskit, PennyLane) used, the extent of experiments on real quantum hardware vs simulation is unclear.
## Open questions
- How well does the proposed QML methodology perform on real-world financial datasets (e.g., time-series, high-frequency, portfolio data) compared to both classical and other quantum baselines?
- What is the end-to-end cost (wall-clock time, number of shots, classical overhead) of the error mitigation (QEM, ZNE) pipeline on real quantum hardware at scale?
- How does the complexity of amplitude encoding (state preparation) scale in practice for very high-dimensional financial features, and are there practical alternatives (e.g., feature selection, hybrid encodings)?
- What are the precise trade-offs between entanglement depth/configuration and noise for different hardware backends, and how to automatically discover near-optimal entanglement patterns?
- How does gradient noise and variance scale with model size (number of parameters) and dataset size in realistic noisy settings, and what optimizers are most robust?
- Can the Quantum Batch Partitioning approach be implemented effectively on current cloud-accessible hardware given limited parallel quantum resources and job queuing/latency?
- How robust are the reported accuracy and fidelity gains across different noise models, hardware backends, and random seeds (statistical significance)?
- What are the privacy, security, and regulatory implications of applying federated quantum training or quantum models in financial services?
- How to integrate this QML methodology into existing classical financial pipelines (latency, throughput, failover) and what hybrid deployment architectures are practical?
- What are the requirements and challenges for scaling from 16-qubit experiments to larger superconducting or other hardware platforms in terms of calibration, error rates and control?

**Future work:**
- Multi-qubit entanglement-aware learning (author-stated).
- Federated quantum training for distributed datasets (author-stated).
- Incorporation of quantum attention mechanisms and error-resistant qubit encoders to improve generalization (author-stated).
- Combining the approach with quantum reinforcement learning for optimization in dynamic data environments (author-stated).
- Supercomputer-scale implementation on larger superconducting quantum systems and investigation of cooperation with classical deep-learning backbones in hybrid intelligence (author-stated).
## Key ideas
- #idea:hybrid-approach — Proposes a hybrid QML pipeline combining amplitude encoding, parameterized quantum circuits (PQC), quantum kernels and classical RMSProp training with parameter-shift gradient estimation.
- #idea:near-term-feasibility — Demonstrates NISQ-oriented design choices (adaptive entanglement layers, Quantum Batch Partitioning) and applies error mitigation (ZNE/QEM) to improve fidelity on 8–16 qubit processors.
- #idea:quantum-advantage — Reports empirical improvements (mean classification accuracy 96.42%, ~5% better than unspecified classical baselines) and fidelity gains (avg 0.856 → 0.927 after mitigation).
- #idea:hybrid-approach — Introduces Quantum Batch Partitioning (QBP) to split large datasets (up to 10,000 samples) into encodable batches enabling parallel execution and adaptive qubit usage.
- #limitation:noise — Shows substantial dependence on error mitigation (fidelity pre/post mitigation reported), highlighting NISQ noise sensitivity despite ZNE/QEM.
- #limitation:data-encoding — Relies on amplitude encoding and claims sub-linear scaling / exponential compression but lacks detail on data-loading costs and feature dimensionality.
## Contradictions
- Paper claims scalability to datasets up to 10,000 samples with sub-linear time growth via amplitude encoding, but provides no accounting for the classical-to-quantum data-loading cost or detailed feature-dimension scaling — a gap that contradicts the stated exponential compression advantage.
- Reported ~5% accuracy improvement over classical baselines is presented without precise descriptions of baseline architectures, hyperparameters, or statistical significance testing, which undermines the strength of the quantum-vs-classical superiority claim.
- Although experiments are described as run on 16-qubit NISQ processors, missing low-level experimental details (shot counts, exact PQC circuits, learning rates, dataset provenance and code) create a reproducibility gap that contradicts the paper's empirical claims being fully validated.
## Notable quotes
<!-- Researcher-added — verbatim quotes with page references -->

## Researcher notes
<!-- Researcher-added — not LLM generated -->
