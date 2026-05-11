<!-- chapter-supporting-literature reading note
     paper_id:        3f4c5ad6749d
     selection_id:    C-04
     source_text:     shared/extracted_text/text/3f4c5ad6749d_quantum_unary_approach_to_option_pricing.md
     generated_at:    2026-05-03T10:00:42.250787+00:00
     model:           gpt-5-mini
     temperature:     0.2
     prompt_version:  1.0 (2026-05-03)
     prompt_sha:      72a0945464a5
     rendered_sha:    7cb5aafbb874
     status:          PENDING researcher review
     accept by:       moving this file to ../<paper_id>__<slug>.md -->

> ⛔ **EXCLUSION FLAG (researcher discretion, 2026-05-03)**: This note is **TOO DETAILED** for the Background chapter scope. Most content (partial-SWAP / partial-iSWAP gate matrices, controlled-RY rotations, amplitude-estimation circuit construction, KL-divergence noise simulations) is below the level of abstraction the chapter operates at.
>
> **Action**: Do NOT use this note as a source for Chapter 1 or Chapter 2 prose. Only the high-level claims remain in scope: "quantum algorithm for European option pricing using a unary encoding of the asset value"; "quadratic speedup of Amplitude Estimation over classical Monte Carlo"; the unary-vs-binary trade-off framed in plain words (linear qubit cost in exchange for shallower circuits and native error mitigation); and the NISQ-feasibility takeaway.
>
> **Retain** the full extraction for possible reuse in Ch.4 / Ch.7.

# Quantum unary approach to option pricing (2021)

**Authors**: Sergi Ramos-Calderer, Adrián Pérez-Salinas, Diego García-Martín, Carlos Bravo-Prieto, Jorge Cortada, Jordi Planagumà, José I. Latorre  
**Venue**: Quantum Science and Technology 6 (2021) 045007 (preprint: arXiv:1912.01618v4)  
**DOI**: n/a  
**Suggested chapter sections**: §1.2 Motivation & contributions, §2.1 Black–Scholes primer, §2.2 Quantum Amplitude Estimation, §2.4 Quantum data encoding (unary vs binary), §2.5 NISQ-era error mitigation

## 1-paragraph summary
This paper proposes a quantum algorithm to price European options by encoding the asset value in a unary basis. The method separates into (1) an amplitude-distributor circuit (low depth, nearest-neighbor partial-SWAPs) that loads the Black–Scholes log-normal distribution into unary amplitudes; (2) a simple payoff encoder using controlled rotations to a single ancilla; and (3) Amplitude Estimation to extract the expected payoff. The unary encoding trades worse asymptotic qubit scaling (linear vs logarithmic) for much simpler circuits, native post-selection error mitigation, and better robustness in NISQ-noise simulations; comparison with a binary/qGAN-based approach is provided via gate counts and noisy simulations.

## Key concepts (with location)
- **Unary representation** — "III. A. Unary representation" — "That means that for every element of the basis only one qubit will be in the |1⟩state, whereas all others will remain in |0⟩."
- **Amplitude distributor (unary)** — "III. B. Amplitude distributor" — "The quantum circuit generating the final register operates as a distributor of probability amplitudes."
- **Partial-SWAP / partial-iSWAP gates** — "III. B. Amplitude distributor" — "The partial-SWAP gate is deﬁned as = (matrix ... )" (matrix shown in paper) and "This partial-iSWAP gate, ... is a universal entangling gate that comes naturally from the capacitive coupling of superconducting qubits [47, 48]."
- **Payoff encoding (ancilla via cRy)** — "III. B. Payoﬀcalculator" — "To be explicit, the computation of the payoﬀcan be achieved by applying controlled Y rotations (cRy gates), whose control qubits are those encoding a price higher than the accorded strike K, namely the operator R."
- **Amplitude Estimation (AE)** — "II. B. Amplitude Estimation" — "Amplitude Estimation (AE) is a quantum technique that allows to estimate the probability of obtaining a certain outcome from a quantum state (with a given precision), with up to a quadratic speedup in the number of function calls as compared to direct sampling [36, 45]."
- **Unary post-selection/error-mitigation** — "III. C. Error mitigation" — "The key idea behind the possibility of accomplishing error mitigation is that unary algorithms should ideally work within the unary subspace of the Hilbert space. As a consequence, the read-out of any measurement should reﬂect this fact. It is then possible to reject any outcome that does not fulﬁl this requirement."
- **Black–Scholes model / log-normal distribution** — "II. A. Black-Scholes model" — "ST = S0e(r−σ2 2 )T eσWT ∼e N ((r−σ2 2 )T,σ √T ), which corresponds to a log-normal distribution." (equation and sentence appear together)

