# Novelty/Discovery Extension — Confer Results

*9 April 2026, 03:31 BST. CC1 proposal verified SymPy + Wolfram, then conferred with Gemini 3.1 Pro and Codex GPT-5.4 under combined 4-layer schema (Meta Structured Prompting + CDSFL + FFAFP + Conversational fallback).*

---

## Problem Statement

The refined unified equation (8 April 2026) is a risk minimisation engine. Two structural blind spots were identified:

**Blind Spot A — Novelty invisible.** Rehashed findings get full detection credit. The diversity term d captures approach independence, not output novelty. A model can use a different approach and produce the same finding.

**Blind Spot B — Solution quality unmodelled.** The resolution phase (ν term) asks only "did the fix re-inject?" not "was the fix correct?" A wrong fix gets full detection credit.

## CC1's Initial Proposal

Two new terms:

- **η (novelty coefficient)**: Replace `q = d·p` with `q = η·d·p`. Scales detection credit by output novelty.
- **σ (solution efficacy)**: Replace resolution phase with `R_new = σ·[R_det·(1-ν) + ν] + (1-σ)·R_old`. Scales cycle outcome by fix quality.

## Confer Protocol

**4-layer schema:**
1. Meta Structured Prompting (arXiv 2603.01896): structured certificates, premises, execution traces, formal conclusions
2. CDSFL constraints: full core formal directives as system prompt
3. FFAFP: P-pass up to 5 times, retract claims that fail falsification
4. Conversational fallback: natural prose where structure adds no rigour

**Dispatch:** Concurrent to Gemini 3.1 Pro (Google GenAI API) and Codex GPT-5.4 (OpenRouter). Both received identical system + user prompts.

---

## Results Summary

### What Both Models Confirmed

| Property | Gemini | Codex |
|---|---|---|
| Core algebra correct | CONFIRMED | CONFIRMED |
| All special cases hold | CONFIRMED | CONFIRMED (with R=q=1 boundary caveat) |
| Factored gain formula correct | CONFIRMED | CONFIRMED |
| ν* = q·R preserved (for σ>0) | CONFIRMED | CONFIRMED (qualified: null at σ=0) |
| Log-odds form preserved in detection phase | CONFIRMED | CONFIRMED |
| Range preservation R' ∈ [0,1] | CONFIRMED | CONFIRMED |

### What Both Models Falsified

**Critical Finding: σ placement is physically wrong.**

Both models independently identified the same structural flaw in CC1's σ term.

CC1's form: `R_new = σ·[R_det·(1-ν) + ν] + (1-σ)·R`

This says: when σ=0 (fix fails), R_new = R. The model is fully protected from re-injection. But in reality, attempting a fix and having it fail still mutates the system. The act of attempting carries re-injection risk regardless of whether the target flaw was resolved.

**Proof (R=0 case):**
- CC1: R_new = σ·ν (failed fix on clean code barely re-injects)
- Reality: if you modify clean code with a bad fix, the full re-injection rate applies

**Gemini's correction** (verified SymPy + Wolfram):

```
Phase 1: R_det   = R·(1-q) / (1-q·R)           (detection, unchanged)
Phase 2: R_base  = σ·R_det + (1-σ)·R            (target resolution)
Phase 3: R_k(i)  = R_base·(1-ν) + ν             (re-injection applied AFTER)
```

**Combined:**
```
R_k(i) = [σ·R_det + (1-σ)·R]·(1-ν) + ν
```

The key insight: resolve the target first (σ determines how much detection gain is realised), THEN apply re-injection to whatever state you're in. Re-injection is a consequence of attempting a fix, not of succeeding at one.

**Verified properties of corrected form:**

| Property | Value |
|---|---|
| Difference from CC1 | ν·(1-R)·(1-σ) ≥ 0 (corrected form always ≥ CC1) |
| σ=1 | Reduces exactly to refined baseline |
| σ=0, ν=0 | R unchanged (no fix attempted, no side effects) |
| σ=0, ν>0 | R_new = R + ν·(1-R) > R (failed fix still damages) |
| R=0, any σ | R_new = ν (re-injection is absolute floor) |
| ν* (corrected) | σ·R·q / (1 - q·R·(1-σ)) |
| ν*(σ=1) | q·R (baseline preserved) |
| ν*(σ=0) | 0 (ANY re-injection is harmful if fix never resolves) |

