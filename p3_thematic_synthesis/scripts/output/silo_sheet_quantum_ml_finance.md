# Silo data sheet — quantum_ml_finance

- total papers: **313**  (single-silo: ?, multi-silo: ?)
- DT count: 14
- AT count: 7

## Descriptive themes (DT)

### DT-QML-001 · 13 papers
**Hybrid quantum-classical variational architectures as the dominant design paradigm**

The overwhelming majority of papers adopt hybrid quantum-classical pipelines where parameterized variational quantum circuits serve as the core trainable quantum layer, trained via parameter-shift gradients and classical optimizers. Classical components handle data preprocessing, feature engineering, and optimization while quantum circuits execute variational subroutines for classification, regression, and generative tasks. This hybrid variational pattern is the dominant design paradigm, motivated by NISQ hardware constraints.

### DT-QML-002 · 12 papers
**Credit risk, fraud detection, and imbalanced financial classification as primary targets**

Credit scoring, default prediction, fraud detection, and insurance fraud classification are the most frequently studied financial tasks, consistently framed as binary classification on severely imbalanced datasets with fraud rates of 0.17-3.5% and default rates of 10-22%. Papers routinely apply SMOTE, undersampling, or class-weighted losses and widely prefer recall, F1, AUC, and precision over raw accuracy as evaluation metrics.

### DT-QML-003 · 15 papers
**NISQ hardware noise, qubit limits, and error mitigation constrain practical deployment**

Current NISQ devices impose limited qubit counts, short coherence times, high gate error rates, and connectivity constraints that prevent running quantum finance models at realistic scale. Papers studying hardware execution report degraded performance and evaluate error mitigation techniques including zero-noise extrapolation, readout calibration, and shallow circuit design to preserve model fidelity under noise.

### DT-QML-004 · 13 papers
**Quantum kernel methods and feature maps for financial class separability**

Quantum support vector machines and quantum kernel classifiers using quantum feature maps are among the most implemented methods, leveraging ZZ, Pauli, and IQP feature map circuits to embed classical financial data into high-dimensional Hilbert spaces. The hypothesis is that quantum encodings capture nonlinear relationships that classical feature spaces miss, improving class separability for fraud, credit risk, and market direction classification.

### DT-QML-005 · 15 papers
**Classical baselines match or outperform quantum models and practical advantage remains undemonstrated**

Multiple papers report that classical baselines such as XGBoost, Random Forest, classical SVMs, and LSTMs match or outperform quantum variants when properly tuned. Review and empirical papers consistently conclude that no end-to-end practical quantum advantage has been demonstrated for financial prediction or classification, with reported gains described as modest, conditional, or dependent on idealized simulation settings.

### DT-QML-006 · 13 papers
**Data encoding strategies and dimensionality reduction as the critical quantum input pipeline**

The choice of quantum data encoding strategy and dimensionality reduction method materially affects model accuracy, trainability, and resource requirements. Papers routinely apply PCA, mutual information, or QUBO-based feature selection to compress high-dimensional financial feature sets to 4-12 inputs before angle, amplitude, or basis encoding, treating this input pipeline as a critical design decision rather than routine preprocessing.

### DT-QML-007 · 14 papers
**Simulator-only evaluation and conceptual reviews dominate the empirical landscape**

The vast majority of empirical studies use noiseless or noisy quantum simulators rather than real hardware, and a substantial fraction of the literature consists of review, conceptual, or framework papers without new empirical experiments. Hardware runs, when attempted, are restricted to very small problem sizes with degraded fidelity, revealing a field that is heavily conceptual and simulator-dependent relative to validated experimental results.

### DT-QML-008 · 11 papers
**Stock and market time-series forecasting via quantum LSTM and hybrid recurrent models**

A large number of papers formulate financial prediction as stock price or market direction forecasting using OHLCV data augmented with technical indicators. Multiple papers replace or augment classical LSTM gates with variational quantum circuits to create QLSTM models, reporting competitive prediction accuracy with fewer trainable parameters but acknowledging limitations of small datasets and simulator-only execution.

### DT-QML-009 · 14 papers
**Quantum generative models for financial distributions and the state preparation bottleneck**

