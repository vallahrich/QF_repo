---
aliases:
- 'Toward Efficient Credit Card Fraud Detection: Leveraging Quantum Neural Networks
  and Modified Feature Selection Techniques'
- Toward Efficient Credit Card
authors:
- Deepa N
- Jayaraj R
- Suguna M
- Sireesha Nanduri
- Banda SNV Ramana Murthy
- Jebakumar Immanuel D
auto_detected: true
classification: ''
contradiction_flags:
- contradiction:classical-vs-quantum
- contradiction:scalability
doi: 10.53759/7669/jmc202505024
evaluation_type: benchmark-comparison
evidence_type: ''
has_quantitative_results: true
idea_tags:
- idea:quantum-advantage
- idea:near-term-feasibility
- idea:hybrid-approach
journal_or_venue: Journal of Machine and Computing
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
- topic/quantum-ml-finance
- topic/fraud-detection
- method/variational-nisq
- method/quantum-ml
- method/hybrid-quantum-classical
- idea/quantum-advantage
- idea/near-term-feasibility
- idea/hybrid-approach
- contradiction/classical-vs-quantum
- contradiction/scalability
title: 'Toward Efficient Credit Card Fraud Detection: Leveraging Quantum Neural Networks
  and Modified Feature Selection Techniques'
topic_tags:
- quantum-ml-finance
- fraud-detection
year: '2025'
zotero_key: ''
---

## Abstract summary
The paper proposes a credit card fraud detection framework that combines a single-qubit based deep quantum neural network (with parameterized convolutional filters to preserve spatial relationships) and a Modified Shuffled Frog Leaping Algorithm (MSFLA) for feature selection. Evaluated on the Kaggle credit card dataset, the approach emphasizes qubit-efficient designs for NISQ devices and reports improved classification metrics (e.g., ~97.06% accuracy, higher precision/recall/F1) compared to several classical deep learning models.
## Methodology
The study develops a hybrid classical–quantum approach for credit card fraud detection. It uses the publicly referenced Kaggle credit card fraud dataset (284,807 transactions, 491 frauds) as the target data. Data preprocessing included cleaning (removing nulls), normalization, removal of features with >50% missing values, removal of near-constant / similar-valued features, and exclusion of high-cardinality categorical/text features (>30 categories). Feature selection is performed using a Modified Shuffled Frog Leaping Algorithm (MSFLA) variant: population initialization, memeplex separation, iterative global search and differentiated local searches within memeplexes, memory T for good solutions, multiple neighborhood operators (N1..N6), and periodic population reshuffling. MSFLA hyperparameters reported or tuned by trials include |T|_max=200, η=0.4, β1=0.4, β2=0.1 and a γ set as 0.1*|T|_max. Selected features are then fed to a single-qubit-based deep quantum neural network arranged as a quantum-convolutional pipeline: the original 2D data is processed by an F×F sliding filter; each F×F patch is encoded onto a single qubit using a sequence of parameterized single-qubit rotations (filter uses a small shared parameter set—six parameters matching θ and φ) applied in a row-wise encoding order; after unitary encoding the qubit state is compared (via fidelity) to target class states and a fidelity-based loss (1/(2D) sum of squared differences between predicted fidelities and target fidelities) is minimized. The classification output picks the class with highest fidelity. The experimental evaluation used 10-fold cross-validation on classical hardware, comparing the proposed pipeline to classical baselines (CNN, DBN, ELM, LSTM, RNN) and reporting accuracy, precision, recall and F1-score. No quantum hardware/SaaS provider or quantum SDK is named in the manuscript.

**Algorithms used:** Modified Shuffled Frog Leaping Algorithm (MSFLA), Single-qubit-based Deep Quantum Neural Network (single-qubit quantum CNN / quantum-convolutional encoding), Classical baselines: CNN, Classical baselines: Deep Belief Network (DBN), Classical baselines: Extreme Learning Machine (ELM), Classical baselines: Long Short-Term Memory (LSTM), Classical baselines: Recurrent Neural Network (RNN)

**Experimental setup:** Software: Python on 64-bit Windows 10; Evaluation: 10-fold cross-validation. Hardware: Intel Xeon CPU E3-1241 v3 @ 3.5 GHz, 16 GB RAM, 4 GB GPU. No quantum simulator or quantum cloud/hardware provider is specified.

