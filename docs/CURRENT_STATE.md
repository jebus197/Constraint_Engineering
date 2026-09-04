# CDSFL Current State

Generated: 5 September 2026 00:11 BST (2026-09-05T00:11:25+01:00)

---

## Git

- **Branch:** main
- **Last commit:** `59af19b` Announce compaction, because the remote interface does not
- **Committed:** 2026-09-04 23:02:27 +0100
- **Remote:** ahead of origin/main by 76
- **Working tree:** DIRTY — uncommitted changes present

Uncommitted files:
- `M experimental_notes/CDSFL_Agent_Operational_Plan.md`
- `M resources/RECOVERY.md`

---

## Tests

**4876 tests collected** at 5 September 2026 00:11 BST, HEAD `59af19b` + uncommitted working tree (`python3 -m pytest bench/tests/ --co -q`)

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

- `59af19b Announce compaction, because the remote interface does not`
- `fe02c87 Panel verification FULL RECORD, 2026-09-04, unfiltered`
- `1928de4 The panel refuted two things in my own change, and both refutations were right`
- `5a0f20c Fix the 4 errors I reported and did not fix, and convert a grep test to an executing one`
- `353151e Morning report, 2026-09-04: the gate that never fired, and the constant that looked like a measurement`
- `bc30e02 Two founder rulings of 2026-09-04, written where they will be read`
- `33ef614 The Valley gate has never fired, and the overlap record now exists`
- `8bc32a9 Session notes: the reduction work, the panel records, and the restore`
- `8d0a7ee The band-sensitivity diagnostic was a constant, and its test grepped the source`
- `643276b Consolidated report: name the subjects the lint flagged, in both copies`
