# CDSFL Current State

Generated: 20 September 2026 01:34 BST (2026-09-20T01:34:19+01:00)

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
- **Last commit (the PARENT of the commit containing this file):** `e5db47d` morning report: a response sheet, so every open item can be answered in 1 file
- **Committed:** 2026-09-19 22:07:40 +0100
- **Remote (as of the snapshot, before the sv push):** ahead of origin/main by 41
- **Working tree at snapshot time:** DIRTY — snapshot-time working tree listed below (NOT the sv commit's file list)

Uncommitted files at snapshot time — the working tree as it stood before the sv commit, NOT that commit's file list:
- `M experimental_notes/Morning_Report_2026-09-18.md`
- `M resources/MEMORY_EXCLUSIONS.md`
- `M resources/ONBOARDING.md`
- `M resources/RECOVERY.md`

---

## Tests

**8041 tests collected** at 20 September 2026 01:34 BST, HEAD `e5db47d` + uncommitted working tree (`python3 -m pytest bench/tests/ --co -q`)

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

- `e5db47d morning report: a response sheet, so every open item can be answered in 1 file`
- `2f69baf Z1 DONE: the Zenodo token is actually rotated, and doing it found 2 defects`
- `38d430c Z1: a rotation tool, so the token moves without hand-editing 10 credentials`
- `674b066 remove the framing I built around the founder's position; keep the plain record`
- `2ad108f morning report: the no-author advice was mine, not his, and the directives' provenance is untraceable`
- `b5c0460 morning report: the completed processes folded in, including a figure I could NOT verify`
- `6a287cb morning report: correct the seat claim -- there are 2 rosters, and 1 of them IS guarded`
- `8a0952a appendix: the coverage-to-risk inverse at line 169 was the NEGATIVE of the inverse`
- `1b2e3d6 morning report: the revised model checks out on first inspection, and it found a real error in our appendix`
- `e99644a codex seat: the producer now measures tool support, and 3 corrections it took an adversarial pass to find`
