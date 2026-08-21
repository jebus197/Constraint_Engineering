# CDSFL Current State

Generated: 22 August 2026 00:18 BST (2026-08-22T00:18:16+01:00)

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
- **Last commit (the PARENT of the commit containing this file):** `4f786a4` Design reviews: the Bugzilla question answered at last, and perturbation assessed.
- **Committed:** 2026-08-21 21:27:14 +0100
- **Remote (as of the snapshot, before the sv push):** up to date with origin/main
- **Working tree at snapshot time:** DIRTY — snapshot-time working tree listed below (NOT the sv commit's file list)

Uncommitted files at snapshot time — the working tree as it stood before the sv commit, NOT that commit's file list:
- `M resources/RECOVERY.md`

---

## Tests

**3607 tests collected** at 22 August 2026 00:18 BST, HEAD `4f786a4` + uncommitted working tree (`python3 -m pytest bench/tests/ --co -q`)

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

- `4f786a4 Design reviews: the Bugzilla question answered at last, and perturbation assessed.`
- `247ee33 Runway: correct three stale rows and finally record the future-work items (item 9).`
- `b1a9ed4 Bugzilla verbatim compendium: every source from the last 3 days, unedited.`
- `5b3043f Fix list from the independent review. Nine defects, six of them CC1's own from this week.`
- `2a422b5 Independent read-only review, verbatim record: Fable 5 and CC2.`
- `ce6337a Items 10 and 13: the fix-complexity measurer (shadow only) and the pre-registration draft.`
- `bd9c569 Items 8, 9, 11, 14: the gate's own count input, exp47's lost rounds, the prose control, and rho's floor in shadow.`
- `3c96d29 Item 7: no voting. Remove every model-vote path to MERGED.`
- `3660816 Items 1-6: repair the R_k reader, the feedback wording and priority, and clamp the similarity map.`
- `210d21d Rescue the one file that existed in no ref: the Exp 39 -> 40-52 renumbering record.`
