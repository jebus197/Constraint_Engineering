# The Discharge Rule, Stated In Full, With Its Alternative


2026-09-05, Saturday.


## Why This Document Exists

The founder was asked to approve a rule that was never written down. The exact objection was that a rule with teeth sounds like a rule worth backing, but that nothing can be approved when neither the rule nor its alternative has been stated. That objection is correct and this document answers it. Both options are written out in full below, in the form they would take if adopted, so the choice is between 2 stated things rather than between a description and nothing.


## The Problem Both Options Are Trying To Solve

A reduction claim is a statement of the form: this complicated expression X becomes this simpler expression Y when condition Z holds. The mathematical appendix contains at least 21 of them. They are the load-bearing statements of the whole model, because they are what makes the model comprehensible: each one says a general form collapses to a familiar one in a special case.

The problem is how such a claim earns the label CONFIRMED.

Until now it could earn that label 3 ways: someone proved it, someone checked it at a few points and it agreed, or someone wrote a sentence saying it had been verified. The third way is not evidence at all, and the second is weaker than it looks.

Here is what that permitted, all measured on 2026-09-04 and 2026-09-05. The appendix carried many statements that something had been verified with symbolic algebra. Exactly 1 test file in the entire suite imported the symbolic algebra library, and it tested a calibrator rather than any appendix claim. One such statement, a constraint on coupling constants attributed to symbolic verification in March, is simply false, and 4 separate reviewers reproduced its falsity. Separately, 3 assertions in the test module written to fix this were substitution tautologies: they subtracted an expression from itself and would pass for any expression whatsoever, including the constant 42.

None of that was dishonesty. It is what happens when the vocabulary does not distinguish between checked and proved.


## Option 1. The Discharge Rule

Adopt this as the verdict vocabulary for reduction claims:

CONFIRMED. Permitted only when the residual, meaning X minus Y, is shown to be exactly zero across the whole declared scope, by symbolic proof or by exhaustive enumeration of a finite scope. Nothing else earns this label.

REFUTED. One counterexample suffices, and it may be found by sampling. This asymmetry is the entire point: a single case can destroy a universal claim, while no finite number of agreeing cases can establish one.

SAMPLED. Agreement observed at a stated number of points, recorded with that number and with an interval. This is real information and is kept. It is never promoted to CONFIRMED.

UNDISCHARGED. No attempt was made, or the attempt did not complete.

Two conditions attach to it.

First, the scope must be declared before the simplification is proposed, not after. A scope chosen once the answer is known can always be drawn around the cases that happen to work.

Second, and this is the amendment that makes the rule survivable, the rule governs identity claims only. A parameter estimate is not a reduction claim. The Duane curve fit and the burst term are measurements of the world, were never candidates for symbolic proof, and keep their existing empirical vocabulary untouched. Without this condition the rule would forbid the appendix's only tie to real data, which would be a worse outcome than the problem it fixes.

What it costs. Some claims that are currently labelled CONFIRMED would move to SAMPLED or UNDISCHARGED. That is not a loss of knowledge, only of unearned confidence, but it will make the record look worse before it looks better, and some of those downgrades will be to work that is in fact correct.

What it buys. Every failure listed above becomes impossible to record as a confirmation. A sentence claiming verification stops counting as verification.


## Option 2. The Alternative, Which Is The Status Quo Written Out Honestly

Keep the present arrangement, stated plainly: CONFIRMED may be awarded on a symbolic proof, on sampled agreement, or on a written assertion that something was checked, and the record does not distinguish between them.

This is not a straw man and it has a real argument behind it. It is flexible, it never blocks work, and it does not require anyone to relabel existing claims. The project has run this way throughout and has still produced correct mathematics, because the model itself has survived every serious attack on it.

What it costs. It produced the 4 failures listed above within a single 48 hour window, and none of them was caught by the test suite or by the falsification pass, which are the 2 mechanisms meant to catch exactly this. All 4 were caught by other models reading the work.

What it buys. No relabelling, no new obligation, no downgrade of anything already recorded.


## A Worked Example, So The Difference Is Concrete

Take the appendix statement that the correlated Ising branch reduces exactly to the independent product when all coupling constants are 0.

Under the status quo this could be marked CONFIRMED by checking it at a handful of parameter values and observing agreement, or by writing that it was verified.

Under the discharge rule it is CONFIRMED only by proving the residual is identically 0. It happens that this one is genuinely provable, and it was proved on 2026-09-05 with 2 independent tools which agree: the exponent is 0, so the exponential factor is 1, and the normalising constant is 1. So this claim keeps its CONFIRMED label and gains an executing test.

Now take the neighbouring statement, the coupling constant bound. Under the status quo it was marked as verified by symbolic algebra in March and carried that status for 6 months. Under the discharge rule it could never have been marked CONFIRMED, because no proof exists, and it is false.

That is the whole difference, in 2 adjacent lines of the same document. One claim survives the stricter rule unchanged. The other could not have acquired its false status in the first place.


## What Is Being Asked

A choice between option 1 and option 2, and if option 1, confirmation that the parameter estimate exemption is included. There is no third option being withheld.

Nothing has been applied. The appendix corrections made today are separate and were made under a different ruling.

Written under CDSFL note standard v1.7.
