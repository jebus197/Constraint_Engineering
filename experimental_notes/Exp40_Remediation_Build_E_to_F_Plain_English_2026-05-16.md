# The Repair Work — What Was Built, in Plain English

2026-05-16 23:46 BST

## What this note is

A plain-English account of the repair work carried out in one
autonomous overnight session to fix the cause of Experiment 40's
repeated failure to settle. The technical companion carries the commit
hashes and test counts.

## The cause, recapped in one line

When a fix was checked it was applied only to a private scratch copy
that was then thrown away; the real file the panel read never changed,
so the same bugs were re-found every round and the work never ran out.

## What was built

Six pieces of work were agreed and all but the last are finished,
tested, and committed; the last is running.

First, every fix from every past run of this experiment was collected
and checked. Forty-four had been recorded as closed. A clean version of
the file was rebuilt by applying them one at a time, keeping a fix only
if the whole test suite still passed afterwards. Eleven held up. Most of
the rest were competing edits to the same lines — the long-known
churn — and were set aside with reasons logged.

That collection step turned up something important. One "closed" fix
had in fact failed a test in its own original check, and was still
recorded as closed because its overall score was high enough. So
"closed" never reliably meant "correct" — it meant "scored well
enough", which lets a fix that breaks something slip through. This
matters, and it shaped the rest of the work.

Second, a silent data-loss bug was fixed: when two findings shared an
identifier, one was quietly dropped and its model never received the
corrective feedback it was owed, so that model kept repeating the same
point. Now both are kept and routed correctly.

Third, the immediate re-ask was built: when a model answers in the
wrong format, it is sent straight back, in the same round, with the
correct template, instead of waiting a round.

Fourth, and most important, fixes are now applied back to a working
copy of the file that the next round actually reads — but only if the
whole test suite still passes with the fix in place (the lesson from
the "closed is not correct" discovery). The real repository file is
never touched; a pristine copy is kept. This is the change that lets
the work actually run out, which is what the project's own model needs
in order for the panel to ever settle.

Fifth, the file was cut down to its smallest self-contained piece — the
admissibility parser, about a hundred lines — so runs are short and can
be watched, and so a small finite amount of work can genuinely be
exhausted.

Sixth, a fresh run was started on that small piece with everything
above switched on, a generous twenty-round limit, watched live every
sixty seconds, with a terminal window left open for morning review.

## One change stated plainly

Applying fixes back changes what this experiment is: from a test of
whether a panel agrees about an unchanging file into a test of whether
it can repair a file and settle on a finished result. That was a
deliberate, recorded decision, not slipped through. It is the right
change and it matches the goal of building one working result.

## For the morning

The final run's outcome is not known at the time of writing — it is
still going. The honest answer to the project's central question, does
the system settle once the work can actually run out, is whatever that
run produces, and it should be reported plainly either way: a quick,
clean settle is a real positive; a continued plateau means the cause is
not only the work-never-running-out mechanism and the search moves to
the novelty dynamics. Where to look is recorded in the technical note
and the tracker. Nothing in the finished work was left unresolved or
smoothed over; the one real surprise was handled in the design, not
deferred.

Written under CDSFL note standard v1.2 (14 May 2026).
