"""
Phase 1 — Steps 5-9: Aggregate codes, build taxonomies, write output files.

Reads review_data_done.json and produces:
  - s3_taxonomy/problem-space.md
  - s3_taxonomy/solution-space.md
  - s4_outputs/codebook.md
  - s4_outputs/conceptual-framework.md
  - Updated audit-trail.md
"""

import json
from pathlib import Path
from collections import Counter, defaultdict

ROOT = Path(__file__).resolve().parent.parent
REVIEW_DATA = ROOT / "s2_coding" / "review_data_done.json"
TAXONOMY_DIR = ROOT / "s3_taxonomy"
OUTPUTS_DIR = ROOT / "s4_outputs"
AUDIT_TRAIL = ROOT / "audit-trail.md"

# ── Taxonomy definitions ───────────────────────────────────────────────
# These are the researcher-synthesised categories built from inspecting
# the aggregated open codes. Each category has:
#   - name (human-readable)
#   - key (machine-readable)
#   - definition (working definition for codebook)
#   - scope (what is included / excluded)
#   - constituent_codes (open codes that map to this category)

PROBLEM_TAXONOMY = [
    {
        "name": "Portfolio Optimisation and Asset Allocation",
        "key": "PD-01",
        "definition": "Problems concerning the selection, weighting, and rebalancing of financial "
                      "assets in a portfolio to maximise return, minimise risk, or satisfy "
                      "complex constraints. Includes mean-variance optimisation, index tracking, "
                      "factor investing, and multi-period rebalancing.",
        "scope_in": "Portfolio construction, asset allocation, diversification, index tracking, "
                    "factor models, ESG-constrained portfolios, multi-objective portfolio problems.",
        "scope_out": "General combinatorial optimisation not applied to portfolios; trading "
                     "execution (see PD-06).",
        "constituent_codes": [
            "portfolio-optimization", "mean-variance", "asset-allocation", "markowitz",
            "diversification", "index-tracking", "factor-investing", "combinatorial-optimization",
            "constraint-satisfaction"
        ],
    },
    {
        "name": "Derivative Pricing and Valuation",
        "key": "PD-02",
        "definition": "Problems related to computing the fair value of financial derivatives "
                      "including options, swaps, and structured products. Encompasses both "
                      "closed-form and simulation-based pricing methods.",
        "scope_in": "European/American/Asian/barrier option pricing, exotic derivatives, "
                    "interest rate derivatives, credit valuation adjustment (CVA/XVA), "
                    "Black-Scholes extensions, stochastic volatility models.",
        "scope_out": "Pure Monte Carlo methodology without a pricing context (see PD-09); "
                     "generic risk metrics (see PD-03).",
        "constituent_codes": [
            "derivative-pricing", "option-pricing", "european-options", "american-options",
            "asian-options", "barrier-options", "exotic-derivatives", "black-scholes",
            "interest-rate-derivatives", "swaps", "cva", "xva"
        ],
    },
    {
        "name": "Risk Management and Assessment",
        "key": "PD-03",
        "definition": "Problems involving the measurement, modelling, and mitigation of "
                      "financial risk. Includes market risk, credit risk, systemic risk, "
                      "and operational risk quantification.",
        "scope_in": "Value-at-Risk (VaR), Conditional VaR (CVaR), stress testing, "
                    "credit risk modelling, systemic risk analysis, counterparty risk, "
                    "tail risk estimation, risk aggregation.",
        "scope_out": "Credit scoring as a classification task (see PD-07); "
                     "derivative-specific risk measures tied to pricing (see PD-02).",
        "constituent_codes": [
            "risk-management", "value-at-risk", "cvar", "stress-testing",
            "market-risk", "credit-risk", "systemic-risk", "operational-risk",
            "tail-risk", "counterparty-risk", "risk-aggregation", "risk-analysis"
        ],
    },
    {
        "name": "Machine Learning and Pattern Recognition in Finance",
        "key": "PD-04",
        "definition": "Applications of quantum-enhanced machine learning techniques to "
                      "financial data analysis, including classification, regression, "
                      "forecasting, and natural language processing tasks.",
        "scope_in": "Time-series forecasting, return prediction, sentiment analysis, "
                    "financial NLP, clustering of market regimes, pattern recognition, "
                    "quantum-enhanced classification of financial data.",
        "scope_out": "ML used purely for fraud detection (see PD-05); "
                     "generic QML algorithm development without financial application.",
        "constituent_codes": [
            "machine-learning", "classification", "forecasting", "nlp-sentiment",
            "pattern-recognition", "regression", "clustering"
        ],
    },
    {
        "name": "Fraud Detection and Anomaly Detection",
        "key": "PD-05",
        "definition": "Problems concerning the identification of fraudulent transactions, "
                      "money laundering activity, and other financial anomalies.",
        "scope_in": "Anti-money laundering (AML), transaction monitoring, "
                    "anomaly detection in financial networks, Know-Your-Customer (KYC).",
        "scope_out": "General anomaly detection outside finance; "
                     "cybersecurity threats (see PD-08).",
        "constituent_codes": [
            "fraud-detection", "aml", "transaction-monitoring", "anomaly-detection"
        ],
    },
    {
        "name": "Trading and Market Microstructure",
        "key": "PD-06",
        "definition": "Problems related to trade execution, market making, arbitrage, "
                      "and the design of trading strategies.",
        "scope_in": "Algorithmic trading, optimal execution, arbitrage detection, "
                    "high-frequency trading, market microstructure, order routing.",
        "scope_out": "Portfolio-level allocation decisions (see PD-01); "
                     "return prediction (see PD-04).",
        "constituent_codes": [
            "trading", "arbitrage", "high-frequency-trading",
            "market-microstructure", "order-execution"
        ],
    },
    {
        "name": "Credit Scoring and Lending",
        "key": "PD-07",
        "definition": "Classification and scoring problems in the credit domain, "
                      "including default prediction and lending decisions.",
        "scope_in": "Credit scoring models, default prediction, loan approval, "
                    "creditworthiness assessment.",
        "scope_out": "Credit risk as a risk management aggregate (see PD-03); "
                     "fraud in lending (see PD-05).",
        "constituent_codes": [
            "credit-scoring", "default-prediction", "credit-lending"
        ],
    },
    {
        "name": "Cryptography and Financial Security",
        "key": "PD-08",
        "definition": "Security problems arising from quantum computing capabilities, "
                      "including threats to existing cryptographic systems and "
                      "quantum-safe alternatives.",
        "scope_in": "Quantum key distribution (QKD), post-quantum cryptography, "
                    "threats to RSA/ECC, cybersecurity in financial infrastructure.",
        "scope_out": "Non-financial cryptographic applications; "
                     "quantum computing hardware security.",
        "constituent_codes": [
            "quantum-cryptography", "post-quantum", "cybersecurity",
            "classical-crypto-vulnerability"
        ],
    },
    {
        "name": "Simulation and Monte Carlo Methods",
        "key": "PD-09",
        "definition": "General simulation problems in finance, particularly "
                      "Monte Carlo integration and stochastic process simulation.",
        "scope_in": "Monte Carlo integration, stochastic simulation, path simulation, "
                    "random walk models, quantum simulation of financial processes.",
        "scope_out": "Monte Carlo specifically for option pricing (see PD-02); "
                     "Monte Carlo for VaR estimation (see PD-03).",
        "constituent_codes": [
            "monte-carlo-simulation", "stochastic-simulation", "path-simulation",
            "random-walk", "quantum-simulation"
        ],
    },
    {
        "name": "Insurance and Actuarial Science",
        "key": "PD-10",
        "definition": "Problems specific to the insurance industry including "
                      "premium calculation, claims modelling, and underwriting.",
        "scope_in": "Insurance pricing, actuarial models, underwriting optimisation, "
                    "claims prediction.",
        "scope_out": "General risk management not specific to insurance (see PD-03).",
        "constituent_codes": [
            "insurance-actuarial"
        ],
    },
]

