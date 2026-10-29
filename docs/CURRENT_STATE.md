# CDSFL Current State

Generated: 29 October 2026 01:33 GMT (2026-10-29T01:33:30+00:00)

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
- **Last commit (the PARENT of the commit containing this file):** `14e1a5c5` T3 closed and marked DONE; 2 questions left for his ruling rather than decided
- **Committed:** 2026-10-29 01:25:25 +0000
- **Remote (as of the snapshot, before the sv push):** up to date with origin/sim/shakedown-2026-09-29
- **Working tree at snapshot time:** DIRTY — snapshot-time working tree listed below (NOT the sv commit's file list)

Uncommitted files at snapshot time — the working tree as it stood before the sv commit, NOT that commit's file list:
- `M bench/tests/test_what_a_round_waits_on_its_slowest_seat_2026-10-28.py`
- `M resources/RECOVERY.md`
- `M scripts/note_vagueness_lint.py`
- `M scripts/what_a_round_waits_on_its_slowest_seat_2026-10-28.py`

---

## Tests

**13184 tests collected** at 29 October 2026 01:33 GMT, HEAD `14e1a5c5` + uncommitted working tree (`python3 -m pytest bench/tests/ --co -q`)

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

- `14e1a5c5 T3 closed and marked DONE; 2 questions left for his ruling rather than decided`
- `5be94c2f T3 converged, and the barrier his ruling asked for is measured: one seat is the critical path in 5 of 5 rounds`
- `479fbfb9 B24 closed with its verification, and marked DONE`
- `c5f681b0 B24 built: Rule 27 enforced in full going forward, on his ruling of 2026-10-19`
- `31ba2157 The previous commit message was eaten by the shell: the corrected text, and the lesson generalised`
- `c6930ab5 T4: the chat source is RETIRED on his ruling, with the condition tested rather than assumed`
- `481aaa03 T3 entry corrected to record the panel's refusal of --severity-spec, and the task list gains its foot-line`
- `52ab58a0 T2 DONE: the joint round found what neither blind seat saw, and 3 of my own claims are withdrawn`
- `c8152668 T2 blind half: both seats refused tonight's --severity-spec, and found 2 real defects in my own producer`
- `a6c50b9e T1 closed with its verification`
