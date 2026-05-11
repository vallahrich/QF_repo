---
aliases:
- Contextual Quantum Neural Networks for Stock Price Prediction
- Contextual Quantum Neural Networks
authors:
- Sharan Mourya
- Hannes Leipold
- Bibhas Adhikari
auto_detected: true
classification: ''
contradiction_flags:
- contradiction:scalability
- contradiction:classical-vs-quantum
doi: https://doi.org/10.1038/s41598-025-34413-5
evaluation_type: simulator
evidence_type: ''
has_quantitative_results: true
idea_tags:
- idea:quantum-advantage
- idea:near-term-feasibility
- idea:hybrid-approach
journal_or_venue: Scientific Reports
methodology_tags:
- variational-nisq
- quantum-ml
- hybrid-quantum-classical
paper_type: ''
quantum_advantage_claim: speculative
related_papers: []
relevance_phase1: high
relevance_phase3: high
source_type: peer-reviewed-empirical
source_type_confidence: high
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
- topic/quantum-ml-finance
- method/variational-nisq
- method/quantum-ml
- method/hybrid-quantum-classical
- idea/quantum-advantage
- idea/near-term-feasibility
- idea/hybrid-approach
- contradiction/scalability
- contradiction/classical-vs-quantum
title: Contextual Quantum Neural Networks for Stock Price Prediction
topic_tags:
- quantum-ml-finance
year: '2026'
zotero_key: ''
---

## Abstract summary
The paper develops contextual quantum neural networks to predict distributions of future stock returns and introduces a quantum batch gradient update (QBGU) to accelerate and improve training. It also proposes a share-and-specify ansatz for quantum multi-task learning (QMTL) that enables simultaneous training of multiple assets on a single quantum circuit with logarithmic qubit overhead; experiments on S&P 500 stocks (Apple, Google, Microsoft, Amazon) demonstrate improved convergence and better capture of inter-asset correlations versus single-task quantum models.
## Methodology
The study develops and evaluates a contextual quantum neural network (QNN) approach for short-horizon stock-return distribution prediction and a quantum multi-task learning (QMTL) architecture (share-and-specify ansatz) to train multiple assets on one circuit. Classical preprocessing converts raw prices to finite differences (returns) and applies a moving average smoothing; returns are quantized (binary by default, d=2; experiments with d=4 density-based quantization reported). The contextual distribution P(X(T)) is loaded once onto a quantum register using a hardware-efficient ansatz trained (via an MSE loss + SPSA) to approximate the amplitude-encoded state psi(T). A parametrized quantum circuit (PQC) ˆU(θ) with layered RY/RZ/CNOT blocks (L layers) and ancilla qubits is then trained to produce conditional continuation distributions. Training uses a fidelity-based loss computed with a SWAP test between the predicted and target quantum states; gradient estimates are obtained via SPSA (and parameter-shift is discussed). The authors introduce Quantum Batch Gradient Update (QBGU): by loading the entire contextual distribution in superposition the circuit's gradients correspond to the dataset-weighted sum (an effective batch/SGD update in one quantum forward), accelerating training. For multi-task learning they propose share-and-specify layers where a shared block is followed by label-controlled, task-specific blocks (control built via single-qubit controls and Toffoli gates for K>2). Experiments are simulation-based (including Qiskit AerSimulator noise tests) on S&P 500-derived stocks (Apple, Google, Microsoft, Amazon, etc.), comparing QSTL vs QMTL, studying loss curves, KL divergence between predicted and target conditional distributions, training stability, MSE vs SWAP-loss behavior, scalability to K=4 and K=8, and noise sensitivity (depolarizing and readout). Key hyperparameters reported include context sizes (T), number of layers L, shots, SPSA perturbation and learning rates; random seed and measurement counts are provided to aid reproducibility.

**Algorithms used:** Quantum Neural Network (QNN) / Parametric Quantum Circuit (PQC), Hardware-efficient ansatz (state-loading ansatz), SWAP test (fidelity loss), Simultaneous Perturbation Stochastic Approximation (SPSA), Parameter-shift rule (discussed), Quantum Batch Gradient Update (QBGU) (novel training technique), Quantum Multi-Task Learning (QMTL) with share-and-specify ansatz, Toffoli-based label-controlled gates (for multi-task control)
**Frameworks:** Qiskit (AerSimulator used for noise experiments)

