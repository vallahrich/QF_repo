# **Focus beyond quadratic speedups for error-corrected quantum advantage** 

Ryan Babbush,[1,] _[ ∗]_ Jarrod R. McClean,[1,] _[ †]_ Michael Newman,[1] Craig Gidney,[1] Sergio Boixo,[1] and Hartmut Neven[1] 

> 1 _Google Quantum AI, Venice, CA 90291, United States of America_ 

(Dated: April 2, 2021) 

In this perspective, we discuss conditions under which it would be possible for a modest faulttolerant quantum computer to realize a runtime advantage by executing a quantum algorithm with only a small polynomial speedup over the best classical alternative. The challenge is that the computation must finish within a reasonable amount of time while being difficult enough that the small quantum scaling advantage would compensate for the large constant factor overheads associated with error-correction. We compute several examples of such runtimes using state-of-theart surface code constructions under a variety of assumptions. We conclude that quadratic speedups will not enable quantum advantage on early generations of such fault-tolerant devices unless there is a significant improvement in how we would realize quantum error-correction. While this conclusion persists even if we were to increase the rate of logical gates in the surface code by more than an order of magnitude, we also repeat this analysis for speedups by other polynomial degrees and find that quartic speedups look significantly more practical. 

## **Introduction** 

One of the most important goals of the field of quantum computing is to eventually build a fault-tolerant quantum computer. But what valuable and classically challenging problems could we actually solve on such a device? Among the most compelling applications are quantum simulation [1, 2] and prime factoring [3]. Quantum algorithms for these tasks give exponential speedups over known classical alternatives but would have limited impact compared to significant improvements in our ability to address problems in broad areas of industrial relevance such as optimization and machine learning. However, while quantum algorithms exist for these applications, the most rigorous results have only been able to show a large speedup in contrived settings or a smaller speedup across a broad range of problems. For example, many quantum algorithms (often based on amplitude amplification [4]) give quadratic speedups for tasks such as search [5], optimization [5–7], Monte Carlo [4, 8, 9], various areas of machine learning [10, 11] and more. However, attempts [7, 12] to assess the overheads of some such applications within fault-tolerance have come up with discouraging predictions for what would be required to achieve practical advantage against classical algorithms. 

The central issue is that quantum error-correction and device operation time introduce significant constant factor slowdowns to the algorithm runtime (see Figure 1). These large overheads present many challenges for the practical realization of useful fault-tolerant devices. However, for applications that benefit from an exponential speedup relative to classical algorithms, the exponential scaling of the classical approach quickly catches up to the large constant factors of the quantum approach so that one can achieve a practical runtime advantage for 

> _∗_ Corresponding author: babbush@google.com 

> _†_ Corresponding author: jmcclean@google.com 

**==> picture [98 x 135] intentionally omitted <==**

**==> picture [128 x 128] intentionally omitted <==**

**==> picture [222 x 18] intentionally omitted <==**

**----- Start of picture text -----**<br>
(a) “Quantum nand” (b) “Classical nand”<br>>  10 qubitseconds <  10 [−] [9] transistorseconds<br>**----- End of picture text -----**<br>


FIG. 1. The primary obstacle in realizing a runtime advantage for low degree quantum speedups is the enormous slowdown when performing basic logic operations within quantum error-correction. (a) A surface code Toffoli factory for distilling Toffoli gates (which act as the nand gate when the target bit is on) requires spacetime volume greater than ten qubitseconds under reasonable assumptions on the capabilities of an error-corrected superconducting qubit platform [13]. (b) A nand circuit realized in CMOS can be executed with just a few transistors in well under a nanosecond. Thus, there is roughly a ten order of magnitude difference between the spacetime volume required for comparable operations on an error-corrected quantum computer and a classical computer. 

even modest problem sizes. This is borne out through numerous studies on the cost of error-correcting applications with exponential scaling advantage in areas such as quantum chemistry [14–16], quantum simulation of lattice models [17, 18] and prime factoring [19]. 

In this perspective we discuss when it would be practical for a modest fault-tolerant quantum computer to realize a quantum advantage with quantum algorithms giving only a small polynomial speedup over their classical competition. We will see that with only a low order (e.g., quadratic) speedup, exorbitantly long runtimes are 

2 

sometimes required in order for the slightly worse scaling of the classical algorithm to catch up to the slightly better scaling (but worse constant factors) of the quantum algorithm. We will argue that the problem is especially pronounced when the best classical algorithms for a problem can also be easily parallelized. 

Our analysis will emphasize current projections within the surface code [20] since it has the highest threshold error rate for a two-dimensional quantum computing architecture and is generally regarded as the most practical quantum error-correcting code [21]. We will focus on a modest realization of the surface code that would involve enough resources to perform classically intractable calculations but only support a few state distillation factories. Our analysis differs from results analyzing the viability of error-correcting quadratic speedups for combinatorial optimization such as [7, 12], by addressing the prospects for achieving quantum advantage via polynomial speedup for a broad class of algorithms, rather than for specific problems. Note that [7] was the first study to detail poor prospects for error-correcting an algorithm achieving a quadratic speedup with a small fault-tolerant processor. 

Here we will assume that there is some problem which can be solved by a classical computer that makes _M[d]_ calls to a “classical primitive” circuit or by a quantum computer which makes _M_ calls to a “quantum primitive” circuit (which is often, but not always, related to the classical primitive circuit). This corresponds to an order _d_ polynomial quantum speedup in the number of queries to these subroutines. For _d_ = 2, this is especially evocative of a common class of quantum algorithms leveraging amplitude amplification. This generously assumes no prefactor overhead in a quantum implementation of an algorithm with respect to the number of calls required and along with other crude assumptions, allows us to bound the crossover time. 

Our back-of-the-envelope analysis makes many assumptions which are overly optimistic towards the quantum computer and yet we still conclude that the prospects look poor for quadratic speedups with current error-correcting codes and architectures to outperform classical computers in time-to-solution. It seems that to realize a quantum advantage with reasonable fault-tolerant resources, one must either focus beyond quadratic speedups, dramatically improve techniques for error-correction, or do both. Our conclusion is already “folk wisdom” among some in the small community that studies quantum algorithms and error-correction with an eye towards practical realization; however, this reality is not widely appreciated in the broader community that studies algorithms and applications of quantum computers more generally and there is value in presenting a specific argument to this effect in written form. An encouraging finding is that the prospects for error-corrected quantum advantage look significantly better with quartic speedups. Of course, there might exist use cases involving quadratic speedups that defy the framework of this analysis. Either way, we hope this perspective will encourage 

the field to critically examine the prospects for quantum advantage with error-corrected quadratic speedups and either produce examples where it is feasible, or focus more effort on algorithms with larger speedups. 

## **Relationship between primitive times and runtime** 

Many quantum algorithms are built on coherent access to primitives implemented with classical logic. For example, this classical logic might be required to compute the value of a classical cost function for optimization [12], to evaluate a function of a trajectory of some security that one is pricing with Monte Carlo [9], or to compute some classical criteria that flags a marked state for which one might be searching [5]. We will define the runtime of the quantum and classical algorithms as 

**==> picture [194 x 13] intentionally omitted <==**

where _T_ gives the total runtime of the algorithm, _M_ is the number of primitive calls required, _d_ is the order of the polynomial speedup the quantum computer achieves and _t_ is the time required to perform a call. Throughout this perspective the subscripts _Q_ and _C_ will denote “quantum” and “classical” implementations. 

