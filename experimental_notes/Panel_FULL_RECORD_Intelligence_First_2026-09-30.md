# Intelligence first, tools second: the panel refuted the brief, and the unit of admissibility is a claim

Record written 2026-09-30T23:48:21+01:00.

**This is the seats' own output, reproduced in full.** The Personalisation directive requires external review output preserved *"in full and in unfiltered format"* and says *"Never summarise in place of the full output"*. Any summary elsewhere is downstream of this file, not a substitute for it.

## The dispatch

**FREE SEATS ONLY. 0 paid dispatches, 0 spend.** Third design review held BEFORE implementation under the founder's 2026-09-30 policy. `PANEL_ONLY=cc2,fable`, because the harness warned that 4 of its 6 default seats are paid and his standing rule forbids paid dispatch without express authorisation.

| seat | route | elapsed | tool calls | passes |
|---|---|---|---|---|
| cc2 | claude_cli (Max) | 953.3 s | 136 | — |
| fable | claude_cli (Max) | 1554.7 s | 88 | 4 |

**5 figures were declared for RE-EXECUTION** rather than typed, and both seats confirmed all 5 reproduce. The brief also carried CC1's own reading explicitly marked for attack rather than as a premise.

## THE HEADLINE: BOTH SEATS REFUTED THE BRIEF'S CENTRAL FRAMING, IN THE SAME PLACE

**CC1 invented a verdict and briefed the panel on it.** The brief and its producer printed `ADMISSIBLE` or `INADMISSIBLE` from a truthiness test on an extractor's return. **There is no verdict named `INADMISSIBLE`.** The live vocabulary is `SK_ADMISSIBLE / SK_REJECTED / SK_NO_SCORE / SK_ESCALATE`, and measured here: the string appears **0 times in `reference_runner_v3.py` and 3 times in CC1's own producer**. Both example documents actually return **NO_SCORE**, which `docs/GLOSSARY.md:237` defines as *"S_k has no opinion"* — the correct answer rather than a defect. cc2 found it; fable confirmed the real verdict on 4 of 4 calls.

**And the mislabel was not cosmetic.** cc2: *"`_gateable_source` is not a triage before reasoning; it is an extractor INSIDE `compute_sk`, which scores a proposed fix. It was never asked whether a document is worth reviewing."* Its executed refutation of the brief's thesis is the cleanest in the round: *"the real gap is not that reasoning is gated — this brief has 0 fenced listings and I reasoned on it unimpeded."* CC1's 3-stage diagnosis rested on a component whose role it had mislabelled.

**Half the brief's specimen claim was true, and cc2 caught it with the brief's own material.** The example document claimed "the mean of 2, 4 and 6 is 4.5 and the standard deviation is 2.0". The mean claim is false. **The standard-deviation claim is true under the sample convention**: for that series the ddof=1 standard deviation is EXACTLY 2 — sympy returns the integer `2`, numpy 2.0000000000, mpmath 2.0 — while ddof=0 gives 1.6329931619. The brief called the whole claim false by quoting numpy's DEFAULT without naming the convention. cc2 turned that into its Q4 answer: *"a connector given the stated question returns the right number and never asks which convention the author meant."*

## Where the seats AGREE

1. **The unit of admissibility is wrong, and it is one level above where A19 puts it.** cc2: *"S_k classifies neither target nor element — it classifies a FIX."* fable, of `compute_sk` and the routing ladder together: *"does NOT lack REASON/REDUCE — it has all three stages for findings; it lacks them as the unit of admissibility."*
2. **The remedy is a claim-level channel bound to existing machinery.** Both recommend it; both leave S_k untouched; neither invents new science. fable falsified 3 of its own 4 candidate architectures to reach it.
3. **`ADMISSIBLE` is unreachable on any prose target**, so repairing the detector alone buys zero reachable states. cc2's sweep plus the project's own producer, 20 evaluations, 0 admitted.
4. **The harness never decided wrongly during the review.** fable, having driven it including on itself: *"every failure is a correct abstention on the wrong trigger (blindness, not corruption)."*
5. **The boundary of inadmissibility should be an OUTCOME, not a pre-gate** — zero decidable claims after looking, rather than a syntactic gate before.
6. **Neither seat will guess whether a small classifier can draw that boundary.** fable specifies a labelled set with executable ground truth instead; cc2 declines likewise.
7. **`n*` is not recoverable from the current archive**, and the coefficient pair (4.89, 0.709) is a chimera assembled from 2 different records.

