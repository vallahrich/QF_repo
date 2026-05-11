# `p4_experiments/scripts/` — P4 audit scripts

Cross-cutting audit and reporting scripts for P4 (not pipeline phases —
those live under [`../canonical/pipeline/`](../canonical/pipeline/)).

| File | Purpose |
|------|---------|
| `audit_implementation_type.py` | Per-label implementation-tier audit (paper-faithful-strict / paper-family-template / proxy); writes `implementation_type_audit_report.json`. |
| `implementation_type_audit_report.json` | Output of `audit_implementation_type.py`. |

The canonical entrypoint to rebuild the P4 shortlist is
`python -m p4_experiments.core.build_p4_shortlist`.

See parent [`../README.md`](../README.md).