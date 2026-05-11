# Solution-Space Taxonomy

_Produced during Phase 1 — Framework Synthesis (LLM-assisted, researcher-curated)_
_Date: 2026-04-11 (header reframed 2026-05-02 freeze) | Method: Cruzes & Dybå (2011) within an Arksey & O'Malley (2005) scoping approach_

> **Active partition (post 2026-05-02):** the active solution categories remain SA-01..SA-11 — no SA-level retractions — but for any paper carrying a PD-08 (cryptography) primary problem statement, prefer the disambiguation rule in [`s4_outputs/codebook.md`](../s4_outputs/codebook.md) (PD-08 ↔ SA-09 overlap policy).

## Overview

The solution-space taxonomy comprises **11 categories** derived from LLM-assisted extraction over the Phase 1 exploratory corpus, followed by deductive normalisation against an a-priori code vocabulary (`scripts/build_review_data_done.py::SOLUTION_CODE_MAP`). The original framing as "Elo & Kyngäs inductive content analysis" was **not the executed protocol** — see audit-trail D-5.

Each category represents a family of quantum or quantum-inspired algorithmic approaches applied to financial problems. Categories were formed by grouping LLM-proposed labels under a-priori PD-/SA- codes, with attention to both algorithmic similarity and hardware/paradigm distinctions (annealing vs. gate-based, NISQ vs. fault-tolerant). The SA-02 ∧ SA-04 multi-tag policy is in [`codebook.md`](../s4_outputs/codebook.md).

---

## SA-01: Quantum Annealing and QUBO Formulations

**Definition:** Approaches that solve optimisation problems by encoding them as Quadratic Unconstrained Binary Optimisation (QUBO) or Ising models and solving via quantum annealing hardware (e.g., D-Wave) or adiabatic quantum computing.

**Scope (included):** Quantum annealing, D-Wave implementations, QUBO formulations, Ising model encodings, simulated annealing benchmarks, adiabatic quantum computing.

**Scope (excluded):** Gate-based variational approaches (see SA-02); classical simulated annealing without quantum comparison.

**Papers contributing:** 17

**Constituent codes:**
- `quantum-annealing` — 78 entries across 16 papers
- `d-wave` — 20 entries across 6 papers
- `qubo-formulation` — 54 entries across 12 papers
- `ising-model` — 2 entries across 1 papers
- `simulated-annealing` — 2 entries across 2 papers
- `adiabatic-quantum-computing` — 10 entries across 7 papers

**Contributing papers:**
- 2019_Ors_Quantum_Computing_Finance_Overview
- 2020_AdamBouland_Prospects_Challenges_Quantum_Finance
- 2022_Albareti_Structured_Survey_Quantum_Computing
- 2022_Canabarro_Quantum_Finance_Tutorial_Quantum
- 2022_DylanHerman_Survey_Quantum_Computing_Finance
- 2023_Abbas_Quantum_Optimization_Potential_Challenges
- 2023_Herman_Quantum_Computing_Finance
- 2023_Markna_Unveiling_Advanced_Computational_Applications
- 2024_Abbas_Challenges_Opportunities_Quantum_Optimization
- 2024_OmosholaSOwolabi_Quantum_Computing_Applications_Challenges
- 2024_Sotelo_Quantum_Computing_Finance_Intesa
- 2025_Aggarwal_Comprehensive_Review_Convergence_Quantum
- 2025_Irfan_Quantum_Finance_Unleashed_Transforming
- 2025_Irfan_Quantum_Future_Finance_Applications
- 2025_Uppaluri_Quantum_Computing_Financial_Systems
- 2026_ArnoldCAlguno_Quantum_Computing_Drives_Innovation
- 2026_AtharvaJain_Quantum_Computing_S_Role

---

## SA-02: Variational and NISQ Algorithms

