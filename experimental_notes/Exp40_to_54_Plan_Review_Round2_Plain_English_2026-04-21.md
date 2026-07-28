# What the plan review panel decided in Round 2

21 April 2026.

CDSFL, the Constraint-Driven Synthesis and Falsification Loop, is the methodology under test in this project: a Popperian arrangement in which several frontier models produce, critique, and attempt to falsify technical claims under a shared rule set. Experiments 40 through 54 are the fifteen-experiment arc that tests how CDSFL behaves across a widening set of technical domains. Before those experiments begin, the plan that orchestrates them is itself reviewed by the same five-model panel that will run them (Claude Opus 4.6, Codex GPT-5.4, Gemini 3.1 Pro, ChatGPT GPT-5.4, and DeepSeek Reasoner).

## Summary

Round 1 of the plan review left six questions where the panel had split — different models favouring different answers, with no single conclusion emerging from each question. Round 2, held on 21 April 2026, used a stricter discussion discipline to force the panel either to converge on one answer per question, or to mark the remaining disagreement as the founder's to resolve. Five of the six questions converged. The sixth, concerning Experiment 54's first cell, remains for the founder to decide at Experiment 54 entry.

This note walks through each of the six questions in plain English: what the question asked, what the panel settled on in Round 2, and what that means in practice for the experiments ahead.

## How Round 2 was run

The discussion discipline used in Round 2 is called **compelled convergence**, implemented via a **star-topology** conversation in which the working-session director sits at the hub and no model talks directly to any other. Each model must read the panel's current state, either yield to the majority position or defend its own position with evidence, and — if it cannot convince the others — accept the majority answer rather than continuing to argue in parallel. The goal is to produce one panel answer for each question, rather than handing the founder a menu of five conflicting opinions.

## Question 1 — is the pre-launch work for Experiment 40 complete?

The question was whether any unaddressed fix threatened the **gate condition** that tells the CDSFL loop when to stop a round of the experiment. Round 1 split three-to-two: three saying yes, F1 through F4 are sufficient; two saying no, something more is needed.

**Round 2 outcome.** Three of five yielded to accepting a Codex-proposed addition. The addition, a preflight check on the **admissibility parser** (the component that decides whether a claim is well-formed enough to enter the loop), should be folded in not as another fix item, but as part of a validation step called **Gate C**. Two of five held the position that F1 through F4 were sufficient on their own. Codex's own proposal was accepted as the unifying position.

**What this means in practice.** The plan treats F1, F2, F3, and F4 as the only fix items, and adds the preflight as a Gate C step wired into the Experiment 40 launcher. F1 is a sandbox allow-list around the project's SymPy component, so that admissibility and verdict checks do not silently return "uncertain" because the sandbox blocks ordinary arithmetic. F2 activates an identity-mode wrapper around the runner's core recurrence call, so that a later non-identity rewrite lands on already-instrumented code rather than on a fresh code path. F3 adds a debug-time assertion that the wrapper's identity-mode output matches the bare call within a tight tolerance, as a regression guard against future refactors. F4, landed earlier in the arc, is the closure-state lexicon that labels every schema element as `library_complete`, `shadow_integrated`, or `live_operational`, so that the state of each component is inspectable from the code and the documentation at a glance; it is a documentation-standard fix, not a code fix. Decision 4 in the companion five-decision register tracks the Gate C launcher wiring as still-open.

## Question 2 — will Experiment 54 interact with earlier experiments in a way that requires thresholds to be frozen?

Experiment 54 is a **factorial** experiment — one that varies two treatments across its four cells, labelled A, B, C, and D, to see how they interact. The panel was asked whether running those four cells with differently-tuned thresholds would contaminate the comparison. Round 1 split three yes, two no.

**Round 2 outcome.** Five of five yes. Thresholds must be frozen before Experiment 54, and applied identically across Cells A, B, C, and D. The thresholds in question are three: **admissibility** (whether a claim is allowed into the loop at all), **severity** (how serious a finding is rated when the loop produces one), and **tier** (how findings are ranked for subsequent attention). DeepSeek withdrew an earlier related concern about a different low-level interaction, judging on its own reread that it was a separate issue not germane to threshold freezing.

**What this means in practice.** Before Experiment 54 begins, the three thresholds are fixed at specific values and not re-tuned during the factorial. Decision 5 in the companion register tracks the freeze as still-open pending the close of Experiment 53.

## Question 3 — is the evidence for Experiment 54's first cell sufficient?

Cell A of Experiment 54 is the factorial's baseline cell, with both the §17 feedback directive and the §18 divergence directive off. The archive Cell A compares against is the one produced across Experiments 36, 37, and 38, where the runner ran in that same baseline configuration. Between that archive and Experiment 54, the runner has evolved substantially, because every experiment in between has been a falsification of the methodology by the methodology itself — the project's standing **ouroboros** framing, in which the instrument and the thing being measured are the same system at different points in its development. The panel's technical label for the resulting concern is a **version confound** at the measurement level: the archived results were produced under a code path that is not identical to the current one. Whether the confound is decision-changing is what the panel was asked to adjudicate.

