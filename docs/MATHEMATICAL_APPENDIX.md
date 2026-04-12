# Mathematical Appendix: Extensions to the CDSFL Formal Model

*Technical supplement to the [White Paper](../PAPER.md). For the core models (simple corroboration C(n), structured operational F_n, anchor states A0–A3), see Part II §2.1–2.2 and Part XIII of the white paper. This appendix contains extensions in three groups: §0.1 establishes the corroboration branching foundation (independent vs correlated passes); §1–6 extend the detection and coverage models; §7–8 introduce the cognitive measurement framework and formalise the emergence of second-order cognitive properties in composite analytical systems. All formulas were computationally verified using SymPy and Wolfram Alpha (March 2026). An 8-round coherence audit (6 models, 39 SymPy checks, all passing) declared the model mathematically coherent and complete on 31 March 2026.*

---

## Status

The models in this appendix are **extensions**, not replacements. The core equations in the white paper remain the canonical formal statement. Benchmark data from the three-architecture adversarial review now provides a basis for initial calibration of these extensions. They are stated precisely so they can be tested, and discarded if they do not improve prediction. The full model was declared mathematically coherent after an 8-round audit (31 March 2026) involving 6 models with 39 independent algebra checks, all passing. The unified self-assessment equation (§1.1, April 2026) collapses the residual risk model into a recursive form and extends it with fix-phase mechanics (novelty η, fix efficacy σ, re-injection ν). This is the operational form used in the CDSFL directive and by the Exp 37+ runner. The white paper §2.3 documents the full lineage from C(n) to the three-phase operational form.

---

## 0.1 Corroboration Branching C(n)

The white paper's simple corroboration model C(n) = 1 − ∏q_i assumes strict independence between passes. When passes are correlated (e.g., models sharing training data, prompts, or analytical framing), this assumption produces domain violations in the joint probability. The corroboration model branches:

**Branch 1 (Independent):**

> **C(n) = 1 − ∏_{i=1}^{n} q_i**

Valid when passes are operationally independent (distinct architectures, independent prompts, no shared context).

**Branch 2 (Correlated — Normalised Ising/Boltzmann):**

> **C(n) = 1 − P(x_1 = 1, ..., x_n = 1)**

Where x_i ∈ {0, 1} indicates detection failure for pass i. The joint failure probability is:

> **P(x) = (1/Z) · [∏_{i=1}^{n} q_i^{x_i} · (1 − q_i)^{1 − x_i}] · exp(Σ_{1≤i<j≤n} ψ_ij · x_i · x_j)**

Where:
- q_i ∈ [0, 1]: baseline independent failure probability (Bernoulli parameters, not post-coupling marginals)
- ψ_ij ∈ ℝ: pairwise correlation coupling between passes i and j
- Z: partition function summing over all 2^n states, strictly guaranteeing P(x) ∈ [0, 1]

**Reduction property:** When ψ_ij = 0 for all pairs, the exponent equals 1, Z = 1, and the Ising model reduces exactly to the independent product ∏q_i (Branch 1). The independent model is a special case of the correlated model.

**Boundedness constraint:** The coupling constants must satisfy Σψ_ij ≤ −Σlog(1 − q_i) to ensure all state probabilities remain non-negative. (Verified by SymPy, March 2026.)

**Selection criterion:** Use Branch 1 when models are architecturally distinct and prompts are independent. Use Branch 2 when models share training lineage, are given each other's outputs (confer rounds), or systematic correlation is suspected. The structured F_n model in §2 functions as a computationally tractable approximation of this exact physical model.

---

## 1. Residual Risk Model (R_n)

### The Gap

The coverage model F_n answers: *how much of the important failure surface has been meaningfully attacked and survived?*

It does not answer: *how much risk is plausibly left after a clean run?*

These are different quantities. A coverage score of F_n = 0.95 means 95% of the failure surface was tested. But the residual risk depends on how likely flaws were to exist in the first place. Reviewing mature, well-tested code (low prior flaw rate) with 95% coverage leaves much less residual risk than reviewing suspect, hastily written code (high prior flaw rate) with the same coverage.

### Definitions

- **π_risk,k** — prior flaw rate for class k. The probability, before any testing, that a flaw of class k exists. Domain-dependent. Must be estimated from experience, historical data, or conservatively set high.
- **m_k** — miss probability for class k after n passes:

> m_k = Π_{i=1}^{n} (1 − d_i · p_ik)

This is the probability that *all* passes missed a flaw of class k, given that the flaw exists.

### Formula

By Bayes' theorem, the posterior probability that a flaw of class k remains after n passes that found nothing:

> P(flaw_k | no detection) = (π_risk,k · m_k) / ((1 − π_risk,k) + π_risk,k · m_k)

Weighted residual risk across all flaw classes:

> **R_n = Σ_k w_k · (π_risk,k · m_k) / ((1 − π_risk,k) + π_risk,k · m_k)**

### Interpretation

- When π_risk,k is low (well-tested domain, mature code), R_n is small even with moderate coverage.
- When π_risk,k is high (suspect code, novel domain), R_n remains substantial even with high coverage.
- When m_k → 0 (perfect detection), R_n → 0 regardless of prior. As expected.
- When m_k → 1 (no detection capability), R_n → Σ_k w_k · π_risk,k. The prior is unchanged. Testing added nothing.

**Domain note:** R_n is defined for π_risk,k ∈ [0, 1) or m_k ∈ (0, 1]. The boundary (π_risk,k = 1, m_k = 0) represents a logical contradiction (certain flaw + perfect detection + no finding) and is excluded.

### Relationship to F_n

F_n and R_n are complementary views of the same underlying process:

| Quantity | Measures | Useful for |
|---|---|---|
| F_n | How hard did we try to break it? | Process quality assessment |
| R_n | How much risk plausibly remains? | Decision-making under uncertainty |
| A | How much external reality contact? | Epistemic anchoring |

The reporting format extends from (F_n, A) to **(F_n, R_n, A)**.

### Calibration

π_risk,k values must come from domain experience, not from the model's self-assessment. Candidate sources:
- Historical defect rates for the domain and task type
- Conservative defaults (π_risk,k = 0.5 when unknown)
- Expert estimation at the constraint-bounding stage (Part III of the white paper)

R_n is only as good as the prior. When π_risk,k is unknown, report R_n with explicit prior assumptions stated.

**Termination-aware R_n:** When the falsification loop terminates by budget exhaustion rather than convergence (see §3 of the core directives), π_risk,k should be inflated to reflect the residual falsification debt. A conservative approach: π_risk,k(exhausted) = π_risk,k + (1 − π_risk,k) · Δ(k_max), treating the terminal Δ as evidence of remaining undiscovered flaws. This is a first-order approximation; refinement via Duane extrapolation (§7.1) is possible but adds complexity. (Added during 3-model confer, 27 March 2026.)

### Reduction Property

Under simplifying assumptions (K = 1, d_i = 1, all p_ik = p, π = 0.5), R_n reduces to:

> R_n = (1 − p)^n / (1 + (1 − p)^n)

which is the standard Bayesian posterior for a symmetric prior under repeated Bernoulli non-detection. The residual risk model is the Bayesian generalisation of the coverage model in the same way that F_n is the multi-class generalisation of C(n).

### Empirical Prior Anchor (Seeded Defect Injection)

The model uses abstract miss probabilities m_k but lacks an empirical ground-truth anchor for validating those estimates during runtime. Seeded defect injection provides this anchor.

Given N_k seeded defects of class k injected into the task context, the empirical detection sensitivity is:

> **Ŝ_{H,k} = n_found / N_k**

This directly updates the machine miss probability empirical bounds:

> **𝔼[m_k] ≈ 1 − Ŝ_{H,k}**

**Interpretation:**
- Ŝ_H = 1 (found all seeds): m_k ≈ 0 — strong detection capability for this class
- Ŝ_H = 0 (found no seeds): m_k ≈ 1 — no detection capability for this class

If Ŝ_H drops as rounds progress, the models are becoming "blind" (due to framing bias or context exhaustion), allowing the Manager to dynamically increase adversarial diversity or reset context. Ŝ_H feeds directly into the sycophancy trigger (§7.5) and eliminates floating assumptions in the Bayesian updating.

**Domain:** Ŝ_{H,k} ∈ [0, 1] and m_k ∈ [0, 1] by construction. No clipping required.

(Adopted during Round 8 construct evaluation, 31 March 2026. SymPy verified: S_H ∈ [0,1] → m_k ∈ [0,1].)

### Substrate Ceiling (Asymptotic Boundary)

The model implicitly assumes that with sufficient iterations and model diversity, residual risk converges to zero. This is not true when the ensemble lacks fundamental capability for a specific defect class.

For any defect class k, if the requisite analytical capability is absent across all models (∀i, m_{i,k} = 1), infinite iterative application yields a strictly positive residual risk limit:

> **lim_{n→∞} R_{n,k} = π_risk,k**

The methodology is an efficiency multiplier on the union of substrate capabilities, bounded globally by max_i(Ω_i) where Ω_i is the analytical capability set of model i. It is not an intelligence generator.

**Hard Exit:** The SymPy Deterministic Governor enforces a Hard Exit if ΔR_n = 0 over successive passes — indicating the system has hit the substrate ceiling and further iteration is futile.

**Relationship to §8.4:** §8.4 asserts substrate agnosticism (the framework applies to any analytical agent). The substrate ceiling establishes the complementary boundary: the framework cannot exceed the union of its components' capabilities, regardless of substrate type.

(Modified from informal Gemini constructs and adopted during Round 8, 31 March 2026. SymPy verified: R → π_risk,k when all m = 1.)

---

## 1.1 Unified Self-Assessment Equation

### Model Evolution

The mathematical model evolved through five stages. Each is a strict generalisation of the previous — the earlier model is a special case of the later one under simplifying assumptions.

| Stage | Equation | What it adds | Source |
|---|---|---|---|
| 1 | C(n) = 1 − (1−p)ⁿ | Core corroboration | White paper §2.1 |
| 2 | F_n = Σ_k w_k · [1 − Π_i (1 − d_i · p_ik)] | Multi-class, diversity | White paper §2.2 |
| 3 | R_n = Σ_k w_k · (π_k · m_k) / ((1−π_k) + π_k · m_k) | Bayesian posterior, prior | This appendix §1 |
| 4 | R_k(i) = R_k(i-1) · (1−q) / (1−q·R_k(i-1)), q = d·p | Recursive collapse, π vanishes | This section |
| 5 | Three-phase: R_det → R_base → R_k with q = η·d·p, σ, ν | Novelty, fix efficacy, re-injection | Operational directive §3 |

### From R_n to the Recursive Form (Stage 3 → 4)

The batch formula in §1 computes residual risk after n passes by accumulating the miss probability product m_k = Π_i(1 − d_i · p_ik) and applying Bayes' theorem once. The recursive form computes the same quantity one pass at a time.

Define q_ik = d_ik · p_ik as the effective detection probability of pass i for flaw class k. After pass i, the single-step Bayesian update is:

> **R_k(i) = R_k(i-1) · (1 − q_ik) / (1 − q_ik · R_k(i-1))**

with initial condition R_k(0) = π_k.

**Derivation.** The batch Bayesian posterior for class k is:

> R_k = π_k · m_k / ((1−π_k) + π_k · m_k)

Substituting m_k = Π_j(1 − q_jk) and unrolling the product one factor at a time produces the recursive form. The prior π_k enters once at R_k(0) and never appears in the update rule again — it is absorbed into the running estimate. (Verified by SymPy and Wolfram Alpha, 8 April 2026.)

**The π-vanishing property.** Once you have your current risk estimate R_k(i), the update depends on only two quantities: R_k(i) itself and the effective detection q of the next pass. No history beyond the current state is required. This makes the equation self-contained at every step — a model can pick it up at any point, assess current risk, and decide what to do next.

**Marginal gain.** The risk reduction from one additional pass is:

> ΔR_k = q · R_k · (1 − R_k) / (1 − q · R_k)

