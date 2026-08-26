# CDSFL Current State

Generated: 26 August 2026 01:28 BST (2026-08-26T01:28:16+01:00)

---

## Git

- **Branch:** build-experiment-2026-08-22
- **Last commit:** `4354eab` Overnight window closes: six decisions consolidated, tracker resume pointer advanced.
- **Committed:** 2026-08-26 01:26:06 +0100
- **Remote:** ahead of origin/main by 65 [no upstream configured]
- **Working tree:** DIRTY — uncommitted changes present

Uncommitted files:
- `M bench/tests/_private_memory.py`
- `M bench/tests/test_sv_memory_unreadable_2026-08-26.py`
- `M docs/CURRENT_STATE.md`
- `M experimental_notes/CDSFL_Agent_Operational_Plan.md`
- `M experimental_notes/Decisions_Awaiting_The_Founder_2026-08-26.md`
- `M resources/ONBOARDING.md`
- `M resources/RECOVERY.md`
- `M scripts/cdsfl_sv.py`

---

## Tests

**3966 tests collected** at 26 August 2026 01:28 BST, HEAD `4354eab` + uncommitted working tree (`python3 -m pytest bench/tests/ --co -q`)

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

- `4354eab Overnight window closes: six decisions consolidated, tracker resume pointer advanced.`
- `8f9fe35 sv crashed mid-session because existence is not readability -- and I had just told the founder sv works.`
- `012b8c8 Scaling spec: at the measured correlation, fifty architectures do the work of about four.`
- `14b2df3 Measuring first refuted the renumbering premise: the order is already correct, and two other things are not.`
- `1cbc337 sv printed "State save complete." BEFORE committing and pushing. Same defect, one level up.`
- `0bec80b Note: exp55's answers were public three days before it ran, and the sync repair.`
- `53edabe sv now MEASURES the remote after pushing, and says public main is 58 commits behind.`
- `20d2ccf Keys move out of the repository -- and the door they were guarding has been open since 20 August.`
- `914a11d "Not mechanically detectable" was wrong: withdraw the claim and build the checker that refutes it.`
- `3ec8003 sv tooling: the Desktop mirror cannot be maintained from this process, and the save now says so instead of crashing.`
