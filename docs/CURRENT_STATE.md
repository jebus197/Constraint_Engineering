# CDSFL Current State

Generated: 8 September 2026 02:14 BST (2026-09-08T02:14:44+01:00)

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
- **Last commit (the PARENT of the commit containing this file):** `2230744` One defect shape, 12 instances, and 2 things that would have made a PoC release misleading
- **Committed:** 2026-09-08 00:35:09 +0100
- **Remote (as of the snapshot, before the sv push):** ahead of origin/main by 18
- **Working tree at snapshot time:** clean

---

## Tests

**5404 tests collected** at 8 September 2026 02:14 BST, HEAD `2230744` (`python3 -m pytest bench/tests/ --co -q`)

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

- `2230744 One defect shape, 12 instances, and 2 things that would have made a PoC release misleading`
- `ebd9e34 Wire the Wilson checker into the suite as a live ratchet`
- `0ebe0ee The panel's tool-call counter was 0 by construction, and I invented a provenance for a number that was already right`
- `29a432f The additive standard, enforced in both directions -- and it was itself unwired`
- `ae234e1 The panel broke 4 of my 5 fixes. All repaired, and the two seats disagreed on the worst one.`
- `cd40243 Five approved fixes: Opus seats, severity wiring, round-0 root cause, S* promoted, second key store`
- `4319935 `rs` now has to report the recovery script's exit code, and it never had an obligation at all`
- `2bab3ff Remove the duplicate MC commands: ext, rc and rr`
- `25fefbf Overnight report for 2026-09-07, with 3 corrections to what was reported earlier`
- `2c1b57c Codex was right: 3 files parse only on Python 3.12+, and 14 tests import one`