## Where they DISAGREE, preserved, and ADJUDICATED BY MEASUREMENT rather than by vote

**Q6(c), rounds from target complexity.** cc2 reported that `gamma_input` gives **9 distinct values across 9 targets**, r-squared above 0.99, computable before a run. fable reported that the archive covers **only 2 distinct targets** and that round counts are configured caps, so `n*` as a function of target complexity is **not estimable**.

**MEASURED HERE over the 9 non-harvest reports carrying `target_complexity`: 2 distinct targets** — `bench/cdsfl_registry/engine.py` 7 times and `bench/BUILD_BOT_TEST_BENCH_FIX_SPEC.md` twice — **and 3 distinct `gamma_input` values** (0.146807, 0.497905, 0.512858). Round counts are `(8,8)` 4 times, `(8,4)` 3 times and `(8,1)` twice, so only 4 of 9 runs used their cap and the cap was 8 in all of them.

**fable is right. cc2 counted REPORTS as TARGETS** — 9 reports became "9 targets" — which is the copies-as-originals conflation in its fifth guise in a single day. `feedback_no_model_voting` is why this was settled by counting rather than by preferring a seat.

## New findings, and 2 bear on the founder's hard rules

**TWO LIVE FENCED-PYTHON EXTRACTORS HAD DRIFTED.** `bugzilla_loop._PY_FENCE` and `reference_runner_v3._gateable_source` answer the same question about the same target and split on **3 of 13 realistic shapes** — a tilde fence, a fence carrying an info-string attribute, and a CRLF-authored document — every one in the direction "the runner sees code, bugzilla does not". On such a document S_k's prose path engages while `bugzilla_loop` logs *"carries no fenced Python listing"*, which is false of the document, and the weaker claim is the one that reaches the record. cc2 also reports a THIRD extractor, `_MD_PY_FENCE`, with **zero callers** — reported, not removed.

**A MEASURED NON-CURE IS ABSENT FROM THE CATALOGUE RECORD ENTIRELY.** `FIX_DOES_NOT_CURE_ITS_OWN_FALSIFIER` is not among the record's fields, so a human reading the export cannot see that a fix was measured and failed. cc2's advice: add the field first and separately; the status is the founder's call.

**SANDBOX CONFINEMENT IS TOOL-ASYMMETRIC.** fable reports Write and Edit blocked while Bash writes are permitted. That bears directly on the founder's rule that no model should be able to reach the real repository.

**THE ARCHIVE CARRIES A DECIDABLE-FALSE CLAIM ITS OWN MACHINERY CANNOT SEE.** fable computed `(4.89)^(1/0.709)` = **9.3805193079360563458** against a recorded "9.37", off by 0.0105193079 — reproduced here in sympy and mpmath agreeing to 20 digits, numpy to 15.

**AND THE HARNESS CAUGHT 3 OF cc2's OWN ERRORS, which cc2 names as the strongest evidence for the founder's position.** `execute-do-not-grep` caught a wrong instrument that reading would have missed; its own falsifier refuted its reading that `gamma_input` is constant; and **the additive standard's removal clause REFUSED a deletion it proposed**, because 2 blockquote shapes were recognised only by the code it wanted to remove. Its words: *"in each case reasoning proposed something plausible and a tool refused it, and in none would the tool have had anything to chew on without the reasoning that proposed the claim."*

## What was APPLIED from this round, composed rather than chosen

The founder's instruction was to apply the fixes derived from the study, under the composability, additive and simplest-sufficient standards. All 4 are in disjoint regions and were composed, not selected between.

