<!-- chapter-supporting-literature reading note
     paper_id:        d0568e395fbf
     selection_id:    C-10
     source_text:     shared/extracted_text/text/d0568e395fbf_11_a_review_of_different_techniques_and_challenges_of_quantum_computing_in_vario.md
     generated_at:    2026-05-03T10:02:24.036965+00:00
     model:           gpt-5-mini
     temperature:     0.2
     prompt_version:  1.0 (2026-05-03)
     prompt_sha:      72a0945464a5
     rendered_sha:    5d4df280350a
     status:          PENDING researcher review
     accept by:       moving this file to ../<paper_id>__<slug>.md -->

> ✅ **REVIEW NOTE (researcher discretion, 2026-05-03)**: This note is **at an appropriate level of detail** for the Background chapter. Use the survey-style claims about NISQ limits, decoherence as engineering challenge, and the broad QC technique taxonomy.
>
> **Skip / do not quote**: the QNN "immune to noise and decoherence" claim (factually wrong; flagged in REVIEW_QUEUE Tier-C). LLM-assigned page numbers are tentative; verify against PDF before citation.

# 11 A review of different techniques and challenges of quantum computing in various applications (2022)

**Authors**: B. Aruna Devi, N. Alangudi Balaji, Mulugeta Tesema  
**Venue**: book chapter / preprint (chapter in edited volume)  
**DOI**: https://doi.org/10.1515/9783110798159-011  
**Suggested chapter sections**: §1.2 Motivation (Intro), §2.1 NISQ & limits, §2.2 Taxonomy of QC, §2.3 Challenges (decoherence, interconnect), §2.4 QC models & QNNs

## 1-paragraph summary
This chapter is a broad review of quantum computing techniques, a proposed taxonomy, representative models, and the principal challenges for near-term devices. It emphasizes limitations of current NISQ hardware, highlights variational approaches (VQE and related variational algorithms), surveys models (circuit, perceptron, automata, neural computation, abelian doubles), and outlines open problems such as qubit decoherence, interconnectivity, and scaling. The authors position the work as a state-of-the-art summary intended to identify areas needing further research and to inform industry-relevant applications and post-quantum cryptography.

## Key concepts (with location)
- **NISQ (Noisy Intermediate Scale Quantum)** — 11.1 Introduction — "NISQ machines have already proven that they are more effective than conventional computers at tackling a subset of tasks that are ideally suited for quantum computing [1]." (11.1 Introduction — p.148)
- **Decoherence of qubits** — 11.3 Challenges — "The term “decoherence of qubits” refers to the process by which qubits lose their coherent properties as a result of interaction with their surroundings." (11.3 Challenges — p.150)
- **Quantum gates / operation minimization** — 11.1 Introduction — "It is important to keep the number of operations, which are also known as quantum gates, to a minimum because the longer it takes to perform them, the more errors are introduced into the quantum state, and the more likely it is to decohere." (11.1 Introduction — p.148)
- **Variational Quantum Eigensolver (VQE)** — 11.1 Introduction — "In the field of NISQ algorithms, the Variational Quantum Eigensolver (VQE) stands out as one of the most promising instances [5]." (11.1 Introduction — p.148)
- **Quantum computing taxonomy (features categories)** — 11.2 Taxonomy — "The quantum computing taxonomy takes into account all of the relevant elements, including the fundamental features, the algorithmic features, the time and gate features, and the extra features: A) Features that are fundamental, B) Features that are algorithmic, C) Features that are time and gate, and D) Features that are additional." (11.2 Taxonomy — p.149)
- **Four major categories of quantum models** — 11.4 Models in QC — "It will be considerably simpler to undertake an analysis of the articles described here due to the fact that there are only four major categories of quantum models." (11.4 Models in QC — p.152)
- **Quantum Neural Network (QNN)** — 11.4.4 Quantum neural computation — "A Quantum Neural Network (QNN) that can be taught by supervised learning and can represent either classical or quantum labeled input." (11.4.4 Quantum neural computation — p.154)
- **Entangled quantum neural processing robustness claim** — 11.4.4 Quantum neural computation — "Entangled quantum neural processing is immune to both noise and loss of coherence." (11.4.4 Quantum neural computation — p.154)

