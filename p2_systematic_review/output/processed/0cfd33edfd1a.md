---
aliases:
- Empowering Credit Scoring Systems with Quantum-Enhanced Machine Learning
- Empowering Credit Scoring Systems
authors:
- Javier Mancilla
- André Sequeira
- Tomas Tagliani
- Francisco Llaneza
- Claudio Beiza
auto_detected: true
classification: ''
contradiction_flags: []
doi: ''
evaluation_type: simulator
evidence_type: ''
has_quantitative_results: true
idea_tags:
- idea:quantum-advantage
- idea:near-term-feasibility
- idea:hybrid-approach
journal_or_venue: arXiv preprint (arXiv:2404.00015, q-fin.RM)
methodology_tags:
- quantum-ml
- hybrid-quantum-classical
- variational-nisq
paper_type: ''
quantum_advantage_claim: speculative
related_papers: []
relevance_phase1: high
relevance_phase3: high
source_type: preprint
source_type_confidence: high
step1_date: '2026-04-14T09:27:51.115033'
step1_model: gpt-5-mini
step2_date: '2026-04-14T09:27:51.115033'
step2_model: gpt-5-mini
step3_date: '2026-04-14T09:27:51.115033'
step3_model: gpt-5-mini
step4_date: '2026-04-14T09:27:51.115033'
step4_model: gpt-5-mini
step5_date: '2026-04-14T09:27:51.115033'
step5_model: gpt-5-mini
step6_date: '2026-04-14T09:27:51.115033'
step6_model: gpt-5-mini
steps_completed:
- 1
- 2
- 3
- 4
- 5
- 6
tags:
- topic/credit-lending
- topic/quantum-ml-finance
- topic/risk-management
- method/quantum-ml
- method/hybrid-quantum-classical
- method/variational-nisq
- idea/quantum-advantage
- idea/near-term-feasibility
- idea/hybrid-approach
title: Empowering Credit Scoring Systems with Quantum-Enhanced Machine Learning
topic_tags:
- credit-lending
- quantum-ml-finance
- risk-management
year: '2024'
zotero_key: ''
---

## Abstract summary
The paper proposes Systemic Quantum Score (SQS), an end-to-end approach that uses quantum kernels and an evolutionary algorithm to automatically design quantum feature maps for credit scoring. Evaluated on a production-grade Fintonic loan/default dataset, SQS shows improved generalization and better performance than classical baselines (SVC and XGBoost) in scarce, imbalanced-data regimes, suggesting potential near-term usefulness of quantum-enhanced machine learning for finance.
## Methodology
The authors propose Systemic Quantum Score (SQS), an end-to-end pipeline that combines classical preprocessing, quantum kernel design via an evolutionary search over quantum feature maps, and classical kernel-based classification. Starting from a production-grade Fintonic loans dataset, they perform data cleaning, automatic feature engineering (featuretools), feature selection by mutual information (top 10 features) and dimensionality reduction with Linear Discriminant Analysis and standardization to obtain a low-dimensional input (up to 10 dimensions) suitable for quantum encoding. Quantum feature maps are represented as sequences of n-qubit Pauli words (individuals). An evolutionary algorithm (population-based, crossover, mutation, elitism) searches the space of Pauli-word feature-map circuits; each individual is locally optimized further by gradient-based tuning of continuous parameters appended to rotation gates. Fitness is measured by kernel target alignment (comparison of the fidelity kernel matrix to the ideal yy^T target) using spectral criteria (maximum normalized eigenvalue). Kernels (estimated as state-fidelity / trace overlap via the inversion test in simulation) are then used within a support-vector classifier framework (quantum-kernel SVM) and compared against classical baselines (SVC and XGBoost). Experiments evaluate multiple random-seed runs, varying population sizes, qubit counts and number of generations, and examine performance across dataset sizes (downsampled subsets and full data) using AUC as the primary metric.

