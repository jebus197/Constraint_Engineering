# The Five-Model Verdict on Fixing Gamma — Plain English

2026-05-17 20:13 BST

## What this is

A plain-English account of a five-model panel run to settle how to fix
the gamma measure — the project's depletion metric — given the firm
decision that gamma must not be sidelined. All five models answered
cleanly and independently; the full unedited answers are kept in the
project logs.

## The headline

All five agreed: harden gamma, do not sideline it — and each argued
sidelining it is technically unnecessary, not just disallowed. That
backs the founder's position. More usefully, four of five raised, on
their own, that the proposed fix is itself a form of cooking the books
unless specific safeguards are enforced. So the panel converged not
only on a fix but on the conditions that make the fix honest.

## What they agreed on

Feed gamma the stream of serious, structural findings — the kind whose
exhaustion actually means the work is done — and keep the
all-findings stream as a separate noise diagnostic, logged but not
gating. Recalibrate the pass mark properly and in advance, never tuned
to make the recent run pass. Keep applying fixes back to the file
during a run; do not revert to the old collect-at-the-end method, which
is the documented cause of the system never settling. Gamma stays the
real gate. And the striking number from earlier — the much higher gamma
on the serious-only stream — is not yet trustworthy; it must be
recomputed through the real production pipeline, and it visibly
disagrees with the run's own record of when serious findings stopped.
Three of the five caught that disagreement independently. That caution
stands regardless of the panel.

## The honest centre

Four of five flagged, unprompted, that moving the gate to the
serious-only stream after seeing the recent run miss the bar is exactly
what cooking the books looks like. Their shared answer is the valuable
part: it is a legitimate correction only if the definition of "serious"
is fixed in advance on principle rather than a round number, the pass
mark is recalibrated on held-out data rather than tuned to the recent
run, the production figure is recomputed before being quoted, and the
recalibrated gate is genuinely allowed to fail future runs. With those
controls it is fixing a real specification error; without them it is
cooking. That is the true result of the exercise.

## Where they differed, and how it was resolved

The core was unanimous; three real disagreements were settled using the
no-cooking rule as the deciding test, and that resolution is the
working model's synthesis, stated as such, not a vote count. A clean,
frozen-file calibration phase is kept as the integrity anchor, because
the two models who wanted to drop it both admitted their alternative
introduces tunable knobs that are themselves a cooking risk. The more
complex extended model is deferred until its parameters can be fixed
from real data rather than guessed. The "serious" cut must be the
project's existing hard-versus-soft-constraint definition, validated,
not a bare number — one model's claim that the number is already sound
was recorded as an unverified assertion. And one model alone caught
that on short runs the serious-only stream is too sparse to fit
reliably, so below a minimum count the gate must fall back to the
robust simple count of consecutive rounds with no new serious findings.

## The working model's own position

It agrees with the agreed core — it is its own earlier finding,
independently reproduced by five models, and it is the integrity-
preserving answer. Its one disagreement with a panel member is
rejecting the "the number is already sound" claim as unproven. Its
strongest standing caution, recorded so it cannot be quietly bypassed:
the production recomputation may show the serious-only gamma does not
cleanly clear a properly set bar. If so, the honest outcome is that the
bar holds and the run did not fully settle, to be reported, not
engineered around. The plan is sound precisely because it can still
fail.

## Status

No code was changed; this was analysis and a panel only. The seven-step
fix is real engineering work needing a decision before implementation,
not a quick switch. The recommended next move is a ruling on the agreed
position, then building the low-risk, high-value first steps with the
no-cooking safeguards fixed in advance of any new run.

Written under CDSFL note standard v1.2 (14 May 2026).
