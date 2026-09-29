# Why rho could never fall, and what it took to fix

**2026-09-29, 20:40 BST (Europe/London).** Audience: a reader who does not read code. Companion to the technical account in "The Shakedown's First Finding: Convergence By Saturation Is Unreachable, By Construction".

## The short version

The simulated shakedown found that rho, the measure of how much of each round's work is genuinely new, was stuck at exactly 1.000 in every round of every simulated run. Stuck at 1.000 means the runner believed every single finding it received was a fresh discovery, so the discovery curve could never flatten, so a run could only ever end by running out of rounds.

The founder ruled for the narrowest of the 3 available repairs: count novelty from the record of how many times a defect has been sighted, and let that record grow whenever a second model corroborates a defect rather than only when 2 findings are formally merged.

That ruling was correct and it works. Implementing it also uncovered a second defect sitting underneath the first, and the 2 turned out to be a single repair rather than 2.

## What was actually wrong, in plain terms

Picture the runner as a clerk keeping a ledger of defects. Every round, 5 reviewers hand in findings. The clerk's job includes deciding which findings are new.

**The first defect: the clerk asked the wrong question.** Instead of asking "is this defect already in the ledger?", the clerk asked "has this particular reviewer used this particular reference number before?". So when 2 reviewers independently found the same defect and each gave it their own reference number, the clerk logged both as new. The ledger had a column for recording repeat sightings, added on the founder's ruling in September, and it was never filled in: it was only ever written to when 2 entries were formally merged, and merging requires a verdict from a tool, and no component of the runner produces one. So the column stayed empty at exactly the moment it was needed.

Measured on the run that died: all 53 ledger entries carried exactly 1 sighting. None carried 2. Yet the same run had separately recorded 10 corroboration events across 8 of those entries, in a different field that nothing counted. **The signal was arriving and being filed somewhere no one read.**

**The second defect: the clerk published the figure before finishing the arithmetic.** rho was calculated early in the round, immediately after the findings were logged. Later in the same round, after the verification stage had run, the runner recalculated how many of those findings were genuinely novel and corrected the number. It corrected the number and never recalculated rho. So the published rho and the corrected novelty total sat side by side in the same saved file, disagreeing.

This is measurable across the whole archive. Over 49 archived runs and 406 rounds, 25 rounds carry a rho that disagrees with the run's own corrected count. That is 6.1576%, with a 95% confidence interval of 4.2053% to 8.9318%. The direction never varies: all 25 are overstatements, never understatements, with a confidence interval of 86.6808% to 100.0000%. The average overstatement is 0.2066 and the worst is 0.5000, so when rho is wrong it is wrong by roughly a fifth of rho's own range.

**An honest limit on how serious that is.** On that archive it changed no convergence decision, 0 of 406 rounds, confidence interval 0.0000% to 0.9373%. The reason is mundane: all the affected rounds are early ones, and the condition rho feeds into does not switch on until round 12. So the defect corrupted a reported figure and the saturation diagnostic, not a recorded verdict. That is a fact about this particular archive, not a guarantee about future runs.

## Why the 2 defects are 1 repair

The corroboration record for a given round is not complete until the verification stage has run, and that happens after the point where novelty is counted. So moving the novelty question to the sightings record, on its own, changes nothing: at that moment in the round, the sightings record only knows about earlier rounds, which the old method already covered.

Recalculating rho after the verification stage is therefore not extra work bolted on. Recalculating rho after verification is what makes the founder's ruling function at all.

## What it produces

Replaying the change against the corroboration those runs already recorded, using nothing invented:

The run that died had a recorded rho of 1.000 in all 5 of its completed rounds. Under the repair it becomes 0.5909, 0.7500, 0.5714, 0.8750, 0.8750.

The archived panel run from 21 September had a recorded rho of 1.000 in all 8 rounds. Under the repair it becomes 0.9130, 0.8571, 0.7500, 0.2857, 0.4000, 0.8750, 0.5000, 0.3333.

