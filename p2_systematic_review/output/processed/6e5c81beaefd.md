---
aliases:
- Classification of Financial Data Using Quantum Support Vector Machine
- Classification Financial Data Using
authors:
- Seemanta Bhattacharjee
- MD. Muhtasim Fuad
- A.K.M. Fakhrul Hossain
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
journal_or_venue: arXiv preprint (arXiv:2412.10860)
methodology_tags:
- quantum-ml
- hybrid-quantum-classical
paper_type: ''
quantum_advantage_claim: demonstrated
related_papers: []
relevance_phase1: high
relevance_phase3: high
source_type: preprint
source_type_confidence: high
step1_date: '2026-04-14T10:42:19.791854'
step1_model: gpt-5-mini
step2_date: '2026-04-14T10:42:19.791854'
step2_model: gpt-5-mini
step3_date: '2026-04-14T10:42:19.791854'
step3_model: gpt-5-mini
step4_date: '2026-04-14T10:42:19.791854'
step4_model: gpt-5-mini
step5_date: '2026-04-14T10:42:19.791854'
step5_model: gpt-5-mini
step6_date: '2026-04-14T10:42:19.791854'
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
title: Classification of Financial Data Using Quantum Support Vector Machine
topic_tags:
- quantum-ml-finance
year: '2024'
zotero_key: ''
---

## Abstract summary
The paper evaluates quantum kernel methods for binary classification on a self‑curated Dhaka Stock Exchange Broad Index (DSEx) dataset, comparing several quantum feature maps against classical SVMs. They report that a Pauli Y YY feature‑map based quantum kernel consistently outperforms classical RBF SVMs on small financial datasets (200–400 samples, 5–7 features), verify predictions with the Phase Space Terrain Ruggedness Index (PTRI), and provide resource estimates and implementation details using Qiskit and IBM quantum backends.
## Methodology
The authors formulate a binary classification task to predict daily changes of the Dhaka Stock Exchange Broad Index (DSEx) using quantum kernel methods (Quantum Support Vector Machine) and compare these against classical SVM baselines (RBF kernel). They curate a financial dataset by merging historical DSEx index data from Investing.com with gold price data from usagold.com and augment it with other economic features (resulting in 460 total data points). They construct multiple quantum feature maps (Pauli Y-YY, Pauli Z, Pauli ZZ, Pauli Y-ZZ, Pauli Z-ZZ) and compute quantum kernels by executing the feature-map circuits on Qiskit qasm simulator (no noise model) and on IBM Quantum hardware (ibm_nairobi 7-qubit device). The computed kernel matrices are saved and provided to scikit-learn's SVM using the precomputed kernel option. Experiments vary dataset size (approximately 200–400 sampled points) and feature dimensionality (typically 5–7 features), and measure performance with Balanced Accuracy and F1 score. The study also evaluates variability through repeated random-seed experiments (e.g., 200 runs for one configuration) and inspects empirical advantage regions with the Phase Space Terrain Ruggedness Index (PTRI). The paper provides analytical resource-estimation formulae for gate counts and circuit depth as functions of feature count F and repetition number R, and reports practical limits used (up to 1024 measurement shots).

**Algorithms used:** Quantum Support Vector Machine (quantum kernel methods), Support Vector Machine (classical, RBF kernel), Phase Space Terrain Ruggedness Index (PTRI) for problem-space analysis
**Frameworks:** Qiskit, scikit-learn, IBM Quantum services / devices

**Experimental setup:** Quantum kernels computed with Qiskit qasm simulator (no noise model) and executed on IBM Quantum hardware (ibm_nairobi, a 7-qubit QPU). Kernel matrices were exported and SVMs trained classically using scikit-learn's precomputed-kernel option. Experiments used up to 1024 measurement shots and fixed random seed(s) for consistency.

**Dataset:** Curated DSEx Broad Index dataset: historical Dhaka Stock Exchange Broad Index data from Investing.com merged with ~10 years of gold price data from usagold.com, plus additional economic features. Final merged dataset contains 460 data points; experiments used random subsets of ~200–400 samples and 5–7 features in most runs. The task is binary classification of daily index change (up/down).
## Experiment details
### Input
{'sources': ['Investing.com (Dhaka Stock Exchange Broad historical data)', 'usagold.com (gold prices)'], 'total_points_full_dataset': 460, 'experiment_sample_sizes': 'varied, typically 200 to 400 samples', 'feature_counts_tested': 'typically 5 to 7 features (experiments across 5–7)', 'label': 'binary: daily change in DSEx index (direction)', 'preprocessing': 'datasets merged and augmented with additional economic features; exploratory data analysis performed; random subsets selected for experiments. No detailed normalization/feature-scaling procedure is reported in the paper.'}

