# Experiment 40 — Did the Stricter "Done" Test Stop the Books Being Cooked?

2026-05-18 22:27 BST

## The question

Experiment 40 studies whether five frontier AI models, reviewing a
piece of software in rounds, can be trusted to *stop* at the right
moment — to declare "this is done" only when it genuinely is, and never
because a convenient number happened to cross a line. The old "done"
test was loose: it stopped if a depletion measure crossed a threshold
*or* if no new serious problems appeared for three rounds. Either
condition alone was enough. That "or" is the single biggest way the
result could be flattered.

A stricter test was designed and frozen in advance. It now requires
*both* conditions at once, and it adds a robustness check: the
depletion trend must survive having any one round removed, so it cannot
rest on a single lucky round. It also separates the count of *serious*
problems from the count of *all* problems, and uses only the
serious-problem trend to decide — the all-problems figure is recorded
but never allowed to drive the verdict. A consequence-based definition
of "serious" was written down and locked before any run, so the
boundary could not be moved after seeing results.

## What was tested

The target file was split along its natural internal seams into three
honest pieces, not chopped into artificially small fragments (which
would have been its own kind of distortion). The smallest piece is a
self-contained detector. The middle piece is a self-contained parser.
The largest is a tightly-bound cluster of five functions that share one
data structure and cannot be separated without faking their
surroundings. Each piece was reviewed in rounds by all five models,
with verified fixes folded back in as the rounds progressed, and the
whole thing watched minute by minute.

## What happened

The strict test converged **only the smallest piece**, and refused the
other two. That is the headline, and it is the right outcome.

The smallest piece is genuinely tiny and its problem space genuinely
runs out. The gate recognised this, set its unreliable depletion figure
aside (it explicitly did *not* let that figure decide), and closed on
the honest signal that nothing serious had been newly found for three
settled rounds. This is exactly the behaviour written into the frozen
design for small, fully-exhaustible artefacts.

The other two pieces were refused — not because the depletion figure
was too low (it sat comfortably above the threshold the whole time, in
every round) but because that figure was not robust. Remove a single
round and it collapsed. For the parser it collapsed to nothing on every
one of its nine measured points; for the cluster it crept upward but
never reached the robustness floor. The decay was riding on individual
lucky rounds, not a real downward trend, and the strict test is built
to reject precisely that.

The most telling moment came from the cluster. At two consecutive
rounds its no-new-serious-problems condition was satisfied — the old
loose test would have declared victory there. The strict test refused,
because the depletion trend was not robust. One round later a brand new
serious problem appeared. So the loose test's "done" would have been
*wrong*, and the next round's evidence proved it wrong. The strict
test's refusal was vindicated by what actually happened. That is the
strongest possible demonstration that the change from "or" to "and"
prevents real false declarations of success, not hypothetical ones.

## Things that went wrong, and were handled honestly

Watching the runs live surfaced three latent bugs in the experiment
harness itself. The most serious: a safety mechanism that is supposed
to halt a model when it returns nothing had been silently broken for a
long time, because its error object could not survive being passed
between processes. It was failing in a way that hid the real cause. All
three bugs were traced to root, fixed between units (never mid-run, so
no run was ever split across two versions of the harness), tested, and
then seen working correctly in production later in the campaign. None
of them had corrupted any measurement — they misreported, they did not
distort.

An external network outage killed one run partway through. That is
infrastructure, not a verdict; the run was started again cleanly from
an archived copy rather than resumed into a half-broken state. One
model was repeatedly very slow, once taking more than twenty minutes
for a single step; each time the harness's own recovery brought the
content back, and the disciplined choice was to wait rather than kill a
recovering run. Across the three pieces, nineteen verified fixes were
folded back in, each gated on the full test suite staying green.

## A few tidy-ups noted for later

Some older hard-coded numbers in the harness should be replaced by the
single named constant the new test uses; one status label reads
"incomplete" when "reached the round limit without converging" would be
clearer; one message guesses "wall clock" when the real cause was the
round limit; and the slow-model recovery path should print a heartbeat
so a watcher can tell "slow but fine" from "stuck". None of these
affects a verdict. All are recorded for routine attention, not skipped.

## Bottom line

The Experiment 40 question — does the stricter test stop convergence
being flattered? — is answered yes, with evidence, and reproducibly.
The test passed the one piece that genuinely deserved to pass, refused
the two that did not, and in the one case where the old and new designs
could be compared head to head, the new design was proved right by the
data the old one would have ignored.

Written under CDSFL note standard v1.2 (14 May 2026).
