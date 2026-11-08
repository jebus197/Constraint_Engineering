# CDSFL Current State

Generated: 8 November 2026 22:30 GMT (2026-11-08T22:30:28+00:00)

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
- **Last commit (the PARENT of the commit containing this file):** `675af51e` I built 5 of his entries and left all 5 marked OPEN: the 2-surface lesson, applied all night and missed on my own work
- **Committed:** 2026-11-08 22:16:11 +0000
- **Remote (as of the snapshot, before the sv push):** ahead of origin/sim/shakedown-2026-09-29 by 68
- **Working tree at snapshot time:** clean

---

## Tests

**16420 tests collected** at 8 November 2026 22:30 GMT, HEAD `675af51e` (`python3 -m pytest bench/tests/ --co -q`)

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

- `675af51e I built 5 of his entries and left all 5 marked OPEN: the 2-surface lesson, applied all night and missed on my own work`
- `655aa815 A stamper with 15 tests and its own mutation harness had stamped 0 of 148 briefs, because it was wired to 1 of 2 builders`
- `507ad73c B84 field 1 of 4, built because it costs nothing, and the other 3 named with what each actually needs`
- `c8a12052 A producer whose figures were RIGHT and which could not run: 2 independent faults made the number entry B84 quotes him unproducible`
- `a2ecde6b A question is not a ruling: the board refused 9 of my own ruled dates, and 4 of his annotations ask rather than decide`
- `249f8122 The reached-producers rule extended to today, composed with a date-independent ratchet because closing 1 date would have left 229 debts on 36 others`
- `2f3b7af3 A report that counts its own commits cannot carry a live figure: the corrected 5 went stale by 1 the instant the correction was committed`
- `9f98ce27 The closing report claimed 7 commits and 2 refusals; git says 5 and the session's own logs say 4, and both figures were typed rather than derived`
- `0630a5b1 B129, B93 and B96 on his rulings, and the 2-surface lesson applied on the third attempt: marking an entry DONE is not closing its ticket`
- `2e5665f0 B135 closes at 7 of 13 delegated and 6 excluded on their merits: the invisible set was never the weaker set, and 6 instrument false positives came out of reading it`