Quantum generative adversarial networks, quantum circuit Born machines, and quantum quantile models are studied for learning probability distributions of financial returns, implied volatilities, and asset prices. Efficient loading of classical distributions into quantum states is identified as a fundamental bottleneck, since exact preparation requires exponentially many gates while approximate methods via qGANs or tensor networks introduce fidelity-depth-cost trade-offs.

### DT-QML-010 · 7 papers
**Barren plateaus and vanishing gradients as fundamental trainability barriers**

Barren plateaus, where gradient variance vanishes exponentially with circuit depth or qubit count, are widely reported as a major obstacle to scaling variational quantum models for finance. Authors respond with shallow circuits, local cost functions, hardware-efficient ansaetze, and adaptive strategies, but the fundamental trainability problem remains a key concern for practical circuit design.

### DT-QML-011 · 7 papers
**Quantum reinforcement learning agents for financial trading decisions**

Several papers apply quantum-enhanced reinforcement learning to trading and portfolio decision tasks, replacing classical policy or value network encoders with variational quantum circuits within standard RL frameworks like A3C, PPO, and DQN. Trading environments are modeled as MDPs with buy/hold/sell actions and reward signals based on returns or Sharpe ratios.

### DT-QML-012 · 7 papers
**Quantum anomaly detection for financial transaction monitoring**

Papers propose quantum autoencoders, quantum one-class SVMs, and quantum kernel-based anomaly detectors for identifying fraudulent or anomalous financial transactions. These models train on normal transaction data and flag deviations via reconstruction error or decision boundary distance, targeting credit card fraud and high-frequency trading anomalies.

### DT-QML-013 · 13 papers
**Small-data regimes and parameter efficiency as potential quantum niches**

Several papers report that quantum models are more competitive in small-data regimes or scarce-label scenarios, and frequently achieve comparable predictive performance with 60-230x fewer trainable parameters than classical baselines. This parameter efficiency is attributed to the exponential dimensionality of Hilbert space and entanglement-based feature interactions, suggesting a potential niche for near-term quantum advantage.

### DT-QML-014 · 7 papers
**QUBO-based optimization for portfolio selection and feature subset selection**

Papers formulate portfolio selection, feature subset selection, and asset clustering as quadratic unconstrained binary optimization problems solved by QAOA, VQE, or quantum annealers. Budget constraints are encoded as quadratic penalty terms in the QUBO Hamiltonian, and runtime scaling is studied relative to classical solvers.

## Analytical themes (AT)

### AT-QML-001 · C2=partially_grounded (medium)
**The NISQ pragmatism trap: hybrid design as both enabler and architectural ceiling**

_Interpretation:_ The universal adoption of hybrid quantum-classical architectures reflects a pragmatic accommodation to NISQ hardware, but this accommodation creates a structural ceiling on demonstrable quantum advantage. By offloading most computation to classical components and restricting quantum circuits to shallow variational subroutines, the field limits the quantum contribution to a narrow bottleneck. Barren plateaus further constrain circuit depth, producing a self-reinforcing cycle where practical designs are too shallow for advantage and expressive designs are too deep to train or execute reliably.

_grounded_in DT:_ DT-QML-001, DT-QML-003, DT-QML-010

**B2 counter_evidence:**
- `35da1ebe30e2` (boundary_condition): Proposes adaptive ansatz strategies and local cost functions that partially mitigate barren plateaus, suggesting the trainability ceiling may be softened through circuit design rather than being an absolute barrier.
- `2abf80ef91e3` (boundary_condition): Demonstrates that carefully structured variational circuits with problem-specific ansaetze achieve convergent training even at moderate depths, qualifying the universality of the shallow-circuit constraint.

**C2 flagged_papers:**
- `0d70169cb87f` (partially_grounded): The memo supports practical evaluation constraints and the importance of baselines, but it does not say hybrid design creates an architectural ceiling on advantage.
- `1312e9d3c55e` (partially_grounded): This memo supports hybrid workflows and data-pipeline integration, but it does not discuss shallow-circuit bottlenecks, barren plateaus, or a self-reinforcing ceiling on advantage.
- `6190538f1800` (partially_grounded): The memo is about fault-tolerance, state preparation, and decoherence limits in general, not specifically about hybrid QML architectures offloading most computation to classical components.
- `30afc00e8912` (misaligned_claim): The memo reports "performance gains from scaling qubits and circuit depth," which cuts against the theme's stronger claim that practical designs are structurally stuck in too-shallow regimes for advantage.

