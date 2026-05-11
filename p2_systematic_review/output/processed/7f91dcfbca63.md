---
aliases:
- Quantum-inspired anomaly detection, a QUBO formulation
- Quantum inspired anomaly detection
authors:
- Julien Mellaerts
auto_detected: true
classification: ''
contradiction_flags:
- contradiction:classical-vs-quantum
- contradiction:scalability
doi: ''
evaluation_type: benchmark-comparison
evidence_type: ''
has_quantitative_results: true
idea_tags:
- idea:quantum-advantage
- idea:near-term-feasibility
journal_or_venue: arXiv preprint (arXiv:2311.03227)
methodology_tags:
- quantum-annealing-qubo
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
- topic/fraud-detection
- method/quantum-annealing-qubo
- idea/quantum-advantage
- idea/near-term-feasibility
- contradiction/classical-vs-quantum
- contradiction/scalability
title: Quantum-inspired anomaly detection, a QUBO formulation
topic_tags:
- quantum-ml-finance
- fraud-detection
year: '2023'
zotero_key: ''
---

## Abstract summary
The paper proposes a QUBO (Quadratic Unconstrained Binary Optimization) formulation for anomaly detection that combines statistical (linear) and density-based (quadratic) terms to select k outliers, with a penalty to enforce the selection constraint. It benchmarks the approach against classical methods on synthetic Gaussian data, MNIST subsets, and a credit card fraud dataset, reporting improved accuracy, and discusses scalability limits on current QPUs due to all-to-all interactions while noting it is solvable with classical QUBO solvers.
## Methodology
The paper proposes a quantum-inspired anomaly detection method by formulating anomaly selection as a Quadratic Unconstrained Binary Optimization (QUBO) problem. Each data point i is represented by a binary variable xi indicating whether it is selected as an outlier. The QUBO objective combines a linear term proportional to the Mahalanobis distance from the dataset centroid (di) and a quadratic term proportional to pairwise distances between selected points (di,j) with a tunable weight α ∈ [0,1] that balances statistical (linear) and density (quadratic) contributions. A constraint on the number of outliers k is enforced via a quadratic penalty term −A(Σi xi − k)^2 with A chosen larger than the maximum QUBO coefficient magnitude. To reduce connectivity, quadratic interactions per variable are limited to the k furthest neighbors (sparsified). The QUBO is solved using qbsolv (a classical QUBO solver / partitioning solver for large QUBOs); the learned/selected α is obtained during a training phase. The method is benchmarked against classical anomaly detectors from scikit-learn (EllipticEnvelope, One-Class SVM, SGDOneClassSVM, Isolation Forest, Local Outlier Factor) using ROC AUC as the evaluation metric on three experiments: synthetic Gaussian data (varying standard deviations), small MNIST subsets (three 50-sample configurations with 45 inliers/5 outliers), and a credit card fraud dataset (284,807 transactions, 492 frauds).

**Algorithms used:** QUBO formulation (custom quantum-inspired model), qbsolv (QUBO solver/partitioning solver), Mahalanobis distance (for linear terms), k-furthest-neighbors sparsification (to limit quadratic terms), Classical baselines: EllipticEnvelope (Robust covariance), One-Class SVM, SGDOneClassSVM, IsolationForest, LocalOutlierFactor, Simulated annealing / simulated quantum annealing (mentioned as alternative solvers)
**Frameworks:** scikit-learn (used for baseline algorithms), qbsolv (used to solve QUBOs)

**Experimental setup:** QUBO instances constructed from datasets (linear Mahalanobis distances and sparse pairwise distances limited to k furthest neighbors) and solved with qbsolv on classical hardware. No quantum processing unit was used; simulated or classical QUBO solvers (qbsolv) were used for all reported benchmarks. Evaluation metric: ROC AUC versus classical baseline methods.

