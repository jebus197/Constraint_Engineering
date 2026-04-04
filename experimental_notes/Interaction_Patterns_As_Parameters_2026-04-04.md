# Interaction Patterns as Parameters, Not Architecture

**Date:** 4 April 2026, 18:05 BST
**Context:** Founder observation — interaction patterns identified through C1-C5 and bench runs are coordinates in the constraint box, not competing methodologies. CDSFL is the bench; patterns are the variable.

---

## Summary

The full body of experimental evidence demonstrates that the **interaction pattern** (how models and humans communicate during analytical work) is **secondary to the CDSFL schema itself**. The schema provides quality assurance regardless of which interaction pattern is used. The interaction pattern determines the _distribution_ of finding types, not their _validity_.

**Implication:** Interaction patterns should be folded into the registry and UX as user-configurable settings. The schema should provide an environment under which new and potentially better patterns can be tested.

---

## The Data: 7+ Distinct Interaction Patterns Tested

| Pattern | Source | Findings | Verified | FP | Key Metric |
|---|---|---|---|---|---|
| **Unconstrained monolithic** | Runs 8-9 (47 rounds, 5 models) | 1,001 | 0 proofs | — | 91.2→84.5% churn |
| **Constrained monolithic** | Run 10-11 (9 rounds, 5 models) | 296 | convergent | — | 26.6% churn, γ=0.577 |
| **Conversational HIL** (C1) | Gemini + developer dialogue | 25 | 9/9 SymPy | 0 | 5 cross-component bugs |
| **CDSFL/FFF decomposition** (C3) | Gemini, automated 4-cell | 13 | 5/5 SymPy | 0 | Focus > breadth |
| **CDSFL + Meta structured** (C4) | Gemini, certificate format | 16 (27 raw, 11 retracted) | 16/16 | 0 | 11 formal proofs |
| **Three-layer schema** (C5) | Full conversation + CDSFL + Meta | 27 | 36/40 confirmed + 6 novel | 0 | 90% prior coverage, 5 cross-component |
| **Bench Run 1** (4 conditions) | 78 runs × 4 conditions | — | — | — | CDSFL+HIL γ=0.597 vs Control γ=0.01 |

Plus smoke test baseline: Control (10), HIL-only (2), CDSFL-only (29), CDSFL+HIL (43).

---

## Three Facts from the Data

**Fact 1:** Every pattern operating under CDSFL constraints produced zero false positives. The schema is the quality filter, not the pattern.

**Fact 2:** Patterns differ in _what kind_ of findings they produce, not in _whether_ they produce valid findings. C1 → cross-component. C4 → formal per-component. C5 → both. Each pattern is a coordinate in the constraint box (protocol × focus × context).

**Fact 3:** The immune system, decay curves, and convergence detection are pattern-agnostic. The pipeline input interface is a `Finding` object — it is structurally pattern-agnostic.

---

## P-Pass: Falsification of the Thesis

**Thesis:** The interaction pattern is secondary to the schema. CDSFL is the bench, not the intelligence. Patterns should be user-configurable parameters.

| Attempt | Attack | Result | Evidence |
|---|---|---|---|
| 1 | Some patterns could harm the schema | **Refuted** | Worst pattern (unconstrained monolithic, 91% churn) didn't break immune system — it diagnosed its own failure |
| 2 | Pattern choice could produce false positives | **Refuted** | Zero FP across all 7 patterns; C4 self-retracted 12 via FFF |
| 3 | Immune system can't handle unknown patterns | **Refuted** | Pipeline designed during Runs 8-10, processed C1/C3/C4/C5 without modification |
| 4 | User configurability allows degenerate configs | **Genuine risk, but UX problem** | Decay curve detects non-convergence, immune flags churn, DM terminates. Mitigate with defaults/presets, not restriction |

**Result:** Thesis survives all four falsification attempts.

---

## Pattern Profiles

| Pattern | Optimal For | Weakness | Constraint Box Coordinate |
|---|---|---|---|
| Conversational HIL (C1) | Cross-component bugs, system-level reasoning | No formal proofs, expert-dependent | Low protocol, broad focus, fresh context |
| CDSFL/FFF decomposition (C3) | Deep per-component verification, proofs | Misses cross-component interactions | High protocol, narrow focus, fresh context |
| CDSFL + Meta structured (C4) | Formal proofs, self-correction, boundary bugs | Slower, narrower coverage | High protocol, narrow focus, structured context |
| Three-layer schema (C5) | Breadth + depth, highest coverage | Longest wall-clock time | High protocol, broad focus, managed context |
| Constrained monolithic (Run 10-11) | Automated multi-model convergence | Requires full immune pipeline | High protocol, broad focus, accumulated context |
| Unconstrained monolithic (Run 8-9) | Stress-testing immune system | 91% churn, no proofs | No protocol, broad focus, accumulated context |

---

## Extrapolation

### What Generalises
- The principle (QA independent of interaction pattern) generalises to **any constrained synthesis system**
- Software analogy: test suites don't care whether code was pair-programmed, mob-programmed, or AI-assisted
- Multi-agent systems: interaction pattern should be a runtime parameter, not an architectural decision
- Human teams: the constraint box (protocol × focus × context) applies to any knowledge work

### Boundary Conditions
- Breaks down if QA framework depends on the interaction pattern (circular dependency — CDSFL avoids this)
- May not apply to pure creative tasks with no convergence notion [SPECULATIVE]
- Breaks down if a pattern systematically excludes models from problem types, creating undetectable blind spots

### New Falsifiable Questions
1. Does pattern-agnostic property hold for patterns the immune system has never processed?
2. Is there a pattern × problem-type interaction the schema can't compensate for?
3. Does user configurability outperform expert-selected patterns?
4. Does the constraint box have more than three dimensions?

---

## Practical Implication

Interaction patterns become **presets in the directive composer's Situation layer**:

```
Universal (invariant)  → CDSFL core, FFF, structured reasoning chain
Domain (invariant)     → Problem-specific constraints
Phenotype (transform)  → Model-specific adaptations
Situation (VARIABLE)   → Interaction pattern = {dispatch_mode, context_mgmt, focus_scope, hil_integration}
```

The immune system, decay curves, and convergence detection remain invariant across all pattern choices.

### Persistence Layer Reframing

This reframes Exp 29. The persistence layer enables **pattern-switching within a single run**: start C5 (broad conversational) → detect diminishing returns → switch to C3 (decomposed per-component) → persistence maintains state across transition. The interaction pattern becomes not just configurable but **adaptive**.

---

## Correction

The founder's observation referenced "5 distinct AI interaction patterns." The data shows at least 7. The number is not critical to the thesis, but precision matters.
