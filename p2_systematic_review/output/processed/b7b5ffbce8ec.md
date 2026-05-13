---
aliases:
- Quantum Variational Autoencoder
- Quantum Variational Autoencoder
authors:
- Amir Khoshaman
- Walter Vinci
- Brandon Denis
- Evgeny Andriyash
- Hossein Sadeghi
- Mohammad H. Amin
auto_detected: true
classification: ''
contradiction_flags:
- contradiction:classical-vs-quantum
doi: ''
evaluation_type: simulator
evidence_type: ''
has_quantitative_results: true
idea_tags:
- idea:quantum-advantage
- idea:near-term-feasibility
- idea:hybrid-approach
journal_or_venue: arXiv (arXiv:1802.05779)
methodology_tags:
- quantum-ml
- hybrid-quantum-classical
paper_type: ''
quantum_advantage_claim: speculative
related_papers: []
relevance_phase1: medium
relevance_phase3: high
source_type: preprint
source_type_confidence: high
step1_date: '2026-04-14T11:35:18.850532'
step1_model: gpt-5-mini
step2_date: '2026-04-14T11:35:18.850532'
step2_model: gpt-5-mini
step3_date: '2026-04-14T11:35:18.850532'
step3_model: gpt-5-mini
step4_date: '2026-04-14T11:35:18.850532'
step4_model: gpt-5-mini
step5_date: '2026-04-14T11:35:18.850532'
step5_model: gpt-5-mini
step6_date: '2026-04-14T11:35:18.850532'
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
- topic/simulation-monte-carlo
- method/quantum-ml
- method/hybrid-quantum-classical
- idea/quantum-advantage
- idea/near-term-feasibility
- idea/hybrid-approach
- contradiction/classical-vs-quantum
title: Quantum Variational Autoencoder
topic_tags:
- quantum-ml-finance
- simulation-monte-carlo
year: '2019'
zotero_key: ''
---

## Abstract summary
The paper introduces the Quantum Variational Autoencoder (QVAE), a VAE whose latent generative process is implemented by a quantum Boltzmann machine (QBM). It derives a tractable quantum lower bound (Q-ELBO) for end-to-end training, uses quantum Monte Carlo to train and evaluate QVAEs on MNIST, and demonstrates competitive performance with discrete VAEs while highlighting opportunities for sampling acceleration via quantum annealers.
## Methodology
The authors introduce a Quantum Variational Autoencoder (QVAE) in which the latent prior p_theta(z) is implemented as a quantum Boltzmann machine (QBM). They derive a tractable training objective by replacing the intractable ELBO terms involving the QBM with a Golden–Thompson-based lower bound (Q-ELBO). For discrete latent variables they use a DVAE construction: introduce continuous auxiliary variables ζ with a smoothing distribution r(ζ|z) (spike-and-exponential) so that the reparameterization trick can be applied. They support hierarchical approximating posteriors q_phi(z|x) to increase expressivity. For classical RBM priors (DVAE baseline) they train using persistent contrastive divergence (PCD) to estimate the negative phase; for QBM priors they estimate gradients of the Q-ELBO using sampling from the quantum distribution implemented via continuous-time quantum Monte Carlo (CT-QMC) combined with population annealing (PA). Training uses neural network encoder/decoder parameterizations (sigmoidal Bernoulli outputs, ReLU hidden layers). Evaluation metrics include ELBO, Q-ELBO and log-likelihood estimated via importance weighting, and they compare to other discrete-latent methods on MNIST. Hyperparameters and practical training details (optimizer, learning rates, batch size, annealing schedules, RBM/QBM sizes, number of sampling chains/sweeps) are reported and chosen to accommodate the computational cost of CT-QMC.

**Algorithms used:** Variational Autoencoder (VAE), Discrete VAE (DVAE), Quantum Variational Autoencoder (QVAE), Restricted Boltzmann Machine (RBM), Quantum Boltzmann Machine (QBM), Reparameterization trick, Spike-and-exponential smoothing (for discrete reparameterization), Hierarchical variational posterior, Persistent Contrastive Divergence (PCD), Continuous-time Quantum Monte Carlo (CT-QMC), Population Annealing (PA), Importance weighting (multi-sample ELBO), ADAM optimizer

