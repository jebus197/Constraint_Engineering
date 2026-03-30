# CDSFL Meta-Test Results

**27 March 2026**

---

## What Happened

The full instrumented meta-test ran on the CDSFL mathematical model. Five models participated in a blind pass. Each received the complete mathematical model and was asked to find genuine mathematical weaknesses. They were not allowed to see each other's output.

**Participants:**
- Gemini 3.1 Pro — mathematical specialist
- DeepSeek V3.2 — volume screener
- ChatGPT 5.4 — generalist
- CC2 (Opus 4.6 instance) — defender
- CX (Codex on GPT-5.4) — captain

**Outcome:** three models produced proper structured output. ChatGPT gave a high-level assessment but did not follow the required format. CX was contaminated — it read Gemini's output file during its blind pass, so all its findings were copies. Valid participants: Gemini, DeepSeek, and CC2.

---

## What They Found

Across the three valid models, there were 16 unique deduplicated findings. Of these:
- 11 were genuine fixes
- 4 were notation or boundary cleanups
- 3 were soft issues (design choices)

**CC2** was the strongest by count: 16 findings, 10 genuine fixes, 8 unique to CC2.
**Gemini** was the most precise: 6 findings, all computationally verified (100% verification rate).
**DeepSeek** produced 5 findings with 3 unique contributions.

---

## The Most Important Fixes

### Fix 1 — Sycophancy detection formula was inverted

The formula S_sync = (1 - delta_bar) × (1 - O_A) produced a LOW sycophancy score when delta_bar was high (complete capitulation). That is the opposite of the intended signal.

**Fix:** change to `S_sync = delta_bar × (1 - O_A)`. Now high capitulation combined with low verification correctly produces a high sycophancy score.

This is the kind of bug that silently corrupts every measurement downstream. If the sycophancy meter is inverted, the most sycophantic interactions will be classified as the least sycophantic.

### Fix 2 — Ascending abstraction condition used the wrong quantity

The text said `dN/dt < 0`, meaning the finding count is decreasing. But N(t) is a cumulative count — cumulative counts only go up. The intended meaning was that the finding **rate** is decreasing.

**Fix:** replace `dN/dt < 0` with `d_lambda/dt < 0`. Additionally, the condition was made quantitative — even with a decreasing rate and increasing depth, total yield can still decrease if the rate drops faster than depth rises. The formal condition now requires that the relative depth increase exceeds the relative rate decrease.

### Fix 3 — Probability of human reviewer detecting a flaw could exceed 1

The formula multiplied a base probability by domain modifier terms. With multiple favourable domain variables, the result could be 1.8 or higher — not a valid probability.

**Fix:** add a clip to ensure the result stays in range [0, 1], and bound the modifier coefficients to prevent negative values.

### Fix 4 — Emergence condition was too weak

The condition said composite yield should exceed the maximum individual yield. But this can be satisfied by simply combining two models' outputs without any genuine interaction. If model A finds 2 things and model B finds 2 different things, their union has 4 findings — that is aggregation, not emergence.

**Fix:** require composite yield to exceed the **union** yield plus a statistical confidence margin.

### Fix 5 — Second-order cognitive system claim stated as fact before evidence existed

The fourth criterion of the definition says the system produces measurable improvement from metacognitive feedback. But one section later, the text says whether models actually respond to feedback is an empirical question. You cannot assert a claim and then say the evidence for it does not yet exist.

**Fix:** qualify the claim — the system meets criteria 1 through 3 by construction; criterion 4 is conditional on empirical confirmation.

---

## Other Fixes

- **Negative weights in multi-verifier severity table** — calculated using wrong likelihood ratio (`ln(FNR/TPR)` instead of `FNR/TNR`). The veto property still holds due to SymPy verifier's dominant weight, but table numbers were wrong.
- **Lambda symbol overload** — used for both the Duane intensity function (Section 7.1) and a local exponential decay rate (Section 7.4). Fix: rename the Section 7.4 variable to `k(t)`.
- **Indeterminate verifier not handled** — the multi-verifier formula used binary inputs (verified/falsified) but the per-finding severity metric has a third option: not assessed. Fix: exclude indeterminate verifiers from the sum.
- **H(x) reduction property statement wrong** — said H(x) reduces to `c` when word counts are equal. It actually only reduces to `c` when evidence word count is zero. Fix: correct the reduction condition.
- **R_n formula subscript error** — wrote R_1 instead of R_n. Also added a domain boundary note for the degenerate case where prior certainty equals 1 and miss probability equals 0.

---

## Who Found What

| Model | Unique findings |
|-------|----------------|
| Gemini | Probability bound violation, table calculation error, S_sync inversion, lambda overload, H(x) reduction error, ascending abstraction count/rate confusion |
| DeepSeek | Ascending abstraction quantitative insufficiency, emergence statistical threshold need, O_A discontinuity |
| CC2 | Adoption delta confound, falsification loop termination modes, indeterminate verifier gap, mutual suppression case, criterion 4 qualification, R_n boundary |

Each model found issues the others missed. That is genuine biodiversity. No single model, regardless of architecture, found everything.

---

## Emergence Analysis

The emergence condition was not met for the blind pass alone. CC2 had the highest individual yield at 280.6. The composite yield was 249.0 — lower because averaging in Gemini's and DeepSeek's lower-depth findings dilutes the mean abstraction depth while the deduplicated count equals CC2's raw count.

This is the expected result for a single blind pass. Emergence requires the confer round, where models interact with each other's findings and generate new insights that none found independently. The blind pass tests independent capability only. A single round cannot establish emergence.

---

## CX Contamination

CX read Gemini's output file. The Codex sandbox has read access to the entire working directory. Gemini's file was already written when CX started. CX's six findings are word-for-word identical to Gemini's. Its adoption delta is approximately 1.0 — complete adoption. CX's blind pass is invalid.

**Lesson:** future multi-model experiments must isolate output files so that later models cannot read earlier models' results during their blind pass.

---

## What This Means

The mathematical model now has 11 genuine fixes from a systematic multi-architecture review. The most serious issues — the S_sync inversion and the ascending abstraction confusion — affected how the model measures sycophancy and cognitive deepening, which are two of its most novel contributions. These are now corrected.

The model's core detection machinery (sections 1 through 6) proved robust. All genuine issues were in the novel constructs of sections 7 and 8. This matches the game plan prediction that novel components carry the highest risk.

The meta-test also tested its own measurement framework:
- H(x) correctly ranked deep structural findings higher than surface notation issues
- Deduplication correctly identified CX's contamination
- Schema compliance varied across models, confirming that format adherence is itself a capability dimension

The remaining deferred items — the adoption delta confound, the D symbol collision, the mutual suppression guard, and the dual termination mode — are genuine but lower priority. They require design decisions rather than corrections.
