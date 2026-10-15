# Status, the decisions waiting on you, and what I recommend

2026-10-15 12:51 BST. Written for the founder. This is a discussion document, not a plan already in motion: nothing below has been started.

## Where things stand

Both free runs ran and both converged cleanly. Run 1 reached the hardened gate at round 3 of a 10-round budget with 22 findings in 82.4 minutes; run 2, identical except that the section 7.7 severity was DECIDING rather than recorded, converged at round 4 with 19 findings in 57.2 minutes. Both hit gamma_critical 1.000 sustained over 2 rounds with a leave-one-out minimum of 1.000, both ended with 0 unresolved criticals, both reached a cumulative critical count of 12, and round 0 produced exactly 14 findings in each. That is 2 of the 3 consecutive clean convergences the success criterion asks for.

The specification arrived whole for the first time: 22 of 22 HARD blocks reaching every seat, against 0 of 22 before the repair.

3 fixes from the night before are confirmed working in a live run rather than asserted. The decomposition futility guard held 24 of 24 decisions across all 6 seats with 0 splits, so the confound that would have force-split every simulated dispatch while leaving paid seats untouched did not fire. The round-budget advisory fired into a round log for the first time and correctly declined to project. And the directive repair delivered without breaking convergence.

## A correction to my own framing, which you should have before the rest

I have been reporting that the programme went from 5 outstanding measurements to 1. That is true as bookkeeping and it oversells the position.

Of the 12 measurements, 1 is outstanding (arm5) and 11 carry a result. But a keyword scan over those results flags 7 of 12 — 58.3333%, Wilson [31.9511%, 80.6740%] — as carrying a BOUND rather than a figure for the effect, rate or behaviour that arm was written to establish. That scan over-flags, and the considered reading is narrower: **2 could not be answered as asked at all**, and **3 more carry a named bound on part of what was asked**.

The 2 that could not be answered: in_round_clearance cannot be read from a clean run, because the form it looks for can only appear when an unconfirmed critical is waiting and a clean convergence leaves none. And the coherence-budget recalibration cannot be driven from runs at all, because it is inert on 3 independent layers.

The 3 carrying a bound: the severity specification's key property was never exercised; the Haiku classifier's PRIMARY mode was never entered, because that depends on the software domain and both runs were mathematics; and the invariance probe's single eligible falsifier returned indeterminate.

"A demonstrated reason something cannot be measured in this configuration" is still information, and in 2 cases it is the most useful thing the runs produced. But it is not the same as having answered the question, and I should not have let one number stand for both.

## The sharpest result, and it is a negative one

Section 7.7's whole point is that a disproved finding scores zero regardless of what the model claimed — a tool outcome annihilating the model's number is what makes it structurally unlike a vote. Across both runs, **0 of 41 findings carried a disproved verification**, 95 per cent interval 0 to 8.5668 per cent. So the annihilating case never arose and the specification's distinguishing term could not bite.

I re-checked that after it looked contradicted, because both runs show 2 findings marked REFUTED. The fields differ: the specification reads the falsifier's verdict, not the finding's status. Confirmed at 2 moments by 2 independent routes.

And it is the confinement defect seen from the other end. A finding reaches a disproved verification only when its falsifier runs and refutes, and the confinement guard was refusing falsifiers permission to read their own review target 18 times per run. That is now fixed, so the next run is the first that can test the key property at all.

## What I got wrong today

Three things, because they bear on how much weight to put on the rest.

My lint-ratchet comparisons were unsound. The linter is path-sensitive — its standard-stamp rule only fires for a file under a directory named experimental_notes — so comparing a working file against a bare temporary copy silently drops a finding and reads as +1. I chased a finding I had not created and deleted good prose to fix it. The paragraph is restored and the lesson recorded.

My first check that run 2's severity switch was actually live counted 52 matches that were all the run's own name, which contains the string I was grepping for. The real check is a line where the deciding layer states its own mode.