### Process
{'pipeline_steps': ['Curate and merge financial datasets; perform EDA and add economic features.', 'Select random subset (varying sizes) and choose feature subset (5–7 features).', 'Encode classical inputs into parameterized quantum circuits using chosen feature maps (e.g., Pauli Y-YY).', 'Execute circuits on Qiskit qasm simulator (no noise model) and on IBM hardware (ibm_nairobi) to compute kernel entries (state overlaps) using up to 1024 shots.', 'Save the computed kernel matrix.', 'Train classical SVM with precomputed kernel in scikit-learn (baseline: SVM with RBF kernel trained on same data).', 'Evaluate models on test splits using Balanced Accuracy and F1 score.', 'Repeat experiments across configuration space (data size × feature count).', 'Assess problem-space ruggedness and regions of empirical quantum advantage using PTRI.'], 'feature_maps_and_variants': ['Pauli Y-YY (primary reported best-performing map)', 'Pauli Z', 'Pauli ZZ', 'Pauli Y-ZZ', 'Pauli Z-ZZ'], 'repetitions_and_variability': 'Multiple random-seed trials; example: 200 independent experiments for one configuration to estimate distribution (reported std dev ~2.1% for classical SVM in one case).', 'notes': 'Random seed was fixed across comparisons for consistency; exact seed value is not reported. Circuits used repetitions R (unspecified in experiments), and the authors provide formulae to compute gates and depth as functions of F and R.'}

### Output
{'metrics_reported': ['Balanced Accuracy', 'F1 Score'], 'baselines': ['Classical SVM with RBF kernel'], 'output_format': 'Aggregated performance metrics (means across random subsets and repeats) reported across configuration grid (feature count × dataset size). Graphical comparisons (figures) of average Balanced Accuracy differences, PTRI surface plots, and distributions of Balanced Accuracy across repeated runs.'}

### Parameters
- qubits: equal to number of features (F); typical F=5..7 in reported experiments
- shots: up to 1024 (maximum reported)
- simulator_noise_model: none for qasm simulator runs (simulations performed without noise models)
- feature_map_repetition_R: parameter R (circuit repetition) used in formulas; explicit R values for runs not always specified
- gate_types: ['H', 'Rx', 'P (phase)', 'Cx (CNOT)']
- gate_count_formula: Total gates = (11 * F - 7) * R; H = F * R; Rx = (6 * F - 4) * R; P = (2 * F - 1) * R; Cx = (2 * F - 2) * R
- depth_formula: Depth = (5 * F - 1) * R
- random_seed: fixed for each experiment comparison but numeric value not reported
- optimizer: not applicable (SVM trained classically with scikit-learn; quantum circuits used for kernel evaluation rather than variational optimization)

### Hardware
{'simulator': 'Qiskit qasm simulator (no noise model)', 'quantum_processor': {'name': 'ibm_nairobi', 'qubits': 7, 'provider': 'IBM Quantum Services'}, 'note': 'Multiple instances of experiments were run on IBM hardware and results reportedly aligned with simulations.'}

### Reproducibility
The paper does not provide links to code repositories, explicit experiment scripts, or public data files for the curated DSEx dataset. The data sources (Investing.com, usagold.com) are cited, and detailed resource-estimation formulae are given, but exact random seeds, train/test split procedures, preprocessing steps (scaling/normalization), and the final curated dataset are not published in the text. Reproducibility is therefore limited unless authors release code and the curated dataset.
## Findings
- [supported] The authors curated a Dhaka Stock Exchange Broad Index (DSEx) dataset (merged from Investing.com and gold prices) with a total of 460 data points and used subsets (typically 200–400 points) for experiments.
- [supported] Experiments used 5–7 features (configuration space explored) and evaluated models with Balanced Accuracy and F1 score.
- [supported] The quantum kernel constructed from a Pauli Y YY feature map consistently outperformed other tested quantum kernels and a classical SVM (RBF kernel) across the tested configuration space in this study.
- [supported] The authors report empirical quantum advantage (EQA) for the tested problems/configurations and state the Pauli Y YY kernel showed EQA across the configuration points they examined.
- [supported] PTRI (Phase Space Terrain Ruggedness Index) was computed for the configuration space and the authors report that PTRI behavior aligned with their experimental observations (quantum kernels performed better on smoother terrain in their runs).
- [supported] Quantum experiments were performed on Qiskit/IBM Quantum simulators (qasm simulator without noise models) and some runs on IBM hardware (ibm_nairobi); the hardware results were reported to be consistent with simulation.
- [supported] The paper provides explicit resource-estimation formulas for their Pauli Y YY circuit: total gates = (11 × F − 7) × R; H = F × R; Rx = (6 × F − 4) × R; P = (2 × F − 1) × R; Cx = (2 × F − 2) × R; depth = (5 × F − 1) × R, and states qubit count equals number of features.
- [supported] The experiments used at most 1024 shots per circuit (they note this is smaller than many larger-scale QML studies, increasing sampling noise).
- [supported] Empirical variability in classical SVM balanced accuracy at one configuration (200 samples, 5 features) showed a standard deviation of about 2.1% over repeated runs with different random seeds.
- [speculative] The authors suggest Bloch sphere encoding could reduce the number of qubits required for fixed-feature experiments (presented as a potential optimization, not demonstrated here).
- [speculative] The paper asserts that quantum feature maps (class of circuits they test) are a promising avenue to outperform classical SVMs on complex, high-dimensional, non-stationary financial data in general (a generalization beyond their specific experiments).
- [speculative] The authors state that the Pauli Y YY feature map (and related class of feature maps) come from families conjectured to be hard to simulate classically (cites literature) — framed as conjectured/hard-to-simulate rather than proven here.
- [speculative] The authors propose that expanding to larger, more diverse financial datasets and tuning hyperparameters/regularization could further validate and/or improve quantum kernel performance (future work suggestion).

