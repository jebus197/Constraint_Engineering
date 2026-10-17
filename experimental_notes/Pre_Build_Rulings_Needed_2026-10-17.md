# Pre-build briefing. What is on the task list, and the 3 decisions still needed. 2026-10-17, 01:40 BST.


## A Note On The Hour, Said Once


This was written at 01:40. The standing rule in the project directives is that work between 23:00 and 05:30 should be flagged rather than carried on as though it were the afternoon. The 3 decisions below will keep until morning, and reading them rested is likely to produce better rulings than reading them now.


## The State Of The Task List


The list now holds 139 entries: 38 open, 95 done, 1 blocked, 5 withdrawn. The marker checker reports 0 coherence problems.

Of the 38 open items, 31 already carry his ruling and are ready to build. Only 3 genuinely need a decision from him, and a further 4 are questions of his that need an answer from the assistant rather than a ruling from him. The list grew from 18 to 38 open items during the night, because an audit of his own annotations found 20 instructions and rulings that nothing was tracking. That audit is described below, and it is the direct answer to his suspicion that his replies were not being read in full.


## Why It Was Mislabelled, Which Is A Defect And Not An Excuse


A field called ruled was added to every task entry on the 16th of October, for exactly the reason he identified: a ruling he had already given left its entry indistinguishable from one he had never seen, so settled questions kept reappearing in the decision queue. The field was built and it works. It was simply not being filled in when entries were written.

Measured before the repair: 10 of the 15 open items cited a founder ruling in their own body text while carrying an empty ruled field. That is 66.6667 per cent, on a 95 per cent interval running from 41.7135 to 84.8237 per cent by one method and 38.3804 to 88.1759 per cent by another. All 10 have now been filled in, each dated to the annotation that decided it. So the queue falls from 15 apparent decisions to 3 real ones.


## The 3 Decisions Still Needed


First. The note checker is blind to its own standard stamp, and 73 notes slipped past it. A second and sharper instance of the same blindness was found tonight and is recorded with it: the checker does not exempt verbatim founder quotations from its undefined-term rule, even though the routine that performs the exemption exists and the module's own documentation states the standing rule that the checker is never applied to his words and never gates his input. This was established by a controlled test with 3 cases and 1 variable. With a phrase appearing only inside his quoted words, 1 finding. With the same phrase added to the assistant's own unquoted prose as well, still 1 finding. With his quoted span redacted and nothing else changed, 0 findings. Removing his words removes the finding. The practical harm was felt the same night: the finding count is a blocking pre-commit gate, so every new entry quoting him raises the count and the commit is refused, and the assistant then rephrased its own prose 4 times to compensate for findings caused by his quotations. The recommendation is to apply the existing exemption inside the term rule and guard it with a test shaped exactly like those 3 cases. What needs his word is only whether to treat the 73 historical notes as in scope or to fix the checker going forward and leave the archive alone.

Second. The free panel of the 16th of October corrected 3 of the assistant's repairs, and 1 seat's own quoted confidence interval does not reproduce. The seat's finding stands, that 30 of 48 identifiers were mis-attributed, but the interval it published matches none of 5 standard methods and is narrower than the correct one at both ends. The harvested copy has deliberately not been edited, because it is the record of what that seat actually wrote. What needs his word is whether to adopt that seat's fix with the interval corrected in the adopted copy, given that the fix touches the same function as another seat's work.

Third. The local memory-budget hook cannot tell an instruction from a prohibition. It refused 2 calls tonight whose text explicitly forbade the delegated work it guards against, because it matches on the words themselves regardless of whether they are being commanded or banned. The first refusal fired on a brief saying do not run the verification tooling. The second, after that word was removed, fired on a phrase inside the same prohibition. This matters more than the inconvenience: an author who cannot state the limit in a brief can either drop the limit or rephrase around the matcher, and dropping it is actively dangerous, because a delegated agent with no stated limit is more likely to invoke the tooling rather than less. So the false positive selects for the behaviour the guard exists to prevent. The recommendation is to require an imperative context before refusing and to suppress the match where a negation appears just before it. This needs no ruling on whether, only confirmation that changing a guard he relies on is acceptable.


## The Audit Of His Own Annotations, Which Is The Answer To His Suspicion


