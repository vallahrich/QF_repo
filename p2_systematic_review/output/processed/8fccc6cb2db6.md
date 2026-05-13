---
aliases:
- Quantum on the MONEY
- Quantum MONEY
authors:
- James Hayes
auto_detected: true
classification: ''
contradiction_flags:
- contradiction:scalability
doi: ''
evaluation_type: conceptual-only
evidence_type: ''
has_quantitative_results: true
idea_tags:
- idea:quantum-advantage
- idea:near-term-feasibility
- idea:hybrid-approach
journal_or_venue: Engineering & Technology (E&T magazine)
methodology_tags:
- quantum-annealing-qubo
- amplitude-estimation
- quantum-cryptography
- qft-phase-estimation
- error-mitigation
- hybrid-quantum-classical
paper_type: ''
quantum_advantage_claim: theoretical
related_papers: []
relevance_phase1: high
relevance_phase3: medium
source_type: industry-report
source_type_confidence: medium
step1_date: '2026-04-14T11:05:34.378916'
step1_model: gpt-5-mini
step2_date: '2026-04-14T11:05:34.378916'
step2_model: gpt-5-mini
step3_date: '2026-04-14T11:05:34.378916'
step3_model: gpt-5-mini
step4_date: '2026-04-14T11:05:34.378916'
step4_model: gpt-5-mini
step5_date: '2026-04-14T11:05:34.378916'
step5_model: gpt-5-mini
step6_date: '2026-04-14T11:05:34.378916'
step6_model: gpt-5-mini
steps_completed:
- 1
- 2
- 3
- 4
- 5
- 6
tags:
- topic/portfolio-optimization
- topic/derivative-pricing
- topic/risk-management
- topic/trading-execution
- topic/simulation-monte-carlo
- topic/fraud-detection
- topic/cryptography-security
- method/quantum-annealing-qubo
- method/amplitude-estimation
- method/quantum-cryptography
- method/qft-phase-estimation
- method/error-mitigation
- method/hybrid-quantum-classical
- idea/quantum-advantage
- idea/near-term-feasibility
- idea/hybrid-approach
- contradiction/scalability
title: Quantum on the MONEY
topic_tags:
- portfolio-optimization
- derivative-pricing
- risk-management
- trading-execution
- simulation-monte-carlo
- fraud-detection
- cryptography-security
year: '2019'
zotero_key: ''
---

## Abstract summary
Industry-report overview of how quantum computing is expected to affect financial services, summarising market forecasts, emerging commercial hardware (IBM Q System One, D-Wave, Rigetti, Fujitsu) and key use cases such as portfolio optimisation, risk analysis, high-frequency trading and CRM, with case studies from banks like NatWest and JPMorgan Chase. It also highlights major cyber-security concerns — particularly the threat to current public-key cryptography and cryptocurrencies — and discusses preparedness measures including post-quantum cryptography, standards activity (X9 study group) and quantum-safe initiatives such as MIKEY-SAKKE.
## Methodology
This article is an industry survey and journalistic review rather than an empirical research study. The authors synthesize public-facing materials (vendor press releases and product launches such as IBM Q System One, Fujitsu Digital Annealer, D-Wave and Rigetti offerings), market research (BCC Research forecasts), organisational reports (Atos 2018 report, Global Risk Institute commentary), standards activity (Accredited Standards Committee X9 study group) and first-hand quotes from industry experts and practitioners (e.g., JPMorgan Chase, NatWest, Secure Chorus, Ridgeback Network Defense). It uses illustrative case studies (for example, a NatWest–Fujitsu proof-of-concept on High Quality Liquid Assets) and expert opinion to identify potential applications (portfolio optimisation, HFT, Monte Carlo pricing, fraud detection), threats (cryptographic vulnerability to Shor-style attacks) and mitigation efforts (post-quantum cryptography, MIKEY-SAKKE evolution). The piece also provides a historical timeline of quantum milestones to contextualise adoption expectations. No original experimental protocol, datasets, or computational experiments are reported by the authors; the methodology is therefore a qualitative synthesis of secondary sources and interviews.

