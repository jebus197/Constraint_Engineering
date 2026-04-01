# Run 5 — Substantive Findings (Clustered)

**Date:** 1 April 2026, 16:33 UTC
**Source:** 155 corrected findings from 5 models × 5 rounds
**Method:** Content-based clustering — same bug found by different models grouped together
**Total unique bug clusters:** 31
**Independently discovered (2+ models):** 18 (58%)

---

## Critical Bugs (severity ≥ 0.85) — 16 clusters

### 1. Adaptive Sensitivity Window — Inverted Direction (AW-1)

**Severity:** 0.94 · **Found by:** CC2, ChatGPT, Codex (3 models independently)

The `effective_window()` formula moves sensitivity in the wrong direction.
`decay^resolved` *shrinks* the window after false alarms (should widen — less
sensitive). `(1 + growth * persistent)` *grows* the window for persistent
pathologies (should narrow — more sensitive). The detector becomes
trigger-happy after false positives and unresponsive to real problems.
**Corrupts all downstream detection thresholds.**

### 2. FailureHandler Not Idempotent (FH-1)

**Severity:** 1.00 · **Found by:** Gemini, ChatGPT (2 models)

If `get_recovery()` is called twice for the same round (network retry),
`same_type_count` increments because the first call already appended to
`_failure_history`. Causes false escalations to ABORT/EXCLUDE from retry
artifacts alone.

### 3. LOG_ONLY Violates CDSFL Hard Constraint (FH-3)

**Severity:** 1.00 · **Found by:** Gemini, DeepSeek, CC2 (3 models)

`get_recovery()` returns `LOG_ONLY` for non-repeated UNDERPERFORM and as
the default fallback for unknown failure types. Violates the explicit CDSFL
constraint that "catch-and-log-only is NOT handling." Failed models continue
receiving task allocations with no intervention.

### 4. detect_failure Not Idempotent (FH-2)

**Severity:** 0.90 · **Found by:** Gemini, CC2 (2 models)

`detect_failure()` appends to `_perf_history` on every call. Duplicate
deliveries inflate the persistence window, triggering false UNDERPERFORM.

### 5. Mu Persistence Never Incremented (MU-1)

**Severity:** 0.93 · **Found by:** ChatGPT, Codex, CC2 (3 models)

Check 2 (mu increasing) creates a diagnosis but never calls
`_pathology_counts["mu"] += 1`. The mu pathology can never benefit from
adaptive sensitivity escalation. Check 1 (kappa stuck) correctly increments
its counter — this is an omission, not a design choice.

### 6. False Positive Rate Denominator Broken (FP-1)

**Severity:** 0.92 · **Found by:** CC2, DeepSeek (2 models)

The windowed denominator assumes diagnoses are uniformly distributed across
rounds. Pathological rounds produce clusters, making the approximation
wildly inaccurate. The false positive rate becomes semantically meaningless.

### 7. Deferred Remediations Bypass Safety Envelope (PR-2)

**Severity:** 0.91 · **Found by:** Codex

Approved deferred remediations are applied as if they happened at the
original diagnosis round, bypassing the safety envelope that AUTO
remediations must pass through. Creates an unguarded path for parameter
mutations.

### 8. Correlated Failure Model Uses Wrong Formula (CF-1)

**Severity:** 0.90 · **Found by:** Gemini, CC2 (2 models)

The >2 model path uses `p_min^2 + rho * p_min * (1 - p_min)` instead of
calling `pairwise_joint_failure()` with actual per-model probabilities.
Systematically underestimates joint failure risk. Pre-dispatch feasibility
checks become unsafely permissive.

### 9. Vocab Saturation Hardcoded Window (VS-1)

**Severity:** 0.89 · **Found by:** ChatGPT, CC2, DeepSeek (3 models)

Code checks `len >= 3` using `[-3:]` while config defines
`vocab_sustained_window=5`. Fires at 3 rounds instead of configured 5.

### 10. Record_model_round Bypasses Consolidation (DC-1)

**Severity:** 0.89 · **Found by:** CC2, ChatGPT (2 models)

`record_model_round()` appends directly to `_diagnoses` while
`record_round()` uses a separate collection. No ordering contract.
`false_positive_rate` sees inconsistent counts depending on call order.

### 11. Role Reassignment Uses Stale Fingerprints (PR-1)

**Severity:** 0.89 · **Found by:** Codex

In `process_round()`, role reassignment executes before
`update_fingerprints()`. Decisions use capability data from the previous
round, not the current one.

### 12. Chain Index Exceeds Chain Length (RV-1)

**Severity:** 0.88 · **Found by:** CC2 (rounds 0, 1, 2)

When remediation is INEFFECTIVE, `chain_idx` increments without bounds
checking. Exceeding chain length causes IndexError or creates zombie entries
that persist and are re-verified indefinitely.

