# CDSFL Current State

Generated: 29 September 2026 13:51 BST (2026-09-29T13:51:29+01:00)

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
- **Last commit (the PARENT of the commit containing this file):** `ea43d3f` Apply both of Astra's corrections; assess its distributed-compute spec
- **Committed:** 2026-09-29 13:49:56 +0100
- **Remote (as of the snapshot, before the sv push):** up to date with origin/main
- **Working tree at snapshot time:** clean

---

## Tests

**8966 tests collected** at 29 September 2026 13:51 BST, HEAD `ea43d3f` (`python3 -m pytest bench/tests/ --co -q`)

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

- `ea43d3f Apply both of Astra's corrections; assess its distributed-compute spec`
- `d6eeb90 Retract the invented Wolfram denial rule; explorer A-vs-M; I31 cannot fire`
- `9c39332 sv: resume pointer rewritten for compaction — the shakedown is next and is NOT blocked`
- `28c4234 None of the 3 "rulings before the run" actually blocks the run, checked against the code`
- `f33da34 sv: the study window measured against the founder's own marker, and it changes nothing`
- `9e9dc3f GREEN: 8878 passed, 0 failed — and 3 guards moved to commit time so tonight does not repeat`
- `1cfc30e The suite found 6 more, and all 6 were consequences of the work that made it green`
- `6b9074a Three red tests had one cause: simulated rehearsals counted as real archive evidence`
- `177dac6 The --help guard caught my own measurement script, and the suite record says so`
- `f60df73 The founder's September notes, and the release plan recorded as the runway's last step`