1. **cc2's regex widening** in `reference_runner_v3.py`: `[ \t]?` becomes `[ \t]*` after the blockquote marker. **Verified STRICTLY ADDITIVE by measurement over a 48-shape product: 0 shapes lost, 6 gained**, Wilson [0.0000%, 7.4100%]. This is what LICENSES the next item under the removal clause — the survivor did not dominate until the widening landed.
2. **cc2's de-duplication** in `bugzilla_loop.py`: both live call sites now use `_gateable_hunks`. The 2 remaining mentions of the old regex are in comments quoting it, and **`_PY_FENCE` stays DEFINED** with cc2's dominance measurement recorded beside it, so the removal remains a human decision. Verified: the 2 extractors now agree 6 of 6 on the shapes that split them.
3. **fable's `collect_non_cure_ledger`** plus its report wiring, which discharges the founder's ruling that a measured non-cure be recorded and open to HIL inspection. Pure, `informative_only`, moves no verdict, and distinguishes measured non-cures from entries probed otherwise and entries never probed — so "0 non-cures" cannot be read as "all fixes cure" when the probe never looked.
4. **fable's carrier-abstain guards** in the fixture corpus. A falsifier that cannot locate the evidence it recomputes from raised `AssertionError`, which the decider reads as CONFIRMED, so *"I cannot read the evidence"* was indistinguishable from *"the defect is demonstrated"*. It is the same class as the absent-or-empty guard added earlier the same day, extended one level inward, and it **builds on that guard rather than replacing it** — fable's version retains all 5 of CC1's and adds 3 of its own.

**3 OF THE 4 ARRIVED WITH NO GUARD, and that was found by P-passing them.** Reverting the widening, the de-duplication, or the carrier guards each left the adjacent suite green at 253 passed. cc2's reported "250 targeted tests pass" was the existing suite continuing to pass, not new coverage; it delivered 6 falsifier scripts and no test file. `bench/tests/test_one_fence_extractor_2026-09-30.py` now covers all 3, and each reversion fails exactly 1 test.

**12 falsifier scripts and both design notes were rescued from the harvest**, which is gitignored — the same stranding defect measured this morning at 41 of 220 seat scripts reachable from no clone. cc2's note is 640 lines, fable's 400.

## Still open, and the founder's

The claim-level channel both seats recommend is designed and not built. The catalogue field for a measured non-cure is cc2's recommended first step and is separate from the ledger now applied. `n*` from complexity is **not estimable** on fable's evidence and its recommendation is not to build it. The tool-asymmetric sandbox confinement is reported and unaddressed.

## Seats and cost

2 seat(s): `cc2`, `fable`. **0 paid dispatches**, enforced by `PANEL_ONLY=cc2,fable`.

## The brief, as dispatched

<!-- verbatim-begin: the brief as dispatched -->

# Free panel, design review BEFORE build: intelligence first, tools second — and what that means for admissibility

**Dispatched 2026-09-30 by CC1 on the founder's instruction.** Standing policy since 2026-09-30: the panel reviews a DESIGN before it is built. Nothing asked for here is built. Your job is to say what should be built, what evidence would show it works, and — because you are running under the full CDSFL harness while you answer — **how the harness itself behaves under these conditions, and how it would behave under whatever you propose.** You are unusually well placed to answer that last part, and the founder has asked for it explicitly.

## Hard constraints, non-negotiable

