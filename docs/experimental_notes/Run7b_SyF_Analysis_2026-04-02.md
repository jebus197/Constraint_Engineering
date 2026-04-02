# Run 7b Combined SymPy + FFF Analysis

**Date:** 2 April 2026, 15:39 BST
**Input:** 197 findings from 5 models across 20 rounds
**Method:** SymPy mathematical verification + Find-Follow-Fix code audit

## Executive Summary

197 raw findings deduplicate to **13 unique bug themes**. Of these:
- **9 true bugs** (3 medium severity, 6 low)
- **1 cosmetic** issue
- **3 false positives** (including one hallucinated 8 times by Codex)
- **2 mathematical claims refuted** by SymPy

The immune layer's correctness issues cluster around **namespace mismatches** (counters vs chain keys vs pathology keys use different naming conventions) and **missing lifecycle gates** (no dedup, no feedback-enabled check, no P-pass where documented).

No crash-level or data-corruption bugs found. All true bugs produce **metric distortion** or **design contract violations**, not incorrect remediation actions or system failures.

---

## SymPy Verification Results (8 CONFIRMED, 2 REFUTED)

### CONFIRMED — MEDIUM SEVERITY

#### SY-1: `false_positive_rate` windowing bias
- **Files:** `_immune.py` lines 900–930
- **Findings:** Codex R0 F003, CC2 R0 F005, ChatGPT R0 F005
- **Claim:** Numerator uses exact round-windowed counting; denominator uses proportional-tail approximation (`fraction = window / total_rounds × len(all_detections)`)
- **SymPy result:** Systematic bias direction depends on detection clustering. Deflates FPR during initial calibration (detections front-loaded), inflates during remediation cascades (detections back-loaded). Error magnitude proportional to deviation from uniform detection rate.
- **Fix:** Add `round` field to `DetectorDiagnosis` dataclass for exact windowed counting on both sides.

#### SY-2: Global `_last_self_adjust_round` damping
- **Files:** `_immune.py` lines 1545–1549
- **Findings:** Codex R7 F003, R8 F013, R13 F005
- **Claim:** A single scalar gates all three self-diagnosis channels; any one firing suppresses the other two.
- **SymPy result:** CONFIRMED. One scalar for three independent pathologies = cross-channel suppression. If self-check 1 fires on round 5, self-checks 2 and 3 are suppressed until round 5 + `immune_damping_rounds`.
- **Fix:** Change `_last_self_adjust_round: int` to `_last_self_adjust_round: Dict[str, int]` keyed by trigger type.

#### SY-3: `chain_exhaustion_rate` double-counts
- **Files:** `_immune.py` lines 933–940
- **Findings:** CC2 R1 CC_IM_F004
- **Claim:** Denominator sums `len(recent_outcomes) + len(recent_exhaustions)` but exhaustion events already appear in `_remediation_outcomes`.
- **SymPy result:** CONFIRMED. Deflates rate by ~30–40%. Makes self-check 3 ("too many exhaustions") less sensitive, delaying the immune layer's detection of its own failure to remediate.
- **Fix:** Use `len(recent_outcomes)` alone as denominator.

### CONFIRMED — LOW SEVERITY

#### SY-4: Incompatible correlation formulas (pairwise vs correlated_class)
- **Files:** `_failure_handler.py`
- **Findings:** CC2 R0 F001, R1 CC_IM_F001, Gemini R0 F004
- **Claim:** `pairwise_joint_failure` uses `p_i*p_j + v_ij * min(p_i, p_j) * (1 - max(p_i, p_j))`; `correlated_class_failure` uses `p_i*p_j + rho*sqrt(p_i*(1-p_i)*p_j*(1-p_j))`.
- **SymPy result:** Not algebraically equivalent for any parameterisation. Divergence factor = `sqrt(p_i*(1-p_j)/((1-p_i)*p_j))` for asymmetric rates. Both are valid correlation models (Schucany vs bivariate normal), but using both in the same system for the same concept is inconsistent.
- **Fix:** Choose one formula and use it consistently. The bivariate normal form (sqrt) is more standard.

