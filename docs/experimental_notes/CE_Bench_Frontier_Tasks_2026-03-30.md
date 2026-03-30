# CDSFL Bench: 27 Frontier-Level Tasks

**30 March 2026**

---

## Overview

The CDSFL bench consists of 27 frontier-difficulty tasks where single-pass model accuracy ranges from 10 to 50 percent. These are genuine hard problems across 8 domains and 7 categories. Each task is defined as a JSON file in `bench/tasks_frontier/`. The bench tests whether CDSFL improves detection and correctness compared to unstructured review.

---

## Category 1: Proof — 5 tasks

Mathematical proofs and constructions.

- **FT-001. Monotone Subsequence Bound Tightening.** Mathematics. Expected accuracy 40 to 50 percent. Prove the Erdos-Szekeres theorem and construct a tight example for n equals 4. Models commonly produce wrong sequence length or confuse grid orderings.

- **FT-002. Irrationality of Sum of Square Roots.** Mathematics. Expected accuracy 30 to 40 percent. Prove that the square root of 2 plus the square root of 3 plus the square root of 5 is irrational using minimal polynomial with field extension degree 8. Requires computing correct polynomial coefficients and proving irreducibility where Eisenstein does not work.

- **FT-003. Divisibility in Lucas Sequence.** Mathematics. Expected accuracy 25 to 35 percent. Prove L sub p is congruent to 1 mod p for all primes p. Models forget special cases for p equals 2 and p equals 5, invoke identities without justification, and confuse Lucas with Fibonacci numbers.

- **FT-004. Continuous Nowhere-Differentiable Function.** Mathematics. Expected accuracy 15 to 25 percent. Construct and prove the Weierstrass function is continuous everywhere and differentiable nowhere. Continuity is straightforward. Nowhere-differentiability requires explicit sequence construction, detailed error bounds, and correct conditions.

- **FT-005. Sylow Subgroup Counting for Order 2024.** Mathematics. Expected accuracy 30 to 40 percent. Apply Sylow theorems to determine whether certain subgroup counts must equal 1. Tests whether models can construct or rule out semidirect products.

---

## Category 2: Code — 5 tasks

Programming and algorithms.

- **FT-006. Interval Scheduling with Weighted Dependencies.** Software. Expected accuracy 20 to 30 percent. Weighted interval scheduling with directed acyclic graph dependency constraints. Optimal substructure breaks when dependencies force inclusion of overlapping ancestors.

- **FT-007. Persistent Red-Black Tree.** Software. Expected accuracy 15 to 25 percent. Implement a red-black tree with persistent (immutable) versioning where rotations must use path copying instead of in-place mutation. Models often produce mutable implementations.

- **FT-008. Exact Convex Hull of Rational Points.** Software. Expected accuracy 25 to 35 percent. Compute convex hull maintaining exact rational arithmetic with no floating point. Must handle collinear point degeneracy.

- **FT-009. Lock-Free Concurrent Queue Simulation.** Software. Expected accuracy 20 to 30 percent. Simulate a lock-free queue with compare-and-swap. Prove no deadlocks and no lost operations under concurrent stress. Models miss race conditions and the ABA problem.

- **FT-010. Compiler for a Tiny Language with Type Inference.** Software. Expected accuracy 10 to 20 percent. Implement a compiler with Hindley-Milner type inference including generics, polymorphic functions, and type unification. Models commonly miss the occurs check.

---

## Category 3: Design — 5 tasks

Engineering design with quantifiable constraints.

- **FT-011. Battery Thermal Management Trade-off.** Hardware. Expected accuracy 15 to 25 percent. Battery charging rate versus thermal dissipation with chemical constraints including Arrhenius and diffusion equations and safety limits. Multi-physics coupling.

- **FT-012. Steel Column with Buckling and Fire Resistance.** Structural. Expected accuracy 20 to 30 percent. Design steel column for buckling using Euler and Perry-Robertson formulas while meeting fire resistance via ISO 834 thermal analysis. Interaction between cold and hot criteria.

- **FT-013. Solar-Powered Water Purification System.** Cross-domain. Expected accuracy 15 to 25 percent. Design complete system coupling solar photovoltaic, desalination, thermal storage, and filtration. Efficiency losses cascade through the chain.

- **FT-014. Audio DAC Signal Chain.** Hardware. Expected accuracy 10 to 20 percent. Design digital-to-analog converter with noise shaping, anti-alias filtering, and impedance matching. Many interacting constraints including z-transforms and component parasitics.

