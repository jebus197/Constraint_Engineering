# Prediction for the next full suite, written before the run — 2026-11-06

Against `resources/suite_record.json` at `e0feed27`: 15,580 passed, 17 failed,
37 skipped, 7,845.45 s, pytest exit 1.

## Sequencing, and why it is not optional

The detector widening lands FIRST. A 2-hour measurement of a tree I am about to
change measures nothing I will still have. That is the same error as quoting a
figure whose producer has since moved.

## The 17, and what is expected of each

| n | file | expectation | basis |
|---|---|---|---|
| 12 | `test_an_interval_rests_on_two_routes_2026-11-03` | **PASS** | its subject `is_any_external_citation_verified_2026-11-04` was repaired (12 failed → 19 passed locally), AND the detector blindness that re-reddened it to 13 is widened in the same commit |
| 2 | `test_the_morning_report_is_generated_2026-10-12` | **PASS** | both were the line ceilings; now derived per item; 22 tests pass locally |
| 1 | `test_task_list_burndown_2026-09-11` | **FAIL, correctly** | it reports a true state — the branching ratio's upper bound sits above 1 — and nothing tonight closed entries |
| 1 | `test_live_notes_are_reproducible_2026-09-10` | **PASS** | its failing node is `test_none_carries_a_figure_without_a_source`, and the scan it runs now returns **0 of 87** live notes carrying a figure with no source, Wilson [0.0000%, 4.2288%], Clopper-Pearson [0.0000%, 4.1515%], routes agreeing to 0.0e+00. Tonight's 3 new notes are among the 87 and clean; a FULL_RECORD is exempt as a transcript by the guard's own rule |
| 1 | `test_open_brain_assessment_2026-09-10` | **PASS** | repaired in `624686db`: the guard was OUTGROWN, asserting `hi < 0.6` on a coverage that had risen to [0.476717, 0.604188]; restated as a straddle pin, since the interval contains 0.5 and so shows neither a clear minority nor a clear majority |

## The numeric prediction

**Failures expected: exactly 1** — `test_task_list_burndown_2026-09-11`, which reports a true state, that the branching ratio's upper bound sits above 1, and which nothing tonight could close because 35 of the 37 live entries await the founder.

**Tightened twice, each time by CHECKING rather than assuming**: `[1, 3]` became `[1, 2]` on finding the Open Brain guard already repaired in `624686db`, and `[1, 2]` became exactly 1 on running the live-notes scan directly instead of waiting 2 hours to be told. So 16 of the 17 are closed, not 14.

Passed at or above 15,580, since 24 guard files were added tonight and none removed.
## What would falsify it, stated so the run can fail

**Any failure in a file not named above.** That would mean tonight's repairs
broke something the commit gate cannot see — and the gate is 128 files of 832,
with 12,048 tests unreached, which is exactly why a full suite is worth 2 hours.

A second falsifier: **failures above 1**. The claim is that 16 of the 17 are
closed, so anything above 3 means at least 1 repair did not take.

A third, and the one I would bet against myself on: **`test_an_interval_rests_on_two_routes_2026-11-03` still
red after the widening.** That would mean its 13 failures were not the
detector's spelling blindness but a real single-route defect in producers I
wrote tonight — in which case the widening is a false fix and must be reverted,
not adjusted.

## Why the record matters more than the run

`sv` CITES this record rather than re-measuring. While it names `e0feed27` with
17 failures, every save for the rest of the project's life quotes a figure
taken before tonight's repairs.

## Outcome of the interval row, recorded before the suite ran

**It passes: 19 passed in 189.49 s, from 13 failed.** But the row's stated
basis was WRONG. It said those 12 would pass because the detector blindness was
widened in the same commit. The widening accounts for exactly **1** of the 13.
The other **12** were a help handler placed at module level, where
`answer_help` exits 2 on pytest's own argv, so importing the module raised
`SystemExit: 2` — a defect introduced in this same session and never traced,
because FOLLOW was run on the detector change and not on the handler
placement.

**So the prediction is right in its conclusion and wrong in its reason**, which
is the shape this project records as a verification passing for the wrong
reason. The runtime is the measurement that settles it: 12.34 s while the tests
were aborting on import, 189.49 s once they execute, a factor of 15.3. A guard
that got faster had stopped testing.

**And it corrects a figure prepared for entry B103 on the gate's growth.** That
file's cost was first measured at 16.59 s, 0.025136 of the gate's 660 s budget,
WHILE SHORT-CIRCUITED. Its real cost is 189.49 s, 0.287106 of the budget —
understated by a factor of 11.4219 — and adding it alone would take the gate to
849.49 s against its own stated 660 s limit.

Written under CDSFL note standard v1.9 (1 November 2026).
