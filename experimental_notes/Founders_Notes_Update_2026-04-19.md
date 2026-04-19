# Founder's Notes — April 2026 Update

**Date:** 19 April 2026
**Document updated:** `docs/FOUNDERS_NOTES.md`
**Scope:** Twelve new dated entries covering the period 5 to 19 April 2026, inserted between "Complementarity, Not Competition (4 April 2026)" and the closing reflection.
**Voice:** first-person reflective, consistent with existing entries. Observation and lesson structure preserved. No decoration, no theatrics.

---

## Background

`docs/FOUNDERS_NOTES.md` is the long-form reflective record of the CDSFL project. It sits alongside the more technical `resources/ONBOARDING.md` and `resources/RECOVERY.md`, but serves a different function: it is where the project's designer writes out, in first person and with the benefit of short-range hindsight, what was learned from each phase of work. Prior to this update the final dated entry was "Complementarity, Not Competition" from 4 April 2026. Substantive experimental and architectural work has continued every day since. The update records that work.

Twelve entries have been added. Each corresponds to a distinguishable phase of work, ordered by the date on which the phase closed. Numbers are preserved directly from the canonical project record — `ONBOARDING.md`, the mathematical appendix, the experimental-notes archive — so that a reader can cross-reference any specific claim.

## Entries added

### 1. The Confound Cascade (5 April 2026)

Experiment 29 converged cleanly at nine rounds, 340 findings, and an inter-rater agreement of 0.960. Experiments 30, 31, and 32, planned as incremental validation, produced a cascade of confounds. Experiment 30 failed to converge across 15 rounds and 378 findings. Deep analysis identified three overlapping causes: directed messaging sustaining genuine novelty rather than depleting it, two models resetting finding identifiers between rounds and producing apparent duplication, and 62 parser-garbage entries that were not findings. The deeper diagnosis was fix-level churn: 232 proposed fixes for roughly 83 distinct bugs. The architectural response was a bug-closed gate — the first programmatically verified fix wins and subsequent findings about the same bug are rejected on sight. Experiment 31 reran with 39 fixes applied and still failed to converge; inter-rater agreement reached 0.619, but a deep-copy operation was severing the verified flag between rounds, leaving the bug-closed gate as dead code. Experiment 32 was a meta-experiment in which the panel was asked to analyse the convergence data. Four of five models recommended design parameters that would have reduced the ability to falsify convergence — a confound traceable to the anchoring framing of the question put to them. Prompt framing was recorded as a confounding variable in multi-model panels.

### 2. Model Relay versus Structured Blackboard (6 April 2026)

Experiment 34 introduced a structured-blackboard topology as an alternative to the earlier model-relay topology. Experiment 35 exposed the choice as a command-line switch, `--topology relay|star`. The shared infrastructure — finding registry, convergence gate, immune pipeline, endocrine health monitor, Merkle-sealed verification chain — was indifferent to which topology was active. When topology becomes a parameter rather than a commitment, the questions worth asking become experimental rather than architectural.

### 3. MIDCA Reassessment (7 April 2026)

The prior "six of eight with two partial" MIDCA-coverage summary became obsolete. MIDCA presumes a single reasoning substrate that monitors itself and carries state forward; CDSFL is substrate-agnostic by construction. The two MIDCA requirements most affected by substrate agnosticism — self-monitoring and cross-experiment memory — are distributed across the cell hierarchy and across Merkle-sealed verification chains respectively. The reframing produced eight additional coverage domains that MIDCA does not enumerate because its underlying single-substrate assumption forecloses them.

### 4. Mathematical Model Under Audit (7-8 April 2026)

A formal audit of the mathematical appendix returned internal consistency of 25 of 25 propositions. Two empirical claims were disputed; five framework gaps were confirmed. On 8 April the unified self-assessment equation R_k(i) was derived, collapsing three earlier formalisms into a single recursive form. The Popperian propensity parameter π vanishes from the recursion and is mathematically redundant. R_k(i) replaced the earlier C(n) corroboration function in the operational directives. Models now compute R_k at each round and carry it forward as the stopping heuristic.

### 5. Cell Type Architecture (9 April 2026)

