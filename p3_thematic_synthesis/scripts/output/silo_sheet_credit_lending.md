# Silo data sheet — credit_lending

- total papers: **63**  (single-silo: ?, multi-silo: ?)
- DT count: 8
- AT count: 4

## Descriptive themes (DT)

### DT-CL-001 · 14 papers
**Variational and kernel-based quantum classifiers for credit default prediction**

Studies implement diverse quantum supervised classification approaches for credit scoring and default prediction, including hybrid quantum-classical neural networks with variational circuits and quantum kernel or support vector methods with engineered feature maps. Both algorithmic families target binary credit outcomes on structured borrower datasets and are systematically benchmarked against classical ML baselines.

### DT-CL-002 · 6 papers
**QUBO and constrained optimization formulations for credit pipeline tasks**

Papers formulate credit-related problems as quadratic unconstrained or constrained optimization tasks solved via quantum annealing or QAOA. Applications span borrower feature selection through relevance-redundancy QUBO encodings, credit scorecard threshold optimization, loan collection action planning with borrower network effects, and SME distress propagation modeling.

### DT-CL-003 · 5 papers
**Quantum amplitude estimation for credit portfolio loss measurement**

Papers apply quantum amplitude estimation and related quantum Monte Carlo methods to compute tail-risk metrics such as VaR and CVaR for credit portfolios. Default probabilities and loss exposures are encoded into quantum circuits under models like Gaussian Conditional Independence and Merton single-factor frameworks, targeting theoretical quadratic speedups over classical Monte Carlo sampling.

### DT-CL-004 · 9 papers
**Classical preprocessing adaptations for quantum-compatible credit data**

Quantum credit studies routinely apply classical dimensionality reduction (PCA, LDA, neural front-ends) to compress borrower features before quantum encoding, and employ class-imbalance mitigation strategies (SMOTE, undersampling, balanced subsampling) to address severe default-rate skew. Both adaptations are necessitated by limited qubit budgets and the sensitivity of quantum classifiers to data characteristics.

### DT-CL-005 · 6 papers
**Empirical performance parity between quantum and classical credit models**

Multiple empirical studies report that quantum and hybrid models achieve comparable but not clearly superior performance relative to well-tuned classical baselines such as gradient boosting and XGBoost on credit-risk tasks. Observed gains are small, sometimes within error margins, and dataset-dependent rather than systematic.

### DT-CL-006 · 12 papers
**Simulator reliance and NISQ hardware degradation in quantum credit experiments**

Most quantum credit-risk experiments execute on noiseless simulators, and the minority conducted on real hardware consistently report performance degradation from noise, decoherence, and limited qubit counts. Error mitigation techniques help but add overhead, and direct runtime comparisons under simulation are acknowledged as non-meaningful for establishing practical quantum advantage.

### DT-CL-007 · 8 papers
**Survey and review literature framing quantum methods for credit risk**

A substantial portion of the corpus consists of review and survey papers that conceptually position quantum computing for credit risk without reporting original experiments. These surveys map quantum algorithms to credit use cases and consistently highlight that reported advantages are theoretical or small-scale, with hardware constraints, data encoding bottlenecks, and absent benchmarking standards remaining unresolved.

### DT-CL-008 · 5 papers
**Explainability and regulatory transparency demands for quantum lending models**

Several papers address interpretability requirements for quantum models used in credit decisions, proposing techniques such as gradient-based attributions, LIME, occlusion testing, and poisoning-based metrics. Regulatory demands for auditable decision logic in lending are cited as a key motivation, with authors noting that classical methods generally offer greater interpretability than their quantum counterparts.

## Analytical themes (AT)

### AT-CL-001 · C2=unsupported (high)
**Convergence to classical parity despite proliferating quantum circuit designs for credit scoring**

_Interpretation:_ Despite substantial architectural diversity—variational circuits, quantum kernels, data re-uploading, quantum reservoir computing—quantum credit classifiers consistently converge toward performance parity with well-tuned classical models rather than surpassing them. This pattern suggests the bottleneck is not circuit design but the fundamental encoding of tabular credit data into quantum states, where the low intrinsic dimensionality and feature heterogeneity of borrower datasets may not match the expressive strengths of quantum Hilbert spaces. The field appears locked in an exploration phase where algorithmic variety substitutes for a principled theory of when quantum encoding yields genuinely richer representations.

