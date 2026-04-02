# PM Filter Architecture: Automated Quality Gate Between Rounds

**Date:** 2 April 2026
**Trigger:** Run 7b sy+f analysis showed 76% churn, 24% FP rate by theme
**Status:** DESIGN — P-passed, not yet implemented

## Problem Statement

Run 7b produced 197 findings. After SymPy verification and FFF code audit:
- 150 of 197 (76%) were churn — the same bug re-reported across rounds
- 5 of 21 unique themes (24%) were false positives
- Codex hallucinated a missing `@dataclass` decorator 8 times (7% of its output)
- Novel bugs after Round 2: ~3

The pipeline has no quality filter between rounds. All raw findings are
injected into the next round's context. The `verified` field on `Finding`
exists but is always `False`. The `verify_sympy()` function exists but
isn't wired in. The PM role exists in `RoleAssignment` but the runner
ignores it. The `_finding_similarity()` dedup function exists but is
only used for convergence detection, not filtering.

**All the infrastructure exists. None of it is connected.**

## Proposed Architecture

### Stage 1: Similarity Dedup (zero API cost, ~100ms)

Wire `_finding_similarity()` from `_convergence.py` as a **filter**, not
just a detector. After each round's raw findings are collected:

1. Compute pairwise similarity between new findings and all prior findings
2. If `sim(new, existing) >= tau_sim` (0.8), mark new finding as DUPLICATE
3. DUPLICATE findings are logged but not injected into next round's context

**Expected reduction:** 76% of findings eliminated (based on Run 7b data).

### Stage 2: Automated Verification (zero API cost, ~500ms)

Two sub-stages:

**2a. SymPy verification** — for findings containing mathematical claims:
- Lift `verify_sympy()` from `interactive_smoke.py` into a shared utility
- Extract verifiable expressions (regex for formulas, or model-provided)
- Run SymPy: tag `Finding.verified = True/False`
- REFUTED findings are marked, not injected into next round

**2b. AST verification** — for findings making factual claims about code:
- Parse the target source with `ast.parse()`
- Check structural claims: "class X has no @dataclass decorator" →
  `any(d.id == 'dataclass' for d in node.decorator_list)`
- Check existence claims: "method Y doesn't exist" → search AST
- REFUTED findings are marked, not injected into next round

**Expected additional reduction:** ~10-15% of remaining findings verified
or rejected without an API call.

### Stage 3: PM FFF Review (one API call, ~60-90s)

CC2 reviews the **deduplicated, verified** finding set against actual
source code. Prompt template:

```
You are the project manager. Below are {n} findings from this round's
review of {target_file}. Each finding has been:
- Deduplicated against all prior findings
- SymPy-verified where mathematical claims exist
- AST-checked where structural claims exist

For each finding, verify it against the actual source code provided.
Mark each as:
- CONFIRMED: the bug exists in the code
- REJECTED: the finding is incorrect (explain why)
- NEEDS_INFO: cannot determine from available code

Use Find-Follow-Fix: FIND the exact code, FOLLOW consequences, then
give your verdict.

{findings}

{actual_source_code}
```

**Expected additional reduction:** ~20-30% of remaining findings rejected
(based on Run 7b FP rate).

### Stage 4: Filtered Context Injection (free)

Only CONFIRMED findings enter context for the next round. REJECTED
findings are logged with PM's reasoning. All raw findings preserved in
checkpoint for auditability.

Subsequent rounds' models see the filtered set. If the PM made errors,
these models catch them — they have fresh eyes on the code and see the
PM's CONFIRMED set as their "prior findings." Any genuine bug the PM
wrongly rejected will be rediscovered independently.

## Cost Analysis

| Metric | Current (Run 7b) | Proposed |
|--------|-------------------|----------|
| Per-round time | ~300s (5 models) | ~390s (5 models + PM) |
| Rounds to useful convergence | ~20 | ~8-10 (estimated) |
| Total wall-clock | ~6,000s | ~3,900s |
| Findings entering context | 197 (all) | ~30-40 (filtered) |
| Churn rate | 76% | ~5% (estimated) |
| False positive rate | 24% by theme | ~1-2% after 3 rounds |

**Net saving: ~35% wall-clock, ~85% context waste eliminated.**

## Declining Error Rate (Swiss Cheese Model)

If each review layer catches ~76% of errors:
- After 1 round: 24% FP pass-through
- After 2 rounds: 0.24² ≈ 5.8%
- After 3 rounds: 0.24³ ≈ 1.4%

The D-decay (Duane NHPP) model applies to the error rate of the review
process itself. The methodology reviews itself.

## Existing Infrastructure to Wire

| Component | Status | Location |
|-----------|--------|----------|
| Similarity dedup | EXISTS | `_convergence.py:_finding_similarity()` |
| SymPy verification | EXISTS | `interactive_smoke.py:verify_sympy()` |
| PM role | EXISTS | `_types.py:Role.PM` |
| `Finding.verified` field | EXISTS | `_types.py:Finding` |
| Claim extraction | MISSING | CC2 prompt or regex |
| AST structural checking | MISSING | ~30 lines with `ast` module |
| PM FFF prompt template | MISSING | ~50 lines |
| Filter wiring in runner | MISSING | ~100 lines in `run_baseline_confer.py` |

**Estimated build: ~200-300 lines of new code.**

## Extrapolation

This is the immune layer for findings themselves. The current
`DetectorHealthMonitor` watches kappa, mu, novelty — system health
metrics. A `FindingsHealthMonitor` would watch duplication rate,
verification rate, false-positive rate — output quality metrics. Same
architecture, applied reflexively.

The compound objective Ω becomes most powerful when computed on filtered
findings. Currently Ω is noisy because it operates on raw output
including all churn. Filtered Ω would be a much cleaner signal.

Boundary condition: breaks down when the PM model shares systematic
biases with generators. Defence: architectural diversity (Claude
reviewing Codex/ChatGPT/DeepSeek/Gemini output).

## Implementation Decision

Awaiting founder approval. Estimated build: one session. All
infrastructure exists — this is a wiring job, not a design job.
