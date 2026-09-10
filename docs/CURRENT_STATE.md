# CDSFL Current State

Generated: 10 September 2026 03:36 BST (2026-09-10T03:36:58+01:00)

---

## Git

- **Branch:** main
- **Last commit:** `efbaf8a` Four agents measured the unbacked figures, and 9 of them were wrong — including a script the fix itself had broken
- **Committed:** 2026-09-10 03:19:04 +0100
- **Remote:** up to date with origin/main
- **Working tree:** DIRTY — uncommitted changes present

Uncommitted files:
- `M experimental_notes/CDSFL_MASTER_TASK_LIST.md`
- `M experimental_notes/data/adjudication_by_repair.json`
- `M experimental_notes/data/instrument_inventory.json`
- `?? bench/tests/test_task_list_entry_count_2026-09-10.py`
- `?? scripts/lint_reach_over_notes_2026-09-10.py`
- `?? scripts/task_list_entry_count_2026-09-10.py`

---

## Tests

**5877 tests collected** at 10 September 2026 03:36 BST, HEAD `efbaf8a` + uncommitted working tree (`python3 -m pytest bench/tests/ --co -q`)

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

- `efbaf8a Four agents measured the unbacked figures, and 9 of them were wrong — including a script the fix itself had broken`
- `03254e8 Task 6.7: the assessment declined a question that was answerable, and both verdicts are now executed`
- `fc479bb V5: the restore now reads the FRESHER document first, which is what cost the founder a drive home`
- `8f88650 Panel round 3: both seats PARTIAL, 6 findings, and the worst one was a guard that audited itself`
- `2360462 Pass 4: 5.1's figure corrected with a script, 6.4's 2 missed sites wired, and the cycle gate says keep going`
- `663a5eb V1 built, and the FFAFP stop criterion is now computed from the maths model instead of asserted`
- `7e93585 V3: the commit guard had 2 demonstrated bypasses and now has neither, plus 3 of V2's corrections`
- `d03465f The verification result, the mechanism the founder asked for and did not get, and 5 tasks for the gap`
- `25e5b34 URGENT: task 6.3 shipped a regression that sent every production run into one shared directory`
- `1ee7e9e Correct the stale sealing claim I repeated during rs, and add the 12 tasks that arose from the work`