_grounded_in DT:_ DT-CL-001, DT-CL-005

**B2 counter_evidence:**
- `30afc00e8912` (boundary_condition): Reports competitive accuracy for a hybrid quantum-classical neural network on a specific credit dataset configuration, suggesting that under narrow experimental conditions some quantum architectures can match or marginally exceed particular classical baselines.
- `f96f14134a21` (boundary_condition): Observes dataset-dependent gains for dressed quantum circuits on certain credit benchmarks, qualifying the parity finding as contingent on dataset characteristics rather than universal.

**C2 flagged_papers:**
- `01e7ba36bcfc` (misaligned_claim): The memo reports that the hybrid model "outperforms the classical benchmark" on the balanced sample, which conflicts with a convergence-to-parity reading.
- `10be86fe1795` (misaligned_claim): The memo says the hybrid QCNN "outperformed the classical baseline" and does not mention parity, encoding bottlenecks, or lack of theory.
- `30afc00e8912` (misaligned_claim): The memo emphasizes strong predictive performance and faster training, not convergence toward classical parity.
- `b9aa74e4bc0d` (misaligned_claim): This memo reports a tuned QSVC that "outperforms the classical SVC baseline," which cuts against the theme's parity claim.
- `f55fea197b67` (misaligned_claim): The memo says QSVM outperforms classical SVM on default prediction; it does not support the claim that diverse quantum classifiers converge to parity.
- `ff36740b3b52` (unsupported): The memo focuses on loan-category modeling, minority-class weakness, and deployment limits, but it does not provide a classical-parity or encoding-bottleneck claim.

_C2 reason:_ Only 2a0770a1a995 and f9e5b6ee139d clearly support the parity portion of the claim: 2a0770a1a995 says orthogonal QNNs "match the classical residual baseline's Gini" and f9e5b6ee139d says German Credit results are "competitive with the classical model." In contrast, 01e7ba36bcfc says the hybrid model "outperforms the classical benchmark," 10be86fe1795 says the QCNN "outperformed the classical baseline," 30afc00e8912 reports "0.88 accuracy" plus faster training, b9aa74e4bc0d says the best QSVC setup "outperforms the classical SVC baseline," and f55fea197b67 says QSVM "outperform[s] classical SVM." None of the sampled memos state that tabular encoding is the bottleneck or that circuit diversity is substituting for a principled theory, so the interpretation is not recoverable from this memo set.

### AT-CL-002 · C2=partially_grounded (medium)
**Classical scaffolding as structural necessity rather than transitional convenience**

_Interpretation:_ The ubiquity of classical dimensionality reduction and imbalance correction preceding quantum encoding is not merely a pragmatic workaround but a structural dependency imposed by NISQ-era qubit limitations and noise characteristics. Because quantum circuits degrade rapidly beyond a few qubits on current hardware, classical front-ends become load-bearing components that absorb most of the computational heavy lifting, leaving the quantum layer to operate on an already-simplified representation. This raises a fundamental attribution question: observed classification performance may owe more to the quality of classical preprocessing than to quantum circuit expressiveness, undermining claims that quantum components contribute meaningful learning.

_grounded_in DT:_ DT-CL-004, DT-CL-006

**B2 counter_evidence:**
- `c434305b37fb` (boundary_condition): Demonstrates quantum amplitude estimation encoding default probabilities directly into quantum circuits for portfolio-level loss computation without requiring classical dimensionality reduction of borrower features, showing that certain quantum financial applications bypass the classical preprocessing bottleneck.
- `0cfd33edfd1a` (boundary_condition): Applies quantum kernel methods with relatively direct feature-map encoding and error mitigation, suggesting that kernel approaches may tolerate raw features better than variational classifiers even under hardware noise.