- **FT-015. Multi-Objective Truss Optimisation.** Structural. Expected accuracy 20 to 30 percent. Minimise mass, deflection, and stress in a truss under load. Pareto frontier and trade-off analysis. Not a single optimum.

---

## Category 4: Synthesis — 5 tasks

Multi-domain physical systems.

- **FT-016. Electrochemical Water Splitting Cell.** Chemistry. Expected accuracy 20 to 30 percent. Design electrochemical cell with electrodes, membrane, and electrolyte to achieve target current density and overpotential. Butler-Volmer kinetics and Nernst-Planck transport.

- **FT-017. Rocket Engine Nozzle Design.** Industrial. Expected accuracy 25 to 35 percent. Isentropic flow analysis, nozzle shape optimisation via method of characteristics, thermal stresses, and structural margins.

- **FT-018. Pharmaceutical Crystallisation Process.** Chemistry. Expected accuracy 15 to 25 percent. Design batch crystallisation for yield, purity, and particle size distribution. Nucleation is stochastic. Polymorph risk.

- **FT-019. Building Energy Model.** Cross-domain. Expected accuracy 20 to 30 percent. Thermal model of a building including insulation, solar gain, internal loads, and HVAC. Coupled heat transfer and occupancy schedules.

- **FT-020. Distillation Column Design.** Chemistry. Expected accuracy 25 to 35 percent. Design distillation column with stages, reflux ratio, and reboiler duty. Equilibrium versus rate-based models and pinch analysis.

---

## Category 5: Reasoning — 5 tasks

Self-referential and meta-level verification.

- **FT-021. Self-Verifying Proof Protocol.** Cross-domain. Expected accuracy 10 to 15 percent. Design a protocol where agents mutually verify proofs. Prove the protocol itself is sound. Self-application creates recursion.

- **FT-022. Calibration Protocol for Uncertain Estimates.** Cross-domain. Expected accuracy 25 to 35 percent. Design iterative calibration of estimates with confidence intervals. Prove convergence. Requires measure theory.

- **FT-023. Adversarial Prompt Detection Framework.** Software. Expected accuracy 15 to 25 percent. Design classifier to detect adversarial prompts while simultaneously attacking your own design. Tests cognitive conflict between defending and attacking.

- **FT-024. Verification Oracle Paradox.** Mathematics. Expected accuracy 15 to 20 percent. Design an oracle that verifies proofs, then apply it to verify its own correctness. Godel incompleteness applies.

- **FT-025. Consistency of a Constraint Classification System.** Cross-domain. Expected accuracy 20 to 30 percent. Analyse CDSFL's own constraint classification rules for internal consistency. Directly tests the framework against itself.

---

## Category 6: Special — 2 tasks

- **FT-026. Superdeterminism versus Quantum Randomness.** Physics. Expected accuracy 10 to 20 percent. Analyse the CHSH inequality, statistical independence assumptions, and no-faster-than-light-signaling compatibility. Requires simultaneous understanding of quantum mechanics, statistical mechanics, and special relativity.

- **FT-027. Riemann Hypothesis Structured Analysis.** Mathematics. No expected accuracy (open problem). Structured analysis of the Riemann Hypothesis. Not a proof attempt. Tests whether models can honestly classify claims as HARD, SOFT, or SPECULATIVE without false confidence.

---

## Summary by Domain

| Domain | Tasks |
|---|---|
| Mathematics | 7 |
| Software | 6 |
| Cross-domain | 5 |
| Chemistry | 3 |
| Hardware | 2 |
| Structural | 2 |
| Industrial | 1 |
| Physics | 1 |

---

## Experimental Conditions

Each task runs under 4 conditions.

1. **Control.** No CDSFL directives. The model works without methodology.
2. **Universal directives only.** The core CDSFL framework as system prompt.
3. **Universal plus domain-specific directives.** CDSFL with domain expertise.
4. **Domain-specific directives only.** Domain expertise without CDSFL.

This is a 2 by 2 factorial design. 27 tasks times 4 conditions equals 108 experimental runs. 5 models per run: Claude Opus 4.6, GPT 5.4 via ChatGPT, GPT 5.4 via Codex, Gemini 3.1 Pro, and DeepSeek Reasoner. Bench Run 1 completed approximately 78 of 108 runs.

### P-pass Schemas

3 P-pass schemas are used.

- **Schema A.** Standard monolithic. 5 passes. All 27 tasks.
- **Schema B.** Extended modular. 4 passes plus 1 adversarial pass. 20 tasks with 3 or more independent modules.
- **Schema C.** Cross-model adversarial. 13 representative tasks. Models review each other's work.
