---
aliases:
- 'Continual Quantum Architecture Search with Tensor-Train Encoding: Theory and Applications
  to Signal Processing'
- Continual Quantum Architecture Search
authors:
- Jun Qi
- Chao-Han Huck Yang
- Pin-Yu Chen
- Javier Tejedor
- Ling Li
- Min-Hsiu Hsieh
auto_detected: true
classification: ''
contradiction_flags: []
doi: ''
evaluation_type: real-hardware
evidence_type: ''
has_quantitative_results: true
idea_tags:
- idea:quantum-advantage
- idea:near-term-feasibility
- idea:hybrid-approach
journal_or_venue: arXiv preprint (arXiv:2601.06392v1)
methodology_tags:
- variational-nisq
- quantum-ml
- hybrid-quantum-classical
- error-mitigation
paper_type: ''
quantum_advantage_claim: not-applicable
related_papers: []
relevance_phase1: high
relevance_phase3: high
source_type: preprint
source_type_confidence: high
step1_date: '2026-04-14T09:42:50.848621'
step1_model: gpt-5-mini
step2_date: '2026-04-14T09:42:50.848621'
step2_model: gpt-5-mini
step3_date: '2026-04-14T09:42:50.848621'
step3_model: gpt-5-mini
step4_date: '2026-04-14T09:42:50.848621'
step4_model: gpt-5-mini
step5_date: '2026-04-14T09:42:50.848621'
step5_model: gpt-5-mini
step6_date: '2026-04-14T09:42:50.848621'
step6_model: gpt-5-mini
steps_completed:
- 1
- 2
- 3
- 4
- 5
- 6
tags:
- topic/quantum-ml-finance
- method/variational-nisq
- method/quantum-ml
- method/hybrid-quantum-classical
- method/error-mitigation
- idea/quantum-advantage
- idea/near-term-feasibility
- idea/hybrid-approach
title: 'Continual Quantum Architecture Search with Tensor-Train Encoding: Theory and
  Applications to Signal Processing'
topic_tags:
- quantum-ml-finance
year: '2026'
zotero_key: ''
---

## Abstract summary
This preprint introduces CL-QAS, a continual-learning framework for variational quantum circuits that combines Tensor-Train (TT) amplitude encoding, a bi-loop quantum architecture search driven by a transformer-based reinforcement learning policy, and Elastic Weight Consolidation to mitigate costly encoding and catastrophic forgetting. The authors provide theoretical bounds on approximation, trainability, generalization, and robustness to quantum noise, and empirically demonstrate improved performance and noise resilience on ECG classification and financial time-series forecasting, including experiments on IBM hardware.
## Methodology
The paper proposes CL-QAS, a continual quantum architecture search framework combining Tensor-Train (TT) amplitude encoding, a variational quantum circuit (VQC) classifier, and a transformer-based reinforcement-learning policy for architecture search. High-dimensional classical inputs are compressed via TT decomposition (TT-SVD) into low-rank amplitude encodings that produce normalized qubit product states. A parameterized VQC consisting of layers of single-qubit RX/RY/RZ rotations and nearest-neighbor CNOT entanglers processes the encoded states and outputs Pauli-Z expectation values that are converted to class probabilities via a softmax. Training uses a bi-loop scheme: an inner loop optimizes circuit parameters θ for a fixed architecture Am using cross-entropy loss (Adam optimizer), and an outer loop adapts the architecture via a policy πϕ (REINFORCE) that receives validation accuracy penalized for entanglement (CNOT count). Continual-learning stability is enforced using Elastic Weight Consolidation (EWC) on the policy parameters and a KL divergence term to a prior policy. Theoretical analysis derives bounds on TT fidelity, trainability (gradient variance), PAC-Bayes generalization for the policy, and robustness to depolarizing/readout noise. Empirical evaluation includes simulated-noise and real-hardware experiments on IBM’s Heron r2 (156-qubit) processor, comparing CL-QAS against Naive-VQC, QAS-No-CL, TTN+VQC, and Differential QAS baselines using metrics (accuracy, balanced accuracy, F1, reward) averaged over sequential tasks and random seeds.

