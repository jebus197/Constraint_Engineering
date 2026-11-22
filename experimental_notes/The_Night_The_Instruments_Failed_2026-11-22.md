# THE NIGHT THE INSTRUMENTS FAILED

Constraint Engineering, the 22nd of November 2026, from about 06:30 to 07:45
GMT. A session report covering the work done under the autonomy handover, while
a commit board held the machine.


## THE HEADLINE

Of every defect found in this window, almost none was in the code the project
is building. They were in the instruments built to check that code, and 5 of
them were in work produced during this very session. Every single one was found
by running something. Not one was found by reading.


## WHAT A COMMIT BOARD IS, AND WHAT IT COSTS

A commit in this project is gated by a board: a fixed list of 322 guard files
that must all pass before the commit is allowed. Re-measured on the 22nd of
November over 91 determinate runs, that board costs a mean of 1866.296703
seconds, which is 31.10 minutes, with a 95 per cent confidence interval on the
mean running from 1736.805540 to 1995.787866 seconds. It refuses 44 of those 91
runs, a proportion of 0.483516, with a Wilson 95 per cent interval from 0.383609
to 0.584760.

That refusal proportion of 0.483516 had never been written down anywhere,
although it is the figure that actually governs planning. About half of all boards refuse, and each
costs roughly half an hour of an 8 core, 8 gibibyte machine.


## THE CHEAP CHECK THAT RAN A BOARD INSIDE ITSELF

A pre-board ladder is a small subset of those guards, run first, so a refusal is
caught in minutes rather than in half an hour. The ladder stalled. The watchdog
fired with no log growth for 904 seconds and processor time frozen.

Its only live child was a real commit running inside a temporary clone, with 2
live hook processes beneath it. 1 guard file makes a genuine commit, which
fires the genuine hook, which runs the genuine board. A check built to cost less
than a board was running one of its own. A sibling guard with the same property
had already been excluded by name. Exactly 1 was named and there were at least 2.

Selecting that ladder has now defeated 3 separate predicates. Choosing by
subject words omitted the guard of the very file being rewritten. Deriving the
set from the changed files included the board runner and hung for 18 minutes.
Searching for board containment over-matched at 45 of 322, because most of those
merely read the hook rather than run it. A standing rule says that when a surface
defeats 3 predicates, stop building predicates. The replacement is a mechanism:
a per test time limit bounds any guard that hangs, whatever the reason.


## THE KILL THAT KILLED NOTHING

The stalled processes were terminated with a loop over their identifiers. The
loop passed the entire list as a single argument, the operating system rejected
it, and the resulting error was discarded by a redirection to the null device.
The output said a signal had been sent. No signal had been sent, and all 6
processes survived.

This was caught only because the check that followed was unconditional rather
than conditional on the kill reporting a failure. Had it been conditional, a 31
minute board would have continued running while the record said it had been
stopped.


## A RUN RECORDED AS OUTSTANDING HAD ALREADY HAPPENED

The master task list carries a ticket for a simulated validation run on the
severity mechanics, to be performed before the orchestrator experiment, and the
body of that entry states the run has not happened. That sentence was written on
the 3rd of November. The operational tracker records the run as completed on the
2nd of November: 6 rounds, 25 findings, 85.5 minutes, scored against 4
predictions committed before it launched. Reading the tracker before acting
avoided repeating it.


3 GUARD FAILURES, AND ALL 3 WERE THE GUARDS

The ladder eventually completed with 7 failures out of 4,070 tests. 1 of those
could block a commit and 5 could not. Each of the 3 confirmed failures was
traced to its cause, and none was a fault in the code being guarded.

The first claimed a missing time limit. The limit exists, written as a sum rather
than as a plain number, and the checker accepts only plain numbers, so an
expression is invisible to it. The checker's own documentation claims it reads
the value from the running test. It does not. It parses the source.

The second was a guard outgrown by its subject. It asserts that a verification
chain covers an amount indistinguishable from half. Measured now: 160 valid of
266, which is 0.601504, with a 95 per cent interval from 0.541626 to 0.658492.
That interval clears half, so the finding needs restating. But the increase since
the 6th of November is NOT statistically significant, at a p value of about 0.20
on 2 independent routes, so the honest restatement says coverage is above half
and explicitly does not say it rose.

The third was a test whose expected answer is read from live project state
rather than from its own fixture. Its own sibling was repaired for exactly that
on the 17th of September, with a note saying an anti vacuity test must depend on
its own fixture and never on the state it happens to be surrounded by. That
repair reached the sibling and left this case.