- **You are in your own sandbox copy. Do NOT write to the real repository.** The founder's rule: *"none of the models... should ever be able to reach the real repo, let alone edit it!"*
- **Never touch `~/.config/cdsfl/scoring.env` or any answer-key store. Never print a secret value.**
- **`execute-do-not-grep`.** A claim asserting on the SOURCE TEXT of a module asserts only that the module describes itself consistently. Where a producer and a consumer both exist as live code, CALL them and compare outputs. This session has been bitten by grep-shaped predicates 4 times in one day, 3 of them in CC1's own instruments.
- **`measured-rate-travels-with-its-script`.** Every rate, proportion or count must come from code you ran, shown with its command and output. Any proportion needs a confidence interval.
- **Cross-verify every computational claim with at least 2 independent tools.** A Wolfram call that errored verified nothing.
- **`feedback_no_model_voting`.** Findings are confirmed programmatically or by the human, never by model agreement. Report executed evidence, not consensus.
- **`feedback_fixes_hil_only`.** Every fix is SUGGESTED to the human.
- **No compelled convergence.** Disagreement between seats is information and is preserved. Say where you disagree with the other seat and why, with evidence.
- **`simplicity-default` and the additive standard, both directions.** The simplest sufficient design wins. An addition nothing reaches is not additive; a removal needs a committed measurement showing the replacement dominates on a named property.

## Declared figures. RE-EXECUTED when this brief is validated, not taken from CC1's typing.

<!-- figure: corpus_claims_live_in_prose | scripts/intelligence_first_brief_figures_2026-09-30.py | 29 of 29 -->
<!-- figure: stripping_the_fences_flips_the_triage | scripts/intelligence_first_brief_figures_2026-09-30.py | 5 of 5 -->
<!-- figure: live_path_modules_reaching_the_corpus | scripts/intelligence_first_brief_figures_2026-09-30.py | 0 of 5 -->
<!-- figure: claims_in_prose_interval | scripts/intelligence_first_brief_figures_2026-09-30.py | statsmodels [88.3030%, 100.0000%] -->
<!-- figure: the_false_claim_really_is_false | scripts/intelligence_first_brief_figures_2026-09-30.py | claimed_mean_is_false = 4.0 -->

## The founder's principle, verbatim, and it is 5 months old

From `experimental_notes/CDSFL_Stage_Three_Closure_Explained_2026-04-17.md:28`, dated 2026-04-17:

> *"The language models propose claims, the mechanical tools verify them, and the human in the loop makes the final call on anything that remains uncertain."*

And from his message of 2026-09-30, restating it and drawing the boundary he cares about:

> *"I am not simply interested in turning current AI systems into simple 'number crunchers', that is I am not interested in potentially having spent months upon months building a system that ultimately does what any human can do, that looks directly at a problem, then simply uses tools to try to solve it... Rather my goal was to leverage the clear reasoning capacities that current (and future) LLM (and other AI) systems possess innately *and then* use tools/falsifiers to prove/disprove them. Otherwise you just end up with a vastly complicated system that may hold no advantage over current conventional methodologies."*

> *"Neither can exist in isolation from the other. Neither can be considered valid without the other. Neither can be considered preferable to the other. They are simply two sides to the same coin."*

**THE PROJECT HAS ALREADY REJECTED THE TOOLS-ONLY FORM ONCE**, which is the strongest internal support for his position. `docs/EXTENDED_RATIONALE.md:119`, March 2026: a proposed threshold rule *"would have silently discarded every finding that could not be computationally verified — design findings, prose findings, everything qualitative. One reviewing model caught this. The fix was a one-character change. The project manager did not see it."*

**EXTERNAL, AND UNVERIFIED BY CC1.** He cites a Nature news article (`nature.com/articles/d41586-026-03039-6`) reporting that a model asked to find CRISPR-like sequences in giant viruses performed WORSE when instructed to take a tools-first or tools-only approach. **CC1 has not read it and makes no claim about it.** Treat it as the founder's input, note that one external study plus one internal near-miss does not establish a mechanism, and say whether anything in THIS project's archive could test the same hypothesis.

## Measured facts, established 2026-09-30 by execution. Re-verify anything you rely on.