**Experimental setup:** Simulation experiments using parametrized quantum circuits (hardware-efficient ansatz) and SWAP-test based fidelity loss. Main training performed in simulation with shots=10,000, SPSA optimizer (delta=0.01), random seed=42. Noise sensitivity tested on Qiskit AerSimulator using depolarizing and readout-error noise models. No physical QPU was reported.

**Dataset:** Historical S&P 500 stock price data for selected constituents (Apple, Google, Microsoft, Amazon, Pepsi, Western Digital, Texas Instruments, IBM). Primary dataset: ~10,033 raw price records (weekly-averaged with stride 1 → 10,029 samples). Split 80% train / 20% test. Preprocessing: finite-difference returns, moving-average smoothing, quantization (binary d=2 by default; also d=4 density-based quantization in experiments).
## Experiment details
### Input
Source: S&P 500 historical stock prices for named tickers. Size: ~10,033 raw records, after weekly averaging (stride 1) 10,029 samples; typical train/test split 80/20. Preprocessing steps: compute finite differences between consecutive prices (returns), apply moving-average smoothing, normalize, compute histogram to get contextual probability distribution P(X(T)), quantize returns into discrete bins (default binary: d=2 where 0=down,1=up; alternative non-uniform density-based 4-level quantization used in one experiment). Typical context window T=3 (some experiments used T=2), prediction horizon τ=1 (sequential R-step application discussed), ancilla qubits τ=1.

### Process
Pipeline: (1) Preprocess raw prices → returns → moving-average smoothing → quantize to discrete levels. (2) Compute empirical contextual distribution P(X(T)) (histogram) and prepare amplitude-encoded quantum state psi(T) via a hardware-efficient ansatz: iteratively optimize ansatz parameters using MSE loss + SPSA to approximate psi(T). (3) Construct PQC ˆU(θ) with L layered blocks (shared and task-specific in QMTL) acting on context qubits + ancilla + label qubits. (4) Preload target distribution psi(T+1) (for supervised loss) on target qubits. (5) Evaluate SWAP test between predicted and target states to obtain fidelity-based loss. (6) Compute gradients via SPSA (or parameter-shift) and update θ. For QBGU, load entire contextual distribution in superposition so a single forward corresponds to dataset-weighted gradient (batch update). (7) For QMTL use share-and-specify ansatz: shared block then label-controlled task blocks (controls implemented via X and Toffoli gates for K>2). (8) Training regimes: context/state-loading trained 3000 epochs; QSTL training 3000 epochs; QMTL trained sequentially per asset (e.g., 250 epochs per asset for K=2/4; 100 epochs per asset for K=8). (9) Evaluation: compare predicted conditional distributions to empirical targets via KL divergence, plot loss curves, test MSE-loss vs SWAP-test loss, and run noise sensitivity experiments on AerSimulator measuring KL divergence vs noise probability.

### Output
Outputs include learned quantum states representing conditional continuation distributions and sampled continuation outcomes. Reported metrics: fidelity-based training loss (from SWAP test) and KL divergence between predicted and target conditional distributions. Comparisons/baselines: quantum single-task learning (QSTL) vs quantum multi-task learning (QMTL); MSE-loss training versus SWAP-test (fidelity) loss; evaluation of convergence speed and final KL divergence. Also noise sensitivity outputs: KL divergence between noisy and noiseless output distributions as a function of depolarizing/readout error probability. Tabulated example: QSTL Apple KL=0.1047 vs QMTL Apple KL=0.0614 (parameters counts reported).

### Parameters
- context_length_T: 3
- prediction_horizon_tau: 1
- quantization_levels_d: 2
- alternate_quantization: d=4 density-based non-uniform quantization in one experiment
- ansatz_layers_L: 4
- shots: 10000
- optimizer: SPSA (primary), parameter-shift discussed
- SPSA_delta: 0.01
- learning_rate: 0.1
- epochs_context_loading: 3000
- epochs_QSTL: 3000
- epochs_QMTL_per_asset: {'K=2_or_4': 250, 'K=8': 100}
- random_seed: 42
- example_qubits_QSTL: 8
- ancilla_qubits_tau: 1
- label_qubits: ceil(log2(K)) (+ additional control qubit in their scheme; paper uses log(K)+1 labeling scheme)
- reported_parameter_counts: {'QSTL': 32, 'QMTL_per_asset': 16}

