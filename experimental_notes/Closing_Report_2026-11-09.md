# Closing Report, 9 November 2026

*9 November 2026, 03:11 GMT*

## Summary

2 instructions were carried out overnight. The 11 failing tests were repaired, and the 104 guard files dated 29 October or later were added to the project's pre-commit gate, which grew from 128 files to 232. This report supersedes the closing report of 8 November 2026.

1 decision is returned to him, and it is the only thing in this report that needs him. The gate now costs more than the limit written into its own header, and it had already exceeded that limit before any of this work began.

## What Was Closed, And The Number That Moved

Entry B21 concerned how much work it takes to add a model to the harness, and the real cost was never the number of edits. It was that the failures were silent. A new seat passes through 10 admission steps, and until tonight 1 of those 10 could fall back to a default without recording anything an instrument could count.

That step was the composer directive-set fallback. It wrote a log line reading COMPOSER FALLBACK, and a log line is not a record: nothing downstream can tally it. The recording function now has 1 definition in bench/routing.py with 2 callers, and bench/reference_runner_v3.py calls it at the fallback from inside a try block, because a record is worth a lost log line and never a dead experimental round.

The measurement is now 0 of 10 steps failing silently, against 1 of 10 before. As a proportion that is 0 per cent, with a 95 per cent Wilson interval running from 0 to 27.7533 per cent and a Clopper-Pearson interval from 0 to 30.8497 per cent. Both intervals are wide because the denominator is 10, and a wide interval is the honest report of a small sample. Of the remaining steps, 9 announce their default and 1 fails loudly, which is the intended behaviour. The producer is scripts/how_many_places_must_change_to_add_a_model_2026-10-16.py.

## The Decision That Is His

The pre-commit gate's own header records a judgement that a gate costing 11 minutes would be bypassed within a day, and that a guard which gets bypassed is not a guard. That limit is 660 seconds.

Measured from the gate's own duration ledger by scripts/what_the_commit_gate_actually_costs_over_time_2026-11-08.py, the gate has exceeded that limit on 7 of its 8 recorded runs. As a proportion that is 0.875000, with a 95 per cent Wilson interval of 0.529112 to 0.977583 and a Clopper-Pearson interval of 0.473490 to 0.996840, the 2 routes of each agreeing to 1.11e-16. The 104 added files run 1,271 tests in 890.45 seconds, and the 2 boards actually measured at the new size came in at 1,593.05 and 1,587.85 seconds, or about 26.5 minutes. Against the stated limit the projection is a factor of 2.373157.

A STRONGER CLAIM MADE EARLIER THE SAME NIGHT IS WITHDRAWN, AND THE REASON IS INSTRUCTIVE. A second instrument, written without first checking that the one above already existed, read 5 rows of the ledger at about 01:45 and reported a mean of 706.000000 seconds with a one-sided t-test giving 0.022365, which rejects the hypothesis that the gate sat at or below its limit. That was quoted as the gate being significantly over its limit before any of tonight's work. On the fuller ledger the mean over the 6 boards at or under 900 seconds is 675.833333 seconds with a standard deviation of 80.474634, the test statistic is 0.481936 on 5 degrees of freedom, and the probability is 0.325103 by 2 independent routes that agree. The 95 per cent interval, 591.380385 to 760.286282 seconds, CONTAINS the 660 second limit. So the hypothesis cannot be rejected and the significance claim does not stand.

WHY THE NUMBER MOVED IS THE POINT, NOT THAT IT MOVED. The 5 row sample was read before this session's own commit attempts appended 4 more rows to the same ledger, one of them a 525 second board that lowers the mean and widens the standard deviation from 35.64 to 80.474634. The gate writes that ledger when it runs, and it runs because a commit is attempted, so measuring the gate's cost while committing is measuring a population the act of measuring is adding to. The 7 of 8 figure is the frame that survives this, because it does not depend on the mean of a sample being stable.

AND THE SECOND INSTRUMENT SHOULD NOT HAVE BEEN WRITTEN AT ALL. 1 already existed, reading the same ledger, taking the 660 second limit from the commit hook's own header, and excluding an interrupted 12 second run by naming it rather than averaging it in. It is retired, its 2 unique contributions, the test and the projection, are folded into the one that existed, and that one was already covered by tests where the duplicate was covered by none. This is a failure this project has recorded before, under the heading of using the instrument that exists.

