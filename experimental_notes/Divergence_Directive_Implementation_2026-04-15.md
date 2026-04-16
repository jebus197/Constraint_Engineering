# Divergence Directive (§18) — Implementation Summary

**Date:** 15 April 2026 (22:40 BST)
**Companion to:** `Invention_Engine_Divergence_Directive_2026-04-15.md` (scoping)
**Audience:** anyone — no CDSFL background required

---

## What this is

The divergence directive (§18, the Divergence Directive) is the Popperian **bold-conjectures arm** of CDSFL (Constraint-Driven Synthesis and Falsification, a multi-vendor LLM falsification framework). The framework already had the **severe-tests arm** — the falsification pipeline, the admissibility gates, the cross-model corroboration, the §17 (Feedback Channel directive) added earlier today. Until now the generator side was implicit, inherited from whatever the models happened to produce unprompted. §18 closes that gap.

Per the directive, every non-trivial finding must now supply one of two structures:

- **Structure A** — Primary solution plus at least one alternative that differs on a named dimension (mechanism, assumption, scope, timescale, or tradeoff).
- **Structure B** — Primary solution plus a scoped null-alternative justification that names the search space, enumerates candidates considered, and explains why each rejected candidate collapsed to the primary.

Cosmetic rewordings are rejected. An alternative that differs only in surface wording earns no novelty credit and incurs a double penalty.

---

## What got built today

### Files changed

| File | Change | Size |
|---|---|---|
| `bench/directives/universal/cdsfl_operational.md` | New §18 directive text | ~90 lines added |
| `bench/directives/universal/cdsfl_core_formal.md` | New Classification Summary row | 1 row added |
| `bench/cdsfl_registry/universal.toml` | New `[divergence]` live-default block | 11 lines added |
| `bench/cdsfl_registry/schema.toml` | Six `[divergence.*]` parameter entries | 43 lines added |
| `bench/dm/_divergence.py` | **New module** — parser, validator, penalty | 443 lines |
| `bench/tests/test_divergence_directive.py` | **New test file** — 52 tests across 7 classes | 440 lines |

**Total new Python: ~883 lines. Schema math changes: zero.**

### The module — `bench/dm/_divergence.py`

Four distinct surfaces:

1. **`ALLOWED_DIMENSIONS`** — the canonical five: mechanism, assumption, scope, timescale, tradeoff. Plus a synonym normaliser that maps variants (`premise` → `assumption`, `trade-off` → `tradeoff`, `mechanisms` → `mechanism`, and so on).

2. **Parsers** — `parse_alternative_block()` and `parse_null_justification_block()`. Permissive on header format; strict on semantics. Accepts inline dimension tags (`(dimension: X)`), dash tags (`— dimension: X`), follow-up `Dimension:` lines, bold-emphasis headers, and markdown heading syntax. The dimension line is stripped from the body before isomorphism scoring so it does not inflate similarity.

3. **Validators** — `validate_alternative()` enforces dimension presence, length cap, and isomorphism threshold. `validate_null_justification()` enforces minimum-length floor. Both report every failure, not just the first.

4. **Pipeline integration** — `build_divergence_record()` assembles a per-finding audit and sets `compliant = True` iff at least the minimum number of admissible alternatives survive, OR a valid null-justification is supplied. `divergence_penalty_multiplier()` exposes a scalar in `(0, 1]` that the R_k pipeline can apply at its discretion.

### Penalty tiers

| Condition | Multiplier |
|---|---|
| Compliant finding | 1.0 (no penalty) |
| Engaged but failed gate (missing dimension, too-short null) | 0.85 |
| No engagement (neither alternative nor null) | 0.70 |
| Isomorphic rewording only (all alternatives cosmetic) | 0.60 (double penalty per §18) |

These are deliberately conservative for the MVP. Final calibration depends on Exp 39 / Exp 40 baseline data.

---

## Five design principles

1. **Imperative, not advisory.** The default mode mirrors §17: divergence must be supplied; only controlled-ablation research may toggle it off. The toggle lives in `universal.toml`.

2. **Live by default.** `divergence_enabled = true` out of the box. No shadow-first phase. The whole point of CDSFL is structured novelty under structured falsification — the directive is not an experimental add-on.

3. **Zero schema math changes.** R_k(i), the recursive corroboration equation (the iterative residual-risk self-assessment after round i), is untouched. The penalty multiplier is an optional pre-factor that can be wired in after Exp 39 baseline measurement, or left unwired so Exp 40 can isolate the prompt-level effect alone.

4. **Defensive under all conditions.** Parse failure returns empty records, not exceptions. Unknown dimensions resolve to `None` and surface as a validation reason. Disabled directive returns a compliant neutral record so downstream code never branches on the toggle.

5. **Isomorphism detection is lexical, not semantic.** MVP uses Jaccard (a token-overlap similarity metric) over normalised token sets: deterministic, fast, no model dependency. Swapping in sentence-transformer embeddings is a follow-up (scheduled as Exp 39 Phase 2).

---

## The wiring decision

The penalty multiplier function is exposed but **not yet wired into `compute_rk()`** in the reference runner. This is deliberate.

The Invention Engine scoping memo (written earlier today) recommended sequencing the work after the Exp 39 baseline:

1. Run Exp 39 with §17 live, no divergence directive → baseline measurement of measurement-to-correction effect.
2. Add divergence directive (§18) → Exp 40 or §18-extension run.
3. Measure novelty-yield (`nu_k`, the literature-novelty score) delta, corroboration (`R_k`) delta, convergence-rounds delta, novel-AND-survived ratio.

Each change gets its own signal and effects attribute cleanly. Wiring the penalty into R_k now would compound two independent interventions. The penalty function is there when Exp 39 data tells the team how to calibrate it.

---

## The directive text

§18 opens by naming the gap: the bold-conjectures arm of Popper's method is missing from CDSFL, and the asymmetry is arbitrary. It lists the five allowed dimensions explicitly. It defines the two admissible structures (alternative on a named dimension, or scoped null-justification). It rejects cosmetic rewordings and states the double penalty. It explains the interaction with HARD constraints — divergence operates only in SOFT space; physics, mathematics, law, and safety remain inviolable for the primary and every alternative. It explains the interaction with §17 — a prior-round refuted alternative resurfacing unchanged is treated as a resubmitted flagged finding and is inadmissible. It notes that disablement is a controlled-ablation tool, not a user convenience, and that disabling reverts CDSFL to pure error-correction mode.

The final footnote captures the frame: **the schema stops being a pure critic and starts being an invention engine. This is the missing symmetry in Popper's arms and the reason CDSFL was built.**

---

## The tests — 52 across 7 classes

| Class | Tests | Coverage |
|---|---|---|
| `TestAllowedDimensions` | 6 | Canonical set, each dimension parseable, synonym normalisation, unknown-dimension rejection, hyphenated variants |
| `TestParseAlternativeBlock` | 9 | Header tolerance (parenthetical, bracket, dash, follow-up, bold, markdown heading), empty input, no-header input, multi-alternative parsing |
| `TestIsomorphismScoring` | 7 | Identical → 1.0, disjoint → 0.0, symmetry, both-empty convention, one-empty, partial overlap in (0, 1), stopword-only does not spuriously match |
| `TestValidateAlternative` | 5 | Valid passes, missing dimension fails, isomorphic fails, over-length fails, multiple failures all reported |
| `TestParseNullJustification` | 7 | No block → `None`, empty → `None`, basic extraction, alternate header forms, length-ok, too-short, missing |
| `TestBuildDivergenceRecord` | 7 | Valid alt compliant, null-only compliant, isomorphic non-compliant, no-engagement non-compliant, missing-dimension non-compliant, short-null non-compliant, one-of-many admissible is enough |
| `TestDivergencePenalty` | 5 | Compliant → 1.0, isomorphic → 0.60, no-engagement → 0.70, engaged-failed → 0.85, all results in (0, 1] |
| `TestDisabledDirective` | 2 | Disabled returns compliant neutral record; penalty is identity |
| `TestConfigFromDict` | 4 | Empty dict disabled, None disabled, full payload loaded, partial payload uses defaults |

All 52 green on first real run. Full regression: **912/912 pass** (832 baseline + 28 sv-script + 52 divergence).

---

## What this changes in practice

**Before today.** A model produced a primary finding and stopped. The framework measured whether the finding survived falsification. Novelty was inherited — whatever the model chose to volunteer.

**After today.** A model producing only a primary finding earns a failed compliance verdict. The model must enumerate an alternative mechanism, assumption, scope, timescale, or tradeoff — or explicitly justify why no distinct alternative exists. The schema can detect and reject cosmetic rewordings. The falsification machinery filters across a wider candidate space.

The pathway to solving problems in a single locally-optimal way is closed. The pathway to solving problems with reasoned alternatives is the only admissible pathway.

---

## Summary

| Artefact | Size |
|---|---|
| `bench/dm/_divergence.py` | 443 lines (new) |
| `cdsfl_operational.md` §18 | ~90 lines (new) |
| `cdsfl_core_formal.md` table | 1 new row |
| `universal.toml` + `schema.toml` | 6 new parameters, registered both places |
| `test_divergence_directive.py` | 52 tests across 7 classes (new) |
| Schema math changes | **zero** |
| R_k pipeline wiring | deferred by design — penalty function exposed for post-Exp 39 calibration |
| Regression impact | **912/912 pass** |

The framework now asks both sides of Popper's question:

- *Is this model's answer correct?* (§17, built yesterday — the critic)
- *Is there a better answer that would also be correct?* (§18, built today — the generator)

That second clause is what turns a verification framework into an invention engine.

---

## References

- `bench/dm/_divergence.py` — core module
- `bench/directives/universal/cdsfl_operational.md` §18 — directive
- `bench/directives/universal/cdsfl_core_formal.md` — Classification Summary table (new row)
- `bench/cdsfl_registry/universal.toml` `[divergence]` — live-default config
- `bench/cdsfl_registry/schema.toml` `[divergence.*]` — parameter registration
- `bench/tests/test_divergence_directive.py` — 52 tests
- `experimental_notes/Invention_Engine_Divergence_Directive_2026-04-15.md` — scoping memo (companion)
- `experimental_notes/Feedback_Channel_Explanation_2026-04-15.md` — §17 plain-English summary (sibling)
