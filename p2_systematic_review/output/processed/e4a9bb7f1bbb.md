---
aliases:
- Exploring Quantum Machine Learning Algorithms for Enhanced Data Classification and
  Clustering in Complex Systems - Integration with Gradient Boosting and K-means for
  Improved Performance
- Exploring Quantum Machine Learning
authors:
- M. Babu
- A. Muthukrishnan
- M. Arun
- N. Poongavanam
- S. Pushparani
auto_detected: true
classification: ''
contradiction_flags:
- contradiction:classical-vs-quantum
- contradiction:scalability
doi: 10.1109/CYBERCOM63683.2024.10803157
evaluation_type: real-hardware
evidence_type: ''
has_quantitative_results: true
idea_tags:
- idea:quantum-advantage
- idea:near-term-feasibility
- idea:hybrid-approach
journal_or_venue: 2024 International Conference on Cybernation and Computation (CYBERCOM)
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
step1_date: '2026-04-14T12:13:18.175622'
step1_model: gpt-5-mini
step2_date: '2026-04-14T12:13:18.175622'
step2_model: gpt-5-mini
step3_date: '2026-04-14T12:13:18.175622'
step3_model: gpt-5-mini
step4_date: '2026-04-14T12:13:18.175622'
step4_model: gpt-5-mini
step5_date: '2026-04-14T12:13:18.175622'
step5_model: gpt-5-mini
step6_date: '2026-04-14T12:13:18.175622'
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
- method/quantum-ml
- method/hybrid-quantum-classical
- idea/quantum-advantage
- idea/near-term-feasibility
- idea/hybrid-approach
- contradiction/classical-vs-quantum
- contradiction/scalability
title: Exploring Quantum Machine Learning Algorithms for Enhanced Data Classification
  and Clustering in Complex Systems - Integration with Gradient Boosting and K-means
  for Improved Performance
topic_tags:
- quantum-ml-finance
year: '2024'
zotero_key: ''
---

## Abstract summary
This paper investigates hybrid quantum-classical machine learning approaches—including Quantum SVM, Quantum Boosting, and Quantum K-means—integrated with classical Gradient Boosting and K-means to improve classification and clustering on healthcare, financial, and cybersecurity datasets. Experiments implemented in Qiskit show the quantum-enhanced models achieve higher accuracy, faster training times, and improved clustering performance compared to classical counterparts, while noting that quantum ML remains in early stages and requires further hardware and algorithmic development.
## Methodology
The study implements a hybrid quantum-classical approach to improve classification and clustering on three complex datasets (healthcare EHR, financial stock-market data with technical indicators, and cybersecurity network traffic). The pipeline begins with dataset selection and preprocessing (not detailed), then applies quantum-enhanced algorithms for classification and clustering: Quantum Support Vector Machine (QSVM) and a Quantum-augmented Gradient Boosting (referred to as Quantum Boosting) for classification, and Quantum K-means for clustering. Classical counterparts (SVM, Gradient Boosting, K-means) are implemented using scikit-learn and XGBoost for benchmarking. Quantum components are implemented in Qiskit and experiments are first run on quantum simulators and subsequently executed on real IBM Quantum Experience hardware (5-qubit and 16-qubit processors). Evaluation metrics include classification accuracy, clustering accuracy, training time, and resource utilization. Performance comparisons against classical baselines are reported (accuracy, time, resource usage) to demonstrate claimed improvements of the quantum-augmented methods.

**Algorithms used:** Quantum Support Vector Machine (QSVM), Quantum Boosting (quantum-enhanced Gradient Boosting), Quantum K-means, Classical SVM, Gradient Boosting, K-means, XGBoost
**Frameworks:** Qiskit, scikit-learn, XGBoost, Python, IBM Quantum Experience (as backend)

**Experimental setup:** Initial development and testing on Qiskit quantum simulators; subsequent experiments executed on IBM Quantum Experience hardware including 5-qubit and 16-qubit processors. Classical algorithms run with scikit-learn/XGBoost in Python. Models benchmarked by accuracy, clustering accuracy, training time (seconds), and resource utilization (%).