The (1 − R_k) factor encodes diminishing returns: the less risk remains, the less there is to gain. The stopping rule follows naturally — continue while Σ_k w_k · ΔR_k > θ, where θ is the consequence threshold.

**Reduction.** Under K=1, d=1, all q=p, π=0.5, the recursive form produces R_n = (1−p)^n / (1 + (1−p)^n), the standard Bayesian posterior for repeated Bernoulli non-detection. This is the simplified model in the white paper §2.1, re-derived from first principles.

### Three-Phase Extension (Stage 4 → 5)

The recursive form (Stage 4) models detection only. Two confer analyses (Gemini 3.1 Pro and Codex GPT-5.4, 8 April 2026) independently identified that detection-only risk is incomplete — the act of fixing introduces its own risk. The extension adds three parameters:

- **η (novelty):** Is this finding genuinely new? Restating a known issue gives η ≈ 0. New content gives η ≈ 1. Replaces the implicit assumption that all passes contribute novel information.
- **σ (fix efficacy):** Does the proposed fix actually resolve the detected flaw? σ = 1 means the fix works perfectly. σ = 0 means the fix fails entirely and risk reverts to the pre-detection level.
- **ν (re-injection rate):** Does the fix attempt introduce new flaws? Localised one-line changes have low ν. Changes to shared interfaces have higher ν.

The three phases per cycle are:

**Phase 1 — Detection.** Effective detection now includes novelty:

> q = η · d · p
>
> R_det = R_old · (1 − q) / (1 − q · R_old)

**Phase 2 — Resolution.** The fix may or may not resolve the target flaw:

> R_base = σ · R_det + (1 − σ) · R_old

When σ = 1, the full detection benefit is captured. When σ = 0, risk stays at R_old — the fix failed and the pre-detection risk level applies.

**Phase 3 — Re-injection.** Modifying the system can introduce new problems:

> R_k(i) = R_base · (1 − ν) + ν

Re-injection applies to the result of the attempt, not the success. A failed fix that modifies code still carries re-injection risk.

**Break-even re-injection rate.** Below this threshold, the cycle does more good than harm:

> ν* = σ · R · q / (1 − q · R · (1 − σ))

When σ = 1: ν* = q · R. When σ = 0: ν* = 0 (any re-injection is harmful since the fix provides zero benefit).

**Divergence condition.** If ν > ν*, the cycle is net harmful — ΔR_cycle < 0. This is a hard exit condition: stop fixing and report the finding for human review.

**Substrate ceiling (re-derived).** The re-injection rate ν is the absolute floor for residual risk:

> lim_{n→∞} R_{n,k} ≥ ν_k

This is consistent with §1's substrate ceiling result but more precise — the floor is set by fix quality, not just detection capability.

### Reduction Properties (All Verified)

| Condition | Result | Meaning |
|---|---|---|
| η = 1, σ = 1, ν = 0 | Stage 4 (detection-only recursive) | Clean fix, novel finding |
| Additionally K=1, d=1, p uniform, π=0.5 | Stage 1 (white paper C(n)) | All simplifications applied |
| σ = 0, ν = 0 | R unchanged | Fix failed, no side effects |
| σ = 0, ν > 0 | R increases | Fix failed and introduced new problems |
| η = 0 | q = 0, R unchanged | Redundant finding adds nothing |
| ν = 1 | R = 1 | Fix always breaks something |
| q = 1, σ = 1, ν > 0 | R = ν | Perfect detection, re-injection is the floor |

The complete lineage from C(n) to the three-phase operational form is a chain of strict generalisations, each adding one mechanistic dimension that the previous stage assumed away.

(Unified equation derived 8 April 2026. Three-phase extension derived 8–9 April 2026. Confer-verified by Gemini 3.1 Pro and Codex GPT-5.4. SymPy + Wolfram Alpha verified. Full derivation logs: `bench/logs/confer_unified_equation/`. Operational specification: `bench/directives/universal/cdsfl_operational.md` §3.)

---

## 1.2 FFAFP Calibration Protocol

### Motivation

The unified self-assessment equation R_k(i) is only as trustworthy as its inputs. If the prior flaw rate π is poorly estimated, if detection probability d is inflated by a model that claims to find flaws it did not actually investigate, or if a "fix" is declared effective without re-testing, then R_k(i) will produce a confident but wrong residual risk estimate. The equation itself cannot prevent garbage inputs from producing garbage outputs.

FFAFP — Full Falsification of All Falsification Passes — is the calibration protocol that ensures R_k(i) inputs are valid before they enter the recursive update. It is not a separate equation or an alternative to the self-assessment model. It is the operational procedure that makes the model's assumptions hold in practice.

Without structural enforcement of input quality, empirical evidence from Experiments 12–37 shows that 0–13% of model-submitted findings survive independent falsification. This means models, left unconstrained, routinely submit findings that fail their own claimed standards. FFAFP closes this gap by requiring that every input to R_k(i) passes through a defined constraint set before it is accepted.

### The Constraint Set

FFAFP defines an admissibility constraint set C_FFAFP. A finding or parameter update is admissible (may enter R_k(i)) if and only if it satisfies all constraints in this set simultaneously.

**C_FFAFP = { S_min, G-completeness, d_tool, σ_measured, q_retest }**

Each constraint is defined below with its plain-English meaning and formal expression.

**S_min — Minimum evidence standard.**

A finding must include concrete evidence: a specific location in the code (file, function, line), a description of the flaw mechanism, and either a proof-of-concept or a falsification argument for why the flaw exists. Findings that consist only of general warnings ("this code may have race conditions") without specific evidence are inadmissible.

> Formally: for finding f to be admissible, f must contain (location, mechanism, evidence) where evidence ∈ {proof-of-concept, formal argument, tool output}. Findings with evidence = ∅ are rejected.

**G-completeness — The finding must be complete enough to verify.**

A finding cannot be independently verified if it omits critical information. G-completeness requires that another agent (human or machine), given only the finding text, could reproduce the investigation and reach a verdict. If verification requires information not present in the finding, the finding is incomplete and inadmissible.

> Formally: f is G-complete iff an independent verifier V, given only f, can execute a verification procedure and produce a verdict v ∈ {CONFIRMED, REJECTED, INCONCLUSIVE} without requesting additional information from the finder.

**d_tool — Detection probability must be grounded in tool output.**

The detection probability d entering q = η · d · p must come from actual tool execution (static analysis, test runner, SymPy verification, AST parse), not from the model's self-assessed confidence. A model claiming d = 0.9 based on its own certainty is not admissible. A model that ran a test suite and observed 9/10 relevant tests catching the flaw class is admissible.

> Formally: d_i must be supported by tool output T_i where T_i is the result of executing a defined verification tool on the artifact under test. d_i = f(T_i) for some defined mapping f, not d_i = model_confidence.

**σ_measured — Fix efficacy must be measured, not assumed.**

When the three-phase extension uses fix efficacy σ, this parameter must come from re-running the verification tools after the fix is applied. A model declaring σ = 1.0 ("my fix definitely works") without re-testing is not admissible.

> Formally: σ is admissible iff post-fix verification V_post was executed and σ = g(V_pre, V_post) for some defined mapping g that compares pre-fix and post-fix tool outputs.

**q_retest — Effective detection probability must be retestable.**

The effective detection probability q = η · d · p used in the Bayesian update must be decomposable into its factors, and each factor must be independently verifiable. If q is a single opaque number produced by the model, it cannot be audited and is inadmissible.

> Formally: q_eff = η · d · p where each factor has an independent evidence trail. η (novelty) comes from similarity computation against prior findings. d (detection) comes from tool output (see d_tool). p (prior) comes from domain configuration or memory (see §1.2 above). None of these factors may be model self-assessments.

### What FFAFP is NOT

FFAFP is not a separate mathematical model. It does not add equations to the R_k(i) framework. It is the operational guarantee that the *assumptions* underlying R_k(i) hold in practice.

FFAFP is not `sth` (synthesis). The `sth` metacognitive command consolidates findings into a coherent whole. FFAFP validates individual findings before they enter the model. These are independent operations.

### Empirical justification

Without FFAFP structural enforcement:
- Experiments 12–15: 0–13% of submitted findings survived independent falsification
- Experiments 29–37: after FFAFP enforcement, survival rates rose to 60–85%

The difference is not model capability improving — it is the constraint set preventing inadmissible inputs from entering the model in the first place.

### Confounds

**Self-fulfilling calibration.** If the tools used to verify d_tool are themselves unreliable, FFAFP may create false confidence. Mitigation: tool diversity (multiple verification methods) and periodic tool-output audits by HIL.

**Constraint completeness.** C_FFAFP contains five constraints. There may be failure modes not covered by these five. The set should be treated as extensible, not closed.

**Human bottleneck.** FFAFP increases the verification burden. In practice, many verifications are automated (SymPy, test suites, AST checks), but some require HIL judgement. At scale (>50 findings per round), HIL cognitive overload becomes a genuine risk (identified by Gemini 3.1 Pro confer, 12 April 2026).

(FFAFP calibration protocol formalised 12 April 2026. Constraint set confer-verified by Codex GPT-5.4, ChatGPT GPT-5.4, and Gemini 3.1 Pro. Empirical data from Experiments 12–37.)

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

### Delivery Feasibility Factor (f_del)

The structured model implicitly assumes that every pass i produces a parseable response. In practice, model-architecture-specific constraints can cause a pass to produce zero usable output even when the model is functioning correctly. The primary observed mechanism is chain-of-thought budget exhaustion: models that allocate a shared output token budget between invisible reasoning and visible content can consume the entire budget on reasoning, producing a valid API response with empty content.

Define the delivery feasibility factor for model i:

> **f_del(i) = I(context_complete_i) · P(|response_i| > 0 | budget_i, arch_i)**

where I(context_complete_i) is a binary indicator (1 if model i received complete context, 0 if context was truncated), budget_i is the max_tokens allocation and arch_i encodes architecture-specific output constraints (e.g., shared CoT budget, output length limits). If a model's context is truncated, I = 0 makes feasibility zero, preventing downstream computation on incomplete input.

The effective detection probability becomes:

> q_ik = f_del(i) · d_ik · p_ik

When f_del(i) = 1 (all responses parseable), this reduces to the existing model.

**Estimation:** f_del can be estimated empirically from the ratio of non-empty responses to total API calls for each model, stratified by budget allocation. For models with CoT architectures, f_del is a decreasing function of prompt complexity (more complex prompts → more reasoning → higher probability of budget exhaustion).

**Context degradation (Exp 36 audit):** f_del is not a fixed per-model constant. In multi-round experiments where context grows monotonically, f_del degrades as a per-model function of cumulative context size:

> **f_del(i, t) = f_del,0(i) + α_i · context%(t)**

Where f_del,0(i) is the baseline delivery feasibility for model i, α_i is the per-model context sensitivity coefficient, and context%(t) is the context size at round t as a fraction of model i's context budget. The slope α_i differs by model and can be positive (model improves with context, e.g. DeepSeek) or negative (model degrades, e.g. Codex).

Exp 36 per-model output (early 8 rounds → late 8 rounds mean findings/round): Codex 5.8 → 1.6 (α < 0, sharp degradation); DeepSeek 3.8 → 6.1 (α > 0); ChatGPT 4.2 → 3.9 (α ≈ 0); Gemini 3.1 → 3.9 (α ≈ 0); CC2 1.9 → 1.1 (α < 0, mild). Context grew from 94.8% to 405.6% of budget over 23 rounds. The aggregate correlation (r = −0.260, p = 0.269) is non-significant because opposite per-model trends cancel in aggregation. Per-model analysis is required. (Added 8 April 2026, computed during mathematical model audit.)

**Calibration from Experiment 15:** DeepSeek Reasoner with max_tokens=32768 showed f_del ≈ 0.8 (1 budget exhaustion in 5 rounds). Reducing max_tokens to 16384 with retry-on-empty is the operational mitigation; the formal model captures the residual risk. (Added during failure mode analysis, 30 March 2026.)