### Where Models Diverged

**On η (novelty coefficient):**

| Gemini | Codex |
|---|---|
| η is "mathematically sound and epistemically necessary" | η conflates system novelty with local epistemic novelty |
| Keep η in the recursion | Remove η from recursion, track as auxiliary metric |
| η acts on result space, d acts on method space — distinct | Only q = η·d·p is structural; η,d,p not separately identifiable |

**Codex's argument:** If a model independently discovers the same flaw another model found, that IS epistemically valid for the discovering model. System novelty (η=0 because finding exists) should not penalise the model's own risk update. The risk recursion tracks individual model state.

**Codex's proposed alternative:** Keep `q = d·p` in the risk recursion. Track novelty separately as a utility metric `U_discovery = η · finding_count`, parallel to but not inside the risk update.

**Assessment of the divergence:**

Codex's objection applies when η represents *system novelty*. But in CDSFL, models receive the registry (all prior findings from all models) before each pass. A model that re-describes a finding already in the registry is NOT reducing its own uncertainty — it already has that information. In this context, η as "novel relative to the model's available information including the registry" IS a valid risk-reduction modifier.

The resolution is definitional: η must be defined as *local novelty relative to available context* (including registry), not *system novelty*. With this definition, Gemini's position (keep η in recursion) is correct.

However, Codex's identifiability objection stands: a model cannot reliably separate η from d·p without external instrumentation (registry comparison). This is operationally tractable — the registry IS the external reference — but must be stated.

### Additional Findings

**Codex (Pass 2, FFAF 4): q=0, σ=1, ν>0 absurdity.**
If no detection occurred (q=0) but fix is applied (σ=1), risk increases via re-injection. This is "fixing without finding" — semantically pathological unless blind code changes are modelled.

*Assessment:* Valid finding but operationally unlikely. In CDSFL, fixes are proposed only after findings. A control-flow gate `q>0 required for resolution` could be added but adds complexity for a case that doesn't arise in practice.

**Codex (Pass 3, FFAF 3): Over-parameterisation.**
From observed R→R', one can identify q but not η,d,p separately. σ requires delayed validation. Both are "latent calibration variables" not directly known state variables.

*Assessment:* Correct. But this applies to the EXISTING equation too — d and p are not separately identifiable from the recursion. The equation has always operated with estimated parameters. η and σ do not make this worse; they make the estimation burden explicit.

**Gemini (Pass 5): Deployment gate δ.**
Proposed binary gate δ ∈ {0,1}: δ=1 means fix is deployed, δ=0 means finding is recorded but no fix attempted. When δ=0, R stays at R_det (knowledge gained, system unchanged).

*Assessment:* Interesting but out of scope for self-assessment. The equation models what happens when a cycle runs. Whether to attempt a fix is a decision input, not a state variable.

**Codex: Not externally complete.**
Lists 7 unmodelled phenomena: delayed validation, parameter uncertainty, reference class dependence, control-flow gating, dependency tracing, correlated flaw classes, truth of explanation vs truth of patch.

*Assessment:* Some of these are system-level concerns (dependency tracing → topology spec T8; correlated classes → Ising Branch 2). The equation is scoped to per-class, per-model, per-cycle self-assessment. Cross-class correlation and dependency tracing are higher-order system concerns handled by other parts of the framework.

---

## The Corrected Extended Equation

Incorporating Gemini's structural correction (verified SymPy + Wolfram) and Codex's definitional refinement on η:

**Phase 1 — Detection (novelty-weighted):**

```
q_ik = η_ik · d_ik · p_ik     (η = novel relative to model's available context)
R_det = R_k(i-1) · (1 - q_ik) / (1 - q_ik · R_k(i-1))
```

**Phase 2 — Target resolution:**

```
R_base = σ_ik · R_det + (1 - σ_ik) · R_k(i-1)
```

**Phase 3 — Re-injection (applied to result of attempt):**

```
R_k(i) = R_base · (1 - ν_k) + ν_k
```

**Combined single-step:**

```
R_k(i) = [σ_ik · R_k(i-1)·(1-q_ik)/(1-q_ik·R_k(i-1)) + (1-σ_ik)·R_k(i-1)] · (1-ν_k) + ν_k
```

