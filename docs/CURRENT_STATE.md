# CDSFL Current State

Generated: 17 October 2026 13:59 BST (2026-10-17T13:59:50+01:00)

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
- **Last commit (the PARENT of the commit containing this file):** `98710718` B3: regenerate the parked file, and stop a teardown chmodding his machine
- **Committed:** 2026-10-17 13:56:38 +0100
- **Remote (as of the snapshot, before the sv push):** up to date with origin/sim/shakedown-2026-09-29
- **Working tree at snapshot time:** DIRTY — snapshot-time working tree listed below (NOT the sv commit's file list)

Uncommitted files at snapshot time — the working tree as it stood before the sv commit, NOT that commit's file list:
- `?? experimental_notes/Parked_File_And_A_Teardown_Reaching_Out_2026-10-17.md`

---

## Tests

**12206 tests collected** at 17 October 2026 13:59 BST, HEAD `98710718` + uncommitted working tree (`python3 -m pytest bench/tests/ --co -q`)

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

- `98710718 B3: regenerate the parked file, and stop a teardown chmodding his machine`
- `73025e95 C32: the harness registry does not work like the ticket register, and should not`
- `63955c65 C31: the register beats a word search on the error that matters`
- `e3c94518 C30: the register was dropping his shortest rulings, and they are his most decisive`
- `7534743e C5: the serialisation cure is a hypothesis, and its measurement is now scheduled`
- `ed3c1d73 C3: the note standard is v1.8, and half of its new rule was already a rule`
- `ab1bf1be A19 measured: the script that seemed to argue against the flag says the opposite`
- `542bca49 V9: the evidence must go red, and 2 of 19 DONE entries do not`
- `4949d5f9 sv: the overnight task list, 19 commits, guard set 793 to 927`
- `545f9405 Closing report on the overnight task list, paired TTS and markdown`
