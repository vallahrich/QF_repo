---
aliases:
- 'Toward Practical Quantum Machine Learning: A Novel Hybrid Quantum LSTM for Fraud
  Detection'
- Toward Practical Quantum Machine
authors:
- Rushikesh Ubale
- Sujan K. K.
- Sangram Deshpande
- Gregory T. Byrd
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
journal_or_venue: arXiv preprint
methodology_tags:
- variational-nisq
- quantum-ml
- hybrid-quantum-classical
paper_type: ''
quantum_advantage_claim: speculative
related_papers: []
relevance_phase1: high
relevance_phase3: high
source_type: preprint
source_type_confidence: high
step1_date: '2026-04-14T12:15:33.135660'
step1_model: gpt-5-mini
step2_date: '2026-04-14T12:15:33.135660'
step2_model: gpt-5-mini
step3_date: '2026-04-14T12:15:33.135660'
step3_model: gpt-5-mini
step4_date: '2026-04-14T12:15:33.135660'
step4_model: gpt-5-mini
step5_date: '2026-04-14T12:15:33.135660'
step5_model: gpt-5-mini
step6_date: '2026-04-14T12:15:33.135660'
step6_model: gpt-5-mini
steps_completed:
- 1
- 2
- 3
- 4
- 5
- 6
tags:
- topic/fraud-detection
- method/variational-nisq
- method/quantum-ml
- method/hybrid-quantum-classical
- idea/quantum-advantage
- idea/near-term-feasibility
- idea/hybrid-approach
- contradiction/classical-vs-quantum
- contradiction/scalability
title: 'Toward Practical Quantum Machine Learning: A Novel Hybrid Quantum LSTM for
  Fraud Detection'
topic_tags:
- fraud-detection
year: '2025'
zotero_key: ''
---

## Abstract summary
The paper proposes a hybrid quantum–classical neural network that integrates a classical LSTM with a variational quantum circuit (using AngleEmbedding and StronglyEntanglingLayers) for credit card fraud detection. The model is trained end-to-end with classical backpropagation and quantum parameter gradients via the parameter-shift rule, reporting improved recall and F1 over a classical LSTM and per-epoch training times of 45–65 seconds on the PennyLane default.qubit simulator.
## Methodology
The authors propose a hybrid quantum–classical fraud-detection pipeline that combines a classical LSTM for temporal feature extraction with a variational quantum circuit (VQC) for enhanced representation learning. Raw transaction data (a synthetically generated credit-card fraud dataset with 27 features) is cleaned (PII removed), categorical features label-encoded, continuous features z-score normalized, and a balanced subset selected (baseline: 10,000 samples: 5,000 fraud / 5,000 non-fraud). Each static sample is reshaped into a sequence of length 1 (unsqueeze) and fed to a PyTorch LSTM (batch_first=True) to obtain a final hidden state h_T. A fully connected layer projects h_T to a vector sized to the number of qubits. That vector is encoded into a PennyLane quantum circuit via AngleEmbedding (RY rotations), processed through StronglyEntanglingLayers (trainable parameterized rotations interleaved with entangling gates), and measured in the Pauli-Z basis to produce a quantum feature vector. A final FC layer with sigmoid produces the fraud probability. Training is end-to-end: classical gradients are computed by PyTorch autograd, while quantum parameter gradients are obtained via the parameter-shift rule; gradients are combined and updated jointly with Adam. Training hyperparameters include BCEWithLogitsLoss, Adam (lr=0.001, weight_decay=1e-4), batch size 32, 80 epochs, dropout 0.3, and gradient clipping. Experiments use PennyLane's default.qubit state-vector simulator (CPU); additional scaling experiments vary qubit count (10 and 12) and dataset size (10k, 30k, 35k) to assess performance/time trade-offs.

