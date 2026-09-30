# CLOSING REPORT, 2026-09-30. TWO PANEL REVIEWS, AND THE DECISIONS THAT NEED THE FOUNDER

> **Plain-English companion.** The spoken version is `~/Desktop/CDSFL_tts/Closing_Report_Both_Panels_2026-09-30.txt`.
> The engineer-facing records, with every seat reply verbatim, are
> `Panel_FULL_RECORD_Falsifier_Root_Cause_2026-09-30.md` (morning) and
> `Panel_FULL_RECORD_A19_Calculator_Design_2026-09-30.md` (afternoon).

Constraint Engineering project. Written 2026-09-30, 14:55 BST. Both reviews used FREE seats only, 0 paid dispatches, 0 spend.


## The one thing that should be read first

A sandbox containment breach was found, and it was found by a review seat inspecting its own failure rather than by any guard. The fable seat's regression run produced error traces pointing at the REAL repository. The cause: the staging copy handed to each seat carried 988 compiled Python cache files whose internal records still name the real repository, so a cached test module asking "where am I" resolves to a path outside its sandbox and can import real repository modules into a panel measurement. It demonstrated this by inspecting the raw bytes of the cache files, purging them, and re-running.

This bears directly on the founder's hard rule that no model should ever be able to reach the real repository. The immediate remedy is a single line: staging and harvesting must exclude compiled cache directories. The staging code is not in this repository, so the seat offered it as a suggestion with evidence rather than as a patch. It is the highest priority item in this document and it is not a design decision, it is a repair.


## The headline, and both reviews reached it independently

The switch the founder has been asked to rule on for 19 days is the wrong instrument for what he wants.

His requirement is a calculator: a computationally reducible question in, a definitive answer out. The switch under review grades a proposed FIX using static tools, lint and a security scanner, applied to code samples inside a document. The cc2 seat put the distinction plainly: it scores a fix, while the calculator needs a verdict on a claim. The fable seat put it as an image: the flag is a smoke detector being asked to certify the building.

Measured, by execution: with the switch on, no fix on a prose document can ever be recorded as admissible. It can be rejected, or it can return no score. The fable seat drove 10 fixes through it and got 0 admissible, with a 95 per cent confidence interval from 0 to 27.75 per cent. So the founder's own observation, that under either option the result produces nothing useful, is confirmed rather than contradicted.

The good news is larger than the bad. A committed corpus of claim checkers CAN give a definitive affirmative answer, it already exists in this repository, it is already validated in both directions, and it is connected to nothing. Each checker is a small runnable test written for 1 specific claim, run by the project's own decider, reverify_falsifier. It is a corpus of 5 ground truth science and engineering documents carrying 29 tagged claims and a runnable checker for each. All 5 checkers correctly confirm a planted false claim and correctly withdraw once it is corrected. The 5 modules that a real review actually passes through mention that corpus 0 times. What is missing is wiring, not new science. The fable seat names exactly 3 connections and says explicitly that no new science is required.


## Decisions from the first review, held this morning

Decision 1. Which cure to build first. The cc2 seat says connect the existing corpus to the live path, having measured that the routing ladder resolves 0 of 5 findings with the pattern removed and 5 of 5 with it supplied, Fisher exact probability 0.007936508. Its formulation: routing is a multiplier on supply, and here a multiplier on zero. The fable seat says make routing unconditional instead, since it currently defaults to off and is forced on only for prose. Recommendation: they sequence rather than conflict, and both seats say so. Connect the corpus first, then make routing unconditional, then measure. Nothing is lost by that order and the reverse order measures a multiplier against nothing.

Decision 2. The round limit. Both seats recommend 10, and both now say it must stand as an empirical budget cap rather than as a derived optimum, for reasons in decision 9 below. Recommendation: adopt 10 as a cap that declares unfinished business when it is hit, and make the binding stop condition novelty falling below threshold for 2 consecutive rounds. The first arm ended at the cap with novelty RISING, at 9 new findings in its final round, which is unfinished work rather than convergence.

