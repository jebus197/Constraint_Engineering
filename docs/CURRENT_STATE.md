# CDSFL Current State

Generated: 17 October 2026 22:52 BST (2026-10-17T22:52:36+01:00)

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
- **Last commit (the PARENT of the commit containing this file):** `31a85e94` B25 is complete: all 318 of his annotations carry a verdict with its evidence
- **Committed:** 2026-10-17 22:44:14 +0100
- **Remote (as of the snapshot, before the sv push):** up to date with origin/sim/shakedown-2026-09-29
- **Working tree at snapshot time:** clean

---

## Tests

**12602 tests collected** at 17 October 2026 22:52 BST, HEAD `31a85e94` (`python3 -m pytest bench/tests/ --co -q`)

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

- `31a85e94 B25 is complete: all 318 of his annotations carry a verdict with its evidence`
- `ed4c0ee0 B25: 241 of 318 verdicted, and his duplicate rule is the register's own rule`
- `efe1c313 B28: he ruled state be detected not declared, and the runners still declare it`
- `0136a324 B25: past halfway, 173 of 318 annotations verdicted`
- `d77333b4 The timestamp hook was right and my reason for it was wrong`
- `480c9379 I typed 10 timestamps instead of reading the clock; now a hook refuses it`
- `29565256 B25: 9 files audited, 140 of 318 annotations verdicted`
- `d5c668bb B25: 8 files audited, and a correction that stopped 2 wrong entries`
- `07ce845d B25: a keying defect that would have silently lost up to 37 verdicts`
- `c3c6b83e B27: the review stop fires on a flag, and he gave it a condition it lacks`
