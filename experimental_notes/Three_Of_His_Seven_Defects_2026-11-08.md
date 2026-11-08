# 3 of the 7 defects he ruled on, and 2 of them were already fixed

2026-11-08, Europe/London. ## Producers

`scripts/a4_doors_are_shared_2026-11-08.py` runs the 4 door cases through the real registry. `bench/tests/test_the_band_label_needs_an_estimable_gamma_2026-11-08.py` holds 19 tests over the interpretation label, with 2 of 2 mutations red. `scripts/the_second_board_was_red_for_the_same_reason_2026-11-07.py`, `scripts/b96s_cause_was_wrong_2026-11-07.py`, `scripts/whose_words_does_the_register_say_they_are_2026-11-07.py` and `scripts/what_does_a_new_script_owe_2026-11-07.py` carry the measurements quoted in the companion note for the second board.

Written under CDSFL note standard v1.9 (1 November 2026).

## Summary

On 2026-10-16 the founder ruled on a list of 7 smaller defects with the words "Fix it all". The morning report of 2026-11-08 still showed several of them as outstanding work. Examining 3 of them by running the code rather than by reading its records found that **2 were already repaired and their records had never been advanced**, and that **1 of those 2 would have been made worse by doing what its own record prescribes**. The third is genuinely unrepaired, its cause is a single missing clause, and the predicate needed to fix it has existed since 2026-10-08.

## The counter and the valve already share one severity predicate

The record `A4-counter-valve-severity-mismatch` states that the blocker counter applies no severity test while the only release valve requires a severity of 0.7 or above, so a sub-critical candidate can enter the counter and never leave. Its `needs` field asks for 1 thing: that the counter and the valve share a **single** severity predicate.

They now do, by 2 changes neither of which was recorded against this entry. The severity test was restored on 2026-10-06, gated on a **proven** severity — a recomputation of the stated residual risk from the entry's own stated inputs — rather than on the raw model-assigned number. And on 2026-10-17 the counter became a thin wrapper over a single shared door predicate, after a measurement found the counter returning 4 blockers where a sibling reader returned 11 on the same run.

**Verified by calling it, which matters here because this predicate's docstring was measurably wrong about this exact rule from 2026-09-06 to 2026-10-12.** 4 entries were built by hand and put through the real registry: a critical entry with an unproven severity blocks; a sub-critical entry with an unproven severity blocks, which is the stated design; a sub-critical entry with a proven severity does not; a sub-critical entry marked exhausted does not. The counter equals the size of the shared set, and the routing reader returns a subset of it.

**The probe's own first version reported a defect that was not there, and that is recorded rather than quietly corrected.** It asserted that the counter's set and the routing reader's set must be identical. They must not: the routing reader returns the subset of blockers the ladder would decline to admit, 73 of 167 across the archive by its own measurement, so an empty result on entries carrying no routing history is the right answer. The claim the code actually makes is that both read the same door, so the testable relation is containment, not equality.

**What remains is his and is not a mismatch.** The live instance, a finding at severity 0.6 with no falsifier, still blocks. It does so because an unproven sub-critical severity buys no release, and releasing it would loosen the gate on a model-assigned number — the change he has rejected 4 times and struck permanently on 2026-10-16. A separate reader exists to report that permanent-limbo class instead of releasing it.

## The immune-memory backfill would now re-create the hazard it was written to close

The record `immune-memory-names-2-of-its-5-experiments` states that the live immune memory counts 5 experiments while naming only 2, and that the 3 unnamed ones should be backfilled so the duplicate-ingestion guard can refuse a re-run.

**The store it describes no longer exists.** The live file records 3 experiments and names 3, and the class's own completeness property returns true when asked. His reset ruling of 2026-10-16 replaced that store, and the record of that reset already states that a fresh store has complete provenance by construction, so the reset he ordered for 1 reason closed this defect too.

**Doing the prescribed backfill now would be actively harmful, which is the finding worth keeping.** The check against re-ingestion refuses an identifier it has already seen. Adding the 3 old experiment names to a store that no longer holds their counts would make the guard refuse those runs as already ingested, so a genuine re-ingestion would be silently **skipped** rather than silently **doubled**. A stale remedy is not merely useless; it can invert the protection it describes.

## The gate learned to tell a sentinel from a slope and the diagnostic never did

The record `gamma-band-label-is-applied-to-an-unestimable-gamma` is genuinely unrepaired, and it was deferred for a reason that has since lapsed: a run was in flight, and changing a decay-curve code path mid-experiment would have made that run uninterpretable.

The decay-curve estimator returns 0.0 as a **sentinel** for 4 distinct non-measurements: too few rounds, no novelty at all, fewer than 2 usable points, and a degenerate fit. The band covering 0.00 to 0.20 reads that the decay curve disagrees with state closure and a human audit is recommended. So a gamma that has not been measured is labelled with the worst available verdict.

**Reproduced at the current commit rather than cited from the record.** With 1 round of history the estimate is 0.000, the estimability predicate returns false, and the printed label asks for a human audit. With 2 rounds, the same. With 3 rounds the estimate is 0.358 and the label moves to moderate depletion. **So the referral fires in the first 2 rounds of every run, and the record's own falsifiable prediction — that gamma becomes estimable at round 3 and the label leaves the band covering 0.00 to 0.20 — is now tested and holds.**

**The predicate needed to fix this has existed since 2026-10-08.** It was added for his ruling that the decay curve gates in all cases, it mirrors the estimator's conditions, and a guard of 30 tests already runs both against the same inputs over an exhaustive sweep of short series so the 2 cannot drift. **None of those 30 tests reaches the labelling function.** The gate was taught the distinction that day and the human-facing diagnostic was not, which is why the fix is 1 clause and not a new mechanism.

**It does not demote the decay curve, and that is stated because a standing directive requires it.** No band is removed, no threshold moves, nothing that gated before stops gating, and the new argument defaults to the old behaviour so every existing caller is unchanged. The only difference is that an unmeasured gamma says so instead of asserting the worst band. A diagnostic that cries wolf in the first round of every run is what erodes a load-bearing signal.

## A record-integrity gap found in the same pass

The study file's open-defect records carry no common schema. 4 of 16 express their state through differently named fields — 1 uses a done marker, 1 a not-a-defect marker, 1 a final-state field — so a reader keyed on the usual status field is blind to them. 1 of the 16 carries **no identifier field at all**, which is why the generated morning report prints a bare question mark where its name should be. An entry a reader cannot name is an entry that cannot be ruled on, and giving it a name removes nothing.

**A side-finding buried inside that unnamed record was checked and is sound.** It recorded that the age valve's threshold defaults to 8 while the maximum attainable age in an 8-round run is 7, so the valve could not fire at all — proven 3 ways, by a solver returning unsatisfiable, an enumeration of all 36 legal pairs giving a maximum of 7, and a symbolic derivation giving the general condition. That is repaired: the threshold is now clamped to what the run can reach and the clamp is announced in the log, with the producer cited beside it. It was clamped rather than re-defaulted, so a configured value remains the operator's intent.

## What the record should carry forward

2 of the 3 defects examined were fixed and still being shown to him as work, and the cause in both cases was the same: **the repair was made against the code and never written back to the record that tracks it.** The reverse failure is already named in this project's own lessons, where an entry was updated and the file never touched. Both halves are the same defect, and the asymmetry is worth stating: a stale record costs attention, while a stale remedy can invert the protection it describes.

Written under CDSFL note standard v1.9 (1 November 2026).
