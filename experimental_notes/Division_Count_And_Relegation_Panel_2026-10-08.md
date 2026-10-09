# How many divisions a promotion ladder should have, and what relegates a model

2026-10-08, 17:13 BST

## Summary

A 2 seat panel answered this question in 2 halves, blind and then jointly, over 4 dispatches on 2026-10-08. No paid dispatches were made. The round settled 3 of its 4 questions, found that the fourth has no answer as posed, and overturned 3 claims made by the orchestrating model in the brief that framed it.

The resolution of the fourth question is the most important result. Relegation on sustained degradation cannot be measured at all without an anchor set of items whose difficulty is fixed externally and which are re-run every assessment window. This is a symbolic fact rather than a tuning difficulty. The composition of the 2 proposed statistics does not solve the problem, it detects when the problem is unsolvable and declines to answer.

## What the round asked

3 things, all raised by the project founder. Whether the number of promotion divisions can be derived at the start of an experiment from the relative complexity of the task and the resources available. Whether the cost of a taller ladder rises monotonically with the number of divisions, as a theorem or only as an observed pattern. And how a model is relegated when it degrades over time, with the founder's standing guard that a run of failures on hard problems must never demote a capable model, and that a tally of successes must never be mistaken for improved capability.

## The gate family question, settled, and the framing was wrong

The brief posed a choice between randomised promotion gates, which make the cost curve provably monotone, and deterministic gates, which are reproducible but make the curve non monotone. The joint round showed this is not the choice.

A deterministic gate that reads which attempts succeeded, rather than only how many, reaches statistical power 0.9833784264 at size 0.0099919656 against a randomised optimum of 0.9834296545. The shortfall is 5.1 times 10 to the minus 5, which is negligible. A gate that reads only the count of successes reaches 0.9298091736. So determinism costs almost nothing. What costs is a different property called exchangeability, meaning that the verdict depends only on how many attempts succeeded and how many were made.

An order reading gate violates exchangeability, because 2 models with identical records of successes and attempts would receive different verdicts depending on the order in which their successes fell. That is a concealed coin toss, and it contradicts the project's standing rule that capability is measured as successes over attempts and nothing else.

Adopting both properties, determinism and exchangeability, settles the matter. Gates become thresholds on the number of successes, the cost curve is not monotone, and the number of divisions is priced by a scan over the budget. The price of this choice was measured at the project's own committed operating point and is 0 additional attempts. The deterministic minimum is 19 attempts and the randomised minimum is also 19.

## The division count formula, settled, and there was only ever 1 formula

The 2 blind replies produced formulae that appeared to disagree, one doubling a quantity called the arcsine span and the other not. The doubling cancels exactly, because doubling the span also doubles the critical value it is divided by. Both forms give an identical bracket of 1.228677 at 19 attempts over a resolve rate span of 0.50 to 0.90.

What genuinely remains open is which error quantity is held fixed, a per side error rate or a two sided one. An independent check by the orchestrating model found that one algebraic form matches an equally spaced per side arbiter at 4 of 6 sample sizes while the other matches a two sided arbiter at 4 of 6. Both seats were therefore correct under their own convention, and the brief failed to state which convention applied. That omission was the orchestrating model's.

One result is robust under every convention tested. At 19 attempts of evidence per model, over a resolve rate span of 0.50 to 0.90, the number of supportable divisions is 1 or 2. The project's committed promotion rule assumes 5. A 4 division ladder at that span requires roughly 300 attempts of evidence per model per assessment window.

## The cost scan, settled, and both blind positions were wrong

One blind reply held that the cost objective always returns 2 divisions and is therefore useless. The other treated it as half of a 2 sided derivation. Neither survived. The objective is not confined to 2 or 3 divisions, and there are budgets where 2 divisions are not feasible at all under a per gate attempt ceiling. But the objective takes no argument for the number of attempts available, so it cannot track resolution and cannot derive the number of divisions. Its role narrows to pricing candidate counts below the resolution bound and taking divisions that cost nothing.

## Relegation, which has no answer as the brief posed it

The brief asked the panel to choose between a statistic that compares a model to its peers and one that compares it to a model of item difficulty, or to compose them. One seat showed that neither measures the intended quantity. In the standard difficulty model only the difference between a model's capability and an item's difficulty enters, so a capability drop across the whole roster and a difficulty rise across the whole task stream produce identical distributions on every outcome. The orchestrating model verified this 3 ways, with symbolic algebra returning exactly 0, a constraint solver returning unsatisfiable on any separating value, and arbitrary precision arithmetic returning 0 difference across 27 test points.

