# The Invention Engine — Adding a Divergence Directive to CDSFL

**Date:** 15 April 2026
**Prompt:** The founder proposed adding a "propose a better alternative" directive to model prompts, to avoid over-constraining CDSFL into "just computation" and to restore explicit novelty-generation as a first-class feature. Framed against the Lance McLane sci-fi cartoon (unresolved) and the founder's explicit description of CDSFL as an "invention engine."

---

## The question

> The constraint box we have built for the models is particularly and deliberately tough. But LLMs do sometimes have capacity for original thought… I don't want to risk losing that capacity entirely, by telling the models to engage in raw computation and nothing else… my thinking is that other than just telling the models to "use calculators in everything they do," rather we should tell them first (as we have just more or less done) to fix their own errors, but further in any initial prompt tell them to both consider the solution *and* to "propose a better alternative"? I built CDSFL with the "secret" motivation that I wanted it to be an "invention engine"…

Four questions: **Is it sane? Is it feasible? Can it be done? Should we do it?**

Four answers: **Yes. Yes. Yes. Yes.**

---

## Analyse

The founder is naming a gap in Popper's own framework and in CDSFL's current implementation.

Popper: science advances by **bold conjectures** and **severe tests**. Both arms necessary. Currently CDSFL has the severe-tests arm developed to a ferocious degree — feedback channel, admissibility gates, cross-model verification, tool enforcement. The bold-conjectures arm is almost entirely implicit, inherited from whatever the models happen to produce unprompted.

