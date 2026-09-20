# CDSFL Current State

Generated: 20 September 2026 23:12 BST (2026-09-20T23:12:26+01:00)

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

- **Branch:** main
- **Last commit (the PARENT of the commit containing this file):** `e8f5641` sv: 6-round paid panel — the degeneracy was ours (appendix 7.12), 191-claim withdrawn, containment repaired, optimal round count derived
- **Committed:** 2026-09-20 22:48:54 +0100
- **Remote (as of the snapshot, before the sv push):** up to date with origin/main
- **Working tree at snapshot time:** DIRTY — snapshot-time working tree listed below (NOT the sv commit's file list)

Uncommitted files at snapshot time — the working tree as it stood before the sv commit, NOT that commit's file list:
- `M resources/RECOVERY.md`
- `?? experimental_notes/Maths_Revision_Review_Synthesis_2026-09-20.md`
- `?? experimental_notes/Maths_Revision_Review_Synthesis_Plain_English_2026-09-20.md`
- `?? scripts/maths_review_synthesis_figures_2026-09-20.py`

---

## Tests

**8243 tests collected** at 20 September 2026 23:12 BST, HEAD `e8f5641` + uncommitted working tree (`python3 -m pytest bench/tests/ --co -q`)

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

- `e8f5641 sv: 6-round paid panel — the degeneracy was ours (appendix 7.12), 191-claim withdrawn, containment repaired, optimal round count derived`
- `f253fa7 Round 3 brief: the definitive way forward, under a new hard constraint`
- `0c4f3e5 A review seat could write to the repository it was reviewing, and I opened that hole this morning`
- `31537d0 Round 2 setup: Kimi timed out at 904.5 s and the direct routes ignored the iteration budget`
- `afa218f The panel's paid seats could not read the thing they were reviewing`
- `7c9609a No model gets a free pass on tool use: DeepSeek's had never actually run`
- `abc0e5e A mirrored machine dump became 91% of the citation census, and I put it there`
- `1f0c383 task list: the Desktop mirror refresh the pre-commit hook applied after staging`
- `87b55d9 The full suite found 12 failures my 448-test pre-commit hook could not, and an audit found 15 more`
- `02302cf A8 closes: both seats found a defect the committed suite could not see, and they were different defects`