**Dataset:** Financial dataset: stock market historical prices and derived technical indicators (used alongside healthcare EHR and cybersecurity network-traffic datasets). Exact source and sizes are not specified in the paper.
## Experiment details
### Input
{'domain': 'finance', 'description': 'Stock market historical prices and technical indicators (financial dataset used for classification experiments).', 'source': None, 'size': None, 'preprocessing': None}

### Process
{'steps': ['Select three domain datasets: healthcare (EHR), finance (stock prices + indicators), cybersecurity (network traffic).', 'Implement classical baselines: SVM, Gradient Boosting, K-means using scikit-learn and XGBoost.', 'Implement quantum-enhanced models in Qiskit: QSVM for classification, Quantum Boosting (hybrid boosting using quantum classifiers), and Quantum K-means for clustering.', 'Run experiments first on Qiskit simulators for development and validation.', 'Deploy and run selected experiments on IBM Quantum Experience hardware (5-qubit and 16-qubit devices) to compare simulator vs real-device performance.', 'Evaluate models using metrics: classification accuracy, clustering accuracy, training time, and resource utilization; compare quantum models against classical baselines.'], 'parameters_and_iterations': 'Not specified in the paper (no details on circuit depth, number of shots, optimizers, training iterations, hyperparameter settings or exact quantum-classical hybrid training loop).'}

### Output
{'metrics': ['classification_accuracy', 'clustering_accuracy', 'training_time_seconds', 'resource_utilization_percent'], 'baselines': ['Classical SVM', 'Gradient Boosting', 'Classical K-means'], 'representative_results_reported': [{'summary_table': {'Classical SVM_accuracy_percent': 85, 'Quantum SVM_accuracy_percent': 91, 'Gradient_Boosting_accuracy_percent': 89, 'Quantum_Boosting_accuracy_percent': 94}}, {'per_domain_examples': [{'healthcare': {'Classical SVM_accuracy_percent': 92, 'QSVM_accuracy_percent': 96}}, {'finance': {'Gradient_Boosting_accuracy': 0.9, 'Quantum_Boosting_accuracy': 0.95}}, {'cybersecurity_clustering': {'Classical_K-means_accuracy_percent': 80, 'Quantum_K-means_accuracy_percent': 89}}]}, {'training_time_seconds': {'Classical_SVM': 120, 'Quantum_SVM': 100, 'Gradient_Boosting': 150, 'Quantum_Boosting': 110}}, {'resource_utilization_percent': {'Classical_models': 75, 'Quantum_models': 90}}], 'output_format': 'Reported as comparative tables and plots of accuracy, clustering accuracy, training time (s), and resource utilization (%) across quantum and classical models.'}

### Parameters
N/A

### Hardware
{'simulator': 'Qiskit simulator (IBM Qiskit)', 'qpu_models': ['IBM 5-qubit processor', 'IBM 16-qubit processor'], 'cloud_provider': 'IBM Quantum Experience'}

### Reproducibility
N/A
## Findings
- [supported] The authors implemented hybrid quantum-classical models (QSVM, Quantum Boosting, Quantum K-means) and evaluated them on three complex datasets (healthcare EHR, financial time series, cybersecurity network traffic).
- [supported] Quantum models in the experiments produced higher classification accuracy than the corresponding classical models (tables and per-dataset examples reported).
- [supported] Quantum clustering (Quantum K-means) produced higher clustering accuracy than classical K-means on the cybersecurity dataset in the reported experiments.
- [supported] Quantum models in the reported experiments required less training time than the classical counterparts.
- [supported] The authors report higher resource utilization for quantum models (90%) versus classical models (75%).
- [speculative] The paper attributes the observed performance improvements to quantum phenomena (superposition, entanglement, interference) enabling faster search of the solution space and better handling of high-dimensional data.
- [speculative] The authors claim that hybrid quantum-classical integration is a promising basis for further developments in machine learning and real-world applications (finance, healthcare, cybersecurity).
- [speculative] The paper suggests quantum-augmented Gradient Boosting (Quantum Boosting) reduces overfitting and improves classification in complex datasets.
- [disputed] The paper asserts that higher resource utilization reported for quantum models indicates better resource efficiency; this interpretation conflicts with the usual meaning of higher utilization and is internally inconsistent.
- [supported] The authors acknowledge that quantum machine learning is in its infancy and that further hardware and algorithmic developments are needed.

