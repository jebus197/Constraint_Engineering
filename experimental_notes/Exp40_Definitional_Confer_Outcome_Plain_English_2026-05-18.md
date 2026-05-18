# What "Done" Should Mean — the Five-Model Verdict, in Plain English

2026-05-18 12:25 BST

## What this is

An advisory five-model panel, run with a deliberately neutral,
fact-only brief and no preferred answer from anyone, to inform — not
decide — what "converged / done" should mean for the project, given the
fixed goal (a genuinely useful science calculator, not a demo) and the
hard limit (one person, one small machine, about one month of money
left). All five answered cleanly. The result is one strong agreement
and one real disagreement, and both are reported here without being
smoothed over.

## The strong agreement

On the first question — can the project realistically reach a state
where nothing new of any kind is being found — all five said no, for
the same reason: the surface of small possible refinements to code and
language is effectively endless, the maths the project relies on
assumes a finite pool that drains, and the numbers already show the
all-findings measure never empties. Chasing total exhaustion is the
permanent dead end. This independently confirms the project lead's own
view.

## The real disagreement (kept intact, because it is the useful part)

On what "done" should instead mean, the panel did not agree, and that
is not papered over. Two models said: define done as exhausting the
serious, structural problems. Two said: that is not enough — the system
must also be shown to actually solve real test problems whose answers
are known in advance. One sat between, accepting the structural
definition only with conditions strong enough that it nearly joins the
second camp.

Underneath that split, all five did agree on a shared core: stop
chasing total exhaustion; the current "serious = severity above 0.7"
line is the single biggest weakness and must be replaced by a rule
written down in advance that defines "serious" by consequence — a
finding is serious if leaving it in would make the result wrong or
unreliable; measure on the settled record, not the moment-to-moment
one; declare the scope honestly and let a hostile reviewer reproduce
it.

The disagreement that remains matters: is it enough that the panel
stops finding serious problems, or must the system also be proven to
get real problems right? "The panel stopped complaining" is not the
same as "the answers are correct." Given the goal is a calculator that
must produce dependable results, the second, stricter view is the
stronger one. The sharpest idea in the whole exercise came from the
model that proposed making "serious" mechanical: a finding counts as
serious only if fixing it would change the answer to a pre-set test
problem. That removes the arbitrary threshold entirely.

## The synthesised answer

The honest resolution is not to pick one camp but to require both:
define "serious" by consequence and in advance, measure on the settled
record, show the serious problems are exhausted, **and** show the
system correctly solves a frozen set of real test problems it was not
tuned against. Each camp's requirement is the other's blind spot.
Together they are harder to pass than the current rule, not easier —
which is the point.

## Honest checks on this conclusion

A frozen ten-problem test set is itself a small target someone could
game — but it is harder to game than the existing measure, and that is
exactly why the answer is "both conditions," not "swap one for the
other." And a fair question: is the working model proposing a
harder-and-external answer just to please the lead and let everyone
move on? No — this answer makes the bar higher, narrows the claim, and
delivers an unwelcome message: the convergence work so far does not by
itself prove the goal. One panel member also misread the brief as if
it were being asked directly rather than as one of five; its reasoning
was sound and matched the others, so it corroborates, but it counts as
four-plus-one, not a clean five.

## What happens in the month

Week one: freeze the scope; write down the consequence-based "serious"
rule before any run; make the measure use the settled record; freeze a
small set of real STEM test problems with known answers. Weeks two and
three: run the bounded proof on small pieces, with fixes applied back,
and only call it done when the serious problems are exhausted and every
frozen test problem is solved correctly. Week four: stress-test the
result, run one cold adversarial check, package it honestly with the
limitations stated, and write up exactly what is and is not claimed.
Set aside the harder modelling extensions and the full large benchmark
as future work.

## The bottom line

The internal convergence work so far does not, on its own, prove the
goal. A defensible one-month proof must show the system correctly
solving pre-set problems it was not tuned against, with "serious"
defined by consequence and fixed before the run. That is harder than
the path so far — and it is the first point in all of this that ends
somewhere a sceptical outsider could accept. This is advice; the
decision remains the lead's.

Written under CDSFL note standard v1.2 (14 May 2026).
