# CDSFL Current State

Generated: 17 September 2026 15:23 BST (2026-09-17T15:23:11+01:00)

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

- **Branch:** main
- **Last commit (the PARENT of the commit containing this file):** `a2999f1` fix: hold a note to its foot-line's version, failing closed; the 15.8% was a mislabel
- **Committed:** 2026-09-17 11:22:16 +0100
- **Remote (as of the snapshot, before the sv push):** ahead of origin/main by 25
- **Working tree at snapshot time:** DIRTY — snapshot-time working tree listed below (NOT the sv commit's file list)

Uncommitted files at snapshot time — the working tree as it stood before the sv commit, NOT that commit's file list:
- `M experimental_notes/CDSFL_Agent_Operational_Plan.md`
- `M resources/ONBOARDING.md`
- `M resources/RECOVERY.md`

---

## Tests

**7499 tests collected** at 17 September 2026 15:23 BST, HEAD `a2999f1` + uncommitted working tree (`python3 -m pytest bench/tests/ --co -q`)

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

- `a2999f1 fix: hold a note to its foot-line's version, failing closed; the 15.8% was a mislabel`
- `1c4c84f docs: the green board, and the defects behind it`
- `725d1f9 fix: one foot-line, with the addendum above it`
- `cea399c fix: an inert --help on the new producer, and a foot-line for the addendum`
- `7cc1530 perf: answer citations from 1 index pass, not 1 git grep per path`
- `f22e95e fix: one boundary for entry bodies, and every interval cross-verified`
- `75b1163 Panel round 16: the full unfiltered record, and what was verified before adoption`
- `d673edd A26: three scripts destroyed content under -m --help, not one`
- `aeda07a A26 shut one entrance: --help still destroyed a panel record under -m`
- `16ccdf2 The overclaim figure was wrong twice over, and both seats were right`
