# CDSFL Current State

Generated: 22 November 2026 05:16 GMT (2026-11-22T05:16:34+00:00)

---

## Git

> **SNAPSHOT TAKEN IMMEDIATELY BEFORE THE sv COMMIT — NOT CURRENT TRUTH.**
> This file is generated first and committed second, so it cannot describe
> the commit that carries it. Read the block below as follows:
> **"Last commit" is the PARENT** of the commit containing this file, and
> **the uncommitted list is the working tree at snapshot time — it is NOT
> that commit's file list.** The two differ in both directions: sv rewrites
> docs/CURRENT_STATE.md, resources/ONBOARDING.md and resources/RECOVERY.md
> *after* this snapshot, and it stages only whitelisted paths. For the
> commit this file actually lives in and its real contents, run
> `git log -1 --stat -- docs/CURRENT_STATE.md`.

- **Branch:** sim/shakedown-2026-09-29
- **Last commit (the PARENT of the commit containing this file):** `b1d5d5db` 4 entries investigated, 4 wrong claims of mine corrected, and a hand-edit caught by its own guard
- **Committed:** 2026-11-17 09:34:32 +0000
- **Remote (as of the snapshot, before the sv push):** ahead of origin/sim/shakedown-2026-09-29 by 4
- **Working tree at snapshot time:** DIRTY — snapshot-time working tree listed below (NOT the sv commit's file list)

Uncommitted files at snapshot time — the working tree as it stood before the sv commit, NOT that commit's file list:
- `M  bench/tests/test_a_prior_ruling_is_acknowledged_2026-11-03.py`
- `M  bench/tests/test_a_refusal_names_every_failure_2026-11-09.py`
- `M  bench/tests/test_blocker_triage_2026-09-10.py`
- `M  bench/tests/test_desktop_mirrors_stay_current_2026-09-10.py`
- `A  bench/tests/test_his_copy_carries_the_entrys_status_2026-11-21.py`
- `A  bench/tests/test_the_board_detector_fails_toward_writing_2026-11-22.py`
- `M  bench/tests/test_the_board_verdict_reaches_the_refusal_2026-11-17.py`
- `A  bench/tests/test_the_boards_guard_phase_streams_2026-11-21.py`
- `M  bench/tests/test_the_cheap_checks_run_before_the_board_2026-11-09.py`
- `A  bench/tests/test_the_index_can_never_stop_filling_2026-11-21.py`
- `A  bench/tests/test_the_preflight_population_is_the_gates_2026-11-22.py`
- `A  bench/tests/test_the_standing_goal_survives_compaction_2026-11-22.py`
- `A  bench/tests/test_todays_producers_run_2026-11-21.py`
- `A  bench/tests/test_todays_producers_run_2026-11-22.py`
- `A  bench/tests/test_was_this_batch_reviewed_2026-11-22.py`
- … and 71 more, not shown (list capped at 15 of 86 — run `git status --porcelain` for the full set)

---

## Tests

**18276 tests collected** at 22 November 2026 05:16 GMT, HEAD `b1d5d5db` + uncommitted working tree (`python3 -m pytest bench/tests/ --co -q`)

This is a COLLECTION count, not a pass count, and it says nothing about whether the run was offline. Quote it only with the timestamp and commit above. The total is not stable: `bench/tests/test_immune_memory_consumption.py` parametrises over the timestamped run directories under `bench/logs/`, so it grows whenever an experiment archives, and new test files land between saves.

For a pass count, run the suite offline and record the result with its own date and command: `python3 -m pytest bench/tests/ -q --netguard-strict`. The suite is offline by default via `bench/tests/conftest.py`; see docs/REPRODUCING.md. Figures labelled "non-network" before 2026-07-31 were hand-curated exclusions and included live model dispatch — do not quote them as offline results.

---

## Latest Experiment

- **Experiment:** exp55_v3_control (#55)
- **Status:** INCOMPLETE
- **Topology:** star
- **Target:** `bench/cdsfl_registry/targets/control_two_distinct_defects.md`
- **Rounds:** 1
- **Total findings:** 10
- **Gamma:** 0.0000
- **Models:** CC2, ChatGPT, Codex, DeepSeek, Gemini
- **Per model:**
  - ChatGPT: 2
  - Gemini: 2
  - Codex: 2
  - DeepSeek: 2
  - CC2: 2
- **Logs:** `/Users/georgejackson/Developer_Projects/Constraint_Engineering/bench/logs/exp55_v3_control_20260823T153955Z`

---

## Recent Commits

- `b1d5d5db 4 entries investigated, 4 wrong claims of mine corrected, and a hand-edit caught by its own guard`
- `fa0fcb48 7 entries closed by running their evidence, and 6 silent failures found by doing it`
- `b8f556d3 A guard that ran a 45-minute board to prove something that finishes 221 lines earlier`
- `725ec976 A board fix that was half a fix, and the 1-line completion that would have turned the gate into a rubber stamp`
- `bb315555 The full suite ran against a committed tree, and 8 of its 10 new failures were invisible to the board that passed it`
- `6304f771 The 3 panel rounds he ordered, run blind and joint, and every round refuted something in my own brief`
- `4a802768 One batch, as he instructed: his 16 verdicts worked through, the encoding layer built, and a sentence every seat is given that was false`
- `84fd2253 B169: the permission predicate under-reported a residue, and composing was measured rather than asserted`
- `665a4b41 B165: the clean-tree full-suite measurement, and what it caught doing`
- `846c4ffe fix: 21 anchored corrections, 4 entries raised, 7 guards repaired`
