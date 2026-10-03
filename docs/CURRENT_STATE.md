# CDSFL Current State

Generated: 3 October 2026 06:19 BST (2026-10-03T06:19:47+01:00)

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
- **Last commit (the PARENT of the commit containing this file):** `6b3f689` sv: suite citation for the 2026-10-03 session state block (follow-up to cd19903; memory written at 06:09)
- **Committed:** 2026-10-03 06:17:56 +0100
- **Remote (as of the snapshot, before the sv push):** up to date with origin/sim/shakedown-2026-09-29
- **Working tree at snapshot time:** DIRTY — snapshot-time working tree listed below (NOT the sv commit's file list)

Uncommitted files at snapshot time — the working tree as it stood before the sv commit, NOT that commit's file list:
- `M resources/RECOVERY.md`

---

## Tests

**9793 tests collected** at 3 October 2026 06:19 BST, HEAD `6b3f689` + uncommitted working tree (`python3 -m pytest bench/tests/ --co -q`)

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

- `6b3f689 sv: suite citation for the 2026-10-03 session state block (follow-up to cd19903; memory written at 06:09)`
- `cd19903 sv: 3 panel rounds, the Haiku arm, and an adjudication neither seat's fix wins`
- `2a3d6e3 sv: 2 October 2026 — the $HOME hole, the green board, and the watch that starts itself`
- `abef2f2 fix: $HOME was in scope, so the listing that finds the key store was not flagged`
- `854efaa fix: the full suite found 4 same-day regressions the 501-test subset cannot reach`
- `199cadb test: the stale-label trap now has a guard that bites`
- `bcbe0c1 fix: I read a label the runner documents as stale, and withdrew a true claim`
- `d8aa279 docs: 3 load-bearing claims in the guard note are refuted by execution`
- `7b583c0 docs: the census counted lines as occurrences and counted itself`
- `dc3921e test: the note's producer was an addition nothing executed`