### Hardware
{'simulator': 'Qiskit AerSimulator', 'noise_models': ['depolarizing error (gate noise)', 'readout error'], 'QPU_model': None, 'cloud_provider': None}

### Reproducibility
The paper states that data generated in the study are available from the corresponding author upon reasonable request. No public code repository or execution scripts are provided in the manuscript. Important hyperparameters (context size T, layers L, shots=10,000, SPSA delta=0.01, learning rates, epochs, random seed=42) and circuit design descriptions (ansatz structure, share-and-specify layout, SWAP-test loss) are reported, which partially supports reproducibility, but replication will require reimplementation of the circuits and access to the original preprocessed dataset unless the authors provide it upon request.
## Findings
- [supported] The proposed quantum multi-task learning (QMTL) share-and-specify ansatz can be trained to predict conditional distributions for multiple equities on a single quantum circuit (demonstrated up to 8 assets in simulation).
- [supported] QMTL outperformed quantum single-task learning (QSTL) in the paper's simulations: lower KL divergences and faster convergence were observed when training multiple assets together.
- [supported] Using a SWAP-test (fidelity) loss combined with SPSA-style gradient estimation produced better distribution learning in the authors' experiments than using an MSE loss with SPSA.
- [supported] Loading a contextual probability distribution via a hardware-efficient ansatz and training (SPSA, SWAP-test) can accurately encode contextual distributions (demonstrated for T=3 contexts on real stock data).
- [supported] The share-and-specify architecture achieves parameter sharing so that the number of trainable parameters did not grow when moving from 2 to 4 (and up to 8) assets in the reported experiments.
- [supported] The authors empirically evaluated noise sensitivity in simulation (depolarizing gate noise and readout error) and observed increasing KL divergence between noisy and noiseless outputs as noise increases.
- [speculative] The paper introduces Quantum Batch Gradient Update (QBGU) — loading an entire contextual distribution in superposition so a single quantum forward pass yields an aggregate gradient update equivalent to batching over classical samples — as a mechanism to accelerate SGD in quantum settings.
- [speculative] The authors claim QBGU will accelerate standard stochastic gradient descent and improve convergence quality compared to classical SGD in quantum applications (no direct head-to-head empirical comparison to classical SGD presented).
- [speculative] The authors claim that the QMTL/QBGU framework could enable quantum-advantageous downstream tasks (e.g., amplitude-estimation-based risk analysis or quantum linear-system speedups at inference) by producing continuations in superposition; this is presented as potential future benefit rather than demonstrated advantage.
- [supported] In the authors' experiments, QMTL exhibited faster empirical convergence than QSTL (loss curves show faster reduction and lower final losses in the multi-task case).
- [supported] The SWAP-test fidelity loss was empirically more effective than MSE loss for the quantum circuits and optimizers used in these experiments (MSE+SPSA failed to capture the target distributions in their tests).
- [supported] The authors used real S&P 500-derived historical data (Apple, Google, Microsoft, Amazon, plus expanded sets up to 8 assets) and binary (and in one test 4-level) quantization of returns to evaluate the method.

**Results summary:** The paper proposes a quantum multi-task learning architecture (share-and-specify ansatz) and a training concept (Quantum Batch Gradient Update, QBGU) for contextual stock-return distribution prediction. In numerical simulations using S&P-500-derived data (Apple, Google, Microsoft, Amazon and up to eight assets), the authors demonstrate that (i) a hardware-efficient ansatz can load contextual distributions, (ii) SWAP-test fidelity loss with SPSA yields better learned conditional distributions than MSE+SPSA in their setting, and (iii) the QMTL design achieves lower KL divergences and faster convergence than quantum single-task training while keeping parameter counts low. They also report experiments on effects of depolarizing and readout noise. The paper frames potential future uses where the learned superposed continuations could enable quantum-advantageous downstream algorithms, but does not empirically demonstrate a provable or experimentally measured quantum advantage over classical methods.

