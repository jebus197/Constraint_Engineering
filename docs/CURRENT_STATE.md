# CDSFL Current State

Generated: 16 October 2026 17:28 BST (2026-10-16T17:28:18+01:00)

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
- **Last commit (the PARENT of the commit containing this file):** `46bb8cd9` a harvested seat file is verbatim seat output, and I walked into the trap its own test documents
- **Committed:** 2026-10-16 17:28:02 +0100
- **Remote (as of the snapshot, before the sv push):** ahead of origin/sim/shakedown-2026-09-29 by 20
- **Working tree at snapshot time:** clean

---

## Tests

**11653 tests collected** at 16 October 2026 17:28 BST, HEAD `46bb8cd9` (`python3 -m pytest bench/tests/ --co -q`)

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

- `46bb8cd9 a harvested seat file is verbatim seat output, and I walked into the trap its own test documents`
- `cd14a2d7 the panel closed 2 of 2, and the set-form ratchet immediately named what my count form could not`
- `4aac3124 a gate whose exit code is discarded is not a gate`
- `61c33af7 my admission figure was understated, and the producer had the defect it reports`
- `bedf9717 the panel's first seat found a regression I shipped, and 2 of my 3 repairs were worse than inert`
- `e0832bee I repeated the citation omission 40 minutes after recording it, so it is now a script`
- `18eeb705 94 of 212 blockers could never be worked, and now a run says so`
- `d5428c01 end-of-day report: 6 built, 5 needing a ruling, and 3 of my own claims corrected`
- `8197faf3 the capacity number measured, his admission question answered, and a hypothesis that died on the way`
- `47c51b1b a ratchet that could not say what tripped it now names the path, and the swap it used to miss`