**Results summary:** The paper reports a small-scale empirical evaluation of quantum-augmented ML methods (QSVM, Quantum Boosting, Quantum K-means) versus classical baselines on healthcare, finance, and cybersecurity datasets. Reported results show the quantum models achieved higher classification and clustering accuracies and faster training times than classical SVM, Gradient Boosting, and K-means. The authors attribute improvements to quantum computational properties and advocate hybrid quantum-classical approaches, while noting the field remains nascent and further work on hardware and algorithms is required. The paper also reports higher resource utilization for quantum models and interprets this as improved resource efficiency.

**Performance claims:**
- [supported] Overall table: Classical SVM accuracy 85% vs Quantum SVM 91%.
- [supported] Overall table: Gradient Boosting accuracy 89% vs Quantum Boosting 94%.
- [supported] Per-dataset example (healthcare): QSVM 96% vs classical SVM 92%.
- [supported] Per-dataset example (financial): Quantum Boosting 95% vs classical Gradient Boosting 90%.
- [supported] Clustering (Table II): Classical K-means 78% vs Quantum K-means 85% on the cybersecurity dataset (the text also mentions other clustering numbers such as 89% vs 80% and 90% vs 82% in different places).
- [supported] Training time (Table III): Classical SVM 120s vs Quantum SVM 100s.
- [supported] Training time (Table III): Gradient Boosting 150s vs Quantum Boosting 110s.
- [supported] Resource utilization (Table 4): Classical models 75% vs Quantum models 90%.
## Quantum advantage claim
**Classification:** demonstrated

