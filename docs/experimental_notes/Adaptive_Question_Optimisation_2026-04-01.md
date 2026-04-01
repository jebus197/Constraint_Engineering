# Adaptive Question Optimisation — P-Pass

**Date:** 1 April 2026
**Context:** Founder extension of amplification factor hypothesis
**Status:** Hypothesis — P-pass complete, compound objective defined

## The Proposal

If CDSFL can measure amplification (A = β_output/β_input), it can learn which
question patterns produce high-A responses and preferentially generate those
questions. Subject always to Occam: simplest sufficient solution.

**This moves CDSFL from passive measurement to active question optimisation.**

## The Compound Objective

Select question Q that maximises:

```
E[A(Q)] × E[steepness(γ_output(Q))]
```

subject to:

```
simplicity(Q) ≤ Occam_threshold    (HARD)
novelty(Q)    > novelty_threshold   (no repetition)
```

Where E[·] is estimated from historical (question, output) pairs.

**Key insight:** Not "maximise A." Maximise A × output decay steepness.
A question producing 20 findings where the first 5 are high-severity scores
better than one producing 20 mediocre findings. Same A, steeper decay.

## P-Pass Falsification

### 1. Can A be estimated for unasked questions?

Learnable features that predict high A:
- **Referential density** — how many existing concepts the question connects
- **Novelty** — targets unexplored territory
- **Specificity** — targeted vs broad

The founder's input complexity question: 5 existing concepts in 2 sentences.
High referential density, low lexical density → high A.

**Verdict:** Survives. Feature-based estimation is learnable.

### 2. Does maximising A always help?

Three constraints prevent pathological outcomes:
1. **Occam** — prefer simplest high-A question
2. **Output γ** — convergence detection catches churn
3. **Steep decay preference** — front-loads value, self-limits

**Verdict:** Survives with compound criterion.

### 3. Runaway feedback loop?

Three brakes: Occam (hard), convergence detection (γ), and steep-decay self-limitation.
Questions that resolve quickly are preferred over questions that open infinite scope.

**Verdict:** Survives. Converges on efficient questions, not escalating ones.

### 4. Overfitting to past success?

Feature space must be abstract (referential density, novelty, specificity) not
template-based. Novelty feature actively penalises repetition.

**Verdict:** Survives if features are structural, not content-specific.

## Extrapolation

**(a) Generalises to:** Any iterative LLM pipeline. Formalises what senior
researchers do intuitively — learn which questions are productive. [SPECULATIVE]
Basis for autonomous research agents that improve questioning over time.

**(b) Boundary conditions:**
- Cold-start on new domains (no history)
- Occam must be HARD constraint (physics-tier in P-pass classification)
- Best for iterative review, not one-shot queries
- "Question quality" is partly subjective — measurable proxies (A, steepness)
  approximate but don't fully capture insight

**(c) Falsifiable predictions:**
1. High referential density + low lexical density → higher A (controlled for length)
2. E[A] × E[steepness] question selection → more unique HARD findings per round
3. Occam constraint reduces wall-clock vs unconstrained A-maximisation
4. Question quality (A × steepness) improves monotonically over rounds, then plateaus

## The Popper Connection

CDSFL formalises falsification (testing hypotheses). This extends it to
formalise **bold conjectures** (selecting hypotheses worth testing).

Popper's bold conjecture: simple, high testable consequences, resolves quickly.
Compound objective: high A, steep decay, Occam-simple.

**Same criterion. Same mathematics. Same framework.**

The scientific method is not just about testing hypotheses.
It is about learning which hypotheses are worth testing.
CDSFL can now formalise both.