**Dataset:** Credit card fraud detection dataset: 284,807 transactions (two days of card transactions, Europe, Sept 2013) with 492 frauds (≈0.172% positives). Also used non-financial datasets: synthetic Gaussian-distributed samples (three standard deviations) and MNIST subsets (three configurations of 50 samples each: 45 of one digit and 5 of another).
## Experiment details
### Input
{'synthetic_gaussian': {'description': 'Random Gaussian-distributed data points experiments with three different standard deviations.', 'size': 'Not explicitly stated (varied per experiment).', 'preprocessing': 'Mahalanobis distance computed; no additional preprocessing described.'}, 'mnist_subsets': {'description': 'Three configurations each containing 50 samples: (45 zeros + 5 nines), (45 sevens + 5 ones), (45 twos + 5 threes). Minority digit treated as outliers.', 'size': 'Each configuration: 50 samples (45 inliers, 5 outliers).', 'preprocessing': 'Not specified beyond distance computations (Mahalanobis).'}, 'credit_card_fraud': {'description': 'Public credit-card fraud dataset commonly used in literature (284,807 transactions, 492 frauds).', 'size': '284,807 samples, 492 positive (fraud) cases.', 'preprocessing': 'Not detailed in the paper; Mahalanobis distance used to compute linear QUBO terms. No other preprocessing steps (scaling, PCA, feature selection) explicitly reported.'}}

### Process
{'steps': ['Compute dataset centroid and Mahalanobis distance di for each data point xi.', 'Compute pairwise distances di,j between data points; for each point keep only quadratic interactions to its k furthest neighbors to sparsify the QUBO.', 'Formulate QUBO objective Q(x, α) = α Σi di xi + (1−α) Σi≠j di,j xi xj.', 'Add a cardinality constraint via penalty term −A(Σi xi − k)^2 with A scaled larger than max(Q) to enforce selection of exactly k outliers.', 'Select/tune α during a training phase specific to the dataset.', 'Solve the resulting QUBO with qbsolv (classical solver). Alternative solvers such as simulated annealing or simulated quantum annealing are mentioned as possible.', 'Evaluate the selected outliers against ground truth using ROC AUC and compare results to classical baselines from scikit-learn.'], 'solver_details': 'qbsolv used to solve QUBO instances. No solver hyperparameters (partitioning size, num_repeats, timeout, temperature schedule, etc.) are reported.', 'iterations_and_parameters': 'Not reported (no number of solver iterations, restarts, or convergence criteria provided).'}

### Output
{'format': 'ROC AUC scores are reported and plotted for each method and dataset/experiment configuration.', 'baselines': ['EllipticEnvelope (Robust covariance)', 'One-Class SVM', 'SGDOneClassSVM', 'IsolationForest', 'LocalOutlierFactor'], 'results_summary': 'QUBO-based (quantum-inspired) method reported improved ROC AUC compared to the listed classical baselines on the presented synthetic and real-world datasets. Figures show ROC AUC per method for each experiment.'}

### Parameters
- alpha: Weighting parameter between linear and quadratic QUBO terms; float in [0,1]; dataset-specific and learned during training.
- k: Number of outliers to select (integer, 0 < k ≤ N); specified per experiment (e.g., 5 outliers in MNIST subsets).
- A_penalty: Penalty weight for enforcing cardinality constraint; must satisfy A > max(|Q|) (paper states A > max(Q)).
- distance_metric: Mahalanobis distance for linear terms; pairwise distances for quadratic terms.
- quadratic_sparsification: Only k furthest neighbors retained per variable to limit quadratic interactions.
- solver: qbsolv (no additional solver parameters reported).

### Hardware
N/A

