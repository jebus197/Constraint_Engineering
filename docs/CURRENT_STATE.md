# CDSFL Current State

Generated: 7 November 2026 21:10 GMT (2026-11-07T21:10:48+00:00)

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
- **Last commit (the PARENT of the commit containing this file):** `45cea3f9` The complete board returned 11 failures: 16 of 17 fixed, the 1 survivor exactly as predicted, and 10 new ones that this session's own repairs created
- **Committed:** 2026-11-07 20:31:36 +0000
- **Remote (as of the snapshot, before the sv push):** ahead of origin/sim/shakedown-2026-09-29 by 24
- **Working tree at snapshot time:** DIRTY — snapshot-time working tree listed below (NOT the sv commit's file list)

Uncommitted files at snapshot time — the working tree as it stood before the sv commit, NOT that commit's file list:
- `A  bench/tests/test_a_restatement_must_see_the_anchor_2026-11-07.py`
- `M  bench/tests/test_a_ticket_identity_survives_a_reword_2026-10-17.py`
- `M  bench/ticket_store.py`
- `M  bench/tickets/tickets.jsonl`
- `M  bench/tickets/tickets_searches.jsonl`
- `MM experimental_notes/The_Complete_Board_And_Its_Ten_New_Failures_2026-11-07.md`
- `MM resources/MEMORY_EXCLUSIONS.md`
- `M resources/RECOVERY.md`
- `A  scripts/the_anchor_in_the_identity_check_mutations_2026-11-07.py`
- `?? scripts/the_gate_board_serialises_the_tree_2026-11-07.py`

---

## Tests

**15945 tests collected** at 7 November 2026 21:10 GMT, HEAD `45cea3f9` + uncommitted working tree (`python3 -m pytest bench/tests/ --co -q`)

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

- `45cea3f9 The complete board returned 11 failures: 16 of 17 fixed, the 1 survivor exactly as predicted, and 10 new ones that this session's own repairs created`
- `e796a010 The answer to his repeat question was wrong by a key spelling: 3 live entries were called repeats on an empty string, B20 among them, and 0 of the 29 are repeats at all`
- `6955397a A guard that got faster had stopped testing: 12 of its 13 failures were a help handler I added at module level, and the cost figure I prepared for his gate decision was understated 11-fold because I timed a test that was not running`
- `6751cdb0 4 verdicts on 1 figure and only 1 was right, so the night's lesson is that a seat which catches your error can commit it and your correction of it can be worse than both`
- `58995566 The panel round refuted me 4 times, my correction of the seat that caught me was itself wrong, and the method I reached for had been in the project for 25 days`
- `624686db He ruled on a line cap he never set, the report that asked him was hand-written, and recording his ruling broke 3 instruments that each held a different view of what he owes`
- `e2a87dac The complete board's largest failure cluster was one interval helper, and the detector that found it is blind to 43% of the same algebra`
- `e0feed27 A resume pointer's git facts were unreachable by the guard written to check them, and the FOLLOW that found it took 3 passes`
- `da38d9ac The independent check he ordered never ran: a 2-seat pair stood in for a 5-seat panel, and the cause is the dispatcher's own default`
- `4d363c52 The figure withdrawn from B120 now has a producer, and it says the withdrawn number overstated the evidence by 9 orders of magnitude`
