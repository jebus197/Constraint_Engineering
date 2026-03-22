# Mathematical Appendix: Extensions to the CDSFL Formal Model

*Technical supplement to the [White Paper](../PAPER.md). For the core models (simple corroboration C(n), structured operational F_n, anchor states A0–A3), see Part II §2.1–2.2 and Part XIII of the white paper. This appendix contains extensions that are mathematically well-defined. Benchmark data from the three-architecture review (March 2026) now exists for initial calibration; full calibration against frontier task data is in progress.*

---

## Status

The models in this appendix are **extensions**, not replacements. The core equations in the white paper remain the canonical formal statement. Benchmark data from the three-architecture adversarial review now provides a basis for initial calibration of these extensions. They are stated precisely so they can be tested, and discarded if they do not improve prediction.

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
| R_n (residual risk) | Well-defined, reduction verified | Three-architecture review data available for initial calibration | Calibrate against review convergence data |
| d_ik (class-specific diversity) | Well-defined, reduces to d_i | Cross-architecture defect data available (Claude/Codex/Gemini) | Estimate per-class correlations from review data |
| Parameter uncertainty | Standard Bayesian treatment | Initial data from completed review rounds | Point estimates first, intervals as data accumulates |
| Severity separation | Well-defined, reduces to w_k model | Requires domain-specific severity data | Conflate for non-safety work, separate for safety-critical |
| G_n (combined detection) | Well-defined, all reductions verified | Numerical illustration computed; empirical calibration pending | Integrate into benchmark when HIL review data is collected |
| κ (calibration metric) | Well-defined, asymmetric variant specified | Simulated convergence (~5 reviews); empirical confirmation pending | Deploy when repeated HIL reviews generate sufficient data |

---

## 6. Combined Machine-HIL Detection Model (G_n)

### The Gap

The structured model F_n quantifies cumulative detection across machine passes. The four-tier review structure (white paper Part III) specifies that the HIL at Tier 2 runs their own independent falsification — not a passive review. But F_n treats the HIL as just another row in the diversity discount table, indistinguishable from any other pass type. This undersells the active HIL and fails to capture three variables that materially affect combined detection: the cross-correlation between human and machine reasoning, the formality of the human's methodology, and the extensibility of detection probability through domain-specific factors.

### Combined Detection Formula

> **G_n = Σ_{k=1}^{K} w_k · [1 − (1 − C_M(k)) · (1 − C_H(k) · (1 − ρ_MH))]**

Where:
- C_M(k) = 1 − Π_{i=1}^{n_M} (1 − d_{M,i} · p_{M,i,k}) — machine cumulative detection (= F_n)
- C_H(k) = 1 − Π_{j=1}^{n_H} (1 − d_{H,j} · p_{H,j,k}) — HIL cumulative detection
- ρ_MH ∈ [0,1] — cognitive priming correlation

The formula models two independent detection streams (machine and human) whose combined coverage is degraded by the priming correlation ρ_MH. When the human has seen the machine's output before forming their own analysis, ρ_MH > 0 and the human's effective contribution is reduced. At ρ_MH = 1, the human adds nothing — their reasoning is fully absorbed into the machine's framing.

### HIL Detection Probability

The HIL's per-pass detection probability is parameterised as:

> **p_{H,j,k} = f_k(E, M) · Π_s (1 + λ_s · V_s)**

> **f_k(E, M) = E · (α + (1−α) · M)**

Where:
- E ∈ [0,1] — domain expertise level
- M ∈ [0,1] — methodology formality (0 = informal judgment, 1 = fully formal)
- α ∈ (0,1) — floor coefficient (expertise alone, without formal method)
- λ_s — sensitivity coefficient for domain variable s
- V_s ∈ [-1,1] — domain-specific variable s (pluggable by operator)

The base function f_k(E, M) captures two empirical observations: expertise is necessary but not sufficient (the floor is α·E without formal method), and methodology is a multiplier on expertise, not an independent contributor (M without E produces nothing). The product term Π_s(1 + λ_s · V_s) allows domain operators to extend detection probability with context-specific factors. When V_s = 0 for all s, the formula reduces to the base case.

### Reduction Properties