SOLUTION_TAXONOMY = [
    {
        "name": "Quantum Annealing and QUBO Formulations",
        "key": "SA-01",
        "definition": "Approaches that solve optimisation problems by encoding them as "
                      "Quadratic Unconstrained Binary Optimisation (QUBO) or Ising models "
                      "and solving via quantum annealing hardware (e.g., D-Wave) or "
                      "adiabatic quantum computing.",
        "scope_in": "Quantum annealing, D-Wave implementations, QUBO formulations, "
                    "Ising model encodings, simulated annealing benchmarks, "
                    "adiabatic quantum computing.",
        "scope_out": "Gate-based variational approaches (see SA-02); "
                     "classical simulated annealing without quantum comparison.",
        "constituent_codes": [
            "quantum-annealing", "d-wave", "qubo-formulation",
            "ising-model", "simulated-annealing", "adiabatic-quantum-computing"
        ],
    },
    {
        "name": "Variational and NISQ Algorithms",
        "key": "SA-02",
        "definition": "Gate-based quantum algorithms that use parameterised circuits "
                      "optimised by a classical outer loop. Designed for near-term "
                      "noisy intermediate-scale quantum (NISQ) devices.",
        "scope_in": "QAOA, VQE, variational quantum algorithms, parameterised circuits, "
                    "NISQ-specific algorithm design.",
        "scope_out": "Variational QML models (see SA-04); "
                     "fault-tolerant algorithms (see SA-03, SA-05, SA-06).",
        "constituent_codes": [
            "qaoa", "vqe", "variational-algorithm",
            "parameterized-circuits", "nisq"
        ],
    },
    {
        "name": "Quantum Amplitude Estimation and Monte Carlo Integration",
        "key": "SA-03",
        "definition": "Algorithms based on quantum amplitude estimation (QAE) that "
                      "provide quadratic speedups for Monte Carlo integration tasks. "
                      "Core primitive for derivative pricing and risk computation.",
        "scope_in": "Quantum amplitude estimation, quantum Monte Carlo integration (QMCI), "
                    "amplitude amplification, quantum counting, quantum sampling.",
        "scope_out": "Grover search for database tasks (see SA-05); "
                     "generic circuit constructions.",
        "constituent_codes": [
            "quantum-amplitude-estimation", "quantum-monte-carlo-integration",
            "amplitude-amplification", "quantum-counting", "quantum-sampling"
        ],
    },
    {
        "name": "Quantum Machine Learning",
        "key": "SA-04",
        "definition": "Quantum algorithms for machine learning tasks including classification, "
                      "regression, generative modelling, and dimensionality reduction. "
                      "Includes both gate-based and kernel-based approaches.",
        "scope_in": "Quantum neural networks (QNN), quantum SVM (QSVM), quantum kernel methods, "
                    "quantum Boltzmann machines, quantum GANs, quantum autoencoders, "
                    "quantum transfer learning, quantum reservoir computing, quantum PCA, "
                    "quantum feature maps, quantum reinforcement learning.",
        "scope_out": "Classical ML with quantum data encoding only; "
                     "variational algorithms for optimisation (see SA-02).",
        "constituent_codes": [
            "quantum-neural-network", "quantum-svm", "quantum-kernel-methods",
            "quantum-machine-learning", "quantum-classification",
            "quantum-reinforcement-learning", "quantum-boltzmann-machine",
            "quantum-generative-model", "quantum-transfer-learning",
            "quantum-feature-map", "quantum-reservoir-computing",
            "quantum-autoencoder", "quantum-pca"
        ],
    },
    {
        "name": "Grover's Search and Variants",
        "key": "SA-05",
        "definition": "Algorithms based on Grover's search providing quadratic speedup "
                      "for unstructured search problems. Includes variants and "
                      "applications to combinatorial search in finance.",
        "scope_in": "Grover's algorithm, quantum search, unstructured database search "
                    "applied to financial problems.",
        "scope_out": "Amplitude estimation (see SA-03); "
                     "quantum walk-based search (see SA-07).",
        "constituent_codes": [
            "grover-search", "quantum-search"
        ],
    },
    {
        "name": "Quantum Linear Systems (HHL and Extensions)",
        "key": "SA-06",
        "definition": "Algorithms for solving linear systems of equations on quantum computers, "
                      "based on the HHL algorithm and its extensions.",
        "scope_in": "HHL algorithm, quantum linear systems algorithms, "
                    "quantum matrix operations, quantum linear algebra.",
        "scope_out": "Quantum PCA (see SA-04); "
                     "classical linear algebra acceleration.",
        "constituent_codes": [
            "hhl-algorithm", "quantum-linear-systems", "quantum-linear-algebra"
        ],
    },
    {
        "name": "Quantum Walks",
        "key": "SA-07",
        "definition": "Algorithms based on quantum walks on graphs, with applications "
                      "to search, sampling, and financial network analysis.",
        "scope_in": "Discrete and continuous quantum walks, graph-based quantum algorithms.",
        "scope_out": "Classical random walks (problem domain, not solution).",
        "constituent_codes": [
            "quantum-walk"
        ],
    },
    {
        "name": "Hybrid Quantum-Classical Approaches",
        "key": "SA-08",
        "definition": "Architectural patterns that integrate quantum subroutines within "
                      "larger classical computation pipelines. Cross-cuts other solution "
                      "categories as an integration paradigm.",
        "scope_in": "Hybrid QPU-CPU workflows, classical pre/post-processing, "
                    "quantum-classical feedback loops, divide-and-conquer decomposition.",
        "scope_out": "Variational algorithms are inherently hybrid but classified under SA-02; "
                     "this category captures the integration architecture rather than the algorithm.",
        "constituent_codes": [
            "hybrid-quantum-classical"
        ],
    },
    {
        "name": "Quantum Cryptography and Post-Quantum Security",
        "key": "SA-09",
        "definition": "Quantum-based security solutions and post-quantum cryptographic "
                      "protocols relevant to financial infrastructure.",
        "scope_in": "Quantum key distribution (QKD), post-quantum cryptographic algorithms, "
                    "Shor's algorithm (as a threat), quantum-safe protocols.",
        "scope_out": "Cryptographic problems framed as threats to finance (see PD-08); "
                     "this category covers the solutions/responses.",
        "constituent_codes": [
            "quantum-key-distribution", "post-quantum-cryptography", "shor-algorithm"
        ],
    },
    {
        "name": "Quantum Fourier Transform and Phase Estimation",
        "key": "SA-10",
        "definition": "Primitive quantum subroutines (QFT, QPE) that underpin many "
                      "higher-level algorithms. Included as a solution category because "
                      "several papers discuss their direct application to finance.",
        "scope_in": "Quantum Fourier transform, quantum phase estimation, "
                    "applications to period finding and eigenvalue estimation in finance.",
        "scope_out": "When used only as a subroutine within HHL (see SA-06) or QAE (see SA-03).",
        "constituent_codes": [
            "quantum-fourier-transform", "quantum-phase-estimation"
        ],
    },
    {
        "name": "Error Mitigation and Fault Tolerance",
        "key": "SA-11",
        "definition": "Techniques for managing noise and errors in quantum computations, "
                      "including error mitigation for NISQ and full error correction for "
                      "fault-tolerant systems.",
        "scope_in": "Error mitigation techniques, fault-tolerant quantum computing, "
                    "quantum error correction, noise-aware algorithm design.",
        "scope_out": "Hardware-level discussions without algorithmic implication.",
        "constituent_codes": [
            "error-mitigation", "fault-tolerant"
        ],
    },
]


