# CDSFL Current State

Generated: 30 October 2026 04:20 GMT (2026-10-30T04:20:23+00:00)

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
- **Last commit (the PARENT of the commit containing this file):** `eb2730e3` A cited path that never existed, and the obvious guard for it would have been wrong
- **Committed:** 2026-10-30 04:11:44 +0000
- **Remote (as of the snapshot, before the sv push):** up to date with origin/sim/shakedown-2026-09-29
- **Working tree at snapshot time:** DIRTY — snapshot-time working tree listed below (NOT the sv commit's file list)

Uncommitted files at snapshot time — the working tree as it stood before the sv commit, NOT that commit's file list:
- `M resources/ONBOARDING.md`
- `M resources/RECOVERY.md`

---

## Tests

**13642 tests collected** at 30 October 2026 04:20 GMT, HEAD `eb2730e3` + uncommitted working tree (`python3 -m pytest bench/tests/ --co -q`)

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

- `eb2730e3 A cited path that never existed, and the obvious guard for it would have been wrong`
- `73333e0a 2 of the 3 entries asking him to rule already carried his ruling`
- `8cdcc0a6 The report he reads now carries B50 and the guard that was red beneath it`
- `57bd99fb B21 and C1 both argued from claims they never executed, and 3 of the 4 are false`
- `b59446dd The Stop gate's defect is a ticket now, not prose in a log`
- `498002bb A completeness check on his report found 1 gap, and it was the gate that prodded all night`
- `22bc65f6 I put a transient obstacle of mine into his parked file, and a guard caught the repair`
- `8d240655 His report carries B21's price as well as its question`
- `d595b945 B21's cost side measured, and the producer I wrote for it had 2 defects in 2 minutes`
- `207faed2 B41 reduced in the canonical place, and the marker lesson applied rather than relearnt`
