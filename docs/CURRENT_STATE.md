# CDSFL Current State

Generated: 11 October 2026 23:10 BST (2026-10-11T23:10:34+01:00)

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
- **Last commit (the PARENT of the commit containing this file):** `fda2dfcd` morning report extended: the substance test is wired and the risk was measured, not asserted
- **Committed:** 2026-10-11 23:09:21 +0100
- **Remote (as of the snapshot, before the sv push):** ahead of origin/sim/shakedown-2026-09-29 by 3
- **Working tree at snapshot time:** DIRTY — snapshot-time working tree listed below (NOT the sv commit's file list)

Uncommitted files at snapshot time — the working tree as it stood before the sv commit, NOT that commit's file list:
- `M resources/MEMORY_EXCLUSIONS.md`

---

## Tests

**10802 tests collected** at 11 October 2026 23:10 BST, HEAD `fda2dfcd` + uncommitted working tree (`python3 -m pytest bench/tests/ --co -q`)

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

- `fda2dfcd morning report extended: the substance test is wired and the risk was measured, not asserted`
- `be5ff31c his 0.05 false-alarm proportion pinned, with the ruling it depends on`
- `44e82fe5 the runner now refuses a reply that is merely non-empty, and the risk was measured first`
- `beb718f1 sv: recovery is mechanical now, item 13 is closed, and 3 of the 4 panel lessons had already landed`
- `8877d9c7 morning report for 12 October: recovery is mechanical, 13 complete, 3 of 4 lessons had landed`
- `9ebf843b his 4 panel lessons verified: 3 of 4 had landed, and my "0 of 4" is withdrawn`
- `46613332 recovery now runs itself, and a long save gap refuses the turn`
- `d0013b34 the citation repair the gate could not stage during the merge`
- `c46ef2b8 recover the 4 commits stranded on r3-parser-envelope, on his ruling`
- `791e4db5 sv: the suite figure named no producer, which is the defect A23 was built for`
