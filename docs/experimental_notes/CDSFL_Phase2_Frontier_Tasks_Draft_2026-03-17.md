# CDSFL Phase 2 Frontier Tasks Draft

**Generated 2026-03-17**

This document drafts 25 frontier tasks for Phase 2 of the CDSFL experiment. These are research drafts for review, not final versions. The tasks are designed to be hard enough that frontier models make genuine errors on a single pass, and to benefit from iterative falsification and cross-model checking.

There are five categories with five tasks each.

---

## Category 1 — Proof Tasks

### Task ft-001: Monotone Subsequence Bound Tightening

Prove the Erdos-Szekeres theorem (every sequence of n² + 1 distinct reals has a monotone subsequence of length n + 1), then construct a tight example showing the bound cannot be improved. The construction must be explicit, not just an existence argument. Verification is by generating the sequence for small n and computationally confirming no long monotone subsequence exists. Models frequently botch the construction details, confusing row-major and column-major grid orderings or producing the wrong number of elements. **Expected single-pass accuracy: 40–50%.**

### Task ft-002: Irrationality of Sum of Square Roots

Prove that √2 + √3 + √5 is irrational, with a fully rigorous proof. If using a minimal polynomial argument, exhibit the polynomial and prove irreducibility. The minimal polynomial is degree 8 with specific coefficients, and the field extension has degree 8 over the rationals. Models commonly claim Eisenstein's criterion applies when it does not, compute the wrong polynomial coefficients, or assert the field extension degree without proof. **Expected single-pass accuracy: 30–40%.**

### Task ft-003: Divisibility in Lucas Sequence

Prove that for every prime p, the p-th Lucas number is congruent to 1 mod p. Must handle p = 2 and p = 5 as special cases and give a uniform argument for all other primes. Requires connecting Lucas numbers to Fibonacci numbers via matrix methods or the Binet formula mod p. Models frequently forget the Legendre symbol case split or invoke identities without proving them. **Expected single-pass accuracy: 25–35%.**

### Task ft-004: Continuous Nowhere-Differentiable Function

Construct a function that is continuous everywhere on the unit interval and differentiable nowhere, then prove both properties rigorously. The Weierstrass function is the standard choice but the nowhere-differentiability proof is genuinely hard. Models almost universally hand-wave the key technical lemma showing that difference quotients diverge along suitable subsequences. **Expected single-pass accuracy: 15–25% for a fully rigorous proof.**

### Task ft-005: Sylow Subgroup Counting for Order 2024

For a group of order 2024 (= 2³ × 11 × 23), prove the Sylow 23-subgroup is normal, then determine whether the Sylow 11-subgroup must also be normal. The first part is mechanical Sylow counting. The second part requires either ruling out or constructing a semidirect product, and models frequently construct invalid ones. **Expected single-pass accuracy: 30–40%.**

---

## Category 2 — Code Tasks

### Task ft-006: Interval Scheduling with Weighted Dependencies

Implement a function solving weighted interval scheduling where intervals have DAG dependencies. An interval can only be selected if all its dependencies are also selected, and no two selected intervals may overlap. The interaction between interval scheduling dynamic programming and DAG constraint propagation is subtle. Models typically get one aspect right but not both. **Expected single-pass accuracy: 20–30%.**

### Task ft-007: Persistent Red-Black Tree

Implement a fully persistent red-black tree in Python where insert and delete return new trees without mutating old ones. All red-black invariants must hold, and old versions must remain accessible. Path copying during rotations interacts badly with uncle-checking logic in rebalancing. Delete is especially treacherous in the persistent version. **Expected single-pass accuracy: 15–25%.**

### Task ft-008: Exact Convex Hull of Rational Points

Compute the convex hull of 2D points with rational coordinates using exact rational arithmetic throughout, with no floating point at any stage. Must handle all degenerate cases including collinear points, duplicates, and fewer than 3 non-collinear points. Near-collinear points that floating point would misclassify are the key test. **Expected single-pass accuracy: 25–35%.**