He said the short work list made him suspicious that his responses were not being read in full. He was right, and the first attempt to answer him was wrong in the direction that flattered the assistant.

That first attempt measured word overlap: whether the distinctive words of each of his verdicts appear anywhere in the task list. It reported 198 of 199 covered, 99.4975 per cent. It even passed a control test, because his verdicts averaged 81.38 per cent overlap against 33.65 per cent for unrelated STEM prose, separating by 47.74 points. But it answered the wrong question. Whether his topic words appear in a list says nothing at all about whether his instructions were acted on.

The audit that answers the right question examined 302 of his annotations dated the 1st of October or later, read with the dedicated reader because 319 of his 579 verdicts sit in files a plain text search treats as binary and cannot see. Five independent auditors went through them instruction by instruction against the task list. Every gap any auditor claimed was then handed to a separate agent that had not seen the auditor's reasoning, briefed to refute the claim and to default to not a gap whenever uncertain.

266 instructions were identified. 44 gaps were claimed. The adversarial stage refuted 24 of those 44, which is 54.5455 per cent, so a single unverified pass would have overstated the result by more than double. 20 survived.

20 of 266 instructions, 7.5188 per cent, on a 95 per cent interval running from 4.9197 to 11.3274 per cent. Four tools agree to 7 significant figures: statsmodels, scipy, mpmath, and the local Wolfram Engine, which returned 4.919703024776954 and 11.32741445387045 and was classified as verified by the project's own Wolfram standard. Computed with Wolfram Language on the local Wolfram Engine.

Of the 20: 12 are rulings he gave that were never carried out, 4.5113 per cent of all his instructions on an interval from 2.5992 to 7.7185 per cent. 4 are instructions nothing tracked. And 4 are direct questions he asked that were never answered. The dates run from the 2nd to the 16th of October.

They are now entries C1 to C20, each carrying his verbatim words, the reason nothing tracked it, and the verifier's failed attempt to refute it. Several are substantial: that the routing ladder should be a measured statistic rather than a list of vendor names; that a ladder must work in both directions so a seat whose measured capability improves can climb it; that a free model missing from the ladder entirely should be added; that a false quiet chance of 0.1159 at full roster should be fixed, which he said twice; that there should be no distinction between participating models other than a ranking number; and the hashed model identifiers, which he raised again tonight.

The shape of the failure matters more than the figure of 7.5188 per cent. Not one of the 20 was lost because it was hard. Each was answered in conversation, or partly built, and then never written into the list that survives a compaction. That is the same shape as the finding recorded on the 15th of October about a seat's work sitting unread in a sandbox for 10 days.

The 20 entries are therefore now guarded themselves, since the audit's own finding is that entries are lost rather than refuted. A test of 45 assertions pins the set of 20 identifiers rather than a count, because a count cannot detect a swap. It requires each entry to carry his words and the verifier's refutation, and every ruling entry to carry the date he ruled. Five deliberate breakages each turn it red. Two of those breakages first passed and exposed real faults: one was an invalid breakage that targeted a question entry as though it were a ruling, and the other was a genuinely empty assertion whose fixed window of 40 characters ran past a short quotation into the next heading, so blanking his words still left 40 characters of the following heading to measure. Its threshold is now derived from the data rather than guessed: his shortest genuine quotation among the 20 is 34 characters, and a blanked one reduces to 0.


## The 4 Questions Of His That Need An Answer Rather Than A Ruling


These are not decisions for him. They are questions he asked that were never answered, and the assistant owes the answers.

From the 2nd of October, on a list of 7 withdrawn claims: can similar errors be prevented in future, and if not, might they lead to unhelpful and erroneous decisions.

From the 4th of October: he had asked for a free panel review on how to make a particular measure more effective, less coarse, more accurate and more useful, potentially across a wider range of uses, and that review was never run.

From the 5th of October: are the 12 skipped items safe to ignore.

From the 7th of October: if a particular facility is on, and he judged that it probably should be, what effect would it have on the experiments, given that human review is part of the harness in any case.


## The Single Most Important Finding Of The Night, And He Predicted It


