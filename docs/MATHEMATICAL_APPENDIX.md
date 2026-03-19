# Mathematical Appendix: Extensions to the CDSFL Formal Model

*Technical supplement to the [White Paper](../PAPER.md). For the core models (simple corroboration C(n), structured operational F_n, anchor states A0–A3), see Part II §2.1–2.2 and Part XII of the white paper. This appendix contains extensions that are mathematically well-defined but not yet empirically calibrated.*

---

## Status

The models in this appendix are **extensions**, not replacements. The core equations in the white paper remain the canonical formal statement. The extensions here become actionable when empirical benchmark data is available to calibrate their additional parameters. Until then, they are stated precisely so they can be tested, and discarded if they do not improve prediction.

---

## 1. Residual Risk Model (R_n)

### The Gap

The coverage model F_n answers: *how much of the important failure surface has been meaningfully attacked and survived?*

It does not answer: *how much risk is plausibly left after a clean run?*

These are different quantities. A coverage score of F_n = 0.95 means 95% of the failure surface was tested. But the residual risk depends on how likely flaws were to exist in the first place. Reviewing mature, well-tested code (low prior flaw rate) with 95% coverage leaves much less residual risk than reviewing suspect, hastily written code (high prior flaw rate) with the same coverage.

### Definitions

- **π_k** — prior flaw rate for class k. The probability, before any testing, that a flaw of class k exists. Domain-dependent. Must be estimated from experience, historical data, or conservatively set high.
- **m_k** — miss probability for class k after n passes:

> m_k = Π_{i=1}^{n} (1 − d_i · p_ik)

This is the probability that *all* passes missed a flaw of class k, given that the flaw exists.

### Formula

By Bayes' theorem, the posterior probability that a flaw of class k remains after n passes that found nothing:

> P(flaw_k | no detection) = (π_k · m_k) / ((1 − π_k) + π_k · m_k)

Weighted residual risk across all flaw classes:

> **R_n = Σ_k w_k · (π_k · m_k) / ((1 − π_k) + π_k · m_k)**

### Interpretation

- When π_k is low (well-tested domain, mature code), R_n is small even with moderate coverage.
- When π_k is high (suspect code, novel domain), R_n remains substantial even with high coverage.
- When m_k → 0 (perfect detection), R_n → 0 regardless of prior. As expected.
- When m_k → 1 (no detection capability), R_n → Σ_k w_k · π_k. The prior is unchanged. Testing added nothing.

### Relationship to F_n

F_n and R_n are complementary views of the same underlying process:

| Quantity | Measures | Useful for |
|---|---|---|
| F_n | How hard did we try to break it? | Process quality assessment |
| R_n | How much risk plausibly remains? | Decision-making under uncertainty |
| A | How much external reality contact? | Epistemic anchoring |

The reporting format extends from (F_n, A) to **(F_n, R_n, A)**.

### Calibration

π_k values must come from domain experience, not from the model's self-assessment. Candidate sources:
- Historical defect rates for the domain and task type
- Conservative defaults (π_k = 0.5 when unknown)
- Expert estimation at the constraint-bounding stage (Part III of the white paper)

R_n is only as good as the prior. When π_k is unknown, report R_n with explicit prior assumptions stated.

### Reduction Property

Under simplifying assumptions (K = 1, d_i = 1, all p_ik = p, π = 0.5), R_n reduces to:

> R_1 = (1 − p)^n / (1 + (1 − p)^n)

which is the standard Bayesian posterior for a symmetric prior under repeated Bernoulli non-detection. The residual risk model is the Bayesian generalisation of the coverage model in the same way that F_n is the multi-class generalisation of C(n).

---

## 2. Class-Specific Diversity Discount (d_ik)

### The Gap

The current structured model uses one diversity discount per pass: d_i. This means pass i is treated as equally independent (or dependent) for all flaw classes. In practice, a reviewer may be highly independent for logic errors (different reasoning approach) and weakly independent for interface errors (same API documentation, same blind spot).

### Extension

Replace scalar d_i with matrix d_ik:

> q_ik = d_ik · p_ik

The structured model becomes:

> **F_n = Σ_k w_k · [1 − Π_i (1 − d_ik · p_ik)]**

And for the distributed compute coverage model (Part XII):

> D_n = Σ_k w_k · [1 − Π_i (1 − p_ik · (1 − o_ik))]

where o_ik is the expected overlap of reviewer i with prior reviewers for flaw class k, replacing the scalar ρ.

### Reduction Property

When all d_ik for a given i are equal (d_ik = d_i for all k), the model reduces exactly to the current structured model. The current model is a special case.

### Calibration

d_ik values require per-class, per-reviewer empirical measurement. This is more data-intensive than scalar d_i. Practical approach:
- Use scalar d_i as default
- Override to d_ik only for flaw classes where there is evidence of class-specific correlation (e.g., two reviewers who share the same API documentation have high overlap for interface errors but not for logic errors)

---

## 3. Parameter Uncertainty

### The Gap

The current framework treats p_ik, d_i (or d_ik), and ρ as point estimates. In practice, these are empirical estimates with uncertainty. Reporting a single F_n or R_n value invites false precision.