**Algorithms used:** Quantum kernel methods (QSVC / fidelity kernel), Evolutionary algorithm (genetic search over Pauli-word feature maps), Gradient-based local optimization for continuous gate parameters, Support Vector Classifier (SVC), XGBoost, Featuretools (deep feature synthesis), Linear Discriminant Analysis (LDA), Mutual information feature selection, Optuna (for XGBoost hyperparameter tuning)
**Frameworks:** featuretools, optuna

**Experimental setup:** All quantum-kernel experiments were executed in simulation (no QPU experiments). The pipeline first selects the top 10 engineered features (mutual information), applies LDA to reduce dimensionality (to at most 10, sometimes 2), maps the reduced vector to an n-qubit quantum feature map (n up to 10), and estimates fidelity kernels via the inversion test in simulator. An evolutionary search over Pauli-word sequences (individuals) with population sizes 10/100/1000 and up to 50 generations was used; each individual includes continuous rotation parameters that are locally gradient-optimized. Selected kernels are evaluated by kernel-target alignment and then used with an SVM for classification; baselines are classical SVC and XGBoost. Evaluation uses downsampled dataset sizes (500, 1000, 2000, 3000, full 4763) and AUC metrics, plus a generalization test with a 10%/90% train/test split.

**Dataset:** Proprietary Fintonic / Wanna loans dataset: 4763 loans (2017–2023) with engineered banking features (~350 features originally); class imbalance with approximately 10% positive class (defaults).
## Experiment details
### Input
{'source': 'Fintonic (Wanna) proprietary loan records and aggregated banking transactions', 'size': 4763, 'class_balance': 'approximately 10% positive (defaulters)', 'preprocessing': ['Data cleaning: duplicate removal and imputation of missing fields', 'Automatic feature engineering using featuretools (deep feature synthesis) to produce ~350 features', 'Feature selection by mutual information to select the top 10 features', 'Dimensionality reduction with Linear Discriminant Analysis (LDA) and standardization to at most 10 dimensions (sometimes reduced further to 2 for some quantum experiments)', 'Creation of downsampled experiment subsets: 500, 1000, 2000, 3000, and full dataset']}

### Process
{'pipeline_steps': ['Preprocess and feature-engineer raw transaction and account data (featuretools)', 'Select top features via mutual information and reduce dimensionality with LDA', 'Encode reduced data into quantum feature maps UM(x) defined as sequences of Pauli-word rotations (product of R_mi(x) operations)', 'Represent candidate feature maps as individuals (strings of Pauli words) in an evolutionary algorithm', "Evaluate each individual by constructing the fidelity/kernel matrix (Tr(ρ_x ρ_x')) and computing kernel-target alignment fitness (spectral criterion / maximum normalized eigenvalue)", 'Apply elitist selection, crossover, mutation to produce new generations; complement with local gradient-based optimization of continuous gate parameters α_mi per elite individual', 'Stop when maximumGenerations or target fitness achieved; select best kernel', 'Train a kernel SVM using the selected quantum kernel; compare performance to classical baselines (SVC and XGBoost)', 'Repeat experiments across different dataset sizes (downsampled regimes) and report AUC'], 'iteration_details': {'population_sizes_tested': [10, 100, 1000], 'generations_tested': 'up to 50', 'qubit_counts_tested': [2, 3, 5, 10], 'crossover_and_mutation': 'applied (percentages and exact operators not fully specified)', 'local_optimization': 'gradient-based tuning of continuous rotation parameters added to each rotation gate in the feature map'}}

### Output
{'metrics': ['Area Under ROC Curve (AUC) as primary performance metric', 'Kernel fitness: normalized fitness / kernel-target alignment (reported as mean ± std)', 'Average entangling-block counts of generated circuits'], 'baselines': ['Classical SVC (Support Vector Classifier)', 'XGBoost (gradient boosted trees)'], 'representative_results': {'generalization_test_10pct_train_90pct_test': {'SQS_AUC': 0.658, 'SVC_AUC': 0.638, 'XGBoost_AUC': 0.632}, 'kernel_fitness_examples': 'Normalized fitness values reported in Table 2 (e.g., 0.998 ± 0.004 for 3 qubits, population 100)'}}