def load_review_data():
    with open(REVIEW_DATA, "r", encoding="utf-8") as f:
        return json.load(f)


def aggregate_codes(data):
    """Step 5: Aggregate all codes across accepted entries."""
    problem_codes = Counter()
    solution_codes = Counter()
    claim_codes = Counter()
    maturity_codes = Counter()
    question_codes = Counter()

    # Track which papers contribute to each code
    problem_papers = defaultdict(set)
    solution_papers = defaultdict(set)

    for paper in data["papers"]:
        pid = paper["id"]
        review = paper.get("_review", {})
        if review.get("status") == "exclude":
            continue

        for entry in paper.get("problem_domains", []):
            if entry.get("review", {}).get("decision") != "accept":
                continue
            for code in entry.get("codes", []):
                problem_codes[code] += 1
                problem_papers[code].add(pid)

        for entry in paper.get("solution_approaches", []):
            if entry.get("review", {}).get("decision") != "accept":
                continue
            for code in entry.get("codes", []):
                solution_codes[code] += 1
                solution_papers[code].add(pid)

        for entry in paper.get("key_claims", []):
            if entry.get("review", {}).get("decision") != "accept":
                continue
            for code in entry.get("codes", []):
                claim_codes[code] += 1

        for entry in paper.get("maturity_indicators", []):
            if entry.get("review", {}).get("decision") != "accept":
                continue
            for code in entry.get("codes", []):
                maturity_codes[code] += 1

    return {
        "problem_codes": problem_codes,
        "solution_codes": solution_codes,
        "claim_codes": claim_codes,
        "maturity_codes": maturity_codes,
        "problem_papers": problem_papers,
        "solution_papers": solution_papers,
    }