And fixing one defect broke its own producer, because the producer's verdict required the defect to be present. It now reports the repair instead. The same thing had happened to the fable seat's script on the same day.

## The decisions waiting on you

There are 4, and none of them is more work for me. Each has one recommendation.

**1. The coherence-budget recalibration.** It is inert 3 ways: nothing calls it, it changes a value that lives only in memory, and handed a real run's logs it returns its own existing defaults because none of the 61 recorded entries carries the 2 fields it reads. The arithmetic inside it is sound — given data in the documented shape it moves the first seat's budget from 0.02 to 0.0571 — so this is a mismatch between what the runner writes down and what the calibrator expects to read. The repair means emitting 2 extra fields per dispatch into every run's own records, which changes what every future run writes, so it is a replay-invalidation decision rather than a repair I should take on my own judgement. Until it closes, the lean-versus-full comparison that every proposed directive cut has been gated on since the 18th of July cannot be run.

My recommendation: authorise it, but fold it into one batched change alongside anything else that alters run output, so the replay cost is paid once rather than twice.

**2. The paired baseline, arm5.** Its core assumption still holds — its target is byte-identical at the old commit and today, 3,498 bytes with the same checksum — but its design names a run from the 3rd of October as the comparison arm, because that run WAS the head of the branch when the design was verified. The branch has moved 141 commits since, 24 of them touching the runner and 3 the composer, including the rulebook repair that arm5 exists to evaluate. So it is now 2 free runs rather than 1 if it is to speak about the runner and composer as they currently stand.

My recommendation: run both arms, and run them after the third convergence rather than before, so what is evaluated is the runner and composer you will actually keep.

**3. The 7 board failures where the archive grew.** Three test suites pin a snapshot of the archive, and 2 runs landing moved it: the immune memory now records 5 experiments where its suite describes 3, with a flaw-class weight moving from 0.0724 to 0.0594, which is immune persistence doing exactly its job. I have not re-pinned them, because deciding what the baseline should be after a run lands is a judgement about what the baseline IS, not a repair.

My recommendation: make each suite derive its baseline from the archive rather than pin a number, and accept that doing so weakens them slightly as regression detectors. Re-pinning to 5 runs just moves the same problem to the next run.

**4. The in-round clearance arm.** It asks whether the unresolved section elicits the identifier-addressed falsifier form at all, and a clean convergence is precisely the state in which the question cannot be asked. The better the runs go, the less readable it becomes. Three options are on the record: accept it as unreadable on clean runs and read it only from runs that stall; seed a run with a known unconfirmable critical; or replay the 175 attributed blockers from the archive through the repaired summary and measure elicitation against the corrected prompt rather than a live run.

My recommendation: the third. It is free, it needs no run, and it measures the elicitation the repaired summary was supposed to change rather than waiting for a run to misbehave.

## What I would do next, in order, on your go-ahead

1. A third free run on the same target, unchanged. It completes the success criterion, and it is the first run in which a falsifier can reach a refutation, so it is also the first that can exercise the severity specification's key property. That single run answers 2 open things at once.
2. The archive replay for the in-round clearance arm, which needs no run and can go alongside.
3. Whichever of the schema change and the baseline decision you rule on, batched together if both.
4. The paired baseline last, for the reason above.

I would not start the third run without your word, because the last 2 cost about 2.5 hours of your machine and you asked for 2.

## The board, plainly

33 failed against 1 before the runs, and 24 of those 33 were mine — producers ignoring the help flag, a script doing its work at import time so it could not be inspected, a note carrying 26 figures while naming no producer, citations pointing at files nobody can open. All 24 are fixed. Of the 9 remaining, 1 is red because the day created more entries than it closed, 1 is red because greening it would mean rewriting experimental evidence, and 7 are the archive-growth decision above.

The lesson I would draw is procedural: I wrote 11 producers and 2 guard files in a day and ran the cheap convention checks only at the end. Running them as each producer was written would have caught 24 failures one at a time instead of in a heap.

Written under CDSFL note standard v1.7 (26 August 2026).
