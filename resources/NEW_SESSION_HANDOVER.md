# NEW SESSION HANDOVER

**Written 2026-11-04. Resume from here immediately; do not wait to be asked.**

## What to do first, in this order

1. Run `rs` as the founder instructed. That is `python3 scripts/cdsfl_recover.py --record-restore`, **capturing and reporting its exit code**, then Open Brain session context, then `MEMORY.md`, then this project's recovery resources.
2. Read `resources/RECOVERY.md`, newest SESSION STATE block. **That block is the state, not this file.** This file only says where to start and in what order.
3. Read `experimental_notes/CDSFL_MASTER_TASK_LIST.md` and `experimental_notes/CDSFL_Agent_Operational_Plan.md`.
4. Then continue at the resume pointer below.

## The resume pointer

**Nothing is owed to the founder before work continues.** The 3 items below are mine, bounded, and each names its own evidence.

### 1. A producer is owed for entry B120's withdrawn Fisher figure
Entry B120 carried `Fisher exact p = 1.108513e-11` and it was **WITHDRAWN on 2026-11-04** because no script produces it and its 2 by 2 table was never recorded. 6 candidate tables consistent with the entry's prose were tested with `scipy.stats.fisher_exact` and none reproduces it; the nearest is `9.526969e-11`. The counts underneath it stand and are checkable: a 1-character fix to the panel disagreement predicate flips exactly 6 of 392 archived replies and 0 in the losing direction. **What to build:** a producer that applies the predicate both ways across the 392 archived replies, states its table explicitly, and computes the test from that table with 2 routes. Then cite it in B120 and remove the withdrawal note.

### 2. Two pre-existing failures were never diagnosed this period
Both were red on the morning board of 2026-11-04 and are **not** regressions from the repairs:
- `bench/tests/test_desktop_mirrors_stay_current_2026-09-10.py::TestTheOrderingActuallyHolds::test_a_drifted_mirror_does_not_refuse_the_commit`
- `bench/tests/test_operational_scripts.py::TestNoScriptSwallowsAnErrorIntoSilence::test_no_bare_or_silently_swallowed_exception_handlers`

The second belongs to a file where **7 of 21 findings were measured as its own false positives** on 2026-11-04, so check whether the checker is wrong before repairing the subject it accuses.

### 3. Then the founder's roadmap, which he stated in his instruction of 2026-11-03
In his order: the orchestrator test, together with research into Meta-Agent Architectures and the Model-Agent Interface; then the B-cell build-out and its exams; then completing the UX.

## What is waiting on the founder, and must NOT be worked around

**29 decisions** sit in `experimental_notes/Decisions_Awaiting_You_2026-11-04.md`. 2 of them are blocking a green board, and the project's own instrument says so rather than my judgement:

- **Decision 24.** The task list's branching ratio is **0.9502 with a 95% interval of [0.7869, 1.1475]**. The upper bound has reached 1, so the list can no longer be said to terminate. He asked to be told if that happened. Entries B11 and C29 rest on it.
- **Decision 23.** The generated morning report breaks the line caps he set: **616 markdown lines against 300, and 673 spoken lines against 400**. Entry B41 rests on it.

`scripts/which_completion_claims_the_board_unsupported_2026-11-04.py` measures this: **21 of 24 completion claims restored, 0.875000, Wilson 95% [0.689961, 0.956557]**, and all 3 that remain wait on these 2 rulings and on nothing else. **Loosening either cap or threshold to turn the board green is the move his own rules forbid.** Do not do it.

Also awaiting him and recorded, not to be inferred:
- The edit to `~/.claude/hooks/cy_monitor_gate.py` was **refused as self-modification** and both hook copies are unmodified. It needs his permission. Entry B113, decision 21.
- **The push.** The local branch is **540 commits ahead of `origin/main` and 1 behind**, and the remote commit touches `.claude/CLAUDE.md`, so it needs a merge rather than a fast-forward. His standing policy is that the remote holds the project's best work and the local repository is where things are built and tested. **Do not push without asking him.**

## What is NOT owed, so no time is spent re-deriving it

- **No memory was ever at risk.** The 331 memory files live at `~/.claude/projects/-Users-georgejackson-Developer-Projects/memory`, outside the repository, outside the session scratchpad and outside the session directory. A restart does not touch them.
- A full read-only copy of every recovery resource, including all the memory files, sits at **`~/Desktop/CDSFL_recovery_snapshot_2026-11-04/`** with a README. It is not canonical; the repository is. If they disagree, the repository wins.
- The staged corrections of 2026-11-04 at `~/Desktop/CDSFL_staged_corrections_2026-11-04/` are **applied or superseded except `fix_decision27.py`**, which is still owed and whose premise was re-verified against the live text on 2026-11-04.

## One thing that cost 3 reports today, so do not repeat it

**Read a command's exit code from its LOG, never from the harness task notification.** The 2-hour full suite finished and the notification read *completed (exit code 0)*. The log read `PYTEST_EXIT=1` with 28 failures. The notification reports the exit of the whole backgrounded shell, whose last stage was the `echo` that wrote the failure line. Write it with `cmd >> LOG 2>&1` then `echo "NAME_EXIT=$?" >> LOG`, and read that line back.
