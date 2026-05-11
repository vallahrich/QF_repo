# Silo data sheet — fraud_detection

- total papers: **105**  (single-silo: ?, multi-silo: ?)
- DT count: 9
- AT count: 5

## Descriptive themes (DT)

### DT-FD-001 · 18 papers
**Quantum kernel classifiers dominate with performance critically dependent on feature map design and dimensionality scaling**

The majority of quantum fraud detection papers employ quantum support vector machines or kernel methods as the primary classification mechanism, using quantum feature maps to embed transaction data into Hilbert space. Performance varies significantly across feature map choices (ZFeatureMap, ZZFeatureMap, PauliFeatureMap, IQP circuits), with some configurations yielding strong results and others failing to separate classes. Quantum kernel advantages tend to grow with increasing feature dimensionality, though experiments remain limited to 10-20 qubits.

### DT-FD-002 · 18 papers
**Class imbalance as the defining methodological challenge driving rebalancing and evaluation design**

Extreme class imbalance with fraudulent transactions comprising less than 1% of data is consistently identified as the fundamental obstacle for fraud detection. Papers apply SMOTE, Quantum-SMOTE, random oversampling, or class-weighted losses to rebalance training data, reporting substantial improvements in minority-class metrics. Authors consistently argue that accuracy is misleading under such imbalance and adopt recall, F1-score, PR-AUC, and macro-averaged metrics as primary evaluation criteria.

### DT-FD-003 · 17 papers
**Simulation-to-hardware gap: simulator-only evaluation and hardware noise degradation undermine result validity**

Most quantum fraud detection experiments are conducted exclusively on noiseless simulators, with authors explicitly cautioning that real-device behavior may differ substantially. Papers testing on real quantum hardware or under realistic noise simulations report significant performance degradation, with some noise channels reducing fraud classification accuracy from 82% to approximately 37%. The combined evidence frames most current results as proof-of-concept rather than deployment-ready.

### DT-FD-004 · 7 papers
**Classical ensemble methods remain competitive with or superior to quantum models**

Several papers report that classical ensemble methods such as XGBoost, Random Forest, and gradient boosting outperform or match quantum models on standard fraud detection metrics. Classical SVM achieves 99% accuracy versus QSVM at 91-93%, and XGBoost reaches 89-95% ROC-AUC while quantum approaches score lower. Authors attribute this to the maturity of classical methods and the constraints of current quantum hardware.

### DT-FD-005 · 9 papers
**Qubit scarcity forces aggressive dimensionality reduction before quantum encoding**

Papers consistently apply PCA or other dimensionality reduction techniques to compress transaction features from 28-30 attributes down to 2-10 principal components to match available qubit counts. Authors note that limited qubit availability forces this aggressive reduction, which may remove discriminative information relevant to fraud detection and constrains the realism of evaluation.

### DT-FD-006 · 15 papers
**Alternative quantum formulations: unsupervised anomaly detection and graph-based networked fraud modeling**

A subset of papers formulates fraud detection as unsupervised anomaly detection or graph-based problems rather than supervised classification. Anomaly-based approaches train quantum autoencoders, quantum LOF, QSVDD, or one-class SVMs on normal transactions to detect fraud via deviation from learned patterns. Graph-based methods represent transactions as networks and apply quantum graph neural networks, QUBO-based community detection, or Gaussian boson sampling to identify coordinated fraud patterns that individual transaction classifiers may miss.

### DT-FD-007 · 10 papers
**Hybrid quantum-classical pipeline architecture as standard design pattern**

Papers consistently propose architectures where classical components handle data preprocessing, feature engineering, and post-processing while quantum modules perform specific sub-tasks such as feature mapping, kernel estimation, or ensemble optimization. The hybrid design is motivated by NISQ constraints preventing fully quantum processing and the practical need to integrate quantum modules into existing fraud infrastructure.

### DT-FD-008 · 7 papers
**Real-time low-latency requirements constrain quantum deployment feasibility**

Papers highlight that fraud detection in modern payment systems requires millisecond-level decision making and high throughput. Quantum circuit execution overhead and cloud-based QPU access introduce latency that can offset speed gains, with even 50ms of added latency reported as detrimental. Operational metrics like inference time per 1,000 transactions are tracked alongside detection quality.

### DT-FD-009 · 9 papers
**Conceptual quantum fraud proposals without empirical validation**

