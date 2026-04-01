# Input Complexity via Decay Curves — Analysis & P-Pass

**Date:** 1 April 2026
**Context:** Run 5 preparation (5-model baseline confer)
**Status:** Hypothesis — P-pass complete, testable predictions generated

## The Proposal

All decay curve analysis in the CDSFL codebase currently operates on **output** (findings produced by models). Dispatch decisions use model identity and failure history only. No complexity metric is computed on **input** text before dispatch.

**Proposal:** Compute a Heaps' law vocabulary growth curve on the input text itself:

1. Scan input in sequential windows (~10K chars each)
2. Measure cumulative unique vocabulary per window (after stopword removal)
3. Fit V ~ K·n^β to get β

| β value | γ = 1−β | Input character | Dispatch implication |
|---------|---------|-----------------|---------------------|
| β → 1 | γ → 0 | High lexical novelty, complex | Multi-turn FFF, WAIT steps |
| β → 0 | γ → 1 | Vocabulary saturates fast, simple | Single-turn FFF sufficient |

This is the **same Heaps/Duane duality** already proven equivalent via SymPy (1 April 2026). Same equation applied to input instead of output.

## P-Pass Falsification

### Attempt 1: Does vocabulary growth track semantic complexity in code?

**Potential flaw:** Code reuses keywords heavily (`def`, `self`, `return`). Vocabulary growth could be low even when semantic complexity is high.

**Counter:** After stopword removal (which `_tokenize_for_similarity()` already does), what remains are domain-specific tokens: class names, function names, variable names. These **do** track structural complexity.

**Verdict:** Survives. Content-token vocabulary growth correlates with structural complexity.

### Attempt 2: Is complexity→dispatch monotonic?

Dispatch should be **two-dimensional** (length × complexity):

| | Low complexity (high γ) | High complexity (low γ) |
|---|---|---|
| **Short** | Single-turn, basic FFF | Single-turn, full FFF |
| **Long** | Decomposed, basic FFF per chunk | Multi-turn, WAIT steps, FFF synthesis |

We currently only have the length axis (feasibility gate). This adds the complexity axis.

**Verdict:** Survives. Two-dimensional model is strictly more informative.

### Attempt 3: Is computation cheap enough?

~12 windows for a 120K input. Tokenization + set operations + log-log regression. Milliseconds vs seconds of API latency.

**Verdict:** Trivially cheap.

## What This Augments

| Current mechanism | Limitation | γ_input improvement |
|---|---|---|
| `_should_decompose()` — hardcoded model identity | Reactive, not input-aware | Proactive routing by complexity |
| Feasibility gate — length-based P(fits) | Ignores information density | Two-dimensional capacity model |
| Timeout — fixed per model | Doesn't scale with difficulty | Adaptive timeout from γ_input |
| FFF mode — one size fits all | Same FFF for trivial and deep tasks | FFF complexity matched to input |

## Extrapolation

**(a) What generalises:** γ_input is model-agnostic and task-agnostic. Any LLM orchestration system routing prompts to models could use it. [SPECULATIVE] This may be a publishable finding independent of CDSFL.

**(b) Boundary conditions:** Breaks down when:
- Input domain has tiny vocabulary but deep logical structure (pure mathematics)
- Difficulty dominated by reasoning depth, not concept breadth
- Formatting/boilerplate inflates token counts without adding complexity

**(c) Falsifiable predictions:**
1. γ_input predicts per-model processing time better than prompt length alone
2. γ_input correlates with finding density (findings per unit input)
3. Routing by γ_input reduces total wall-clock time vs routing by length alone
4. There exists a γ_input threshold below which multi-turn FFF outperforms single-turn

## The Popper Circle

The system uses the **same mathematical framework** (Heaps/Duane duality) to:
1. **Measure input complexity** → decide how to process (γ_input)
2. **Route dispatch** → single-turn vs multi-turn vs decomposed
3. **Detect convergence** → stop when output γ > threshold

One equation, three applications. The instrument calibrates itself with the same tool it uses to measure.
