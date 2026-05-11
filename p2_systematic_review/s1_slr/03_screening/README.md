# `s1_slr/03_screening/` — Title/abstract screening artifacts

Inputs and outputs of the dual-coder screening stage (ASReview + LLM-assisted), including calibration, AI screening decisions, validation, and discrepancy resolution.

## Notable files

| File | Purpose |
|------|---------|
| `asreview_dataset.csv` / `asreview_prior_labels.csv` | ASReview input dataset and seed labels. |
| `calibration_*` | Two-coder calibration round artifacts (decisions, decisions log, source workbook). |
| `ai_screening_decisions.csv` | LLM-assisted screening decisions per record. |
| `ai_validation_report.md` | Validation of the LLM screener against human-coded validation set. |
| `ai_discrepancy_review.csv` / `ai_rescue_review.xlsx` | Human resolution of LLM/human disagreements and borderline rescues. |
| `exclusion_reason_codes.md` | Controlled vocabulary for exclusion reasons (PRISMA-aligned). |

> See [`../01_protocol/protocol.md`](../01_protocol/protocol.md) for the screening procedure.