_C2 reason:_ Partially grounded. Memos for 01e7ba36bcfc, 109c9406f3df, 35da1ebe30e2, and 7c795b799d02 all show the NISQ-era hybrid pattern: 01e7ba36bcfc says the architecture "reduces feature dimensionality classically so the quantum part can be used," 109c9406f3df says NISQ limits "force dimensionality reduction before quantum embedding and limit circuit size," 35da1ebe30e2 calls the "recommended hybrid quantum-classical direction" the most actionable path, and 7c795b799d02 says the method uses a "practical hybrid workflow rather than an idealized quantum-only model." However, the stronger causal claim that hybridization itself creates a universal ceiling on quantum advantage through shallow variational bottlenecks and barren plateaus is only directly evidenced in 109c9406f3df, so the theme over-extends beyond several supporting memos.

**C3 crosswalk entries:**
- **confirms** (high) · `674c681a57d0` *NExt ApplicationS of Quantum Computing – D5.7: Update of*
  > "Variational state-preparation and qGAN methods suffer from training challenges (local minima, barren plateaus) and often require multiple restarts and heavy classical optimization"
- **extends** (medium) · `d0568e395fbf` *A review of different techniques and challenges of quantum*
  > "Hybrid quantum-classical algorithms (e.g., VQE and variational approaches) are highlighted as the most promising near-term direction, especially for chemistry and potential ML tasks"
- **extends** (medium) · `f88bb4cc0c22` *Systematic Review on the Influence of Classical and Quantum*
  > "partially disputes blanket claims that QNNs and QSVMs 'maintain accuracy in noise-heavy environments' or 'consistently train significantly faster'"

### AT-QML-002 · C2=partially_grounded (medium)
**The credibility gap: quantum advantage claims untethered from rigorous financial evidence**

_Interpretation:_ The QML finance literature exhibits a systematic disconnect between theoretical optimism and empirical rigor. The majority of work is conceptual or simulator-only, classical baselines are inconsistently tuned, and claimed advantages are conditional or marginal. This gap exists because the field imported quantum computing's theoretical speedup narrative before developing the experimental infrastructure needed to test it rigorously in financial domains, creating a literature where promise systematically outpaces evidence.

_grounded_in DT:_ DT-QML-005, DT-QML-007

**B2 counter_evidence:**
- `9170a0c2d3a2` (boundary_condition): Executes experiments on real quantum hardware rather than simulators alone, providing more credible evidence that partially addresses the simulation-reality gap, though still at small scale.
- `29f1f2555efe` (boundary_condition): Provides careful methodological assessment with explicit acknowledgment of limitations and controlled classical comparisons, demonstrating that rigorous evaluation practices do exist in a minority of studies.

**C2 flagged_papers:**
- `0d70169cb87f` (partially_grounded): The memo emphasizes walk-forward validation, baselines, and governance, which supports the need for rigor, but it does not itself evidence a literature-wide credibility gap or imported speedup narrative.
- `1a05f3c9e973` (partially_grounded): This review memo stresses NISQ feasibility constraints and hybrid pathways, but it does not directly show that promise systematically outpaces evidence in financial experiments.

_C2 reason:_ Partially grounded. Several memos directly support the evidence gap: 21611a37dd85 says the HQGAN "did not achieve adequate accuracy" on the financial dataset, 4b22c753a5a4 reports "mixed" performance under comparable model sizes, 5081ec6b6068 says "pure quantum models underperform," 95ecf8c43fd1 concludes classical ensembles remain the preferred deployment choice, and f85bdc99d9eb says speedups "depend on strong assumptions" and are "conditional." But the final causal explanation—that the literature imported quantum computing's speedup narrative before the financial experimental infrastructure existed—is not stated in these memos, so the theme's explanatory layer is stronger than the memo evidence.

### AT-QML-003 · C2=partially_grounded (medium)
**The classical data bottleneck: preprocessing costs as quantum advantage's hidden tax**

