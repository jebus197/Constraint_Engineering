# Exp 39-0 Gate — Post-Mortem Report

**Date:** 14 April 2026
**Experiment:** exp39_0_gate (infrastructure gate test)
**Target:** `bench/runner_core.py` (38K)
**Models:** CC2 (the CLI-piped Claude Opus 4.6 instance), Codex GPT-5.4, ChatGPT GPT-5.4, Gemini 3.1 Pro, DeepSeek R1-0528
**Rounds:** 6 (R0-R5), terminated by wall clock cap (4388s / ~73 min)
**Convergence:** Never reached (gate too strict)

---

## Executive Summary

Exp 39-0 was a gate test for infrastructure validation. It ran to wall clock cap, producing 111 findings (41 canonical, 2 phantom from parser bugs, effective 39). Gamma (the depletion coefficient measuring novel-finding fall-off across rounds) reached 0.461, indicating strong depletion. R_k (the iterative residual-risk self-assessment after round k) mathematical model adoption was 5/5 (100%). The experiment exposed 8 bugs across 4 severity levels. Two bugs were fixed mid-session (race condition, double-counting). Six remain for fixing before Exp 39-1.

The pipeline's immune system works correctly at the per-step level. The systemic failures are all integration bugs — format mismatches, attribute name mismatches, and over-strict thresholds. No architectural redesign is needed.

---

## Bugs Found — Priority Order

### P0 (blocking, fix before next run)

**1. S_k (the severity/stringency tristate gate) format mismatch (0% ADMISSIBLE across all rounds)**
- The prompt tells models format A (`====` separator, `>>>> REPLACE` closer)
- The parser reconstructs format B (`==== REPLACE` separator, `>>>>` closer)
- The S_k evaluator checks for format C (bare `====` separator)
- Result: every finding fails S_k evaluation, 0% fix verification
- Fix: 5 lines in `parse_search_replace_blocks()` at `reference_runner.py` line 2094
- Impact: until fixed, no proposed fix can ever be verified

**2. Parser emitting source code as finding IDs**
- `CC2_full_id,` — Python variable name from `parse_findings()` leaks as finding ID
- `DeepSeek_f"{model_id}_UNSTRUCTURED"` — unevaluated f-string template leaks as alias
- Creates 2 phantom canonical entries (C0023, C0038)
- Fix: parser regex/fallback path in `runner_core.py`

**3. Convergence gate structurally unreachable**
- `max_open_crit_high` defaults to 0 (zero open challenges allowed)
- With 41 canonical entries and only 6 closures, this never triggers
- The config documents `gamma >= 0.30 OR 3 consecutive rounds with 0 novel CRITICAL` but this isn't implemented
- Fix: set threshold to 3-5, or implement gamma-based alternative path

### P1 (important, fix before Exp 39-1)

**4. Macrophage is blind — verdict wiring broken**
- `immune_result.cell_verdicts` attribute doesn't exist or extracted objects lack `.verdict`/`.confidence`
- All 6 rounds produced zero observations, zero anomalies
- Three monitoring capabilities implemented but never wired (provenance, gate_stats, ouroboros_metrics)
- Fix: verify attribute name, add diagnostic log when verdict list empty

**5. DeepSeek decomposition trap**
- Decomposed every round (6/6), 67% of chunks returned 0 chars
- Parser captures only 55% of actual findings (12 of 22) — format incompatibility
- Self-confirmation loop: resubmits findings because no feedback that they were registered
- Fingerprint bootstrapping trap: chunk successes don't prevent future decomposition
- Fix: multiple — fingerprint override, parser format, feedback loop, reasoning token capture

**6. DeepSeek parser for markdown bold headers**
- DeepSeek uses `**Finding:**` format that the parser doesn't handle
- R5: parsed 1 of 6 actual findings (parser catastrophe)
- 9 genuinely novel findings across the experiment were lost to parsing

### P2 (desirable, improves quality)

**7. Autoimmune false alarm in late rounds**
- RT v2 flags 100% removal rate as AUTOIMMUNE every round from R1
- All removals are legitimate duplicates (rejected=0, duplicated=N)
- Fix: split flag into AUTOIMMUNE_REJECTION vs DEPLETION_EXPECTED

**8. ITC degradation false trigger**
- Codex and CC2 hit 5 consecutive DEGRADATION flags
- Caused by verdict-heavy output deflating parse_yield
- Fix: count verdicts as valid output in parse_yield calculation

---

## Previously Fixed (this session)

**9. Race condition in `_load_fingerprint_cache()`** (FIXED, verified 793 tests)
- `_fp_cache = {}` set before loading files, concurrent threads saw empty dict
- Caused ChatGPT, Gemini, DeepSeek to be incorrectly decomposed in R2
- Fix: build local cache, then atomic assignment