**Experimental setup:** All experiments are simulations. Classical DVAE models use RBMs trained with PCD (1000 persistent chains, 200 block-Gibbs updates per gradient evaluation). QVAE models use CT-QMC sampling with population annealing to approximate quantum distributions and gradient negative phases. Population size for PA was 1000 and 5 sweeps per gradient evaluation for QVAE CT-QMC. Evaluation of log partition functions was done with population annealing. Models were trained on binarized MNIST (static binarization). No quantum hardware was used.
## Experiment details
### Input
{'dataset': 'MNIST (static binarization)', 'source': 'LeCun MNIST', 'train_test_split': 'standard MNIST splits (training and test sets used; validation used for reported metrics)', 'preprocessing': 'static binarization of images', 'details': {'input_representation': 'binary 28x28 images', 'latent_space': 'discrete binary vectors z in {0,1}^L', 'latent_sizes_tested': [32, 64, 128, 256, 16, 32, 64]}}

### Process
{'pipeline_steps': ['Define DVAE/QVAE architecture: encoder q_phi(z|x) (hierarchical Bernoulli outputs), smoothing r(ζ|z), decoder p_theta(x|ζ).', 'For DVAE: use RBM prior p_theta(z) (classical) and train by maximizing ELBO. Positive phase computed via reparameterized encoder samples; negative phase estimated using PCD.', 'For QVAE: replace RBM with QBM (transverse field Γ fixed hyperparameter). Use Golden–Thompson to obtain Q-ELBO lower bound and compute gradients; positive phase via reparameterized samples, negative phase via CT-QMC + population annealing sampling from QBM.', 'Training details: encoder networks with two ReLU hidden layers (2000 units each) for q_phi; decoder as sigmoidal outputs of a ReLU network (1 layer, 250–2000 units depending on model to avoid overfitting).', 'Optimization: ADAM with learning rate 1e-3 (default ADAM params), batch size 200.', 'Auxiliary schedules: β (spike-and-exponential parameter) annealed linearly from 1.0 to 10 over 2000 epochs; learning rate annealed exponentially.', 'Evaluate: ELBO and log-likelihood (LL) estimated via importance weighting (multi-sample ELBO with 30000 latent samples per test example). Partition functions computed via population annealing.'], 'training_iterations': {'DVAE': {'RBM256x256': 'trained up to unspecified epochs; reported LL -83.5 ± 0.2', 'hierarchies': 8}, 'QVAE': {'RBM16x16': '800 epochs', 'RBM32x32': '250 epochs', 'RBM64x64': '50 epochs'}}, 'sampling_parameters': {'PCD': {'chains': 1000, 'gibbs_updates_per_gradient': 200}, 'CT-QMC+PA': {'population': 1000, 'sweeps_per_gradient': 5, 'annealing_schedule': 'linear in parameter space theta_t = t * theta'}}}

### Output
{'metrics_reported': ['Evidence Lower Bound (ELBO)', 'Quantum ELBO (Q-ELBO)', 'Importance-weighted Log-Likelihood (LL)', 'Generated and reconstructed images (qualitative)'], 'baselines_compared': ['VIMCO', 'NVIL', 'CONCRETE (Gumbel-Softmax)', 'GS (Gumbel-Softmax)', 'RWS (Reweighted Wake-Sleep)', 'REBAR'], 'format': 'Numeric ELBO and LL values on validation set with uncertainty estimates; visual samples of generated/reconstructed MNIST digits', 'example_results': {'DVAE_RBM256x256_LL': -83.5, 'QVAE_QELBO_vs_Gamma': 'Q-ELBO worsens as transverse field Γ increases; ELBO (true) remains closer to classical case for Γ up to 2'}}

