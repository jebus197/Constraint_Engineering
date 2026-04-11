# Experiment 38 Fix Cycle — 10 April 2026

## Overview

Exp 38 Round 0 produced 26 findings, 14 CONFIRMED (70% true positive). The immune
pipeline returned UNEVALUABLE for all fix evaluations. Three gaps identified, all fixed.
Additionally, all 14 confirmed runner bugs were fixed before restart.

**Total: 17 fixes. 714 tests pass (was 690).**

---

## Immune/Endocrine Fixes

### Fix 1: Endocrine SEARCH/REPLACE Parser

**File:** `bench/endocrine.py` — `_apply_fix_to_source()`

**Problem:** CC2 produces structured `<<<< SEARCH ... ==== ... >>>> REPLACE` blocks.
The endocrine fix evaluator had three strategies (prose replace, whole-file, line hints)
but none handled this format. Runner had `parse_search_replace_blocks()` but importing
it would create a circular import.

**Fix:** Inline state machine parser added as Strategy 0 (tried first). Extracts
search/replace pairs from fix text, applies each to source via `str.replace()`.
No external dependencies.

**Tests:** 2 new (`test_search_replace_blocks`, `test_search_replace_blocks_multiple`).

### Fix 2: Target File Fallback

**File:** `bench/endocrine.py` — `_find_target_file()`

**Problem:** CC2 doesn't include `.py` paths in finding descriptions. Regex returns
no matches → function returns None → fix marked UNEVALUABLE.

**Fix:** When `len(source_paths) == 1` and no regex match, return `source_paths[0]`.
Multiple paths with no match still returns None (ambiguous).

**Tests:** 2 updated (`test_no_match_single_path_falls_back`, `test_no_match_multiple_paths_returns_none`).

### Fix 3: Formalisation Agent Promotion

**File:** `bench/immune_agents.py` — `formalisation_agent()`

**Problem:** Shadow-only. Extracted preconditions and logged comparisons but produced
no output feeding into the pipeline. False rejections from B-Cell context erasure were
not corrected.

**Fix:** Returns `Tuple[List[Dict], List[CellVerdict]]`. When B-Cell REJECTED a claim
with extractable preconditions, produces UNCERTAIN counter-verdict (confidence 0.45).
Counter-verdicts added to `all_verdicts` in `run_immune_pipeline()` before reconciliation gate.

**Tests:** 2 updated (`test_runs_on_math_findings_with_counter_verdicts`, `test_skips_behavioural`).

---

## Runner Bug Fixes (14 Confirmed Findings)

### Status Transition Chain

| Finding | Description | Fix | Line(s) |
|---------|-------------|-----|---------|
| F2/F5/F9 | `add_verdict()` corrupts `last_status_change_round` | Remove timer update from `add_verdict`; only `resolve()` updates timer | 305 |
| F6 | `escalate_stale_contested` + `auto_resolve_contested` bypass `resolve()` | Use `resolve()` for status changes | 413, 435 |
| F0/F4 | CONFIRMED+verified close before challenge check | Reorder: challenges checked before close | 604-607 |
| F24 | Same-round CONFIRM overrides CHALLENGE (`>` not `>=`) | Changed to `>=` in both `_update_finding_statuses` and `contested_count` | 603, 340 |
| F18 | REOPENED→OPEN direct mutation | Use `resolve()` | 614-615 |

### Convergence Gate

| Finding | Description | Fix | Line(s) |
|---------|-------------|-----|---------|
| F7/F23 | `cfg.max_open_crit_high` dead config | Added threshold check in `_evaluate_gate_conditions` | 623-664 |
| F14/F17/F22 | `contested_count` includes terminal statuses | Added `_TERMINAL` set, skip CLOSED/REFUTED/DUPLICATE/UNCONFIRMED | 332-344 |
| F12 | `_evaluate_gate_conditions` mutates `open_ch_history` | Guard against duplicate append (idempotent) | 640 |

### Protocol

| Finding | Description | Fix | Line(s) |
|---------|-------------|-----|---------|
| F8 | Single MERGE kills finding, no quorum | Require 2 distinct models for merge | 590-599 |
| F11 | Confirmation quorum: 1+external (source counted) | Require 2 external confirms, source excluded | 618-620 |

### Cosmetic

| Finding | Description | Fix | Line(s) |
|---------|-------------|-----|---------|
| F13 | `_VERDICT_RE` limited to `C\d{4}` | Changed to `C\d{4,}` | 459 |
| F19 | Unnecessary `\|` in regex char class | Cleaned to bare `|` | 460 |

---

## New Test File

`bench/tests/test_runner_status_transitions.py` — 21 tests:

- `TestAddVerdictNoTimerCorruption` (2 tests)
- `TestEscalationUsesResolve` (2 tests)
- `TestChallengeBeforeClose` (2 tests)
- `TestSameRoundChallenge` (1 test)
- `TestMergeQuorum` (2 tests)
- `TestConfirmationQuorum` (3 tests)
- `TestReopenedTransition` (1 test)
- `TestContestedCountTerminal` (3 tests)
- `TestMaxOpenCritHigh` (1 test)
- `TestIdempotentHistoryAppend` (1 test)
- `TestVerdictRegex` (3 tests)

---

## State After Fix Cycle

- **714 tests pass** (693 original + 21 new)
- Working tree dirty — needs commit + push
- Ready for Exp 38 restart from Round 0
