# The Falsification Core Ran. Zero Residue.

2026-08-31, 02:12 BST (UTC+1)

The overnight simulated run converged at round 3, on the two-sided gate, and its post-convergence sweep cleared every remaining finding: 11 cleared, 5 withdrawn, 0 remaining. 25 findings, 78.3 minutes, runner v3.2.

The result that matters is not the convergence, which has now happened three times on this target. It is that the parts of the schema which have never worked in a simulated run all worked in this one.


## What Was Silent Last Night And Is Not Silent Now

Last night's run converged on model agreement alone. Not one finding carried a proof-program, not one fix was verified by execution, and the check that asks whether two models found the same defect recorded nothing at all. Tonight, measured from the run's own artefact:

Proof-programs written: 18 of 25 findings, 72 percent, 95 percent confidence interval [52.4, 85.7]. Last night: 0 of 19. Fisher exact p equals 7.5e-07.

Fixes verified by execution: 20 of 25, 80 percent, interval [60.9, 91.1]. Last night: 0 of 19. p equals 3.3e-08.

The fix-efficacy probe, which asks whether a proposed fix silences the proof-program that demonstrated the defect: 22 of 25 entries carry a result, 88 percent. Last night it reached nothing and left no trace of why. It returned real verdicts this time: 5 fixes cured their own proof-program, 1 did not, 1 was indeterminate, and 15 recorded that no proof-program existed to test against.

Cross-model co-discovery: 11 of 25 findings were raised by more than one panel member, 44 percent, interval [26.7, 62.9]. Across the entire modern arc of 566 findings, that number has been zero. The recorder was written on 23 August, could never match a cross-model pair, and was repaired last night.

For reference, the real experiment 45 on this same target wrote proof-programs for 23 of 39 and verified 24 of 39. The simulation now sits above both, though the difference is not statistically distinguishable at these sample sizes.


## The Discrimination Control Fired For The First Time In This Project'S Life

It asks whether a proof-program fires because of the defect, or whether it would fire regardless. It needs two things on the same finding: the proof-program, and a corrected copy of the file. Across the real experiment 45 and last night's run combined, the number of findings carrying both was 0 of 58.

Tonight 22 of 25 findings carried a corrected copy, and the control ran in every round. Its outcomes: it confirmed discrimination twice, recorded one case where the proof-program errored against the corrected copy and correctly concluded nothing from that, and found one case where a proof-program fired just as hard against a corrected file, meaning it was not testing its claim at all. That last one was escalated to a human and not closed.

That is exactly the behaviour the ruling of yesterday evening was meant to produce. The reversal step that could have silently un-confirmed a sound finding is now behind its switch, and the switch is off, so the control reports without being able to overturn anything.


## The Terminal States Changed Shape

Last night's run reached no terminal state at all. Every finding stopped at an intermediate one. Tonight: 9 closed, 11 confirmed, 5 refuted. Findings were refuted, which requires a proof-program to have been run and to have failed to demonstrate the claim. That has never happened in a simulated run.

Discovery decayed 16, 8, 6, 3 across the four rounds, strictly monotonically, and the decay-curve measure went 0.0, 0.0, 1.0, 1.0.


## Two Problems Found During The Run

The run crashed 55 seconds after its first launch, on a defect of my own making. A note recording that Fable's tuning values are inherited rather than measured was stored in the same table as the values themselves, and was then passed to a constructor that does not accept notes. Fixed so that a specification table can carry a note about itself without breaking anything, because a table that cannot hold its own provenance invites the provenance to be dropped instead. Five tests. The run was relaunched and completed.

The macrophage monitor, enabled for the first time tonight, produced 11 false alarms. It compares each stage's duration against a running median, that median is 0.00 seconds early in a run, and so any genuine model latency of 20 to 97 seconds is reported as a spike of 23,000 to 161,000 times the median at maximum severity. It is advisory by construction and changed no verdict, which is why the run was not paused for it, but it would drown a Bench Run 2 log in noise. It is the first thing to fix this morning.


## What Still Does Not Run

The decomposed-dispatch path is entered on every model in every round and fails immediately, because it does not know how to reach a simulated agent. It degrades to the ordinary path and costs nothing, exactly as predicted in review yesterday. But it means that path remains unexercised, and it is the one that activates at Bench Run 2 payload sizes. It is on the runway.

The seeded pairs for the upcoming cell build-out exams are not vaulted. That is recorded as runway item 4B.8 and is not a blocker.


## State Of The Work

The test suite reports 4599 passed, 0 failed and 0 skipped. All work is committed and pushed, and a state save was completed before the run started. The runner is version 3.2.

Three runs have now converged at round 3 on this target: the real experiment 45, last night's simulation, and this one. The difference is that this one got there by running proof-programs rather than by counting agreement.


Written under CDSFL note standard v1.7 (26 August 2026).