# CDSFL closing report, 2026-09-11


## What This Covers

A single morning's work, from 05:00 to 10:05. The starting point was a task entry marked complete, A2, whose claim was that anyone who clones the repository and runs the test suite sees the same result the maintainer sees. That claim turned out to be false, and everything below follows from establishing why.

## The Headline, Stated Plainly

A2 said a fresh clone runs green. It did not. Cloning the repository at its current commit and running the full suite there gave 3 failures against 6952 passes, while the same suite in the maintainer's own working copy gave 6988 passes and 0 failures. The claim had been wrong for 2 days and nothing in the project could have noticed, because nothing in the project performed a clone at all.

Both of the instruments A2 declared as its evidence were sound, were about the right subject, and could not see the claim. One of them guards the individual repairs and clones nothing. The other re-runs the named tests in the maintainer's own checkout, which is the tree whose greenness was never in doubt. A script that actually performs the clone now exists, and a test runs it end to end on 1 fast test file so that a clone-and-run script nobody has executed cannot sit in the tree unnoticed.

## The Cause, Which Is Small And Was Invisible

A commit-time guard sees the staged snapshot of a change, not the working files. The repairs that run before each commit, which fix stale line references and refresh a derived ledger, wrote their corrections to the working files and never added those corrections to the commit. So every commit shipped the unrepaired version, and the repair sat waiting to be swept into the next commit. The repairs were permanently 1 commit behind. In the maintainer's own copy everything looked correct; in any fresh copy it was broken. The only visible symptom was that git reported some files as modified, which is unremarkable.

## The Probe That Proved The Fix Also Broke Something

To prove the repair now reaches the commit, 1 line reference in the master task list was deliberately made wrong and a commit was allowed to run. The repair landed, which is what the test was for. It also destroyed 3 correct line references in the same pass, because the repair replaced text by simple substitution with no boundary, so a short number rewrote the beginning of every longer one. Those 3 wrong references reached the permanent record and were restored. The repair now edits at the exact position it already computed, rather than searching for the text again.

## A Class Of Script That Never Answered A Request For Help

A survey in the project runs every measurement script with the standard request for usage information and counts how many answer cleanly. It decided that on the exit code alone. A script with no argument handling does not answer at all: it ignores the request, runs its entire measurement, and finishes successfully, which an exit code cannot distinguish from an answer.

Requiring a usage line instead: 30 of 53 measurement scripts did not answer, 56.6038 percent, with a 95 percent Wilson interval of 43.2654 to 69.0496 percent. 2 of those 30 were among the 3 failures in the clone, because the work they silently did happens to need files a clone does not carry. The figure is now 0 of 54.

## The Review Panel Found 5 Defects In Those Fixes

Two reviewing models were dispatched, both on the existing subscription, with no paid dispatch. They found 5 distinct defects, 3 of them independently of each other, which is 60 percent agreement with a 95 percent Wilson interval of 23.0724 to 88.2379 percent. One model found nothing the other missed; the other found 2 more.

The most serious was that adding a repaired file to a commit adds the whole file, so a repair sweeps in changes the author had deliberately held back. Both models proposed a fix and they proposed different mechanisms. That disagreement was settled by measurement rather than by argument: with the repair 1 line away from the withheld change, one mechanism conflicts and the other succeeds with the withheld change correctly excluded. The second was adopted. Where both fail, which is when the repair and the withheld change touch the same line, the commit now refuses and says so, because there is no right answer without asking.

## The Entire External Review Record Was Nearly Unrecoverable

The project's standing instruction is that review output from other models must be preserved in full and unfiltered, and never summarised in place of the full output. That output is written to a directory the version control system is configured to ignore.

Measured: 78 directories hold a review record. 64 of them, 82.0513 percent with a 95 percent Wilson interval of 72.0976 to 88.9961 percent, existed on 1 machine and in no commit. Of the 14 that would survive a copy of the repository, not 1 is a round run under the current review condition. None was partially preserved, which is the single good thing in that measurement, because a half-preserved record looks complete and is not.

