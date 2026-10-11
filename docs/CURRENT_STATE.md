# CDSFL Current State

Generated: 12 October 2026 00:09 BST (2026-10-12T00:09:30+01:00)

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
- **Last commit (the PARENT of the commit containing this file):** `a4a5a4a6` two correct safety mechanisms were leaving a stale citation between them
- **Committed:** 2026-10-12 00:04:21 +0100
- **Remote (as of the snapshot, before the sv push):** ahead of origin/sim/shakedown-2026-09-29 by 6
- **Working tree at snapshot time:** DIRTY — snapshot-time working tree listed below (NOT the sv commit's file list)

Uncommitted files at snapshot time — the working tree as it stood before the sv commit, NOT that commit's file list:
- `M experimental_notes/Morning_Report_2026-10-12.md`
- `M resources/RECOVERY.md`

---

## Tests

**10885 tests collected** at 12 October 2026 00:09 BST, HEAD `a4a5a4a6` + uncommitted working tree (`python3 -m pytest bench/tests/ --co -q`)

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

- `a4a5a4a6 two correct safety mechanisms were leaving a stale citation between them`
- `45ba58b4 item 5: the domain-verdict gap is measured again, and my own withdrawal was miscalculated`
- `6a2e87f0 item 12: a human review fires on substantial evidence, and the naive design was refuted first`
- `8288b40b item 9: the round count is computed per run, and my own 2026-09-20 wiring was wrong`
- `a1014a47 item 14: the sim seam lost substance and 3 guards went blind to a wrapper split`
- `7a8fd077 I invented 2 timestamps; the clock was right and 3 guard designs cannot catch it`
- `183f7dc2 sv: the substance test is wired after measuring it, and his 0.05 is pinned`
- `fda2dfcd morning report extended: the substance test is wired and the risk was measured, not asserted`
- `be5ff31c his 0.05 false-alarm proportion pinned, with the ruling it depends on`
- `44e82fe5 the runner now refuses a reply that is merely non-empty, and the risk was measured first`
