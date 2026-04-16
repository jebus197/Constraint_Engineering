# 5-Panel CDSFL/FFAFP Review — §17 Feedback Channel + §18 Divergence Directive

**Date:** 15 April 2026, 23:15 BST
**Dispatch:** 22:02Z (parallel, ThreadPoolExecutor max_workers=5)
**Protocol:** CDSFL (Constraint-Driven Synthesis and Falsification) directives (system prompt) + FFAFP (Find, Follow, Analyse, Fix, P-pass) (user prompt)
**Logs:** `bench/logs/confer_divergence_directive/combined_20260415T220231Z.json`

---

## Panel

| Model | Route | Time | Chars |
|---|---|---|---|
| Gemini 3.1 Pro | Google GenAI native | 51.3s | 8304 |
| Codex GPT-5.4 | OpenRouter | 64.1s | 11437 |
| ChatGPT GPT-5.4 | OpenRouter | 65.7s | 11443 |
| CC2 Opus 4.6 | Claude CLI | 96.5s | 11609 |
| DeepSeek R1-0528 | OpenRouter | 176.7s | 5866 |

Wall-time: ~3 min parallel (bottlenecked by DeepSeek). All responses succeeded first-try; no fallbacks needed.

---

## Review questions

Q1 — Is the dimension set (mechanism / assumption / scope / timescale / tradeoff) sufficient and non-overlapping?

Q2 — Is Jaccard (a token-overlap similarity metric)-over-stopword-filtered-token-sets an adequate isomorphism metric for MVP?

Q3 — Are the penalty tiers (1.0 / 0.85 / 0.70 / 0.60) coherent with the rest of the R_k (the iterative residual-risk self-assessment) equation?

Q4 — Does the sequencing plan (Exp 39 baseline §17 (the Feedback Channel directive), Exp 40 §17+§18 (the Divergence Directive)) actually isolate the signal, or do §17 and §18 interact confoundingly?

Q5 — P-pass the whole pair: most plausible scenario under which §17 + §18 make CDSFL worse.

---

## Convergence map — what all 5 panel members flag

| Finding | Gemini | Codex | ChatGPT | CC2 | DeepSeek | Consensus |
|---|---|---|---|---|---|---|
| Dimension non-orthogonality (tradeoff as meta) | ✓ | ✓ | ✓ | ✓ | ✓ | **5/5** |
| Jaccard is lexical, not semantic | ✓ | ✓ | ✓ | ✓ | ✓ | **5/5** |
| Jaccard FP/FN on technical vocab | ✓ | ✓ | ✓ | ✓ | ✓ | **5/5** |
| Exp 39/40 confounds §17+§18 signals | ✓ | ✓ | ✓ | ✓ | ✓ | **5/5** |
| Compliance theatre is top Q5 risk | ✓ | ✓ | ✓ | ✓ | ✓ | **5/5** |
| Q4 experimental design is HARD | ✓ | ✓ | ✓ | SOFT | ✓ | **4/5 HARD** |
| Ship both as MVP | Implicit | ✓ | ✓ | ✓ | ✓ | **5/5** |
| Sibling alt-vs-alt check missing | — | ✓ | ✓ | — | — | **2/5 independent** |

## Divergence map — where the panel splits

**On Jaccard threshold:**
- Gemini: raise to 0.95 (protect genuine math from FP)
- DeepSeek: lower to 0.75 (catch more duplicates)
- Codex / ChatGPT: threshold is not the fix — reframe semantic claim, add sibling check
- CC2: ship at 0.85 with logging, recalibrate from data

**On penalty tiers:**
- Gemini: flatten 0.60 → 0.85 (P-passed out, revised to gated 0.85/0.98)
- Codex: 0.60 → 0.85 until stronger detector
- ChatGPT: milder 1.0/0.90/0.80/0.70 or novelty-only scope
- CC2: keep tiers as-is (0.60 is correctly harsh)
- DeepSeek: wire post-Exp 40, add 0.50 for recidivism

**On experimental design:**
- Codex / ChatGPT / DeepSeek: 2×2 factorial required
- Gemini: §17/§18 are structurally coupled — §18-only is scientifically invalid (its own P-pass falsified this)
- CC2: SOFT confound, attribute via `correction_source` tag

---

## HARD findings — panel-identified structural issues

1. **Sibling alt-vs-alt check missing** (Codex, ChatGPT — independent). §18 directive text says alternatives must pass against primary *and all other alternatives*. Implementation only checks alt-vs-primary. Spec/implementation gap. Estimated fix cost: ~10 LOC in `build_divergence_record`, ~3 new tests.

2. **Q4 experimental design confound** (4/5 agree HARD). Current plan cannot cleanly attribute §18's effect when §17 absorbs part of §18's enforcement.

3. **Null-justification is gameable** (Gemini, ChatGPT). `len > 60` defeated by stock macro. HARD in principle, SOFT in practice per CC2's bounded-blast-radius argument.

4. **Compliance theatre risk** (5/5, intensity varies). Models converge on formulaic alternative shapes; ν_k (the literature-novelty score) rises nominally while semantic novelty stagnates.

## SOFT findings — calibration

- Dimension taxonomy (5/5 agree SOFT for MVP)
- Jaccard threshold numerics (panel fractures)
- Penalty tier numerics (panel fractures)
- Dimension synonym handling

---

## Synthesised action plan

### Ship-blockers (do before Exp 40)