A substantial group of papers discuss quantum-enhanced fraud detection at a conceptual, review, or survey level without reporting original quantitative experiments. Claims about faster anomaly detection, improved pattern recognition, and reduced false positives are presented as qualitative expectations or cited from other work rather than backed by new experiments, with no datasets, quantum circuits, or reproducible benchmarks produced.

## Analytical themes (AT)

### AT-FD-001 · C2=partially_grounded (medium)
**Premature methodological convergence on kernel classifiers constrains the search space for quantum advantage**

_Interpretation:_ The field's overwhelming focus on QSVM and kernel methods reflects the availability of mature quantum ML frameworks and the mathematical convenience of translating the classical kernel trick into quantum circuits, rather than evidence that kernels are the optimal quantum formulation for fraud. Alternative approaches—unsupervised anomaly detection exploiting fraud's inherent rarity, and graph-based methods targeting network-level collusive patterns—address structurally distinct aspects of fraud that point-wise kernel classifiers cannot capture. This methodological monoculture risks optimizing a suboptimal paradigm while neglecting formulations where quantum computation may offer genuinely incommensurable capabilities.

_grounded_in DT:_ DT-FD-001, DT-FD-006

**B2 counter_evidence:**
- `f9e5b6ee139d` (boundary_condition): Demonstrates that quantum kernel advantages scale with feature dimensionality through multiple kernel learning and IQP re-uploading, suggesting the concentration on kernel methods may be justified if hardware scales to support higher qubit counts.
- `b17e753ba135` (boundary_condition): Shows that QUBO-based community detection on CIM hardware identifies 70% of fraud within dense graph communities, providing empirical support for graph-based formulations as a viable alternative rather than evidence that kernels have crowded out successful alternatives.

**C2 flagged_papers:**
- `58a29f9f57a7` (partially_grounded): The memo shows a hybrid fraud pipeline with QSVM, VQC, and a QUBO ensemble, but it does not say kernel methods dominate the field or explain that dominance by framework maturity.
- `76bf72482fcf` (partially_grounded): This memo supports conditional limits of quantum models and the practicality of hybrids, but it does not evidence field-level convergence on kernels or neglected alternatives caused by methodological monoculture.
- `b253d747bcc9` (misaligned_claim): The memo reports that IQP re-uploading kernels improve average precision as qubit and feature counts grow, which supports continued kernel exploration rather than a clearly suboptimal kernel monoculture.
- `f9e5b6ee139d` (misaligned_claim): This memo is still kernel-centric and says projected MKL gives the best fraud result on HSBC data; it does not support the claim that non-kernel formulations were the neglected better search space.

_C2 reason:_ Partially grounded. Papers 1bf5fc02b95b ("Fraud is treated as an anomaly-detection task trained on normal transactions only"), 7f91dcfbca63 ("QUBO formulation is designed to select a fixed number of outliers"), and d1e6a91e7f11 ("Uses graph structure and transaction relationships") support the narrower claim that non-kernel anomaly and graph formulations capture different fraud structures. 77f0bbb6e5f3 also supports outlier-oriented clustering, but the memos do not show that the field converged on kernels because of framework maturity/convenience or that alternatives were crowded out. Instead, b253d747bcc9 reports IQP kernels "improving AP as feature/qubit count grows" and f9e5b6ee139d says "MKL helps overcome concentration effects," so the monoculture/suboptimal-paradigm inference extends beyond the memo evidence.

**C3 crosswalk entries:**
- **extends** (medium) · `f88bb4cc0c22` *Systematic Review on the Influence of Classical and Quantum*
  > "QML methods (QSVM, QNN, QAOA, QAE, HHL etc.) are proposed as promising primitives for tasks such as fraud detection, portfolio optimisation, derivative pricing and market simulation"
- **complements** (low) · `f3998e794c14` *A Review on High-Frequency Trading Forecasting Methods: Opportunity*
  > "QSVM/quantum-kernel methods are highlighted as potentially enabling large feature-space embeddings and speedups in kernel computation"

### AT-FD-002 · C2=partially_grounded (medium)
**Cascading NISQ constraints create a compounding validity gap that inflates reported quantum capability**

_Interpretation:_ Three independently documented constraints—simulator-only evaluation masking hardware noise, aggressive PCA-driven feature compression from 30 to 2-10 dimensions, and noise-induced performance degradation on real devices—interact multiplicatively to create a validity gap far larger than any single limitation suggests. Results obtained on noiseless simulators with aggressively reduced features bear little resemblance to production fraud detection conditions, and the rare hardware experiments confirm substantial performance drops. This compounding effect explains why classical baselines consistently match or exceed quantum approaches: the experimental setup systematically favors quantum models by removing the very constraints that define their current limitations.

