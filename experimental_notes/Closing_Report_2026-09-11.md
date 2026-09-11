# CDSFL closing report, 2026-09-11


## What This Covers

A single day's work, from 05:00 to 13:11. The sections up to and including "Two Things Recorded Honestly Rather Than Closed" were written at 10:05 and cover the morning; the afternoon sections were added later and correct 2 of the morning's own figures where they had been measured wrongly. The starting point was a task entry marked complete, A2, whose claim was that anyone who clones the repository and runs the test suite sees the same result the maintainer sees. That claim turned out to be false, and everything below follows from establishing why.

## The Result, Measured At The End Of The Day

A fresh copy of the repository now runs the complete test suite green: 7,237 tests passed, 52 skipped, 1 expected failure, nothing failed, and pytest exited with code 0.

That is the claim task A2 had been making. It is the first time it has been true. It was asserted on 10 September and again on 11 September and was false both times, and on each occasion it was discovered by somebody actually making a copy rather than by anything in the project. The script that makes the copy and runs the suite is committed, so the claim is now reproducible rather than asserted.

Getting there took the whole day, and the last three failures were one defect wearing three different sets of clothes. A copy whose folder is called "clone" could not recognise itself, because identity was decided by the folder's name. A request for help ran a script's ordinary work and destroyed a verbatim record, because the flag fell through to the work. And guarding the flag closed only one of two doors: the suite also inspects scripts by importing them, and the work ran on import.

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

## The Afternoon: A Second Review Panel Broke 2 Of The Morning's 5 Fixes

The same 2 models were asked to attack the 5 repairs written that morning, with instructions to deliver working fixes rather than a list of problems. Both returned a split verdict. Both confirmed 2 repairs closed the holes they named. Both found a third bypassable, and both picked out the same bypass as the sharpest finding. Neither softened its disagreement to match the other.

Every finding was reproduced here before anything was changed, because a repair proposed by another model is a hypothesis until it has been run, exactly as one written locally is. All 8 defects were confirmed and none was refuted. One attack the briefing itself invited turned out to be wrong, and is recorded as refuted.

## A Guard That Switched Itself Off

The guard written that morning to stop a throwaway copy overwriting the founder's files began by asking whether the folder it was about to write belonged to the current user. If it did not, the guard concluded a rehearsal was in progress and allowed everything.

That question has a wrong answer under one common circumstance. When a command runs with elevated privileges, this operating system keeps the original home folder setting while changing the numeric identity of the user. The guard then looked up the wrong folder, found a mismatch, concluded rehearsal, and skipped both of its remaining checks. It disabled itself precisely on the most privileged kind of run there is, and it did so in the permissive direction, which is the one that lets a throwaway copy through.

Two further ways round followed from the same design. A copy living outside the usual scratch area satisfied neither remaining check and reproduced the original accident exactly. And when one environment setting is absent, the scratch area resolves elsewhere, so a copy in the usual place escaped entirely.

The decision now depends only on values handed to it rather than on the surrounding environment, which is what made all 3 failing cases reachable by a test at all. A marker file now records which single copy of the project may write those files. All 4 behaviours were verified end to end after committing: a copy in the scratch area is refused, a copy elsewhere is refused by name, a copy cannot register itself, and the founder's own checkout still refreshes normally.

One rule was adopted from a model's proposal over anything written here, because it is better. Before any file is replaced, the bytes about to be overwritten are kept. It is the only rule in the guard that is about content rather than location, which is exactly why it is right in every case a location rule gets wrong, and every hole found so far has been a location the rules did not anticipate. It turns the one remaining gap from silent loss into something recoverable.

## Counting Is Not The Same As Knowing The Order

The verbatim-region exemption, which lets a review record be stored without editing what a model said, marks passages and exempts them from the writing checker. A check written that morning compared the number of opening marks with the number of closing ones.

Both models showed that comparison answers the wrong question. A closing mark that closes nothing, followed by an opening mark that nothing closes, gives one of each: the totals match while a passage is genuinely left open and everything after it silently stops being checked. Worse, a closing and an opening mark inside the same paragraph ended the exemption rather than restarting it, so a model's quoted words were then checked as though they were the project's own writing. That is the precise outcome the exemption exists to prevent.

The repair reads the marks in the order they appear. Across all 402 notes the change alters the result for none of them, so it adds no new complaints about existing documents.

