---
aliases:
- 'HQNN-FSP: A Hybrid Classical-Quantum Neural Network for Regression-Based Financial
  Stock Market Prediction'
- HQNN FSP Hybrid Classical
authors:
- Prashant Kumar Choudhary
- Nouhaila Innan
- Muhammad Shafique
- Rajeev Singh
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
- idea:hybrid-approach
- idea:near-term-feasibility
journal_or_venue: arXiv preprint (arXiv:2503.15403, q-fin.ST)
methodology_tags:
- variational-nisq
- quantum-ml
- hybrid-quantum-classical
paper_type: ''
quantum_advantage_claim: not-applicable
related_papers: []
relevance_phase1: high
relevance_phase3: high
source_type: preprint
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
- idea/hybrid-approach
- idea/near-term-feasibility
- contradiction/classical-vs-quantum
- contradiction/scalability
title: 'HQNN-FSP: A Hybrid Classical-Quantum Neural Network for Regression-Based Financial
  Stock Market Prediction'
topic_tags:
- quantum-ml-finance
year: '2025'
zotero_key: ''
---

## Abstract summary
This preprint proposes a hybrid classical-quantum framework for stock price forecasting, introducing a custom QNN regressor with a novel Hamiltonian-inspired ansatz and two integration strategies: sequential classical feature extraction followed by quantum processing, and joint end-to-end quantum-classical optimization. Evaluation using technical indicators, TimeSeriesSplit and k-fold validation, and RMSE/error analyses shows hybrid models improve over standalone QNNs (with HybridQNN2 the best hybrid), though classical LSTM-style models still achieve the lowest RMSE; the work highlights computational and NISQ-era limitations and avenues for further optimization.
## Methodology
The study develops and evaluates hybrid classical-quantum models for stock price regression by combining classical recurrent networks (RNN, LSTM, BiLSTM, GRU) with parameterized quantum circuits (PQCs). Historical intraday stock-price data (open, high, low, close, date) are augmented with technical indicators (RSI, MACD, ADX, SMA5/SMA20). Feature selection (SelectKBest) selects the top K features which are normalized (MinMaxScaler) and arranged into sequences with a lookback window (lookback=2). Three quantum-driven approaches are implemented: (i) a standalone custom QNN based on a Hamiltonian-inspired PQC with angle encoding (arcsin/arccos mappings) and layered parameterized rotations + entanglers (CNOT/CZ/TimeEvolutionGate); (ii) HybridQNN1 where a classical network (LSTM-based) extracts features which are then encoded and processed by a shallow QNN regressor; (iii) HybridQNN2 where the classical and quantum components run in parallel and their outputs are fused and trained end-to-end (joint optimization). Training uses ADAM optimizer with learning-rate scheduling, early stopping (patience=10), batch training (batch_size=32), a maximum of 500 iterations, and cross-validation via TimeSeriesSplit and k-fold CV. Evaluation employs RMSE as the primary metric, error-distribution analyses (histograms with Gaussian fits, violin plots), and comparisons to classical baselines. Experiments are executed on a quantum simulator (QULACS) and implemented with Qiskit/scikit-QULACS and TensorFlow/scikit-learn on an HPC cluster (PARAM Shivay) to measure accuracy and training time across qubit counts (3, 4, 5) and circuit depths.

**Algorithms used:** Parameterized Quantum Circuit (PQC), Quantum Neural Network (QNN), Hamiltonian-inspired ansatz, Angle encoding (RY, RZ with arcsin/arccos transforms), TimeEvolutionGate, HybridQNN1 (classical feature extraction -> QNN regressor), HybridQNN2 (joint quantum-classical end-to-end training), LSTM, RNN, BiLSTM, GRU, SelectKBest feature selection, MinMaxScaler normalization, ADAM optimizer, TimeSeriesSplit cross-validation, k-Fold cross-validation, SHAP (interpretability), GradientTape (for joint training in HybridQNN2)
**Frameworks:** Qiskit, scikit-QULACS, QULACS (simulator), TensorFlow, scikit-learn, CUDA (for GPU acceleration), Slurm (job scheduling)