Round 1 split four to one: four yes-conditional (expand the integrity check and keep a fresh-run fallback); one no (skip the integrity check, fresh-run unconditionally).

**Round 2 outcome.** The split persists at three to two. Three of five yielded to Gemini's unconditional fresh-run position; two of five held the integrity-check-first-with-fallback position. Both sides agree the version-level difference is real — what they differ on is operational ordering, not on whether the ouroboros-framed evolution of the runner has any measurement consequences.

**What this means in practice.** The panel could not converge on one answer, and the plan carries both paths as layers of a **three-layer Cell A strategy**: Layer 1 is the archive-integrity check; Layer 2 is the fresh-run fallback; Layer 3 is a sensitivity-bounding check that measures how much any given result depends on the archive versus the fresh run. The founder selects which layer is treated as authoritative at Experiment 54 entry. Decision 2 in the companion register carries this decision forward.

## Question 4 — does enabling shadow-mode components now carry offsetting risks?

A **shadow-mode component** runs alongside live code and receives the same inputs, but never affects the outcome, so its behaviour can be audited before it is promoted to live operation. Three such components, labelled K, L, and M, had been ready for promotion for some time. The question was whether promoting them now, rather than deferring, would introduce **silent coupling** — the risk that a shadow component begins to influence the outcome through a side channel before it is formally activated.

Round 1 split two "safe" and three "conditionally safe".

**Round 2 outcome.** Five of five conditionally safe, with a **non-distortion check**: before any shadow component is promoted to live operation, it must produce empirical evidence that it did not distort the live output during its shadow period. Gemini and DeepSeek yielded on a silent-coupling counterexample raised by the other models. The project's standing policy of enabling shadow elements early rather than deferring was ratified, with the non-distortion requirement as the bounding condition.

**What this means in practice.** On 21 April 2026 the shadow-audit logging around K, L, and M was enriched so that it captures the evidence the non-distortion check needs. The set of domains counted as "live specialists" (the cells that contribute to the panel's synthesis step) was not yet flipped to include K, L, or M; that flip is held pending the audit evidence.

## Question 5 — should the ordering of Experiments 41 through 53 be changed?

Round 1 split two no-reorder, three "yes" — but the three who said yes proposed three mutually incompatible replacement orderings.

**Round 2 outcome.** Five of five no-reorder. The three incompatible alternative proposals could not converge on a single replacement order, and none of them tightened the hard dependencies stated in the plan (for example, later experiments that build on earlier ones' runners or target articles).

**What this means in practice.** The current order of Experiments 41 through 53 stands. The alternative proposals are carried forward as watch-items for the post-mortem review of Experiment 49, in case its results motivate a reorder of Experiments 50 through 53. No action before that post-mortem.

## Question 6a — for Experiment 51's physics target, synthesise or adapt?

Experiment 51 tests CDSFL on a physics article. The question was whether the target article should be written for the purpose (**minimal native synthesis**) or an existing code module adapted in its place. Round 1 split four native, one yes to adapting a file called `composer.py` in the CDSFL registry.

**Round 2 outcome.** Five of five native. DeepSeek withdrew the `composer.py` claim on its own reread, judging that the file handles routing and composition across the CDSFL architecture, not physics reasoning, and so is not a candidate physics target.

**What this means in practice.** A short native physics module is to be synthesised for Experiment 51, of the order fifteen to twenty-five thousand characters. Decision 3 in the companion register tracks this target article and the three others as still-open.

## Question 6b — and for Experiments 47, 52, and 53?

Round 1 split three synthesise, one adapter, one synthesise-with-a-physics-exception.

**Round 2 outcome.** Five of five synthesise. Codex yielded on an **orthogonality** argument raised by the other models — orthogonality here meaning that two variables are meant to vary independently of each other. Using an adapter would conflate **c_ext** (a search-quality metric measuring how well the loop explores the claim space) with **target-module validity** (whether the article under review is sound in its domain). Those are meant to be independent variables in the experiment design, and an adapter would bind them together in a way that muddies the interpretation.

**What this means in practice.** Four target articles (one each for Experiments 47, 51, 52, 53) are to be written natively, each approximately fifteen to twenty-five thousand characters, under the same standard. Decision 3 in the companion register covers all four.

## What now remains open

Of the six questions, one (question 3, Experiment 54 Cell A) carries forward for the founder to decide at Experiment 54 entry. The other five are closed; their operational consequences are tracked in the companion five-decision register titled "Five open founder decisions for the Exp 40–54 arc" of 21 April 2026.

The next review trigger is the launch of Experiment 40 itself: with Round 2 closed and the pre-launch code fixes landed, the panel's recommendations are now ready for the founder's go or no-go call.

Written under CDSFL note standard v1 (21 April 2026).