The condition for quantum advantage is 

**==> picture [220 x 28] intentionally omitted <==**

We see then that whenever a problem will require enough calls _M_ that a quantum advantage is possible, 

**==> picture [177 x 28] intentionally omitted <==**

where _T[⋆]_ is the “breakeven time” which occurs when _TQ_ = _TC_ , corresponding to onset of quantum advantage. As emphasized in Figure 1, we will see that the fundamental challenge in realizing this runtime advantage against classical computers (for small _d_ ) is that _tQ ≫ tC_ in error-corrected contexts, making _T[⋆]_ very large. 

Rather than use a single CPU for the classical approach, one might instead parallelize the algorithm using _P_ classical CPUs. This will reduce the total classical runtime to 

**==> picture [211 x 27] intentionally omitted <==**

where _α_ is the fraction of the algorithm which must be executed in serial and _S_ is the speedup factor due to parallelization consistent with the “Amdahl’s law” [22]. Note that Amdahl’s law scaling is considered somewhat pessimistic as one can often adjust the size of problems to fully exploit the computing power that becomes available with more parallelism (e.g., see “Gustafson’s law” [23] for a more optimistic formula for _S_ ). But it 

3 

also seems that in most situations where one might hope to find a quadratic speedup with a quantum computer (e.g. applications such as search, optimization, Monte Carlo, regression, etc.) the corresponding classical approach is embarrassingly parallel (suggesting that _α_ is small enough that _S ≈ P_ for reasonable values of _P_ ). Regardless of the form of _S_ , classical parallelism leads to the following revised conditions for quantum advantage: 

**==> picture [238 x 28] intentionally omitted <==**

While parallel efficiency might be limited for some applications, any implementation of an error-correcting code will also require substantial classical co-processing in order to perform decoding, and this is likely to require thousands of classical cores. Although many quantum algorithms can also benefit from various forms of parallelism, we are considering an early fault tolerance setting where there is likely an insufficient number of logical qubits to exploit a space-time tradeoff to the same extent. 

## **Implementing error-corrected quantum primitives** 

We will now explain the principle overheads believed to be required for the best candidate for quantum errorcorrection on a two-dimensional lattice: the surface code. Toffolis are the most commonly used gate for implementing classical logic on a quantum computer but cannot be implemented transversally within practical implementations of the surface code. Instead, one must implement these gates by first distilling resource states. In particular, to implement a Toffoli gate one requires a CCZ state ( _|_ CCZ _⟩_ = CCZ _|_ + + + _⟩_ ) and these states are consumed during the implementation of the gate. Distilling CCZ states requires a substantial amount of both time and hardware and thus, they are usually the bottleneck in realizing quantum algorithms within the surface code. 

Here, we will focus on the state-of-the-art Toffoli factory constructions of [13] which are based on applying the lattice surgery constructions of [24] to the fault-tolerant Toffoli protocols of [25, 26]. Using that approach one Toffoli gate requires 5 _._ 5 _× d_ surface code cycles, where _d_ is the code distance. The time per round of the surface code, including decoding time is expected to be around 1 _µs_ in superconducting qubits. Our analysis will assume a code distance in the vicinity of _d_ = 30. This would be sufficient for an algorithm with billions of gates and physical gate error rates on the order of 10 _[−]_[3] (as our analysis will reveal, even more than a billion gates would likely be required to obtain quantum advantage with a modest polynomial speedup). With these assumptions, our model predicts a Toffoli gate time of 

**==> picture [190 x 11] intentionally omitted <==**

This rough approximation matches the more detailed resource estimate of Ref. [13]. We discuss these estimates in more detail in Appendix A. 

Under the aforementioned assumptions which are specific to contemporary realizations of the surface code using superconducting qubits we could express the quantum primitive runtime as 

**==> picture [179 x 12] intentionally omitted <==**

where _G_ is the number of Toffoli gates required to implement the quantum primitive. Although we have focused on superconducting qubits, we can also contextualize the performance of ion traps — another leading architecture for quantum advantage. Ion qubits enjoy hour-long coherence times [27], but are typically gated by the performance of their two-qubit gate [28]. Gate times within a single ion crystal can range from hundreds of microseconds to sub-microsecond speeds [29–33], and can be efficiently parallelized [34, 35]. 

Multiple ion crystals can be connected to form a networked quantum computer, either through a chargecoupled device [36, 37] or via photonic interfaces [38, 39]. While a charge-coupled device may support thousands of qubits, millions of qubits will likely require photonic interconnects, although large shuttling-based traps have been proposed [40]. For either architecture, a _∼_ 10 kHz cycle frequency has been identified as an ambitious but attainable goal [40–42]. Consequently, we can roughly estimate that such a device will be limited by a clockspeed about 100 _×_ slower than the 1 _µ_ s decoding throughput limit, commensurate with typical high-fidelity two-qubit gate times [43, 44] and corresponding to a _tG ≈_ 17 ms. However, in trade, such a device may support the requisite connectivity for non-2D error-corrected codes and fault-tolerant gates. While the advantages of such approaches are speculative, we touch on some of these alternate proposals in Appendix B. 

On a very large surface code quantum computer one could instead use multiple Toffoli factories (at a high cost in the number of physical qubits required) in order to reduce _tQ_ by performing state distillation in parallel. However, the Toffoli gates are only about two orders of magnitude slower than the Clifford gates and when using multiple factories one needs to account for routing overhead. Thus, while _tQ_ can be reduced at the cost of using many more qubits, only by a factor that is between about ten and one-hundred. 

If _N_ is the number of qubits on which this problem is defined then a sensible lower bound would seem to be _G ≥ N_ and thus, _tQ ≥_ 170 _µ_ s _· N_ . For example, in Grover’s algorithm [5] one must perform a reflection that requires _O_ ( _N_ ) Toffoli gates. In order to achieve a quantum advantage we would need to focus on problem sizes that are sufficiently large that enough calls can be made so that Eq. (2) is satisfied. We find it difficult to imagine satisfying this condition for problem sizes less than one-hundred qubits. Thus, an approximate “lower bound” (using _N_ = 100) would be 

**==> picture [150 x 11] intentionally omitted <==**

4 

In addition to this lower bound, we will also consider a specific, realistic example to keep our estimates grounded. We will focus on the quantum accelerated simulated annealing by qubitized quantum walk algorithm studied in [45, 46], which appears to provide a quadratic speedup over classical simulated annealing (at least in terms of the best known bounds) in terms of the mixing time of the Markov chain under certain assumptions [47]. This is among the most efficient algorithms compiled in [12] and for the Sherrington-Kirkpatrick model [48], the implementation complexity is 5 _N_ + _O_ (log _N_ ) (neglecting some subdominant scalings that depend on precision), which is only worse than the scaling of our lower bound by a factor of five. For example, for an _N_ = 512 qubit instance, the work of [12] shows that only about 2 _._ 6 _×_ 10[3] Toffoli gates are required to make an update. Thus, for that problem size (which we choose to facilitate a comparison to classical algorithms that we will discuss later) we have that 

what appears to be a fairly cheap primitive on the classical side. However, because Eq. (5) scales worse with _tQ_ than with _tC_ , this assumption is ultimately optimistic towards the overall crossover time. 

