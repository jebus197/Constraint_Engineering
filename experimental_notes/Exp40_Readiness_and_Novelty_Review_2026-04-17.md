# Experiment 40 Readiness and Novelty Review

**Date:** 17 April 2026
**Branch:** `exp39-experimental`
**HEAD:** `cc6cc1a`
**Scope:** three threads — novelty work completed in CDSFL (Constraint-Driven Synthesis and Falsification, a Popperian multi-vendor large language model falsification framework) during the 72 hours from 14 to 16 April 2026; the structure and coverage of Experiment 39; and the remaining work not yet folded into a runner for Experiment 40, alongside other factors worth attention.

---

## Scope and current state

The canonical project state sits at `exp39-experimental`, commit `cc6cc1a`, with 935 tests passing and a clean working tree. The last substantive schema change was the round-two implementation of the divergence directive on 16 April, 02:30 BST. Two live-default directives have landed since Experiment 39-0 was run on 13 April:

- The feedback channel directive, known internally as §17.
- The divergence directive, known internally as §18.

Experiment 40 will be the first experiment to exercise either.

---

## The novelty thread, 14 to 16 April

Two distinct novelty concepts emerged and were disambiguated over three days. They are not the same thing. Conflating them was the original architectural error the five-panel model review corrected between 15 and 16 April.

### Type 1: literature novelty (ν_k)

- Per-finding score in [0, 1].
- Computed by the Ouroboros literature-search cell (O1) against arXiv, Semantic Scholar, Unpaywall, CORE, and OpenAlex.
- Paired with c_ext (coverage confidence). Never collapsed into a single headline score; that collapse was rejected after the 14 April second-round confer on the grounds that it produced pseudo-corroboration from search difficulty.
- Composition: `η_combined = η_int × (1 − c_ext × (1 − ν_k))`. SymPy and Wolfram verified all boundary conditions.

### Type 2: internal novelty generation (§18 divergence directive)

- Generator-side requirement that every non-trivial finding supplies either at least one alternative on a named dimension, or a scoped null-justification.
- Allowed dimensions: mechanism, assumption, scope, timescale, tradeoff.
- Cosmetic rewordings rejected by Jaccard token-overlap isomorphism check at threshold 0.85.

### Round-two five-panel architectural crystallisation

Panel: Gemini 3.1 Pro, Codex GPT-5.4, CC2 Opus 4.6, ChatGPT GPT-5.4, DeepSeek R1-0528. Unanimous 5/5:

1. **Divergence multiplier does not belong on R_k.** R_k measures validity; an isomorphic alternative is redundant, not false. Penalising R_k for redundancy is a category error.
2. **Three orthogonal channels:** R_k (validity) / η_int (internal novelty) / ν_k · c_ext (literature novelty × search quality). Any new mechanism must declare its channel; mixing is structural error.
3. **§18 multiplier routes to three places:** FFAFP admissibility gate (structural violations), η_int modulator (continuous scaling for admissible alternatives), w(f) in κ_set (automatic decay for isomorphic findings).
4. **ν_k must never be modulated by §18.** Literature novelty is O1-external; not a subject for internal-novelty enforcement.
5. **Experiment 40 requires a 2×2 factorial** for clean signal attribution between §17 and §18.

### 16 April implementation

- Function renamed `divergence_penalty_multiplier → eta_int_modulator` (alias retained).
- Mandatory contrast statement parser.
- Sibling alt-vs-alt mandatory rejection gate.
- Near-copy 0.98 severe tier (triggers: near-copy, all-isomorphic, recidivism).
- **Verification:** 935/935 full suite, 75/75 divergence, 41/41 SymPy/z3, ruff + mypy clean.
- **Round-three five-panel review:** 3/5 immediate convergence, 2/5 on single prose/code mismatch corrected → 5/5 effective.

### CDSFL self-assessment