**Algorithms used:** Variational Quantum Circuit (VQC), Tensor-Train (TT) amplitude encoding / TT-SVD, Quantum Architecture Search (QAS) via Reinforcement Learning (REINFORCE), Transformer-based policy network for architecture proposal, Elastic Weight Consolidation (EWC), REINFORCE policy gradient, Adam optimizer

**Experimental setup:** Simulations with injected quantum noise (single-qubit depolarizing p1=0.1%, two-qubit Pauli p2=0.1%, readout flips pr=1%) and real-device runs on IBM Heron r2 (156-qubit superconducting QPU). VQC models use 20 qubits for the ECG and financial experiments, 6-layer circuits of RX/RY/RZ and CNOT entanglers, 1024 measurement shots per circuit evaluation. Training: Adam (lr=3e-3), batch size 128, 100 epochs. Architecture search uses a Transformer policy trained with REINFORCE, reward = validation accuracy − α*(CNOT penalty). Results averaged over 8 sequential tasks and 5 random seeds.

**Dataset:** Synthetic financial time-series dataset: ~6,000 simulated closing prices partitioned into 6 market regimes (regime shifts). For each decision point, 8 technical indicators are computed and the most recent 32 steps are stacked to form a 256-dimensional feature vector; label is next-step direction (up/down). Data are split chronologically into 8 sequential tasks (non-overlapping windows) and within each task a chronological 80% train / 10% validation / 10% test split is used. Features normalized with a robust median-based scaler. (Paper also uses ECG data from MIT-BIH for additional experiments.)
## Experiment details
### Input
{'source': 'Synthetic generator (autoregressive-like process) for financial time-series; ECG data from MIT-BIH Arrhythmia Database (PhysioNet) for separate experiments', 'size': 'Approximately 6,000 simulated closing-price steps (financial). Data partitioned into 8 sequential tasks (market regimes). Each sample: 256-dimensional vector (8 indicators × 32 time steps).', 'preprocessing': 'Compute 8 technical indicators per timestep (returns, rolling mean/volatility, RSI, MACD components, momentum, Bollinger-band z-scores). Stack recent 32 steps to form 256-dim vector. Robust median-based scaling for normalization. Chronological 80/10/10 split within each regime for train/validation/test. For TT encoder, factorization modes (e.g., (4,16,4) → (5,2,2) in examples) and TT-ranks used (e.g., (1,2,3,1)).'}

### Process
{'pipeline_steps': ['Generate or load time-series data; compute 8 indicators and stack 32-step windows to form 256-dim inputs', 'Normalize features using robust median-based scaling', 'Factorize input vector using Tensor-Train decomposition (TT-SVD) to specified mode shapes and TT-ranks to produce amplitude-encoding angles', 'Prepare a 20-qubit product state from TT-encoded amplitudes', 'Construct a VQC with L layers (6 in experiments) of parameterized RX/RY/RZ rotations and nearest-neighbor CNOT entanglers; measurement in Z basis yields expectation vector', 'Inner loop: for a fixed architecture Am, optimize circuit parameters θ by minimizing cross-entropy loss using Adam (lr=3e-3), batch size=128, epochs=100; use 1024 shots per circuit evaluation', 'Outer loop: architecture policy πϕ (Transformer) proposes architectures Am; evaluate candidate Am by training VQC inner loop and computing validation accuracy; compute reward = validation accuracy − entanglement penalty', 'Update policy parameters ϕ using REINFORCE with detached rewards, with EWC penalty (Fisher diagonal) and KL divergence to prior added to policy loss', 'Repeat bi-loop optimization across sequential tasks; enforce continual-learning regularization to mitigate forgetting'], 'key_parameters_used_in_run': {'TT_ranks_example': '(1,2,3,1)', 'TT_modes_example': '(4,16,4) or (5,2,2) depending on factorization', 'circuit_layers': 6, 'shots_per_evaluation': 1024, 'optimizer': 'Adam', 'learning_rate': 0.003, 'batch_size': 128, 'epochs': 100, 'policy_update': 'REINFORCE with EWC and KL regularization', 'reward': 'validation accuracy with mild CNOT penalty'}}

