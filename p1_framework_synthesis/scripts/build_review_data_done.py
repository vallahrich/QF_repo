"""
Phase 1 — Steps 1-4: Load the Phase 1 s1 extraction files, assess each paper
and entry, normalise candidate labels, and produce review_data_done.json.

Methodology framing (clarified 2026-05-02):
  This is *not* strict inductive open coding (Elo & Kyngäs 2008). The PROBLEM_CODE_MAP
  and SOLUTION_CODE_MAP regex dictionaries below define an *a priori* canonical
  code vocabulary; the LLM-extracted labels are then deductively normalised onto
  that vocabulary. Paper-level inclusion/exclusion decisions (EXCLUSIONS,
  NEEDS_RECHECK below) were similarly encoded as Python dictionaries rather than
  as per-document JSON files in s2_coding/. The accurate methodological
  description is "LLM-assisted candidate code generation followed by
  researcher-curated regex normalisation against an a priori vocabulary
  (Cruzes & Dybå 2011)". See README.md and audit-trail.md Divergence Log entry D-5.

This script implements:
    Step 1: Load all extractions into a unified structure
    Step 2: Paper-level quality triage (status, relevance, exclusion_reason)
    Step 3: Entry-level accept/reject decisions
    Step 4: Candidate-code normalisation per accepted entry

Assessment criteria (from REVIEW_CHECKLIST.md):
  - Does the paper substantively discuss quantum computing applied to finance?
  - Is the venue credible?
  - Does the extraction quality support taxonomy building?

Output: p1_framework_synthesis/s2_coding/review_data_done.json
"""

import json
import re
import os
from pathlib import Path
from collections import Counter

# ── Paths ──────────────────────────────────────────────────────────────
ROOT = Path(__file__).resolve().parent.parent
EXTRACTIONS_DIR = ROOT / "s1_extractions"
OUTPUT_FILE = ROOT / "s2_coding" / "review_data_done.json"

# ── Paper-level assessment rules ───────────────────────────────────────
# Papers are triaged based on: (a) finance relevance, (b) venue credibility,
# (c) extraction depth, (d) whether the paper is a generic QC intro with
# no substantive finance content.

# Papers explicitly marked for exclusion (generic QC, no finance substance,
# or toy work with minimal taxonomy value).
EXCLUSIONS = {
    "2022_Khari_Quantum_Computing": {
        "reason": "Misidentified paper — extraction covers CryptoQNet (crypto market prediction), "
                  "not the original Khari paper. Narrow scope (cryptocurrency forecasting only) "
                  "with limited taxonomy value for the broader QC-in-finance framework.",
        "relevance": "low",
    },
    "2024_Pasupuleti_Advancements_Quantum_Computing_Information": {
        "reason": "Generic quantum computing overview with no substantive finance-specific content. "
                  "Covers QC principles, healthcare, and general applications. Finance mentioned "
                  "only in passing.",
        "relevance": "low",
    },
    "2024_VenkataRamana_Fundamentals_Quantum_Computing_Principles": {
        "reason": "Introductory QC fundamentals paper (qubits, gates, circuits). No finance-specific "
                  "content. Educational material not suitable for taxonomy building.",
        "relevance": "low",
    },
    "2025_Chawla_Quantum_Computing_Underlying_Principle": {
        "reason": "Beginner-level QC overview. Discusses basic principles without substantive "
                  "finance application analysis. No problem–solution mappings for finance.",
        "relevance": "low",
    },
    "2026_RejinaPV_Quantum_Computing_Beginner_S": {
        "reason": "Beginner's guide to QC. No finance-specific analysis. General QC overview "
                  "not useful for taxonomy construction.",
        "relevance": "low",
    },
    "2026_Dumba_Quantum_Thinking_Finance": {
        "reason": "Toy model applying quantum superposition metaphor to risk. Not actual quantum "
                  "computing for finance — uses quantum-inspired thinking, not quantum algorithms. "
                  "No algorithmic content or implementation.",
        "relevance": "low",
    },
    "2024_Singh_Challenges_Opportunities_Quantum_Computing": {
        "reason": "Broad multi-sector QC overview (healthcare, logistics, finance, chemistry). "
                  "Finance is one of many sectors covered superficially. Insufficient depth "
                  "for taxonomy building.",
        "relevance": "low",
    },
}