ν_k(CDSFL) = **0.807** against current published literature. Nearest competitor: Stanford POPPER (February 2025), different mechanism and narrower scope.

---

## The structure of Experiment 39

Experiment 39 is **not a single experiment**. It is a set of 14 sub-experiments defined in [bench/exp39_config.json](bench/exp39_config.json) with a dependency DAG and fail-fast gate policy.

| ID | Name | Domain | Type | Rounds | Wall | Status |
|---|---|---|---|---|---|---|
| 39-0 | Infrastructure Gate | software | gate | 8 | 1h | **Ran** — confounded, non-convergent |
| 39-A | Mathematics Specialist | mathematics | research | 15 | 4h | Not run |
| 39-B | Expert Encodings S_k | software | research | 12 | 3h | Not run |
| 39-C | Macrophage Admissibility | software | research | 10 | 2h | Not run |
| 39-D | Composition Test | software | integration | 6 | 1h | Not run |
| 39-E | Statistics Specialist | statistics | research | 12 | 3h | Not run |
| 39-F | CS/Software Specialist | software | research | 12 | 3h | Not run |
| 39-G | Biology Specialist | biology | research | 10 | 2h | Not run |
| 39-H | Information Science | information_science | research | 10 | 2h | Not run |
| 39-I | Cross-domain Synthesis | software | integration | 10 | 2h | Not run |
| 39-J | Microglia | software | research | 10 | 2h | Not run |
| 39-K | Physics Shadow | physics | shadow | 6 | 1h | Not run |
| 39-L | Chemistry Shadow | chemistry | shadow | 6 | 1h | Not run |
| 39-M | Engineering Shadow | engineering | shadow | 6 | 1h | Not run |

### Pipeline coverage summary

- **Tested via full CDSFL pipeline:** 1 of 14 (39-0, at reduced 6-round cap).
- **Reached convergence:** 0 of 14. 39-0 terminated at wall-clock with γ = 0.461. Structural gate (`max_open_crit_high = 0`) unreachable; documented γ-based alternative path never implemented in code.

---

## Confound analysis for 39-0

All 6 rounds of 39-0 are confounded by three independent factors per [Exp39_Confound_Analysis_2026-04-13.md](experimental_notes/Exp39_Confound_Analysis_2026-04-13.md):

| # | Confound | Severity | Detail |
|---|---|---|---|
| C1 | User prompt missing CORROBORATION/FALSIFICATION/ANALYSE | Critical | Exp 37 had 10 mandatory fields incl. R_k; ref_runner had 7 — no R_k mandate |
| C2 | Payload 4.6× system decomposition threshold | Critical | 368,683 chars (ref_runner.py 163K + immune_agents.py 167K + runner_core.py 38K) vs 80K threshold |
| C3 | Monolithic dispatch despite payload > threshold | High | CC2, ChatGPT, Gemini received 369K monolithically; only Codex and DeepSeek decomposed |

**Salvageable:** 78 findings about reference_runner.py bugs, S_k pipeline verdicts, convergence dynamics, γ history, per-model finding counts.
**Not salvageable:** R_k adoption rates. The oscillation measures prompt construction quality and context budget management, not model metacognitive capability.

---

## What has NOT been folded into an Experiment 40 runner

Three layers in order of load-bearing weight.

### Layer 1 — 39-0 post-mortem bugs (8 of 10 open)

Two fixed mid-session (race condition, `_total_payload_chars` double-counting). Remaining:

| # | Bug | Severity | Fix |
|---|---|---|---|
| 1 | S_k format mismatch (0% ADMISSIBLE) | P0 | 5 LOC at [reference_runner.py:2094](bench/reference_runner.py#L2094) |
| 2 | Parser emitting source code as finding IDs | P0 | Parser regex/fallback |
| 3 | Convergence gate structurally unreachable | P0 | Threshold 0 → 3–5, or implement γ path |
| 4 | Macrophage verdict wiring broken (blind 6/6) | P1 | Attribute audit + diagnostic |
| 5 | DeepSeek decomposition trap (6/6, 67% zero-char chunks) | P1 | Fingerprint override + parser + feedback |
| 6 | DeepSeek parser can't read `**Finding:**` markdown | P1 | Parser format |
| 7 | Autoimmune false alarm late rounds | P2 | Split flag |
| 8 | ITC degradation false trigger | P2 | Count verdicts as valid output |

P0 #1–3 are prerequisites for any fix-verification or convergence claim.

### Layer 2 — 6 lessons-forward still missing (was 11, 5 fixed/subsumed)

| # | Lesson | Status |
|---|---|---|
| 6 | Prior fix summary context | Missing |
| 7 | Consolidation phase (final 3 rounds) | Not implemented |
| 8 | Per-model ρ tracking with targeted ITC | Not implemented |
| 9 | Context windowing for long runs | Not implemented |
| 10 | S_k format pre-check with reformat request | Partial (§17 admissibility parser catches some) |
| 11 | Parser P2/P3 — CC2 leak FIXED, Gemini verdict pending | Half done |

### Layer 3 — schema landed after 39-0, never exercised live

- §17 feedback channel (39 tests, live-default).
- §18 divergence directive (original 52 tests).
- §18 round-two extensions (23 additional tests, channel reassignment, contrast statement, sibling check, near-copy severe tier).
- `eta_int_modulator` function exposed but not wired into `compute_rk()` by design (isolates prompt-level divergence signal from penalty signal).
- B-Cell specialist dispatch (14 active verifiers, shadow mode). Promotion = single-line flip at ~[reference_runner.py:3741](bench/reference_runner.py#L3741).
- Stage 6 shadow calibrator logging (ν_k, c_ext, H_ratio) triples per round — no live-run data.
- ν_k implementation in O1 (design complete, code pending). O1 currently uses finding IDs as search terms; arXiv only; falls back to mock.
- Unpaywall + CORE + OpenAlex source adapters (design only).
- OpenRouter function-calling for four non-CC2 models (not implemented).
- DeepSeek specialist role (Phase 6, not wired).
- Recidivism detection within-round only; cross-round state from `reference_runner.py` open.
- End-to-end channel-assignment boundary verification at integration call site outstanding.

---

## Other factors worth attention

### Test article size is structural

10/14 sub-experiments target the same 163K reference_runner.py file. Only 39-H uses a right-sized article (evidence.py, 23K). If Experiment 40 inherits configs without re-partitioning by size, nine sub-experiments repeat the 39-0 confound. Fix: choose test articles sized for the dispatch pipeline, not make decomposition more aggressive.

### Measured vs advertised attention is the most replicated finding and is operationally unused

Spans 78 rounds × 5 models × 4 experiments. Gemini (1M token advertised) compressed 369K payload to 3.6K JSON on R1. ChatGPT (128K advertised) produced 0 chars on R1. All fingerprint attention metrics remain null: `measured_attention_span`, `compression_threshold`, `quality_at_capacity`, `decomposition_recommended`, `attention_ratio`, `D_decay`. Infrastructure exists (`decay_analysis.py` fits Duane curves; `burst_planner.py` has D_decay trigger) but is disconnected. Wire before Experiment 40.

### Prompt schema is a string literal in a 3,700-line file

Root cause of lesson attrition across 36→37, 37→38, 38→39 transitions. Until the prompt schema is a first-class tested artefact, the next transition loses more.

### Compliance theatre is the dominant §18 risk (5/5 panel)

Failure mode: ν_k rises nominally while semantic novelty stagnates, templates converge. Defensive instrument: per-round cross-model diversity metric (mean pairwise Jaccard across all alternatives across all models). Trend to 1.0 = template collapse. Logging-only, not currently in runner.

### Schema drift between 39-0 and current HEAD is load-bearing

Sub-experiment configs predate §17, §18, and §18 round-two. Either regenerate configs for current schema or narrow scientific claim per sub-experiment run.

### Opportunity-cost sufficiency is CC2's open falsifier

Does §18 require an explicit penalty, or does differential convergence credit suffice? Only a 2×2 factorial with cell B (§17 on, §18 off) vs cell D (both on) answers this. Mathematical justification for the Option C recommendation.

### "14 sub-experiments" = 14 convergence units, not 14 sub-phases

39-A (15 rounds, 4h, mathematics) is scientifically distinct from 39-D (6 rounds, 1h, software integration). A "Experiment 39 complete/incomplete" binary obscures this.

### DeepSeek fingerprint bootstrapping trap remains

Chunk successes don't update fingerprints to prevent future decomposition. `max_successful_prompt_chars = 102,942` is a phantom from decomposed chunks. DeepSeek decomposes on monolithic ~104K regardless. Trap persists across all sub-experiments until broken.

### Gate fail-fast propagation can hide scope

Failed gate skips all downstream dependents. If 39-0 is re-run under schema drift and fails for a new reason, every dependent silently skips.

---

## Summary of open questions

Three decisions pending founder approval.

1. **Proceed to Experiment 40 planning on the round-two foundation?** Channel reassignment implemented and tested.
2. **Experimental design:** Option C (cells B+C+D, reuse Exp 36–38 for A) recommended. Option B (B+D with narrowed claim) fallback. Option A (full 2×2 with fresh A) overkill.
3. **Ordering:**
   - Path 1: close all three runner bug layers before Exp 40 (clean attribution, delay).
   - Path 2: scope Exp 40 to sub-experiments that avoid the large-payload confound (faster data, narrower claim).
   - Path 3 (not previously discussed): re-run 39-0 alone on current runner under schema drift as cheap forward signal — tests whether §17 + §18 converge on the same test article where the prior schema could not.

---

## References

- [experimental_notes/Novelty_Scoring_nu_k_Design_2026-04-14.md](experimental_notes/Novelty_Scoring_nu_k_Design_2026-04-14.md)
- [experimental_notes/Stage6_Confer_Synthesis_2026-04-14.md](experimental_notes/Stage6_Confer_Synthesis_2026-04-14.md)
- [experimental_notes/Stage6_R2_Confer_Synthesis_2026-04-14.md](experimental_notes/Stage6_R2_Confer_Synthesis_2026-04-14.md)
- [experimental_notes/Invention_Engine_Divergence_Directive_2026-04-15.md](experimental_notes/Invention_Engine_Divergence_Directive_2026-04-15.md)
- [experimental_notes/Divergence_Directive_Implementation_2026-04-15.md](experimental_notes/Divergence_Directive_Implementation_2026-04-15.md)
- [experimental_notes/Panel_Review_Section17_Section18_2026-04-15.md](experimental_notes/Panel_Review_Section17_Section18_2026-04-15.md)
- [experimental_notes/Round2_Convergence_Section17_Section18_2026-04-15.md](experimental_notes/Round2_Convergence_Section17_Section18_2026-04-15.md)
- [experimental_notes/Divergence_Round2_Implementation_2026-04-16.md](experimental_notes/Divergence_Round2_Implementation_2026-04-16.md)
- [experimental_notes/Exp39_0_Gate_PostMortem_2026-04-14.md](experimental_notes/Exp39_0_Gate_PostMortem_2026-04-14.md)
- [experimental_notes/Exp39_Confound_Analysis_2026-04-13.md](experimental_notes/Exp39_Confound_Analysis_2026-04-13.md)
- [experimental_notes/Exp39_Infrastructure_Build_2026-04-12.md](experimental_notes/Exp39_Infrastructure_Build_2026-04-12.md)
- [experimental_notes/Exp39_Revised_Scope_2026-04-12.md](experimental_notes/Exp39_Revised_Scope_2026-04-12.md)