**Experimental setup:** Experiments run primarily on a quantum simulator (QULACS) and Qiskit tooling; classical and hybrid training executed on the PARAM Shivay HPC cluster (2 × Intel Xeon Skylake 6148 CPUs, 192GB RAM, 2 × NVIDIA Tesla V100 GPUs per node). Code execution was parallelized with CUDA and scheduled with Slurm; communication via 100Gbps InfiniBand EDR. Training used up to 500 iterations, batch size 32, early stopping, and TimeSeriesSplit/k-fold CV for validation. Qubit counts tested: 3, 4, 5. Circuit depth reported as 10 in the pipeline.

**Dataset:** Historical stock price data (open, high, low, close, date) augmented with technical indicators (RSI (14), MACD (12,26) + 9-day signal, ADX (14), SMA5/SMA20). The paper cites the Kaggle dataset 'Stock market data - nifty 100 stocks (5 min) data' (D. Sahoo). Exact record count/size not specified in the text.
## Experiment details
### Input
{'source': "Kaggle: 'Stock market data - nifty 100 stocks (5 min) data' (reference [54]); example mentions Wipro stock time-series as a case.", 'raw_fields': ['date', 'open', 'high', 'low', 'close'], 'engineered_features': ['RSI (14-day)', 'MACD (12/26 EMA) + 9-day signal', 'ADX (14-day)', 'SMA5', 'SMA20'], 'feature_selection': 'SelectKBest (k varied: 3, 4, 5); selected features mapped to number of qubits', 'preprocessing_steps': ['Datetime conversion', 'Missing value handling', 'Compute technical indicators (RSI, MACD, ADX, SMA)', 'Normalize features: MinMaxScaler ([0,1] for classical, [-1,1] noted for quantum in pipeline)', 'Create time sequences with lookback=2', 'Train/test split: 80% train, 20% test'], 'dataset_size': 'Not specified in manuscript'}

### Process
{'pipeline_steps': ['Load and clean historical price data; compute technical indicators and moving averages.', 'Select top-K features with SelectKBest (K matched to qubit count: 3,4,5).', 'Normalize features (MinMaxScaler) and create sequences using a lookback window of 2 timesteps.', 'For QNNs: encode selected features into qubits using angle encoding (per-qubit RY(arcsin(f(x))) followed by RZ(arccos(g(x)))).', 'Construct Hamiltonian-inspired PQC ansatz with layers of parameterized single-qubit rotations (RX/RY/RZ), entangling gates (CNOT, CZ), and TimeEvolutionGate layers; circuit depth ≈ 10.', 'Model variants: (a) CustomQNN standalone trained on encoded inputs; (b) HybridQNN1: classical LSTM feature extractor -> encode -> QNN regressor -> measurement -> post-processing; (c) HybridQNN2: parallel classical (LSTM) and QNN processing -> feature fusion (concatenation with learned weights) -> fully connected prediction layer.', 'Train models end-to-end (for hybrids, jointly optimize classical and quantum parameters). Use ADAM optimizer, batch_size=32, max_iter=500, early stopping (patience=10), learning-rate scheduling. HybridQNN2 uses gradient synchronization / TensorFlow GradientTape for joint updates.', 'Validate using TimeSeriesSplit (primary) and k-Fold CV (comparative); compute loss (MSE) during training.', 'Evaluate on test set with RMSE, analyze error distributions (histograms + Gaussian fits, violin plots), compare training times and RMSE across qubit counts (3,4,5) and against classical baselines (LSTM, RNN, BiLSTM, GRU).'], 'hyperparameter_tuning': 'Systematic hyperparameter tuning using TimeSeriesSplit and k-fold CV; key hyperparameters explored: number of qubits (3/4/5 corresponding to selected features), circuit depth (~10), lookback (2), batch size (32), learning rate schedule, max iterations (500), early stopping patience (10).'}

### Output
{'primary_metrics': ['RMSE (reported per model and qubit setting)', 'Training time (seconds)'], 'secondary_outputs': ['Prediction traces (actual vs predicted time series)', 'Error histograms with Gaussian fits', 'Violin plots of error distributions', 'Comparative tables of RMSE and training time across models and qubit counts', 'SHAP feature importance (interpretability)'], 'baselines': ['Classical recurrent models: LSTM, RNN, BiLSTM, GRU'], 'representations': 'Tabular RMSE & training-time results; figures of time-series predictions and error-distribution plots; analyses across TimeSeriesSplit and k-Fold CV.'}

