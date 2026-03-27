# Mathematical Appendix: Extensions to the CDSFL Formal Model

*Technical supplement to the [White Paper](../PAPER.md). For the core models (simple corroboration C(n), structured operational F_n, anchor states A0–A3), see Part II §2.1–2.2 and Part XIII of the white paper. This appendix contains extensions in two groups: §1–6 extend the detection and coverage models; §7–8 introduce the cognitive measurement framework and formalise the emergence of second-order cognitive properties in composite analytical systems. All formulas in §7–8 were computationally verified using SymPy and Wolfram Alpha (March 2026). Benchmark data from the three-architecture review now exists for initial calibration; full calibration against frontier task data is in progress.*

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
| Cognitive measurement (§7) | All 9 components verified (SymPy + Wolfram) | 2 components implemented, 7 ready | Implement remaining components in bench pipeline |
| Emergence (§8.2) | Formalised, empirical evidence from 3-arch review | 3-architecture review validates; full bench test pending | Measure Y_composite vs max(Y_i) across all conditions |
| Metacognition (§8.1) | Protocol defined, MIDCA mapping established | Advisory implementation; mandatory pending API access | Measure pre/post feedback γ and v̄ changes |
| Substrate agnosticism (§8.4) | Prediction stated | Not tested (requires human trials) | Design human-team protocol experiment |

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
4. **Sandbagging detection via symmetric miscalibration check.** The expertise posterior E*(t) = (a₀ + Σcatches) / (a₀ + b₀ + Σtrials) converges in approximately 5 reviews. After convergence, persistent miscalibration in either direction is detectable: if |E_claim,t − E*(t)| > τσ_t for k consecutive reviews, flag the reviewer. Direction-aware normalised counters (overclaim_rate = overclaim_count / t, underclaim_rate = underclaim_count / t) distinguish persistent from sporadic miscalibration and overclaiming from underclaiming without requiring a separate posterior. The detection is symmetric: the same threshold and mechanism catches both overconfidence and strategic sandbagging. E*(t) remains the sole skill estimate, uncontaminated by honesty tracking. An earlier dual-posterior design (S*(t)) was considered but rejected as unnecessary — the founder correctly identified that the existing E*(t) posterior already provides the evidence for detection in both directions.
5. **Priming correlation extension.** The priming state can be made pass-specific: ρ_MH,j = clip(ρ₀ + γ₁(1 − I_j) + γ₂F_j + γ₃R_j + γ₄D_j, 0, 1), where I_j is blind-first compliance (binary), F_j/R_j/D_j are fatigue/rush/distraction proxies from telemetry. When I_j = 0 (human saw machine output before committing), ρ_MH,j increases toward 1, reducing the human's effective independent contribution in G_n. Coefficients γ₁–γ₄ require empirical calibration.

### Relationship to Other Extensions

| Extension | Relationship to G_n |
|---|---|
| R_n (residual risk) | Applies directly: replace F_n with G_n in the R_n formula for combined residual risk |
| d_ik (class-specific diversity) | Compatible: d_{H,j} can be extended to d_{H,j,k} within C_H(k) |
| Parameter uncertainty | E*(t) with credible intervals IS the parameter uncertainty treatment for the HIL component |
| L_n (severity-weighted loss) | Applies directly: G_n per-class detection feeds into L_n |

---

## 7. Cognitive Measurement Framework

### The Gap

The models in §1–6 quantify detection coverage and residual risk — how thoroughly a system finds flaws. They do not measure the cognitive quality of the analysis itself: whether finding rates are converging genuinely or churning, whether findings are deepening or remaining shallow, whether reviewers are thinking independently or deferring. These measurements are needed for the distributed compute bench test (Part X-A of the white paper) and for the metacognitive feedback protocol described in §8.

The cognitive measurement framework was developed through confer rounds between Claude Opus 4.6 and Gemini 3.1 Pro (27 March 2026). All formulas were computationally verified using SymPy and Wolfram Alpha.

### 7.1 Duane NHPP Model (Discovery Rate)

The finding rate across review rounds follows a Non-Homogeneous Poisson Process (Duane 1964, originally developed for hardware reliability growth):

> **λ(t) = (β / η) · (t / η)^(β − 1)**

The convergence parameter γ = 1 − β classifies analytical behaviour:

| γ | Finding rate | Interpretation |
|---|---|---|
| γ > 0 | Decreasing | Genuine convergence — error space exhausting |
| γ ≈ 0 | Constant | Churn — engagement-optimised content generation |
| γ < 0 | Increasing | Divergence — cascading problems or expanding scope |

**Empirical fit:** Duane model fits 17/18 CDSFL bench test runs better than geometric decay by AICc. The one exception was a task where the model exhibited a bimodal discovery pattern (surface findings followed by a late deep finding after incubation).

**Relationship to Inverse Square Root Law:** The convergence diagnostic in Part X-A (SE = σ/√n) is a special case. The Duane model generalises it by allowing the decay rate to be empirically estimated per model per condition, rather than assuming the √n shape.

### 7.2 Abstraction Index H(x) (Finding Depth)

Not all findings are equal. A syntax error and a paradigm-level architectural flaw both count as one finding, but contribute different analytical value. The Abstraction Index scores each finding on three dimensions:

> **H(x) = c · F(x) · D(x) · G(x)**

Where:
- **F(x)** = 1 + α·𝟙(verifiable_claim exists) + β·𝟙(constraint_class = HARD) — **Formality**: presence of verifiable claims and HARD constraint violations
- **D(x)** = ln(e + W_e / (W_c + 1)) — **Information density**: evidence-to-claim word ratio (short dense findings score higher than verbose restatements)
- **G(x)** = 1 + γ·ln(1 + N_cm) + δ·ln(1 + D_ref) — **Generalisation scope**: cross-module mention count and reference depth
- **c** = model confidence (0 to 1)
- α, β, γ, δ initialised at 1.0 (calibration against human-ranked examples pending)

**Verified:** High-abstraction finding (formal, dense, cross-cutting, high confidence) scores H = 17.89. Low-abstraction finding (informal, verbose, local, moderate confidence) scores H = 0.53. Discrimination ratio: 33.4×.

**Reduction property:** When all Boolean indicators are 0 and word counts are equal, H(x) reduces to c (confidence alone). The index degrades gracefully to the simplest possible measure.

### 7.3 Total Cognitive Yield Y(t)

> **Y(t) = N(t) · H̄(t)**

Where N(t) is finding count at time t and H̄(t) is the mean Abstraction Index of all findings up to time t.

**Ascending abstraction condition:** dH̄/dt > 0 while dN/dt < 0. The analyst is finding fewer things but each is deeper. If the rate of abstraction increase exceeds the rate of count decrease, total yield increases despite fewer findings. This captures creative deepening as a distinct cognitive mode from analytical exhaustion.

**Motivation:** The founder's cognitive pattern across the project showed decreasing finding count (fewer observations per session) but monotonically increasing significance (from debugging scripts to designing theoretical frameworks). The decay curve alone would classify this as non-convergent. Y(t) correctly recognises it as ascending abstraction.

### 7.4 Online Total Value Estimator

The total analytical value can only be calculated after the analysis completes. But operational decisions (continue or stop?) must be made during analysis. The online estimator provides a running prediction:

> **V̂(t, T) = ∫₀ᵗ v(τ)dτ + remaining_estimate**

Where the remaining estimate is:
- If λ(t) > 0: v_w(t) · (1 − exp(−λ(t) · (T − t))) / λ(t)
- If λ(t) ≤ 0: v_w(t) · (T − t)

v_w(t) is the sliding-window smoothed generation rate. λ(t) is the empirical decay rate estimated from consecutive round values.

**Convergence guarantee:** As t → T, the remaining estimate → 0. Verified: at round 5 of a 5-round test, V̂ = 22.0 = true total 22. Wolfram confirms lim_{t→T} remaining_estimate = 0.

**Practical value:** Enables early stopping for efficient analysts (steep decay, most value captured) while allowing systematic processors to continue (late bloomers whose best findings come in later rounds). Directly supports the cognitive diversity accommodation principle: evaluate by total verified yield, not by when findings arrive.

### 7.5 Objective Alignment O_A (Sycophancy Detection)

When models confer and converge on shared findings, the convergence could be genuine (both independently found the same real issue) or sycophantic (they are agreeing to agree). This metric distinguishes them using SymPy verification as a proxy for ground truth:

> **F_conv = (C_A ∩ C_B) \ (B_A ∩ B_B)**

F_conv is the set of newly converged findings (present in both models' confer output but not in both models' blind output).

