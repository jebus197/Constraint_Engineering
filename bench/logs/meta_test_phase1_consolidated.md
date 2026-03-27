# CDSFL Meta-Test: Phase 1 Consolidated Findings

**Date:** 27 March 2026, 13:20 UTC
**Status:** Blind pass complete for Gemini, DeepSeek. ChatGPT non-compliant (no structured output). CX contaminated (read Gemini output). CC2 pending (subagent).

## Blind Pass Results Summary

| Model | Findings | Format Compliance | Genuine Fixes | Notes |
|-------|----------|-------------------|---------------|-------|
| Gemini 3.1 Pro | 6 (1 truncated) | Full | 4 | Output truncated at MATH-06 |
| DeepSeek V3.2 | 5 | Full | 4 | Structured, some overlap |
| ChatGPT 5.4 | 0 structured | None | N/A | Gave high-level assessment, no MATH-XX format |
| CX (Codex GPT-5.4) | 6 | Full | 4 | CONTAMINATED: read Gemini output file |
| CC2 (Opus 4.6) | Pending | Pending | Pending | CLI stuck, subagent running |

## Deduplicated Finding Set

### F1: §7.3 — dN/dt < 0 impossible for cumulative count (HARD)
- **Found by:** Gemini (MATH-01), CX (MATH-01, contaminated)
- **Verified:** YES (SymPy)
- **Fix:** Replace "dN/dt < 0" with "dλ/dt < 0" or "d²N/dt² < 0" in ascending abstraction condition
- **Impact:** Affects §7.3 and §7.4 (stop guard)

### F2: §7.2 — H(x) reduction property false for W_e = W_c > 0 (HARD)
- **Found by:** Gemini (MATH-02), CX (MATH-02, contaminated)
- **Verified:** YES (SymPy). D(1) = 1.169, D(10) = 1.289
- **Fix:** Correct reduction statement to "W_e = 0" or fix D(x) formula
- **Impact:** Cosmetic — does not affect H(x) operational use

### F3: §7.8 — Table negative weights use wrong likelihood ratio (HARD)
- **Found by:** Gemini (MATH-03), CX (MATH-03, contaminated)
- **Verified:** YES (numerical). Dim: table=-1.39 vs correct=-1.50. Num: table=-0.85 vs correct=-1.04
- **Fix:** Recalculate table with correct ln(FNR/TNR)
- **Note:** Veto property STILL HOLDS with correct values (S_v = 0.272 unchanged). SymPy weight unchanged (-4.60)

### F4: §7.5 — S_sync formula uses undefined δ̄ and inverts sycophancy logic (HARD)
- **Found by:** Gemini (MATH-04), CX (MATH-04, contaminated)
- **Verified:** YES (SymPy). dS/dΔ = O_A - 1 < 0 for O_A < 1
- **Fix:** Define δ̄ = Δ̄ (mean Adoption Delta). Change formula to S_sync = Δ̄ · (1 - O_A)
- **Impact:** CRITICAL — current formula produces opposite of intended signal

### F5: §7.4/§7.1 — λ(t) symbol overloaded (notation)
- **Found by:** Gemini (MATH-05), CX (MATH-05, contaminated)
- **Verified:** YES (SymPy). Duane λ(t) always positive; §7.4 uses λ(t) ≤ 0 branch
- **Fix:** Rename §7.4 decay rate to k(t) or similar

### F6: §6 — p_H can exceed 1.0 (HARD)
- **Found by:** Gemini (MATH-06, truncated), CX (MATH-06, contaminated)
- **Verified:** YES (numerical). 2 vars: p_H = 1.8
- **Fix:** Add clip: p_{H,j,k} = min(1, f_k(E,M) · Π_s(1 + λ_s·V_s))

### F7: §7.2 — H(x) calibration parameters arbitrary (SOFT)
- **Found by:** DeepSeek (MATH-01)
- **Verified:** Known soft issue (confirmed in Gemini consultation)
- **Fix:** None needed until calibration data exists

### F8: §7.3 — Ascending abstraction insufficient for Y increase (HARD)
- **Found by:** DeepSeek (MATH-02)
- **Verified:** YES (SymPy). N(t)=10-t, H̄=1+0.05t → dY/dt = -0.6 at t=1
- **Fix:** Formalise as: dY/dt > 0 ⟺ (dH̄/dt)/H̄ > |dN/dt|/N
- **Note:** Overlaps with F1 but is a distinct issue — even fixing the count/rate confusion, the condition is still insufficient

### F9: §7.5 — O_A domain guard discontinuity (SOFT)
- **Found by:** DeepSeek (MATH-03)
- **Verified:** Logical argument valid. Threshold at |verifiable| = 2 creates step function
- **Fix:** Consider Bayesian smoothing (v+1)/(n+2) or accept as design choice

### F10: §7.8 — Veto property parameter-dependent (SOFT)
- **Found by:** DeepSeek (MATH-04)
- **Verified:** TRUE — veto depends on SymPy TPR/FPR settings
- **Fix:** Note as design choice. Veto holds for any verifier with TPR > 0.95 and FPR < 0.01

### F11: §8.2 — Emergence condition lacks statistical threshold (HARD)
- **Found by:** DeepSeek (MATH-05)
- **Verified:** Logical argument valid
- **Fix:** Y_composite > max(Y_i) + k·σ, with bootstrap SE

### ChatGPT Qualitative Findings (unstructured)
- Parameter identifiability concern (overlaps F7)
- Emergence circularity risk (overlaps F11)
- Scope discipline on "validated" claims
- Overparameterisation warning

## Unique Findings per Model (post-dedup)

| Model | Unique Verified | Shared | Total |
|-------|----------------|--------|-------|
| Gemini | F3, F4, F5, F6 (4 unique) | F1, F2 | 6 |
| DeepSeek | F8, F9, F11 (3 unique) | F7 (known), F10 | 5 |
| ChatGPT | 0 structured | Qualitative overlap | 0 |
| CX | 0 (contaminated) | All copied from Gemini | 6 |
| CC2 | Pending | Pending | Pending |

## Classification

| Severity | Count | Findings |
|----------|-------|----------|
| Genuine fix (HARD) | 5 | F1, F4, F6, F8, F11 |
| Genuine fix (notation/table) | 2 | F3, F5 |
| Soft/design choice | 3 | F7, F9, F10 |
| Reduction property error | 1 | F2 |