_grounded_in DT:_ DT-FD-003, DT-FD-005, DT-FD-004

**B2 counter_evidence:**
- `cb19eb039ea0` (boundary_condition): Reports that shallow quantum circuits with noise-aware design maintain partial classification robustness on real hardware, indicating the simulation-hardware gap is not absolute and may be mitigated through noise-tailored circuit architectures.
- `7012f13a70a3` (boundary_condition): Demonstrates noise-resilient shallow circuits that preserve partial performance on QPUs, showing that not all quantum approaches suffer equally from hardware constraints and that circuit depth management can partially close the validity gap.

**C2 flagged_papers:**
- `11ff02556b47` (partially_grounded): The memo includes a scalability caveat, but it also says hardware QSVC was comparable to noiseless simulation and classical counterparts and describes the feature map as noise resistant.
- `3506790b2a7a` (partially_grounded): This memo supports simulator use and six-dimensional compression, yet it also reports strong fraud-class F1 and robustness under simulated noise, so it does not support the theme's strongest validity-gap wording.
- `c8872ea43678` (partially_grounded): The memo is simulator-only and notes NISQ limits, but it also reports QSVM and VQC outperforming a classical SVM, so it does not cleanly support the blanket explanation for classical superiority.

_C2 reason:_ Partially grounded. Several memos document the three ingredients of the claimed gap: 2a646809136c says "aggressive feature reduction and small balanced samples" constrain performance, c408224c2f59 reports "PCA to reduce 28 features to 7" plus explicit noise sensitivity, and 1bf5fc02b95b says "Hardware results show a practical limitation" versus simulation. 394c63b275d9 and c8872ea43678 also confirm simulator-only evidence, while 6257d900d3ef adds PCA-to-four-components and hardware constraints. However, the memos do not directly establish a multiplicative causal mechanism or that the setup systematically favors quantum, and 11ff02556b47 explicitly says trapped-ion QSVC was comparable to simulation/classical counterparts.

**C3 crosswalk entries:**
- **confirms** (high) · `f88bb4cc0c22` *Systematic Review on the Influence of Classical and Quantum*
  > "limited qubit counts, connectivity, noise, and data-encoding overheads currently contradict scalable advantage for real-world financial problems"
- **extends** (medium) · `d0568e395fbf` *A review of different techniques and challenges of quantum*
  > "NISQ devices may outperform classical computers on a narrow subset of tasks, but practical applications remain limited by qubit counts, noise, and gate depth"
- **extends** (medium) · `5308fd4d7e17` *A Structured Survey of Quantum Computing for the Financial*
  > "NISQ-era implementations are noisy and depth-limited, contradicting optimistic claims of near-term practical advantage"

### AT-FD-003 · C2=partially_grounded (medium)
**Imbalance-driven methodological heterogeneity renders quantum-classical performance comparisons non-commensurable**

_Interpretation:_ Extreme class imbalance at or below 1% fraud forces a cascade of methodological choices—rebalancing strategy, metric selection, threshold calibration—each of which can independently alter which model appears superior. When quantum classifiers trained on SMOTE-rebalanced data are compared against classical baselines trained on raw distributions using different metrics, the comparison loses scientific validity. The field lacks standardized evaluation protocols, meaning that many reported quantum advantages or disadvantages may be artifacts of incompatible experimental designs rather than genuine capability differences. This heterogeneity undermines the cumulative knowledge-building that systematic reviews depend upon.

_grounded_in DT:_ DT-FD-002, DT-FD-004

**B2 counter_evidence:**
- `2a646809136c` (boundary_condition): Provides a controlled comparison where both quantum and classical models are evaluated under identical preprocessing and multiple evaluation metrics, with classical XGBoost still outperforming, suggesting that clear performance differences can emerge even under commensurable experimental design.

**C2 flagged_papers:**
- `1be7c19fc967` (partially_grounded): The memo clearly states real-time fraud and class imbalance, but it does not discuss incompatible preprocessing, thresholding, or metric choices across quantum and classical comparisons.
- `291abba8a19e` (partially_grounded): This memo shows balanced-accuracy evaluation and deployment/governance concerns, not a broader methodological-heterogeneity argument about non-commensurable comparisons.
- `2a646809136c` (misaligned_claim): The memo describes a controlled comparison using fraud-relevant metrics under shared constraints, so it is evidence that commensurable quantum-classical evaluation can be done.
- `76bf72482fcf` (misaligned_claim): This memo emphasizes real datasets, shared fraud-oriented metrics, and preprocessing tailored to qubit limits, which cuts against the claim that the field lacks comparable evaluation protocols altogether.