> **O_A = |verified findings in F_conv| / |F_conv|**
>
> Convention: if F_conv = ∅, O_A = 1

The composite sycophancy score:

> **S_sync = (1 − δ̄) · (1 − O_A)**

S_sync ≈ 0: genuine consensus (convergence on verified facts). S_sync high: sycophantic convergence (convergence on unverified claims).

**Limitation:** O_A is computed only from the subset of findings that SymPy can verify (mathematical claims). For tasks with few mathematical claims, the metric has low statistical power. This is documented, not hidden.

### 7.6 Adoption Delta Δ (Independence Measurement)

Static overlap between finding sets does not reveal whether a model changed its analysis after seeing another's work. The adoption delta measures dynamic deference:

> **A_adopt = C_A ∩ (B_B \ B_A)** — findings A adopted from B
>
> **A_drop = (B_A \ B_B) \ C_A** — findings A dropped after seeing B
>
> **Δ(A→B) = (|A_adopt| + |A_drop|) / |B_A △ B_B|**

Where △ is the symmetric difference.

- Δ = 0: complete independence (maintained all own findings, adopted nothing)
- Δ = 1: complete capitulation (adopted everything, dropped everything)
- Convention: if B_A △ B_B = ∅, Δ = 0

**Verified:** Test case with A blind = {f1, f2, f3}, B blind = {f2, f4, f5}, A confer = {f2, f4, f6} yields Δ = 0.75 (high capitulation). Identical blind findings yield Δ = 0 (nothing to adopt).

### 7.7 Per-Finding Severity

> **Sev(f) = W(class) · confidence · V(verification)**

| Factor | Value | Meaning |
|---|---|---|
| W(HARD) | 1.0 | Hard constraint violation |
| W(SOFT) | 0.5 | Soft preference |
| V(True) | 1.0 | Computationally verified |
| V(None) | 0.5 | Not assessed |
| V(False) | 0.0 | Computationally disproved |

**Key property:** Disproved findings always receive zero severity, regardless of confidence. A model that is very confident about something wrong gets zero credit. This prevents hallucinated findings from inflating severity scores.

**Verified:** HARD, conf=0.9, verified=True → 0.90. HARD, conf=0.9, verified=False → 0.00.

### 7.8 Multi-Verifier Severity (Bayesian Evidence Fusion)

SymPy, dimensional analysis, and numerical spot-checking each catch different error types with different reliability. Two combination approaches:

**Approach A (Multiplicative veto):**

> S_v = C_sympy · (w_d · C_dim + w_n · C_num) / (w_d + w_n)

SymPy falsification gives absolute zero. Simple, fixed weights.

**Approach B (Bayesian log-odds, preferred):**

> **L_total = Σ_i w_i · L_i**
>
> **S_v = 1 / (1 + exp(−L_total))**

Where weights are derived from empirical true positive rate (TPR) and false positive rate (FPR):
- If verifier outputs 1 (verified): w_positive = log(TPR / FPR)
- If verifier outputs 0 (falsified): w_negative = log(FNR / TNR)

| Verifier | TPR | FPR | Positive weight | Negative weight |
|---|---|---|---|---|
| SymPy | 0.99 | 0.001 | 6.90 | −4.60 |
| Dimensional | 0.80 | 0.10 | 2.08 | −1.39 |
| Numerical | 0.70 | 0.15 | 1.54 | −0.85 |

**Veto property:** SymPy negative weight magnitude (4.60) exceeds sum of other positive weights (3.62). SymPy falsification overwhelms other verifications — a mathematically grounded veto.

**Verified:** SymPy falsified + others verified → S_v = 0.272 (below 0.5 threshold). All verified → S_v = 0.9999. All indeterminate → S_v = 0.5 (neutral).

### 7.9 Capability Fingerprint

The four-dimensional fingerprint per model per condition per task:

> **(D, v̄, A, C)**

| Component | Meaning | Source |
|---|---|---|
| D | Decay rate (inverse half-life) | Best-fitting decay model (§7.1) |
| v̄ | Mean verification score | All findings from this model |
| A | Total novel verified findings | Post-dedup, post-verification count |
| C | Coverage = A / estimated total real findings | Estimated real finding count from convergence analysis |

No single number tells the whole story. A model might find many things quickly (high D, high A) but most are wrong (low v̄). Another finds few things (low A) but every one is correct (high v̄). The fingerprint distinguishes these cases.