### Reproducibility
The paper does not provide code, solver hyperparameters, or detailed preprocessing steps. Datasets are standard/public (MNIST and the commonly used credit-card fraud dataset), so data access is feasible, but key solver parameters for qbsolv runs (partitioning strategy, number of repeats, timeout, random seed) and the procedure to learn α are not specified, limiting exact reproducibility. No repository or scripts are referenced.
## Findings
- [supported] The paper proposes a QUBO formulation for anomaly detection that combines linear terms (distance to the centroid) and quadratic terms (pairwise distances) with a weighting parameter alpha.
- [supported] The QUBO objective includes a penalty term -(A(sum_i x_i - k)^2) to constrain the number of selected outliers to k.
- [supported] The authors implemented and benchmarked the QUBO approach (solved with qbsolv) against classical anomaly detectors (Robust covariance, One-Class SVM, SGD One-Class SVM, Isolation Forest, Local Outlier Factor) on synthetic Gaussian data, MNIST subsets, and a credit card fraud dataset, reporting ROC AUC comparisons.
- [supported] The paper reports that the quantum-inspired QUBO method achieved improved accuracy (ROC AUC) compared to the listed classical methods on the tested random and real-world datasets.
- [supported] The Mahalanobis distance was chosen as the distance metric in the formulation and experiments.
- [supported] The penalty term (sum_i x_i - k)^2 expands to all-to-all quadratic interactions, which the authors argue makes the naive QUBO formulation incompatible with connectivity-limited near-term QPUs.
- [supported] The proposed QUBO can be solved at scale using classical QUBO solvers (qbsolv), simulated quantum annealing, or simulated annealing, i.e., without requiring quantum hardware.
- [speculative] The alpha weighting parameter is dataset-specific and needs to be learned/tuned per dataset.
- [speculative] Limiting quadratic terms to only the k-furthest neighbors will improve accuracy and may enable embedding on actual QPUs.
- [speculative] Alternative formulations or restrictions on outlier selection are required to allow the problem to be solved on connectivity-limited QPUs; the paper suggests this but does not provide a concrete QPU-compatible alternative.

**Results summary:** The paper presents a quantum-inspired anomaly detection method formulated as a QUBO that mixes centroid-based (linear) and pairwise (quadratic) distance terms, with a penalty enforcing selection of exactly k outliers. The formulation was implemented and solved with qbsolv and compared (via ROC AUC) against several classical anomaly detectors on synthetic Gaussian data, selected MNIST subsets, and a credit-card fraud dataset. The authors report improved ROC AUC for the QUBO approach on these benchmarks. They note a practical limitation: the penalty enforcing exactly k outliers creates all-to-all quadratic couplings which impede direct mapping to current connectivity-limited QPUs, so the approach was evaluated using classical QUBO solvers rather than on quantum hardware.
## Quantum advantage claim
**Classification:** not-applicable

