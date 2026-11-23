# BOARD POLICY: THE MEASURED ANSWER

**Date:** 23 November 2026. Companion to the spoken delivery
`Board_Policy_The_Answer_2026-11-23.txt`, re-rendered rather than copied, and to
the archival record `experimental_notes/Panel_Board_Policy_FULL_RECORD_2026-11-23.md`
which holds both seats' complete replies verbatim.

## The answer to the question asked

A full board should run BEFORE each experiment, always. It should run AFTER an
experiment only when something a board guard actually reads has changed, and
that condition should be COMPUTED rather than judged. Both free panel seats,
`cc2` and `fable`, reached that answer independently and from different
reasoning. Testing their shared proposal found 1 gap in it, described below.

## The advisory's central number is wrong

An external advisory states that full board runs now exceed 3 hours. That is
false of the instrument which gates commits. Across 114 determinate recorded
runs in the project's own duration ledger, the longest commit board ever
recorded is 3313 s = 55.22 min, and the number of runs reaching 3 hours is 0.
Producer: `scripts/what_the_commit_gate_actually_costs_over_time_2026-11-08.py`,
re-run 2026-11-23.

The 3.13 h figure belongs to the FULL SUITE of 18,419 tests, a different
instrument that does not gate commits. The advisory conflated the 2, so its
recommendation cannot be adopted on the basis it gives.

## The concern behind it survives, and this is the figure that governs planning

The gate REFUSES 55 of 114 recorded runs = 0.482456, Wilson [0.392806,
0.573250], Clopper-Pearson [0.387886, 0.577960]. Landing 1 batch therefore costs
1.932203 boards in expectation, computed on NumPy and on an exact SymPy rational
in agreement, which is 66.76 min rather than the 34.55 min a single board costs.
About half of all boards refuse, and that is where the calendar time goes.

## Why a cheap layer cannot replace the board

A diff-derived ladder selects guards whose text contains the changed path. But
68 of 332 board guards = 0.204819, Wilson [0.164902, 0.251489], derive their
subject set at runtime through `glob`, `rglob`, `iterdir` or `os.walk`. Such a
guard holds no literal member path, so a newly added member cannot select it
while being exactly the member the guard exists to judge. Seat `cc2` measured
this; the figure reproduced exactly here against the same instrument,
`scripts/which_guards_does_this_commit_risk_2026-11-22.py`.

The board run of 2026-11-23 supplied a live confirmation no panel could have
arranged. It refused with 6 failures across 4 guard files, and all 4 derive
their populations at runtime:
`test_recovery_memory_doc_repairs.py`,
`test_panel_records_are_preserved_2026-09-11.py`,
`test_panel_rounds_have_a_full_record_2026-09-11.py` and
`test_tonights_producers_are_reached_2026-11-08.py`.
No staged file named any of them, so the ladder would have selected 0 of the 4.
The ladder is therefore sound as a pre-filter and unsound as a substitute, which
answers entry B216, the pre-board ladder already selects the guards that refuse,
in the negative for this class.

## Where testing refined the panel's own proposal

Both seats proposed the same mechanism for the after case: a digest of the tree
before and after the experiment, with the post-board required if and only if the
digests differ. Tested, that is insufficient. The guard that failed reads
`~/.claude/projects/-Users-georgejackson-Developer-Projects/memory`, which holds
405 files and lies OUTSIDE the repository, so a digest over tracked paths cannot
see it. A memory file written at 21:59 while the board ran from 21:12 is exactly
what turned that guard red, and a tree digest would have reported no change and
skipped a post-board that was needed.

The condition must therefore be a digest over the populations the guards
themselves walk, at least 1 of which is outside the repository. That is an
addition to the seats' answer, not a reversal of its direction, and it is held
rather than built, because changing when a gate refuses is a change to the gate.

## Why before and after are not the same check

A board BEFORE protects the experiment's VALIDITY: a run on a broken harness
yields a result that must be discarded, and for a paid run the spend is not
recoverable.

A board AFTER protects the RECORD: an experiment writes artefacts into
directories board guards walk, so those guards can turn red with no code change
at all. The night of 2026-11-23 demonstrated that mechanism with no experiment
running: 3 panel directories and 1 memory file were enough to refuse a commit.

The composed policy is therefore justified on a named property rather than on
the observation that both halves can be done. Before always, at full board;
after only when the digest over the guards' own populations has changed, which
costs seconds. Where it is unchanged the post-board is skipped, so the policy
costs less than running both unconditionally and catches a class that running
only the pre-board misses.

## What is still owed, and what is not claimed

The decision on the after half belongs to the founder, because building the
digest condition changes when a gate refuses.

Both seats report that the board's own `--durations=25` table, the 1 instrument
that can attribute board time per guard, was generated and deleted on every one
of 113 boards. The shape of `hooks/pre-commit` is consistent with the claim:
line 1237 exports the option and line 1253 removes the log. The claim is NOT
confirmed by execution here, and the retention repair both seats wrote sits in
their sandbox diffs rather than in this tree. It is the first item of the next
batch.

The 2 seats also disagree with the project's recorded decomposition of board
growth. The record holds 4.0172x total as guard count 2.6111x times per-guard
cost 1.5385x; seat `cc2` reports 4.3357x as 1.4310x times 3.0298x over the
window the ledger actually covers. Both cannot describe the same window, and the
disagreement is preserved rather than resolved, because an aggregate figure
without its window is not a measurement.

Entry B178, every pinned commit-cost figure in both instruction files is stale,
is confirmed again: the pinned mean of 1876.858696 s over 92 boards is now
2073.061404 s over 114, and the pinned refusal count of 44 of 92 is now 55 of
114.

Written under CDSFL note standard v1.9.
