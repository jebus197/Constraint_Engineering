# CDSFL Current State

Generated: 30 October 2026 01:41 GMT (2026-10-30T01:41:17+00:00)

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
- **Last commit (the PARENT of the commit containing this file):** `5d22540b` I typed a future timestamp again, and this linter could not see the shape I write
- **Committed:** 2026-10-30 01:22:01 +0000
- **Remote (as of the snapshot, before the sv push):** ahead of origin/sim/shakedown-2026-09-29 by 6
- **Working tree at snapshot time:** DIRTY — snapshot-time working tree listed below (NOT the sv commit's file list)

Uncommitted files at snapshot time — the working tree as it stood before the sv commit, NOT that commit's file list:
- `M experimental_notes/CDSFL_MASTER_TASK_LIST.md`
- `M experimental_notes/Morning_Report_2026-10-30.txt`
- `M resources/RECOVERY.md`

---

## Tests

**13535 tests collected** at 30 October 2026 01:41 GMT, HEAD `5d22540b` + uncommitted working tree (`python3 -m pytest bench/tests/ --co -q`)

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

- `5d22540b I typed a future timestamp again, and this linter could not see the shape I write`
- `0a5b971e His 7 questions are answered AND RECORDED, and their answers were in a sandbox`
- `39b6b9ac A test refused my commit and it was right: I typed a timestamp 2.1 minutes ahead`
- `27063184 4 entries closed on executed evidence, and 2 attributions of mine corrected`
- `cacd22d4 The board's own report, and the producer for the figure it rests on`
- `589f7bc6 THE ONE board found a 9th failure and it was my own repair removing a capability`
- `5180b471 3 register checks still assumed 1 ticket per entry, and his `qs` ruling broke that by design`
- `22528777 the miss ledger was split across 2 module objects, and the guard that refused the fix was celebrating its own obsolescence`
- `ec03aa25 3 silent capability lookups now announce, and the instrument that measured them was reading the wrong ledger`
- `553df767 B21 has a design for his yes-or-no, and writing it found a live seat routed as the weakest of all`