| Condition | G_n reduces to | Interpretation |
|---|---|---|
| n_H = 0 | F_n | No human passes — machine-only structured model |
| ρ_MH = 0 | 1 − (1−C_M)(1−C_H) | Full independence — multiplicative gain |
| ρ_MH = 1 | F_n | Fully primed — human adds nothing |
| K=1, d=1, uniform p | C(n) | Simple corroboration model |
| M = 0 | p_H = α·E | Expertise floor — reduced detection |
| All V_s = 0 | p_H = f(E,M) | Base case — no domain modifiers |

Every simpler model in the white paper and this appendix is a special case of G_n.

### Numerical Illustration

Representative parameters: 3 machine passes (p_M = 0.3, d_M = 0.7), 2 human passes (E = 0.85, M = 0.9, α = 0.4, d_H = 0.9):

| Scenario | Detection |
|---|---|
| Machine only (C_M) | 0.507 |
| Human only (C_H) | 0.698 |
| Combined, ρ = 0 (fully independent) | 0.961 |
| Combined, ρ = 0.3 (mild priming) | 0.851 |
| Combined, ρ = 0.6 (significant priming) | 0.748 |
| Combined, ρ = 1.0 (fully correlated) | 0.507 |

The methodology formality gap at constant expertise E = 0.85:

| M (formality) | p_H | Ratio vs informal |
|---|---|---|
| 0.0 (informal) | 0.34 | 1.0× |
| 0.5 (semi-formal) | 0.60 | 1.75× |
| 1.0 (fully formal) | 0.85 | 2.5× |

### Self-Correcting Parameters: Bayesian Calibration

E is initially self-declared. Over repeated reviews, the system accumulates empirical data on actual detection performance. The posterior expertise estimate replaces the self-declared value:

> **E*(t) = (a₀ + Σ catches) / (a₀ + b₀ + Σ trials)**

This is a standard Beta-Binomial update with weak prior Beta(a₀, b₀). With a₀ = b₀ = 2 (weak, open-minded prior):

| Reviews completed | Posterior E* (true rate 0.55, claimed 0.80) | 95% CI | Claimed E outside CI? |
|---|---|---|---|
| 1 | 0.357 | [0.14, 0.61] | No (wide CI) |
| 3 | 0.588 | [0.42, 0.75] | Yes |
| 5 | 0.593 | [0.46, 0.72] | Yes |
| 10 | 0.625 | [0.53, 0.72] | Yes |
| 20 | 0.627 | [0.56, 0.69] | Yes |

By approximately five reviews, an overclaimed E is statistically falsifiable.

### HIL Calibration Metric (κ)

The divergence between claimed and observed performance is the calibration signal:

> **κ = 1 − |E_claimed − E*(t)|**

For asymmetric calibration (penalising overconfidence more than underconfidence):

> **κ_asym = 1 − β · max(0, E_claimed − E*(t)) − max(0, E*(t) − E_claimed)**

Where β > 1 penalises overconfidence. With β = 1.5:

| Scenario | E_claimed | E*(t) | κ (symmetric) | κ (asymmetric, β=1.5) |
|---|---|---|---|---|
| Well-calibrated expert | 0.75 | 0.72 | 0.97 | 0.955 |
| Overconfident (dangerous) | 0.85 | 0.40 | 0.55 | 0.325 |
| Underconfident (cautious) | 0.40 | 0.70 | 0.70 | 0.70 |
| Honest novice | 0.30 | 0.25 | 0.95 | 0.925 |
| Bluffer | 0.90 | 0.15 | 0.25 | −0.125 |

The bluffer scores negative under asymmetric calibration. The honest novice scores almost as well as the well-calibrated expert. The metric rewards self-knowledge, not raw ability.

### Feedback into G_n

The self-correcting parameter transforms G_n into G_n(t):

> Replace E_claimed with E*(t) in the p_H calculation

The system's predicted combined detection adjusts automatically. An overclaiming expert (E_claimed = 0.80, E*(t) = 0.627) inflates predicted G_n by approximately 5.7 percentage points. That gap is the cost of taking the expert's word for it.

### Future Research Directions

