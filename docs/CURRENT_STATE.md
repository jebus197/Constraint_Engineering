# CDSFL Current State

Generated: 12 September 2026 21:30 BST (2026-09-12T21:30:59+01:00)

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
- **Last commit (the PARENT of the commit containing this file):** `1d8d305` The 59-entry decision file, as a TTS text and a markdown mirror
- **Committed:** 2026-09-12 00:04:40 +0100
- **Remote (as of the snapshot, before the sv push):** ahead of origin/main by 174
- **Working tree at snapshot time:** clean

---

## Tests

**7351 tests collected** at 12 September 2026 21:30 BST, HEAD `1d8d305` (`python3 -m pytest bench/tests/ --co -q`)

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

- `1d8d305 The 59-entry decision file, as a TTS text and a markdown mirror`
- `7294680 Parking the hook now takes effect immediately, because renaming a key did not`
- `8c0967d Supplementary list: the 59 entries the work generated, with their source`
- `48db9c2 Park the Stop hook on his instruction, reversibly`
- `c112dc1 A command he explains is still a command, and there is now 1 parser not 2`
- `86fdcf0 Flag the 9.4 cardinality glitch on item 46, per the founder's instruction`
- `fdaadc7 The Stop hook read its own words as the founder's and erased his command`
- `529dada The triage gate cannot see an entry that says it needs his ruling`
- `ffae638 rs: fresh resume pointer, recording what the restore corrected`
- `8768311 Audit coverage is complete: 84 of 84, and 30 carry an overclaim`
