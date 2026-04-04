# CC2 Dispatch Diagnosis

**Date:** 4 April 2026, 02:10 BST
**Context:** Post-Run 11 investigation into CC2 reliability degradation

---

## Trajectory

| Run | CC2 Responded | Findings | Timeouts | Amplification |
|-----|--------------|----------|----------|---------------|
| 9 | 20/20 | 129 | 0 | 1.4856 |
| 10 | 5/7 | 36 | 2 (R3, R6) | ~1.47 |
| 11 | 1/2 | 12 | 1 (R1) | 1.4833 |

**Key observation:** Per-response quality is unchanged. Amplification is stable at ~1.48. The problem is availability, not capability.

## Root Cause: Three Compounding Factors

CC2 is the **only model** affected by all three:

### 1. Full Monolithic Payload

~250K chars source code + 80K chars findings budget + 10K preamble = **~340-360K chars**. CC2 is explicitly exempted from decomposition (`_should_decompose("CC2")` returns `False`) because decomposition was shown to be *worse* in Run 10 — 13 sequential chunks accumulated ~330K context plus CLI overhead.

CC2 is trapped between two broken delivery modes: monolithic (too big for CLI) and decomposed sequential (accumulating context makes it worse).

### 2. CLI Subprocess Dispatch

CC2 is dispatched via `subprocess.run()` piping stdin to `claude -p`. All other non-decomposed models use HTTP APIs:

| Model | Dispatch | Why It Works |
|-------|----------|-------------|
| Gemini | Google HTTP API | 3.8M char capacity, payload is ~9% |
| ChatGPT | OpenRouter HTTP API | Tight fit but HTTP is fast |
| DeepSeek | Decomposed chunks | Never sees full payload |
| Codex | Decomposed chunks | Never sees full payload |
| **CC2** | **CLI subprocess** | **Payload fits model (672K capacity) but CLI can't deliver** |

The CLI imposes a hard 600s timeout per attempt that cannot be overridden.

### 3. No Context Budget Override

DeepSeek has a 30K char findings budget. CC2 gets the default 80K. On adaptive rounds with 44 prior findings, this adds substantial payload.

## Why Run 9 Worked and Runs 10-11 Didn't

**Our own fixes caused this.** In Run 9, 84.5% of findings were churn — the same bugs restated 425 times with only 65 unique IDs. The immune pipeline (tau_sim=0.8, effectively disabled) didn't filter. The payload grew slowly.

We fixed churn in Run 10: tau_sim→0.33, B-Cell revived, NK Cell deduplicating. Churn dropped to 26.6%, unique IDs jumped to 174. The pipeline now produces genuinely novel findings each round → larger adaptive payloads → CC2 timeouts.

**Irony:** Improving the immune pipeline made CC2 less reliable. Better deduplication → more unique context → larger payloads → more timeouts. A negative feedback loop inside a positive one.

## Fix (Three Layers)

### Layer 1 — Immediate (pre-Exp 29)

Add CC2 context budget override: cap findings at 30K chars (same as DeepSeek). Cuts adaptive payload from ~340K to ~290K. Won't eliminate timeouts but buys margin.

### Layer 2 — Exp 29 Architecture

Cell-level decomposition: ~2K chars per cell vs ~358K monolithic = 180× reduction. Fresh instances per cell eliminate context accumulation. Gemini proof-of-concept validates this (13 findings, 12 rounds, same codebase).

### Layer 3 — Strategic (Exp 29 or 30)

Replace CLI subprocess with direct Anthropic API calls. The model can handle 358K chars (168K token window). Direct API gives: configurable timeouts, connection reuse, no process spawn overhead, streaming responses.

## Cross-Cell Blindness Risk

Cell-level decomposition trades payload size for cross-cell visibility. Findings spanning multiple modules (state mutation leaks, interface mismatches) become harder to detect. Mitigation: insect brain persistence layer relays cross-cell findings as pointers, models can request related cells.

## Falsifiable Predictions

1. Direct API with 1200s timeout → Run 11 R1 would have succeeded (testable immediately)
2. CC2 findings budget capped at 30K → next run shows CC2 responding in ≥1 more round (testable next run)
3. Cell-level decomposition eliminates CC2 timeouts but reduces cross-cell findings by 20-40% vs successful monolithic runs [SPECULATIVE — inferred from Gemini comparison]

## Extrapolation

**Generalises:** Any system where output quality feeds back as input size will hit this — better downstream processing → more unique upstream context → delivery bottleneck. The specific manifestation (CLI timeout) is CC2-specific, but the feedback loop pattern is universal.

**Breaks down when:** Context window is effectively unlimited (Gemini) or dispatch uses streaming HTTP (no hard timeout ceiling).