# Papers flagged for reduced relevance but still included
NEEDS_RECHECK = {
    "2023_Markna_Unveiling_Advanced_Computational_Applications": {
        "reason": "Very high-level overview with limited depth per topic. Finance is mentioned "
                  "alongside many other domains. Extraction is shallow.",
        "relevance": "medium",
    },
    "2024_Coccia_Evolution_Quantum_Computing_Theoretical": {
        "reason": "Innovation management perspective on QC evolution. Limited technical depth "
                  "on finance applications but provides useful industry trajectory context.",
        "relevance": "medium",
    },
    "2026_AtharvaJain_Quantum_Computing_S_Role": {
        "reason": "Focuses on quantum communication networks. Finance applications are secondary. "
                  "May contribute to cryptography/security taxonomy category.",
        "relevance": "medium",
    },
    "2026_MohammadAliTagati_Quantum_Computing_Future_Finance": {
        "reason": "Borderline relevance — published in ISRG J Econ Bus Manag (low-impact venue); "
                  "extraction depth is shallow with mostly generic statements about ‘large volume "
                  "of financial data’ and ‘complexity of financial decision-making’ and little "
                  "algorithmic specificity. Re-checked 2026-05-02; demoted from auto-verified "
                  "to needs-recheck pending re-read against the PDF.",
        "relevance": "medium",
    },
}

# High-relevance surveys that anchor the taxonomy. 2026-05-02 freeze: was a
# bare `set` literal; converted to dict-with-rationales for symmetry with
# EXCLUSIONS / NEEDS_RECHECK so every triage decision has a recorded reason.
HIGH_RELEVANCE = {
    "2019_Ors_Quantum_Computing_Finance_Overview":
        "Foundational industry-credible overview; broad coverage of QC-in-finance applications.",
    "2020_AdamBouland_Prospects_Challenges_Quantum_Finance":
        "High-citation foundational survey of prospects and challenges; deep extraction with verbatim evidence.",
    "2022_Albareti_Structured_Survey_Quantum_Computing":
        "Structured survey with explicit taxonomy of QC-in-finance approaches.",
    "2022_AndrsGmez_Survey_Quantum_Computational_Finance":
        "Comprehensive survey of quantum computational finance methods and case studies.",
    "2022_Canabarro_Quantum_Finance_Tutorial_Quantum":
        "Tutorial-style coverage with worked examples across portfolio / pricing / ML silos.",
    "2022_DylanHerman_Survey_Quantum_Computing_Finance":
        "arXiv preprint of the Herman survey \u2014 superseded by the 2023 published version (see SUPERSEDED).",
    "2023_Abbas_Quantum_Optimization_Potential_Challenges":
        "Quantum optimization in finance \u2014 high-quality assessment of potential and challenges.",
    "2023_Herman_Quantum_Computing_Finance":
        "Published version of the Herman et al. survey; canonical entry (cf. 2022 preprint).",
    "2024_Abbas_Challenges_Opportunities_Quantum_Optimization":
        "Follow-up survey on quantum optimization opportunities in finance with expanded scope.",
    "2024_Sotelo_Quantum_Computing_Finance_Intesa":
        "Industry case-study survey from Intesa Sanpaolo \u2014 substantive QC-in-finance coverage.",
    "2025_Irfan_Quantum_Finance_Unleashed_Transforming":
        "Recent (2025) survey of QC applications across multiple finance silos.",
    "2026_Sarin_Leveraging_Quantum_Computing_Business":
        "Recent (2026) overview of QC for finance/business with explicit problem\u2013solution mapping.",
}

# Superseded papers — the SOURCE id is collapsed onto the TARGET id during
# downstream aggregation so matrix counts are not double-counted (D-6).
# Both files remain in s1_extractions/ for provenance.
SUPERSEDED = {
    # Herman et al. survey: arXiv preprint (2022) → published version (2023).
    "2022_DylanHerman_Survey_Quantum_Computing_Finance":
        "2023_Herman_Quantum_Computing_Finance",
}

# ── Open coding vocabulary ─────────────────────────────────────────────
# Maps common terms found in problem/solution labels to standardised codes.
# This is an inductive codebook built from observing the extraction data.

