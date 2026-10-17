# The task list: what was done in 48 hours, what remains, what is owed, and the rulings still needed. 2026-10-17, 04:00 BST.


## Where The List Stands


141 entries. 38 open, 95 done, 1 blocked, 7 withdrawn. The marker checker reports 0 problems and the repository's 530 tests pass.

Of the 38 open items, 31 already carry his ruling and need no decision. 3 need a decision from him. 4 are questions of his that need an answer from the assistant rather than a ruling. 1 more, the orchestrator experiment, needs a ruling on placement only.

85 commits landed in the 48 hours to 04:00 on the 17th.


## He Was Right About The Routing Ladder, And The Cause Was A Search Scope


He said the routing ladder work was a rediscovery. It was, twice over.

The first entry claimed his ruling that a ladder must work in both directions had not been carried out. It had. The simulated launcher declares its seat-model option with the default set to ladder, and its own help text records that this has been the default since a commit of the 7th of October. The memory note on the subject is headed, superseded on its headline claim, and says in terms, do not raise either with the founder again. That entry is now withdrawn.

The second claimed that one of the project's 2 free models does not appear on the ladder at all. It does. The default ladder maps the Fable seat to Fable, 1 of the 3 distinct backing models across the 6 seats. Withdrawn.

Both were withdrawn rather than deleted, with the evidence recorded in place, because the audit's own central finding is that entries get lost rather than refuted.

Then a second error of the same kind. The assistant searched for his Snakes and Ladders framing, found 0 files, and reported the framing as new to the record. That search covered only the experimental notes folder and the memory files. It did not cover the source tree, the documentation, or the chat transcripts. He then supplied the exact quote, dated the 15th of October at 03:40:13, and the transcript confirms it. It also confirms that the assistant answered it in full 103 seconds later, conceding the point in these words: your snakes and ladders description is not a change request, it is what the code already does, side steps are already permitted, routing is already blind to version and keyed on what is available.

That 2 day old answer has now been verified by execution rather than trusted, because a prior claim of the assistant's is still only a claim. The ranking routine was called directly. It ranks strongest first over what is actually available, returning 3 names in strength order when only 3 are available. It drops the model that just failed, in 3 of 3 cases tried. With the paid seat excluded it still offers that seat's stand in, so it is blind to version exactly as he specified. And excluding 1 model from a group of 3 equal peers still leaves 2, so a side step genuinely exists. The movement mechanism is built, settled, and must not be raised again.


## What The Same Execution Showed Is Genuinely Open


The ranking order is a hard coded tuple of 6 vendor names. That is verbatim what he objected to on the 5th of October: the routing ladder should be a measured statistic, not simply a list of named vendors based on what you, or I may have read about them on the internet. So the order is open and the movement is done. A single entry now carries that distinction, and a second entry sharing the same root is his ruling that there should be no distinction between models other than a ranking number.

ALSO RECOVERED FROM THE RECORD, so it is not rediscovered again. The number of fallback steps a round may spend, not the scattering of seats across models, is what mixes the ladder: 2 steps gives none of 6 seats mixed, 3 gives 3 of 6, and 4 gives 6 of 6 mixed and all 6 correctly directed. The shakedown ran with that budget exhausted, which is past 4. And Sonnet is ruled out on his ruling of the 7th of September, which the assistant then contradicted on the 15th of October and conceded.


## What Remains Of The Ladder Question Is A Different Question


His reframing of the 9th of October, recorded in 9 annotations on the division and relegation panel, is about promotion and relegation rather than movement, and the task list carried none of its substance until tonight. The panel of the 8th of October settled 2 things: that promotion gates should be both deterministic and exchangeable, at a measured price of 0 extra attempts, and that there was only ever 1 division count formula rather than the 2 that appeared to disagree.

It also established something stronger. Relegation on sustained degradation is not identifiable at all without a pool of items whose difficulty is fixed externally and re run every window. In the standard model only the difference between a model's capability and an item's difficulty enters, so a capability drop across the whole roster and a difficulty rise across the whole task stream produce identical distributions on every outcome. That was verified 3 ways: symbolic algebra returning exactly 0, a constraint solver returning unsatisfiable on any separating value, and arbitrary precision arithmetic returning 0 difference across 27 test points. Comparing a model to its peers detects a roster wide decline only 0.0190 of the time against its own false alarm rate of 0.0475, and the difficulty model demotes a perfectly stable model 1.0000 of the time when its estimates are stale.