**Performance claims:**
- Apple (QSTL) KL Divergence: 0.1047 (Table I)
- Google (QSTL) KL Divergence: 0.1239 (Table I)
- Apple (QMTL) KL Divergence: 0.0614 (Table I)
- Google (QMTL) KL Divergence: 0.0754 (Table I)
- Training settings reported: commonly 3000 epochs, learning rate 0.1, 10,000 measurement shots (used in distribution-loading and prediction experiments).
- Noise experiment: under increasing depolarizing noise the KL divergence between noisy and noiseless outputs increased to around ~0.1 at high noise probabilities (figure reported qualitatively).
## Quantum advantage claim
**Classification:** speculative

The authors propose that QBGU and producing continuations in superposition could enable quantum-advantageous downstream algorithms (e.g., amplitude-estimation-based sampling/risk analysis) at inference; however, no theoretical proof-of-advantage or empirical demonstration against classical baselines is provided in the paper, so any claim of quantum advantage remains speculative.
## Limitations
- NISQ-era hardware constraints (small qubit counts, short coherence times) limit near-term realizations and potential advantage (author-stated).
- Classical deep learning models (e.g., large Transformers / LSTMs) can outperform the presented QML approach for large-scale time-series prediction due to classical scalability and capacity (author-stated).
- Use of feature maps is computationally expensive and slow to train; the paper avoids feature maps by preloading distributions onto an ansatz (author-stated).
- The fidelity (SWAP-test) loss was required for effective training; standard MSE combined with SPSA failed to capture target distributions reliably in their experiments (author-stated).
- Most experiments use small temporal contexts (T typically 2–3) and low quantization (binary d=2 in primary experiments), limiting representational granularity and temporal horizon in reported results (author-stated).
- Training is performed sequentially per asset in practice (e.g., 250 epochs per stock) rather than a truly simultaneous joint optimization over all tasks, which limits demonstrated concurrency (author-stated / described).
- [inferred] Experiments are primarily simulation-based (Qiskit Aer + noise models); no demonstration on error-corrected or larger-scale quantum hardware is provided, so hardware feasibility remains unvalidated.
- [inferred] The approach requires significant measurement resources (e.g., 10,000 shots) and many training epochs (thousands), indicating high runtime/sample complexity for the simulation results.
- [inferred] The share-and-specify scheme requires additional control circuitry (Toffoli and multi-control constructions) to implement label-based task selection; this increases gate count and circuit depth which may exacerbate noise sensitivity on real devices.
- [inferred] The SWAP test and distribution-loading procedure require ancilla qubits and many controlled/SWAP operations, potentially creating practical overheads on limited hardware.
- [inferred] Excluding label qubits from measurement and fixing labels during training effectively reduces controlled gates to independent task layers; this may limit benefits from fully joint quantum gradients across tasks.
- [inferred] Preloading a (historic) contextual distribution once assumes some stationarity; in non-stationary markets the preloaded distribution may become stale and require frequent re-loading, increasing operational overhead.
- [inferred] No comprehensive quantitative comparison to strong classical baselines (trained and tuned for the same tasks) is presented, leaving practical performance advantage unclear.
## Open questions
- Does Quantum Batch Gradient Update (QBGU) provide a provable or empirical training/runtime advantage over classical batch SGD or over repeated SGD/stochastic methods in practice?
- Can the QMTL (share-and-specify) architecture yield a systematic, practical advantage over classical multi-task learning approaches for financial time-series when both are optimized at scale?
- How well does the presented approach perform on actual quantum hardware with realistic noise, limited connectivity, and limited qubit counts?
- What are the noise tolerance thresholds (gate/readout error rates) under which the learned quantum distributions remain useful for downstream financial tasks?
- Can amplitude-estimation-based inference (or other quantum subroutines) produce a real-world advantage for downstream finance tasks (e.g., risk analysis, portfolio statistics) when paired with the QMTL-trained models?
- How to scale the approach to longer contexts (larger T) and higher-resolution quantization (d > 2) while keeping circuits shallow enough for NISQ devices?
- How to design / tune the share-and-specify ansatz (layer counts, parameter allocation between shared and task-specific parts) to maximize cross-task transfer and minimize negative transfer?
- What are the resource (qubit, gate, shot) requirements to represent and predict distributions for realistic portfolio sizes (large K) and longer horizons (R) on near-term devices?
- Can the distribution-loading method (hardware-efficient ansatz + SPSA) be made robust and efficient for frequently updating, non-stationary contextual distributions?
- Is the SWAP-test-based fidelity loss practical on hardware at scale (ancilla/qubit overhead, additional gates), or are alternative fidelity/overlap estimators needed?
- How does truly joint quantum training (not sequential per label) behave—does simultaneous multi-label gradient estimation produce better generalization or faster convergence?
- How sensitive are the claimed benefits (faster convergence and lower KL) to hyperparameters (shots, learning rate, SPSA perturbation, layer counts)?