### Parameters
- optimizer: ADAM
- learning_rate: 0.001
- batch_size: 200
- encoder_hidden_units: 2000
- decoder_hidden_units_range: [250, 2000]
- hierarchical_levels: 8
- spike_and_exponential_beta_schedule: {'start': 1.0, 'end': 10.0, 'epochs': 2000, 'type': 'linear'}
- PCD: {'persistent_chains': 1000, 'gibbs_updates_per_gradient': 200}
- CT_QMC_population_annealing: {'population_size': 1000, 'sweeps_per_gradient': 5, 'annealing_schedule': 'linear in parameter space'}
- importance_weighting_samples_for_LL: 30000
- latent_layer_sizes_used: [16, 32, 64, 128, 256]
- transverse_field_Gamma_values_tested: [0, 1, 2]

### Hardware
{'simulator': 'Continuous-time Quantum Monte Carlo (CT-QMC) implementation with Population Annealing', 'quantum_hardware': None, 'cloud_provider': None, 'compute_resources': 'Not specified; authors note CT-QMC + PA is computationally expensive which limited QBM sizes and training epochs'}

### Reproducibility
The preprint does not provide a link to code or exact implementation scripts. Key hyperparameters, model architectures (encoder/decoder unit counts), sampling configurations (PCD chains, Gibbs updates, PA population and sweeps), and training schedules are reported in the text, but implementation-level details (random seeds, full training duration per model, exact network layer sizes for each experiment, and source code) are not made available in the manuscript. Partition function and sampling procedures rely on population annealing CT-QMC, which the authors note is computationally expensive; reproducing results requires implementing CT-QMC + PA or equivalent samplers.
## Findings
- [supported] Introduced the Quantum Variational Autoencoder (QVAE): a VAE whose latent generative model is a quantum Boltzmann machine (QBM), and described how to train it end-to-end via a tractable "quantum" lower bound (Q-ELBO).
- [supported] Demonstrated practical training and evaluation of QVAE models using continuous-time quantum Monte Carlo (CT-QMC) simulations (implemented via population annealing CT-QMC) for sampling from QBMs in the latent space.
- [supported] Developed and validated a discrete VAE (DVAE) platform with RBMs in the latent space, which achieves state-of-the-art performance among variational models that use only discrete latent variables on the MNIST dataset.
- [supported] Reported empirical performance numbers for DVAE with RBMs (e.g., RBM256x256 achieving estimated log-likelihood -83.5 ± 0.2 on MNIST validation), showing competitive results compared to other discrete-latent methods.
- [supported] Showed that the Q-ELBO (the tractable bound used for training QBMs) becomes looser as the transverse field Γ increases; nevertheless, QVAEs can be trained and produce reasonable generative samples even for nonzero Γ (they report experiments up to Γ = 2).
- [supported] Noted that using the Q-ELBO prevents optimizing the transverse-field parameters Γ during training (Γ must be treated as a fixed hyperparameter when using the Q-ELBO).
- [speculative] Argued that quantum annealers could be used as sampling devices to scale QVAEs to larger latent spaces, potentially leveraging quantum tunnelling to accelerate mixing between modes and thus provide a computational advantage over classical MCMC.
- [speculative] Suggested that QVAEs open a practical path to applying current and future quantum annealers to train generative models with large QBMs in latent spaces for machine learning tasks.
- [supported] Clarified that QVAEs differ from previously proposed quantum autoencoders (QAEs): QVAEs have a classical autoencoding structure with a quantum generative process, whereas QAEs implement quantum autoencoding circuits and do not provide a classical generative model.
- [speculative] Raised an open question for future work about whether tighter bounds than the Q-ELBO can be derived so that QBMs could be trained more directly (potentially improving performance when Γ is large).