All 78 are now copied into the tracked part of the repository, 364 files, each one checked against its original by cryptographic hash. Every review round run under the current condition now also has a readable full record note, with each model's reply reproduced word for word.

## A Cost Figure That Undercounted By A Factor Of 3

Spending on paid model seats is reserved to the founder. The instrument reporting it printed 10 paid replies, described as covering every round. It was searching only directories whose names begin with a particular prefix, which is 46 of the 78. Worse, it decided whether a reply was paid by reading a field inside the reply, and treated a missing field as free. 20 of the 30 paid-seat replies in the record have no such field at all, 66.6667 percent with a 95 percent Wilson interval of 48.7801 to 80.7695 percent, all from an older tool that did not write it.

The real count is 30, not 10. The conclusion is unchanged and is now measured across the whole record: the most recent paid dispatch was on 5 September, and 0 of the 24 rounds since then involved one.

The guard that asserts this was blind in the same 2 ways, which matters more than the figure. A paid reply planted in a differently named directory was demonstrated to pass the old guard, both with and without the route field. It is caught now.

## The Recurring Shape Of The Whole Morning

Nearly every defect above is the same shape: an instrument that recognises 1 form of a thing and reports a confident zero for the other. A search that required a leading absolute path and missed the same path built a different way. A selector that matched a naming convention adopted yesterday and reported 100 percent coverage while covering 15 percent. A tally that read a missing field as the safe value, turning 30 paid replies into 10. A comparison that searched only the first 4000 characters of each document. A check keyed to a field name the brief had since renamed, which reported 42.8571 percent compliance where the true figure is 92.8571 percent, and would have shown the review panel abandoning a founder condition it was in fact still meeting.

Each was caught, and several were caught only because a control was written that could fail. The cost of the shape is that it always reports the reassuring answer.

## What Remains Open

2 items, and both are decisions rather than work.

The first concerns evidence cited in notes that lives in the ignored directory. That question is now much smaller than it was. 20 of the 23 cited paths have a preserved copy, 86.9565 percent with a 95 percent Wilson interval of 67.8725 to 95.4623 percent. The remaining 3 name log files for an experiment that has never been run, so they are citations to a future artefact rather than lost evidence. What is left to decide is whether to repoint 20 citations at their copies. The recommendation is to leave them, because a note records where an artefact was produced, and a tool now exists that takes a reader from the citation to the copy.

The second is a design point about the admissibility gate and prose documents. The switch, which lets the admissibility gate read the runnable code fragments inside a prose document instead of the prose around them, is built, tested, and off by default. Turning it on changes what reaches a verdict, which is a founder decision. One fact bears on it directly: with the switch on, the project's own archived exploit still scores 1.0000 and fully admissible, identical to a correct fix, because the security scanner rates that particular construction as low severity and the gate counts only high and medium severities. The switch repairs what the gates read, not how strictly they judge.

## Two Things Recorded Honestly Rather Than Closed

A test in the suite has now failed twice in 5 full-size runs, both times in a fresh copy of the repository, and passes in the maintainer's copy, in isolation, and in a partial run. Reading the source produced no mechanism, and inventing one would be exactly the habit this project exists to avoid. Its failure message now prints the internal state a diagnosis would need, so the next occurrence explains itself. A full run is under way to try to catch it.

The Wolfram licence observation, which was deliberately deferred to today, was made at 09:37. The licence file has not been rewritten and the expiry date has not moved: it is today. The engine still computes correctly, verified on 2 known results that match independent tools exactly. So nothing is broken, and the founder's reading, that renewal happens close to the expiry date, is not contradicted at 09:37 on that date. The question becomes real only if the date has still not moved once today has passed.

## The State Of The Work List

92 entries. 81 complete, 2 open, 4 blocked on the founder, 1 deferred, 4 withdrawn.

Written under CDSFL note standard v1.7 (26 August 2026).