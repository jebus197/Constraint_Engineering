# Experiment 30 Post-Analysis and Fix Application

**Date:** 5 April 2026, 04:47 BST

## Overview

After Exp 30 completed with 378 findings across 15 rounds but no epistemic convergence, deep analysis revealed **fix-level churn** as the root cause. 232 proposed fixes for ~83 distinct bugs — models endlessly debating alternative solutions instead of finding new bugs.

39 bug fixes + 3 architectural changes applied. 571 tests pass.

## Why Exp 30 Did Not Converge

| Cause | Mechanism | Impact |
|-------|-----------|--------|
| κ_rate instability | Directed messaging sustains genuine novelty | κ_rate oscillates -0.33 to +0.31 (was 1.0 in Exp 29) |
| Fix-level churn | 232 fixes for ~83 bugs (3-4 per bug) | Each alternative fix appears "novel" to convergence detector |
| No bug closure | System had no concept of "this bug is fixed, move on" | Models relitigate indefinitely via directed messages |

The convergence detector was asking "are we still finding new things?" The answer was technically yes — but only because "new fix for old bug" looked like "new finding" to the similarity metric.

## Architectural Fixes (3)

### 1. Bug-Closed Gate (NK Cell v1 + v2)

When a new finding matches a prior finding that already has a **programmatically verified** fix (`finding.verified == True`), the new finding is rejected immediately. First verified fix wins. Bug closed.

### 2. Programmatic Fix Evaluation (Immune Pipeline Stage 4)

Wired `evaluate_fix()` from `endocrine.py` into `run_immune_pipeline()`. For surviving findings with proposed fixes:
- Copy source to temp directory
- Apply proposed fix
- Run pyright, ruff, bandit, pytest
- Compare before/after diagnostic counts
- SAFE or NEUTRAL → `finding.verified = True`

No model opinion. The tools decide.

### 3. BUDGET_EXHAUSTED Status

`check_convergence()` at max rounds now sets `converged = False` with reason `"BUDGET_EXHAUSTED"`. Budget exhaustion is not epistemic convergence. `signal_complete()` emits this as a distinct status.

### 4. Context Formatting (CLOSED/PENDING/OPEN)

Findings summary now categorises bugs:
- **CLOSED**: Programmatically verified fix exists — "do not relitigate"
- **PENDING**: Fix proposed, awaiting tool verification
- **OPEN**: No fix yet — "contributions welcome"

## Bug Fixes Applied (39 total)

### immune_agents.py (18 fixes)

| Bug# | Severity | Fix |
|------|----------|-----|
| #1 | 0.9 | SMT-LIB multi-condition negation in B-Cell v2 classifier |
| #33 | 0.9 | Log-odds sign bug — floor clamped to 0.50 |
| #4 | 0.9 | Threading lock for concurrent claude CLI calls |
| #16 | 0.9 | Reconciliation gate minimum margin (0.10) |
| #9 | 0.8 | Z3 if/then returns UNCERTAIN, grounded_vars word-boundary regex |
| #5 | 0.8 | Skin barrier citation pattern widened to all extensions |
| #10 | 0.8 | NK v1 control flow leak (FP → skip anomaly detection) |
| #34 | 0.8 | SymPy regex matches multi-character variables |
| #17 | 0.8 | Dendritic cell uses comma separator instead of " AND " |
| #41 | 0.7 | Skin barrier line-only citation fallback removed |
| #46 | 0.7 | Barrier rejections included in rejection rate totals |
| #56 | 0.7 | Autoimmune override preserves barrier rejections |
| #20 | 0.6 | Dead code removed (shadow log directory) |
| #14 | 0.6 | Lazy tool discovery syncs module-level variables |
| #67 | 0.6 | AST constant extraction cached |
| #69 | 0.6 | Skin barrier basename ambiguity handling |
| #72 | 0.5 | Statistical claim verification extended |
| #82 | 0.5 | Tool usage counting made consistent |

### insect_brain.py (10 fixes)

| Bug# | Severity | Fix |
|------|----------|-----|
| #2/#3 | 0.9 | Checkpoint recovery loads model_responses from round files |
| #13 | 0.9 | Immune response serialised to checkpoints |
| #62 | 0.85 | signal_complete() uses atomic writes |
| #6 | 0.85 | gamma_hat div-by-zero guard (requires round >= 2) |
| #22 | 0.7 | handle_model_failure saves checkpoint |
| #36 | 0.65 | max_rounds=0 guard |
| #19 | 0.6 | compute_metrics exception specificity narrowed |
| #48 | 0.62 | Truncation marker on round JSON model responses |
| #15 | 0.85 | Findings summary newline handling |
| #63 | 0.3 | run_immune_pipeline docstring updated |

### verification_chain.py (8 fixes)

| Bug# | Severity | Fix |
|------|----------|-----|
| #58 | 0.85 | Epoch ordering and monotonicity validation |
| #38 | 0.85 | Orphan epoch check (empty records + existing epochs) |
| #52 | 0.76 | CLI/API proof verification contract aligned |
| #79 | 0.76 | seal_epoch idempotent + fsync durability |
| #40 | 0.58 | Records/epochs properties return deep copies |
| #12 | 0.85 | load_json structure validation |
| #70 | 0.52 | Sub-second timestamp precision preserved |
| #76 | 0.61 | Error message input truncated (injection surface) |

## Skipped (with reasons)

| Bug# | Reason |
|------|--------|
| #8 | False positive — `_normalize_timestamp` correctly handles trailing Z |
| #7 | Performance optimisation, not correctness bug |
| #32 | By design — `canonical_json` TypeError on floats is intentional |
| #53 | False positive — `Signer.__init__` already checks `_HAS_CRYPTO` |
| #61 | By design — domain separation unnecessary for fixed 32-byte inputs |

## SymPy Verification (4 key findings confirmed)

1. **Log-odds sign bug**: `log(0.3 / 0.7) = -0.847` — confirmed negative for c < 0.5
2. **Z3 if/then always-SAT**: Abstract `Implies(X, Y)` with `X=True, Not(Y)` always satisfiable
3. **CT partial-evidence threshold**: `>= 0.5` triggers CONFIRMED on single evidence item
4. **Reg T v1 rejection rate**: UNRESOLVED excluded from denominator, understating rate

## Test Results

571 passed, 0 failed (unchanged test count — existing tests + 2 updated tests).
