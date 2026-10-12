# CDSFL Current State

Generated: 12 October 2026 19:34 BST (2026-10-12T19:34:57+01:00)

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
- **Last commit (the PARENT of the commit containing this file):** `e05bf903` his 9 annotations read in full, 2 rulings recorded, 2 explanations discounted, panel running
- **Committed:** 2026-10-12 19:25:01 +0100
- **Remote (as of the snapshot, before the sv push):** ahead of origin/sim/shakedown-2026-09-29 by 1
- **Working tree at snapshot time:** DIRTY — snapshot-time working tree listed below (NOT the sv commit's file list)

Uncommitted files at snapshot time — the working tree as it stood before the sv commit, NOT that commit's file list:
- `A  bench/logs/clear_the_outstanding_2026-10-12/sandbox_harvest/cc2/attempt-1/files/experimental_notes/data/morning_report_decisions.json`
- `A  bench/logs/clear_the_outstanding_2026-10-12/sandbox_harvest/fable/attempt-1/files/experimental_notes/data/morning_report_decisions.json`
- `M  docs/CURRENT_STATE.md`
- `A  experimental_notes/seat_evidence/clear_the_outstanding_2026-10-12/cc2/PROVENANCE.json`
- `A  experimental_notes/seat_evidence/clear_the_outstanding_2026-10-12/cc2/bench/tests/test_a_second_interpreter_is_not_an_integrity_violation_2026-10-12.py`
- `A  experimental_notes/seat_evidence/clear_the_outstanding_2026-10-12/cc2/bench/tests/test_an_unserved_finding_cannot_block_for_ever_2026-10-12.py`
- `A  experimental_notes/seat_evidence/clear_the_outstanding_2026-10-12/fable/PROVENANCE.json`
- `A  experimental_notes/seat_evidence/clear_the_outstanding_2026-10-12/fable/bench/tests/test_never_served_findings_enter_the_ladder_2026-10-12.py`
- `A  experimental_notes/seat_evidence/clear_the_outstanding_2026-10-12/fable/bench/tests/test_spawned_interpreter_falsifiers_are_not_refused_2026-10-12.py`
- `M  resources/MEMORY_EXCLUSIONS.md`
- `M  resources/ONBOARDING.md`
- `M  resources/RECOVERY.md`

---

## Tests

**10970 tests collected** at 12 October 2026 19:34 BST, HEAD `e05bf903` + uncommitted working tree (`python3 -m pytest bench/tests/ --co -q`)

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

- `e05bf903 his 9 annotations read in full, 2 rulings recorded, 2 explanations discounted, panel running`
- `2f9aa6eb sv: his 3 rulings built, board 20 red to 2, outputs hashed`
- `47c5529e the 2 remaining board reds are now ENTRIES rather than a conversation, and the report is rebuilt`
- `fa787d59 his 3 rulings built: the 11 cases used as intended, the seats staggered, outputs hashed`
- `979fce32 the measurement's own instrument is now guarded, and the hyphen defect cannot return`
- `e54cf07e the test-value measurement he commissioned, with its own first figure withdrawn`
- `687a5594 the generated report was not reproducible, and the P-pass caught it before he read it`
- `7f88a467 the morning report's decision list is now DERIVED, and it found 3 decisions I had missed`
- `54c4bbf0 morning report extended: it ended at 00:05 and the overnight work was not in it`
- `0a0d1657 the night's error shape, recorded as a hypothesis rather than a finding`
