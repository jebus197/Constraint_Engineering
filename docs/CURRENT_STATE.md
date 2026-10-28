# CDSFL Current State

Generated: 28 October 2026 19:10 GMT (2026-10-28T19:10:49+00:00)

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
- **Last commit (the PARENT of the commit containing this file):** `ec7cd73b` Baseline triage, batch 4: 34 of 36, and 4 more guards were accusing correct code
- **Committed:** 2026-10-28 18:48:41 +0000
- **Remote (as of the snapshot, before the sv push):** up to date with origin/sim/shakedown-2026-09-29
- **Working tree at snapshot time:** DIRTY — snapshot-time working tree listed below (NOT the sv commit's file list)

Uncommitted files at snapshot time — the working tree as it stood before the sv commit, NOT that commit's file list:
- `M bench/tests/test_precommit_guard_2026-09-09.py`
- `M resources/RECOVERY.md`

---

## Tests

**13030 tests collected** at 28 October 2026 19:10 GMT, HEAD `ec7cd73b` + uncommitted working tree (`python3 -m pytest bench/tests/ --co -q`)

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

- `ec7cd73b Baseline triage, batch 4: 34 of 36, and 4 more guards were accusing correct code`
- `dc5e4280 Baseline triage, batch 3: 27 of 36, and 2 facilities had silently stopped being tested`
- `b3ad797d Baseline triage, batch 2: 13 more of the 36, and 3 of them were guards accusing correct code`
- `042d6e89 Baseline triage, batch 1: 4 of the 36 fixed, and 2 of them were mine`
- `a39d8da6 His login policy built as a route probe that reads the roster, and Rule 14a reached for the first time`
- `fd2eb1c5 B37 answered on evidence, and the overnight run is blocked on an expired CLI login`
- `2f3388f6 The ticket store over-matched because chat items carried no identity, and the chat half was never reachable`
- `90a6d4bd Outstanding rulings for 2026-10-27: 10 decisions, each with its evidence and its register id`
- `2534c614 Quiet run reverted to 3 and the gamma arm repaired, on his rulings of 2026-10-27`
- `931bcf2e The quiet run is not the lever: the panel refuted my own recommendation and corrected my headline by 37%`