PROBLEM_CODE_MAP = {
    # Portfolio optimization family
    r"portfolio\s*(optimi[sz]|construct|alloc|select|rebalanc)": ["portfolio-optimization"],
    r"mean[- ]variance": ["portfolio-optimization", "mean-variance"],
    r"asset\s*alloc": ["portfolio-optimization", "asset-allocation"],
    r"markowitz": ["portfolio-optimization", "mean-variance", "markowitz"],
    r"portfolio\s*diversif": ["portfolio-optimization", "diversification"],
    r"index\s*track": ["portfolio-optimization", "index-tracking"],
    r"factor\s*invest": ["portfolio-optimization", "factor-investing"],
    # Derivative pricing family
    r"option\s*pric": ["derivative-pricing", "option-pricing"],
    r"derivative\s*pric": ["derivative-pricing"],
    r"derivative\s*valuat": ["derivative-pricing"],
    r"exotic\s*(option|derivative)": ["derivative-pricing", "exotic-derivatives"],
    r"european\s*option": ["derivative-pricing", "european-options"],
    r"american\s*option": ["derivative-pricing", "american-options"],
    r"asian\s*option": ["derivative-pricing", "asian-options"],
    r"barrier\s*option": ["derivative-pricing", "barrier-options"],
    r"black[- ]scholes": ["derivative-pricing", "black-scholes"],
    r"interest\s*rate\s*(deriv|model|pric)": ["derivative-pricing", "interest-rate-derivatives"],
    r"swap": ["derivative-pricing", "swaps"],
    r"credit\s*valuation\s*adjust|cva": ["derivative-pricing", "cva"],
    r"xva": ["derivative-pricing", "xva"],
    # Risk management family
    r"risk\s*manage": ["risk-management"],
    r"value[- ]at[- ]risk|var\b": ["risk-management", "value-at-risk"],
    r"cvar|conditional\s*value": ["risk-management", "cvar"],
    r"stress\s*test": ["risk-management", "stress-testing"],
    r"market\s*risk": ["risk-management", "market-risk"],
    r"credit\s*risk(?!\s*scor)": ["risk-management", "credit-risk"],
    r"systemic\s*risk": ["risk-management", "systemic-risk"],
    r"operational\s*risk": ["risk-management", "operational-risk"],
    r"tail\s*risk": ["risk-management", "tail-risk"],
    r"counterparty": ["risk-management", "counterparty-risk"],
    r"risk\s*aggregat": ["risk-management", "risk-aggregation"],
    r"risk\s*analys": ["risk-management", "risk-analysis"],
    # Monte Carlo / simulation family
    r"monte\s*carlo": ["monte-carlo-simulation"],
    r"stochastic\s*simul": ["stochastic-simulation"],
    r"path\s*simul": ["monte-carlo-simulation", "path-simulation"],
    r"random\s*walk": ["stochastic-simulation", "random-walk"],
    # Machine learning family
    r"machine\s*learn": ["machine-learning"],
    r"classif": ["machine-learning", "classification"],
    r"time[- ]series|forecast": ["forecasting"],
    r"natural\s*language|nlp|sentiment": ["machine-learning", "nlp-sentiment"],
    r"anomaly\s*detect": ["anomaly-detection"],
    r"pattern\s*recogn": ["machine-learning", "pattern-recognition"],
    r"regression": ["machine-learning", "regression"],
    r"clustering": ["machine-learning", "clustering"],
    # Fraud detection family
    r"fraud\s*detect": ["fraud-detection"],
    r"anti[- ]money|aml": ["fraud-detection", "aml"],
    r"transaction\s*monitor": ["fraud-detection", "transaction-monitoring"],
    # Trading family
    r"trad(e|ing)\s*(strat|execut|optimi)": ["trading"],
    r"arbitrage": ["trading", "arbitrage"],
    r"high[- ]frequency|hft": ["trading", "high-frequency-trading"],
    r"market\s*micro": ["trading", "market-microstructure"],
    r"order\s*(rout|execut)": ["trading", "order-execution"],
    # Credit / lending family
    r"credit\s*scor": ["credit-scoring"],
    r"default\s*predict": ["credit-scoring", "default-prediction"],
    r"loan|lend": ["credit-lending"],
    # Cryptography / security family
    r"cryptograph|qkd|quantum\s*key": ["quantum-cryptography"],
    r"post[- ]quantum": ["quantum-cryptography", "post-quantum"],
    r"cyber\s*secur": ["quantum-cryptography", "cybersecurity"],
    r"rsa|elliptic\s*curve": ["quantum-cryptography", "classical-crypto-vulnerability"],
    # Insurance / actuarial
    r"insur|actuari|underwrit": ["insurance-actuarial"],
    # Optimization (generic)
    r"optimi[sz]ation(?!\s*portf)": ["optimization"],
    r"combinatorial": ["combinatorial-optimization"],
    r"np[- ]hard": ["np-hard-problems"],
    r"constraint\s*satisf": ["constraint-satisfaction"],
    r"scheduling": ["scheduling-optimization"],
    r"supply\s*chain": ["supply-chain-optimization"],
    # Simulation
    r"pricing\s*simulation": ["derivative-pricing", "monte-carlo-simulation"],
    r"quantum\s*simul": ["quantum-simulation"],
}

