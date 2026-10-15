# Both free runs converged, and the pair bought more than the contrast it was designed for

2026-10-15 09:55 BST. Plain-English companion to the technical note of the same name. Audience: a reader who does not read code.

## The result

Both runs converged cleanly on the hardened gate. That is 2 of the 3 consecutive clean convergences the success criterion requires.

Run 1, with the rulebook delivered whole and the severity specification recorded only, converged at round 3 of 10 in 82.4 minutes with 22 findings. Run 2, identical but with the severity specification actually deciding, converged at round 4 in 57.2 minutes with 19 findings. Both reached gamma_critical 1.000, sustained for 2 rounds with a leave-one-out minimum of 1.000, and both ended with 0 unresolved criticals. Cumulative criticals came out at 12 in both. Round 0 produced exactly 14 findings in both.

The contrast was checked at the layer that actually decides, not taken from the command line, because a flag in the launch arguments proves the launch and nothing else. The runner states its own mode in the log: run 1 says the severity is asserted and the specification merely recorded, run 2 says the section 7.7 specification is deciding. One line each, and none of the other.

## With the specification deciding, nothing changed and nothing broke

That is the question run 2 was able to answer, and the answer is clean. The specification agreed with the asserted critical count at 12 in both runs, nothing crossed downward in either, and no key-property violation was recorded in either.

## What may not be blamed on the flag

Rounds 1 and 2 differ between the runs, and run 2 has 19 findings against 22. None of that can be attributed to the severity specification, which governs release decisions and cannot make a seat report fewer findings in a round. The seats are simulated subagents and are not deterministic. With only 2 runs the variation between runs cannot be estimated from the pair itself, so the pair can only detect a large effect, and the archive has already measured the effect as small. The same caution applies to the intervention flags: 3 seats were flagged in run 2 against 1 in run 1, which is an observation needing a larger sample rather than a result.

## Run 2 exercised a path run 1 could not reach

Run 2 declined to converge at round 3. The gate refused because 1 finding was still contested, so the critical picture was not settled, even though every other condition was already met. The finding settled and the gate passed at round 4. That is the gate working, and it is coverage a single run could not have bought. The monitoring watchdog labelled the refusal as trouble, which is a false positive in its labelling: a correct refusal is not trouble.

## The sharpest finding, and it only became visible because both runs ran

The whole point of the severity specification is that a disproved finding scores zero regardless of what the model claimed. A tool outcome annihilates the model's number, and that is what makes it structurally unlike a vote.

Across both runs, not one of 41 findings carried a disproved verification. So the annihilating case never arose and the specification's distinguishing term could not bite.

That claim looked contradicted and was re-checked rather than defended. Both runs show 2 findings marked refuted, which a reader could take as disproving it. The two things are different fields: the specification reads the falsifier's verdict, not the finding's status, and a finding can be refuted by routes that are not a falsifier returning a refutation. Checked on exactly those findings, run 1's two carry no falsifier verdict at all, and run 2's two carry a confirmation and an integrity violation. Recomputing the census independently from the final reports agrees with the runner's own census on the only number that matters: zero disproved verifications, at two different moments, by two different routes.

So the empty result has 2 causes rather than 1: the low base rate already measured, and the complete absence of any disproved verification.

## The severity question is now answered in 3 parts, by 3 different instruments

The effect is answered by the archive replay across 2,994 findings: promoting the specification changes 7 releases, and it is small because the other half of the release test holds for only about 1 finding in 10. The switch's own behaviour is answered by run 2: it computes, agrees, breaks nothing and still converges. The key property is answered by neither run, and was gated on a staging defect that is now fixed.

A zero would need 688 findings before it carried information at the measured rate, so the 2-run contrast is under-powered by a factor of 31.27.

## 2 defects found during the runs are fixed

The first is that the confinement guard refused a falsifier permission to read the very document it was asked to review, 18 times per run. Both halves were individually right: the guard refuses anything inside the run-evidence tree because a falsifier that can read run evidence can read earlier verdicts, and that hole was closed on the 12th of October after both free seats found it independently; separately, since the 1st of September, the runner had placed its working copy of the target inside that same tree. The date is settled by the refused paths rather than by commit history: the run of the 3rd of October has 81 refusals and not one is a target, while both runs today have 18 and all 18 are. The working copy now lives in the designated, permitted place for a staged review target, and is mirrored back into the run's archive on every write so nothing is lost. The fix was proved sound before a line of it was written, by extracting the guard's own decision function and calling it on both the old and new locations. 15 tests that execute, 4 mutations each turning them red, and the guard that closed the original hole still passes.

