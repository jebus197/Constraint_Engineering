# CDSFL Current State

Generated: 26 August 2026 01:21 BST (2026-08-26T01:21:33+01:00)

---

## Git

- **Branch:** build-experiment-2026-08-22
- **Last commit:** `80faf11` sv crashed mid-session because existence is not readability -- and I had just told the founder sv works.
- **Committed:** 2026-08-26 01:17:33 +0100
- **Remote:** ahead of origin/main by 64 [no upstream configured]
- **Working tree:** DIRTY — uncommitted changes present

Uncommitted files:
- `M docs/CURRENT_STATE.md`
- `M resources/ONBOARDING.md`
- `M resources/RECOVERY.md`
- `?? tmp49uop3i9.py`

---

## Tests

**3966 tests collected** at 26 August 2026 01:21 BST, HEAD `80faf11` + uncommitted working tree (`python3 -m pytest bench/tests/ --co -q`)

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

- `80faf11 sv crashed mid-session because existence is not readability -- and I had just told the founder sv works.`
- `370d9f2 Scaling spec: at the measured correlation, fifty architectures do the work of about four.`
- `e8123ff Measuring first refuted the renumbering premise: the order is already correct, and two other things are not.`
- `730dac4 sv printed "State save complete." BEFORE committing and pushing. Same defect, one level up.`
- `5d038fc Note: exp55's answers were public three days before it ran, and the sync repair.`
- `1cb88fc sv now MEASURES the remote after pushing, and says public main is 58 commits behind.`
- `0cfcb8b Keys move out of the repository -- and the door they were guarding has been open since 20 August.`
- `a26e758 "Not mechanically detectable" was wrong: withdraw the claim and build the checker that refutes it.`
- `d35703e sv tooling: the Desktop mirror cannot be maintained from this process, and the save now says so instead of crashing.`
- `0fe5b19 Merge origin/main: pick up the three commits published directly tonight.`
