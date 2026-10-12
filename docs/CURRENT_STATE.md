# CDSFL Current State

Generated: 12 October 2026 23:51 BST (2026-10-12T23:51:55+01:00)

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
- **Last commit (the PARENT of the commit containing this file):** `90361ff8` sv: his 3 rulings built and tested, the board triaged, 3 corrections to one predicate
- **Committed:** 2026-10-12 23:47:57 +0100
- **Remote (as of the snapshot, before the sv push):** up to date with origin/sim/shakedown-2026-09-29
- **Working tree at snapshot time:** DIRTY — snapshot-time working tree listed below (NOT the sv commit's file list)

Uncommitted files at snapshot time — the working tree as it stood before the sv commit, NOT that commit's file list:
- `M experimental_notes/EXPERIMENT_RUN_LEDGER.md`
- `M resources/ONBOARDING.md`
- `M resources/RECOVERY.md`

---

## Tests

**11120 tests collected** at 12 October 2026 23:51 BST, HEAD `90361ff8` + uncommitted working tree (`python3 -m pytest bench/tests/ --co -q`)

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

- `90361ff8 sv: his 3 rulings built and tested, the board triaged, 3 corrections to one predicate`
- `1d18b0c6 board triage: 13 red, 10 of them mine, and 2 were real defects in tonight's work`
- `d164a906 his ruling 1: the severity specification EXISTS, was never implemented, and he is right`
- `e8ee2e18 his ruling 2: the fix EXISTS and is built. A falsifier can no longer read our evidence.`
- `f26d64e5 his ruling 3: a never-read finding is FED BACK, never excused. Release withdrawn.`
- `6949248e d + t: the panel refuted its own answer, and 3 decisions wait on him`
- `716248fd joint round: both seats refuted their own blind answer, and mine was INERT`
- `a20640df WITHDRAWN: no seat deleted his rulings. The diff direction did, and I accused cc2 of it.`
- `b912268d panel harvest: both seats' fixes tested, composed, and a defect NEITHER could see repaired`
- `e05bf903 his 9 annotations read in full, 2 rulings recorded, 2 explanations discounted, panel running`
