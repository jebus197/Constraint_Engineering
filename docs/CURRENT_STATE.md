# CDSFL Current State

Generated: 17 October 2026 20:07 BST (2026-10-17T20:07:08+01:00)

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
- **Last commit (the PARENT of the commit containing this file):** `2169e7c6` The task list's code work is complete; B24 raised on a measured linter gap
- **Committed:** 2026-10-17 20:01:24 +0100
- **Remote (as of the snapshot, before the sv push):** up to date with origin/sim/shakedown-2026-09-29
- **Working tree at snapshot time:** clean

---

## Tests

**12557 tests collected** at 17 October 2026 20:07 BST, HEAD `2169e7c6` (`python3 -m pytest bench/tests/ --co -q`)

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

- `2169e7c6 The task list's code work is complete; B24 raised on a measured linter gap`
- `27a2a853 B23 backfills 1,701 commits; A19 closes by construction; B20 deferred`
- `c595db96 B21 step 4 wired; step 1 refused on measurement; and a skip survey that lied`
- `bb04b721 C1: the claim channel's commissioning measurement, which was never produced`
- `cbe4bd53 C6, C7 and B17: the notice now delivers the work instead of naming it`
- `edabd00a Close C2 and C9; a dropped-in brief was being read as his verdicts`
- `8e2af8b5 C29: my own forecast was invalidated by the commit that carried it`
- `dee78c5c his word-plus-hash register, his 3-element dupe test, and 0 of 6 needing him`
- `4d9b146a C21: the terminology he rejected is absent from the ranking code, measured by AST`
- `6028976d B11: a reset immune memory was being reported as the confinement defect returning`