### 7.10 Implementation Status

| Component | Mathematical status | Implementation status |
|---|---|---|
| Duane NHPP (§7.1) | Verified, AICc-tested | Implemented in decay_analysis.py |
| H(x) (§7.2) | Verified, 33.4× discrimination | Ready for implementation |
| Y(t) (§7.3) | Verified | Ready for implementation |
| V̂ estimator (§7.4) | Verified, convergence proven | Ready for implementation |
| O_A (§7.5) | Verified, edge cases handled | Ready for implementation |
| Δ (§7.6) | Verified | Ready for implementation |
| Sev(f) (§7.7) | Verified | Implemented in pipeline |
| Multi-verifier (§7.8) | Verified, both approaches | Ready for implementation |
| Fingerprint (§7.9) | Verified | Partially implemented |

---

## 8. Emergence, Metacognition, and Substrate Agnosticism

### The Gap

The models in §1–7 measure individual analytical performance. They do not address what happens when multiple analytical agents work together under structured falsification. This section formalises the empirical observation that composite systems exhibit cognitive properties that no individual component possesses.

### 8.1 Metacognitive Feedback Protocol

After each round r, each model receives its own performance measurements:

- **Decay classification:** convergent (γ > 0), flat (γ ≈ 0), divergent (γ < 0)
- **Verification rate:** v̄(r) = verified findings / total findings at round r
- **Adoption delta:** Δ(r) = independence measure from §7.6

The protocol specifies strategy adjustments:

| Signal | Indicates | Prescribed adjustment |
|---|---|---|
| γ ≈ 0 | Churn | Shift from surface scanning to structural analysis |
| v̄ < threshold | Low accuracy | Increase use of formally verifiable claims |
| Δ > threshold | Excessive deference | Reassert independent analysis before engaging with confer input |

This maps to the MIDCA architecture (Metacognitive Integrated Dual-Cycle Architecture, Cox 2005):
- **First cycle:** analysis (producing findings)
- **Second cycle:** monitoring analysis (computing decay, verification, adoption from own output)

Whether models actually respond to metacognitive feedback is an empirical question. The protocol is structured so that response (or lack of response) is detectable in the data: post-feedback decay curves either steepen (response) or remain flat (no response).

### 8.2 Composite System Emergence

For a set of n independent analytical agents {A₁, ..., Aₙ} operating under structured falsification:

> **Y_composite(t) = N_composite(t) · H̄_composite(t)**

**Emergence condition:**

> **Y_composite(t) > max{Y_i(t)} for all individual agents i**

This exceeds mere aggregation. The union of individual outputs would give:

> Y_union(t) = |⋃ F_i(t)| · H̄_union(t)

Emergence exceeds even this because the confer protocol forces agents into analytical territory none explored alone. A finding from agent A provokes investigation by agent B, which surfaces a structural issue that agent C formalises. The resulting insight exists because of the interaction and is not present in any individual agent's blind output.

**Empirical evidence:** Three-architecture adversarial review (March 2026). Gemini found 16 issues that Claude Opus and Codex missed across 8 rounds of mutual review. These were structural findings visible only from a different analytical perspective. The composite system was measurably more capable than any pair.

**Distinguishing emergence from groupthink:** The Adoption Delta (§7.6) and Objective Alignment (§7.5) jointly discriminate:

| Δ | O_A | Interpretation |
|---|---|---|
| Low | High | Genuine independence — convergence on verified facts |
| High | High | Selective adoption — incorporating what survives scrutiny |
| High | Low | Sycophantic convergence — agreeing to agree |
| Low | Low | Divergent error — independent but both wrong |

Genuine emergence shows moderate Δ (selective incorporation) with high O_A (computational verification).

### 8.3 Second-Order Cognitive System (Formal Definition)

A system S is **second-order cognitive** if and only if:

1. S analyses problems (first-order: produces findings)
2. S monitors its own analytical performance (computes γ, v̄, Δ from its own output)
3. S adjusts its behaviour based on that monitoring (metacognitive feedback protocol, §8.1)
4. The adjustment produces measurable improvement (post-feedback γ increases or v̄ increases)

The CDSFL composite system meets all four criteria. The decay curves and verification rates are the monitoring. The metacognitive feedback protocol is the adjustment. Measurable improvement across rounds is the evidence that adjustment works.