Consistent with the prior section, we will also discuss the classical primitive time required to apply simulated annealing to an instance of the Sherrington-Kirkpatrick model. Using the techniques developed in [49], a performant implementation of classical simulated annealing code for an _N_ = 512 instance of the SherringtonKirkpatrick model can perform a simulated annealing step in roughly 7 CPU-nanoseconds [12] (this accounts for the fact that most updates for the SherringtonKirkpatrick model are rejected); thus in that case, 

**==> picture [145 x 11] intentionally omitted <==**

But given the high costs of quantum computing it is unclear that we should compare to a single classical core. 

**==> picture [152 x 11] intentionally omitted <==**

## **Minimum runtime for quadratic quantum advantage** 

## **Implementing classical primitives** 

Classical computers are very fast; a typical 3 GHz CPU can perform several billion 64 bit operations (e.g., floating point multiplications) per second. We might crudely write that the classical primitive time is _tC_ = 330 ps _· L_ where _L_ is the number of classical clock cycles required to implement the classical primitive. For our first example comparison of quantum and classical primitives we will assume that any classical logic operation that would require one Toffoli in the quantum primitive can be executed during one classical clock cycle in the classical primitive. This seems generous to the quantum computer since many operations that would take a single clock cycle on a classical computer would actually require thousands of Toffolis. (Note that we are not assuming any scaling advantage for the quantum computer in the primitive implementations.) One might worry about memory-bound classical primitives (since calls to main memory can take hundreds of clock cycles) but since problems defined on more than thousands of logical bits would be infeasible to process on a small fault-tolerant quantum computer we expect that the memory required for the corresponding classical primitives can be held in cache. 

Thus, a corresponding bound on the time to realize a classical primitive for a problem where a quantum computer could realize a quantum primitive with anywhere near the lower bound time given in the prior section ( _tQ ≥_ 170 _µ_ s _· N_ ) is _tC ≤_ 330 ps _· N_ , and for _N_ = 100, 

**==> picture [149 x 11] intentionally omitted <==**

Even though the equivalence we make between Toffolis and classical compute cycles is seemingly generous to the quantum computer, the assumption of such a cheap primitive on the quantum side (only 100 Toffolis) results in 

Here we discuss the ramifications that the primitive runtimes discussed in the prior two sections have for the minimum time to achieve advantage according to Eq. (3) in the case of a quadratic quantum speedup. First, we will compare the example of a quantum primitive requiring only _N_ = 100 Toffolis and _tQ_ = 17 ms. We argued that any such primitive could likely be computed in _tC_ = 33 ns on a single core. For this example, _T[⋆]_ = _t_[2] _Q[/t][C]_[=][2] _[.]_[4][hours.][One][might][object][to][this] minimal example on the grounds that it seems unlikely any interesting primitive would require only 100 Toffolis. While this is true, we point out that because quantum runtime is quadratic in the quantum primitive time and only inversely proportional to the classical primitive time, the overall crossover time can only get worse by assuming that more than 100 Toffolis would be required. 

Next, we will compare to the example of quantum accelerated simulated annealing. We focus on this example because the steps of the quantum algorithm have been concretely compiled, appear quite efficient, and have a clear classical analogue. Here, for an _N_ = 512 qubit instance we have that _t_[2] _Q[/t][C]_[=][320 days,][reproducing][the] finding in [12]. We note that quantum advantage in this case would occur when _M > tQ/tC_ = 6 _._ 3 _×_ 10[7] . This means that 4 _._ 0 _×_ 10[15] calls would need to be required for the classical algorithm. However, most _N_ = 512 Sherrington-Kirkpatrick model instances would require many fewer calls to solve with classical simulated annealing and so one would need to focus on an even bigger system for which the numbers will look yet worse for the quantum computer. Notice that our simulated annealing example gave a quantum runtime that is much longer than the resources required for the quantum primitive with _N_ = 100 Toffolis. This is because the notion that it would take a classical computer an entire clock cycle to 

5 

do what a quantum computer could accomplish with a single Toffoli is very generous to the quantum computer. 

At first glance, the quantum runtime of 2.4 hours to achieve advantage for the primitive with just 100 Toffolis seems encouraging. Unfortunately, this was just for a single classical core. Even most laptops have on the order of ten cores these days and again, most of the problems where quantum computers display a quadratic advantage are classically embarrassingly parallel problems. Furthermore, error-corrected quantum computers are likely to use thousands of classical CPUs just for decoding. When using _P_ different classical CPUs in parallel then the breakeven time is given by Eq. (5). Using that equation, if we take _P_ = 3 _,_ 000 CPUs for the classical task (rather than using them for error-correction), and if the classical algorithm is sufficiently parallelizable ( _α[−]_[1] _≪ P_ so _S ≈ P_ ), we see that the breakeven time even in this still quantum-generous example becomes one year. As we discuss in the next section there are also ways of parallelizing the quantum computations; e.g., by using multiple quantum computers or distillation factories. 

## **The viability of higher polynomial speedups and the impact of faster error-correction** 

We report values of both _M_ and _T[⋆]_ assuming quantum speedups by different polynomial degrees under different amounts of classical parallelism in Table I. While the viability of quantum advantage with cubic speedups is still a bit ambiguous, the prospects of achieving quantum advantage given a quartic speedup are promising. Even the simulated annealing example run with a classical adversary with _S_ = 10[6] parallelism would give quantum advantage after five hours of runtime if we assume a quartic speedup (while we do not expect a quartic speedup in that case, the comparison is still instructive). 

It is rather surprising just how much of a difference there is for this example between assuming a quadratic speedup (requiring 880 millennia of runtime for advantage) and a quartic speedup (requiring just 4.9 hours of runtime for advantage). There are not as many examples of quartic speedups in quantum computing but there are a few, such as the tensor principle component analysis algorithm of Hastings [50]. Another example is the quartic query complexity reductions of Ambainis _et al._ [51] and Aaronson _et al._ [52]. We also expect that certain applications of quantum algorithms for linear systems [53] (such as for solving linear differential equations in high dimension [54]) might lead to modest polynomial speedups higher than quadratic. It is also possible that some heuristic quantum algorithms for optimization might give larger than quadratic improvements for some class of problems, although this is still speculative. 

Another question we might ask is, what happens if we were somehow able to implement Toffoli gates much faster in the surface code? For example, we might achieve this by fanning out and using more physical qubits per 

factory, more Toffoli factories, by inventing significantly more efficient protocols for Toffoli state distillation, or even by switching to a different technology with an intrinsically faster cycle time. We will perform this analysis for the case of quadratic speedups; there, the quantum runtime is reduced to _TQ_ = _M tQ/R_ where _R ≥_ 1 is a speedup factor corresponding to performing Toffoli distillation in time 170 _µ_ s _/R_ . In analogy to Eq. (5) this leads to the equations for a quadratic quantum speedup 

**==> picture [202 x 25] intentionally omitted <==**

In Table II we compute Eq. (12) for our example problems with _R_ = 10, _R_ = 10[2] and _R_ = 10[3] , assuming a classical adversary capable of achieving an _S_ = 10[3] parallelism. We restrict ourselves to _S_ = 10[3] due to the general difficulty in achieving high parallel efficiency described by Amdahl’s law. However, note that for simulated annealing we can achieve _S_ = 10[6] in practice (and so these numbers are overly optimistic for that case). 