**Algorithms used:** Quantum annealing, Shor's algorithm, Monte Carlo (quantum-accelerated Monte Carlo), Quantum error correction (surface code)
**Frameworks:** IBM Q Network / IBM Q System One, IBM Q Experience (cloud), Fujitsu Digital Annealer, QCaaS (Quantum-Computing-as-a-Service, discussed conceptually), MIKEY-SAKKE (cryptography protocol / standardisation effort)
## Experiment details
<!-- Step 3 output — experiment replication details -->

## Findings
- [supported] IBM announced the Q System One, a 20-qubit integrated quantum system positioned for commercial use.
- [supported] Commercial vendors and start-ups (D-Wave, Rigetti) sell quantum or quantum-annealing machines; Fujitsu markets a quantum-inspired Digital Annealer.
- [speculative] Estimates for mainstream commercial quantum adoption vary widely (IBM: ~4–5 years; others: a decade or more).
- [speculative] Market research (BCC Research) projects rapid market growth for quantum computing (CAGR figures to 2022 and 2027) and very high sectoral uptake in financial services (quoted CAGR).
- [supported] NatWest (with Fujitsu) reports a proof-of-concept in which optimisation of a High Quality Liquid Assets portfolio (£120bn) was completed ~300× faster than conventional cloud compute and with higher accuracy.
- [supported] Quantum methods can speed up Monte Carlo–style algorithms used in pricing financial derivatives (article cites a Physical Review A paper demonstrating a quantum speedup for Monte Carlo).
- [supported] Quantum computers (per theoretical results such as Shor's algorithm) threaten current public-key cryptography and therefore pose systemic cyber-security risks to financial services.
- [supported] Some financial organisations and standards bodies are actively assessing quantum risk and exploring/posting quantum-resistant algorithms (e.g., ASC X9 study group, bank PoCs, Secure Chorus/ISARA collaboration).
- [supported] Some banks have already used quantum cryptography in link encryption products (e.g., protecting off-site backups).
- [speculative] Quantum technologies are claimed to have potential applications across finance: portfolio optimisation, asset pricing, risk analysis, fraud detection, CRM personalisation, and HFT acceleration, but these are presented as prospective or exploratory.
- [speculative] Cryptocurrency wallets (private keys) are vulnerable to future quantum attacks; proof-of-work consensus mechanisms are described as comparatively less vulnerable (statement presented as tentative/observational).
- [speculative] Quantum-Computing-as-a-Service (QCaaS) is anticipated as a delivery model and raises questions about access controls, regulation and criminal use — but practical access controls and timelines are uncertain.
- [supported] High-frequency trading represented around 50% of US equity trades (citing TABB Group as the source).
- [supported] The article recounts established quantum-research milestones (Shor's algorithm, quantum error correction, surface code, increasing coherence times) as supporting the technical basis for claimed future capabilities.

**Results summary:** The article (industry-report style) reports that financial services are both early movers and prime targets for quantum computing: vendors (IBM, D-Wave, Rigetti, Fujitsu) are delivering hardware or quantum-inspired systems, banks and fintech firms are running proofs-of-concept (notably NatWest/Fujitsu reporting a 300× speedup on an HQLA portfolio case), and market analysts forecast rapid market growth. It also highlights a major, well-founded cybersecurity concern: quantum algorithms (e.g., Shor) threaten existing public-key cryptography, prompting industry and standards activity around post-quantum cryptography. Many operational benefits (HFT acceleration, portfolio optimisation, fraud detection, CRM improvements) are presented as promising but largely exploratory at present.

**Performance claims:**
- NatWest/Fujitsu PoC: optimised calculations on a £120bn High Quality Liquid Assets (HQLA) portfolio completed ~300× faster than conventional cloud-based compute, with higher accuracy.
- IBM Q System One: 20-qubit integrated general-purpose quantum system (commercial offering).
- BCC Research market forecast: industry CAGR 37.3% to 2022 with a projected market value of $161M (2022); CAGR ~53% to 2027 with projected market value $1.3B (2027); financial services sector CAGR 62.6% (2022–2027) — quoted market-research figures.
- HFT statistic: high-frequency trading accounts for around 50% of all US equity trades (TABB Group).
## Quantum advantage claim
**Classification:** theoretical

The article presents theoretically established quantum advantages (e.g., Shor's algorithm breaking public-key crypto; quantum speedups for Monte Carlo methods) and several vendor/PoC performance claims, but does not document widely replicated, large-scale, fault-tolerant demonstrations of practical quantum advantage for core financial workloads. Many application claims remain exploratory or vendor/forecast-driven rather than independently validated at production scale.
## Limitations
- Uncertainty over timeframe for commercial-scale, general-purpose quantum computers (estimates range from ~4-5 years to a decade or more).
- Current quantum hardware scale is small (controlled qubits are measured in the tens, not the thousands or millions required for large-scale cryptanalytic attacks or broad commercial workloads).
- Significant technical barriers remain: error correction, coherence times, bandwidth, environmental requirements and fault-tolerance are not yet solved for large-scale systems.
- Many existing quantum applications are heuristic or approximate (e.g., quantum Monte Carlo speedups are not exact methods but probabilistic/heuristic approaches).
- Public-key cryptography in widespread use is vulnerable to future quantum attacks; migration to quantum-safe schemes is non-trivial.
- Cryptocurrency wallets and some blockchain components are vulnerable to quantum attacks; asymmetric distribution of quantum capability could threaten distributed ledgers.
- Access models such as Quantum-Computing-as-a-Service (QCaaS) raise unresolved security and vetting challenges (how to prevent criminal use of cloud quantum resources).
- Adoption and integration into financial institutions require substantial proof-of-concept, changes to digital transformation roadmaps, and replacement of aged platforms.
- There is limited visibility into when/how malicious actors (nation-states or cybercriminals) will obtain quantum capability and how immediate the risk becomes.
- Standards and industry-wide agreements on quantum-safe cryptography and practices are still under development (work in progress by standards bodies like Accredited Standards Committee X9).
- [inferred] Economic and operational costs of migrating large financial infrastructures and cryptographic ecosystems to quantum-safe solutions are likely to be substantial and uncertain.
- [inferred] Potential systemic risks from uneven adoption (e.g., firms that lag in migration being exploited) and from new quantum-enabled market dynamics (such as amplified HFT advantages) are not quantified.
- [inferred] Legal and regulatory frameworks to govern access to quantum computing services and to mandate or incentivize crypto migration are lacking or immature.
- [inferred] Limited availability of verified, production-ready quantum algorithms that deliver clear, reproducible advantage for concrete financial use-cases beyond proofs of concept.
## Open questions
- When will large-scale, fault-tolerant, general-purpose quantum computers become available and at what scale will they pose real cryptographic risk?
- Which specific financial services operations will obtain the greatest, demonstrable benefit from quantum acceleration (portfolio optimisation, asset pricing, risk analysis, HFT, CRM, fraud detection, etc.)?
- How should financial institutions prioritise systems and data for migration to quantum-safe cryptography?
- Which post-quantum (quantum-safe) public-key cryptosystems are most suitable for financial services and legacy interoperability (e.g., suitability of MIKEY-SAKKE evolution)?
- How can QCaaS providers be regulated or monitored to minimise the risk of malicious actors gaining access to quantum capabilities?
- What is the realistic timeframe for threat actors (state or non-state) to use quantum computing to decrypt archived or in-transit sensitive data?
- How vulnerable are different blockchain consensus mechanisms and cryptocurrency implementations to quantum attacks, and how should blockchains be redesigned for quantum resistance?
- How can financial institutions detect and evaluate the extent of quantum-related threats before an attack occurs?
- What standards, governance and industry collaboration models are required to coordinate a secure migration to quantum-safe infrastructure across the financial sector?
- How will quantum-enabled trading (e.g., HFT) affect market stability and volatility, and what safeguards are needed?
- What are effective operational and organisational changes (people, processes, tooling) needed to integrate quantum technologies into existing IT and risk frameworks?
- How should financial institutions balance early investment in quantum technologies with the immediate need to secure systems against future quantum threats?

**Future work:**
- Banks and financial institutions performing quantum risk assessments and implementing proofs of concept to map benefits and exposures.
- Pilot deployments and selective rollout of quantum-resistant algorithms in selected systems within financial organisations.
- Standards and study-group work (e.g., Accredited Standards Committee X9) to review quantum risk and recommend industry actions and algorithm selections.
- Development and standardisation efforts to evolve existing protocols (for example, Secure Chorus and ISARA's work to make MIKEY-SAKKE quantum-safe).
- Research and development of quantum algorithms for finance (portfolio optimisation, Monte Carlo speedups for derivative pricing, fraud detection and risk-evaluation algorithms).
- Industry collaborations and initiatives (e.g., IBM Q Network engagement with banks) to provide cloud-based access, simulators and shared development frameworks for experimentation.
- Development of vendor and third-party solutions (e.g., Fujitsu Digital Annealer, Ridgeback's quantum-enabled risk evaluation algorithms) and additional proof-of-concept studies like NatWest–Fujitsu.
- Exploration of governance, regulatory and access-control mechanisms for QCaaS to mitigate criminal or state misuse.
- Continued research into error correction, coherence improvement, scalable qubit architectures and environment engineering to enable fault-tolerant quantum computing.
## Key ideas
- #idea:quantum-advantage — Industry claims and theoretical results (Shor, amplitude-estimation for Monte Carlo) suggest potential for quantum speedups in cryptography-breaking, Monte Carlo pricing, and certain optimisation tasks.
- #idea:near-term-feasibility — Vendors and market analysts project near- to mid-term commercial uptake (IBM 4–5 years claim; several CAGR market forecasts), and some banks report proofs-of-concept.
- #idea:hybrid-approach — Discussion of QCaaS, vendor cloud offerings (IBM Q Experience), and PoCs (NatWest/Fujitsu) implies hybrid quantum-classical workflows and service-delivery models for financial firms.
- #limitation:qubit-count — Commercial systems cited are small (IBM Q System One ~20 qubits) and the report notes absence of large-scale, fault-tolerant hardware required for many proposed workloads.
- #limitation:noise — The article highlights the need for quantum error correction (surface code) and ongoing R&D, indicating hardware noise and error rates remain limiting factors.
- #limitation:no-empirical-validation — Many performance claims (market forecasts, vendor PoCs such as the NatWest 300× claim) are reported secondarily with little methodological detail or independent replication.
## Contradictions
- The article promotes optimistic near-term commercialisation timelines and large market-growth forecasts while simultaneously acknowledging there are no widely replicated, large-scale, fault-tolerant demonstrations — a tension over scalability and readiness.
- Vendor/PoC performance claims (e.g., NatWest/Fujitsu 300× speedup) are presented alongside admission of limited methodological detail and independent validation, contradicting the strength of the claimed practical quantum advantage.
- The report stresses the existential cryptographic threat from Shor-style algorithms yet notes that many operational applications (HFT acceleration, portfolio optimisation, fraud detection) remain exploratory — contrasting high confidence in cryptographic impact with lower confidence in other financial use-cases.
## Notable quotes
<!-- Researcher-added — verbatim quotes with page references -->

## Researcher notes
<!-- Researcher-added — not LLM generated -->
