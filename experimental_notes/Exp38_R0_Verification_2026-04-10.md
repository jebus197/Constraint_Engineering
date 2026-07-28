# Experiment 38 Round 0 — Verification Results

**Date:** 10 April 2026
**Type:** Ouroboros — the system reviews and improves itself under structured falsification
**Target:** `bench/reference_runner.py`, star topology, 5 models, burst mode (5 phases)
**Status:** PAUSED after Round 0 to fix immune/endocrine gaps

## Summary

| Metric | Value |
|--------|-------|
| Raw findings | 26 |
| Unique claims (after dedup) | 20 |
| CONFIRMED | 14 (70%) |
| PARTIAL | 2 (10%) |
| REJECTED | 4 (20%) |
| Immune UNCERTAIN | 23/26 |
| Fix verification UNEVALUABLE | 20/20 |
| S_k (severity/stringency tristate gate) evaluated (before pause) | 3/26, all ADMISSIBLE |

## Confirmed Findings (14)

### Status Transition Chain (most consequential cluster)

| ID(s) | Sev | Finding | Lines |
|--------|-----|---------|-------|
| F0/F4 | 0.95/0.91 | CONFIRMED+verified entries close before challenge check — `continue` at L607 skips unresolved challenges | 604–607 |
| F2/F5 | 0.82/0.88 | `add_verdict()` unconditionally overwrites `last_status_change_round` on every verdict, corrupting escalation timer | 305 |
| F6 | 0.83 | `escalate_stale_contested` and `auto_resolve_contested` bypass `resolve()` — direct mutation, stale timer | 413, 435 |
| F9 | 0.70 | Escalation timer resets on any verdict, so findings stay CONTESTED indefinitely | Follows F2/F5 |
| F18 | 0.80 | REOPENED status silently overwritten to OPEN next round | 614–615 |

### Convergence Gate Bugs

| ID(s) | Sev | Finding | Lines |
|--------|-----|---------|-------|
| F7/F23 | 0.79/0.90 | `cfg.max_open_crit_high` is dead config — never read in `_evaluate_gate_conditions` | 623–664 |
| F14/F17/F22 | 0.55–0.90 | `contested_count` only skips MERGED — includes terminal statuses. F17: strict `>` misses current-round challenges | 332–344 |
| F12 | 0.55 | `_evaluate_gate_conditions` mutates `open_ch_history` via `append()` — side effect in evaluator | 640 |

### Protocol Bugs

| ID(s) | Sev | Finding | Lines |
|--------|-----|---------|-------|
| F8 | 0.75 | Single MERGE verdict from any model permanently kills a finding — no quorum, irrevocable | 590–599 |
| F11 | 0.60 | Confirmation quorum: source model counted as implicit confirmer (1+1=2≥2) — only 1 external confirm needed | 618–620 |
| F24 | 0.80 | Same-round CONFIRM silently overrides CHALLENGE — strict `>` excludes concurrent events | 603 |

### Cosmetic

| ID(s) | Sev | Finding | Lines |
|--------|-----|---------|-------|
| F13 | 0.50 | `_VERDICT_RE` limited to `C\d{4}` — 4-digit IDs only | 459 |
| F19 | 0.60 | Unnecessary `\|` in regex character class — harmless | 460 |

## Partial Findings (2)

| ID | Sev | Finding | Issue |
|----|-----|---------|-------|
| F16 | 0.90 | `__post_init__` overrides `rho_earliest_round` | Override is conditional (`!=`), not "unconditional" — but effect is real |
| F25 | 0.70 | MERGE regex expects `merged_into=` format | Runner-internal, not model-facing as claimed |

## Rejected Findings (4)

| ID(s) | Sev | Claim | Why Wrong |
|--------|-----|-------|-----------|
| F1/F3 | 0.90/0.94 | Rho off-by-one | File is uniformly 0-based; `len(raw_counts)-1` is correct |
| F10 | 0.65 | Gamma direction inverted for back-loaded | Inverted claim: front-loaded→γ≈1.0 (correct), back-loaded→γ≈0.0 (correct) |
| F15 | 0.45 | Gamma gate `<=` vs `<` inconsistency | No inconsistency — each comparison type is uniform |
| F21 | 0.70 | `gamma_prev` missing default | Wrong exception type; only call site always provides it |

## Immune System Gap Analysis

### B-Cell Math Verification
- `_build_smt2_from_claim()` only handles `VARIABLE >= VALUE` patterns
- 17/26 findings contain mathematical/logical claims about algorithm behaviour
- All 17 returned UNCERTAIN, of which 9 escalated to HIL
- The Formalisation Agent (shadow only) extracted preconditions from 8, translated 2 to z3

### Fix Verification (Endocrine)
- `_apply_fix_to_source()` handles: "Replace X with Y", whole-file replacement, line hints
- Does NOT handle `<<<< SEARCH / ==== / >>>> REPLACE` blocks
- The runner has `parse_search_replace_blocks()` (line 1485); endocrine does not use it
- CC2: `_find_target_file()` returns None (no `.py` path in description text)

### Required Fixes Before Restart
1. Wire `parse_search_replace_blocks()` + `apply_fix_blocks()` into endocrine as Strategy 0
2. Fall back to `source_paths[0]` in `_find_target_file()` when no match found
3. Promote the Formalisation Agent from shadow to active
4. Add a SymPy verification pathway for mathematical claims about known formulas

## Burst Architecture Performance

- Phase 0 Round 0: all 5 models responded successfully
- No context overflow errors (vs 178K chars in monolithic mode)
- DeepSeek: 225s response (vs 534s monolithic)
- 26 findings vs 16 in failed monolithic run
- All findings passed the skin barrier (vs many UNEVALUABLE in monolithic)