### Decomposition Yield Bounds (η_dec)

When a model's context or output capacity is insufficient for the full artifact, the orchestrator decomposes the task into area-specific sub-prompts. The implicit assumption is that decomposition preserves or improves detection: Σ_a |F_decomposed(a)| ≥ |F_full|. Experiment 15 falsified this for Gemini 3.1 Pro: full-artifact review produced 6 findings; decomposed review produced 1.

Define the decomposition yield ratio for model i:

> **η_dec(i) = exp(−τ_defer(i)) · (|F_decomposed(i)| / |F_full(i)|_expected)**

Where τ_defer(i) ≥ 0 represents the integration complexity permanently lost by severing cross-module context. Decomposition is penalised exponentially based on how much structural synthesis was deferred. This creates a provable optimisation threshold: decomposition is only mathematically viable when the capacity yield multiplier exceeds the synthesis deferral penalty exp(τ_defer).

When η_dec(i) < 1, decomposition is counter-productive for model i. The effective detection probability under decomposition becomes:

> q_ik^dec = η_dec(i) · d_ik · p_ik

This introduces a testable prediction: for each model, there exists a context threshold below which decomposition improves yield (η_dec > 1) and above which it degrades yield (η_dec < 1). The optimal decomposition threshold is model-specific and should be calibrated empirically.

**Reduction property:** When τ_defer = 0, the decomposed metric reduces to the simple ratio |F_decomposed|/|F_full|_expected. (τ_defer replaces the falsified attention yield claim from Rounds 2–6 of the coherence audit, 31 March 2026.)

**Interaction with f_del:** For models where decomposition is applied specifically to avoid budget exhaustion, η_dec and f_del are coupled. The orchestrator should choose the strategy that maximises f_del · η_dec, not f_del alone. A model that produces 6 findings with f_del=0.8 (expected yield: 4.8) outperforms the same model decomposed with f_del=1.0 but η_dec=0.17 (expected yield: 1.0).

**Reduction property:** When η_dec(i) = 1 for all i (decomposition neither helps nor hurts), the model reduces to the existing formulation. (Added during failure mode analysis, 30 March 2026.)

### Format Yield and Inter-Model Convergence (φ_fmt(i))

The inter-model convergence metrics (kappa_set, kappa_rate, kappa_adopt) defined in the operational layer compute agreement over the set of parsed findings per model. When a model produces findings in a format the parser does not recognise, |F_parsed(i)| = 0 even though the model produced substantive output. This creates a specification error: the convergence metric treats the model as having found nothing, and inter-model agreement (kappa) computes over incomplete sets.

Define the format yield for model i:

> **φ_fmt(i) = |F_parsed(i)| / |F_actual(i)|**

where |F_actual(i)| is the count of genuine findings in the model's raw output (regardless of format compliance) and |F_parsed(i)| is what the parser extracts.

The convergence metric should operate on the effective finding set:

> **F_eff(i) = F_parsed(i) ∪ F_rescued(i)**

where F_rescued(i) are findings recovered by format-adaptive re-extraction when φ_fmt(i) < 1 is detected. The detection condition is:

> **|raw_chars(i)| > τ_chars ∧ φ_fmt(i) < τ_φ**

where τ_chars is a minimum response size threshold (indicating the model produced substantive output) and τ_φ is the minimum acceptable format yield (typically 0.5).

**Relationship to f_del:** f_del captures whether the model produces any output at all; φ captures whether produced output is parseable. The two are sequential: first f_del determines if there is a response, then φ determines if the response is usable. The combined effective detection probability is:

> q_ik = f_del(i) · φ_fmt(i) · d_ik · p_ik

When both f_del(i) = 1 and φ_fmt(i) = 1, this reduces to the existing model.

**Calibration from Experiment 15:** DeepSeek Reasoner used `**F001**` format (bold markdown IDs) instead of the expected `FINDING_ID: F001` text format. Raw output: 9738 chars, 14 actual findings, 0 parsed findings → φ = 0. This is a pure format divergence, not a detection failure — the model's analytical capability was intact. (Added during failure mode analysis, 30 March 2026.)

**Fix pipeline format failure (Exp 36 audit):** The fix pipeline (NL fix → applicable code change) showed φ_fmt = 0.0 across 285 fix evaluations in 23 rounds — 100% UNEVALUABLE. This is distinct from the per-model finding format yield above: it is a complete pipeline-level format failure where no proposed fix was ever in a form the pipeline could evaluate. The fix pipeline's φ_fmt is effectively a separate parameter from the finding-level φ_fmt(i) and should be tracked independently. (Added 8 April 2026, computed during mathematical model audit.)

### Diversity Separability Axiom

The diversity discount d_ik decomposes into two independent factors:

> **d_ik ≡ d_weight(i, k) · d_config(i, k)**

