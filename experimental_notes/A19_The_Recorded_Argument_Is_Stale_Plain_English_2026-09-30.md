# A19, and why the recorded argument for leaving it off no longer holds

> **Plain-English companion.** The spoken version is `~/Desktop/CDSFL_tts/A19_The_Recorded_Argument_Is_Stale_2026-09-30.txt`
> and the engineer-facing version, with file paths, line numbers and commands, is
> `A19_The_Recorded_Argument_Is_Stale_2026-09-30.md`. Content mirrors the spoken version.

Constraint Engineering project. 2026-09-30, 12:20 BST. Prepared for the founder's ruling on task A19.


## What this document is for

There is 1 decision waiting on the founder, task A19, and it has been waiting since 2026-09-11. This document explains what the decision is, what the record says about it, and what an independent review of that record found on 2026-09-30. The short version is that the strongest argument the project had written down for deciding 1 way has gone out of date, because the code changed 11 days after the argument was measured, and nobody re-measured it until now.


## What A19 actually asks

The project has a scorer that grades a proposed fix before it is accepted. The scorer was built for Python source files. When the file under review is a written document rather than a program, the scorer declines to grade it and returns a verdict of "no score", which means "this instrument has no opinion", not "this fix is bad".

The founder's design point, made on 2026-09-10, was that declining entirely is too crude. A written specification often contains code samples inside it. Those samples are computationally reducible, which simply means a machine can check them. His words were that a purely prose input should be marked inadmissible while still solving any computationally reducible elements within that prose, because this is a science and engineering project and nobody will be using it to write poetry.

A switch to do exactly that was built and wired up, and it is called sk_score_prose_listings. It is off by default. Turning it on changes which fixes reach a verdict, and that is why it was left as the founder's call rather than the assistant's. A19 is the decision to turn it on or leave it off.


## Why it was left off, as recorded

The master task list carries a paragraph headed as the decisive fact for the ruling. It says that with the switch turned on, this project's own archived exploit is still admitted at a perfect score of 1.0000. The exploit in question is a real one that cost a discarded experimental run: a fix that smuggled a destructive shell command into a code sample inside a document. The entry then concludes, in its own words, that this is the strongest argument for leaving the switch off.

The reasoning behind that was specific and it was correct at the time. The security scanner used by the project assigns LOW severity to a destructive shell command written as a plain text string. The gate that reads the scanner looks only at HIGH and MEDIUM findings. So the gate never sees the exploit. The entry also states that 1 new HIGH severity finding is not enough to cause a rejection, and that 2 are needed.

That measurement was taken on 2026-09-11.


## What changed, and why nobody noticed

On 2026-09-22, 11 days later, a separate repair was made to the same scoring path. It added what the code calls a 1 sided veto. The rule is simple: when the target is a written document and the scorer is about to return an admissible verdict, the code checks whether the fix introduced any new defect at all, and if it did, the verdict becomes rejected and the score is forced to 0.

Re-run today against the same committed test fixture, the archived exploit returns "no score" at a score of 0. It is not admitted at 1.0000. And the companion sentence is also now false: 1 new HIGH severity finding is enough to reject, not 2. Injecting 1, 2, 5 and 20 new HIGH findings into a code sample was rejected on all 4 attempts, 4 of 4, with a 95 per cent confidence interval from 51.0109 per cent to 100 per cent. A single new lint diagnostic, which is a far milder complaint than a security finding, is also enough to reject.

So the decisive fact recorded for the ruling is stale. The behaviour it describes was changed 11 days after it was written, and the entry was never updated. This matters because the entry is what the founder would read in order to rule.


## A separate defect, found the same day, and how it was got wrong first

While reading the A19 entry against the code it rules on, the assistant found a genuine defect and then drew the wrong conclusion from it. Both halves are worth recording, because the wrong conclusion was corrected by execution rather than by argument.

The defect is real. The scorer has 4 component gates. 1 of them, called the regression gate, runs the project's test suite and asks whether the fix broke anything. The scorer's own documentation states that this gate is permanently unavailable on a written document, for 2 reasons: that such targets live outside the repository, and that no configuration sets a test command for them. Both halves of that sentence are false for the run that actually tested it. The document under review, a build specification, is inside the repository. And a test command is set, not by the configuration but by the command line parser, which substitutes its own default when the configuration passes nothing. The default is a test suite belonging to an entirely unrelated Python file.

The consequence is that on a written document the regression gate runs the wrong test suite and returns the same number every time: 52 out of 55 tests passing, which is 0.9454545454545454. It is not measuring the fix at all. The clearest demonstration is this: destroying the document's contents entirely leaves that number unchanged, while doing the same to a Python target correctly returns no score. The gate cannot see its own target.

The assistant's conclusion from that was that no number of new security findings could ever cause a rejection. That conclusion is false, and 4 of the 5 independent checks said so. The error was a mechanism error rather than an arithmetic one. Every number in the calculation reproduced exactly, in 3 separate mathematical tools. But the calculation described the wrong path. On a Python target the weighted average of the gates does decide the outcome. On a written document the 1 sided veto intercepts first, and the weighted average decides nothing. The assistant had also reversed the direction of the risk, hunting for a gate that lets harm through when the gate in question cannot admit anything at all.


## What the corrupted gate actually costs

Because the veto decides the outcome, the corrupted regression gate does not change any machine verdict on a written document. That was established by execution: 7 different values for the regression gate and 4 for another gate all produced 1 outcome, and removing the gate's record entirely changed nothing, while removing either of the 2 gates the veto does read changed the result immediately. No archived fix on a written target was ever admitted: 0 of 8 deduplicated records, with a 95 per cent Wilson interval from 0 per cent to 32.4408 per cent and a Clopper Pearson interval from 0 per cent to 36.9417 per cent.