def count_papers_per_category(taxonomy, papers_map):
    """Count how many unique papers contribute to each taxonomy category."""
    for cat in taxonomy:
        cat_papers = set()
        for code in cat["constituent_codes"]:
            cat_papers.update(papers_map.get(code, set()))
        cat["paper_count"] = len(cat_papers)
        cat["contributing_papers"] = sorted(cat_papers)
    return taxonomy


def build_problem_solution_matrix(data):
    """Build a mapping matrix: which solution families are applied to which problem families."""
    matrix = defaultdict(lambda: defaultdict(int))

    for paper in data["papers"]:
        if paper.get("_review", {}).get("status") == "exclude":
            continue
        for mapping in paper.get("problem_solution_mappings", []):
            if mapping.get("review", {}).get("decision") != "accept":
                continue
            p_codes = mapping.get("codes", [])
            # Find which problem and solution categories these codes belong to
            p_cats = set()
            s_cats = set()
            for pc in PROBLEM_TAXONOMY:
                if any(c in pc["constituent_codes"] for c in p_codes):
                    p_cats.add(pc["key"])
            for sc in SOLUTION_TAXONOMY:
                if any(c in sc["constituent_codes"] for c in p_codes):
                    s_cats.add(sc["key"])
            for p in p_cats:
                for s in s_cats:
                    matrix[p][s] += 1

    return matrix


