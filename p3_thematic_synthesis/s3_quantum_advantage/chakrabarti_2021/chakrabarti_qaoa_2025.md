Threshold for Fault-tolerant Quantum Advantage
with the Quantum Approximate Optimization Algorithm
Sivaprasad Omanakuttan,∗Zichang He, Zhiwei Zhang, Tianyi Hao, Arman Babakhani, Sami Boulebnane,
Shouvanik Chakrabarti, Dylan Herman, Joseph Sullivan, Michael A. Perlin,† Ruslan Shaydulin,‡ and Marco Pistoia
Global Technology Applied Research, JPMorganChase, New York, NY 10001, USA
Optimization is often cited as a promising application of quantum computers. However, the low
degree of provable quantum speedups has led prior rigorous end-to-end resource analyses to conclude
that a quantum computer is unlikely to surpass classical state-of-the-art on optimization problems
under realistic assumptions.
In this work, we compile and analyze the Quantum Approximate
Optimization Algorithm (QAOA) combined with Amplitude Amplification (AA) applied to random
8-SAT at the satisfiability threshold. Our compilation involves careful optimization of circuits for
Hamiltonian simulation, which may be of independent interest. We use the analytical scaling of the
time-to-solution for QAOA identified by Boulebnane and Montanaro [1] and find that with QAOA
depth p = 623, QAOA+AA achieves a crossover with state-of-the-art classical heuristics at 179
variables and 14.99 hours of runtime when executed on a surface-code-based fault-tolerant quantum
computer with 73.91 million physical qubits, a physical error rate of 10−3, and a 1 µs code cycle
time. Notably, we allow the classical solver to be parallelized as long as its total energy consumption
is equal to that required for decoding in the surface code. We further show that this restriction
on classical solver energy consumption can be relaxed given optimistic but plausible reductions in
physical error rates and fault-tolerance overheads, enabling a crossover of 2.94 hours using 8.88
million physical qubits against a classical solver running on a supercomputer with 725, 760 CPU
cores. These findings support the hypothesis that large-scale fault-tolerant quantum computers will
be useful for optimization.
I.
Introduction
Optimization is often included in the list of the do-
mains for which quantum computers are likely to have
an impact [2–4] due to the existence of many broadly
applicable quantum algorithms with provable asymp-
totic speedups [5–13]. However, most such speedups are
obtained using a variant of amplitude amplification [5]
and are therefore only quadratic [6–10].
Recently, al-
gorithms with super-quadratic speedups have been pro-
posed based on the short-path algorithm [11–13]; how-
ever, their speedup is only slightly better than quadratic
and is only over a restricted set of classical algorithms,
namely brute force [11, 12] and Markov chain search [13].
In some restricted cases, quantum algorithms have been
shown to achieve an exponential speedup over the best
known classical algorithms [14–16]. However, it remains
to be seen whether superpolynomial separations can be
achieved for more general classes of optimization prob-
lems.
In addition to the small degree of the speedup, the
practical applicability of these algorithms is limited by
the high cost of their implementation, including the need
for very deep circuits and extensive amounts of quan-
tum arithmetic. Combined with overhead of error cor-
rection, these observations led prior resource analyses to
conclude that quantum algorithms with small polynomial
∗sivparasad.thattupurackalomanakuttan@jpmchase.com
† michael.perlin@jpmchase.com
‡ ruslan.shaydulin@jpmchase.com
speedups in general [17] and for optimization in partic-
ular [18–21] are unlikely to deliver a practical speedup
on realistic large-scale fault-tolerant quantum comput-
ers. Notably, a detailed analysis of quantum algorithms
for unstructured random k-SAT problems concluded that
a speedup is unlikely once the classical cost of decod-
ing is taken into account [19]. For structured problems,
the speedup is absent even if the cost of decoding is ig-
nored [21].
The quantum approximate optimization algorithm
(QAOA) [22–24] is a quantum heuristic for optimization
that has recently been shown to provide a polynomial
speedup over classical state-of-the-art for the Low Auto-
correlation Binary Sequences [25] and random 8-SAT [1]
problems. QAOA solves optimization problems by using
a parameterized quantum circuit consisting of p steps of
applying, in alternation, two Hamiltonian evolution op-
erators. The first operator is called the “phaser” and ap-
plies a phase to computational basis states proportionally
to the objective function value of the corresponding bit-
string. The second operator is called the “mixer” and in-
duces non-trivial dynamics equivalent to a quantum walk
on the boolean hypercube. A notable attribute of QAOA
is the simplicity of its circuit, consisting of repetitions of
two fast-forwardable Hamiltonian evolutions, which has
enabled small-scale hardware demonstrations [26–30].
In this work, we focus on the random 8-SAT prob-
lem, for which Boulebnane and Montanaro [1] analyti-
cally derive the instance-average success probability and
show that it decays exponentially with problem size
n, with empirical results showing a power-law depen-
dency on QAOA depth p.
Specifically, the time-to-
solution of QAOA with p layers for 8-SAT is shown
arXiv:2504.01897v1 [quant-ph] 2 Apr 2025


2
to be O(20.69p−0.32n).
The exponent can be reduced
by another factor of two by using amplitude amplifica-
tion (QAOA+AA). For sufficiently large p, this approach
gives a polynomial speedup over state-of-the-art classical
algorithms.
Our main result is an analysis of the conditions for a
quantum advantage for the random 8-SAT problem using
QAOA+AA compiled to a fault-tolerant quantum pro-
cessor based on the surface code. On the quantum algo-
rithm side, we compile QAOA+AA and optimize multi-
ple aspects of the circuit, including reducing the circuit
depth required to implement QAOA phaser and k-SAT
oracle, and identifying the optimal number of T gates to
maximize the fidelity of Hamiltonian evolutions, among
other improvements. As some of these optimizations ap-
ply to Hamiltonian evolution more broadly and are not
specific to QAOA, they may be of independent inter-
est. We note that our logical circuit is composed only
of single-qubit Pauli gates, single- and two-qubit Pauli
measurements, and the preparation of logical |0⟩, |+⟩, T,
and CCZ states, allowing us to give a complete resource
estimate.
On the classical algorithm side, we benchmark state-of-
the-art classical heuristics for random 8-SAT and iden-
tify Sparrow [31] as the most performant one, with a
time-to-solution that scales as 20.176n with the number
of variables n, which is a notable improvement over the
scaling of 20.42n and 20.345n used as the classical point
of comparison in prior analyses of the prospects for a
quantum advantage for random 8-SAT [1, 19]. We fur-
ther allow for the parallelization of Sparrow, whose effec-
tive speedup from running on multiple cores was stud-
ied in Ref. [32], and assume that Sparrow parallelizes
as well as the most parallelizable unstructured problem
instance considered in Ref. [32]. The number of CPUs
used by Sparrow in our analysis is determined by energy
consumption; namely, we require that the total energy
consumption of the CPUs running Sparrow is equal to
that required to perform real-time decoding of the sur-
face code [33].
We find that for random 8-SAT on n = 179 vari-
ables, QAOA+AA with p = 623 executed on 73.91 × 106
physical qubits has an expected time-to-solution of 14.99
hours, which is equal to that of state-of-the-art classical
solver running on 46 CPU cores with a power budget of
269.27 W. For n = 233 variables, QAOA+AA achieves
100× speedup over classical state-of-the-art with a quan-
tum runtime of 82.21 hours.
Our main result relies only on existing techniques and
a relatively conservative set of hardware assumptions.
However, we anticipate that the rapid progress in error
correction and hardware will lead to further reductions in
resource requirements, which are not taken into account
in our main results. We therefore analyze the impact of
potential future progress in magic state cultivation [34],
algorithmic fault-tolerance [35], and hardware error rates.
We find that these improvements may lead to a crossover
time of only 2.94 hours using 8.88×106 physical qubits
against classical solver running on all 725, 760 cores of
MareNostrum 5 GPP supercomputer [36].
Our results contrast with the negative findings of
previous works [17–19] and are enabled by combin-
ing multiple contributions with recent developments in
the field.
First, we leverage improved decoding tech-
niques [33, 37, 38], which have led to a 100× reduction
in the classical computing overheads of decoding as com-
pared to the estimates used in Ref. [19].
Second, we
leverage improved resource-state factories [39] and (simi-
larly to Ref. [19]) allow for their parallelization, such that
the runtime of the quantum algorithm is not limited by
the time required to produce a resource state.
Third,
we trade space for time by optimizing the compilation,
scheduling, and parallelism of circuit components. These
techniques reduce the effective time cost of one clause in
the QAOA phaser to one logical QEC cycle (d rounds of
syndrome extraction in a distance-d surface code). Fi-
nally, we use QAOA+AA, which has a simple circuit
and, as shown by Boulebnane and Montanaro [1], offers
a super-quadratic speedup.
II.
Results
We study the regime of quantum advantage for the
random k-SAT problem [40], which has been studied
extensively from the perspective of both classical [41–
44] and quantum [1, 19, 21, 45–47] algorithms. In this
problem, the objective is to determine whether there ex-
ists an assignment of n truth values to variables that
satisfies a Boolean formula with m clauses, where each
clause in the formula contains exactly k literals. We de-
fer formal definition of the ensemble of instances used
to Methods.
As the clause-to-variable ratio
m
n grows,
k-SAT undergoes a phase transition from random in-
stances being satisfiable with high probability to being
almost surely unsatisfiable at
m
n ≈2k log 2 (up to the
leading order in k) [40]. Whereas efficient classical al-
gorithms or performant heuristics exist for k-SAT with
m
n < 2k log k
k
[43], it remains an open question to under-
stand the power of algorithms to address problems with
2k log k
k
< m
n ≲2k log 2. Following Ref. [1], we focus on
random 8-SAT close to the satisfiability threshold and
set m
n = 176.
A.
Clasical solvers
We begin by benchmarking the state-of-the-art clas-
sical solvers. We include in our comparison incomplete
classical algorithms, i.e., algorithms that cannot deduce
that an instance is unsatisfiable.
We remark that our
quantum algorithm, QAOA, is also an incomplete solver.
We include winners of the three latest random track SAT
competitions (Sparrow [31], 2018 [48], yalSAT [49], 2017
[50] and Dimetheus [51], 2016 [52]; random track removed
in 2019 [53]). Additionally, we include probSAT [54] and


3
30
40
50
60
problem size n
108
1011
median runtime (ns)
Sparrow
YalSAT
dimetheus
probSAT
walksatlm
2(0.176n+19.4)
2(0.288n+17.1)
2(0.194n+18.9)
2(0.195n+18.6)
2(0.197n+19.1)
ee
𝑒−𝑖𝛽𝑙𝑋
e
𝑃𝛾𝑙
ee
𝑒−𝑖𝛽𝑙𝑋
ee
𝑒−𝑖𝛽𝑙𝑋
ee
𝑒−𝑖𝛽𝑙𝑋
× 𝑝 layers
+
+
+
+
𝑒−𝑖𝛾𝑙𝐻𝑐
e
e
𝑃𝛾𝑙
𝑃𝛾𝑙
0
200
400
600
QAOA depth p
0.00
0.25
0.50
scaling exponent
QAOA
Sparrow
0
0
0
0
𝑍
𝑼𝑸𝑨𝑶𝑨
†
𝑼𝑸𝑨𝑶𝑨
× 𝜋/4 PrQAOA
success
𝑂𝐶
|QAOA⟩
0
200
400
600
QAOA depth p
0
2
4
scaling advantage
QAOA
QAOA+AA
A
D
B
C
E
Figure 1.
Classical and quantum algorithms for 8-SAT. (A) Median time-to-solution (TTS) of state-of-the-art classical
solvers for random 8-SAT near the satisfiability threshold with a clause-to-variable ratio of r = 176. The best scaling is achieved
by the Sparrow solver, for which the TTS is 20.176n+19.369 ns. (B) Example QAOA circuit for an instance of 3-SAT, which is
composed of p layers that alternate the phaser and mixer, where the phaser (orange dotted box) encodes the k-SAT objective
function and the mixer consists of single-qubit rotations Rx(βl) = e−iβlX/2. (C) The TTS scaling exponent of QAOA with
varying QAOA depths p, reproduced from Ref. [1]. The dashed line indicates the scaling exponent for Sparrow, for reference.
(D) The full circuit for QAOA+AA consists of π/(4pPrsuccess
QAOA ) repetitions of a module that contains two QAOA circuits, an
oracle OC that flips the sign of solutions to k-SAT, and a “zero-state oracle” that flips the sign of the all-0 state. (E) The
asymptotic speedup of QAOA and QAOA+AA over the state-of-the-art classical solver Sparrow for varying values of QAOA
depth p. QAOA+AA scales quadratically better than QAOA, enabling larger speedups.
WalkSATlm [55], which are known to perform well on
random problems [56]. Fig. 1A shows the growth of time-
to-solution (TTS) with number of variables, with addi-
tional details deferred to Methods. We find Sparrow [31]
to be the most performant solver, with median TTS given
by
Tc (n) = 2(0.176±0.011)n+(19.369±0.657) ns,
(1)
where the error bars denote a 90% confidence interval.
This scaling is a notable improvement over the scal-
ing exponents 0.42 and 0.345 used in prior analyses of
the prospects for a quantum advantage for random k-
SAT [1, 19].
We remark that our benchmarking finds
a lower exponent of 0.197 for WalkSATlm than that re-
ported Ref. [1] due to our use of an optimized implemen-
tation [55, 57].
The parallelization behavior of Sparrow, and specifi-
cally the effective speedup obtained by running on mul-
tiple cores, was studied in Ref. [32]. Therein, the authors
found that the effective speedup from parallelization is
linear in the number of cores for structured boolean sat-
isfiability problems, but sublinear for unstructured prob-
lem instances. We allow for the parallelization of Spar-
row in our analysis, and assume that Sparrow parallelizes
as well as the most parallelizable unstructured problem
instance (Rand-9) considered in Ref. [32].
The num-
ber of CPUs used by Sparrow is determined by setting
their power budget ( 280
48 ≈5.8 watts per CPU; see Sec-
tion IV F) equal to that required to perform real-time de-
coding of surface code (8 milliwatts per decoder) [33]. We
remark that the parallelization of Sparrow in the regime
corresponding to our main results is near-perfect since
the number of CPU cores is modest (≤71).
See Sec-
tions IV E and IV G for additional details.
B.
Quantum algorithm
We consider QAOA, which solves satisfiability prob-
lems using a parameterized quantum state (shown in
Fig. 1B),
|QAOA⟩= UQAOA |+⟩⊗n ,
(2)
UQAOA =
p
Y
l=1
e−iβlHM e−iγlHC,
(3)
where β and γ are free parameters; p is the number of
alternating layers, also called the QAOA depth; |+⟩⊗n ∝
P
x∈{ 0,1 }n |x⟩is a superposition over all computational
basis states; HC is the cost Hamiltonian encoding the
optimization problem; and we set the mixer Hamiltonian
to HM = 1
2
Pn
j=1 Xj with Xj = |0⟩⟨1|j + |1⟩⟨0|j.
The cost Hamiltonian HC for k-SAT energetically re-


