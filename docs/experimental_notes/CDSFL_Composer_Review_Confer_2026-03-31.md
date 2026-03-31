# Composer Review Confer — 5-Model Problem Box Results

**Date:** 31 March 2026
**Models:** CC2 (Claude Opus 4.6), CX (Codex/GPT-5.4), ChatGPT (GPT-5.4), Gemini 3.1 Pro, DeepSeek Reasoner
**Rounds:** 2 (max 2 — refinement only)
**Total output:** ~303,000 chars across 10 dispatches
**Protocol:** "Problem box" — models MUST solve all 6 problems, no critique, no escape

## Context

The Dynamic Directive Composer was built from the findings of the prior 5-model Composable Directive Architecture Confer. Six concrete problems were identified in the built composer. All five models were constrained to produce working code solutions only — no critique, no "needs further research", no convergence signals.

## Problem Box Results

### Problem 1: Universal Packet Too Large for Small-Context Models

**Winner:** CX (endorsed by ChatGPT, DeepSeek)

**Solution:** Three-function architecture:
1. `_flatten_policy_items()` — deterministic TOML policy flattening to key=value lines
2. `_extract_hard_behavioural_directives()` — regex extraction from Non-Formalisable Directives section
3. `_render_universal_minimal()` — assembles minimal rendering from policy + behaviour

Static fallback tuple (`HARD_BEHAVIOURAL_FALLBACK`) covers all behavioural directives if regex extraction fails. Result: ~1,865 chars vs 9,597 chars original — fits within DeepSeek's 4,000-char cap with room for other layers.

### Problem 2: Pruning Too Coarse (Whole-Packet Only)

**Winner:** CX (all 5 models agreed on architecture)

**Solution:** Two-pass pruning strategy:
1. **Intra-packet pruning:** Split packets into blocks via `_DIRECTIVE_START_RE`, classify each as HARD/SOFT via keyword markers, remove SOFT blocks from end until budget met
2. **Whole-packet pruning:** Only if intra-packet pruning insufficient

Key functions: `_split_packet_directives()`, `_block_is_hard()`, `_prune_packet_directives()`

### Problem 3: Phenotype Transform Too Basic

**Winner:** CX (Jaccard dedup), ChatGPT strong second (synonym normalisation)

**Solution:** Nine-step transform pipeline:
1. Strip examples (block detection with heading/blank-line boundaries)
2. Strip rationale ("Why:", "Rationale:", etc.)
3. Compress tables (pipe-delimited → comma-separated, separator rows removed)
4. Flatten headers (markdown `##` → `LABEL:`)
5. Collapse multi-line directives to single-line
6. Deduplicate semantically similar directives (Jaccard ≥ 0.85 or containment ≥ 0.95)
7. Simplify language (synonym replacement: "therefore"→"so", "however"→"but", etc.)
8. Clean blank lines
9. Enforce max length

### Problem 4: No Phenotype × Domain Interaction Handling

**Winner:** CX (full ComposedDirectiveSet integration)

**Solution:** Topic/polarity-based conflict detection + three-rule resolution:
1. HARD always wins over SOFT
2. Higher layer wins (universal > domain > phenotype > situation)
3. Same-layer tie: more specific (domain-tagged) wins

Detects conflicts on five semantic dimensions: verbosity, examples, rationale, tables, proofs. Every resolution logged in manifest for transparency.

### Problem 5: Coherence Budget Thresholds Ungrounded

**Winner:** CX (no numpy dependency, field fallbacks, minimum-data guards)

**Solution:** `calibrate_coherence_thresholds()` reads experiment logs, computes per-model quality curves (findings per 1000 tokens vs constraint density), finds peak quality, identifies density where quality drops >10% from peak. Requires minimum 5 data points per model. Bins by density, averages quality, walks curve from peak looking for sustained drop (≥2 consecutive bins).

### Problem 6: Composer Not Wired Into Orchestrator

**Winner:** CX (correct function names, complete integration)

**Solution:** `compose_for_dispatch()` convenience function + `COMPOSER_MODEL_MAP` (maps orchestrator labels → composer model keys). Drop-in replacement for static prompt loading in `dispatch()`.

## Consensus Matrix

| Problem | CC2 | CX | ChatGPT | Gemini | DeepSeek |
|---------|-----|-----|---------|--------|----------|
| 1. Universal minimal | Provided | **Best** | Strong 2nd | Weak | Moderate |
| 2. Intra-packet prune | Provided | **Best** | Strong 2nd | Baseline | Moderate |
| 3. Phenotype transform | Provided | **Best** | Strong 2nd | Baseline | Moderate |
| 4. Conflict resolution | Provided | **Best** | Strong 2nd | Moderate | Moderate |
| 5. Threshold calibration | Provided | **Best** | Strong 2nd | Weak (numpy) | Weak (numpy) |
| 6. Orchestrator wiring | Provided | **Best** | Strong 2nd | Minimal | Minimal |

**CX won all 6 problems.** ChatGPT was consistently second with complementary ideas (synonym normalisation, recursive finding extraction, task domain inference).

## Test Results After Fixes Applied

| Model | Chars | Density | Budget | Status | Conflicts |
|-------|-------|---------|--------|--------|-----------|
| opus_4_6 | 12,035 | 0.0060 | 0.020 | WITHIN | 0 |
| codex_5_3 | 1,865 | 0.0408 | 0.012 | OVER (pruned 4) | 0 |
| chatgpt_5_4 | 5,300 | 0.0143 | 0.015 | WITHIN | 0 |
| gemini_3_1_pro | 5,300 | 0.0143 | 0.015 | WITHIN | 0 |
| deepseek_v3 | 1,865 | 0.0408 | 0.010 | OVER (pruned 4) | 0 |

All compositions valid. No monotonicity violations. Codex and DeepSeek still exceed budgets after full pruning (only universal HARD packet remains at 1,865 chars — can't prune further without losing mandatory constraints).

## Key Insight

The "problem box" prompt format — forcing models to produce solutions with no escape options — produced dramatically better output than the open-ended review format. The first confer (open format) generated ~191K chars of mixed critique and analysis. This confer (problem box) generated ~303K chars of working code. The constraint paradox in action: tighter constraints produced more useful output, not less.