And he rejected the panel's own figure, which was never recorded until now. Roughly 300 attempts per model per assessment window for a 4 division ladder. His words: clearly vastly much too much, and, are you even checking if these numbers make any practical sense before writing them? He proposed 2 or 3 attempts instead.

His own design resolves it and is not built. A season is 1 round. Promotion and relegation are computed from the evidence of the first experimental round, and then rankings stay fixed for the remainder of that experiment. That bounds the evidence requirement to 1 round rather than 300 attempts, and it is the single change that makes the whole mechanism affordable. For the cold start he proposes a knockout draw in which no capability is assumed: every model gets 1 hard randomly generated mathematics problem, ranked by who solves it fastest using tools and writing proofs or falsifiers, and most cost effectively, with weaker performers then given a less demanding problem and the step repeated. Under the no benching rule a loser keeps its position rather than being knocked out.


## The Ticket Store Is Now The First Item On The List, On His Instruction


He asked whether the project's existing Bugzilla machinery could be repurposed so that settled issues cannot be resurrected, and checked mechanically so that its use is compelled.

The machinery exists. A module of 898 lines implements the Bugzilla paradigm from the Experiment 36 design analysis of the 7th of April, with a state machine running from open to confirmed to closed, where closed is documented as challenge resistant and terminal. Duplicates merge. A closed item can only be reopened by an explicit reopen with human escalation, which means only by him. And its own documentation says closed items appear in summaries carrying a do not re describe instruction. That is precisely the set in concrete facility he described, and it already exists for experiment findings. What it does not cover is project level instructions and rulings, whose state the assistant currently infers from prose.

The evidence that inference cannot work is this session. 6 separate attempts to determine from text whether something was settled or novel all failed in 1 night. A measure of how many of his words appear in the list, which passed its own control and answered the wrong question. A repeatability measure saturated at the same figure across every threshold from 10 per cent to 99 per cent. A claim about the note checker that rested on calling a function with a string when it takes a file path, so it silently returned nothing for every input. A rediscovery check that matched every entry against the task list itself. A novelty search that returned 0 files because it covered neither the source tree nor the transcripts. And a routine called with the wrong positional argument. Every one produced a clean looking answer that was an artefact of scope or signature rather than a measurement. A recorded state field has neither a scope nor a signature.

The harvest must cover chat as well as his written replies, and there is a measurement that settles why. Of his 579 recorded annotations, 0 mention the orchestrator question he has now asked 3 times. It exists only in chat. So a harvester reading only his replies is blind to it by construction. The transcripts are readable, because his exact message of the 15th and the assistant's reply 103 seconds later were both recovered from them by timestamp tonight. So chat harvesting is feasible rather than aspirational.

He asked whether such a store could be made almost impossible to lie, or for the assistant to make a mistake with. The honest answer has 2 halves. It can make the state impossible to misreport, because a state is read rather than inferred, and a gate on the turn's end can refuse to let the assistant present a closed item as open. 4 such gates refused work correctly over the last 2 days. What it cannot do is make identity impossible to misjudge: deciding that a new finding is the same thing as a given closed ticket is the duplicate problem, and tonight shows the assistant's text matchers fail at exactly that. The mitigation is that a ticket carries his verbatim words, so a human read settles it in seconds, which is how the routing ladder rediscovery was caught. So: state yes, identity reduced but not eliminated.


## The Orchestrator Experiment, Answered On His 3Rd Asking


He is right that each previous turn mentioned this and answered none of it.

Is it sound as an experiment in its own right? Yes, with 1 correction: it is 2 arms and not 1, because the role he describes bundles 2 separable jobs. Deciding which candidate repair is better, which compose, and which meet the simplest sufficient and additive standards has an executable criterion today, because an existing module already asks of a single repair whether it cures the defect its own falsifier demonstrates. That arm can be scored against ground truth. The monitoring job, which is his continuous monitoring protocol performed from inside the harness, has no defined predicate at all, because nothing anywhere specifies what counts as something having gone wrong. Running both as 1 experiment would confound a measurable arm with an unmeasurable one.

