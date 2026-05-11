# Thesis Repository Architecture

This repository is organised as a clean thesis hand-in artifact. Its active structure has four research-phase folders plus shared contracts, examiner-facing documentation, verification tooling, and log/audit signposts. Local-only working material, source PDFs, high-volume raw evidence, raw model payloads, and non-final support material are stored in the external source archive listed in [README.md](../README.md).

## Reader Path

1. Start with [README.md](../README.md) for the hand-in boundary and verification commands.
2. Read [PIPELINE.md](PIPELINE.md) for the phase-by-phase flow.
3. Use [PROJECT_STATE.yaml](PROJECT_STATE.yaml) for machine-readable status and phase contracts.
4. Use [AUDIT_INDEX.md](AUDIT_INDEX.md) when a claim needs traceability to evidence.
5. Use [FREEZE.md](../FREEZE.md) and the per-folder `FREEZE.md` files for frozen numbers and claim limitations.

## Repository Tree

This tree shows the retained hand-in architecture at reviewer depth. It does not enumerate every generated paper-level file, and it omits ignored local/runtime folders such as `.venv/`, `__pycache__/`, `.pytest_cache/`, and `tools/rag/.chroma/`.

```text
QF_repo/
	README.md
	FREEZE.md
	CONTRIBUTING.md
	LICENSE
	pyproject.toml
	verify.ps1
	pre_zip_check.ps1
	.env.example
	.gitattributes
	.gitignore
	docs/
		README.md
		ARCHITECTURE.md
		AUDIT_INDEX.md
		METHODOLOGY_DESIGN.md
		PIPELINE.md
		PROJECT_STATE.yaml
		PROJECT_TIMELINE.md
	logs/
		README.md
	p1_framework_synthesis/
		README.md
		FREEZE.md
		audit-trail.md
		REVIEW_CHECKLIST.md
		prompts/
		s1_extractions/
		s2_coding/
		s3_taxonomy/
		s4_outputs/
			codebook.md
			conceptual-framework.md
			README.md
		scripts/
	p2_systematic_review/
		README.md
		FREEZE.md
		s1_slr/
		s2_classification/
		output/
			README.md
			audit/
			processed/
		scripts/
		tests/
	p3_thematic_synthesis/
		README.md
		FREEZE.md
		AUDIT_REPORT.md
		GL10_AUDIT.md
		P3_AUDIT_STATUS.md
		docs/
		output/
		problems/
		prompts/
		s1_silo_scoping/
		s2_quantitative/
			output/
		s3_quantum_advantage/
			combined/
				output/
		s4_thematic_coding/
		s5_cross_silo/
		s6_silo_framing/
		shared/
		scripts/
		tests/
	p4_experiments/
		README.md
		FREEZE.md
		canonical/
			cohort.json
			PRE_REGISTRATION.md
			REPRODUCE.md
			DECISIONS_LOG.md
			pipeline/
			outputs/
			reports/
			release/
				README.md
				zenodo_bundle.tar.gz
				zenodo_bundle.tar.gz.sha256
		common/
		core/
		docs/
		experiments/
		infra/
		prompts/
		scripts/
	shared/
		README.md
		FREEZE.md
		bridge/
		chapter_supporting_literature/
		config/
			schemas/
			silo_inclusion.json
			unified_taxonomy.json
		extracted_text/
		phase3/
		tests/
		tools/
		validate_taxonomy.py
	tools/
		README.md
		aggregate_audits.py
		regen_requirements_lock.ps1
		rag/
		verify/
			reports/
```

## Active Structure And Roles

| Area | Role | Reader Notes |
|---|---|---|
| Repository root | Submission boundary, freeze status, dependency metadata, and verification entry points. | Start with `README.md`, then use `FREEZE.md`, `pyproject.toml`, `verify.ps1`, and `pre_zip_check.ps1` as needed. |
| `docs/` | Examiner-facing navigation and project-state documentation. | Keep this folder small and navigational; detailed evidence is phase-local and indexed through `AUDIT_INDEX.md`. |
| `logs/` | Signpost for log and audit evidence. | `logs/README.md` explains that retained logs are mostly phase-local rather than copied into one root folder. |
| `p1_framework_synthesis/` | Builds the problem-domain and solution-approach taxonomy. | Use `s4_outputs/` for the final framework and codebook; `audit-trail.md` records researcher overrides and taxonomy decisions. |
| `p2_systematic_review/` | Search, screening, and deductive classification of the corpus. | `output/processed/` contains the retained per-paper traceability evidence; `output/audit/` and `s1_slr/` hold audit, protocol, and screening records. |
| `p3_thematic_synthesis/` | Silo scoping, quantitative extraction, quantum-advantage assessment, thematic coding, cross-silo synthesis, and finance framing. | S1-S5 are active thesis evidence. S6 is a descriptive sibling; active S3 claims should use the filtered files in `s3_quantum_advantage/combined/output/`. |
| `p4_experiments/` | Canonical experiment/resource-estimation pipeline and claim-boundary audits. | Use `FREEZE.md`, `canonical/REPRODUCE.md`, `canonical/cohort.json`, and `canonical/release/` first. `common/`, `core/`, `experiments/`, and `infra/` are supporting implementation layers. |
| `shared/` | Shared taxonomy, bridge files, schemas, extracted-text support, phase-3 support data, and reusable utilities. | `shared/config/` and `shared/bridge/` define cross-phase contracts; `shared/FREEZE.md` controls shared claim boundaries. |
| `tools/verify/` | Cross-phase verification scripts and generated verifier reports. | `verify.ps1` runs the current verification surface; detailed JSON outputs are retained in `tools/verify/reports/`. |
| `tools/rag/` | Local reviewer/research retrieval tooling. | The source files and manifest are retained; the regenerable vector store is ignored under `tools/rag/.chroma/`. |

## Phase Flow

The research pipeline is sequential, with shared configuration and bridge files enforcing cross-phase contracts:

```text
P1 framework synthesis
	-> shared taxonomy and codebook
P2 systematic review
	-> screened/classified corpus and post-classification audit records
P3 thematic synthesis
	-> active-silo synthesis, quantitative extraction, and quantum-advantage assessment
P4 experiments
	-> canonical resource-estimation cohort, audit reports, and release bundle
```

## Evidence Policy

The hand-in repository keeps current/canonical outputs, freeze records, audit indexes, verifier scripts, and the retained evidence needed for traceability. It excludes source-paper PDFs, full-text dumps, raw model payloads, raw request/response logs, local environments, caches, and noisy historical drafts.

Archived files are not deleted. They are recorded in `SOURCE_ARCHIVE_MANIFEST.csv` under the external archive root named in [README.md](../README.md).

Ignored or regenerated local folders may exist in a working copy, but they are not part of the hand-in architecture. Examples include `.venv/`, `__pycache__/`, `.pytest_cache/`, transient log files, and the local RAG vector store.

## Claim Boundary

The freeze records control all scientific claims. Do not update extracted data, classifications, experiment outputs, freeze numbers, or limitations during submission cleanup. Documentation edits should clarify navigation, evidence location, and repository structure only.