4
wards satisfying clauses,
HC = −
m
X
j=1
X
x∈{ 0,1 }n
Cj(x) |x⟩⟨x| ,
(4)
where each clause can be written in the form
Cj(x) = ℓj1(xj1) ∨ℓj2(xj2) ∨· · · ∨ℓjk(xjk).
(5)
Here xji is the i-th variable addressed by clause Cj, and
ℓji(xji) = xji or ℓji(xji) = ¬xji = 1 −xji depending on
the clause. Note that this notation is over-complete, as
the same variable may be addressed by multiple clauses.
Ref. [1] derives an analytical expression for instance-
average success probability of QAOA with p layers. Eval-
uating this expression with optimized parameters β, γ,
Ref. [1] obtains Prsuccess
QAOA = 2−0.69p−0.32n. The expected
TTS of QAOA is equal to the inverse of the success prob-
ability (up to a polynomial cost for QAOA circuit imple-
mentation). As Fig. 1C shows, QAOA with a moderate
depth achieves a speedup over Sparrow.
The scaling of TTS for QAOA with problem size n
can be improved quadratically by boosting the success
probability with amplitude amplification (AA) [58]. The
combined QAOA+AA circuit, summarized in Fig. 1D,
applies the following operator
π
4√
Prsuccess
QAOA times [58]:
Q = UQAOAO0U †
QAOAOC.
(6)
Here O0 is a “zero-state oracle” that flips the sign of
the all-0 state, O0 |x⟩= −|x⟩if x = (0, · · · , 0) and
O0 |x⟩= |x⟩otherwise; and the OC is a k-SAT oracle
defined by OC |x⟩= (−1)C(x) |x⟩, where C(x) = 1 for
solutions x to the 8-SAT problem instance and C(x) = 0
otherwise. Leveraging the quadratic speedup from AA,
QAOA+AA improves the time-to-solution for random 8-
SAT to 20.345p−0.32n. The asymptotic speedup of QAOA
and QAOA+AA over the state-of-the-art Sparrow solver
as a function of QAOA depth p is shown in Fig. 1E.
We note that we have reported an instance-averaged
TTS for both the classical (Sparrow) and quantum
(QAOA+AA) algorithms. However, for a given instance,
the required time to find a solution could be higher or
lower than the average. When running a classical algo-
rithm in practice, we can estimate an upper bound on
the required runtime and implement a check that stops
the run early whenever a satisfying assignment is found.
In the quantum case, additional care is required to avoid
“overshooting” the target state with amplitude amplifi-
caton.
We show in Theorem IV.1 of Methods how to
prevent overshooting at the cost of quadrupling the quan-
tum runtime, and include this overhead in our analysis.
For clarity of presentation, we use the instance-averaged
TTS as the runtime for both classical and quantum al-
gorithms; however, the crossover point does not change
if both times are scaled by a constant.
C.
Quantum runtime
To compute the quantum TTS, we analyze the cost
of implementing the QAOA+AA circuit in detail. The
quantum TTS Tq is equal to the combined runtime of the
four components in Eq. (6), also shown in Fig. 1D:
Tq =
π
4
q
Prsuccess
QAOA
[2p (Tmixer + Tphaser) + TOC + TO0] .
(7)
Here Tmixer, Tphaser, TOC, and TO0 are, respectively, the
runtimes of the QAOA mixer e−iβHM , the QAOA phaser
e−iγHC, the k-SAT oracle OC, and the zero-state oracle
O0.
To evaluate the runtime of these components, we con-
sider their fault-tolerant implementation in a surface code
architecture with a Clifford+T+CCZ gate set that is real-
ized with lattice surgery [59] and resource-state factories
[39]. Our runtimes will be provided in units of the logical
cycle time TLC = d×1 µs, or the time needed to perform d
rounds of syndrome measurement in a distance-d surface
code. For reference, we find that code distances d ≈30
are sufficient for all crossovers reported in this work (see
Section IV D), in agreement with findings elsewhere in
the literature [17, 60].
The mixer acts independently on each qubit, and can
thereby be reduced to n parallel implementations of
the single-qubit phase gate P(γ) = eiγ|1⟩⟨1| (in the X
basis).
We consider the approximation of single-qubit
phase gates in the Clifford + T gate set with the ancilla-
assisted mixed fallback method of Ref. [61], and iden-
tify the required decomposition accuracy for achieving
a QAOA+AA circuit fidelity of 99% with a depolariz-
ing noise model (see Fig. 2A and Section IV B of the
Methods). Denoting the number of logical cycles required
to thus implement P(γ) to the desired accuracy by nP ,
which is approximately equal to the number of T gates
of the decomposition, we use the method of Ref. [62] to
consume one T state per logical cycle, and account for
a sufficient number of T-state factories to match this T
state consumption rate. The runtime of the mixer is then
Tmixer = nP × TLC.
(8)
While the precise value of nP depends on the choice of
QAOA depth p, for reference we note that nP ∈[25, 29]
for the cases analyzed in this work.
The phaser e−iγHC applies, for each clause Cj of the
form in Eq. (5), a phase eiγ to all bitstrings that satisfy
the clause. To minimize the runtime of the phaser, we
use a graph coloring algorithm [63] to partition clauses
into subsets such that every subset consists of clauses
that address mutually disjoint sets of qubits.
Specifi-
cally, construst a clause collision graph, which associates
each clause with the node of a graph, and draw an edge
between any pair of clauses that address the same qubit.
Coloring the nodes in this graph thereby identifies, by


5
20
40
60
80
problem size n
1800
1900
2000
2100
colors c
10−6
10−3
100
δ
10−4
100
Ient(ϵT, δ)
simulation
analytical
mixer
phaser
oracle OC
oracle O0
logical cycles
111 × 103
107 × 105
115 × 103
32
% of logical cycles
1.02
97.92
1.05
2.9 × 10−3
8
=
=
TACU
Z
|CCZ⟩⊗7
|0⟩⊗51
|0⟩
P(γ)
P(γ)
|0⟩
P(γ)
A
C
B
D
Figure 2. Compilation of QAOA+AA for 8-SAT. (A) Given a T-state infidelity ϵT (here ϵT = 10−8), we optimize the
accuracy δ with which phase gates P(γ) = eiγ|1⟩⟨1| are decomposed into a Clifford + T gate set by minimizing the entanglement
infidelity Ient of the decomposition (see Section IV B of the Methods). Increasing δ leads to greater decomposition error, while
smaller δ increases the number of noisy T gates in the decomposition. The dashed line shows analytical estimates for Ient,
while the solid line and shaded region shows the mean and standard deviation from numerical trials with 40 random angles.
(B) The number of colors c empirically found to be necessary to color the clause collision graph for random instances of 8-SAT
with different problem sizes n and a clause-to-variable ratio of r = m
n = 176. These colors are used to partition 8-SAT clauses
into c subsets such that every subset consists of clauses that address mutually disjoint sets of qubits. The value of c sets a
lower bound on the runtime of the QAOA phaser for k-SAT. (C) Schematic of the circuit to implement an 8-qubit phase gate
P8(γ) = eiγ|1⟩⟨1|⊗8, which requires 7 CCZ states and 52 logical |0⟩-state ancillas. The operation schematically labelled “TACU”
addresses the top 8 qubits for only one logical cycle, and the final operation labelled “Z” indicates the application of Pauli-Z
correction gates as determined by measurement outcomes. These correction gates can be deferred to the end of the phaser,
allowing a new batch of clauses to be dispatched at every logical cycle of the phaser (see Section IV C of the Methods and
Appendix B). (D) The time budget for different components of the QAOA+AA circuit corresponding to the crossover point
for a cubic speedup in Fig. 3. The k-SAT phaser dominates this budget, highlighting the importance of its optimization.
color, subsets of clauses that can be applied in parallel.
A simple counting argument suggests that a k-SAT in-
stance with a clause-to-variable ratio of r = m
n should be
colorable with c ∼k2r colors: each clause has k variables,
each of which belong to km
n = kr clauses on average. The
graph we construct can be thereby expected to have de-
gree ∼k2r, and by Vizing’s theorem [64] be colorable
with ∼k2r colors. As we show in Fig. 2B, for k = 8, a
clause-to-variable ratio of r = m
n = 176, and n ≳40, this
argument empirically overestimates the number of colors
by a factor of ∼5, and that in practice clauses can be
partitioned into c ≈12r subsets of average size m
c ≈n
12.
We now consider the time required to apply the phase
for each clause. The phase for each clause can be imple-
mented by a k-qubit phase gate eiγ|1⟩⟨1|⊗k that is sand-
wiched by bit-flip (Pauli-X) gates on variables that are
negated in the clause. In turn, the k-qubit phase gate can
nominally be implemented by sandwiching a single-qubit
phase gate P(γ) between two (k + 1)-qubit Toffoli gates.
In practice, these two Toffoli gates can be merged into a
single k-qubit temporary-AND-compute-and-uncompute
(TACU) gadget that “dispatches” the phase gate to an
ancilla qubit, measures that ancilla qubit, and adap-
tively applies Pauli-Z corrections to the k variable qubits,
shown schematically in Fig. 2C. We optimize the two-
qubit TACU gadget of Ref. [62] to construct a k-qubit
TACU gadget that consumes k−1 CCZ states, addresses
the k-SAT variable qubits for one logical cycle, and can
be executed in a total of nP + 4⌈log2 k⌉logical cycles
(see Appendix B). This gadget allows us to dispatch one
batch of clauses at each logical cycle of the k-SAT phaser,
deferring Pauli-Z corrections to the end of the phaser.
In total, the phaser can be implemented by dispatch-
ing clauses for c logical cycles, waiting for all gadgets
to complete, and applying adaptive Pauli-Z corrections,
such that the total runtime of the phaser is
Tphaser = (c + nP + 4⌈log2(k)⌉) × TLC.
(9)
We provide additional details in Section IV C and Ap-
pendix B.
The k-SAT oracle OC flips the sign of states that sat-
isfy m clauses, each of which is an OR of k bits. Similarly
to the phaser, we use a k-qubit TACU gadget to flag the
satisfaction of each clause with an ancilla qubit, and use
a graph coloring algorithm to identify clauses whose sat-
isfaction can be computed in parallel. In turn, the ancilla


6
A
asymptotic speedup QAOA depth p problem size n code distance d physical qubits (×106) crossover time
quadratic
71
242
35
152.43
3 y
cubic
253
191
29
84.43
64.57 h
quartic
623
179
28
73.91
14.99 h
2.0
2.5
3.0
3.5
4.0
speedup
101
102
103
crossover time (hours)
2
4
6
0
50
100
crossover time (hours)
0
20
40
60
physical qubits (millions)
quartic speedup
100
200
300
problem size n
10−8
10−4
100
104
108
runtime (hours)
Tq
Tc
Tc/Tq = 100
B
C
D
Figure 3. Crossover times for random 8-SAT near the satisfiability threshold. (A) Parameters for crossover points at
which QAOA+AA and the classical solver Sparrow take, in expectation, equal time to solve random instances of 8-SAT near the
satisfiability threshold. Crossover points are shown for QAOA depths p that correspond to asymptotically quadratic, cubic, and
quartic speedups. Here n is the number of 8-SAT variables at the crossover point and d is the surface code distance required to
achieve a QAOA+AA circuit fidelity of 99%. We also report the number of physical qubits required when accounting for both
logical ancilla qubits and resource-state factories from Ref. [39], as well as the runtime of the algorithms at the crossover point.
(B) The crossover time as a function of the asymptotic speedup for QAOA+AA over Sparrow. The speedup is determined
by the QAOA depth p, and the QAOA+AA algorithm has a crossover time of less than a day for a large range of speedups.
(C) Different choices of a spacetime tradeoff in the QAOA+AA algorithm can reduce qubit overheads at a cost of increasing
the crossover time. Specifically, we show how the time and space requirements for the crossover point with an asymptotically
quartic speedup vary with respect to a “slowdown factor” τ that controls the number of logical cycles between dispatched
clauses in the k-SAT phaser. Dispatching clauses at a slower rate (increasing τ) reduces the resource-state consumption rate
of the phaser, thereby requiring fewer resource-state factories and allowing for more reuse of ancilla qubits that are devoted to
applying phases. (D) Classical runtimes Tc for Sparrow and quantum runtime Tq for QAOA+AA as a function of the problem
size n. Here the QAOA depth p is chosen for an asymptotically quartic speedup. The dashed vertical line indicates the problem
size, n = 233, for which Tc/Tq = 100.
qubits that flag the satisfaction of individual clauses can
be pairwise AND-ed in a binary tree to flag the satis-
faction of all clauses with one qubit, at which point the
oracle phase is applied with a single-qubit Pauli-Z gate.
A time-optimal implementation of the k-SAT oracle leads
to an increase in both the CCZ consumption rate and the
number of computational ancilla qubits required by the
QAOA+AA algorithm, thereby greatly increasing space
overheads. Our implementation of the oracle therefore
includes intentional delay times to reduce its CCZ con-
sumption rate and allow for the recycling of ancilla qubits
that compute the satisfaction of clauses. Altogether, up
to minor corrections (see Appendix C) we find that the
oracle can be implemented with runtime
TOC = 4c log2
km
c