### Task ft-009: Lock-Free Concurrent Queue Simulation

Implement the Michael-Scott lock-free queue using simulated compare-and-swap semantics, with a test harness running 4 producers and 4 consumers. Must verify no values lost, no duplicates, and FIFO ordering within each producer. The tail-lagging case and dequeue of the dummy node are common failure modes. **Expected single-pass accuracy: 20–30%.**

### Task ft-010: Compiler for a Tiny Language with Type Inference

Implement a parser, Hindley-Milner type inference with let-polymorphism, stack-based bytecode compiler, and interpreter for a small functional language. Each component is individually manageable but the interactions between type inference and closure compilation are where models fail. Most models implement simple type checking and incorrectly claim it is Hindley-Milner. **Expected single-pass accuracy: 10–20%.**

---

## Category 3 — Design Tasks

### Task ft-011: Battery Thermal Management Trade-off

Design a thermal management system for a 27 kWh electric vehicle battery pack satisfying 6 simultaneous constraints: temperature range, cell uniformity, parasitic power, coolant volume, pressure drop, and system mass. The constraints form a tightly coupled system where optimising one degrades others. Models typically satisfy 4 or 5 constraints but violate 1 or 2. **Expected single-pass accuracy: 15–25%.**

### Task ft-012: Steel Column with Buckling and Fire

Select the lightest standard steel column section satisfying both ambient buckling resistance and 60-minute fire resistance for a 6-storey building. The optimal section for ambient design is not optimal for fire (fire favours heavier sections with lower section factor). Models frequently forget imposed load reduction factors or use the wrong buckling curve. **Expected single-pass accuracy: 20–30%.**

### Task ft-013: Solar-Powered Water Purification

Design a standalone solar-powered reverse osmosis system producing 5000 litres per day from seawater, fitting in a shipping container for under $50,000. The osmotic pressure at high recovery is nonlinear and reverse osmosis membranes have a maximum recovery per element requiring staging. These are the primary failure modes. **Expected single-pass accuracy: 15–25%.**

### Task ft-014: Audio Digital-to-Analog Converter Signal Chain

Design an analog output stage achieving -100 dB total harmonic distortion plus noise with 100 mW into 32 Ω, all from a single 5V USB supply drawing under 500 mA. The 5V constraint is the killer: achieving the required output voltage swing is impossible without either a charge pump or rail-to-rail operation, both of which compromise distortion performance. **Expected single-pass accuracy: 10–20%.**

### Task ft-015: Multi-Objective Truss Optimization

Design a planar truss bridge spanning 12 metres satisfying stress, deflection, minimum area, mass, buckling slenderness, and static determinacy constraints simultaneously. Member sizing from a discrete set of standard circular hollow sections adds a combinatorial element. The virtual work deflection calculation is tedious and error-prone. **Expected single-pass accuracy: 20–30%.**

---

## Category 4 — Synthesis Tasks

### Task ft-016: Electrochemical Water Splitting Cell

Design a proton exchange membrane electrolysis cell producing 1 Nm³/hour of hydrogen. Requires simultaneous correctness in electrochemistry (Nernst equation, Tafel kinetics), thermodynamics (reversible voltage versus thermoneutral voltage, which models confuse), and engineering sizing. The anode overpotential for oxygen evolution being much larger than the cathode hydrogen evolution overpotential is frequently missed. **Expected single-pass accuracy: 20–30%.**

### Task ft-017: Rocket Engine Nozzle Design

Design a converging-diverging nozzle for a 5 kN liquid rocket engine with specific heat ratio 1.2. Models often default to the standard air value of 1.4, producing wrong isentropic flow results. The wall thickness calculation combining pressure vessel hoop stress with thermal stress is the second failure mode. **Expected single-pass accuracy: 25–35%.**

### Task ft-018: Pharmaceutical Crystallisation Process