### 13. Improvement Direction Wrong for Non-Mu Metrics (RV-2)

**Severity:** 0.87 · **Found by:** CC2, ChatGPT (2 models)

Default `improved = current_val > old_val` is applied universally.
For `vocab_growth`, success should be measured against threshold, not as
raw increase. A threshold-lowering fix resolves the pathology but is
judged "not improved."

### 14. Failure History Uses Unbounded Lifetime (FH-6)

**Severity:** 0.85 · **Found by:** CC2, Gemini (2 models)

`same_type_count` sums ALL historical failures, not recent window.
A model that recovered fully will still carry old failure counts,
causing premature escalation on the next single failure.

### 15. Self-Diagnosis Lacks Damping Enforcement (SD-2)

**Severity:** 0.85 · **Found by:** Gemini, DeepSeek (2 models)

`self_diagnose()` does not check `immune_damping_rounds` before applying
adjustments. Can fire on consecutive rounds, creating runaway parameter
oscillation.

### 16. Diagnosis Ordering Contract Missing (DC-2)

**Severity:** 0.85 · **Found by:** CC2

The immune layer's correctness depends on `record_model_round()` being
called before `record_round()`, but this is neither documented nor enforced.

---

## Significant Bugs (severity 0.50–0.84) — 15 clusters

| ID | Severity | Models | Summary |
|----|----------|--------|---------|
| PK-1 | 0.91 | CC2, ChatGPT, DeepSeek | Mu distortion diagnosis missing `pathology_key` — unroutable |
| PK-2 | 0.84 | CC2, ChatGPT | parser_yield, monotonic_decline, cpf_spike missing `pathology_key` |
| PR-3 | 0.84 | Codex, DeepSeek | Regression detection is advisory only — "first do no harm" has no enforcement |
| MU-2 | 0.83 | Codex, DeepSeek, CC2 | Mu detection uses inconsistent abs vs signed comparison |
| AW-2 | 0.82 | CC2 | effective_window has no upper bound — can prevent detection entirely |
| VS-2 | 0.82 | ChatGPT, CC2 | Vocab saturation has no resolution path — persists forever |
| DM-1 | 0.82 | DeepSeek | `_apply_transform` never enforces `immune_damping_rounds` cooldown |
| FH-4 | 0.81 | CC2, ChatGPT | DOWNGRADE_ROLE not propagated to RoleAssignment/LoadBalancer |
| AW-3 | 0.80 | CC2 | `_pathology_counts` keyed inconsistently — persistent count always 0 for per-model keys |
| PK-3 | 0.76 | CC2, ChatGPT | `_REMEDIATION_CHAINS` never defined — entire remediation system inoperative |
| VM-2 | 0.76 | Gemini, ChatGPT | Verification pathology state leaks permanently — no reset on recovery |
| FH-7 | 0.75 | CC2, DeepSeek | Reallocation depth counter never resets between rounds |
| SD-1 | 0.75 | CC2 | Self-diagnosis can apply contradictory adjustments simultaneously |
| RV-4 | 0.74 | ChatGPT | Chain exhaustion does not clear remediation state |
| DM-2 | 0.70 | DeepSeek | Damping keying ambiguous — per-model adjustment blocks all models |
| VM-1 | 0.65 | CC2, DeepSeek | z-score threshold statistically meaningless for N=3 |
| FH-5 | 0.65 | CC2 | PM downgrade is a no-op — only COL→PAR implemented |
| MU-3 | 0.68 | CC2 | Mu resolution resets on wrong compound condition |
| FD-1 | 0.55 | CC2 | Findings decline threshold hardcoded, inappropriate for small pools |
| FD-2 | 0.68 | CC2 | Resolution condition uses wrong comparison — creates dead zone |
| SD-3 | 0.50 | CC2 | Simplest-sufficient candidate ordering reversed |
| RV-3 | 0.85 | CC2 | Remediation success never clears pathology_counts |

---

## Thematic Summary

The immune layer has **three systemic failure modes**, each spanning
multiple clusters:

1. **State leaks** (AW-3, RV-3, RV-4, VM-2, FH-5, FH-6, FH-7, VS-2):
   Pathology counts, remediation state, failure history, and reallocation
   depth accumulate monotonically and are never cleaned up. The system
   becomes increasingly dysfunctional as rounds progress.

2. **Direction inversions** (AW-1, RV-2, MU-2, SD-3): Multiple subsystems
   have their sensitivity, improvement, or ordering logic backwards. The
   most impactful is AW-1 (effective_window), which propagates through all
   detection thresholds.

3. **Missing contracts** (DC-1, DC-2, PK-1, PK-2, PK-3, FH-4): The immune
   subsystems were developed independently and their interfaces are not
   formally specified. Call ordering, key naming, state propagation, and
   remediation routing all depend on implicit assumptions that are violated
   in practice.