### Parameters
- qubits_tested: [3, 4, 5]
- circuit_depth: 10
- ansatz_components: ['Parameterized RX/RY/RZ rotations', 'Entanglers: CNOT, CZ', 'TimeEvolutionGate layers (Hamiltonian-based terms)']
- encoding: Angle encoding using RY(arcsin(f(x))) and RZ(arccos(g(x)))
- optimizer: ADAM
- loss_function: Mean Squared Error (MSE); evaluation metric RMSE
- batch_size: 32
- max_iterations: 500
- early_stopping_patience: 10
- lookback_window: 2
- validation_methods: ['TimeSeriesSplit', 'k-Fold cross-validation']
- feature_selection_k_values: [3, 4, 5]
- shots: Not specified
- learning_rate_schedule: Applied (details not specified)

### Hardware
{'simulator': 'QULACS (used via scikit-QULACS); Qiskit used for quantum tooling', 'qpu_model': None, 'cloud_provider': None, 'classical_hardware': 'PARAM Shivay supercomputer (2 × Intel Xeon Skylake 6148 CPUs per node, 192GB RAM, 2 × NVIDIA Tesla V100 GPUs per node); 100Gbps InfiniBand EDR interconnect'}

### Reproducibility
Dataset source is cited (Kaggle: 'Stock market data - nifty 100 stocks (5 min) data', reference [54]) and frameworks (Qiskit, scikit-QULACS, TensorFlow, scikit-learn) are listed. The paper does not provide a public code repository or exact dataset subset sizes, random seeds, or full hyperparameter search logs. Circuit definitions and model architectures are described in text and figures (ansatz diagrams, encoding), but low-level implementation details (exact parameter initialization, learning-rate schedule values, shot counts) are not specified. Reproducing the results is feasible in principle given the described components and HPC/simulator environment, but would require reimplementation and parameter tuning; no direct code/data links were provided in the manuscript.
## Findings
- [supported] The authors developed a hybrid quantum-classical architecture integrating a custom parameterized quantum circuit (QNN regressor) with classical recurrent networks (RNN/LSTM/GRU/BiLSTM).
- [supported] Two hybrid optimization strategies were implemented and evaluated: (1) sequential classical feature extraction followed by quantum processing (HybridQNN1) and (2) end-to-end joint training of classical and quantum components (HybridQNN2).
- [supported] HybridQNN1 and HybridQNN2 outperform the standalone CustomQNN (pure quantum model) in RMSE on the used dataset and experimental setup.
- [supported] Among the evaluated quantum/hybrid configurations, HybridQNN2 achieved the lowest RMSE (best performance) of the quantum-enhanced models across the tested qubit counts.
- [supported] Classical recurrent models (LSTM, RNN, BiLSTM, GRU) achieve substantially lower RMSE than the tested quantum and hybrid models on the same forecasting task/dataset.
- [supported] Increasing the number of qubits (3→4→5) produced mixed effects on RMSE but increased computational/training time, highlighting an accuracy vs. computational-cost trade-off for the quantum/hybrid models.
- [supported] All evaluated models (custom QNN and hybrid variants) struggled to promptly adapt to abrupt market regime shifts (a pronounced drop in prices in the test sequence), indicating limited responsiveness to sudden changes.
- [supported] Error-distribution analyses (histogram with Gaussian fits and violin plots) show that hybrid models have narrower, more concentrated error distributions than the standalone CustomQNN, indicating lower variance and more consistent predictions.
- [supported] The study used TimeSeriesSplit and k-fold cross-validation; TimeSeriesSplit produced higher RMSE (more conservative / realistic for sequential forecasting), while k-fold gave lower RMSE estimates but at higher computational cost.
- [supported] The authors report that SHAP interpretability analysis identified domain-specific technical indicators (e.g., RSI, MACD) as influential features for model predictions.
- [speculative] The paper argues that quantum-enhanced feature spaces (via entanglement and superposition) could, in principle, improve separability and pattern recognition for financial time-series tasks.
- [speculative] The custom Hamiltonian-inspired ansatz and entangling structure are claimed to improve expressivity and help mitigate training issues such as barren plateaus (this is a proposed design rationale rather than a fully proven empirical result in the paper).
- [speculative] The authors suggest that hybrid quantum-classical models could become more competitive with classical approaches as quantum hardware, noise reduction, and algorithmic refinements improve.

