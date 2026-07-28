# Exp 40 Pre-Launch Focused Round 3 Outcome and Three-Round Synthesis

2026-05-13 02:06 BST

## Summary

The three-question compelled-convergence follow-up round dispatched at 02:00 BST on 13 May 2026 closed cleanly. All five panel members returned within 166 seconds wall-clock. Two of the three questions converged 5/5; the third (the F3 closure-state label) converged 4/5 with the dissent neither blocking the consensus nor refuting it. Verification against the source TOML routing files resolved two of the four sub-items in Q3 in favour of the single-model dissent rather than the four-model majority, because the majority anchored to a partial routing excerpt in the consolidated plan that did not match the actual TOML. The source files won, as Find-Follow-Analyse-Fix-P-pass discipline requires.

The full set of focused panel rounds for Experiment 40 pre-launch is now closed. Round 1 (21 April 2026, plan review) consolidated the Exp 40-54 plan and surfaced the fix items F1 through F3 plus the gap-closure list G1 through G9. Round 2 (10 May 2026, focused follow-up) addressed items not previously panel-reviewed: G2 code correctness, section 2a target-article scope briefs, section 6b trigger specifications, the trigger-versus-implement policy for G6/G7/G8, and the closure-now disposition of the four 22-April-residuals. Round 3 (13 May 2026, this round) closed the residual divergence from Round 2 under compelled convergence.

The runtime code is closed. The four residuals are closed. The §6b triggers are reworded to align with structural reality. The F4 closure-state lexicon now carries a fourth label (`tripwire`) that relieves the edge-case pressure on flag-gated assertions like F3. The Exp 51 / 52 / 53 native-module scope briefs are aligned to the actual TOML routings. Experiment 40 is ready to launch.

## Round 3 panel composition (unchanged from Round 2)

| Slot | Model | Route | Identifier |
|---|---|---|---|
| CC2 | Claude Opus 4.7 | Claude CLI piped mode (Max subscription) | `opus` |
| Codex (cx) | GPT-5.5 | OpenRouter | `openai/gpt-5.5` |
| Gemini (ge) | 3.1 Pro Preview | OpenRouter | `google/gemini-3.1-pro-preview` |
| ChatGPT (cgpt) | GPT-5.5 | OpenRouter | `openai/gpt-5.5` |
| DeepSeek (ds) | V4 Pro | DeepSeek direct API | `deepseek-v4-pro` |

## Round 3 wall-clock and yield

| Model | Response chars | Wall-clock |
|---|---|---|
| Gemini 3.1 Pro | 5049 | 36.6 s |
| Codex GPT-5.5 | 5996 | 62.3 s |
| ChatGPT GPT-5.5 | 7465 | 44.7 s |
| CC2 Opus 4.7 | 6564 | 103.1 s |
| DeepSeek V4 Pro | 5000 (+15874 reasoning) | 166.4 s |

Total prompt size per model: 82,093 characters (system 11,821 + user 70,272 — the user prompt embedded the full Round 3 framing, the three questions with their full Round 2 dissent context, the consolidated plan as background, and the response-format constraints).

## Per-question outcome

### Q1 — Exp 44 versus Exp 49 as primary trigger for G6 and G7

**Convergence: 5/5 on B** — reword §6b to make Experiment 49 the primary trigger, with Experiment 44 retained as an early-observation checkpoint. The migration logic between the two is unchanged. Trigger fires on the first observed multi-specialist verdict conflict (G6) or MERGE deadlock (G7) from Experiment 49 onwards; Experiment 44 logs are still parsed in case any anomalous cross-specialist path is exercised, but cross-specialist co-rule is not in its dispatch by design.

Round 2 had divided 4/1 on this point: four models endorsed §6b as written (Exp 44 primary, Exp 49 migration), DeepSeek dissented with structural analysis showing Exp 44 composes mathematics-specialist + composer + macrophage outputs and therefore lacks multi-specialist co-rule. Round 3 put DeepSeek's argument explicitly in front of the four models that had previously endorsed Exp 44 primary. All four moved to position B (Exp 49 primary). Codex, ChatGPT, CC2, and Gemini each cited the structural argument back as the reason for the move. DeepSeek held the position it had originated.

§6b now reads with Exp 49 as the primary trigger for both G6 and G7, with Exp 44 logs parsed as an early-observation checkpoint. The change is wording, not logic — the migration clauses in the prior text already produced the same operational behaviour, but the wording now matches reality.

