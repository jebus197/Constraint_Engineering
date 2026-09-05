# CDSFL Current State

Generated: 5 September 2026 14:13 BST (2026-09-05T14:13:50+01:00)

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
- **Last commit (the PARENT of the commit containing this file):** `554cb59` The panel has 4 distinct configurations across 5 seats, and the guard caught my own artefact
- **Committed:** 2026-09-05 14:13:39 +0100
- **Remote (as of the snapshot, before the sv push):** ahead of origin/main by 4
- **Working tree at snapshot time:** clean

---

## Tests

**5168 tests collected** at 5 September 2026 14:13 BST, HEAD `554cb59` (`python3 -m pytest bench/tests/ --co -q`)

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

- `554cb59 The panel has 4 distinct configurations across 5 seats, and the guard caught my own artefact`
- `ee72ad5 D5's "why not fix the other instruments too": 4 of the 5 alarms were the tool's own`
- `21ace37 Housekeeping done, and the v2 path in the audit script is load-bearing, not stale`
- `7d4f5fe The frozen threshold IS reachable: 111-day-old anti-cooking condition discharged`
- `f5aef4f sv: the record holds 122 open decisions, not 9, and a phantom ruling has stood 110 days`
- `3377e67 I reported 9 open decisions; the record holds 122, and a phantom one has stood 110 days`
- `94f5035 Revised morning report: decisions first, and the 55-item list carries a staleness caveat`
- `55d02eb sv: the panel was never tool-enabled, and 3 of 4 red guards were wrong`
- `b6a2032 The stop was right: I built a 488-agent runaway, and nothing was lost`
- `99cc5bb Morning report Part 4: suite green at 5153, and 3 of 4 red guards were wrong`