Unfortunately, even if Toffoli distillation rates improve by an order of magnitude it would not be enough to make quantum advantage with a quadratic speedup viable. If Toffoli distillation rates improve by two orders magnitude (making them essentially as cheap as Clifford gates) then it would still be challenging to obtain quantum advantage with a quadratic speedup (it would take more than a month for the simulated annealing example despite limiting the classical parallelism to _S_ = 10[3] ) but we cannot categorically rule it out for all algorithms. At three orders of magnitude speedup the story would be materially different but this would likely require a significant breakthrough. Even if classical processing and signal propagation were instantaneous, and we could adapt measurements to take advantage feedforward single-qubit gates only being applied half the time, a single layer of non-Clifford gates would still take a hard limit of the measurement time plus half the single qubit gate time. 

## **Conclusion** 

We have investigated simple conditions that must be satisfied to realize a quantum advantage through polynomial speedups on a small fault-tolerant quantum computer. Our ultimate finding is that the prospects are generally poor for a quadratic speedup, consistent with folk knowledge in the error-correction community and recent work such as [7, 12]. The comparison to parallel classical resources is particularly damning for quantum computing and unfortunately, many quadratic quantum speedups (especially those leveraging amplitude amplification) apply to problems that are highly parallelizeable. The strongest conclusions in this work assume that one can achieve classical parallelism speedups on the order of 10[3] or more. But if one can produce a quadratic speedup for a problem where that is not the case, the prospects of quantum advantage would be improved. 

6 

|polynomial degree _d_|parallelism<br>speedup _S_|resource “lower bound”|resource “lower bound”|simulated annealing|simulated annealing|
|---|---|---|---|---|---|
|||iterations _M_|runtime _T ⋆_|iterations _M_|runtime _T ⋆_|
|Quadratic, _d_= 2|1<br>103<br>106|5_._2_×_105<br>5_._2_×_108<br>5_._2_×_1011|2_._4 hours<br>100 days<br>280 years|6_._3_×_107<br>6_._3_×_1010<br>6_._3_×_1013|320 days<br>880 years<br>880 millennia|
|Cubic, _d_= 3|1<br>103<br>106|7_._2_×_102<br>2_._3_×_104<br>7_._2_×_105|12 seconds<br>6_._4 minutes<br>3_._4 hours|7_._9_×_103<br>2_._5_×_105<br>7_._9_×_106|58 minutes<br>1_._3 days<br>40 days|
|Quartic, _d_= 4|1<br>103<br>106|8_._0_×_101<br>8_._0_×_102<br>8_._0_×_103|1_._4 seconds<br>14 seconds<br>2_._3 minutes|4_._0_×_102<br>4_._0_×_103<br>4_._0_×_105|2_._9 minutes<br>29 minutes<br>4_._9 hours|



TABLE I. Resources required to achieve quantum advantage assuming speedups of various polynomial degrees, _d_ . We make this comparison against an adversary using distributed classical computing resources that achieve a speedup factor _S_ and report the number of algorithm steps _M_ and total runtime _T[⋆]_ before a quantum speedup is possible. We make this comparison for both the informal resource “lower bound” we argued for in the text (using _tQ ≥_ 17 ms and _tC ≤_ 33 ns), and for the specific example of quantum simulated annealing applied to the Sherrington-Kirkpatrick model using the quantum and classical implementations discussed in [12, 49] (giving _tQ_ = 440 ms and _tC_ = 7 ns). 

These findings do not apply to all polynomial speedups. We found that while one would need to very significantly improve the rate of an error-corrected processor to help the case of quadratic speedups, having a quartic speedup rather than a quadratic speedup is often sufficient to restore the viability of achieving quantum advantage on a modest processor. Thus, we believe that these results suggest that the field should focus beyond quadratic speedups to find viable applications that might produce a quantum advantage on the first several generations of fault-tolerant quantum computers. 

We expect this conclusion will persist under a variety of different cost models (e.g., were we to focus on the energy consumption of a computation rather than the runtime). However, we also expect that the community will make progress on some of the challenges described here, or perhaps identify circumstances under which the assumptions of this analysis do not apply. Either way, we hope that these arguments will foster further discussion about how we might develop broadly applicable algorithms that can achieve quantum advantage on small error-corrected quantum computers. 

|speedup<br>factor|resource “lower bound”|resource “lower bound”|simulated annealing|simulated annealing|
|---|---|---|---|---|
||iterations _M_|runtime _T ⋆_|iterations _M_|runtime _T ⋆_|
|_R_= 101|5_._2_×_107|1_._0 day|6_._3_×_109|8_._8 years|
|_R_= 102|5_._2_×_106|15 minutes|6_._3_×_108|32 days|
|_R_= 103|5_._2_×_105|8_._8 seconds|6_._3_×_107|7_._7 hours|



TABLE II. Resources required to achieve quantum advantage under a quadratic speedup assuming Toffoli distillation time of 170 _µ_ s _/R_ and a classical adversary making use of classical parallelism with _S_ = 10[3] . The speedup factor _R_ can account for improvements in error-correction implementations or in our estimates of their overheads. For example, _R_ = 10 could be reached by using ten Toffoli factories if routing were very efficient (at the cost of requiring many more qubits). 

## **Acknowledgments** 

The authors thank Dave Bacon, Dominic Berry, Ken Brown, Eddie Farhi, Austin Fowler, Bill Huggins, Sergei Isakov, Evan Jeffrey, Cody Jones, John Platt, Rolando Somma, Nathan Wiebe and Will Zeng for helpful discussions and feedback on earlier drafts. 

- [1] Richard P Feynman, “Simulating physics with computers,” International Journal of Theoretical Physics **21** , 467–488 (1982). 

- [2] Seth Lloyd, “Universal Quantum Simulators,” Science **273** , 1073–1078 (1996). 

- [3] P W Shor, “Algorithms for quantum computation: discrete logarithms and factoring,” Proceedings 35th Annual Symposium on Foundations of Computer Science , 124–134 (1994). 

- [4] Gilles Brassard, Peter Høyer, Michele Mosca, and Alain Tapp, “Quantum amplitude amplification and estima- 

   - tion,” in _Quantum Computation and Information_ , edited by Vitaly I Voloshin, Samuel J. Lomonaco, and Howard E. Brandt (American Mathematical Society, Washington D.C., 2002) Chap. 3, pp. 53–74. 

- [5] Lov K Grover, “A fast quantum mechanical algorithm for database search,” in _Proceedings of the TwentyEighth Annual ACM Symposium on Theory of Computing_ , STOC ’96 (ACM, New York, NY, USA, 1996) pp. 212–219. 

- [6] R. D. Somma, S. Boixo, H. Barnum, and E. Knill, “Quantum Simulations of Classical Annealing Pro- 

7 

cesses,” Physical Review Letters **101** , 130504 (2008). 

- [7] Earl Campbell, Ankur Khurana, and Ashley Montanaro, “Applying quantum algorithms to constraint satisfaction problems,” Quantum **3** , 167–undefined (2019). 

- [8] Ashley Montanaro, “Quantum speedup of Monte Carlo methods,” Proceedings of the Royal Society A: Mathematical, Physical and Engineering Sciences **471** , 20150301 (2015). 

- [9] Patrick Rebentrost, Brajesh Gupt, and Thomas R. Bromley, “Quantum computational finance: Monte Carlo pricing of financial derivatives,” Physical Review A **98** , 022321 (2018). 

