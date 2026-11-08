# Pre-registration: the second full board of 2026-11-07, at `aea4ec9b`

Written 2026-11-07T21:28:18+00:00, with the board at about 460 marks of roughly 15,900 and
1 failure seen. Committed AFTER the result, so the transcript and this timestamp
are what establish the order; nothing below is amended once the board reports.

## The claim

**Exactly 2 failures.**

1. `test_a_blind_round_has_a_joint_round_2026-10-08.py::TestTheDebtCheckRefusesANewBlindRound::test_the_live_registry_blocks_nothing_right_now`
   — entry **B124**, queue state rather than a regression, because the free panel
   round of 2026-11-06 was dispatched blind and its joint half was never run.
   Paying it costs money and needs his authorisation. **Already observed at stream
   position 82**, so this half is confirmed rather than predicted.
2. `test_task_list_burndown_2026-09-11.py::TestTheListTerminates::test_the_process_is_subcritical`
   — entry **B123**, `R = 0.9685` with a 95% interval whose upper bound exceeds 1.
   His decision, not a repair available here.

**And 0 new failures.**

## WHY THE "0 NEW" CLAUSE IS MADE AGAIN HAVING BEEN REFUTED BY 10 THIS MORNING

The identical clause failed on the previous board, and repeating it without
saying what changed would be worthless. What changed, and what did not:

**What changed.** This morning's 10 new failures were 10 of 10 introduced by the
2026-11-06 and 2026-11-07 sessions, and 9 are repaired. The repairs were verified
3 ways rather than 1: each guard alone; **all 9 together in a single pytest
process, 372 passed in 140.61 s**, which is the shared-state question the earlier
prediction left open; and the commit gate's 128-file board green twice, at
`45cea3f9` (2,574 passed) and inside `sv` at `bab7044a`.

**What did NOT change, and this is the honest exposure.** The gate board is 128
files of 835, so 707 files have not run against the current tree since the
repairs. 3 commits have landed since the board being compared against: `45cea3f9`,
`bab7044a` and `aea4ec9b`. They touch `bench/ticket_store.py` (both identity
check sites), 2 test doubles in
`bench/tests/test_a_ticket_identity_survives_a_reword_2026-10-17.py`, the ticket
store's own rows, 4 notes, `resources/RECOVERY.md`, `resources/MEMORY_EXCLUSIONS.md`,
`docs/CURRENT_STATE.md`, `resources/ONBOARDING.md` and 5 new scripts.
**`bench/ticket_store.py` is the exposure that matters**: 29 guards read the
ticket store and only 16 of those are on the gate board, so 13 have not run
against the anchor repair.

## FALSIFIERS, STATED SO THIS CAN FAIL CLEANLY

1. **More than 2 failures** refutes the "0 new" clause. The most likely source is
   1 of the 13 ticket-store guards outside the gate board disagreeing with the
   anchor repair — which would be the same shape as the 2 test doubles that broke
   this evening, and would mean the repair's blast radius was traced too narrowly.
2. **Fewer than 2** means either B124's joint round was run, which it was not, or
   the subcritical measure moved back under 1, which would make B123's premise
   stale rather than this prediction wrong.
3. **A failure in a file touched by none of the 3 commits** would point at
   something older surfacing, and would refute the attribution claim that 10 of
   10 of this morning's new failures came from the repairing sessions.

## THE ERROR THIS PREDICTION IS TRYING NOT TO REPEAT

The previous one verified the repairs and then asserted 0 new failures **without
asking what the predicting session had itself done to the board**. 3 commits have
landed since, so that question is asked above and answered with a named exposure
rather than an assurance. If a new failure appears in a ticket-store guard, this
prediction will have named its own cause in advance, which is the only thing that
makes a pre-registration worth the time.

## STATED LIMIT

This predicts the board at `aea4ec9b` only. It says nothing about whether B123's
and B124's underlying questions are settled — both are his and neither is
answered by any board.

Written under CDSFL note standard v1.9 (1 November 2026).

---

## ADDENDUM 2026-11-07T21:31:12+00:00: THE NAMED EXPOSURE IS CLOSED, AND THE CLAIM IS UNCHANGED