**C2 flagged_papers:**
- `0cfd33edfd1a` (unsupported): The memo stresses scarce-data kernel performance and simulator limits, but not a classical preprocessing stage doing most of the work.
- `7c795b799d02` (partially_grounded): The memo mentions preprocessing realities such as high dimensionality and imbalance, but it does not show that classical scaffolding is a structural necessity imposed by qubit limits.
- `c434305b37fb` (unsupported): This memo is about direct quantum encoding of conditional default probability in a credit-risk circuit, not a preprocessing-heavy hybrid front-end.
- `ff36740b3b52` (partially_grounded): SMOTE and imbalance concerns support the existence of classical preprocessing, but the memo does not attribute the model's performance primarily to that classical stage.

_C2 reason:_ Several memos clearly show substantial classical scaffolding before the quantum step: 01e7ba36bcfc says the model "downscale[s] many borrower features into a quantum circuit," 0c49909a73ca uses a "classical-ensemble-to-QNN pipeline," 85fbbb9f2a42 reports that "LDA is the strongest preprocessing choice" in a "two qubits" NISQ setup, and c408224c2f59 reduces the dataset to "seven PCA features and uses SMOTE." That supports a real preprocessing dependency. But the stronger causal claim that observed performance is mostly attributable to preprocessing rather than quantum expressiveness is not stated directly in these memos, and some sampled papers weaken universality: 0cfd33edfd1a emphasizes low-data kernel gains without a dimensionality-reduction front-end, while c434305b37fb directly encodes conditional default probability in a credit-risk circuit. The pattern is present, but the theme extends beyond what the memos strictly say.

**C3 crosswalk entries:**
- **confirms** (high) · `f88bb4cc0c22` *Systematic Review on the Influence of Classical and Quantum*
  > "Hybrid quantum–classical architectures (classical preprocessing + quantum subroutines) are advocated as the pragmatic near-term deployment path and form a central recommendation of the roadmap"
- **extends** (medium) · `246963801530` *A Systematic Literature Review of Classical and Quantum Machine*
  > "most practical implementations reviewed are hybrid classical–quantum pipelines (classical optimizers plus quantum subroutines, QUBO mappings, annealers) due to current hardware limits"

### AT-CL-003 · C2=partially_grounded (medium)
**Combinatorial credit decisions as a more natural quantum-hardware fit than predictive scoring**

_Interpretation:_ Quantum optimization formulations (QUBO feature selection, scorecard threshold optimization, loan collection planning) and quantum amplitude estimation for portfolio loss exploit the native strengths of quantum hardware—combinatorial search and probabilistic amplitude manipulation—more directly than quantum classifiers applied to tabular credit data. While quantum ML classifiers struggle to outperform classical models on structured borrower features, optimization and estimation approaches encode business constraints and probability distributions into Hamiltonians or amplitude operators with well-defined theoretical speedup guarantees. This divergence suggests that the credit domain's most promising quantum applications lie not in replacing classical ML for individual scoring but in solving the combinatorial and stochastic problems surrounding credit portfolio management.

_grounded_in DT:_ DT-CL-002, DT-CL-003

**B2 counter_evidence:**
- `e0a04002122e` (methodological_critique): Despite formulating feature selection as QUBO, the study executes only on simulators and does not demonstrate wall-clock advantage over classical solvers, indicating that the theoretical natural fit has not yet translated into practical hardware advantage.
- `46db6505e091` (methodological_critique): Uses a D-Wave hybrid solver that offloads substantial computation to classical processors, blurring the boundary between quantum and classical optimization and complicating claims of genuine quantum contribution to the credit decisioning task.

**C2 flagged_papers:**
- `0757b9aa9a3b` (partially_grounded): The memo supports a QUBO feature-selection formulation, but it also says gains are modest and that classical methods can beat or match the quantum approach.
- `b524b2fc9631` (partially_grounded): The memo acknowledges theoretical QAE speedup, but it also says classical Monte Carlo is already practical, so it does not clearly support a superior quantum fit.
- `e0a04002122e` (partially_grounded): This memo is about simulation-only QAOA feature selection for classifiers, so it only partly supports the broader claim about combinatorial credit decisions being the most natural quantum target.