- [10] Esma A¨ımeur, Gilles Brassard, and S´ebastien Gambs, “Machine learning in a quantum world,” in _Advances in Artificial Intelligence_ , edited by Luc Lamontagne and Mario Marchand (Springer Berlin Heidelberg, Berlin, Heidelberg, 2006) pp. 431–442. 

- [11] Nathan Wiebe, Ashish Kapoor, and Krysta M. Svore, “Quantum algorithms for nearest-neighbor methods for supervised and unsupervised learning,” Quantum Info. Comput. **15** , 316–356 (2015). 

- [12] Yuval R. Sanders, Dominic W. Berry, Pedro C. S. Costa, Louis W. Tessler, Nathan Wiebe, Craig Gidney, Hartmut Neven, and Ryan Babbush, “Compilation of FaultTolerant Quantum Heuristics for Combinatorial Optimization,” PRX Quantum **1** , 020312–020382 (2020). 

- [13] Craig Gidney and Austin G. Fowler, “Efficient magic state factories with a catalyzed —CCZ¿ to 2—T¿ transformation,” Quantum **3** , 135 (2019). 

- [14] Ian D. Kivlichan, Craig Gidney, Dominic W. Berry, Nathan Wiebe, Jarrod McClean, Wei Sun, Zhang Jiang, Nicholas Rubin, Austin Fowler, Al´an Aspuru-Guzik, Hartmut Neven, and Ryan Babbush, “Improved FaultTolerant Quantum Simulation of Condensed-Phase Correlated Electrons via Trotterization,” Quantum **4** , 296 (2020). 

- [15] Vera von Burg, Guang Hao Low, Thomas Haner, Damian Steiger, Markus Reiher, Martin Roetteler, and Matthias Troyer, “Quantum computing enhanced computational catalysis,” arXiv:2007.14460 (2020). 

- [16] Joonho Lee, Dominic Berry, Craig Gidney, William Huggins, Jarrod McClean, Nathan Wiebe, and Ryan Babbush, “Even more efficient quantum computations of chemistry through tensor hypercontraction,” arXiv:2011.03494 (2020). 

- [17] Jessica Lemieux, Guillaume Duclos-Cianci, David S´en´echal, and David Poulin, “Resource estimate for quantum many-body ground state preparation on a quantum computer,” arXiv:2006.04650 (2020). 

- [18] Andrew M Childs, Dmitri Maslov, Yunseong Nam, Neil J Ross, and Yuan Su, “Toward the first quantum simulation with quantum speedup,” Proceedings of the National Academy of Sciences **115** , 9456–9461 (2018). 

- [19] Craig Gidney and Martin Eker˚a, “How to factor 2048 bit RSA integers in 8 hours using 20 million noisy qubits,” arXiv:1905.09749 (2019). 

- [20] Alexei Kitaev, “Fault-tolerant quantum computation by anyons,” Annals of Physics **303** , 2–30 (2003). 

- [21] Austin G Fowler, Matteo Mariantoni, John M Martinis, and Andrew N Cleland, “Surface codes: Towards practical large-scale quantum computation,” Physical Review A **86** , 32324 (2012). 

- [22] Gene M. Amdahl, “Validity of the single processor approach to achieving large scale computing capabilities,” 

in _AFIPS ’67 (Spring): Proceedings of the April 18-20, 1967, Spring Joint Computer Conference_ (1967) pp. 483– 485. 

- [23] John L. Gustafson, “Reevaluating Amdahl’s law,” Communications of the ACM **31** , 532–533 (1988). 

- [24] Austin G. Fowler and Craig Gidney, “Low overhead quantum computation using lattice surgery,” arXiv:1808.06709 (2018). 

- [25] Cody Jones, “Low-overhead constructions for the faulttolerant Toffoli gate,” Physical Review A **87** , 22328 (2013). 

- [26] Bryan Eastin, “Distilling one-qubit magic states into Toffoli states,” Physical Review A **87** , 032321 (2013). 

- [27] Ye Wang, Mark Um, Junhua Zhang, Shuoming An, Ming Lyu, Jing-Ning Zhang, L-M Duan, Dahyun Yum, and Kihwan Kim, “Single-qubit quantum memory exceeding ten-minute coherence time,” Nature Photonics **11** , 646– 650 (2017). 

- [28] Colin D Bruzewicz, John Chiaverini, Robert McConnell, and Jeremy M Sage, “Trapped-ion quantum computing: Progress and challenges,” Applied Physics Reviews **6** , 021314 (2019). 

- [29] Klaus Mølmer and Anders Sørensen, “Multiparticle entanglement of hot trapped ions,” Physical Review Letters **82** , 1835 (1999). 

- [30] Juan Jos´e Garc´ıa-Ripoll, Peter Zoller, and J Ignacio Cirac, “Speed optimized two-qubit gates with laser coherent control techniques for ion trap quantum computing,” Physical Review Letters **91** , 157901 (2003). 

- [31] JD Wong-Campos, SA Moses, KG Johnson, and C Monroe, “Demonstration of two-atom entanglement with ultrafast optical pulses,” Physical Review Letters **119** , 230501 (2017). 

- [32] VM Sch¨afer, CJ Ballance, K Thirumalai, LJ Stephenson, TG Ballance, AM Steane, and DM Lucas, “Fast quantum logic gates with trapped-ion qubits,” Nature **555** , 75–78 (2018). 

- [33] E Torrontegui, D Heinrich, M I Hussain, R Blatt, and J J Garc´ıa-Ripoll, “Ultra-fast two-qubit ion gate using sequences of resonant pulses,” New Journal of Physics **22** , 103024 (2020). 

- [34] Nikodem Grzesiak, Reinhold Bl¨umel, Kenneth Wright, Kristin M Beck, Neal C Pisenti, Ming Li, Vandiver Chaplin, Jason M Amini, Shantanu Debnath, Jwo-Sy Chen, _et al._ , “Efficient arbitrary simultaneously entangling gates on a trapped-ion quantum computer,” Nature Communications **11** , 1–6 (2020). 

- [35] Kevin A Landsman, Yukai Wu, Pak Hong Leung, Daiwei Zhu, Norbert M Linke, Kenneth R Brown, Luming Duan, and C Monroe, “Two-qubit entangling gates within arbitrarily long chains of trapped ions,” Physical Review A **100** , 022332 (2019). 

- [36] David Kielpinski, Chris Monroe, and David J Wineland, “Architecture for a large-scale ion-trap quantum computer,” Nature **417** , 709–711 (2002). 

- [37] Juan M Pino, Jennifer M Dreiling, Caroline Figgatt, John P Gaebler, Steven A Moses, CH Baldwin, M FossFeig, D Hayes, K Mayer, C Ryan-Anderson, _et al._ , “Demonstration of the qccd trapped-ion quantum computer architecture,” arXiv preprint arXiv:2003.01293 (2020). 

- [38] C Monroe, R Raussendorf, A Ruthven, KR Brown, P Maunz, L-M Duan, and J Kim, “Large-scale modular quantum-computer architecture with atomic mem- 

8 

ory and photonic interconnects,” Physical Review A **89** , 022317 (2014). 

- [39] David Hucul, Ismail V Inlek, Grahame Vittorini, Clayton Crocker, Shantanu Debnath, Susan M Clark, and Christopher Monroe, “Modular entanglement of atomic qubits using photons and phonons,” Nature Physics **11** , 37–42 (2015). 

