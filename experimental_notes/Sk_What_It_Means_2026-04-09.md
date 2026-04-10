# What the S_k Confer Actually Tells Us

**Date:** 9 April 2026
**Type:** Analytical synthesis of S_k reliability confer results
**Predecessor:** Exp 37 (converged), S_k confer round (Codex + Gemini)

---

## 1. Original Questions

Five questions were posed:
1. Is the mathematical model truly optimal?
2. Can the system self-regulate toward novel discovery — not just finding problems but fixing them?
3. Can it work beyond code, across STEM domains?
4. How does it scale with more models?
5. How do we actually get solutions out of these models instead of just a list of complaints?

---

## 2. Is the Model Optimal?

The detection side is strong. Exp 37 proved it: all five models used R_k to calibrate
their own reliability, converged in 16 rounds with an 18× improvement in confirmation
rate. The microscope works.

The resolution side was barely functional. σ (solution efficacy) was model-estimated —
models grading their own homework. One fix out of six worked. Not tool-verified. Hope.

S_k closes this gap. Instead of models estimating their own fix quality, S_k derives
it from tool output. Does the fix parse? Do tests pass? Are there regressions? Each is
a measurable, verifiable score ∈ [0, 1]. Model opinion replaced by evidence.

Both Codex and Gemini independently confirmed algebraic soundness. No inconsistencies.
All special cases hold. The extension slots into the existing equation without changing
anything that already works.

**Verdict:** Detection phase was optimal. Resolution phase was a placeholder. Extended
model is now sound. Remaining gap: empirical calibration (Exp 38).

---

## 3. Self-Regulation and the Valley of Bad Fixes

Gemini discovered, and we verified numerically, that the extended equation has a
built-in penalty for half-baked fixes.

R_new(S) is not monotonically decreasing. It is a downward-opening parabola:
- S = 0: fix rejected, risk stays at baseline
- S = 1: fix works perfectly, risk drops
- S ≈ 0.3–0.5: fix **increases** risk above baseline

A fix that looks just good enough to pass some checks but is fundamentally flawed
gets merged, introduces subtle problems, and the system is worse off. The equation
captures this through the interaction between solution quality and re-injection risk.

The break-even threshold S* falls out of the mathematics — it is not a tuning parameter.

**Verdict:** The system self-regulates. It evaluates proposed solutions, rejects those
that would make things worse, and accepts only fixes that demonstrably improve the system.

---

## 4. Getting Solutions Out

Both models agreed on the core problem. The NL pipeline (describe fix in prose →
convert to code) fails 83% of the time and violates the constraint box principle.

Models must output fixes in machine-verifiable format. Two composable proposals:
- **Codex:** FixSpec JSON envelope (target file, edit operations, preconditions,
  expected properties, forbidden regressions)
- **Gemini:** SEARCH/REPLACE blocks (exact lines to find, exact replacement)

These compose: SEARCH/REPLACE blocks are edit operations inside a FixSpec envelope.
Use both. The edit block gives the change; the envelope gives the metadata.

Once in machine-readable format, the tool gate pipeline evaluates automatically:
parse → lint → test → targeted test → full regression. Each gate produces a score.
Combined: S_k.

**Verdict:** The missing piece was not the tools. It was the format.

---

## 5. Cross-Domain Generalisation

The equation R_new(S) contains no reference to code, Python, AST, or any specific
domain. It operates on abstract inputs: R (risk), q (detection), S (solution
reliability ∈ [0,1]).

What changes across domains is how S is computed:
- **Code:** parse, test, targeted test, regression
- **Mathematics:** proof parses, axiomatic step valid, target theorem satisfied
- **Chemistry:** SMILES parses, stoichiometric balance, thermodynamic viability
- **Physics:** dimensional consistency, governing equations

The minimal interface: a function that takes (proposed_fix, target_domain) and
returns a list of gate scores. The equation does the rest.

Bench Run 2's 27 STEM tasks need 27 verification functions, not 27 mathematical
models. The expert encoding architecture is exactly right.

---

## 6. Scaling

The per-finding update equation does not change with more models. What changes is
orchestration:

- **Detection:** Codex proposes correlation-adjusted q_eff to account for model
  overlap (naive independence breaks down at 10+ models)
- **Resolution:** Gemini proposes max-pooling — compute S_k for each model's fix,
  pick the best. If even the best falls below S*, all rejected.

These operate at different levels (detection vs resolution) and compose without conflict.

Recommended topology: star (proven in Exp 37). Parallel finding, centralised
verification, parallel fix generation, centralised S_k evaluation.

---

## 7. The Composed Model

The proposals from Codex and Gemini operate at different layers and compose fully:
- A·E structure (hard admissibility × graded evidence) subsumes simpler product form
- Bounded ν_eff subsumes linear form
- FixSpec envelope contains SEARCH/REPLACE blocks
- Correlation-adjusted detection and max-pooling resolution complement each other

Zero mutual exclusivity at the mathematical level.

**Note (updated 10 April 2026):** The "three-arm experiment" mentioned in the
original confer synthesis (baseline vs minimal S_k vs full composed) was superseded
by the ouroboros design for Exp 38. Three-arm calibration is deferred to post-Exp 38
as a follow-up to empirically measure S_k gate weighting. See Exp 38 plan for
current experiment design.

---

## 8. ν* and S* Duality

The confer produced two dual perspectives on the break-even condition:

**S* (implemented):** Minimum fix quality for a given re-injection rate.
```
S* = (ν_b + ν_f - ν_b·ν_f - q·R) / (ν_f · (1 - ν_b))
```
Answers: "Is this fix good enough?"

**ν\* (documented, not separately computed):** Maximum tolerable re-injection rate
for a given fix quality.
```
ν* = S_k · R · q / (1 - q · R · (1 - S_k))
```
Answers: "How much re-injection can I tolerate?"

These are algebraic duals — knowing one gives you the other. The runner implements
S* because it answers the operational question. ν* answers the design question and
is available for analytical use but is not computed in the pipeline.

---

## 9. What Comes Next

1. ~~Add ν_b + ν_f ≤ 1 constraint~~ — DONE (Fix 5)
2. ~~Implement machine-readable fix output~~ — DONE (SEARCH/REPLACE parser)
3. ~~Build tool gate pipeline~~ — DONE (AST, py_compile, ruff, bandit, regression)
4. ~~Implement S* threshold gate~~ — DONE (Fix 7, with edge cases)
5. Run Experiment 38 — ouroboros design (supersedes three-arm)
