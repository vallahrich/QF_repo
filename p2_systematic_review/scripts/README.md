# `scripts/` — Phase 2 ad-hoc scripts

Top-level scripts that operate on the Phase 2 corpus but are not part of the canonical extraction pipeline (which lives under [`../s2_classification/scripts/`](../s2_classification/scripts/)).

## Subdirectories

| Folder | Contents |
|--------|----------|
| `triage/` | Post-classification triage utilities — flagging, re-running, and excluding likely off-scope papers. Drove the 22-paper exclusion in [`../output/audit/excluded_post_classification.csv`](../output/audit/excluded_post_classification.csv). See [`triage/README.md`](triage/README.md). |
