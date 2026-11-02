# CDSFL Current State

Generated: 2 November 2026 16:37 GMT (2026-11-02T16:37:51+00:00)

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
- **Last commit (the PARENT of the commit containing this file):** `cf215aa8` B77's recommendation corrected a second time to the right design, a folded-back file credited the wrong seat, and 8 predicate slips of one shape
- **Committed:** 2026-11-02 16:19:58 +0000
- **Remote (as of the snapshot, before the sv push):** ahead of origin/sim/shakedown-2026-09-29 by 13
- **Working tree at snapshot time:** DIRTY — snapshot-time working tree listed below (NOT the sv commit's file list)

Uncommitted files at snapshot time — the working tree as it stood before the sv commit, NOT that commit's file list:
- `M bench/seat_readiness.py`
- `M bench/tests/test_a_seat_declares_what_it_is_missing_2026-11-02.py`
- `M bench/ux_backend_2026-10-20.py`
- `M experimental_notes/CDSFL_MASTER_TASK_LIST.md`
- `M resources/RECOVERY.md`
- `M scripts/the_seat_readiness_mutations_2026-11-02.py`
- `?? bench/logs/severity_bounds_validation_20261102T004713Z_20261102T004713Z/panel_worktree_harvest/`
- `?? bench/logs/study_run1b_rerun_20261102T033919Z_20261102T033920Z/`

---

## Tests

**14857 tests collected** at 2 November 2026 16:37 GMT, HEAD `cf215aa8` + uncommitted working tree (`python3 -m pytest bench/tests/ --co -q`)

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

- `cf215aa8 B77's recommendation corrected a second time to the right design, a folded-back file credited the wrong seat, and 8 predicate slips of one shape`
- `a59fc3ac 7 of 23 seat designs judged, a ruling of his found uncarried in prose, and 2 of 8 commit failures that were my own editing rather than defects`
- `db28f43e Runway Stage 1 answered on both items, 7 decisions written up for him, and 3 claims of mine corrected within minutes of being made`
- `4ba32d32 5 ruled entries closed with evidence, and 2 of them were already repaired while their entries said OPEN`
- `b7cf4c13 cy has a deadline now; the Stop gate was being killed by a timeout; 1 declaration admits a model; and the fix comparator refuses to rank`
- `66c487d0 Predictions for the live re-run, committed while it is at round 2 of 12 and its outcome unknown`
- `69628a38 The resume pointer records the re-run as running, with the diagnosis that changed its design`
- `130a8a35 The re-run was diagnosed before being repeated, and 3 of my own scripts were refusing nothing`
- `d4631894 The morning report carries the severity-spec defect it was written before finding, and the resume pointer is current`
- `4832fedd B21's role layer built and guarded; the run scored; 2 defects found in the severity mechanics it was validating`
