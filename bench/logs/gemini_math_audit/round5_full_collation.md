# Full Collation: Mathematical Coherence Audit Rounds 1-5

Timestamp: 2026-03-31T12:25Z

## Round Summary

| Round | Action | Output |
|-------|--------|--------|
| 0 | Gemini Phase 1 (8-chunk decomposed) | 14,872 chars, 6 tasks |
| 1 | SymPy verification | 13/13 PASS |
| 2 | Gemini Phase 2 (with SymPy + CC obs) | 8,688 chars, 4 tasks |
| 4 | All-model review (5 models) | CC2 5,021 + CX 6,860 + ChatGPT 4,964 + DeepSeek 5,754 + Gemini 5,489 = 28,088 chars |
| 5 | SymPy verification of Round 4 claims | 10/10 PASS |

## Updated 5-Model Consensus Matrix

| Item | CC2 | CX | ChatGPT | DeepSeek | Gemini(self) | Consensus |
|------|-----|-----|---------|----------|--------------|-----------|
| A. Namespace | APPROVE | MODIFY | APPROVE | APPROVE | REJECT | 3A, 1M, 1R |
| B. §9/§10 text | MODIFY | MODIFY | APPROVE | MODIFY | REJECT | 1A, 3M, 1R |
| C. Deferred items | APPROVE | MODIFY | APPROVE | APPROVE | APPROVE | 4A, 1M |
| D. New additions | MODIFY | MODIFY | APPROVE | APPROVE | MODIFY | 2A, 3M |
| E. Self-falsification | MODIFY | MODIFY | APPROVE | APPROVE | APPROVE | 3A, 2M |
| F. Synthesis deferral | APPROVE | MODIFY | APPROVE | APPROVE | APPROVE | 4A, 1M |
| G. Ising model | APPROVE | REJECT | APPROVE | MODIFY | MODIFY | 2A, 2M, 1R |
| H. Missed issues | 2 found | 1 found | None | 1 found | 1 MAJOR | 4 found, 1 none |

## Resolved Items (convergence achieved)

### R1: §9.1 P(y_t|x_{<t}) = ⊥ → P = 0
4/5 models flag this. SymPy confirms ⊥ ∉ [0,1]. RESOLVED: use P = 0
or indicator function I(context complete) = 0.

### R2: §9.2 Uniqueness of N_len* needs proof
3/5 models flag this. SymPy confirms unimodality requires parameter constraints.
RESOLVED: state as conditional — "when β > 0 and k > 0 and L_c < L₀,
Λ(L) has a unique maximum" — or weaken to "has at least one maximum."

### R3: A-N1 rejection correct
5/5 APPROVE. RESOLVED.

### R4: A-N2 acceptance correct
5/5 APPROVE. RESOLVED.

### R5: §11 fold into §9.4 correct
5/5 APPROVE. RESOLVED.

### R6: Synthesis deferral (not attention yield) correct
5/5 APPROVE substance. RESOLVED.

### R7: Deferred items A-D1 through A-D5 correct
4/5 APPROVE. CX's modifications are editorial, not mathematical. RESOLVED.

### R8: ρ_eff formula domain restriction
Gemini proved ρ_eff = -3 when inputs are -1,-1. SymPy confirms.
DeepSeek was wrong that it exceeds 1 for positive inputs (SymPy: 0.96 at 0.8,0.8).
RESOLVED: formula valid only for ρ ∈ [0,1] (probability union form).
Must explicitly state domain restriction. For full Pearson range, need
different formula (e.g., Fisher z-transform or covariance matrix).

## Outstanding Items (need next iteration)

### O1: Ising model — the sharpest disagreement
- CX: REJECT. Proper normalisation (Z) makes bound redundant. SymPy confirms.
- DeepSeek: MODIFY. Bound applies to max-over-states, not raw sum.
- Gemini: MODIFY. Must be pairwise ψ_ij, not 3-tensor ψ_ijk.
- CC2/ChatGPT: APPROVE.

CC assessment: CX is RIGHT that a normalised Ising model doesn't need the
bound. The question is whether we use normalised or unnormalised. The
unnormalised form Π(1-q)·exp(Σψ) is what the model originally proposed.
DECISION NEEDED: Either (a) switch to normalised Ising with partition function Z,
making the bound unnecessary but adding complexity, or (b) keep unnormalised
with the corrected pairwise bound.

### O2: C(n) independence contradiction (Gemini self-review)
C(n) = 1-(1-p)^n assumes independence. §10.2/10.3 define correlation.
This is a FUNDAMENTAL contradiction in the model. SymPy confirms.
RESOLUTION: C(n) must branch — independence form for isolated passes,
generalised joint distribution for correlated passes. Gemini proposed:
C(n) = 1 - P(∩ fail_i) using the joint distribution from §10.3.

### O3: Namespace — additional collisions found
- Gemini self-review: φ_fmt vs φ_mass inconsistency, N collision with population
- CX: C(n)/C_M/C all mapped to Ω_cap loses information
- CC2: π collision (risk vs corroboration)
Total confirmed collisions now: 14 original + 3 new = 17.

### O4: A-N3 null vector attack
Gemini self-review: model outputs null → S_sync = 0 → max weight.
3/5 models flag A-N3 needs work. Gemini proposes indicator I(||y||>0).
CX proposes separating independence from quality.
RESOLUTION PENDING: combine both — w = v̄ · u_qual · (1-S_sync) · I(||y||>0).

### O5: Multiplicative separability assumptions (CX)
CX: κ_coh = κ_load · κ_focus and d = d_weight · d_config are separability
ASSUMPTIONS, not derived results. Must be presented as definitions.
No other model raised this. CC agrees this is methodologically important.

## CC Assessment: Convergence Status

The cycle is CONVERGING but not yet complete:
- 8 items resolved (R1-R8)
- 5 items outstanding (O1-O5)
- Of the 5 outstanding, O2 (C(n) independence) is the most fundamental
- O1 (Ising) has a clear resolution path (normalise properly)
- O3 (namespace) is editorial
- O4 (null vector) is a minor edge case
- O5 (separability) is a presentation issue

RECOMMENDATION: One more iteration targeting O1-O2 specifically (the
mathematical substance). O3-O5 are resolvable editorially.
