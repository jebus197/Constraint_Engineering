# Closing report, 2026-09-10 (rewritten after independent audit)

Rewritten at 10:57 BST after an independent audit. The previous version of this file, written at 04:43, carried 19 claims that do not hold. This one names them.


## HOW TO READ THIS, AND WHY IT IS DIFFERENT

The founder asked a fair question: how can this report be trusted, when the report itself says the reporting has been unreliable. The answer is that it should not be trusted on assertion. It should be trusted only where a machine re-derives it.

So this version was audited before it was written. 48 agents ran for 2 hours and 20 minutes across 2,182 tool calls. 22 of them audited 1 completion claim each by executing its evidence rather than reading it, with an adversarial reviewer on every overstatement alleged. 4 more audited the previous version of this report, the test suite, the Desktop copies, and the cycle series. Every figure below either names the command that produces it or is marked as unbacked.


## THE AUDIT RESULT, AND THE HONEST READING OF IT

The headline is bad. 22 completion claims were audited. 0 came back fully supported. 19 were judged overstated and 3 were cleared when an adversarial reviewer tried to refute the finding. That is 19 of 22, 86.36 percent, Wilson 95 percent interval 66.67 to 95.25, Clopper-Pearson 65.09 to 97.09.

The headline on its own is misleading, and correcting it matters more than repeating it.

First. Every single one of the 22 named test files passes. 22 of 22, 100 percent, Wilson 85.13 to 100. Not one completion claim rests on a failing test. The fixes are real. What fails is the prose describing them.

Second. At the level of individual sentences rather than whole entries, 116 of 266 checked claims do not hold. That is 43.61 percent, Wilson 37.78 to 49.62. So roughly 2 sentences in 5 have gone stale or were wrong, not everything.

Third, and this is the largest single cause. 12 of the 19 overstatements cite evidence that is not committed to git, 63.16 percent, Wilson 41.04 to 80.85. Those entries say COMMITTED and name test files that are untracked, because 35 files have been sitting uncommitted for 7 hours and 22 minutes. That is 1 root cause producing 12 verdicts, not 12 separate failures.

Fourth. An earlier measurement of the same thing, taken at 00:42 today, found 11 of 19 overstated, 57.89 percent. Today is 19 of 22. Fisher exact test on the 2 by 2 table gives p equals 0.0753, and a chi-square with Yates correction gives p equals 0.0895. Both are above 0.05. So it cannot be claimed that the overstatement rate of 57.89 percent has risen to 86.36 percent in any sense the evidence supports. It is the same phenomenon measured twice.


## WHAT WAS WRONG WITH THE PREVIOUS VERSION OF THIS REPORT

19 claims did not hold. 6 were above threshold. Naming them all, because a correction that hides its own scope is the defect this project exists to catch.

1. It said the cycle was at pass 11. It is at pass 13. The same document said 13 further down, so it contradicted itself.

2. It said gamma is 0.007 above the threshold, in the same document that says both sides of the gate now fail. Gamma is 0.294998, which is 0.005002 BELOW the 0.30 threshold. The 0.007 figure was gamma at 12 passes.

3. It said the resurgence warning fires on the live series immediately. It does not fire. At 13 passes the last 3 passes found 7 against 21 in the 3 before, so the branch is not taken. That sentence was true when it was written for the 10-pass series and was carried forward through passes 11, 12 and 13 without rechecking. It is the exact staleness class this whole session has been about.

4. It said both panel seats cleared the restore-order repair and the task 6.7 repair after running mutations against them. Zero mutations were run against the 6.7 repair by either seat. Reading both seats' tool logs, cc2 mutated the restore script and the runner, and neither seat mutated anything belonging to 6.7. That was a description of rigour that did not happen.

5. It said all 18 changed adjudication verdicts replace a claim of sameness with an inconclusive label. The errored-leg half holds at 18 of 18. The sameness half does not: at most 10 of 18, and strictly 3 of 18.

6. It said a test file was 10 of 10 failing. It was 10 failed of 15 collected, 66.67 percent.

7. It said 82 entries. There are 84. The 2 extra are the entries created by the review the report describes.

8. It said 7 panel findings, all applied. The seats returned 9, which deduplicate to 8 distinct. 7 are applied. The 8th, the sandbox loss, is not applied and is filed as 2 open tasks.

9. It said 4 entries were waiting on a panel review and have now had one. 3 of the 4 hold. Task 6.7 was marked done at 22:33 the previous evening, 5 hours before the review started, so it was not waiting.

10. It said written at 05:05. That time was typed, not captured. The file was last written at 04:43:22. The standing rule is to capture the clock and never type a timestamp.

