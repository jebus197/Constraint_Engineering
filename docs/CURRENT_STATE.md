# CDSFL Current State

Generated: 6 September 2026 10:55 BST (2026-09-06T10:55:38+01:00)

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
- **Last commit (the PARENT of the commit containing this file):** `6908eec` Date the superseded suite figures rather than rewriting them
- **Committed:** 2026-09-06 04:08:50 +0100
- **Remote (as of the snapshot, before the sv push):** up to date with origin/main
- **Working tree at snapshot time:** DIRTY — snapshot-time working tree listed below (NOT the sv commit's file list)

Uncommitted files at snapshot time — the working tree as it stood before the sv commit, NOT that commit's file list:
- `M experimental_notes/CDSFL_Agent_Operational_Plan.md`

---

## Tests

**5203 tests collected** at 6 September 2026 10:55 BST, HEAD `6908eec` + uncommitted working tree (`python3 -m pytest bench/tests/ --co -q`)

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

- `6908eec Date the superseded suite figures rather than rewriting them`
- `b5638c5 Today's single note, rewritten: the directive finding supersedes the 02:30 version`
- `061d4be Recovery state: the directive shipped a false claim, and 9 sites carried an over-broad one`
- `2813a99 9 sites called all 5 stage links strict generalisations. Four are; one is not`
- `b815abf We were telling every model a false thing about our own model's lineage`
- `b6599ba cc2 refuted my own consolation: the coordinate story holds per class, not aggregated`
- `74b4458 4 of the 5 stages nest. Link 2 to 3 does not, and the founder's instinct is why`
- `351da30 Instrument inventory picks up tonight's new gate coverage`
- `1148052 Recovery state for 2026-09-06, and the READ-THIS-FIRST block was not first`
- `4a5aa73 Prove the S* shadow RUNS, not that it is written down`
