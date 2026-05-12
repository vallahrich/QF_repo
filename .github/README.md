# Skills Handover — AI-Use Disclosure Bundle

Companion bundle to the MSc thesis *Quantum Computing in Financial Services* (Copenhagen Business School, 2026). This folder contains the six Copilot **skills** (procedural prompt scaffolds) used during the research and write-up of Chapter 6 (per-silo synthesis) and surrounding work.

Skills are **prompt-level workflow definitions** invoked inside VS Code's GitHub Copilot Chat. They do not, on their own, make analytical decisions: every persisted output is researcher-authored and -approved. The skills exist to standardise *how* the LLM is invoked across repeated tasks (retrieval, review, audit), so that the AI's role is auditable rather than ad hoc.

## Cross-references in the thesis

- **Chapter 4 — Methodology, §4.7** (GenAI declaration): declares the use of LLM-assisted tooling for idea generation, conceptualisation, retrieval, and pipeline review.
- **Appendix — AI Use Declaration**: per-phase scope of LLM use.
- **Chapter 6 Annex (this bundle)**: lists the six skills, classifies them, and links to this folder in the external repository for full text.

## Classification

| Class | Skill | Role |
|---|---|---|
| Governance / self-audit | `methodology-guard` | Validates research-design integrity against the canonical methodology document |
| Governance / self-audit | `genai-compliance` | Audits LLM-assisted steps against the five CBS GenAI compliance pillars |
| Retrieval / workflow | `evidence-navigator` | Read-only retrieval of pipeline artefacts |
| Retrieval / workflow | `manual-review` | Capture-and-resolve workflow for PDF manuscript review notes |
| Retrieval / workflow | `p3-r1-review` | Per-paper triangulation scaffold for the P3/s4 R1 memo review |
| Analytical sparring | `research-sparring` | Conversational pre-writing partner; produces researcher-curated handoffs |

## Compliance posture

Each SKILL.md in this bundle has been reviewed for the published handover and reflects the following posture:

- **Researcher-authored decisions only.** No persisted artefact carries an LLM-generated verdict, score, or interpretive claim. Where skills surface orientation hints in chat, those hints are explicitly flagged as ephemeral and non-persistent.
- **No pre-baked answers.** Example prompts and questions in skill text are illustrative scaffolds, not pre-determined analytical outputs. The actual content of any analytical exchange is built live from the data and the researcher's input.
- **No analytical authority.** The most analytically-active skill in this bundle (`research-sparring`) explicitly declares its CBS §4.7 scope ("idea generation and conceptualisation") and operates under a hard rule that the researcher's interpretation always takes priority.

## Provenance

These skills were used by Aleix Telesforo (@TelesforoAleix) and Vallahrich (@vallahrich) during the 2026 thesis cycle. The live versions reside in `.github/skills/` of the project repository; this folder is a redacted snapshot for external publication alongside the thesis disclosure.

Date of snapshot: 2026-05-12.
