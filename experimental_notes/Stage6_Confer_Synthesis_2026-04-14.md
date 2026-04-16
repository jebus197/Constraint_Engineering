# Stage 6 Confer Synthesis — Gemini 3.1 Pro and Codex GPT-5.4

**Date:** 14 April 2026
**Protocol:** CDSFL (Constraint-Driven Synthesis and Falsification) + FFAFP (Find, Follow, Analyse, Fix, P-pass)
**Subject:** Stage 6 (the current mathematical framework) literature-calibrated extension to the mathematical model
**Models:** Gemini 3.1 Pro (65.9s, 10274 chars), Codex GPT-5.4 (89.7s, 22236 chars)

---

## Converged Findings (Both Models)

### 1. Abstraction Adjustment Backdoor (HARD — FIXED)

Both models independently identified the same critical flaw: the original abstraction adjustment formula `confidence = c_ext + (1 - c_ext) * (H / H_max)` allows zero-search, high-abstraction claims to retain full novelty credit. At H = H_max and c_ext = 0, confidence becomes 1, completely bypassing the literature calibration that Stage 6 was designed to provide.

**Fix applied:** Added β_abs cap (default 0.5). New formula: `confidence = c_ext + β_abs * (1 - c_ext) * (H / H_max)`. At H = H_max, c_ext = 0, confidence = 0.5 (not 1). SymPy verified.

### 2. E-value Mapping Invalid (HARD — FIXED)

The original mapping (pass → 1/α, fail → 0) violates the fundamental e-value property E[e|H₀] ≤ 1 for tools with FPR > α. Gemini provided the precise failure: a tool with 30% FPR mapped to e = 20 gives E[e] = 6, violating the bound.

**Fix applied:** Mapping changed to e = 1/FPR_tool for pass. This guarantees E[e|H₀] = FPR · (1/FPR) = 1 ≤ 1. Rejection criterion changed from > to ≥. SymPy verified.

### 3. Source Correlation Inflation (SOFT — FIXED)

Both models noted the c_ext formula assumes source independence, which is violated by overlapping literature databases.

**Fix applied:** Added γ_src correlation discount (default 0.7): c_ext_adj = γ_src · c_ext. Also added operational definition of c_s = r_s · q_s · a_s (recall, query quality, access completeness).

### 4. "Strict Generalisation" Overstated (SOFT — FIXED)

Codex correctly noted that Stage 6 is a bundle: η decomposition is in the state equation, but e-values affect admissibility only and frequency-scaled confidence is a d-fallback. Not all components are strict generalisations of Stage 5.

**Fix applied:** Language softened. Stage 6 described as "integrated novelty-calibration branch plus auxiliary mechanisms" rather than strict generalisation.

---

## Gemini-Unique Findings

### 5. E-value Threshold Collision (HARD — FIXED)

Strict > criterion means a single test producing e = 1/α exactly fails the threshold. Changed to ≥.

### 6. Continuous Evidence Discard (SOFT — ACKNOWLEDGED)

E_combined (the corroborated e-value across tools) is used for binary admissibility only; its magnitude does not propagate into R_k(i). Gemini proposed linking E_combined to d_eff (the effective detection probability). This is marked [SPECULATIVE] and deferred; the coupling would add complexity without empirical justification yet.

**Response:** Added explicit statement that e-values currently bound admission only, not risk magnitude. Future coupling to d is possible but requires empirical calibration.

---

## Codex-Unique Findings

### 7. c_s Underspecified (SOFT — FIXED)

"Per-source confidence" was not operationally defined. Added c_s = r_s · q_s · a_s decomposition.

### 8. Frequency-Scaled Double Counting (SOFT — FIXED)

Memory enters through π_mem (blended prior) and c_freq (detection confidence). Both use the same historical data, risking overconfidence on common flaw classes.

**Fix applied:** Added double-counting guard with explicit precedence rules. Noted that c_freq should ideally derive from detection success rates, not raw encounter counts.

### 9. d_tool to c_freq Fallback Underspecified (SOFT — FIXED)

Added explicit three-tier precedence rule: d_tool > min(d_partial, c_freq, c_max) > min(c_freq, c_max).

### 10. Missing Boundary Conditions (SOFT — PARTIALLY FIXED)

Codex listed: S=0, T=0, H>H_max, c_freq>1. Added T=0 edge case to §1.8. H/H_max clamping and c_freq capping are implementation constraints, noted in text.

### 11. E-value Gate Should Be "Proposed" (SOFT — FIXED)

Both models agreed the gate cannot be considered operationally valid until per-tool e-process mappings are specified. Changed heading to "Proposed Integration" and added contingency language.

### 12. Lineage Novelty Claims (SOFT — PARTIALLY FIXED)

"Multi-cell architecture is structurally novel" marked [VERIFY:current]. Other specific novelty claims retained pending systematic prior-art survey.

---

## Unfixed / Deferred Items

1. **E-value → d coupling** (Gemini Fix 2): Linking E_combined magnitude to d_eff would preserve continuous evidence. Deferred as [SPECULATIVE] — needs empirical calibration before formal inclusion.

2. **Per-pair source correlation weights** (beyond γ_src): Full Ising-style modelling of source dependencies. Deferred — global discount is sufficient at current scale.

3. **Per-tool e-process specifications**: Defining valid null models and e-processes for each tool family (theorem prover, SMT solver, static analyser, test suite). Required before e-value gate deployment.

4. **Systematic prior-art survey**: Several lineage claims should be backed by formal literature review, not just targeted searches.

---

## Mathematical Verification

All corrections verified by SymPy (14 April 2026):

- β_abs-capped confidence: 5 boundary conditions pass
- Confidence bounded [0, 1] for all valid inputs
- E-value mapping: E[e|H₀] = 1 for FPR-based mapping (FPR = 0.2, 0.05 tested)
- Two-tool corroboration: E_combined = 25 ≥ 20 (threshold at α = 0.05)
- Updated Stage 6 integration: R_new = 0.163 (more conservative than pre-correction 0.141)

---

## Logs

- Gemini: `bench/logs/confer_stage6_model/gemini_20260414T091448Z.json`
- Codex: `bench/logs/confer_stage6_model/codex_20260414T091448Z.json`
- Combined: `bench/logs/confer_stage6_model/combined_20260414T091448Z.json`