The composition law for multi-cell admissibility was written down explicitly. Each cell contributes a gate value g in [0,1] and an evidence weight e with confidence w. Admissibility of a claim under a cell panel is the product of the gates: A equals the product of g_j. Aggregate evidence is the weighted aggregate of e_m under w_m. Per-claim score S_k equals A times E. The product structure gives any cell independent veto and allows confidence to accumulate only when every gate passes. The structural shape of the composition mirrors mammalian B-Cell and T-Cell co-evolution in the immune system.

### 6. Three-Layer Schema, Conversational Default, and the Ouroboros (10-11 April 2026)

Layer one is Meta structured-prompting format. Layer two is the CDSFL constraint set. Layer three is the session architecture, now conversational by default, with independent-turn-context (ITC) as fallback invoked only on model failure or context degradation. This inverts the earlier default. Experiment 38, on 11 April, tested the framework's reach by directing it at the reference runner itself — CDSFL reviewing its own orchestration code. The panel produced 545 raw findings and 169 canonical across 24 rounds over an eight-hour wall-clock cap. The Ouroboros cell — literature-checking discipline applied by the framework's own models to findings the framework has produced — is the inbuilt protection against rediscovery mistaken for invention.

### 7. Tranches A, B, and C — the B-Cell Complex (13-14 April 2026)

Three sequential sessions on 13-14 April reorganised the B-Cell specialist dispatch. Tranche A was housekeeping (sv sequential-reading protocol, CrossHair reclassification). Tranche B added five new specialist wrappers (CrossHair for behavioural contracts, RDKit for chemistry structure, Biopython for biological sequence validation, scikit-learn for ML claims, NetworkX for graph-theoretic claims); the earlier session had added nine (pint, uncertainties, stoichiometric balance, PuLP, astropy, mypy, ruff, bandit, dis). Tranche C refactored a 46-line elif chain into a 12-line manifest-driven loop. The dispatch manifest at `bench/cdsfl_registry/tool_manifest.toml` now carries 18 active entries plus 2 delegated. Adding a new B-Cell specialist is a TOML-only edit. All three tranches preserved the 793-test regression throughout. Session sequencing was itself a response to an Anthropic API 500 earlier that day, which had killed a single 580-line edit.

### 8. Stage 6 — Two-Dimensional Novelty (14 April 2026)

Literature novelty is now measured on two dimensions rather than one. Nu_k is how unprecedented a claim is against external sources. C_ext is how thoroughly the literature was actually consulted. The composition with internal novelty is multiplicative: eta_combined equals eta_int multiplied by one minus c_ext multiplied by one minus nu_k. Strong external search of an already-published finding (nu_k near zero, c_ext near one) pulls eta_combined toward zero regardless of how novel the finding looked internally. Confer rounds produced seven corrections. Abstraction is context only — it does not modify scores. A metric with two coupled dimensions rewards disciplined behaviour in a way that a single dimension cannot.

### 9. The Feedback Channel — Section 17 (15 April 2026)