**Future work:**
- Extend the method to create a superposition state over all d^R possible future paths with logarithmic qubit depth O(R), enabling compact sequential prediction over longer horizons (author-stated).
- Leverage amplitude estimation and other quantum subroutines at inference time for downstream tasks such as quantum risk analysis to potentially obtain quantum advantage (author-stated).
- Generalize from binary quantization (d = 2) to multi-level quantization (higher d) to capture finer-grained return dynamics (author-stated / suggested by experiments with d = 4).
- Investigate methods and circuit designs that reduce gate-depth and control overhead (e.g., optimizing Toffoli / control constructions) to improve realizability on noisy hardware (implied / suggested).
- Study robustness to realistic noise by testing on real quantum devices or more detailed noise models and exploring error mitigation strategies (author-experiment noise section points to this).
- Explore joint (simultaneous) training across assets (rather than sequential per-label training) and analyze its effect on convergence and generalization (implied).
- Develop efficient protocols for updating preloaded contextual distributions to handle non-stationary market conditions without prohibitive re-loading costs (inferred / practical next step).
- Benchmark QMTL and QBGU quantitatively against tuned classical baselines (LSTMs, Transformers, classical MTL models) on the same prediction tasks and datasets to clarify comparative strengths and weaknesses (inferred).
- Optimize hyperparameters of the share-and-specify ansatz (how many shared vs task-specific parameters, layer depth) to balance transfer and task specialization (inferred).
## Key ideas
- #idea:quantum-advantage — Quantum Batch Gradient Update (QBGU) enables dataset-weighted gradient updates by loading contextual distributions in superposition; in simulation this yields faster convergence and lower KL divergence for QMTL vs QSTL (example: QSTL Apple KL=0.1047 vs QMTL Apple KL=0.0614).
- #idea:hybrid-approach — The pipeline combines classical preprocessing (returns, smoothing, quantization) and classical optimizers (SPSA) with parametrized quantum circuits (PQC) and SWAP-test fidelity losses in a hybrid training loop.
- #idea:near-term-feasibility — The hardware-efficient ansatz, share-and-specify multi-task design with logarithmic qubit overhead, and AerSimulator noise experiments are positioned as NISQ-relevant approaches for small K (demonstrated up to K=8 in simulation).
- #limitation:simulation-only — All empirical results are from classical simulation (Qiskit AerSimulator, including noise models); no experiments on physical QPUs are reported.
- #limitation:noise — Sensitivity analysis with depolarizing and readout-error models shows degradation of output distributions under realistic noise levels, indicating fragility on current NISQ hardware.
- #limitation:data-encoding — The method depends on amplitude/state-loading of contextual distributions via a trained ansatz (state-preparation cost), which may be expensive and undermine claimed qubit-scaling or speedups in practice.
- #limitation:qubit-count — Although a logarithmic qubit overhead for multi-task learning is claimed, experiments remain small-scale and require ancilla/label qubits; practical scaling to large asset universes is not demonstrated.
## Contradictions
- contradiction:scalability — The paper claims logarithmic qubit overhead for multi-task learning, but only provides small-scale simulated evidence (K up to 8) and reports noise sensitivity and state-loading costs that challenge scaling to larger, real-world asset sets.
- contradiction:classical-vs-quantum — Improved convergence and better capture of inter-asset correlations are demonstrated relative to single-task quantum models, but no classical ML baselines are provided; thus claims of superiority over classical approaches are unsubstantiated.
## Notable quotes
<!-- Researcher-added — verbatim quotes with page references -->

## Researcher notes
<!-- Researcher-added — not LLM generated -->
