# CDSFL Current State

Generated: 29 September 2026 08:33 BST (2026-09-29T08:33:29+01:00)

---

## Git

- **Branch:** main
- **Last commit:** `9e9dc3f` GREEN: 8878 passed, 0 failed — and 3 guards moved to commit time so tonight does not repeat
- **Committed:** 2026-09-29 03:20:49 +0100
- **Remote:** up to date with origin/main
- **Working tree:** clean

---

## Tests

**8884 tests collected** at 29 September 2026 08:33 BST, HEAD `9e9dc3f` (`python3 -m pytest bench/tests/ --co -q`)

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

- `9e9dc3f GREEN: 8878 passed, 0 failed — and 3 guards moved to commit time so tonight does not repeat`
- `1cfc30e The suite found 6 more, and all 6 were consequences of the work that made it green`
- `6b9074a Three red tests had one cause: simulated rehearsals counted as real archive evidence`
- `177dac6 The --help guard caught my own measurement script, and the suite record says so`
- `f60df73 The founder's September notes, and the release plan recorded as the runway's last step`
- `6f9a2f6 Four panel-found defects in my own fixes, the explorer rebuilt on the founder's ruling, and W1 closed`
- `6ed7cf6 A test asserted a phrase was absent from the repo, then committing it made the phrase present`
- `b16edf4 The harvest recorded the dispatcher's own log output as seat-written work`
- `a05d7c7 The published explorer applies a stopping rule the appendix retired, and paid dispatch was the default`
- `9f8a10a I raised a false alarm on the Wolfram licence twice, and CLAUDE.md was why`