1. **Add sibling alt-vs-alt isomorphism check** in `build_divergence_record`. The only HARD finding where the panel converges on a mechanical action.

### Text / docs reframing (alongside)

2. **Rename internal notion from "isomorphism" to "lexical near-duplicate heuristic"** in comments and §18 text. Matches what the code actually does. Zero code change.

3. **Add non-exclusivity statement to §18:** "These are allowed declared difference axes, not a non-overlapping partition. Tradeoff does not excuse sameness on the other four dimensions unless the trade itself is the substantive difference."

### Optional but cheap

4. **Add `min_alternative_tokens: int = 15`** config field in `DivergenceConfig`, apply in `validate_alternative`. Catches "Brief vague sentence" loophole.

5. **Add per-round cross-model diversity metric** to Exp 40 logging — mean pairwise Jaccard across all alternatives across all models. Trending to 1.0 = template convergence. Logging-only.

6. **Tag `correction_source`** on each alternative — `{§17_feedback | §18_refinement | ambiguous}`. Post-hoc annotation.

### Experimental design — two options

**Option A (panel-majority, conservative):** Add Exp 41 as §18-only arm. Yields 2×2 factorial for clean main effects.

**Option B (pragmatic, Gemini/CC2 position):** Keep Exp 39/40 as planned, add diversity metric and correction-source logging, publish attribution limitation honestly. Research claim becomes "marginal effect of §18 given §17".

Recommendation: Option B sufficient for invention-engine objective. Option A sufficient for scientific-isolation objective. Pending founder decision.

### Defer (do not touch now)

- Penalty tier recalibration (panel fractures philosophically — let Exp 39/40 data argue)
- Jaccard threshold numerics (0.85 with logging until empirical data)
- Dimension taxonomy expansion (5/5 SOFT for MVP)
- Sentence-transformer embeddings (Phase 2 as planned)

---

## Extrapolation

### Within CDSFL

The panel review itself was a §17+§18 test. Five models in parallel produced primary verdicts with explicit alternatives tagged by dimension. Convergence on the sibling-check gap (2 independent models) and the experimental-design confound (4/5) is weak-but-positive evidence that structured-divergence prompts surface true-positive HARD findings that individual-model review would miss.

Boundary condition: all five models are transformer LLMs on overlapping corpora. Shared training-distribution bias could drive convergence toward the same wrong answer as easily as the same right one. Discriminator: findings that any model can mechanically verify survive multi-vendor cross-check better than findings that depend on judgement. The HARD/SOFT split maps roughly onto this mechanism.

### For Popper operationalisation

§17+§18 is a concrete operationalisation of Popper's asymmetry in an LLM framework. The panel's convergence on compliance theatre as the dominant failure mode is non-obvious: the risk is not that methodology fails, it is that subjects learn the shape of Popperian output without the substance. This generalises: any behavioural directive imposed on LLMs faces template-collapse risk proportional to validator observability.

The panel's own behaviour suggests a counter-measure: multi-vendor cross-checking with dimensional diversity requirements attenuates template collapse, because the template must satisfy five independent models simultaneously. [SPECULATIVE] but testable: if Exp 40 shows template convergence within a model but divergence across models, that is weak evidence the multi-vendor setup is the natural anti-theatre mechanism.

### For multi-vendor frontier falsification

If the sibling-check finding holds (small code change verifies), this is a reproducible example of the thesis: **multi-vendor review catches single-vendor-miss spec/implementation bugs**. The finding is mechanical (parser stores singular, text says plural), not a matter of taste. A weak but real data point for the claim that multi-vendor falsification produces findings monocular review does not.

### For the invention-engine framing

The panel's top Q5 risk — convergence to "one thin tradeoff alternative, one stock null-justification" — is exactly the pattern that would reduce CDSFL back to the verification framework it started as, with a §18 tax on output length. The directive survives this only if the diversity metric (fix 5) catches convergence and triggers recalibration.

The honest research claim is narrower than "invention engine": §18 is an *enforced surface area for divergence generation*. Whether that surface fills with genuine alternatives or with compliance theatre is an empirical question Exp 40 must instrument for.

---

## Panel P-pass discipline

Self-falsification intensity was uneven across the panel:

- **Gemini** — highest rate: 2 fixes revised under its own falsifier, 1 rejected outright
- **ChatGPT** — marked Jaccard recommendation [SPECULATIVE], partial
- **CC2** — tested each fix for perverse incentives, found bounded
- **Codex** — lighter P-pass, accepted MVP constraint
- **DeepSeek** — applied P-pass, all fixes survived

Weak data point: FFAFP as a prompt pattern does not uniformly produce the same intensity of self-falsification across frontier models.

---

## Open decisions for the founder

1. **Sibling check ship-blocker?** Recommend yes, before Exp 40 launch.
2. **Exp 41 §18-only for 2×2 factorial?** Option B (honest disclosure) recommended unless publication-grade isolation is the goal.
3. **Optional fixes 4 / 5 / 6?** Recommend yes to all three.

Penalty calibration question deferred to Exp 39/40 empirical data — panel split is philosophical, not calibration-numeric.

---

## Files

- `bench/confer_divergence_directive.py` — dispatcher (270 lines)
- `bench/logs/confer_divergence_directive/` — per-model JSON logs + combined
- `bench/dm/_divergence.py` — module under review (443 lines)
- `bench/tests/test_divergence_directive.py` — 52 tests, all green
- `bench/directives/universal/cdsfl_operational.md` §17, §18 — directive text
