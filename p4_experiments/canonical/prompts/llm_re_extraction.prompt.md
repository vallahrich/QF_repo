# LLM Re-Extraction Prompt — Phase 3 (TODO → F or P)

> **Purpose.** Recover paper-stated circuit parameters that the manual
> Phase-1 read did not yield, using a reasoning LLM with structured
> output. Used in Phase 3 (PRE_REGISTRATION.md §5.3) to demote a TODO
> label to either Faithful (F) or Proxy-declared (P).
>
> **Determinism.** Single fixed model + temperature 0 + this prompt
> verbatim. The full prompt text and the LLM transcript are committed
> per-label as `<paper_dir>/llm_re_extraction.{prompt,response}.md`.
> The model identifier and version are recorded in
> `<paper_dir>/notes.md`.

---

## System message (verbatim)

```
You are an expert quantum-information researcher with deep knowledge of
quantum-finance algorithms (amplitude estimation, HHL, QSVM, QAOA,
amplitude encoding, Hamiltonian simulation, ansatz-style variational
circuits). You will read a quantum-finance paper and extract the
specific circuit parameters required to construct a paper-faithful
implementation.

You will reply ONLY in the structured JSON schema described in the
USER message. Do NOT include narrative outside the JSON. Do NOT
hallucinate values: every field MUST cite the page or section of the
paper where the value appears. If a field cannot be determined from
the paper or its supplementary materials, use the literal string
"NOT_STATED" and explain why in the "operator_notes" field of the
output.
```

## User message (template — fill `{{...}}` per label)

```
PAPER:
- title: {{paper_title}}
- authors: {{paper_authors}}
- year: {{paper_year}}
- doi: {{paper_doi}}
- arxiv_id: {{paper_arxiv_id}}
- silo: {{silo}}
- algorithm_family: {{algorithm_family}}
- experiment_id: {{experiment_id}}

PAPER FULL TEXT (PDF + supplementary, attached / inline):
{{paper_full_text}}

REQUIRED EXTRACTION:

Return a JSON object with this exact schema:

{
  "paper_id": "{{paper_id}}",
  "experiment_id": "{{experiment_id}}",
  "fidelity_assessment": "F" | "P",     // F if every required field below is recovered; P otherwise
  "circuit": {
    "num_qubits": <int> | "NOT_STATED",
    "ansatz_layers": <int> | "NOT_STATED",
    "depth_estimate": <int> | "NOT_STATED",
    "t_count_estimate": <int> | "NOT_STATED",
    "two_qubit_gate_count": <int> | "NOT_STATED",
    "encoding": "amplitude" | "basis" | "angle" | "QGAN" | "matrix-product" | "NOT_STATED",
    "ansatz_type": "RealAmplitudes" | "EfficientSU2" | "TwoLocal" | "custom" | "NOT_STATED",
    "oracle_structure": "amplitude_estimation" | "block_encoded_QSP" | "QROM" | "MCM" | "trivial" | "NOT_STATED",
    "measurement": "computational" | "X-basis" | "QPE" | "NOT_STATED"
  },
  "instance_parameters": {
    // Algorithm-family-specific params; see the schema in the codebase
    // for `instance.json["parameters"]`. Include every parameter the
    // paper states. Examples:
    //   amplitude-estimation:  S0, K, T, r, vol, num_eval_qubits, num_state_prep_qubits
    //   hhl:                   matrix_dim, condition_number, num_clock_qubits, eigenvalue_range
    //   quantum-svm:           feature_dim, num_qubits, kernel_circuit, num_train, num_test
    //   quantum-ml:            input_dim, num_qubits, ansatz_reps, observable
    //   qaoa:                  problem_size, p (depth), mixer, cost_hamiltonian
    //   vqe:                   ansatz, num_qubits, num_layers, observable
    "<param_name>": <value> | "NOT_STATED"
  },
  "classical_baseline": {
    "algorithm_label": "<short name>",
    "wall_clock_seconds": <float> | "NOT_STATED",
    "reported_complexity": "<O(...) string>" | "NOT_STATED",
    "source_section": "<paper section / page>"
  },
  "citations": {
    // For every numeric value above, the paper section/page where it appears.
    "num_qubits": "<page or section>",
    "ansatz_layers": "<page or section>",
    "...": "..."
  },
  "operator_notes": "<narrative explaining anything unusual: missing values, multiple stated alternatives, ambiguity, conflicts between main text and supplementary material, etc.>"
}
```

---

## Operator review protocol (after LLM response)

1. Read the LLM response. Verify every cited page/section in the paper.
2. If every required field is recovered AND citations are accurate,
   set `cohort.json[paper_id][experiment_id].fidelity = "F"` and proceed
   to Phase 2 (faithful circuit implementation).
3. Otherwise, set `cohort.json[paper_id][experiment_id].fidelity = "P"`,
   commit the LLM transcript at
   `<paper_dir>/llm_re_extraction.response.md`, and write
   `<paper_dir>/proxy_justification.md` documenting which fields could
   not be recovered and which template will be used (see Phase 4
   protocol in PRE_REGISTRATION.md §5.4).

The operator's verification step is non-negotiable: the LLM cannot
unilaterally promote a label to Faithful. The verification adds
operator initials and date to `<paper_dir>/notes.md`.