Decision 3. The faked regression gate on the prose arm. Both seats fixed this independently at the real path in their own sandboxes. It is not in the working tree. Recommendation: apply it, and prefer the fable seat's version, which makes the intent explicit where the setting is declared and also corrects a committed test that had encoded the defect it was supposed to catch. The cc2 seat chose a narrower one line change specifically to avoid editing that test, which is a reason to fix the test rather than a reason to avoid it.

Decision 4. Whether an untoolable finding should cost something. The cc2 seat measured that 28 of 28 findings marked untoolable were in fact toolable, so the label is currently a free exit. Recommendation: make it a routing input rather than a terminal state, which is also the fable seat's second proposal, so the 2 reviews agree here.

Decision 5. Whether routing should be on by default. See decision 1; this is the second half of that sequence.


## Decisions from the second review, held this afternoon

Decision 6. Turn the prose scoring switch on, or leave it off. The argument recorded against it has expired: the entry states as its decisive fact that a known dangerous fix is still admitted at a perfect score, and against current code that same fix returns no score at 0. The companion claim that 1 new security finding is not enough to reject is also now false, because a repair added 11 days after that measurement rejects on any new defect at all. Recommendation: turn it on. It is a working harm guard and the objection to it no longer holds. But treat that as a small separate benefit, not as progress toward the calculator, because it cannot affirm anything.

Decision 7. The 3 connections that would make prose answerable. Supply, meaning the corpus reaching the live path. A fix efficacy check for prose. And a replacement for the regression gate on prose, where the document's own claim checkers become the test suite, which the fable seat calls the honest prose test command. Recommendation: build all 3, in that order. The fable seat deliberately did not half build them, on the grounds that an addition must arrive with a caller and a test, which is the project's own standard.

Decision 8. Should a fix measured NOT to work be rejected, or escalated to a human. The fable seat built rejection and gives the cost asymmetry that decides it: a wrong rejection comes back with feedback, while a wrong admission has already lowered the recorded risk 73 times. It states plainly that escalation is the softer alternative if the founder wants a person to see every non curing fix, and that this is a ruling rather than a computation. Recommendation: rejection. The measured asymmetry favours it, and escalating every non cure risks the human review flooding that this project has already recorded as a hazard.

Decision 9. How many rounds a run should be allowed, and this one is load bearing. Both seats agree the coefficient is a cumulative one, settled by calling the fitting code rather than reading it. Both also agree the pair of numbers the project has been using, 4.89 and 0.709, appears in NO archived fit: the cc2 seat swept 421 committed curves and found 0 matches, the fable seat swept 379 and calls it mixed provenance. And both found that two incompatible quantities are called gamma in this codebase, one being 1 minus the other, giving 0.8776 against 0.2143 on the same data in one measurement and 0.2654 against 0.2583 in another. The cc2 seat adds that no live module even emits the coefficient, so the software cannot evaluate the formula at all.

The seats then disagree about the corrected value, by a factor of about 33, each with 3 or 4 independent tools agreeing to every digit. The cc2 seat gives 2.1879, arguing the previous correction wrongly took a continuous derivative of a series indexed in whole rounds. The fable seat gives 71.6994, arguing the convention consistent form is different again, and that the previous correction is refuted by the fitting data itself.

Recommendation: rule on neither number. Both rest on a coefficient pair that reproduces from nothing, and on a symbol that means two different things in two files. The honest sequence is to fix the naming collision first, then re fit from a curve with stated provenance, and only then choose the formula. Adopting either value now would pin a decision to an unsourced input, which is the defect this project has spent the day finding in other forms.

Decision 10. The remedy for copies being counted as originals. This class was found in 3 separate mechanisms in one morning, and the review added a fourth, the compiled cache breach described at the top. The cc2 seat recommends identifying duplicates by content hash, having measured that the conflation inflated its own headline number by 53.7313 per cent, from 309 down to 201, and that a path based rule would need 259 separate edits. The fable seat recommends separating the storage namespaces entirely, arguing that a shared rule cannot bind either the version control ignore file or the internal records inside compiled caches, and that a guard test shares the same blind spots. Recommendation: the fable seat's separation. The cache breach is direct evidence that the blind spot it names is real and already cost a measurement.