1. **THE TRIAGE TESTS FOR FENCED PYTHON, NOT FOR COMPUTATIONAL REDUCIBILITY.** Called directly: a markdown document carrying a computable FALSE claim ("the mean of 2, 4 and 6 is 4.5", where sympy, numpy and mpmath all give 4.0) returns **INADMISSIBLE** — the identical verdict to a document about the mood in a room. `_gateable_source` reports "target carries no code; syntax gates not applicable". So the instrument cannot distinguish *no computable elements* from *computable elements not written as Python*.
2. **THE CORPUS NEVER EXPOSED THIS, because its claims are not where its admissibility comes from.** All 5 fixture documents carry fenced Python and so pass the triage. But **29 of 29 of their claims live in PROSE**, 0 inside a code fence, Wilson [88.3030%, 100.0000%]. Strip the fences and **5 of 5 documents flip to INADMISSIBLE while 5 of 5 keep 100% of their claims in the text.** The admissibility signal and the decidable content are DISJOINT.
3. **The affirmative channel exists and the live path does not reach it.** The corpus's 5 falsifiers discriminate bidirectionally through the runner's own `reverify_falsifier`, and now also ABSTAIN (ERROR) on an absent or empty document after a repair landed today. `reference_runner_v3.py`, `routing.py`, `falsifier_verify.py`, `immune_agents.py` and `runner_core.py` reach it **0 of 5**.
4. **On a prose target, `ADMISSIBLE` is unreachable.** `_prose_one_sided` at `reference_runner_v3.py:11656` rewrites every would-be ADMISSIBLE into REJECTED (any new defect) or NO_SCORE. The founder's response to that: *"by either of these options the result would produce nothing useful?"*
5. **The abstain semantics are already right.** `docs/GLOSSARY.md:237`: *"NO_SCORE is not a third grade of admissibility: it is the statement that S_k has no opinion."* A correct prose fix is unscoreable, not defective. So what is wrong is the DETECTION, not the response.
6. **A19's own title already names the unit error:** *"S_k classifies the TARGET, not the ELEMENT, so a computable fragment inside prose is never scored."*

## Questions. Answer each separately. Where execution cannot settle one, say so and name what would.

**Q1 — THE PRIMARY QUESTION. What does "intelligence first, tools second" require of the architecture, and what is the simplest sufficient way to build it?** Fact 1 says the current triage gates reasoning on a tool's readability, which is the opposite order. CC1's reading is that his principle implies 3 stages — REASON (the model produces candidate claims, including ones the problem never states), REDUCE (decide which are decidable and write a falsifier), VERIFY (run it) — and that the machinery has only the last 2, with the triage sitting *before* stage 1 and gating on syntax. **Attack that reading before adopting it.** Generate 2 to 4 distinct candidate architectures independently, falsify each, then recommend one.

**Q2 — Is the unit of admissibility wrong, and what is the correct one?** A current-affairs article has no decidable STEM claims. The founder's own message is prose-heavy and carries several. His words: *"It can't exactly be judged as 'inadmissible' simply because it does not specify exactly what the question is, or what the answer might be."* Should admissibility attach to a CLAIM rather than a DOCUMENT, and if so what carries the claim-level verdict, what does the file-level verdict become, and does anything downstream break?

**Q3 — Where is the honest boundary of inadmissibility?** He names the cases he would accept as genuinely non-computable: a current-affairs article, a short story, poetry, "anything generally of a non-STEM nature". Can that boundary be drawn mechanically, or only by a model's judgement? If by judgement, can a small classifier (Haiku-class) do it reliably, and what labelled set would establish that? **CC1 has no evidence either way and declines to guess.**

**Q4 — Is the Wolfram-connector parallel deep or shallow?** In the earlier round a seat wrote: *"what Wolfram's connector does — NL in, computation out — is what a panel model does when it writes a falsifier. The LLM is the translator; the open-source set is the engine."* CC1's objection: a connector translates a STATED question into a computation, whereas the founder is describing the model forming the claim that is worth computing — so translation is a proper subset of reasoning, and the parallel describes the narrower thing. Is that objection right, and does the distinction change what should be built?

**Q5 — HOW DOES THE HARNESS ACTUALLY BEHAVE UNDER THESE CONDITIONS, and how would it behave under your proposal?** You are running under the full CDSFL harness while answering, which no static analysis can substitute for. Drive it: give it a prose-heavy problem with unstated computable elements — this brief is one, and the founder's own message is another — and report what the harness does, where it abstains, where it decides something it should not, and what your proposal would change. Report the harness's behaviour on ITSELF where you can.

