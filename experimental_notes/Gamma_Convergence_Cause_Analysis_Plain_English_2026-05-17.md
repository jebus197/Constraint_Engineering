# Why Gamma Convergence Stays Elusive — Plain-English Analysis

2026-05-17 01:42 BST

A plain-English account of why the γ (gamma) convergence target keeps
proving hard to reach, the actual cause, what can be done, and whether
a multi-model confer round would help. γ is the project's depletion
measure — the number whose rise is meant to signal the review is
running out of new things to find. Written to be read without session
context.

## The direct answer

The elusiveness of γ is mostly an artefact of how the measure is
specified, not the system failing to deplete. The runner has two
convergence tests: the γ ≥ 0.30 threshold, and the one that actually
fired in the recent successful run — three consecutive rounds with zero
new critical findings. They are fed different data and measure
different processes, so γ sitting at 0.267 at a genuine convergence is
expected by construction, not evidence of premature closure. Two
further real but secondary contributors exist. The yardstick is
mismatched to the regime; the underlying analysis is not broken.

## The cause, with an honest correction

The first hypothesis — a pure run-length problem — was disproved by a
direct numerical test (a clean decaying series crosses 0.30 in ~5
rounds; the real run did not). Tracing the code gives a three-tier
cause:

1. **Primary (verified).** `_estimate_gamma` is fed every new finding
   each round, all severities, and fits the cumulative total. The gate
   that fired counts only new findings of severity ≥ 0.7. In the run
   the critical stream went to zero for three rounds (real convergence)
   while minor novelty kept trickling on the small target, so the
   cumulative slope stayed high and γ stayed ≈ 0.27. The two
   instruments answer different questions. The runner's "weak depletion
   — state closure may be premature" label is itself misleading here.

2. **Secondary.** The estimator is global-cumulative, so early
   high-discovery rounds dominate it and a short flat tail barely moves
   it. The 0.30 threshold was calibrated on long runs (an earlier
   16-round experiment reached 0.467) and does not transfer to short
   ones.

3. **Tertiary [SPECULATIVE].** Applying fixes back changes the file
   every few rounds; the standard model behind the estimator assumes a
   fixed defect pool. The appendix's extended model for the
   changing-file case is unimplemented. Plausible further contributor;
   not isolable from this run.

## Viable fixes (one rejected honestly)

1. **Best, simplest-sufficient.** Demote γ ≥ 0.30 from a co-equal gate
   to the diagnostic band it already half is; add ρ (efficiency) as the
   genuineness check. The appendix already states γ and ρ are
   complementary diagnostics, not a single gate, and that γ is
   churn-blind by design. "Zero new critical for 3 rounds AND ρ above
   floor" certifies genuine, non-churn convergence without needing γ to
   reach 0.30.
2. **Complement.** Feed `_estimate_gamma` the same critical-only series
   the gate uses, so the two track the same process; recalibrate the
   threshold.
3. **Longer term.** Implement the re-injection-extended model for the
   apply-back regime (the appendix flags it pending).
4. **Rejected, stated plainly.** A naive recent-window estimator —
   tested directly, swung 0.0–0.43 on small samples, unstable. Not a
   fix.

## Suggestion

Treat this as a measurement-calibration correction, not a hunt for more
depletion. Adopt fix 1; also log γ on the critical-only series
alongside the all-novelty one so the two are comparable; defer the
extended-model work until apply-back is the standard regime. This
removes the false elusiveness without weakening the convergence test.

## On a confer round — independent assessment: not here

A confer is not the right next step. This was a falsifiable
code-and-maths question; direct inspection plus a numerical test
answered it and corrected the first hypothesis — a five-model confer
reasoning without running the estimator would have produced exactly the
unverified narrative the test overturned. The documented framing-bias
of confers and the documented history of the working model steering
them weigh against convening one on a question where it already holds a
view. Higher-value independent scrutiny would be an isolated
adversarial re-examination of this estimator analysis (fresh context,
cold brief) or a second statistical pass. A neutrally framed confer on
the fix-design trade-off is defensible only if that choice stays
genuinely contested after such a check; it is not warranted to
establish the cause, which is already determined.

Written under CDSFL note standard v1.2 (14 May 2026).
