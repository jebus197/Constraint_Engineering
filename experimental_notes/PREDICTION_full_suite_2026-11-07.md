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

---

## SCORED AGAINST THE FINISHED BOARD: THE HARD CLAUSE HELD EXACTLY, THE EASY CLAUSE IS REFUTED BY 10

**Appended 2026-11-07 after the board finished. Everything above is UNCHANGED, because
amending a pre-registration after the fact destroys the only property that makes it
worth having.** An earlier append written mid-run said the second clause was refuted
3 times; that was a partial count taken at 43% of the run and is superseded by the
figures below.

### The board

15,858 passed, 11 failed, 37 skipped, 8,247.78 s (2:17:27), pytest exit 1, at `e796a010`
on a tree with 0 uncommitted paths, from `python3 -m pytest bench/tests/ -q --netguard-strict`.

### The partition against `e0feed27`

| | measured |
|---|---|
| of the 17 recorded failures, FIXED | **16 of 17** = 0.941176, Wilson [0.730180, 0.989540], CP [0.713111, 0.998512] |
| of the 17, STILL RED | **1 of 17** = 0.058824, Wilson [0.010460, 0.269820], CP [0.001488, 0.286889] |
| NEW failures | **10** |

Producer: `scripts/compare_this_board_against_the_record_2026-11-07.py`. Both interval
routes agree to within 1.2e-16 throughout.

### Clause 1: HELD, and exactly

The prediction named **1** survivor and said it would be the subcritical branching
check. The board returned exactly 1, and it is
`test_task_list_burndown_2026-09-11.py::TestTheListTerminates::test_the_process_is_subcritical`,
reporting `R = 0.9685 with 95% interval [0.8031, 1.1679]`. The upper bound is above 1,
which is entry **B123** and his decision.

### Clause 2: REFUTED BY 10

Which stated falsifier fired: the 1st, *"More than 1 failure means something since
`e0feed27` broke, or one of the 16 repairs does not hold under the full suite's shared
state."* It is the first branch, and the something was **this session's own work**.

**10 of 10 new failures were introduced on or after 2026-11-06**: 1.000000,
Wilson [0.722467, 1.000000], Clopper-Pearson [0.691503, 1.000000], decision rule
(Wilson lower bound > 0.5000) UPHELD at 0.722467. Every row carries its own dating
evidence. Producer: `scripts/who_made_this_board_red_2026-11-07.py`. **0 came from the
product.**

### The instrument built to score this would have CONFIRMED the refuted clause

The comparator's 3 refusals — unfinished log, narrower run, missing baseline — all
passed, and it still measured nothing: the suite wrapper overwrites
`resources/suite_record.json` with the board it has just finished, so the comparator
partitioned the board **against itself** and printed `0 fixed, 11 of 11 still red, 0 NEW`.

**`0 NEW` is this prediction's own refuted clause.** An instrument in that state agrees
with whatever prediction it is pointed at. A 4th refusal now fires when the record's
`commit` equals the current HEAD.

### What was repaired, and what the board still owes

8 of the 10 were repaired in this session and verified by re-running their guards:
the 2 help-flag guards, `test_fresh_clone_is_actually_run_2026-09-11.py`, `test_note_standard_v17_enforced_2026-08-26.py`, `test_every_test_file_is_collected_2026-09-01.py`, the source-text census, and both halves of the reachedness check (667 of 667
reached, 100.0000%, CP [99.4485%, 100.0000%]). The gate's declared figure was refreshed
to 128 files and 2,585 tests.

**2 remain and both are his**: the blind round's joint half (**B124**, queue state its
own option 3 predicted in writing before this run existed, and paid work needing
authorisation), and the subcritical measure (**B123**).

### The error, named without generalising past it

The prediction verified the 16 repairs and `bench/tests/test_operational_scripts.py`, then asserted
0 new failures. **It never asked what the predicting session had itself done to the
board.** 2 of the 10 were created by work he had ordered (the panel round, the fold-back);
8 were created by the repairing itself. A prediction about a board must account for the
predictor's own commits to that board, and this prediction did not. The scope of that lesson is
this prediction and predictions of the same shape — not predictions in general.

Written under CDSFL note standard v1.9 (1 November 2026).
