# CDSFL Current State

Generated: 11 October 2026 21:54 BST (2026-10-11T21:54:24+01:00)

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
- **Last commit (the PARENT of the commit containing this file):** `cd149682` sv: the reader was mangling his writing, 4 of his rulings land, and a precondition is not a question
- **Committed:** 2026-10-11 21:48:47 +0100
- **Remote (as of the snapshot, before the sv push):** up to date with origin/sim/shakedown-2026-09-29
- **Working tree at snapshot time:** DIRTY — snapshot-time working tree listed below (NOT the sv commit's file list)

Uncommitted files at snapshot time — the working tree as it stood before the sv commit, NOT that commit's file list:
- `M resources/MEMORY_EXCLUSIONS.md`
- `M resources/RECOVERY.md`

---

## Tests

**10692 tests collected** at 11 October 2026 21:54 BST, HEAD `cd149682` + uncommitted working tree (`python3 -m pytest bench/tests/ --co -q`)

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

- `cd149682 sv: the reader was mangling his writing, 4 of his rulings land, and a precondition is not a question`
- `15a0d6dd the single file now records what became of all 18 of his responses`
- `fd2eae8a his rulings 1 and 2 pinned where they would otherwise have been lost`
- `48c6bd53 his 18 responses worked: 256 characters of his writing were being dropped, and 4 rulings land`
- `3c4e0e37 the older 233 audited, and the file written to stop decisions going missing had lost 3`
- `2935d57b Pass B: his own words as the source, and 4 of 12 checkable rulings had not landed`
- `d4e48d3b his machine is a fixed resource, and 221 of his 691 verdicts were unreadable`
- `fbbd9163 the Lean anchor set is built, and a mutation pass caught me writing a guard that could not fail`
- `7bc4a390 sv: Lean checks the proof and not the statement, and that gap is the one CDSFL already closes`
- `f5093e36 sv: the prior art is largely invented, the research proving it needed correcting, and the gap is what sets the attempts budget`
