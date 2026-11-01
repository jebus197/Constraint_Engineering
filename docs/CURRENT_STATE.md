# CDSFL Current State

Generated: 1 November 2026 12:16 GMT (2026-11-01T12:16:44+00:00)

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
- **Last commit (the PARENT of the commit containing this file):** `619a7081` B63: the third instance, and 2 of the 3 were mine not the gate's
- **Committed:** 2026-11-01 04:42:12 +0000
- **Remote (as of the snapshot, before the sv push):** ahead of origin/sim/shakedown-2026-09-29 by 5
- **Working tree at snapshot time:** DIRTY — snapshot-time working tree listed below (NOT the sv commit's file list)

Uncommitted files at snapshot time — the working tree as it stood before the sv commit, NOT that commit's file list:
- `M bench/tickets/tickets.jsonl`
- `M bench/tickets/tickets_searches.jsonl`
- `M experimental_notes/CDSFL_MASTER_TASK_LIST.md`
- `M experimental_notes/Morning_Report_2026-11-01.md`
- `M experimental_notes/Morning_Report_2026-11-01.txt`
- `M resources/ONBOARDING.md`
- `M resources/RECOVERY.md`
- `?? scripts/a_first_anchored_window_is_unsatisfiable_2026-11-01.py`
- `?? scripts/how_many_decisions_actually_need_him_2026-11-01.py`

---

## Tests

**14203 tests collected** at 1 November 2026 12:16 GMT, HEAD `619a7081` + uncommitted working tree (`python3 -m pytest bench/tests/ --co -q`)

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

- `619a7081 B63: the third instance, and 2 of the 3 were mine not the gate's`
- `2322ad5f B63, B21 and C0001 corrected; a comment that inverted a safety default`
- `7a36ae2c A suite figure with no producer reached the recovery document`
- `0fab7c9b Five entries closed, R1 scheduled, and a fix that was hiding live work`
- `ea799770 His 12 annotations answered, the parked presentation rebuilt, and 3 entries were asking for rulings he had already given`
- `8b1f50d7 sv: the dispatch sequence is complete, 5 rounds and 0 paid seats, and his severity question is answered`
- `59e086f0 The severity panel answers his question, and finds a blocker the carry does not clear`
- `db8d48eb The polarity round converged on CONFIRMED BUT LATENT, and the reach is disputed by execution`
- `802d7834 sv: disc, R_k carries forward, 2 free panels, and 4 figures corrected`
- `39a26603 29 guards join the gate, the B22 panel refuted my own brief, and a full-record script was hanging on stdin`
