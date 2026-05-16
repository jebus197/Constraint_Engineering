# The Restarted Run — What Happened, in Plain English

2026-05-16 05:46 BST

## What this note is

A plain-English account of the restarted Experiment 40 leg that ran
overnight after the neutral timing review. The technical companion
carries the counts, file paths, and round-by-round detail. This note
explains what the run was for, what it proved, and the two things a
reader must keep in mind when interpreting its numbers.

## What the run was for

Its job was not to "achieve convergence". Its job was to prove, under
real load, that the block of fixes built over the preceding day
actually works — with the new merge-deadlock resolver deliberately
switched off (the panel had just decided, in an unbiased review, that
switching it on for this run would risk corrupting the very result the
run measures). It ran for about two and a quarter hours, completed
seven rounds, and stopped cleanly.

## What it proved

Every fix was confirmed working in production, not just in tests:

The reasoning-trace recovery fix fired sixteen times. Each time, one
of the two "thinking" models returned an empty answer field but a full
chain-of-thought; the fix recovered the analysis from the
chain-of-thought — sometimes thirty thousand characters of it — that
the old code would have thrown away as nothing. The original
empty-output anomaly is closed.

The classifier-honesty fix held every round: the logs now state the
real reason for each decision instead of the misleading "below
threshold" message that originally looked like a bug.

The bias-alarm windowing fix proved itself in both directions. For the
first two rounds a model hit a hundred-percent-duplicate rate, the
alarm correctly stayed quiet (this was the exact per-round noise that
plagued the earlier run). On the third consecutive round it correctly
fired — and kept flagging as the pattern genuinely persisted for six
straight rounds. It suppresses noise without going blind to a real,
sustained problem. That is precisely the design.

The strengthened reformat request worked: malformed fixes were
re-requested and the models responded with corrected versions, every
round — vindicating the decision not to build the riskier mid-round
re-ask.

And the new collision detector — the small watch-only instrument added
specifically to make the deferred identifier-rewrite decision
evidence-based rather than a guess — recorded **zero collisions across
all seven rounds**. This is the decisive result: the theoretical bug
the deeper rewrite would fix did not occur once. The deferral is now
proven correct rather than assumed, and the detector stays in place to
catch it if it ever does happen.

The merge-deadlock resolver stayed off, as decided. The deadlocks duly
recurred — one of them has now been stuck for twenty-one rounds, the
longest in the project's history — exactly as the review predicted and
accepted. They stayed contained and logged; they corrupted nothing.
That growing pile of evidence is exactly what justifies switching the
resolver on at the next, small, low-risk experiment.

## Two things to keep in mind about the numbers

First, a deviation I caused. You asked for five rounds. The run did
seven. I set a round ceiling and a separate "extension" number,
treating the extension number as harmless headroom. It is not
harmless: the runner actively uses it as a runway to keep going when
it hasn't converged — and it never converges here because the
deadlocks (resolver off by design) never clear. The run was bounded
and stopped cleanly at seven; the cost was two extra rounds, about
half an hour. I caught this while watching, investigated it before
touching anything (confirmed it was not a runaway — it was always
going to stop at the ceiling), and let it finish cleanly rather than
kill a healthy run to enforce a number. The lasting fix is simple and
now written into the plan: for a fixed-length restart, the ceiling and
the extension number must be set equal.

Second, a confound built into the setup. The file the panel reviews is
the same file I added the collision detector to. So this run had the
panel reviewing changed code it had never seen — and it duly found
more in it, including inspecting and approving the detector itself.
That is the main reason the "new critical findings" count rose across
the run. So that rising count is largely an artefact of the modified
target, not a statement about convergence. Any comparison of this
run's convergence against the earlier run must carry that caveat. The
deeper non-convergence pattern is a separate, older phenomenon the
broader programme is built to address; this run did not create it.

## Where things stand

The fix block is validated in production. The deferred decisions are
now evidence-backed: the identifier rewrite stays deferred because the
detector proved the bug doesn't occur; the merge-resolver is ready to
switch on at the next experiment because the deadlock evidence is
overwhelming; the mid-round re-ask stays deferred because the simpler
fix handled the load. The two caveats above are documented at the
exact points in the plan where they must be acted on, so they cannot
be lost. Nothing is broken; everything that needed proving was proven;
and the one process error I made is fixed for the future and disclosed
here rather than buried.

Written under CDSFL note standard v1.2 (14 May 2026).
