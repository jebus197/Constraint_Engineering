# CDSFL Current State

Generated: 30 September 2026 11:06 BST (2026-09-30T11:06:59+01:00)

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
- **Last commit (the PARENT of the commit containing this file):** `79aa4ec` Seat evidence was 100% gitignored, and the on-disk gate count was counting the copies
- **Committed:** 2026-09-30 10:57:14 +0100
- **Remote (as of the snapshot, before the sv push):** up to date with origin/sim/shakedown-2026-09-29
- **Working tree at snapshot time:** DIRTY — snapshot-time working tree listed below (NOT the sv commit's file list)

Uncommitted files at snapshot time — the working tree as it stood before the sv commit, NOT that commit's file list:
- `M resources/ONBOARDING.md`
- `M resources/RECOVERY.md`

---

## Tests

**9126 tests collected** at 30 September 2026 11:06 BST, HEAD `79aa4ec` + uncommitted working tree (`python3 -m pytest bench/tests/ --co -q`)

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

- `79aa4ec Seat evidence was 100% gitignored, and the on-disk gate count was counting the copies`
- `f3b35d9 The second invented Wolfram rule in 2 days, struck with his words beside it`
- `33f6a1e Cycle 3 simulation output: 4 arms, 1 halt, 0 clean convergences, 1 cause`
- `9a12ab1 Cycle 2 closed: exit 0, 42 findings, rho verified, 4 defects found and fixed`
- `0e51c7b Option 3 repaired the counter; corroboration SUPPLY is the next bound`
- `59a15f5 F2's 4th confirmation: the live artefact contradicts itself`
- `c1b6b3c F2 confirmed by a live out-of-sample prediction on the unfixed run`
- `7cc5514 The free panel found a correctness defect in the option-3 repair, and both seats found it independently`
- `b1a2263 VERIFIED: rho moved off 1.000 for the first time in a simulated run`
- `80f0a0c An interrupted simulated run cannot age the archive — the same defect, 3rd door`