_Interpretation:_ The field faces a fundamental paradox: quantum models promise advantage through high-dimensional Hilbert spaces, but accessing those spaces requires encoding classical financial data through circuits that are themselves exponentially expensive or lossy. Classical preprocessing via PCA or feature selection, and approximate state preparation via qGANs or variational loaders, effectively filter the data before it reaches the quantum component, potentially discarding the very structure that quantum processing should exploit. The encoding step thus functions as a hidden classical tax that erodes the theoretical quantum speedup.

_grounded_in DT:_ DT-QML-006, DT-QML-009

**B2 counter_evidence:**
- `59cca9744140` (boundary_condition): Proposes efficient approximate state preparation methods that achieve acceptable fidelity with polynomial circuit depth, suggesting the exponential loading cost can be circumvented for specific distribution families relevant to finance.
- `69a4901976a9` (boundary_condition): Demonstrates that quantum circuit Born machines can learn financial return distributions with compact circuits, partially addressing the state preparation bottleneck through learned rather than exact loading.

**C2 flagged_papers:**
- `50989fdc9ad1` (partially_grounded): The memo is mostly about efficient, parameter-efficient state preparation and mixture modeling; it does not itself frame preprocessing as a hidden classical tax eroding speedup.
- `55496bcdeaa7` (partially_grounded): This memo supports feature selection on a finance task, but it does not discuss encoding cost, lossy loading, or speedup erosion from classical preprocessing.
- `e0a04002122e` (partially_grounded): The memo shows QAOA-based feature selection reducing dimensionality, but it does not say the encoding step discards quantum-relevant structure or functions as a hidden tax on advantage.

_C2 reason:_ Partially grounded. The memos repeatedly show classical preprocessing or approximate loading before quantum computation: 01e7ba36bcfc says the architecture "reduces feature dimensionality classically," 85fbbb9f2a42 says "LDA is the key preprocessing choice," 59cca9744140 identifies loading depth as a bottleneck, and both 872cedb13e27 and c57f6422ed7b describe qGANs as approximate loaders for downstream pricing/risk workflows. Still, the strongest interpretive move—that preprocessing necessarily discards the very structure quantum methods should exploit and thereby imposes a hidden tax that erodes theoretical speedup—is more sweeping than what several memos explicitly claim.

### AT-QML-004 · C2=partially_grounded (medium)
**Application-selection bias: evaluating quantum on classical ML's home turf**

_Interpretation:_ The concentration on credit scoring, fraud detection, stock prediction, and anomaly detection reflects a field that evaluates quantum models on tasks specifically optimized for classical ML over decades. This selection bias systematically disadvantages quantum approaches while providing false comparability: the literature mostly asks whether quantum can match classical on classical's strongest benchmarks rather than identifying financial problems where quantum structure offers inherent advantages. The imbalanced-classification and time-series tasks dominating the silo are precisely those where ensemble methods and deep learning have been extensively refined.

_grounded_in DT:_ DT-QML-002, DT-QML-008, DT-QML-012

**B2 counter_evidence:**
- `69a4901976a9` (boundary_condition): Targets quantum distribution learning for financial returns, a task without a simple classical analog, demonstrating that the silo does contain quantum-native application formulations beyond standard supervised benchmarks.
- `3f8ab7317ca4` (opposing_claim): Formulates portfolio optimization as a QUBO problem with provable classical hardness, illustrating that some financial tasks are inherently better matched to quantum hardware than classical ML benchmarks.

**C2 flagged_papers:**
- `01a1ecaddb94` (partially_grounded): The memo clearly concerns stock prediction, but it does not compare that choice to quantum-native financial problems or argue that the field is biased toward classical ML's home turf.
- `14777484b99d` (partially_grounded): This anomaly-detection memo supports use of a familiar ML task, yet it focuses on algorithmic speedup and error bounds rather than on the theme's broader selection-bias diagnosis.
- `7012f13a70a3` (partially_grounded): The memo benchmarks fraud anomaly detection, but it does not state that choosing such tasks creates false comparability with mature classical ML.