**Definition:** Gate-based quantum algorithms that use parameterised circuits optimised by a classical outer loop. Designed for near-term noisy intermediate-scale quantum (NISQ) devices.

**Scope (included):** QAOA, VQE, variational quantum algorithms, parameterised circuits, NISQ-specific algorithm design.

**Scope (excluded):** Variational QML models (see SA-04); fault-tolerant algorithms (see SA-03, SA-05, SA-06).

**Papers contributing:** 17

**Constituent codes:**
- `qaoa` — 72 entries across 16 papers
- `vqe` — 30 entries across 11 papers
- `variational-algorithm` — 64 entries across 11 papers
- `parameterized-circuits` — 10 entries across 5 papers
- `nisq` — 10 entries across 6 papers

**Contributing papers:**
- 2019_Ors_Quantum_Computing_Finance_Overview
- 2020_AdamBouland_Prospects_Challenges_Quantum_Finance
- 2022_Albareti_Structured_Survey_Quantum_Computing
- 2022_AndrsGmez_Survey_Quantum_Computational_Finance
- 2022_Canabarro_Quantum_Finance_Tutorial_Quantum
- 2022_DylanHerman_Survey_Quantum_Computing_Finance
- 2023_Abbas_Quantum_Optimization_Potential_Challenges
- 2023_Herman_Quantum_Computing_Finance
- 2024_Abbas_Challenges_Opportunities_Quantum_Optimization
- 2024_OmosholaSOwolabi_Quantum_Computing_Applications_Challenges
- 2025_Aggarwal_Comprehensive_Review_Convergence_Quantum
- 2025_Helmy_Unveiling_Quantum_Realm_Comprehensive
- 2025_Irfan_Quantum_Finance_Unleashed_Transforming
- 2025_Irfan_Quantum_Future_Finance_Applications
- 2026_ArnoldCAlguno_Quantum_Computing_Drives_Innovation
- 2026_AtharvaJain_Quantum_Computing_S_Role
- 2026_Sarin_Leveraging_Quantum_Computing_Business

---

## SA-03: Quantum Amplitude Estimation and Monte Carlo Integration

**Definition:** Algorithms based on quantum amplitude estimation (QAE) that provide quadratic speedups for Monte Carlo integration tasks. Core primitive for derivative pricing and risk computation.

**Scope (included):** Quantum amplitude estimation, quantum Monte Carlo integration (QMCI), amplitude amplification, quantum counting, quantum sampling.

**Scope (excluded):** Grover search for database tasks (see SA-05); generic circuit constructions.

**Papers contributing:** 16

**Constituent codes:**
- `quantum-amplitude-estimation` — 48 entries across 12 papers
- `quantum-monte-carlo-integration` — 44 entries across 14 papers
- `amplitude-amplification` — 6 entries across 5 papers
- `quantum-counting` — 0 entries across 0 papers
- `quantum-sampling` — 3 entries across 2 papers

**Contributing papers:**
- 2019_Ors_Quantum_Computing_Finance_Overview
- 2020_AdamBouland_Prospects_Challenges_Quantum_Finance
- 2022_Albareti_Structured_Survey_Quantum_Computing
- 2022_AndrsGmez_Survey_Quantum_Computational_Finance
- 2022_DylanHerman_Survey_Quantum_Computing_Finance
- 2023_Abbas_Quantum_Optimization_Potential_Challenges
- 2023_Herman_Quantum_Computing_Finance
- 2023_Markna_Unveiling_Advanced_Computational_Applications
- 2024_Abbas_Challenges_Opportunities_Quantum_Optimization
- 2025_Aggarwal_Comprehensive_Review_Convergence_Quantum
- 2025_Helmy_Unveiling_Quantum_Realm_Comprehensive
- 2025_Irfan_Quantum_Finance_Unleashed_Transforming
- 2025_Irfan_Quantum_Future_Finance_Applications
- 2025_Uppaluri_Quantum_Computing_Financial_Systems
- 2026_ArnoldCAlguno_Quantum_Computing_Drives_Innovation
- 2026_AtharvaJain_Quantum_Computing_S_Role