**Results summary:** The preprint reports that, on their curated Dhaka Stock Exchange Broad Index dataset (460 total points, experiments on 200–400 point subsets with 5–7 features), a quantum kernel derived from a Pauli Y YY feature map outperformed other tested quantum kernels and a classical RBF-SVM across the tested configuration grid. They measured performance with Balanced Accuracy and F1 score, observed empirical quantum advantage (EQA) across the examined instances, and used PTRI to characterize where quantum kernels showed stronger performance. Experiments were run on Qiskit simulators (no noise model) and on IBM hardware; the authors additionally provide circuit resource-estimation formulas and note practical constraints (limited shots, sampling noise).

**Performance claims:**
- 460 total data points in the curated DSEx dataset (merged from Investing.com and gold prices).
- Experimental subsets used typically 200–400 data points and 5–7 features.
- Maximum of 1024 shots per circuit execution used in experiments.
- Classical SVM balanced accuracy variability: ~2.1% standard deviation for the configuration with 200 samples and 5 features over 200 repeated experiments.
- Resource formulas for the Pauli Y YY circuit: total gates = (11 × F − 7) × R; H = F × R; Rx = (6 × F − 4) × R; P = (2 × F − 1) × R; Cx = (2 × F − 2) × R; depth = (5 × F − 1) × R.
- Number of qubits required equals the number of features (independent of repetition R).
## Quantum advantage claim
**Classification:** demonstrated

The authors present empirical results claiming an empirical quantum advantage (EQA) in this dataset: the Pauli Y YY quantum kernel outperformed a classical RBF-SVM across the tested configuration space (200–400 samples, 5–7 features). This demonstration is limited in scope (small datasets, specific kernel family, simulations without noise models, limited shots) and thus represents an empirical, small-scale demonstration rather than a broad, general proof of advantage.
## Limitations
- The experiments use small datasets (the curated DSEx dataset contains 460 data points) which limits statistical power and generalizability.
- Only small circuit sampling was used (no circuit executed with more than 1024 shots), increasing sampling noise and estimator variance (author-stated).
- Quantum simulations were performed without noise models on the qasm simulator, so results may not reflect realistic noisy-hardware performance (author-stated).
- Experiments employed a single random seed for SVM training/prediction, making results susceptible to randomness and reducing robustness of reported comparisons (author-stated).
- PTRI verification and performance summaries were produced over a small configuration grid (15 averaged points, two selected datasets), limiting the coverage of the configuration space (author-stated).
- Experiments used limited feature counts (5–7 features) and low data sizes (200–400 samples in many tests), constraining exploration of higher-dimensional or larger-scale regimes (inferred).
- Only binary classification was considered; multi-class or regression tasks on financial data were not studied (inferred).
- Baselines were limited to classical SVM with RBF kernel; broader classical baselines (other ML models or simpler/stronger kernels) were not compared (inferred).
- Resource scaling shows qubit count equal to feature count for the used encoding, which limits scalability to higher-dimensional feature sets unless alternative encodings are used (inferred).
- Bloch Sphere Encoding and other resource-reduction strategies were only suggested and not implemented or benchmarked here (author-stated/inferred).
- Hyperparameter tuning and regularization exploration were not reported in depth; the impact of those on results is therefore unclear (author-stated/inferred).
- Merging of multiple sources to curate the DSEx dataset introduces potential curation and selection biases (inferred).
## Open questions
- Does the observed empirical quantum advantage (EQA) generalize to larger and more diverse financial datasets beyond the small DSEx dataset used here?
- How robust are the reported quantum kernel advantages to realistic device noise and finite sampling on actual noisy quantum hardware?
- How sensitive are results to the choice of feature map (e.g., Pauli Y YY vs. other maps) across a wider set of financial tasks and encodings?
- Can custom quantum feature maps specifically designed for financial data characteristics provide larger and more consistent advantages?
- How effective is Bloch Sphere Encoding (or other encoding schemes) at reducing qubit requirements for realistic, higher-dimensional financial feature sets without degrading kernel performance?
- What is the effect of more extensive hyperparameter tuning and regularization (both for quantum kernels and classical baselines) on the comparative performance?
- How many shots and what sampling strategy are required to reliably estimate quantum kernels for finance tasks while keeping hardware costs practical?
- Why did quantum kernels perform better on ‘smoother terrain’ in PTRI for this dataset, and is that observation general across other datasets and domains?
- How do quantum kernel methods compare to a broader set of classical baselines (e.g., ensemble methods, neural networks, gradient-boosted trees) on the same dataset and configurations?
- Can quantum kernels handle non-stationarity and temporal dependencies typical of real-world financial time series in an online or continual-learning setting?
- What are the full resource (qubits, gates, depth, shots) and error-correction requirements to scale these experiments to production-relevant problem sizes?