That seat's reported measurements, which the orchestrating model has not re run, show the consequence. The peer comparison always attributes the ambiguity to a hardening task stream and is blind to a roster wide decline, detecting it 0.0190 of the time against its own false alarm rate of 0.0475. The difficulty model always attributes the ambiguity to decline and demotes a perfectly stable model 1.0000 of the time when its difficulty estimates are stale.

The other seat, working independently, measured a composition of the 2 mechanisms that weakly dominates each alone in every tested regime and strictly beats each in 1 regime. Peers govern where a group of models shares the same task stream. The difficulty model governs where difficulty is calibrated and no such group exists. Where neither condition holds, the composition declines to issue a verdict. Its reported figures show the difficulty arm raising false alarms 1.0000 of the time when difficulty is uncalibrated against 0.0167 when it is calibrated.

These are the same finding reached from opposite directions. One seat's anchor set and the other's calibration share are the same object, a pool of items whose difficulty is fixed externally and which are re-run every window. With such a pool, relegation is locally identified. Without one, the correct output is no verdict at all rather than a statistic that substitutes an assumption for a measurement.

## Both seats corrected their own specifications

Each seat killed claims of its own with its own falsifiers and repaired rather than reverted them. One replaced a 2 sample separation formula with a 1 sample form after its falsifier rejected it, and reported its own transient outage bound as unsafe as stated. The other found that the peer comparison as literally specified in the brief, against a majority of division peers, breaks the test's statistical null under a drifting task stream and raises false demotions to 0.5167. Pairing against 1 randomly chosen peer per item repairs it.

That correction lands on the orchestrating model's own earlier simulation, which reported 3.65 percent false demotion under a hardening stream against 98.35 percent for a simple absolute threshold. That simulation paired against a single peer, which is the repaired form rather than the specified one. The number describes a mechanism the brief did not specify, and the specification text was defective irrespective of which figure stands.

## A separate finding about the project's own measurement apparatus

The formula for the number of divisions needs the gap between the weakest and strongest measured performance, 0.50 to 0.90 at the figures used here, as its measure of relative complexity. Those rates can only come from findings that reach a confirm or refute verdict. Measured across the archive, findings in the statistics domain reach a terminal closed status 0.7603 of the time, with a 95 percent interval of 0.7341 to 0.7847, against 0.4003 for the software domain, interval 0.3740 to 0.4272. The difference is 0.3600 with an interval of 0.3233 to 0.3967. An exact test gives odds of 4.7516 at a probability of 3.87 times 10 to the minus 72, with a second exact test and a proportion test agreeing.

The consequence is that 96.84 percent of all adjudicated outcomes come from a single domain, with an interval of 0.9526 to 0.9790, even though the underlying corpus is nearly balanced at 1304 software findings against 1093 statistics findings. So the span feeding the number of divisions is measured on one domain while the intended workload is not. The same gap makes the founder's separate hypothesis untestable, that different models have different domain strengths. 3 independent instruments agree that domain specific skill is not established in this archive, on 2 to 8 statistics observations per model.

## The 5 decisions that belong to the founder

1. The 2 gate properties, determinism and exchangeability. Both seats now recommend both. The measured price is 0 additional attempts at the committed operating point. Accepting both closes the gate family question permanently.

2. The error convention for the division count, per side or two sided, and its level. At 2000 attempts of evidence this is the difference between 13 divisions and 11. This is a convention rather than a measurement, and the brief should have stated it.

3. A single false alarm proportion for relegation, for example 0.05 on a stable model. Both decision thresholds are then solved from it rather than chosen.

4. Whether an anchor set exists, meaning a pool of items with externally fixed difficulty re-run every window. This is a precondition rather than a parameter. Without it, relegation remains unspecified rather than shipping an assumption dressed as a measurement.

5. Whether to repair the adjudication gap. Until findings outside the software domain reach a verdict at a proportion closer to the software domain's 0.5268, neither the domain strength hypothesis nor the resolve span feeding the number of divisions can be measured.

## Dispatch record

4 dispatches, 2 seats, 0 paid. Blind half: 13415 characters in 1305.4 seconds with 36 tool calls, and 18606 characters in 1826.8 seconds with 46 tool calls. Joint half: 13064 characters in 2426.4 seconds with 38 tool calls, and 22167 characters in 2550.6 seconds with 39 tool calls. 3 of the 4 exceeded the 1800 second ceiling that stood that morning, so the round would have produced nothing at the previous setting. The ceiling was raised to 3000 seconds on a survival estimate that corrected an earlier figure computed on censored data.

Written under CDSFL note standard v1.7, 26th of August 2026.