### Parameters
- qubit_size_range: [2, 3, 5, 10]
- max_generations: 50
- population_sizes: [10, 100, 1000]
- gene_chain_size: variable / not precisely specified
- elite_size: used but not numerically specified
- crossover: applied, exact operator/ratio not specified
- mutation_percentage: tunable hyperparameter, exact values not specified
- quantum_dimensionality: up to 10 (limited by reduced dataset features)
- average_entangling_blocks_reported: typically between 1 and 3 (see Table 2)
- shots: None
- optimizer_for_local_tuning: gradient-based optimizer (type unspecified)

### Hardware
N/A

### Reproducibility
N/A
## Findings
- [supported] The proposed Systemic Quantum Score (SQS) pipeline (evolutionary search over quantum feature maps + local gradient tuning) can be executed in simulation and produces quantum kernels with high kernel-target alignment (normalized fitness ~0.99) on the Fintonic loan dataset.
- [supported] On the authors' dataset and experimental setup, SQS outperformed a classical SVC and XGBoost in the low-data / scarce-training regime: when training on 10% of the data, SQS achieved AUC=0.658 versus SVC=0.638 and XGBoost=0.632.
- [supported] In down-sampled experiments (500–3000 samples) SQS provided better discrimination than the compared classical models; XGBoost performance improved as more data were added and eventually overtook SQS on the full dataset.
- [supported] Evolutionary search over Pauli-word-based feature-map structures produced a variety of compact feature maps (including low-qubit maps) that achieved high fitness; increasing qubit-count (up to 10 qubits) did not yield clear fitness improvements in these experiments.
- [supported] The pipeline used dimensionality reduction / feature selection to reduce 350 original features to a tractable quantum input (10 features via mutual information, then LDA/standardization to quantumDim ≤10).
- [supported] All experiments reported were run in simulation (no real quantum hardware experiments were performed).
- [speculative] Quantum kernel methods (and SQS specifically) provide an opportunity for industry benefit in early-stage FinTech/Neobank scenarios characterized by scarce, imbalanced, and noisy data, because they may generalize better than data-hungry classical ensembles.
- [speculative] Small quantum feature maps (few qubits / shallow circuits) can match or approach the expressivity needed for classification tasks in finance, potentially replacing more complex classical models when data are scarce.
- [speculative] Evolutionary search over quantum feature-map topologies is an effective automated strategy to discover useful quantum kernels for applied classification tasks.
- [speculative] The observed simulation results indicate an avenue toward near-term usefulness of quantum-enhanced ML (quantum kernels) in specific industrial niches, but not a general, unconditional advantage.

**Results summary:** The paper presents SQS, an automated pipeline that combines an evolutionary algorithm over Pauli-word-based quantum feature maps with local gradient tuning to produce quantum kernels for a loan default prediction task from Fintonic. Using classical simulation and a two-stage feature reduction (mutual information to 10 features, then LDA to ≤10 dimensions), the authors report high kernel-target alignment (normalized fitness ≈0.99) and improved performance in scarce-data regimes: when training on only 10% of the data SQS achieved AUC=0.658 compared to SVC=0.638 and XGBoost=0.632. Down-sampled experiments (500–3000 samples) also favored SQS, while XGBoost overtook SQS on the full dataset. All experiments were simulation-based; no hardware runs were performed. The authors conclude quantum kernels may be especially useful for early-stage financial applications with limited labeled data, while noting scaling and hardware evaluation remain open issues.

**Performance claims:**
- Dataset: 4763 loans, ~350 engineered features; positive (default) class ≈10% of population (paper also refers to extreme generalization test with a 10% training set that contains 1% of original defaulters).
- Training/test split extreme-generalization: training on 10% of the dataset (remaining 90% used for testing).
- AUC (10% training regime): SQS = 0.658, SVC = 0.638, XGBoost = 0.632 (Table 3).
- Downsampled experiments: evaluated at sample counts 500, 1000, 2000, 3000 and full dataset; SQS outperformed SVC and XGBoost in the 500–3000 sample range (no single numeric AUCs given in text for each point).
- Kernel-target alignment (normalized fitness) achieved across multiple runs: typical values reported in Table 2 around 0.960–0.998 (examples: initial population 10, 3 qubits -> 0.992±0.005; initial population 100, 3 qubits -> 0.998±0.004; initial population 1000, 10 qubits -> 0.991±0.03).
- Evolutionary search hyperparameters examples: initial populations of 10, 100, 1000; up to 50 generations evaluated; qubit ranges tested 2–10; gene chain sizes and entangling-block averages reported (e.g., avg entangling blocks 1–3 depending on run).
## Quantum advantage claim
**Classification:** speculative