**Q6 — Propose fixes for the 3 outstanding items, since they interact with Q1.** (a) **The 3 wirings** for prose answerability: corpus on the live path, a fix-efficacy check for prose, and the document's own claim suite as the prose test command. (b) **A measured non-cure must be recorded in the registry and open to HIL inspection** — his ruling of 2026-09-30, which is neither plain REJECT nor plain ESCALATE, and CC1 has not yet built it. (c) **`n*` and the gamma collision**: 2 incompatible quantities are both named `gamma`, no live module emits the coefficient, and the pair (4.89, 0.709) reproduces from no archived fit. The founder asks whether the round count can instead be computed from TARGET COMPLEXITY before a run — note that `target_complexity` is already recorded in every report, carrying `gamma_input`, `beta`, `r_squared`, `n_windows` and `target_chars`, and that `EXTENDED_RATIONALE.md:65` already hypothesises the threshold *"may correlate with constraint count multiplied by constraint interaction density"*, never measured.

## Delivery. A design left in prose is destroyed at teardown and does not count.

**Write your answer INTO the sandbox repository tree at its real path, not into scratch space.** Rounds 5 and 6 of a prior arc returned 0 source files because both seats wrote into scratch that `panel_sandbox.teardown` deleted.

- **The design** goes to `experimental_notes/<seat>_intelligence_first_2026-09-30.md`.
- **Every falsifier you run** goes to `scripts/<descriptive_name>_2026-09-30.py`, runnable from the repository root, so each figure travels with the script that produced it.
- **Any proposed code change** is written as a fix INTO the module it belongs to, at its real path, so a reviewer can diff it. Do not paste a patch into your reply and leave the tree untouched.

A design that exists only in your reply is not delivered. Your reply should point at the files, not replace them.

## When to stop

**Terminate on diminishing returns, this project's own criterion.** Stop when 2 consecutive falsification passes produce no new finding above the real-world-consequence threshold, or when every HARD assumption in your design has been tested and survives. Budget up to 5 passes. `p-pass-anti-nitpick` forbids padding: a review that stops early with its HARD assumptions tested is finished, not lazy. If a question cannot reach that state, name the HARD assumption still untested and what would test it.

## Output format

For each question: your position, the executed evidence, and your strongest attempt to refute your own answer. State explicitly what would overturn it. Name any disagreement with the other seat. Where a question is not computationally reducible, say which part is not and why, rather than producing a qualitative opinion dressed as a finding.


<!-- verbatim-end -->

## Seat: cc2

Route `claude_cli`, 136 recorded tool call(s).

<!-- verbatim-begin: cc2 (panel intelligence_first_2026-09-30) -->

Both changes confirmed on disk. The sandbox is not a git repo, so there is no diff to show — files are at their real paths as required.

## Delivered

- **`experimental_notes/claude_intelligence_first_2026-09-30.md`** — the design, Q1–Q6
- **7 falsifier scripts** in `scripts/`, each runnable from the repo root
- **2 code changes** in `bench/reference_runner_v3.py` and `bench/bugzilla_loop.py`

All 5 declared brief figures re-executed and reproduce exactly.

## My verdict, briefly

**I disagree with the brief's central framing, and the disagreement is executed.** Fact 1 bundles three propositions: the observation is true, the *label* is false, and the remedy it motivates is inert.

There is no verdict named `INADMISSIBLE` — the live vocabulary is `{ADMISSIBLE, ESCALATE, NO_SCORE, REJECTED}`. The word is the producer script's own (`'ADMISSIBLE' if red else 'INADMISSIBLE'`, a truthiness test on an extractor's return). Both documents actually return `NO_SCORE`, which `GLOSSARY.md:237` defines as "S_k has no opinion" — the correct answer. And `_gateable_source` is not a triage before reasoning; it is an extractor *inside* `compute_sk`, which scores a **proposed fix**. It was never asked whether a document is worth reviewing.

