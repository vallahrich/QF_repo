---
aliases:
- An Empirical Study on Enhancing Explainability through Quantum Machine Learning
  for Credit Risk Analysis
- Empirical Study Enhancing Explainability
authors:
- Aadrian Routh
- Parvathy Gopakumar
- Rubell Marion Lincy G
auto_detected: true
classification: ''
contradiction_flags: []
doi: 10.1109/FMLDS63805.2024.00084
evaluation_type: simulator
evidence_type: ''
has_quantitative_results: true
idea_tags:
- idea:quantum-advantage
- idea:hybrid-approach
journal_or_venue: 2024 IEEE International Conference on Future Machine Learning and
  Data Science (FMLDS)
methodology_tags:
- quantum-ml
- hybrid-quantum-classical
paper_type: ''
quantum_advantage_claim: demonstrated
related_papers: []
relevance_phase1: high
relevance_phase3: high
source_type: conference-paper
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
- topic/credit-lending
- method/quantum-ml
- method/hybrid-quantum-classical
- idea/quantum-advantage
- idea/hybrid-approach
title: An Empirical Study on Enhancing Explainability through Quantum Machine Learning
  for Credit Risk Analysis
topic_tags:
- quantum-ml-finance
- credit-lending
year: '2024'
zotero_key: ''
---

## Abstract summary
This paper investigates combining classical and quantum machine learning methods for credit score classification, including data preprocessing, exploratory data analysis, and dimensionality reduction with KPCA. It compares a classical SVC baseline with Quantum Support Vector Classifiers using ZZFeatureMap, PauliFeatureMap and a combined ZZPauliMap, and applies LIME to improve interpretability; the hybrid quantum feature map notably improved QSVC performance versus individual quantum maps and approached or exceeded classical performance after tuning.
## Methodology
The study conducts an empirical comparison of classical and quantum approaches for credit score classification. The pipeline begins with data loading (Kaggle Credit Score Classification dataset), label-encoding of categorical variables and standard scaling of numerical features. Exploratory Data Analysis (pair plots) is performed followed by dimensionality reduction using Kernel PCA (with RBF kernel). A classical Support Vector Classifier (SVC) is trained as a baseline using a train/test split and evaluated with cross-validation and grid-search hyperparameter tuning. For the quantum approach, multiple quantum feature maps (ZZFeatureMap, PauliFeatureMap and a combinational ZZPauliMap) are implemented to construct a quantum kernel; the combinational map is described mathematically as layers of single-qubit rotations RX/RY/RZ followed by entangling ZZ terms exp(i γ x_i x_j Z_i Z_j) repeated for L layers. A Quantum Support Vector Classifier (QSVC) is trained using the quantum kernel; stratified k‑fold cross-validation and grid search are used for model selection. Model interpretability is addressed by applying LIME to the QSVC predictions and aggregating local feature importances. Reported experiments include configurations with the ZZPauliMap using 3 repetitions and linear entanglement, comparisons of test accuracies between classical SVC and QSVC variants, ROC plotting, and LIME-based feature importance (Income identified as top feature).

**Algorithms used:** Support Vector Classifier (SVC), Kernel Principal Component Analysis (KPCA), Quantum Support Vector Classifier (QSVC), ZZFeatureMap, PauliFeatureMap, ZZPauliMap (hybrid quantum feature map), Grid Search (hyperparameter tuning), Stratified k-fold Cross-Validation, LIME (Local Interpretable Model-agnostic Explanations)
**Frameworks:** Qiskit (qiskit-machine-learning / qiskit circuit library referenced), scikit-learn, LIME (explainability library referenced implicitly)

**Dataset:** Kaggle 'Credit Score Classification' dataset (features include Age, Gender, Income, Education, Marital Status, Number of Children, Home Ownership; target: Credit Score). Exact dataset size not specified in paper.
## Experiment details
### Input
{'source': 'Kaggle - https://www.kaggle.com/datasets/sujithmandala/credit-score-classification-dataset', 'size': None, 'features': ['Age', 'Gender', 'Income', 'Education', 'Marital Status', 'Number of Children', 'Home Ownership', 'Credit Score (target)'], 'preprocessing': ['Label encoding of categorical variables', 'Standard scaling (zero mean, unit variance) of numerical features', 'Kernel PCA (RBF kernel) for dimensionality reduction prior to modelling']}