The authors report simulation results that show SQS (a quantum-kernel-based method discovered via evolutionary search) outperforming classical SVC and XGBoost on a single, domain-specific dataset in low-data regimes. However, experiments were run in classical simulation (no quantum hardware), on a single use case, with dimensionality reduction and limited quantum input size (≤10 qubits). Thus the reported advantage is empirical within the constrained experimental setup but remains speculative as a general quantum advantage for finance; broader demonstration (hardware runs, more datasets, statistical robustness) is not provided.
## Limitations
- Experiments were performed exclusively in simulation; no experiments were run on real quantum hardware (author-stated).
- Feature maps were limited to at most 10 qubits because of simulation tractability and an upstream feature-selection + LDA reduction to 10 features (author-stated).
- SQS performance degrades as dataset size grows and XGBoost overtakes SQS on the full dataset (author-stated).
- The dataset is from a single production use case (Fintonic/Wanna) with 4,763 loans and class imbalance (~10% positive in some descriptions), so results may not generalize across other financial datasets (author-stated / implied).
- The evolutionary algorithm’s hyperparameters (number of generations, crossover and mutation rates, population size, etc.) were left to researcher choice and not exhaustively optimized; a full hyperparameter search would be computationally expensive (author-stated).
- Some generated quantum circuits contained inefficient sequences (e.g., redundant Hadamard gates) which would increase noise and depth when transpiled for hardware (author-stated).
- Kernels and feature maps were evaluated and selected with alignment and normalized eigenvalue metrics; other evaluation criteria (robustness to noise, calibration, statistical significance tests) were not reported (inferred).
- [inferred] The up-front dimensionality reduction (mutual information selection then LDA) may discard relevant information, and the impact of that preprocessing choice on final performance was not fully quantified.
- [inferred] Only a small set of classical baselines were compared (XGBoost and SVC); comparisons to other modern or regularized classical methods (ensembles, neural nets with strong regularization, etc.) were limited.
- [inferred] Computational cost and wall-clock time of the evolutionary search and kernel evaluation (especially at larger initial population sizes and generations) were not reported, leaving unclear the practical resource requirements.
- [inferred] The paper did not evaluate the susceptibility of the learned quantum kernels to realistic hardware noise or the effect of measurement shot noise; robustness claims remain untested on NISQ devices.
- [inferred] The question of whether the discovered quantum feature maps are classically simulable or confer provable hardness was not addressed.
## Open questions
- How well do the SQS-designed quantum kernels translate to real NISQ hardware when accounting for device noise, connectivity, gate fidelities, and limited measurement shots?
- To what extent do the upstream preprocessing choices (feature selection by mutual information, dimensionality reduction via LDA) drive the reported quantum advantage, versus the quantum kernel itself?
- How does SQS compare against a broader set of classical baselines (regularized logistic regression, neural networks tuned for small-data regimes, other ensemble methods) when given equivalent hyperparameter optimization budgets?
- What are the computational resource requirements (CPU/GPU time, memory) and wall-clock times for the evolutionary search at practical scales, and are those costs acceptable in production workflows?
- Does the apparent advantage of quantum kernels in low-data, imbalanced regimes hold across other financial datasets and other domains (e.g., healthcare), or is it dataset-specific?
- Can the evolutionary search be constrained to produce feature maps that are more hardware-friendly (shallower, fewer multi-qubit gates) without sacrificing separability?
- Are the discovered quantum feature maps classically simulable (i.e., do classical kernel approximations reproduce them), and what are the implications for claimed quantum advantage?
- How sensitive is SQS to hyperparameter choices of the evolutionary algorithm (population size, mutation rate, number of generations) and to random seed variability?
- What are the implications for explainability, regulatory compliance, fairness, and model auditability when integrating SQS into financial decision-making pipelines?
- Can ensemble or multiple-kernel combinations (including classical + quantum kernels) further improve performance or robustness in the studied scenarios?