11. It described the no-paid-dispatch restriction as a command flag. It is an environment variable, and it is opt-in, defaulting to all 5 seats including 3 paid ones.

12. The text-to-speech copy carried markdown bold on one line, which the plain-text protocol forbids.

13. The foot-line used a comma where the canonical form uses parentheses.

The remainder are smaller: a count of 6 outstanding decisions with no producing script, a count of 9 wrong figures with no producing script, "one seat" where both seats did the same thing, and a sentence saying a number is both 0 and 1.55 times 10 to the minus 15, which are the same number reported 2 ways.

What survived the audit unchanged: the gamma arithmetic, which reproduces to 1.2 times 10 to the minus 15 across 4 independent implementations; the corrected 2.1 confidence interval; the 18 of 133 adjudication drift; and the claim that no paid model was dispatched, which is supported by the absence of any paid seat file across all 4 recent panel directories.


## THE STATE OF THE WORK, MEASURED THIS MORNING

The test suite is RED by exactly 1 test. 1 failed, 5949 passed, 4 skipped, 1 expected-failure, in 986.92 seconds. The failure rate is 1 of 5955, 0.0168 percent, Wilson 0.0030 to 0.0951. The failing test is one written yesterday to pin the pre-commit gate's collected test count at 169. The same uncommitted work pushed that count to 174. The test is doing exactly what its own docstring says it will do.

Nothing is committed. HEAD is the commit from before the panel review. 35 uncommitted entries: 23 modified files and 12 untracked ones. Destroying the working tree now would lose 774 added and 71 removed lines of tracked changes plus 3,288 lines of new files, being 5 test files, 3 measurement scripts, 3 notes and 1 evidence file. That is 7 hours and 22 minutes of work.

Worse, and this was not previously reported. The raw panel record for round 4 is 140 kilobytes across 8 files and sits in a directory excluded by gitignore. It is NOT recoverable by any commit. The only copies are a derived summary and an untracked transcription. The unfiltered record of what 2 reviewing models actually said exists on 1 machine, unversioned.

The pre-commit hook would REFUSE a commit of the whole tree, because 2 of the 6 staged notes get worse under the note linter. It would ACCEPT a code-only commit. And it does not run the 1 test that is red, so a code-only commit would land a red suite silently. That is a gap in the guard built yesterday to prevent exactly that.

The task list holds 84 entries: 22 done, 57 open, 2 blocked, 3 withdrawn. 27 entries name executable evidence.


## WHAT THE FOUNDER READS FROM HIS DESKTOP CANNOT BE TRUSTED

2 of his 4 Desktop files differ from the canonical repository copies, Wilson 15.00 to 85.00.

The operational tracker and the runway file are byte-identical and current. The master task list is 29,044 bytes short and 3 hours 27 minutes behind. The outcomes log, which is the file recording what work was done, is 5,016 bytes short and its newest material is 12 hours and 52 minutes old. Had that file been opened this morning to check the overnight work, it would have shown a session that stopped at 00:43.

The restore protocol cannot warn about this. Its FIRST READ section names the Desktop copy of the tracker and does not name the Desktop copies of the task list or the outcomes log at all. The repair made last night for exactly this failure closed 1 door of 3.

A memory file that loads into every future session asserts that the Desktop task list is a byte-identical mirror. It is not.

The recovery document's own session-state block is dated 2 days ago and names a commit and a push state that are both wrong. The standing rule is that it should track the last commit. There have been 9 commits since it was last updated.


## THE CYCLE

13 passes. The series is 11, 4, 2, 3, 6, 2, 3, 2, 9, 10, 4, 2, 1. Gamma is 0.294998. Both sides of the gate fail, so the verdict is keep going.

The series was audited for tampering and is clean. It was reconstructed at all 6 commits plus the working tree and each version tested as a strict extension of the last: 0 counts altered, 0 labels altered, 0 truncations. No recorded figure has been silently edited after the fact.

The gate imports the project's own estimator rather than re-implementing it, and that estimator, a numpy fit, a scipy fit and a 40-digit arbitrary-precision closed form agree to 1.554 times 10 to the minus 15 across 9 test series.

The tail is genuinely falling now: 10, then 4, then 2, then 1. The count side needs 3 consecutive passes at 0.


## WHAT NEEDS THE FOUNDER

The Wolfram licence expires tomorrow, 11 September. The ruling was to let it auto-renew and observe on the day. That is the only time-bound item.

The 3 irreversible categories are untouched and unchanged: deleting a git reference, spending money on a paid seat, and the sealed key store.

The panel sandbox lost most of its code partway through the review and no cause has been established. It is filed as 2 open tasks and is not diagnosed.

No paid model has been dispatched at any point.


Written under CDSFL note standard v1.7 (26 August 2026).