def write_problem_space_md(taxonomy, agg):
    """Write problem-space.md taxonomy file."""
    lines = [
        "# Problem-Space Taxonomy",
        "",
        "_Produced during Phase 1 — Framework Synthesis (Inductive Content Analysis)_",
        f"_Date: 2026-04-11 | Method: Elo & Kyngäs (2008) inductive process_",
        "",
        "## Overview",
        "",
        f"The problem-space taxonomy comprises **{len(taxonomy)} categories** derived from "
        f"inductive open coding of {sum(1 for p in agg['problem_papers'].values() for _ in p)} "
        f"accepted problem-domain entries across the Phase 1 exploratory corpus.",
        "",
        "Each category was constructed bottom-up: open codes were assigned to individual "
        "extraction entries, codes were aggregated across papers, and categories were formed "
        "by grouping semantically related codes. Category boundaries were drawn to maintain "
        "mutual exclusivity where possible, with scope notes clarifying edge cases.",
        "",
        "---",
        "",
    ]

    for cat in taxonomy:
        lines.extend([
            f"## {cat['key']}: {cat['name']}",
            "",
            f"**Definition:** {cat['definition']}",
            "",
            f"**Scope (included):** {cat['scope_in']}",
            "",
            f"**Scope (excluded):** {cat['scope_out']}",
            "",
            f"**Papers contributing:** {cat['paper_count']}",
            "",
            "**Constituent codes:**",
        ])
        for code in cat["constituent_codes"]:
            count = agg["problem_codes"].get(code, 0)
            n_papers = len(agg["problem_papers"].get(code, set()))
            lines.append(f"- `{code}` — {count} entries across {n_papers} papers")
        lines.append("")

        if cat.get("contributing_papers"):
            lines.append("**Contributing papers:**")
            for pid in cat["contributing_papers"]:
                lines.append(f"- {pid}")
            lines.append("")

        lines.append("---")
        lines.append("")

    path = TAXONOMY_DIR / "problem-space.md"
    path.write_text("\n".join(lines), encoding="utf-8")
    print(f"  Written: {path}")


def write_solution_space_md(taxonomy, agg):
    """Write solution-space.md taxonomy file."""
    lines = [
        "# Solution-Space Taxonomy",
        "",
        "_Produced during Phase 1 — Framework Synthesis (Inductive Content Analysis)_",
        f"_Date: 2026-04-11 | Method: Elo & Kyngäs (2008) inductive process_",
        "",
        "## Overview",
        "",
        f"The solution-space taxonomy comprises **{len(taxonomy)} categories** derived from "
        f"inductive open coding of accepted solution-approach entries across the Phase 1 "
        f"exploratory corpus.",
        "",
        "Each category represents a family of quantum or quantum-inspired algorithmic "
        "approaches applied to financial problems. Categories were formed by grouping "
        "semantically related open codes, with attention to both algorithmic similarity "
        "and hardware/paradigm distinctions (annealing vs. gate-based, NISQ vs. fault-tolerant).",
        "",
        "---",
        "",
    ]

    for cat in taxonomy:
        lines.extend([
            f"## {cat['key']}: {cat['name']}",
            "",
            f"**Definition:** {cat['definition']}",
            "",
            f"**Scope (included):** {cat['scope_in']}",
            "",
            f"**Scope (excluded):** {cat['scope_out']}",
            "",
            f"**Papers contributing:** {cat['paper_count']}",
            "",
            "**Constituent codes:**",
        ])
        for code in cat["constituent_codes"]:
            count = agg["solution_codes"].get(code, 0)
            n_papers = len(agg["solution_papers"].get(code, set()))
            lines.append(f"- `{code}` — {count} entries across {n_papers} papers")
        lines.append("")

        if cat.get("contributing_papers"):
            lines.append("**Contributing papers:**")
            for pid in cat["contributing_papers"]:
                lines.append(f"- {pid}")
            lines.append("")

        lines.append("---")
        lines.append("")

    path = TAXONOMY_DIR / "solution-space.md"
    path.write_text("\n".join(lines), encoding="utf-8")
    print(f"  Written: {path}")