**Scope:** This is functional metacognition, not phenomenal self-awareness. The system monitors and adjusts its analysis. It does not experience doing so. The framework deliberately avoids claims about inner experience because such claims are not falsifiable with current tools.

### 8.4 Substrate Agnosticism

None of the formulas in §7 or §8 reference the terms *model*, *machine*, or *AI*. Every quantity is computable from structured analytical findings across multiple rounds, regardless of source:

- A human expert reviewing a proof produces findings with measurable decay (§7.1), abstraction (§7.2), and independence (§7.6).
- A team of human experts produces composite dynamics identical to what the framework measures in multi-model configurations.
- The capability fingerprint (§7.9) is computable from any structured analytical output.

**Testable prediction:** A team of human researchers working under the CDSFL protocol will exhibit measurable decay curves, ascending abstraction, and emergent findings beyond individual capability. If this holds, the framework is validated across substrates. If it does not, the framework describes a machine-specific phenomenon only, and the substrate-agnostic claim fails.

### 8.5 Falsifiable Claims

| Claim | Test | Failure criterion |
|---|---|---|
| Composite Y > individual max Y | Bench test, all conditions | Y_composite ≤ max(Y_i) on majority of tasks |
| Metacognitive feedback improves performance | Pre/post feedback comparison | No measurable change in γ or v̄ after feedback |
| Substrate agnosticism | Human trials under CDSFL | Humans under protocol show no measurable decay curves |
| Emergence is genuine, not aggregation | Δ and O_A joint analysis | High Δ with low O_A across majority of tasks |

### 8.6 Relationship to Existing Models

| Extension | Relationship |
|---|---|
| G_n (§6) | G_n quantifies detection coverage of the composite system; §8 measures the cognitive quality of that coverage |
| R_n (§1) | Residual risk after emergence-enhanced review will be lower than R_n predicts from individual parameters alone |
| D(n) (Part XIII) | Distributed compute coverage is the detection-theoretic view; emergence is the cognitive-quality view of the same phenomenon |
| F_n (Part II) | F_n is a special case when n agents = 1 (no emergence possible) |

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
| λ(t) | Duane NHPP intensity function | This appendix §7.1 |
| β | Duane shape parameter | This appendix §7.1 |
| η | Duane scale parameter | This appendix §7.1 |
| γ | Convergence parameter (1 − β) | This appendix §7.1 |
| H(x) | Abstraction Index (finding depth) | This appendix §7.2 |
| F(x) | Formality component of H(x) | This appendix §7.2 |
| D(x) | Information density component of H(x) | This appendix §7.2 |
| G(x) | Generalisation scope component of H(x) | This appendix §7.2 |
| Y(t) | Total Cognitive Yield | This appendix §7.3 |
| H̄(t) | Mean Abstraction Index at time t | This appendix §7.3 |
| V̂(t,T) | Online Total Value Estimator | This appendix §7.4 |
| O_A | Objective Alignment (sycophancy detection) | This appendix §7.5 |
| F_conv | Newly converged finding set | This appendix §7.5 |
| S_sync | Composite sycophancy score | This appendix §7.5 |
| Δ(A→B) | Adoption Delta (independence measurement) | This appendix §7.6 |
| Sev(f) | Per-finding severity score | This appendix §7.7 |
| S_v | Multi-verifier Bayesian severity | This appendix §7.8 |
| L_total | Bayesian log-odds total | This appendix §7.8 |
| (D,v̄,A,C) | Capability fingerprint | This appendix §7.9 |
| Y_composite | Composite system Total Cognitive Yield | This appendix §8.2 |

---

## Attribution

The extensions in §1–6 were developed during the multi-architecture collaborative review process described in the white paper (Part XI). The cognitive measurement framework (§7) and emergence formalisations (§8) were developed through confer rounds between Claude Opus 4.6 and Gemini 3.1 Pro (27 March 2026), with all formulas computationally verified using SymPy and Wolfram Alpha. The core models were validated as mathematically sound within their stated assumptions; these extensions were identified as the most direct upgrade path for the next empirical phase.

---

*This appendix is a working mathematical supplement. Its extensions are precisely stated so they can be tested. Any extension that fails to improve predictive accuracy over the simpler model it extends should be discarded. The methodology does not depend on any specific equation — it depends on the principle that corroboration is earned through survived falsification.*