**Algorithms used:** LSTM (Long Short-Term Memory), Variational Quantum Circuit (VQC), AngleEmbedding (RY encoding), StronglyEntanglingLayers, Parameter-shift rule for quantum gradients, Adam optimizer, BCEWithLogitsLoss (binary cross-entropy with logits), Label Encoding, Z-score normalization (StandardScaler), SMOTE (mentioned as common technique; not explicitly stated as used in experiments)
**Frameworks:** PennyLane, PyTorch, NumPy

**Experimental setup:** Simulations performed on PennyLane using the default.qubit statevector simulator (CPU-based, no GPU acceleration). The quantum circuit uses AngleEmbedding (RY), StronglyEntanglingLayers, and Pauli-Z measurements. Training used PyTorch DataLoader with batch size 32 and Adam optimizer. Baseline classical LSTM implemented in PyTorch. Reported per-epoch times reflect CPU simulation overhead.

**Dataset:** A synthetically generated credit-card transaction dataset with 27 features (card details, merchant, amount, timestamps, geospatial coordinates, demographics, encoded categorical variables). For main experiments a balanced subset of 10,000 transactions (5,000 fraud, 5,000 non-fraud) was used; additional experiments used 30k and 35k sample subsets.
## Experiment details
### Input
{'source': 'Synthetic credit card fraud dataset (designed to mimic real-world transactions); exact external source or public link not provided in the paper.', 'size': 'Baseline: 10,000 samples (5k fraud, 5k non-fraud). Additional experiments: 30,000 and 35,000 samples.', 'features': 27, 'preprocessing_steps': ['Remove PII columns (first, last, street, trans_num)', 'Label encoding for categorical features (merchant, city, category, job, state, gender, etc.)', 'Compute derived features (customer_age from DOB; customer-merchant distance via haversine formula; hour/day/month/year/weekday from timestamp)', 'Z-score normalization (standardization) for continuous features', 'Stratified split into train/validation/test (70%/15%/15%)', 'Tensor conversion to PyTorch tensors', 'Balanced sampling for experiments (explicitly selected balanced subsets)']}

### Process
{'pipeline_steps': ['Data cleaning and feature engineering (time, geospatial, demographic features; label encoding; normalization)', 'Build PyTorch Dataset/DataLoader (batch size 32, shuffle enabled)', 'Reshape static feature vectors to sequences of length 1 (unsqueeze) to feed LSTM', 'Pass sequence through LSTM (batch_first=True) and extract final hidden state h_T', 'Project h_T to R^{n_qubits} via a fully connected (FC) layer', 'Encode the projected vector into quantum circuit using AngleEmbedding (RY rotations)', 'Apply StronglyEntanglingLayers (parameterized single-qubit rotations + entangling CNOTs / staggered adjacency)', 'Measure each qubit in the Z basis to obtain a quantum feature vector q', 'Pass q through final FC layer with sigmoid activation to obtain fraud probability', 'Compute BCEWithLogitsLoss; compute classical gradients via autograd; compute quantum parameter gradients via parameter-shift rule (shift typically pi/2); combine gradients and perform joint optimizer step (Adam)', 'Repeat for 80 epochs; monitor training/validation loss and accuracy; record per-epoch time'], 'training_details': {'epochs': 80, 'batch_size': 32, 'optimizer': 'Adam', 'learning_rate': 0.001, 'weight_decay': 0.0001, 'loss_function': 'BCEWithLogitsLoss', 'dropout': 0.3, 'gradient_clip': 'applied to LSTM (value unspecified)', 'quantum_gradient_method': 'parameter-shift (evaluations at theta+delta and theta-delta; delta typically pi/2)'}, 'quantum_settings': {'encodings': 'AngleEmbedding (RY)', 'ansatz': 'StronglyEntanglingLayers (repeated blocks; exact number of blocks/layers not specified)', 'measurements': 'Expectation values of Pauli-Z on each qubit'}, 'variations_tested': ['Baseline: 10 qubits, 10k samples', '10 qubits, 35k samples', '12 qubits, 30k samples']}