SOLUTION_CODE_MAP = {
    # Quantum annealing family
    r"quantum\s*anneal": ["quantum-annealing"],
    r"d[- ]wave": ["quantum-annealing", "d-wave"],
    r"qubo|quadratic\s*unconstrained": ["qubo-formulation"],
    r"ising\s*(model|formul)": ["ising-model"],
    r"simulated\s*anneal": ["simulated-annealing"],
    r"adiabatic": ["adiabatic-quantum-computing"],
    # Variational / NISQ family
    r"qaoa|quantum\s*approximate\s*optim": ["qaoa"],
    r"vqe|variational\s*quantum\s*eigen": ["vqe"],
    r"variational": ["variational-algorithm"],
    r"parameteriz|parameterised\s*circuit": ["parameterized-circuits"],
    r"nisq|noisy\s*intermediate": ["nisq"],
    # Amplitude estimation family
    r"amplitude\s*estimat|qae": ["quantum-amplitude-estimation"],
    r"quantum\s*monte\s*carlo|qmci": ["quantum-monte-carlo-integration"],
    r"quantum\s*speed[- ]?up.*monte\s*carlo": ["quantum-monte-carlo-integration"],
    # Quantum ML family
    r"quantum\s*neural\s*network|qnn": ["quantum-neural-network"],
    r"quantum\s*support\s*vector|qsvm": ["quantum-svm"],
    r"quantum\s*kernel": ["quantum-kernel-methods"],
    r"quantum\s*machine\s*learn": ["quantum-machine-learning"],
    r"quantum\s*classif": ["quantum-classification"],
    r"quantum\s*reinforcement": ["quantum-reinforcement-learning"],
    r"quantum\s*boltzmann": ["quantum-boltzmann-machine"],
    r"quantum\s*generative|qgan": ["quantum-generative-model"],
    r"quantum\s*transfer\s*learn": ["quantum-transfer-learning"],
    r"quantum\s*(feature|embedding)": ["quantum-feature-map"],
    r"quantum\s*reservoir": ["quantum-reservoir-computing"],
    r"quantum\s*autoencoder": ["quantum-autoencoder"],
    # Grover family
    r"grover": ["grover-search"],
    r"amplitude\s*amplif": ["amplitude-amplification"],
    r"quantum\s*search": ["quantum-search"],
    # HHL / linear systems
    r"hhl|harrow[- ]hassidim": ["hhl-algorithm"],
    r"quantum\s*linear\s*system": ["quantum-linear-systems"],
    r"quantum\s*matrix": ["quantum-linear-algebra"],
    # Quantum walks
    r"quantum\s*walk": ["quantum-walk"],
    # Hybrid approaches
    r"hybrid\s*(quantum|classical)": ["hybrid-quantum-classical"],
    r"classical[- ]quantum\s*(hybrid|integrat)": ["hybrid-quantum-classical"],
    # Quantum PCA / data analysis
    r"quantum\s*pca|quantum\s*principal": ["quantum-pca"],
    r"quantum\s*fourier|qft": ["quantum-fourier-transform"],
    r"quantum\s*phase\s*estimat": ["quantum-phase-estimation"],
    # Error mitigation
    r"error\s*(correct|mitigat)": ["error-mitigation"],
    r"fault[- ]tolerant": ["fault-tolerant"],
    # Quantum cryptography solutions
    r"quantum\s*key\s*distribut|qkd": ["quantum-key-distribution"],
    r"post[- ]quantum\s*crypto": ["post-quantum-cryptography"],
    # Specific algorithm families
    r"shor": ["shor-algorithm"],
    r"quantum\s*counting": ["quantum-counting"],
    r"quantum\s*sampling": ["quantum-sampling"],
    r"quantum\s*random\s*(number|walk)": ["quantum-random-generation"],
}