× TLC
(10)
without exceeding the qubit requirements of the phaser.
The zero-state oracle O0 is equal, up to conjugation by
Pauli-X gates, to an n-qubit multi-control π-phase (Z)
gate. This gate can be implemented with a multi-qubit
TACU gadget that consumes n−1 CCZ states. The total
runtime of the zero-state oracle is then
TO0 = 4 log2 n × TLC.
(11)
As illustrated by the time budget in Fig. 2D, the runtime
Tq is dominated by the time to implement the QAOA
phaser.
D.
Qubit requirements
The qubit requirements of the QAOA+AA algorithm
are dominated by two contributions: the number of log-
ical ancilla qubits required for TACU gadgets, and the
number of resource-state factories required to match T
and CCZ consumption rates of the algorithm. Both con-
tributions are, in turn, determined by the number of
TACU gadgets that run in parallel as they are dispatched
in the phaser. If s TACU gadgets dispatched at every log-
ical cycle and each gadget runs for λ logical cycles, the
qubits used for the first batch of gadgets can be used
for the batch at logical cycle λ + 1, such that the total
number of TACU gadgets that run in parallel is
njobs = s × λ.
(12)


7
For the cases analyzed in this work, s ≈m
c ≈
n
12 ≲20
and λ = 4⌈log2(k)⌉+ nP ≤41.
Every TACU gadget in the phaser uses ⌊13
2 k⌋logical
ancilla qubits (see Appendix B). For resource-state fac-
tories, we use the (15-to-1)4
13,5,5×(20-to-4)27,13,15 T fac-
tory and (15-to-1)6
13,7,7×(8-to-CCZ)25,15,15 CCZ factory
developed in Ref. [39], and account for a sufficient num-
ber of factories to produce one T state per TACU gad-
get per logical cycle. The number of qubits required for
this T-state production rate is sufficient to produce CCZ
states at the rate that is required in CCZ consumption
stages of the QAOA+AA algorithm, so we repurpose T
state factories into CCZ state factories on an as-needed
basis. We note that each of our T state factories take just
over 5 logical cycles to produce 4 T states, so we need
about 1.3 factories per TACU gadget. In principle, one
could slow down the T state consumption stages of the
QAOA+AA algorithm to consume T states at a rate that
is commensurate with the production rate of one factory.
While simplifying architectural (e.g., qubit layout and
routing) considerations for the QAOA+AA algorithm, we
note that the optimization of resource-state factories is
an active area of research with notable recent advance-
ments [34] and pathways for further improvement that
have not been accounted for in this work. We therefore
defer a more detailed analysis of architectural consider-
ations with improved resource-state factories to future
work.
E.
Quantum-classical crossover
Fig. 3A provides a summary of quantum resources
at the crossover point at which Tq = Tc for choices of
the QAOA depth p that correspond to asymptotically
quadratic, cubic, and quartic speedups over state-of-the-
art classical solvers. Even when accounting for the ben-
efits of classical parallelization, our analysis finds, for
example, that QAOA+AA is capable of outperforming
state-of-the-art classical solvers on 8-SAT instances with
n = 179 with a few hours of runtime using 73.91 mil-
lion physical qubits.
A more detailed dependence of
the crossover time on the asymptotic speedup is pro-
vided in Fig. 3B. We note that the parameters for the
crossover point depend on a choice of spacetime tradeoffs
in the quantum algorithm, and show in Fig. 3C how the
crossover time and qubit overheads change if the QAOA
phaser is slowed down by a factor of τ to decrease the rate
at which the phaser dispatches TACU gadgets. A lower
dispatch rate reduces the number of parallel jobs njobs
that run during the phaser, thereby reducing both the
number of ancillas that are required for these jobs, and
the number of resource-state factories required to main-
tain the resource-state consumption rate of the phaser.
Finally, in Fig. 3D, we show how the gap between clas-
sical and quantum runtime grows with n. For example,
n = 233 corresponds to 100× speedup over classical with
quantum runtime of 82.21 hours.
F.
Opportunities for quantum resource reduction
Our main results show that taking gate paralleliza-
tion into account and carefully optimizing the quantum
circuit for fault-tolerant execution can substantially re-
duce the crossover point for solving 8-SAT using the
QAOA+AA algorithm implemented on the surface code.
However, our analysis has so far relied only on exist-
ing techniques and conservative assumptions about hard-
ware performance (10−3 physical error rate and 1 µs cycle
time). We now discuss the impact of potential future im-
provements to the surface code and hardware, focusing
on three realistic improvements: reduced overheads for
resource state factories via magic state cultivation [34],
reduced logical cycle times through improved decoding
and algorithmic fault-tolerance [35], and reduced physi-
cal error rates. As summarized in Table I, we estimate
that these improvements enable a crossover time of only
2.94 hours against a classical solver parallelized over all
725, 760 CPU cores of MareNostrum 5 GPP, which is the
35th largest supercomputer in the world at the time of
writing and one of the largest CPU-only systems, with
total energy consumption of 5.75 MW [36].
1.
Better resource-state factories
Recently, Gidney et al. introduced magic state cultiva-
tion [34] as an alternative to distillation. This protocol
leads to an order-of-magnitude reduction in the space-
time footprint required to produce a high-quality T state.
At physical error rates of 10−3, however, none of the con-
figurations considered in Ref. [34] achieve the requisite T
state fidelity (≈10−12) for running QAOA+AA for 8-
SAT. Nonetheless, we note that the distillation protocols
used for our main results are in fact two-stage distilla-
tion protocols, and one could imagine similarly perform-
ing magic-state cultivation as the first step in a multi-
stage protocol to further improve the fidelity of a resource
state. Moreover, standalone cultivation is a new protocol
with potential room for refinement, and it may be possi-
ble to achieve cultivation fidelities sufficiently high to ob-
viate the need for secondary distillation. With these con-
siderations in mind, Table I shows the impact of reducing
spacetime footprint of a resource state by a (modest) fac-
tor of 5 over the distillation-only approach considered in
Fig. 3.
2.
Reducing logical cycle times
Our main results assumed a logical cycle time of
d×1 µs, where d is the code distance of the surface code.
This logical cycle time sets an effective clock speed for
the fault-tolerant quantum computing architecture that
we consider. A clear way of speeding a quantum algo-
rithm is to decrease this logical cycle time. For exam-
ple, one can imagine incorporating improved decoding


8
no
improvements
smaller
resource
factories
reduced
logical cycle
time
pphys = 10−4
combined
improvements
realistic
classical
parallelization
[32]
problem size n
203
203
185
195
177
crossover time Tq
65.24 h
65.5 h
7.23 h
25.45 h
2.94 h
physical qubits (×106)
45.25
29.82
40.84
25.77
8.88
perfect
classical
parallelization
problem size n
296
296
278
289
271
crossover time Tq
20.7 d
20.74 d
2.31 d
7.83 d
21.75 h
physical qubits (×106)
153.67
107.14
135.81
77.31
29.92
Table I. Impact of potential future advances on crossover against the MareNostrum 5 GPP supercomputer.
Here we consider the impact of the potential future improvements in quantum computing on estimated crossover points for
8-SAT with QAOA+AA with an asymptotically quartic speedup. Unlike our main results presented in Fig. 3, here we do not
restrict the energy consumption of the classical solver and instead estimate the time-to-solution for the classical solver if it was
run on all 725, 760 cores of MareNostrum 5 GPP (35th largest supercomputer in the world) [36]. For the classical algorithm, we
consider both “realistic” parallelization of Sparrow based on the most parallelizable unstructured problem instance in Ref. [32]
(see Section IV G), and perfect classical parallelization, which assumes that using ncores CPUs speeds up the classical solver
by a factor of ncores. For the quantum algorithm, we consider three potential improvements, namely: a fivefold reduction in
the spacetime cost of a resource state, a fivefold reduction in the logical cycle time, and a tenfold reduction in physical error
rates. As both sobering and aspirational points of reference, we also consider the possibility of achieving none or all these
improvements. For each scenario, we report the number of variables (n), quantum runtime (Tq), and the required number
of physical qubits (in millions) at the crossover point. We set the slowdown factor τ = 2 (discussed in Fig. 3) in the rows
corresponding to realistic parallelization to reduce the memory footprint at the cost of increased quantum runtimes, and set
τ = 1 for perfect classical parallelization.
schemes such as algorithmic fault tolerance [35] in or-
der to reduce the requirement of performing d syndrome
measurement for every logical cycle. The surface code er-
ror correction cycle time of 1 µs may also be reduced due
to algorithmic or hardware innovations, most notably re-
duced measurement times in superconducting platforms
[65].
We consider the impact of reducing logical cycle
times by a factor of 5 in Table I.
3.
Lower physical error rates
Quantum hardware has matured remarkably over the
last decade [66] and we expect this progress to continue.
In particular, two-qubit error rates of 6×10−4 have been
demonstrated in fluxonium superconducting qubits [67]
and 3 × 10−4 in trapped ions [68].
In Table I, we re-
port how a reduction of physical error rates from 10−3 to
10−4 would impact the performance of QAOA+AA for
8-SAT. We note that a reduction of this kind makes the
cultivation protocol considered above sufficient in its cur-
rent form to solve 8-SAT with QAOA+AA. The results
of [34] indicate that physical error rates of 10−4 lead to
T-states with fidelity of 4×10−11 and a 10-fold reduction
in the spacetime cost of a T state. We consider the im-
pact of reducing physical error rates to 10−4 (though still
keeping the same distillation protocols that were used in
our main results) in Table I.
4.
Additional directions
In addition to the specific improvements discussed
above, other developments and optimizations may yield
additional quantum resource reductions. We do not an-
alyze these reductions in Table I as their impact is more
difficult to quantify. For example, further optimizing the
circuit gadgets used in this work may lead to reduced
time and ancilla-qubit overheads. Aside from the pro-
duction of resource states, most quantum processing in
QAOA is devoted to implementing the single-qubit phase
gate P(γ). Reducing the cost of implementing this gate
in a surface code architecture—for example, by finding
more gate-efficient or parallelizable implementations in a
Clifford+T gate set [69], or by finding more efficient im-
plementations in a different gate set [61, 70] that is com-
patible with the surface code architecture—may therefore
yield substantial speedups for QAOA+AA. Finally, there
has been a great interest in recent years in the devel-
opment of new quantum low-density-parity-checks codes
[71] and concatenated quantum codes [72, 73]. Benefits
of these codes include more favorable encoding rates and
higher relative code distances which may reduce over-
heads for universal quantum computation [74, 75].
III.
Discussion
Our result is the first complete and realistic resource
estimate for a fault-tolerant quantum advantage in op-


9
timization.
More generally, our findings indicate that
low-degree polynomial speedups may be practical on
realistic large-scale fault-tolerant quantum computers.
This has outsized implications for domains like opti-
mization, in which complexity-theoretic evidence sug-
gests that broadly applicable exponential speedups are
unlikely. However, we expect our findings to translate
to other domains where low-degree polynomial speedups
are available such as planted inference [76] and machine
learning [77].
We focus our study on random satisfiability, which is
well-studied and enables careful analysis. However, an
important future direction is validating that the speedups
we estimate also hold for hard industrially-relevant opti-
mization problems, which are more challenging to char-
acterize mathematically and study rigorously.
Our results rely on recent progress in surface code and
decoding. The parallelization of resource-state factories
and careful scheduling of quantum subroutines, in par-
ticular, proved to be an effective strategy for minimizing
computation time while avoiding large space overhead.
Continued advancements in quantum hardware and error
correction can be expected to further reduce resource re-
quirements for fault-tolerant quantum computation, and
may thereby make practical the deployment of quantum
algorithms for which a fault-tolerant quantum advantage
was previously deemed implausible [17].
While the resource requirements we find are unlikely
to be satisfied by near-term or early-fault-tolerant quan-
tum processors, there are further optimizations one can
consider. In particular, we can simply run QAOA with
very large p such that Prsuccess
QAOA is a large constant (e.g.,
2/3) and bypass amplitude amplification. Ref. [78] shows
that a simple parameter extrapolation procedure appears
to lead to good QAOA parameters for large p, enabling
execution at very large depth with no instance-specific
parameter optimization. Further investigation is need to
ascertain the potential of this scheme and to understand
its resource requirements.
There are two major limitations of our work. First,
we rely on the power-law decay of the asymptotic quan-
tum scaling exponent with QAOA depth p, reported in
Ref. [1].
The evidence in Ref. [1] is for small QAOA
depths p and may not persist as p grows. Second, we
do not consider the cost of routing qubits.
The over-
head of routing may become non-negligible given the
large amount of parallelization in our quantum algorthm,
though it may be overcome by careful optimization of the
qubit layout and overall fault-tolerant architecture.
IV.
Methods
A.
Amplitude amplification with unknown initial
success probability
Here we present a procedure inspired by Ref. [58] for
ensuring that we do not overshoot in the amplitude am-
plification process.
The overhead comes from needing
to repeat the amplification process multiple times to ac-
count for uncertainty in the success probability of QAOA.
Theorem IV.1. Let PSAT be the projector on the space
of satisfying assignments and USAT an oracle for flag-
ging satisfying assignments. Suppose |ψ⟩= Uψ|0⟩is a
quantum state satisfying p = ∥PSAT|ψ⟩∥2
2. Then there is
a quantum algorithm that with probability at least 1 −δ,
makes at most
⌈π
4√p log2(1/δ)⌉
queries to Uψ, U †
ψ, USAT, and U †
SAT to output a satisfying
assignment.
Proof. Recall that if θa = sin−1(∥PSAT|ψ⟩∥2) for a state
|ψ⟩, then m rounds of amplitude amplification with Uψ
and USAT boosts the amplitude to sin((2m + 1)θa) [58].
Begin by measuring |ψ⟩in the computational basis
⌈log(1/δ)⌉times. If p ∈[ 1
2, 1], then we will find a sat-
isfying assignment with probability at least 1 −δ. If no
solution is found, then take θ = sin−1( 1
√
2) and perform
⌈π
8θ −1
2⌉
(13)
round of amplitude amplification and then measure the
result.
This will ensure that if θa ∈[ θ
2, θ], then the
probability of success will be boosted to at least 1
2. We
then repeat this log2(1/δ) times, which ensures that if
θa ∈[ θ
2, θ], we will see a satisfying bitstring with prob-
ability at least 1 −δ. If we get a satisfying assignment,
then we stop.
Otherwise, we continue to halve θ and
repeat the above until a satisfying bit string is found.
Let k = ⌊log2(θ/θa)⌋. With probability at least 1 −δ,
the number of calls to the unitaries specified in theorem
will be at most
⌈log2(1/δ)⌉·
k
X
i=0
⌈2iπ
8θ −1
2⌉≤
≤⌈log2(1/δ)⌉
k
X
i=0
⌈
π
8√p · 2k−i −1
2⌉
≤⌈log2(1/δ)⌉⌈π
4√p⌉.
Note only the interval containing θa needs to succeed
for us to terminate successfully in the above specified
time.
We set δ = 1/24 = 0.0625 for the analysis in the main
text, which corresponds to an overhead of ⌈log2(1/δ)⌉=
4 over ordinary Grover.