### Process
{'steps': ['Load dataset and perform EDA (pair plots).', 'Encode categorical variables and standardize numerical features.', 'Apply Kernel PCA (RBF kernel) to reduce dimensionality.', 'Split data into training and test sets (split ratio not specified).', 'Train classical SVC baseline; perform grid search and cross-validation for hyperparameter tuning.', 'Construct quantum kernels using ZZFeatureMap, PauliFeatureMap, and a combined ZZPauliMap (multi-layer feature map of RX/RY/RZ rotations and ZZ entangling gates).', 'Train QSVC using the constructed quantum kernel(s); evaluate with stratified k-fold cross-validation and grid search for hyperparameter selection.', 'Aggregate results, plot ROC for QSVC, and apply LIME to obtain local feature importances and aggregate them.'], 'notable_parameters_or_choices': {'KPCA_kernel': 'RBF (Radial Basis Function)', 'quantum_feature_map': 'ZZFeatureMap, PauliFeatureMap, ZZPauliMap (combined)', 'ZZPauliMap_configuration': '3 repetitions and linear entanglement (reported)', 'cross_validation': 'stratified k-fold (k not specified)', 'hyperparameter_search': 'grid search (parameter grid not specified)'}, 'iterations_or_repetitions': 'ZZPauliMap tested with 3 repetitions; number of CV folds and other iteration counts not specified.'}

### Output
{'metrics_reported': {'classical_SVC': {'training_accuracy': 'approx. 79%', 'test_accuracy_before_cv_tuning': None, 'test_accuracy_after_cv_tuning': 'approx. 78.7%'}, 'quantum_QSVC': {'ZZFeatureMap_or_PauliFeatureMap_individual': '75.7% (initial test accuracy)', 'ZZPauliMap': {'before_cv_tuning': '78.7%', 'after_cv_tuning': '84.8%'}}, 'explainability': {'LIME_feature_importance': {'Income': 'average importance 0.33 (highest ranked feature)'}}, 'plots': ['Pair plots (EDA)', 'ROC curve for QSVC', 'LIME aggregated feature importance plot']}, 'baselines': ['Classical SVC (baseline referenced and compared)'], 'output_format': 'Classification accuracies, ROC curve, aggregated LIME feature importance scores'}

### Parameters
- n_qubits: None
- feature_map_repetitions: 3
- entanglement: linear
- feature_map_type: ZZPauliMap (combined RX/RY/RZ and ZZ entanglers)
- KPCA_kernel: RBF
- layers_L: None
- shots: None
- optimizer: None
- quantum_parameter_names: ['theta1, theta2, theta3 (single-qubit rotation angles)', 'gamma (entangling interaction strength)']
- notes_on_unspecified: Many low-level quantum/hyperparameter settings (qubit count, circuit depth/layers, shots, optimizer, CV folds, exact grid-search parameter ranges) are not specified in the paper.

### Hardware
N/A

