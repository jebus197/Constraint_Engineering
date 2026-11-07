# PRE-REGISTERED PREDICTION for the full suite of 2026-11-07

**Written and committed BEFORE the run starts.** A prediction written after the result is not a
prediction, and this project's own record is that the order is the only thing that makes the
exercise worth anything.

## The baseline this replaces

`resources/suite_record.json` records the last full-suite measurement at commit `e0feed27` on
2026-11-06: **15,580 passed, 17 failed, 37 skipped, 0 xfailed, 7,845.45 s, pytest exit code 1**,
from `python3 -m pytest bench/tests/ -q --netguard-strict`.

## The prediction

**Exactly 1 of those 17 still fails, and it is a decision rather than a defect.**

| what | count | why |
|---|---|---|
| `test_an_interval_rests_on_two_routes_2026-11-03.py` | 12 | one cause, the interval helper resting 1 family on 1 route; repaired and re-measured today at 19 passed in 189.49 s |
| `test_the_morning_report_is_generated_2026-10-12.py` | 2 | the 2 line-limit tests, replaced by per-item budgets derived from the item count on his ruling that he never set a cap |
| `test_live_notes_are_reproducible_2026-09-10.py` | 1 | the 2026-08-16 note's 55 figures now declare that they are quoted from published external work |
| `test_open_brain_assessment_2026-09-10.py` | 1 | a guard OUTGROWN rather than broken; coverage rose to 125 of 231 and the finding is restated as indistinguishable from half |
| `test_task_list_burndown_2026-09-11.py::TestTheListTerminates::test_the_process_is_subcritical` | **1** | **PREDICTED STILL RED.** This is entry B123, the master list no longer being provably finite. It is a decision awaiting him, not a repair available to me, so nothing done since could have closed it. |

**And 0 new failures from the work since**, because the guard that found tonight's 4 operational
defects, `bench/tests/test_operational_scripts.py`, is now fully green at 1,336 passed in 281.77 s,
and both guards added today pass: `test_a_store_key_is_not_an_identifier_2026-11-07.py` at 12 and
`test_the_decisions_file_is_generated_2026-11-07.py` at its own count.

## What would falsify it

* **More than 1 failure** means something since `e0feed27` broke, or one of the 16 repairs does not
  hold under the full suite's shared state when it held in isolation. The project has met exactly
  that: a test can pass alone and fail in a board of 13,465.
* **0 failures** means B123's subcritical check has started passing without his ruling, which would
  mean the list stopped growing for a reason nothing recorded, and is itself a finding.
* **A different test failing in place of B123's** means the prediction identified the wrong
  survivor, and the 16 I claim are closed were not all closed.

## The honest limit of it

The 16 are verified by running them, in isolation, at the tree being committed. The full suite runs
them in a board of over 15,000 with shared state, and that is a different experiment. This prediction
is therefore about the DEFECTS being closed, and a failure arising from board order would refute the
prediction without refuting the repairs.

Written under CDSFL note standard v1.9 (1 November 2026).
