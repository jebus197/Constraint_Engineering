# CDSFL Current State

Generated: 31 August 2026 19:58 BST (2026-08-31T19:58:29+01:00)

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
- **Last commit (the PARENT of the commit containing this file):** `20ce683` Panel fixes, part 4: the four archive guards re-measured, not deleted
- **Committed:** 2026-08-31 19:52:05 +0100
- **Remote (as of the snapshot, before the sv push):** ahead of origin/main by 7
- **Working tree at snapshot time:** clean

---

## Tests

**4607 tests collected** at 31 August 2026 19:58 BST, HEAD `20ce683` (`python3 -m pytest bench/tests/ --co -q`)

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

- `20ce683 Panel fixes, part 4: the four archive guards re-measured, not deleted`
- `e7c4ed7 Panel fixes, part 3: post-sweep reconciliation, and the bare-fence extractor case`
- `f198d0b Panel fixes, part 2: the second 500-char cut, and a comment that misdescribed its own function`
- `08ab43c Panel fixes, part 1: one clear-list at both rescue sites; macrophage residuals closed`
- `25f4f49 Three founder-ruled fixes, each tool-verified; the routing architecture was already right`
- `77c3d1a Lint: numerals stay numerals (Rule 27)`
- `a4f710f Panel review: I shipped a RED suite, and my option-A fix removed the A4 fail-safe`
- `5abe4f8 Overnight run COMPLETE: converged at round 3, zero residue, falsification core live`
- `d04fada Runway 4B.8: seeded exam pairs are NOT vaulted, and my "already vaulted" was over-broad`
- `8f04a1a Re-arm the corrected-copy ask; the reversal it endangered is now gated`
