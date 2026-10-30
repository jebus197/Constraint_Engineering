# CDSFL Current State

Generated: 30 October 2026 12:53 GMT (2026-10-30T12:53:20+00:00)

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
- **Last commit (the PARENT of the commit containing this file):** `671b9133` His inline markers were invisible to the reader, including 2 rulings I acted on
- **Committed:** 2026-10-30 11:45:43 +0000
- **Remote (as of the snapshot, before the sv push):** ahead of origin/sim/shakedown-2026-09-29 by 1
- **Working tree at snapshot time:** DIRTY — snapshot-time working tree listed below (NOT the sv commit's file list)

Uncommitted files at snapshot time — the working tree as it stood before the sv commit, NOT that commit's file list:
- `M experimental_notes/All_Verdicts_Consolidated_2026-10-30.md`
- `M experimental_notes/All_Verdicts_Consolidated_2026-10-30.txt`
- `M resources/ONBOARDING.md`
- `M resources/RECOVERY.md`

---

## Tests

**13705 tests collected** at 30 October 2026 12:53 GMT, HEAD `671b9133` + uncommitted working tree (`python3 -m pytest bench/tests/ --co -q`)

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

- `671b9133 His inline markers were invisible to the reader, including 2 rulings I acted on`
- `686e08a8 sv: the board held the prediction, the triage could not see 72 of 186 entries, and 5 of 6 tickets checked were already done`
- `9f8003dd 2 more tickets discharged, and 1 of his questions was filed as a proposed fix`
- `2f98fcfa 3 gate tickets were stale recording, not undone work, and are closed`
- `8643fbd3 The paid-dispatch gate missed the plainest phrasing of a paid dispatch`
- `04a89609 6 figures about the panel backlog had no producer, and the split is withheld`
- `044b2c75 Correct the consolidated file: it called a validator-refused brief ready`
- `1477c7bf B21's panel brief was refused by the validator, and I had called it ready`
- `9014f98f Every outstanding verdict in 1 file, built from the register not from 5 reports`
- `8a05a1e3 The blocker triage could not see 72 of 186 entries, nor any that were open`