### Output
{'metrics_reported': ['Accuracy (Acc)', 'Balanced accuracy (bAcc)', 'F1-score (F1)', 'Reward (Rwd)'], 'baselines_compared': ['Naive-VQC (fixed architecture)', 'QAS-No-CL (QAS without continual regularization)', 'TTN+VQC', 'Differential QAS'], 'output_format': 'Per-task and aggregate means ± standard deviations across 8 sequential tasks and 5 random seeds; tables reporting Acc, bAcc, F1, Reward for noiseless simulation, simulated-noise, and IBM Heron r2 hardware runs'}

### Parameters
- qubits: 20
- circuit_depth_layers: 6
- shots: 1024
- optimizer: Adam
- learning_rate: 0.003
- batch_size: 128
- epochs: 100
- TT_factorization_modes_examples: ['(4,16,4)', '(5,2,2)']
- TT_ranks_example: [1, 2, 3, 1]
- noise_parameters_simulation: {'single_qubit_depolarizing_p1': '0.1%', 'two_qubit_depolarizing_p2': '0.1%', 'readout_error_pr': '1%'}
- policy_regularization: {'EWC_weight_lambda': 'tunable (µ in paper for outer-loop; λ for EWC definition)', 'KL_weight_beta': 'tunable (β)'}
- measurement_count_per_eval: 1024
- number_of_tasks: 8
- random_seeds: 5

### Hardware
{'simulator': 'No specific simulator name provided; simulations with injected noise reported', 'qpu_model': 'IBM Heron r2 (156-qubit superconducting processor, tunable-coupler architecture)', 'cloud_provider': 'IBM (Heron r2)'}