**Results summary:** This preprint defines the QVAE, a variational autoencoder using a quantum Boltzmann machine as the prior in the latent space, derives a tractable training objective (Q-ELBO) based on the Golden–Thompson inequality, and validates the approach experimentally. Using CT-QMC (population-annealed) sampling, the authors trained QVAEs (limited to modest latent sizes due to sampling cost) and demonstrated that (i) a classical DVAE with RBM latent priors attains state-of-the-art results among discrete-latent variational models on MNIST, and (ii) QVAEs can be trained via the Q-ELBO and yield reasonable generated samples even when quantum effects (transverse field Γ) are present, though the Q-ELBO bound degrades as Γ increases. The paper argues that quantum annealers could potentially accelerate sampling for larger QBMs, but does not demonstrate a practical quantum speedup.

**Performance claims:**
- [supported] DVAE with RBM256×256: estimated log-likelihood (LL) on MNIST validation -83.5 ± 0.2 (ELBO -89.2).
- [supported] DVAE with RBM128×128: ELBO -90.4, LL -84.7.
- [supported] DVAE with RBM64×64: ELBO -92.4, LL -85.5.
- [supported] DVAE with RBM32×32: ELBO -99.3 ± 0.2, LL -90.8 ± 0.2.
- [supported] QVAE ELBO / Q-ELBO examples (validation): QBM16×16 with Γ=0: ELBO and Q-ELBO -109.3; with Γ=1: ELBO -110.5, Q-ELBO -120.6; with Γ=2: ELBO -115.3, Q-ELBO -135.8.
- [supported] QVAE ELBO / Q-ELBO examples (validation): QBM32×32 with Γ=0: ELBO and Q-ELBO -101.8; with Γ=1: ELBO -103.6, Q-ELBO -117.9; with Γ=2: ELBO -112.1, Q-ELBO -139.7.
- [supported] QVAE ELBO / Q-ELBO examples (validation): QBM64×64 with Γ=0: ELBO and Q-ELBO -105.7; with Γ=1: ELBO -108.7, Q-ELBO -133.9; with Γ=2: ELBO -120.0, Q-ELBO -165.2.
## Quantum advantage claim
**Classification:** speculative

The authors propose that quantum annealers could speed sampling from QBMs (and thereby training of QVAEs) by exploiting quantum tunnelling to mix between modes more efficiently than classical MCMC. However, no empirical quantum-device speedup or advantage is demonstrated in the paper: all QVAE training/evaluation is performed via classical CT-QMC simulations, and claims about potential advantages of real quantum hardware remain theoretical/speculative and are presented as future research directions.
## Limitations
- Training and evaluation via quantum Monte Carlo (CT-QMC) is computationally expensive, which constrained experiments to QBMs with relatively small latent spaces (up to 64×64) and limited number of training epochs.
- The quantum variational bound (Q-ELBO) used for training is a looser lower bound than the true ELBO because of the Golden–Thompson inequality approximation, and the bound becomes looser as the transverse field Γ increases, degrading training effectiveness.
- Use of the Q-ELBO precludes treating the transverse field parameters (Γ) as trainable; Γ must be held fixed as a hyperparameter during training.
- Gradients of the exact quantum cross-entropy (involving Tr[Λz e^{-Hθ}]) are intractable, necessitating the looser bound and approximation strategies.
- Accurate estimation of partition functions and quantum probabilities (required for log-likelihood evaluation and importance sampling) is costly; importance-weighted LL estimation for QVAEs was not reported due to computational expense.
- Persistent, well-separated modes in trained RBMs/QBMs make MCMC mixing slow; classical MCMC methods (and PA-CT-QMC) struggle to sample efficiently from such multimodal distributions.
- Scaling QVAE training to large latent dimensions with CT-QMC is impractical; samples from large QBMs would require alternative hardware (quantum annealers) or much more compute.
- Practical use of quantum annealers as samplers will likely require tailored implementations to mitigate device limitations (control errors, limited coupling range and connectivity).
- [inferred] The experiments and demonstrated performance are limited to relatively small models and MNIST; generalization to larger, real-world financial datasets or more complex generative tasks is untested.
- [inferred] The paper does not demonstrate end-to-end advantage of quantum latent models over classical models when accounting for the cost of quantum sampling or QMC, so practical benefit remains unproven.
- [inferred] Training time, wall-clock resources, and computational cost trade-offs (classical vs quantum-assisted training) are not quantified, limiting assessment of practicality.
## Open questions
- Is it possible to improve the performance of QVAE by using bounds to the log-likelihood that are tighter than the Q-ELBO used in this work?
- Can quantum annealers provide a computational advantage in sampling (mixing between modes) over classical MCMC / QMC methods for training (Q)VAEs, especially for multimodal latent distributions?
- How can one mitigate physical limitations of actual quantum annealing devices (control errors, limited coupling range and connectivity) in order to deploy QBMs in practical machine-learning pipelines?
- Can QBMs trained by directly maximizing the true log-likelihood (rather than the Q-ELBO) yield better generative performance than classical RBMs in regimes where quantum effects are relevant?
- What are effective methods to scale QVAE training to large latent spaces and large datasets (beyond MNIST) using either improved classical sampling or quantum hardware?
- How to obtain tractable, low-variance, and unbiased gradient estimates for quantum models that avoid the need for the Golden–Thompson inequality approximation?
- [inferred] Under what realistic hardware and noise conditions would quantum sampling provide a net computational or model-quality advantage for generative modeling in applied domains (e.g., finance)?
- [inferred] How does the extra approximation (Q-ELBO) interact with model expressivity and encoder design when attempting to leverage quantum latent priors?

