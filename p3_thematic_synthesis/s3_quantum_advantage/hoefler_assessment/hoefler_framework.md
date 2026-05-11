# Hoefler et al. (2023) — Precise Assessment Framework

**Reference:** Hoefler, T., Häner, T., & Troyer, M. (2023). Disentangling Hype from Practicality: On Realistically Achieving Quantum Advantage. *Communications of the ACM*, 66(5), 82–87. DOI: 10.1145/3571725

---

## 1. Comparison Setup (from the paper)

### Classical Baseline
- **Single NVIDIA A100-class chip**: 54.2 billion transistors, TSMC 7nm, 0.7ns cycle time
- **OR custom ASIC** with equivalent transistor budget (2–15× faster than GPU for specific operations)
- NOT a cluster, NOT multiple chips — a single chip manufactured with today's technology

### Quantum Computer (Optimistic Assumptions)
- **10,000 error-corrected logical qubits**
- **10 μs gate time** for logical operations
- **Simultaneous gate execution** on all qubits
- **All-to-all connectivity** for fault-tolerant two-qubit gates
- Note: "No quantum error correction scheme exists today that allows simultaneous execution of gates and all-to-all connectivity without at least O(√N) slowdown for N qubits" (footnote a)

### Key: These assumptions are deliberately optimistic for quantum, pessimistic for classical.

---

## 2. Performance Comparison (Table 1 — exact values)

| Metric | GPU (A100) | Custom ASIC | Future Quantum |
|---|---|---|---|
| **I/O Bandwidth** | 10,000 Gbit/s | 10,000 G/s | **1 Gbit/s** |
| **fp16 throughput** | 195 Top/s | 550 Top/s | **10.5 kop/s** |
| **int32 throughput** | 9.75 Top/s | 215 Top/s | **0.83 kop/s** |
| **binary (logical) throughput** | 4,992 Top/s | 77,000 Top/s | **235 kop/s** |

**Performance ratios (ASIC vs Quantum):**
- fp16: 550 Top/s ÷ 10.5 kop/s = **5.24 × 10^10**
- int32: 215 Top/s ÷ 0.83 kop/s = **2.59 × 10^11**
- binary: 77,000 Top/s ÷ 235 kop/s = **3.28 × 10^11**

**I/O ratio:** 10,000 Gbit/s ÷ 1 Gbit/s = **10,000×** slower for quantum

---

## 3. Crossover Analysis (Table 2 — exact values)

Maximum number of operations that can be afforded **per oracle call** for quantum to show advantage over classical within a runtime of 10^6 seconds (~2 weeks):

| Operation Type | Quadratic Speedup (k=2) | Cubic Speedup (k=3) | Quartic Speedup (k=4) |
|---|---|---|---|
| **fp16** | **0.2** | 45,800 | 2,800,000 |
| **int32** | **0.003** | 1,630 | 130,000 |
| **binary (logical)** | **68** | 12,500,000 | 712,000,000 |

### How to read this table:
- With **quadratic speedup** and fp16 operations: you can afford **less than 1 floating-point operation** per oracle call → impossible for any real computation
- With **quadratic speedup** and binary operations: you can afford **68 logic gates** per oracle call → insufficient for any non-trivial function
- With **cubic speedup** and binary: **12.5 million gates** → potentially feasible
- With **quartic speedup**: hundreds of millions of operations → feasible for complex oracles

### The crossover formula:

For polynomial speedup of order k (quantum needs N calls, classical needs N^k):

$$M_{max} = \frac{T_{budget}}{t_q} \cdot \left(\frac{t_c}{t_q}\right)^{\frac{1}{k-1}}$$

where:
- M_max = maximum operations per oracle call
- T_budget = 10^6 seconds (≈ 2 weeks)
- t_q = time per quantum operation (from Table 1)
- t_c = time per classical operation (from Table 1)

---

## 4. The Three Feasibility Tests

