---
aliases:
- Analysis of a hybrid quantum network for classification tasks
- Analysis hybrid quantum network
authors:
- Gerhard Hellstern
auto_detected: true
classification: ''
contradiction_flags:
- contradiction:classical-vs-quantum
- contradiction:scalability
doi: 10.1049/qtc2.12017
evaluation_type: simulator
evidence_type: ''
has_quantitative_results: true
idea_tags:
- idea:quantum-advantage
- idea:near-term-feasibility
- idea:hybrid-approach
journal_or_venue: IET Quantum Communication
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
source_type_confidence: high
step1_date: '2026-04-14T09:21:06.234919'
step1_model: gpt-5-mini
step2_date: '2026-04-14T09:21:06.234919'
step2_model: gpt-5-mini
step3_date: '2026-04-14T09:21:06.234919'
step3_model: gpt-5-mini
step4_date: '2026-04-14T09:21:06.234919'
step4_model: gpt-5-mini
step5_date: '2026-04-14T09:21:06.234919'
step5_model: gpt-5-mini
step6_date: '2026-04-14T09:21:06.234919'
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
- method/variational-nisq
- method/quantum-ml
- method/hybrid-quantum-classical
- idea/quantum-advantage
- idea/near-term-feasibility
- idea/hybrid-approach
- contradiction/classical-vs-quantum
- contradiction/scalability
title: Analysis of a hybrid quantum network for classification tasks
topic_tags:
- quantum-ml-finance
- credit-lending
year: '2021'
zotero_key: ''
---

## Abstract summary
The paper presents a hybrid classical–quantum neural network architecture for supervised classification that embeds a parametrised quantum circuit between classical encoding and decoding networks. The author evaluates this approach on realistic datasets (finance credit-scoring data and MNIST) using TensorFlow Quantum, reports improved performance over a comparable classical network on several metrics, and investigates overfitting with proposed regularisation strategies for the hybrid model.
## Methodology
The study develops and evaluates a hybrid quantum-classical neural network (QNet) for binary and multiclass classification on realistic datasets (finance credit scoring and MNIST). The hybrid architecture places a classical encoding neural network in front of a parametrised quantum circuit and a classical post-processing network after quantum measurement. The classical encoder maps high-dimensional input features to rotation angles that parametrise single-qubit rotations Ry(phi_i1) Rz(phi_i2) Ry(phi_i3) for each qubit; CNOT gates provide entanglement. The variational (trainable) part of the circuit applies layers of parametrised single-qubit rotations and entangling CNOTs; the number of variational parameters equals 3 * n_qubits * n_layers. Two encoding strategies are compared: (1) encode once then apply variational layers repeatedly, and (2) data re-uploading where encoding is repeated together with each variational layer. Qubit measurement expectation values are passed to the classical output network that ends with a softmax; categorical cross-entropy is used as loss. Training is performed end-to-end with backpropagation using TensorFlow Quantum (TFQ) with the ADAM optimizer (learning rate 0.01). The hybrid QNet is compared against a fully classical neural network (NNet) where the quantum block is replaced by a classical hidden layer with approximately equal parameter count. Regularisation experiments include dropout between the quantum measurements and the post-processing network and L2 penalties on measurement outputs (and attempted L2 on angles). Performance is evaluated using ACC and AUC (finance) and ACC/confusion matrices (MNIST), reporting both training and held-out test results.

**Algorithms used:** Variational Quantum Classifier (VQC / parametrised quantum circuit), Data re-uploading (repeated encoding), Classical feedforward neural network (encoder and post-processing), ADAM optimizer, Dropout regularization, L2 regularization (on measurement outputs)
**Frameworks:** TensorFlow Quantum

**Experimental setup:** All experiments were conducted using TensorFlow Quantum simulators. The author reports that TFQ allowed simulation of circuits up to ~10 qubits and ~10 layers on a local notebook (Intel Pentium i7, 16 GB RAM) within a few hours. No physical quantum hardware/QPU was used.

