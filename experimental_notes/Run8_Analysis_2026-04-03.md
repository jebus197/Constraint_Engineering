# Run 8 Analysis: 20 Rounds, 339 Findings, Convergence Detection Gap Identified

**Date:** 3 April 2026, 00:53 BST
**Duration:** 52 minutes (3,111 seconds)
**Termination:** MAX_ROUNDS (20)
**Logs:** `bench/logs/baseline_confer_run8_20260402/`

---

## Summary

| Metric | Value | Interpretation |
|--------|-------|----------------|
| Total findings | 339 | Across 20 rounds |
| Unique finding IDs | 30 | 91.2% churn rate |
| γ (Duane) | −0.041 | Not converging (threshold 0.5) |
| C(H,E) | 0.789 | Strong corroboration |
| Models | 5 → 3 | Gemini benched R6, DeepSeek R10 |
| Immune verdicts | 331 UNCERTAIN | Expected (CT disabled, observation mode) |
| AQO confidence | 0.188 | No useful signal |

## Per-Model Performance

| Model | Findings | Rounds Active | Mean Ω | Amplification A |
|-------|----------|---------------|--------|----------------|
| CC2 | 126 | 20 | 0.275 | 1.613 |
| ChatGPT | 83 | 20 | 0.360 | 1.488 |
| Codex | 83 | 20 | 0.345 | 1.512 |
| DeepSeek | 34 | 11 | 0.298 | 0.878 |
| Gemini | 13 | 7 | 0.235 | 0.977 |

## Per-Round Finding Counts

```
R 0: 15 (blind, 5 models)     R10: 19 [−DS,Gem]
R 1: 18 (adaptive, 5 models)  R11: 14 [−DS,Gem]
R 2: 20 (adaptive, 5 models)  R12: 18 [−DS,Gem]
R 3: 18 (adaptive, 5 models)  R13: 18 [−DS,Gem]
R 4: 17 (adaptive, 5 models)  R14: 16 [−DS,Gem]
R 5: 23 (adaptive, 5 models)  R15: 14 [−DS,Gem]
R 6: 19 [−Gemini]             R16: 13 [−DS,Gem]
R 7: 16 [−Gemini]             R17: 15 [−DS,Gem]
R 8: 14 [−Gemini]             R18: 15 [−DS,Gem]
R 9: 24 [−Gemini]             R19: 13 [−DS,Gem]
```

First half mean: 18.4, second half mean: 15.5. Trend: −0.246 findings/round (insufficient for γ > 0).

## The Convergence Detection Gap

**The core finding:** The system is **exhausted** but not **convergent** as measured.

- Every genuine issue was found by Round 3–4
- Rounds 5–19 are restating the same 30 findings with cosmetic variation
- γ measures total finding rate, which stays flat (~17/round) because models don't produce fewer findings when they run out of new things — they restate
- Ω oscillates at ~0.30 because cosmetic variation keeps similarity below the dedup threshold

**Why the maths is correct but the measurement is wrong:**

Duane γ assumes found defects are *removed*. In hardware reliability, a discovered defect is fixed. In AI review, a stated finding persists in context and gets restated. The finding rate doesn't decline because the output is constant-volume regardless of novelty.

**Fix:** Compute γ on **deduplicated findings** (by semantic similarity clustering), not raw counts. Or: compute γ after immune pipeline filtering.

## Finding ID Repetition

| Finding ID | Repetitions |
|------------|-------------|
| Codex_IM_F001 | 14 |
| Codex_IM_F002 | 13 |
| Codex_IM_F003 | 13 |
| CC2_CC_IM_F001 | 12 |
| CC2_CC_IM_F002 | 12 |
| CC2_CC_IM_F003 | 12 |
| CC2_CC_IM_F004 | 12 |
| Codex_IM_F004 | 12 |
| CC2_CC_IM_F005 | 11 |
| ChatGPT_IM_F001 | 8 |

## Dominant Themes (clustered)

1. **Shim is wrong artefact** — models can't review immune behaviour from a re-export file (15 occurrences)
2. **Interface contract incompleteness** — ordering, typing, ownership (10)
3. **Lifecycle gaps** — deferred remediations, rollback, threshold feedback (10)
4. **Missing `__all__`** — export surface ambiguous (8)
5. **Temporal ordering** — immune mutations vs convergence checks (6)
6. **Convergence threshold mutation** — read-after-write ordering (5)

## Immune Pipeline (Observation Mode)

- 100% UNCERTAIN verdicts (331/331) — expected with CT disabled
- B-Cell can only verify mathematical/statistical/logical claims; findings are code-structural
- NK Cell dedup below threshold on cosmetically varied restatements
- Regulatory T-Cell: 0% rejection rate, no autoimmune condition
- **Conclusion:** CT is the critical cell for code-review tasks. Without it, pipeline is nearly blind.

## AQO (Adaptive Question Optimisation)

- Confidence: 0.188 (very low)
- Best correlation: referential_density r=0.094 (negligible)
- **Cause:** Prompt features don't vary (same artefact, same structure every round)
- **Conclusion:** AQO needs diverse prompt strategies to learn. Single-task fixed-artefact runs provide no signal. Bench Run 2 is the appropriate test.

## Ω Churn Guard

- Correctly benched Gemini (R6) and DeepSeek (R10) — both hit Ω=0 for 2 consecutive rounds
- Surviving trio (CC2, Codex, ChatGPT) maintained Ω≈0.30
- Guard catches total stall but not steady-state churning masked by cosmetic variation
- Same underlying issue as γ: measures presence of variation, not presence of novelty

## Highest-Value Findings (for verification)

From CC2 Round 19 (the most mature cross-cutting analysis):

1. **CC_IM_F001 (sev 0.88):** `_deferred_remediations` is write-only — no re-evaluation lifecycle
2. **CC_IM_F002 (sev 0.84):** `_pre_fix_snapshots` is write-only — no rollback mechanism
3. **CC_IM_F003 (sev 0.82):** Temporal ordering of immune threshold mutations vs convergence checks unspecified
4. **CC_IM_F004 (sev 0.78):** `CorrelatedFailureModel` exported but undocumented
5. **CC_IM_F005 (sev 0.76):** Remediation chain index-based tracking fragile across chain modifications
6. **CC_IM_F006 (sev 0.72):** `event_callback` injection mechanism undocumented

## Next Steps

1. **Collate ~30 unique findings** — deduplicate by finding_id
2. **Verify with SymPy/z3/FFF** against actual implementation files
3. **Fix γ computation** — track deduplicated findings, not raw counts
4. **Run 9** — flip `observation_only=False`, `ct_enabled=True`