The second is that a simulated run restamped all 5 real paid seats' fingerprints at the moment of convergence, in both runs. No measured value moved, so it was a labelling fault rather than corruption, and what kept the records apart was one thing only: the mandatory simulation suffix makes them different keys. The fable seat found this on the 5th of October and named the load-everything-then-save-everything asymmetry precisely. Its script existed only inside the sandbox it was written in, absent from the scripts directory and named nowhere in the task list, and the defect survived 10 days. The saver now writes a seat only when something about it actually changed, fable's script is promoted unchanged under a header naming it as the author, and that script now reports the repair from its own output.

## 2 remain open, deliberately

The coherence-budget recalibration is inert in 3 separate ways, each sufficient on its own: nothing calls it, it changes a value that lives only in memory, and when handed a real run's logs it returns its own existing defaults because none of the 61 recorded entries carries the 2 fields it reads. Its arithmetic is sound, so this is a mismatch between what the runner writes and what the calibrator expects to read. Until it is closed, the lean-versus-full comparison that every proposed cut has been gated on since the 18th of July cannot be run.

The other open item is the 3 defects recorded on the night before the runs and deliberately left unfixed, unchanged by these runs.

## 2 more arms answered from the runs' own logs

On the discrimination guard the answer has 2 halves. The probe's population is nearly empty and that is good news: 40 corrected copies were accepted of 57 offered, so the real control could act on nearly everything and the synthesised side was needed for just 1 falsifier across both runs. But that single probe could not speak, because of the staging defect above. So that defect blocked the post-run sweep as well as verification inside the run, and 2 arms were gated on the same repair. Both are unblocked now.

On the classifier, the answer needed no new run, because it was already running. It made 22 classifications and the accounting closes exactly: 9 agreed with the pattern-matching classifier, 10 overrode it, and 3 had the override refused by a guard protecting the mathematical label. Agreement is better than chance but indistinguishable from a coin flip, which is unsurprising on a document whose planted defects are a variance estimator and a confidence interval, where 7 of the 10 overrides are exactly the move from statistical to mathematical. Of the 3 clauses in the founder's confidence composition, 2 hold: the classifier does decide, and it never blocks. The word "blocked" in the log points the other way, at the guard refusing the classifier. The third clause, that syntax raises confidence, cannot be measured from any run log, because only 1 confidence is recorded per classification and no earlier value exists to compare. That is filed as an instrumentation gap.

## A tension in the programme's own design

The in-round clearance arm asks whether the unresolved section elicits the identifier-addressed falsifier form at all. Run 1 gives none in 29 seat replies, and that zero means nothing, because the form can only be supplied if there was an unconfirmed critical for a seat to address, and run 1 ended with none. The success criterion is 3 consecutive clean convergences; a clean convergence leaves no unresolved criticals; and that is exactly the state in which this arm cannot be read. The better the runs go, the less measurable it becomes. 3 options are on the record, and the choice is a decision rather than a repair.

## Where the programme stands

6 of the 7 outstanding measurements now carry results, and 4 of those were answered from the runs' own completed logs with no additional dispatch. Only the paired baseline remains, and its cost has doubled: its core assumption still holds, because its target is byte-identical at the old commit and today, but its comparison arm names a run that was current 141 commits ago, including the rulebook repair that arm exists to evaluate. So it is 2 free runs rather than 1 if it is to speak about the runner and composer as they now stand.

## The board, and why one test is red

The single failure before the fixes was the burndown test, and it is red for the right reason: today created 6 entries and has closed 4. The test requires closures to outpace discovery, and that cannot be reached today by honest means, because it would need 7 closures against 6 entries created. Closing an item that is not actually done would turn it green and would be precisely the dishonesty the test exists to prevent. A fresh board is running at the time of writing.

## Cost

Neither run spent money. The simulation substitutes subagents at the single point a paid model would be called, every seat label carries the simulation marker at source, and the spending limit is zero. No archived run can now be replayed against the current composer and expected to reproduce, which is the price the rulebook repair was parked for and which was accepted in terms.

Written under CDSFL note standard v1.7 (26 August 2026).