CLAIM_CODE_MAP = {
    r"quadratic\s*speed": ["quadratic-speedup"],
    r"exponential\s*speed": ["exponential-speedup"],
    r"polynomial\s*speed": ["polynomial-speedup"],
    r"quantum\s*advantage": ["quantum-advantage"],
    r"quantum\s*supremacy": ["quantum-supremacy"],
    r"nisq|noisy\s*intermediate": ["nisq-era"],
    r"fault[- ]tolerant": ["fault-tolerant-era"],
    r"qubit\s*(count|number|require)": ["qubit-requirements"],
    r"decoherence|noise|error\s*rate": ["hardware-noise"],
    r"scalab": ["scalability"],
    r"barren\s*plateau": ["barren-plateaus"],
    r"classical\s*simul": ["classical-simulability"],
    r"practical\s*advantage": ["practical-advantage"],
    r"near[- ]term": ["near-term-feasibility"],
    r"long[- ]term": ["long-term-potential"],
    r"gate\s*depth|circuit\s*depth": ["circuit-depth"],
    r"resource\s*estimat": ["resource-estimation"],
    r"benchmark": ["benchmarking"],
}


def load_extractions() -> list[dict]:
    """Step 1: Load all extraction JSONs."""
    papers = []
    json_files = sorted(EXTRACTIONS_DIR.glob("*.json"))
    print(f"Found {len(json_files)} extraction files")

    for jf in json_files:
        with open(jf, "r", encoding="utf-8") as f:
            data = json.load(f)

        paper_id = jf.stem
        # Ensure the paper has an id field
        data["id"] = paper_id

        # Ensure all expected sections exist
        for section in [
            "problem_domains", "solution_approaches", "problem_solution_mappings",
            "key_claims", "maturity_indicators", "open_questions"
        ]:
            if section not in data:
                data[section] = []

        # Ensure every entry in each section has a review object
        for section in [
            "problem_domains", "solution_approaches", "problem_solution_mappings",
            "key_claims", "maturity_indicators", "open_questions"
        ]:
            for entry in data[section]:
                if "review" not in entry:
                    entry["review"] = {"decision": None, "tags": {}}

        papers.append(data)
        print(f"  Loaded: {paper_id} ({len(data.get('problem_domains', []))} problems, "
              f"{len(data.get('solution_approaches', []))} solutions)")

    return papers


def assess_paper(paper: dict) -> dict:
    """Step 2: Paper-level quality triage."""
    paper_id = paper["id"]

    if paper_id in EXCLUSIONS:
        info = EXCLUSIONS[paper_id]
        paper["_review"] = {
            "reviewer": "LLM-assisted",
            "date": "2026-04-11",
            "status": "exclude",
            "relevance": info["relevance"],
            "exclusion_reason": info["reason"],
            "notes": "Excluded during Phase 1 paper-level triage."
        }
    elif paper_id in NEEDS_RECHECK:
        info = NEEDS_RECHECK[paper_id]
        paper["_review"] = {
            "reviewer": "LLM-assisted",
            "date": "2026-04-11",
            "status": "needs-recheck",
            "relevance": info["relevance"],
            "exclusion_reason": None,
            "notes": info["reason"]
        }
    elif paper_id in HIGH_RELEVANCE:
        paper["_review"] = {
            "reviewer": "LLM-assisted",
            "date": "2026-04-11",
            "status": "verified",
            "relevance": "high",
            "exclusion_reason": None,
            "superseded_by": SUPERSEDED.get(paper_id),
            "notes": HIGH_RELEVANCE[paper_id],
        }
    else:
        # Default: verified with medium relevance (contributes to taxonomy
        # but is not a primary anchor)
        doc_type = paper.get("metadata", {}).get("document_type", "")
        n_problems = len(paper.get("problem_domains", []))
        n_solutions = len(paper.get("solution_approaches", []))

        if n_problems >= 10 and n_solutions >= 10:
            rel = "high"
            note = "Substantial extraction depth supports taxonomy building."
        elif n_problems >= 5 or n_solutions >= 5:
            rel = "medium"
            note = "Moderate extraction depth; contributes specific problem–solution evidence."
        else:
            rel = "medium"
            note = "Limited extraction depth but provides focused evidence on specific topics."

        paper["_review"] = {
            "reviewer": "LLM-assisted",
            "date": "2026-04-11",
            "status": "verified",
            "relevance": rel,
            "exclusion_reason": None,
            "notes": note
        }

    return paper