Where d_weight models underlying parameter space overlap (how similar the models' internal representations are for class k) and d_config models operational inference overlap (how similar the prompts, context, and instructions are). This grounds inter-model orchestration: the penalty of using two models from the same architecture family (d_weight < 1) is separable from the penalty of giving them identical prompts (d_config < 1).

**Reduction property:** When d_config = 1 for all pairs (fully distinct operational setups), d_ik = d_weight — the pure architectural diversity term.

(Separability axiom from Round 7 coherence audit, 31 March 2026.)

### NMI Diversity Estimator (δ_ij)

The observable output correlation between models i and j is estimated via Normalised Mutual Information:

> **δ_ij = 1 − I(X_i; X_j) / min(H(X_i), H(X_j))**

Where:
- I(X_i; X_j): mutual information (overlap of discovered errors between models i and j)
- H(X_i): Shannon entropy (total analytical content of model i's output)
- δ_ij → 1: orthogonal discovery (maximum diversity — models finding different defects)
- δ_ij → 0: identical information manifolds (models echoing each other)

**Relationship to Ising model:** (1 − δ_ij) directly parameterises the pairwise coupling constants ψ_ij in §0.1. High mutual information (low δ) implies strong positive coupling (correlated failures). This provides the missing observable estimator for the theoretical d_ik parameter and the Ising coupling constants.

**Domain:** NMI ∈ [0, 1] by information theory (I(X;Y) ≤ min(H(X), H(Y))), therefore δ_ij ∈ [0, 1]. No clipping required.

(NMI diversity estimator adopted during Round 8 construct evaluation, 31 March 2026. SymPy verified.)

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
- **R_{n,k}** = per-class residual risk: (π_risk,k · m_k) / ((1 − π_risk,k) + π_risk,k · m_k)
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
| f_del (delivery feasibility) | Well-defined, reduces to existing when f_del=1; context degradation formalised (Exp 36 audit) | Exp15: DeepSeek f_del≈0.8 at 32K. Exp36: per-model α_i diverge (Codex −4.1, DeepSeek +2.4) | Calibrate per-model f_del(i,t) from multi-round API response data |
| η_dec (decomposition yield) | Well-defined, reduces to existing when η_dec=1 | Exp15: Gemini η_dec≈0.17 (6→1 findings) | Measure per-model η_dec across decomposition thresholds |
| φ_fmt(i) (format yield) | Well-defined, sequential with f_del; fix pipeline φ_fmt=0.0 documented (Exp 36 audit) | Exp15: DeepSeek φ=0. Exp36: fix pipeline 285/285 UNEVALUABLE | Implement format-adaptive re-extraction; fix pipeline format separately |

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

**Identifiability note:** ρ_MH and E*(t) (the evolving expertise estimate from the Feedback section) are confounded in outcome data. Both reduce the same C_H(k)·(1−ρ_MH) product, so the model cannot distinguish "human expertise is low" from "human is cognitively primed" using confer-round outcomes alone. Identification requires experimental variation: blind rounds (ρ_MH ≈ 0) provide unconfounded E*(t) estimates; confer rounds with independently calibrated E*(t) provide ρ_MH estimates. Joint estimation from confer-only data is ill-posed. (Finding from 5-model Experiment 17, March 2026.)

### HIL Detection Probability

The HIL's per-pass detection probability is parameterised as:

> **p_{H,j,k} = min(1, f_k(E, M) · Π_s (1 + λ_s · V_s))**

> **f_k(E, M) = E · (α + (1−α) · M)**

Where:
- E ∈ [0,1] — domain expertise level
- M ∈ [0,1] — methodology formality (0 = informal judgment, 1 = fully formal)
- α ∈ (0,1) — floor coefficient (expertise alone, without formal method)
- λ_s ∈ [0, 1) — sensitivity coefficient for domain variable s (bounded to ensure (1 + λ_s · V_s) > 0)
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

> **κ_asym = 1 − β_pen · max(0, E_claimed − E*(t)) − max(0, E*(t) − E_claimed)**

Where β_pen > 1 penalises overconfidence. With β_pen = 1.5:

| Scenario | E_claimed | E*(t) | κ (symmetric) | κ (asymmetric, β_pen=1.5) |
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
2. **Asymmetric calibration outcomes:** Does penalising overconfidence more heavily than underconfidence (β_pen > 1) produce better system-level detection than symmetric calibration (β_pen = 1)? Testable by comparing aggregate detection rates under both regimes.
3. **Calibration score publication effects:** Does publishing the calibration score change reviewer behaviour? Specifically: does it produce honest self-assessment (the intended outcome) or strategic sandbagging (claiming low E to appear well-calibrated when overperforming)? This is a behavioural question, not a mathematical one, but it affects whether the metric is deployable.
4. **Sandbagging detection via symmetric miscalibration check.** The expertise posterior E*(t) = (a₀ + Σcatches) / (a₀ + b₀ + Σtrials) converges in approximately 5 reviews. After convergence, persistent miscalibration in either direction is detectable: if |E_claim,t − E*(t)| > τσ_t for k consecutive reviews, flag the reviewer. Direction-aware normalised counters (overclaim_rate = overclaim_count / t, underclaim_rate = underclaim_count / t) distinguish persistent from sporadic miscalibration and overclaiming from underclaiming without requiring a separate posterior. The detection is symmetric: the same threshold and mechanism catches both overconfidence and strategic sandbagging. E*(t) remains the sole skill estimate, uncontaminated by honesty tracking. An earlier dual-posterior design (S*(t)) was considered but rejected as unnecessary — the founder correctly identified that the existing E*(t) posterior already provides the evidence for detection in both directions.
5. **Priming correlation extension.** The priming state can be made pass-specific: ρ_MH,j = clip(ρ₀ + γ₁(1 − I_j) + γ₂F_j + γ₃R_j + γ₄D_j, 0, 1), where I_j is blind-first compliance (binary), F_j/R_j/D_j are fatigue/rush/distraction proxies from telemetry. When I_j = 0 (human saw machine output before committing), ρ_MH,j increases toward 1, reducing the human's effective independent contribution in G_n. Coefficients γ₁–γ₄ require empirical calibration.

### Correlation Domain Constraint

All correlation variables (including ρ_MH) are valid exclusively on the domain [0, 1]. The framework unconditionally applies:

> **ρ_effective = max(0, min(1, ρ))**

to all derived correlations. This ensures that behavioural modifiers (e.g., fatigue, rush) cannot accidentally flip the cognitive priming equation into generating mathematically impossible negative correlations.

(Domain constraint from Round 7 coherence audit, 31 March 2026.)

### Hint Framing Penalty (F_HIL)

When a human provides a hint, it collapses the search space to a sub-manifold Ω_hint ⊂ Ω. This produces a quantifiable blind spot for defect classes outside the hinted region. The penalty is modelled via KL divergence information gain:

> **IG_HIL = D_KL(P(Ω | Hint) ‖ P(Ω))**

The empirical miss probability m_k for defect class k ∉ Ω_hint is penalised:

> **m_{k|hint} = 1 − (1 − m_k) · exp(−IG_HIL)**

**Boundary conditions:**
- IG_HIL = 0 (no hint): m_{k|hint} = m_k — no penalty
- IG_HIL → ∞ (maximally constraining hint): m_{k|hint} → 1 — total blindness outside hint scope

Highly specific hints mathematically degrade the system's ability to find orthogonal defects, enforcing the principle that the search should be "wide" in early rounds and "deep" in later rounds. The Team Manager calculates the optimal entropy path to ensure the search remains broad before narrowing.

**Relationship to ρ_MH:** The priming correlation ρ_MH captures the general correlation between human and machine reasoning. IG_HIL captures the specific damage a particular hint does to the search space. Both reduce effective HIL contribution, but through different mechanisms: ρ_MH through overlap of analytical framing, IG_HIL through restriction of the prior domain.

(Hint framing penalty modified from informal Gemini constructs and adopted during Round 8, 31 March 2026. SymPy verified: IG=0 → no penalty, IG→∞ → m=1.)

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

**Error re-injection extension:** The standard Duane model assumes monotonic decay of latent defects. In practice, iterative multi-model refactoring introduces new defects. The extended intensity function accounts for error re-injection:

> **λ_ext(n) = (β / η) · (n / η)^(β − 1) + ν · Δ_{n−1}**

Where ν ∈ [0, 1] is the Re-injection Coefficient (probability that a structural adoption in round n−1 yields a new fault) and Δ_{n−1} is the quantified adoption magnitude from §7.6.

**Divergence condition:** If ν · Δ_{n−1} > |dλ_Duane/dn|, the system transitions from convergence to entropy generation (producing more noise than signal). This triggers an automatic halt. The Team Manager monitors the re-injection term to detect when fixes are destabilising the system.

**Reduction property:** When ν = 0 (no re-injection), λ_ext = λ — the standard Duane model.

(Error re-injection modified from informal Gemini constructs and adopted during Round 8, 31 March 2026. SymPy verified: dλ/dn < 0 for β < 1 confirmed.)

**Context-loss re-injection extension:** The ν · Δ_{n−1} term above models fix-induced re-injection: adopting a structural fix in round n−1 introduces a new fault with probability ν. A distinct re-injection mechanism was observed in Exp 36 at R8 (ITC restart_fresh). When the runner wipes a model's context and restarts it, the model re-enters a partially depleted defect space with no memory of prior discoveries — producing rediscoveries, not new defects.

Define the context-loss re-injection term:

> **λ_itc(n) = μ_i · I(restart_i, n) · D_seen(n − 1)**

Where μ_i ∈ [0, 1] is the per-model context-loss rediscovery rate (fraction of previously seen defects the model will re-find after context wipe), I(restart_i, n) is a binary indicator for whether model i underwent restart_fresh at round n, and D_seen(n − 1) is the cumulative unique defect count at the end of round n − 1.

The full extended intensity becomes:

> **λ_full(n) = (β / η) · (n / η)^(β − 1) + ν · Δ_{n−1} + Σ_i λ_itc,i(n)**

**Distinction from ν · Δ:** The fix-induced term (ν · Δ) introduces genuinely new faults; the context-loss term (λ_itc) rediscovers existing faults. The fix-induced term depends on adoption magnitude; the context-loss term depends on cumulative discovery count and is per-model (different models have different μ_i values — Exp 36 data: Codex jumped 1→9, DeepSeek 2→7, Gemini 1→4 at R8).

**Reduction properties:** When no restart occurs (I = 0 for all i), λ_full = λ_ext. When additionally ν = 0, λ_full = λ — the standard Duane model.

**Empirical calibration (Exp 36):** The R8 burst produced 21 novel findings from 29 raw. Adding a burst term to the standard Duane model improved fit significantly (F = 13.49, p = 0.0017, burst magnitude ν_burst = 12.96). The standard Duane under-predicts post-R8 cumulative novel counts. (Added 8 April 2026, computed during mathematical model audit.)

### 7.1a Discovery Efficiency ρ (Churn Detection)

The Duane convergence parameter γ classifies the finding rate trajectory but is blind to a specific failure mode: the system can maintain a constant raw output rate while novel output declines — churn. Gamma sees the novel deceleration and reports convergence, but cannot detect that operational waste is increasing because it does not track raw output independently.

Define the discovery efficiency for round t:

> **ρ(t) = novel(t) / raw(t)**

Where novel(t) is the count of findings in round t that are not duplicates of any prior finding, and raw(t) is the total finding count in round t. ρ(t) ∈ [0, 1]; ρ = 1 means all output is novel; ρ → 0 means the system is churning.

**Churn detection condition:** Define the 3-round rolling discovery efficiency:

> **ρ̄₃(t) = (ρ(t) + ρ(t−1) + ρ(t−2)) / 3**

The churn signal activates when:

> **churn(t) ≡ (ρ̄₃(t) < θ_ρ) ∧ (t ≥ t_earliest)**

Where θ_ρ = 0.25 is the churn threshold and t_earliest is the minimum round for convergence evaluation (matching the runner's earliest_stop parameter). The t_earliest guard prevents false positives from early-round depletion, which is a normal phase of the discovery process and not churn.

**Justification (Exp 36):** Logistic regression comparing gamma-only (AIC = 24.2) vs gamma + rho (AIC = 17.7) for predicting convergence gate satisfaction: ΔAIC = 6.5 in favour of the combined model. Rho carries predictive information gamma does not have. Cross-experiment rho trends: significant decline in Exp 33 (p = 0.003) and Exp 36 (p = 0.035). Threshold θ_ρ = 0.25 with t_earliest = 12 first triggers at R16 in Exp 36, matching the estimated epistemic saturation point (~R15). (Added 8 April 2026, computed during mathematical model audit.)

**Relationship to gamma:** γ and ρ are complementary, not redundant. γ measures the rate of novel discovery deceleration (power-law shape). ρ measures the ratio of useful work to total work (efficiency). A system can have γ > 0 (novel rate declining, classified as converging) while ρ is low (most output is waste). Exp 36 demonstrated this: γ = 0.411 (converging) while post-R8 mean ρ = 0.242 (75.8% of output was waste).

### 7.2 Abstraction Index H(x) (Finding Depth)

Not all findings are equal. A syntax error and a paradigm-level architectural flaw both count as one finding, but contribute different analytical value. The Abstraction Index scores each finding on three dimensions:

> **H(x) = c · F(x) · ρ_info(x) · G(x)**

Where:
- **F(x)** = 1 + c_F1·𝟙(verifiable_claim exists) + c_F2·𝟙(constraint_class = HARD) — **Formality**: presence of verifiable claims and HARD constraint violations
- **ρ_info(x)** = ln(e + W_e / (W_c + 1)) — **Information density**: evidence-to-claim word ratio (short dense findings score higher than verbose restatements)
- **G(x)** = 1 + c_G1·ln(1 + N_cm) + c_G2·ln(1 + D_ref) — **Generalisation scope**: cross-module mention count and reference depth
- **c** = model confidence (0 to 1)
- c_F1, c_F2, c_G1, c_G2 initialised at 1.0 (calibration against human-ranked examples pending)

**Verified:** High-abstraction finding (formal, dense, cross-cutting, high confidence) scores H = 17.89. Low-abstraction finding (informal, verbose, local, moderate confidence) scores H = 0.53. Discrimination ratio: 33.4×. (D(x) renamed to ρ_info(x) during 3-model confer, 27 March 2026, to resolve triple collision with D(n) distributed coverage and D_decay in the capability fingerprint.)

**Reduction property:** When all Boolean indicators are 0, evidence word count W_e = 0, and there are no cross-module references (N_cm = D_ref = 0), H(x) reduces to c · ln(e) · 1 = c (confidence alone). The index degrades gracefully to the simplest possible measure. (Note: the density function ρ_info(x) = ln(e + W_e/(W_c + 1)) equals 1 only when W_e = 0, not when W_e = W_c > 0. This is by design — any evidence content adds informational value.)

### 7.3 Total Cognitive Yield Y(t)

> **Y(t) = N(t) · H̄(t)**

Where N(t) is finding count at time t and H̄(t) is the mean Abstraction Index of all findings up to time t.

**Ascending abstraction condition:** dH̄/dt > 0 while dλ/dt < 0 (equivalently, d²N/dt² < 0 — the finding *rate* is decreasing, not the cumulative count, which is monotonically increasing by definition). The analyst is producing findings at a decreasing rate but each is deeper. Total yield Y(t) increases despite the rate decrease when the relative depth increase exceeds the relative rate decrease:

> **(dH̄/dt) / H̄(t) > |dλ/dt| / λ(t)**

This is the formal condition for ascending abstraction. When this inequality holds, dY/dt > 0 despite declining finding rate. This captures creative deepening as a distinct cognitive mode from analytical exhaustion.

**Motivation:** The founder's cognitive pattern across the project showed decreasing finding count (fewer observations per session) but monotonically increasing significance (from debugging scripts to designing theoretical frameworks). The decay curve alone would classify this as non-convergent. Y(t) correctly recognises it as ascending abstraction.

### 7.4 Online Total Value Estimator

The total analytical value can only be calculated after the analysis completes. But operational decisions (continue or stop?) must be made during analysis. The online estimator provides a running prediction:

> **V̂(t, T) = ∫₀ᵗ v(τ)dτ + remaining_estimate**

Where the remaining estimate is:
- If k_decay(t) > 0: v_w(t) · (1 − exp(−k_decay(t) · (T − t))) / k_decay(t)
- If k_decay(t) ≤ 0: v_w(t) · (T − t)

Here k_decay(t) is the local exponential decay rate of the sliding-window generation rate v_w(t), estimated from consecutive round values. This is distinct from the Duane NHPP intensity λ(t) in §7.1, which is the global power-law intensity and is always positive.

v_w(t) is the sliding-window smoothed generation rate. λ(t) is the empirical decay rate estimated from consecutive round values.

**Convergence guarantee:** As t → T, the remaining estimate → 0. Verified: at round 5 of a 5-round test, V̂ = 22.0 = true total 22. Wolfram confirms lim_{t→T} remaining_estimate = 0.

**Practical value:** Enables early stopping for efficient analysts (steep decay, most value captured) while allowing systematic processors to continue (late bloomers whose best findings come in later rounds). Directly supports the cognitive diversity accommodation principle: evaluate by total verified yield, not by when findings arrive.

**Ascending abstraction guard:**

> **stop_valid(t) = (V̂_remaining(t) < ε) ∧ ¬ascending_abstraction(t)**
>
> **ascending_abstraction(t) ≡ (dH̄/dt > 0) ∧ (dλ/dt < 0) ∧ ((dH̄/dt)/H̄(t) > |dλ/dt|/λ(t))**

V̂ stop recommendations require both conditions: the count-based remaining estimate is below threshold ε, AND ascending abstraction is not active. Ascending abstraction (§7.3) holds when the finding rate is decreasing but the relative depth increase exceeds the relative rate decrease, guaranteeing that total yield Y(t) is still increasing. V̂ underestimates remaining value in this mode because it is count-based. In bimodal discovery patterns (surface findings → lull → late deep findings), ungated V̂ would recommend premature termination during the lull. (Originally identified during CC × Gemini 3.1 Pro Extended P-Pass; quantitative condition added during 5-model meta-test, 27 March 2026.)

**Runner convergence gate (operational implementation):** The experiment runners implement termination as a 5-condition Boolean gate, all conditions must be satisfied for `consecutive_required` (default: 2) consecutive rounds:

> **converged(t) ≡ C₁(t) ∧ C₂(t) ∧ C₃(t) ∧ C₄(t) ∧ C₅(t)**
>
> C₁: t ≥ t_earliest (minimum round threshold, default 12)
> C₂: contested(t) ≤ 1 (finding-level dispute near resolution)
> C₃: novel(t) ≤ max_novel (default 2) for consecutive_required rounds
> C₄: γ(t) < γ_hard (default 0.35, hard threshold)
> C₅: γ gate passed (γ trend direction confirms deceleration)

**Reconciliation (Exp 36 audit):** The runner gate and the appendix's stop_valid are not equivalent. Three structural differences were identified:

1. The runner has no concept of ascending abstraction. V̂ underestimates remaining value during creative deepening; the runner gate cannot detect this mode. **Action required (runner → appendix direction):** implement H̄(t) tracking and the ascending abstraction guard as a convergence gate override — if ascending abstraction is active, the gate cannot trigger regardless of other conditions.

2. The appendix has no concept of contested findings. In Exp 36, contested findings were the sole convergence blocker at R19 (4/5 conditions met, C₂ failed). The appendix's V̂ estimator does not distinguish contested from confirmed findings. **Action required (appendix → runner direction):** the contested condition (C₂) is load-bearing and should be formalised in the appendix as a finding-level dispute resolution requirement.

3. Two of the runner's 5 conditions (C₃ and C₄) were non-contributing in Exp 36: C₃ was met in 1/11 eligible rounds; C₄ was met in 0/11 rounds (γ stalled at 0.411). The churn detection condition from §7.1a (ρ̄₃ < θ_ρ) should replace or augment C₄, since γ's hard threshold does not fire when γ stalls above it. **Action required (both directions):** add churn(t) (§7.1a) as C₆ in the runner gate, and add the runner's contested condition as a formal term in the appendix.

(Reconciliation added 8 April 2026, based on mathematical model audit of Exp 33-36 data.)

### 7.5 Objective Alignment O_A (Sycophancy Detection)

When models confer and converge on shared findings, the convergence could be genuine (both independently found the same real issue) or sycophantic (they are agreeing to agree). This metric distinguishes them using SymPy verification as a proxy for ground truth:

> **F_conv = (C_A ∩ C_B) \ (B_A ∩ B_B)**

F_conv is the set of newly converged findings (present in both models' confer output but not in both models' blind output).

> **O_A = |verified findings in F_conv| / |F_conv|**
>
> Convention: if F_conv = ∅, O_A = 1

The composite sycophancy score:

> **S_sync = Δ̄ · (1 − O_A)**

Where Δ̄ is the mean Adoption Delta (§7.6) across all model pairs. S_sync ≈ 0: genuine consensus (low deference or high verification). S_sync high: sycophantic convergence (high deference on unverified claims). High Δ̄ (capitulation) combined with low O_A (unverified) correctly maximises the sycophancy signal. (Formula corrected during 5-model meta-test, 27 March 2026 — original formula (1 − δ̄)·(1 − O_A) was inverted with respect to Δ.)

**Non-verifiable domain guard:**

> **O_A defined iff |{f ∈ F_conv : verifiable(f)}| ≥ 2**
>
> **If |{f ∈ F_conv : verifiable(f)}| < 2: O_A = ⊥, S_sync = Δ̄**

When the verifiable subset of F_conv contains fewer than 2 findings, O_A is undefined (⊥) and S_sync relies on Δ̄ alone. The threshold at 2 is deliberate: a single verification outcome produces O_A ∈ {0, 1}, making S_sync binary on one data point. Two or more verifiable findings provide the minimum discriminative power for a meaningful verification rate. Without this guard, O_A = 0/|F_conv| = 0 on non-mathematical claims, producing S_sync = Δ̄ · 1 = Δ̄ — flagging all convergence with high deference as sycophantic regardless of content quality. (Guard identified during CC × Gemini 3.1 Pro Extended P-Pass; rationale formalised during 3-model confer, 27 March 2026.)

**Mutual suppression guard:**

S_sync measures convergence on unverified shared claims. A separate failure mode exists: both models drop their blind findings without converging on anything new. When F_conv = ∅ and both models abandoned findings, S_sync = 0 (because O_A = 1 by convention), which misclassifies mutual analytical collapse as independence. The mutual suppression metric detects this:

> **M_suppress(A, B) = I(|B_A \ B_B| > 0 ∧ |B_B \ B_A| > 0) · 𝟙(F_conv = ∅) · (Δ_drop(A→B) + Δ_drop(B→A)) / 2**

Where Δ_drop is the asymmetric drop rate from §7.6 and I(·) ensures mutual suppression only triggers when both models actually had unique work to drop. When M_suppress > τ_suppress, flag as destructive convergence (distinct from sycophancy). When F_conv = ∅ and M_suppress triggers, O_A = ⊥ and S_sync = ⊥ — evaluate mutual suppression instead. τ_suppress calibration: start conservatively at 0.5 (both models dropped at least half their unique findings). (Identified during 5-model meta-test; formalised during 3-model confer, 27 March 2026.)

**Limitation:** O_A is computed only from the subset of findings that SymPy can verify (mathematical claims). For tasks with few mathematical claims, the metric has low statistical power. This is documented, not hidden.

**Null-vector yield weighting:**

To avert evaluating S_sync on empty sets, the aggregate value of a composite finding set y is:

> **w(y) = 0, if ‖y‖₂ = 0**
>
> **w(y) = v̄(y) · u_qual(y) · (1 − S_sync(y)), if ‖y‖₂ > 0**

When a model pair outputs zero new findings, w(y) = 0, avoiding a divide-by-zero cascade inside Objective Alignment (O_A). (Null-vector guard from Round 7 coherence audit, 31 March 2026.)

**Empirically-anchored sycophancy trigger:**

When seeded defect injection (§1) and NMI diversity estimation (§2) are available at runtime, S_sync can be anchored to empirical observables:

> **S_sync^emp = (1 − δ̄_cp) · (1 − Ŝ_H)**

Where δ̄_cp is the mean NMI-based diversity (§2) between the Captain and Position players, and Ŝ_H is the seeded detection sensitivity (§1). This distinguishes:
- **Valid convergence:** δ low (models agree) but Ŝ_H high (found planted defects) → S_sync^emp low
- **Sycophantic collapse:** δ low (models agree) and Ŝ_H low (missed planted defects) → S_sync^emp high
- **Diverse but weak:** δ high (models disagree) and Ŝ_H low → S_sync^emp low (not sycophancy, just capability gap)

Bench-and-Swap is executed if S_sync^emp > τ_sync: relegate the sycophantic model, promote a Wildcard with known low correlation.

**Selection:** Use S_sync (behaviour-based, §7.5) when seeded defects are not available. Use S_sync^emp (empirically-anchored) when both seeded sensitivity and NMI diversity are available. S_sync^emp is strictly preferred because it distinguishes valid convergence from sycophantic collapse using ground-truth measurement. (Adopted during Round 8 construct evaluation, 31 March 2026. SymPy verified: three-regime discrimination confirmed.)

### 7.6 Adoption Delta Δ (Independence Measurement)

Static overlap between finding sets does not reveal whether a model changed its analysis after seeing another's work. The adoption delta measures dynamic deference via two asymmetric rates:

> **A_adopt = C_A ∩ (B_B \ B_A)** — findings A adopted from B
>
> **A_drop = (B_A \ B_B) \ C_A** — findings A dropped after seeing B
>
> **Δ_adopt(A→B) = |A_adopt| / |B_B \ B_A|** — adoption rate (fraction of available novel findings incorporated)
>
> **Δ_drop(A→B) = |A_drop| / |B_A \ B_B|** — drop rate (fraction of unique own findings abandoned)

Convention: if a denominator is zero, the corresponding rate is zero.

- Δ_adopt = 0, Δ_drop = 0: complete independence
- Δ_adopt = 1, Δ_drop = 1: complete capitulation
- High Δ_adopt with low Δ_drop: selective incorporation (incorporating what survives scrutiny)
- Low Δ_adopt with high Δ_drop: self-suppression (abandoning own work without replacement)

Where a single scalar is needed (e.g., for S_sync in §7.5), the derived scalar is:

> **Δ̄(A→B) = (Δ_adopt(A→B) + Δ_drop(A→B)) / 2**

The asymmetric rates are the primary construct. The derived scalar is a convenience summary that should not be used for cross-pairing comparison, because the underlying opportunity sets (|B_B \ B_A| and |B_A \ B_B|) differ across pairings. (Confound identified during 5-model meta-test, 27 March 2026; asymmetric split resolved during 3-model confer, 27 March 2026.)

**Verified:** Test case with A blind = {f1, f2, f3}, B blind = {f2, f4, f5}, A confer = {f2, f4, f6}: Δ_adopt = |{f4}|/|{f4,f5}| = 0.5, Δ_drop = |{f3}|/|{f1,f3}| = 0.5, Δ̄ = 0.5. Identical blind findings yield Δ_adopt = 0, Δ_drop = 0 (nothing to adopt or drop).

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

> **Λ_total = Λ_prior + Σ_{i ∈ D_det} [o_i · log(TPR_i / FPR_i) + (1 − o_i) · log(FNR_i / TNR_i)]**
>
> **S_v = 1 / (1 + exp(−Λ_total))**

Where Λ_prior = 0 (uniform prior: P(claim true) = 0.5 before any verification). o_i ∈ {0, 1} is the binary output of verifier i (1 = verified, 0 = falsified), evaluated over the determinate set D_det (verifiers that returned a definite result). When verifier i returns indeterminate (neither verified nor falsified), it is excluded from D_det and does not contribute to Λ_total. When all verifiers are indeterminate, D_det = ∅, Λ_total = Λ_prior = 0 and S_v = 0.5 (neutral prior). The formula encodes conditional weight selection: when o_i = 1, the positive log-likelihood ratio log(TPR/FPR) is applied; when o_i = 0, the negative log-likelihood ratio log(FNR/TNR) is applied. This is a standard Naive Bayes log-odds update. The Λ_prior term makes the Bayesian structure explicit; the ≥ 0.5 selection threshold in §7.11 is calibrated to this specific prior. (Notation clarified during CC × Gemini 3.1 Pro Extended P-Pass; indeterminate handling formalised during 5-model meta-test, 27 March 2026. L→Λ rename and o_i notation applied during 8-round coherence audit, 31 March 2026.)

| Verifier | TPR | FPR | Positive weight log(TPR/FPR) | Negative weight log(FNR/TNR) |
|---|---|---|---|---|
| SymPy | 0.99 | 0.001 | 6.90 | −4.60 |
| Dimensional | 0.80 | 0.10 | 2.08 | −1.50 |
| Numerical | 0.70 | 0.15 | 1.54 | −1.04 |

**Veto property:** SymPy negative weight magnitude (4.60) exceeds sum of other positive weights (3.62). SymPy falsification overwhelms other verifications — a mathematically grounded veto. (Table corrected during 5-model meta-test, 27 March 2026 — original Dimensional and Numerical negative weights were computed as ln(FNR/TPR) instead of the correct ln(FNR/TNR). Veto property is strengthened by the correction since correct negative weights are more negative.)

**Verified:** SymPy falsified + others verified → S_v = 0.272 (below 0.5 threshold). All verified → S_v = 0.9999. All indeterminate → S_v = 0.5 (neutral).

### 7.9 Capability Fingerprint

The four-dimensional fingerprint per model per condition per task:

> **(D_decay, v̄, A, C)**

| Component | Meaning | Source |
|---|---|---|
| D_decay | Decay rate (inverse half-life) | Best-fitting decay model (§7.1) |
| v̄ | Mean verification score | All findings from this model |
| A | Total novel verified findings | Post-dedup, post-verification count |
| C | Coverage = A / estimated total real findings | Estimated real finding count from convergence analysis |

No single number tells the whole story. A model might find many things quickly (high D_decay, high A) but most are wrong (low v̄). Another finds few things (low A) but every one is correct (high v̄). The fingerprint distinguishes these cases.

### 7.10 Implementation Status

| Component | Mathematical status | Implementation status |
|---|---|---|
| Ising branching (§0.1) | Verified, reduction proven | Ready for implementation |
| Seeded sensitivity (§1) | Verified, domain [0,1] | Ready for implementation |
| Substrate ceiling (§1) | Verified, asymptote proven | Ready for implementation |
| NMI diversity (§2) | Verified, domain [0,1] | Ready for implementation |
| Separability axiom (§2) | Defined | Ready for implementation |
| τ_defer (§2) | Verified, reduction proven | Ready for implementation |
| ρ domain constraint (§6) | Verified | Ready for implementation |
| HIL framing penalty (§6) | Verified, limits confirmed | Ready for implementation |
| Duane NHPP + re-injection (§7.1) | Verified, AICc-tested, divergence condition proven | Implemented in decay_analysis.py (base); fix re-injection pending; context-loss re-injection pending |
| Context-loss re-injection (§7.1) | Defined, Exp 36 calibrated (F=13.49, p=0.0017) | Pending implementation |
| ρ discovery efficiency (§7.1a) | Defined, ΔAIC=6.5, θ_ρ=0.25 calibrated | Pending implementation (Task 3 runner fix) |
| H(x) (§7.2) | Verified, 33.4× discrimination | Ready for implementation |
| Y(t) (§7.3) | Verified | Ready for implementation |
| V̂ estimator (§7.4) | Verified, convergence proven | Ready for implementation |
| Runner convergence gate (§7.4) | 5-condition gate operational; 2/5 non-contributing in Exp 36 | Implemented; C₆ (churn) pending; ascending abstraction guard pending |
| O_A + S_sync^emp (§7.5) | Verified, edge cases handled, 3-regime discrimination | Ready for implementation |
| Δ (§7.6) | Verified | Ready for implementation |
| Sev(f) (§7.7) | Verified | Implemented in pipeline |
| Multi-verifier (§7.8) | Verified, Λ notation, both approaches | Ready for implementation |
| Fingerprint (§7.9) | Verified | Partially implemented |
| Manager selection (§7.11) | Defined, uses §7.7/§7.8 | Ready for implementation |
| FFF convergence (§7.12) | Verified, 7 properties proven | Process model; implemented via round instructions |

### 7.11 Manager Selection Function

In a multi-agent review, a formal predicate is required to decide which findings are actioned. The selection function filters the union of all proposed findings:

> **selected(f) ≡ (Sev(f) > τ_sev) ∧ (S_v(f) ≥ 0.5) ∧ (class(f) = HARD ∨ Sev(f) > τ_soft)**

Where:
- Sev(f) is per-finding severity (§7.7)
- S_v(f) is multi-verifier Bayesian severity (§7.8)
- τ_sev is the minimum severity threshold (task-dependent; default 0.0 for safety-critical, 0.3 for routine)
- τ_soft is the elevated severity threshold for SOFT constraints (default τ_sev)

This function prioritises verified, severe findings concerning HARD constraints, while allowing exceptionally severe SOFT findings to pass. The ≥ 0.5 threshold (not strict >) ensures that unverifiable findings (which default to S_v = 0.5 when all verifiers are indeterminate) are not systematically excluded — they are evaluated on severity and constraint class alone.

When 2/3 or more models agree on a finding but S_v < 0.5 (computational evidence is net negative), the finding is rejected. Model agreement does not override computational falsification. This is by design: the framework trusts mathematics over consensus.

(Added during 3-model confer, 27 March 2026.)

### 7.12 Find-Fix-Follow (FFF) Convergence Model

Standard CDSFL confer rounds require models to report findings but not to resolve them within their own turn. Find-Fix-Follow (FFF) extends this by requiring each model to (1) find a defect, (2) produce an exact fix, and (3) analyse the consequences of that fix — all in a single turn. This produces scope expansion: consequence analysis surfaces cross-section integration issues that finding-only rounds miss.

**State transition:** Each FFF cycle transforms the model state:

> **M_{n+1} = apply(M_n, r_j)**

Where r_j is the resolution of defect d_j found in state M_n. The "follow" step produces consequent defects:

> **D_{n+1} = ν · D_n + ε_n**

Where ν ∈ [0, 1) is the re-injection rate (§7.1) and ε_n ≥ 0 represents novel defects surfaced by consequence analysis.

**Contraction condition:** The FFF operator is contractive when:

> **ε_n < D_n · (1 − ν)**

That is, the novel defects from consequence analysis must be fewer than the net defects resolved. When ν < 1 and this condition holds, |D_n| decreases monotonically.

**Fixed point:** The defect count converges to:

> **D* = ε* / (1 − ν)**

Where ε* is the steady-state novel defect rate. When ε* = 0 (no novel follow defects), D* = 0 — clean convergence. When ε* > 0, D* > 0 — a residual defect floor bounded by the substrate ceiling (§1).

**Convergence rate:** The half-life of the defect count is:

> **n_{1/2} = −ln(2) / ln(ν)**

At ν = 0.5, half-life is 1 round. At ν = 0.8, half-life is 3.1 rounds. This is directly measurable from experimental data.

**Scope expansion ratio:** FFF surfaces more issues per cycle than findings-only confer:

> **D_total = D_found · (1 + σ)**

Where σ = |D_follow| / |D_found| is the scope expansion ratio. When σ = 0, FFF reduces to standard confer. When σ > 0, FFF discovers (1 + σ)× more issues per cycle.

**Relationship to Duane γ (§7.1):** For large n, the Duane intensity ratio λ(n+1)/λ(n) ≈ 1 − γ/n. The FFF contraction rate ν maps to this: γ > 0 ↔ ν < 1 (contractive), γ = 0 ↔ ν = 1 (churn), γ < 0 ↔ ν > 1 (divergent). The FFF convergence model is the discrete-round analogue of the continuous Duane NHPP.

**Termination:**
- **Natural termination:** D* < τ_D (defect count below threshold), equivalent to ε* < τ_D · (1 − ν)
- **Substrate ceiling (§1):** D* ≥ τ_D → Hard Exit (the ensemble lacks capability to resolve remaining defects)
- **Successive stall:** ΔR_n = 0 for consecutive passes → no further progress possible

**Efficiency comparison:** FFF is strictly more efficient than findings-only confer when σ > 0 and ν < 1. Each FFF round costs one model call (same as confer) but resolves issues and surfaces consequences in the same turn. Rounds-to-convergence ratio: n_FFF / n_confer ≈ 1 / (1 + σ).

**Empirical evidence:** Round 7 (31 March 2026). A single Gemini FFF round on the full 826-line appendix produced 6 integration issues — approximately 2 direct finds and 4 follow-consequences (σ ≈ 2.0). These were cross-section issues between Round 6 resolutions and existing appendix text that would have required multiple findings-only rounds to surface.

**Reduction property:** When σ = 0 (no follow step), the FFF model reduces to the standard confer model with findings-only rounds. When ν = 0 (no re-injection), convergence is immediate upon resolution. The standard models are special cases.

(FFF pattern identified from founder's informal Gemini interaction, 31 March 2026. Formalised and SymPy-verified 7/7 during 8-round coherence audit.)

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

> **Y_composite(t) > max{Y_i(t)} + z_conf · σ̂(Y)**

Where σ̂(Y) is the bootstrap standard error of the Y estimates and z_conf is a confidence multiplier (z_conf = 1.96 for 95% confidence). The strict inequality Y_composite > max(Y_i) is necessary but not sufficient — it must exceed the measurement uncertainty to distinguish genuine emergence from statistical noise. (Statistical threshold added during 5-model meta-test, 27 March 2026. k→z_conf rename during 8-round coherence audit, 31 March 2026.)

The Y_composite > max(Y_i) condition is necessary but not sufficient to distinguish emergence from simple aggregation. The union of individual outputs would give:

> Y_union(t) = |⋃ F_i(t)| · H̄_union(t)

**Strong emergence condition:** Y_composite(t) > Y_union(t) + z_conf · σ̂(Y). This establishes that interaction produced cognitive value beyond what the union of independent outputs would yield. The weaker condition (composite > max individual) is satisfiable by trivial aggregation and should not be used alone. Genuine emergence is the confer protocol forcing agents into analytical territory none explored alone. A finding from agent A provokes investigation by agent B, which surfaces a structural issue that agent C formalises. The resulting insight exists because of the interaction and is not present in any individual agent's blind output.

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

The CDSFL composite system meets criteria 1–3 by construction. Criterion 4 (measurable improvement from metacognitive adjustment) is a testable empirical claim. If confirmed, the system qualifies as second-order cognitive under this definition. (Qualification added during 5-model meta-test, 27 March 2026 — the original categorical assertion preceded the necessary empirical evidence.)

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
| Composite Y > individual max Y + z_conf·σ̂ | Bench test, all conditions | Y_composite ≤ max(Y_i) + 1.96·σ̂(Y) on majority of tasks |
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

## 1.3 Embedding-Based Similarity

### Motivation

The original CDSFL similarity function uses unigram/bigram Jaccard distance. This works for findings with substantial lexical overlap (same words, same phrasing) but fails for semantically equivalent findings expressed differently. "Buffer overflow in network parser" and "Memory corruption in packet handler" describe the same class of vulnerability but share almost no words. Jaccard scores them as dissimilar; a human reads them as the same finding.

Convergence detection depends on correctly identifying when a finding is novel versus when it repeats what a previous round already found. If the similarity function cannot recognise semantic equivalence, kappa_set will undercount novelty (treating rephrased findings as new) and the system will fail to converge even when no genuinely new findings are being produced.

### Formal Definition

The similarity function s(f1, f2) computes a bounded similarity score between two findings using a convex combination of content similarity and flaw-class matching:

> **s(f1, f2) = (1 - β) · content_sim(f1, f2) + β · b_class(f1, f2)**

where:
- **content_sim** is the content similarity backend (embedding or lexical)
- **β = 0.2** is the class bonus weight
- **b_class = CLASS_BONUS if f1.flaw_class == f2.flaw_class, else 0**
- **CLASS_BONUS = 0.3**

**Embedding backend** (primary, when sentence-transformers available):
> content_sim = (cos(emb(f1), emb(f2)) + 1) / 2

where emb(f) is the sentence embedding from all-MiniLM-L6-v2, and the cosine similarity is mapped from [-1, 1] to [0, 1].

**Lexical backend** (fallback):
> content_sim = 0.6 · J_unigram(f1, f2) + 0.4 · J_bigram(f1, f2)

where J is the Jaccard index over tokenised, stopword-filtered descriptions.

### Boundedness

Both backends produce content_sim ∈ [0, 1]. The class bonus b_class ∈ {0, 0.3}. Since β = 0.2:

> s ∈ [(1-0.2)·0 + 0.2·0, (1-0.2)·1 + 0.2·0.3] = [0, 0.86]

The maximum possible similarity is 0.86 (perfect content match + class match). This is by design: no two findings should be scored as identical (1.0) since they may differ in severity, proposed fix, or context even when describing the same flaw.

(SymPy verified: bounded convex combination stays in [0, 1] for all valid inputs. Implementation: `bench/dm/_similarity.py`. April 2026.)

### Confound

**Embedding bias.** Sentence-transformer models are trained on general English corpora, not security finding descriptions. The embedding space may not distinguish security-relevant differences (e.g., "race condition in authentication" vs "race condition in logging" may score as highly similar despite very different severity implications). Mitigation: the flaw-class bonus provides a domain-aware signal independent of embedding quality, and tau_sim thresholds are calibrated empirically per experiment.

---

## 1.4 Continuous Suppression

### Motivation

When a finding is highly similar to many prior findings, it contributes less new information. The naive approach is binary: above a similarity threshold, a finding is "duplicate" and ignored; below, it counts fully. This creates a cliff effect at the threshold boundary and makes kappa_set sensitive to small perturbations in similarity scores.

Continuous suppression replaces the binary duplicate/novel decision with a smooth weight function that gradually reduces a finding's contribution as it becomes more similar to what has already been found.

### Formal Definition

For a finding f with prior cumulative findings G, the suppression weight is:

> **w(f) = max(exp(-λ_s · Σ_{g ∈ TopK(f, G)} sim(f, g)), w_floor)**

where:
- **TopK(f, G)** is the set of k findings in G most similar to f
- **λ_s = 1.5** is the suppression decay rate
- **w_floor = 0.05** is the minimum weight (prevents total silencing)
- **k = 3** (default suppression_k)

The weight enters kappa_set via the numerator only:

> **kappa_set(r) = 1 - Σ(w_c · Sev_novel_c) / (Σ Sev_cumulative + ε)**

where w_c = max(w(m) for m in members_c) is the per-class weight (conservative: least suppressed member determines class weight). The denominator uses raw, unweighted severity.

### Permutation Invariance

The predecessor-product approach (w(f) = Π_{all priors} (1 - sim)) is order-dependent: processing findings in different orders produces different weights. This violates the expectation that the same set of findings should produce the same convergence assessment regardless of arrival order.

Top-k selection is permutation-invariant by construction: sorting similarities and taking the top k does not depend on the order in which findings were processed. This was the critical fix for Error 2 (12 April 2026).

### Corroboration Collapse Prevention

**CRITICAL CONSTRAINT:** w(f) must NEVER enter q_eff in the Bayesian update. The effective detection probability q = η · d · p in the R_k(i) recursive equation must use raw, unsuppressed values.

If suppression weights entered q_eff, they would reduce the effective detection probability for corroborated findings — the exact opposite of what corroboration should do. Findings confirmed by multiple sources should strengthen the Bayesian update, not weaken it. This was Error 1 (12 April 2026), which caused a 113x residual risk overestimate in testing.

Suppression weights apply to: kappa_set numerator (convergence metric), report ordering (triage priority), finding weight in summary statistics. They do NOT apply to: q_eff, R_k(i) recursive update, Bayesian posterior computation, or the kappa_set denominator.

(SymPy verified: w ∈ [w_floor, 1], kappa_set ∈ [0, 1] with weighted numerator. Permutation invariance verified by test. Implementation: `bench/dm/_convergence.py`. April 2026.)

### Confound

**Threshold sensitivity.** The suppression parameters (λ_s, w_floor, k) interact with tau_sim to determine effective novelty detection. If λ_s is too high, even mildly similar findings are fully suppressed, preventing genuine variants from being counted. If too low, repetitive findings inflate the novelty count. These parameters require empirical calibration per domain.

---

## 1.5 Persistent Memory and Blended Prior

### Motivation

Each CDSFL experiment starts with a uniform prior for flaw rates. But after running 30+ experiments, we have substantial empirical data about which flaw classes are common and which are rare. A buffer overflow in a well-tested parser module is much less likely than a boundary condition error in newly written configuration parsing. Ignoring this historical knowledge wastes the first rounds of each experiment rediscovering what prior experiments already established.

Persistent memory allows the system to start with calibrated priors based on historical confirmation rates, while maintaining the ability to detect when the historical pattern no longer applies (drift detection).

### Formal Definition

**Per-flaw-class memory** stores decayed confirmation rates:

> **π_mem(k) = (c_k + α_0) / (c_k + r_k + α_0 + β_0)**

where c_k and r_k are the exponentially decayed confirmed and rejected counts for flaw class k, and α_0 = β_0 = 0.5 are Jeffreys prior pseudocounts (Beta-Binomial smoothing).

**Exponential decay** ensures recent experiments weigh more:

> After each new experiment, existing counts are multiplied by exp(-λ_decay) before adding new observations.

**Blended prior:**

> **π(k) = (1 - ρ) · π_base(k) + ρ · π_mem(k)**

where ρ ∈ [0, 1] is the memory blending weight (default 0.2) and π_base is the domain-default prior.

### Drift Detection

Historical patterns may become stale if the codebase changes significantly. CUSUM (Cumulative Sum) drift detection monitors whether incoming flaw rates diverge from memory predictions:

> **S_pos(t) = max(0, S_pos(t-1) + (observed_rate - π_mem))**
> **S_neg(t) = min(0, S_neg(t-1) + (observed_rate - π_mem))**

Drift is flagged when |S_pos| or |S_neg| exceeds the drift threshold (default 2.0). When drift is detected, the blended prior should be treated with reduced confidence.

### Advisory-Only Constraint

Memory is advisory: it informs the initial prior but cannot override pipeline verdicts. A finding confirmed by tool verification (SymPy, z3, test suite) is confirmed regardless of what memory says about its flaw class frequency. Memory can suggest "this flaw class is rare, so the prior should be low" — it cannot say "this finding is false because flaw class 3 is historically rare."

### File-Hash Invalidation

Memory is grounded to the source files it was built from. If the source code changes significantly (detected via SHA-256 hash of source files), the memory is invalidated and the system starts fresh. This prevents memory built on one codebase from being applied to a different one.

(SymPy verified: π_blended ∈ [0, 1], decay preserves positivity, Beta-Binomial is a proper distribution. Implementation: `bench/dm/_memory.py`. April 2026.)

### Confound

**Memory poisoning.** If a prior experiment produced incorrect results (e.g., due to a pipeline bug), those results are now encoded in memory and will bias future experiments. Mitigation: exponential decay naturally reduces the influence of old experiments, and drift detection catches cases where memory predictions diverge from observed reality. Additionally, the advisory-only constraint ensures memory cannot force incorrect verdicts.

**Single-operator validation.** All experiments to date have been conducted by one operator. Memory may encode operator-specific biases (e.g., systematically investigating certain flaw classes more thoroughly). This limitation will only be addressable when multiple independent operators run CDSFL experiments.

---

## 7.13 Convergence Metrics: kappa_set, kappa_rate, kappa_adopt

### Motivation

Convergence detection answers: "Have we found everything there is to find, or are new findings still emerging?" This is critical for round progression — continuing to run rounds after convergence wastes resources, while stopping too early misses genuine flaws.

A single convergence metric is fragile. If it measures only novelty (are findings new?), it misses the case where findings are new but trivial. If it measures only rate (are findings slowing down?), it misses the case where a burst of high-severity findings arrives late. Three independent metrics, combined conservatively, provide robust convergence detection.

### Formal Definitions

**kappa_set — Set-theoretic stability (severity-weighted novelty):**

> **κ_set(r) = 1 - Σ(w_c · Sev_novel_c) / (Σ Sev_cum_c + ε)**

Measures how much of the current round's severity comes from genuinely novel findings (those not equivalent to any prior finding under the ≈ relation). Higher = more converged. When all new findings are duplicates of previous ones, κ_set = 1.

**kappa_rate — Rate-based stability (Duane connection):**

> **κ_rate(r) = 1 - λ_hat(r) / (λ_hat(1) + ε)**

where λ_hat(r) = |F^(r)| / Δt_r is the instantaneous finding rate. Measures whether the rate of new finding discovery is decreasing relative to the initial rate. Connected to the Duane reliability growth model: if findings follow a power law, κ_rate estimates the growth parameter. Clamped to [-1, 1].

**kappa_adopt — Adoption stabilisation:**

> **κ_adopt(r) = clamp(1 - Δ_r, 0, 1)**

where Δ_r is the adoption delta from the existing schema. Measures whether fixes are stabilising or still producing churn. Clamped to [0, 1].

**Combined metric:**

> **κ(r) = min(κ_set(r), max(0, κ_rate(r)), κ_adopt(r))**

Conservative combination: convergence requires ALL three metrics to indicate stability. The max(0, ·) on κ_rate prevents negative rate metrics (divergence) from being the bottleneck — divergence is handled by the veto mechanism instead.

**Convergence predicate:**

> **converged(r) iff κ(r) ≥ τ_κ AND r ≥ r_min AND NOT veto(r)**

where τ_κ = 0.95 (the convergence threshold, SEPARATE from γ the Duane parameter), r_min = 2 (minimum rounds), and veto(r) fires when any novel finding has aggregated severity ≥ η_veto = 0.9 (a single high-severity discovery blocks convergence regardless of the metrics).

### Relationship to Duane Model

The estimated gamma parameter:

> **γ_hat = 1 - (log(|F^(≤r)|) - log(|F^(≤1)|)) / log(r)**

is a DIAGNOSTIC, not the convergence threshold (founder decision §9.2). It estimates reliability growth rate but is not directly compared against τ_κ. This separation prevents the system from declaring convergence based on a statistical trend when individual metrics disagree.

(Implementation: `bench/dm/_convergence.py`. SymPy + z3 verified: κ ∈ [0, 1], veto is a strict gate, τ_κ separation preserves reduction properties.)

---

## 8.7 Ouroboros Cell (O1)

### Motivation

The immune pipeline has six cell types that verify individual findings. But no cell watches the pipeline itself. Systemic issues — correlated false positives across cells, declining verification quality over rounds, emergent biases from tool monoculture — are invisible to cells that only see their own inputs and outputs.

The ouroboros cell (O1) is a self-referential observer: it watches the pipeline's aggregate behaviour and flags patterns that no individual cell could detect.

### Operating Modes

**Macrophage mode** (active hunting): Scans pipeline output for anomalies.
- Verdict clustering: >80% of verdicts are the same type → possible systemic bias
- Severity concentration: variance in confidence scores < 0.01 → uniform over-confidence
- Timing spikes: any stage >3× median duration → possible bottleneck or hang

**Microglia mode** (self-referential): Monitors pipeline health assumptions.
- Tool monoculture: all verdicts from single tool → verification diversity compromised
- Persistent anomalies: same anomaly type in 3+ consecutive rounds → systemic issue not addressed
- Tool-claim mismatch: mathematical claims present but no SymPy/z3 verdicts → verification not grounded

### Shadow Mode Architecture

For Exp 39, O1 operates exclusively in shadow mode. It observes and logs but NEVER modifies pipeline state or verdicts. This is not a soft guideline — it is a structural guarantee enforced by the `pipeline_modified = False` invariant on every OuroborosSummary.

Promotion to active mode requires:
1. Precision threshold: O1's anomaly flags must be confirmed by HIL at >70% rate
2. Novelty yield: O1 must identify anomalies that no other cell flagged
3. Explicit HIL approval: the founder must review shadow-mode data and approve promotion

### Evidence Architecture (L1/L2/L3)

O1 observations are signed into the VerificationChain:
- **L1 (signing/provenance):** Each observation is recorded with timestamp, cell mode, and content hash. This proves the observation was made at a specific time. Cryptographic signing establishes provenance, not correctness.
- **L2 (correctness/falsification):** Whether the observation is correct (the anomaly is real) is determined by independent verification — tool output, cross-round comparison, or manual inspection. L1 signing does not imply L2 correctness.
- **L3 (HIL arbitration):** The human-in-the-loop reviews flagged anomalies and decides whether to act on them. L1 provenance and L2 evidence inform this decision; they do not replace it.

This three-level separation addresses the category error identified by Gemini 3.1 Pro (12 April 2026): signing proves when and by whom an observation was made (provenance), not that the observation is true (correctness).

### Audit Logging

O1 uses exception-based audit logging: only anomalies are surfaced to HIL, not routine observations. This prevents cognitive overload at scale (>50 findings/round), which was identified as a genuine risk by the Gemini confer (12 April 2026).

(Implementation: `bench/ouroboros_cell.py`. Shadow guarantee verified by test. April 2026.)

---

## 9. Confounds and Threats to Validity

This section documents known limitations, errors caught during development, and potential failure modes. The purpose is not to undermine confidence in the model but to make its boundaries explicit so that other researchers can evaluate, reproduce, and extend the work.

### 9.1 Critical Errors Caught During Development

Three critical errors were identified and corrected during the 12 April 2026 development session. All were caught by confer rounds (multi-model peer review) before they entered production.

**Error 1: Corroboration Collapse.** Suppression weights w(f) were initially fed into q_eff in the Bayesian update. This caused a 113x overestimate of residual risk for corroborated findings. The fix: w(f) applies to kappa_set numerator and report ordering ONLY, never to q_eff. Root cause: conflation of "finding weight in convergence metric" with "finding weight in Bayesian update" — these serve different purposes.

**Error 2: Order Dependence.** The predecessor-product suppression formula w(f) = Π(1 - sim_i) produced different weights depending on the order findings were processed. The fix: top-k exponential suppression, which is permutation-invariant by construction. Root cause: sequential processing assumption embedded in the formula design.

**Error 3: kappa Overflow.** Applying suppression weights to both numerator and denominator of kappa_set caused the metric to leave [0, 1]. The fix: numerator-only weighting, with the denominator always using raw unweighted severity. Root cause: insufficient SymPy verification of boundary conditions before implementation.

### 9.2 Embedding Bias

Sentence-transformer embeddings are trained on general English, not security finding descriptions. The model may:
- Score semantically different security findings as similar (high false-duplicate rate)
- Score genuinely similar findings as different when they use domain-specific terminology
- Produce systematically different similarity distributions for different domains

Mitigation: empirical calibration of tau_sim per experiment, flaw-class bonus as domain signal, Jaccard fallback when embedding quality is suspect.

### 9.3 Memory Poisoning

Persistent memory accumulates confirmation rates from prior experiments. If a prior experiment was conducted incorrectly (pipeline bug, misconfigured tools, contaminated prompts), those results are now encoded as "historical truth." Mitigation: exponential decay, drift detection, advisory-only constraint, file-hash invalidation.

### 9.4 Single-Operator Validation

All experiments to date have been conducted by one operator (the founder) on one codebase (the CDSFL implementation itself). This means:
- All priors reflect one operator's domain expertise and biases
- All tool configurations reflect one operator's choices
- Memory is calibrated to one codebase's flaw distribution
- The pipeline has never been independently replicated

This is the most significant threat to external validity. The mathematical model is general; the empirical calibration is not. Independent replication by other operators on other codebases is required before the model's parameters can be considered validated.

### 9.5 Statistical Power

With K ≤ 5 models and R ≤ 15 rounds per experiment, the sample sizes for per-model statistics are small. This means:
- Capability fingerprint estimates have wide confidence intervals
- Convergence detection may be premature with aggressive thresholds
- Per-flaw-class statistics are sparse for rare flaw classes

The model is designed to be conservative (min-combination for kappa, severity veto, FFAFP constraints), which trades statistical power for safety: it is more likely to declare "not converged" than to miss a genuine flaw.

### 9.6 Falsification Rate Without Structural Enforcement

Without FFAFP, 0–13% of model-submitted findings survived independent falsification in Experiments 12–15. This means 87–100% of submitted findings were false or unverifiable. The improvement to 60–85% after FFAFP enforcement demonstrates that the constraint set works, but also that even with enforcement, 15–40% of findings still fail verification. The residual failure rate may reflect:
- Genuine difficulty of the verification task (some claims are hard to verify mechanically)
- Incomplete tool coverage (claims requiring tools not in the envelope)
- Model hallucination that passes format checks but fails substance checks

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
| d_weight(i,k) | Parameter space overlap component of d_ik | This appendix §2 |
| d_config(i,k) | Operational inference overlap component of d_ik | This appendix §2 |
| o_ik | Overlap of reviewer i with priors, flaw class k | This appendix §2 |
| δ_ij | NMI-based diversity between models i and j | This appendix §2 |
| w_k | Consequence weight, flaw class k | White paper §2.2 |
| s_k | Expected harm/severity, flaw class k | This appendix §4 |
| π_risk,k | Prior flaw rate, flaw class k | This appendix §1 |
| m_k | Miss probability, flaw class k | This appendix §1 |
| Ŝ_{H,k} | Seeded detection sensitivity for class k | This appendix §1 |
| A | Anchor state (A0–A3) | White paper §2.2 |
| ρ | Inter-architecture correlation | White paper Part XIII |
| ψ_ij | Ising pairwise correlation coupling | This appendix §0.1 |
| Z | Ising partition function | This appendix §0.1 |
| G_n | Combined machine-HIL detection | White paper §7.1, this appendix §6 |
| C_M(k) | Machine cumulative detection for class k | This appendix §6 |
| C_H(k) | HIL cumulative detection for class k | This appendix §6 |
| ρ_MH | Cross-correlation (cognitive priming) | White paper §7.1, this appendix §6 |
| IG_HIL | Hint framing penalty (KL divergence) | This appendix §6 |
| E | HIL domain expertise level | White paper §7.1, this appendix §6 |
| M | HIL methodology formality | White paper §7.1, this appendix §6 |
| α | Expertise floor coefficient | This appendix §6 |
| β_pen | Asymmetric calibration overconfidence penalty | This appendix §6 |
| λ_s | Domain variable sensitivity | White paper §7.1, this appendix §6 |
| V_s | Domain-specific variable (pluggable) | White paper §7.1, this appendix §6 |
| E*(t) | Bayesian posterior expertise estimate | White paper §7.1, this appendix §6 |
| κ | HIL calibration metric | This appendix §6 |
| λ(t) | Duane NHPP intensity function | This appendix §7.1 |
| ν | Re-injection rate (fix introduces new flaw) | This appendix §1.1, §7.1 |
| β | Duane shape parameter | This appendix §7.1 |
| η (§1.1) | Novelty of finding (new content vs restated) | This appendix §1.1 |
| η (§7.1) | Duane scale parameter | This appendix §7.1 |
| σ (§1.1) | Fix efficacy (probability fix resolves flaw) | This appendix §1.1 |
| R_det | Post-detection residual risk (Phase 1 output) | This appendix §1.1 |
| R_base | Post-resolution residual risk (Phase 2 output) | This appendix §1.1 |
| ν* | Break-even re-injection rate | This appendix §1.1 |
| γ | Convergence parameter (1 − β) | This appendix §7.1 |
| τ_defer | Synthesis deferral penalty | This appendix §2 |
| H(x) | Abstraction Index (finding depth) | This appendix §7.2 |
| F(x) | Formality component of H(x) | This appendix §7.2 |
| c_F1, c_F2 | Formality coefficients (verifiable, HARD) | This appendix §7.2 |
| ρ_info(x) | Information density component of H(x) | This appendix §7.2 |
| G(x) | Generalisation scope component of H(x) | This appendix §7.2 |
| c_G1, c_G2 | Generalisation coefficients (cross-module, ref depth) | This appendix §7.2 |
| Y(t) | Total Cognitive Yield | This appendix §7.3 |
| H̄(t) | Mean Abstraction Index at time t | This appendix §7.3 |
| V̂(t,T) | Online Total Value Estimator | This appendix §7.4 |
| k_decay(t) | Local exponential decay rate of v_w(t) | This appendix §7.4 |
| Δ̄ | Mean derived scalar Adoption Delta across model pairs | This appendix §7.5 |
| z_conf | Confidence multiplier for emergence threshold | This appendix §8.2 |
| σ̂(Y) | Bootstrap standard error of Y estimates | This appendix §8.2 |
| O_A | Objective Alignment (sycophancy detection) | This appendix §7.5 |
| F_conv | Newly converged finding set | This appendix §7.5 |
| S_sync | Composite sycophancy score (behaviour-based) | This appendix §7.5 |
| S_sync^emp | Empirically-anchored sycophancy score (NMI + Ŝ_H) | This appendix §7.5 |
| w(y) | Null-vector yield weighting | This appendix §7.5 |
| Δ_adopt(A→B) | Adoption rate (fraction of novel partner findings incorporated) | This appendix §7.6 |
| Δ_drop(A→B) | Drop rate (fraction of unique own findings abandoned) | This appendix §7.6 |
| Δ̄(A→B) | Derived scalar adoption delta (mean of rates) | This appendix §7.6 |
| M_suppress | Mutual suppression metric | This appendix §7.5 |
| Sev(f) | Per-finding severity score | This appendix §7.7 |
| S_v | Multi-verifier Bayesian severity | This appendix §7.8 |
| Λ_total | Bayesian log-odds total | This appendix §7.8 |
| Λ_prior | Bayesian log-odds prior | This appendix §7.8 |
| o_i | Determinate verifier output (binary) | This appendix §7.8 |
| D_det | Determinate verifier set | This appendix §7.8 |
| (D_decay,v̄,A,C) | Capability fingerprint | This appendix §7.9 |
| selected(f) | Manager selection predicate | This appendix §7.11 |
| D_n | Defect count at FFF round n | This appendix §7.12 |
| D* | FFF fixed-point defect count | This appendix §7.12 |
| σ | FFF scope expansion ratio | This appendix §7.12 |
| n_{1/2} | FFF convergence half-life | This appendix §7.12 |
| Y_composite | Composite system Total Cognitive Yield | This appendix §8.2 |
| s(f1, f2) | Finding similarity (embedding or lexical) | This appendix §1.3 |
| β | Class bonus weight (similarity) | This appendix §1.3 |
| CLASS_BONUS | Flaw-class match bonus | This appendix §1.3 |
| w(f) | Suppression weight | This appendix §1.4 |
| λ_s | Suppression decay rate | This appendix §1.4 |
| w_floor | Minimum suppression weight | This appendix §1.4 |
| TopK(f, G) | k most similar prior findings | This appendix §1.4 |
| π_mem | Memory-based prior (Beta-Binomial) | This appendix §1.5 |
| ρ_memory | Memory blending weight | This appendix §1.5 |
| S_pos, S_neg | CUSUM drift statistics | This appendix §1.5 |
| κ_set | Set-theoretic convergence stability | This appendix §7.13 |
| κ_rate | Rate-based convergence stability | This appendix §7.13 |
| κ_adopt | Adoption convergence stability | This appendix §7.13 |
| κ(r) | Combined convergence metric | This appendix §7.13 |
| τ_κ | Convergence threshold | This appendix §7.13 |
| η_veto | Severity veto threshold | This appendix §7.13 |
| C_FFAFP | FFAFP admissibility constraint set | This appendix §1.2 |

---

## Attribution

The extensions in §1–6 were developed during the multi-architecture collaborative review process described in the white paper (Part XI). The cognitive measurement framework (§7) and emergence formalisations (§8) were developed through confer rounds between Claude Opus 4.6 and Gemini 3.1 Pro (27 March 2026), with all formulas computationally verified using SymPy and Wolfram Alpha. The core models were validated as mathematically sound within their stated assumptions; these extensions were identified as the most direct upgrade path for the next empirical phase. A subsequent 3-model confer (Claude Opus 4.6, Codex GPT-5.4, Gemini 3.1 Pro, 27 March 2026) resolved 5 deferred design decisions, added the manager selection function (§7.11) and mutual suppression metric, and rejected 2 proposed additions (anti-parroting and contribution discount) as premature for formal inclusion. An 8-round mathematical coherence audit (31 March 2026) involving 6 models (Claude Opus 4.6, CC2, Codex GPT-5.4, ChatGPT 5.4, DeepSeek V3.2, Gemini 3.1 Pro) with 39 independent SymPy checks (all passing) produced: §0.1 corroboration branching with normalised Ising/Boltzmann model, full namespace refactor (17 collisions resolved), synthesis deferral operator τ_defer, null-vector guards, separability axioms, ρ domain constraint, seeded defect injection, NMI diversity estimator, empirically-anchored sycophancy trigger, error re-injection rate, HIL framing penalty, and substrate ceiling boundary. The unified self-assessment equation (§1.1, 8 April 2026) was derived during the Exp 37 build. The recursive form was verified by SymPy and Wolfram Alpha. The three-phase extension (η, σ, ν) was confer-verified by Gemini 3.1 Pro and Codex GPT-5.4 — both falsified the original σ placement and corrected it (confer logs: `bench/logs/confer_unified_equation/`). A 25-check internal consistency audit (SymPy, Wolfram, z3) confirmed all 5 identified gaps and disputed two prior claims. The operational form is specified in the CDSFL operational directive §3 and first deployed in Experiment 37 (9 April 2026). The FFAFP calibration protocol (§1.2), embedding similarity (§1.3), continuous suppression (§1.4), persistent memory (§1.5), convergence metrics (§7.13), ouroboros cell (§8.7), and confounds section (§9) were formalised on 12 April 2026 during the Exp 39 preparation session. Three critical errors (corroboration collapse, order dependence, kappa overflow) were caught and corrected through multi-model confer rounds. All extensions were SymPy-verified and are implemented in the `bench/dm/` module.

---

*This appendix is a working mathematical supplement. Its extensions are precisely stated so they can be tested. Any extension that fails to improve predictive accuracy over the simpler model it extends should be discarded. The methodology does not depend on any specific equation — it depends on the principle that corroboration is earned through survived falsification.*