Load-bearing: **`ADMISSIBLE` is unreachable on any prose target** — my sweep, plus the project's own producer (20 evaluations, 0 admitted). Detector repair buys zero reachable states.

The real gap is not that reasoning is gated — this brief has 0 fenced listings and I reasoned on it unimpeded. It is that **nothing in the harness takes a claim as its unit**. That is one level above A19's title: S_k classifies neither target nor element — it classifies a *fix*. I recommend a claim ledger as an additive channel, S_k untouched.

## Three things worth your attention

**Q4 is settled on the brief's own specimen.** "The standard deviation is 2.0" — sympy, numpy, mpmath and Wolfram all agree it is **2.0 exactly** under ddof=1, and 1.633 under ddof=0. The brief reports it flatly false by quoting numpy's default. The mean half is false; the SD half is convention-dependent. A connector given the stated question returns the right number and never asks which convention the author meant. Translation is a proper subset of reasoning — demonstrated against the brief arguing for it.

**Q6(c): n\* is not recoverable.** Three gamma conventions, not two (0.8776 vs 0.2143 on identical data). (4.89, 0.709) is a chimera — α from one record, γ from another, 0 of 379 archived fits reproduce the pair. But your alternative is live: γ_input gives **9 distinct values** across 9 targets, r² > 0.99, computable pre-run. Its correlation with rounds-needed has never been measured, so it must stay `informative_only`.

**Q6(b) is worse than a missing status.** `FIX_DOES_NOT_CURE_ITS_OWN_FALSIFIER` is not among the catalogue record fields at all. A HIL reviewer reading the export cannot see that a fix was measured and failed. Add the field first, separately; the status is your call.

## What the harness did to me

I made three errors. All three were caught by your own rules, no model vote involved: `execute-do-not-grep` caught a wrong instrument that reading would have missed; the **additive standard's removal clause refused my proposed deletion** (2 blockquote shapes were recognised only by the code I wanted to remove); and my own falsifier refuted my "γ_input is constant" reading. That is the strongest evidence in the note for your position — in each case reasoning proposed something plausible and a tool refused it, and in none would the tool have had anything to chew on without the reasoning that proposed the claim.

Found by execution while answering Q5: **two live fenced-Python extractors disagreed** on 3 of 13 realistic shapes, plus a false FAIL accusing a valid document. Fixed by widening one and rewiring both call sites — **nothing removed**, dominance recorded so a human can make that call later. 250 targeted tests pass; extraction byte-identical across all 5 corpus documents and 1200 repo markdown files. A third extractor, `_MD_PY_FENCE`, has **zero callers** — reported to you, not removed.

Three HARD assumptions remain untested; the strongest attack on my own §1 is that a claim ledger may duplicate the finding registry, and I did not run that check. Both are named in §8 with the test that would settle them. I have not seen the other seat's return and name no disagreement with it.

<!-- verbatim-end -->

## Seat: fable

Route `claude_cli`, 88 recorded tool call(s).

<!-- verbatim-begin: fable (panel intelligence_first_2026-09-30) -->

All deliverables are in the sandbox tree. Final report.

## Delivered files

**Design:** `experimental_notes/fable_intelligence_first_2026-09-30.md`
**Falsifiers** (all runnable from repo root, all re-executed clean):
- `scripts/fable_sk_verdict_is_syntax_bound_2026-09-30.py`
- `scripts/fable_falsifier_path_is_substrate_independent_2026-09-30.py`
- `scripts/fable_reason_reduce_verify_probe_2026-09-30.py`
- `scripts/fable_nstar_from_complexity_archive_sweep_2026-09-30.py`
- `scripts/fable_prose_fix_efficacy_probe_2026-09-30.py`

**Suggested diffs** (in the modules, per delivery rules; all fixes HIL-only): carrier-abstain guards in `bench/tests/fixtures/stem/stem_fixtures.py` (226/226 acceptance tests pass after); `collect_non_cure_ledger` + report wiring in `bench/reference_runner_v3.py` with `bench/tests/test_non_cure_ledger_2026-09-30.py` (3/3 new, 78/78 adjacent pass).