### Reproducibility
Dataset is public on Kaggle (link provided). The paper references Qiskit and scikit-learn but does not provide code, exact train/test split ratios, CV fold count, hyperparameter grids, or low-level quantum execution details (qubit count, simulator vs real QPU, shots). These omissions limit full reproducibility without contacting the authors or re-implementing with unstated choices.
## Findings
- [supported] A classical Support Vector Classifier (SVC) baseline achieved ~79% training accuracy and ~78.7% test accuracy after cross-validation and hyperparameter tuning on the studied credit-score dataset.
- [supported] Quantum Support Vector Classifiers (QSVC) using ZZFeatureMap or PauliFeatureMap individually achieved ~75.7% test accuracy prior to combining feature maps.
- [supported] A combinational quantum feature map (ZZPauliMap) combined with QSVC improved test accuracy to 78.7% (before CV/tuning) and to 84.8% after cross-validation and hyperparameter tuning on the same dataset.
- [supported] KPCA (Kernel PCA) was used for dimensionality reduction as a preprocessing step and reported as part of the modelling pipeline to address high-dimensional data.
- [supported] LIME-based explainability analysis identified Income as the most important feature for the QSVC model, with an average importance score reported as 0.33.
- [speculative] The authors claim that hybrid quantum feature maps (ZZPauliMap) are superior because they capture both local (single-qubit rotations) and global (entangling) interactions, yielding a more expressive quantum feature space.
- [speculative] The paper asserts general advantages of quantum models (enhanced expressiveness, efficient computation leveraging superposition, and potential for improved accuracy) as reasons QML can outperform classical methods in complex/high-dimensional tasks.
- [speculative] Practical adoption of QSVC in financial institutions is limited by current quantum hardware constraints (coherence times, error rates, scalability) and integration overhead with classical infrastructure, according to the authors.

**Results summary:** The study compares classical SVC and quantum SVC approaches on a credit score classification dataset. Classical SVC attained a test accuracy around 78.7% after tuning. QSVC with individual ZZ or Pauli feature maps reached about 75.7% test accuracy, while a combined ZZPauliMap feature map paired with QSVC improved performance substantially, reaching 84.8% after hyperparameter tuning and cross-validation. KPCA was used for dimensionality reduction and LIME provided interpretability, identifying Income as the most influential feature. The authors argue that hybrid quantum feature maps increase expressiveness and that quantum techniques show promise, while noting practical hardware and integration challenges.

**Performance claims:**
- Classical SVC training accuracy ≈ 79%
- Classical SVC test accuracy after cross-validation and tuning ≈ 78.7%
- QSVC with ZZFeatureMap or PauliFeatureMap individually: test accuracy = 75.7% (before combination)
- QSVC with combined ZZPauliMap (3 repetitions, linear entanglement): test accuracy = 78.7% (before CV/tuning)
- QSVC with combined ZZPauliMap after cross-validation and hyperparameter tuning: test accuracy = 84.8%
- LIME feature importance: Income average importance = 0.33
## Quantum advantage claim
**Classification:** demonstrated

