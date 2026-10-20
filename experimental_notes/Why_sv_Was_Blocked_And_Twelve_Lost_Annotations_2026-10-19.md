# Why the save was blocked, 12 lost annotations, and the orchestrator specification

Written 2026-10-19 23:58 BST under CDSFL note standard v1.8, at commit `f0794ad3` on branch `sim/shakedown-2026-09-29`.

## The save was blocked by a question the founder had already answered, and the mechanism that failed was a single line

`scripts/cdsfl_sv.py` wrote its state files and passed all 4 of its own completeness checks. The commit hook then refused with 6 failures. One of them was `test_a_ruled_item_is_not_a_decision_2026-10-16.py`, whose final assertion refuses to let a save proceed while any decision is still owed to the founder. It named 7: entries B24, B29, B31, B33, B34, B39 and the outstanding programme measurement.

An earlier reading of this, recorded as entry B43, proposed deleting that assertion on the ground that it asserted an empty decision list and the project's design contradicts it, because questions accumulate. **That reading was wrong and the founder's own file disproved it.** `Responses/Morning_Report_2026-10-19_GENERATED.txt` carries his verdict on all 7. The assertion was never a snapshot; it is a live gate that refuses to save while decisions are owed, and the correct response was to get them ruled. With his rulings recorded the file returns 17 passed. B43 is withdrawn.

**The real defect was one line, and it is the reason he was asked twice.** `scripts/morning_report_build_2026-10-12.py`'s `decisions()` routed an item out of the decision list on `d.get("ruled")`, where `d` is the AUTHORED DETAIL held in `experimental_notes/data/morning_report_decisions.json`. A task entry's ruling does not arrive there. It arrives on `it`, from the marker's `ruled:` field in the master task list. The merge `{**it, **d}` then carried the date into the OUTPUT record, so anything reading the merged result saw the ruling while the routing predicate did not. A producer and a consumer that disagree, each individually correct, which is the shape the project's `execute-do-not-grep` rule names: reading either half alone shows nothing wrong.

The cost was the founder's time. He ruled on entry B31 on 2026-10-18, writing "Your fix is approved" in `Responses/Review_Stop_And_Declared_Modes_2026-10-18.txt`, and the generated report of 2026-10-19 put the same question to him again. His reply: "Then if I already ruled. Why are you presenting it as a decision required from me again? Again your fix is approved. Do it." **6 of the 7 live decisions were in this state**, and 51 of 173 entries carried a `ruled:` date against 682 annotations on record.

The fix reads both halves. It is guarded by `bench/tests/test_his_ruling_reaches_the_report_2026-10-19.py`, 8 tests, and 3 of 3 mutants are caught: reverting the predicate fails 2 tests, dropping the explicit ruling from the output record fails 1 that `bench/tests/test_a_ruled_item_is_not_a_decision_2026-10-16.py` missed entirely, and routing every item out regardless fails 1.

## He was asked the same question twice in one report, and that is now measured

His second complaint was sharper than a general impression. The report of 2026-10-19 put the serialisation measurement to him as DECISION 5, as entry B34, and again as DECISION 7, as the programme measurement `serialisation_cures_matched_failures`. His annotation on the second: "I literally just answered this above! And I ruled previously!"

Measured on the figures each decision cites, the 2 share 9 figures at a Jaccard overlap of **0.6000** — the entire measurement, namely 1 of 68 rounds, 1.4706%, interval 0.2601% to 7.8710%, 47 rounds for 50% power and 109 for 80%. Computed by hand, by SciPy's Jaccard distance over indicator vectors, and by exact rational arithmetic in mpmath, all 3 agreeing to within 1e-12.

A first attempt to detect this by exact equality of the figure tuples returned 0 duplicates and was the wrong test, because the study item carries extra figures that B34 does not. A threshold of 0.55 rather than 0.50 is required, because a pair whose only shared token is the digit 1 scored exactly 0.5000 on the same data and is not a duplicate. Both cases are now exercised by the guard rather than assumed.

## 12 of the founder's own annotations no longer exist in his file, and 3 are rulings still owed to him

The remaining 4 commit-hook failures are a different and more serious matter.

`Responses/TASK_LIST_48_Hours_And_Rulings_2026-10-17.txt` is **108 lines** long and holds **8** annotations. That was confirmed twice over: by counting lines beginning with a hash character in the raw Windows-1252 bytes, and by `scripts/read_founder_responses_2026-10-11.py`, which returns the same 8. The verdicts recorded against that file on 2026-10-17 name anchors at lines **108, 114, 116 and 120**, which lie beyond the file's current end. The file is therefore shorter than the one the verdicts were taken from. It was replaced, not rearranged. Its modification time is 2026-10-19T07:19:02+01:00.

**The first diagnosis was wrong and is withdrawn.** It was recorded as a line-anchoring fragility curable by anchoring verdicts on his quoted words instead of a line number. Measured, 14 of 16 quote-matching failures are in the same file, so the quoted text dangles as well. Re-anchoring cures nothing when the annotation itself is gone.