### Output
{'metrics_reported': ['Accuracy', 'Precision', 'Recall', 'F1 Score', 'Confusion Matrix (counts)', 'Inference time on test set', 'Average time per epoch (training)'], 'baseline_comparison': 'Classical LSTM (two-layer LSTM with hidden_size 32, dropout 0.3) trained with same preprocessing and loss/optimizer', 'example_results': {'quantum_hybrid_10k': {'accuracy': '95.33%', 'precision': '94.16%', 'recall': '96.67%', 'f1_score': '95.39%', 'inference_time': '6.32 s', 'avg_epoch_time': '45-65 s'}, 'classical_lstm_10k': {'accuracy': '94.33%', 'precision': '95.61%', 'recall': '92.93%', 'f1_score': '94.25%', 'inference_time': '0.07 s', 'avg_epoch_time': '< 2 s'}, 'quantum_10qubits_35k': {'accuracy': '98.38%', 'recall': '99.81%', 'f1_score': '98.40%', 'avg_epoch_time': '165-180 s'}, 'quantum_12qubits_30k': {'accuracy': '98.04%', 'recall': '100.00%', 'f1_score': '98.08%', 'avg_epoch_time': '4-5 minutes'}}}

### Parameters
- n_qubits: {'baseline': 10, 'other_runs': [12]}
- ansatz_layers: StronglyEntanglingLayers (number of repeated layers L not explicitly specified)
- encoding: AngleEmbedding (RY rotations)
- shots: statevector simulator; not applicable (expectation values computed deterministically)
- optimizer: Adam
- learning_rate: 0.001
- weight_decay: 0.0001
- batch_size: 32
- epochs: 80
- dropout: 0.3
- parameter_shift_delta: typically pi/2 (as described)
- loss_function: BCEWithLogitsLoss

### Hardware
{'simulator': 'PennyLane default.qubit (CPU-based statevector simulator)', 'accelerated_simulators_mentioned': ['pennylane_lightning.qubit', 'pennylane_lightning.gpu'], 'qpu_model': None, 'cloud_provider': None, 'notes': 'Experiments reported on CPU simulator; no physical QPU or cloud provider execution reported.'}

