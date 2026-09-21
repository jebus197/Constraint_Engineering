# CDSFL Current State

Generated: 21 September 2026 21:30 BST (2026-09-21T21:30:36+01:00)

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
- **Last commit (the PARENT of the commit containing this file):** `7f7a443` Commission the 5 safe flags, record the 3 harmful ones as study items with reasons
- **Committed:** 2026-09-21 20:40:23 +0100
- **Remote (as of the snapshot, before the sv push):** up to date with origin/main
- **Working tree at snapshot time:** DIRTY — snapshot-time working tree listed below (NOT the sv commit's file list)

Uncommitted files at snapshot time — the working tree as it stood before the sv commit, NOT that commit's file list:
- `M resources/RECOVERY.md`

---

## Tests

**8287 tests collected** at 21 September 2026 21:30 BST, HEAD `7f7a443` + uncommitted working tree (`python3 -m pytest bench/tests/ --co -q`)

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

- `7f7a443 Commission the 5 safe flags, record the 3 harmful ones as study items with reasons`
- `e61a83c Astra landed 3 correct hits; 1 of my claims is withdrawn and 1 of my figures had no producer`
- `0a4a491 Mark the 7.12 confound the founder ruled on, and correct my own first draft of it`
- `b509a44 I attacked the maths model's Phase 2 and lost; 3 corrections landed, 0 equations changed`
- `f802512 The fix score was measuring absence of harm; the appendix defines it as presence of repair`
- `775c81c Runway: the founder's ordered sequence, NOW-1 to NOW-7, written down rather than held in context`
- `f7d04b4 sv: 6-round review synthesised — the degeneracy was ours, 3 CC1 claims withdrawn, the scorer is the live finding`
- `e8f5641 sv: 6-round paid panel — the degeneracy was ours (appendix 7.12), 191-claim withdrawn, containment repaired, optimal round count derived`
- `f253fa7 Round 3 brief: the definitive way forward, under a new hard constraint`
- `0c4f3e5 A review seat could write to the repository it was reviewing, and I opened that hole this morning`