10
B.
Optimal decomposition accuracy for phase gates
In the context fault-tolerant quantum computing, im-
plementing arbitrary rotations is challenging due to the
constraints of the fault-tolerant universal gate set for a
given architecture. Typically, these gate sets include the
Clifford group gates (such as the Hadamard, Phase, and
CNOT gates) and a non-Clifford gate such as the T-gate.
While the Clifford gates are relatively easy to implement
fault-tolerantly, they are not sufficient for universal quan-
tum computation. The inclusion of the T-gate allows for
universality, enabling the approximation of any quantum
operation to arbitrary precision at the cost of additional
overhead such as magic state distillation.
The
Solovay-Kitaev
theorem
provides
a
general
method for approximating any single-qubit unitary op-
eration using a finite gate set [79]. While this method
is general, it is not always the most efficient in practice
[61, 80, 81]. For a fixed decomposition accuracy δ, the
required number of T gates, NT , typically scales as
NT = b log2 δ−1 + c,
(14)
where b, c are positive real numbers whose precise value
depends on the decomposition scheme [80, 81]. In this
section, we consider two decompositions schemes with
(b, c) = (3, 9.19) and (0.57, 8.83), which are studied in
detail in Refs. [80] and [61], respectively.
We can decompose a phase gate into a sequence of X
and Z rotations, where each rotation consumes T states
and addresses the rotated qubit for one logical cycle [62].
Treating the infidelity ϵT of a faulty T state as a prob-
ability of a depolarization error after consuming this T
state, we combine the infidelity after NT depolarization
channels (see Appendix A) with the decomposition er-
ror δ of a phase gate to obtain an overall entanglement
infidelity of decomposition,
Ient(ϵT , δ) = 1 −1
4(1 + 3(1 −ϵT )NT )
1 −δ2
.
(15)
For a fixed T gate infidelity ϵT , the optimal decomposi-
tion accuracy is δopt = arg minδ Ient(ϵT , δ). Substituting
Eq. (14) into Eq. (15) and setting ∂Ient(ϵT , δ)/∂δ = 0, we
find that the optimal decomposition accuracy δopt satis-
fies
2δ2
opt

1 + 3(1 −ϵT )b log2 δ−1
opt+c
= −3b(1 −ϵT )b log2 δ−1
opt+c log2(1 −ϵT )
1 −δ2
opt

.
(16)
This condition is a transcendental equation that can be
solved numerically to compute δopt for any given value of
ϵT . As an estimate, however, in the regime ϵT , δopt ≪1
we can simplify
δopt ≈
s 3bϵT
8 ln 2

.
(17)
104
106
108
number of gates G
10−11
10−9
10−7
10−5
ϵmax
T
I = 0.01, (b,c)=(3,9.19)
I = 0.01, (b,c)=(0.57,8.83)
I = 0.1, (b,c)=(3,9.19)
I = 0.1, (b,c)=(0.57,8.83)
Figure 4.
The desired infidelity of the T state to achieve a
target QAOA+AA circuit infidelity as a function of the to-
tal number of phase gates (G) in Eq. (18). We consider two
different decomposition schemes and two different target in-
fidelities I for the simulations. The plot suggests a notable
dependence on the number of gates and target accuracy (en-
tanglement fidelity) in determining the needed T state fidelity.
To better understand the impact of decomposing arbi-
trary rotations on the fidelity of a quantum circuit, we
consider the following. We have a circuit with a total of
G rotation gates, and we aim to achieve a final infidelity
of the circuit I. Thus one can write,
I ≥1 −(1 −I(ϵT , δopt))G .
(18)
From this one can obtain a maximum value of ϵT
that achieves a target infidelity for the circuit.
Fig. 4
shows the T state fidelity required to achieve a target
QAOA+AA circuit infidelities I for different numbers of
phase gates G. We consider two different decomposition
schemes and two different target entanglement fidelities
for the calculations. Fig. 4 suggests a significant depen-
dence on the number of gates G and target accuracy 1−I
in determining the needed T state fidelity 1 −ϵT .
C.
Resource requirements for the k-SAT QAOA
phaser
Here we consider the spacetime cost of applying the
QAOA phaser for 8-SAT, which is the dominant cost of
the k-SAT QAOA+AA circuit as sketched out in Fig. 1
of the main text. The k-SAT phaser is
UC(γ) = e−iγHC =
m
Y
j=1
Uj(γ),
(19)
where
Uj(γ) =
X
x∈{ 0,1 }n
e−iγCj(x) |x⟩⟨x| ,
(20)
is an exponentiated clause that can be converted into a
k-qubit phase gate Pk(γ) = eiγ|1⟩⟨1|⊗k by appropriately


11
conjugating qubits that are negated in Cj by Pauli-X
gates.
For brevity, we henceforth keep the value of γ
arbitrary but fixed, and suppress the explicit dependence
of UC(γ), Uj(γ), and derived objects on γ.
We say that a circuit V is Z-equivalent to the unitary
U if the action of U is equal to the action of V followed
by single-qubit Pauli-Z corrections that can be efficiently
computed from the outcomes of measurements performed
in V . For the purposes of the statements below, we de-
fine a logical cycle to be the time required to perform one
logical two-qubit Pauli operator measurement. In prac-
tice, one logical cycle in a distance-d surface code on a
square lattice with nearest-neighbor interactions is the
time required to perform d rounds of syndrome measure-
ment [82]. The key technical result that we leverage to
bound the resource requirements of the k-SAT phaser UC
is the following:
Theorem IV.2. The K-qubit phase gate PK(γ)
=
eiγ|1⟩⟨1|⊗K is Z-equivalent to a circuit that addresses
the K qubits of PK(γ) for one logical cycle, introduces
⌊13
2 K⌋ancilla qubits, consumes P⌈log2 K⌉
ℓ=1
⌊K/2ℓ⌋≤K−1
CCZ states, and can be implemented in a total of nP +
4⌈log2 K⌉logical cycles, where nP is the number of log-
ical cycles required to implement the single-qubit phase
gate P1(γ).
We prove this theorem by construction in Appendix B.
Let Qj be the set of qubits that correspond to the vari-
ables addressed in the clause Cj. Since all exponentiated
clauses Uj are diagonal in the computational basis, in
order to implement the phaser UC it is sufficient to im-
plement each exponentiated clause Uj by a Z-equivalent
circuit Vj, and defer all Pauli-Z corrections to the end of
VC = Q
j Vj. We refer to the circuit Vj as a task, and we
say that task Vj has been dispatched once all of the the
gates in Vj that address qubits in Qj have been applied.
Let LogicalDepth(W) denote the total number of log-
ical cycles required to implement the circuit W.
We
say that a partition C = { C1, C2, · · · , Cc } of the k-SAT
clauses C = { C1, · · · , Cm } is disjoint if each part Cℓ⊂C
consists of clauses that address mutually disjoint sets
of qubits, which is to say that if Ci, Cj ∈Cℓ, then
|Qi ∩Qj| = 0. Theorem IV.2 implies that
Corollary IV.1. A circuit VC = Q
j Vj in which Vj is
Z-equivalent to the exponentiated k −SAT clause Uj can
be implemented in LogicalDepth(VC) ≤c+nP +4⌈log2 k⌉
logical cycles, where c is the size of a disjoint partition
partition of C.
The basic idea here is that a disjoint partition C
of C induces a schedule VC = (V1, V2, · · · , Vc), where
Vℓ= { Vi : Ci ∈Cℓ} is a collection of tasks that can
be executed in parallel in one logical cycle. It therefore
takes c logical cycles to sequentially dispatch all tasks in
VC according to the schedule VC. The additional contri-
bution of nP + 4⌈log2 k⌉in Corollary IV.1 accounts for
the time required for the first task prior to dispatching,
and the last task after dispatching. For the 8-SAT in-
stances considered in the main text, c ≫nP + 4⌈log2 k⌉,
so LogicalDepth(VC) ≈c ≈12r = 2112.
D.
Target distance of the surface code
To determine the target distance of the surface code for
the QAOA+AA algorithm applied to 8-SAT, we consider
the physical error rate pph and the total number of non-
Clifford gates G in the circuit. The final infidelity of I
the circuit is conservatively bounded by:
I ≤1 −F(pph)G
(21)
where the fidelity function F(pph) is approximately given
by:
F(pph) ≈1 −
pph
pth
d/2
.
(22)
Here pth ≈10−2 is the threshold error rate for the surface
code. For a target infidelity Itar, we therefore solve these
expressions for d in the limits that Itar, 1 −F(pph) ≪1,
and set the code distance to
d =
2 log(Itar/G)
log(pph/pth)

.
(23)
We set Itar = 0.99 and pph/pth = 0.1 in the main text.
E.
Number of surface code decoders
To determine the number of surface-code decoders re-
quired by the QAOA+AA algorithm, we first assign one
decoder to each logical data and ancilla qubit. Recogniz-
ing that resource-state factories may require more com-
plex processing, as a heuristic we assign 10 decoders to
each resource-state factory, in total setting
ndecoders = n + nancilla + 10 × nfac.
(24)
F.
Classical solvers for random 8-SAT
a.
SAT and random k-SAT
As the first problem
known to be NP-complete [83], the Boolean satisfiability
problem (SAT) is a fundamental challenge in mathemat-
ics and computer science, with wide-ranging applications
in hardware verification [84], motion planning [85], dis-
crete optimization [86], machine learning [87] and quan-
tum computing [88].
A SAT formula is conventionally represented in the
conjunctive normal form (CNF). A (CNF) k-SAT prob-
lem instance on n Boolean variables x1, · · · , xn is a con-
junction (AND, ∧) of m clauses, where each clause is a
disjunction (OR, ∨) of k literals and a literal is a Boolean
variable or its negation. An example for a 3-SAT formula


