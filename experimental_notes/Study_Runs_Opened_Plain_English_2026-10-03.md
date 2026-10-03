# The day the merge was settled and three of the project's own instruments were caught

3 October 2026, 09:40 BST (British Summer Time)

## Summary

A 2 seat standoff over how to repair 3 defects was settled by asking the seats to adjudicate the merge one assertion at a time rather than one fix at a time. Both reached the same decisions independently. Along the way 3 separate instruments belonging to the project were found to be measuring the wrong thing, and in each case the instrument was corrected rather than the result accepted. The first of 3 simulated runs that carry the programme of study is now under way.

## The merge, and why it needed a third round

On 2 October two model seats, referred to here as cc2 and fable, each repaired the same 3 defects in their own private copy of the repository. Neither repair was better than the other in any simple sense. Measured before the third round was dispatched: applying cc2's repair left 8 of fable's own tests failing, applying fable's left 6 of cc2's failing, and a single line of code combining the two moved cc2's failures from 6 to 5 without resolving the disagreement. Reading the two sets of changes side by side could not decide between them, because each was internally consistent.

So the third round asked a different question. Instead of "whose fix wins", it asked "who wins on each individual assertion". Both seats decomposed the disagreement the same way, independently of one another, and reached the same 5 decisions. The most interesting of those is the only genuine composition in the merge: for one defect, the 2 repairs are both necessary, and that was shown by executing all 4 combinations rather than argued. cc2's repair alone leaves a safety blocker reading zero on entries restored from an older checkpoint, because the point in the code where it writes its mark never runs again for them. fable's repair alone leaves the record asserting that a machine tried and failed on a finding that no machine ever reached. Only both together satisfy both properties.

The merge was applied by hand rather than wholesale, because 2 of the files each seat delivered had been edited after their private copies were taken, and copying them in would have silently undone a separate piece of work finished earlier that morning. Verified afterwards on the live repository: all 3 of the seats' own falsifying scripts exit cleanly, 94 tests pass on one side's set, and 43 of the other side's variants pass against the same single set of files.

## Three instruments caught measuring the wrong thing

**A fix that armed a decision the founder had deferred.** One archived finding stood recorded as confirmed and verified, at high severity, on a falsifier that the discrimination control had already voided, with the claim withdrawn by the very model that raised it. The obvious repair was to stop the record claiming verification. That repair looked free, because the convergence machinery does not read the field in question. It was not free. The project's own committed test says in its own words that withholding that field is what keeps a finding from closing, so the repair had quietly armed a blocking behaviour whose arming the founder had deliberately deferred, on his own measurement that 126 of 246 fixes fail to silence their own falsifier. Two committed tests went red and named it. The repair was withdrawn. What shipped instead records that the verification was voided, with a reason, read by no decision at all, so the contradiction is visible and the decision stays where it belongs.

**A cost estimate wrong by a factor of 68.** A new guard was built to extend the discrimination control to the falsifiers it cannot currently reach, by synthesising the comparison it normally needs supplied. It was first wired to run inside every round, on a projected cost of 1.4 minutes per experiment. That projection came from timing the probe against a directory holding a single file. Timed against the real repository, one setup step costs 14.034 seconds, because the sandbox machinery recursively scans the copy for anything that should not have been copied. Inline, that is roughly 187 minutes added to every run, for a statistic that nothing in the convergence path reads. It now runs once per distinct falsifier after a run finishes, where it cannot slow or disturb what it measures. Before the cost was even the question, the same guard was simply unreachable: the function it had been added to is never called in the case it was written for, which was found by measuring that the stamp it would leave appears zero times across the whole archive.

**A ratchet that fired on obedience.** A guard that watches for panel evidence being left where no one can retrieve it reported 8 stranded files. All 8 were scratch files, which the founder ruled stay unpreserved and which the preservation mechanism deliberately skips. The rescue tool could never have cleared the alarm, because the rescue tool honours the same ruling. The guard was counting compliance as a regression. Its rule now comes from the preservation mechanism itself rather than a second copy of the rule that can drift away from it.

## The desktop alert, proven rather than claimed

The founder reported that a compaction alert in the operating system's notifications had never worked. That was correct: no hook emitted one at all. The repair was written, and then nearly lost, because editing the installed copy broke the link to the committed copy and left the repository with none of it. Both are relinked, every hook is now guarded against that specific drift by name rather than by count, and the guard runs the committed hook with a stand in for the notification tool and reads what the hook genuinely tried to execute. It fires, the text tells the founder to issue the recovery command, and a second run over the same event stays silent, so the alert cannot become 42 banners that get muted within the hour.

## The board

The full test suite ran on a frozen repository: 23 failed, 9868 passed, 9 skipped, in 3259.81 seconds. Every one of the 23 was caused by the day's own work, and all were repaired at the root. Two of them were not defects at all: the reachability guard reads the list of files known to version control, so a test written minutes earlier cannot yet vouch for the script it tests.

## The repointing experiment

The founder approved an experiment asking whether archived falsifiers are specific to the file they were written for. It has 2 arms: one replays the script unedited, to measure how much simply decays over time, and one points it at a different file of the same kind. The control arm is what makes the treatment arm readable, and without it decay and generality cannot be told apart.

The experiment's own entry condition was the first thing it found. It initially reported 203 of 233 scripts failing, 87.1245 per cent, which tripped its own stopping rule and would have decided nothing. The cause was the condition, not the archive: most of those file names are not written relative to the repository at all, but relative to the temporary directory the script ran in, or are bare file names with no directory. Counting those as missing files confuses decay, which is what the control arm measures, with a path that was never repository relative and means nothing either way. Correcting it took 3 measurements, including one that looked worse until the duplicate hits turned out to be the same file inside 3 agent working copies.

The result, over the corrected population of 143 scripts of which 56 produced a scorable pair: the unedited arm confirms 54 of 56, 96.4286 per cent, and the repointed arm confirms 49 of 56, 87.5 per cent. The Fisher exact test gives a 2 sided p value of 0.1617149, against a pre-registered threshold of 0.01, so the 2 arms cannot be separated at this sample size. The second hypothesis, that the repointed rate falls inside the unedited arm's confidence interval, also fails, by 0.38 of a percentage point.

Neither pre-registered hypothesis is supported, and the figure worth carrying forward sits underneath the test: 49 of 56 archived falsifiers still report a defect when pointed at a file they were never written for. That is the generality concern made concrete rather than asserted, and it is exactly the population the new post-run sweep exists to examine on live runs.

## What is running now

The first of 3 simulated runs started at 09:35:20 on the prose target, 8 rounds at most, with 6 simulated seats. The scoring keys were verified sealed before anything ran, the panel is confined to a disposable copy of the repository, and the fix admission gates are restricted to vetoing on a prose target, meaning they can reject a repair that damages a quoted listing but can never approve one. A monitor polls the run every 60 seconds and treats a dead process or a log that stops growing as events in their own right, so silence cannot be mistaken for health. A terminal window on the founder's own machine follows the run's full output.

Written under CDSFL note standard v1.7 (26 August 2026).
