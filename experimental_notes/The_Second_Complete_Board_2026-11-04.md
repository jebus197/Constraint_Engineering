# The second complete board of 4 November 2026: 36 of 44 repaired, 20 new failures found, and 3 completion claims left waiting on 2 rulings

## What this records

A second complete run of the CDSFL test collection on 4 November 2026, taken after the repairs that followed the first complete run the same morning. The first run had found 44 failing tests where the commit gate reported none, because the gate runs a fixed list of 129 guard files rather than the whole collection. The purpose of the second run was to establish whether those repairs held and whether they introduced anything new.

The run started at 14:00:07 and ended at 16:09:42, taking 2 hours 9 minutes 28 seconds against a clean working tree at commit `c4553e95`. It reported **28 failed, 15,498 passed, 37 skipped**.

## The headline, and a correction to how it was first reported

The harness notification for the finished run read *completed (exit code 0)*. The run's own log read `PYTEST_EXIT=1`. The notification was reporting the exit status of the backgrounded shell, whose final stage was the `echo` that wrote the `PYTEST_EXIT=1` line, so the statement recording the failure is what reported success. This is the 4th occurrence of a single arithmetic error in this project, and the first on this surface: the previous 3 were shell pipelines whose last stage was a convenience command added for readability. The rule now applied without exception is to read the exit status from the log and never from the notification.

Had the notification been believed, a board carrying 28 failures would have been recorded as green on the day the founder stated explicitly that corners were not to be cut to make it green.

## The comparison against the morning's 44

A comparison tool was run against the 44 node identifiers recorded that morning. It refuses an unfinished log and refuses a run narrower than the collection, because both of those conditions were caught earlier producing a false report of 44 of 44 repaired.

Exact node-identifier comparison: **36 of 44 repaired, 0.818182, Wilson 95% [0.680394, 0.904872], Clopper-Pearson 95% [0.672863, 0.918081]**, with an independent mpmath closed form agreeing with the statsmodels interval to 0. **8 remained red and 20 were new.** With parametrised identifiers normalised the same comparison reads 32 of 41, 0.780488, and both forms are reported rather than either chosen alone, because they answer different questions.

20 new failures is the finding that matters. A second complete board exists precisely to catch a regression introduced by the repairs, and it caught 20.

## The 20 new failures reduced to 6 causes, 5 of them self-inflicted

**First, an outgrown pin.** A guard asserted that a producer prints the substring `of 1421`, the count of distinct messages the founder has written. The producer now prints 1424, because 3 further messages were written on 4 November. The substantive assertion that the producer still reaches the right verdict was unaffected. The repair replaces the pinned value with 3 checks that cannot be outgrown: a floor at 1421 so a reader that collapsed could not pass, live equality against the reader's own count so the figure cannot drift from its mechanism, and a check that de-duplication is still active, measured at 1424 distinct against 2663 raw rows. This was the only member of the 28 inside the commit gate's own list, so it was the only failure blocking a commit.

**Second, a flag that acted.** A mutation harness wrote to 3 tracked files and did not answer `--help`, so the flag ran the measurement, which in that script means editing the repository in order to print usage. The repair adds the project's standard help guard. The same defect had been repaired on a different script earlier the same day, which is the uncomfortable part: the first instance was fixed and a second was shipped.

**Third, an unwired script.** A producer written that morning was reached by nothing: no caller, no citation, no document naming it as a command. Under the project's additive standard an addition that nothing reaches is not additive. The repair is a citation, and this note is where it lands: `scripts/which_completion_claims_the_board_unsupported_2026-11-04.py` is the producer of the completion-claim figures in the final section below.

**Fourth, a deliverable pair reported as divergent when both halves were correct.** A markdown note and its spoken companion differed on 9 of 161 lines. All 9 of them differed only by removed bold markers and backticks, which the spoken standard requires to be absent. The checker stripped heading hashes alone, so it accused 2 correct files. The repair normalises both sides for bold spans and backticks before comparing. The distinction that justifies it is that normalising both sides of a comparison is symmetric, whereas a detector that inspects only the markdown side may not look for a bare backtick, which appears in chemical structure strings in 226 spoken files.

**Fifth, and the largest cluster at 13 of the 20, a shape that read as a missing measurement.** A guard executes every interval helper in the session's producers against the same inputs and requires them to agree. 3 producers returned a different shape from the convention: a dictionary of 8 keys in the first case and a formatted string in the second. The dictionary carried the 2-route disagreement under a key, so the arithmetic was right, but nothing could read it: the guard that executes them raised a key error and the static route detector reported that a quantity stood on a single route. A third producer's second route existed but was written with an exponent operator where the detector looks for a multiplication. The repair installs the project's canonical helper verbatim in all 3 rather than widening the detector, because 14 producers already conformed and the convention was never in doubt.

**Sixth, and this cause was latent rather than introduced.** Installing the canonical helper surfaced a crash in the canonical helper itself. Its second route for the exact binomial interval inverts the regularised incomplete beta function through mpmath, and that function fails to converge for large parameters at mid-range arguments. Measured at the shape parameters 2437 and 17564 it succeeds below 0.1264 and above 0.9 and raises an error in between, which is exactly where a bisection over the unit interval takes its first step. No test could have caught it: the guard that executes every copy uses sample sizes of at most 38, and the failure needs 20,000.

The helper is copied into 16 producers, so hardening some and not others would have gone undetected. All 16 were changed in a single pass and then executed against each other: 16 of 16 loaded, 1 distinct answer per case, worst 2-route disagreement 1.1 times 10 to the power minus 16, and the formerly crashing case now returns an interval matching the scipy quantile to every printed digit. Where the fast route fails, the integral is computed by quadrature in log space instead. That costs about 28 milliseconds per evaluation against microseconds, so it runs only after a failure.