1. **Posterior convergence rate:** Does the Bayesian posterior on E converge at the rate the Beta-Binomial model predicts? Simulation suggests approximately five reviews; empirical confirmation is needed across different domains and task complexities.
2. **Asymmetric calibration outcomes:** Does penalising overconfidence more heavily than underconfidence (β > 1) produce better system-level detection than symmetric calibration (β = 1)? Testable by comparing aggregate detection rates under both regimes.
3. **Calibration score publication effects:** Does publishing the calibration score change reviewer behaviour? Specifically: does it produce honest self-assessment (the intended outcome) or strategic sandbagging (claiming low E to appear well-calibrated when overperforming)? This is a behavioural question, not a mathematical one, but it affects whether the metric is deployable.
4. **Sandbagging detection via dual-posterior design.** The expertise posterior E*(t) = (a₀ + Σcatches) / (a₀ + b₀ + Σtrials) measures skill. A separate sandbag propensity posterior S*(t) = (u₀ + Σz_t) / (u₀ + v₀ + t) measures honesty, where z_t = 1 when E_claim,t < μ_{t-1} − τσ_{t-1} (the claim is suspiciously below the posterior mean). The calibration penalty κ_sb(t) = 1 − β₊·max(0, E_claim − E*) − β₋(t)·max(0, E* − E_claim) uses β₋(t) = 1 + λ·S*(t) to amplify the underclaiming penalty for persistent sandbaggers. Properties: (a) reduces to symmetric penalty when S* = 0 (no sandbagging history), (b) penalty is monotonically increasing with sandbagging count, (c) E*(t) remains uncontaminated as a skill estimate. Verified via SymPy (2026-03-22).
5. **Priming correlation extension.** The priming state can be made pass-specific: ρ_MH,j = clip(ρ₀ + γ₁(1 − I_j) + γ₂F_j + γ₃R_j + γ₄D_j, 0, 1), where I_j is blind-first compliance (binary), F_j/R_j/D_j are fatigue/rush/distraction proxies from telemetry. When I_j = 0 (human saw machine output before committing), ρ_MH,j increases toward 1, reducing the human's effective independent contribution in G_n. Coefficients γ₁–γ₄ require empirical calibration.

### Relationship to Other Extensions

| Extension | Relationship to G_n |
|---|---|
| R_n (residual risk) | Applies directly: replace F_n with G_n in the R_n formula for combined residual risk |
| d_ik (class-specific diversity) | Compatible: d_{H,j} can be extended to d_{H,j,k} within C_H(k) |
| Parameter uncertainty | E*(t) with credible intervals IS the parameter uncertainty treatment for the HIL component |
| L_n (severity-weighted loss) | Applies directly: G_n per-class detection feeds into L_n |

---

## Notation Summary

| Symbol | Meaning | Introduced in |
|---|---|---|
| C(n) | Simple corroboration (baseline model) | White paper §2.1 |
| F_n | Structured falsification coverage | White paper §2.2 |
| D(n) | Distributed compute coverage | White paper Part XIII |
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
| ρ | Inter-architecture correlation | White paper Part XIII |
| G_n | Combined machine-HIL detection | White paper §7.1, this appendix §6 |
| C_M(k) | Machine cumulative detection for class k | This appendix §6 |
| C_H(k) | HIL cumulative detection for class k | This appendix §6 |
| ρ_MH | Cross-correlation (cognitive priming) | White paper §7.1, this appendix §6 |
| E | HIL domain expertise level | White paper §7.1, this appendix §6 |
| M | HIL methodology formality | White paper §7.1, this appendix §6 |
| α | Expertise floor coefficient | This appendix §6 |
| λ_s | Domain variable sensitivity | White paper §7.1, this appendix §6 |
| V_s | Domain-specific variable (pluggable) | White paper §7.1, this appendix §6 |
| E*(t) | Bayesian posterior expertise estimate | White paper §7.1, this appendix §6 |
| κ | HIL calibration metric | This appendix §6 |

---

## Attribution

The extensions in this appendix were developed during the multi-architecture collaborative review process described in the white paper (Part XI). The core models were validated as mathematically sound within their stated assumptions; these extensions were identified as the most direct upgrade path for the next empirical phase.

---

*This appendix is a working mathematical supplement. Its extensions are precisely stated so they can be tested. Any extension that fails to improve predictive accuracy over the simpler model it extends should be discarded. The methodology does not depend on any specific equation — it depends on the principle that corroboration is earned through survived falsification.*
