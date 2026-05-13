---
aliases:
- A performance characterization of quantum generative models
- performance characterization quantum generative
authors:
- Carlos A. Riofrío
- Oliver Mitevski
- Caitlin Jones
- Florian Krellner
- Aleksandar Vučković
- Joseph Doetsch
- Johannes Klepsch
- Thomas Ehmer
- Andre Luckow
auto_detected: true
classification: ''
contradiction_flags:
- contradiction:scalability
doi: ''
evaluation_type: simulator
evidence_type: ''
has_quantitative_results: true
idea_tags:
- idea:quantum-advantage
- idea:near-term-feasibility
- idea:hybrid-approach
journal_or_venue: arXiv (quant-ph) preprint
methodology_tags:
- variational-nisq
- quantum-ml
- hybrid-quantum-classical
paper_type: ''
quantum_advantage_claim: speculative
related_papers: []
relevance_phase1: high
relevance_phase3: high
source_type: preprint
source_type_confidence: high
step1_date: '2026-04-14T11:13:34.236829'
step1_model: gpt-5-mini
step2_date: '2026-04-14T11:13:34.236829'
step2_model: gpt-5-mini
step3_date: '2026-04-14T11:13:34.236829'
step3_model: gpt-5-mini
step4_date: '2026-04-14T11:13:34.236829'
step4_model: gpt-5-mini
step5_date: '2026-04-14T11:13:34.236829'
step5_model: gpt-5-mini
step6_date: '2026-04-14T11:13:34.236829'
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
- method/variational-nisq
- method/quantum-ml
- method/hybrid-quantum-classical
- idea/quantum-advantage
- idea/near-term-feasibility
- idea/hybrid-approach
- contradiction/scalability
title: A performance characterization of quantum generative models
topic_tags:
- quantum-ml-finance
year: '2024'
zotero_key: ''
---

## Abstract summary
This preprint systematically compares quantum generative model architectures (continuous vs. discrete, including a copula variant) and data transformations (min-max vs. probability integral transform) trained with QCBMs and QGANs. Benchmarks on six synthetic and two real financial datasets show quantum models often require similar or fewer parameters than classical GANs, and a discrete copula architecture trained on PIT-transformed data consistently outperforms other methods.
## Methodology
The authors perform a systematic numerical benchmarking study of quantum generative modeling approaches on low-dimensional (2D and 3D) synthetic and real financial datasets. They compare two families of parametrized quantum-circuit ansatzes — a continuous (expectation-value based) architecture and a discrete (basis-measurement based) architecture — with a further distinction for the discrete ansatz into a standard variant and a copula-structured variant. Two data pre-processing transforms are evaluated: min-max normalization and the probability integral transform (PIT, i.e., mapping marginals to uniform to learn the copula). Two training paradigms are used: Quantum Circuit Born Machines (QCBMs) trained via a gradient-free optimizer (CMA-ES) and Quantum Generative Adversarial Networks (QGANs) where the generator is quantum and the discriminator classical (QGANs trained by gradient descent; parameter-shift rule for discrete circuits, Optax/JAX for the continuous variant). A classical fully-connected GAN is used as baseline; its architecture (input noise dim = 8) and hidden-layer depth/width are varied. Experiments are run with state-vector simulators (Qiskit and PennyLane) and the authors vary model sizes by changing circuit depth (adding parametric blocks) or neural-network hidden-layer sizes; each experiment is repeated five times to obtain mean and standard deviation. Performance is evaluated using the Kullback–Leibler (KL) divergence between histograms of training data and generated samples. The authors report KL values, parameter counts, and visual sample comparisons and explore runtime/resource implications (qubits, gates, shots) for the tested architectures.