def apply_codes(text: str, code_map: dict) -> list[str]:
    """Match text against a code map and return all matching codes."""
    codes = []
    text_lower = text.lower() if text else ""
    for pattern, code_list in code_map.items():
        if re.search(pattern, text_lower):
            codes.extend(code_list)
    return sorted(set(codes))


def assess_entry(entry: dict, section: str, paper_status: str) -> dict:
    """Step 3 & 4: Entry-level accept/reject + open coding."""
    # If paper is excluded, reject all entries
    if paper_status == "exclude":
        entry["review"]["decision"] = "reject"
        entry["review"]["tags"] = {}
        return entry

    # Decision logic
    confidence = entry.get("confidence", "medium")
    has_quote = bool(entry.get("quote", "").strip())
    has_location = bool(entry.get("location", "").strip())

    # Reject entries with low confidence AND no supporting quote
    if confidence == "low" and not has_quote:
        entry["review"]["decision"] = "reject"
        return entry

    # Accept everything else (high/medium confidence, or low with quote)
    entry["review"]["decision"] = "accept"

    # Step 4: Open coding
    codes = []
    if section == "problem_domains":
        label = entry.get("problem", "")
        desc = entry.get("description", "")
        codes = apply_codes(f"{label} {desc}", PROBLEM_CODE_MAP)
        if not codes:
            # Fallback: use the problem label itself as a code
            codes = [re.sub(r'[^a-z0-9]+', '-', label.lower()).strip('-')]
    elif section == "solution_approaches":
        label = entry.get("approach", "")
        desc = entry.get("description", "")
        codes = apply_codes(f"{label} {desc}", SOLUTION_CODE_MAP)
        if not codes:
            codes = [re.sub(r'[^a-z0-9]+', '-', label.lower()).strip('-')]
    elif section == "problem_solution_mappings":
        problem = entry.get("problem", "")
        approach = entry.get("approach", "")
        p_codes = apply_codes(problem, PROBLEM_CODE_MAP)
        s_codes = apply_codes(approach, SOLUTION_CODE_MAP)
        codes = p_codes + s_codes
        if not codes:
            codes = [
                re.sub(r'[^a-z0-9]+', '-', problem.lower()).strip('-'),
                re.sub(r'[^a-z0-9]+', '-', approach.lower()).strip('-')
            ]
    elif section == "key_claims":
        claim = entry.get("claim", "")
        claim_type = entry.get("claim_type", "")
        codes = apply_codes(claim, CLAIM_CODE_MAP)
        if claim_type:
            codes.append(f"claim-{claim_type}")
        if not codes:
            codes = [f"claim-{claim_type}" if claim_type else "claim-general"]
    elif section == "maturity_indicators":
        indicator = entry.get("indicator", "not-stated")
        codes = [f"maturity-{indicator}"]
    elif section == "open_questions":
        question = entry.get("question", "")
        codes = apply_codes(question, {**PROBLEM_CODE_MAP, **SOLUTION_CODE_MAP})
        codes.append("open-question")

    entry["codes"] = sorted(set(codes)) if codes else ["uncoded"]
    return entry


