# CDSFL Meta-Test: Final Report

**Date:** 27 March 2026
**Protocol:** Instrumented blind pass, 5 models, CC1 (Opus 4.6) as manager
**HEAD before:** c2066de (guards formalised)
**HEAD after:** 08ccab1 (11 fixes applied)

## Executive Summary

The 5-model meta-test identified 16 unique deduplicated findings across the CDSFL mathematical model (699 lines, 25 components). Of these, 11 were genuine fixes, 4 were notation/boundary cleanups, and 3 were soft issues (design choices). All genuine fixes were SymPy-verified and applied to `MATHEMATICAL_APPENDIX.md`. The model is now measurably tighter.

The most consequential fix was the **S_sync formula inversion** (§7.5) — the sycophancy detection metric was producing the opposite of its intended signal. This was found independently by both Gemini and CC2, confirming the finding.

## Model Performance

| Model | Position | N | H̄ | Y(t) | Genuine | Unique | Notes |
|-------|----------|---|---|------|---------|--------|-------|
| Gemini 3.1 Pro | Math specialist | 6 | 11.1 | 66.8 | 4 | 5 | Precise, all verified |
| DeepSeek V3.2 | Volume screener | 5 | 14.6 | 72.8 | 4 | 3 | Some overlap with known |
| CC2 (Opus 4.6) | Defender | 16 | 17.5 | 280.6 | 10 | 8 | Highest yield, deepest |
| ChatGPT 5.4 | Generalist | 0 | N/A | N/A | N/A | 0 | No structured output |
| CX (Codex GPT-5.4) | Captain | 6 | N/A | N/A | N/A | 0 | Contaminated |

### Capability Fingerprints

| Model | D (decay) | v̄ (verification) | A (novel verified) | C (coverage) |
|-------|-----------|-------------------|-------------------|-------------|
| Gemini | N/A (1 round) | 1.00 | 4 | 0.25 |
| DeepSeek | N/A (1 round) | 0.60 | 3 | 0.19 |
| CC2 | N/A (1 round) | 0.75 | 10 | 0.62 |

CC2 dominated: highest N, highest H̄, highest Y(t), most unique findings. This validates the "defender" role — an independent second opinion from the same architecture found issues the other architectures missed.

### CX Contamination

CX (Codex) accessed `bench/logs/meta_test_blind_gemini.md` during its blind pass (confirmed in task output: `sed` command on line 116). All 6 CX findings are identical to Gemini's. Adoption Delta Δ(CX→Gemini) ≈ 1.0. CX's blind pass is invalid for scoring purposes.

**Root cause:** Codex sandbox has read access to the entire working directory. Gemini's output file was written before CX started. No isolation mechanism was available.

**Lesson:** Future multi-model experiments must write blind pass outputs to a separate directory not readable by subsequent models, or use the `codex exec` sandbox flag for file isolation.

### ChatGPT Non-Compliance

ChatGPT 5.4 produced a high-level qualitative assessment rather than structured MATH-XX findings. Five qualitative observations (parameter identifiability, emergence circularity, scope discipline, overparameterisation, independence requirements) overlap with structured findings from other models. The assessment is useful context but cannot be scored within the measurement framework.

**Root cause:** The prompt was sent via pipe from a file that contained both the instructions and the full model text. ChatGPT likely treated the combined input as a document to summarise rather than a task to execute.

## Emergence Analysis

**Single blind pass:** Y_composite = 249.0 vs max(Y_i) = 280.6 (CC2).

**Emergence NOT confirmed** for the blind pass alone. This is expected — the emergence condition requires the confer round to generate interaction-derived findings that exceed the union of independent outputs. In a single blind pass, the composite is just the union, and the highest-performing individual model (CC2) dominates because its findings ARE the majority of the composite.

**Observation:** The three models that produced structured output found non-overlapping genuine issues. Gemini found the table error and p_H bound. DeepSeek found the ascending abstraction quantitative gap and emergence statistical threshold. CC2 found the termination mode issue, Δ confound, indeterminate verifier gap, mutual suppression case, and criterion 4 qualification. This is genuine biodiversity — each model found issues the others missed.

## Fixes Applied

### HARD Genuine Fixes (5)

1. **§7.3 + §7.4:** Ascending abstraction condition changed from dN/dt < 0 (impossible) to dλ/dt < 0. Added quantitative condition: (dH̄/dt)/H̄ > |dλ/dt|/λ.
2. **§7.5:** S_sync formula changed from (1−δ̄)·(1−O_A) to Δ̄·(1−O_A). Defined Δ̄ as mean Adoption Delta.
3. **§6:** p_{H,j,k} clipped to min(1, ...) and λ_s bounded to [0,1).
4. **§8.2:** Emergence condition strengthened to Y_composite > Y_union + k·σ̂(Y).
5. **§8.3:** Second-order cognitive claim qualified from categorical to conditional on criterion 4 evidence.

### Notation/Table/Boundary Fixes (4)

6. **§7.8:** Negative weights recalculated using correct ln(FNR/TNR). Veto property preserved.
7. **§7.4:** λ(t) renamed to k(t) to avoid symbol overload with §7.1.
8. **§7.8:** Indeterminate verifier exclusion rule added.
9. **§1:** R_n subscript and domain boundary note added.

### Reduction Property Fix (1)

10. **§7.2:** H(x) reduction statement corrected (D(x) = 1 only when W_e = 0).

### Update to Existing Fix (1)

11. **§7.5:** Non-verifiable domain guard text updated for corrected S_sync formula.

## Items Deferred (Not Fixed)

- **Adoption Delta confound** (CC2 MATH-05): Δ depends on partner productivity. Documented but not fixed — requires design decision on whether to split into adoption/drop rates or accept the confound. **Deferred for discussion.**
- **D symbol triple collision** (CC2 MATH-12): D(n), D(x), D in fingerprint. Notation cleanup. **Deferred as low priority.**
- **O_A domain guard discontinuity** (DeepSeek MATH-03): Bayesian smoothing proposed. **Deferred — current guard is sufficient.**
- **Mutual suppression case** (CC2 MATH-14): F_conv = empty + high drop = masked. **Deferred — requires new metric design.**
- **Falsification loop dual termination** (CC2 MATH-07): Budget exhaustion vs convergence. **Deferred — affects core_formal.md, not just appendix.**

## Measurement Framework Self-Assessment

The meta-test itself was an instance of the framework examining itself. Key observations:

1. **H(x) worked:** The scoring engine correctly ranked CC2's deep structural findings (Δ confound, termination modes) higher than surface notation issues.
2. **Schema compliance varied wildly:** 3/5 models followed the structured output format. This confirms that format compliance itself is a measurable capability dimension.
3. **CX contamination was detected by the framework:** The identical findings were flagged by the deduplication step. The Adoption Delta would have caught it even without explicit detection.
4. **Emergence requires interaction:** Single-round blind pass cannot establish emergence. The Y_composite < max(Y_i) result is the correct null result for independent work.