**Algorithms used:** Quantum Circuit Born Machine (QCBM), Quantum Generative Adversarial Network (QGAN), Classical Generative Adversarial Network (GAN) baseline, CMA-ES (Covariance Matrix Adaptation Evolution Strategy), Parameter-shift rule (for gradient evaluation on quantum circuits), Gradient descent (Optax/JAX for continuous QGANs)
**Frameworks:** Qiskit (state-vector simulator), PennyLane (state-vector simulator), JAX / Optax, pycma (CMA-ES implementation) - referenced, qugen (authors' open-source simulation library)

**Experimental setup:** All quantum experiments were simulated using classical state-vector simulators (Qiskit and PennyLane). Classical GANs were trained on a GPU-accelerated machine. Quantum circuits were simulated shot-wise for discrete architectures (one shot per sample) and expectation values were computed exactly from the state vector for the continuous architecture. Circuit size was varied by changing the number of parametric blocks; discrete circuits used r qubits per data dimension (precision bits), continuous circuits used one qubit per data dimension. Each experiment was repeated five times. No physical quantum hardware/QPU was used.

**Dataset:** Eight low-dimensional datasets: six synthetic (mixtures of Gaussians (MG), X-shaped distribution (X), O-shaped distributions (O) in 2D/3D, and other synthetic variants) and two real financial datasets derived from Yahoo! Finance (daily returns used as a 'Stocks' dataset). Synthetic 2D sets: 50,000 samples; synthetic 3D sets: 100,000 samples; Stocks sets: 1,877 samples. Preprocessing compared min-max normalization and the probability integral transform (PIT) to map marginals to uniform (copula learning).
## Experiment details
### Input
{'sources': {'synthetic': 'Generated by authors (Mixture of Gaussians, X-shape, O-shape, etc.)', 'financial': 'Yahoo! Finance (daily close prices converted to daily returns)'}, 'sizes': {'2D_synthetic': 50000, '3D_synthetic': 100000, 'stocks_2D_3D': 1877}, 'preprocessing': ['Min-max normalization (scale to [0,1])', 'Probability integral transform (PIT) computed empirically from sample histograms to produce uniform marginals; used for copula learning'], 'discretization': 'For discrete architectures each data dimension was discretized using r qubits per dimension (examples: r=4 in many experiments → 16 bins per dimension → 8 qubits for 2D, 12 for 3D). When necessary, uniform continuous noise was added around discrete grid centers to produce continuous-valued outputs for visualization/analysis.'}

### Process
{'pipeline_steps': ['Preprocess dataset (min-max or PIT).', 'Select model family: classical GAN, continuous quantum generator, discrete-standard quantum generator, or discrete-copula quantum generator.', 'Set circuit/NN size: vary number of parametric blocks (quantum) or vary number/width of hidden layers (classical) to create model size sweep.', 'For QCBM: optimize parameters to minimize discretized KL divergence between model histogram and data histogram using CMA-ES; training often applied blockwise (train small depth, then add blocks initialized to identity/zeros).', 'For QGAN: train generator (quantum) and discriminator (classical) adversarially via gradient descent; for discrete quantum circuits gradients via parameter-shift rule, for continuous generator gradients via JAX/Optax; QGANs were cold-started (no warm-start from lower depth).', 'For discrete quantum models: generate samples by single-shot measurement of computational basis; for continuous quantum models: evaluate expectation values of Pauli-Z on each qubit (in simulation exact expectation values from state vector used) for each noise input z; external noise vector z (dimension 8) fed into continuous architectures (data re-uploading).', 'Repeat training runs 5 times per experimental condition to collect mean and standard deviation.', 'Evaluate performance by computing Kullback–Leibler divergence between data histogram and generated-sample histogram; report minimum KL achieved and parameter counts.'], 'key_hyperparameters_and_controls': ['Classical GAN: input noise dimension = 8; hidden layer counts varied (2 or 4 layers) and hidden widths varied (2 to 64) to sweep parameter count.', 'Discrete quantum: r qubits per dimension (common r=4); number of blocks Nb varied to change parameter count; discrete-standard and discrete-copula circuits have different gate/parameter counts per block.', 'Continuous quantum: one qubit per data dimension; number of blocks Nb varied; noise z re-uploaded between blocks.', 'QCBM optimizer: CMA-ES (gradient-free).', 'QGAN optimizers: gradient descent; parameter-shift rule for discrete circuits; Optax/JAX for continuous circuits.', 'Training repetitions: 5 runs per experiment; large number of total runs (~1200) across configurations.']}

### Output
{'primary_metrics': 'Kullback–Leibler divergence (discretized) between empirical data histogram and generated-sample histogram (CKL).', 'secondary_outputs': 'Minimum KL per configuration, number of variational parameters, visual sample plots, training loss curves over epochs, resource estimates (qubits, gates, circuit depth, shots) and estimated runtime per sample.', 'baselines': 'Classical fully-connected GAN with varied depth/width used as baseline; comparisons across architectures and data pre-processing reported.', 'reporting': 'Tables of minimal KL and parameter counts (Tables I and II), aggregated KL-versus-parameter curves, example sample plots, and training dynamics plots.'}

### Parameters
- qubits: {'continuous': '1 qubit per data dimension (e.g., 2 qubits for 2D, 3 for 3D)', 'discrete': 'n = r * d qubits, where r is precision bits per dimension; common example r=4 → n=8 for 2D, n=12 for 3D', 'example_counts_reported': {'2D_discrete': 8, '3D_discrete': 12, 'continuous_2D': 2, 'continuous_3D': 3, 'max_used_in_study': 12}}
- circuit_depth: Varied by number of parametric blocks Nb; each block adds a fixed number of parametrized gates (continuous block ≈ 8 rotations + 2 CNOTs; discrete standard block ≈ 22 parametric gates; discrete copula block ≈ 36 parametric gates plus one-time initialization). Depths swept to vary total parameter count.
- shots: {'discrete': '1 shot per sample (single measurement = one sample).', 'continuous': 'Many shots required in hardware to estimate expectation values; simulations used exact state-vector expectation values. Authors estimate Ns > 100 shots would be needed on hardware; in simulation expectation values are exact (no shot noise).'}
- optimizers: {'QCBM': 'CMA-ES (pycma)', 'QGAN_continuous': 'Gradient descent via Optax (JAX)', 'QGAN_discrete': 'Gradient descent with parameter-shift gradient estimation', 'classical_GAN': 'Standard gradient-based optimizers (unspecified optimizer family; classical training on GPU)'}
- training_iterations_and_batching: {'repetitions_per_config': 5, 'examples_from_appendix': {'QGAN_discrete_2D': '50 gradient evaluations per epoch (mini-batch ~1000) for most sets; stocks used 18 (mini-batch ~10000).', 'QGAN_discrete_3D': '100 gradient evaluations per epoch (mini-batch ~1000); stocks used 18.', 'QGAN_continuous_2D': '1 gradient evaluation per epoch (mini-batch ~50000) in reported experiments.', 'QGAN_continuous_3D': '100 gradient evaluations per epoch (mini-batch ~1000); stocks used 1 (batch = 1877).', 'QCBM_epochs_examples': 'Examples show up to several hundred to a few thousand epochs depending on architecture (varies by experiment).'}}

### Hardware
{'quantum_simulators': ['Qiskit state-vector simulator', 'PennyLane state-vector simulator'], 'classical_training_hardware': 'GPU-accelerated machine for classical neural-network training', 'quantum_hardware': 'No QPU / physical quantum hardware used (all results from classical simulation)'}

### Reproducibility
The authors state they open-sourced their simulation library 'qugen' for reproducibility. Experiments were run with standard publicly available frameworks (Qiskit, PennyLane, JAX/Optax, pycma). Randomized aspects (training) were repeated five times and seeds/number of repetitions are reported; tables and plots give parameter counts and configurations. (The preprint references the qugen repository but does not include an explicit URL in the provided text.)
## Findings
- [supported] For the tested 2D and 3D synthetic and real (stocks) data sets, quantum generative models required similar or fewer trainable parameters than classical neural-network GANs; in some cases quantum models used up to two orders of magnitude fewer parameters.
- [supported] A discrete 'copula' circuit architecture trained on PIT-transformed data (probability integral transform) consistently outperformed the other quantum architectures (discrete standard and continuous) on most data sets.
- [supported] Both quantum training paradigms studied (QCBM and QGAN with a quantum generator + classical discriminator) can learn the target distributions in simulation; QGANs tended to perform slightly better than QCBMs in the experiments presented.
- [supported] The continuous quantum architecture uses one qubit per data dimension and produces continuous outputs via expectation-value estimation (requires many measurement shots), while discrete architectures use multiple qubits per dimension, sample directly in a discretized grid, and require only one shot per sample.
- [supported] Experiments were run on state-vector simulators (Qiskit and PennyLane) over >1200 runs using low-dimensional (2D/3D) data sets (six synthetic + two real financial data sets) and the KL divergence to compare learned vs. target distributions.
- [supported] The discrete copula circuit enforces uniform marginals by construction (analysis and derivation provided), which matches PIT-preprocessed data and simplifies learning.
- [supported] The authors do not claim practical quantum supremacy: they explicitly state they did not demonstrate quantum circuits surpassing classical GANs in practical tasks, only that some quantum circuits required fewer parameters in these low-dimensional simulated tests.
- [speculative] Resource and runtime scaling estimates indicate that for realistic high-dimensional industrial problems (e.g., d ~ 100) the continuous ansatz would require ~100 qubits and a few hundred gates, while a discrete copula approach with moderate precision (r=16) would require ~1600 qubits and many more gates — these are projections rather than demonstrated hardware results.
- [speculative] The paper suggests that copula learning via quantum circuits may in general simplify learning and reduce instabilities (e.g., fewer mode collapses in GAN training) — an empirical signal in these experiments but a broader generalization remains to be established on larger/harder tasks.
- [supported] The authors open-sourced their simulation library (qugen) and provide reproducible experiments on simulators, facilitating follow-up validation.

**Results summary:** In state-vector simulations on low-dimensional (2D/3D) synthetic and financial data, the authors benchmarked continuous and discrete quantum generative circuit architectures (including a discrete copula variant) trained by QCBM and QGAN procedures and compared them to classical fully-connected GANs. They found that the discrete copula architecture trained on PIT-transformed data gave the best empirical performance across most data sets. Quantum models often achieved equal or better KL divergence with fewer trainable parameters than classical GANs (occasionally by up to ~100x fewer parameters). Continuous circuits used fewer qubits but require many measurement shots to produce continuous outputs, whereas discrete circuits used more qubits but enable one-shot sampling. All results are based on noiseless state-vector simulation; the authors did not demonstrate a provable quantum advantage on hardware or large-scale datasets.

**Performance claims:**
- [supported] Example (3D X dataset): classical GAN (min-max) achieved KL = 0.089 with 9,475 parameters, while a QGAN with discrete copula + PIT achieved KL = 0.029 with 54 parameters.
- [supported] Example (2D X dataset): discrete copula QGAN (PIT) achieved KL = 0.019 with 72 parameters vs classical GAN (min-max) KL = 0.020 with 9,410 parameters.
- [supported] Across the presented tables, discrete copula QGAN/QCBM configurations attained the lowest KL divergences for most data sets (see Tables I & II in the paper for per-dataset minima and parameter counts).
- [supported] The study comprised over 1,200 numerical experiments using state-vector simulation (Qiskit and PennyLane) and reported KL divergence as main performance metric.
- [supported] Maximum circuit sizes used in these experiments were on the order of 12 qubits and up to ~174 gates (authors assert these are comparable to some current NISQ hardware capabilities).
- [speculative] Resource scaling estimate (authors' calculation): for d = 100, continuous architecture ≈ 100 qubits and ≈ 400 gates; discrete copula with r = 16 precision ≈ 1600 qubits and >52,000 gates — these are theoretical extrapolations based on the circuit templates in the paper.
- [supported] Operational/runtime observation: discrete architectures require a single shot per generated sample; continuous architectures require many shots (authors estimate Ns > 100 for reasonable variance) and thus will have larger runtime per sample on hardware.
## Quantum advantage claim
**Classification:** speculative

The paper provides empirical evidence (simulations) that some quantum generative circuits can fit target low-dimensional distributions with far fewer parameters than classical GANs and that a discrete copula design with PIT simplifies learning. However, the authors explicitly do not claim a demonstrated practical quantum advantage: results are from noiseless state-vector simulation on small (2D/3D) problems, no hardware demonstrations of superiority were shown, and scaling/resource estimates for realistic high-dimensional industrial tasks remain projections. Therefore any suggestion of quantum advantage is speculative and not demonstrated.
## Limitations
- Experiments were performed using classical state-vector simulators rather than running on real quantum hardware (author-stated).
- Study restricted to low-dimensional data (2D and 3D); scalability to higher-dimensional, industrial datasets is not demonstrated (author-stated).
- The evaluation focuses on training quality (fit to training distribution) using KL divergence; generalization to unseen data was not assessed (author-stated).
- The impact of decoherence, gate noise and other hardware errors on generative-model performance was not explored (author-stated).
- Continuous architecture results used exact expectation values from state-vector simulation (no shot noise); this understates practical measurement/shot noise costs on hardware (author-stated).
- Finite-sampling (shot) effects, especially for higher-width discrete circuits and for continuous architectures on hardware, were not fully analyzed (author-stated).
- Only a small set of circuit ansatzes, data encodings, cost functions, and hyper-parameters were explored; better performing designs may exist beyond those tested (author-stated).
- QGAN training stability is highly dependent on model/circuit architecture; adversarial training instability remains an unresolved practical limitation (author-stated).
- Discrete architectures require substantially more qubits (and gates) for fine-grained discretization, which is a major constraint in NISQ devices (author-stated).
- Continuous architectures require many measurement shots per sample, implying longer runtime on real quantum hardware (author-stated).
- Resource and runtime estimates indicate extremely large resource requirements (qubits and gates) for industrial-scale, high-dimensional problems (author-stated).
- The choice of circuit architectures was partly arbitrary and hardware-dependent; there is limited exploration of alternative architectures such as tensor-network-inspired ansatzes (author-stated).
- Evaluation used a single primary metric (Kullback–Leibler divergence); other distributional metrics (Wasserstein, Hellinger, etc.) and qualitative assessments were not included (inferred).
- [inferred] The reported parameter-count advantages may be less meaningful if parameter types, circuit expressivity, or optimization difficulty differ substantially between classical and quantum models.
- [inferred] Training time and wall-clock runtimes on actual quantum hardware (including queuing, calibration, and error mitigation overheads) may diminish the practical advantage.
- [inferred] The experiments cold-start or warm-start choices (e.g., for QGANs they did not initialize high-depth circuits from low-depth trained circuits) may impact convergence comparisons and were not exhaustively studied.
## Open questions
- Does the empirical parameter-count advantage of quantum models extend to higher-dimensional, industrially relevant datasets?
- How does realistic hardware noise (decoherence, gate errors, readout errors) affect the performance and relative advantage of the studied quantum generative models?
- How well do the trained quantum generative models generalize to unseen data (i.e., what is their generalization performance vs. overfitting)?
- What are the practical shot/noise/sample-size requirements for the continuous and discrete architectures on hardware to achieve comparable performance to simulations?
- Which circuit ansatzes, data encodings, and cost functions are optimal for different classes of generative tasks (and can better choices materially improve performance)?
- Can discrete copula architectures and PIT preprocessing continue to provide advantages in more complex, higher-dimensional, or real-world distributions?
- How will hybrid training dynamics and adversarial instability behave on noisy hardware, and what stabilization/regularization procedures are effective?
- To what extent can tensor-network-inspired circuits or circuit-cutting techniques enable scaling to larger problems while remaining practical on near-term devices?
- How much do wall-clock runtimes and end-to-end resource costs (shots × circuit depth × qubits) affect the feasibility of deploying these models in industry?
- Would alternative evaluation metrics (e.g., Wasserstein distance) lead to different conclusions about model performance and robustness?
- How effective are quantum variants like quantum Wasserstein GANs for stabilizing training or improving sample quality for continuous/discrete data?

**Future work:**
- Explore the effects of decoherence and realistic hardware noise on generative modeling performance.
- Test and benchmark the simulator-trained models on commercially available quantum hardware to measure the impact of hardware noise and practical constraints.
- Study generalization behavior and the interplay between learning and generalization for higher-dimensional data (beyond 2D/3D).
- Investigate tensor-network-inspired circuit architectures and circuit-cutting techniques to scale the proposed models to larger problems.
- Explore quantum Wasserstein GANs and other alternative training procedures to potentially improve adversarial training stability.
- Analyze the effects of finite sample sizes / number of shots for higher-width quantum circuits, especially for continuous architectures, and characterize shot-noise trade-offs.
- Perform broader searches over data encodings, cost functions, hyper-parameters and alternative ansatzes to identify better-performing configurations.
- Assess how the copula + PIT approach scales with dimension and complexity, and whether its empirical advantage persists for real-world financial and healthcare datasets.
## Key ideas
- #idea:quantum-advantage — A discrete copula-style quantum generator trained on PIT-transformed data consistently outperforms other tested generative models (including a classical GAN baseline) on multiple low-dimensional synthetic and real financial datasets, often using similar or fewer parameters.
- #idea:hybrid-approach — The study evaluates hybrid training paradigms (quantum generator + classical discriminator in QGANs) and classical-quantum combinations (QCBM with classical CMA-ES), highlighting practical hybrid workflows.
- #idea:near-term-feasibility — Effective quantum generative models in this work operate with low qubit counts (examples: r=4 → 8 qubits for 2D, 12 for 3D) and modest circuit depths, suggesting potential NISQ-era applicability for small-dimensional problems.
- #idea:hybrid-approach — Training details (CMA-ES for QCBMs, parameter-shift rule and Optax/JAX for QGANs) and classical preprocessing (min-max vs PIT) materially affect performance; PIT + copula structure is particularly beneficial.
- #limitation:simulation-only — All experiments were run on noiseless state-vector simulators (Qiskit and PennyLane); no physical QPU experiments or shot-noise emulation were performed.
- #limitation:no-empirical-validation — Results are based solely on classical simulation; there is no hardware validation to support claims under real-device noise/shot constraints.
- #limitation:data-encoding — The discrete approach requires discretization (r qubits per dimension) and binning choices; performance depends on these encoding decisions and on PIT preprocessing, which may not scale favorably.
- #limitation:noise — Continuous-generator results use exact expectation values from the state vector (no shot noise), likely yielding optimistic performance compared to real-device implementations.
- #limitation:qubit-count — Experiments are limited to low-dimensional (2D/3D) tasks and small qubit counts; scalability to higher-dimensional financial data is untested.
## Contradictions
- #contradiction:scalability — The paper reports quantum models outperforming classical GANs on low-dimensional datasets and claims NISQ-era relevance, but all evidence comes from noiseless state-vector simulation, exact expectation evaluations, small datasets and small qubit counts. This undermines broader claims about scalability and real-device advantage for practical, higher-dimensional financial problems.
## Notable quotes
<!-- Researcher-added — verbatim quotes with page references -->

## Researcher notes
<!-- Researcher-added — not LLM generated -->
