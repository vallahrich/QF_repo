---
name: evidence-navigator
description: "Find and surface relevant pipeline artifacts from any phase. Use when: searching for papers by topic/method/claim, retrieving silo data, checking what evidence exists for a specific argument, or exploring pipeline outputs before writing. Returns structured evidence packs with counts, findings, and gaps."
argument-hint: "Pass a natural-language query (e.g., 'VQE for portfolio optimization'), a PD/SA code (e.g., 'PD-01'), or 'inventory' for a full artifact scan"
---

# Evidence Navigator — Pipeline Artifact Retrieval

Retrieval-only skill for finding and surfacing relevant evidence from quantum-finance pipeline outputs. This is the data access workhorse — it finds what exists, translates between naming conventions, and presents structured evidence packs.

## When to Use

- "What papers discuss VQE for portfolio optimization?"
- "Show me the contradiction register for PD-03"
- "Which silos have completed B2 themes?"
- "What quantum advantage claims exist in derivative pricing?"
- "What data do I have for writing the PD-06 chapter?"
- Before invoking `research-sparring` — to understand what's available

## Scope Constraint

This skill does **retrieval and summarization only**. It does NOT:
- Interpret findings or propose arguments (use `research-sparring`)
- Write prose or LaTeX (use `academic-writer`)
- Grade or review (use `professor-review`)

## Procedure

### Step 1 — Parse the Query

Classify the search intent:

| Intent type | Examples | Search targets |
|------------|---------|----------------|
| By silo | "PD-01", "portfolio optimization" | All artifacts for that silo |
| By method | "SA-03", "QAOA", "VQE" | Papers with matching methodology_tags |
| By claim type | "quantum advantage", "limitation" | QA verdicts, contradiction registers |
| By artifact type | "themes", "memos", "contradictions" | Specific artifact class |
| Inventory | "what exists", "inventory" | Full artifact scan across all phases |

### Step 2 — Translate Codes

Use `shared/config/unified_taxonomy.json` to translate between:
- **PD codes** (PD-01) ↔ **topic tags** (portfolio-optimization) ↔ **folder names** (portfolio_optimization)
- **SA codes** (SA-03) ↔ **methodology tags** ↔ algorithm names

Common translations:
| Code | Tag | Folder | Common names |
|------|-----|--------|-------------|
| PD-01 | portfolio-optimization | portfolio_optimization | portfolios, asset allocation, MPT |
| PD-02 | derivative-pricing | derivative_pricing | options, derivatives, Black-Scholes |
| PD-03 | risk-management | risk_management | VaR, CVaR, stress testing, credit risk |
| PD-04 | quantum-ml-finance | quantum_ml_finance | QML, classification, forecasting |
| PD-05 | fraud-detection | fraud_detection | AML, anomaly detection |
| PD-06 | trading-execution | trading_execution | algorithmic trading, HFT |
| PD-07 | credit-lending | credit_lending | credit scoring, default prediction |
| PD-09 | simulation-monte-carlo | simulation_monte_carlo | Monte Carlo, QAE, amplitude estimation |
| PD-10 | insurance-actuarial | → merged into PD-03 | insurance, actuarial |

Note: PD-08 (cryptography-security) is excluded from P3 scope (QKD-dominated, out of gate-based scope).

### Step 3 — Search Artifacts

Search the canonical locations. For each, check existence before attempting to read:

**Phase 2 processed papers** (`p2_systematic_review/output/processed/`):
- 777 markdown files with YAML frontmatter
- Searchable fields: `topic_tags`, `methodology_tags`, `quantum_advantage_claim`, `evidence_type`, `paper_type`
- Use grep on frontmatter to filter

**Phase 3 coding artifacts** (`p3_thematic_synthesis/coding/{silo}/`):
- `codes/*.jsonl` — A1 open codes per paper
- `memos/*.json` — A2 compressed memos per paper
- `reviewed/*.json` — R1 approved memos per paper
- `themes.json` — B1/B2 silo-level themes
- `contradictions.jsonl` — A3 contradiction register
- `REVIEW_LOG.md` — researcher decision trail

**Phase 3 frozen outputs**:
- `p3_thematic_synthesis/quantitative/` — benchmark extractions (459 papers)
- `p3_thematic_synthesis/quantum_advantage/` — triangulation verdicts (1,185 experiments)

**Phase 3 cross-cutting**:
- `p3_thematic_synthesis/cross_cutting/` — cross-silo catalogues

**Silo problem configs**:
- `p3_thematic_synthesis/problems/{silo}/config.yaml` — silo scope and paper lists

**Phase 4**:
- `p4_experiments/` — experiment shortlists and results

### Step 4 — Present Evidence Pack

Format findings as a structured evidence pack:

```
## Evidence Pack: [query]

### Artifact Inventory
| Artifact | Status | Count/Path |
|----------|--------|------------|
| P2 processed papers | ✅ Available | N papers matching |
| P3 open codes | ✅/❌ | N files or "not yet generated" |
| P3 approved memos | ✅/❌ | N files or "not yet generated" |
| P3 silo themes | ✅/❌ | path or "not yet generated" |
| Contradiction register | ✅/❌ | N entries or "not yet generated" |
| Quantitative extractions | ✅ FROZEN | N papers in silo |
| QA triangulation verdicts | ✅ FROZEN | N experiments in silo |

### Matching Records (factual)
1. [paper_id, title, matching field — factual citation only, no interpretation]
2. [paper_id, title, matching field]
...

### Gaps & Missing Data
- [what doesn't exist yet]
- [what the researcher should be aware of]
```

### Step 5 — Offer Drill-Down

After presenting the evidence pack, offer:
- "Want me to show the full memo for paper X?"
- "Want me to list all contradictions in this silo?"
- "Want me to compare this across silos?"

## Invariants

1. **Never fabricate evidence.** If a file doesn't exist, say so explicitly.
2. **Never interpret.** Present data; let the researcher or `research-sparring` interpret.
3. **Always report gaps.** Missing artifacts are as important as present ones.
4. **Respect FROZEN status.** Quantitative and QA outputs are read-only.