### Reproducibility
The paper gives reasonably detailed model architecture, preprocessing steps, and hyperparameters (optimizer, lr, weight decay, batch size, epochs) and specifies frameworks used (PennyLane, PyTorch). However, it does not provide links to code or the exact synthetic dataset used, nor does it enumerate some circuit hyperparameters (exact number of StronglyEntanglingLayers blocks, random seeds, complete model source code). Data availability or code repository is not stated, limiting immediate reproducibility.
## Findings
- [supported] The authors implemented a hybrid quantum–classical architecture that integrates a classical LSTM with a variational quantum circuit (VQC) using AngleEmbedding and StronglyEntanglingLayers (implemented via PennyLane and PyTorch).
- [supported] The hybrid model was trained end-to-end with unified backpropagation where quantum parameter gradients are evaluated via the parameter-shift rule and combined with classical gradients.
- [supported] On a balanced, synthetically generated subset of 10,000 transactions (5,000 fraud / 5,000 non-fraud), the hybrid model achieved test metrics: Accuracy 95.33%, Precision 94.16%, Recall 96.67%, F1 95.39%.
- [supported] The hybrid model incurred per-epoch training times of about 45–65 seconds on PennyLane's default.qubit (CPU) simulator for the 10k-sample, 10-qubit configuration.
- [supported] The classical LSTM baseline (two-layer LSTM, hidden_size=32, dropout=0.3) on the same data achieved: Accuracy 94.33%, Precision 95.61%, Recall 92.93%, F1 94.25%, and per-epoch training time under ~2 seconds.
- [supported] The hybrid model shows improved recall and F1 compared to the classical LSTM baseline on the reported experiment, suggesting fewer false negatives (important for fraud detection).
- [supported] Increasing dataset size and qubit count improved reported performance but increased computational cost: 10 qubits on 35k samples achieved Accuracy 98.38% / Recall 99.81% / F1 98.40% (~165–180 s/epoch), and 12 qubits on 30k samples achieved Accuracy 98.04% / Recall 100% / F1 98.08% (~4–5 min/epoch).
- [supported] The model exhibited significant overfitting: training accuracy approached 99%+ while validation/test accuracy remained lower, and the authors acknowledge the gap and propose more data and regularization as remedies.
- [supported] The dataset used in experiments is synthetically generated and heavily preprocessed (features extracted, categorical label encoding, z-score normalization, stratified splits, and balanced via resampling).
- [speculative] The paper claims quantum phenomena (superposition and entanglement) provide enhanced feature representation and expressivity over classical models, enabling capture of complex non-linear patterns difficult for purely classical architectures.
- [speculative] The authors assert that their circuit design and choice of simulator make the approach practical on CPU-based systems without GPU acceleration, making hybrid quantum–classical models more accessible for real-world deployment.
- [speculative] The claim that AngleEmbedding + StronglyEntanglingLayers (SEL) materially increase expressivity relative to classical alternatives is presented as a motivation and inferred from improved metrics, but no ablation study isolating these components was reported.
- [speculative] Future-scope claims: scaling to more qubits on real quantum hardware would increase expressivity but will require advanced error mitigation strategies (e.g., zero-noise extrapolation, probabilistic error cancellation).
- [supported] The implementation details include specific training choices (Adam optimizer with lr=0.001, weight decay=1e-4, batch size=32, BCEWithLogitsLoss, 80 epochs) and practicalities like inserting a dummy time dimension to feed static feature vectors to the LSTM.

**Results summary:** The paper presents a hybrid quantum–classical fraud detection model combining an LSTM for temporal feature extraction with a variational quantum circuit (AngleEmbedding + StronglyEntanglingLayers) implemented via PennyLane and PyTorch. On a synthetically generated, balanced 10k-sample dataset the hybrid model outperformed a closely matched classical LSTM baseline on recall and F1 (Hybrid: Acc 95.33%, Prec 94.16%, Rec 96.67%, F1 95.39% vs Classical: Acc 94.33%, Prec 95.61%, Rec 92.93%, F1 94.25%). The authors report practical per-epoch training times of 45–65 seconds for the 10k/10-qubit configuration on a CPU state-vector simulator, and show improved metrics (but substantially higher runtime) when scaling dataset size and qubit count. They note overfitting issues and emphasize the synthetic nature of the dataset, recommending larger datasets, further regularization, and future hardware validation with error mitigation.

**Performance claims:**
- Hybrid model (10 qubits, 10k samples): Accuracy 95.33%, Precision 94.16%, Recall 96.67%, F1 95.39%; inference time on test set 6.32 seconds; average training time per epoch ~55 seconds.
- Classical LSTM baseline (same data): Accuracy 94.33%, Precision 95.61%, Recall 92.93%, F1 94.25%; inference time 0.07 seconds; average training time per epoch ~1.5 seconds (authors also report 'under 2 seconds').
- Training accuracy reported up to ~99.69% for the hybrid model (indicating overfitting relative to test accuracy).
- 10 qubits, 35k samples configuration: Accuracy 98.38%, Recall 99.81%, F1 98.40%; average time per epoch 165–180 seconds.
- 12 qubits, 30k samples configuration: Accuracy 98.04%, Recall 100.00%, F1 98.08%; average time per epoch ~4–5 minutes.
- Comparison to literature: authors contrast their 45–65 s/epoch (default.qubit CPU) to a cited study reporting ~1 h 26 min per epoch for a QLSTM, asserting substantially faster per-epoch training in their setup.
## Quantum advantage claim
**Classification:** speculative

