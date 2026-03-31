# Experiment 18: Three-Way FFF Convergence Test

## Metadata

| Field | Value |
|-------|-------|
| **Experiment ID** | 18 |
| **Title** | Three-Way FFF Convergence Test |
| **Date** | 31 March 2026 |
| **Status** | COMPLETE |
| **Commits** | `050fd20` (35 Exp 17 fixes), `d85eb5a` (7 FFF fixes), `989894a` (docs update) |
| **Logs** | `bench/logs/gemini_fff_exp17_fixes/` (symlink: `bench/logs/experiment_18`) |

## Hypothesis

Find-Fix-Follow (FFF) produces integration-level findings that standard confer misses. Specifically: the resolution-and-consequence obligation within a single model turn forces cross-section tracing that multi-model confer without FFF does not achieve.

## Method

Three-way round-robin under CDSFL with FFF instructions:

1. **Round 1:** Gemini with FFF instructions
2. **Round 2:** CX GPT-5.4 (xhigh reasoning effort) with FFF instructions
3. **Round 3:** Gemini (convergence check)

All rounds operated on the same codebase with the same CDSFL system prompt. The only methodological addition was the FFF obligation: find the issue, produce the fix, then trace the consequences of the fix.

## Test Articles

- `bench/dynamic_management.py` (6,354 lines) — dynamic management and immune layer
- `bench/verification_chain.py` (~910 lines) — RFC 9162 Merkle trees, hash chains, Ed25519

## Pre-condition

35 code fixes from Experiment 17 triage already applied (commit `050fd20`):
- 8 Immune Manager fixes (IM_F001–F013)
- 9 Load Balancer fixes
- 14 Verification Chain fixes
- 4 Mathematical Model fixes
- 351 tests passing

These fixes addressed all findings from the standard (non-FFF) Exp 17 rounds. The FFF convergence test started from a clean baseline where conventional confer had already been exhausted.

## Results

### Round 1 — Gemini FFF

**2 findings:**

1. **`estimate_gamma` inf→1.0:** When all findings cluster in early rounds (perfect convergence pattern), the gamma estimator returned `inf` instead of clamping to `1.0`. FFF's follow step traced the consequence: downstream convergence detection would never trigger because `inf > threshold` is always true, masking genuine convergence.

2. **`kappa_rate` divergence masking:** The rate-of-change calculation for kappa returned `0.0` when the denominator was zero, which masked genuine divergence in inter-rater agreement. FFF's follow step identified that this zero return propagated into the immune layer's health monitor as a false "stable" signal.

### Round 2 — CX GPT-5.4 xhigh FFF

**5 findings:**

1. **`verify_chain` exception safety:** Malformed digest strings could raise unhandled exceptions in the verification path. FFF's follow step traced the failure through the full chain validation pipeline.

2. **`Verifier.verify` type guard:** Non-string signatures passed type checks but caused cryptographic verification failures downstream. Follow step identified the specific Ed25519 code path.

3. **`mu+novelty` routing key unreachable:** A pathology key combining mu and novelty metrics was defined but never matched by the routing logic. Follow step confirmed the dead code path through the immune response dispatcher.

4. **`pm_performance_warning` unwired:** The player manager warning system was defined but not connected to the event propagation pipeline. Follow step traced the gap from detection through to the expected consumer.

5. **`estimate_gamma` zero-data refinement:** CX refined Gemini's Round 1 fix. Gemini had clamped to `1.0` for the perfect-convergence case, but CX's follow step identified that zero-data (no findings at all) is semantically different from perfect convergence. Zero data should return a sentinel or raise, not claim convergence.

### Round 3 — Gemini

**Convergence declared.** No new findings above 0.5 severity threshold. All Round 2 fixes reviewed and confirmed sound.

### Summary

| Metric | Value |
|--------|-------|
| Total genuine fixes | 7 |
| Rounds to convergence | 3 |
| Models involved | 2 (Gemini, CX GPT-5.4) |
| Tests passing (post-fix) | 351 |
| False positives | 0 |

## Key Observations

### Model/effort configuration matters more under FFF than under standard confer

CX at o4-mini with medium reasoning effort produced **0 genuine findings** during an earlier attempt — all were false positives caused by insufficient context processing. The same model family at GPT-5.4 with xhigh reasoning effort produced **5 genuine findings**, all confirmed by tests and code review.

This suggests FFF amplifies the capability gap between model configurations. The follow step requires deeper reasoning chains (trace fix consequences through multiple code paths), which weaker configurations cannot sustain. Under standard confer, where models only report findings without resolution, the capability floor is lower.

### Cross-model refinement demonstrates FFF working as designed

CX's refinement of Gemini's `estimate_gamma` fix (finding #5 in Round 2) is the clearest demonstration of FFF's value in a multi-model context. Gemini found the issue and produced a valid fix. CX, reviewing Gemini's fix under FFF instructions, applied its own follow step and found an edge case within the fix itself. This is the FFF mechanism operating across model boundaries — the follow obligation forced CX to treat Gemini's fix as a new starting point for consequence tracing, not just a finding to validate.

### Comparison with standard Exp 17 triage

Standard Exp 17 triage: 140 findings across 5 models and 4 rounds produced 35 fixes. FFF convergence: 7 findings across 2 models and 3 rounds produced 7 additional fixes, all genuine, all in code that the standard triage had already reviewed and cleared.

## Conclusion

FFF demonstrated measurable value as a methodology extension to CDSFL. The three-way round-robin converged in 3 rounds with 7 genuine fixes that standard confer had missed. The follow obligation forces cross-section analysis that reporting-only protocols do not achieve.

This was an observational test, not a controlled experiment. The pre-condition (35 prior fixes already applied) means FFF operated on a codebase that standard confer had already processed — which makes the 7 additional findings more significant, not less, but does not constitute controlled comparison.

A formal controlled test is designed as **Experiment 19**: a 2-condition factorial (standard confer vs FFF) on matched test articles, with the composable directive architecture providing the experimental manipulation.