The work is 'quantum-inspired' and uses a QUBO formulation solved with classical QUBO solvers (qbsolv / simulated annealing). No quantum hardware speedup or advantage is demonstrated; moreover the authors state that the penalty term induces all-to-all interactions that prevent straightforward implementation on current QPUs.
## Limitations
- The outlier-selection penalty (equation 3) imposes all-to-all quadratic interactions, making the QUBO not solvable by near-term QPUs (author-stated).
- The weighting parameter α is dataset-specific and must be learned during a training phase (author-stated).
- Accurate performance requires limiting quadratic terms of each variable (filling only k-furthest neighbors), i.e., the formulation relies on sparsification for good results (author-stated).
- The penalty weight A must be scaled relative to QUBO terms (A > max(Q)), introducing a delicate scaling/tuning requirement (author-stated).
- [inferred] Embedding the all-to-all QUBO onto connectivity-limited quantum hardware will incur large overheads (qubit count and chain lengths), limiting practical scalability on current QPUs.
- [inferred] The method requires choosing k (number of outliers); performance and behavior depend on this choice and thus on hyperparameter tuning.
- [inferred] Use of Mahalanobis distance implies reliance on a well-conditioned covariance estimate; performance may degrade in high-dimensional or small-sample regimes.
- [inferred] Benchmarks are reported for specific, relatively small/configured datasets (synthetic Gaussians, small MNIST subsets, and the credit-card dataset) with no detailed runtime, resource, or statistical-significance analysis; generalizability is not demonstrated.
- [inferred] The reported work relies on classical QUBO solvers (qbsolv, simulated annealing) rather than execution on quantum hardware, so claims about quantum applicability or advantage remain unverified.
- [inferred] All-to-all quadratic interactions imply O(N^2) storage and computation for pairwise distances, which becomes impractical for large N without further approximations or sparsification.
- [inferred] Penalty-based enforcement of exact k-outlier selection can be sensitive and may require careful calibration to avoid infeasible or suboptimal solutions.
## Open questions
- How can outlier selection be constrained or reformulated to avoid all-to-all quadratic interactions and make the QUBO compatible with connectivity-limited QPUs?
- What are effective methods to learn or set the weighting parameter α automatically and robustly across different datasets?
- How should the number of outliers k be selected in a principled way (automatically or adaptively) for different applications and data regimes?
- What strategies (sparsification, neighborhood selection, approximation) best trade off solution quality and embeddability on real quantum annealers?
- How sensitive is the approach to the choice of distance metric (Mahalanobis vs. Euclidean or learned metrics) and to errors in covariance estimation?
- Can this QUBO formulation be efficiently minor-embedded and solved on current quantum annealers or other QPUs, and what are the empirical limits (problem size, connectivity)?
- Is there any practical quantum advantage (speed, quality, or resource usage) over classical anomaly-detection methods when using actual QPUs rather than classical QUBO solvers?
- How does the method scale (accuracy, runtime, memory) to large, high-dimensional, and highly imbalanced real-world datasets typical in financial services?
- How robust is the approach to noise and errors when implemented on noisy quantum hardware (NISQ/QA devices)?
- What are the impacts on detection performance and false-positive rates when limiting quadratic terms to k-furthest neighbors?

**Future work:**
- Develop alternative methods to restrict outlier selection so the QUBO does not require all-to-all quadratic interactions and can be solved on connectivity-limited QPUs (author-suggested).
- Learn or tune the α weighting parameter per dataset in a training phase (author-suggested).
- Explore limiting quadratic terms (e.g., using only k-furthest neighbors) to enable embeddings on actual QPUs and study the trade-offs between sparsity and accuracy (author-suggested).
- Investigate embedding and solver strategies (minor-embedding, decomposition) that permit execution on present-day quantum annealers or other QPUs (author-implied).
## Key ideas
- #idea:quantum-advantage — A QUBO (quantum-inspired) formulation for anomaly detection combining a Mahalanobis-distance linear term and a density-based quadratic term, with a cardinality penalty, achieves higher ROC AUC than several classical baselines on synthetic, MNIST subsets, and a credit-card fraud dataset (reported using qbsolv).
- #idea:near-term-feasibility — The method is explicitly quantum-inspired but is solved with classical QUBO solvers (qbsolv); the authors argue sparsification (keeping k furthest neighbors) and penalty tuning make the formulation tractable on current solvers and potentially on near-term hardware after connectivity reduction.
- #limitation:qubit-count — The paper notes scalability limits for current QPUs due to required all-to-all interactions and the need to sparsify quadratic terms, indicating practical qubit/connectivity constraints for direct QPU implementation.
- #limitation:simulation-only — All experiments were run with classical QUBO solver qbsolv (no QPU experiments); solver hyperparameters, partitioning details and code are not provided, limiting reproducibility and preventing demonstration of advantage on quantum hardware.
## Contradictions
- The paper presents the approach as "quantum-inspired" and reports better performance than classical baselines, yet all experiments use a classical QUBO solver (qbsolv) rather than quantum hardware — so any claim of quantum advantage is not demonstrated on QPUs (contradiction between quantum framing and classical-only validation).
- The authors claim potential applicability to quantum hardware but simultaneously acknowledge current QPU connectivity/scalability limitations and require sparsification; this undermines claims that the method is ready for direct quantum deployment without significant further engineering.
## Notable quotes
<!-- Researcher-added — verbatim quotes with page references -->

## Researcher notes
<!-- Researcher-added — not LLM generated -->