**Results summary:** The paper introduces and evaluates a custom QNN regressor and two hybrid quantum-classical models for stock price regression. Empirically, the hybrid approaches (HybridQNN1 and HybridQNN2) yield substantially lower RMSE than a standalone QNN, with HybridQNN2 performing best among quantum-enhanced variants. However, classical recurrent models (LSTM, RNN, BiLSTM, GRU) outperform the quantum and hybrid models on the tested dataset. The experiments reveal a trade-off between qubit count and training time, and all models struggle with abrupt regime shifts in the test series. Interpretability analysis highlights the importance of technical indicators (e.g., RSI, MACD) for predictions. The authors frame their results as evidence that hybridization mitigates some limitations of purely quantum models but do not claim a practical quantum advantage over classical baselines.

**Performance claims:**
- CustomQNN RMSEs: 3 qubits = 0.07603, 4 qubits = 0.05528, 5 qubits = 0.06120 (Table II / Table III).
- HybridQNN1 RMSEs: 3 qubits = 0.02605, 4 qubits = 0.02161, 5 qubits = 0.01740 (Table II / Table III).
- HybridQNN2 RMSEs: 3 qubits = 0.02312, 4 qubits = 0.01959, 5 qubits = 0.01920 (Table II / Table III).
- Classical model RMSEs (examples for 5 selected features): LSTM = 0.00649, RNN = 0.00659, BiLSTM = 0.00669, GRU = 0.00669 (Table III).
- Training times (approx., seconds) reported in Table II for QNN/hybrids: CustomQNN: 120,765.63 (3q), 155,362.05 (4q), 139,337.06 (5q); HybridQNN1: 121,020.84 (3q), 155,336.05 (4q), 227,781.18 (5q); HybridQNN2: 69,841.69 (3q), 92,337.84 (4q), 118,833.32 (5q).
- Reported observation: all three quantum/hybrid models partially overlap with actual values in a stable phase but fail to capture a sharp downward shift in a later phase (Phase 2), indicating poor responsiveness to abrupt changes (qualitative).
## Quantum advantage claim
**Classification:** not-applicable

The paper does not claim a demonstrated quantum advantage over classical methods. Empirical results show hybrid quantum-classical models improve over a standalone QNN but still underperform classical recurrent models (lower RMSE for LSTM/GRU/BiLSTM/RNN). The authors present potential/theoretical benefits of quantum feature spaces but stop short of claiming practical quantum advantage.
## Limitations
- Quantum hardware constraints: noise, limited qubit reliability, and scalability issues that restrict large-scale QML applications (author-stated).
- Limited circuit depth of current quantum devices, restricting processing of high-dimensional financial data (author-stated).
- High computational cost and long training times for quantum and hybrid models, especially for higher qubit counts and HybridQNN1 (author-stated).
- Models trained/evaluated primarily on quantum simulators (QULACS) and HPC resources rather than on real NISQ hardware, leaving hardware-specific performance untested (author-stated).
- Hybrid models and QNNs did not outperform state-of-the-art classical deep learning (LSTM/BiLSTM) in RMSE, i.e., no decisive performance advantage demonstrated (author-stated).
- Poor responsiveness to abrupt market regime shifts: models failed to promptly adjust to sharp downward price changes in experiments (author-stated).
- Trade-off between accuracy and efficiency: increasing qubits improved accuracy but substantially increased resource/time costs (author-stated).
- Interpretability of QML remains underexplored; while SHAP was used, broader explainability for quantum components is not established (author-stated).
- Validation methodology concerns: k-Fold can introduce information leakage for time series; TimeSeriesSplit yielded higher RMSE reflecting sequential forecasting challenges (author-stated).
- [inferred] Potential overfitting or poor generalization in volatile/non-stationary regimes despite hybridization—models showed instability during abrupt shifts.
- [inferred] Limited lookback period (lookback = 2) likely constrained the models' ability to capture long-range temporal dependencies common in financial series.
- [inferred] Reliance on a small set of selected technical indicators and handcrafted features may limit generalization across different assets/markets.
- [inferred] Use of simulators and resource-rich HPC (GPUs, multi-node) may mask practical deployment challenges (latency, cost) for real-world or cloud quantum services.
- [inferred] Custom ansatz and encoding choices may not be optimal; suboptimal encoding/circuit design could lead to barren plateaus or inefficient learning.
## Open questions
- Can quantum-enhanced models provide a genuine, reproducible advantage over classical deep learning methods for financial time-series forecasting?
- How effective are quantum error mitigation techniques and noise-resilient processors at improving QML performance in realistic NISQ settings?
- Which quantum encoding schemes and ansatz structures are best suited for financial time-series data to maximize expressivity while maintaining trainability?
- How to design hybrid architectures that balance predictive accuracy with computational efficiency (qubit count, circuit depth, classical–quantum split)?
- How to make QML models adaptive and responsive to abrupt market regime shifts (rapid retraining, online/adaptive learning, reinforcement learning integrations)?
- What is the practical feasibility and performance of these hybrid models when deployed on real quantum hardware (latency, throughput, noise) as opposed to simulators?
- How to improve interpretability/explainability for the quantum components and reliably attribute feature importance in hybrid QML systems?
- What are the scalability limits (dataset size, number of features/qubits) for hybrid models before costs outweigh benefits?
- How does the choice of cross-validation strategy (k-Fold vs TimeSeriesSplit) affect reliable performance estimation for hybrid QML in finance?
- What are principled methods to mitigate training issues such as barren plateaus in financial QNNs?

