# CDSFL Current State

Generated: 12 October 2026 15:07 BST (2026-10-12T15:07:44+01:00)

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
- **Last commit (the PARENT of the commit containing this file):** `47c5529e` the 2 remaining board reds are now ENTRIES rather than a conversation, and the report is rebuilt
- **Committed:** 2026-10-12 15:00:08 +0100
- **Remote (as of the snapshot, before the sv push):** up to date with origin/sim/shakedown-2026-09-29
- **Working tree at snapshot time:** DIRTY — snapshot-time working tree listed below (NOT the sv commit's file list)

Uncommitted files at snapshot time — the working tree as it stood before the sv commit, NOT that commit's file list:
- `M resources/MEMORY_EXCLUSIONS.md`

---

## Tests

**10970 tests collected** at 12 October 2026 15:07 BST, HEAD `47c5529e` + uncommitted working tree (`python3 -m pytest bench/tests/ --co -q`)

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

- `47c5529e the 2 remaining board reds are now ENTRIES rather than a conversation, and the report is rebuilt`
- `fa787d59 his 3 rulings built: the 11 cases used as intended, the seats staggered, outputs hashed`
- `979fce32 the measurement's own instrument is now guarded, and the hyphen defect cannot return`
- `e54cf07e the test-value measurement he commissioned, with its own first figure withdrawn`
- `687a5594 the generated report was not reproducible, and the P-pass caught it before he read it`
- `7f88a467 the morning report's decision list is now DERIVED, and it found 3 decisions I had missed`
- `54c4bbf0 morning report extended: it ended at 00:05 and the overnight work was not in it`
- `0a0d1657 the night's error shape, recorded as a hypothesis rather than a finding`
- `8705b6ab sv: the restore fires at a task boundary; the board's 20 reds are all accounted for`
- `9061ddf1 the restore now fires at a task boundary, and the board accounted for all 20 reds`