- [40] Bjoern Lekitsch, Sebastian Weidt, Austin G Fowler, Klaus Mølmer, Simon J Devitt, Christof Wunderlich, and Winfried K Hensinger, “Blueprint for a microwave trapped ion quantum computer,” Science Advances **3** , e1601540 (2017). 

- [41] Kenneth R Brown, Jungsang Kim, and Christopher Monroe, “Co-designing a scalable quantum computer with trapped atomic ions,” npj Quantum Information **2** , 1–10 (2016). 

- [42] Naomi H Nickerson, Joseph F Fitzsimons, and Simon C Benjamin, “Freely scalable quantum technologies using cells of 5-to-50 qubits with very lossy and noisy photonic links,” Physical Review X **4** , 041041 (2014). 

- [43] CJ Ballance, TP Harty, NM Linke, MA Sepiol, and DM Lucas, “High-fidelity quantum logic gates using trapped-ion hyperfine qubits,” Physical Review Letters **117** , 060504 (2016). 

- [44] John P Gaebler, Ting Rei Tan, Y Lin, Y Wan, R Bowler, Adam C Keith, S Glancy, K Coakley, E Knill, D Leibfried, _et al._ , “High-fidelity universal gate set for be 9+ ion qubits,” Physical Review Letters **117** , 060505 (2016). 

- [45] R D Somma, S Boixo, H Barnum, and E Knill, “Quantum Simulations of Classical Annealing Processes,” Physical Review Letters **101** , 130504 (2008). 

- [46] Jessica Lemieux, Bettina Heim, David Poulin, Krysta Svore, and Matthias Troyer, “Efficient quantum walk circuits for metropolis-hastings algorithm,” Quantum **4** , 287 (2020). 

- [47] Sergio Boixo, Emanuel Knill, and Rolando Somma, “Quantum state preparation by phase randomization,” Quantum Information & Computation **9** , 0833–0855 (2009). 

- [48] S. Kirkpatrick, C. Gelatt Jr., and M. Vecchi, “Optimization by Simulated Annealing,” Science **220** , 671–680 (1983). 

- [49] S V Isakov, I N Zintchenko, T F Ronnow, and M Troyer, “Optimized simulated annealing code for Ising spin glasses,” Computer Physics Communications **192** , 265– 271 (2015). 

- [50] Matthew B. Hastings, “Classical and Quantum Algorithms for Tensor Principal Component Analysis,” Quantum **4** , 237– (2020). 

- [51] Andris Ambainis, Kaspars Balodis, Aleksandrs Belovs, Troy Lee, Miklos Santha, and Juris Smotrovs, “Separations in Query Complexity Based on Pointer Functions,” arXiv:1506.04719 (2015). 

- [52] Scott Aaronson, Shalev Ben-David, Robin Kothari, and Avishay Tal, “Quantum Implications of Huang’s Sensitivity Theorem,” arXiv:2004.13231 (2020). 

- [53] Aram W. Harrow, Avinatan Hassidim, and Seth Lloyd, “Quantum Algorithm for Linear Systems of Equations,” Physical Review Letters **103** , 150502 (2009). 

- [54] Dominic W Berry, “High-order quantum algorithm for solving linear differential equations,” Journal of Physics A: Mathematical and Theoretical **47** , 105301– (2014). 

- [55] Colin J Trout, Muyuan Li, Mauricio Guti´errez, Yukai Wu, Sheng-Tao Wang, Luming Duan, and Kenneth R Brown, “Simulating the performance of a distance-3 surface code in a linear ion trap,” New Journal of Physics **20** , 043038 (2018). 

- [56] Stephen Crain, Clinton Cahall, Geert Vrijsen, Emma E Wollman, Matthew D Shaw, Varun B Verma, Sae Woo Nam, and Jungsang Kim, “High-speed low-crosstalk detection of a 171 yb+ qubit using superconducting nanowire single photon detectors,” Communications Physics **2** , 1–6 (2019). 

- [57] LJ Stephenson, DP Nadlinger, BC Nichol, S An, P Drmota, TG Ballance, K Thirumalai, JF Goodwin, DM Lucas, and CJ Ballance, “High-rate, high-fidelity entanglement of qubits across an elementary quantum network,” Physical Review Letters **124** , 110501 (2020). 

- [58] Ting Rei Tan, John P Gaebler, Yiheng Lin, Yong Wan, R Bowler, D Leibfried, and David J Wineland, “Multielement logic gates for trapped-ion qubits,” Nature **528** , 380–383 (2015). 

- [59] CJ Ballance, VM Sch¨afer, Jonathan P Home, DJ Szwer, Scott C Webster, DTC Allcock, Norbert M Linke, TP Harty, DPL Aude Craik, Derek N Stacey, _et al._ , “Hybrid quantum logic and a test of bell’s inequality using two different atomic isotopes,” Nature **528** , 384–386 (2015). 

- [60] Vlad Negnevitsky, Matteo Marinelli, Karan K Mehta, H-Y Lo, Christa Fl¨uhmann, and Jonathan P Home, “Repeated multi-qubit readout and feedback with a mixed-species trapped-ion register,” Nature **563** , 527– 531 (2018). 

- [61] Austin G Fowler, “Time-optimal quantum computation,” arXiv:1210.4626 (2012). 

- [62] Craig Gidney and Austin G Fowler, “Flexible layout of surface code computations using autoccz states,” arXiv:1905.08916 (2019). 

- [63] Nicolas Delfosse, Ben W Reichardt, and Krysta M Svore, “Beyond single-shot fault-tolerant quantum error correction,” arXiv:2002.05180 (2020). 

- [64] Bryan Eastin and Emanuel Knill, “Restrictions on Transversal Encoded Quantum Gate Sets,” Physical Review Letters **102** , 110502 (2009). 

- [65] Austin G. Fowler, “Optimal complexity correction of correlated errors in the surface code,” arXiv:1310.0863 (2013). 

- [66] Robert Raussendorf and Jim Harrington, “Fault-Tolerant Quantum Computation with High Threshold in Two Dimensions,” Physical Review Letters **98** , 190504 (2007). 

- [67] Sergey Bravyi and Robert K¨onig, “Classification of topologically protected gates for local stabilizer codes,” Physical review letters **110** , 170503 (2013). 

- [68] Michael Vasmer and Dan E Browne, “Three-dimensional surface codes: Transversal gates and fault-tolerant architectures,” Physical Review A **100** , 012312 (2019). 

- [69] Benjamin J Brown, “A fault-tolerant non-clifford gate for the surface code in two dimensions,” Science advances **6** , eaay4929 (2020). 

- [70] Hector Bombin, “2d quantum computation with 3d topological codes,” arXiv preprint arXiv:1810.09571 (2018). 

- [71] Jonas T Anderson, Guillaume Duclos-Cianci, and David Poulin, “Fault-tolerant conversion between the steane and reed-muller quantum codes,” Physical Review Letters **113** , 080501 (2014). 

9 

- [72] Adam Paetznick and Ben W Reichardt, “Universal faulttolerant quantum computation with only transversal gates and error correction,” Physical Review Letters **111** , 090505 (2013). 

- [73] H´ector Bomb´ın, “Gauge color codes: optimal transversal gates and gauge fixing in topological stabilizer codes,” New Journal of Physics **17** , 083002 (2015). 