Decision 11. The advisory number shown to a human reviewer. The founder ruled that false information must not be presented and that hiding it is not acceptable either, and asked whether it could be made accurate and meaningful. The answer is yes, and both seats reached the same 2 part shape: accuracy comes from fixing the inputs, and meaning comes from stating what the number is able to say. The cc2 seat measured the trap in doing only the first half: with proper baselines the number reads a perfect 1.0 on all 5 correct fixes AND 1.0 on both harmful fixes it scores, so it separates 0 of 5, while the decision printed beside it separates 3 of 5. A number correctly derived from true inputs can still say nothing, so correct derivation and usefulness are 2 different properties. Recommendation: do both halves. Rename it so it says what it measured, a static harm sweep, carry alongside it which gates were consulted and which were absent and whether any affirmative evidence exists, and it becomes fully meaningful once decision 7 gives it an evidence bearing input. Nothing is suppressed.

Decision 12. Two of the 5 committed claim checkers have the same defect as the faked gate, one level down. The cc2 seat proposes a third test beside the existing two: a checker run against a document whose contents have been deleted must not report that the claim is withdrawn. Executed across the 5 checkers, the existing 2 tests pass 5 of 5 and 5 of 5, and the new one passes only 3 of 5. Two of the checkers this project relies on as proof that prose is decidable cannot tell a real claim from an absent document. Recommendation: adopt the third test and repair the 2 checkers before the corpus is wired to anything, since wiring a checker that cannot see its target would carry the defect into production.


## What was built today without needing a ruling

Two controls that both seats of the first review reached independently, which change no verdict and therefore needed no decision.

The first requires every scoring gate to produce different output for a known good and a known bad input, because a gate whose output does not vary with its input decides nothing. It calls each gate and compares what comes back rather than reading the source. It also holds the other half, that declining to answer is correct behaviour and must not be penalised, because without that leg the test would push toward gates that always answer, which is how a gate ends up answering with a constant. It carries one measured hazard: breaking the checking probe must never score better than honestly failing it, because the project has recorded that dropping the broken probe case created a reward for destroying the instrument, worth 0.4 on the score.

The second requires every declared reusable pattern to have both an executing test and a caller on the live path. This is an extension rather than a duplicate: an existing guard checks whether a configuration setting is named in any test, and the corpus IS named in 2 tests while being reachable from nothing that would use it, so a name based check scores that as reached.

Both were verified by deliberately breaking the property and confirming the tests go red, which is the only evidence that a guard guards. Making one gate return a constant produced 1 failure; making another produced 2; adding a declared pattern with no caller and no test produced 3; pointing the live path list at a missing file produced 1; renaming the marker so nothing is enumerated produced 2. Restored, all pass.


## Three errors of the assistant's own, corrected rather than omitted

A number quoted in the second review's briefing document, 73 of 73, was a hardcoded value typed into a script rather than a live measurement. The cc2 seat caught it and gave 201 as the deduplicated count. Three figures now exist, 73, 201 and 309, a re measurement returned 0 records because the accessor does not match the archive's shape, and rather than substituting one of the 3 the figure has been WITHDRAWN and the dispute recorded as open.

A claim that the contaminated gate was decision inert was correct but incomplete, which the fable seat names as its disagreement. No verdict and no risk figure moves, which both seats re executed. But the contaminated value also reaches the archived record and the evidence bundle a human reads, and costs roughly 1.7 gigabytes of repository copying plus 55 unrelated tests of waiting per fix per round.

A full test suite run was started and then invalidated by the assistant editing, mid run, documents the suite reads. It was stopped at 48 per cent. The founder has directed that the clean run happen after these issues are resolved, and it has not yet been taken.


## The state of the repository

The canonical branch received exactly 1 file today, a correction to a wrongly attributed rule, committed with a deliberate single use bypass the founder authorised for that file alone. Everything else lives on a simulation branch which is pushed, so simulated results survive independently of this machine. Both branches are level with their remote and the working tree is clean. The only measured statement about the current state is that the commit gate's 501 fast checks pass.

The commit gate refused work 6 times today and was obeyed every time. Its reasons were a stale ledger, an unmirrored panel record, a missing full record note, a script that ran a measurement when asked for help, and twice a note carrying a vague phrase. Each refusal named a real defect, and the one bypass used was the one the founder authorised.
