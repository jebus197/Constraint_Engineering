# SymPy Verification of Run 7b Mathematical Claims

**Date:** 2 April 2026
**Scope:** 10 key mathematical claims from Run 7b findings verified against immune layer code in `bench/dm/`
**Result:** 8 CONFIRMED, 2 REFUTED, 0 INCONCLUSIVE

---

## Confirmed Findings

### Claim 1: `false_positive_rate` Windowing Bias — CONFIRMED (MEDIUM)

**Finding IDs:** Multiple (Codex, CC2, ChatGPT)
**Files:** `_immune.py` lines 900–930

The `false_positive_rate` property uses a proportional-tail approximation for the denominator:
```python
fraction = min(1.0, window / total_rounds)
windowed_count = max(1, int(len(all_detections) * fraction))
```
But the numerator uses exact round-based filtering:
```python
natural_resolutions = sum(1 for fp in history if fp["round"] >= start_round)
```

**SymPy result:** Error = `(d_early + d_late) * w/T - d_late` = `d_early * w/T - d_late * (T-w)/T`. Zero only when detections are uniformly distributed. With early clustering (common during initial calibration), the denominator is overestimated → FPR deflated. With late clustering (remediation cascade), FPR inflated.

**Fix:** Add a `round` field to `DetectorDiagnosis` and use exact windowed counting for the denominator.

---

### Claim 2: `pairwise_joint_failure` vs `correlated_class_failure` Formula Inconsistency — CONFIRMED (MEDIUM)

**Finding IDs:** CC2 R0 F001, R1 CC_IM_F001, Gemini R0 F004
**Files:** `_failure_handler.py` lines 488–523 vs 525–611

Two different correlation terms for the same concept:
- **pairwise:** `v_ij * min(p_i, p_j) * (1 - max(p_i, p_j))`
- **correlated_class:** `rho * sqrt(p_i*(1-p_i)*p_j*(1-p_j))`

**SymPy result:** Algebraically identical only when `p_i == p_j`. For `p_i=0.1, p_j=0.3, rho=v=0.8`: pairwise gives 0.086, correlated gives 0.140. Difference factor: `sqrt(p_i*(1-p_j)/((1-p_i)*p_j))`. The correlated formula is the standard bivariate normal copula term; the pairwise formula is a heuristic.

**Fix:** Unify to one formula. The sqrt formula is mathematically standard but needs per-pair clamping.

---

### Claim 3: N≥3 Decomposition Not a True Upper Bound — CONFIRMED (LOW)

**Finding IDs:** CC2 R0 F002
**Files:** `_failure_handler.py` lines 584–609

The docstring (line 532) claims "conservative upper bound" but the decomposition `P(pair_ij) × Π(P(other_k))` treats remaining models as independent of the correlated pair. For 3 models with `rho=0.9, p=0.5`: decomposition gives 0.2375 but the true probability is higher because `P(k fails | i,j fail) > P(k fails)`.

**Fix:** Correct docstring from "upper bound" to "approximation", or implement inclusion-exclusion.

---

### Claim 4: Intermediate `pair_joint` Exceeds Fréchet Bound — CONFIRMED (LOW)

**Finding IDs:** CC2 R0 F006
**Files:** `_failure_handler.py` lines 577–582

**SymPy result:** With `p_i=0.3, p_j=0.8, rho=1.0`, the sqrt formula gives 0.423 > `min(0.3, 0.8) = 0.3`. Critical rho for these rates: 0.327. Systematic scan found 36/45 asymmetric pairs violate the bound at `rho=1.0`. The final clamp at line 611 catches this, but intermediate values in the N≥3 path are unclamped.

**Fix:** Add `min(joint, min(p_i, p_j))` clamp at lines 581–582.

---

### Claim 5: `chain_exhaustion_rate` Denominator Double-Counts — CONFIRMED (MEDIUM)

**Finding IDs:** CC2 R1 CC_IM_F004
**Files:** `_immune.py` lines 933–940, 775–809

```python
total = len(recent_outcomes) + len(recent_exhaustions)  # BUG
rate = len(recent_exhaustions) / max(1, total)
```

`record_remediation_outcome()` is called at line 775 for **all** outcomes. `record_chain_exhaustion()` is called at line 809 for exhaustions specifically. An exhaustion event appears in both `_remediation_outcomes` and `_chain_exhaustion_history`, inflating the denominator.

**Example:** 5 attempts, 2 exhaustions → `total = 5+2 = 7` (should be 5), rate = 2/7 = 0.286 (should be 2/5 = 0.4).

**Fix:** `total = len(recent_outcomes)` — exhaustions are already included.

---

### Claim 6: `findings_decline` Threshold `>` vs `>=` — CONFIRMED (LOW)

**Finding IDs:** Multiple Codex findings
**Files:** `_immune.py` lines 357–361

Comment says "At least 30% decline" but code uses `total_decline > decline_threshold` (strict `>`). At the exact boundary (`recent_3 = [10, 7, 7]`), `3 > 3` is `False` but `3 >= 3` is `True`.

**Fix:** Change `>` to `>=`.

---

### Claim 8: Global `_last_self_adjust_round` Suppresses All Channels — CONFIRMED (MEDIUM)

**Finding IDs:** Multiple models
**Files:** `_immune.py` lines 1545–1549, 1643, 1719

`_last_self_adjust_round` is a single scalar. The damping check exits `self_diagnose()` entirely:
```python
if current_round - self._last_self_adjust_round < damping_rounds:
    return diagnoses  # Exits ALL self-checks
```
When any one self-check fires, all three channels (success rate, false positive, chain exhaustion) are suppressed for `immune_damping_rounds` rounds.

**Fix:** Change to `Dict[str, int]` keyed by trigger type for independent per-channel damping.

---

### Claim 10: `_vocab_growth_history` / `_finding_counts` Alignment — CONFIRMED (LOW)

**Finding IDs:** Multiple findings
**Files:** `_immune.py` lines 412–416, 477–479; `_manager.py` line 495

No explicit guard ensures both lists have the same length before slicing in Check 5. Normal flow keeps them aligned (both appended in sequence during `process_round`), but an exception between `record_vocab_growth()` and `record_round()` causes silent divergence.

**Fix:** Add `min(len(self._vocab_growth_history), len(self._finding_counts))` alignment check before slicing.

---

## Refuted Findings

### Claim 7: `mu` Improvement Criterion Directionally Wrong — REFUTED

**Finding IDs:** ChatGPT R1 F007

The claim conflates normal-operation semantics (higher mu = more value = good) with pathology-remediation context (mu was increasing anomalously → decrease is the fix). `abs(current_val) < abs(old_val) * 0.95` correctly checks for stabilisation after an anomalous mu increase.

---

### Claim 9: Wrong Improvement Direction for Novelty — REFUTED

**Finding IDs:** Codex R6 F012

`novelty_rate` = fraction of novel findings. Higher = more unique findings = good. `improved = current_val > old_val` is correct — remediation for a novelty-dropping pathology should increase novelty.

---

## Priority Summary

| Severity | Count | Claims |
|----------|-------|--------|
| MEDIUM   | 3     | 1 (FPR windowing), 5 (chain exhaustion), 8 (global damping) |
| LOW      | 5     | 2 (formula inconsistency), 3 (docstring), 4 (Fréchet), 6 (>=), 10 (alignment) |
| REFUTED  | 2     | 7 (mu direction), 9 (novelty direction) |

**Recommended fix order:** Claims 5 → 8 → 1 → 4 → 2 → 6 → 10 → 3