_C2 reason:_ The sampled memos do show quantum lending work clustering around optimization and estimation tasks: 9700e75505fd "optimiz[es] borrower-level collection actions," 980d054544f5 frames threshold selection as "two QUBO optimization problems," 0a824fa99e38 "directly models portfolio loss and VaR," and c434305b37fb studies a quantum credit-risk circuit for VaR/CVaR. Those papers support the claim that combinatorial and stochastic formulations are a major application stream. However, the theme overreaches when it says these are already a more natural hardware fit with well-established advantage: 0757b9aa9a3b reports only "similar performance" and "mixed outcomes," e0a04002122e is simulation-only feature selection, and b524b2fc9631 says classical Monte Carlo already makes tail-risk estimation feasible while QAE remains theoretical. The memos support the direction of travel, but not a strong conclusion that these approaches are clearly more promising than predictive scoring.

### AT-CL-004 · C2=partially_grounded (medium)
**Quantum circuit opacity compounds lending-specific regulatory barriers to adoption**

_Interpretation:_ Credit and lending is among the most heavily regulated financial domains, with fair-lending statutes and data-protection regulations requiring that automated credit decisions be auditable and explainable. The inherent opacity of parameterized quantum circuits—where decision boundaries exist in exponentially large Hilbert spaces—compounds this regulatory challenge beyond what classical black-box models face, because existing post-hoc explanation tools such as LIME and SHAP are not validated for quantum state spaces and quantum-native interpretability methods remain nascent. The survey literature reinforces this concern by consistently ranking explainability as an unresolved prerequisite for quantum adoption in lending, while experimental papers treat it as an afterthought rather than a design constraint.

_grounded_in DT:_ DT-CL-008, DT-CL-007

**B2 counter_evidence:**
- `1a0d37057236` (boundary_condition): Develops an interpretable QNN framework with gradient-based feature attributions and inter-class alignment metrics specifically designed for credit classification, demonstrating that quantum-native explainability approaches are feasible even if still early-stage.
- `2849bbcb864e` (boundary_condition): Proposes a single-qudit QNN architecture with transparent parameter-feature mappings and poisoning-based interpretability scores, showing that architectural simplification can partially address the opacity problem for quantum lending models.

**C2 flagged_papers:**
- `2849bbcb864e` (partially_grounded): The memo acknowledges the accuracy-interpretability trade-off, but it is also a counterexample because the model was designed for transparency and tested with feature-level interpretability checks.
- `8d08019fb608` (unsupported): This survey memo discusses credit risk, feature selection, and NISQ limits, but it does not provide evidence about explainability or lending-specific regulatory opacity.
- `b9aa74e4bc0d` (partially_grounded): The memo treats interpretability as an explicit design element via LIME rather than as an afterthought, so it only partly supports the theme.
- `f85bdc99d9eb` (unsupported): The memo is mainly about end-to-end advantage, data loading, and optimization limits; it does not clearly support the lending-specific explainability claim.

_C2 reason:_ Regulatory explainability concerns are directly evidenced in 1a0d37057236, which says credit scoring operates in "regulated environments" where interpretability is "mandatory for deployment," in ca17c4baa8d1, which notes "compliance barriers," and in f88bb4cc0c22, which "flags interpretability and regulatory explainability as a major limitation." c60694a1e2ed also describes an "interpretability-versus-speed tradeoff" for lending decisions. But the theme overstates the sample when it claims experimental papers treat explainability as an afterthought or that current explanation tools are simply unusable: 2849bbcb864e was "designed to preserve a transparent link" to feature importance, and b9aa74e4bc0d explicitly "emphasized" LIME for local explanations. The regulatory barrier is real, but the stronger opacity claim is only partly grounded across this memo set.

## C2 silo summary

- **themes_checked**: 4
- **grounded**: 0
- **partially_grounded**: 3
- **unsupported**: 1
- **overall_note**: The credit-lending analytical layer contains real patterns, but most themes extend beyond what the sampled memos strictly support. The strongest overreach appears when observational benchmark or preprocessing findings are turned into causal claims about encoding bottlenecks, preprocessing attribution, or uniquely severe regulatory opacity. The most weakly grounded theme is AT-CL-001, while the optimization/estimation and explainability themes are directionally supported but still interpretively ambitious.