## Quotable claims (with location)
- Abstract — "We present a quantum algorithm for European option pricing in ﬁnance, where the key idea is to work in the unary representation of the asset value." — *useful for: §1.2 Motivation & contributions*
- Abstract — "The algorithm needs novel circuitry and is divided in three parts: ﬁrst, the amplitude distribution corresponding to the asset value at maturity is generated using a low depth circuit; second, the computation of the expected return is computed with simple controlled gates; and third, standard Amplitude Estimation is used to gain quantum advantage." — *useful for: §2.4 Quantum algorithm overview*
- Abstract — "On the positive side, unary representation remarkably simpliﬁes the structure and depth of the quantum circuit." — *useful for: §2.4 Unary encoding advantages*
- Abstract — "Amplitude distributions uses quantum superposition to bypass the role of classical Monte Carlo simulation." — *useful for: §2.2 Quantum advantage rationale*
- Abstract — "The unary representation also provides a post-selection consistency check that allows for a substantial mitigation in the error of the computation." — *useful for: §2.5 Error mitigation in NISQ*
- Abstract — "On the negative side, unary representation requires linearly many qubits to represent a target probability distribution, as compared to the logarithmic scaling of binary algorithms." — *useful for: §2.4 Limitations & trade-offs*
- Introduction — "It has been shown that quantum computers can provide a quadratic speedup in the number of quantum circuit runs as compared to the number of classical Monte Carlo runs needed to reach a certain precision in the estimation." — *useful for: §1.1 Quantum speedups for Monte Carlo*
- III.B (Amplitude distributor) — "To be precise, given n qubits, the circuit will always be of depth ⌊n/2⌋+ 1." — *useful for: §2.4 Circuit depth comparison*
- III.B (Payoﬀcalculator) — "Applying the payoﬀcalculator to a quantum state representing the probability distribution, as depicted in Fig. 2, results in ... The state is now in the form of Eq. (15). It is straight-forward to see that the probability of measuring |1⟩in the ancillary qubit is P(|1⟩) = ΣSi>K pi (Si −K)/(Smax −K)." — *useful for: §2.4 Encoding payoff into amplitude (mechanics)*
- III.B (AE implementation) — "Sψ0 = (I⊗n ⊗(XZX))." — *useful for: §2.2 Practical AE implementation in unary*
- III.B (AE implementation) — "S0 can be constructed out of 2 single-qubit gates and one entangling gate." — *useful for: §2.4 Unary simplifications*
- III.C (Error mitigation) — "It is then possible to reject any outcome that does not fulﬁl this requirement. As a matter of fact, a number of failed repetitions of the experiment could be discarded, what results in a trade-oﬀbetween reduction of errors and loss of accepted samples." — *useful for: §2.5 Post-selection trade-offs*
- IV.B (Gate count) — "The unary algorithm needs O(n) partial-SWAP gates in order to distribute the amplitude and O(κn) controlled-Ry gates to encode the payoﬀin an ancillary qubit, where 0 ≤κ ≤1 depends on the strike price K." — *useful for: §2.4 Resource scaling discussion*
- V.A (Simulation model) — "The simulations in this work were carried out using a simple yet descriptive model. In the case of single-qubit and two-qubit gate errors, we consider depolarizing noise." — *useful for: §2.5 Simulation assumptions & noise model*
- V.A (KL divergence result) — "For the maximum allowed error, the KL divergence of the binary algorithm is one order of magnitude larger than that of the unary one." — *useful for: §2.5 Empirical robustness*
- VI (Conclusions) — "Unary representation deﬁnitely oﬀers relevant advantages over the binary one. First, it allows for a simple distribution of probability amplitudes. Second, it provides a trivial computation of expected returns. Third, unary representation should only trigger one output qubit, while reading the expected return in the ancilla. This oﬀers a consistency check. If no output, or more than one are triggered, the run is rejected." — *useful for: §1.2 Takeaway messages*