**Future work:**
- Explore larger-scale quantum architectures, including noise-resilient quantum processors, to enhance scalability and precision (author-stated).
- Extend the models with larger datasets and additional financial indicators to improve adaptability and generalization (author-stated).
- Test real-time applications and deploy the hybrid models on actual quantum hardware to assess practical feasibility (author-stated).
- Enhance adaptability through reinforcement learning or other adaptive mechanisms to better handle abrupt market fluctuations (author-stated/inferred).
- Optimize hybrid architectures to reduce circuit depth and improve qubit utilization to balance accuracy and computational cost (author-stated).
- Explore alternative quantum encoding schemes to improve feature representation and model expressivity (author-stated).
- Leverage quantum error mitigation and noise-reduction techniques to improve model reliability on NISQ devices (author-stated).
- Algorithmic refinements to reduce training time and resource consumption (author-stated/inferred).
- Further work on interpretability and explainable AI tailored to quantum and hybrid models (author-stated/inferred).
## Key ideas
- #idea:hybrid-approach — Proposes two hybrid architectures: HybridQNN1 (classical feature extractor -> QNN regressor) and HybridQNN2 (parallel classical and quantum branches with end-to-end joint training); HybridQNN2 is reported as the best hybrid.
- #idea:near-term-feasibility — Experiments run on a quantum simulator (QULACS) exploring NISQ-relevant regimes (3–5 qubits, circuit depth ≈10) and explicitly discuss NISQ-era computational limits.
- #idea:hybrid-approach — Classical LSTM-style components remain strong baselines and are incorporated into hybrid designs to leverage classical sequence modelling strengths.
- #idea:near-term-feasibility — Introduces a Hamiltonian-inspired PQC ansatz with angle encoding (arcsin/arccos transforms) and TimeEvolutionGate layers for regression tasks.
- #idea:hybrid-approach — Maps selected top-K features to qubits (SelectKBest with K matched to qubit count) highlighting a clear data-to-qubit encoding strategy.
- #idea:near-term-feasibility — Comprehensive evaluation pipeline (TimeSeriesSplit, k-fold CV, RMSE, error-distributions, training time) on simulated hardware provides empirical baseline comparisons across qubit counts.
## Contradictions
- The paper's empirical results show classical LSTM-style models achieve lower RMSE than the hybrid and standalone QNN models, contradicting any claim that the proposed quantum or hybrid models currently outperform classical baselines (contradiction:classical-vs-quantum).
- Results are limited to small qubit counts (3–5) and simulator experiments; the authors note NISQ-era hardware and computational constraints, which contradict broad claims that the described approaches scale to practical, real-world production workloads (contradiction:scalability).
## Notable quotes
<!-- Researcher-added — verbatim quotes with page references -->

## Researcher notes
<!-- Researcher-added — not LLM generated -->
