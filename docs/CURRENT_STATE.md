# CDSFL Current State

Generated: 15 October 2026 12:46 BST (2026-10-15T12:46:51+01:00)

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
- **Last commit (the PARENT of the commit containing this file):** `82efc9b1` board: 24 of 33 fixed, and the rest classified in B11 rather than suppressed
- **Committed:** 2026-10-15 11:24:47 +0100
- **Remote (as of the snapshot, before the sv push):** up to date with origin/sim/shakedown-2026-09-29
- **Working tree at snapshot time:** DIRTY — snapshot-time working tree listed below (NOT the sv commit's file list)

Uncommitted files at snapshot time — the working tree as it stood before the sv commit, NOT that commit's file list:
- `M resources/MEMORY_EXCLUSIONS.md`
- `M resources/RECOVERY.md`

---

## Tests

**11371 tests collected** at 15 October 2026 12:46 BST, HEAD `82efc9b1` + uncommitted working tree (`python3 -m pytest bench/tests/ --co -q`)

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

- `82efc9b1 board: 24 of 33 fixed, and the rest classified in B11 rather than suppressed`
- `dac69496 board: 3 more of the 33, and 2 of them were my notes citing what nobody can open`
- `9148e0a3 board: fix 20 of the 33 failures, all of them mine`
- `ce820098 sv: both free runs converged, B7 and B9 fixed, B10 found, programme down to arm5`
- `cb732717 B10: the note-lint ratchet is blind to the standard stamp, by construction`
- `21cb7e46 correct: the note lint is PATH-SENSITIVE, and my ratchet checks were unsound`
- `d87fea07 tracker: advance the resume pointer — both runs done, both converged`
- `87846b68 chore: carry the citation repairs the B9 hardening shifted`
- `c9dcca45 harden B9: an unusable staged root now falls back loudly instead of crashing`
- `90a9713d notes: the 2 free runs, technical and plain-English, with the TTS companion`
