# eviewed/ — R1 review dispositions for portfolio_optimization

Per-paper review dispositions from the R1 (round-one) memo review pass on the portfolio_optimization silo. Each 1_review_*.json file records, for one paper, the reviewer's verdict on the LLM-generated A1/A2/L3 codes and memos: accepted, accepted-with-edit, or rejected, with rationale.

| File pattern | Purpose |
|--------------|---------|
| 1_review_<paper_id>.json | Reviewer's per-paper verdict + rationale + edited-memo (if any). |
| 1_review_<paper_id>.meta.json | Provenance: reviewer id, timestamp, A1/A2/L3 source manifest hashes. |

The aggregated cross-silo summary lives at [../../r1_review_summary.json](../../r1_review_summary.json).

See parent [../README.md](../README.md) for the S4 pipeline overview.