### Q2 — F3 DEBUG_CHANNEL_CHECK closure-state label

**Convergence: 4/5 on C (new `tripwire` label)** — F3 takes a newly-defined fourth lexicon label, `tripwire`, that captures flag-gated runtime guards which are off by default but become assertive when toggled. CC2 held the prior position A (`library_complete` is the best fit given the existing three-label lexicon). The other four moved to C and articulated the architectural argument: the existing lexicon was designed for components that are off, observing, or driving live decisions; F3 fits none cleanly because it is off-by-default-but-assertive-when-flagged. Adding `tripwire` solves the labelling problem permanently rather than forcing F3 into a poor fit.

The `tripwire` definition folded into the F4 lexicon in `resources/ONBOARDING.md`:

> Code is present in the live or dev/CI pipeline and is observation-only by default — off, or on-emit-only — but becomes assertive (halts the run, blocks the gate, or otherwise drives an outcome) when an explicit flag (environment variable, config key, or CLI option) is set. Distinguished from `library_complete` because the code IS hooked into a pipeline path; distinguished from `shadow_integrated` because its activated behaviour can drive run-level outcomes rather than just emit observations.

Promotion order updated: `library_complete → tripwire (if applicable) → shadow_integrated → live_operational`. The tripwire tier is optional in a component's lifecycle; most components flow directly library-complete → shadow-integrated → live-operational without passing through it. Tripwire applies specifically to flag-gated assertions and runtime guards that exist to catch refactor drift, mismatch, or other should-never-happen conditions and halt rather than observe.

F3 was relocated in the Component Closure-State Index from `library_complete` to `tripwire`. The `library_complete` section of the index is now empty; the next entrants are expected during target-article drafting for Experiments 47, 51, 52, 53.

CC2's dissent on Q2 is defensible — its argument is that the three-label lexicon, as it stood, did not need expansion because F3 fits `library_complete` reasonably (inert by default, hooked-on-flag is a developer affordance). Under compelled convergence, the dissent does not block the consensus position because the four-model majority is on the new label and CC2 does not refute the proposed addition; it simply prefers the existing lexicon. Folding the new label in is the right move and it is what was applied.

### Q3 — Experiment 51 / 52 / 53 brief refinements

Four sub-items, each requiring a single yes/no answer:

**Q3(a) Add z3-routable conservation-violation cluster to Exp 51 physics brief.** Round 3 panel split 4/1: Gemini, Codex, ChatGPT, DeepSeek answered NO, anchoring to the §2a routing excerpt "physics mathematical → sympy + dimensional_analysis + astronomical", which does not include z3. CC2 answered YES, anchoring directly to the source file `bench/cdsfl_registry/domains/immune/physics.toml`. Verification under sy (file inspection) found the source TOML routes mathematical claims to `["sympy", "dimensional_analysis", "z3", "astronomical"]` AND logical claims to `["z3", "sympy"]`. **CC2 was correct. The four-model majority anchored to a partial, misleading excerpt in §2a.** Under Find-Follow-Analyse-Fix-P-pass discipline, the source wins.

Fold-in applied: a fifth claim cluster ("Logical / conservation-violation claims") added to the Exp 51 brief, with explicit z3 routing for propositional structures the specialist can test for unsatisfiability. Example claim added to the brief: "energy in = energy out + dissipation; dissipation asserted negative — z3 derives the contradiction." The §2a routing text for Exp 51 was also corrected to name z3 in both mathematical and logical routings.

**Q3(b) Rename `collections.Counter` → `stoichiometric_balance` in Exp 52 chemistry brief.** Round 3 panel **5/5 YES**. Anchored to `bench/cdsfl_registry/tool_manifest.toml`: `stoichiometric_balance` is the manifest entry name for the routed atom-balance verifier; `collections.Counter` is the underlying stdlib primitive used inside the routed tool. Briefs name manifest entries, not primitives. Fold-in applied.

**Q3(c-units) Drop `astropy.units` from Exp 53 engineering brief cluster 4.** Round 3 panel **5/5 YES-drop**. Anchored to `bench/cdsfl_registry/domains/immune/engineering.toml`: `astropy.units` is not declared in any engineering routing. The §2a brief had been carrying a tool not actually routed. Fold-in applied.