### Reproducibility
Authors provided a GitHub repository link for CL-QAS implementation: https://github.com/jqi41/CL_QAS. ECG data are publicly available from MIT-BIH via PhysioNet (https://physionet.org/content/mitdb/1.0.0/). The financial dataset is synthetically generated by the authors (approximately 6,000 steps); generation procedure and preprocessing details are described in the Methods. Hyperparameters (Adam lr=3e-3, batch=128, epochs=100, shots=1024, TT ranks/modes examples, circuit layers=6) are reported, and noise-model parameters are specified, supporting reproducibility given access to code and random seeds.
## Findings
- [speculative] CL-QAS is a continual quantum architecture search framework that integrates Tensor-Train (TT) amplitude encoding, a bi-loop (inner/outer) quantum architecture search driven by a transformer-based RL policy, and Elastic Weight Consolidation (EWC) to mitigate catastrophic forgetting.
- [speculative] TT-based amplitude encoding compresses high-dimensional inputs into low-rank tensor-train representations, reducing memory/state-preparation cost from O(2^U) to O(U r^2) and enabling a fidelity-compression trade-off controlled by TT-rank r (Theorem 1).
- [speculative] The authors derive theoretical upper bounds on approximation (TT fidelity), trainability (gradient-variance), generalization (PAC-Bayes style combined inner/outer bound), and robustness to quantum noise for CL-QAS (Theorems 1–4 and supporting lemmas).
- [supported] In simulation experiments on an ECG classification benchmark (8 sequential tasks), CL-QAS outperforms a fixed-architecture VQC (Naive-VQC) and a QAS without continual regularization (QAS-No-CL) on averaged metrics (e.g., mean F1: CL-QAS 0.819 vs Naive-VQC 0.741 and QAS-No-CL 0.748 under noiseless simulation).
- [supported] Under simulated noise (0.1% depolarizing, 0.1% two-qubit Pauli, 1% readout error), CL-QAS retains higher robustness than the baselines on ECG tasks (reported mean F1 0.729 for CL-QAS vs 0.713 and 0.688 for baselines).
- [supported] On real IBM Heron r2 hardware for ECG tasks, CL-QAS achieved higher reported mean performance than TTN+VQC and Differential QAS (e.g., Acc = 0.863 ± 0.008, bAcc = 0.900 ± 0.060, F1 = 0.496 ± 0.009).
- [supported] On a synthetic-realistic financial time-series benchmark (8 sequential regimes), CL-QAS achieves the best reported average metrics versus Naive-VQC and QAS-No-CL in simulation (e.g., mean Acc ~0.604, bAcc ~0.604, F1 ~0.624).
- [supported] Under noisy simulation and on IBM Heron r2 hardware for financial tasks, CL-QAS retains better or comparable performance than TTN+VQC and Differential QAS (hardware: Acc = 0.607 ± 0.015, bAcc = 0.607 ± 0.011, F1 = 0.624 ± 0.019 reported for CL-QAS).
- [supported] An ablation study reported that TT encoding improved ECG classification performance and reduced runtime slightly (CL-QAS with TT: Acc 0.932 ± 0.015, F1 0.729 ± 0.041, runtime 38.0 ± 6.0s; without TT: Acc 0.922 ± 0.009, F1 0.714 ± 0.053, runtime 43.5 ± 6.8s under noisy simulation).
- [speculative] Theoretical analysis claims CL-QAS mitigates barren-plateau-like exponential gradient vanishing by yielding polynomially-bounded gradients scaling like O(1/|Dm|) + O(1/r^2) under stated assumptions (Theorem 2, Corollary 1).
- [speculative] The authors claim objective-level robustness bounds under a noise model combining single- and two-qubit depolarizing channels, readout flips and encoder jitter (Theorem 4), producing additive bounds on loss degradation.
- [speculative] The bi-loop separation (inner-loop parameter training / outer-loop architecture policy adaptation) combined with EWC stabilizes architecture updates across sequential tasks (Lemma 1 and policy regularization formulations).
- [speculative] CL-QAS is presented as a practical approach for adaptive, noise-resilient quantum learning on near-term NISQ devices and as a bridge between tensor-network encoders and quantum feature maps.

**Results summary:** The preprint proposes CL-QAS, a continual-learning quantum framework combining Tensor-Train amplitude encoding, reinforcement-learning-driven quantum architecture search, and Elastic Weight Consolidation. The authors present theoretical bounds on fidelity (TT approximation), trainability (gradient variance), generalization (PAC-Bayes style outer-loop + inner-loop bounds), and robustness to a composite noise model. Empirically, on simulated ECG classification and synthetic financial time-series forecasting (both framed as sequences of tasks), CL-QAS outperformed fixed-architecture VQCs and a QAS without continual regularization in averaged accuracy, balanced accuracy, F1, and task reward, and maintained performance under simulated noise. Hardware experiments on IBM's Heron r2 device report CL-QAS beating TTN+VQC and Differential QAS on the reported metrics. Ablation studies indicate TT encoding contributes to performance and runtime improvements. Theoretical claims and empirical results together are used to argue for improved scalability, stability, and noise resilience for continual quantum learning in NISQ settings.

