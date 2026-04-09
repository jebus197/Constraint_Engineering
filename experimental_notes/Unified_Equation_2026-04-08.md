# Unified Self-Assessment Equation — Plain English Explanation

*8 April 2026. Derived during Exp 37 build. Verified by SymPy and Wolfram Alpha.*

---

## The Core Idea

The entire CDSFL mathematical model, as it relates to a model's own reasoning, collapses into a single equation. Not a system of equations. Not a collection of separate metrics. One equation, applied recursively after each falsification pass.

The equation answers one question: **how much risk remains that I have missed something?**

That question is the only question that matters for self-assessment. Not "how hard did I try?" (which is what the coverage model F_n measures). Not "how many passes did I run?" The question is about residual risk — the weighted probability, across all types of flaw, that a flaw still exists despite testing.

---

## The Equation

**Per-class risk update (recursive):**

> **R_k(i) = R_k(i-1) · (1 − q_ik) / (1 − q_ik · R_k(i-1))**

**Effective detection:**

> **q_ik = d_ik · p_ik**

**Total weighted residual risk:**

> **R_n = Σ_k w_k · R_k(n)**

**Marginal gain from next pass:**

> **ΔR_k = q · R_k · (1 − R_k) / (1 − q · R_k)**

**Stopping rule:**

> Continue while Σ_k w_k · ΔR_k > θ

**Initial condition:**

> R_k(0) = π_k

---

## Term-by-Term Walkthrough

**R_k — residual risk for flaw class k.** The probability that a flaw of this type still exists, given everything checked so far. Starts at the prior flaw rate π_k. Decreases after each pass. How much depends on the quality of the pass.

**q_ik — effective detection probability.** The product of two factors:

- **p_ik — detection capability.** How likely is this check to catch a flaw of type k, if one exists? A model catching logic errors at p=0.7 might catch unit-of-measure errors at p=0.05. Varies by flaw class. The model should be honest about what it is good at.

- **d_ik — diversity of approach.** How independent is this check from previous ones? Repeating exactly the same analysis: d ≈ 0 (learn nothing new). Switching tools, changing perspective, examining different boundary conditions: d is high (genuinely informative). This is the mathematical formalisation of Popper's principle — corroboration is proportional to the severity of the test.

**w_k — consequence weight.** Not all flaw classes matter equally. Logic errors in safety-critical code carry more weight than stylistic inconsistencies. The model weights risk by consequence, naturally investing more falsification effort where stakes are higher.

**π_k — prior flaw rate.** Initial condition only. How likely was a flaw of this type before any testing? Appears once, at the start, then **vanishes from the update rule entirely** (mathematically verified — see below).

---

## The Elegant Property: π Vanishes

Verified independently by SymPy and Wolfram Alpha.

Once you have your current risk estimate R_k, the update rule depends on only two things: your current risk, and the effective detection of your next pass. The prior is absorbed into the running risk estimate and never referenced again.

This makes the equation **self-contained at every step**. A model can pick it up at any point, assess current risk, and decide what to do next. No history required beyond the current state.

---

## The Marginal Gain and Stopping

**ΔR_k = q · R_k · (1 − R_k) / (1 − q · R_k)**

The **(1 − R_k) factor** is the key: the less risk remains, the less there is to gain. Diminishing returns are built into the mathematics. No external rule needed — the marginal gain drops below threshold naturally.

When **Σ_k w_k · ΔR_k < θ**, further testing is not justified.

---

## Special Cases (All Verified)

| Condition | Result | Meaning |
|---|---|---|
| q = 0 (same check repeated) | R unchanged | Learned nothing |
| q = 1 (perfect, fully independent) | R → 0 | Ideal; never quite reached |
| R = 0 (no risk) | Stays 0 | Cannot create risk by testing |
| R → 1 (certain flaw) | Stays near 1 | Cannot trick self into false confidence |
| d = 0 (fully correlated pass) | q = 0, R unchanged | Correlated testing adds nothing |

Every simpler model (C(n), F_n, R_n) is a special case of this equation.

---

## Relationship to External Signals

External signals inform parameter estimates — they do not add terms:

| Signal | Informs | How |
|---|---|---|
| γ (reliability growth) | p for next pass | High γ → panel depleted → low p likely |
| ρ (discovery efficiency) | d for next pass | Low ρ → redundancy → need different approach |
| v̄ (verification rate) | p calibration | Dropping v̄ → be more conservative on p |

---

## Practical Usage (5 Steps)

1. **Classify** flaw types relevant to the task. Assign consequence weights w_k.
2. **Set priors** π_k per class. Novel/untested → high. Well-verified → lower.
3. **After each pass**, estimate p and d. Compute q = d·p. Update R_k.
4. **Compute marginal gain**. If Σ w_k · ΔR_k < θ, stop. Otherwise target highest weighted R_k with most independent approach available.
5. **Report** final R_k per class and total R_n. This is computed residual risk, not a confidence score.

---

## Reduction Property

Under simplifying assumptions (K=1, d=1, all p_ik = p, π=0.5):

> R_n = (1−p)^n / (1 + (1−p)^n)

This is the standard Bayesian posterior for repeated Bernoulli non-detection — the simplified model kept for the white paper. The unified equation generalises it to multi-class, diversity-aware, consequence-weighted self-assessment.