He ruled the addition with the 26 minute figure in front of him, so the addition stands and is not revisited here. What cannot stand is a file that asserts a limit and breaks it in the same breath, so the limit itself is what has been left open. 3 options are named in the hook and none is recommended, because nothing measures any of them against the others. Raise the stated limit to match what he accepted. Split the list into a fast tier that gates every commit and a slow tier that gates a push. Or run the slow tier concurrently, which spends his 8 processor cores and 8 gibibytes of memory and is therefore his call rather than the assistant's.

His instruction to extend the commit timeout within reasonable bounds needed no action, because a mechanism already does it. The waiter is computed as the larger of 300 seconds and 4 times the gate's last recorded duration, and it stood at 2,724 seconds, or 45.40 minutes. Nothing was typed.

## A Short Answer To His Question About Whether This Is Normal

He asked whether it is normal for a simple commit to take so long, and said he is not a developer. It is not normal. A pre-commit check in most projects runs in seconds, because it is meant to catch cheap mistakes before they are recorded. This project's gate is unusual by design: it runs a sixth of the whole test suite on every commit, because guards left outside it were found sitting red for 26 consecutive commits with nothing reporting it. The 26 minutes buys that. Whether it is worth 26 minutes is exactly the decision above.

## A Figure That Could Not Be Quoted, And Was Not

An earlier note of the assistant's cited 17 observations of the gate at a mean of 681.94 seconds. The ledger the gate writes held 6 rows, and the 17 came from a session log that is not committed to the repository. Under the project's standing rule that a measured figure must travel with the script that produced it, that number had no producer and was dropped rather than repeated. The producer named above was written in its place, and it reports a different mean over a different and smaller population, with 1 short run of 12 seconds named and excluded rather than averaged in. A 12 second run is the gate failing closed on missing infrastructure, not a measurement of what a board costs, and averaging it in would make an expensive gate look cheap.

## The Instruments, Which Is Where The Errors Were

The repair to the admission step was real and its own measurement could not see it. The producer classified that step as silent because the log string appears in the runner's source text, so once the recording call was added the producer went on reporting 1 of 10. A working fix and a measurement that reports failure is the harder of the 2 states to notice, because the number looks like evidence.

The producer's test is now structural rather than textual. It parses the runner with Python's own syntax tree, which it already imported, and requires the call to be a whole statement. This matters because a textual search cannot tell a live call from a disabled one. 2 reversions were put to the new guard and both came back green: a call written as a disabled conjunction still contains the function's name, and a call commented out in the middle of a line sits on a line that begins with something else, so stripping comments does not help. After the correction, 5 of 5 reversions fail as they should, across 9 assertions.

A second instrument fault in the same pass: Python's parser accepted a generated file whose import ordering Python refuses to actually import. Validation of generated source now uses the compiler rather than the parser, because the parser checks grammar and the compiler checks the rules that decide whether a file can load at all.

A third, and it is the clearest illustration of why a passing test proves little. A small script was written to re-point the 6 line references that the night's edits had moved, twice, by 144 lines and then by a further 15. It has 3 protections. Each had a test. Removing each protection left its test passing, for 3 unrelated reasons, all with the same root cause: every test ran against the healthy reference table, which is the state in which none of the protections is needed. The tests were rewritten against the degraded inputs, and 5 of 5 reversions now fail. The sharpest consequence was never a failing test but a passing one: if the re-pointer picks the wrong one of 2 identical lines, the reference names a line that does hold the expected text, so the guard goes green while the claim points at unrelated code.

## A Correction That Would Itself Have Been The Error

The closing report of 8 November said of entry B21 that the entry still says 5 of 10 and is out of date. That sentence was logged as a false claim to be corrected, on the stated grounds that the entry does not contain that figure at all. Checked against the file before anything was written, the entry contains it once, in the clause that reads the count is now 5 of 10. The report's sentence was true, and the correction would have introduced the error into the document he reads as the record.

This is the third time a correction of the assistant's has needed checking before being written, and it differs from the earlier 2. Both of those were arithmetic. This was a claim about what a file says, which is the cheapest kind of claim to verify and the easiest to assert from memory, because having read the file once makes the recollection feel like evidence. The entry has been superseded rather than called false, because it was true when written and that is a different statement from being wrong.

## What A Tool Did While The Board Was Running