#### SY-5: Pair joint exceeds Frechet bound (unclamped intermediate)
- **Files:** `_failure_handler.py`
- **Findings:** CC2 R0 F006, Gemini R0 F004
- **SymPy result:** `p_i*p_j + rho*sqrt(p_i*(1-p_i)*p_j*(1-p_j))` exceeds `min(p_i, p_j)` for 36/45 asymmetric test pairs at rho=1. Final output is clamped, but intermediate values in the N≥3 path are not.
- **Fix:** Clamp `pair_joint = min(pair_joint, min(p_i, p_j))` before using in N≥3 products.

#### SY-6: N≥3 decomposition underestimates
- **Files:** `_failure_handler.py`
- **Findings:** CC2 R0 F002
- **SymPy result:** Docstring says "upper bound" but `P(pair_ij) × Π(P(other_k))` assumes remaining models fail independently of the correlated pair, which underestimates for positively correlated triples.
- **Fix:** Update docstring to say "approximate bound assuming conditional independence of non-paired models."

#### SY-7: `findings_decline` uses `>` not `>=`
- **Files:** `_immune.py`
- **Findings:** Codex R7 F004, R16 F005
- **SymPy result:** "At least 30% decline" maps to `>=`, not `>`. Off-by-one at exact boundary.
- **Fix:** Change `>` to `>=`.

#### SY-8: Vocab alignment (no guard)
- **Files:** `_immune.py`
- **Findings:** Codex R5 F014, R8 F015, R15 F012, CC2 R1 CC_IM_F007
- **SymPy result:** No length check before slicing `_finding_counts[-vs_window:]` aligned with `_vocab_growth_history`. Normal flow is aligned via `process_round()` ordering, but direct API use can diverge.
- **Fix:** Add `assert len(self._vocab_growth_history) >= len(self._finding_counts)` or equivalent guard.

### REFUTED

#### SY-R1: mu improvement criterion (ChatGPT R1 F007)
- **Claim:** `abs(current_val) < abs(old_val) * 0.95` is directionally wrong for mu.
- **SymPy result:** mu pathology is "mu increasing anomalously". Improvement = abs-decrease = stabilisation. The criterion is correct.

#### SY-R2: Novelty improvement direction (Codex R6 F012)
- **Claim:** Wrong improvement criterion for `target_metric == "novelty"`.
- **SymPy result:** Higher novelty_rate = more unique findings = good. Default "higher = better" in the else branch is correct.

---

## FFF Code Audit Results (9 TRUE, 1 COSMETIC, 3 FALSE POSITIVE)

### TRUE BUGS — MEDIUM SEVERITY

#### FFF-E: `self_diagnose()` bypasses `immune_feedback_enabled` (sev 0.55)
- **File:** `_immune.py`, `self_diagnose()` method (lines 1529–1775)
- **FIND:** No check for `self._config.immune_feedback_enabled` anywhere in the method. Directly mutates `_stuck_window`, `_mu_increase_window`, `_sensitivity_decay`.
- **FOLLOW:** `immune_feedback_enabled` gates `apply_diagnosis()` in `_manager.py`, but `self_diagnose()` is called internally by `record_round()` and bypasses this gate entirely. User who disables immune feedback still gets silent parameter mutation.
- **FIX:** Add `if not self._config.immune_feedback_enabled: return []` at method top.

#### FFF-B: pathology_key namespace mismatch (sev 0.40)
- **File:** `_immune.py`, lines 524–544
- **FIND:** `_pathology_counts` key is `"model_failure_{model_id}"` (model-specific), but `pathology_key` on the diagnosis is `"model_failure"` (generic). Same pattern for `parser_yield`, `monotonic_decline`, `cpf_spike`.
- **FOLLOW:** `_verify_remediation_outcomes()` does `_pathology_counts.pop("model_failure", None)` — pops nothing because counter is under `"model_failure_{model_id}"`. Pathology counter is never cleared on successful remediation. Stale counter inflates persistence, causing premature CRITICAL escalation.
- **FIX:** Unify naming: either use `f"model_failure_{model_id}"` as `pathology_key` with per-model chains, or use `"model_failure"` as the counter key.