- [74] Tomas Jochym-O’Connor and Raymond Laflamme, “Using concatenated quantum codes for universal faulttolerant quantum gates,” Physical Review Letters **112** , 010505 (2014). 

- [75] Theodore J Yoder, Ryuji Takagi, and Isaac L Chuang, “Universal fault-tolerant gates on concatenated stabilizer codes,” Physical Review X **6** , 031039 (2016). 

- [76] Theodore J Yoder, “Universal fault-tolerant quantum computation with bacon-shor codes,” arXiv preprint arXiv:1705.01686 (2017). 

- [77] Christopher Chamberland, Tomas Jochym-O’Connor, and Raymond Laflamme, “Overhead analysis of universal concatenated quantum codes,” Physical Review A **95** , 022313 (2017). 

- [78] Michael E Beverland, Aleksander Kubica, and Krysta M Svore, “The cost of universality: A comparative study of the overhead of state distillation and code switching with color codes,” arXiv preprint arXiv:2101.02211 . 

- [79] Sergey Bravyi, David Poulin, and Barbara Terhal, “Tradeoffs for reliable quantum information storage in 2d systems,” Physical Review Letters **104** , 050503 (2010). 

- [80] Sergey Bravyi, “Subsystem codes with spatially local generators,” Physical Review A **83** , 012320 (2011). 

- [81] Jean-Pierre Tillich and Gilles Z´emor, “Quantum ldpc codes with positive rate and minimum distance proportional to the square root of the blocklength,” IEEE Transactions on Information Theory **60** , 1193–1202 (2013). 

- [82] Pavel Panteleev and Gleb Kalachev, “Degenerate quantum ldpc codes with good finite length performance,” arXiv preprint arXiv:1904.02703 (2019). 