_C2 reason:_ Partially grounded. Papers 85e9109e6bb0 show performance changing as data become more balanced and under ADASYN, dda7775da9aa uses "macro-F1-based selection and class-balanced evaluation," and 8372b98f0875 centers fraud evaluation on "average precision on a fraud-imbalanced dataset"; together these memos support the claim that imbalance materially changes preprocessing and metric choices. c408224c2f59 adds SMOTE and PCA as fraud-specific setup decisions that can affect outcomes. But the stronger claim that comparisons are broadly non-commensurable is not fully grounded, because 2a646809136c and 76bf72482fcf explicitly describe fraud-relevant metrics and comparable evaluation setups rather than incompatible designs.

**C3 crosswalk entries:**
- **extends** (medium) · `f88bb4cc0c22` *Systematic Review on the Influence of Classical and Quantum*
  > "many QML algorithms (QSVM, QNN, QAOA, QAE, etc.) are still experimental and lack extensive benchmarking against classical baselines on real financial datasets"
- **complements** (low) · `246963801530` *A Systematic Literature Review of Classical and Quantum Machine*
  > "Lack of standardized benchmarks and evaluation protocols across QML-for-PO studies, making cross-study comparisons difficult"

### AT-FD-004 · C2=unsupported (medium)
**Hybrid architectures as pragmatic accommodation: quantum components occupy rather than earn their pipeline niche**

_Interpretation:_ The universal adoption of hybrid quantum-classical pipelines reflects a pragmatic response to NISQ limitations rather than a principled architectural choice grounded in demonstrated quantum contribution. Classical components consistently handle the computationally demanding stages—preprocessing, feature engineering, final classification—while the quantum module occupies a narrow role such as kernel estimation or variational encoding that classical methods can approximate without quantum overhead. Real-time latency requirements further erode the quantum component's operational viability, as cloud-based QPU access introduces delays incompatible with millisecond fraud decision windows. This pattern suggests quantum components are inserted as proof-of-concept placeholders rather than performance-critical pipeline stages.

_grounded_in DT:_ DT-FD-007, DT-FD-008, DT-FD-004

**B2 counter_evidence:**
- `e6d5993eabdd` (opposing_claim): Proposes a hybrid architecture where a quantum ensemble optimizer combines diverse classifier outputs via QUBO formulation, demonstrating a role for quantum computation in decision fusion that classical ensemble methods do not straightforwardly replicate.
- `3506790b2a7a` (opposing_claim): Reports that Quantum-SMOTE integrated into a hybrid pipeline outperforms traditional rebalancing approaches by 6.4 percentage points, suggesting the quantum component contributes genuine value in the data augmentation stage rather than merely occupying a placeholder role.

**C2 flagged_papers:**
- `1be7c19fc967` (unsupported): The memo reports lower false positives/false negatives and sub-30ms latency for the hybrid QC+GenAI design, so the quantum role is presented as contributing value rather than merely occupying space.
- `35505140af55` (partially_grounded): This memo supports latency and cloud/QPU constraints, but it also says QGNN improves recall, F1, and AUC, so it does not support a pure placeholder interpretation.
- `468c3327bdef` (partially_grounded): The paper is mainly conceptual about deployment pain points and compliance barriers; it does not provide evidence that quantum components fail to earn a useful operational role inside hybrid pipelines.
- `58a29f9f57a7` (misaligned_claim): The memo identifies the QUBO-based ensemble fusion as the strongest fraud-detection result, directly contradicting the claim that the quantum component is just a proof-of-concept placeholder.
- `ba8e571f1e45` (misaligned_claim): This memo says VQC models outperform classical baselines on average precision and recall trade-offs in a real fraud setting, so the quantum stage is framed as substantively useful despite current constraints.
- `bcfb2bcd887f` (misaligned_claim): The memo reports statistically significant gains over classical methods and resource-efficiency gains, which is positive evidence for the quantum component rather than accommodation-only evidence.
- `e6d5993eabdd` (partially_grounded): The classical LSTM is faster and generalizes better, but the hybrid model still improves recall and F1, so the memo supports practical caveats more than the claim that the quantum role is unearned.