---

## SA-04: Quantum Machine Learning

**Definition:** Quantum algorithms for machine learning tasks including classification, regression, generative modelling, and dimensionality reduction. Includes both gate-based and kernel-based approaches.

**Scope (included):** Quantum neural networks (QNN), quantum SVM (QSVM), quantum kernel methods, quantum Boltzmann machines, quantum GANs, quantum autoencoders, quantum transfer learning, quantum reservoir computing, quantum PCA, quantum feature maps, quantum reinforcement learning.

**Scope (excluded):** Classical ML with quantum data encoding only; variational algorithms for optimisation (see SA-02).

**Papers contributing:** 17

**Constituent codes:**
- `quantum-neural-network` — 22 entries across 8 papers
- `quantum-svm` — 16 entries across 6 papers
- `quantum-kernel-methods` — 8 entries across 6 papers
- `quantum-machine-learning` — 32 entries across 14 papers
- `quantum-classification` — 5 entries across 2 papers
- `quantum-reinforcement-learning` — 10 entries across 7 papers
- `quantum-boltzmann-machine` — 7 entries across 4 papers
- `quantum-generative-model` — 13 entries across 5 papers
- `quantum-transfer-learning` — 0 entries across 0 papers
- `quantum-feature-map` — 4 entries across 3 papers
- `quantum-reservoir-computing` — 0 entries across 0 papers
- `quantum-autoencoder` — 0 entries across 0 papers
- `quantum-pca` — 11 entries across 8 papers

**Contributing papers:**
- 2019_Ors_Quantum_Computing_Finance_Overview
- 2020_AdamBouland_Prospects_Challenges_Quantum_Finance
- 2022_Albareti_Structured_Survey_Quantum_Computing
- 2022_AndrsGmez_Survey_Quantum_Computational_Finance
- 2022_DylanHerman_Survey_Quantum_Computing_Finance
- 2023_Abbas_Quantum_Optimization_Potential_Challenges
- 2023_Herman_Quantum_Computing_Finance
- 2023_Markna_Unveiling_Advanced_Computational_Applications
- 2024_Abbas_Challenges_Opportunities_Quantum_Optimization
- 2024_Sotelo_Quantum_Computing_Finance_Intesa
- 2025_Aggarwal_Comprehensive_Review_Convergence_Quantum
- 2025_Irfan_Quantum_Finance_Unleashed_Transforming
- 2025_Irfan_Quantum_Future_Finance_Applications
- 2025_Uppaluri_Quantum_Computing_Financial_Systems
- 2026_ArnoldCAlguno_Quantum_Computing_Drives_Innovation
- 2026_AtharvaJain_Quantum_Computing_S_Role
- 2026_Sarin_Leveraging_Quantum_Computing_Business

---

## SA-05: Grover's Search and Variants

**Definition:** Algorithms based on Grover's search providing quadratic speedup for unstructured search problems. Includes variants and applications to combinatorial search in finance.

**Scope (included):** Grover's algorithm, quantum search, unstructured database search applied to financial problems.

**Scope (excluded):** Amplitude estimation (see SA-03); quantum walk-based search (see SA-07).

**Papers contributing:** 11

**Constituent codes:**
- `grover-search` — 31 entries across 11 papers
- `quantum-search` — 4 entries across 4 papers

**Contributing papers:**
- 2019_Ors_Quantum_Computing_Finance_Overview
- 2020_AdamBouland_Prospects_Challenges_Quantum_Finance
- 2022_AndrsGmez_Survey_Quantum_Computational_Finance
- 2022_DylanHerman_Survey_Quantum_Computing_Finance
- 2023_Abbas_Quantum_Optimization_Potential_Challenges
- 2023_Herman_Quantum_Computing_Finance
- 2024_Abbas_Challenges_Opportunities_Quantum_Optimization
- 2025_Aggarwal_Comprehensive_Review_Convergence_Quantum
- 2025_Irfan_Quantum_Finance_Unleashed_Transforming
- 2026_AtharvaJain_Quantum_Computing_S_Role
- 2026_MohammadAliTagati_Quantum_Computing_Future_Finance

