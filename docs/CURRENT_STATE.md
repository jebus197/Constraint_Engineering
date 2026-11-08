# CDSFL Current State

Generated: 8 November 2026 22:00 GMT (2026-11-08T22:00:46+00:00)

---

## Git

- **Branch:** sim/shakedown-2026-09-29
- **Last commit:** `655aa815` A stamper with 15 tests and its own mutation harness had stamped 0 of 148 briefs, because it was wired to 1 of 2 builders
- **Committed:** 2026-11-08 21:45:16 +0000
- **Remote:** ahead of origin/sim/shakedown-2026-09-29 by 67
- **Working tree:** DIRTY — uncommitted changes present

Uncommitted files:
- `A  bench/tests/test_the_gate_records_its_own_cost_2026-11-08.py`
- `M  bench/tests/test_tonights_producers_are_reached_2026-11-08.py`
- `M  experimental_notes/CDSFL_MASTER_TASK_LIST.md`
- `M  experimental_notes/Closing_Report_2026-11-08.md`
- `M  experimental_notes/Closing_Report_2026-11-08.txt`
- `M  experimental_notes/data/unreached_producers_2026-11-08.json`
- `M  hooks/pre-commit`
- `M  resources/MEMORY_EXCLUSIONS.md`
- `A  scripts/what_the_commit_gate_actually_costs_over_time_2026-11-08.py`

---

## Tests

Test count unavailable (pytest collection failed or timed out)

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

- `655aa815 A stamper with 15 tests and its own mutation harness had stamped 0 of 148 briefs, because it was wired to 1 of 2 builders`
- `507ad73c B84 field 1 of 4, built because it costs nothing, and the other 3 named with what each actually needs`
- `c8a12052 A producer whose figures were RIGHT and which could not run: 2 independent faults made the number entry B84 quotes him unproducible`
- `a2ecde6b A question is not a ruling: the board refused 9 of my own ruled dates, and 4 of his annotations ask rather than decide`
- `249f8122 The reached-producers rule extended to today, composed with a date-independent ratchet because closing 1 date would have left 229 debts on 36 others`
- `2f3b7af3 A report that counts its own commits cannot carry a live figure: the corrected 5 went stale by 1 the instant the correction was committed`
- `9f98ce27 The closing report claimed 7 commits and 2 refusals; git says 5 and the session's own logs say 4, and both figures were typed rather than derived`
- `0630a5b1 B129, B93 and B96 on his rulings, and the 2-surface lesson applied on the third attempt: marking an entry DONE is not closing its ticket`
- `2e5665f0 B135 closes at 7 of 13 delegated and 6 excluded on their merits: the invisible set was never the weaker set, and 6 instrument false positives came out of reading it`
- `f8305b1e B135 option 1, as he ruled: 4 of the 13 now execute the canonical helper, 4 made importable first, 1 excluded because delegating it would remove a feature`
