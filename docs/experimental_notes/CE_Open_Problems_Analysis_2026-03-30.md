# Open Problems Analysis for the CDSFL Bench

**Date:** 30 March 2026

---

## The Training Data Problem

The CDSFL bench currently has 27 frontier tasks, all with known solutions. If CDSFL improves performance on these, critics can say the solutions were already in the training data and CDSFL just helped the models retrieve them more reliably. This criticism has force.

The known-solution tasks are not wasted — they are calibration data. You need problems with known answers to measure methodology performance. But they are not sufficient to demonstrate the thesis. The strong claim — that CDSFL is a science calculator for extending the frontier — requires testing against problems where the answer does not exist.

---

## What CDSFL Can Do on Open Problems

CDSFL cannot generate breakthroughs. It cannot invent new mathematical techniques. It cannot run experiments. What it can do:

- Systematically map the constraint space of a problem
- Classify what is proven versus conjectured versus speculative, and force honesty about which is which
- Find contradictions between existing approaches using multi-architecture review
- Identify precisely where each proof strategy fails and why
- Verify intermediate results computationally where possible
- Produce a rigorous structured analysis that a domain expert can act on

The measured output on open problems is not whether it got the right answer. It is whether CDSFL produced more rigorous, more honestly classified, more gap-aware analysis than unstructured review. FT-027 on the Riemann Hypothesis already tests this. The question is which other open problems are most amenable.

---

## Selection Criteria

For an open problem to be a good CDSFL bench candidate, it needs:

- A rich, encodable constraint space
- Decomposable sub-problems that can be individually falsified
- Computational verifiability on at least some components
- Multi-domain intersection where cognitive biodiversity gives the most advantage
- Known failure modes in existing approaches
- Amenability to systematic analysis rather than requiring purely novel techniques

---

## Tier 1: Strongest Candidates

### 1. Turbulence and the RANS Closure Problem

The Navier-Stokes equations are defined. Closure models exist (k-epsilon, k-omega, Reynolds stress models). Direct numerical simulation (DNS) data exists for computational verification.

The constraint box is extraordinarily rich: realizability conditions, tensor symmetry requirements, known asymptotic limits, Galilean invariance. CDSFL could:
- Systematically evaluate existing closure models against these constraints and DNS benchmarks
- Identify where each model fails and why
- Explore the parameter space for modifications

Progress is measurable. A closure model that better matches DNS data is objectively better regardless of whether it was in the training data. Engineering impact is immediate: better turbulence models mean better aircraft, better engines, better weather prediction.

---

### 2. Navier-Stokes Existence and Smoothness

This is a Clay Millennium Prize problem. The mathematical structure is deeply known. Partial results exist including Leray weak solutions, Caffarelli-Kohn-Nirenberg partial regularity, and the recent failed Lean-verified proof attempt in late 2025. Each existing approach has identifiable failure modes.

CDSFL could produce the most rigorous map of the proof strategy landscape ever assembled: where each approach works, where it breaks, what mathematical tools are missing, and what a successful proof would require.

The recent failed Lean proof is a perfect case study. It got past formal verification but had conceptual errors. That is exactly the kind of failure CDSFL's adversarial methodology catches.

---

### 3. Catalytic Nitrogen Fixation

The thermodynamic constraints are hard. The nitrogen triple bond energy is 945 kJ/mol. The biological mechanism is known: nitrogenase uses an iron-molybdenum cofactor with a specific electron transfer pathway and specific intermediates. The target is defined: ambient temperature and pressure.

CDSFL could:
- Systematically explore the catalyst design space within those bounds
- Falsify proposed mechanisms against computational chemistry benchmarks
- Identify the most promising directions

This is multi-domain: chemistry, materials science, thermodynamics, and biology.

---

### 4. The Collatz Conjecture

Deceptively simple statement, profoundly resistant to proof. Known approaches include probabilistic arguments, p-adic analysis, Markov chain models, and connections to automata theory. Each has clear failure modes. The constraint space is pure number theory with computational verifiability.

CDSFL could:
- Map exactly where each approach breaks and why
- Classify each claim rigorously (probabilistic arguments are SOFT, not HARD)
- Explore less-trodden paths

---

## Tier 2: Strong Candidates with Caveats

### 5. The Arrow of Time

Well-defined statistical mechanics. Clear mathematical problem: derive macroscopic irreversibility from time-symmetric micro-laws. Known approaches each have identifiable circular reasoning. CDSFL's falsification methodology is specifically designed to catch circular arguments.

**Caveat:** Resolution may ultimately require a conceptual shift rather than a technical fix.

---

### 6. Baryon Asymmetry and Baryogenesis

Well-defined Sakharov conditions. The Standard Model satisfies all three conditions but not sufficiently. Known candidate mechanisms exist.

**Caveat:** Falsification ultimately requires experimental particle physics data.

---

### 7. The Battery Dendrite Problem

Clear electrochemistry, well-defined failure mode, existing computational models, known constraints. Multi-physics coupling.

**Caveat:** Progress is primarily experimental.

---

### 8. Carbon Capture Thermodynamics

The minimum work of separation is a thermodynamic hard constraint. The engineering challenge is approaching it. Known sorbent chemistries with defined performance envelopes.