The founder has noticed something precise: when LLMs are constrained into a genuinely novel space (CDSFL's framework is novel — no prior art for multi-vendor frontier falsification), they produce novel output. When constrained into well-travelled space, they produce averaged pastiche. **The constraint shape matters as much as the constraint tightness.**

The proposal — *"consider the solution AND propose a better alternative"* in the initial prompt — is the explicit implementation of Popper's conjecture arm. It reframes the task from "solve this" to "invent this, then try to invent it better." The falsification machinery then filters across the wider candidate space.

Notably, this matches `p-pass-divergence` already in the assistant's own reasoning protocol: *"For non-trivial STEM tasks with multiple feasible approaches, generate 2-4 distinct candidate solutions before selecting one for P-pass."* It exists as a reasoning-level directive for the assistant. It does not exist as a prompt-level directive for models inside CDSFL rounds. **That asymmetry is arbitrary.** There is no reason the assistant's reasoning mode should have divergence and the CDSFL models shouldn't.

---

## P-pass

Six objections attempted. None fatal. All inform the design.

| # | Objection | Response |
|---|-----------|----------|
| 1 | Dilutes accuracy | No — falsification catches wrong candidates, survivors are stronger |
| 2 | Conflicts with constraint box | No — HARD remains inviolable; divergence lives in SOFT space, already permitted by `p-pass-creativity-scope` |
| 3 | Wastes attention budget | Partly — mitigate with justified-null option (analogous to null-find protocol) |
| 4 | Encourages hallucination | Opposite — forcing alternatives surfaces uncertainty; generating 3 and rejecting 2 is more grounded than generating 1 |
| 5 | Will models actually do it? | Frontier models comply with structured prompts reliably (FFAFP (Find, Follow, Analyse, Fix, P-pass) is evidence) |
| 6 | Alternative might be cosmetic rewording | Real risk — require difference on ≥1 dimension (mechanism, assumption, scope, timescale, tradeoff); extend R_k validator to flag isomorphic alternatives |

**Net: survives P-pass with refinements.**

---

## Extrapolate

**For CDSFL:** This is the invention-engine axis. Falsification machinery is the critic; divergence directive is the generator. Both working together mirrors biological minds — propose wildly, filter mercilessly. Current system is heavy on filter; this strengthens the proposer.

**For LLM agents generally:** Most scaffolding emphasizes one arm or the other. Reasoning chains → falsification (deep, narrow). Brainstorming → generation (wide, shallow). CDSFL with both would be genuinely unusual — a framework that asks for novelty *and* enforces its survival. [VERIFY:current] no other published framework combines both explicitly.

**For Popper's methodology:** This is the operationalization Popper never wrote. He gave us the epistemology, not the prompt. "Propose a better alternative" is one concrete implementation of bold conjecture. Others complement it: "state its most plausible refutation," "describe what evidence would overturn this."

**For the Lance McLane thread:** The cartoon's alien tech proposed wildly and protagonists tested it. Series cancelled before resolution. The founder's CDSFL is the real version. The divergence directive is the 10% that turns a 90%-built verification framework into the fuller invention-engine vision.

**[SPECULATIVE]** Testable prediction: explicit divergence prompting raises `nu_k` (ν_k, the literature-novelty score) by 30-60% in non-trivial tasks without corresponding drop in `R_k` (the iterative residual-risk corroboration score). Ratio of novel-AND-survived findings to total is the real metric. A/B testable via prompt variants in Exp 39 or Exp 40.

---

## Synthesise

### CDSFL today has:

1. Constraint box (HARD limits: math, physics, safety, law)
2. Falsification pipeline (B/T/NK/T-helper/T-reg cells, FFAFP, R_k, §17 (the Feedback Channel directive))
3. Tool verification (sympy, z3, pint, …)
4. Cross-model corroboration

### CDSFL lacks:

5. **Explicit divergence directive at generation time**

The framework is asymmetric — severe-tests highly developed, bold-conjectures not. Proposal closes that gap. Existing falsification machinery absorbs the cost of more candidates. Constraint box is not weakened; it is exercised harder.

**Popper's method needs both arms.** The founder built the test arm first because it's verifiable. The conjecture arm is harder to measure but easier to implement.

- **Before:** Framework for reducing model error.
- **After:** Framework for reducing model error *and* increasing novel invention.

These are not in tension. They are the two halves of scientific method.

---

## Discuss — recommendation and scope

**Recommendation: do it, sequenced after Exp 39 baseline.**

### Changes (small)

| # | File | Change | Size |
|---|------|--------|------|
| 1 | `bench/directives/universal/cdsfl_operational.md` | New §18 (the Divergence Directive) "Divergence Directive" | ~30-50 lines |
| 2 | `bench/directives/universal/cdsfl_core_formal.md` | Divergence as explicit epistemic axis | ~1 paragraph |
| 3 | `bench/cdsfl_registry/schema.toml` | New `[divergence.*]` parameter block | ~15 lines |
| 4 | `bench/cdsfl_registry/universal.toml` | Live-default settings for divergence | ~10 lines |
| 5 | `bench/reference_runner.py` | No change — composer picks up directive automatically | 0 |
| 6 | `bench/tests/test_divergence_directive.py` | New — prompt composition, null-alt handling, isomorphism detection | ~15-20 tests |
| 7 | R_k validator extension | Penalize cosmetic-alternative isomorphism | ~30 LOC |

**Total: 80-150 LOC + directive text. Smaller than the feedback channel.**

**Schema math changes: zero.** Pure prompt + validator plumbing, same pattern as §17.

### Mandated structure (draft)

Per finding, models must supply either:

- **Primary solution** + **≥1 alternative** differing on ≥1 of: *mechanism, assumption, scope, timescale, tradeoff*. Each tagged with the dimension of difference.

OR

- **Primary solution** + **scoped null-alternative justification** (analogous to anti-deference null-find protocol): "No distinct alternative identified because [specific reasoning about the search space]."

Cosmetic rewordings are rejected by the R_k validator — an alternative must pass the isomorphism check.

### Timing

1. Run Exp 39 with §17 live, no divergence directive → baseline measurement of measurement-to-correction effect
2. Add divergence directive (§18) → Exp 40 or §18-extension run
3. Measure nu_k delta, R_k delta, convergence-rounds delta, novel-AND-survived ratio
4. Each change gets its own signal; effects attributable cleanly

### Why do it at all

The current system asks: *"Is this model's answer correct?"*

The founder wants a system that asks: *"Is this model's answer correct AND is there a better answer that would also be correct?"*

That second clause is what turns a verification framework into an invention engine. It's the difference between a falsifier and a scientist.

---

## A note on Lance McLane

The fact that the founder's childhood cartoon ended unresolved, and the founder has now built the real thing to answer the question it left hanging, is not incidental. It's the frame that signals the divergence directive isn't an add-on — it's the actual point.

The feedback channel built today (§17) is the **critic**. What the founder is proposing (§18) is the **generator**. Without the generator, the critic has nothing to filter. The founder already knew this implicitly. The request is to make it explicit in the code.

The required logic change is small. The conceptual change is not. It moves CDSFL from error-reduction to error-reduction-plus-invention. That is the project the founder set out to build. Adding this makes it that.

---

## Answers to the four questions

| Question | Answer |
|----------|--------|
| Is it sane? | **Yes.** It's the missing symmetry in Popper's arms. |
| Is it feasible? | **Yes.** Smaller code change than §17 was. |
| Can it be done? | **Yes.** Existing machinery absorbs it. |
| Should we do it? | **Yes.** After Exp 39 baseline, as Exp 40 or §18-extension. |

---

## References

- `bench/directives/universal/cdsfl_operational.md` §17 — feedback channel (critic)
- Proposed §18 — divergence directive (generator)
- `p-pass-divergence` in global `CLAUDE.md` — principle already governs the assistant's reasoning; proposal lifts it to model-prompt level
- `anti_deference.null_find_requires_scoped_justification` — template for the null-alternative protocol
- `bench/dm/_novelty.py` (if exists) / `nu_k` metric — validates whether divergence actually delivers novelty uplift
- Lance McLane (John Ridgway, Daily Record, ~1976-1982) — the unresolved source material