The authors report improved recall and F1 over a classical LSTM on their synthetic, balanced dataset and argue that quantum embedding + entangling layers increase expressivity. However, these claims are based on limited experiments (synthetic data, a single dataset, no ablation to isolate quantum contribution, and CPU simulation rather than real hardware), so a definitive, general quantum advantage is not demonstrated and remains speculative.
## Limitations
- Overfitting: training accuracy (≈99.69%) is substantially higher than validation/test accuracy (test 95.33%), indicating the model may be overfitting to the training data (author-stated).
- Use of a synthetically generated dataset rather than real-world transactional data, limiting ecological validity and generalizability (author-stated).
- Small experimental subset for many experiments: primary comparisons reported on a balanced subset of 10,000 samples (5k fraud, 5k non-fraud), which may be insufficient to assess generalization (author-stated).
- Performance vs. compute trade-off: while 10k experiments ran in 45–65s/epoch on CPU simulator, scaling to larger datasets and more qubits caused epoch time to increase dramatically (e.g., 10 qubits/35k samples → 165–180s/epoch; 12 qubits/30k samples → 4–5 min/epoch) (author-stated).
- Simulated-only evaluation: experiments were run on PennyLane default.qubit CPU simulator; no experiments on real quantum hardware are reported, so hardware noise and real-device constraints are not evaluated (author-stated).
- Need for error mitigation when moving to hardware: scaling to more qubits on real devices will require advanced error mitigation (zero-noise extrapolation, probabilistic error cancellation) (author-stated).
- Limited comparison baseline: primary benchmark is a classical LSTM; comparisons to strong classical non-RNN baselines common in fraud detection (e.g., XGBoost, Random Forest) are not reported (inferred).
- Artificial dataset balancing via oversampling/downsampling to 50k per class and later use of 10k balanced subset may not reflect real-world class distributions and could bias performance estimates (inferred).
- [inferred] Potential increase in model capacity as confounder: improvements attributed to the quantum layer may partly arise from increased model complexity/capacity rather than a genuine quantum advantage, but the paper does not fully disentangle these effects.
- [inferred] Parameter-shift gradient evaluation introduces extra computational overhead (multiple circuit evaluations per parameter), which may limit scalability and was not fully quantified beyond epoch timings.
- [inferred] Lack of multiple independent runs / statistical testing: results are reported as point estimates (accuracy, precision, recall, F1) without confidence intervals or significance testing to assess variability and robustness.
- [inferred] No ablation study presented to quantify contribution of individual components (e.g., AngleEmbedding vs. other embeddings, SEL vs. shallower ansatzes, LSTM depth) to the observed performance.
- [inferred] Interpretability concerns: integrating a variational quantum circuit makes model interpretability harder, and the paper does not present explainability analyses for model decisions.
- [inferred] Barren plateau risk and optimization landscape issues for VQCs are mentioned as a general challenge but not empirically characterized for the specific circuits used.
## Open questions
- How does the hybrid quantum–classical model perform on real-world (non-synthetic) credit card transaction datasets with realistic class imbalance and distributional properties?
- To what extent do the observed performance gains come from quantum feature transformation versus simply increasing model capacity or classical representational power?
- How robust are the results across multiple random seeds, dataset splits, and repeated training runs (i.e., what is the variance of reported metrics)?
- What is the impact of different quantum encodings (e.g., AngleEmbedding vs. other feature maps) and different variational ansatz designs on fraud-detection performance?
- How does the hybrid model compare to state-of-the-art classical fraud-detection methods (e.g., XGBoost, Random Forest, gradient-boosted trees) on identical data and evaluation protocols?
- How will the model perform when deployed on real quantum hardware given noise, limited qubit counts, gate errors, and decoherence?
- Which error mitigation strategies (and at what cost) are required to retain the model’s performance on noisy intermediate-scale quantum (NISQ) devices?
- How can the training-time overhead introduced by parameter-shift gradient evaluations be reduced for larger circuits and datasets (e.g., through analytic gradients, stochastic parameter-shift, or gradient-free optimizers)?
- What regularization techniques or architectural changes best reduce the overfitting gap observed, and how do they affect both classical and quantum parameter training?
- How sensitive is model performance to the number of qubits, number of entangling layers, and other VQC hyperparameters?
- How does the model generalize under dataset shift, temporal drift, or adversarial attempts to evade detection?
- Can the hybrid approach be adapted for privacy-preserving or federated settings (the paper cites related work but does not evaluate federated scenarios)?
- How interpretable are the quantum-enhanced features and predictions to domain experts, and can explainability techniques be adapted to hybrid quantum-classical models?
- What are the practical cost-benefit trade-offs (accuracy vs. compute/time) when choosing between purely classical models and quantum-hybrid models for fraud detection in production contexts?