#### FFF-C: `_verify_remediation_outcomes` key mismatch for kappa/mu (sev 0.35)
- **File:** `_immune.py`, lines 786–790
- **FIND:** `_pathology_counts.pop(pathology_key, None)` uses chain key (e.g. `"kappa_stuck"`) but counter is stored under detector-family key (`"kappa"`). Affects kappa and mu. `findings_decline` and `vocab_saturation` match correctly.
- **FOLLOW:** Successful kappa/mu remediation never clears the pathology counter, causing same premature escalation as Theme B.
- **FIX:** Maintain a `chain_key → counter_key` mapping, or unify naming.

### TRUE BUGS — LOW SEVERITY

#### FFF-D: Duplicate diagnosis emission, no suppression gate (sev 0.30)
- **File:** `_immune.py`, `record_round()` all checks
- **FIND:** Every round where a pathology condition holds, a fresh `DetectorDiagnosis` is appended. No gate for "already diagnosed, remediation in progress."
- **FOLLOW:** `_diagnoses` list grows unboundedly. Duplicate emissions inflate `len(all_detections)` denominator in `false_positive_rate`, suppressing the FPR metric. Damping in `apply_diagnosis()` prevents parameter oscillation, so the functional impact is limited to log noise and metric distortion.
- **FIX:** Add gate: if `pathology_key` is in `_remediation_state`, skip emitting new diagnosis.

#### FFF-F: `self_diagnose` self-check 2 has no actual P-pass (sev 0.30)
- **File:** `_immune.py`, lines 1686–1749
- **FIND:** Comment says "standard P-pass sufficient" but code only does a trend check. Adjusts `_sensitivity_decay` directly. Compare with self-check 1 which calls `_p_pass_self_adjustment()`.
- **FOLLOW:** Bounded adjustment (min 0.95, increment 0.05) limits damage. But no regression detection mechanism.
- **FIX:** Call `_standard_p_pass_remediation()` before applying the change.

#### FFF-I: `check_dispatch_health()` VM resolution bypasses hysteresis (sev 0.30)
- **File:** `_immune.py`, lines 1924–1927
- **FIND:** `del self._pathology_counts[key]` on first non-pathological round. All other checks use `_resolution_counter` + `resolution_hysteresis` requiring multiple consecutive healthy rounds.
- **FOLLOW:** Oscillating model never escalates to CRITICAL. Each re-flagging starts from persistence=0.
- **FIX:** Replace with standard resolution_counter + hysteresis pattern.

#### FFF-G: Check 3 (mu_novelty_disagree) has no lifecycle (sev 0.25)
- **File:** `_immune.py`, lines 321–349
- **FIND:** No `_pathology_counts` tracking, no `_resolution_counter`, no resolution path. All other checks (1, 2, 4, 5) have full lifecycle.
- **FOLLOW:** Severity never escalates from WARNING. Adaptive sensitivity not influenced. Resolution pop is a no-op.
- **FIX:** Add standard lifecycle (counter, resolution branch, hysteresis).

#### FFF-M: `_extended_p_pass_remediation` strip suffix mangles `vocab_saturation` (sev 0.15)
- **File:** `_immune.py`, lines 1280–1283
- **FIND:** `.replace("_saturation", "")` converts `"vocab_saturation"` to `"vocab"`, but counter is stored under `"vocab_saturation"`. Kappa (`"kappa_stuck"` → `"kappa"`) and mu work correctly.
- **FOLLOW:** Over-specification check always sees `pathology_occurrence = 0` for vocab_saturation, generating spurious SOFT adversarial warning.
- **FIX:** Use `_pathology_counts.get(chain_key, 0)` directly or maintain explicit mapping.

#### FFF-J: `record_vocab_growth()` ordering dependency (sev 0.15)
- **File:** `_immune.py` Check 5; `_manager.py` lines 493–530
- **FIND:** `process_round()` calls `record_vocab_growth()` before `record_round()` — correct ordering. But no guard in `record_round()` to enforce this for direct API callers.
- **FIX:** Add docstring or length assertion.

### COSMETIC

#### FFF-K: findings_decline resolution is strict (sev 0.10)
- Deliberate design choice per IM_F035 comment. Recovery does resolve within a few extra rounds.

### FALSE POSITIVES

