# CDSFL Current State

Generated: 4 October 2026 03:00 BST (2026-10-04T03:00:26+01:00)

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
- **Last commit (the PARENT of the commit containing this file):** `1259b87` the run-end harvest, and a discriminator that was looking for a field that does not exist
- **Committed:** 2026-10-03 13:51:00 +0100
- **Remote (as of the snapshot, before the sv push):** ahead of origin/sim/shakedown-2026-09-29 by 2
- **Working tree at snapshot time:** DIRTY — snapshot-time working tree listed below (NOT the sv commit's file list)

Uncommitted files at snapshot time — the working tree as it stood before the sv commit, NOT that commit's file list:
- `M  START_HERE.md`
- `M  bench/fingerprints/CC2-SIM.json`
- `M  bench/fingerprints/CC2.json`
- `M  bench/fingerprints/ChatGPT-SIM.json`
- `M  bench/fingerprints/ChatGPT.json`
- `M  bench/fingerprints/Codex-SIM.json`
- `M  bench/fingerprints/Codex.json`
- `M  bench/fingerprints/DeepSeek-SIM.json`
- `M  bench/fingerprints/DeepSeek.json`
- `M  bench/fingerprints/Fable-SIM.json`
- `M  bench/fingerprints/Gemini-SIM.json`
- `M  bench/fingerprints/Gemini.json`
- `A  bench/logs/study_run1_2026-10-03_20261003T083519Z/runner_state.json`
- `A  bench/logs/study_run1b_2026-10-03_20261003T100439Z/runner_state.json`
- `A  bench/logs/study_run1b_2026-10-03_20261003T100439Z/study_run1b_2026-10-03_report.json`
- … and 65 more, not shown (list capped at 15 of 80 — run `git status --porcelain` for the full set)

---

## Tests

**10027 tests collected** at 4 October 2026 03:00 BST, HEAD `1259b87` + uncommitted working tree (`python3 -m pytest bench/tests/ --co -q`)

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

- `1259b87 the run-end harvest, and a discriminator that was looking for a field that does not exist`
- `10606f0 the barrier was discarding findings for their quoting, and its ambiguity guard was overridden by the branch below it`
- `1d51fee sv: the adjudicated merge, refused-body visibility, the widened guard as a post-run sweep, and 23 board failures repaired`
- `c62ac5a The study now carries its own reason, and the compaction alert exists at last`
- `a0a2283 sv: name the commit in the session state so A23 passes`
- `6b3f689 sv: suite citation for the 2026-10-03 session state block (follow-up to cd19903; memory written at 06:09)`
- `cd19903 sv: 3 panel rounds, the Haiku arm, and an adjudication neither seat's fix wins`
- `2a3d6e3 sv: 2 October 2026 — the $HOME hole, the green board, and the watch that starts itself`
- `abef2f2 fix: $HOME was in scope, so the listing that finds the key store was not flagged`
- `854efaa fix: the full suite found 4 same-day regressions the 501-test subset cannot reach`