### Test 1: Speedup Order
- k = 1 (no speedup): **FAIL** — no advantage possible
- k = 2 (quadratic, e.g., Grover, QAE): **FAIL** — "quadratic speedups are insufficient for practical quantum advantage"
- k = 3 (cubic): **CONDITIONAL** — depends on oracle complexity
- k ≥ 4 (quartic+): **LIKELY PASS** — if oracle is not too complex
- Exponential (e.g., Shor's, quantum simulation): **PASS** — if I/O constraint met

### Test 2: Oracle Complexity
For the identified speedup order k, is the number of operations per oracle call M below Table 2 threshold?
- Determine operation type (fp16, int32, or binary)
- Look up M_max from Table 2 for the speedup order
- If M_reported > M_max: **FAIL** — oracle too complex for advantage within 2 weeks

### Test 3: I/O Constraint
- Quantum I/O bandwidth: 1 Gbit/s
- If the problem requires loading N_bits of classical data:
  - Loading time: N_bits / 10^9 seconds
  - If loading time > T_budget: **FAIL** — I/O bottleneck negates speedup
- "Quantum computers will be practical for 'big compute' problems on small data, not big data problems"
- Database search, loading full matrices, reading full solution vectors → all I/O limited

---

## 5. Conclusions from the Paper (Direct Quotes)

1. "Quadratic speedups are insufficient for practical quantum advantage" (p. 85)
2. "At least cubic or quartic speedups are required for a practical quantum advantage" (p. 85)
3. "The most promising candidates for quantum practicality are small-data problems with exponential speedup" (p. 85)
4. "Quantum computers will be practical for 'big compute' problems on small data, not big data problems" (p. 83)
5. "These conclusions will remain valid even with significant advances in quantum technology of multiple orders of magnitude" (p. 85)

### Application-Specific Verdicts from the Paper:
- **Cryptanalysis (Shor's)**: Exponential speedup → **PROMISING**
- **Chemistry / materials science**: Exponential speedup for quantum simulation → **MOST PROMISING**
- **Machine learning training**: Quadratic speedup → **UNLIKELY**
- **Monte Carlo / quantum walks**: Quadratic speedup → **UNLIKELY**
- **Database search (Grover)**: Quadratic + I/O limited → **UNLIKELY**
- **Linear systems (HHL)**: Exponential but I/O limited → **UNLIKELY** (unless matrix is computable from small data)
- **Fluid dynamics / weather**: Quadratic → **UNLIKELY**
- **Drug design / protein folding**: Quadratic (Grover) → **UNLIKELY**

---

## 6. Implications for Quantum Finance (Our Assessment)

Based on the Hoefler thresholds, most quantum finance approaches face fundamental barriers:

| Finance Application | Typical Algorithm | Speedup Order | Hoefler Verdict | Why |
|---|---|---|---|---|
| Portfolio optimization (QAOA) | QAOA/VQE | None proven asymptotic | **FAIL** | No proven speedup over classical solvers like Gurobi |
| Portfolio optimization (QUBO/annealing) | Quantum annealing | None proven | **FAIL** | Heuristic, no proven speedup |
| Derivative pricing (QAE) | Amplitude estimation | Quadratic (k=2) | **FAIL** | Quadratic insufficient per Table 2 |
| Risk management (QAE) | Amplitude estimation | Quadratic (k=2) | **FAIL** | Same |
| Monte Carlo integration | Quantum walk / QAE | Quadratic (k=2) | **FAIL** | Same |
| ML classification (QML) | QSVM, QNN | None proven | **FAIL** | No proven asymptotic speedup |
| Fraud detection (QML) | QSVM, QNN | None proven | **FAIL** | Same + large data I/O |
| Database search | Grover | Quadratic (k=2) | **FAIL** | Quadratic + I/O limited |
| Cryptography (Shor) | Shor's algorithm | Exponential | **PASS** | Exponential speedup, small data |

**The only quantum finance application that passes the Hoefler test is cryptanalysis — which is a threat, not an application.**

### Caveats:
1. These are **lower bounds** — the actual barrier is even higher because Hoefler's assumptions are optimistic for quantum
2. New algorithms with super-quadratic speedup could change the picture
3. NISQ heuristic algorithms (QAOA, VQE) have no proven speedups — they may or may not beat classical, but Hoefler cannot assess them (the framework requires known asymptotics)
4. For NISQ/heuristic approaches, the correct assessment is "no proven asymptotic speedup" rather than "quadratic fail"

---

## 7. How to Classify Papers in Our Pipeline

For each extracted experiment:

```
IF speedup_order is None or "none":
    verdict = "no_proven_speedup"
    reasoning = "No asymptotic quantum speedup proven for this algorithm"

ELIF speedup_order == "quadratic":
    verdict = "quadratic_insufficient"
    reasoning = "Quadratic speedup insufficient per Hoefler Table 2"

ELIF speedup_order == "cubic":
    IF oracle_complexity_M is known:
        threshold = Table2[operation_type]["cubic"]
        IF M <= threshold:
            verdict = "potentially_viable"
        ELSE:
            verdict = "oracle_too_complex"
    ELSE:
        verdict = "cubic_conditional"
        reasoning = "Cubic speedup may be viable if oracle complexity is below threshold"

ELIF speedup_order in ["quartic", "polynomial_other"]:
    verdict = "likely_viable"

ELIF speedup_order == "exponential":
    IF io_limited:
        verdict = "io_bottleneck"
    ELSE:
        verdict = "viable"

ELSE:
    verdict = "insufficient_data"
```

### Verdict Categories:
- `viable`: Passes all Hoefler tests — quantum advantage is theoretically achievable
- `likely_viable`: Quartic+ speedup, likely passes unless oracle is extreme
- `potentially_viable`: Cubic speedup with oracle below threshold
- `cubic_conditional`: Cubic speedup but oracle complexity unknown
- `quadratic_insufficient`: Quadratic speedup — fails per Hoefler Table 2
- `no_proven_speedup`: No asymptotic speedup proven (NISQ heuristics)
- `oracle_too_complex`: Cubic+ speedup but oracle exceeds threshold
- `io_bottleneck`: Exponential speedup but I/O limited
- `insufficient_data`: Not enough information to assess
