# CDSFL Current State

Generated: 11 October 2026 22:33 BST (2026-10-11T22:33:13+01:00)

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
- **Last commit (the PARENT of the commit containing this file):** `8877d9c7` morning report for 12 October: recovery is mechanical, 13 complete, 3 of 4 lessons had landed
- **Committed:** 2026-10-11 22:31:25 +0100
- **Remote (as of the snapshot, before the sv push):** ahead of origin/sim/shakedown-2026-09-29 by 9
- **Working tree at snapshot time:** DIRTY — snapshot-time working tree listed below (NOT the sv commit's file list)

Uncommitted files at snapshot time — the working tree as it stood before the sv commit, NOT that commit's file list:
- `M resources/MEMORY_EXCLUSIONS.md`

---

## Tests

**10791 tests collected** at 11 October 2026 22:33 BST, HEAD `8877d9c7` + uncommitted working tree (`python3 -m pytest bench/tests/ --co -q`)

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

- `8877d9c7 morning report for 12 October: recovery is mechanical, 13 complete, 3 of 4 lessons had landed`
- `9ebf843b his 4 panel lessons verified: 3 of 4 had landed, and my "0 of 4" is withdrawn`
- `46613332 recovery now runs itself, and a long save gap refuses the turn`
- `d0013b34 the citation repair the gate could not stage during the merge`
- `c46ef2b8 recover the 4 commits stranded on r3-parser-envelope, on his ruling`
- `791e4db5 sv: the suite figure named no producer, which is the defect A23 was built for`
- `cd149682 sv: the reader was mangling his writing, 4 of his rulings land, and a precondition is not a question`
- `15a0d6dd the single file now records what became of all 18 of his responses`
- `fd2eae8a his rulings 1 and 2 pinned where they would otherwise have been lost`
- `48c6bd53 his 18 responses worked: 256 characters of his writing were being dropped, and 4 rulings land`
