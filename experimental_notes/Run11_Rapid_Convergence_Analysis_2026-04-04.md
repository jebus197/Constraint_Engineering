# Run 11 (Exp 28b) — Rapid Convergence Analysis

**Date:** 4 April 2026, 01:54 BST
**Duration:** 2518s (~42 minutes)
**Result:** Converged at Round 1 (2 rounds total) — fastest convergence in bench history

---

## Results Summary

| Metric | R0 (blind) | R1 (adaptive) |
|--------|-----------|---------------|
| Findings | 44 (5 models) | 15 (4 models — CC2 failed) |
| Novel clusters | 35 | 7 |
| Rejection rate | 0% | 67% |
| Verdicts | 41 UNCERTAIN, 2 CONFIRMED | 10 DUPLICATE, 5 UNCERTAIN |

**Convergence:** γ_novel = 0.737 (threshold 0.5)
**Popper C(H,E):** 0.873 (strong corroboration)

## Per-Model Performance

| Model | Findings | Amplification (A) | Ω Trajectory | Status |
|-------|----------|-------------------|--------------|--------|
| CC2 (Opus) | 12 R0, 0 R1 | 1.48 | [0.116] | **Dispatch failure** |
| Codex (GPT-5.4) | 13 R0, 6 R1 | 1.42 | [0.272, 0.038] | Active |
| ChatGPT (GPT-5.4) | 10 R0, 7 R1 | 1.37 | [0.184, 0.225] | Active (Ω rising) |
| DeepSeek | 4 R0, 1 R1 | 1.07 | [0.227, 0.402] | Active |
| Gemini (2.5 Pro) | 5 R0, 1 R1 | 1.21 | [-0.011, 0.000] | **Benched** |

## Three Factors Behind Rapid Convergence

### 1. CC2 Dispatch Failure

CC2 spent 21 minutes failing all dispatch methods:
- 3× single-shot timeout at 300s each (900s)
- Multi-turn fallback: 14 chunks delivered in 63s
- Chunk 14 timed out at 600s
- Final instruction (chunk 15) timed out at 600s
- Circuit breaker tripped at 1262.8s

CC2 had the highest amplification (1.48) and produced 12/44 R0 findings. Its absence from R1 is a significant confound. The 358K char payload exceeds reliable CLI delivery capacity.

### 2. Aggressive Immune Rejection in R1

10/15 R1 findings classified DUPLICATE by NK Cell (tau_sim=0.33). The 44 R0 findings served as prior evidence. NK v2 shadow agreed on all 10 duplicates — the dedup is consistent, not artefactual.

### 3. Gemini Benched

Ω < 0.1 for 2 consecutive rounds → benched. Gemini produced 5 blind, 1 adaptive. The monolithic approach demonstrably underutilises this model — the CDSFL/FFF review hours earlier found 13 deep findings from Gemini alone under focused conversation.

## Shadow V2 Data (First Production Run)

| Component | R0 | R1 | Key Finding |
|-----------|----|----|-------------|
| NK v2 intra-round dedup | **9 caught** | 0 | v1 missed these entirely; inflated R0 by 9 |
| B-Cell v2 (AST z3) | 42 checks | 4 checks | First grounded SMT-LIB production data |
| DC v2 | 7.4ms | 2.0ms | Tightened classification comparison logged |
| Helper T v2 | 0.2ms | 0.1ms | Domain-based synthesis comparison logged |
| RT v2 | <1ms | <1ms | Combined removal rate vs rejected-only logged |
| NK v2 cross-round dedup | — | 10 (matches v1) | v1/v2 agreement validates approach |

**Notable:** NK v2 caught 9 intra-round duplicates in R0 that v1 allowed through. These inflated R0's finding count from ~35 to 44. The feature is already validated.

## Immune Pipeline Detail

**R0:** 0% rejection, 41 UNCERTAIN, 2 CONFIRMED. B-Cell ran 36 SymPy + 6 z3 checks. Skin barrier flagged 1 citation failure.

**R1:** 67% rejection, 10 DUPLICATE, 5 UNCERTAIN. NK Cell deduplicated 10/15 against R0 findings.

## Assessment: Real or Premature?

**Probably real but accelerated.** R0 was exceptionally thorough (44 findings, 35 novel clusters). R1 naturally overlapped because the adaptive prompt showed what R0 found. The 80% novelty drop is steep but mechanistically explicable.

**Two caveats:** CC2's absence is a confound — it might have prevented convergence. Gemini's benching reflects delivery limitations, not analytical capability.

## Implications for Exp 29

- Monolithic delivery caused CC2 failure and Gemini underperformance
- Cell-level decomposition (the Exp 29 design) sidesteps both problems
- Shadow v2 data from this run informs v2 activation decisions
- The CDSFL/FFF Gemini review (13 findings, 12 rounds, same code) vs Run 11 Gemini (6 findings, benched) is a direct comparison of constraint box vs monolithic delivery
