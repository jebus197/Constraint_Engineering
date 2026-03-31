# Mathematical Coherence Audit — Full Results

**Date:** 31 March 2026
**Lead:** Gemini 3.1 Pro (mathematical specialist)
**Reviewers:** CC2 (Claude Sonnet 4), CX (Codex/GPT-5.4), ChatGPT (GPT-4.1), DeepSeek (deepseek-reasoner)
**Verifier:** SymPy (23 checks, 23/23 PASS)
**Duration:** ~2.5 hours, 6 rounds
**Logs:** `bench/logs/gemini_math_audit/`

## Process

The full CDSFL mathematical model (~700 lines, ~65K chars) was delivered to Gemini in 8 chunks using the decomposed dispatch infrastructure (tutor/"WAITING" pattern). Gemini performed initial analysis, then its output was verified with SymPy, refined in a second Gemini phase, reviewed by all 5 models under tight mathematical constraints, re-verified with SymPy, and iterated to convergence in a final targeted round.

| Round | Action | Output |
|-------|--------|--------|
| 0 | Gemini Phase 1 (8-chunk decomposed) | 14,872 chars, 6 tasks |
| 1 | SymPy verification | 13/13 PASS |
| 2 | Gemini Phase 2 (with SymPy + CC observations) | 8,688 chars, 4 tasks |
| 4 | 5-model CDSFL review | 28,088 chars total |
| 5 | SymPy verification of Round 4 claims | 10/10 PASS |
| 6 | Gemini final resolutions + CX verification | 8,015 chars |

## 5-Model Consensus Matrix

| Item | CC2 | CX | ChatGPT | DeepSeek | Gemini | Consensus |
|------|-----|-----|---------|----------|--------|-----------|
| A. Namespace | APPROVE | MODIFY | APPROVE | APPROVE | REJECT | 3A, 1M, 1R |
| B. §9/§10 text | MODIFY | MODIFY | APPROVE | MODIFY | REJECT | 1A, 3M, 1R |
| C. Deferred items | APPROVE | MODIFY | APPROVE | APPROVE | APPROVE | 4A, 1M |
| D. New additions | MODIFY | MODIFY | APPROVE | APPROVE | MODIFY | 2A, 3M |
| E. Self-falsification | MODIFY | MODIFY | APPROVE | APPROVE | APPROVE | 3A, 2M |
| F. Synthesis deferral | APPROVE | MODIFY | APPROVE | APPROVE | APPROVE | 4A, 1M |
| G. Ising model | APPROVE | REJECT | APPROVE | MODIFY | MODIFY | 2A, 2M, 1R |
| H. Missed issues | 2 found | 1 found | None | 1 found | 1 MAJOR | 4/5 found new |

## Findings and Resolutions

### 1. Symbol Collisions (17 confirmed) — RESOLVED

14 original collisions + 3 new (φ_fmt/φ_mass, N/n population, π risk/corroboration). Full renaming table produced: C → Ω_cap for capacity, π → π_risk for falsification debt, φ split into φ_fmt and φ_mass. Editorial, not mathematical.

### 2. C(n) Independence Contradiction — RESOLVED (FUNDAMENTAL)

C(n) = 1-(1-p)^n assumes independence; §10.2/10.3 define correlation. Fundamental contradiction. **Resolution:** C(n) branches:

- **Branch 1 (Independent):** C(n) = 1 - ∏q_i. Applicable only when passes share no state.
- **Branch 2 (Correlated):** C(n) = 1 - (1/Z)(∏q_i)exp(Σψ_ij). Uses normalised Ising from §10.3.

CX modification (accepted): q_i must be baseline Bernoulli parameters, not post-coupling marginals.

### 3. Ising Model Normalisation — RESOLVED

Original unnormalised form Π(1-q)·exp(Σψ) needs artificial bounds. **Resolution:** Switch to normalised pairwise Boltzmann:

P(**x**) = (1/Z) [∏ q_i^{x_i} (1-q_i)^{1-x_i}] exp(Σ ψ_ij x_i x_j)

Z guarantees P(**x**) ∈ [0,1] and Σ P(**x**) = 1 for any finite ψ. Reduces to independent product when ψ_ij = 0 ∀i,j. CX APPROVE. SymPy confirmed.

### 4. Decomposed Delivery Attention Claim — FALSIFIED, reformulated

In cumulative context, α_staged = α(L_total) regardless of chunking. The benefit is **synthesis deferral**, not attention preservation. Reformulated as τ_defer operator.

### 5. A-N1 Anti-Parroting — REJECTED (5/5 APPROVE rejection)

Penalises verified convergence. Contradicts O_A. Existing S_sync handles unverified sycophancy. Blind rounds are the only reliable mechanism for the underlying identifiability problem.

### 6. ρ_eff Domain Restriction — RESOLVED

ρ_eff = -3 at inputs (-1,-1). Valid only for ρ ∈ [0,1]. Full Pearson range requires Fisher z-transform or covariance matrix.

### 7. §9.1 P(y_t|x) = ⊥ — RESOLVED

⊥ ∉ [0,1]. Replace with P = 0 or indicator I(context complete) = 0.

### 8. §9.2 N_len* Uniqueness — RESOLVED

State conditionally: "when β > 0, k > 0, L_c < L₀, Λ(L) has a unique maximum."

### 9. §11 → §9.4 — RESOLVED (5/5 APPROVE)

Single item (composition monotonicity) folded into §9.4 as structural constraint.

### 10. Null-Vector Attack (A-N3) — RESOLVED

CX modification (accepted): piecewise weight definition avoids evaluating S_sync at ||y|| = 0:

```
w(y) = 0,                                    if ||y||₂ = 0
w(y) = v̄ · u_qual · (1 - S_sync(y)),         if ||y||₂ > 0
```

### 11. Separability Assumptions — RESOLVED

κ_coh ≡ κ_load · κ_focus and d ≡ d_weight · d_config declared as axiomatic separability assumptions, not derived theorems. CX raised, all models approved.

### 12. Deferred Items A-D1 through A-D5 — ALL RESOLVED (4/5 APPROVE)

- **A-D1:** Asymmetric Δ formulation
- **A-D2:** D symbol triple collision → rename
- **A-D3:** Step function kept as design choice
- **A-D4:** Mutual suppression flagged as pathological state
- **A-D5:** Budget vs convergence formalised with falsification debt D_F

### 13. A-N2 and A-N3 Accepted

Manager selection function (A-N2) approved 5/5. Contribution weight (A-N3) approved with null-vector guard.

## SymPy Verification Summary

| Round | Checks | Result |
|-------|--------|--------|
| 1 | 13 (budget termination, novelty rate, S_v, unbounded weight, strict inequality, cumulative context, collisions) | 13/13 PASS |
| 5 | 10 (ρ_eff domain, C(n) independence, Ising pairwise, normalised Ising, ⊥ probability, Λ uniqueness) | 10/10 PASS |
| **Total** | **23** | **23/23 PASS** |

## Process Efficiency Factors

1. **Decomposed dispatch** — reusable 8-chunk delivery, all 5 APIs
2. **CX efficiency fixes** — reasoning medium, no MCP, ephemeral mode
3. **Problem box / tight math box** — models constrained to pure maths output
4. **SymPy pipeline** — cumulative from composer confer (12 prior checks)
5. **API dispatch patterns** — all 5 models pre-tested from Exp 11-17
6. **CDSFL schema** — structured verdicts, measurable convergence

## Outstanding (2 minor)

1. CX's q_i terminology clarification → fold into O2 text
2. CX's piecewise weight definition → fold into O4 text

Both editorial. Mathematical convergence achieved.