_C2 reason:_ Partially grounded. The sampled memos overwhelmingly sit on standard classical-ML tasks—stock prediction (01a1ecaddb94), credit risk/default classification (0c49909a73ca, 10be86fe1795), fraud/transaction classification (394c63b275d9, 924cd91fefd6, d186493da11a), and anomaly detection (14777484b99d, 7012f13a70a3)—which supports the observation that QML finance is being tested on classical ML's established benchmark terrain. But the additional claim that this reflects a field-wide application-selection bias that falsely centers comparability and systematically disadvantages quantum approaches is interpretive; the memos mostly describe task choices and results, not that causal diagnosis.

### AT-QML-005 · C2=partially_grounded (medium)
**The expressivity-trainability dilemma: a fundamental quantum model design constraint**

_Interpretation:_ Quantum feature maps and deep variational circuits offer theoretical expressivity advantages in exponentially large Hilbert spaces, but barren plateaus and hardware noise ensure that only shallow, low-expressivity circuits are practically trainable. This creates an unresolved design dilemma: the quantum models that could theoretically outperform classical ones are precisely those that cannot be trained or executed on current hardware. The field has not yet found circuit families that simultaneously offer high expressivity, efficient trainability, and financial-data-relevant inductive biases.

_grounded_in DT:_ DT-QML-004, DT-QML-010, DT-QML-001

**B2 counter_evidence:**
- `b9aa74e4bc0d` (boundary_condition): Shows that projected quantum kernels with structured feature maps achieve competitive classification results without requiring deep circuits, suggesting the dilemma can be partially resolved by moving expressivity into the kernel rather than the circuit.
- `1d16f793a68b` (boundary_condition): Demonstrates that local cost functions and problem-specific circuit topologies reduce barren plateau severity, indicating that domain-aware ansatz design may partially navigate the trade-off.

**C2 flagged_papers:**
- `0030bd185e0d` (unsupported): The memo discusses simulator validation and hardware constraints, but it does not address expressivity, barren plateaus, or the unresolved design trade-off claimed by the theme.
- `1312e9d3c55e` (partially_grounded): This memo covers quantum kernels and hybrid workflows, but it does not speak to the dilemma between high expressivity and trainability on current hardware.
- `8372b98f0875` (partially_grounded): The memo notes deployment scaling constraints, yet it does not connect those limits to a specific expressivity-versus-trainability dilemma inside quantum model design.
- `f9e5b6ee139d` (partially_grounded): The memo supports kernel-selection strategies that avoid variational training, but it does not directly show that highly expressive circuits are the ones that become untrainable on finance tasks.

_C2 reason:_ Partially grounded. The core dilemma is directly evidenced in 109c9406f3df, which says NISQ limits "force dimensionality reduction before quantum embedding" and that scaling hits "barren plateaus," in 2ae3455aa47b, which lists "barren plateaus" and hardware error rates as trainability barriers, and in 34a99682d20c, which presents shallow QEKLR as a practical alternative to "deep quantum models affected by barren plateaus." 6e5c81beaefd also supports the shallow-circuit side by emphasizing feature maps that are "implementable as short-depth circuits," but several other memos only discuss kernels, deployment, or hardware generally rather than the full expressivity-versus-trainability trade-off.

### AT-QML-006 · C2=partially_grounded (medium)
**Combinatorial financial optimization as the most defensible quantum-native application class**

_Interpretation:_ Unlike supervised classification tasks where quantum models compete against decades of refined classical ML, QUBO formulations for portfolio selection and quantum RL for sequential trading decisions exploit quantum parallelism for search over combinatorial spaces with provable classical hardness. This distinction is fundamental: optimization tasks map naturally to quantum Hamiltonians and have worst-case complexity arguments supporting potential speedups, whereas pattern recognition tasks lack comparable theoretical foundations for quantum advantage. The optimization-native quantum-finance interface represents a qualitatively different and more defensible research direction.

_grounded_in DT:_ DT-QML-014, DT-QML-011

**B2 counter_evidence:**
- `8a2ce0575ff1` (null_result): Reports that quantum RL agents do not consistently outperform classical RL counterparts in trading tasks, suggesting that even optimization-native quantum formulations do not automatically guarantee practical advantage.
- `99e391ee5e85` (methodological_critique): Shows that QAOA for portfolio optimization requires many variational layers to approach classical solver quality at current problem sizes, questioning whether the advantage materializes before fault-tolerant hardware.

