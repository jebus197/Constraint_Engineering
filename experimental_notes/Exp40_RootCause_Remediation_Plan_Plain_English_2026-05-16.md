# Why Convergence Kept Failing, and the Plan to Fix It — Plain English

2026-05-16 22:57 BST

## What this note is

A plain-English account of why Experiment 40 has repeatedly failed to settle
on a single stable set of conclusions, and the agreed plan to fix it. The
technical companion carries the code references and the numbers.

## The root cause, in one idea

When a model proposes a fix for a bug in the code under review, the system
checks that fix in a private scratch copy: it applies the change there, runs
the linters and the test suite, and if everything passes it records the bug
as closed. Then it throws the scratch copy away. The real file the panel
reads is never changed.

So the next round, all five models open the same file, the bug is still there,
and they find it again — correctly, because it really is still there. The only
things stopping endless rediscovery are a de-duplication step and a short note
in the prompt saying "these issues are already closed, do not repeat them" —
and that note is capped in length, so once enough bugs accumulate it can no
longer list them all. The result is a system that keeps re-finding work it has
already done. This is not a guess; it is visible in the code, confirmed by the
file's change history, and was already flagged in an earlier audit. It is, as
the project lead put it, probably the most persistent single problem in the
whole project.

## Why this explains the numbers

The convergence measure tells the story cleanly. It needs to reach a set line
to count as converged. Early on it climbed almost to that line — the easy
repeats were being cleared and progress looked real. Then it fell back and sat
flat, just above one-sixth of the way to the line, for twenty-five rounds in a
row. The mathematical model the project is built on actually predicts this:
when new findings are re-injected faster than old ones are exhausted, the
system stops converging and starts churning. An unfixed file guarantees that
re-injection, because the bugs are never removed. The measure is not broken —
it is correctly reporting a system that can never run out of things to find.
Convergence itself is real and was demonstrated cleanly in an earlier
experiment; the problem here is purely that the error space is never allowed
to shrink.

## The plan

A separate mathematical re-audit was considered and set aside as unnecessary —
the model is sound and convergence is taken as a real, reachable goal for a
bounded proof-of-concept. The agreed work is:

1. Fix the silent finding-loss bug. A line that indexes findings by their ID
   currently overwrites one finding with another whenever two share an ID,
   quietly dropping data and corrupting the very count convergence is measured
   by. It will be changed to keep both and log the clash instead of dropping
   one. This replaces a long-deferred "watch and wait" with an actual fix.

2. Build the immediate re-ask. When a model answers in the wrong format, the
   system will bounce it straight back to that model, in the same round, with
   the correct template, instead of waiting until the next round. This is the
   active error-correction that was always intended.

3. Apply verified fixes back to the file. This is the core cure. Once a fix
   has fully passed all checks, it is written into a working copy of the file
   that the next round actually reviews — so the bug is genuinely gone and the
   panel has less to find each round, not the same amount forever. The next
   run starts from a copy that already has every previously-verified fix
   folded in, so it begins from cleaned code and only has to settle what
   genuinely remains. A fix is only kept if the file still passes all checks
   with it in place.

4. Work on a smaller piece at a time. Instead of one large file reviewed for
   many rounds before anything can be judged, the next run targets the
   smallest self-contained part first. Short, watchable runs mean problems are
   caught early and fixed on the fly, rather than discovered after hours.

5. Collect every fix from every past Experiment 40 run, check each one, and
   fold the valuable ones in — methodology fixes into the runner, code fixes
   into the cleaned starting file. Stale or duplicate ones are discarded and
   logged.

6. Re-run, with all of the above in place, watched live every sixty seconds,
   with a generous round limit — generous now being reasonable because the
   design is finally sound, where it would have been wasteful before.

## One change stated plainly

Applying fixes back to the file changes what this experiment is. It stops
being a test of whether a panel agrees about an unchanging piece of code, and
becomes a test of whether the panel can repair code and settle on a finished
result. That is a deliberate change, recorded here so it is not slipped
through quietly. It is the right change: it is what the project's own decay
model needs in order to finish, and it matches the goal of building one
working result rather than endlessly re-examining a static one.

## Order of work

The collection and folding of past fixes comes first, because it produces the
cleaned starting file the core cure needs. The two bounded fixes (silent
finding-loss, immediate re-ask) run alongside. The apply-back cure follows,
the smaller-piece decision is made with it, and the watched re-run comes last.

Written under CDSFL note standard v1.2 (14 May 2026).