**10. Double-counting in `_total_payload_chars`** (FIXED, verified 793 tests)
- `full_code` added twice (once embedded in `prompt`, once separately)
- Inflated payload by ~64K chars
- Fix: `_total_payload_chars = len(model_cdsfl) + len(prompt)`

---

## Shadow Systems Assessment

### Ouroboros Cell (O1)
- **Working correctly** in shadow mode
- Active only in R0 (4 UNCERTAIN findings as targets), empty R1-R5 (no targets — all DUPLICATE)
- Query quality poor: uses internal finding IDs as search terms instead of descriptions
- Source rotation not implemented (arXiv only, never Semantic Scholar)
- API calls fall back to shadow_mock (arxiv package likely not installed)

### Macrophage
- **Effectively blind** — see Bug #4 above
- Structurally correct but receives no usable verdict data
- Three monitoring modes implemented but unwired

---

## R_k Mathematical Model

**5/5 models computing R_k (100%).** Not regressed from Exp 37.

| Model | R_k Quality | Falsification Quality |
|-------|------------|----------------------|
| CC2 | Detailed, correct | Strong |
| Codex | Detailed, correct | Very strong |
| ChatGPT | Detailed, correct | Strong |
| Gemini | Abbreviated, fixed nu_eff | Good |
| DeepSeek | Present, has errors | Weak-moderate |

SymPy/z3 tool execution is 0% — models cannot execute code in API dispatch mode. This is an infrastructure limitation, not a regression. Manual R_k arithmetic is the current mechanism.

---

## Key Metrics

| Metric | Value | Assessment |
|--------|-------|------------|
| Gamma final | 0.461 | Strong depletion — correct |
| Total findings | 111 | Normal for 6 rounds |
| Canonical entries | 41 (39 real + 2 phantom) | Reasonable yield |
| Novel yield R0 to R5 | 100% to 12.5% | Correct depletion curve |
| S_k ADMISSIBLE | 0% | BUG — format mismatch |
| Convergence gate | Failed all rounds | BUG — threshold=0 |
| R_k adoption | 5/5 (100%) | Matches Exp 37 |
| DeepSeek round time | 397-1125s (avg 657s) | 7-22x slower than fastest |
| Test suite | 793 passed, 0 failed | Clean |

---

## Timing Per Model (seconds)

| Round | CC2 | Codex | ChatGPT | Gemini | DeepSeek |
|-------|-----|-------|---------|--------|----------|
| R0 | 213 | 133 | 196 | 223 | 397 |
| R1 | 289 | 148 | 161 | 291 | 428 |
| R2 | 396 | 73 | 97 | 384 | 748 |
| R3 | 349 | 48 | 78 | 263 | 836 |
| R4 | 167 | 75 | 38 | 176 | 409 |
| R5 | 330 | 51 | 52 | 220 | 1125 |

---

## Output Sizes (chars)

| Round | CC2 | ChatGPT | Codex | DeepSeek | Gemini |
|-------|------|---------|-------|----------|--------|
| R0 | 12,712 | 24,431 | 18,725 | 20,209 | 11,306 |
| R1 | 16,607 | 19,424 | 22,272 | 22,703 | 14,605 |
| R2 | 17,398 | 13,623 | 14,166 | 10,750 | 16,094 |
| R3 | 16,885 | 14,404 | 11,847 | 12,642 | 17,671 |
| R4 | 18,464 | 8,071 | 21,686 | 8,178 | 4,777 |
| R5 | 8,231 | 13,065 | 12,689 | 16,964 | 8,362 |

---

## Recommendations for Exp 39-1

1. Fix P0 bugs 1-3 (S_k format, parser IDs, convergence gate)
2. Fix P1 bug 4 (Macrophage wiring)
3. Fix DeepSeek fingerprint to prevent decomposition, or switch to specialist role
4. Fix DeepSeek parser for markdown bold format
5. Consider: implement gamma-based convergence as alternative path
6. Consider: add post-parse R_k validation (~10 LOC)
7. Do NOT start Exp 39-1 until HIL reviews this report

---

## Detailed Analysis Files

All in `bench/logs/exp39_0_gate_20260413T193320Z/`:
- `analysis_maths_usage.md` — per-model mathematical tool usage
- `analysis_deepseek_performance.md` — DeepSeek decomposition impact and quality
- `analysis_shadow_systems.md` — O1 ouroboros and Macrophage assessment
- `analysis_immune_convergence.md` — immune pipeline and convergence gate analysis
- `analysis_cross_verification.md` — data integrity and anomaly findings
- `exp39_0_gate_report.json` — machine-readable experiment report
