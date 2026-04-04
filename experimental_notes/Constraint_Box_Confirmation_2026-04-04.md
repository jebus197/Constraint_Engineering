# Constraint Box Confirmation: Immune Cell Review as Empirical Test

**Date:** 4 April 2026, 00:00 BST
**Context:** Founder observation — the immune cell review results confirm the founding thesis, not a new discovery

---

## Core Insight

The immune cell review experiment (4 Gemini conversations under CDSFL/FFF) did not discover a new principle. It empirically confirmed the constraint box thesis proposed at the project's outset: models operating within tighter, well-defined solution spaces produce higher-quality output.

What was previously decomposed as "focus + protocol" is the constraint box applied across three dimensions simultaneously:

| Dimension | Constraint | Unconstrained (Runs 8-10) | Fully Constrained (Cell Review) |
|-----------|-----------|--------------------------|--------------------------------|
| Protocol | How to reason | CDSFL on models, but broad mandate | CDSFL/FFF with "press harder" |
| Focus | What to reason about | 244K chars, full codebase | 2K chars, single cell |
| Context | How much to carry | Accumulated findings, 47 rounds | Fresh instance, zero history |

## Evidence

- **Unconstrained:** 47 rounds, 5 models, 1,001 findings, 0 verified proofs
- **Fully constrained:** 12 rounds, 1 model, 13 findings, 5/5 verified proofs

Same model. Same code. Different constraint box.

## Proposed 4-Condition Comparison Experiment

| Condition | Protocol | Focus | Context | Prediction |
|-----------|----------|-------|---------|------------|
| 1 | None | Broad | Accumulated | Worst |
| 2 | CDSFL/FFF | Broad | Accumulated | Intermediate |
| 3 | None | Cell-level | Fresh | Intermediate |
| 4 | CDSFL/FFF | Cell-level | Fresh | Best |

If C3 ≈ C4: effect is primarily attention management (routing)
If C2 ≈ C4: effect is primarily methodological rigour (protocol)
If C2 ≈ C3 ≪ C4: interaction effect dominates (all dimensions needed)

## Key Principle

The box constrains the **method**, not the **conclusion**. FFF says *how* to think, not *what* to think. The model is free to find anything — including things that surprise the operator — as long as it arrives there through structured falsification.