**Written BEFORE the board reported and AFTER the prediction above, which is why
it is an addendum and not an edit. It alters no claim and no falsifier.** It
closes an exposure the prediction named, which makes falsifier 1 SHARPER rather
than weaker: if a ticket-store guard fails on the board now, the cause is not the
one named in advance and something else is wrong.

**2 CORRECTIONS TO THE PREDICTION'S OWN ARITHMETIC, BOTH AGAINST ME.**

1. It said **13** ticket-store guards sit outside the gate board. The figure is
   **14**. 30 guards read the ticket store and 16 are on the board. The missing 1
   is `bench/tests/test_a_restatement_must_see_the_anchor_2026-11-07.py`, the
   guard written this evening for the anchor repair itself — so the count
   silently excluded the newest reader, which is the one most exposed.
2. It said 29 guards read the ticket store. The figure is **30**, for the same
   reason.

**THE MEASUREMENT.** All 14 were run directly rather than waited for:
`python3 -m pytest` over those 14 paths returned **161 passed in 110.05 s**. The
files are `test_a_note_registers_what_it_asks_2026-10-24.py`,
`test_a_panel_request_is_tracked_2026-10-20.py`,
`test_a_question_is_its_own_kind_2026-10-19.py`,
`test_a_restatement_must_see_the_anchor_2026-11-07.py`,
`test_an_identity_is_derived_not_remembered_2026-10-28.py`,
`test_his_duplicate_taxonomy_2026-10-24.py`,
`test_his_ruling_reaches_the_report_2026-10-19.py`,
`test_the_chat_half_raises_only_real_markers_2026-10-28.py`,
`test_the_kind_filter_reopens_the_cross_kind_rediscovery_2026-10-28.py`,
`test_the_kind_filter_three_variants_measured_2026-10-28.py`,
`test_the_subject_tier_splits_questions_from_work_2026-10-28.py`,
`test_the_ticket_gate_states_2026-10-24.py`,
`test_the_type_check_task_is_its_own_task_2026-11-01.py` and
`test_tonights_producers_are_reached_2026-11-03.py`, all under `bench/tests/`.

**WHY THIS WAS DONE RATHER THAN WAITED FOR.** The prediction named a specific
exposure and the board would have answered it in about 2 hours. Running the 14
guards answered it in 110 seconds. Naming an exposure and then waiting for a
2-hour instrument to report on it is breadth standing in for depth: the question
was already specified, so it was already answerable.

Written under CDSFL note standard v1.9 (1 November 2026).

---

## SCORED AGAINST THE FINISHED BOARD: BOTH CLAUSES REFUTED, AND THE SECOND ONE FOR THE SECOND TIME IN ONE NIGHT

**Appended 2026-11-07 after the board finished. Everything above is UNCHANGED.**

**A STANDING WEAKNESS OF THIS PRE-REGISTRATION, NAMED FIRST BECAUSE IT WEAKENS EVERYTHING BELOW IT.** The claim and its falsifiers were written at 21:31:12 GMT, before the board reported at 23:37:42, but the FILE WAS NOT COMMITTED UNTIL AFTER THE RESULT. So its pre-registration rests on file timestamps and this session's transcript, not on the version history — materially weaker evidence than `PREDICTION_full_suite_2026-11-07.md`, which was committed before its run began. A reader who distrusts the timestamps is entitled to read this as post-hoc, and nothing here can refute them.

### The board

15,904 passed, **4 failed**, 37 skipped, 8,036.30 s (2:13:56), pytest exit 1, at `aea4ec9b` on a tree with 0 uncommitted paths, from `python3 -m pytest bench/tests/ -q --netguard-strict`. Recorded in `resources/suite_record.json`.

### The partition against `e796a010`

| | measured |
|---|---|
| of the 11 recorded failures, FIXED | **9 of 11** = 0.818182, Wilson [0.523019, 0.948632], CP [0.482244, 0.977169] |
| of the 11, STILL RED | **2 of 11** = 0.181818, Wilson [0.051368, 0.476981], CP [0.022831, 0.517756] |
| NEW failures | **2** |

Producer: `scripts/compare_this_board_against_the_record_2026-11-07.py`, run with `--baseline HEAD:resources/suite_record.json` because the wrapper had already overwritten the live record. Both interval routes agree to within 1.2e-16 throughout.