def write_codebook_md(p_tax, s_tax):
    """Write codebook.md for Phase 2 classification."""
    lines = [
        "# Phase 2 Classification Codebook",
        "",
        "_Derived from Phase 1 Framework Synthesis — 2026-04-11_",
        "",
        "## Purpose",
        "",
        "This codebook provides structured classification codes for deductively tagging "
        "papers in Phase 2 (Systematic Identification and Classification). Each paper in the "
        "Phase 2 corpus should be tagged with **one or more problem-space categories** and "
        "**one or more solution-space categories** from the taxonomies below.",
        "",
        "## Instructions for Classifiers",
        "",
        "1. Read the paper's abstract, introduction, and methodology sections.",
        "2. Identify which **financial problem(s)** the paper addresses.",
        "3. Assign one or more problem-space codes (PD-01 through PD-10).",
        "4. Identify which **quantum solution approach(es)** the paper uses or proposes.",
        "5. Assign one or more solution-space codes (SA-01 through SA-11).",
        "6. If a paper does not clearly fit any category, flag for manual review.",
        "7. Multi-tagging is expected — many papers span multiple categories.",
        "",
        "---",
        "",
        "## Problem-Space Codes",
        "",
        "| Code | Category | Definition |",
        "|------|----------|------------|",
    ]

    for cat in p_tax:
        lines.append(f"| {cat['key']} | {cat['name']} | {cat['definition'][:120]}... |")

    lines.extend([
        "",
        "### Detailed Problem-Space Definitions",
        "",
    ])
    for cat in p_tax:
        lines.extend([
            f"#### {cat['key']}: {cat['name']}",
            "",
            f"**Definition:** {cat['definition']}",
            "",
            f"**Include:** {cat['scope_in']}",
            "",
            f"**Exclude:** {cat['scope_out']}",
            "",
        ])

    lines.extend([
        "---",
        "",
        "## Solution-Space Codes",
        "",
        "| Code | Category | Definition |",
        "|------|----------|------------|",
    ])

    for cat in s_tax:
        lines.append(f"| {cat['key']} | {cat['name']} | {cat['definition'][:120]}... |")

    lines.extend([
        "",
        "### Detailed Solution-Space Definitions",
        "",
    ])
    for cat in s_tax:
        lines.extend([
            f"#### {cat['key']}: {cat['name']}",
            "",
            f"**Definition:** {cat['definition']}",
            "",
            f"**Include:** {cat['scope_in']}",
            "",
            f"**Exclude:** {cat['scope_out']}",
            "",
        ])

    path = OUTPUTS_DIR / "codebook.md"
    path.write_text("\n".join(lines), encoding="utf-8")
    print(f"  Written: {path}")


def write_conceptual_framework_md(p_tax, s_tax, matrix):
    """Write conceptual-framework.md with problem×solution matrix."""
    lines = [
        "# Conceptual Framework: Quantum Computing in Financial Services",
        "",
        "_Phase 1 output — Framework Synthesis (Inductive Content Analysis)_",
        f"_Date: 2026-04-11_",
        "",
        "## Overview",
        "",
        "This conceptual framework organises the landscape of quantum computing in finance "
        "along two orthogonal dimensions:",
        "",
        "1. **Problem space** — the financial problems being targeted (10 categories)",
        "2. **Solution space** — the quantum/hybrid approaches being applied (11 categories)",
        "",
        "The framework was constructed inductively through open coding of an exploratory "
        "corpus of academic papers and industry reports. It provides the classification "
        "structure for Phase 2 (Systematic Identification and Classification) and defines "
        "the silo boundaries for Phase 3 (Thematic Synthesis).",
        "",
        "---",
        "",
        "## Problem-Space Taxonomy (10 categories)",
        "",
        "| Code | Category | Papers |",
        "|------|----------|--------|",
    ]
    for cat in p_tax:
        lines.append(f"| {cat['key']} | {cat['name']} | {cat.get('paper_count', 0)} |")

    lines.extend([
        "",
        "## Solution-Space Taxonomy (11 categories)",
        "",
        "| Code | Category | Papers |",
        "|------|----------|--------|",
    ])
    for cat in s_tax:
        lines.append(f"| {cat['key']} | {cat['name']} | {cat.get('paper_count', 0)} |")

    lines.extend([
        "",
        "## Problem × Solution Mapping Matrix",
        "",
        "The following matrix shows the density of problem–solution connections "
        "identified in the exploratory corpus. Cells indicate the number of "
        "explicit mappings found.",
        "",
    ])

    # Build matrix header
    s_keys = [s["key"] for s in s_tax]
    header = "| | " + " | ".join(s_keys) + " |"
    separator = "|---|" + "|".join(["---"] * len(s_keys)) + "|"
    lines.append(header)
    lines.append(separator)

    for pc in p_tax:
        row = f"| **{pc['key']}** |"
        for sk in s_keys:
            count = matrix.get(pc["key"], {}).get(sk, 0)
            cell = str(count) if count > 0 else "·"
            row += f" {cell} |"
        lines.append(row)

    lines.extend([
        "",
        "## Downstream Dependencies",
        "",
        "- **Phase 2** uses this framework as the deductive classification scheme. "
        "The codebook (`codebook.md`) operationalises the taxonomy for systematic coding.",
        "- **Phase 3** uses problem-space categories as silo boundaries for within-silo "
        "thematic synthesis.",
        "- **Background chapter** (Chapter 2) presents this framework narratively, "
        "integrating the taxonomy within the literature review.",
        "",
        "---",
        "",
        "_Produced by LLM-assisted inductive content analysis. All final categorisation "
        "decisions subject to researcher review per the Phase 1 design principle._",
    ])

    path = OUTPUTS_DIR / "conceptual-framework.md"
    path.write_text("\n".join(lines), encoding="utf-8")
    print(f"  Written: {path}")