What would be predicted, recorded now so it can be falsified later rather than rationalised afterwards. Across the 3 shakedown legs, 77 of 79 adjudications were made by tools rather than by assertion, 97.4684 per cent, on an interval from 91.2314 to 99.3030 per cent. So a bound orchestrator would operate in a system where its own assertions mostly decide nothing, and the classifier arm should come close to parity. The monitoring half should degrade, because monitoring is the one judgement the harness does not instrument. This session is evidence for that prediction rather than an argument for it: 6 of the assistant's own monitoring judgements failed tonight, and because each has a known correct answer, that failure set is a usable test corpus for the monitoring half.

Where on the runway, and the recommendation is not last. His instinct was that this is one of the last tests before final release. Against that: the orchestrator role is where the measured failures are, so testing it last means finding orchestration faults after everything else is frozen. In favour of waiting: a live bound arm needs a harness that is not still moving under it. Both are satisfied by a shadow run first, in which the bound orchestrator observes a real experiment and records what it would have decided while the assistant continues to decide, and agreement is measured afterwards. That costs 1 run's observation, risks no decision, and needs no stable harness because it changes nothing. Recommended placement: the shadow run immediately after the first stage's replay test, which is free and already the nearest actionable item on the whole runway, and the live bound run after the migration to the canonical branch and before the final capstone experiment.


## The 3 Rulings Still Needed


First. The note checker does not exempt his verbatim quotations from its undefined term rule, although the routine that performs the exemption exists and the module's own documentation states the standing rule that the checker is never applied to his words and never gates his input. This was established by a controlled test with 3 cases and 1 variable: with a phrase appearing only inside his quoted words, 1 finding; with the same phrase also in the assistant's own prose, still 1; with his quotation redacted and nothing else changed, 0. What needs his word is only whether the 73 historical notes are in scope, or whether the checker is fixed going forward and the archive left alone.

Second. The free panel of the 16th corrected 3 of the assistant's repairs, and 1 seat's own quoted confidence interval does not reproduce under any of 5 standard methods. That seat's finding stands. What needs his word is whether to adopt its fix with the interval corrected in the adopted copy, given that the fix touches the same function as another seat's work.

Third. The local memory budget hook cannot tell an instruction from a prohibition. It refused 2 calls tonight whose text explicitly forbade the delegated work it guards against, because it matches on the words regardless of whether they are commanded or banned. This matters more than the inconvenience, because an author who cannot state the limit in a brief will either drop the limit or rephrase around the matcher, and dropping it makes the delegated agent more likely to run the very tooling the guard exists to prevent. What needs his word is only confirmation that a guard he relies on may be made aware of negation.

And a fourth, which is a placement rather than a decision: whether the orchestrator shadow run goes where it is recommended above.


## The 4 Questions The Assistant Owes Him


These are not decisions for him. They are questions he asked that were never answered.

From the 2nd of October, against a list of 7 withdrawn claims: can similar errors be prevented in future, and if not, might they lead to unhelpful and erroneous decisions.

From the 4th of October: he had asked for a free panel review on how to make a particular measure more effective, less coarse, more accurate and more useful, potentially across a wider range of uses. That review was never run.

From the 5th of October: are the 12 skipped items safe to ignore.

From the 7th of October: if a particular facility is on, and he judged that it probably should be, what effect would it have on the experiments, given that human review is part of the harness in any case.


## Work Remaining That Carries His Ruling Already


31 items, in the order his rulings arrived. The oldest 2 are from September: the target classification point of the 10th, and the requirement that a completed entry's evidence must fail when its own repair is reverted, from the 17th. From early October: the claim channel's promotion, official terminology, a measurement owed to the programme of study, the routing ladder's order, a facility that should default to on, the false quiet chance which he ruled on twice, the seat time cap, the ranking number, and the zero plant control. From the 11th: the fold fixes back timing and default, which is 0 of 2 built and is the only outstanding item that changes what a paid run does. From the 15th and 16th: the board triage, the parked file reconciliation, 3 recorded but unfixed defects, the coherence budget recalibration, the per seat capacity ceiling, the 94 unservable blockers, the fingerprint reset, the immune memory reset with a researcher switch, the hashed model identifiers, retiring the density ceiling, and the whole correction list. From the 17th: model admission, mechanical restore after compaction, the orchestrator entry, model and role selection, the general purpose STEM panel question, and the ticket store which he placed first.

2 of those are prerequisites for several others regardless of date order. Wiring the policy engine into the current runner makes the model and role work declarative rather than scattered across 12 tables. And moving the fix promotion out of the per round loop must precede switching its default on, or the first live run inherits the moving target he ruled against.

Written under CDSFL note standard v1.7, 26 August 2026.
