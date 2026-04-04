# CDSFL Experiment Significance: Conversational FFF vs Monolithic Review

**Date:** 3 April 2026, 23:53 BST
**Context:** Immune cell review — 4 Gemini conversations under CDSFL/FFF vs Runs 8-10 (47 rounds, 5 models, monolithic)

---

## Results Comparison

| Metric | Runs 8-10 (Monolithic) | Gemini CDSFL/FFF |
|--------|----------------------|-------------------|
| Rounds | 47 | 12 |
| Models | 5 | 1 |
| Findings | 1,001 | 13 genuine |
| SymPy-verified proofs | 0 | 5/5 |
| Dead code found | 0 | 1 (Helper T else block) |
| Broken algebra found | 0 | 3 (dead code + 1.5x bias + ganging) |
| State mutation bugs | 0 | 1 (NK Cell FP fallthrough) |
| Regex misclassification | 0 | 2 (math hijack + missing citation) |

## Five Observations (P-Passed)

1. **Conversational CDSFL/FFF > monolithic.** Mechanism is focus + protocol, not protocol alone.
2. **Validates insect brain architecture.** Routing is load-bearing; models are stateless workers.
3. **CDSFL works single-system.** Same model, same code, different protocol → different results.
4. **Novel synthesis.** Elementary proof (Pr+Pc=1) hiding in production code for 10 runs.
5. **Fresh instances outperform accumulated context.** Attention budget management matters.

## Lessons for Future Runs

1. Decompose review to component-level granularity
2. Structure review as multi-turn CDSFL conversations, not single-turn prompts
3. Protocol quality > model quantity
4. Fix Helper T voting algebra before pipeline goes active (Run 12 critical path)
5. Build CDSFL vs no-CDSFL comparison experiment (same model, same focus, different protocol)
6. Formalise fresh-instance pattern in insect brain architecture

## Extrapolation

- **Generalises to:** any LLM-based analysis task (legal, medical, engineering)
- **Breaks down when:** problems require holistic system understanding (cross-cell interactions)
- **Falsifiable questions:**
  - Does CDSFL advantage scale with problem complexity?
  - Optimal conversation length before churn?
  - Fresh-instance effect: model-dependent or universal?
  - CDSFL vs focused-HIL-without-CDSFL: how much is protocol vs routing?
- **[SPECULATIVE]** CDSFL/FFF will outperform standard patterns, but gap may narrow if routing + fresh instances are the dominant factors