**Future work:**
- Use larger and more diverse financial datasets to validate generalizability of the reported quantum kernel advantages.
- Study the effects of classically hard-to-simulate kernels on financial data.
- Develop and test custom feature maps specifically designed for financial data characteristics.
- Explore Bloch Sphere Encoding and other encodings to reduce qubit requirements and assess trade-offs.
- Perform systematic hyperparameter tuning and investigate regularization techniques for both quantum and classical models.
- Run larger-scale experiments with more shots, noise modeling, and on contemporary noisy quantum hardware to assess practical performance.
- Provide more comprehensive resource estimates and scaling studies for conducting these experiments at larger scales.
- Investigate additional classical baselines and more robust evaluation protocols (e.g., cross-validation, multiple random seeds) to strengthen comparisons.
- Explore application extensions beyond binary classification (e.g., multi-class classification, regression, time-series forecasting).
- Examine why PTRI-indicated regions (e.g., smoother terrain) favor quantum kernels and test PTRI-based selection across other datasets.
## Key ideas
- #idea:quantum-advantage — A Pauli Y-YY quantum feature-map kernel consistently outperforms a classical RBF SVM on small curated DSEx financial datasets (200–400 samples, 5–7 features) by Balanced Accuracy and F1 across repeated trials.
- #idea:quantum-advantage — The authors use the Phase Space Terrain Ruggedness Index (PTRI) to map problem-space ruggedness and identify regions where the quantum kernel exhibits empirical advantage over classical baselines.
- #idea:hybrid-approach — Quantum kernel entries are evaluated using quantum circuits (simulator and IBM QPU) and the resulting kernel matrices are fed to classical SVM training (scikit-learn precomputed-kernel), demonstrating a pragmatic QPU+CPU pipeline.
- #idea:near-term-feasibility — Experiments include runs on a 7-qubit IBM device (ibm_nairobi) with up to 1024 shots and provide explicit gate-count and circuit-depth formulas (gates/depth scale as functions of feature count F and repetition R), arguing feasibility on current small QPUs.
- #limitation:qubit-count — Experiments are limited to small numbers of qubits (qubits = feature count, typically 5–7), restricting the demonstrated results to low-dimensional problems and leaving scalability to larger feature sets unproven.
- #limitation:noise — Simulator experiments were run without a noise model; although some runs were performed on ibm_nairobi and reportedly aligned with simulation, the absence of detailed noise-modelled simulations and limited discussion of error mitigation weakens claims about noise robustness.
- #limitation:data-encoding — Encoding strategy requires one qubit per feature and circuit resources grow linearly with F and R (gate-count and depth formulas provided), indicating nontrivial encoding/resource costs that may limit larger-scale applicability.
- #limitation:simulation-only — Some key simulation results used a noise-free qasm simulator; while hardware runs are reported, substantial portions of analysis (e.g., broader configuration grids or many repeats) appear to rely on simulation without noise models.
- #limitation:noise — Reproducibility is limited: the paper does not provide code, experiment scripts, or public curated dataset files, making independent verification of hardware-vs-simulator alignment and reported advantage difficult.
## Contradictions
<!-- Step 6 output — where this paper contradicts others -->

## Notable quotes
<!-- Researcher-added — verbatim quotes with page references -->

## Researcher notes
<!-- Researcher-added — not LLM generated -->