## Limitations stated by authors
- Unary qubit-scaling trade-off — "On the negative side, unary representation requires linearly many qubits to represent a target probability distribution, as compared to the logarithmic scaling of binary algorithms." — Abstract
- AE resource demands (QPE) — "The original Amplitude Estimation procedure requires the implementation of QPE, which is highly resource demanding. Hence, the complexity of the circuit precludes its feasibility in the NISQ era." — "II. B. Amplitude Estimation"
- Asymptotic scaling remark — "This results in a worse asymptotic scaling for the unary algorithm." — "I. INTRODUCTION"
- Gate-count / connectivity assumptions caveat — "Existing quantum devices need to implement extra SWAP gates to account for insuﬃcient connections, which are not taken into account in this calculations. Therefore, the gate counting on a computer with less than this ideal connectivity will result in a worse scaling." — "IV. B. Gate count"
- Simulation model simplifications — "Let us remark here that we have not included thermal relaxation or thermal dephasing. The reason is that, given the shallow depth of the simulated circuits, the execution times are far below current coherence times of qubits (the latter being ∼1000 times the duration of a single-qubit gate), and thermal errors are therefore negligible." — "V. SIMULATIONS"

## How this paper might be used in the chapter
- §1 (Introduction): Use the abstract and concluding quotes to state the paper’s primary contribution and the unary-vs-binary trade-off as a motivating example of NISQ-oriented algorithm design.
- §2.1 (Black–Scholes background): Cite the paper’s Black–Scholes setup and the use of log-normal ST distribution when introducing the financial model for option payoff expectations.
- §2.2 (Quantum Monte Carlo & AE): Use the Amplitude Estimation discussion to explain expected quadratic speedups and practical constraints (QPE vs iterative AE).
- §2.4 (Data encoding & circuit resources): Use the gate-count and depth claims (partial-SWAP distributor depth ⌊n/2⌋+1; O(n) gate counts) to illustrate engineering trade-offs between unary and binary encodings.
- §2.5 (NISQ error mitigation): Use the paper’s native post-selection strategy as an example of algorithm-level error mitigation and as empirical evidence (simulations) that encoding design affects noise robustness.
- Consider citing alongside other quantum option-pricing proposals (e.g., qGAN + binary AE approaches) when discussing alternative loading strategies and practical implementations.

## Researcher to verify
- [x] Confirm the exact arXiv version and year to cite (arXiv:1912.01618v4 16 Mar 2021) and whether a journal version exists. — RESOLVED: cite the journal version (Quantum Sci. Technol. 6 (2021) 045007); arXiv kept as preprint pointer in Venue line.
- [x] Verify the literal matrix forms and Eq. (13)/(14) in the PDF (partial-SWAP/partial-iSWAP) for any transcription artefacts before quoting formulas in the thesis. — RESOLVED-VIA-EXCLUSION: gate matrices are below the chapter's level of abstraction (see EXCLUSION FLAG above). Will not be quoted.
- [x] Check the assumptions behind Table I gate counts (connectivity model, κ choices, qGAN layer count l) against the Appendix and code to ensure counts align with the narrative in Chapter 2. — RESOLVED-VIA-EXCLUSION: gate-count details are below the chapter's level of abstraction. Will not be quoted.
- [x] Reproduce or re-run the authors’ simulation code (GitHub link in paper) to confirm KL-divergence / robustness results and the noise model parameters (depolarizing error levels, measurement error multiplier = 10ϵ). — RESOLVED-VIA-EXCLUSION: simulation reproducibility is below the chapter's level of abstraction. Mention the unary-encoding robustness story in plain words only.
- [x] Confirm the precise formula used for payoff rotation angles (Eq. (16)) in the PDF to ensure correct presentation (square-root / normalization details). — RESOLVED-VIA-EXCLUSION: payoff-rotation formula is below the chapter's level of abstraction. Will not be quoted.