### Clause 1, "exactly 2 failures": REFUTED. There were 4.

The 2 that were predicted both held and both are his: the blind round's joint half (**B124**, whose own option 3 predicted this in writing before the run existed) and the subcritical branching measure (**B123**, reporting `R = 0.9685` with 95% interval `[0.8031, 1.1679]`). The prediction was right about which failures would persist and wrong about the total.

### Clause 2, "0 new failures": REFUTED BY 2 — the same clause board 1 refuted by 10 hours earlier

Which stated falsifier fired: falsifier 1, more than the predicted number of failures.

**2 of 2 new failures have subjects first committed 2026-11-07, in this session's own 2 commits** — 1.000000, Wilson [0.342380, 1.000000], Clopper-Pearson [0.158114, 1.000000]. **0 came from the product.** Both guards that caught them already existed: `test_an_interval_rests_on_two_routes_2026-11-03.py` since 2026-11-03 and `test_operational_scripts.py` since 2026-08-15. Producer: `scripts/the_second_board_was_red_for_the_same_reason_2026-11-07.py`.

**THE DECISION RULE ADDS NOTHING AND IS REPORTED AS SUCH.** It was pre-stated as a Wilson lower bound above 0.3400, and the measured bound is 0.342380, so it passes by 0.002380. A control over every reachable value at n = 2 shows 0 of 2 gives 0.000000 and 1 of 2 gives 0.094531, both failing, and only 2 of 2 passes. **So at this sample size the rule is exactly equivalent to asking "were both of them mine?", and expressing it as an interval test dresses a yes/no question in statistics it does not need.** The threshold was also chosen knowing 2 of 2 was the only value that could pass it. The provenance finding stands on the dating evidence, which is per-artefact and checkable; it does not stand on the interval.

### The 2 new failures, named

1. **`scripts/the_gate_board_serialises_the_tree_2026-11-07.py`** carried Wilson on 2 independent routes and Clopper-Pearson on **1** — scipy's `beta.ppf` alone — while the printed "2-route disagreement" compared only the 2 Wilson values. The figure was true of Wilson and silent about the Clopper-Pearson pair on the same line. 2 library names bought 1 cross-check. Repaired by restoring the arbitrary-precision inversion of the regularised incomplete beta as the second route and widening the disagreement to cover all 4 values. **Every printed interval is byte-identical before and after; the only line that moved is the disagreement, 5.551e-17 to 1.110e-16** — which is simultaneously the proof the new terms are reached and the proof no citation went stale. The detector now reports 0 of 26 producers on a single route.

2. **`scripts/the_help_matcher_needed_both_halves_2026-11-07.py` and `scripts/who_made_this_board_red_2026-11-07.py`** each cut a printed listing to a fixed length under a heading that reads as complete. Repaired by stating the remainder. **This is the defect class repaired that same morning in 3 other scripts** — the session fixed the class and then committed 2 fresh instances of it, which is why the guard that caught them is worth more than the guard's author.

### Verification, and why no third board

`bench/tests/test_an_interval_rests_on_two_routes_2026-11-03.py`, `bench/tests/test_operational_scripts.py`, `bench/tests/test_tonights_producers_are_reached_2026-11-03.py` and `bench/tests/test_fresh_clone_is_actually_run_2026-09-11.py` together: **1,429 passed, 0 failed, 617.15 s**. These are the 4 files that reach the 3 repaired producers, established by tracing every reader rather than assumed. A third full board would cost 2 hours 14 minutes of the founder's machine to re-confirm 2 helpers that 617 seconds already confirm.

### What the record should carry forward

The lesson of board 1 was stated correctly and **did not transfer**. Board 2's pre-registration cited board 1's refutation as its reason for believing the clause this time, then repeated it. The asymmetry is the useful part: the hard clause — naming exactly which failures would survive and why — held on both boards, while the easy clause about the predictor's own work was refuted on both. **A prediction about a board is reliable about the code and unreliable about the predictor.** Scope: these 2 predictions and predictions of the same shape.

Written under CDSFL note standard v1.9 (1 November 2026).