**Future work:**
- Explore and develop bounds to the log-likelihood tighter than the Q-ELBO to improve QVAE training.
- Use quantum annealers to sample from large QBMs in the latent space of QVAEs to enable scaling to larger latent dimensions and datasets.
- Design tailored implementations and device-level mitigations to handle quantum annealer limitations (control errors, limited coupling range and connectivity) for effective sampling.
- Investigate training QBMs via direct maximization of the true log-likelihood (instead of the Q-ELBO) to potentially exploit quantum advantages.
- Study whether and when quantum annealers can accelerate mixing between different modes compared to classical QMC, and quantify any resulting computational advantage.
- Extend experiments to larger models and more complex datasets (scaling beyond MNIST) to evaluate practical applicability.
- Develop and test improved sampling and inference techniques (classical or quantum-assisted) that reduce the computational cost of estimating partition functions and quantum probabilities.
## Key ideas
- #idea:hybrid-approach — QVAE integrates a quantum Boltzmann machine (QBM) latent prior with classical encoder/decoder neural networks and trains end-to-end using a Golden–Thompson-based Q-ELBO.
- #idea:quantum-advantage — The paper argues that sampling acceleration via quantum annealers could benefit training/evaluation of QBM priors, offering a potential quantum advantage in sampling.
- #idea:near-term-feasibility — Using CT-QMC + population annealing to simulate QBM priors, QVAE attains competitive ELBO/LL on binarized MNIST versus discrete VAE baselines, suggesting the approach is worth exploring in near-term hybrid contexts.
- #limitation:simulation-only — All experiments were performed via continuous-time quantum Monte Carlo simulations with population annealing; no experiments on physical quantum hardware were presented.
- #limitation:no-empirical-validation — Claims about practical benefits from quantum hardware (e.g., annealers) are not validated experimentally on QPUs.
- #idea:quantum-advantage — Empirical results show Q-ELBO degrades as the transverse field Gamma increases and classical DVAE baselines remain competitive (e.g., DVAE RBM256x256 LL = -83.5), tempering claims of clear quantum superiority.
## Contradictions
- Authors highlight potential sampling speedups from quantum annealers, yet simulated experiments (CT-QMC+PA) show QVAE only matches classical DVAE performance and Q-ELBO worsens with increasing transverse field Gamma, which undermines strong claims of quantum superiority on the tested tasks.
## Notable quotes
<!-- Researcher-added — verbatim quotes with page references -->

## Researcher notes
<!-- Researcher-added — not LLM generated -->