## THE GATE THAT REFUSED THE SESSION ALL NIGHT HAS A MEASURABLE FAULT

A standing directive forbids going idle while a run is live. Its gate refused 9
times, and each refusal carried a contradiction: a status line reporting the
watch healthy, and an advice line reporting that no watchdog exists.

The cause is a wrong liveness signal. The gate judges whether a watchdog exists
by the age of its log file, under a comment stating that the watchdog writes on a
60 second cadence. It does not. It polls every 60 seconds and, in its own words,
speaks only when it matters, writing to the log on events and on a heartbeat
whose default is 30 minutes. So a healthy, quiet watchdog is invisible for 1500
of every 1800 seconds, which is 0.833333 of the time, and the failure is
guaranteed rather than occasional.

The signal written every interval is the pulse file, and the gate already reads
it: that is where the healthy status line comes from. The repair is to select on
the pulse. It was written test first, and the first attempt was wrong in an
instructive way: it judged pulse age by the file's timestamp while the gate's own
status line judges it by a field inside the file. Those disagree exactly when a
watchdog stalls, so the first fix would have reported a dead watch as live,
reinstating an older defect that the current code had corrected. The second
version reads the field. 19 tests pass against a patched copy where 2 fail
against the real one, and the real file was never modified.

That whole diagnosis, it turns out, was already in the project, written earlier
the same day and staged in the same batch of work. It was re-derived from scratch
at a cost of about 20 minutes. That was the 9th time in the session that a
finding already in the record was rebuilt from nothing.


## THE RESPONSE TO THAT WAS A TOOL, NOT A PROMISE

The rule to check the record first has existed for weeks. Restating it a 10th
time would be the failure the founder's own ruling names, in his words: the
failure was never the absence of a rule or a checker, it was never running the
checker. The reason the check was skipped is that it cost a tool call and a guess
about where to look.

A small tool now searches all 5 places in 1 command: producers, guards, hooks,
the task list and the memory directory. It requires every search term rather than
any, because 1 shared word matches a large fraction of the repository and teaches
the reader to ignore the output. It prints each result's first line of
documentation, which is usually the whole answer. Run against the case that
motivated it, the first result is the file that was duplicated, and its printed
line answers the question outright. It has 9 tests and 4 of 4 deliberate
sabotages are detected.

It has no automatic caller, and that is recorded as owed rather than claimed as
done.


5 DEFECTS IN THIS SESSION'S OWN WORK

A scoring script would have falsely condemned every real run, because the 9
fields it checks are nested 1 level deeper than it looked. Its own 18 test
guard did not catch this, because the guard's fixture invented the same wrong
shape, so every test passed against a fiction.

A probe built to enumerate a supervisor's decisions built 1 property into
another and produced an inverted table, appearing to show the supervisor acting
in a state it is guaranteed never to act in.

A repair to the gate read the wrong clock, as described above.

A file written to demonstrate rigour defined a function and never called it,
using an inline copy instead. 1 definition, 0 callers, which is precisely the
shape the project's additive standard forbids.

And 2 alarms raised in this session were withdrawn after measurement. The 1st
reported that most new scripts fail to answer a help request; re-measured where
those scripts would actually live, most of them pass, and a third of the apparent
The 2nd predicted a board refusal from those scripts. The guard that enforces
help answering was run against the live tree and passed with 27 tests.


## WHAT IS READY, AND WHAT IS OWED

The orchestrator experiment is build complete, with all 4 components present,
verified by execution rather than by reading. What stands between the project and
running it is 2 decisions that belong to the human in the loop by the project's
own definition: the bounds on a run that spends money, and a re-run the founder
said he would start when at the keyboard.

A middle setting exists that was judged to fall outside those reserved
categories, because it spends nothing and takes no action: the supervisor
classifies what happened and writes the verdict down, re-invoking nothing. The
complete set of conditions under which it would act was enumerated: over 28
states, 22 hold, 4 report completion, and exactly 2 would re-launch, both
requiring a specific pause code and a process that has already exited. That
enumeration is the decision the founder is being asked to make, stated
exhaustively rather than described.

The next batch of work stands at 10 items in 4 tiers. The 2 that go first are
defects the current batch itself introduces, named before it lands rather than
discovered afterwards.

Written under CDSFL note standard v1.9 (1 November 2026).
