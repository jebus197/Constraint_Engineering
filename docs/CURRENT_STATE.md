# CDSFL Current State

Generated: 9 November 2026 04:11 GMT (2026-11-09T04:11:08+00:00)

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
- **Last commit (the PARENT of the commit containing this file):** `fc0b2e60` 104 guard files brought inside the gate, and the last silent admission step closed
- **Committed:** 2026-11-09 03:42:26 +0000
- **Remote (as of the snapshot, before the sv push):** ahead of origin/sim/shakedown-2026-09-29 by 72
- **Working tree at snapshot time:** clean

---

## Tests

**16459 tests collected** at 9 November 2026 04:11 GMT, HEAD `fc0b2e60` (`python3 -m pytest bench/tests/ --co -q`)

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

- `fc0b2e60 104 guard files brought inside the gate, and the last silent admission step closed`
- `2c50cf2d A board I killed by hand recorded as a fast refusal, and it moved the figure I had just quoted him`
- `a76f5f61 The sv gate I added to keep local state fresh reintroduced the misreading sv's own banner exists to prevent, realised twice tonight`
- `a1773584 sv: his 29 rulings worked through -- 13 entries built and closed, 9 of my own ruled dates withdrawn as wrong, and 12 decisions left that are his`
- `675af51e I built 5 of his entries and left all 5 marked OPEN: the 2-surface lesson, applied all night and missed on my own work`
- `655aa815 A stamper with 15 tests and its own mutation harness had stamped 0 of 148 briefs, because it was wired to 1 of 2 builders`
- `507ad73c B84 field 1 of 4, built because it costs nothing, and the other 3 named with what each actually needs`
- `c8a12052 A producer whose figures were RIGHT and which could not run: 2 independent faults made the number entry B84 quotes him unproducible`
- `a2ecde6b A question is not a ruling: the board refused 9 of my own ruled dates, and 4 of his annotations ask rather than decide`
- `249f8122 The reached-producers rule extended to today, composed with a date-independent ratchet because closing 1 date would have left 229 debts on 36 others`
