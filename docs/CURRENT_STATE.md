# CDSFL Current State

Generated: 31 October 2026 06:16 GMT (2026-10-31T06:16:39+00:00)

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
- **Last commit (the PARENT of the commit containing this file):** `59e086f0` The severity panel answers his question, and finds a blocker the carry does not clear
- **Committed:** 2026-10-31 06:09:00 +0000
- **Remote (as of the snapshot, before the sv push):** up to date with origin/sim/shakedown-2026-09-29
- **Working tree at snapshot time:** DIRTY — snapshot-time working tree listed below (NOT the sv commit's file list)

Uncommitted files at snapshot time — the working tree as it stood before the sv commit, NOT that commit's file list:
- `M resources/MEMORY_EXCLUSIONS.md`
- `M resources/RECOVERY.md`

---

## Tests

**13942 tests collected** at 31 October 2026 06:16 GMT, HEAD `59e086f0` + uncommitted working tree (`python3 -m pytest bench/tests/ --co -q`)

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

- `59e086f0 The severity panel answers his question, and finds a blocker the carry does not clear`
- `db8d48eb The polarity round converged on CONFIRMED BUT LATENT, and the reach is disputed by execution`
- `802d7834 sv: disc, R_k carries forward, 2 free panels, and 4 figures corrected`
- `39a26603 29 guards join the gate, the B22 panel refuted my own brief, and a full-record script was hanging on stdin`
- `f5807b52 The joint round converged on evidence, and C1's weight is undecidable for a different reason`
- `af56b28f R_k carries forward across passes, and the B21 free panel split 2 ways`
- `6be4f07a disc is the discussion label, and the own-line marker reader was never normalising`
- `f26c5a55 A pass buys q=0.167578 median, and the decay FLATTENS -- my censoring prediction was refuted`
- `47c6fd13 RECOVERY block names its commit and 2 figures with producers, which A23 refused`
- `f50582ed dis replaces ds as the discussion label, and the case for it is namespace not rate`
