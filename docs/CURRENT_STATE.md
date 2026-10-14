# CDSFL Current State

Generated: 14 October 2026 23:03 BST (2026-10-14T23:03:35+01:00)

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
- **Last commit (the PARENT of the commit containing this file):** `c50abdb6` sv: the run is launch-ready, the board went 32 red to 6, and 4 items need his ruling
- **Committed:** 2026-10-14 23:00:35 +0100
- **Remote (as of the snapshot, before the sv push):** up to date with origin/sim/shakedown-2026-09-29
- **Working tree at snapshot time:** DIRTY — snapshot-time working tree listed below (NOT the sv commit's file list)

Uncommitted files at snapshot time — the working tree as it stood before the sv commit, NOT that commit's file list:
- `M resources/RECOVERY.md`

---

## Tests

**11217 tests collected** at 14 October 2026 23:03 BST, HEAD `c50abdb6` + uncommitted working tree (`python3 -m pytest bench/tests/ --co -q`)

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

- `c50abdb6 sv: the run is launch-ready, the board went 32 red to 6, and 4 items need his ruling`
- `797f3dab board: 32 red to 6, and 3 of the 6 are not defects`
- `f0405a6e fix: the script documenting POST had never run its own part 1, and its verdict label lied`
- `d13c28e2 docs: tracker un-stalled and the programme of study revised for the hotel window`
- `da23d286 fix: the cap now records what it cut, the glob sees every run, and arm 4 has a verified prose target`
- `6a29a27f harden: the pre-machinery producer now prefers live registries explicitly`
- `3d942502 measure: the falsifier gap is 83% pre-machinery, and the 2026-10-03 panel already said so`
- `5fb360b5 panel: the directive set and measured capability, 6 items, both seats landed`
- `c6115986 fix: a joint round must ANSWER to discharge a debt; and the joint half lands`
- `8590f6cf t: the directive-set analysis, with the 4 decisions it leaves him`
