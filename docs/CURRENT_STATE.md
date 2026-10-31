# CDSFL Current State

Generated: 31 October 2026 04:39 GMT (2026-10-31T04:39:26+00:00)

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
- **Last commit (the PARENT of the commit containing this file):** `39a26603` 29 guards join the gate, the B22 panel refuted my own brief, and a full-record script was hanging on stdin
- **Committed:** 2026-10-31 04:30:07 +0000
- **Remote (as of the snapshot, before the sv push):** up to date with origin/sim/shakedown-2026-09-29
- **Working tree at snapshot time:** DIRTY — snapshot-time working tree listed below (NOT the sv commit's file list)

Uncommitted files at snapshot time — the working tree as it stood before the sv commit, NOT that commit's file list:
- `M experimental_notes/Panel_FULL_RECORD_Role_Layer_B21_2026-10-31.md`
- `M experimental_notes/Panel_FULL_RECORD_Role_Layer_Joint_2026-10-31.md`
- `M resources/MEMORY_EXCLUSIONS.md`
- `M resources/RECOVERY.md`

---

## Tests

**13901 tests collected** at 31 October 2026 04:39 GMT, HEAD `39a26603` + uncommitted working tree (`python3 -m pytest bench/tests/ --co -q`)

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

- `39a26603 29 guards join the gate, the B22 panel refuted my own brief, and a full-record script was hanging on stdin`
- `f5807b52 The joint round converged on evidence, and C1's weight is undecidable for a different reason`
- `af56b28f R_k carries forward across passes, and the B21 free panel split 2 ways`
- `6be4f07a disc is the discussion label, and the own-line marker reader was never normalising`
- `f26c5a55 A pass buys q=0.167578 median, and the decay FLATTENS -- my censoring prediction was refuted`
- `47c6fd13 RECOVERY block names its commit and 2 figures with producers, which A23 refused`
- `f50582ed dis replaces ds as the discussion label, and the case for it is namespace not rate`
- `eafd2575 RECOVERY block now names its commit and its producer, which A23 refused`
- `a76f34b0 sv: his 16 rulings recorded, ds is the 5th kind and confined by source, B50 took option 1`
- `ca7c0f5c Recovery block for the rewrite, and the gate-reach figure was stale by my own hand`
