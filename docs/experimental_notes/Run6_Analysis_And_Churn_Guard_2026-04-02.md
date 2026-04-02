# Run 6 Analysis, Churn Detection, and Churn Guard Proposal

**Date:** 2026-04-02T09:17:12+01:00

---

## Run 6 Final Results

| Metric | Value |
|--------|-------|
| Duration | 29,223s (8h 7m) — wall-clock cap |
| Rounds | 11 (R0–R10) |
| Total findings | 299 |
| γ (Duane) | 0.027 (NOT converged) |
| C(H,E) Popper | 0.863 (strong corroboration) |
| Termination | Wall-clock cap (not convergence, not round cap) |

**Per-model findings:** ChatGPT 89, CC2 85, DeepSeek 49, Codex 43, Gemini 33

**Per-round findings:** 29, 40, 17, 29, 31, 20, 27, 31, 22, 28, 25

**Y(t) cognitive yield:** 16.1, 24.3, 11.3, 18.3, 19.0, 12.7, 16.5, 19.9, 15.3, 18.3, 16.5

**γ_input trajectory:** 0.523 → 0.537 → 0.498 → 0.469 → 0.463 → 0.444 → 0.419 → 0.418 → 0.361 → 0.417 → 0.434 (input growing more complex as findings accumulate in prompt)

---

## Mathematical Findings Audit

64/299 findings (21%) had substantive mathematical content. 8 distinct claims SymPy-verified:

| # | Claim | Valid? | Valuable? | Notes |
|---|-------|--------|-----------|-------|
| 1 | `effective_window` exponential growth | ✅ Math valid | ⚠️ Code already clamped | 4 findings missed AW-2 fix at line 2760 |
| 2 | `CorrelatedFailureModel` N≥3 overestimate | ✅ | ✅ 10–1000× overestimate | `max()` destroys N-model redundancy benefit |
| 3 | Asymmetric detect vs resolve thresholds | ✅ | ✅ O(2^N) asymmetry | Drives flip-flopping, clamped but wastes cycles |
| 4 | Population vs sample std dev | ✅ | ❌ Low severity | 33% at N=3, doesn't change outcomes |
| 5 | `abs()` mu check blind to sign changes | ✅ | ⚠️ Context-dependent | Real blind spot, needs 2-round lookback |
| 6 | Extended P-pass iteration dead code | ✅ | ✅ Code confirmed | No mutation between iterations → always exits at 2 |
| 7 | Vocab growth rate denominator mismatch | Unconfirmed | — | Needs code check |
| 8 | Flatlined metric at 0.0 bypasses remediation | ✅ | ✅ Highest severity (0.95) | Silently disables immune system |

**Genuinely valuable math bugs: 4** (#2, #3, #6, #8)

---

## Software Findings Audit

6 specific code claims verified against `dynamic_management.py`:

| # | Claim | True? | Fix? | Severity |
|---|-------|-------|------|----------|
| A | `_apply_transform()` missing 7/12 transforms | ✅ | ✅ HIGH | 7 remediation chains silently broken |
| B | PAR `DOWNGRADE_ROLE` has no escalation path | ✅ | ✅ HIGH | Failing models stuck with no-op recovery |
| C | `set_remediation_state()` doesn't store `chain_length` | ❌ | — | Actually stored (RV-1 fix exists) |
| D | `findings_decline` requires `len >= 4` for 3-round window | ✅ | ✅ LOW | 1-round detection delay |
| E | `mu_distortion` pathology key mismatch | ✅ | ✅ MED | Over-specification check always returns 0 |
| F | `_perf_rounds_seen` grows without bound | ✅ | ✅ LOW | Memory leak in long runs |

---

## Churn Analysis

### Repetition Rate
- **44%** of all findings target code previously examined in earlier rounds
- Most hammered targets: `FailureHandler` (6 rounds), `record_round` (4 rounds), `self_diagnose` (4 rounds)

### Severity Inflation
| Round | Avg Severity | High (≥0.8) | Count |
|-------|-------------|-------------|-------|
| R0 | 0.55 | 3 | 35 |
| R1 | 0.78 | 6 | 12 |
| R2 | 0.76 | 10 | 21 |
| R3 | 0.64 | 2 | 14 |
| R7 | 0.75 | 6 | 17 |
| R10 | 0.80 | 6 | 11 |

### The Pattern
R0–R3 produced genuinely novel findings at reasonable severity. R4–R10 re-examined the same code targets with more elaborate descriptions and inflated severity. This matches the Gemini churn pattern from the founder's earlier interaction (Epistemic Mesh → Sovereign Shards → Fractal P-Pass → Canonical State Validator with "Confidence Level: 98%").

---

## Amplification Factor Data (Passive Observation)

| Model | A (avg) | Compound Obj (avg) | n rounds |
|-------|---------|-------------------|----------|
| ChatGPT | 1.6726 | 0.1305 | 11 |
| DeepSeek | 1.5562 | 0.2127 | 11 |
| Codex | 1.5458 | 0.2266 | 11 |
| CC2 | 1.4817 | 0.2591 | 10 |
| Gemini | 1.1246 | 0.3215 | 11 |

ChatGPT is the highest amplifier (produces most complex output relative to input). Gemini's output most closely tracks input complexity.

---

## Churn Guard Proposal

### Why γ Alone Fails
γ measures vocabulary novelty in findings. On a self-referential ouroboros task, the prompt grows each round (131K → 190K+ chars), injecting novelty. γ_input falls (more novel vocabulary entering), preventing γ_output from rising. The system correctly identifies non-convergence but can't distinguish "genuinely new findings" from "elaborately restated old findings with new vocabulary."

### The Compound Objective Solution
The compound objective (A × γ_output) already detected churn passively:
- Gemini compound obj went to 0.0 in R7
- ChatGPT went to -0.558 in R10 (negative = high amplification + negative decay = sounds impressive, adds nothing)

**Proposed mechanism:** When a model's compound objective drops below 0.10 for 2 consecutive rounds, bench it. When ALL models are below threshold, terminate. This measures value-per-round, not vocabulary novelty.

### Expected Impact
If active in Run 6: termination at R5–R7 instead of R10. Wall-clock ~4–5 hours instead of 8+. Same genuinely valuable findings (those came in R0–R3). Fewer redundant findings. Lower API cost.

---

## Confirmed Bugs to Fix (9 total)

### Mathematical (4)
1. Flatlined metric at 0.0 — add `all(v == 0 for v in recent_3)` guard
2. `CorrelatedFailureModel` N≥3 — replace `max()` with proper N-way joint calculation
3. Extended P-pass dead iteration — either mutate state between iterations or remove loop
4. Asymmetric detect/resolve — add resolution hysteresis (require 2+ non-pathological rounds)

### Software (5)
5. `_apply_transform()` missing 7 transforms — implement the remaining handlers
6. PAR `DOWNGRADE_ROLE` — add escalation to EXCLUDE or ABORT
7. `mu_distortion` key mismatch — use consistent key mapping
8. `findings_decline` off-by-one — change `>= 4` to `>= 3`
9. `_perf_rounds_seen` — add bounded sliding window or periodic cleanup

---

## Next Steps

1. Implement compound objective threshold as churn guard
2. Parallelise ALL rounds (not just blind)
3. Switch Codex + DeepSeek to OpenRouter
4. Fix 9 confirmed bugs
5. Run 7 with all changes — expected 5–7 rounds, ~2–3 hours

---

*Generated by CC (Claude Opus 4.6), 2026-04-02T09:17+01:00*