**Dataset:** Finance: Lending Club credit scoring dataset (Kaggle: wordsforthewise/lending-club) with six features scaled to [0,1]. Two prepared samples: Sample I balanced (default rate 50%, training size 340), Sample II unbalanced (original default rate ~16.67% in full dataset, training size 900). Also MNIST benchmark (handwritten digits 0-9) was used: greyscale 28x28 images.
## Experiment details
### Input
{'finance': {'source': 'Kaggle (wordsforthewise/lending-club)', 'features': 6, 'preprocessing': 'Features scaled to [0,1]; for Sample I class balance was adjusted to 50% default; for Sample II original unbalanced distribution retained.', 'training_sizes': {'sample_I': 340, 'sample_II': 900}}, 'mnist': {'source': 'MNIST (standard benchmark)', 'preprocessing': 'Images 28x28 (784 pixels). A classical encoder neural network front-end was used to reduce dimensionality to match the available number of qubits.', 'training_size': 1000, 'test_size': 10000}}

### Process
{'pipeline': ['Preprocess input: scale finance features to [0,1]; optionally balance classes (Sample I). For MNIST flatten or feed images into classical encoder to reduce dimensionality.', 'Classical encoder NN maps input features to rotation angles (phi_ij) used for per-qubit encoding gates Ry(phi_i1) Rz(phi_i2) Ry(phi_i3).', 'Apply CNOT entangling gates after encoding.', 'Apply variational (trainable) layers: for each layer, apply per-qubit parametrised rotations and entangling CNOTs. Two variants: (a) encode once then apply nlayers variational layers; (b) data re-uploading: repeat encoding + variational layer nlayers times.', 'Measure qubits (expectation values); feed measurement results into classical post-processing NN ending with softmax.', 'Train end-to-end with backpropagation using TensorFlow Quantum. Loss: categorical cross-entropy. Optimizer: ADAM with learning rate 0.01.', 'Compare QNet performance to a classical NNet where the quantum block is replaced by a classical hidden layer with approximately equal number of parameters.', 'Apply regularisation experiments: dropout layer between quantum measurement outputs and post-processing NN (dropout probability used e.g. 0.58) and L2 regularisation on measurement outputs (tunable). L2 regularisation on angle parameters was tested and found to degrade performance.'], 'parameters_tuned_and_observed': 'n_qubits and n_layers varied (examples: n_qubits = n_layers = 8 used for finance; MNIST experiments used n_qubits in [2,4,8,12] and varied nlayers). Number of variational parameters n = 3 * n_qubits * n_layers. Training epochs reported in examples (e.g., 30 epochs when using dropout).'}

### Output
{'metrics_reported': ['Accuracy (ACC) on training and test sets', 'Area Under ROC Curve (AUC) for binary finance experiments', 'Confusion matrix for MNIST', 'Training convergence curves'], 'baselines': 'Fully classical neural network (NNet) with same input and output layers and a hidden layer sized to produce approximately equal number of parameters as the hybrid QNet.', 'example_results': {'finance_sample_I_nqubits=nlayers=8': {'QNet_no_reupload': {'ACC_train': 0.68, 'AUC_train': 0.74, 'ACC_test': 0.59, 'AUC_test': 0.65}, 'QNet_with_reupload': {'ACC_train': 0.78, 'AUC_train': 0.86, 'ACC_test': 0.68, 'AUC_test': 0.72}, 'Classical_NNet': {'ACC_train': 0.62, 'AUC_train': 0.66, 'ACC_test': 0.62, 'AUC_test': 0.77}}, 'finance_sample_II_nqubits=nlayers=8': {'QNet_no_reupload': {'ACC_train': 0.84, 'AUC_train': 0.72, 'ACC_test': 0.83, 'AUC_test': 0.55}, 'QNet_with_reupload': {'ACC_train': 0.84, 'AUC_train': 0.77, 'ACC_test': 0.84, 'AUC_test': 0.55}, 'Classical_NNet': {'ACC_train': 0.83, 'AUC_train': 0.66, 'ACC_test': 0.83, 'AUC_test': 0.51}}, 'mnist_example': {'QNet': {'ACC_train': 0.98, 'ACC_test': 0.81}, 'Classical_NNet': {'ACC_train': 0.83, 'ACC_test': 0.81}}}}

