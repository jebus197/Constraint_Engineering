# CDSFL Current State

Generated: 9 October 2026 05:21 BST (2026-10-09T05:21:53+01:00)

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
- **Last commit (the PARENT of the commit containing this file):** `e3297cbb` the wheel is largely invented, the research proving it had fabricated citations, and his "2 or 3" was nearly right
- **Committed:** 2026-10-09 05:20:14 +0100
- **Remote (as of the snapshot, before the sv push):** up to date with origin/sim/shakedown-2026-09-29
- **Working tree at snapshot time:** clean

---

## Tests

**10618 tests collected** at 9 October 2026 05:21 BST, HEAD `e3297cbb` (`python3 -m pytest bench/tests/ --co -q`)

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

- `e3297cbb the wheel is largely invented, the research proving it had fabricated citations, and his "2 or 3" was nearly right`
- `b03aa8a2 both seats refuted me, randomisation settles monotonicity, and 4 launch deficiencies are fixed`
- `b4c897fb the round-3 panel analysis he asked for under `d` and did not receive`
- `6d0f53cc sv: gamma gates wherever a curve exists, the cap default is exhaust, and the panel found 2 critical defects in my fix`
- `3c7240bf the morning report now carries the 4th panel's outcome, which I said I would add and did not`
- `40c4a154 both seats found the same 2 critical defects in my gamma fix, and all 4 are now repaired`
- `80619fa1 p-pass: the hand-maintained mirror holds over a sweep, not over the 10 inputs I first tested`
- `eaadd840 morning report: gamma gates everywhere, and 6 figures I carried to a panel were wrong`
- `8f014a59 he was right: "unestimable" was the demotion renamed, so the proven guarded vacuity is imported`
- `e6cd8ead the 2 guards my gamma fix broke were guarding the defect, and are updated not deleted`
