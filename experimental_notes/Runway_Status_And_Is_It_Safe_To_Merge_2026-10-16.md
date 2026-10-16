# Where the runway stands, and whether it is safe to move this work to main

2026-10-16 12:51 BST

## Your rulings are recorded and the decision queue is now empty

All 11 remaining decisions carry your ruling, and the morning report reads 0 decisions needing you against 16 items of outstanding work, each showing the date you ruled it. The severity-gate provenance question is struck permanently and now has a guard that calls the generator rather than reading its output, so it cannot return.

You were right that it was a repeat, and the project's own record says so. The memory note of 2026-10-06 reads "the removal is reverted, on his 3rd or 4th rejection of it", quoting you, and records that the commit which removed the gate quoted you approving it while that quote existed only in the commit's own code comment and in 5 panel documents all dated after it. No source for the approval ever existed. Putting it to you again made it the 5th time. The repair also works: 20 tests pass, and executing the code rather than reading it confirms the severity test is inside the blocker counter.

One correction on your coherence-budget recollection, because the record differs. On the recalibration itself you had not ruled; on the 15th you wrote "once you tell me what the coherence budget recalibration is, I will clearly be in a better position on whether or not to rule it should be fixed." What you had ruled, and are remembering, is the adjacent point now attached to it as a constraint: the operational directives are not to be trimmed. Today is the first ruling on the recalibration, and it carries that constraint.

## The remaining runway, unchanged by last night

Last night's work was validation and repair. It did not advance the numbered stages and should not be counted as if it had.

Stage 1 has 2 items left. Item 1.6 is the merged-finding semantics, which either folds or stops claiming to. Item 1.7 is the replay of the earlier experiments through the repaired accounting, which is Stage 1's exit test, costs no money and no model time, and whose instrument already exists in the repository. That is the nearest actionable thing on the whole runway.

Stage 2 has 3 items and needs one live run between them: the immune duplicate auto-reject, preserving tool verdicts through synthesis, and validating both on a single physics run.

Stage 3 has all 7 items outstanding. Six are built and have never been run, and all 6 wait on the single decision about whether 3 of them can still be reported as blind exams, given that their articles and answer keys were briefly on a public branch. That was asked for on the 8th of August and remains the longest-standing open item in the project. The seventh, the capstone, is not built.

## The migration, surveyed rather than estimated

The branch is 245 commits ahead of main and main has 1 commit we lack, so this is a merge and not a fast-forward. 1,244 paths differ, counted at commit b1f73115. Of those, 1,203 are applicable to main, which is 96.7042% on a 95 per cent interval from 95.5595% to 97.5613%. The count drifts upward with every commit, so it is about 96.7% as of this commit rather than a fixed figure. Your suspicion was right: the overwhelming majority of what was learned transfers.

The simulation surface is 35 paths, 2.8135% on an interval from 2.0299% to 3.8877%, unchanged at exactly 35 across every re-measurement, and it divides into 3 kinds.

**Two entry points exist only to run a simulated experiment:** the stand-in dispatch shim and the launcher that runs a simulated experiment. Both are additive and inert on main unless something invokes them, and nothing in the live path does. My view is that they should go to main, because the ability to rehearse a run without spending money is a capability worth having there, not a branch artefact.

**Six fingerprints belonging to the stand-in seats** record what the simulated seats did. They are keyed by labels carrying the mandatory simulation suffix, which the live runner never dispatches, so they cannot be read by a real experiment. Harmless either way.

**27 simulated run artefacts** under the logs tree, totalling 174,921 inserted lines. These are the experimental evidence for the shakedown and the whole programme of study, so I would carry them: a result whose evidence lives only on a retired branch is a result nobody can reproduce. The cost is repository size, and that tree is already 776 megabytes on disk.

## The two things that must be dealt with before the merge, not after

**First, and this is the only genuine contamination.** Five real paid-seat fingerprints differ from main: the ones for CC2, ChatGPT, Codex, Gemini and DeepSeek. In each case exactly 2 fields moved, the experiment name and the timestamp, and they now record that the seat was last seen in a simulated run on the 3rd of October. No measured value moved at all; the recorded capacity is identical on both sides. So this is a provenance smear and not a corruption of capability, and it must be corrected before the merge or main will carry 5 paid seats whose records name a run that never dispatched them.

It is also evidence that the repair worked. Those files were last touched on the 4th of October, 11 days before the fix for this landed, and last night's 3 runs moved only the stand-in files. So the defect is historical, the fix held, and what remains is cleaning up what the defect left behind.

**Second, and this one is yours to decide.** The immune memory now holds priors learned from 6 experiments. Three of those carry the live marker in their names and 3 are the simulated runs from the last 2 days. Carrying that file to main means the live runner begins its next real experiment with priors that are half simulated. The numbers are not fabricated, but they were produced by stand-in models rather than by the paid panel, and the memory is read to adjust real decisions. Three options: carry it as it stands and accept that, reset it to the 3 live experiments only, or carry it and record the provenance explicitly so a reader can see which half came from where. I would reset to the live 3, because the memory's whole value is that it learned from real evidence.

There is also one small reconciliation. Main's single extra commit touches only the project directive file, and both versions carry the Wolfram attribution correction, so the merge needs the 2 wordings reconciled rather than a correction rescued. I initially read that diff as main holding a correction we lacked, which was wrong.

## My view

Yes, it is safe, with the fingerprint correction done first and your decision taken on the immune memory. Nothing else in the 1,244 paths changes live behaviour in a way that depends on simulation. The runner repairs, the composer repair, the guard that routes a claim to its checking tool, the note machinery, the report generator, the marker schema and every test are all substrate-neutral: they fix how findings are routed, recorded and reported, not who produces them.

I would do it in this order. Correct the 5 fingerprints. Take your ruling on the memory. Merge to main. Then run the Stage 1 replay there, because it costs nothing and it is the exit test that tells us whether the repaired accounting reproduces the archive. If it does, the migration is validated by the cheapest possible instrument rather than by assertion.

The approved fixes from your annotations are not yet built. That is the next body of work, and it is substantial: the mathematical guard, the coherence recalibration with its directive constraint, the forward normalisation of recorded identifiers, the 7 smaller defects and the 869-term vocabulary backlog.

Written under CDSFL note standard v1.7 (26 August 2026).
