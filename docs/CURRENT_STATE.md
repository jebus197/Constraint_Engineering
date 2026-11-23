# CDSFL Current State

Generated: 23 November 2026 02:15 GMT (2026-11-23T02:15:22+00:00)

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
- **Last commit (the PARENT of the commit containing this file):** `d99c6360` batch 4: B207 fed its reader, B209's guard corrected, B211 raised
- **Committed:** 2026-11-23 00:37:49 +0000
- **Remote (as of the snapshot, before the sv push):** ahead of origin/sim/shakedown-2026-09-29 by 8
- **Working tree at snapshot time:** DIRTY — snapshot-time working tree listed below (NOT the sv commit's file list)

Uncommitted files at snapshot time — the working tree as it stood before the sv commit, NOT that commit's file list:
- `M  docs/CURRENT_STATE.md`
- `M experimental_notes/data/output_hashes.json`
- `M  resources/MEMORY_EXCLUSIONS.md`
- `M  resources/ONBOARDING.md`
- `MM resources/RECOVERY.md`

---

## Tests

**18419 tests collected** at 23 November 2026 02:15 GMT, HEAD `d99c6360` + uncommitted working tree (`python3 -m pytest bench/tests/ --co -q`)

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

- `d99c6360 batch 4: B207 fed its reader, B209's guard corrected, B211 raised`
- `7dd07521 batch 3: B209 recorded, B210 found by a refused board, the census validated`
- `ca0320ba Batch 2: the panel's second round found 2 defects neither seat saw, and the pre-board check found 1 the new test could not`
- `37b87d10 The autonomy handover becomes a mechanism, and the board that refused it found 15 faults of mine`
- `b1d5d5db 4 entries investigated, 4 wrong claims of mine corrected, and a hand-edit caught by its own guard`
- `fa0fcb48 7 entries closed by running their evidence, and 6 silent failures found by doing it`
- `b8f556d3 A guard that ran a 45-minute board to prove something that finishes 221 lines earlier`
- `725ec976 A board fix that was half a fix, and the 1-line completion that would have turned the gate into a rubber stamp`
- `bb315555 The full suite ran against a committed tree, and 8 of its 10 new failures were invisible to the board that passed it`
- `6304f771 The 3 panel rounds he ordered, run blind and joint, and every round refuted something in my own brief`