def write_audit_trail(p_tax, s_tax, agg):
    """Update audit-trail.md with taxonomy construction decisions."""
    lines = [
        "# Phase 1 Audit Trail",
        "",
        "Log of LLM proposals vs. researcher decisions. Each entry records what the "
        "LLM suggested and what was accepted, modified, or rejected.",
        "",
        "---",
        "",
        "## Entry 1: Paper-Level Quality Triage (2026-04-11)",
        "",
        "**Action:** LLM-assisted assessment of 29 extraction files for inclusion in "
        "the Phase 1 framework synthesis corpus.",
        "",
        "**LLM proposal:**",
        "- 19 papers marked as `verified` (taxonomy building quality)",
        "- 3 papers marked as `needs-recheck` (limited depth or off-topic elements)",
        "- 7 papers marked as `exclude` (generic QC intros, toy models, no finance substance)",
        "",
        "**Excluded papers and reasons:**",
    ]

    # List excluded papers from the data
    excluded = [
        ("2022_Khari_Quantum_Computing", "Misidentified paper (CryptoQNet); narrow crypto-only scope"),
        ("2024_Pasupuleti_Advancements_Quantum_Computing_Information", "Generic QC overview, no finance content"),
        ("2024_Singh_Challenges_Opportunities_Quantum_Computing", "Multi-sector overview, finance superficial"),
        ("2024_VenkataRamana_Fundamentals_Quantum_Computing_Principles", "Introductory QC fundamentals only"),
        ("2025_Chawla_Quantum_Computing_Underlying_Principle", "Beginner QC overview, no finance analysis"),
        ("2026_Dumba_Quantum_Thinking_Finance", "Quantum-inspired metaphor, not actual QC algorithms"),
        ("2026_RejinaPV_Quantum_Computing_Beginner_S", "Beginner's guide, no finance-specific content"),
    ]
    for pid, reason in excluded:
        lines.append(f"- `{pid}`: {reason}")

    lines.extend([
        "",
        "**Researcher decision:** PENDING REVIEW — researcher should verify exclusion "
        "decisions and adjust if any excluded paper contains relevant framework material.",
        "",
        "---",
        "",
        "## Entry 2: Problem-Space Taxonomy Construction (2026-04-11)",
        "",
        "**Action:** LLM proposed 10 problem-space categories from aggregated open codes.",
        "",
        "**LLM proposal:**",
    ])

    for cat in p_tax:
        lines.append(f"- **{cat['key']}: {cat['name']}** — "
                      f"{cat.get('paper_count', 0)} papers, "
                      f"{len(cat['constituent_codes'])} codes")

    lines.extend([
        "",
        "**Key design decisions:**",
        "- Separated portfolio optimisation (PD-01) from trading execution (PD-06) to "
        "reflect distinct computational structures (static allocation vs. dynamic execution).",
        "- Separated derivative pricing (PD-02) from general simulation/MC (PD-09) to "
        "align with financial domain boundaries rather than algorithmic similarity.",
        "- Risk management (PD-03) excludes credit scoring (PD-07) — credit scoring is "
        "treated as a classification problem, while risk management covers aggregate measures.",
        "- Cryptography (PD-08) included as a problem domain because the literature treats "
        "quantum threats to financial infrastructure as a distinct research area.",
        "- Insurance/actuarial (PD-10) retained despite low paper count because it is "
        "a distinct financial domain with specific modelling requirements.",
        "",
        "**Researcher decision:** PENDING REVIEW — verify category boundaries, "
        "check for missing categories, assess whether PD-10 (Insurance) should be merged "
        "with PD-03 (Risk Management) given low evidence.",
        "",
        "---",
        "",
        "## Entry 3: Solution-Space Taxonomy Construction (2026-04-11)",
        "",
        "**Action:** LLM proposed 11 solution-space categories from aggregated open codes.",
        "",
        "**LLM proposal:**",
    ])

    for cat in s_tax:
        lines.append(f"- **{cat['key']}: {cat['name']}** — "
                      f"{cat.get('paper_count', 0)} papers, "
                      f"{len(cat['constituent_codes'])} codes")

    lines.extend([
        "",
        "**Key design decisions:**",
        "- Separated quantum annealing (SA-01) from gate-based variational (SA-02) to "
        "reflect fundamentally different hardware paradigms.",
        "- QAE/QMCI (SA-03) given its own category rather than being subsumed under "
        "amplitude amplification because it is the dominant approach for pricing and risk.",
        "- QML (SA-04) covers all ML-adjacent quantum algorithms; variational algorithms "
        "used for optimisation go under SA-02.",
        "- Hybrid quantum-classical (SA-08) is an integration pattern that cross-cuts "
        "other categories — it captures architectural choices rather than specific algorithms.",
        "- Error mitigation/fault tolerance (SA-11) included because several papers focus "
        "specifically on making financial computations viable under noise constraints.",
        "- QFT/QPE (SA-10) included as a separate category because some papers discuss "
        "their direct financial applications beyond being subroutines.",
        "",
        "**Researcher decision:** PENDING REVIEW — verify solution categories, "
        "assess whether SA-10 (QFT/QPE) should be absorbed into SA-03 or SA-06, "
        "and whether SA-07 (Quantum Walks) has sufficient evidence to stand alone.",
        "",
        "---",
        "",
        "## Entry 4: Open Coding Scheme (2026-04-11)",
        "",
        "**Action:** LLM applied regex-based inductive coding to all accepted entries.",
        "",
        f"**Unique problem codes generated:** {len(agg['problem_codes'])}",
        f"**Unique solution codes generated:** {len(agg['solution_codes'])}",
        f"**Unique claim codes generated:** {len(agg['claim_codes'])}",
        "",
        "**Coding methodology:**",
        "- Codes were assigned by matching entry labels and descriptions against "
        "a vocabulary of domain-specific patterns.",
        "- Where no pattern matched, the entry label was normalised to a code.",
        "- Consistent codes were applied across papers for the same concept.",
        "",
        "**Researcher decision:** PENDING REVIEW — verify code assignments, "
        "merge synonymous codes, and flag codes that need splitting.",
        "",
        "---",
        "",
        "_End of current audit trail entries._",
    ])

    AUDIT_TRAIL.write_text("\n".join(lines), encoding="utf-8")
    print(f"  Written: {AUDIT_TRAIL}")