**Caveat:** This is an engineering optimisation problem more than a fundamental science problem, but it has enormous practical value.

---

## Tier 3: Unsuitable for CDSFL Bench

| Problem | Reason |
|---------|--------|
| P versus NP | Requires genuinely new complexity-theoretic techniques |
| Quantum gravity | Too fundamental. Requires new physics, not better analysis |
| Dark matter and dark energy | Resolution requires experimental detection |
| Consciousness | The hard problem is almost definitionally unfalsifiable. Fails Popper's criterion |
| Abiogenesis | Primarily experimental. Chemical pathways must be demonstrated, not argued |
| AGI | Recursive and not falsifiable in the CDSFL sense |
| Room-temperature superconductivity | Materials science discovery, requires synthesis and measurement |
| The Fermi Paradox | Not falsifiable by analysis alone. Requires observation |

---

## Why Turbulence Closure Is the Strongest Single Candidate

The RANS closure problem has the richest constraint box of any problem on this list:

- **Governing physics:** The Navier-Stokes equations
- **Mathematical constraints:** Realizability conditions on any valid closure
- **Ground truth:** DNS data for verification
- **Multi-domain:** Fluid mechanics, turbulence theory, and numerical methods
- **Known failure cases:** k-epsilon failing in separated flows (well-documented)
- **Objective measurement:** Better match to DNS data, satisfied realizability conditions, improved predictions in known test geometries

An expert encoding for this problem would contain:
- The RANS equations
- The Reynolds stress tensor and its properties
- Realizability conditions (Lumley triangle, positive semi-definiteness)
- The known closure hierarchy (algebraic, one-equation, two-equation, Reynolds stress transport)
- Each model's documented failure cases
- The DNS benchmark datasets to verify against

CDSFL would not solve the closure problem. But it could produce a more rigorous, more systematically falsified analysis of existing and proposed closures than any single model or architecture could produce on its own. If it identifies a modification to an existing closure that better satisfies realizability while matching DNS data, that is genuine, measurable, publishable scientific progress.

---

## The Constraint Box Principle Applied to Open Problems

The insight about expert encodings applies directly here:

- For **known problems**, the constraint box bounds the model within the **solution space**. The value is: the model produces the right answer more reliably.
- For **open problems**, the constraint box bounds the model within the **problem space** — what is known about the problem, its structure, its constraints, its symmetries, and its known failure modes. The model is forced to explore within that bounded space rather than generating ungrounded speculation. The value is: the model produces more rigorous analysis by being forced to classify every claim as proven, conjectured, or speculative, and by being forced to work within the constraints of what is actually known rather than generating plausible-sounding narratives.

This is the science calculator thesis in its strongest form. Not "CDSFL solves hard problems." Rather: "CDSFL forces AI-assisted analysis into a discipline where claims are classified, constraints are respected, and the boundary between knowledge and speculation is made explicit." That is what scientific method does. CDSFL is an attempt to formalise it.

---

## Extrapolation

**What generalises.** If CDSFL can produce demonstrably more rigorous analysis of turbulence closure or Navier-Stokes existence than unstructured review — not solving the problem but mapping the solution space more precisely and classifying claims more honestly — that is evidence for the science calculator thesis. The methodology becomes an instrument for extending scientific rigour. The expert encodings for open problems become living documents that communities can iterate on. That is the tradable, shareable, upgradable artifact.

**Boundary conditions.** CDSFL cannot cross the gap from rigorous analysis of known structure to novel insight that resolves the problem. The Arrow of Time probably requires a conceptual shift. P versus NP probably requires a new proof technique. CDSFL can map the terrain up to the edge of current knowledge but it cannot see over the edge. The value is in making the edge sharp and precise — knowing exactly what we do not know. Most of science is not the breakthrough moment. It is the systematic elimination of wrong approaches that makes the breakthrough possible.

**Falsifiable questions.**
1. Does CDSFL-guided analysis of the RANS closure problem produce closure model candidates that better satisfy realizability conditions and DNS benchmarks than existing models? Directly testable.
2. Does CDSFL-guided analysis of the Navier-Stokes existence problem produce a more complete and more honestly classified map of proof strategies than any existing survey? Testable by expert evaluation.
3. Does multi-architecture CDSFL review of nitrogen fixation catalyst proposals identify thermodynamic infeasibility that single-model review misses? Testable against computational chemistry verification.
4. Does the HARD/SOFT/SPECULATIVE classification on open problems agree with expert consensus, and where it disagrees, is the expert or the methodology wrong? This is the meta-test. [SPECULATIVE]

---

## Recommendation

Add 4 to 6 open-problem frontier tasks to the bench drawn from Tier 1 and the strongest Tier 2 candidates. Each gets an expert encoding that contains the known constraint space, not speculative solution attempts. The measured outputs are classification accuracy, gap identification, contradiction detection, and decay curve quality.

The existing 27 known-solution tasks stay for calibration. The open-problem tasks demonstrate the thesis. Together they answer both questions:

1. Does CDSFL improve performance on known problems?
2. Does CDSFL produce better science on unknown ones?

**If adding only one, add turbulence closure. It is the single strongest candidate.**
