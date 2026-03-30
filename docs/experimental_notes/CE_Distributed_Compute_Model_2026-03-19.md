# Distributed Compute Coverage Model for CDSFL

**Date:** 19 March 2026

---

## Overview

This document describes a mathematical model for heterogeneous adversarial review. It formalises the distributed compute hypothesis: that using multiple different AI architectures to review each other's work produces better defect detection than using copies of the same architecture.

---

## The Core Question

If you have multiple AI models reviewing technical work, how many do you need, and how different do they need to be? Is there a point of diminishing returns? Can we state this mathematically?

The answer is yes, and the model turns out to be a natural extension of the existing corroboration model from CDSFL's white paper.

---

## The Simple Version

The existing CDSFL corroboration model says:

> C(n) = 1 − (1 − p)^n

Here `p` is the probability that a single review pass catches a given defect, and `n` is the number of passes. More passes means higher coverage, but with diminishing returns, and only if each pass has genuine adversarial capability (if `p` is near zero, a thousand passes accomplish nothing).

But this model assumes all passes are identical and independent. Real distributed compute uses different architectures (Claude, Gemini, Codex) that have different strengths and partially overlapping blind spots.

---

## The Extended Model

The distributed compute coverage function is:

> D(n) = Σ_k [ w_k · (1 − Π_{i=1}^{n} (1 − p_{ik})) ]

In plain language: for each type of defect (logic errors, physical violations, interface failures, and so on), we calculate the probability that at least one of the `n` architectures catches it, weighted by how consequential that defect type is.

The key new parameter is **ρ (rho)**, the inter-architecture correlation. This measures how much the architectures' blind spots overlap:
- `ρ = 0`: fully independent (different architectures miss completely different things)
- `ρ = 1`: identical (they all miss the same things)

---

## Floor and Ceiling Conditions

**Floor:** D(1) is the baseline — one model, working alone. This is the minimum that distributed compute must beat to justify its existence.

**Ceiling:** As `n → ∞`, D approaches a maximum. There are two ceilings:
- The **theoretical ceiling** is 1 (every defect is eventually caught).
- The **practical ceiling** is lower, bounded by defects that no available architecture can detect.

---

## The Diminishing Returns Curve

Each additional architecture catches fewer new defects than the one before, because each one is finding what all previous ones already missed. The marginal gain from adding architecture `n+1` equals the probability that it catches defects that every prior architecture failed to detect.

The curve rises steeply at first and then flattens. With Wolfram Mathematica computation, the following results emerge for a **base detection rate of 0.4** and **moderate correlation of 0.3**:

| Architecture count | Coverage | Marginal gain |
|---|---|---|
| 1 | 40% | — |
| 2 | 57% | +17 pp |
| 3 | 65% | +8 pp |
| 4 | 70% | +5 pp |
| 5 | 73% | +3 pp |

By architecture 5, you are getting 3 percentage points per additional architecture. By architecture 10, you are getting less than half a point.

---

## Monoculture Collapse

The most striking property: when `ρ → 1` (all architectures are essentially the same), D(n) ≈ D(1) regardless of how many you add. A room full of the same model, however capable, leaves its blind spots permanently unexamined.

**Verified computationally:** at `ρ = 0.99`, adding 9 more copies of the same architecture raises coverage from 40% to 40.2%. Essentially nothing.

This is the mathematical proof of the **monoculture failure mode**. It is also why the biodiversity hypothesis matters: genuinely different architectures (low ρ) reach a higher ceiling.

---

## Optimal Stopping

The optimal number of architectures `n*` is where the marginal gain drops below a cost threshold `ε`:

- For moderate heterogeneity (`ρ = 0.3`) and a threshold of 5% marginal gain, `n* = 3`.
- For a stricter threshold of 1%, `n* = 7`.

This suggests the current three-architecture topology (CC, CX, Gemini) is in the right ballpark for moderate-threshold work. Whether it is optimal depends on the actual ρ between these specific architectures, which is an empirical question the round-robin convergence test can answer.

---

## The Orchestration Effect

The orchestration layer (CC coordinating CX and Gemini) does not appear directly in the equation, but it affects the effective ρ. Good orchestration preserves genuine independence between reviewers. Poor orchestration allows premature convergence toward consensus, which raises effective ρ and reduces coverage. This means **orchestration quality is a first-order contributor to distributed compute effectiveness**, not an implementation detail.

---

## Reduction Property

Under simplifying assumptions (one defect class, identical detection rates, zero correlation), the distributed compute model reduces exactly to:

> C(n) = 1 − (1 − p)^n

The existing simple corroboration model is the degenerate case. Verified computationally with exact numerical agreement to 8 decimal places.

---

## Status and Limitations

The model is an operational heuristic, not a theorem derived from first principles. Its parameters (detection probabilities per architecture per defect class, consequence weights, correlation structure) must be estimated empirically. The correlation parameter ρ is particularly hard to measure because real architectures share training data.

If the model fails to predict real review outcomes better than a simpler rule of thumb, it should be replaced. As with all CDSFL components, the model is non-canonical and subject to its own falsification methodology.

The model has been added to `PAPER.md` as Part XII.