**Future work:**
- Perform experiments on real quantum hardware to evaluate SQS under realistic NISQ noise and device constraints (author-stated).
- Analyze SQS on more production-grade datasets (additional financial datasets and other sectors such as healthcare) to establish generality and robustness of results (author-stated).
- Conduct larger-scale hyperparameter searches for the evolutionary algorithm (generations, population sizes, crossover/mutation rates) to better characterize and optimize performance, acknowledging higher computational cost (author-stated).
- Explore and mitigate circuit inefficiencies discovered (e.g., redundant gates) and prioritize hardware-friendly feature maps (author-stated/inferred).
- Investigate automated/optimized preprocessing choices and quantify their impact (feature selection and dimensionality reduction) on final performance (inferred).
- Study the classical simulability of discovered quantum feature maps and evaluate whether they possess complexity-theoretic properties that resist efficient classical replication (inferred).
- Evaluate combinations of quantum kernels (multiple-kernel learning) and hybrid classical-quantum ensembles to improve performance and robustness (related work cited; implied future direction).
- Measure computational cost, scalability and wall-clock runtimes of SQS to assess practical feasibility for production deployment (inferred).
- Examine fairness, explainability, and regulatory compliance considerations when deploying quantum-kernel models in financial services (inferred).
## Key ideas
- #idea:hybrid-approach — Proposes Systemic Quantum Score (SQS): an end-to-end hybrid pipeline combining classical preprocessing/feature engineering (featuretools, mutual information, LDA) with quantum feature maps (Pauli-word circuits) and classical kernel SVM classification.
- #idea:quantum-advantage — Reports modest empirical improvements in scarce, imbalanced-data regimes: generalization test (10% train / 90% test) AUC SQS=0.658 vs SVC=0.638 and XGBoost=0.632 on a production-grade proprietary loans dataset.
- #idea:quantum-advantage — Uses an evolutionary (genetic) search over Pauli-word feature-map circuits plus local gradient tuning of continuous gate parameters to automatically discover high-fidelity quantum kernels (fitness measured by kernel-target alignment / spectral criterion).
- #idea:near-term-feasibility — Evaluates quantum-kernel methods with up to 10 qubits and reports very high kernel-target alignment (e.g., normalized fitness ≈ 0.998 ± 0.004 for some configurations), suggesting potential usefulness in low-data regimes in the near term.
- #limitation:simulation-only — All quantum kernel experiments are executed in classical simulation (inversion test to estimate fidelity); no QPU experiments were performed.
- #limitation:no-empirical-validation — Absence of real-hardware validation and no noise/fault-tolerance analysis; reported benefits are from simulator-based experiments and may not transfer to noisy QPUs.
- #idea:hybrid-approach — Practical pipeline choices (feature selection to top 10, LDA to reduce dimensionality to ≤10, sometimes 2) are used to make data amenable to current quantum encoding constraints.
- #idea:quantum-advantage — Experimental design includes multiple random seeds, varying population sizes (10/100/1000), generations (up to 50) and qubit counts (2,3,5,10), with AUC as primary metric and kernel fitness reported, providing quantitative benchmarks against classical baselines.
## Contradictions
- The paper claims quantum-enhanced generalization in scarce-data regimes, but the reported results show classical XGBoost outperforms SQS on the full dataset — indicating the advantage is conditional on small-sample settings rather than universal superiority.
- Claims of near-term applicability are tempered by the fact that all results are from classical simulators with no real-hardware experiments; thus practical hardware noise, latency and scaling remain unvalidated (contradiction between claimed NISQ suitability and lack of empirical hardware evidence).
## Notable quotes
<!-- Researcher-added — verbatim quotes with page references -->

## Researcher notes
<!-- Researcher-added — not LLM generated -->