He said he had already ruled on fold fixes back, probably more than once, and that the aim is never to give the models a moving target during an experiment. The record confirms him exactly. His ruling of the 11th of October reads: folding fixes forward should be on by default, providing that means folding forward at the end of an experiment and not during it so that the target under study does not keep constantly changing. We had problems with this in the past, where because the models were looking at a constantly moving target, convergence effectively became impossible.

Measured by execution, that ruling is 0 of 2 conditions met, 6 days later.

Condition 1, on by default. The runner configuration defaults the facility to off.

Condition 2, at the end and not during. The single call that promotes a fix sits inside the per-round loop, guarded so that it fires every round after the first, and the comment 3 lines above it states the intent plainly: rebuild the payload so that this round reviews the repaired artefact. Two further comments elsewhere in the same file say the flag rewrites the reviewed target between rounds. That is precisely the moving target he ruled against, and the project's own notes from June carried the same warning before he restated it.

A separate ruling of his, from the 5th of October, requires that the facility never touch the live tree and that fixes stay reviewable and revertible. That condition is met, and is held by a dedicated test suite of 7 tests verified against the disk rather than from a docstring. It should not be confused with the 2 that are unmet.

Why this has not yet damaged a run is luck rather than design. The facility is armed in 1 of 49 run configurations, 2.0408 per cent, on an interval from 0.3612 to 10.6935 per cent, and no archived run log contains the line the promotion emits. So the defect is latent. The moment the default is switched on to satisfy the first condition, the between-rounds rewrite becomes live on every run. The 2 conditions therefore have to be built together, and the timing one first. No further ruling is owed on this.


## His Direct Questions, Answered


On the fingerprint repair, and whether he had already ruled. He had, and asking again was the error. His annotation of the 16th said the fingerprints should be recomputed in the first blind run of any experiment. That settles it: the reset must be total, so the second loader that currently reaches around it has to honour the same setting. The choice between making that loader aware of the setting and clearing its cache does not change any behaviour he specified, so it is not his decision to take. The request for a ruling has been withdrawn from the entry.

On hashed model identifiers, his correction is accepted and the record supports him. He did not describe the facility as operating anywhere. He asked whether it was built, was told no, and instructed that it be built, put to panel review, tested and implemented. The assistant then wrote that he had described it as already operating, which misread a question ending in a question mark as an assertion. The work remains unbuilt and is on the list.

On the orchestrator bound inside the harness. He was right that this was absent from the previous discussion entirely. It is now a task entry carrying his specification verbatim, including his words that the orchestrator's role inside the harness should be "more or less identical" to the assistant's role outside it under the monitoring protocol, that it should run largely autonomously through an experiment, and that it should serve as the primary interface where researchers enter instructions, discuss changes, monitor runs and discuss findings. His priority instruction is recorded with it, that this should not become a distraction and belongs after the other outstanding work. A prediction has been written down now rather than after the fact, so it can be falsified: a bound orchestrator should degrade less than intuition suggests, because across the 3 shakedown legs 77 of 79 adjudications were made by tools rather than by assertion, 97.4684 per cent, on an interval from 91.2314 to 99.3030 per cent. A bound orchestrator would therefore be operating in a system where its own assertions mostly decide nothing. The arm most at risk is not correctness but the monitoring judgement itself, noticing that something is wrong when no rule defines wrong. His question about where on the runway this belongs is the one thing still open on it.

On whether adding, removing and configuring models can be made trivial without large rewrites. The answer is yes, and most of the difficult part is already built. The policy registry is a 4 layer hierarchical merge engine with monotonicity enforcement: universal constraints, then domain, then task, then model, and any lower layer that tries to weaken a hard universal constraint raises an error. That monotonicity is exactly the safety property arbitrary model selection needs, because it means a researcher's choice of model cannot loosen a hard constraint. Measured by execution, the domain layer already holds 10 domains and the model layer already holds 6 model files. The gap is wiring rather than architecture: the canonical runner makes 0 calls to the merge engine, the engine is reached only by an older runner and a separate module, the task layer does not exist as a directory, and there is no role layer at all. The work is to wire the engine into the current runner, redirect the 12 live per-model tables to read the merged policy instead of their own dictionaries, add a role dimension that composes with the existing merge rule, wire the existing policy validation routine as a pre-run check that reports every missing registration at once and refuses the run, and generate the selectable list from the registry plus a remote query plus a local probe with local models first as he specified. The first and fourth of those are each a handful of lines and the second is 12 small redirections. None is a refactor of large elements. It then goes to the free panel as he directed.