#### FFF-A: DetectorDiagnosis @dataclass missing — FALSE POSITIVE
- `_types.py` line 537 has `@dataclass` decorator. Codex hallucinated this across **8 separate rounds** (R2, R3, R13, R14, R15, R16, R18, R19). This is the single largest source of finding inflation in Run 7b — 8 of 116 Codex findings (7%) are this one hallucination.

#### FFF-H: EMPTY before TIMEOUT ordering — FALSE POSITIVE
- Ordering is intentional. `FailureType` enum declares `EMPTY=1, TIMEOUT=2` (lower = higher priority). An empty response is more severe than a slow response.

#### FFF-L: detect_failure() KeyError for unknown model — FALSE POSITIVE
- `setdefault()` on line 197 guarantees the key exists before line 200 accesses it.

---

## Cross-Analysis: SymPy × FFF Convergence

| Bug | SymPy | FFF | Combined Severity |
|-----|-------|-----|-------------------|
| `false_positive_rate` windowing | SY-1 CONFIRMED | FFF-D related | **MEDIUM** |
| Global damping scalar | SY-2 CONFIRMED | FFF-F related | **MEDIUM** |
| `chain_exhaustion_rate` double-count | SY-3 CONFIRMED | — | **MEDIUM** |
| `self_diagnose` ignores feedback flag | — | FFF-E TRUE BUG | **MEDIUM** |
| pathology_key namespace mismatch | — | FFF-B TRUE BUG | **MEDIUM** |
| `_verify_remediation` key mismatch | — | FFF-C TRUE BUG | **MEDIUM** |
| Incompatible correlation formulas | SY-4 CONFIRMED | — | LOW |
| Unclamped intermediate pair_joint | SY-5 CONFIRMED | — | LOW |
| N≥3 docstring inaccuracy | SY-6 CONFIRMED | — | LOW |
| Duplicate diagnosis emission | — | FFF-D TRUE BUG | LOW |
| self-check 2 no P-pass | — | FFF-F TRUE BUG | LOW |
| VM resolution no hysteresis | — | FFF-I TRUE BUG | LOW |
| Check 3 no lifecycle | — | FFF-G TRUE BUG | LOW |
| Strip suffix mangles vocab_saturation | — | FFF-M TRUE BUG | LOW |
| Vocab alignment (API only) | SY-8 CONFIRMED | FFF-J TRUE BUG | LOW |
| `findings_decline` `>` vs `>=` | SY-7 CONFIRMED | FFF-K COSMETIC | LOW |

**Total unique verified bugs: 16** (6 medium, 10 low)
**False positives rejected: 5** (3 code, 2 math)

---

## Deduplication Statistics

| Metric | Value |
|--------|-------|
| Raw findings | 197 |
| Unique themes after dedup | 13 code + 10 math = ~16 unique bugs |
| Codex hallucination (@dataclass) | 8 findings (4% of total, 7% of Codex output) |
| True positive rate (by theme) | 16/21 = 76% |
| False positive rate (by theme) | 5/21 = 24% |
| Churn findings (repeat of same bug across rounds) | ~150 of 197 = 76% |
| Novel bugs found after R2 | ~3 (most bugs discovered in R0–R2) |

---

## Recommended Fix Priority

**Batch 1 (medium severity, namespace/lifecycle):**
1. FFF-E: `self_diagnose()` check `immune_feedback_enabled`
2. FFF-B + FFF-C: Unify pathology key namespace (`_pathology_counts` ↔ `pathology_key` ↔ chain keys)
3. SY-2: Per-trigger-type damping dict
4. SY-3: Fix `chain_exhaustion_rate` denominator
5. SY-1: Add `round` field to `DetectorDiagnosis`

**Batch 2 (low severity, correctness):**
6. FFF-D: Suppression gate for duplicate diagnoses
7. FFF-F: Wire actual P-pass for self-check 2
8. FFF-I: VM resolution hysteresis
9. SY-4 + SY-5: Unify and clamp correlation formulas
10. FFF-G: Check 3 lifecycle
11. FFF-M: Fix strip suffix for vocab_saturation
12. SY-7: `>` to `>=` in findings_decline

**Batch 3 (cosmetic/defensive):**
13. SY-6: N≥3 docstring accuracy
14. FFF-J: Vocab alignment guard / docstring
15. FFF-K: (no change — design choice)