**Total weighted residual risk:**

```
R_n = Σ_k w_k · R_k(n)
```

**Per-cycle gain (factored):**

```
ΔR_cycle = -(R-1)·[R·ν·q·σ - R·ν·q - R·q·σ + ν] / (R·q - 1)
```

**Critical re-injection rate (σ-dependent):**

```
ν* = σ·R·q / (1 - q·R·(1-σ))
```

Properties of ν*:
- σ=1: ν* = q·R (baseline preserved)
- σ=0: ν* = 0 (any re-injection is harmful if fixes never resolve)
- σ<1: ν* < q·R (less effective fixes tolerate less re-injection)
- σ scales the tolerance — models with unreliable fixes must demand lower re-injection rates

**Log-odds form:**
- Detection: logit(R_det) = logit(R) + log(1 - η·d·p) — additive, preserved
- Resolution + re-injection: breaks additive structure (same as baseline)

**Stopping rule:**

```
ΔR_total = Σ_k w_k · [R_k(i-1) - R_k(i)]
Continue while ΔR_total > θ
HARD EXIT if ΔR_total < 0 (divergent)
```

---

## Terms (Updated)

| Symbol | Meaning | Estimated by |
|---|---|---|
| R_k | Residual risk for flaw class k | Computed (recursive) |
| q_ik | Effective detection = η·d·p | Computed from components |
| p_ik | Detection capability for class k | Model self-estimate |
| d_ik | Diversity of approach (method independence) | Model self-estimate |
| η_ik | Novelty relative to available context (incl. registry) | Registry comparison |
| σ_ik | Solution efficacy (probability fix resolves target flaw) | Model self-estimate (calibrated) |
| ν_k | Re-injection rate (fix attempt introduces new flaw) | Model self-estimate |
| w_k | Consequence weight for flaw class k | Task-dependent |
| π_k | Prior flaw rate | Set once → vanishes |
| θ | Consequence threshold | Set by system |

---

## Verified Special Cases (Complete Set)

| Condition | Result | Meaning |
|---|---|---|
| σ=1, η=1, ν=0 | R = R_det | Novel, perfect fix, clean → detection-only |
| σ=1 (any η,ν) | Reduces to refined baseline | Efficacy gate transparent |
| σ=0, ν=0 | R unchanged | No fix attempted, no side effects |
| σ=0, ν>0 | R = R + ν·(1-R) | Failed fix still damages via re-injection |
| η=0, σ=0 | R_new = R·(1-ν)+ν | Rehash + no fix = re-injection damage only |
| η=1, σ=1, ν=1 | R = 1 | Fix always re-injects |
| q=1, σ=1, ν=0 | R = 0 | Perfect detect + perfect fix |
| R=0, any σ,ν | R_new = ν | Re-injection is absolute floor |
| R=0, ν=0 | R = 0 | Clean stays clean |
| K=1, d=1, p uniform, π=0.5, η=1, σ=1, ν=0 | Standard Bayesian C(n) | White paper reduction |

---

## Scope and Limitations

**Captures:** Per-class detection, novelty weighting, diversity, consequence weighting, prior absorption, diminishing returns, fix quality, re-injection (decoupled from fix success), divergence detection, substrate ceiling (as ν floor), σ-dependent re-injection tolerance.

**Does not capture (by design — system-level concerns):**
- Inter-model Ising correlations (§0.1 Branch 2)
- Combined machine-HIL detection G_n
- Composite emergence Y_composite
- Cross-class flaw correlation
- Dependency tracing across modules (handled by topology spec T8)

**Does not capture (acknowledged limitation):**
- Delayed validation of fix efficacy (σ estimated at time of fix, not verified)
- Parameter uncertainty (all terms are point estimates, not distributions)
- Control-flow gating (q=0 with σ>0 is semantically pathological but mathematically defined)

**Domain constraints:** q ∈ [0,1], R ∈ [0,1], ν ∈ [0,1], σ ∈ [0,1], η ∈ [0,1], w > 0.

---

## Confer Logs

- Gemini: `bench/logs/confer_novelty_extension/novelty_ext_gemini_20260409T022042Z.txt`
- Codex: `bench/logs/confer_novelty_extension/novelty_ext_cx_20260409T022635Z.txt`
- Dispatch script: `bench/confer_novelty_extension.py`