**Performance claims:**
- ECG (noiseless simulation, averaged over 8 sequential tasks): CL-QAS mean F1 = 0.819 vs Naive-VQC 0.741 ± 0.052 and QAS-No-CL 0.748 ± 0.045.
- ECG (noisy simulation: 0.1% depolarizing, 0.1% two-qubit Pauli, 1% readout): CL-QAS mean Acc = 0.932 ± 0.015, bAcc = 0.936 ± 0.012, F1 = 0.729 ± 0.041 vs Naive-VQC F1 = 0.713 ± 0.048 and QAS-No-CL F1 = 0.688 ± 0.058.
- ECG (IBM Heron r2 hardware): CL-QAS Acc = 0.863 ± 0.008, bAcc = 0.900 ± 0.060, F1 = 0.496 ± 0.009, Reward = 0.7674 ± 0.0018; TTN+VQC: Acc = 0.846 ± 0.011, bAcc = 0.881 ± 0.070, F1 = 0.481 ± 0.012; Differential QAS: Acc = 0.822 ± 0.012, bAcc = 0.878 ± 0.080, F1 = 0.437 ± 0.010.
- Ablation (ECG, noisy simulation): CL-QAS with TT: Acc = 0.932 ± 0.015, F1 = 0.729 ± 0.041, Runtime = 38.0 ± 6.0s; CL-QAS without TT: Acc = 0.922 ± 0.009, F1 = 0.714 ± 0.053, Runtime = 43.5 ± 6.8s.
- Financial (noiseless simulation, averaged over 8 tasks): CL-QAS mean Acc = 0.604 ± 0.063, bAcc = 0.604 ± 0.070, F1 = 0.624 ± 0.063, Reward = 0.6054 ± 0.0622 vs Naive-VQC mean Acc = 0.592, bAcc = 0.587, F1 = 0.549.
- Financial (noisy simulation): CL-QAS mean Acc = 0.637 ± 0.110, bAcc = 0.641 ± 0.096, F1 = 0.618 ± 0.168, Reward = 0.6395 ± 0.0882.
- Financial (IBM Heron r2 hardware): CL-QAS Acc = 0.607 ± 0.015, bAcc = 0.607 ± 0.011, F1 = 0.624 ± 0.019, Reward = 0.6067 ± 0.0118; TTN+VQC: Acc = 0.562 ± 0.012, bAcc = 0.587 ± 0.012, F1 = 0.529 ± 0.017.
## Quantum advantage claim
**Classification:** not-applicable

The paper reports improvements of CL-QAS over other variational-quantum baselines (Naive-VQC, QAS-No-CL, TTN+VQC, Differential QAS) in simulation and on IBM hardware, and presents theoretical bounds on trainability and robustness. However, it does not claim or demonstrate a computational or predictive advantage over classical machine learning methods; therefore no claim of a broader quantum advantage is demonstrated.
## Limitations
- Theoretical analysis is limited: it does not explicitly incorporate stochastic quantum-noise models and imperfect measurements (author-stated).
- Empirical scope focused on two domains (ECG classification and financial time-series forecasting); broader domain validation is lacking (author-stated).
- Financial experiments rely on a synthetic financial dataset rather than large-scale proprietary/real market data, which limits assessment of real-world market complexities (author-stated).
- Hardware evaluation is limited to experiments on a single IBM Heron r2 device and mid-scale circuits; scalability to larger qubit systems and diverse hardware is not demonstrated (author-stated).
- The TT-based amplitude encoding introduces a fidelity–compression trade-off governed by TT-rank; selecting appropriate rank incurs a computational/expressivity compromise (author-stated implication).
- [inferred] The reinforcement-learning outer loop uses REINFORCE-style updates, which are known to have high variance and can be sample-inefficient, potentially limiting policy search efficiency.
- [inferred] The bi-loop (inner/outer) optimization—optimizing VQC parameters per candidate architecture—can be computationally expensive, especially as the architecture search space or task count grows.
- [inferred] The noise model used (single/two-qubit depolarizing plus symmetric readout flips and encoder jitter) is simplified; non-Markovian, time-varying, or correlated noise effects are not addressed.
- [inferred] The evaluation lacks comparisons against strong classical baselines (classical ML models) for the same tasks, so relative classical vs quantum advantage is unclear.
- [inferred] The continual-learning regularizer used (EWC) is one approach among many; its limits in complex, highly non-stationary task sequences (e.g., many more tasks, large distribution shifts) are not fully characterized.
- [inferred] The financial prediction task setup (binary next-step direction) is a simplified objective and does not account for transaction costs, slippage, multi-step horizons, or risk-adjusted returns, limiting direct trading applicability.
- [inferred] Hyperparameter sensitivity (EWC weight, KL weight, TT ranks, policy reward shaping) and their tuning cost across tasks are not fully explored.
## Open questions
- How does CL-QAS perform under more realistic, stochastic, and possibly non-Markovian quantum noise models and imperfect measurements?
- How well does the framework scale to larger qubit counts, deeper circuits, and more complex (mixed-state) datasets?
- What are the practical computational and sample-efficiency costs of the bi-loop architecture search in larger search spaces or with many sequential tasks?
- How sensitive are the fidelity–trainability trade-offs (TT-rank vs dataset size) in practice across diverse real-world datasets?
- Can CL-QAS generalize to other application domains beyond ECG and the particular financial forecasting setup studied?
- How do EWC and KL regularization hyperparameters interact with policy learning to control catastrophic forgetting in long task sequences?
- What is the relationship between curvature-based continual-learning regularization (EWC-like) and quantum natural gradient methods — can they be unified or combined for improved stability?
- Can meta-learning or federated quantum update strategies be effectively incorporated into CL-QAS to enable distributed or faster adaptation across heterogeneous devices?
- How robust and transferable are the learned circuit architectures across different hardware backends with distinct connectivity and noise characteristics?
- To what extent do the learned quantum circuits offer practical advantages over classical methods for financial tasks when accounting for realistic constraints (latency, costs, risk metrics)?
- How interpretable are the architectures discovered by the transformer-based policy and can their structure be related to task characteristics?