Design a cooling crystallisation to produce 50 kg/batch of paracetamol from ethanol-water solvent. Requires correct interaction between solubility thermodynamics, cooling rate, nucleation kinetics, and mass balance. Models typically forget residual solubility in the mother liquor, compute supersaturation profiles incorrectly, or ignore the exothermic heat of crystallisation in the energy balance. **Expected single-pass accuracy: 15–25%.**

### Task ft-019: Building Energy Model

Calculate peak cooling load and annual energy for a commercial office in Phoenix, Arizona. The solar gain calculation requires knowing which facade receives peak radiation and when. Models frequently apply peak solar irradiance to all four facades simultaneously (physically impossible), ignore latent ventilation loads, or double-count solar gain. **Expected single-pass accuracy: 20–30%.**

### Task ft-020: Distillation Column Design

Design a continuous distillation column for ethanol-water separation using McCabe-Thiele analysis. The ethanol-water system has a minimum-boiling azeotrope and the equilibrium curve has an inflection that moves the pinch point away from the feed composition. Models frequently use constant relative volatility for this highly non-ideal system or locate the pinch point incorrectly. **Expected single-pass accuracy: 25–35%.**

---

## Category 5 — Reasoning About Reasoning Tasks

### Task ft-021: Self-Verifying Proof Protocol

Design a proof verification protocol with defined inference rules, then encode the soundness proof of the protocol within the protocol itself. Must address why this does not contradict Gödel's second incompleteness theorem. The self-referential step forces a genuine cognitive tension. Most models get the basic protocol right but fail on the self-encoded soundness proof or mischaracterise the Gödel distinction. **Expected single-pass accuracy: 10–15%.**

### Task ft-022: Calibration Protocol for Uncertain Estimates

Design a protocol for producing well-calibrated probabilistic predictions, then apply the protocol to assess its own effectiveness. If the model claims high confidence its protocol works, but the protocol says to be sceptical of unverified confident claims, the model contradicts itself. The resolution requires nuanced meta-reasoning that most models cannot perform consistently. **Expected single-pass accuracy: 25–35%.**

### Task ft-023: Adversarial Prompt Detection Framework

Design a framework for detecting adversarial prompts, including detection heuristics, then construct a specific adversarial prompt that evades your own framework. Also construct a meta-adversarial input that exploits the framework description itself. The model must simultaneously defend and attack its own design. **Expected single-pass accuracy: 15–25%.**

### Task ft-024: Verification Oracle Paradox

Design a verification oracle for checking proofs, implement it for propositional logic, explain what breaks when extending to first-order arithmetic, then apply the oracle to your own response. The self-application step requires honest characterisation of what can and cannot be formalised. **Expected single-pass accuracy: 15–20%.**

### Task ft-025: Consistency of a Constraint Classification System

Analyse the consistency of the HARD versus SOFT constraint classification rules used in CDSFL itself. Must check all pairwise rule interactions, construct a genuinely difficult edge case, challenge the precedence ordering, and find a scenario where defaulting ambiguous constraints to HARD produces worse outcomes than defaulting to SOFT. This directly tests the framework being benchmarked. **Expected single-pass accuracy: 20–30%.**

---

## Cross-Cutting Notes

**Recommended for Schema C cross-model checking (10 tasks):** ft-002, ft-004, ft-006, ft-010, ft-011, ft-014, ft-016, ft-019, ft-021, ft-025. Selected because different models' training biases are most likely to produce complementary errors on these problems.

**Qualifying for Schema B modular treatment (16 tasks):** tasks with 3 or more independent modules.

**Overall difficulty range:** 10–50% single-pass accuracy, giving CDSFL room to demonstrate a statistically detectable improvement of 15–20 percentage points with 25 tasks across 3 core models.

Every task contains a genuine reasoning trap where the obvious approach is subtly wrong. The traps are not tricks — they are real challenges where iterative self-checking or cross-model checking should provide measurable benefit.
