# CDSFL Current State

Generated: 3 November 2026 05:57 GMT (2026-11-03T05:57:34+00:00)

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
- **Last commit (the PARENT of the commit containing this file):** `079471e4` A simulated experiment cannot test most of the last 24 hours, and could not pause at all, so the actuator had nowhere to act
- **Committed:** 2026-11-03 05:42:10 +0000
- **Remote (as of the snapshot, before the sv push):** ahead of origin/sim/shakedown-2026-09-29 by 16
- **Working tree at snapshot time:** DIRTY — snapshot-time working tree listed below (NOT the sv commit's file list)

Uncommitted files at snapshot time — the working tree as it stood before the sv commit, NOT that commit's file list:
- `M resources/RECOVERY.md`

---

## Tests

**15183 tests collected** at 3 November 2026 05:57 GMT, HEAD `079471e4` + uncommitted working tree (`python3 -m pytest bench/tests/ --co -q`)

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

- `079471e4 A simulated experiment cannot test most of the last 24 hours, and could not pause at all, so the actuator had nowhere to act`
- `3c1463aa B20's precondition built on his authorisation: the watchdog's 10 event kinds reached stdout and nothing else, so an actuator would have had to parse prose`
- `64c833e2 He asked whether the decisions were all new, and the detector built for that question could not see the field named ruled`
- `baac39b8 The audit that checked tonight's producers counted library imports, and 4 of 7 passed it while resting an interval on a single route`
- `d6ea0538 Nothing in the suite reached the 3 generator fixes made tonight, and the decisions file was missing the markdown twin the protocol requires`
- `d74a8450 5 of the 7 producers I wrote tonight were run by no test, including the one written 20 minutes earlier to pay off exactly that debt`
- `9419b4b8 Reading the spoken report's owed findings aloud narrowed decision 14 from 15 to 13, and 2 of them were terms the exemption list already covered in principle`
- `01b6e408 The post-compaction re-verification found 2 producers that could not reproduce their own figures, and a self-lint added to the morning report found a defect on its first run`
- `5e4879c4 A mutation harness that skips a stale anchor still prints "N of N applied" and still exits 0, and fixing that found 3 properties already lost`
- `a0eb9d00 A model's own VERIFIED flag closed its finding as tool-adjudicated, and the comment above the gate said that could not happen`
