# Phase 4 Documentation

This directory is the human-facing documentation layer for Phase 4. It explains the handoff architecture, reproducibility surface, and historical migration path that produced the current submission-ready package.

## Documents

| Document | Purpose |
|---|---|
| [ARCHITECTURE.md](ARCHITECTURE.md) | Current handoff architecture and folder responsibilities |
| [MIGRATION_PLAN.md](MIGRATION_PLAN.md) | Historical restructuring provenance; not an active task list |
| [../canonical/README.md](../canonical/README.md) | Active canonical pipeline map and current artifact inventory |
| [../canonical/PRE_REGISTRATION.md](../canonical/PRE_REGISTRATION.md) | Active canonical pre-registration contract |
| [../canonical/REPRODUCE.md](../canonical/REPRODUCE.md) | Current rebuild, audit, and release commands |
| [../canonical/THREATS_TO_VALIDITY.md](../canonical/THREATS_TO_VALIDITY.md) | Threats, mitigations, and residual risks |
| [../canonical/DECISIONS_LOG.md](../canonical/DECISIONS_LOG.md) | Dated operator decisions and methodological changes |

## Current Rule

The canonical documents remain in `../canonical/` because the active cohort, audits, and Phase 11 bundle reference those stable paths directly. Direct phase execution uses `../canonical/pipeline/`; direct audit execution uses `../canonical/audits/`.
