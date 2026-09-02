# The wheel already exists, and our blocker is a recording change

**2 September 2026.** An external sweep of six literatures, a panel dispatch
that could not physically complete, and a reductio that says the harness has
seen a quarter of one percent of what there is to find — or that its matcher is
broken.

---

## The question that turned out to be answered in 1953

CDSFL has asked, for months, at what point it stops paying to put the same
question to another model. The answer is not new. Chao and Jost (2012, *Ecology*
93:2533–2547) give the identity directly: the fraction of the finding population
that one more reviewer would add **is** the estimated coverage deficit of the
sample already taken. Coverage itself is estimable from the sample alone, with
no knowledge of the population, by Turing's estimator (Good, 1953) as improved
by Chao and Shen.

The practical significance is that this is a derivative rather than an
asymptote. Estimating how many defects exist is hard and needs a great deal of
data. Estimating whether the *next* reviewer will find anything new is easy and
needs very little. The stopping rule that follows was justified by Rasmussen and
Starr (1979); the economic form, with an explicit exchange rate between the cost
of another reviewer and the loss from a missed defect, is Dalal and Mallows
(1988), in a paper titled "When Should One Stop Testing Software?".

Every estimator in this family — Lincoln-Petersen, Chapman, Chao, the
Burnham-Overton jackknife — consumes exactly two numbers: how many findings were
seen by exactly one reviewer, and how many by exactly two.

**The harness records the first and destroys the second.**

## The reductio

Of 2,050 real archived findings, 2,048 are recorded as raised by exactly one
model and 2 by more than one. Feeding those figures to the estimators gives a
bias-corrected Chao2 population of 561,017 findings, an incidence jackknife of
3,688, and an estimated sample completeness between 0.24 and 0.37 percent.

Two estimators from the same family disagreeing by a factor of 152 is not a hard
estimation problem. It is a signal that the data lies outside the domain where
the estimators are defined.

The mark-recapture literature names this pathology precisely. When a
previously-detected individual is not recognised on re-encounter, it is recorded
as new — a "ghost". Ghosts inflate the count of things seen once, collapse the
count of things seen twice, and bias the population estimate upward (Yoshizaki
and colleagues 2011; Link and colleagues 2010; Fraysse and colleagues 2023).

So 2 in 2,050 is first a measurement of the finding matcher, and only
second a measurement of the panel. Until that is settled, no downstream number
is actionable — which is why a measured matcher is instrumentation item one
rather than item four.

## What was claimed as novel, and was not

The working assumption had been that allocating effort where ground truth comes
from executing a test, rather than from agreement between judges, was the part
requiring invention. It is not, and it is the easy regime rather than the hard
one. Brown and colleagues (2024) partition verifier-present from verifier-absent
explicitly: with a verifier available, coverage grows log-linearly across four
orders of magnitude of sampling, while without one, majority voting plateaus in
the hundreds. Algorithm-portfolio selection trains on execution outcomes.
Adaptive submodularity requires observing a realised outcome before choosing the
next action.

The defensible claim is the opposite of a novelty claim, and it is stronger:
CDSFL operates in the verifier-present regime, which this literature identifies
as the regime where scaling actually pays.

## What is genuinely unexplored

Two things survive that correction, and the cheaper one is the stronger.

**Open-population estimation.** Every estimator above assumes a closed
population — the artefact does not change while it is being reviewed. CDSFL's
artefact does change, by its own multi-round design, as fixes are applied.
Petersson and colleagues named this as unexplored in 2004, in as many words, and the sweep found nothing addressing it in the 22 years since.

**Capture histories carrying a verdict.** Each time a finding is raised, the
harness also records whether a tool confirmed or refuted it. No formulation in
the capture-recapture literature attaches a validity label to an individual
capture. The software-inspection literature handled false positives by noting
that two errors tended to cancel, which its own survey admits. A three-state
history — not found, found and refuted, found and confirmed — is uninvented, and
is an extension of an existing model rather than a research programme.

## A dispatch that could not finish

The review panel was asked, in the same brief, to implement cross-model
duplicate detection and to run two short simulated experiments.

A simulated experiment takes 69.6 minutes on average, with a 95 percent interval
from 48.3 to 90.9 and a measured range from 37 to 120. The dispatch budget is 40
minutes. Ten of eleven archived simulated runs exceed the entire budget on their
own — 90.9 percent, with a Wilson interval from 62.3 to 98.4.

One run is 1.74 times the budget; two are 3.48 times it. Both reviewers timed
out and retried against the same limit.

The panel did not fail. The instruction was impossible, and the failure belongs
to whoever wrote it. The correction is to split experimental work out of review
dispatches entirely: the harness runs the experiment, the panel reads the
artefact.

## What follows

The instrumentation that unlocks everything else is a recording change rather
than a research project: record, for each finding, the full set of occasions
that raised it, where an occasion is a model, a prompt role, a seed and a round.
That single change makes the overlap statistic available, and with it coverage,
the marginal-yield estimate, and a stopping rule that means the same thing
whether a researcher has one model or a hundred.

For a researcher with a single model, capture across models is impossible, and
the fix is to change what counts as an occasion rather than to abandon the
method. Repeated samples at non-zero temperature and distinct prompt roles are
trapping occasions in exactly the sense the estimators require. Seeded defects
remain the only instrument that bounds what no reviewer can see, and the only
one that works when there is just one reviewer.

One correction to how that seeding has been done here: hand-written seeded
faults are not a valid substitute for real ones, while mechanically generated
mutants are (Andrews, Briand and Labiche, 2005; Just and colleagues, 2014). Both
catalogues used so far were written by hand.
