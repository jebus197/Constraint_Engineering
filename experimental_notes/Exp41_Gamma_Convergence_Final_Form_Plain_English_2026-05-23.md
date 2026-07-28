# How the review decides it is finished — the settled design

2026-05-23 17:13 BST. Constraint Engineering / CDSFL.

> **Superseded (2026-05-23, later the same day).** The "curve sets the waiting
> time" control rule and the 0.85 cut-off described below are withdrawn. The
> settled design is simpler: the serious-findings decay curve is the criterion;
> it is detected by the recent-quiet count (three clean rounds); the curve value
> is reported, not used as a separate gate. The reason is that the slope is a
> laggy instrument, so it should not override the count. See "What convergence
> measures — the settled view" (`Exp41_Gamma_Convergence_Resolved_Plain_English_2026-05-23.md`).

## The question

The system needs to know when a review is genuinely finished. It has two ways of
sensing this, and for a while they looked like they were arguing with each
other. The real question underneath was simpler and more important: are these
two signals actually the same thing seen from different angles, and does the
project's founding idea — the "decay curve" — still genuinely earn its place, or
has it quietly become decoration?

## The founding idea, in plain terms

As a review finds and clears real problems, the rate at which it turns up *new*
serious ones falls off. Plot that and you get a curve that starts steep and
flattens out as the work is exhausted. The flattening is the signal that there
is little left to find. That decay curve is the heart of the whole project. The
measure of how flat the curve has become is called gamma.

There is also a second, blunter signal: simply counting how many rounds in a row
have turned up no new serious problems at all.

## Why they looked like they disagreed

On one clean run the curve measure read low (suggesting "not finished") while the
count said "finished." That looked like a contradiction. It was not. The curve
was being measured over *every* finding, including trivial footnotes that keep
trickling in long after the real work is done, whereas the count was looking only
at *serious* findings. Measured on the same thing — the serious findings — the
two signals agree. The footnotes were dragging the curve down and making it look
busy when the important work had stopped.

So the first fix was simply to measure the curve where it matters: on the
serious findings, and to always show both numbers side by side so nothing is
hidden.

## The real worry

The tempting shortcut was to let the simple count make the decision and treat the
curve as a number you just report. But that would hollow out the founding idea. A
sceptic would fairly ask, "if your decay curve never actually changes any
decision, does your model say anything at all?" Credibility depends on the curve
genuinely doing work, not on it nodding along.

## What the panels were asked, and what they said

To avoid leading the answer, the question was put to five independent frontier
models, twice, with the wording kept deliberately even-handed. The first round
agreed the points above: measure the curve on serious findings, show both
numbers, and require both signals together rather than letting either decide
alone.

The second round settled the exact shape, and all five agreed on the same answer.
The clever move is this: do not bolt the curve on as a separate pass-or-fail test
next to the count. If you did, the two would be mathematically tied — once you
have had a few quiet rounds, the curve is automatically flat, so it would only
ever rubber-stamp what the count already said. Instead, let the curve decide *how
long the quiet stretch has to be*. A clean, steep decline has earned trust, so a
short quiet stretch is enough. A messy, hesitant decline has not, so it must
stay quiet for longer before the review is declared finished.

## Why that makes the curve genuinely matter

Picture two reviews that have both gone quiet for three rounds. In one, serious
findings fell away cleanly and steadily. In the other, they bounced around — a
couple, then more, then finally silence. Under the old "either signal will do"
approach, both would stop now. Under the agreed design, the clean one stops and
the bouncy one is made to wait longer, because its curve has not earned the short
exit. The curve changed the outcome. That is the proof it is load-bearing and
not decoration, which is exactly the credibility point.

It also cannot trap the system: even when the curve is weak or impossible to
measure, a longer quiet stretch still ends the review. So a finished job always
finishes, and the founding idea keeps its teeth.

## The honest catch

The weak spot now moves to one place: how findings are labelled "serious" versus
"trivial." If something serious were wrongly filed as trivial, the curve would
look cleaner than it really is. The guards against that are to fix the labelling
rules in advance, to keep showing every number including the all-findings curve,
and to keep an ongoing tally of how often the curve actually changed a decision.
If that tally ever falls to nothing, the curve has secretly become decoration
again and the settings must be revisited. This turns "is the curve really doing
work?" from a claim into something measured.

## Where this leaves things

The design is approved. The next step is to build it into the runner and confirm
that the recent clean run still finishes as it should — which it will, because on
that run the serious-findings curve was as flat as it gets and the quiet stretch
was already long enough.

Written under CDSFL note standard v1.2 (14 May 2026).