- [83] Antoine Grospellier, Lucien Grou`es, Anirudh Krishna, and Anthony Leverrier, “Combining hard and soft decoders for hypergraph product codes,” arXiv preprint arXiv:2004.11199 (2020). 

- [84] Oscar Higgott and Nikolas P Breuckmann, “Subsystem codes with high thresholds by gauge fixing and reduced qubit overhead,” arXiv preprint arXiv:2010.09626 (2020). 

- [85] Daniel Gottesman, “Fault-tolerant quantum computation with constant overhead,” arXiv preprint arXiv:1310.2984 (2013). 

- [86] Anirudh Krishna and David Poulin, “Fault-tolerant gates on hypergraph product codes,” arXiv preprint arXiv:1909.07424 (2019). 

## **Appendix A: Accounting for error-correction costs** 

In the main text, we provide an estimate for the time that it takes to perform a single Toffoli gate with optimized factories within the surface code. The crux of the argument in the main text, is that this time is so much slower than the classical equivalent, there is a massive overhead which must be first overcome. We believe 

that it is valuable in directing future research in errorcorrection and algorithms to break down the origin of this overhead into its contributions from quantum errorcorrection and the physical device speed itself. Here we do so in some detail for the case of the surface code in superconducting qubits, and in passing for ion traps. We hope that this discussion will elucidate several avenues through which breakthroughs in error-correction might materially change the analysis of the main text. 

To begin, we will assume that there is a physical twoqubit operation and syndrome measurement speed, _τ_ and _τs_ , where _τs > τ_ as _τ_ is used to build measurement circuits along with a base physical measurement time _τm_ . Modern fault-tolerant error-correction proceeds via rounds of syndrome extraction, processing, and correction in order to implement gates. The core physical operation of these rounds on the device is measurement of syndromes, and we are hence lower bounded by the measurement time _τs_ in realistic settings. For context, estimates of these times for high fidelity superconducting qubits that would be realistic upon improvement are roughly _τ ≈_ 10 ns and _τm ≈_ 100 ns. 

For a networked ion trap device, there are extra nuances in estimating a realistic syndrome measurement speed [55]. Currently, high-fidelity two-qubit gates and measurements take approximately _τ ≈_ 100 _µ_ s and _τm ≈_ 10 _µ_ s [43, 56], although high-fidelity microsecond gates have also been demonstrated [32]. Most proposals are limited by a typical trap frequency of _∼_ 1 MHz, although this limit is not fundamental [31] and submicrosecond gate times are possible [30]. 

In addition, communicating between different crystals will likely introduce significant overhead. When using photonic interconnects, the mean connection rate between different modules will be fundamentally limited by the emission rate, which for typical atomic transitions into free space will be _∼_ 100 MHz. However, current state-of-the-art entanglement generation occurs in the _∼_ 200 Hz regime [57]. When accounting for fractional light collection and single-photon detector efficiency, we can ambitiously estimate future mean connection rates of _∼_ 10 kHz [39, 41], which may be amplified by generating entanglement in parallel at an additional cost in space. Without photonic interconnects, shuttling and cooling will introduce additional slowdowns [36], and can currently take hundreds of microseconds [37]. With photonic interconnects, shuttling may still be required to isolate memory ions from light scattered during entanglement generation, although this can be mitigated by using a different atomic species for communication [58–60]. 

None of these components are fundamentally limited below _∼_ 1 MHz. However, many of them must act several times in concert to measure a single round of syndromes. Consequently, _τs ≈_ 100 _µ_ s seems an ambitious goal, and is commensurate with earlier estimates [40–42]. 

If one had perfect operations, but still performed gates via a synthesized and fault-tolerant protocol, these would lower-bound the achievable runtime for a gate. As our 

10 

operations are not perfect, however, we will need to encode in an error-correcting code with some distance _d_ which is chosen based on the error rate in our device, threshold of the code, and total number of operations we expect to perform. If one is allowed to use numerous ancilla qubits, this need not expand the runtime of individual operations by exploiting parallelism through teleportation and spacetime optimization [61, 62]. However, more qubit spartan implementations must use _d_ rounds of measurement and correction to protect against measurement errors in the time direction, adding a factor of _O_ ( _d_ ) in the time cost. Research into one-shot correction techniques hopes to alleviate this time dependence on _d_ without excessive space overhead [63], but current code constructions are not readily implementable. 

On top of each round of these measurements, we must account for the time for this information to leave the device, be processed via decoding, and in some cases, implement active recovery after a gate, where this time depends on the hardware and complexity of the decoding. In order for error-correction to be efficient, it must be possible to process the syndrome data without an accumulation of rounds that grows in time. If we denote this processing latency as _lr_ , then the time for processing _d_ rounds is lower bounded approximately by the time it takes to produce those syndrome measurements on the physical device plus this latency, or ( _dτs_ + _lr_ ). Note that depending on the implementation details, _lr_ is likely to depend on _d_ , but with sufficient classical parallelization it may be possible to make it effectively _d_ independent. 

On top of these costs, each gate has some associated prefactor in number of rounds that depends on the type of gate and its logical locality, _CG_ . For easy, or Clifford, gates in most codes, _CG_ can be made near 1. Unfortunately, in order to perform universal computation, one requires a gate which is not easy to implement [64], and common proposals center around state distillation where the prefactor _CG_ is often on the order of 10. Moreover, if one considers synthesis of arbitrary rotations into multiple of these hard gates, _CG_ can multiply by a factor of 10 or more depending on the precision, leaving _CG_ on the order of 100. Putting these together, we can approximate a lower bound on the quantum gate time scaling in terms of error-correction parameters as 

**==> picture [164 x 11] intentionally omitted <==**

Now that we have a general picture of how the time overhead enters for quantum error-correction, we examine it in a specific gate and context. In particular, we focus on superconducting qubits with feasible error rates and operation times within the surface code. Toffoli gates are required to implement classical logic on a quantum computer but cannot be implemented transversally within practical implementations of the surface code. Instead, one must implement these gates by first distilling resource states. To implement a Toffoli gate one requires a CCZ state ( _|_ CCZ _⟩_ = CCZ _|_ + + + _⟩_ ) and these states are consumed during the implementation of the gate. Dis- 

tilling CCZ states requires a substantial amount of both time and hardware and thus, they are usually the bottleneck in realizing quantum algorithms within the surface code. 

Here, we will focus on the state-of-the-art Toffoli factory constructions of [13] which are based on applying the lattice surgery constructions of [24] to the fault-tolerant Toffoli protocols of [25, 26]. Using that approach one can distill one CCZ state using two levels of state distillation with 5 _._ 5 _d_ + _O_ (1) surface code cycles and a factory with a data qubit footprint of about 12 _d ×_ 6 _d_ where _d_ is the code distance (the total footprint includes measurement qubits as well, and is thus roughly double this number). Hence for the Toffoli gate, we take _CG ≈_ 5 _._ 5. 

We will assume a correlated-error minimum weight perfect matching decoder capable of keeping pace with 1 _µ_ s rounds of surface code error detection [65], and capable of performing with a similar latency of feedforward in about 1 _µ_ s for _d_ around 30, and conservatively lower bound the overall time for _d_ rounds to then be ( _dτs_ + _lr_ ) _≤_ 30 _µs_ . We will also assume physical gate error rates in the vicinity of 10 _[−]_[3] , which we hope will be achievable at scale in the next decade. Since we expect to require on the order of billions of Toffoli gates to achieve quantum advantage for practical applications (we will see this is actually a significant underestimate for the case of quadratic speedups) we will assume that a code distance in the vicinity of _d_ = 30 will be sufficient (since errors are suppressed exponentially in code distance this number will be approximately correct). 

With these assumptions, our model predicts a Toffoli gate time of _tG_ = _CG_ ( _dτs_ + _lr_ ) _≈_ 5 _._ 5 _×_ 30 _µ_ s _≈_ 170 _µ_ s. This rough approximation matches the more detailed resource estimate which shows the spacetime volume required to implement one Toffoli gate is approximately 23 qubit seconds [13]. We discuss the resources required for distillation in terms of qubitseconds because it is generally possible to make tradeoffs between space and time but the critical resource to minimize is actually the product of the two. Under these assumptions we would be able to distill a Toffoli gate in about 170 _µ_ s using around 130,000 physical qubits (see the resource estimation spreadsheet in [13] for detailed assumptions). Due to this large overhead we focus on estimates assuming we distill CCZ states in series, which is likely how we would operate early fault-tolerant surface code computers. For comparison, if ion trap devices used a similar surface code implementation and error rates while achieving a syndrome measurement time of _τs_ = 100 _µ_ s in parallel, the gate time assuming _CG ≈_ 5 _._ 5 is _tG ≈_ 17 _,_ 000 _µ_ s, or roughly a factor of 100 slower. 

To make this more concrete, we can convert this to a unitless error-correction overhead for a particular gate of _CG_ ( _dτs_ + _lr_ ) _/τs_ . If we keep the 30 _µ_ s overall bound for ( _dτs_ + _lr_ ), and make a reasonable estimate for the improvement of physical syndrome measurement times for superconducting qubits to 100 ns, then the errorcorrection overhead at this distance is 1 _,_ 700. 

11 

This suggests that at present for superconducting qubits, the most fruitful improvements with regards to algorithmic speed are the reduction of decoding time, the minimization of time overheads in distillation factories, and then the reduction of number of measurement rounds required to protect in the time direction, perhaps through improved gate fidelities for equivalent operation times to result in lower required distances or through single shot protocols. If this can be achieved, the next milestones would be the reduction of physical syndrome extraction time. However, even such advances would already make prospects for realizing a quantum advantage with quadratic speedups considerably more enticing. 

## **Appendix B: Alternative approaches** 

Throughout this work, we have focused on the time cost of surface code implementations of non-Clifford gates, as the expense of such gates has been highly optimized given the connectivity constraints of a superconducting quantum device. Furthermore, the surface code is one of the few error-correction schemes that can operate efficiently in the high noise regime, with gate infidelities in the range of 10 _[−]_[3] [21, 66]. 

However, there are limitations when considering a twodimensional architecture. We have chosen to report on the time-cost of logical gates (while keeping the space cost low). By this metric, transversal gates are minimally expensive, yet non-Clifford gates cannot be implemented transversally in the surface code. In fact, _any_ constant depth circuit on a 2D-local stabilizer code must be Clifford [67], often leading to a time-dependence on _d_ . Additional connectivity in the device — and likely a requirement of lower error rates — opens up many more avenues towards universal fault-tolerant logic. Beyond magic state distillation, contemporary approaches include, but are not limited to: 

1. **Computing with 3D local codes** , where nonClifford gates are transversal [68] (and may be realized dynamically in 2D [69, 70]). 

2. **Code switching** between codes with complementary transversal gate sets [71]. 

3. **Fixing the gauge** of subsystem codes, where different gauges admit different transversal gates 

[72, 73]. 

4. **Concatenating codes** , each supporting a complementary transversal gate set [74]. 

5. **Pieceable fault-tolerance** , which breaks nontransversal gates into fault-tolerant pieces [75, 76]. 

For non-Clifford gates, there are tradeoffs that can be made to mitigate the distance and routing overhead of our bound at the expense of many more qubits. Whether or not these constructions may yield a lower space and time overhead at reasonable error rates is speculative. Numerical studies of alternative schemes have yet to show a convincing advantage [77, 78], and often require _<_ 10 _[−]_[3] error rates to operate efficiently, although their spacetime footprint can be smaller [69]. Nonetheless, significant optimizations or new approaches are likely needed to recoup a reasonable-sized quadratic quantum advantage. 

A separate avenue towards reducing the space overhead of error-correction are block encodings. While surface codes are robust, they require very many qubits per logical qubit. More generally, 2D-local code families are fundamentally restricted to have a vanishing ratio of logical qubits to physical qubits, assuming an underlying growing code distance [79, 80]. In an all-to-all connected device, a non-vanishing rate is possible without sacrificing the low stabilizer weight often essential for good performance [81]. In particular, there have been promising numerical studies of high-density memories in idealized noise settings using variations on efficient belief propagation decoding [82, 83]. 

For the purposes of our bound, we have assumed first generation fault-tolerant devices will support hundreds of logical qubits each with a distance of _d ∼_ 30, and few distillation factories. The total qubit footprint of such a device will remain in the 10[5] _−_ 10[6] qubit range. By comparison, there exist intermediate-size families of block codes that can encode hundreds of logical qubits using only 10[3] _−_ 10[4] qubits. However, it is difficult to predict the consequences of using such encodings in the context of our computation-time bound. The required physical error rates may be untenably low, with relatively few studies predicting performance in circuit-level error models [84]. In addition, performing gates efficiently on such codes is a difficult task [85, 86]. As such, while a significant reduction in memory space may result, the role of such codes in future fault-tolerant devices remains unclear. 

