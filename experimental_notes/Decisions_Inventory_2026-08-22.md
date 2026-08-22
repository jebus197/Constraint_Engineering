# The decision inventory. Everything currently waiting on the founder, everything that does not need to wait, and everything that can be deleted from the pile.

22 August 2026


## How This Is Organised

Three lists. The first is decisions that are genuinely the founder's and cannot be settled by any measurement. The second is things that were sitting in the pile but need no ruling at all, and will simply be done and reported. The third is items that are already dead and should be struck off.

Each item in the first list gives the choice, a recommendation with the reason, and what it holds up. Most are a one word answer.

Nothing will be built or run until the first list is answered.


## List One. Nine Decisions That Are Actually The Founder'S


ONE. The discrimination gate: block, label, or retry?

Last night's control showed that half the archive's confirmations are backed by a test demonstrated to respond to the accused defect, and half are not. The obvious response is to make the system run that check on every finding. But what it should then DO with a failure is a design decision with real consequences.

Block. A test that fails the check cannot mark a finding confirmed. Quality becomes 100 percent by construction. Yield roughly halves.

Label. Record the outcome and let the finding through, marked as asserted rather than demonstrated. Yield is unchanged and the quality becomes visible rather than enforced.

Retry. A failure is fed back to the model that wrote the test, saying in effect that the test did not respond when the defect was repaired, and asking for a better one. Up to a fixed number of attempts, then block.

The recommendation is retry, then block. The project's own earlier self test recorded that iteration is load bearing, and a filter that only subtracts turns a quality problem into a volume problem. Retry turns the same check into a quality loop. Blocking alone risks leaving too few findings in a large benchmark run to measure anything.

This holds up: the fix experiment, and every future run.


TWO. When a finding is reclassified as equipment error, does it stop counting?

A test that crashes rather than firing is not evidence in either direction. The verdict reader now correctly labels those as equipment error rather than as a result. The question is what happens to the count of open findings.

If equipment errors stop counting as open, a run can reach its stopping condition sooner simply because tests broke. That is the wrong direction: the system would look more converged the more its instruments failed.

The recommendation is that equipment error counts as unresolved, not resolved. It should never bring a run to an end.

This holds up: any future run. On the existing archive nothing moves, because every affected entry is already in a final state.


THREE. The similarity pairs. How many is the founder willing to do?

There are 133 pairs of findings where the question is whether two findings describe the same defect. Machine adjudication by repair settled 33 of them in both directions. It could not settle the other 100: 35 agree in one direction only, 33 are undecidable, 17 agree the other way only, 8 disagree with themselves, and 7 have no usable baseline.

Three panel models also objected that adjudication by repair is not ground truth, because one broad repair can cure two genuinely different defects. So even the 33 settled ones are provisional.

Doing all 100 by hand is several hours of reading pairs of findings and answering same or different. The recommendation is not to do all of them. A stratified sample of 30, drawn across the disagreement categories, is enough to calibrate the operating point and would take roughly an hour. The rest can stay open without blocking anything.

This holds up: any claim about how well the duplicate detection works. It does not hold up the fix experiment.


FOUR. The critical severity threshold, currently 0.7.

One number decides which findings count as critical, and critical findings are the ones that cannot be cleared automatically and become permanent human work. A false positive there costs real time. There is a frozen pre registration in the repository that defines critical by consequence rather than by a number, and 0.7 is described in the code as the operational proxy for it.

The choice is to keep 0.7, or to switch to the consequence based rubric.

The recommendation is to keep 0.7 for now and simply make the pre registration visible from the live work queue, which currently does not cite it at all. Moving the number in the middle of an experimental arc breaks comparability between runs on either side of the change, and that cost is larger than the benefit.

This holds up: nothing immediately. It is on the list because a future agent could move that number without knowing a frozen pre registration governs it.


FIVE. The remaining exams. Redesign before running, or run as they are?

Experiments 48 and 49 have already been excluded from headline claims: their answer keys were contaminated, both target documents have since been deleted from the machine, and every detached test in the whole archive lives in those two runs.

Experiments 50 and 51 are built but not run. They carry the same design feature that caused the problem, which is that true and false statements were paired in a way that made the pairing itself a clue.

The recommendation is to redesign 50 and 51 before running them, pairing true with true so the pairing carries no information. This costs a redraft and a re verification.

This holds up: experiments 50 and 51.


SIX. The load balancer. Retire it?

