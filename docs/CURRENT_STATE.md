# CDSFL Current State

Generated: 7 October 2026 11:52 BST (2026-10-07T11:52:55+01:00)

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
- **Last commit (the PARENT of the commit containing this file):** `e41c7955` record the founder's clear/archive/delete ruling, with what it costs and what it would orphan
- **Committed:** 2026-10-06 08:59:39 +0100
- **Remote (as of the snapshot, before the sv push):** up to date with origin/sim/shakedown-2026-09-29
- **Working tree at snapshot time:** DIRTY — snapshot-time working tree listed below (NOT the sv commit's file list)

Uncommitted files at snapshot time — the working tree as it stood before the sv commit, NOT that commit's file list:
- `M resources/RECOVERY.md`
- `?? experimental_notes/WORK_IN_FLIGHT_2026-10-07.md`

---

## Tests

**10302 tests collected** at 7 October 2026 11:52 BST, HEAD `e41c7955` + uncommitted working tree (`python3 -m pytest bench/tests/ --co -q`)

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

- `e41c7955 record the founder's clear/archive/delete ruling, with what it costs and what it would orphan`
- `1fb40808 a retry no longer erases the attempt it replaces, and 2 zombie waiters are killed`
- `4634c6b9 overnight note: the all-runner probe adoption and the unreadable-field finding`
- `5b27084c the aliveness probe is adopted by every runner, and a brief could declare a field nothing would read`
- `765946c4 the joint round: the 2 seats CROSSED, and 7 pre-existing suite failures closed`
- `e0c9d252 the joint gate was skippable by omission, and 2 source-text assertions now execute`
- `b01bab1e CDSFL POST, the aliveness probe, enforced star topology, and a gamma coupling that needs a ruling`
- `413902a2 sv follow-up: the citation fixer re-pointed ONBOARDING after sv staged`
- `4e0199d1 sv: the severity test is restored on his 4th rejection, and 4 facilities that were off in simulation are on`
- `113d749e sv: the blockers were shown as settled, the ladder was inert in simulation, and the panel caught 3 faults in my own repairs`