**No committed code can have done this.** 22 Python files under `scripts/`, `bench/` and `hooks/` reference that directory and **0** of them contain a write, delete or move call. Every reference is read-only. An ad-hoc shell command cannot be excluded from the record, and is not claimed.

All 12 are now recovered verbatim into `experimental_notes/recovered/Founder_Annotations_Recovered_2026-10-19.md`, held inside verbatim regions so that no linter may alter them. 3 carry the verdict RULING and are questions still owed to him, among them "What are the '94' unsavable blockers?" and a question asking whether a reported collision between 2 seats' findings had been overstated.

**The obvious repair is circular, and that is why it was not applied.** Making those rows resolve against the recovered file would be checking them against a file derived from those same rows. The guard's stated purpose is to stop the record becoming "a list of things I believe he said"; satisfying it with its own output would turn it into a tautology. So the 4 guards remain red and the commit hook continues to refuse.

**The question is short.** Does the founder still hold the original, longer file, in a word processor, a backup, or elsewhere? If he does, restoring it makes all 4 guards honest at once and nothing is demoted. If he does not, the only non-circular option is to mark those 12 rows as carrying a lost anchor, with a second guard asserting that every lost-anchor row has its text preserved in the recovered file. That is an honest demotion rather than a repair, and it is his call.

## The answer to the 94 blockers, which he asked for twice

The figure was never right, and that is the answer.

The authoritative figure is **73 of 167**, not 94 of 212: of 3,020 archived entries across 61 runs, 167 are counted as blockers by `unverified_critical_count`, and 73 of those are entries `_apply_routing` would decline to admit. That is **43.7126%**, Wilson interval 36.4145% to 51.2934%, Clopper-Pearson 36.0626% to 51.5897%, with statsmodels and mpmath agreeing on Wilson and statsmodels and SciPy on Clopper-Pearson to 4 decimal places.

2 independent causes produced the wrong figure. The producer walked the archive recursively and found 74 state files where there are 61 runs, 10 of them inside `sandbox_harvest/` directories, which are archived copies of what a seat saw rather than runs. And 2 predicates disagreed: `unverified_critical_count` held 6 release conditions while `blockers_routing_cannot_serve` held a hand-written copy of 3.

**They block nothing that matters.** Called against each shakedown leg's archived state rather than read from a report: leg 1 returned 0 blockers, leg 2 returned 0, and leg 3 returned 9. Leg 3 converged at round 4 with status HARDENED_CONVERGED and a critical gamma of 1.000, so the gate that closed the run does not read the blocker count at all. 1 of 3 legs affected, Wilson interval 6.1492% to 79.2340%. What such a finding costs is verification depth, because it goes to a human instead of receiving an executed falsifier. Real, but not a blocker.

**His direct question was whether they would block completion of the master task list. They do not.**

This answer was produced on 2026-10-17 and recorded in the ticket store, where he never saw it. An answer that exists only in a registry is not an answer that has been given, which is the same failure as the re-asked decision, running in the other direction.

## The orchestrator: neither objection he suspected was being made

He asked directly whether the claim was that the orchestrator machinery cannot be built to the given specification, or whether the argument was against a bound orchestrator at all. Neither.

The recorded objection, entry B20, was narrower and is about experimental design rather than feasibility. The orchestrator as specified has 2 arms: a repair-adjudication arm, which has an executable criterion today, and a monitoring arm, which has no defined predicate at all. Running both as a single experiment would confound a measurable arm with an unmeasurable one, and across the 3 shakedown legs 77 of 79 adjudications were made by tools rather than by a model's assertion, so a bound orchestrator would be operating in a regime where its own assertions mostly decide nothing. That is an argument for measuring the 2 arms separately. It is not an argument against binding the orchestrator, and the project's position that no model gets a free pass from the harness is not in dispute.

What was missing was the specification, and he has now supplied it in 2 forms. The interface mock-up shows the orchestrator bound by declared constraints displayed alongside it: a stated binding of bounded mode with a tools-decide policy and no prose clearance required, and explicit limits of a high-residual bound of 5, a falsifier budget of 20 runs, and no external tool calls. The orchestrator in the mock-up opens a finding, names the next action, and links out to the findings view. It does not adjudicate.

His second instruction is the harder and more valuable one: that the specification should be derived by examining what the current orchestrating role actually consists of, and written down as a specification; and that alongside a specification for the human in the loop there should be an interaction specification describing how he himself instructs the harness, to be used in the simulated experiments. His reasoning is that these runs are tests of whether the arrangement works, and that if they succeed the bound orchestrator may become the means by which he interacts with the harness as well.

## State

174 task entries: 21 open, 143 done, 2 deferred, 8 withdrawn. 40 of the 44 guards over this work pass. The 4 that fail are in `bench/tests/test_every_annotation_verdict_names_its_evidence_2026-10-17.py`, and they are the only thing preventing the save.