## Verdicts, compressed

**Q1** — Recommend the **claim-unit pipeline bound to existing machinery** (candidate B of 4; A, C, D falsified in the note). CC1's reading was attacked and corrected: the machinery does NOT lack REASON/REDUCE — it has all three stages *for findings*; it lacks them *as the unit of admissibility*. Nothing new needs inventing. Executed support: the corpus falsifiers decide fence-stripped documents through the runner's own decider wherever evidence is prose-carried, and the live fix-efficacy probe returns FIX_CURES on prose. One HARD assumption remains untested and is named: that REASON surfaces material *unstated* claims at a useful rate — needs the unstated-claim corpus extension specified in the note.

**Q2** — Yes, the unit is the claim. File-level verdict becomes a three-state aggregate (claim-addressable / routed-only / no-decidable-claims); NO_SCORE stays S_k's abstention. Nothing downstream breaks by execution (81 targeted tests). Whether claim verdicts may enter σ/R_k is flagged as the founder's call — recommended not in v1.

**Q3** — The boundary should be an **outcome** (zero decidable claims after looking), not a pre-gate. A classifier is cost-optimization only; the labelled set has *executable* ground truth (protocol in note). I decline to guess reliability, as CC1 did.

**Q4** — CC1's objection is right, with an executed counterexample (claim MRS-C3 is translatable by no connector). The parallel is exact for REDUCE only.

**Q5** — Driven, including on itself: the harness never *decided wrongly* today — every failure is a correct abstention on the wrong trigger (blindness, not corruption; this corrects the brief's "INADMISSIBLE" vocabulary — the real verdict is NO_SCORE, 4/4 calls). The harness's own archive carries a decidable-false claim its triage cannot see: `(4.89)^(1/0.709)` = **9.380519307936057** (mpmath, sympy, Wolfram Language via local Wolfram Engine agreeing) vs the recorded "9.37". Also noted for the founder: sandbox confinement is tool-asymmetric (Write/Edit blocked, Bash writes permitted).

**Q6** — (a) Three wirings specified; the corpus-as-arm4-target also gives the internal test of the Nature-cited hypothesis (reason-first vs tools-first over 5 known planted claims). (b) Built as a suggested diff — the ledger records every measured non-cure for HIL, moves no verdict, and refuses the "0 = all cured" conflation. (c) **Not estimable**: 9 archived runs cover only 2 distinct targets and round counts are configured caps; the constraint-count×density hypothesis is untestable (neither factor recorded). Prerequisites ordered in the note; do not build n*(complexity) now.

## The review's own material finding

Pass 4's full probe run surfaced that **3 of 5 corpus falsifiers raised AssertionError (= CONFIRMED) on evidence-carrier failures** — the 2026-09-30 empty-doc defect family, one case wider — which had corrupted the fix-efficacy channel (2/5 FIX_CURES) *and* one of my own first-pass figures. Repaired in the sandbox, re-measured: 226/226 tests, discrimination intact 5/5, probe now **5/5 FIX_CURES**. A review whose instrument-check catches its own first-pass figure is the falsification loop doing its job.

**Convergence declared** per §10 after 5 passes: pass 5 produced no new material finding; every HARD assumption tested except the one named above, with its test specified. Disagreements with CC1 (verdict vocabulary; stage reading) and the earlier seat (Wolfram parallel) are preserved in the note with the evidence that decides each.

<!-- verbatim-end -->

## Where the raw record lives

`bench/logs/intelligence_first_2026-09-30/` holds the brief, every seat reply, the tool logs and `seat_proposals.diff`. That directory is excluded by `.gitignore:41`, so a byte-identical copy is committed under `experimental_notes/evidence/`, verified by sha256 and checked on every suite run by `bench/tests/test_panel_records_are_preserved_2026-09-11.py`.


Written under CDSFL note standard v1.7 (26 August 2026).
