# Core Templates

Authoritative home for reusable Phase 4 circuit templates.

Use these templates through `p4_experiments.core.templates.*`.

## Claim Boundary

Templates in this namespace are reusable implementation scaffolds. They may be
used to build paper-family or proxy circuits, but they are not automatically
paper-exact implementations of the source literature.

A circuit should be treated as `paper-faithful-strict` only when its cohort row,
source audit, and manual review explicitly document that the implemented oracle,
data loading, objective, parameterization, and output contract match the paper.
Absent that evidence, template-based circuits should be reported as
`paper-family-template` or `proxy`, and manuscript claims should use the matching
claim scope.

## Minimum Template Metadata

New templates should make these assumptions easy to audit:

- Problem family and intended silo.
- Input data model and state-preparation assumptions.
- Oracle or ansatz abstraction used by the template.
- Output contract, such as state preparation, scalar observable, sample, or full
	classical vector.
- Known omissions relative to paper-specific algorithms.
- QDK/resource-estimator constraints that can make a cell fail or time out.