def compute_statistics(papers: list[dict]) -> dict:
    """Compute aggregate statistics for the assessment."""
    stats = {
        "total_papers": len(papers),
        "verified": 0,
        "excluded": 0,
        "needs_recheck": 0,
        "high_relevance": 0,
        "medium_relevance": 0,
        "low_relevance": 0,
        "total_entries": 0,
        "accepted_entries": 0,
        "rejected_entries": 0,
        "unique_problem_codes": set(),
        "unique_solution_codes": set(),
        "unique_claim_codes": set(),
    }

    for paper in papers:
        review = paper.get("_review", {})
        status = review.get("status", "unknown")
        relevance = review.get("relevance", "unknown")

        if status == "verified":
            stats["verified"] += 1
        elif status == "exclude":
            stats["excluded"] += 1
        elif status == "needs-recheck":
            stats["needs_recheck"] += 1

        if relevance == "high":
            stats["high_relevance"] += 1
        elif relevance == "medium":
            stats["medium_relevance"] += 1
        elif relevance == "low":
            stats["low_relevance"] += 1

        for section in [
            "problem_domains", "solution_approaches", "problem_solution_mappings",
            "key_claims", "maturity_indicators", "open_questions"
        ]:
            for entry in paper.get(section, []):
                stats["total_entries"] += 1
                decision = entry.get("review", {}).get("decision")
                if decision == "accept":
                    stats["accepted_entries"] += 1
                elif decision == "reject":
                    stats["rejected_entries"] += 1

                # Collect unique codes
                for code in entry.get("codes", []):
                    if section == "problem_domains":
                        stats["unique_problem_codes"].add(code)
                    elif section == "solution_approaches":
                        stats["unique_solution_codes"].add(code)
                    elif section == "key_claims":
                        stats["unique_claim_codes"].add(code)

    # Convert sets to sorted lists for JSON serialisation
    stats["unique_problem_codes"] = sorted(stats["unique_problem_codes"])
    stats["unique_solution_codes"] = sorted(stats["unique_solution_codes"])
    stats["unique_claim_codes"] = sorted(stats["unique_claim_codes"])

    return stats


def main():
    print("=" * 70)
    print("Phase 1 — Building review_data_done.json")
    print("=" * 70)

    # Step 1: Load all extractions
    print("\n── Step 1: Loading all extraction JSONs ──")
    papers = load_extractions()

    # Step 2: Paper-level quality triage
    print("\n── Step 2: Paper-level assessment ──")
    for paper in papers:
        assess_paper(paper)
        review = paper["_review"]
        print(f"  {paper['id']}: status={review['status']}, "
              f"relevance={review['relevance']}")

    # Steps 3-4: Entry-level decisions + open coding
    print("\n── Steps 3-4: Entry-level decisions + open coding ──")
    for paper in papers:
        paper_status = paper["_review"]["status"]
        entry_counts = Counter()

        for section in [
            "problem_domains", "solution_approaches", "problem_solution_mappings",
            "key_claims", "maturity_indicators", "open_questions"
        ]:
            for entry in paper.get(section, []):
                assess_entry(entry, section, paper_status)
                decision = entry.get("review", {}).get("decision", "unknown")
                entry_counts[decision] += 1

        print(f"  {paper['id']}: accepted={entry_counts.get('accept', 0)}, "
              f"rejected={entry_counts.get('reject', 0)}")

    # Compute statistics
    print("\n── Computing statistics ──")
    stats = compute_statistics(papers)

    # Build output structure
    output = {
        "tag_definitions": {
            "paper_section": [
                "introduction", "background", "methodology", "results",
                "discussion", "conclusion", "future-work"
            ],
            "code_type": [
                "problem", "solution", "mapping", "claim", "maturity", "question"
            ],
            "classification": []   # Populated after taxonomy construction
        },
        "_assessment_metadata": {
            "date": "2026-04-11",
            "assessor": "LLM-assisted (Phase 1, Step 2-4)",
            "methodology": "Inductive content analysis (Elo & Kyngäs, 2008)",
            "total_extraction_files": len(papers),
            "statistics": stats,
        },
        "papers": papers,
    }

    # Write output
    print(f"\n── Writing output to {OUTPUT_FILE} ──")
    os.makedirs(OUTPUT_FILE.parent, exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"  Papers loaded:         {stats['total_papers']}")
    print(f"  Verified:              {stats['verified']}")
    print(f"  Needs recheck:         {stats['needs_recheck']}")
    print(f"  Excluded:              {stats['excluded']}")
    print(f"  High relevance:        {stats['high_relevance']}")
    print(f"  Medium relevance:      {stats['medium_relevance']}")
    print(f"  Low relevance:         {stats['low_relevance']}")
    print(f"  Total entries:         {stats['total_entries']}")
    print(f"  Accepted entries:      {stats['accepted_entries']}")
    print(f"  Rejected entries:      {stats['rejected_entries']}")
    print(f"  Unique problem codes:  {len(stats['unique_problem_codes'])}")
    print(f"  Unique solution codes: {len(stats['unique_solution_codes'])}")
    print(f"  Unique claim codes:    {len(stats['unique_claim_codes'])}")
    print("=" * 70)


if __name__ == "__main__":
    main()
