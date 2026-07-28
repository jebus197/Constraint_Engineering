# The Clean Convergence Test — What It Showed, in Plain English

2026-05-16 19:34 BST

## What this note is

A plain-English account of the five-round leg of Experiment 40 that was run
specifically to settle one question: is the experiment's long-standing failure
to "converge" caused by a known mechanical fault, such that fixing the fault
would let it converge? The technical companion carries the round-by-round
numbers; this note explains the question, the answer, and why the answer
matters.

## The question

"Convergence" here means the panel of five models settling on a single,
stable set of conclusions about the code under review — the equivalent of a
calculator returning one definitive answer rather than five models arguing
indefinitely. Experiment 40 had repeatedly failed to reach that state. One
recurring mechanical fault was a "merge deadlock": two findings that should be
combined into one get stuck, unresolved, round after round — one of them had
been stuck for twenty-one rounds, the longest in the project's history. A
resolver was built that breaks such deadlocks by a panel majority vote. The
test: switch the resolver on, hold everything else stable, run exactly five
rounds, and see whether convergence follows.

## The answer

It did not. The resolver worked perfectly on its own terms — it cleared eight
to ten stuck deadlocks by proper majority, including the twenty-one-round one,
resolved unanimously. But the convergence measure did not move. In the five
rounds with the resolver on, that measure sat flat at about 0.05, the same
level as the preceding rounds with the resolver off. The system ended exactly
where it had been: not converged, with twelve open disputes still outstanding
against a ceiling of five.

So the simple idea — that the deadlocks were the thing blocking convergence,
and clearing them would unblock it — is wrong for this target. The deadlocks
were a real fault and the resolver is the right fix for them, but they were
not what was holding convergence back.

## The more revealing number

Looking at the whole twenty-nine-round history, the convergence measure tells
a sharper story. It needs to reach 0.30 for the system to count as converged.
Very early, at round 3, it reached 0.2967 — within about one percent of the
line. Then it fell, every stretch of rounds, and settled at roughly 0.05,
where it stayed for the next twenty-five rounds and never recovered.

That is the important picture. It is not that the system cannot get near
convergence — it got to the doorstep almost immediately. It is that, on this
target, it then walked away from convergence and stayed away. The repeated
failure is not an inability to approach the answer; it is a tendency to
approach it and then diverge.

## Why this is useful, not just disappointing

This is a clean negative result, and it earns its keep by redirecting the
search. For a long time the working assumption was that mechanical faults were
masking a convergence that was really there. That assumption has now been
tested directly on this target and found wanting: the most prominent
mechanical fault was removed and convergence still did not appear.

Convergence itself is not in doubt as a phenomenon — an earlier experiment
reached it cleanly and stably, and this run itself touched its threshold at
round 3. What is now in question, specifically for this kind of rich target,
is whether the panel simply keeps generating genuinely new findings
indefinitely, and whether the convergence measure and its threshold are
calibrated correctly for that situation. There are two independent reasons to
suspect the measure: an earlier mathematical audit found it can misread a
churning system as near-converged, and this run's own logs flagged that the
measure disagreed with the system's own record of what had been settled, and
recommended a human audit. These are leads to follow, not conclusions; the
honest statement is that the next place to look is the novelty dynamics and
the measure itself, not another single mechanical fix.

## Two housekeeping points

The round count was held to exactly five this time. A previous leg overran by
two rounds because a ceiling and an extension number were set differently;
setting them equal fixed it, and that fix is confirmed working here.

The automated supervisor that watched the run needed correcting three times
during the session — every correction was to the supervisor, never to the
experiment, which ran healthy throughout. One of those corrections mattered:
the supervisor briefly froze a perfectly healthy run on a false alarm. It was
unfrozen immediately with no loss, and the supervisor was redesigned so that
fragile heuristics can no longer take drastic action on their own — it now
only freezes the run for unambiguous corruption and otherwise just raises a
flag for a human to judge. This is recorded plainly rather than smoothed over,
because smoothing over exactly this kind of thing has been a named problem.

## Where things stand

Experiment 40 is complete. The five-round test it was built for is done, and
its result is the headline, not a footnote: clearing the mechanical blocker
did not produce convergence on this target. The resolver is sound and stays
on. The unresolved question — why a system that can reach the threshold then
diverges from it — moves to the novelty dynamics and the convergence measure,
and that is where the next work should go.

Written under CDSFL note standard v1.2 (14 May 2026).