12
with n = 4, m = 2 is (x1 ∨x2 ∨x4) ∧(¬x2 ∨x3 ∨¬x4).
A clause is satisfied if at least one of its literals is. A for-
mula is satisfied by an assignment of Boolean variables
if all of its clauses are satisfied. The formula above is
satisfied by x1 = x2 = x3 = x4 = 1.
Random (CNF) k-SAT is an important and well-
studied family of SAT benchmarks, where each clause
consists of k random literals.
The clause-variable ra-
tio, denoted by α, plays a critical role in random k-SAT
problems.
It is observed experimentally that the ran-
dom k-SAT problem goes through a satisfiability phase-
transition as α increases [89]. It is conjectured that the
phase-transition is sharp, which is to say that if fn,k,α is a
random k-SAT formula with n variables and αn clauses,
then there exists a constant αk for which the probability
P[SAT(fn,k,α)] that fn,k,α is satisfiable behaves as
lim
n→∞P[SAT(fn,k,α)] =
(
1
α < αk
0
α > αk
.
The conjuncture has been proven for k = 2 [90, 91] and
large k by the landmark work in Ref. [92]. Experiments
indicate that formulas close to the threshold αk are es-
pecially challenging for practical SAT solvers [93].
b.
Benchmark generation
This work focuses on ran-
dom 8-CNF benchmarks near the satisfiability threshold
α8, which is experimentally observed to be approximately
176 [1]. Each problem is formed by generating 176n ran-
dom OR-clauses where each clause consists of 8 literals
chosen uniformly (with replacement) from { x1, · · · , xn }
and negated with probability 1/2. For each instance gen-
erated, we use the complete solver Kissat [94] to prove
that it is satisfiable; if the instance is not satisfiable, it is
discarded. For each value of n ranging from 30, 31, . . .,
70, at least 70 satisfiable instances were generated.
c.
Experiment configurations
The time limit is set
to 1000 seconds for all problem instances. The experi-
ment is conducted on an AMD EPYC 7R32 CPU with
48 cores and a TDP of 280W.
d.
Solvers Selection
SAT solvers are typically clas-
sified into complete and incomplete solvers.
Complete
solvers are able to determine the satisfiability of such for-
mulas by either giving a satisfying assignment or proving
unsatisfiability.
State-of-the-art complete SAT solvers
based on Conflict-Driven Clause Learning (CDCL) [95],
e.g., Kissat [94] and MapleSAT [96], are dominant in solv-
ing industrial SAT instances. Incomplete solvers based
on (stochastic) local search (SLS) [97, 98] and message
passing (MP) [99] offer a practical alternative by con-
ducting unstructed search, moving quickly in the Boolean
cube to decrease the number of unsatisfied clauses. They
haven shown promise in promptly solving satisfiable large
random instances [100].
We included five state-of-the-art incomplete SAT
solvers in the evaluation of classic SAT solvers:
• probSAT [54], a local search based SAT solver built
on WalkSAT with probabilistic variable selection
heuristics.
• yalSAT [49], the winner of the random track of SAT
Competition (SC) 2017 [50] built based on prob-
SAT.
• Dimetheus [51], a solver combining SLS and MP
techniques and the winner of the random track in
SC 2016 [52].
• Sparrow [31], the winner of the random track of SC
2018 [48].
• WalkSATlm [55], a solver combines the classic
WalkSAT solver with tie-breaking heuristics.
We also considered the following SAT solvers but did
not include them in the evaluation, including SOTA com-
plete solvers MapleSAT and Kissat, incomplete solvers
WalkSAT [101] and Survey Propagation [102]. They are,
however, outperformed by the solvers in the evaluation
by a large margin.
G.
Parallelizing classical solvers for 8-SAT
The local search solvers that are most performant
for random SAT can be straightforwardly parallelized
by running many independent local searches in parallel.
Since no communication is required between independent
local searches, the runtime for a parallelized search can
be predicted by analyzing the distribution of runtimes for
one local search. Specifically, if ncores searches are exe-
cuted in parallel, they can all be terminated as soon as
one of them finishes, so the expected runtime for ncores
searches is the minimum over ncores samples from the
distribution of runtimes for a single search.
Ref. [32] uses this insight to analyze the performance
of Sparrow and predict how it scales to large supercom-
puters. Specifically, they benchmark Sparrow on random
instances from SAT competitions and find that the run-
ning times follow shifted exponential distribution for eas-
ier random instances and lognormal for harder ones. To
make a conservative assumption for our crossover point,
we choose the random instance with the most favorable
classical scaling from Ref. [32], namely Rand-9. The dis-
tributions of runtimes for this instances is the shifted
exponential distribution fY (t) = λe−λ(t−x0) with param-
eters λ = 9.8 × 10−4 and x0 = 6.8. We then use the
model from Ref. [32] to obtain a speedup from paral-
lelization with ncores. Finally, we divide the measured
serial runtime of Sparrow by this speedup factor, obtain-
ing the estimated parallel runtime.
Acknowledgements
The authors thank Pradeep Niroula for helpful discus-
sions about the overhead of fixed-point amplitude ampli-
fication. The authors thank their colleagues at the Global
Technology Applied Research center of JPMorganChase
for support.


13
Data availability
The data for this work is available at 10.5281/zen-
odo.15122122.
[1] S. Boulebnane and A. Montanaro, Solving boolean sat-
isfiability problems with the quantum approximate op-
timization algorithm, PRX Quantum 5, 030348 (2024).
[2] A. Abbas, A. Ambainis, B. Augustino, A. Bärtschi,
H. Buhrman, C. Coffrin, G. Cortiana, V. Dunjko, D. J.
Egger, B. G. Elmegreen, N. Franco, F. Fratini, B. Fuller,
J. Gacon, C. Gonciulea, S. Gribling, S. Gupta, S. Had-
field, R. Heese, G. Kircher, T. Kleinert, T. Koch, G. Ko-
rpas, S. Lenk, J. Marecek, V. Markov, G. Mazzola,
S. Mensa, N. Mohseni, G. Nannicini, C. O’Meara, E. P.
Tapia, S. Pokutta, M. Proissl, P. Rebentrost, E. Sahin,
B. C. B. Symons, S. Tornow, V. Valls, S. Woerner, M. L.
Wolf-Bauwens, J. Yard, S. Yarkoni, D. Zechiel, S. Zhuk,
and C. Zoufal, Challenges and opportunities in quan-
tum optimization, Nature Reviews Physics 6, 718–735
(2024).
[3] Y. Alexeev, D. Bacon, K. R. Brown, R. Calderbank,
L. D. Carr, F. T. Chong, B. DeMarco, D. Englund,
E. Farhi, B. Fefferman, A. V. Gorshkov, A. Houck,
J. Kim, S. Kimmel, M. Lange, S. Lloyd, M. D. Lukin,
D. Maslov, P. Maunz, C. Monroe, J. Preskill, M. Roet-
teler, M. J. Savage, and J. Thompson, Quantum com-
puter systems for scientific discovery, PRX Quantum 2,
10.1103/prxquantum.2.017001 (2021).
[4] D. Herman, C. Googin, X. Liu, Y. Sun, A. Galda,
I. Safro, M. Pistoia, and Y. Alexeev, Quantum com-
puting for finance, Nature Reviews Physics 5, 450–465
(2023).
[5] Christoph Dürr and Peter Høyer, A quantum algorithm
for
finding
the
minimum,
arXiv:quant-ph/9607014
10.48550/arXiv.quant-ph/9607014 (1996).
[6] A. Montanaro, Quantum-walk speedup of backtracking
algorithms, Theory Of Computing 14, 1 (2018).
[7] A. Montanaro, Quantum speedup of branch-and-bound
algorithms, Physical Review Research 2, 013056 (2020).
[8] S. Chakrabarti, P. Minssen, R. Yalovetzky, and M. Pis-
toia,
Universal
quantum
speedup
for
branch-and-
bound,
branch-and-cut,
and tree-search algorithms,
arXiv:2210.03210 10.48550/ARXIV.2210.03210 (2022).
[9] R. D. Somma, S. Boixo, H. Barnum, and E. Knill, Quan-
tum simulations of classical annealing processes, Physi-
cal Review Letters 101, 10.1103/physrevlett.101.130504
(2008).
[10] P. Wocjan and A. Abeyesinghe, Speedup via quan-
tum sampling, Physical Review A 78, 10.1103/phys-
reva.78.042336 (2008).
[11] M. B. Hastings, A short path quantum algorithm for
exact optimization, Quantum 2, 78 (2018).
[12] A. M. Dalzell, N. Pancotti, E. T. Campbell, and F. G.
Brandão, Mind the gap: Achieving a super-grover quan-
tum speedup by jumping to the end, in Proceedings of
the ACM Symposium on Theory of Computing (2023)
p. 1131–1144.
[13] S. Chakrabarti, D. Herman, G. Ozgul, S. Zhu, B. Au-
gustino, T. Hao, Z. He, R. Shaydulin, and M. Pis-
toia, Generalized short path algorithms: Towards super-
quadratic speedup over markov chain search for combi-
natorial optimization, arXiv:2410.23270 (2024).
[14] A. Montanaro and L. Zhou, Quantum speedups in solv-
ing near-symmetric optimization problems by low-depth
qaoa, arXiv:2411.04979 (2024).
[15] S. P. Jordan, N. Shutty, M. Wootters, A. Zalcman,
A. Schmidhuber, R. King, S. V. Isakov, and R. Bab-
bush, Optimization by decoded quantum interferome-
try, arXiv:2408.08292 (2024).
[16] E. Farhi, S. Gutmann, D. Ranard, and B. Villalonga,
Lower bounding the maxcut of high girth 3-regular
graphs using the qaoa, arXiv:2503.12789 (2025).
[17] R. Babbush, J. R. McClean, M. Newman, C. Gid-
ney, S. Boixo, and H. Neven, Focus beyond quadratic
speedups for error-corrected quantum advantage, PRX
Quantum 2, 010103 (2021).
[18] Y. R. Sanders, D. W. Berry, P. C. Costa, L. W. Tessler,
N. Wiebe, C. Gidney, H. Neven, and R. Babbush, Com-
pilation of fault-tolerant quantum heuristics for combi-
natorial optimization, PRX Quantum 1, 020312 (2020).
[19] E. Campbell, A. Khurana, and A. Montanaro, Applying
quantum algorithms to constraint satisfaction problems,
Quantum 3, 167 (2019).
[20] A. M. Dalzell, B. D. Clader, G. Salton, M. Berta,
C. Y.-Y. Lin, D. A. Bader, N. Stamatopoulos, M. J. A.
Schuetz, F. G. S. L. Brandão, H. G. Katzgraber, and
W. J. Zeng, End-to-end resource analysis for quantum
interior-point methods and portfolio optimization, PRX
Quantum 4, 10.1103/prxquantum.4.040325 (2023).
[21] M.
Brehm
and
J.
Weggemans,
Assessing
fault-
tolerant quantum advantage for k-sat with structure,
arXiv:2412.13274 (2024).
[22] T. Hogg and D. Portnov, Quantum optimization, Infor-
mation Sciences 128, 181–197 (2000).
[23] T. Hogg, Quantum search heuristics, Physical Review
A 61, 10.1103/physreva.61.052311 (2000).
[24] E. Farhi, J. Goldstone, and S. Gutmann, A quantum
approximate optimization algorithm, arXiv preprint
arXiv:1411.4028 (2014).
[25] R. Shaydulin, C. Li, S. Chakrabarti, M. DeCross,
D. Herman, N. Kumar, J. Larson, D. Lykov, P. Minssen,
Y. Sun, Y. Alexeev, J. M. Dreiling, J. P. Gaebler,
T. M. Gatterman, J. A. Gerber, K. Gilmore, D. Gresh,
N. Hewitt, C. V. Horst, S. Hu, J. Johansen, M. Math-
eny, T. Mengle, M. Mills, S. A. Moses, B. Neyenhuis,
P. Siegfried, R. Yalovetzky, and M. Pistoia, Evidence
of scaling advantage for the quantum approximate opti-
mization algorithm on a classically intractable problem,
Science Advances 10, 10.1126/sciadv.adm6761 (2024).
[26] R. Shaydulin and M. Pistoia, Qaoa with n · p ≥200, in
2023 IEEE Int. Conf. Quantum Comput. Eng. (IEEE,
2023) p. 1074–1077.
[27] E. Pelofske, A. Bärtschi, and S. Eidenbenz, Quantum
annealing vs. QAOA: 127 qubit higher-order ising prob-


14
lems on NISQ computers, in Lecture Notes in Computer
Science (Springer Nature Switzerland, 2023) pp. 240–
258.
[28] E. Pelofske, A. Bärtschi, L. Cincio, J. Golden, and S. Ei-
denbenz, Scaling whole-chip qaoa for higher-order ising
spin glass models on heavy-hex graphs, npj Quantum
Information 10, 10.1038/s41534-024-00906-w (2024).
[29] Z. He, D. Amaro, R. Shaydulin, and M. Pistoia, Per-
formance of quantum approximate optimization with
quantum error detection, arXiv:2409.12104 (2024).
[30] B. Tasseff, T. Albash, Z. Morrell, M. Vuffray, A. Y.
Lokhov, S. Misra, and C. Coffrin, On the emerging
potential of quantum annealing hardware for combina-
torial optimization, Journal of Heuristics 30, 325–358
(2024).
[31] A. Balint, Engineering stochastic local search for the sat-
isfiability problem, Ph.D. thesis, Universität Ulm (2014).
[32] A. Arbelaez, C. Truchet, and P. Codognet, Using se-
quential runtime distributions for the parallel speedup
prediction of sat local search, Theory and Practice of
Logic Programming 13, 625 (2013).
[33] B. Barber, K. M. Barnes, T. Bialas, O. Buğdaycı, E. T.
Campbell, N. I. Gillespie, K. Johar, R. Rajan, A. W.
Richardson, L. Skoric, C. Topal, M. L. Turner, and A. B.
Ziad, A real-time, scalable, fast and resource-efficient
decoder for a quantum computer, Nature Electronics 8,
84–91 (2025).
[34] C. Gidney, N. Shutty, and C. Jones, Magic state culti-
vation: growing t states as cheap as cnot gates, arXiv
preprint arXiv:2409.17595 (2024).
[35] H. Zhou, C. Zhao, M. Cain, D. Bluvstein, C. Duckering,
H.-Y. Hu, S.-T. Wang, A. Kubica, and M. D. Lukin,
Algorithmic fault tolerance for fast quantum computing,
arXiv preprint arXiv:2406.17653 (2024).
[36] TOP500, Top500 supercomputer sites, https://www.
top500.org/ (2025), accessed: 2025-03-19.
[37] Y. Wu and L. Zhong, Fusion blossom:
Fast mwpm
decoders for qec, in 2023 IEEE International Confer-
ence on Quantum Computing and Engineering (QCE)
(IEEE, 2023) p. 928–938.
[38] O. Higgott and C. Gidney, Sparse blossom: correcting
a million errors per core second with minimum-weight
matching, Quantum 9, 1600 (2025).
[39] D. Litinski, Magic state distillation: Not as costly as
you think, Quantum 3, 205 (2019).
[40] A. Coja-Oghlan, Random constraint satisfaction prob-
lems, Electronic Proceedings in Theoretical Computer
Science 9, 32–37 (2009).
[41] G. Dequen and O. Dubois, An efficient approach to solv-
ing random k-sat problems, Journal of Automated Rea-
soning 37, 261 (2006).
[42] R. Marino, G. Parisi, and F. Ricci-Tersenghi, The back-
tracking survey propagation algorithm for solving ran-
dom k-sat problems, Nature communications 7, 12996
(2016).
[43] A. Coja-Oghlan, A better algorithm for random k-sat,
SIAM Journal on Computing 39, 2823 (2010).
[44] A. S. M. Aguirre and M. Vardi, Random 3-sat and bdds:
The plot thickens further, in Principles and Practice of
Constraint Programming—CP 2001: 7th International
Conference, CP 2001 Paphos, Cyprus, November 26–
December 1, 2001 Proceedings 7 (Springer, 2001) pp.
121–136.
[45] E. Campos, S. E. Venegas-Andraca, and M. Lanzagorta,
Quantum tunneling and quantum walks as algorithmic
resources to solve hard k-sat instances, Scientific Re-
ports 11, 10.1038/s41598-021-95801-1 (2021).
[46] B. Zhang, A. Sone, and Q. Zhuang, Quantum computa-
tional phase transition in combinatorial problems, npj
Quantum Information 8, 87 (2022).
[47] S. Boulebnane, M. Ciudad-Alañón, L. Mineh, A. Mon-
tanaro, and N. Vaishnav, Applying the quantum ap-
proximate optimization algorithm to general constraint
satisfaction problems, arXiv:2411.17442 (2024).
[48] M. J. Heule, M. Järvisalo, and M. Suda, Sat competition
2018, Journal on Satisfiability, Boolean Modelling and
Computation 11, 133 (2019).
[49] A. Biere, Splatz, lingeling, plingeling, treengeling, yalsat
entering the sat competition 2016, Proc. of SAT Com-
petition 14, 316 (2016).
[50] T. Balyo, M. J. Heule, and M. Järvisalo, Sat competi-
tion 2017.
[51] O. Gableske, S. Müelich, and D. Diepold, On the per-
formance of cdcl-based message passing inspired deci-
mation using ρσpmpi, in Pragmatics of SAT Workshop
(2013).
[52] T. Balyo, M. Heule, and M. Jarvisalo, Sat competition
2016: Recent developments, in Proceedings of the AAAI
Conference on Artificial Intelligence, Vol. 31 (2017).
[53] M. J. Heule, M. Järvisalo, and M. Suda, Benchmark
selection of sat race 2019, SAT RACE 2019 , 46 (2019).
[54] A. Balint and U. Schöning, Choosing probability dis-
tributions for stochastic local search and the role of
make versus break, in International Conference on The-
ory and Applications of Satisfiability Testing (Springer,
2012) pp. 16–29.
[55] S. Cai, K. Su, and C. Luo, Improving walksat for ran-
dom k-satisfiability problem with k> 3, in Proceedings of
the AAAI Conference on Artificial Intelligence, Vol. 27
(2013) pp. 145–151.
[56] H. Fu, J. Liu, G. Wu, Y. Xu, and G. Sutcliffe, Im-
proving probability selection based weights for satisfia-
bility problems, Knowledge-based systems 245, 108572
(2022).
[57] S. Cai, http://lcs.ios.ac.cn/~caisw/SAT.html.
[58] G. Brassard, P. Hoyer, M. Mosca, and A. Tapp, Quan-
tum amplitude amplification and estimation, arXiv
preprint quant-ph/0005055 (2000).
[59] D. Horsman, A. G. Fowler, S. Devitt, and R. Van Me-
ter, Surface code quantum computing by lattice surgery,
New Journal of Physics 14, 123011 (2012).
[60] C. Gidney and M. Ekerå, How to factor 2048 bit rsa in-
tegers in 8 hours using 20 million noisy qubits, Quantum
5, 433 (2021).
[61] V. Kliuchnikov, K. Lauter, R. Minko, A. Paetznick, and
C. Petit, Shorter quantum circuits via single-qubit gate
approximation, Quantum 7, 1208 (2023).
[62] D. Litinski and N. Nickerson, Active volume: An ar-
chitecture for efficient fault-tolerant quantum comput-
ers with limited non-local connections, arXiv preprint
arXiv:2211.15465 (2022).
[63] A. Hagberg, P. J. Swart, and D. A. Schult, Exploring
network structure, dynamics, and function using net-
workx (Los Alamos National Laboratory (LANL), Los
Alamos, NM (United States), 2008).
[64] V. G. Vizing, On an estimate of the chromatic class of
a p-graph, Diskret analiz 3, 25 (1964).


15
[65] Y. Ye, J. B. Kline, S. Chen, A. Yen, and K. P. O’Brien,
Ultrafast superconducting qubit readout with the quar-
ton coupler, Science Advances 10, eado9094 (2024).
[66] R. Acharya, L. Aghababaie-Beni, I. Aleiner, T. I. Ander-
sen, M. Ansmann, F. Arute, K. Arya, A. Asfaw, N. As-
trakhantsev, J. Atalaya, et al., Quantum error correc-
tion below the surface code threshold, arXiv preprint
arXiv:2408.13687 (2024).
[67] W.-J.
Lin,
H.
Cho,
Y.
Chen,
M.
G.
Vavilov,
C. Wang, and V. E. Manucharyan, 24 days-stable cnot-
gate on fluxonium qubits with over 99.9% fidelity,
arXiv:2407.15783 (2024).
[68] C. M. Löschnauer, J. M. Toba, A. C. Hughes, S. A.
King, M. A. Weber, R. Srinivas, R. Matt, R. Nour-
shargh, D. T. C. Allcock, C. J. Ballance, C. Matthiesen,
M. Malinowski, and T. P. Harty, Scalable,
high-
fidelity all-electronic control of trapped-ion qubits,
arXiv:2407.07694 (2024).
[69] V. Kliuchnikov and E. Schoute, Minimal entanglement
for injecting diagonal gates (2024), arXiv:2403.18900
[quant-ph].
[70] C. Gidney and A. G. Fowler, Efficient magic state fac-
tories with a catalyzed |CCZ⟩to 2|T⟩transformation,
Quantum 3, 135 (2019).
[71] N. P. Breuckmann and J. N. Eberhardt, Quantum
low-density
parity-check
codes,
PRX
Quantum
2,
10.1103/prxquantum.2.040101 (2021).
[72] S. Yoshida, S. Tamiya, and H. Yamasaki, Concatenate
codes, save qubits (2024), arXiv:2402.09606 [quant-ph].
[73] H.
Goto,
High-performance
fault-tolerant
quantum
computing with many-hypercube codes, Science Ad-
vances 10, eadp6388 (2024).
[74] P. Panteleev and G. Kalachev, Degenerate quantum
ldpc codes with good finite length performance, Quan-
tum 5, 585 (2021).
[75] A. Cowtan, Z. He, D. J. Williamson, and T. J. Yoder,
Parallel logical measurements via quantum code surgery
(2025), arXiv:2503.05003 [quant-ph].
[76] A. Schmidhuber, R. O’Donnell, R. Kothari, and R. Bab-
bush, Quartic quantum speedups for planted inference,
arXiv:2406.19378 (2024).
[77] M. B. Hastings, Classical and quantum algorithms for
tensor principal component analysis, Quantum 4, 237
(2020).
[78] S. Boulebnane, J. Sud, R. Shaydulin, and M. Pis-
toia, Equivalence of quantum approximate optimiza-
tion algorithm and linear-time quantum annealing for
the sherrington-kirkpatrick model, arXiv:2503.09563
(2025).
[79] C. M. Dawson and M. A. Nielsen, The solovay-kitaev
algorithm, arXiv:quant-ph/0505030 (2005).
[80] N. J. Ross and P. Selinger, Optimal ancilla-free clif-
ford+t approximation of z-rotations, Quantum Info.
Comput. 16, 901–953 (2016).
[81] A. Bocharov, M. Roetteler, and K. M. Svore, Efficient
synthesis of universal repeat-until-success quantum cir-
cuits, Phys. Rev. Lett. 114, 080502 (2015).
[82] D. Litinski, A game of surface codes: Large-scale quan-
tum computing with lattice surgery, Quantum 3, 128
(2019).
[83] R. M. Karp, Reducibility among combinatorial prob-
lems, in 50 Years of Integer Programming 1958-2008:
from the Early Years to the State-of-the-Art (Springer,
2009) pp. 219–241.
[84] A. Gupta, M. K. Ganai, and C. Wang, Sat-based ver-
ification methods and applications in hardware verifi-
cation, in International School on Formal Methods for
the Design of Computer, Communication and Software
Systems (Springer, 2006) pp. 108–143.
[85] F. Imeson and S. L. Smith, An smt-based approach to
motion planning for multiple robots with complex con-
straints, IEEE Transactions on Robotics 35, 669 (2019).
[86] M. J. Heule, O. Kullmann, and V. W. Marek, Solv-
ing and verifying the boolean pythagorean triples prob-
lem via cube-and-conquer, in International Conference
on Theory and Applications of Satisfiability Testing
(Springer, 2016) pp. 228–245.
[87] T. Baluta, S. Shen, S. Shinde, K. S. Meel, and P. Sax-
ena, Quantitative verification of neural networks and its
security applications, in Proceedings of the 2019 ACM
SIGSAC Conference on Computer and Communications
Security (2019) pp. 1249–1264.
[88] M. Y. Vardi and Z. Zhang, Solving quantum-inspired
perfect matching problems via tutte-theorem-based hy-
brid boolean constraints, in Proceedings of the Thirty-
Second International Joint Conference on Artificial In-
telligence (2023) pp. 2039–2048.
[89] J. M. Crawford and L. D. Auton, Experimental results
on the crossover point in random 3-sat, Artificial intel-
ligence 81, 31 (1996).
[90] A. Goerdt, A threshold for unsatisfiability, in Inter-
national Symposium on Mathematical Foundations of
Computer Science (Springer, 1992) pp. 264–274.
[91] B. Reed, Mick gets some (the odds are on his side), in
Proceedings of the 32nd IEEE Symposium on Founda-
tionsof Computer Science, pp. 620–626.
[92] J. Ding, A. Sly, and N. Sun, Proof of the satisfiability
conjecture for large k, in Proceedings of the forty-seventh
annual ACM symposium on Theory of computing (2015)
pp. 59–68.
[93] G. Bresler and B. Huang, The algorithmic phase tran-
sition of random k-sat for low degree polynomials, in
2021 IEEE 62nd annual symposium on foundations of
computer science (FOCS) (IEEE, 2022) pp. 298–309.
[94] M. J. Heule, M. Iser, M. Järvisalo, and M. Suda, Pro-
ceedings of sat competition 2024: Solver, benchmark
and proof checker descriptions, in Proceedings of the
SAT Competition (Department of Computer Science,
University of Helsinki, 2024).
[95] A. Biere, M. Heule, H. van Maaren, and T. Walsh,
Conflict-driven clause learning sat solvers, Handbook
of Satisfiability, Frontiers in Artificial Intelligence and
Applications , 131 (2009).
[96] A. Biere, Cadical, lingeling, plingeling, treengeling and
yalsat entering the sat competition 2018, Proceedings of
SAT Competition 14, 316 (2017).
[97] H. Hoos, Stochastic local search-methods, models, appli-
cations (Ios Press, 1999).
[98] A. Kyrillidis, M. Vardi, and Z. Zhang, On continuous lo-
cal bdd-based search for hybrid sat solving, in Proceed-
ings of the AAAI Conference on Artificial Intelligence,
Vol. 35 (2021) pp. 3841–3850.
[99] L. Kroc, A. Sabharwal, and B. Selman, Message-passing
and local heuristics as decimation strategies for satisfi-
ability, in Proceedings of the 2009 ACM symposium on
Applied Computing (2009) pp. 1408–1414.
[100] J.-H. Lorenz and F. Wörz, On the effect of learned
clauses on stochastic local search, in Theory and Ap-


16
plications of Satisfiability Testing–SAT 2020: 23rd In-
ternational Conference, Alghero, Italy, July 3–10, 2020,
Proceedings 23 (Springer, 2020) pp. 89–106.
[101] B. Selman, H. A. Kautz, B. Cohen, et al., Local search
strategies for satisfiability testing., Cliques, coloring,
and satisfiability 26, 521 (1993).
[102] A. Braunstein, M. Mézard, and R. Zecchina, Survey
propagation: An algorithm for satisfiability, Random
Structures & Algorithms 27, 201 (2005).
[103] M. A. Nielsen, The entanglement fidelity and quan-
tum error correction, arXiv preprint quant-ph/9606012
10.48550/arXiv.quant-ph/9606012 (1996).
[104] B. Schumacher, Sending entanglement through noisy
quantum channels, Phys. Rev. A 54, 2614 (1996).
[105] P. Selinger, Efficient clifford+ t approximation of single-
qubit operators, arXiv preprint arXiv:1212.6253 (2012).
[106] M. B. Hastings, Turning gate synthesis errors into inco-
herent errors, arXiv preprint arXiv:1612.01011 (2016).
[107] N. Wiebe and M. Roetteler, Quantum arithmetic and
numerical analysis using repeat-until-success circuits,
arXiv preprint arXiv:1406.2040 (2014).
[108] C. Vuillot, L. Lao, B. Criger, C. G. Almudéver, K. Ber-
tels, and B. M. Terhal, Code deformation and lattice
surgery are gauge fixing, New Journal of Physics 21,
033028 (2019).
Disclaimer
This paper was prepared for informational purposes by
the Global Technology Applied Research center of JP-
MorganChase. This paper is not a product of the Re-
search Department of JPMorganChase or its affiliates.
Neither JPMorganChase nor any of its affiliates makes
any explicit or implied representation or warranty and
none of them accept any liability in connection with
this position paper, including, without limitation, with
respect to the completeness, accuracy, or reliability of
the information contained herein and the potential le-
gal, compliance, tax, or accounting effects thereof. This
document is not intended as investment research or in-
vestment advice, or as a recommendation, offer, or solic-
itation for the purchase or sale of any security, financial
instrument, financial product or service, or to be used in
any way for evaluating the merits of participating in any
transaction.
A.
Entanglement Fidelity
Entanglement fidelity measures how well the state of a system and its entanglement with other systems is preserved
under the action of a quantum channel. The sensitivity of entanglement fidelity to the entanglement between systems
makes it a better measure of how well a state is preserved under the action of a channel than other measures, such as
gate fidelity, in the context of error-corrected quantum computation [103]. Mathematically, the entanglement fidelity
Fent(E) of a quantum channel E that acts on density operators of a d-dimensional Hilbert space is [104]
Fent(E) = ⟨ϕ|(E ⊗I)(|ϕ⟩⟨ϕ|)|ϕ⟩= Tr [Πϕ(E ⊗I)(Πϕ)] ,
(A1)
where |ϕ⟩=
1
√
d
Pd−1
a=0 |a⟩⊗|a⟩is a maximally entangled state of two d-dimensional systems, Πϕ = |ϕ⟩⟨ϕ| is a projector
onto |ϕ⟩, and I is the identity channel. When a fixed channel acts E on a particular state ρ, we may refer to Fent(E)
as the fidelity of ρ after the application of E.
Consider the depolarizing channel Dp that replaces its input by the maximally mixed state σ = 1
d
Pd−1
a=0 |a⟩⟨a| with
probability p,
Dp(ρ) = (1 −p)ρ + pσ.
(A2)
Theorem A.1. The entanglement fidelity of a quantum state after n applications of the depolarizing channel Dp is
Fent(Dn
p ) =

1 −1
d2

(1 −p)n + 1
d2 .
(A3)
Proof. Expanding Πϕ = 1
d
Pd−1
a,b=0 |a⟩⟨b| ⊗|a⟩⟨b|, the action of Dp,0 = Dp ⊗I on Πϕ is
Dp,0(Πϕ) = (1 −p)Πϕ + p × 1
d
X
a,b
σ ⊗|a⟩⟨b| = (1 −p)Πϕ + pσ ⊗ω
(A4)
where ω = |+⟩⟨+| is the density operator of the uniform superposition |+⟩=
1
√
d
Pd−1
a=0 |a⟩. The depolarizing channel
acts trivially on an already depolarized input, which is to say that
Dp,0(σ ⊗ω) = σ ⊗ω.
(A5)


17
Applying the depolarizing channel n times to the maximally mixed state Πϕ thus yields the state
Dn
p,0(Πϕ) = (1 −p)nΠϕ + qn(p)σ ⊗ω,
(A6)
where the coefficient qn(p) can be found be enforcing that the n-fold depolarized state has trace 1,
1 = Tr

Dn
p,0(Πϕ)

= (1 −p)n + qn(p),
(A7)
which implies that qn(p) = 1 −(1 −p)n. Altogether, the entanglement fidelity of the n-fold depolarization channel is
Fent(Dn
p ) = Tr [ΠϕDp,0(Πϕ)] = (1 −p)n + qn(p) Tr [Πϕ(σ ⊗ω)] ,
(A8)
where
Tr [Πϕ(σ ⊗ω)] = 1
d3
X
a,b,i,j,k
Tr[(|a⟩⟨b| ⊗|a⟩⟨b|)(|i⟩⟨i| ⊗|j⟩⟨k|)]
(A9)
= 1
d3
X
a,b,i,j,k
Tr[|a⟩⟨b| |i⟩⟨i|] × Tr[|a⟩⟨b| |j⟩⟨k|]
(A10)
= 1
d2 ,
(A11)
so
Fent(Dn
p ) = (1 −p)n + (1 −(1 −p)n) 1
d2 = d2 −1
d2
(1 −p)n + 1
d2 .
(A12)
1.
Entanglement Fidelity and Operator Norm
It is common in the (deterministic) unitary gate synthesis literature to consider the operator-norm distance
D(U, V ) = ∥U −V ∥as a measure of similarity between two unitaries U and V , where ∥W∥is the largest singu-
lar value of W [80, 105–107]. When synthesizing a gate up to global phase, it is convenient to instead consider the
phase-agnostic distance
˜D(U, V ) = min
α D(U, eiαV ) = min
α
U −eiαV
.
(A13)
Here we establish the relationship between the phase-agnostic operator-norm distance ˜D(U, V ) and the entanglement
fidelity
Fent(U †V ) = 1
d2
Tr
U †V
2.
(A14)
We say that U and V are δ-close if ˜D(U, V ) = O(δ) and δ < 1.
Theorem A.2. The entanglement fidelity Fent(U †V ) and the phase-agnostic distance ˜D(U, V ) between two δ-close
single-qubit unitaries U, V are related by
Fent(U †V ) = 1 −˜D(U, V )2 + O(δ4).
(A15)
Proof. Without loss of generality we can expand, for some angles ϕ, θ ∈[−π, π],
U †V = exp

iϕ + iθ
2⃗v · ⃗X

,
(A16)
where ⃗v = (vx, vy, vz) is a unit vector with v2
x + v2
y + v2
z = 1 and ⃗X = (X, Y, Z) is a vector of Pauli operators. This
expansion allows us to directly compute
Fent(U †V ) = 1
4
Tr

eiϕ+i θ
2⃗v· ⃗
X
2
= 1
4
Tr

ei θ
2⃗v· ⃗
X
2
= cos
θ
2
2
.
(A17)


18
We then observe that
˜D(U, V ) = min
α
1 −eiαU †V
 = min
α
λ+
αΠ+v + λ−
α Π−v
,
(A18)
where λ±
α = 1 −eiα+iϕ±iθ/2 and Π±v = |±v⟩⟨±v| are projectors onto the orthonormal eigenvectors |±v⟩of ⃗v · ⃗X. It
follows that
˜D(U, V ) = 2 min
α max
±
λ±
α

(A19)
= 2 min
α max
±
sin
α + ϕ ± θ/2
2

(A20)
= 2 min
β max
±
sin

β ± θ
4

(A21)
= 2 min
β max
±

|sin β|
cos
θ
4
 ± |cos β|
sin
θ
4


(A22)
= 2 min
β

|sin β|
cos
θ
4
 + |cos β|
sin
θ
4


.
(A23)
Without loss of generality, we can restrict β ∈[0, π/2], and consider the quantity f(β) = sin β
cos
 θ
4
 + cos β
sin
 θ
4

that is minimized over β in Eq. (A23). The derivative ∂βf(β) = cos β
cos
 θ
4
 −sin β
sin
 θ
4
 is positive at β = 0,
negative at β = π/2, and zero once in between. It follows that f(β) achieves a single maximum at some β ∈(0, π/2),
and is otherwise minimal at one of its endpoints, f(0) = |sin(θ/4)| or f(π/2) = |cos(θ/4)|. The fact that |θ| ≤π then
implies that |sin(θ/4)| ≤|cos(θ/4)|, so
˜D(U, V ) = 2
sin
θ
4
.
(A24)
Altogether, for positive θ = δ < 1 we can expand
˜D(U, V ) = 2 sin
δ
4

= δ
2 + O(δ3),
(A25)
and
Fent(U †V ) = 1 −δ2
4 + O(δ4) = 1 −˜D(U, V )2 + O(δ4),
(A26)
thereby arriving at Theorem A.2.
B.
The TACU gadget
An essential circuit primitive for both the Hamiltonian simulation and oracles of the QAOA+AA algorithm in this
work is the K-qubit temporary-AND-compute-and-uncompute (TACU) gadget [62], which we use to apply K-qubit
phase gates of the form PK(γ) = e−iγ|1⟩⟨1|⊗K. Specifically, the K-qubit TACU gadget is defined by
...
...
...
...
. . . . . .
. . . . . .
x
1
=
2
K
|0⟩
,
(B1)
or, for shorthand,
K
K
. . . . . .
. . . . . .
x
=
|0⟩
,
(B2)


19
where the horizontal dots (. . . . . .) are a placeholder for ancilla-qubit operations, the first gate on the right-hand side
is a (K + 1)-qubit Toffoli gate that applies at Pauli-X to the ancilla qubit if all controls are in |1⟩, and the last gate
denotes an X-basis measurement of the ancilla qubit, whose measurement outcome determines whether to apply a
K-qubit multi-controlled-Z gate. The K-qubit TACU gadget can be used to apply a multi-qubit phase gate as
K
K
PK(γ)
γ
=
=
P(γ)
(B3)
where P(γ) = P1(γ) = e−iγ|1⟩⟨1|.
We say that a circuit V is Z-equivalent to the unitary U if the action of U is equal to the action of V followed by
single-qubit Pauli-Z corrections that can be efficiently computed from the outcomes of measurements performed in V .
For the purposes of the work below, we formally define a logical cycle to be the time required to perform one logical
two-qubit Pauli operator measurement. In practice, one logical cycle in a distance-d surface code on a two-dimensional
architecture with local interactions is the time required to perform d rounds of syndrome measurement [82].
The main technical result that we wish to establish in this section is the following:
Theorem B.1. The K-qubit phase gate PK(γ) = eiγ|1⟩⟨1|⊗K is Z-equivalent to a circuit that addresses the K qubits
of PK(γ) for one logical cycle, introduces ⌊13
2 K⌋ancilla qubits, consumes P⌈log2 K⌉
ℓ=1
⌊K/2ℓ⌋≤K −1 CCZ states, and
can be implemented in a total of nP + 4⌈log2 K⌉logical cycles, where nP is the number of logical cycles required to
implement the single-qubit phase gate P1(γ).
Here an adaptive measurement is a measurement whose basis may depend on (and can be efficiently computed
from) the outcomes of past measurements. We prove Theorem B.1 in stages below, by first optimizing the two-qubit
TACU gadget in Ref. [62], and then combining two-qubit TACU gadgets into a K-qubit TACU gadget.
1.
Optimizing the two-qubit TACU gadget
Starting with the two-qubit TACU gadget in Fig. 15(c) of Ref. [62], we can expand the conditional (reactive) CZ
gates therein using Fig. 14(b) of Ref. [62] to write
z
z
. . . . . .
z
. . . . . .
x
z
x
z
x
z
x
=
a
Zp
b
Zq
|0⟩
H
c
H
Xr
k
|CCZ⟩
d
e
f
|0⟩
Ma
g,h
|0⟩
|0⟩
Mb
i,j
|0⟩
|0⟩
Mc⊕k
l,m
|0⟩
.
(B4)
Here circles represent single- and two-qubit Pauli measurements in a basis that is indicated by both text and color,
for clarity, and whose outcomes are saved to bits a, b, c, d, e, f, k; we define the conditional two-qubit measurement


20
gate
a
x
x
Ma
g,h
=
g
h =





















x
x
g
h
if a = 0
x
z
z
x
g
h
if a = 1
,
(B5)
where the a superscript on the CZ gate indicates that this gate is applied only if a = 1; and the control bits p, q, r for
the Pauli gates in Eq. (B4) are
p = (b ∧c) ⊕d ⊕i ⊕l,
(B6)
q = (a ∧c) ⊕e ⊕g ⊕m,
(B7)
r = (a ∧b) ⊕f ⊕h ⊕j.
(B8)
We can “offload” gates from the top qubits in Eq. (B4) by applying the circuit identity
z
z
z
z
z
z
z
z
a
=
a
=
a
=
a
|0⟩
|0⟩
|0⟩
|0⟩
|0⟩
|0⟩
|0⟩
|0⟩
,
(B9)
where the last equality holds because the joint state of the top qubit and the bottom two ancillas after the two CNOTs
looks like ψ0 |000⟩+ ψ1 |111⟩, so the two-qubit ZZ measurement may equivalently address any of these qubits. We
thereby find that
. . . . . .
. . . . . .
x
z
z
z
z
x
z
x
z
x
=
Zp
Zq
|0⟩
Xr
k
|0⟩
Ma
g,h
|0⟩
|0⟩
Mb
i,j
|0⟩
c
|0⟩
a
Mc⊕k
l,m
|0⟩
b
|CCZ⟩
d
e
f
,
(B10)


21
where we use the X-controlled-X gate on the third and fifth qubits, which is simply a CZ gate in the X basis. Finally,
we use a decomposition of the CNOT gate into lattice surgery primitives [108],
z
x
z
x
x
=
b
Za⊕c
|0⟩
a
c
Xb
,
(B11)
to decompose each chain of interactions between the top and bottom three qubits in Eq. (B10) as
z
z
|0⟩
|0⟩
d
=
z
x
z
x
x
z
x
z
x
x
z
z
b1
Za1⊕c1
|0⟩
a1
c1
|0⟩
Xb1
b2
Za2⊕c2
|0⟩
a2
c2
|0⟩
Xb2
d
(B12)
=
z
x
z
x
x
z
x
z
x
x
z
z
b1
Za1⊕c1
|0⟩
a1
c1
|0⟩
b1⊕b2
Xb1Za2⊕c2
|0⟩
a2
c2
|0⟩
b2⊕d
Xb2
,
(B13)
where the superscripts b1 ⊕b2 and b2 ⊕d on ZZ measurements indicate that these measurement outcomes are equated
with b1 ⊕b2 and b2 ⊕d, respectively, which implicitly determines the values of b2 and d. We thus find that the


22
two-qubit TACU gadget can be implemented by a circuit of the form
z
z
. . . . . .
x
. . . . . .
x
x
z
x
x
z
x
z
x
z
x
x
z
x
x
z
x
z
x
z
x
x
z
x
x
z
x
z
x
z
x
z
x
z
x
z
x
=
Z•
Z•
|0⟩
X•
|0⟩
|0⟩
X•Z•
M•
|0⟩
X•
|0⟩
|0⟩
|0⟩
X•Z•
M•
|0⟩
X•
|0⟩
|0⟩
|0⟩
X•Z•
M•
|0⟩
X•
|0⟩
|CCZ⟩
,
(B14)
where bullets (•) indicate unspecified, but simple dependencies on measurement outcomes in the circuit. In total, the
two-qubit TACU gadget addresses its target qubits for one logial cycle, consumes one CCZ state with 13 |0⟩-state
ancilla qubits, requires three logical cycles to “write” the AND of its target qubits to an ancilla qubit for further
processing, and ends with a measurement that requires one logical cycle to determine adaptive Pauli-Z corrections to
the target qubits.
2.
The multi-qubit TACU gadget
The circuit in Eq. (B14) can be schematically written as
2
. . . . . .
•
. . . . . .
. . . . . .
•
=
Z•
=
Z•
Z•
D
D
,
(B15)
where D is an appropriately defined TACU dispatch circuit, and the final measurement in Eq. (B15) includes both
of the rightmost measurement gates in Eq. (B14). This notation thereby suppresses the presence of the two ancilla
qubits introduced in D that are measured at the end of Eq. (B15); namely, the ancilla qubits that participate in the
last conditional measurement (M•) gate in Eq. (B14).
If K = 2L for integer L, then we can construct a K-qubit TACU gadget by AND-ing together pairs of qubits in a
binary tree. Defining Kℓ= K/2ℓand denoting j concurrent copies of the two-qubit TACU dispatch circuit by Dj, we


23
thus find that
K
K
K1
K2
. . . . . .
•
1
•
2
...
...
...
. . . . . .
•
L
=
Z•
DK1
DK2
D1
,
(B16)
where the final measurements have to occur sequentially from bottom to top because the measurements at level ℓmay
induce Pauli-Z corrections at level ℓ−1 that affect the measurement basis.
If K is not a power of two, we instead define Kℓ= ⌈K/2ℓ⌉and L = ⌈log2 K⌉, and replace two-qubit TACU gadgets
in Eq. (B16) as needed to address unpaired qubits by the “one-qubit TACU” gadget
. . . . . .
. . . . . .
x
=
Z
|0⟩
,
(B17)
which can be thought of as a temporary-COPY-compute-and-uncompute gadget. In total, the K-qubit TACU gadget
consumes P⌈log2 K⌉
ℓ=1
Kℓ≤K −1 CCZ states, requires 3⌈log2 K⌉logical cycles to write the AND of its target qubits to
an ancilla qubit for further processing, and ends with ⌈log2 K⌉logical cycles to measure out the ancillas. The dispach
circuits DK1 introduce at most ⌊13
2 K⌋ancilla qubits, and the majority of these ancillas become free at the time of
dispatching DK2, which in turn needs half the number of ancillas as DK1. In total, ⌊13
2 K⌋ancilla qubits thereby
suffice for the K-qubit TACU gadget. These resource counts, together with the facts that (a) when ignoring Pauli-Z
corrections, data qubits are addressed only once by the K-qubit TACU gadget in Eq. (B16), and (b) the K-qubit
phase gate PK(γ) can be implemented by inserting of a single-qubit phase gate P1(γ) into Eq. (B16), prove Theorem
B.1.
C.
Resource bounds for the k-SAT oracle
Here we bound the resources required to implement the k-SAT oracle OC. In principle, this oracle can be imple-
mented using the TACU gadgets in Appendix B. However, a straightforward TACU-based implementation has an
ancilla qubit overhead that would dominate the qubit requirements of the QAOA+AA algorithm in the main text.
We therefore construct an implementation of the oracle with reduced space overheads, based on explicit (as opposed
to temporary) computation and uncomputation.
1.
The multi-qubit Toffoli gate
Starting with the Toffoli gate in Fig. 14(a) of Ref. [62],
2
z
b
c
z
a
z
z
x
z
x
z
x
=
=
a
Z(b∧c)⊕d
b
Z(a∧c)⊕e
H
c
H
X(a∧b)⊕f
|CCZ⟩
d
e
f
,
(C1)


24
the three conditional CZ gates can be performed in two logical cycles,
z
z
z
z
z
z
x
z
x
x
z
x
x
z
x
=
Z•
Z•
Z•
|0⟩
|0⟩
|0⟩
.
(C2)
By commuting through and merging the Hadamard gates in Eq. (C1), we can thus implement the Toffoli gate by
consuming one CCZ state in three logical cycles using three ancilla qubits.
If K = 2L for integer L, then the K-qubit TACU gadget in Eq. (B16) and the three-qubit Toffoli gate in Eq. (C1)
can be combined to construct a (K + 1)-qubit Toffoli gate
K
K
K
K1
K2
2
•
•
...
...
•
=
=
Z•
DK1
DK2
D2
,
(C3)
where Kℓ= ⌊K/2ℓ⌋, and we make a minor optimization that eliminates the final dispatch (D1) in Eq. (B16) and
simplifies the resource accounting below. If K is not a power of two, then two-qubit TACU gadgets and the Toffoli
gate are, respectively, replaced by the one-qubit TACU gadget in Eq. (B17) and a CNOT gate as necessary to address
unpaired qubits. This (K + 1)-qubit Toffoli gate thereby consumes up to P⌈log2 K⌉
ℓ=1
Kℓ≤K −1 CCZ states, requires
3⌈log2 K⌉logical cycles to finish addressing the target qubit, and ends with ⌈log2 K⌉−1 logical cycles to uncompute
all intermediate data on ⌊13
2 K⌋ancilla qubits.
2.
The oracle
Each clause of a k-SAT instance is an OR of k (possibly negated) variables, which can be converted into a k-fold AND
operation by the appropriate insertion of single-bit negations (i.e., using De Morgan’s Law). We can schematically
represent a gadget that temporarily writes clause Cj onto one qubit using the De Morgan’s Law and the k-qubit
TACU gadget in Eq. (B15) by
n
. . . . . .
•
Z•
Cj
.
(C4)
Let Qj be the set of qubits that correspond to the variables addressed in the clause Cj. We say that a partition
C = { C1, C2, · · · , Cc } of the k-SAT clauses C = { C1, · · · , Cm } is disjoint if each part Cℓ⊂C consists of clauses that
address mutually disjoint sets of qubits, which is to say that if Ci, Cj ∈Cℓ, then |Qi ∩Qj| = 0. Given a disjoint
partition C = { C1, C2, · · · , Cc } of C into subsets with maximum size s = maxj |Cj|, without loss of generality we let


25
C1 = { C1, C2, · · · , Cs } and define a gadget that writes the AND of all clauses in C1 onto a single qubit,
n
n
. . .
. . .
. . .
•
. . .
•
...
...
...
...
•
=
Z•
|0⟩
C1
|0⟩
C1
C2
Cs
.
(C5)
The gadgets for C2, C3, · · · , Cc are defined analogously. By construction, all individual clauses in Eq. (C5) can be
computed in parallel. In total, this gadget consumes up to R1 CCZ states in L1 logical cycles using A1 ancilla qubits,
where
R1 = (k −1)s + s −1 = ks −1,
(C6)
L1 = 4⌈log2 k⌉+ 4⌈log2 s⌉−1 ≈4 log2(ks),
(C7)
A1 =
13
2 k

s +
13
2 s

≈13
2 (k + 1)s.
(C8)
We now further partition C into ⌈√c⌉subsets C1, C2, · · · , C⌈√c⌉of size at most ⌈√c⌉, with for example C1 =
{ C1, C2, · · · , C⌈√c⌉}. We can AND together all clauses in C1 by computing all Cj ∈C1, AND-ing them together
with a ⌈√c⌉-qubit Toffoli, and uncomputing all Cj ∈C1 with gadgets of the form
n
n
. . .
. . .
. . .
. . .
. . .
. . .
. . .
. . .
...
...
...
...
...
...
...
=
|0⟩
C1
|0⟩
|0⟩
C1
C1
|0⟩
|0⟩
C2
C2
|0⟩
|0⟩
C⌈√c⌉
C⌈√c⌉
|0⟩
.
(C9)
If all parts Cj are computed sequentially, this gadget consumes up to R2 CCZ states in L2 logical cycles using A2
ancilla qubits, where
R2 = 2⌈√c⌉R1 + ⌈√c⌉−1 ≈2ks√c,
(C10)
L2 = 2⌈√c⌉L1 + 4 log2⌈√c⌉−1 ≈8 log2(ks)√c,
(C11)
A2 = A1 + ⌈√c⌉≈13
2 (k + 1)s + √c.
(C12)
If η ≤L1 parts Cj are computed concurrently, then the number of required logical ancilla qubits grows by a factor of
η, the contribution of 2⌈√c⌉L1 to L2 gets reduced by a factor of η, and an additional η −1 logical cycles are added
to L2 to account for the fact that the parts Cj must be dispatched one logical cycle at a time, such that altogether
L2 =
2⌈√c⌉L1
η

+ η + 4 log2⌈√c⌉−2 ≈8 log2(ks)√c η−1,
A2 = A1η + ⌈√c⌉≈13
2 (k + 1)sη + √c.
(C13)


26
Finally, the oracle OC can be implemented by AND-ing all Cj together onto one qubit, applying a single-qubit phase
(Pauli-Z) gate, and uncomputing,
n
n
. . .
. . .
. . .
. . .
. . .
. . .
...
...
...
...
...
...
...
...
OC
=
|0⟩
C1
C1
|0⟩
|0⟩
C2
C2
|0⟩
|0⟩
C⌈√c⌉
C⌈√c⌉
|0⟩
Z
.
(C14)
The oracle OC therefore consumes up to R3 CCZ states in L3 logical cycles using A3 ancilla qubits, where
R3 = 2⌈√c⌉R2 + ⌈√c⌉−1 = (4ks −2)⌈√c⌉2 −⌈√c⌉−1 ≈4ksc,
(C15)
L3 = 2⌈√c⌉L2 + 4 log2⌈√c⌉≈16 log2(ks)cη−1,
(C16)
A3 = A2 + ⌈√c⌉≈13
2 (k + 1)sη + 2√c.
(C17)
In summary, the oracle OC can be implemented by a circuit that looks like
×⌈√c⌉
×⌈√c⌉
×⌈√c⌉
×⌈√c⌉
×⌈√c⌉
×⌈√c⌉
n
n
⌈√c⌉
⌈√c⌉
OC
=
C
C
|0⟩
|0⟩
C
|0⟩
|0⟩
Z
.
(C18)
In the main text, the space overheads of the parallelized phaser exceed those of the unparallelized (η = 1) oracle. We
therefore parallelize the oracle to the point at which its space overheads (from both logical ancilla qubits and CCZ
factories) nearly match (but do not exceed) the space overheads of the parallelized phaser. In practice, this means
that η ∈[22, 23] for all cases considered in the main text.
D.
Optimal QAOA depths
As illustrated by the time budget in Fig. 2D, the QAOA+AA runtime Tq is dominated by the time to implement
the QAOA phaser. Therefore, to good approximation this runtime goes Tq(n, p) ∝p/
q
Prsuccess
QAOA = p20.69p−0.32n/2,
illustrated also in Fig. 5. This dependence on n and p allows us to compute an optimal QAOA depth p for every
problem size n, namely
popt(n) = min
p Tq(n, p) ≈
ln 2
2
× 0.69 × 0.32 × n

1
0.32
≈3.25 × 10−4 × n
1
0.32 .
(D1)
We note, however, that this optimization relies on a strong commitment to the functional form Tq(n, p) and its
precise parameters (0.69 and 0.32) for arbitrary QAOA depths p. We therefore instead consider, in the main text,
specific values of p that correspond to different asymptotic speedups, which has the added benefit of showcasing
the plausibility of a quantum advantage in optimization with other quantum algorithms that typically have fixed
asymptotic speedups.


27
101
102
103
104
QAOA depth p
time to solution Tq
simulation
popt
Figure 5.
Dependence of the time-to-solution Tq for QAOA+AA on the QAOA depth p for n = 100 8-SAT variables.


28
asymptotic QAOA problem
code
physical classical logical non-Clifford parallel number of number of
number of
decomposition non-Clifford crossover
quantum
cycles
size
distance
qubits
decoder
depth
gates
jobs
classical
logical
T gate
accuracy
infidelity
time
speedup
p
n
d
(×106)
ndecoder (×108)
(×1012)
njobs
cores ncores
ancillas
for rotation NT
δ
ϵT
Tq ≤Tc
quadratic
71
242
35
152.43
52.32k
6750.25
419.0
840
71
43680
27
1.76 × 10−09
1.00 × 10−17
3 y
cubic
253
191
29
84.43
36.9k
20.76
0.96
592
50
30784
24
6.65 × 10−08
1.44 × 10−14
64.57 h
quartic
623
179
28
73.91
33.66k
5.0
0.21
540
46
28080
23
1.41 × 10−07
6.48 × 10−14
14.99 h
Table III. Extended data for the crossover point. This extended table shows parameters, beyond those in Fig 3 of the main text, for crossover points at which
QAOA+AA and the classical solver Sparrow take equal time to solve, in expectation, random instances of 8-SAT near the satisfiability threshold.


29
asymptotic QAOA problem
code
physical classical logical non-Clifford parallel number of number of
number of
decomposition non-Clifford crossover
quantum
cycles
size
distance
qubits
decoder
depth
gates
jobs
classical
logical
T gate
accuracy
infidelity
time
speedup
p
n
d
(×106)
ndecoder (×108)
(×1012)
njobs
cores ncores
ancillas
for rotation NT
δ
ϵT
Tq ≤Tc
quadratic
71
235
18
17.0
25.04k
4594.56
265.24
400
725760
20800
27
1.76 × 10−09
1.00 × 10−17 144.64 d
cubic
253
189
15
9.69
18.54k
19.32
0.87
296
725760
15392
24
8.63 × 10−08
1.57 × 10−14
12.02 h
quartic
623
177
15
8.84
16.92k
4.72
0.2
270
725760
14040
23
1.47 × 10−07
7.00 × 10−14
2.94 h
Table V. Extended data for the crossover point for the combined improvements for realistic classical parallelization.
This extended table shows
parameters, beyond those in Table I of the main text, for crossover points at which QAOA+AA and the classical solver Sparrow take equal time to solve, in
expectation, random instances of 8-SAT near the satisfiability threshold. Classical solver is run on all 725, 760 cores of MareNostrum 5 GPP supercomputer [36] using
the impact of parallelization estimated in Ref. [32].


30
asymptotic QAOA problem
code
physical classical
logical
non-Clifford parallel number of number of
number of
decomposition non-Clifford crossover
quantum
cycles
size
distance
qubits
decoder
depth
gates
jobs
classical
logical
T gate
accuracy
infidelity
time
speedup
p
n
d
(×106)
ndecoder
(×108)
(×1012)
njobs
cores ncores
ancillas
for rotation NT
δ
ϵT
Tq ≤Tc
quadratic
71
366
22
72.22
77.25k
13296817.43 1241049.01
1240
725760
64480
27
1.76 × 10−09
1.00 × 10−17
708 y
cubic
253
286
17
36.41
58.32k
996.59
73.22
936
725760
48672
26
7.15 × 10−09
1.66 × 10−16 354.34 h
quartic
623
263
16
29.81
52.1k
65.25
4.31
836
725760
43472
25
3.17 × 10−08
3.26 × 10−15
21.75 h
Table VII. Extended data for the crossover point for the combined improvements for perfect classical parallelization. This extended table shows
parameters, beyond those in Table I of the main text, for crossover points at which QAOA+AA and the classical solver Sparrow take equal time to solve, in
expectation, random instances of 8-SAT near the satisfiability threshold. Classical solver is run on all 725, 760 cores of MareNostrum 5 GPP supercomputer [36] with
perfect parallelization assumed (i.e., the runtime of classical solver is the serial runtime divided by ncores).