The paper presents empirical results claiming that quantum-augmented models (QSVM, Quantum Boosting, Quantum K-means) achieved higher accuracy and faster training times than classical baselines on three tested datasets, and attributes these gains to quantum computational properties; however, the work is limited in scope and contains interpretive inconsistencies (e.g., equating higher resource utilization with greater efficiency).
## Limitations
- QML is still at its infancy and there is much work to be done in terms of further improvement of quantum sensors as well as adaption and optimization of the used algorithms for quantum hardware.
- Quantum computers themselves are not yet mature and the infrastructure needed to execute large-scale quantum machine learning models is limited.
- Experiments were planned initially on simulators and on small-scale devices (IBM 5-qubit and 16-qubit processors), limiting the experimental scale and realism.
- [inferred] Paper lacks detailed descriptions of datasets (sizes, features, preprocessing) and experimental protocols, hindering reproducibility.
- [inferred] No statistical significance testing, confidence intervals, or variance reporting for reported accuracy/time metrics.
- [inferred] Evaluation appears to rely largely on simulators or small NISQ devices; results may not generalize to noisy real-world quantum hardware.
- [inferred] Limited baseline comparisons: only a few classical algorithms (SVM, Gradient Boosting, K-means) are used as comparators rather than a broader set of state-of-the-art classical methods.
- [inferred] Claims about resource utilization and computational efficiency are not fully substantiated or clearly defined (e.g., what 'resource utilization' measures and how it's measured).
- [inferred] Scalability claims are asserted but not demonstrated for truly large/high-dimensional datasets beyond available qubit counts.
- [inferred] Hyperparameter tuning, model selection procedures, and risk of overfitting are not explained, which may affect the validity of performance comparisons.
- [inferred] Implementation and reproducibility details (code, seeds, hardware/backend configurations) are not provided.
## Open questions
- How should quantum algorithms be adapted and optimized to run effectively on current and near-term quantum hardware?
- At what data size, dimensionality, or problem structure does a practical quantum advantage over classical ML methods emerge?
- What are the precise resource and cost trade-offs (qubits, circuit depth, runtime, energy) when deploying QML versus classical ML in production settings?
- How do quantum-enhanced models perform on noisy real quantum devices compared to ideal simulators, and how robust are they to hardware noise?
- What are best practices for encoding high-dimensional classical data into quantum representations (feature maps/embeddings) for finance and other domains?
- How can hybrid quantum-classical architectures be designed and tuned for optimal integration (e.g., where to place quantum subroutines within classical pipelines)?
- How should benchmarking and standardized evaluation frameworks be established for fair comparison between quantum and classical ML approaches?
- How to quantify uncertainty, interpretability, and explainability of predictions produced by quantum machine learning models?
- What measures are needed to avoid overfitting and ensure generalization in quantum-augmented training procedures?
- How transferable are the reported improvements across different domains and dataset characteristics (e.g., structured vs unstructured financial data)?

**Future work:**
- Performing experiments on real quantum hardware (IBM 5-qubit and 16-qubit processors) in addition to simulators to validate results.
- Evaluating scalability of quantum-classical hybrid methods on larger and higher-dimensional datasets.
- Further integration of quantum and classical models to improve classification and clustering performance in complex systems.
- Adapting and optimizing quantum algorithms specifically for available quantum hardware (circuit optimization, noise mitigation).
- Advancing quantum hardware/sensors and the supporting infrastructure to enable larger-scale QML applications.
- Developing and testing algorithmic variants (e.g., Quantum Boosting, Quantum K-means) tailored to practical ML subtasks.
## Key ideas
- #idea:quantum-advantage — Hybrid quantum-classical QSVM, Quantum Boosting and Quantum K-means report higher accuracy than classical baselines on the presented datasets (e.g., QSVM 91% vs classical SVM 85%, Quantum Boosting 94% vs Gradient Boosting 89%).
- #idea:hybrid-approach — The pipeline integrates quantum components (QSVM, Quantum Boosting, Quantum K-means) with classical preprocessing and classical learners (XGBoost, scikit-learn) to form a practical hybrid workflow.
- #idea:near-term-feasibility — Experiments were run on Qiskit simulators and on IBM Quantum Experience hardware (5-qubit and 16-qubit devices), with reported faster training times for quantum models (e.g., Quantum_SVM 100s vs Classical_SVM 120s).
- #limitation:qubit-count — Experiments are limited to small devices (5 and 16 qubits), constraining problem sizes and raising questions about applicability to production-scale financial datasets.
- #limitation:noise — Real-device runs are presented but the paper lacks discussion of error mitigation or noise impacts, leaving uncertainty about how noise influenced reported gains.
- #limitation:data-encoding — The paper omits dataset sizes, encoding/preprocessing details and circuit/hyperparameter settings, making it unclear how classical data were embedded and whether results are reproducible.
## Contradictions
- contradiction:classical-vs-quantum — The paper claims clear quantum superiority on accuracy and training time, but provides insufficient experimental detail (no dataset sizes, preprocessing, hyperparameter tuning, or optimizer/circuit settings). This raises the possibility that classical baselines were not optimally tuned or that results do not generalize beyond the small, unspecified datasets used.
- contradiction:scalability — The authors present near-term feasibility based on runs on 5- and 16-qubit devices, yet make broader claims about improved performance on complex financial data. The very small qubit counts and lack of discussion on encoding overhead and scaling contradict claims that the approach will scale to realistic, high-dimensional financial problems.
- contradiction:classical-vs-quantum — Reported higher resource utilization for quantum models (90% vs 75%) alongside faster training times is internally ambiguous: higher utilization could reflect device constraints or overheads rather than an intrinsic efficiency advantage, contradicting the assertion of straightforward speed/resource benefits.
## Notable quotes
<!-- Researcher-added — verbatim quotes with page references -->

## Researcher notes
<!-- Researcher-added — not LLM generated -->