---

## SA-06: Quantum Linear Systems (HHL and Extensions)

**Definition:** Algorithms for solving linear systems of equations on quantum computers, based on the HHL algorithm and its extensions.

**Scope (included):** HHL algorithm, quantum linear systems algorithms, quantum matrix operations, quantum linear algebra.

**Scope (excluded):** Quantum PCA (see SA-04); classical linear algebra acceleration.

**Papers contributing:** 9

**Constituent codes:**
- `hhl-algorithm` — 9 entries across 5 papers
- `quantum-linear-systems` — 15 entries across 5 papers
- `quantum-linear-algebra` — 4 entries across 4 papers

**Contributing papers:**
- 2019_Ors_Quantum_Computing_Finance_Overview
- 2020_AdamBouland_Prospects_Challenges_Quantum_Finance
- 2022_Albareti_Structured_Survey_Quantum_Computing
- 2022_AndrsGmez_Survey_Quantum_Computational_Finance
- 2022_DylanHerman_Survey_Quantum_Computing_Finance
- 2023_Abbas_Quantum_Optimization_Potential_Challenges
- 2023_Herman_Quantum_Computing_Finance
- 2023_Markna_Unveiling_Advanced_Computational_Applications
- 2024_Abbas_Challenges_Opportunities_Quantum_Optimization

---

## SA-07: Quantum Walks

**Definition:** Algorithms based on quantum walks on graphs, with applications to search, sampling, and financial network analysis.

**Scope (included):** Discrete and continuous quantum walks, graph-based quantum algorithms.

**Scope (excluded):** Classical random walks (problem domain, not solution).

**Papers contributing:** 8

**Constituent codes:**
- `quantum-walk` — 9 entries across 8 papers

**Contributing papers:**
- 2020_AdamBouland_Prospects_Challenges_Quantum_Finance
- 2022_AndrsGmez_Survey_Quantum_Computational_Finance
- 2022_DylanHerman_Survey_Quantum_Computing_Finance
- 2023_Herman_Quantum_Computing_Finance
- 2024_Abbas_Challenges_Opportunities_Quantum_Optimization
- 2025_Uppaluri_Quantum_Computing_Financial_Systems
- 2026_ArnoldCAlguno_Quantum_Computing_Drives_Innovation
- 2026_AtharvaJain_Quantum_Computing_S_Role

---

## SA-08: Hybrid Quantum-Classical Approaches

**Definition:** Architectural patterns that integrate quantum subroutines within larger classical computation pipelines. Cross-cuts other solution categories as an integration paradigm.

**Scope (included):** Hybrid QPU-CPU workflows, classical pre/post-processing, quantum-classical feedback loops, divide-and-conquer decomposition.

**Scope (excluded):** Variational algorithms are inherently hybrid but classified under SA-02; this category captures the integration architecture rather than the algorithm.

**Papers contributing:** 13

**Constituent codes:**
- `hybrid-quantum-classical` — 35 entries across 13 papers

**Contributing papers:**
- 2022_Albareti_Structured_Survey_Quantum_Computing
- 2022_DylanHerman_Survey_Quantum_Computing_Finance
- 2023_Abbas_Quantum_Optimization_Potential_Challenges
- 2023_Herman_Quantum_Computing_Finance
- 2023_Markna_Unveiling_Advanced_Computational_Applications
- 2024_OmosholaSOwolabi_Quantum_Computing_Applications_Challenges
- 2025_Aggarwal_Comprehensive_Review_Convergence_Quantum
- 2025_Irfan_Quantum_Finance_Unleashed_Transforming
- 2025_Irfan_Quantum_Future_Finance_Applications
- 2026_ArnoldCAlguno_Quantum_Computing_Drives_Innovation
- 2026_AtharvaJain_Quantum_Computing_S_Role
- 2026_MohammadAliTagati_Quantum_Computing_Future_Finance
- 2026_Sarin_Leveraging_Quantum_Computing_Business

