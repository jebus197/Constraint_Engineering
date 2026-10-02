# CDSFL Current State

Generated: 2 October 2026 04:49 BST (2026-10-02T04:49:22+01:00)

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
- **Last commit (the PARENT of the commit containing this file):** `bf04cf7` fix: 3 guards met the same category error, and A7 stops drifting
- **Committed:** 2026-10-02 04:24:13 +0100
- **Remote (as of the snapshot, before the sv push):** ahead of origin/sim/shakedown-2026-09-29 by 8
- **Working tree at snapshot time:** DIRTY — snapshot-time working tree listed below (NOT the sv commit's file list)

Uncommitted files at snapshot time — the working tree as it stood before the sv commit, NOT that commit's file list:
- `M experimental_notes/CDSFL_Agent_Operational_Plan.md`
- `M experimental_notes/data/instrument_inventory.json`
- `M resources/RECOVERY.md`

---

## Tests

**9585 tests collected** at 2 October 2026 04:49 BST, HEAD `bf04cf7` + uncommitted working tree (`python3 -m pytest bench/tests/ --co -q`)

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

- `bf04cf7 fix: 3 guards met the same category error, and A7 stops drifting`
- `ad8fe13 feat: rescue the seat evidence that predated the preservation repair`
- `43d570a fix: the watchdog went blind on truncation, and the Q2 split the founder ruled on`
- `1ac147c fix: closure never asked whether a fix cures the defect its finding claims`
- `057781d fix: the 4 red tests were all mine, and each was a real tension not a typo`
- `8a39117 fix: a prose falsifier could not reach its own target, which halted both runs at round 0`
- `2a06f7b fix: the cy watchdog reported a halt exactly like a convergence`
- `0edee1d feat: a mechanical cy trigger, because the 30-minute cap was a half-truth`
- `04bff14 sv: the alarm's clock, the index audit's grouped pointers, and a report figure withdrawn`
- `5a81bd6 fix: the compaction alarm read UTC as local, and the index audit could not see grouped pointers`