That second series is the point. It rises and falls. It is a real measurement of how productive each round was, where before there was a flat line that could carry no information at all.

All 10 of the first run's corroboration events sat on entries that the verification stage had not already discarded, so every exclusion the repair makes is additional to what was already being removed. The 2 mechanisms are complementary rather than overlapping.

**The limit on those figures, stated because it matters.** They are recalculated from each run's final ledger, which includes information that only arrived after the round in question. The live runner recalculates once per round and can only see what that round knew. So these are an upper bound, not a prediction. The honest comparison is 242 of 406 rounds moving under the upper bound against 25 of 406 for the timing defect alone, with the live figure somewhere between. Only a live run settles it, which is why the shakedown is being run again rather than this being treated as the answer.

## Three further things found along the way

**A defect in the resume path, found by the new guard test itself.** The method that records corroboration refused to do anything at all if it had already recorded that particular reviewer's finding. That sounds like sensible duplicate protection, and it was, until the sightings record was added. A run picked up from a checkpoint saved before the repair would carry its corroboration in the old field and nothing in the new one, and the method would refuse to fill the gap. The whole defect would come back through the resume path alone, silently, with every test passing. Repaired by filling in only the missing piece without duplicating anything else.

**The reason the last run died, and it was not the runner.** The run reached round 5 of 8 and stopped at 18:53:47 because the session that started it ended. There has been a standing instruction since 29 July that every experiment must be launched so it survives its launcher. A script exists that does exactly that, and it only works for one particular launcher, whose arguments it has built in. The simulated runs go through a different launcher, and nothing detached those. So the instruction was in force the whole time and had no working path on the route actually being used. This is the same shape as 2 defects already in the project's record: a rule with nothing calling it. Repaired, and the repair keeps the arms running one after another rather than all at once, because 4 arms in parallel would put 17 simulated reviewers on the founder's subscription simultaneously, which is the overload he reported earlier in the day.

**The commit gate caught a third thing and was right to.** Both new measurement scripts would have run a full archive scan in response to a request for their help text. There is a standing rule that asking a script for help must never cost anything, written after 15 of 17 runners were found to bill a live dispatch on any unrecognised argument. A test enforces it for measurement scripts, and it refused the commit until both scripts answered properly.

## A measurement error caught before it became a claim

The first attempt at measuring the timing defect reported 220 of 406 rounds disagreeing, 94 of them in the opposite direction. Both figures were wrong. rho is saved rounded to 6 decimal places, and the comparison was being made to 9 decimal places, so it was measuring the file writer rather than the runner. The largest of those 94 "opposite direction" differences was 0.000000001. At the precision the figure is actually stored in, the count is 25 and the direction never varies.

This is the same class of error as one caught earlier in the day, where a filter matching anything starting with the letter C treated reviewer reference numbers as ledger numbers and compared findings with themselves.

## What is decided and what is not

Implemented: the sightings record now grows on corroboration; novelty counts distinct defects rather than distinct submissions; rho is recalculated after the verification stage.

Deliberately not taken, and going to the free panel review instead:

1. Whether the critical-severity count should also be corroboration-aware. It is currently logged for inspection and changes nothing, because the critical-severity novelty total is one of the triggers for deciding a run has converged, and moving a convergence trigger is the founder's call.
2. Whether rho's history should be retroactively corrected for earlier rounds. At present only the current round is corrected, so earlier rounds keep whatever was known at the time. The run that died holds 7 for its second round where the final ledger says 6.
3. The 2 repairs the founder did not choose: lowering the threshold at which 2 findings become merge candidates, which admits a great deal of noise at 13.79% precision, and treating a falsifier that fires on both findings' locations as the tool verdict that authorises a merge.

Guard tests: 35 covering the novelty counting, which run both the old and the new calculation and compare their outputs rather than reading the source and trusting it, and 17 covering the launcher, which start a real detached process rather than checking that the source contains the right words.

Written under CDSFL note standard v1.7 (26 August 2026).