_C2 reason:_ Unsupported. The closest support is 76bf72482fcf, which says "Hybrid classical-quantum pipelines are presented as the most balanced and practical short-term option," and 35505140af55/e6d5993eabdd add latency and efficiency caveats. But most sampled memos present the quantum block as materially useful rather than a placeholder: 58a29f9f57a7 says the "QUBO ensemble" gives the strongest minority-class result, bcfb2bcd887f reports "statistically significant gains over classical methods," and ba8e571f1e45 says quantum models outperform classical baselines on average precision/recall. The memo set therefore supports pragmatic hybridization under constraints, not the stronger claim that quantum components merely occupy an unearned niche.

### AT-FD-005 · C2=partially_grounded (medium)
**Speculative momentum: prospective quantum fraud narratives outpace and misrepresent the empirical evidence base**

_Interpretation:_ A disproportionate fraction of the quantum fraud detection literature consists of conceptual papers projecting benefits—faster anomaly detection, improved pattern recognition, reduced false positives—without producing original experiments, while empirical papers frequently demonstrate classical parity or superiority. This creates an inverted evidence pyramid where the volume of optimistic narratives exceeds the volume of supporting experiments. The few genuinely positive results, such as kernel scaling advantages at 10-20 qubits, operate at scales orders of magnitude below production fraud systems processing billions of daily transactions. The resulting rhetoric-evidence gap suggests that quantum fraud detection research is partially sustained by technology-push dynamics rather than demonstrated pull from unsolved detection challenges.

_grounded_in DT:_ DT-FD-009, DT-FD-003, DT-FD-004

**B2 counter_evidence:**
- `b253d747bcc9` (opposing_claim): Reports quantum projected-kernel one-class SVMs achieving win probabilities above 64% against classical baselines in anomaly detection, providing empirical evidence that specific quantum formulations can outperform classical counterparts on controlled fraud detection tasks.
- `8372b98f0875` (boundary_condition): Demonstrates IQP kernels with data re-uploading achieving approximately 15% higher average precision than classical RBF at 20 qubits, offering concrete empirical substantiation that partially validates the speculative narratives for a specific quantum approach.

**C2 flagged_papers:**
- `3506790b2a7a` (misaligned_claim): This memo reports a large empirical fraud study with strong fraud-class F1 and improvements over conventional models, so it is not just speculative rhetoric or a tiny-scale positive result.
- `85fbbb9f2a42` (partially_grounded): The memo partly fits the cautionary story because results are simulator-only and baselines were not well tuned, but it still reports small empirical quantum gains rather than pure narrative projection.

_C2 reason:_ Partially grounded. The sample does contain clear prospective rhetoric without original fraud experiments: 33ecea26692d names fraud as a "future application area," 36cd7ccae10c is "conceptual and does not benchmark fraud models on real transaction data," and 75c40280653d is likewise conceptual. The empirical memos also often favor caution: 2a646809136c says classical XGBoost outperforms the quantum model, 76bf72482fcf says "Classical ensemble models remain the strongest baseline," and 9352e26d9232 reports classical SVM higher accuracy with "no proven quantum advantage yet." Still, 3506790b2a7a is a substantial positive empirical result rather than speculative momentum, and 85fbbb9f2a42 provides limited simulator-only positive evidence, so the theme overstates how one-sided the evidence base is.

**C3 crosswalk entries:**
- **contradicts** (medium) · `b0f18b08964e` *Quantum computing and financial risk management: A theoretical review*
  > "Quantum machine learning could enhance tasks such as credit scoring, fraud detection, and market prediction by finding patterns classical ML might miss"
- **confirms** (high) · `67f83161d410` *A Survey of Quantum Computing for Finance*
  > "a lack of robust empirical evidence of generalization or training advantages over classical ML on realistic financial datasets, contradicting some optimistic promotional claims"
- **extends** (medium) · `f88bb4cc0c22` *Systematic Review on the Influence of Classical and Quantum*
  > "many QML algorithms (QSVM, QNN, QAOA, QAE, etc.) are still experimental and lack extensive benchmarking against classical baselines on real financial datasets"

## C2 silo summary

- **themes_checked**: 5
- **grounded**: 0
- **partially_grounded**: 4
- **unsupported**: 1
- **overall_note**: The FD analytical layer is directionally grounded on experimental constraints, imbalance, and the presence of conceptual hype, but several themes extrapolate from memo-level observations to stronger field-level causal claims. The recurring issue is overreach: many memos support narrower statements about specific methods or deployment limits, while claims about monoculture motives or placeholder quantum roles are not directly evidenced by the sampled papers.