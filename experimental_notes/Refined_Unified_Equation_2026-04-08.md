# Refined Unified Self-Assessment Equation

*8 April 2026. Incorporating Gemini 3.1 Pro and Codex GPT-5.4 confer findings. Verified SymPy + Wolfram Alpha.*

---

## Confer Results

**Gemini 3.1 Pro** and **Codex GPT-5.4** independently reviewed the original unified equation under full CDSFL with FFAFP. Both verified the core equation (π-vanishing, recursive form, special cases, marginal gain). Both identified the same boundary (does not capture Ising Branch 2). Two extensions emerged:

| Source | Extension | Rationale |
|---|---|---|
| Codex | Log-odds form: `logit(R_det) = logit(R_{i-1}) + log(1-q)` | Cleanest representation — additive evidence accumulation |
| Gemini | Re-injection term ν_k: `R_new = R_det·(1-ν) + ν` | Detection-only equation blind to fix-phase risk |

Full confer logs: `bench/logs/confer_unified_equation/`

---

## The Refined Equation

**Phase 1 — Detection (Find + Falsify):**

> **R_det = R_k(i-1) · (1 − q_ik) / (1 − q_ik · R_k(i-1))**

where q_ik = clamp(d_ik · p_ik, 0, 1)

Log-odds form: **logit(R_det) = logit(R_k(i-1)) + log(1 − q_ik)**

**Phase 2 — Resolution (Fix):**

> **R_k(i) = R_det · (1 − ν_k) + ν_k**

**Combined single-step:**

> **R_k(i) = [R_k(i-1)·(1−q_ik)/(1−q_ik·R_k(i-1))]·(1−ν_k) + ν_k**

**Total weighted residual risk:**

> **R_n = Σ_k w_k · R_k(n)**

---

## Critical Re-injection Rate

The break-even point where a cycle does exactly zero net good:

> **ν* = q · R**

- ν < ν*: cycle is **beneficial** (detection gain > fix damage)
- ν > ν*: cycle is **divergent** (fix damage > detection gain) → **HARD EXIT**
- ν = ν*: break-even

Verified across 12 numerical cases (Wolfram Alpha).

---

## Stopping Rule

> **ΔR_cycle = R_k(i-1) − R_k(i)**

- Continue while **Σ_k w_k · ΔR_cycle,k > θ**
- **HARD EXIT** if **ΔR_cycle < 0** (divergent)

---

## Terms

| Symbol | Meaning | Set by |
|---|---|---|
| R_k | Residual risk for flaw class k | Computed (recursive) |
| q_ik | Effective detection = d_ik · p_ik | Model self-estimate |
| p_ik | Detection capability for class k | Model self-estimate |
| d_ik | Diversity of approach (independence) | Model self-estimate |
| ν_k | Re-injection rate (fix introduces new flaw) | Model self-estimate |
| w_k | Consequence weight for class k | Task-dependent |
| π_k | Prior flaw rate | Set once → vanishes |
| θ | Consequence threshold | Set by system |

---

## Special Cases (All Verified)

| Condition | Result | Meaning |
|---|---|---|
| ν = 0 | Reduces to original | Clean fix, detection-only |
| ν = 1 | R_new = 1 | Fix always re-injects |
| q = 0, ν = 0 | R unchanged | Useless pass |
| q = 1, ν = 0 | R = 0 | Perfect detection + clean fix |
| q = 1, ν > 0 | R = ν | Re-injection is the floor |
| R = 0, ν > 0 | R = ν | Fix creates risk from nothing |
| All q=p, d=1, K=1, π=0.5, ν=0 | Standard Bayesian posterior | White paper C(n) |

---

## Scope and Limitations

**Captures:** Per-class detection, diversity, consequence weighting, prior absorption, diminishing returns, fix quality, divergence detection, substrate ceiling (as ν floor).

**Does not capture (by design):**
- Inter-model Ising correlations (§0.1 Branch 2) — system-level, not self-assessment
- Combined machine-HIL detection G_n — system-level
- Composite emergence Y_composite — system-level

**Domain constraints:** q ∈ [0,1], R ∈ [0,1], ν ∈ [0,1], w > 0.

---

## Numerical Example

Two flaw classes: logic (w=0.6, π=0.4, ν=0.02) and interface (w=0.4, π=0.3, ν=0.05).

| Cycle | Class | p | d | q | ν* | R_old | R_det | R_new | ΔR | Status |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | logic | 0.35 | 1.00 | 0.350 | 0.140 | 0.400 | 0.302 | 0.316 | +0.084 | beneficial |
| 1 | interface | 0.20 | 1.00 | 0.200 | 0.060 | 0.300 | 0.255 | 0.293 | +0.007 | beneficial |
| 2 | logic | 0.30 | 0.40 | 0.120 | 0.038 | 0.316 | 0.289 | 0.304 | +0.013 | beneficial |
| 2 | interface | 0.25 | 0.50 | 0.125 | 0.037 | 0.293 | 0.266 | 0.302 | −0.010 | **DIVERGENT** |
| 3 | logic | 0.40 | 0.80 | 0.320 | 0.097 | 0.304 | 0.229 | 0.244 | +0.059 | beneficial |
| 3 | interface | 0.35 | 0.85 | 0.297 | 0.090 | 0.302 | 0.234 | 0.272 | +0.031 | beneficial |

Cycle 2 interface went divergent: low diversity (d=0.5) → low q (0.125) → low ν* (0.037) < ν (0.05). The equation correctly detects that a low-diversity pass with 5% re-injection risk does net harm on interface errors.
