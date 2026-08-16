# CDSFL Current State

Generated: 16 August 2026 23:55 BST (2026-08-16T23:55:38+01:00)

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
- **Last commit (the PARENT of the commit containing this file):** `3a633e1` TTS compliance: remove a second-person phrasing and name a bare referent in the Gemini assessment.
- **Committed:** 2026-08-16 14:19:40 +0100
- **Remote (as of the snapshot, before the sv push):** up to date with origin/main
- **Working tree at snapshot time:** DIRTY — snapshot-time working tree listed below (NOT the sv commit's file list)

Uncommitted files at snapshot time — the working tree as it stood before the sv commit, NOT that commit's file list:
- `M bench/convergence_location.py`
- `M bench/tests/test_combined_identity_rule.py`
- `M bench/tests/test_operational_scripts.py`
- `M experimental_notes/CDSFL_Agent_Operational_Plan.md`
- `M resources/MEMORY_EXCLUSIONS.md`
- `M resources/RECOVERY.md`
- `?? bench/tests/test_anchorless_outcome_guard.py`
- `?? bench/tests/test_operating_characteristic.py`
- `?? experimental_notes/Similarity_Function_Operating_Characteristic_2026-08-16.md`
- `?? experimental_notes/Similarity_Function_Operating_Characteristic_Plain_English_2026-08-16.md`
- `?? experimental_notes/data/`
- `?? scripts/similarity_operating_characteristic.py`

---

## Tests

**3533 tests collected** at 16 August 2026 23:55 BST, HEAD `3a633e1` + uncommitted working tree (`python3 -m pytest bench/tests/ --co -q`)

This is a COLLECTION count, not a pass count, and it says nothing about whether the run was offline. Quote it only with the timestamp and commit above. The total is not stable: `bench/tests/test_immune_memory_consumption.py` parametrises over the timestamped run directories under `bench/logs/`, so it grows whenever an experiment archives, and new test files land between saves.

For a pass count, run the suite offline and record the result with its own date and command: `python3 -m pytest bench/tests/ -q --netguard-strict`. The suite is offline by default via `bench/tests/conftest.py`; see docs/REPRODUCING.md. Figures labelled "non-network" before 2026-07-31 were hand-curated exclusions and included live model dispatch — do not quote them as offline results.

---

## Latest Experiment

- **Experiment:** exp49_engineering_exam_live (#49)
- **Status:** CONVERGED
- **Topology:** star
- **Target:** `/Users/georgejackson/CDSFL_review_targets/exp49_engineering.md`
- **Rounds:** 7
- **Total findings:** 40
- **Gamma:** 0.7738
- **Models:** CC2, ChatGPT, Codex, DeepSeek, Gemini
- **Per model:**
  - Gemini: 13
  - Codex: 8
  - ChatGPT: 7
  - CC2: 6
  - DeepSeek: 6
- **Logs:** `/Users/georgejackson/Developer_Projects/Constraint_Engineering/bench/logs/exp49_engineering_exam_live_20260729T062320Z`

---

## Recent Commits

- `3a633e1 TTS compliance: remove a second-person phrasing and name a bare referent in the Gemini assessment.`
- `f32056f Test Gemini's two duplicate-detection answers against the project. Nothing to adopt.`
- `5176738 Benchmark the similarity function against published work, and correct the Bletchley framing.`
- `34fbe87 Name the rule: "the similarity function", founder-named 2026-08-16.`
- `7c28378 Zenodo archive uploaded as a draft, deposition 21959922. Publication left to the founder.`
- `772e87c README: a five-line signpost at the top, on founder approval.`
- `a44547e CORRECTION to bdadcfe: the answer keys were never at risk, and I briefly unsealed them.`
- `bdadcfe Test the branch-drift guard, and record why the answer keys were nearly destroyed.`
- `723287e sv: guard against branch drift — main is the only branch that gets updated.`
- `2460a25 Repository navigability: a front door, an archive plan, and a stop on log growth.`