The §17 feedback channel closed the gap between schema measurement and model correction. Prior to this session, B-Cell verdicts, admissibility pass/fail, near-duplicate scores, and R_k discrepancy were being written to logs but never routed back to the models that produced the findings. The new module `bench/dm/_feedback.py` is 533 lines, the new §17 directive is approximately 90 lines, and the new test file adds 39 tests. Full regression held at 832. Four design principles governed the build: imperative rather than advisory (must address, with counter-receipts from the model's own tool), live by default rather than shadow-first, no changes to the underlying mathematics, defensive under all conditions. The before-and-after is concrete: a refuted finding in round one can no longer reappear unchanged in round two.

### 10. Divergence Directive — CDSFL as Invention Engine (15-16 April 2026)

The §18 divergence directive completed the Popperian symmetry. Models must now accompany each primary finding with at least one alternative differing on one of five dimensions — mechanism, assumption, scope, timescale, or tradeoff — or supply a scoped null-justification of at least sixty characters. Cosmetic rewordings are rejected by an isomorphism check using Jaccard over normalised token sets, default threshold 0.85, double penalty for isomorphic-only submissions. A five-panel review put Stage 6 mathematics to the panel as binding arbiter. All five models converged unanimously on the channel-assignment question: the §18 multiplier is not on R_k (category error — R_k measures validity, §18 is generator-side novelty enforcement), but on eta_int. The function `divergence_penalty_multiplier` was renamed `eta_int_modulator`. The 75-test divergence module survived a three-round review cycle. CDSFL now has both Popperian arms present: severe tests through §17 and FFAFP admissibility, bold conjectures through §18.

### 11. Experiment 40 Stage 3 Closure (17-18 April 2026)

The Experiment 40-54 plan was drafted on 17 April: fourteen single-target experiments mapped one-to-one from the Experiment 39 sub-experiments, each with a right-sized decomposed article, plus Experiment 54 as the integration run with a two-by-two factorial for §17 and §18 attribution. A new reference runner was scaffolded as a pristine 4,344-line copy of the frozen runner-one. Phase A added 98 new tests across six plan items. Phase B added 200 more tests across seven further items. Test suite stands at 1,250 passing in twenty minutes of wall-clock. Two items remain gated: the live-promotion flip for physics, chemistry, and engineering specialists awaits broader tool-coverage judgement, and the runtime call-site assertion awaits Experiment 54's integration wiring. A significant regression was identified and delegated to a separate session: the SymPy verification wrapper silently returns UNCERTAIN on every claim because the subprocess sandbox uses `global_dict` with an empty `__builtins__`, preventing SymPy from constructing integer literals.

### 12. README v3, the `rg` Command, and the Public Surface (18-19 April 2026)

A third README draft was written on 18 April, rebuilt on the foundation of an April 2026 blog post rather than the previous version's section plan. The draft integrates Stage 6 literature-calibrated novelty, §17 feedback channel, and §18 divergence directive into the opening framing. Hossenfelder's early 2026 article on rediscovery risk in AI-assisted mathematics is cited as the direct prompt for the Stage 6 extension. A thirteen-point correction sweep on 19 April stripped Experiment 39 and 40 references from the README (belongs in RECOVERY.md and experimental_notes), named the Ouroboros cell on first mention, added a "remarkable-fact" framing of the five-model heterogeneous panel to the abstract, made the tool-deterministic constraint box load-bearing in Parts 1 and 5, documented R_k(i) in §6.5 as the models' own reasoning methodology from Experiment 37 onwards, extended substrate-agnosticism framing to human teams and hybrid panels, and gave the human-in-the-loop definition its own block. A new metacognitive command `rg` was introduced: before producing new output on a named topic, re-read the anchoring resources — persistent-memory files, canonical project docs, experimental notes, directive files — and name the resources consulted in a one-line preamble. `rg` is narrower than `rt` (wholesale context rebuild) and narrower than `rs` (session-state restore). It is a surgical regain-context-on-named-topic, expected to be invoked routinely before significant writing work. The command was registered in four locations: the user's global directives, the project directives, `docs/REPRODUCING.md`, and the persistent-memory index.

## Summary

| Aspect | Value |
|--------|-------|
| File updated | `docs/FOUNDERS_NOTES.md` |
| Entries added | 12 |
| Period covered | 5 April 2026 through 19 April 2026 |
| Insertion point | after "Complementarity, Not Competition", before "Closing Reflection" |
| Voice | first-person reflective, consistent with existing document |
| Model-credit framing | avoided per public-attribution directive |
| Regression impact | none — documentation only |

## References

- `docs/FOUNDERS_NOTES.md` — primary target, updated
- `resources/ONBOARDING.md` — factual source material for dates, numbers, and commit identifiers
- `docs/MATHEMATICAL_APPENDIX.md` — source for R_k derivation, Stage 6 composition, FFAFP admissibility
- `experimental_notes/Feedback_Channel_Explanation_2026-04-15.md` — plain-English §17 companion
- `experimental_notes/Invention_Engine_Divergence_Directive_2026-04-15.md` — plain-English §18 scoping memo
- `experimental_notes/Refined_Unified_Equation_2026-04-08.md` — R_k derivation source
- `experimental_notes/Cell_Type_Architecture_2026-04-09.md` — composition-law source
- `bench/dm/_feedback.py` — §17 implementation
- `bench/dm/_divergence.py` — §18 implementation
- `bench/cdsfl_registry/tool_manifest.toml` — Tranche C dispatch manifest
- `~/.claude/projects/-Users-georgejackson-Developer-Projects/memory/rg_command.md` — `rg` command full protocol
