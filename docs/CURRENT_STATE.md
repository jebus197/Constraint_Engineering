# CDSFL Current State

Generated: 4 November 2026 17:14 GMT (2026-11-04T17:14:53+00:00)

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
- **Last commit (the PARENT of the commit containing this file):** `c4553e95` The mypy question deferred for machine cost takes 1.1 seconds, and the figure it yields is half config noise and a third one idiomatic line
- **Committed:** 2026-11-04 13:47:00 +0000
- **Remote (as of the snapshot, before the sv push):** ahead of origin/sim/shakedown-2026-09-29 by 13
- **Working tree at snapshot time:** DIRTY — snapshot-time working tree listed below (NOT the sv commit's file list)

Uncommitted files at snapshot time — the working tree as it stood before the sv commit, NOT that commit's file list:
- `M  bench/tests/test_a_deliverable_pair_uses_the_right_check_2026-11-03.py`
- `M  bench/tests/test_his_words_are_read_from_both_records_2026-11-03.py`
- `A  bench/tests/test_the_severity_frame_counts_one_run_twice_2026-11-04.py`
- `M  experimental_notes/CDSFL_MASTER_TASK_LIST.md`
- `M  experimental_notes/Decisions_Awaiting_You_2026-11-04.md`
- `M  experimental_notes/Decisions_Awaiting_You_2026-11-04.txt`
- `A  experimental_notes/The_Second_Complete_Board_2026-11-04.md`
- `A  resources/NEW_SESSION_HANDOVER.md`
- `M  resources/RECOVERY.md`
- `M  resources/suite_record.json`
- `M  scripts/a_bare_clock_was_dated_from_the_mtime_2026-11-03.py`
- `M  scripts/a_compaction_summary_can_invent_his_question_2026-11-03.py`
- `M  scripts/a_models_own_verified_flag_closes_it_2026-11-03.py`
- `M  scripts/a_per_round_predicate_peeks_2026-11-04.py`
- `M  scripts/a_stale_comment_can_be_load_bearing_2026-11-03.py`
- … and 14 more, not shown (list capped at 15 of 29 — run `git status --porcelain` for the full set)

---

## Tests

**15581 tests collected** at 4 November 2026 17:14 GMT, HEAD `c4553e95` + uncommitted working tree (`python3 -m pytest bench/tests/ --co -q`)

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

- `c4553e95 The mypy question deferred for machine cost takes 1.1 seconds, and the figure it yields is half config noise and a third one idiomatic line`
- `8c1ba3e9 Both mechanisms that keep the memory index inside its limits are exhausted at once, and I nearly rebuilt one of them before tracing its callers`
- `88f30053 His blinkered-depth hypothesis measured for the first time: not supported on this budget, and the decision rule he wrote has a missing third category`
- `03e675b8 A declaration whose purpose is to be checkable had 2 drifted citations and a function that does not exist, and the test written to catch exactly that was too weak to see it`
- `e9c5d587 A panel seat found the weighted risk is not a probability, 3 surfaces said it was, and the detector I wrote to count them matched its own remedy 3 times`
- `a22ff0cb The first complete board since 29 September found 44 failures where the gate showed 0; 40 are fixed and the 4 that remain are his to rule`
- `e6857344 The cy gate refused 5 stops for a run that did not exist, because it matched the git commit shell whose message named the runner - and its repair needs his permission`
- `ed92ccfe Six reporting layers disagreed with the layers that decide, three of them in B20's own status instrument, plus the inventory and the answers still owed`
- `6a423579 sv: his mid-turn words live in a record no instrument read, 206 of 1,421; a panel's own sandbox harvest had inflated 27 of 32 into 37 of 42; B87's letter-level conflict dissolves; 19 decisions owed and every live entry now waits on him`
- `a08c184a The joint round resolved both disagreements, each seat withdrew a round-1 claim, my "opposite failure modes" synthesis was superseded, and I had hand-rolled a record the project already had a tool for`
