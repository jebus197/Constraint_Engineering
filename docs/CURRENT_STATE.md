# CDSFL Current State

Generated: 25 August 2026 23:21 BST (2026-08-25T23:21:31+01:00)

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

- **Branch:** build-experiment-2026-08-22
- **Last commit (the PARENT of the commit containing this file):** `0fe5b19` Merge origin/main: pick up the three commits published directly tonight.
- **Committed:** 2026-08-25 22:44:57 +0100
- **Remote (as of the snapshot, before the sv push):** ahead of origin/main by 55 [no upstream configured]
- **Working tree at snapshot time:** DIRTY — snapshot-time working tree listed below (NOT the sv commit's file list)

Uncommitted files at snapshot time — the working tree as it stood before the sv commit, NOT that commit's file list:
- `M  bench/tests/test_documentation_drift_guards_2026-08-25.py`
- `M docs/CURRENT_STATE.md`
- `M resources/MEMORY_EXCLUSIONS.md`
- `M resources/ONBOARDING.md`
- `M resources/RECOVERY.md`
- `M  scripts/cdsfl_sv.py`
- `?? .cdsfl_tmp/`

---

## Tests

**3905 tests collected** at 25 August 2026 23:21 BST, HEAD `0fe5b19` + uncommitted working tree (`python3 -m pytest bench/tests/ --co -q`)

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

- `0fe5b19 Merge origin/main: pick up the three commits published directly tonight.`
- `83033b6 sv 2026-08-25: NOT COMMISSIONED IS NOT NOT WORKING. The founder caught the same over-statement twice; the cheating audit closed at a blast radius of ONE run; sy caught a boundary defect sixteen tests waved through; and the same failed-measurement defect turned up twice more, in the tools themselves.`
- `931827a sy and the missing half of FFAFP: two hand-picked points do not prove a gate implements what it says.`
- `9fa21e4 Commission the four stopping components, guard the drift class, and fix the instrument that measures instruments.`
- `3b09c6d Explorer: trim the caveat to match the README's register.`
- `f375ade explorer/index.html: mirror the caveat trim (see the explorer repo commit for the reasoning).`
- `f7dfbf9 REPRODUCING.md: point at WORKING_DIRECTIVES.md.`
- `d68fed4 docs: publish WORKING_DIRECTIVES.md and cross-reference it from REPRODUCING.md (see the branch commit for the full account of the split).`
- `115b731 docs/WORKING_DIRECTIVES.md: the portable two-thirds of the working configuration, published because a run cannot be understood without it.`
- `c6b06ea Merge origin/main: reconcile the fork created by publishing through the API.`
