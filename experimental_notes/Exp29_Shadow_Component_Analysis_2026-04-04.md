# Experiment 29: Shadow and V2 Component Performance Analysis

**Date:** 2026-04-04
**Experiment:** exp29_persistence_20260404T193154Z
**Rounds:** 9 (0-8), converged at round 8 (kappa 0.960)
**Total findings:** 340

## Overview

The immune pipeline data in the report covers rounds 3-8. Rounds 0-2 are missing from the report summary but their findings are preserved in the round JSON files and checkpoint.

**Critical gap:** The experiment runner logged only summary immune statistics (rejection_rate, autoimmune_flag, survivors). Detailed per-cell verdict data, shadow comparison records, and reconciliation gate decisions were logged via `_shadow_log` at INFO level, but the experiment runner only captured WARNING+. The majority of shadow component diagnostic data was **lost**. The only shadow data that survived are 310 WARNING-level error messages from the Typed LLM Classifier, which failed on every call.

## Component-by-Component Findings

### 1. Skin Barrier (Stage 0) — ACTIVE

Working. Evidence from autoimmune rounds:

| Round | Findings In | Barrier Rejected | Survivors |
|-------|------------|-----------------|-----------|
| 3 | 48 | ~10 | 38 |
| 6 | 29 | ~1 | 28 |
| 7 | 41 | 0 | 41 |
| 8 | 27 | 0 | 27 |

The barrier filters findings with invalid file/line citations **before** the pipeline. Autoimmune override cannot rescue barrier-rejected findings.

### 2. Dendritic Cell V2 (Stage 1) — PRIMARY

V2 is the primary classifier; V1 runs alongside for comparison logging only. Function is named `dendritic_cell_v2_shadow` but comments say "WP6a: now PRIMARY." No V1/V2 comparison data survived (INFO-level logging). **Should be renamed to drop `_shadow` suffix.**

### 3. NK Cell V2 (Stage 2) — PRIMARY

V2 is the primary dedup cell using `v2_similarity_dedup` and `v2_intra_round_dedup`. Most-discussed V2 component (40 model findings across all rounds).

**Known bug:** The returned triaged list (carrying duplicate flags) is discarded: `_, nk_verdicts = result`. Duplicate annotations on `TriagedFinding` objects never reach Helper T or Regulatory T. Only `CellVerdict` objects with DUPLICATE verdicts propagate.

### 4. B-Cell V2 (Stage 2) — ACTIVE

AST-grounded Z3 verification running in parallel with V1. Both feed Helper T and reconciliation gate.

**Known issues:**
- Constant extraction walks AST without scope awareness (local vars shadow globals)
- SMT2 builder regex fails on scientific notation
- Logical if/then claims produce false REJECTED at confidence 0.30 (unconstrained booleans)

### 5. Cytotoxic T Cell V2 (Stage 2) — ACTIVE

Claude CLI-based falsifier. Zero log messages (no warnings, no INFO captured). Likely ran successfully. Referenced in 30 model findings.

### 6. Helper T Cell V2 (Stage 3a') — ACTIVE

Log-odds synthesis feeding reconciliation gate. **Known issue:** unconditionally maps aggregated rejections to "REJECTED", erasing the DUPLICATE label distinction from NK V2. Breaks Regulatory T V2's dedup-vs-rejection accounting.

### 7. Reconciliation Gate (Stage 3a.5) — ACTIVE

Merges V1 and V2 Helper T outputs. Rules:
1. Agreement → shared verdict, max confidence
2. Disagreement → higher confidence wins
3. Single pipeline → use that verdict

**Critical flaw:** Docstring claims dual-REJECTED verdicts are "locked," but the autoimmune override at lines 2923-2924 unconditionally passes everything through. The lock exists only in the docstring.

All reconciliation diff logging was at INFO level — **not captured**.

### 8. Regulatory T Cell V2 (Stage 3b) — PRIMARY

V2 flag is authoritative. Autoimmune fired in **4 of 6 recorded rounds** (67%):

| Round | Rej Rate | Autoimmune | Effect |
|-------|----------|-----------|--------|
| 3 | 71.05% | True | Partial (barrier had already removed 10) |
| 4 | 45.00% | False | Normal filtering |
| 5 | 50.00% | False | Normal filtering |
| 6 | 53.57% | True | Override (28/29 pass) |
| 7 | 51.22% | True | Full override (41/41 pass) |
| 8 | 74.07% | True | Full override (27/27 pass) |

The 50% threshold is too low for this experiment's characteristics.

### 9. Formalisation Agent (Stage 2.5) — SHADOW ONLY

Genuine shadow. Extracts preconditions from math/logic findings, checks for potential B-Cell false rejections. Zero failure messages. Zero INFO messages captured. Running without errors but **producing no visible output** due to logging configuration.

### 10. Typed LLM Classifier (Stage 1.5) — SHADOW ONLY, BROKEN

**100% failure rate.** Model ID `anthropic/claude-haiku` is invalid on OpenRouter.

- Total API errors: 620 (2 per finding)
- Findings attempted: 310
- Successful classifications: **0**
- Error: `anthropic/claude-haiku is not a valid model ID`

Located at `bench/immune_agents.py:2386`. Needs updating to current OpenRouter model ID.

## Key Answers

### Q1: Which V2 components actually contribute to pipeline decisions?

7 active: Dendritic V2 (primary), NK V2 (primary), B-Cell V2 (parallel), CT V2 (parallel), Helper T V2 (reconciliation), Regulatory T V2 (primary autoimmune), Reconciliation Gate. Plus Skin Barrier.

### Q2: Which are effectively shadow despite "activation"?

Formalisation Agent (genuine shadow, no pipeline impact) and Typed LLM Classifier (broken, no pipeline impact).

### Q3: Is the Formalisation Agent producing useful data?

**Unknown.** Ran without errors but all output at INFO level was not captured.

### Q4: Is the Typed LLM Classifier working?

**No.** Zero successful calls. Dead code.

### Q5: Rejection rate vs novelty correlation?

Approximately inverse. R4: 45% rejection, 43% novel. R8: 74% rejection, 22% novel. But confounded by autoimmune override firing in 4/6 rounds, which sets effective rejection to 0%.

## Critical Issues (Priority Order)

1. **Fix Typed LLM Classifier model ID** — `bench/immune_agents.py:2386`, change `"anthropic/claude-haiku"` to valid OpenRouter ID
2. **Persist per-cell verdict data** — `bench/run_exp29_persistence.py:817` should save `cell_verdicts`, `final_verdicts`, `tool_usage`, `stage_timings` from `ImmuneResponse`
3. **Configure `immune.shadow` logger** to capture INFO level to file
4. **Raise autoimmune threshold** from 50% to ~65-70%, or implement locked-verdict enforcement
5. **Rename activated shadow functions** — drop `_shadow` suffix from active components