**Dataset:** Kaggle credit card fraud dataset (mlg-ulb/creditcardfraud). Reported size: 284,807 transactions with 491 fraudulent transactions; features include Time, Amount, Class and PCA-transformed features V1..V21.
## Experiment details
### Input
Source: Kaggle (https://www.kaggle.com/mlg-ulb/creditcardfraud). Dataset size: 284,807 records; fraud cases: 491 (≈0.172%). Preprocessing: removed nulls and features with >50% missing values, removed near-constant/similar-valued features, excluded text/categorical features with >30 categories, normalized numeric fields. The dataset already contains PCA-transformed features (V1..V21); Time, Amount and Class left intact. Feature selection applied via MSFLA prior to classification.

### Process
Pipeline: (1) Data collection from Kaggle; (2) Data cleaning and normalization, removal of problematic features; (3) Feature selection using MSFLA (population initialization, memeplex partitioning, iterative global and differentiated local searches, memory T for elite solutions, neighborhood operators N1..N6, population reshuffling); (4) Classification using a single-qubit quantum-convolutional encoding: slide F×F filter over 2D data, encode each F×F patch onto a single qubit via sequential parameterized rotations (shared filter parameter set of six trainable parameters), measure fidelity of encoded qubit to class target states, compute fidelity-based loss (equation provided) and train parameters to minimize loss; (5) Model evaluation via 10-fold cross-validation comparing to classical baselines (CNN, DBN, ELM, LSTM, RNN). Reported iterations/looping are implied in MSFLA and training but exact epoch counts, quantum circuit depths, shot counts and optimizers are not specified in the text.

### Output
Outputs reported as classification performance metrics: Accuracy, F1-score, Recall, Precision. Baselines compared: CNN, DBN, ELM, LSTM, RNN. Reported best results for proposed model: Accuracy 97.06%, F1 96.94, Recall 96.67, Precision 97.23. Other baseline metric values are listed in a comparison table.

### Parameters
- qubits: 1
- filter_parameters_per_kernel: 6
- MSFLA: {'T_max': 200, 'eta': 0.4, 'beta1': 0.4, 'beta2': 0.1, 'gamma_factor': 0.1}
- cross_validation_folds: 10
- depth: None
- shots: None
- optimizer: None
- learning_rate: None
- batch_size: None

### Hardware
N/A

### Reproducibility
No code repository or implementation artifacts are provided in the manuscript. The dataset reference (Kaggle mlg-ulb/creditcardfraud) is cited. The Data Availability statement paradoxically says 'No data was used to support this study' despite describing the Kaggle dataset; this contradiction and the absence of code or explicit quantum simulator details hinder exact reproducibility. Key MSFLA hyperparameters and some internal parameter values are reported, but quantum circuit specifics (circuit depth, gate sequence details, optimizer, shot counts, framework) are not provided.
## Findings
- [supported] The proposed single-qubit quantum CNN combined with a Modified Shuffled Frog Leaping Algorithm (MSFLA) feature selection scheme achieves the best reported classification performance in the paper's experiments.
- [supported] The paper reports the proposed model attained accuracy 97.06%, F1-score 96.94%, recall 96.67%, precision 97.23% on their experiments.
- [supported] In the paper's comparative experiments the proposed model outperformed the listed classical baselines (CNN, LSTM, RNN, DBN, ELM).
- [supported] MSFLA is used for feature selection and is claimed (and presented) to improve classification results relative to not using it.
- [supported] The authors used a fidelity-based loss (quantum-state fidelity comparisons to target class states) as the training objective for the quantum classifier.
- [supported] The paper provides baseline performance numbers for comparator models: ELM (accuracy 90.55%), DBN (94.85%), LSTM (95.84%), RNN (95.97%), CNN (95.78%).
- [supported] The methods section states experiments used the public Kaggle credit card fraud dataset (284,807 transactions, 491 frauds) and 10-fold cross-validation; hardware/software environment and training setup are described.
- [disputed] The Data Availability statement reads 'No data was used to support this study', which contradicts other parts of the paper that describe experiments on a publicly available dataset.
- [speculative] The paper claims that a single-qubit encoding scheme with parametrized convolutional filters can preserve spatial relationships of input data and be used to build quantum CNNs suitable for NISQ-era systems.
- [speculative] The authors claim that reducing the number of trainable parameters per filter (to six parameters in their design) is sufficient to obtain good classification performance with the single-qubit approach.
- [speculative] The paper suggests that per-qubit optimization should be prioritized before scaling to larger qubit counts on NISQ devices (a general methodological recommendation rather than a demonstrated empirical result).
- [speculative] The authors state that the proposed model is computationally efficient and well-suited to integrate diverse base models and complex feature engineering, but no runtime/complexity benchmarks are provided.
- [speculative] The paper recommends future research directions including adaptive/streaming sampling methods, adversarial robustness for ML models, and distributed/parallel processing for larger datasets.

**Results summary:** The paper proposes a hybrid approach for credit card fraud detection that combines a Modified Shuffled Frog Leaping Algorithm (MSFLA) for feature selection with a single-qubit-based quantum convolutional neural architecture using a fidelity-based loss. In the authors' experiments (reported on the public Kaggle credit card fraud dataset with 10-fold cross-validation), the proposed model achieved higher classification metrics than several classical baselines: accuracy 97.06%, F1 96.94%, recall 96.67%, and precision 97.23%. Baseline comparators reported lower performance (e.g., CNN ~95.78% accuracy, LSTM ~95.84%, RNN ~95.97%, DBN ~94.85%, ELM ~90.55%). The paper emphasizes methodological design decisions for single-qubit encoding (parametrized filters, six-parameter filters) and argues these choices can preserve spatial information without expensive flattening, while noting future needs for robustness, streaming adaptation, and scalability. However, the manuscript contains an internal contradiction in its Data Availability statement ('No data was used to support this study') versus explicit claims of dataset usage and experimental results.

**Performance claims:**
- Proposed model — Accuracy: 97.06%, F1-score: 96.94%, Recall: 96.67%, Precision: 97.23% [supported]
- CNN baseline — Accuracy: 95.78%, F1-score: 95.93%, Recall: 95.71%, Precision: 96.16% [supported]
- LSTM baseline — Accuracy: 95.84%, F1-score: 95.78%, Recall: 94.76%, Precision: 96.86% [supported]
- RNN baseline — Accuracy: 95.97%, F1-score: 95.07%, Recall: 94.07%, Precision: 95.08% [supported]
- DBN baseline — Accuracy: 94.85%, F1-score: 93.13%, Recall: 93.09%, Precision: 93.17% [supported]
- ELM baseline — Accuracy: 90.55%, F1-score: 90.22%, Recall: 90.55%, Precision: 90.75% [supported]
## Quantum advantage claim
**Classification:** speculative

The paper claims better classification performance using a single-qubit quantum-inspired CNN design (reported higher accuracy and F1 than classical baselines in their experiments), but it does not demonstrate a hardware-level quantum advantage (no runs on quantum hardware, no complexity/speedup proofs, and no ablation isolating quantum-specific benefits). Thus any asserted 'quantum advantage' remains speculative based on the presented simulation/algorithmic results.
## Limitations
- Single-qubit encoding supports only a one-level encoding which can be problematic for tasks that rely on spatial information (author-stated).
- Data availability / provenance issue: the paper's Data Availability section states 'No data was used to support this study' despite describing use of the Kaggle credit-card dataset, creating reproducibility concerns (author-stated).
- [inferred] Extreme class imbalance in the dataset (fraud ≈ 0.172%) may limit generalisation and model reliability if imbalance-handling is insufficiently addressed.
- [inferred] Contradictory/unclear dataset/sample reporting (paper cites 284,807 records but also refers to a 'relatively small trial size (995 declarations)') raises concerns about which data subset was used and representativeness.
- [inferred] No experiments or validation reported on real quantum hardware (NISQ devices); the method appears evaluated via classical simulation only, so hardware feasibility is untested.
- [inferred] Robustness to quantum noise and NISQ-era device limitations is not evaluated.
- Adversarial robustness (resistance to hostile/targeted attacks) is not evaluated; the authors explicitly recommend future research on this (author-stated limitation).
- [inferred] Scalability to much larger datasets and higher-dimensional feature spaces is not demonstrated; only a single-machine setup with limited RAM/GPU is described.
- [inferred] Evaluation is limited to accuracy, precision, recall and F1; no AUC-ROC/PR curves, calibration, uncertainty estimates, or statistical significance testing are reported.
- [inferred] Reproducibility is hindered by missing implementation details (complete training/hyperparameter settings, code availability) and the ambiguous data-availability statement.
## Open questions
- How can data sampling methods be made adaptive so the model can accommodate evolving data distributions over time? (author-raised)
- Which approaches will effectively increase the model's robustness to hostile/adversarial attacks against ML or quantum ML systems? (author-raised)
- How will the proposed model scale as dataset sizes grow and processing requirements increase, and what distributed/parallel computing strategies are most suitable? (author-raised)
- [inferred] Can the single-qubit CNN encoding and the proposed quantum classification pipeline be implemented and validated on real NISQ hardware, and how will device noise affect performance?
- [inferred] What is the impact of using a single shared filter parameter set per F×F region versus using distinct parameter sets per region on accuracy, parameter efficiency, and overfitting?
- [inferred] How does the proposed quantum ML approach compare, on identical data and evaluation protocols, with state-of-the-art classical/transformer models (e.g., BERT/Transformers) and ensemble techniques?
- [inferred] What is the trade-off between number of qubits/encoding strategy (single-qubit vs multi-qubit) and classification performance/resource requirements?
- [inferred] What are the most effective methods to address extreme class imbalance within a quantum ML pipeline (resampling, synthetic sampling, cost-sensitive learning) and how do they interact with quantum encodings?
- [inferred] Are the reported performance gains statistically significant across repeated trials or different data splits?
- [inferred] What are the runtime, computational cost and energy implications of the quantum ML approach compared to classical baselines in practical deployments?

**Future work:**
- Research into adaptive data sampling methods that can be updated to accommodate evolving data distributions (author-suggested).
- Investigate approaches to increase the proposed model's resilience to hostile/adversarial attacks (author-suggested).
- Evaluate how the model performs as dataset sizes grow and processing demands increase; explore use of distributed computing or parallel processing for efficient scaling (author-suggested).
- [inferred] Explore alternative filter parameterisations for the single-qubit convolutional approach (e.g., per-region parameter sets vs shared parameters) as noted by the authors as an avenue for future study.
- [inferred] Validate the method on real quantum hardware (NISQ devices) and study noise mitigation/robustness techniques.
## Key ideas
- #idea:quantum-advantage — The proposed single-qubit quantum-convolutional encoding + training pipeline achieves higher reported classification metrics (Accuracy 97.06%, F1 96.94%) than listed classical baselines on the Kaggle credit-card-fraud dataset.
- #idea:hybrid-approach — A classical Modified Shuffled Frog Leaping Algorithm (MSFLA) is used for feature selection prior to the single-qubit quantum neural network, highlighting a hybrid classical–quantum pipeline
- #idea:near-term-feasibility — The authors emphasize a qubit-efficient, single-qubit design intended for NISQ-era applicability (parameterized single-qubit rotations, shared small parameter set per filter)
- #idea:hybrid-approach — The model leverages classical preprocessing, population-based feature selection, and a fidelity-based loss on single-qubit encodings to reduce quantum resource requirements
- #idea:quantum-advantage — Reported improvement over multiple classical models suggests potential practical benefit, but the improvement source (quantum encoding vs. MSFLA/other engineering) is not experimentally disentangled
## Contradictions
- contradiction:classical-vs-quantum — The paper claims quantum advantage but presents experiments run on classical hardware with no named quantum simulator or QPU; without running on quantum hardware or specifying a quantum execution backend, the claimed advantage may result from classical emulation, preprocessing (MSFLA), or modeling choices rather than genuine quantum effects.
- contradiction:scalability — The authors argue NISQ feasibility via a single-qubit design for large, high-dimensional datasets but do not address encoding overhead, circuit depth, shot counts, or how sequential single-qubit encodings scale computationally; this undermines claims that the approach scales efficiently to real-world deployment.
- contradiction:classical-vs-quantum — The Data Availability statement asserts 'No data was used to support this study' despite explicit use of the Kaggle credit card dataset, introducing inconsistency that reduces confidence in experimental reporting and reproducibility.
## Notable quotes
<!-- Researcher-added — verbatim quotes with page references -->

## Researcher notes
<!-- Researcher-added — not LLM generated -->
