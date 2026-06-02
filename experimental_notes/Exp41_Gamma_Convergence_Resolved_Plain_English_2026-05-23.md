# What convergence measures — the settled view

2026-05-23 18:34 BST. Constraint Engineering / CDSFL.

## Why the explanations kept shifting

Recent discussions about how the review decides it is finished kept changing
shape, which was confusing. The underlying facts did not actually change. What
kept changing was an attempt to answer the wrong question. This note separates
the two ideas that were being tangled together, states the settled answer, and
explains why it stays faithful to the original insight the project was built on.

## The two things both called "gamma"

The confusion comes from one word, gamma, standing for two different things.

**Gamma the idea** is the decay curve. As a review finds and clears real
problems, the rate at which it turns up genuinely new *serious* ones falls
towards zero, and the curve flattens. That flattening is the signal that the work
is essentially done. This decay curve is the founding insight of the whole
project — it *is* what convergence means.

**Gamma the calculation** is one specific way of putting a number on that curve,
by fitting a slope through the whole history of findings. It is only a measuring
instrument, and it turns out to be a poor one in an important way.

## Why the calculation is a poor instrument

The slope looks at the entire history at once, so it reacts slowly to what is
happening now. This shows up in two opposite ways:

- If a serious problem appears late, after a long quiet stretch, the slope barely
  moves — it stays high and would wrongly call the work finished even though a
  serious problem just turned up.
- If problems declined messily before going quiet, the slope stays low for a
  while — it is slow to credit that things have genuinely gone quiet now.

Both are the same flaw: a measure built on the whole history is sluggish about
the present. And the present — "has discovery stopped?" — is exactly what matters.

## The better instrument

There is a simpler, more accurate way to read when the curve has flattened: count
how many recent rounds in a row have turned up no new serious problems. It looks
only at the present, so it reacts immediately. A late serious problem resets the
count at once; a clean recent stop is recognised straight away. This count is the
accurate reading of the founding idea.

## The settled answer

Convergence is the serious-findings decay curve flattening — unchanged from the
beginning. The flattening is **detected with the recent-quiet count**, because
that is the accurate, immediate reading. The slope value is still **computed and
reported** alongside, where at a genuine finish it reads close to 1 and confirms
the picture. A finding only counts as "serious" in the first place after the
intelligent models judge it material **and** a mechanical check confirms it is
real.

This is **not** a demotion of the founding idea — it is the opposite. The decay
curve is still the entire criterion; the only change is that it is now read with
an accurate instrument instead of a sluggish one. To a sceptic the story is
clean: convergence means the serious-discovery curve flattened; here is the curve
value near 1 showing it did; the count is simply how the flattening is detected
without the slope's lag.

## Why this is trustworthy and not just agreeable

The strongest sign this is the right answer rather than a convenient one is that
**it is exactly what the recent successful run already did.** That run finished
because the recent-quiet count reached three clean rounds and the serious-findings
curve stood at its flat value. Nothing new is being invented; the bolted-on
extras are removed and what worked is kept — and what worked is the original
insight.

## How the project proceeds

- The instruction to the models is **reframed**: find the best solution that gets
  the work done efficiently, and the material problems that decide whether it
  works — not every possible fault class.
- The finish rule is the simple one above, with the curve value reported for both
  serious findings and all findings, each clearly labelled.
- The earlier proposal that introduced an unfamiliar new cut-off value (0.85) is
  **withdrawn**.
- The planned experiments (42 → 54) still run, now under this reframing. After
  that the work moves to its next phase and to wider review.

Written under CDSFL note standard v1.2 (14 May 2026).