**Q3(c-LP) Add a linear_programming-routable optimisation cluster to Exp 53.** Round 3 panel split 4/1: Gemini, Codex, ChatGPT, DeepSeek answered NO-skip, anchoring to the §2a routing excerpt "engineering mathematical → sympy + uncertainty_propagation + dimensional_analysis", which does not include linear_programming. CC2 answered YES-add, anchoring directly to the source file `bench/cdsfl_registry/domains/immune/engineering.toml`. Verification under sy (file inspection) found the source TOML routes mathematical claims to `["sympy", "dimensional_analysis", "linear_programming"]`. **CC2 was correct. The four-model majority anchored to a misleading §2a excerpt.** Fold-in applied: a fifth claim cluster ("Optimisation / constrained-design claims") added to the Exp 53 brief, with explicit linear_programming routing. Example claim added: "minimise mass subject to safety-factor ≥ 1.5, deflection ≤ δ_max, cost ≤ budget" with stated optimal vertex. The §2a routing text for Exp 53 was also corrected.

## Three-round synthesis — what the rounds collectively closed

**Round 1 (21 April 2026, plan review).** Five-model panel reviewed the consolidated Exp 40-54 plan. Closed: F1/F2/F3 strategy, Gate C admissibility-parser preflight, Stage 6 calibrator design, scope and ordering for the fifteen-experiment arc, RQ6b native-synthesis commitment for Experiments 47, 51, 52, 53, K/L/M shadow non-distortion principle, shadow-promotion-now policy. Five material fold-ins applied to the plan in the same session.

**Round 2 (10 May 2026, focused follow-up).** Five-model panel reviewed items left open by the 22 April founder oversight Q&A. Closed: G2 code-correctness fix at `bench/immune_agents.py:5411-5421` (5/5 endorsed); section 6b trigger specifications for G6, G7, G8 (4/5 endorsed structure, DeepSeek dissent on Exp 44 trigger); trigger-and-wait policy for G6/G7/G8 (5/5 endorsed); closure-now disposition of the four 22-April residuals (5/5 on three of four; split on F3 label). Two high-confidence fold-ins applied: Exp 47 biology brief gains z3 logical cluster + corrected codon-error attribution; §6b carries a clarifying note on Exp 44 trigger expectations.

**Round 3 (13 May 2026, compelled-convergence follow-up).** Five-model panel forced convergence on the three Round-2 divergent items: Exp 44 vs Exp 49 trigger (5/5 reworded to Exp 49 primary); F3 closure-state label (4/5 adopted new `tripwire` label, lexicon expanded to four labels); three Exp 51/52/53 brief refinements verified against source TOMLs and applied where source-verification supported them (z3 cluster added to Exp 51; `stoichiometric_balance` rename in Exp 52; `astropy.units` dropped from Exp 53; linear_programming cluster added to Exp 53). All routing-text mis-quotations in §2a corrected.

The cumulative effect across the three rounds: every panel-reviewable item touching Experiment 40 pre-launch is now on a converged position with explicit anchors to either code file:line citations, TOML manifest entries, or experimental-plan section numbers. The "items flagged for founder review" list that closed Round 2 is now empty.

## State at session close (02:06 BST, 13 May 2026)

| Field | Value |
|---|---|
| Branch | `exp39-experimental` |
| HEAD before this session-segment | `4d4d4f1` (Round 2 sv) |
| Working tree | dirty pending Round 3 sv (this note + plan fold-ins + ONBOARDING lexicon extension + new Round 3 confer script + Round 3 logs) |
| Tests | 1311 collected |
| Outstanding pre-launch blockers | None |
| Outstanding founder-judgement items | None from the focused rounds |
| Next operational step | Comprehensive documentation sweep (README first, then ONBOARDING, RECOVERY, MATHEMATICAL_APPENDIX, PAPER, GLOSSARY, ARCHITECTURE, REPRODUCING, CURRENT_STATE), followed by Experiment 40 dispatch |

## Path forward

The focused-round workstream is complete. The remaining items in the seven-day window the founder named for this session are operational rather than deliberative: a comprehensive sweep across the canonical documents to ensure everything reflects current project state (README leading, as the founder flagged README neglect as a real prior failure); Experiment 40 dispatch and post-mortem; then the rest of the Experiment 40 to 54 arc with fold-ins between each. None of these require further panel input under the current scope.

## Next review trigger

When the founder resumes work, the natural sequencing is to read this note plus its TTS companion, then either green-light the documentation sweep + Experiment 40 dispatch chain or surface any remaining concern. There is no autonomous decision waiting that the agent can take without founder input on the broader sweep + launch sequencing.

Written under CDSFL note standard v1.1 (10 May 2026).
