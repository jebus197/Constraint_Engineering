# CDSFL Current State

Generated: 17 October 2026 14:28 BST (2026-10-17T14:28:08+01:00)

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
- **Last commit (the PARENT of the commit containing this file):** `559b1d0b` the written note for today's findings, in both required formats
- **Committed:** 2026-10-17 14:24:24 +0100
- **Remote (as of the snapshot, before the sv push):** up to date with origin/sim/shakedown-2026-09-29
- **Working tree at snapshot time:** clean

---

## Tests

**12225 tests collected** at 17 October 2026 14:28 BST, HEAD `559b1d0b` (`python3 -m pytest bench/tests/ --co -q`)

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

- `559b1d0b the written note for today's findings, in both required formats`
- `f8ecadfb B6: all 3 parts settled, and the suspected harm was not where it looked`
- `8eae8dfb the duration recorder was silently discarded by a later trap`
- `2a5950c6 sv could no longer save: its commit timeout was outgrown by its own hook`
- `98710718 B3: regenerate the parked file, and stop a teardown chmodding his machine`
- `73025e95 C32: the harness registry does not work like the ticket register, and should not`
- `63955c65 C31: the register beats a word search on the error that matters`
- `e3c94518 C30: the register was dropping his shortest rulings, and they are his most decisive`
- `7534743e C5: the serialisation cure is a hypothesis, and its measurement is now scheduled`
- `ed3c1d73 C3: the note standard is v1.8, and half of its new rule was already a rule`