## Quotable claims (with location)
- 11.1 Introduction — "Quantum computing does not feature a significant number of actual qubits to make it possible to develop robust error correction systems." — *useful for: §1.2 Motivation / §2.1 NISQ limits*
- 11.1 Introduction — "NISQ machines have already proven that they are more effective than conventional computers at tackling a subset of tasks that are ideally suited for quantum computing [1]." — *useful for: §1.2 Motivation / §2.1 NISQ opportunities*
- 11.1 Introduction — "In the field of NISQ algorithms, the Variational Quantum Eigensolver (VQE) stands out as one of the most promising instances [5]." — *useful for: §2.2 Algorithms (VQE)*
- 11.2 Taxonomy — "In this section, we will organize the various quantum computing technologies into the several groups that they belong to, according to the criteria outlined in the introduction." — *useful for: §2.2 Taxonomy framing*
- 11.3 Challenges — "The term “decoherence of qubits” refers to the process by which qubits lose their coherent properties as a result of interaction with their surroundings." — *useful for: §2.3 Challenges (decoherence)*
- 11.3 Challenges — "The development of effective error correction strategies for NISQ devices is now receiving a large amount of interest in the field of quantum computing research, which is spending a significant portion of its attention on the production of quantum computers." — *useful for: §2.3 Research directions*
- 11.4.4 Quantum neural computation — "A Quantum Neural Network (QNN) that can be taught by supervised learning and can represent either classical or quantum labeled input." — *useful for: §2.4 QML background*
- 11.5 Conclusion and future work — "On the other hand, it is not yet clear how to include all of these various performance characteristics into a single method of quantum computing." — *useful for: §2.5 Open problems / future work*

## Limitations stated by authors
- "Quantum computing does not feature a significant number of actual qubits to make it possible to develop robust error correction systems." — 11.1 Introduction — p.148
- "There are particular problems in developing a large-scale quantum computer." — 11.3 Challenges — p.150
- "On the other hand, it is not yet clear how to include all of these various performance characteristics into a single method of quantum computing." — 11.5 Conclusion and future work — p.155
- "In addition, because of the challenges involved in efficiently expanding the number of qubits that can presently be realized, classical supercomputers cannot yet be fully replaced by commercial quantum computers at their current state of development." — 11.5 Conclusion and future work — p.156

## How this paper might be used in the chapter
- §1 (Introduction): use the authors' pragmatic framing of NISQ limits and potential ("Quantum computing does not feature..." and "NISQ machines have already proven...") to motivate why the thesis focuses on near-term applicability.
- §2 (Background): cite the taxonomy section as a broad organizational reference when summarizing QC feature categories (fundamental, algorithmic, time/gate, extra).
- §2 (Background — Algorithms): cite the VQE and variational-algorithm emphasis as justification for focusing on variational approaches in financial applications.
- §2 (Background — Challenges): use the "decoherence" and "interconnect" quotes to introduce hardware constraints that affect algorithm design and mapping for financial workloads.
- §2 (Background — QML): reference the QNN / QNN training claims when discussing quantum machine learning approaches, while noting the authors' tentative stance on practical speedups.

## Researcher to verify
- [ ] Confirm exact page numbers in the PDF for each quoted passage — ACTION REQUIRED at citation time: page numbers in this note are LLM-assigned; verify each one in the PDF before pasting a citation that uses them.
- [ ] Verify the formal publication venue — ACTION REQUIRED at citation time: confirm the De Gruyter edited-volume title and editors from the official DOI landing page (10.1515/9783110798159-011) before adding to references.bib.
- [ ] Check Figure 11.5 and Table 11.1 in the original PDF — ACTION REQUIRED only if you actually plan to cite the figure/table; otherwise skip.
- [x] Validate the claim "Entangled quantum neural processing is immune to both noise and loss of coherence." — RESOLVED-VIA-BANNER + DO-NOT-CITE: factually wrong claim; not cited (see KEEP-WITH-CAVEAT banner at top).