The cost is to human readers rather than to the machine. When the scorer returns "no score", it deliberately records what the gates would have said, as an advisory number, so that a person reviewing the decision can see it. That advisory number is built from the corrupted gate. It reads 1.0 when the correct test suite is used and 0.9782 when the substituted default is used. The archive holds 2 such records carrying 0.9782, which is a near perfect advisory score computed entirely from an unrelated test suite run against a markdown specification. Anyone reading those records would reasonably conclude the fix had been checked thoroughly. It had not been checked at all.


## The more serious finding, on the path where the arithmetic does decide

The adversarial review pointed out an omission that matters more than the defect that prompted it. There is a 4th gate, called the fix efficacy gate, which is the only 1 that asks whether the fix actually worked. On a Python target, where the weighted average genuinely does decide, a fix measured as not curing its own falsifier still scores 5 sevenths, which is 0.7142857142857143, is recorded as admissible, and lowers the project's running risk estimate from 0.5 to 0.495688. In plain terms, a fix that demonstrably does not work still buys a reduction in recorded risk.

3 tools agree the value is exactly 5 sevenths, and because that is greater than 0, and the verdict is admissible whenever the score is above 0, no finite weight on that gate can ever let it veto. The archive holds 73 such records and all 73 are admissible, 73 of 73, with a 95 per cent interval from 95.0008 per cent to 100 per cent.

This is reproduction rather than discovery. The project's own record already notes it, and already records why it was not fixed: changing the weights would change which fixes are admitted on every Python target ever run. So it is a known hole, not an unnoticed 1. But it sits on the path where the arithmetic really does govern, and the assistant spent its effort on the path where it does not.


## An asymmetry offered as a question

The problem that the 1 sided veto was built to solve on written documents is the same problem that stops the fix efficacy gate from vetoing on Python targets: a hard negative signal dissolved into a weighted average, with no threshold beneath which a verdict is refused. 1 path received a veto. The other did not. The reason the other did not is recorded and is a real cost, namely that every Python verdict ever taken would change. This is raised as a question for the founder rather than as a finding.


3 COUNTING ERRORS, ALL THE SAME SHAPE, ALL IN 1 DAY

The assistant's own figures about how often the corrupted number appears were wrong twice, and the cause is worth stating because it recurred 3 times on 2026-09-30 in 3 different places.

The archive records each score more than once and at more than 1 precision. It also holds verbatim copies of complete run logs, nested inside the working copies made for review panels, 2 levels deep. A scan that takes the first directory name as the run therefore treats those copies as independent observations and files them under the wrong target. Resolved properly, 1066 raw matches collapse to 17 distinct records: 11 legitimate, on the Python file whose test suite it is, and 6 contaminated, on the written document. The assistant reported 50 of 50 for 1 run where the correct figure is 84 of 84, and reported 593 of a further 643 where 593 plus 50 is exactly 643, so the same records were counted twice.

The same shape appeared twice more the same morning. A version control rule meant to preserve run reports was also un-ignoring the review copies of those reports, so 20 duplicate files were versioned while 88 unique review scripts were not. And the project's archive counter was reading review copies as archive records, which inflated a published figure by 14.8359 per cent. In all 3 cases the fault is identical: a copy counted as an original. The reviewing agent fell into the same trap twice itself and recorded a retraction of its own first conclusion, which is the correct handling.


## What is not claimed

The regression gate is not broken everywhere. It varies with its input in 17 of 41 runs, with a 95 per cent interval from 27.7565 per cent to 56.6329 per cent. The failure is specific to written documents, where the substituted test suite has no relationship to the target.

Nothing here establishes that turning the switch on is safe. It establishes that the specific argument recorded against turning it on is no longer accurate.

The 52 out of 55 figure is itself an artefact with a known cause: the test suite is run inside a copy of the repository that deliberately excludes the logs directory, and 3 tests fail because of that exclusion. It is not a signal about anything.


## The decisions waiting

First, and this is the immediate 1: whether to turn the prose scoring switch on. The recorded argument against it has expired. The behaviour now is that a fix introducing any new defect into a code sample is rejected, and a fix introducing none returns no score. It cannot return admissible at all. Whether that is the desired behaviour is a design question, not a measurement question, and it is the founder's.

Second, whether the documentation sentence that is false on both halves should be corrected now or as part of a wider repair, and whether the command line parser should be changed so that passing no test command means no gate rather than a substituted default. That substitution is what made a gate grade a document it cannot read.

Third, whether the fix efficacy gate should be allowed to veto on Python targets, accepting that every past Python verdict would shift, or left as it is with the limitation documented.

Fourth, whether the advisory number preserved for human readers should be suppressed when the gate behind it did not read the target, since at present it reads as a near perfect 0.9782 on a document nothing examined.


## What was done today, for the record

A formal simulation branch was created and pushed, so results from simulated runs are saved without touching the canonical branch. The canonical branch received exactly 1 file, a correction to a Wolfram attribution that the founder authorised crossing, committed with a deliberate 1 time bypass of a records guard that cannot be satisfied from a simulation branch. No other change crossed.

A full test suite run was started and then invalidated by the assistant editing, mid run, documents that the suite reads. It was stopped at 48 per cent rather than reasoned about, because the project's record already contains an instance where 4 of 5 failures were artefacts of exactly that mistake. A clean run is owed and has not yet been taken. The only measured claim about the current state is that the commit gate's 501 fast checks pass.

Every figure in this document was computed twice with independent tools, and the 2 results agree to 1 part in 10 to the power of 16 or better in all cases.
