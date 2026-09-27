# CDSFL Current State

Generated: 27 September 2026 19:29 BST (2026-09-27T19:29:18+01:00)

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
- **Last commit (the PARENT of the commit containing this file):** `c3ad127` Report pair updated with the panel review: 3 defects I had not reached
- **Committed:** 2026-09-24 04:21:34 +0100
- **Remote (as of the snapshot, before the sv push):** ahead of origin/main by 12
- **Working tree at snapshot time:** DIRTY — snapshot-time working tree listed below (NOT the sv commit's file list)

Uncommitted files at snapshot time — the working tree as it stood before the sv commit, NOT that commit's file list:
- `M resources/ONBOARDING.md`
- `M resources/RECOVERY.md`

---

## Tests

**8644 tests collected** at 27 September 2026 19:29 BST, HEAD `c3ad127` + uncommitted working tree (`python3 -m pytest bench/tests/ --co -q`)

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

- `c3ad127 Report pair updated with the panel review: 3 defects I had not reached`
- `4c0caa3 The panel found 3 defects I had not reached, including a test of mine that verified nothing`
- `e9c28e1 Clean suite: 9 failed, 8606 passed -- 38 of the 47 closed; and the gate I armed is evadable`
- `d193539 The classifier repair was insufficient, and my test for it was vacuous`
- `f1ec381 Citations drifted +8 because I inserted 69 lines; a test hardcoded a family the archive had moved`
- `c4ecac7 Closed 27 of the 47 suite failures; 13 shared one cause and it was mine`
- `b48dcb9 The prose flag admitted 5 of 5 harmful fixes; the FFAFP detector was dead for 2 days`
- `43af0e6 Recovery: A19 was built and unreachable, now fixed; the 2 red guards are the founder's`
- `981e38d Reports carry the A19 finding; full record covers all 4 rounds`
- `6e5e22a The founder's prose fix was ALREADY BUILT and had never been reachable`