## The Class-Level Answer The Briefing Asked For

Fixing this defect one instance at a time has a 15-for-15 record of not preventing the 16th, so the briefing asked for a mechanical check that catches the class. Both models built one, and the method is the same: take a checking tool and an input it says yes about, change the form of that input without changing its meaning, and require the answer not to change. No reading of any pattern is involved, which is the point.

It is now in the project, running against 6 real checking tools across 29 different form changes, and it reports no undeclared failures. Re-introducing that morning's anchored pattern makes it report the problem on 3 separate form changes at once.

## Two Findings Against Work Done Hours Earlier

A safety check written that morning failed in every throwaway copy made in the usual scratch area, which is exactly where the reproducibility harness makes its copies. It had also been contaminating a separate record of intermittent failures sitting beside it, because 6 of the 8 recorded runs are such copies.

And a test written to prove a rule was asymmetric left a deliberately broken version of that rule alive. It covered 3 of the 4 cases in the table, and the missing case was the one the broken version changed. Three quarters of a decision table is not a decision table.

## The Intermittent Failure Finally Reproduced, And The Harness Threw The Evidence Away

The intermittent test failure that has been recorded as observed rather than diagnosed for several days occurred again, in a throwaway copy, for the first time since extra diagnostic information was added to it for exactly that purpose.

The harness that ran it reported which test had failed and nothing else. The diagnostic information built to be read from a log could not be read from the log. That, and not the unavailability of the information, is why the entry has said observed rather than diagnosed across 8 runs. The harness now keeps the full output and says where it put it.

The rate is 3 failures in 8 full-size runs, 37.5 percent, with a 95 percent Wilson interval running from 13.6844 to 69.4258 percent. Both models made the same point without being asked twice: an interval spanning a factor of 5 describes 8 runs rather than establishing a rate, and acting on it means collecting more runs rather than reasoning harder about the 8.

## The Intermittent Failure Was Never Intermittent

The test failure that had been carried for several days as observed rather than diagnosed is resolved, and it was deterministic all along.

The project deliberately refuses to treat generic folder names, such as "checkout", "clone" and "git", as a project's identity. That refusal is correct: a copy of the repository sits wherever the reader put it, and it must not claim its parent folder's name as the project's name. The defect was that the code deciding "is this path my own tree?" then had no other way to recognise itself. A copy whose folder is called "clone" could not identify itself as the project.

The harness that makes copies for reproducibility checks names its folder exactly that. So every run through that harness failed and every run through any other harness passed. Measured across 4 folder names at the old revision, only the one called "clone" failed, and on the same shape in a single command the old code gives 1 failure against 35 passes while the fixed code gives 36 passes.

Deciding whether a path belongs to your own project by looking at the folder's name is the same defect shape as everything else recorded here, and it was sitting inside the classifier that decides which rejections are location artefacts rather than real ones. The code now compares the paths themselves before it looks at any name, and keeps the name comparison underneath, because that is still the only way to recognise a path recorded on somebody else's machine.

Two things follow that are worth stating plainly.

The diagnosis was only possible because the harness stopped discarding its own output 2 hours earlier that afternoon. The failure message prints the project names it resolved, where they came from, the folder it is running in, and every path it probed. Before that fix the run reported the test's name and nothing else. The repair to the harness and the diagnosis of the failure are one story, not two.

And the figure computed for it, 3 failures in 8 runs with a confidence interval running from 13.6844 to 69.4258 percent, was measuring which harness made each copy. Over a deterministic process that figure describes the 8 runs rather than the software. The per-run records are kept, because they are the evidence that identified the harness as the variable, but 37.5 percent is withdrawn as a statement about how often the test fails.

## A Request For Help Destroyed A Record And Reported Success

The worst single defect of the day, found last and by accident.

Two scripts rebuild the complete verbatim record of a panel review from the raw model responses. Those responses live in a directory the project deliberately does not track, because it once held 353 megabytes. Neither script understood the request-for-help flag, so passing it did not print a description: it ran the script. In a fresh copy of the repository the raw responses are absent, so the rebuild wrote every model back as "no response file" and replaced a 55,814-byte verbatim record of a 5-model review with a 1,334-byte stub. It then reported success.

This had been happening in every fresh-copy test run. The symptom that reached the test suite was a complaint that two records from August looked like summaries rather than records, which reads as a problem with the records and was a problem with a flag.