### Extension

Treat detection probabilities as distributions rather than point values:

> p_ik ~ Beta(a_ik, b_ik)

Then compute F_n and R_n as distributions rather than scalars, and report:

- Point estimate (median or mean)
- Credible interval (e.g., 5th–95th percentile)

> Report: F_n^{50%}, F_n^{5%–95%}

### Why This Matters

The framework's own falsifiability stance says: if the richer model does not predict outcomes better than a simpler heuristic, it should be dropped. Uncertainty-aware calibration makes that comparison cleaner — you can distinguish "model A is better" from "model A is within the noise of model B."

### Practical Implementation

For the current stage (pre-empirical), point estimates with stated assumptions are sufficient. Parameter uncertainty becomes actionable when:
- Multiple benchmark runs provide distributional data
- Model comparison (simple vs structured vs distributed) requires statistical significance testing

---

## 4. Severity-Detectability Separation

### The Gap

The current w_k term combines two conceptually distinct quantities:
1. How important is flaw class k? (consequence/severity)
2. How does flaw class k contribute to overall coverage? (weighting)

For most engineering work, this conflation is harmless — you weight by importance. But in safety-critical domains, separating them matters: a rare but catastrophic flaw class might have low detection coverage but dominate total risk.

### Extension

Define:
- **F_{n,k}** = per-class coverage: 1 − Π_i (1 − d_ik · p_ik)
- **R_{n,k}** = per-class residual risk: (π_k · m_k) / ((1 − π_k) + π_k · m_k)
- **s_k** = expected harm/severity for class k

Expected residual loss:

> **L_n = Σ_k s_k · R_{n,k}**

### Interpretation

L_n is a risk-weighted residual score. It is dominated by flaw classes that are both hard to detect (high m_k) and high-severity (high s_k). This is the quantity that matters most for safety-critical decisions.

### Relationship to Existing Model

When s_k = w_k (severity IS the weighting), L_n reduces to R_n. The current model is a special case where severity and detection-weighting are conflated. For most non-safety-critical work, that conflation is appropriate.

---

## 5. Model Selection Criteria

The extensions above add parameters. More parameters always improve fit on training data; the question is whether they improve prediction on held-out data.

### Decision Rule

For each extension, test on benchmark data:

1. Fit both the simpler and richer model to a training split
2. Predict detection outcomes on a held-out split
3. Compare prediction accuracy (e.g., log-likelihood, calibration error)
4. Keep the richer model only if it materially outperforms the simpler one

This matches the white paper's stance: "if a better model is proposed that predicts P-Pass outcomes more accurately, this one should be replaced."

### Current Status

| Extension | Mathematical status | Empirical status | Action |
|---|---|---|---|
| R_n (residual risk) | Well-defined, reduction verified | No calibration data | State formula, calibrate when data available |
| d_ik (class-specific diversity) | Well-defined, reduces to d_i | No per-class correlation data | Use scalar d_i as default, note extension |
| Parameter uncertainty | Standard Bayesian treatment | Requires multiple benchmark runs | Point estimates for now, intervals later |
| Severity separation | Well-defined, reduces to w_k model | Requires domain-specific severity data | Conflate for non-safety work, separate for safety-critical |

---

## Notation Summary

| Symbol | Meaning | Introduced in |
|---|---|---|
| C(n) | Simple corroboration (baseline model) | White paper §2.1 |
| F_n | Structured falsification coverage | White paper §2.2 |
| D(n) | Distributed compute coverage | White paper Part XII |
| R_n | Residual risk after clean run | This appendix §1 |
| L_n | Expected residual loss (severity-weighted) | This appendix §4 |
| p_ik | Detection probability, pass i, flaw class k | White paper §2.2 |
| d_i | Diversity discount, pass i (scalar) | White paper §2.2 |
| d_ik | Diversity discount, pass i, flaw class k | This appendix §2 |
| o_ik | Overlap of reviewer i with priors, flaw class k | This appendix §2 |
| w_k | Consequence weight, flaw class k | White paper §2.2 |
| s_k | Expected harm/severity, flaw class k | This appendix §4 |
| π_k | Prior flaw rate, flaw class k | This appendix §1 |
| m_k | Miss probability, flaw class k | This appendix §1 |
| A | Anchor state (A0–A3) | White paper §2.2 |
| ρ | Inter-architecture correlation | White paper Part XII |

---

## Attribution

The residual risk model (§1), class-specific diversity discount (§2), parameter uncertainty treatment (§3), and severity-detectability separation (§4) were developed through independent third-party mathematical assessment (OpenAI GPT, March 2026) applied to the CDSFL white paper and extended rationale. The assessment validated the existing core models as "mathematically sound within their stated assumptions" and "substantially improved" relative to earlier formulations, while identifying these extensions as the "cleanest upgrade path" for the next empirical phase.

---

*This appendix is a working mathematical supplement. Its extensions are precisely stated so they can be tested. Any extension that fails to improve predictive accuracy over the simpler model it extends should be discarded. The methodology does not depend on any specific equation — it depends on the principle that corroboration is earned through survived falsification.*