While the 232 file board was in flight, the project's triage tool was invoked to record that the task list could not safely be written to during that window. The measurement behind that judgement is that 38 of the 232 board guards read one of the surfaces involved. The tool recorded the finding by appending it to a file in a watched directory, which is itself a write of exactly the kind the finding describes. 3 of the 232 guards read that file.

The append was left in place rather than reverted, for 2 reasons. Reverting is a second write to the same file and doubles the exposure window, and a restore is itself a mutation. And if the board fails on one of those 3 guards, that is better evidence than a clean board which would have concealed the hazard.

## The Symlink Defect Was Fixed In 1 Instrument And Is Live In Others

On 8 November a double count was corrected in the severity archive: a directory called exp36_evidence_latest is a symbolic link to a real run directory, and the collecting code walked both paths, so 1 run's data was counted twice. The frame fell from 3,311 severities to 3,094. That fix was scoped to the severity instrument alone.

The same defect is live in the correlation instrument that entry B77 depends on. Demonstrated by execution rather than argued: it globs 101 report files and those resolve to 100 distinct files, the duplicate being that same symbolic link. So the population behind the convergence hazard figure counts 1 run twice.

The scope was then measured, and the first measurement was wrong in a flattering direction, which is worth stating because it is the same failure the project keeps finding in its own instruments. A first pass asked whether a file that globs the log directory mentions path resolution anywhere in the file, and returned 10 of 250, or 4 per cent. That predicate is satisfied by a wholly unrelated call that every script makes to locate itself, and it did not even catch the producer already proved defective. Measured per function instead, so the de-duplication has to happen where the globbing happens, the figure is 173 of 435 functions, 39.7701 per cent, with a 95 per cent Wilson interval from 35.2797 to 44.4396 per cent. 2 independent interval routes agree to 12 decimal places.

That 39.7701 per cent is an upper bound on exposure and not a count of defects. A function may not need de-duplication, or may be de-duplicated by its caller. The number of defects actually demonstrated by execution is 1, and it is the one entry B77 rests on. Both figures are given because reporting only the lower one is how a true sentence acquires a wrong frame.

## The Board

the board result is not yet in

## What Is Still Owed To Him

Entry B77, where he accepted the recommendation to adopt the roster-aware convergence window. What blocks it was described in the previous report as needing a producer. That has now been diagnosed precisely rather than asserted, and it is worse than described.

The module bench/the_intra_round_correlation_measured_2026-10-07.py contains a function that removes the confound, named rho_within_experiment. Read from the code's own syntax tree rather than by text search, it has 0 callers in production and 1 in a test. The module's own main function computes the POOLED figure and feeds that straight into the hazard calculation as the measured value, so the de-confounding function is built, guarded by its own test, and reached by nothing that runs. That is the failure mode the project's additive standard names in its second half, confirmed 11 times before this.

The 2 figures that matter most have no producer at all. The claim that simulated runs sit at 0.681094 and real runs at 0.275298 exists as prose in a docstring and as typed constants inside 2 tests, which test the ratio function at those constants rather than measuring them. No code anywhere classifies an archived run as simulated or real for this purpose. The per-report grouping the de-confounded estimator needs is also built inside the test rather than in the module, so the collection logic exists twice.

So the work is 4 steps and the third is the only one that needs a judgement: extract the per-report collector so 1 definition serves both callers, wire the de-confounding function into the module's main function, decide and record what marks an archived run as simulated, and report the hazard at the de-confounded figure while continuing to print the pooled one. No value should be chosen until that producer exists, because the current headline figure is the confounded one.

Entry B88, which needs a design decision on where a test suite comes from when the target of a run is prose rather than code.

Entry B20, the bound orchestrator experiment, deferred on his own ruling that it runs once everything else is cleared.

The limit question above. Permission over the private hooks directory, which remains the one boundary the assistant has not crossed. And the merge to the main branch, which is 598 commits ahead and 1 behind, so it needs a merge rather than a fast-forward. His instruction to push was read as this working branch, which is 71 ahead and 0 behind and therefore a clean fast-forward. The main branch was not pushed, because a single word should not be read as the larger action.

## What Comes Next

The markers for the 2 completed entries are set across all 3 of their surfaces, the session state block is written into the recovery document, the whole night's work lands as 1 commit, and the state save pushes this branch. Then entry B77's producer, which is the next piece of real work and the only one of the outstanding items that does not need him.

---

Written under CDSFL note standard v1.9.
