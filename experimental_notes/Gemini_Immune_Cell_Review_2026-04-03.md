# Gemini CDSFL Review of All Immune Cell Types

**Date:** 3 April 2026, 23:20 BST
**Method:** 4 conversations with Gemini 3.1 Pro under full CDSFL/FFF, 3 rounds each
**Verification:** SymPy — 5/5 mathematical claims confirmed correct
**Conversations:** `/tmp/gemini_dc_history.json`, `/tmp/gemini_nk_history.json`, `/tmp/gemini_ht_history.json`, `/tmp/gemini_rt_history.json`

---

## Dendritic Cell (Triage/Classification)

**Status:** Convergence declared. Incremental fixes, not redesign.

| # | Finding | Severity | Verified |
|---|---------|----------|----------|
| 1 | `UNCATEGORISED` in enum but never used — all unmatched findings dumped to `CODE_BEHAVIORAL` default | 0.8 | Logic ✓ |
| 2 | `_MATH_PATTERN` matches `+`, `-`, `=`, `<`, `>` as standalone chars — hijacks English text to B-Cell | 0.9 | Logic ✓ |
| 3 | No pattern for `file.py:line` citations — strongest code signal is invisible to triage | 0.8 | Logic ✓ |

**Proposed fixes:**
- Narrow `_MATH_PATTERN` to require equation-like context (both sides of operator)
- Add `_CITATION_PATTERN` for `file.py:NNN` and `line NNN`
- Use `UNCATEGORISED` for low-confidence matches instead of defaulting to `CODE_BEHAVIORAL`
- Add classification confidence (gating, not verdict multiplier)

---

## NK Cell (Pattern Recognition/Dedup)

**Status:** Convergence declared. Incremental fixes.

| # | Finding | Severity | Verified |
|---|---------|----------|----------|
| 1 | FP match path doesn't `continue` — falls through to anomaly detection, producing conflicting verdicts | 0.7 | Code ✓ |
| 2 | `tau_sim=0.33` is below max genuinely-different similarity (0.553) — may over-dedup | 0.7 | SymPy ✓ |
| 3 | No intra-round dedup — same hallucination ×10 in one round all pass through | 0.6 | Logic ✓ |
| 4 | Future: dynamic immune memory needs graduated patterns + decay to prevent autoimmune lock-in | 0.6 | Logic ✓ |

**Proposed fixes:**
- Add `continue` after FP match (and update `tf` state)
- Investigate `tau_sim` empirically: compare dedup accuracy at 0.33 vs 0.55 vs 0.60
- Add intra-round dedup with dynamic `seen_findings` set
- Future: graduated pattern learning with count threshold + round decay

---

## Helper T Cell (Verdict Synthesis)

**Status:** Convergence NOT declared. Redesign needed.

| # | Finding | Severity | Verified |
|---|---------|----------|----------|
| 1 | `else` block is dead code: `Pr + Pc = 1` always, so `Pr < 0.6` ⟹ `Pc > 0.4` | 0.9 | **SymPy ✓** |
| 2 | Rejection requires `R ≥ 1.5C` — 50% stronger than confirmation to win | 0.9 | **SymPy ✓** |
| 3 | Orthogonal ganging: two weak confirms (0.5+0.5=1.0) defeat one strong reject (0.9) | 0.8 | **SymPy ✓** |

**Mathematical proof (dead else block):**
```
Let C = confirm_weight, R = reject_weight, T = C + R
Pr = R/T, Pc = C/T
Pr + Pc = R/T + C/T = (R+C)/T = T/T = 1

If Pr < 0.6, then Pc = 1 - Pr > 1 - 0.6 = 0.4
∴ The elif (Pc >= 0.4) always fires when if (Pr >= 0.6) fails
∴ The else block is unreachable
```

**Proposed alternatives for Run 12:**
- **Option A (Max Signal):** Trust the strongest individual verdict. If cells evaluate independent domains, the most confident cell's verdict should dominate.
- **Option B (Log-Odds):** Convert confidence → log-odds before summing (Naïve Bayes). Mathematically sound aggregation that preserves signal magnitude.

---

## Regulatory T Cell (Meta-verification/Circuit Breaker)

**Status:** Convergence declared. Two mathematical fixes needed.

| # | Finding | Severity | Verified |
|---|---------|----------|----------|
| 1 | `removal_rate` includes duplicates but Check 1 only uses `rejected/total` — NK over-dedup undetected | 0.7 | Logic ✓ |
| 2 | Check 3 denominator mismatch: `model_counts` from `triaged`, rejections from `final_verdicts` | 0.7 | **SymPy ✓** |
| 3 | Binary override is correct (circuit breaker design) — targeted suppression is role creep | <0.5 | Resolved |

**Proposed fixes:**
- Check 1: use combined `removal_rate` (rejected + duplicated) against threshold
- Check 3: build `model_counts` from intersection of `triaged` and `final_verdicts`

---

## Cross-Cell Summary

| Cell | Verdict | Action |
|------|---------|--------|
| Dendritic | Fix regexes, add citation pattern | Run 12 |
| Cytotoxic T | Falsifier architecture (shadow built) | Run 11 shadow, Run 12 active |
| B-Cell | AST-grounded SMT-LIB (shadow built) | Run 11 shadow, Run 12 active |
| NK Cell | Fix state leak, investigate tau_sim | Run 12 |
| **Helper T** | **Redesign voting algebra** | **Run 12 (critical)** |
| Regulatory T | Fix removal rate + denominator | Run 12 |

The Helper T Cell finding is the most significant. The voting algebra creates a systematic confirmation bias that explains the pipeline's tendency toward rubber-stamping findings.