def main():
    print("=" * 70)
    print("Phase 1 — Steps 5-9: Taxonomy Construction")
    print("=" * 70)

    # Load data
    data = load_review_data()
    print(f"Loaded {len(data['papers'])} papers from review_data_done.json")

    # Step 5: Aggregate codes
    print("\n── Step 5: Aggregating codes ──")
    agg = aggregate_codes(data)
    print(f"  Problem codes: {len(agg['problem_codes'])} unique "
          f"({sum(agg['problem_codes'].values())} total)")
    print(f"  Solution codes: {len(agg['solution_codes'])} unique "
          f"({sum(agg['solution_codes'].values())} total)")
    print(f"  Claim codes: {len(agg['claim_codes'])} unique")

    # Top problem codes
    print("\n  Top 20 problem codes:")
    for code, count in agg["problem_codes"].most_common(20):
        n_papers = len(agg["problem_papers"].get(code, set()))
        print(f"    {code}: {count} entries, {n_papers} papers")

    # Top solution codes
    print("\n  Top 20 solution codes:")
    for code, count in agg["solution_codes"].most_common(20):
        n_papers = len(agg["solution_papers"].get(code, set()))
        print(f"    {code}: {count} entries, {n_papers} papers")

    # Steps 6-7: Build taxonomies with paper counts
    print("\n── Steps 6-7: Building taxonomies ──")
    p_tax = count_papers_per_category(PROBLEM_TAXONOMY, agg["problem_papers"])
    s_tax = count_papers_per_category(SOLUTION_TAXONOMY, agg["solution_papers"])

    for cat in p_tax:
        print(f"  {cat['key']}: {cat['name']} — {cat['paper_count']} papers")
    for cat in s_tax:
        print(f"  {cat['key']}: {cat['name']} — {cat['paper_count']} papers")

    # Build problem-solution matrix
    matrix = build_problem_solution_matrix(data)

    # Step 8: Write output files
    print("\n── Step 8: Writing taxonomy and output files ──")
    write_problem_space_md(p_tax, agg)
    write_solution_space_md(s_tax, agg)
    write_codebook_md(p_tax, s_tax)
    write_conceptual_framework_md(p_tax, s_tax, matrix)

    # Step 9: Update audit trail
    print("\n── Step 9: Updating audit trail ──")
    write_audit_trail(p_tax, s_tax, agg)

    print("\n" + "=" * 70)
    print("TAXONOMY CONSTRUCTION COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()
