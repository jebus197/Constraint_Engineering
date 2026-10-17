# CDSFL Current State

Generated: 17 October 2026 02:23 BST (2026-10-17T02:23:36+01:00)

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
- **Last commit (the PARENT of the commit containing this file):** `13f4e6d8` the ownership distinction is now guarded, and 1 of 3 mutations exposed it as too weak
- **Committed:** 2026-10-17 02:20:29 +0100
- **Remote (as of the snapshot, before the sv push):** ahead of origin/sim/shakedown-2026-09-29 by 10
- **Working tree at snapshot time:** clean

---

## Tests

**11716 tests collected** at 17 October 2026 02:23 BST, HEAD `13f4e6d8` (`python3 -m pytest bench/tests/ --co -q`)

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

- `13f4e6d8 the ownership distinction is now guarded, and 1 of 3 mutations exposed it as too weak`
- `c6ee54b3 only 3 items await his ruling; 4 await an answer from me, and the distinction was wrong`
- `9054389b the audit found 20 confirmed gaps in his record, 12 of them rulings never carried out`
- `1df51094 his fold-fixes-back ruling was 0 of 2 built, and 10 of 15 open items hid his own rulings`
- `130d9358 WITHDRAWN: my repeatability figure measured a status phrase, and my own P-pass broke it`
- `f7a3c930 the final discussion before authorisation, with 2 findings made since the last report`
- `21f3cbb5 the fingerprint reset is partial, and the 3 legs repeat by containment not replication`
- `a01090d0 2 unread reports, and reading only the newer one would have cost him a decision`
- `84eeed28 his question was right: the TTS explained 18 findings and recommended on 10`
- `180471d9 the attack broke 3 of my claims, I broke 2 of its findings, and my own published denominator was wrong`