The paper reports an empirical improvement in test accuracy using QSVC with a combinational ZZPauliMap (84.8% after tuning) compared to the classical SVC baseline (78.7% after tuning) on their credit-score dataset, which the authors present as evidence of quantum-model performance benefits; however, the result is dataset- and configuration-specific and practical hardware limitations are acknowledged.
## Limitations
- Classical models: scalability, limited expressiveness for complex/non-linear high-dimensional data, and high computational cost for training and hyperparameter tuning (author-stated).
- Quantum hardware immaturity: limited qubit coherence times, high error rates, and current scalability challenges that hinder large-scale application of QSVCs (author-stated).
- High integration and computational overhead for hybrid quantum-classical workflows: preprocessing, kernel construction, interfacing with quantum hardware, and need for high-performance classical resources (author-stated).
- Tuning quantum feature maps (e.g., ZZPauliMap) requires substantial computational resources for hyperparameter optimization and cross-validation (author-stated).
- Interpretability: QSVC and quantum models are difficult to interpret directly, necessitating surrogate explanation methods (LIME), which may have limitations when applied to quantum models (author-stated/inferred).
- Performance variability: QSVC performance depended strongly on the choice of feature map (individual maps performed worse; combinational ZZPauliMap improved accuracy), indicating sensitivity to feature map design (author-stated).
- Dependence on dimensionality reduction/feature engineering (KPCA) to make quantum approaches feasible and effective, implying preprocessing is critical and may limit applicability (author-stated/inferred).
- [inferred] Dataset and evaluation scope limited: the study appears to evaluate models on a single publicly available credit score dataset, limiting generalizability across other financial datasets and market conditions.
- [inferred] Potential reliance on quantum simulators rather than real quantum hardware is implied (practical hardware limitations discussed) but not clarified, raising questions about real-device performance and noise effects.
- [inferred] Regulatory, fairness, and ethical considerations for deploying QML in credit scoring (e.g., bias, explainability for compliance) are mentioned only tangentially (explainability discussed) but not empirically addressed.
- [inferred] Computational cost / latency concerns for real-time or low-latency financial use cases (e.g., real-time credit scoring, high-frequency trading) remain unresolved.
- [inferred] Limited comparison to a broader set of classical baselines and other quantum algorithms — only SVC vs. QSVC (and KPCA) are extensively compared.
## Open questions
- Can quantum machine learning (e.g., QSVC with advanced feature maps) consistently and robustly outperform classical models across diverse financial datasets and real-world conditions?
- How can quantum feature maps be designed or optimized systematically to maximize classification performance while controlling resource requirements?
- What is the best approach to hyperparameter tuning for quantum feature maps and QSVCs given the high computational cost? Are there efficient heuristics or meta-optimization methods suitable for QML?
- How will quantum models behave on real, noisy quantum hardware compared to simulations? What is the impact of hardware noise on QSVC performance and interpretability?
- How can interpretability methods (like LIME) be validated and adapted for quantum models to ensure trustworthy, regulatory-compliant explanations?
- What are the scalability limits of current hybrid quantum-classical pipelines, and what software/hardware co-designs are needed to process large-scale financial datasets?
- How effective are other quantum algorithms (e.g., Quantum Neural Networks, Quantum Bayesian Networks) for credit risk tasks compared to QSVC, and under what conditions do they offer advantages?
- How does dimensionality reduction (e.g., KPCA) interact with quantum feature embeddings — does it remove information critical for the quantum kernel or improve generalization reliably?
- What are the trade-offs between increased expressiveness of combinational quantum maps and the increased complexity/overhead (both computational and hardware) they introduce?
- How do quantum models perform with imbalanced or biased financial datasets and what mitigation strategies are required to ensure fairness and robustness?

**Future work:**
- Investigate a wider array of quantum algorithms, including Quantum Neural Networks (QNNs) and Quantum Bayesian Networks.
- Refine and develop advanced feature engineering techniques to better leverage quantum model strengths.
- Address scalability challenges and optimize quantum models for larger, more complex datasets.
- Continue integrating and evaluating classical preprocessing (e.g., KPCA) with quantum feature maps to improve efficacy.
- Explore further hyperparameter tuning strategies, cross-validation schemes, and optimization methods specific to quantum feature maps and QSVCs.
## Key ideas
- #idea:quantum-advantage — A combined ZZPauliMap quantum feature map in a QSVC achieved reported test accuracy of 84.8% after tuning, exceeding the classical SVC baseline (~78.7%).
- #idea:quantum-advantage — Individual quantum feature maps (ZZ or Pauli) underperformed initially (~75.7%) but the hybrid/combinational map provided marked improvement after hyperparameter tuning.
- #idea:hybrid-approach — Classical preprocessing (label encoding, standard scaling, Kernel PCA) paired with quantum kernels (feature maps implemented in Qiskit) formed the modelling pipeline.
- #idea:hybrid-approach — Classical model-selection tools (stratified k-fold CV, grid search) and explainability methods (LIME) were integrated with the QSVC to improve performance and interpretability.
- #limitation:qubit-count — The paper does not report n_qubits, circuit depth, shots, or other low-level quantum execution parameters, limiting assessment of scalability and resource requirements.
- #limitation:simulation-only — Hardware details are missing (no indication of real-QPU runs), suggesting results were obtained on simulators or at least without reported real-hardware validation.
- #limitation:data-encoding — While quantum feature maps are described, the computational/encoding cost and scalability of mapping tabular credit data to quantum states are not analyzed.
- #limitation:noise — No discussion of noise, error mitigation, or realistic NISQ hardware effects is provided, leaving uncertainty about real-hardware performance.
## Contradictions
<!-- Step 6 output — where this paper contradicts others -->

## Notable quotes
<!-- Researcher-added — verbatim quotes with page references -->

## Researcher notes
<!-- Researcher-added — not LLM generated -->