**Future work:**
- Extend the theoretical analysis to incorporate stochastic quantum-noise models and imperfect measurements explicitly (author-stated).
- Empirically evaluate CL-QAS on larger qubit systems, mixed-state datasets, and additional real quantum hardware to clarify practical scalability (author-stated).
- Integrate meta-learning or federated quantum updates to enable distributed continual adaptation across heterogeneous devices (author-stated).
- Investigate theoretical and practical connections between curvature-based continual learning and quantum natural gradient methods to exploit parameter manifold geometry for improved convergence and stability (author-stated).
- Explore expanding empirical validation to more domains and more realistic financial setups (longer horizons, transaction costs, risk-adjusted objectives) (inferred/author-suggested).
## Key ideas
- #idea:hybrid-approach — CL-QAS: a hybrid bi-loop quantum-classical architecture search combining a Transformer-based REINFORCE policy (outer loop) with classical optimization of VQC parameters (inner loop).
- #idea:quantum-advantage — Empirical claims of improved classification and forecasting accuracy (Acc, bAcc, F1, Reward) versus Naive-VQC, QAS-No-CL, TTN+VQC and Differential QAS on simulated financial time-series, including runs on IBM Heron r2.
- #idea:near-term-feasibility — Demonstrated NISQ-era applicability: TT amplitude encoding compresses 256-dim inputs into 20-qubit product states and 6-layer VQCs with 1024 shots; experiments include simulated noise and real 156-qubit IBM hardware (using 20 qubits).
- #idea:hybrid-approach — Tensor-Train (TT) amplitude encoding (TT-SVD) is used to reduce encoding cost and qubit requirements for high-dimensional financial features.
- #idea:quantum-advantage — The paper provides theoretical bounds (TT fidelity, gradient variance/trainability, PAC-Bayes generalization for the policy, and robustness to depolarizing/readout noise) to support empirical findings.
- #idea:hybrid-approach — Continual-learning regularization (Elastic Weight Consolidation and KL to prior) is integrated into the architecture search policy to mitigate catastrophic forgetting across sequential market-regime tasks.
## Contradictions
<!-- Step 6 output — where this paper contradicts others -->

## Notable quotes
<!-- Researcher-added — verbatim quotes with page references -->

## Researcher notes
<!-- Researcher-added — not LLM generated -->
