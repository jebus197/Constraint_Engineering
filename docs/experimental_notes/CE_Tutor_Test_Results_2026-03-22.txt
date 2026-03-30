# CE Tutor Style Decomposition Test Results

**Date:** 2026-03-22

---

## Summary

Both models completed all 8 steps of the Weierstrass nowhere-differentiable function proof under persistent conversation tutor-style decomposition. Codex 5.3 went from total failure under stateless invocation to full completion. The approach validates standard pedagogical practice applied to language models.

---

## What We Tested

Task ft-004 asks models to prove that the Weierstrass function f(x) = sum from n=0 to infinity of a^n * cos(b^n * pi * x) is continuous everywhere but differentiable nowhere on the interval [0, 1].

Previous attempts failed: Claude timed out at 900 seconds and 1200 seconds under monolithic prompting. Codex produced zero output under stateless per-step invocation. The problem was too large to present all at once.

---

## The Tutor Approach

We broke the problem into 8 sequential steps presented one at a time in a persistent conversation. Each step builds on the model's own prior answer. The tutor says things like "use your construction from step 4a" and "use your values of C and C'." The model accumulates understanding exactly as a student does during a lecture.

- **Step 1.** Setting and understanding
- **Step 2.** Construction parameters
- **Step 3.** Continuity proof
- **Step 4a.** Construct the sequence x_m
- **Step 4b.** Bound the dominant term
- **Step 4c.** Bound head and tail terms
- **Step 4d.** Combine and conclude
- **Step 5.** Self-verification of the complete proof

---

## Results

**Gemini 3.1 Pro** completed all 8 steps in 220 seconds. It produced the classical proof with C = 2/3 and recovered the standard sufficient condition ab > 1 + 3π/2 ≈ 5.71.

**Codex 5.3** completed all 8 steps in 575 seconds. It produced a non-standard variant with C = 1 and derived the sharper sufficient condition ab > 1 + π ≈ 4.14.

Both algebraic derivations verified correct by Wolfram Mathematica.

---

## The Critical Finding

The two models independently chose different constructions for the sequence x_m.

**Gemini** chose the approach direction with opposite sign to the fractional part e_m. This gives a denominator bound of 3/2 and therefore C = 2/3.

**Codex** chose the approach direction with same sign as the fractional part e_m. This gives a denominator bound of 1 and therefore C = 1. This is a tighter bound that relaxes the sufficient condition.

Neither result is novel in absolute terms — Hardy proved the theorem for ab ≥ 1 in 1916. But the fact that tutor-style decomposition produced two independent valid proofs with different constructions validates the approach for multi-architecture review. You get genuine mathematical diversity, not just stylistic variation.

---

## Self-Verification Quality

Both models identified real issues in their own proofs when given full context.

**Gemini** caught a boundary domain issue: x_m might temporarily fall outside the interval [0, 1] for points near the boundary, and resolved it.

**Codex** caught three issues:
1. The sum/limit interchange needs justification by absolute convergence.
2. Boundary subcases need explicit treatment.
3. A notation mismatch between the tutor prompt and its own variable names.

Neither of these self-verification findings would surface under stateless invocation where the model has no context of its own prior work.

---

## Implications

The tutor approach works because it respects working memory limits that appear to be architectural in language models, not unlike human students. Breaking problems into sequential steps with context accumulation is standard teaching practice. It is not a novel technique. It is established pedagogy applied to machines.

The methodology change from stateless to persistent conversation invocation is documented as a phase boundary in the experimental record. Phase 1 (12 completed stateless runs) is retained as pilot data. Phase 2 (persistent conversations) is the main experiment. The two phases are not pooled for confirmatory analysis.

Codex P-passed this methodology change and raised 5 findings. All were addressed. The key accepted finding is that persistent conversation and sequential decomposition are a confounded intervention, which is architecturally coupled and acknowledged as a known limitation.

---

## Next Steps

A 3-task smoke test covering maths, code, and cross-domain tasks under all 4 factorial conditions with the revised persistent conversation delivery, before proceeding with the remaining 88 runs of the full benchmark.