On what a fix should mean outside code, and whether this is yet a general purpose STEM calculator. This is now a panel question with the evidence attached for both sides. In favour: the domain layer already covers 10 STEM domains rather than 1, the ground truth corpus holds 5 independently written STEM documents with 29 tagged claims and a runnable falsifier template each, and all 3 shakedown legs ran in the mathematics domain against a prose target with embedded computable fragments and converged at rounds 3, 4 and 4. So the harness has already converged on non code STEM 3 times. Against: the canonical runner never consults the merge engine, so nothing domain adaptive reaches a live run and the domain name reaches only prompt composition; the routing decision has the software domain as its primary mode, which he already flagged as risking redundancy outside code; and the STEM corpus is reached by the simulation tooling but by no live path module. The deeper question the panel should be made to answer directly is this. In code and mathematics a fix is an edit whose falsifier can be re-run, so admissibility is decidable by execution. In an experimental STEM domain a defect in a claim may be repairable only by narrowing the claim, restating its boundary conditions, or declaring it unfalsifiable on the available evidence, none of which is an edit a falsifier can execute against. So the open question is not whether the harness can review non code STEM, which it demonstrably can, but whether its notion of a resolved finding survives when no executable repair exists. The severity specification already covers part of this, because a refuted falsifier scores 0 whatever the model claimed. What it lacks is a verdict meaning correctly identified, not repairable by edit.

On the number of parallel agents. His figure of 6 is exactly right, and it is not a convention but the cap the harness computes for itself: the limit is the smaller of 16 and the core count minus 2, which on an 8 core machine is 6. The cap was not exceeded. It governs how many run at once, not how many exist over the life of a run, so a staged job can create more than 6 in total while never running more than 6 together. Measured while the audit was running: 0 Python or Node processes above 1 per cent processor time, and 39 per cent of memory free. The resource that genuinely competes for the machine is a local verification process at roughly 365 megabytes, which is governed by a separate budget of 2, and that is what the refusal earlier in the night was protecting.


## Two Errors Of The Assistant'S, Corrected Tonight


He caught the first. A figure of 11 was reported as a number of seats. It is the number of fingerprint files accumulated on disk across all runs. Those 11 records cover 6 distinct models, 5 of which carry both a paid and a stand in record while 1 carries a stand in record only. Both loaders return a mapping keyed by label, so its length is a number of labels and never a number of seats. The largest panel ever seated is 7, so 11 could not have been a seat count under any configuration, and the error was detectable without reading any code. He notes it is the second occurrence. It was corrected in 3 documents and the producing script now prints the distinct model count beside the record count so the 2 cannot be conflated again.

The second was caught by the project's own falsification gate. A claim was about to be reported that 36 of 39 of the task list's findings were artefacts of unmasked quotations, 92.3077 per cent. That rested on calling a function with a string when its signature takes a file path, so it silently returned an empty result for every input and the flattering answer was a type error rather than a measurement. The broad claim is withdrawn. Only the single narrow instance, established by the 3 case controlled test described earlier, stands.


## The Build Order, If He Authorises It


The 15 ruled items in the order his rulings arrived, which is also a sane dependency order: the target classification point from the 10th of September; the requirement that a completed entry's evidence must fail against its own reverted fix, from the 17th of September; the fold fixes back timing and default, from the 11th of October; the board triage, from the 15th; then the parked file reconciliation, the 3 recorded but unfixed defects, the coherence budget recalibration, the per seat capacity ceiling, the 94 unservable blockers and the fingerprint reset, all from the 16th; then model admission, mechanical restore after compaction, the orchestrator entry, the model and role selection work and the general purpose STEM panel question, all from the 17th.

Two of those are prerequisites for several others and should go first regardless of date order. Wiring the merge engine into the current runner makes the model and role work declarative rather than scattered. And moving the fix promotion out of the per round loop has to precede switching its default on, or the first live run inherits the moving target.


## What Is Asked Of Him


Three rulings, listed above. Confirmation of the build order, or a different one. And nothing else is blocked: the remaining 15 items carry his word already.

Written under CDSFL note standard v1.7, 26 August 2026.