**C2 flagged_papers:**
- `0df7a9f2fffd` (partially_grounded): The memo supports quantum-enhanced RL for adaptive financial selection, but it does not provide the theme's claimed Hamiltonian-mapping or classical-hardness rationale.
- `48fad011ea47` (partially_grounded): This memo is about hybrid quantum-classical RL trading performance on S&P 500 data, not about combinatorial hardness arguments that would make the application class especially defensible.
- `88e7d870aeb0` (partially_grounded): The memo reports improved trading outcomes for a quantum-inspired RL framework, but it explicitly says there is "no quantum speedup or hardware advantage claimed."

_C2 reason:_ Partially grounded. The optimization-native direction is well supported by 3f8ab7317ca4 and 470b798927ef, both of which formulate portfolio optimization as QUBO and report better quantum runtime scaling in the studied regime, by 5f5133229f76, which frames investor clustering as Max-Cut and emphasizes quantum exploration of many candidate cuts, and by 99e391ee5e85, which describes a "quantum-native optimization path" on financial graphs. However, the stronger claim that quantum RL for trading has comparable worst-case hardness foundations and that optimization is therefore categorically more defensible than pattern recognition goes beyond what the RL-oriented memos actually establish.

### AT-QML-007 · C2=partially_grounded (medium)
**Quantum generative models as a cross-cutting bridge between learning and computational finance**

_Interpretation:_ Quantum generative models occupy a unique dual role that distinguishes them from other QML approaches: they function simultaneously as machine learning models that learn financial distributions and as quantum state preparation subroutines for downstream pricing, risk estimation, and Monte Carlo workflows. This dual functionality, combined with reported parameter efficiency and potential small-data advantages, positions quantum generative modeling as a strategically important capability that could bridge the gap between the QML and quantum computational finance research streams, offering utility even before full quantum advantage is demonstrated.

_grounded_in DT:_ DT-QML-009, DT-QML-013

**B2 counter_evidence:**
- `b660e6ffe7f2` (methodological_critique): Highlights that state preparation fidelity degrades substantially for complex multimodal financial distributions, limiting the practical bridging capability of generative models when distribution complexity exceeds what shallow circuits can represent.
- `4b22c753a5a4` (null_result): Reports that quantum neural networks show no clear advantage over classical generative baselines at comparable model sizes, questioning whether parameter efficiency translates to genuine practical benefit.

**C2 flagged_papers:**
- `0c49909a73ca` (unsupported): This memo is about few-shot credit risk prediction with a QNN classifier, not about generative modeling, state preparation, or bridging to pricing/risk/Monte Carlo workflows.
- `59cca9744140` (partially_grounded): The memo supports efficient amplitude encoding and state preparation, but it is not itself about a generative model learning financial distributions.
- `6f139839ae4c` (partially_grounded): The memo mentions distributional inference and volatility-regime classification, but it does not clearly evidence a quantum generative model serving as a cross-cutting bridge to computational finance workflows.

_C2 reason:_ Partially grounded. The bridge claim is strongly supported where generative models also act as loaders: 872cedb13e27 says qGANs are "approximate loaders for financial distributions used in quantum pricing and risk workflows" and then uses qGAN-loaded states in QAE pricing, while 69a4901976a9, 75cd91455541, and 99d3efa89dee all show quantum generative learning on financial distributions with competitive scaling or parameter efficiency. 01326ce2213f further supports the distribution-learning side with "quantum generative modeling" on a financially motivated lognormal distribution. But not every sampled memo supports the full dual-role bridge to downstream computational finance, so the theme is broader than part of its evidence base.

## C2 silo summary

- **themes_checked**: 7
- **grounded**: 0
- **partially_grounded**: 7
- **unsupported**: 0
- **overall_note**: The silo's analytical layer is directionally grounded, but every theme stretches beyond at least part of its cited memo set. The most common issue is not fabricated evidence; it is over-interpretation, especially when the theme adds causal explanations, field-level diagnoses, or stronger claims about quantum advantage than the underlying memos explicitly support.