The fixed 240-step bisection then mattered. The bracket halves at every step, so 2 to the power minus 60 is already below the tolerance that double precision can hold, and 180 of the 240 evaluations were redundant. That is free on the fast route and 5 seconds of waste on the slow route. Stopping on precision instead reduced 6.66 seconds to 1.69 for a bound identical to 12 decimal places.

## What a producer said about entry B121, and the correction that was itself corrected

Entry B121 reports that the severity archive counts 1 experimental run twice, through a symbolic link that the producer's file glob follows. The entry carried 5 quantities and named no script, which is the project's measured-rate rule violated inside an entry reporting a measurement defect. A producer now exists and reproduces every figure: **217 severities enter the frame twice out of 3,311, 0.065539, Wilson 95% [0.057603, 0.074482]** with an mpmath closed form agreeing to 6.9 times 10 to the power minus 18, and Clopper-Pearson 95% [0.057345, 0.074510] with scipy's beta quantiles agreeing exactly. The duplicate is exact rather than approximate: the symbolic link's severity multiset is identical to its target's.

The producer first printed that the entry was wrong. The entry says excluding the duplicate turns **both** of the floors installed by 1 named commit red, and the producer measured 3 floors crossing and declared that a correction. Checking the named commit showed it installed exactly 2 floors; the 3rd, which is older, came from an earlier commit. The entry was therefore correct within the scope it named, and the real finding is that the consequence is wider than it stated rather than different from it. Both the producer's closing text and the entry now say that. A measured number refutes a claim only when it shares that claim's denominator.

## A figure withdrawn, because it cannot be reproduced

Entry B120 carried a Fisher exact probability of 1.108513 times 10 to the power minus 11 for the concentration of replies that a 1-character fix changes. No script in the repository produces it and the 2 by 2 table it came from was never recorded. 6 candidate tables consistent with the entry's own prose were tested and none reproduces it: the nearest gives 9.526969 times 10 to the power minus 11 and another gives 2.062114 times 10 to the power minus 13, a factor of 54 in the other direction.

The figure is withdrawn rather than attached to a producer that does not produce it. A producer was then written, `scripts/what_the_backtick_changed_2026-11-04.py`, and the correction it returns is larger than the withdrawal. It takes the pre-fix predicate by deriving it from the live one rather than retyping it, and asserts the derivation changes exactly 1 character. 3 of the entry's figures move. The denominator is 343 rather than 392, counted by the subject module's own walk of 7 named seats across every archived round, and whether the population definition changed or 392 was wrong cannot be settled from the record, so both are stated. The fix gains 7 verdicts rather than 6, and all 7 sit in 4 rounds dated 4 November 2026, so a further round landed after the entry was written. The direction claim holds exactly: 0 verdicts are lost, and the paired table of 7 gained, 0 lost, 205 true under both forms and 131 false under both closes exactly on 343.

And the test named in the entry was the wrong one. A before-and-after verdict on the same replies is a paired design, whereas Fisher's exact test is for 2 independent samples and on a paired table answers a different question with the wrong denominator. The exact test for this is McNemar's, which conditions on the discordant pairs alone. It gives a probability of 1.562500 times 10 to the power minus 2, with scipy's binomial test and an independent mpmath exact tail agreeing to 0, and equal to the closed form 2 divided by 2 to the power 7. Fisher on the unpaired table gives 4.694395 times 10 to the power minus 2. So the withdrawn figure overstated the evidence by about 9 orders of magnitude, and the strongest claim the data supports is 0.015625.

## The 3 completion claims that remain, and whose move they are

The morning board closed with a section naming 24 task entries marked done whose named evidence was failing. That is a larger fact than the 44 failures, because a failing test is a defect while a completed entry resting on a failing test is a claim the record cannot back.

Measured after the period's repairs by `scripts/which_completion_claims_the_board_unsupported_2026-11-04.py`: **21 of 24 restored, 0.875000, Wilson 95% [0.689961, 0.956557], Clopper-Pearson 95% [0.676389, 0.973441]**. The 3 that remain are entries B11, B41 and C29, and all 3 wait on a founder ruling rather than on work.

2 entries rest on a termination condition. The task list's branching ratio now reads **0.9502 with a 95% interval of [0.7869, 1.1475]**, and the upper bound has reached 1, so the list can no longer be said to terminate. The guard reporting this is correct and the founder asked to be told if it happened. The third entry rests on a generated report exceeding the line limits the founder himself set: 616 lines of markdown against a limit of 300, and 673 lines of spoken text against 400.

Neither is repairable without a ruling, and loosening either in order to turn the board green is the move the project's own rules forbid.

## Producers named in this note

- `scripts/which_completion_claims_the_board_unsupported_2026-11-04.py`, the completion-claim figures
- `scripts/the_severity_frame_counts_one_run_twice_2026-11-04.py`, the duplicated-run figures, with guard `bench/tests/test_the_severity_frame_counts_one_run_twice_2026-11-04.py` at 12 tests and mutation harness `scripts/the_severity_frame_mutations_2026-11-04.py` red on 5 of 5
- `scripts/counting_imports_ranks_producers_backwards_2026-11-03.py`, the route analysis, now reporting 0 single-route producers against 3 before
- `scripts/the_boards_44_partitioned_2026-11-04.py`, the instrument and product partition of the morning's 44
- `scripts/precommit_gate_cost_2026-09-10.py`, the gate's share of the collection

Written under CDSFL note standard v1.9.