**Future work:**
- Address remaining overfitting issues by exploring additional regularization techniques (e.g., advanced dropout schemes, data augmentation, ensemble methods).
- Further optimize quantum circuit parameters and the quantum ansatz design to improve performance and efficiency.
- Expand the dataset (train on a higher number of data samples) to improve generalization and mitigate overfitting.
- Validate the hybrid model on actual quantum hardware and evaluate the effects of noise and device constraints.
- Test with a higher number of qubits to enhance expressivity, while developing and applying advanced error mitigation strategies (such as zero-noise extrapolation or probabilistic error cancellation) for hardware experiments.
- Introduce GPU acceleration (e.g., lightning.gpu simulator) in future studies to further improve training speed and scale to larger datasets.
## Key ideas
- #idea:hybrid-approach — A hybrid pipeline combining a classical LSTM for temporal feature extraction with a variational quantum circuit (AngleEmbedding + StronglyEntanglingLayers) is proposed and trained end-to-end with combined classical and parameter-shift quantum gradients.
- #idea:quantum-advantage — On a balanced synthetic 10k dataset the hybrid model reports modest improvements in recall and F1 (e.g., F1 95.39% vs 94.25% for classical LSTM), suggesting potential representational gains from the VQC.
- #idea:near-term-feasibility — Experiments target small NISQ-scale circuits (10 and 12 qubits) and report wall-clock per-epoch times on a statevector simulator to assess practical runtime trade-offs.
- #limitation:simulation-only — All experiments were performed on the PennyLane default.qubit state-vector simulator (CPU); no real QPU experiments or noise models were used.
- #limitation:qubit-count — Demonstrations are limited to small qubit counts (10, 12), leaving open whether benefits persist for larger, practical problem encodings.
- #limitation:noise — Use of an ideal simulator omits hardware noise; reported metrics do not reflect realistic noisy-device performance.
- #limitation:data-encoding — The approach projects an LSTM hidden state to R^{n_qubits} and uses AngleEmbedding; the paper does not fully address the cost or scalability of this encoding for higher-dimensional inputs.
- #idea:near-term-feasibility — Reported runtimes show substantial simulation/training overhead (avg epoch 45–65 s for hybrid vs <2 s for classical), highlighting practical runtime barriers in current implementations.
## Contradictions
- The paper claims improved predictive performance (higher recall and F1) for the hybrid quantum-LSTM, but classical LSTM baseline is far faster in training and inference (avg epoch <2 s and inference 0.07 s vs hybrid 45–65 s and inference 6.32 s), undermining practical advantage.
- Scalability is questionable: reported experiments are limited to 10–12 qubits and up to 35k synthetic samples on a statevector simulator; large increases in dataset size and qubit count lead to substantial runtime increases, contradicting any implication of immediate scalability to production workloads.
## Notable quotes
<!-- Researcher-added — verbatim quotes with page references -->

## Researcher notes
<!-- Researcher-added — not LLM generated -->