Research confirmed the founder's reasoning about scaling and called it stronger than the founder had stated it. But this particular component does not serve that purpose. It has never run outside its own tests, it contains a fault where an impossible allocation is reported as a success, and its own description of itself has been false for four and a half months.

The recommendation is to retire the component and treat scaling as a separate design question later.

This holds up: nothing. It is dead weight either way, but leaving a component that reports impossible allocations as successes is exactly the failure pattern this project exists to eliminate.


SEVEN. The ledger of claims that survived challenge. Connect it or withdraw it?

A record of claims that survived falsification was built on 8 August without an explicit decision. It has been verified that nothing in the runner reads it. It is not connected to anything.

The recommendation is to withdraw the claim that it exists for now, rather than spend effort connecting it. It is not on the critical path, and an unconnected component described in project records as existing is the precise ambiguity everything else is being cleared out of.

This holds up: nothing. It is a records accuracy question.


EIGHT. The pre registration for the experiment 46 re run. Hold it.

A pre registration document was drafted on 20 August and has been awaiting a signature. It was written before last night's control result.

The recommendation is not to sign it. It should be rewritten to account for what is now known, specifically that the discrimination gate changes what a run produces. Signing a pre registration that predates the finding it needs to account for would be worse than having none.

This holds up: the experiment 46 re run, which is already on hold.


NINE. Two security items that need the founder's own hands.

The environment file needs its values quoted. On 19 August an unquoted value was executed by the shell and printed a token into an error message. The file is parsed in Python now and never sourced, so the immediate risk is closed, but the file itself is still unquoted.

The Zenodo token that was exposed in that incident has still not been rotated.

Neither can be done without the founder, because the file is locked and the token rotation happens on an external site.

This holds up: nothing technical. It is an open exposure that has been open for three days.


## A Tenth Item, Recorded As An Assumption Rather Than A Question

The archive re grade will write sidecar files and will not modify any archived run report. This follows a standing rule already proposed in this project on 29 July, that folding a fix forward never alters a completed experiment's record. If the founder disagrees, that is the moment to say so. Otherwise it proceeds on that basis.


## List Two. Things That Need No Ruling And Will Simply Be Done

The instrument inventory. Roughly seventeen components in this system emit a number or a verdict, and nobody has ever listed them or recorded which have been commissioned, meaning tested against a known good and a known bad input. That list will be written. It is the thing that converts an apparently endless stream of defects into a finite burn down.

The 67 findings whose repair matched no stored version of its file, and the 30 that produced an error. That is a quarter of the population that could not be scored at all, and it is a finding in its own right.

The fault where a test that never ran can still write a final verdict. Four cases out of twenty four, two of them writing a refutation on no evidence. All four were escalated to a human at the time, so nothing was hidden, but the status is still wrong.

The control script that overwrites its own committed output when run with a limit. It needs a dry run option.

The memory ledger bump, which has now needed the same manual correction five times in a row because the remedy recorded on 17 August, to move it into the save state path, was never built.

Whether the component described in project records as running in shadow leaves any trace in any run. That is a measurement, not a decision. Once measured, the choice of whether to connect it or correct its description comes back as a question.

The documentation staleness sweep across everything changed in the last 72 hours.


## List Three. Strike These Off. They Are Already Settled

The perturbation instrument. It was built and run on 21 August. 397 findings tested, none moved on an irrelevant change. Settled by execution.

The file access check, meaning whether a test merely opens a file or genuinely depends on its contents. Last night's control answers it directly. Settled by execution.

Removing file writing tools from the panel dispatch. Verified: the panel route grants only reading, searching and shell tools, with no write or edit. Already done.

The claim that the founding principle is unauditable on its own record. Withdrawn. It is false for every run from experiment 42 onward and true only before 3 June 2026, when the mechanism did not yet exist.

The early convergence alarm raised on 16 August. Refuted on 17 August. No experiment is invalidated.

The two faults in the old control document. A clean control target generated by script was built on 20 August, which was the recommended resolution.


## What Happens Next

Nothing is built and nothing is run until list one is answered. The nine items are mostly single words. The recommendations are: retry then block, counts as unresolved, a sample of 30, keep 0.7, redesign first, retire it, withdraw it, hold it, and the two security items whenever convenient.

Once those are answered, the order is the instrument inventory first, because it is the thing that ends the cycle of discovering problems one at a time, and then the fix experiment.

Written under CDSFL note standard v1.4 (13 August 2026, Rule 24 added 16 August).