It was found by keeping the throwaway copy after the run instead of deleting it, and asking the version-control system what had changed inside it. That is the second time in one day the fix was to stop an instrument throwing away its own evidence; the same harness had been discarding the diagnostic output that solved the intermittent failure described above.

The morning's sweep of this exact hazard reported a clean result, and it was honest. Its population was the measurement scripts, and both offenders are action scripts. There are 122 scripts in the project; the 68 that sweep does not reach are precisely the ones where a flag that acts is destructive rather than merely impolite. The false result was in the choice of population rather than in the matching, which is the same defect one level further out than anyone was looking.

Seven scripts both wrote something and ignored the flag, 5.7 percent of 122 with a 95 percent interval from 2.8 to 11.4 percent. All seven, plus the two record assemblers, now answer it, verified by running each one in a throwaway copy: all nine print a usage line, report success, and leave the copy untouched.

The permanent check is deliberately a static one, and the reason is worth stating. Running every script in the project with that flag is exactly what must not be done: the standing record notes that 15 of 17 dispatch scripts once billed a live model call on any unrecognised argument, and spending money is one of the three things reserved to you. The executing proof was done once, by hand, in a copy that was thrown away.

And the check written to catch this had the defect it was written to catch. Its first version asked whether the name of the help function appeared anywhere in the script's text, so deleting the real call left it satisfied, because the explanatory comment beside the call still contained the name. A guard reading its own comment about a function as evidence that the function is called. It now asks the parsed program whether the function is actually called.

## Half The Orphaned Scripts Did Not Need A Ruling After All

Six committed scripts were reaching nothing at all, and the question of whether to keep or remove them was parked for you. On a closer look, only half of that question is yours.

The project's standard has two halves. Removing something requires a measurement showing that a replacement is better, and that is a decision for you. The other half says an addition nothing reaches is not an addition either, and that one is discharged simply by giving a script a caller. A test that runs it is exactly such a caller.

So three of the six are now wired, and the choice of which three was measured rather than assumed. A structural scan of all six found that three contain no write, no spawned process and no absolute path, so running them cannot change anything. All three still work, which is worth knowing whichever way you rule: a committed measurement that no longer runs is a defect regardless of whether it is kept.

The third of those three was added only after asking which processes the "spawners" actually run. One of them spawns nothing but two read-only version-control queries. Classifying it by the shape of the call rather than by what the call does was a coarser version of the same mistake found repeatedly today.

Three remain parked and unrun, and the reason is now specific rather than general. Two write files outright. The third runs another script with a "change nothing" flag, and that other script carries ten separate writes, so its safety depends on a different program honouring a flag. That is a reasonable bet and not one worth taking against a preserved archive, which is exactly what the standing instruction exists to protect after someone already lost one.

And naming those three in the new test's own explanation un-orphaned one of them within a minute, because writing a script's path into a tracked file is all it takes for the reachability scan to count it as reached. That is the fifth time in a day that prose about an orphan stopped it being one. They are no longer named there; the list lives in the parked file, and the check reads it from the ratchet rather than repeating it.

## Two Things Recorded Honestly Rather Than Closed

A test in the suite has now failed 3 times in 8 full-size runs, every time in a fresh copy of the repository, and passes in the maintainer's copy, in isolation, and in a partial run. Reading the source produced no mechanism, and inventing one would be exactly the habit this project exists to avoid. It reproduced this afternoon, and the harness discarded the diagnostic information rather than recording it; that is fixed, so the next occurrence will explain itself. The earlier figure in this report, 2 failures in 5 runs, was itself undercounted: the audit that produced it searched for failure lines anchored to the start of a line, and the archived logs are indented, so 2 real failures read as none.

The Wolfram licence observation, which was deliberately deferred to today, was made at 09:37 and repeated at 11:09 with the same result. The licence file has not been rewritten and the expiry date has not moved: it is today. The engine still computes correctly, verified on 2 known results that match independent tools exactly. So nothing is broken, and the founder's reading, that renewal happens close to the expiry date, is not contradicted at 09:37 on that date. The question becomes real only if the date has still not moved once today has passed.

## The State Of The Work List

92 entries. 81 complete, 2 open, 4 blocked on the founder, 1 deferred, 4 withdrawn.

Written under CDSFL note standard v1.7 (26 August 2026).