### Parameters
- n_qubits_examples: [2, 4, 8, 12]
- n_layers_examples: [1, 2, 4, 8]
- parameter_count_formula: n_parameters = 3 * n_qubits * n_layers (variational) + encoder/post-processing NN parameters
- optimizer: ADAM
- learning_rate: 0.01
- loss_function: categorical_crossentropy
- regularization: {'dropout_between_quantum_and_postNN': 0.58, 'L2_on_measurements': 'tunable; used to reduce overfitting', 'L2_on_angles': 'tested; degraded performance'}
- epochs_example: 30
- shots: None

### Hardware
{'simulator': 'TensorFlow Quantum simulator', 'compute': 'Local notebook (Intel Pentium i7 CPU), 16 GB RAM. Author remarks simulation of up to ~10 qubits and ~10 layers feasible in a few hours on such hardware.', 'quantum_hardware_used': None, 'cloud_provider': 'None used for QPU access (TFQ is a Google Research project but no QPU access was utilized)'}

### Reproducibility
The paper states that data supporting the findings are available from the corresponding author upon reasonable request and cites the Kaggle Lending Club dataset (https://www.kaggle.com/wordsforthewise/lending-club). Code is not provided in the paper. Experiments were implemented with TensorFlow Quantum; reproducing results requires TFQ and the described architecture/hyperparameters. No public code repository was indicated.
## Findings
- [supported] A hybrid classical–quantum network (QNet) that places a parametrised quantum circuit between two classical neural network layers can be trained to perform supervised classification on non-trivial datasets (finance credit scoring and MNIST).
- [supported] In experiments reported, the hybrid QNet outperformed a classical neural network (NNet) with a similar number of parameters on several performance measures (ACC, AUC) for the tested configurations.
- [supported] Data re-uploading (repeating the data encoding between variational layers) yielded better performance than only repeating the variational part in the experiments.
- [supported] Overfitting occurs with the hybrid approach (high training accuracy with degraded test accuracy); classical regularisation techniques (dropout between quantum measurements and the post-processing classical layers, L2 on measurement outputs) can reduce overfitting.
- [supported] Regularising the angles (quantum circuit parameters) via L2 destroyed classification ability in the reported experiments, while regularising measurement outputs (classical side) could be fine-tuned to mitigate overfitting.
- [supported] The hybrid approach enables handling high-dimensional classical inputs (e.g., MNIST 784 features) by using a classical encoder to reduce dimensionality to the number of qubits; experiments used this to train on MNIST subsets.
- [supported] The QNet showed faster training progress (convergence) than the comparable classical NNet in the MNIST experiments.
- [supported] Classification performance depends on the hybrid network 'complexity' (number of qubits and number of variational layers); a jump in performance was observed between 2 and 4 qubits, with diminishing returns beyond ~8–12 qubits in the reported tests.
- [supported] Experiments were performed using TensorFlow Quantum simulators (simulated quantum circuits); reported results come from simulated (ideal) quantum environments rather than physical hardware.
- [speculative] Entanglement of qubits is expected to improve QML performance (stated expectation, not specifically proven in these experiments).
- [speculative] The hybrid approach, implemented in TensorFlow Quantum, could in principle be deployed within Google's AI ecosystem and on devices in the future (deployment suggested but not demonstrated on hardware).

**Results summary:** The paper presents a hybrid classical–quantum classifier (QNet) where a classical encoder reduces input dimensionality to parameters for a parametrised quantum circuit; a classical post-processing network then maps measurement outcomes to outputs. In simulated experiments on a balanced and unbalanced finance credit dataset and on a 1,000-sample subset of MNIST, the QNet generally outperformed a classical neural network with a similar parameter count, learned faster on MNIST, and benefited from data re-uploading. Overfitting was observed; regularisation via dropout on measurement outputs or L2 on measurement outputs reduced overfitting, while L2 on quantum angles harmed performance. Results were obtained on TensorFlow Quantum simulators and not on physical quantum hardware.

**Performance claims:**
- Finance sample I (balanced, 340 training observations, nqubits=nlayers=8): QNet with data re-uploading — ACC_train 0.78, AUC_train 0.86, ACC_test 0.68, AUC_test 0.72.
- Finance sample I (same config): QNet without data re-uploading — ACC_train 0.68, AUC_train 0.74, ACC_test 0.59, AUC_test 0.65.
- Finance sample I (classical NNet baseline): ACC_train 0.62, AUC_train 0.66, ACC_test 0.62, AUC_test 0.77.
- Finance sample II (unbalanced, 900 training observations, nqubits=nlayers=8): QNet without data re-uploading — ACC_train 0.84, AUC_train 0.72, ACC_test 0.83, AUC_test 0.55.
- Finance sample II (with data re-uploading): ACC_train 0.84, AUC_train 0.77, ACC_test 0.84, AUC_test 0.55.
- Finance sample II (classical NNet baseline): ACC_train 0.83, AUC_train 0.66, ACC_test 0.83, AUC_test 0.51.
- MNIST (training set 1,000 images, full test set 10,000): QNet — ACC_train 0.98, ACC_test 0.81; NNet baseline — ACC_train 0.83, ACC_test 0.81.
- Regularisation via dropout (dropout probability 0.58) in QNet with nqubits=nlayers=8 produced train ≈ test ≈ 0.75 after 30 epochs on the MNIST experiment subset.
- L2 regularisation applied to measurement outputs reduced the training–validation accuracy gap in MNIST experiments; L2 on quantum angles eliminated useful classification ability (qualitative experimental observation).
- Observed dependence on model complexity: notable ACC increase between 2 and 4 qubits; performance plateaued beyond ~8–12 qubits in the MNIST tests (qualitative).
## Quantum advantage claim
**Classification:** speculative

The paper reports empirical advantages of the hybrid QNet over a matched classical NNet in simulated experiments (better ACC/AUC and faster training on tested datasets). However, results are from ideal quantum simulators, limited dataset sizes/configurations, and do not constitute a general or hardware-demonstrated quantum advantage; the claim is therefore presented as preliminary/speculative.
## Limitations
- NISQ-era constraints: available quantum hardware is noisy and limited in qubit count and circuit depth (author-stated).
- Variational quantum classifier (VQC) encoding scales the required number of qubits with the number of classical features (author-stated), motivating the hybrid approach.
- All experiments were performed on an ideal quantum simulator rather than on physical quantum hardware (author-stated).
- Restrictive access to Google's quantum hardware limits deployment and testing on real devices (author-stated).
- Observed overfitting in several experiments; regularisation is required (author-stated).
- Regularisation of quantum parameters was not achieved — regularising angles fed into the quantum circuit destroyed classification performance in the experiments; only classical-output regularisation was effective (author-stated).
- Reported performance improvements are relative and depend on hyperparameter choices; absolute gains can be altered by tuning (author-stated).
- [inferred] Scalability to truly large industrial financial datasets (many thousands of features/samples) is not demonstrated: experiments used relatively small training sets (e.g., 1,000 MNIST samples, small finance samples).
- [inferred] Comparison baseline is limited: hybrid QNet was compared only to a classical neural net with similar parameter count, not to a broader set of classical ML models (e.g., tree ensembles, SVMs).
- [inferred] Sensitivity to hyperparameters and architectural choices (number of qubits, layers, encoding) is implied but not systematically explored.
- [inferred] Simulation resource limits: practical simulation of larger qubit/layer configurations on commodity hardware may be infeasible, so scaling behavior is uncertain.
- [inferred] Role and benefit of entanglement depth and specific circuit design choices across different datasets remains unclear.
## Open questions
- How to distinguish generic features of the hybrid quantum-classical network from features that are specific to particular datasets, and how are they related (author-stated)?
- What is the interdependence of different performance measures (e.g., ACC, AUC, confusion matrices) for quantum classifiers and how should they be interpreted (author-stated)?
- How can the hybrid network (and QML models in general) be regularised more thoroughly, and in particular, is there an effective scheme to regularise quantum parameters without destroying performance (author-stated)?
- How do realistic device error rates and noise on physical quantum hardware affect the results obtained on ideal simulators (author-stated)?
- Can the approach be implemented and validated in other software frameworks and on different quantum hardware (author-stated)?
- [inferred] Under what conditions is data re-uploading strictly beneficial compared to only repeating variational layers, and how does that depend on dataset characteristics?
- [inferred] What is the concrete contribution of entanglement to performance gains in these hybrid classifiers, and how does it scale with qubits/layers?
- [inferred] What are the practical scalability limits (qubits, layers, dataset size) beyond which the hybrid approach ceases to provide benefit or becomes infeasible?
- [inferred] How do hybrid quantum classifiers compare against a wider set of classical baselines (e.g., gradient-boosted trees, SVMs, logistic regression) on financial tasks?

**Future work:**
- Distinguish generic features of the hybrid network from data-related features and understand how they are connected (author-stated).
- Examine in more detail the interdependence of different performance measures for quantum classification (author-stated).
- Perform a more thorough investigation of regularisation strategies, especially methods to regularise quantum parameters (author-stated).
- Explore how realistic error rates on physical quantum devices affect classification results; test on real hardware (author-stated).
- Implement the approach in different software frameworks and evaluate on different quantum hardware (author-stated).
## Key ideas
- #idea:hybrid-approach — Proposes and implements a hybrid classical–quantum neural network (classical encoder -> parametrised quantum circuit -> classical decoder) trained end-to-end with TFQ.
- #idea:quantum-advantage — Reports cases where the hybrid QNet outperforms a classical NNet baseline on some metrics (e.g., higher test ACC in some finance samples and improved MNIST ACC), especially when using data re-uploading.
- #idea:near-term-feasibility — Demonstrates experiments on TensorFlow Quantum simulators up to ~10 qubits / ~10 layers on a consumer notebook, arguing NISQ-era applicability for small problems.
- #idea:hybrid-approach — Data re-uploading (repeated encoding) substantially improves performance vs single encoding in several experiments.
- #idea:quantum-advantage — Regularisation (dropout, L2 on measurement outputs) is necessary to limit overfitting of the hybrid model; naive L2 on angle parameters degraded performance.
- #idea:near-term-feasibility — Uses a classical encoder to reduce dimensionality to match qubit limits, highlighting data-encoding costs and preprocessing requirements for realistic datasets.
## Contradictions
- #contradiction:classical-vs-quantum — Mixed empirical outcomes: while QNet often attains higher training accuracy and sometimes higher test ACC, the classical NNet achieved higher test AUC on Finance Sample I (Classical AUC_test 0.77 vs QNet re-upload AUC_test 0.72), so superiority is not consistent across metrics.
- #contradiction:scalability — Claims of NISQ-era relevance are tempered by experiments limited to TFQ simulation of up to ~10 qubits and small encoded feature sizes; the work provides little evidence that the observed gains would scale to larger, real-world problem sizes or real QPUs.
## Notable quotes
<!-- Researcher-added — verbatim quotes with page references -->

## Researcher notes
<!-- Researcher-added — not LLM generated -->