---

## SA-09: Quantum Cryptography and Post-Quantum Security

**Definition:** Quantum-based security solutions and post-quantum cryptographic protocols relevant to financial infrastructure.

**Scope (included):** Quantum key distribution (QKD), post-quantum cryptographic algorithms, Shor's algorithm (as a threat), quantum-safe protocols.

**Scope (excluded):** Cryptographic problems framed as threats to finance (see PD-08); this category covers the solutions/responses.

**Papers contributing:** 9

**Constituent codes:**
- `quantum-key-distribution` — 33 entries across 4 papers
- `post-quantum-cryptography` — 10 entries across 5 papers
- `shor-algorithm` — 14 entries across 8 papers

**Contributing papers:**
- 2022_DylanHerman_Survey_Quantum_Computing_Finance
- 2023_Abbas_Quantum_Optimization_Potential_Challenges
- 2023_Herman_Quantum_Computing_Finance
- 2025_Aggarwal_Comprehensive_Review_Convergence_Quantum
- 2025_Irfan_Quantum_Finance_Unleashed_Transforming
- 2025_Irfan_Quantum_Future_Finance_Applications
- 2026_AtharvaJain_Quantum_Computing_S_Role
- 2026_MohammadAliTagati_Quantum_Computing_Future_Finance
- 2026_Sarin_Leveraging_Quantum_Computing_Business

---

## SA-10: Quantum Fourier Transform and Phase Estimation

**Definition:** Primitive quantum subroutines (QFT, QPE) that underpin many higher-level algorithms. Included as a solution category because several papers discuss their direct application to finance.

**Scope (included):** Quantum Fourier transform, quantum phase estimation, applications to period finding and eigenvalue estimation in finance.

**Scope (excluded):** When used only as a subroutine within HHL (see SA-06) or QAE (see SA-03).

**Papers contributing:** 5

**Constituent codes:**
- `quantum-fourier-transform` — 11 entries across 3 papers
- `quantum-phase-estimation` — 5 entries across 4 papers

**Contributing papers:**
- 2020_AdamBouland_Prospects_Challenges_Quantum_Finance
- 2022_Albareti_Structured_Survey_Quantum_Computing
- 2022_AndrsGmez_Survey_Quantum_Computational_Finance
- 2023_Abbas_Quantum_Optimization_Potential_Challenges
- 2026_AtharvaJain_Quantum_Computing_S_Role

---

## SA-11: Error Mitigation and Fault Tolerance

**Definition:** Techniques for managing noise and errors in quantum computations, including error mitigation for NISQ and full error correction for fault-tolerant systems.

**Scope (included):** Error mitigation techniques, fault-tolerant quantum computing, quantum error correction, noise-aware algorithm design.

**Scope (excluded):** Hardware-level discussions without algorithmic implication.

**Papers contributing:** 6

**Constituent codes:**
- `error-mitigation` — 15 entries across 5 papers
- `fault-tolerant` — 8 entries across 5 papers

**Contributing papers:**
- 2020_AdamBouland_Prospects_Challenges_Quantum_Finance
- 2022_Albareti_Structured_Survey_Quantum_Computing
- 2023_Abbas_Quantum_Optimization_Potential_Challenges
- 2024_Abbas_Challenges_Opportunities_Quantum_Optimization
- 2026_AtharvaJain_Quantum_Computing_S_Role
- 2026_Sarin_Leveraging_Quantum_Computing_Business

---
