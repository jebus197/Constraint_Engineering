# CDSFL Current State

Generated: 31 August 2026 00:42 BST (2026-08-31T00:42:11+01:00)

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
- **Last commit (the PARENT of the commit containing this file):** `e766935` Pre-push privacy scan: remove 2 new personal-detail additions
- **Committed:** 2026-08-31 00:41:26 +0100
- **Remote (as of the snapshot, before the sv push):** up to date with origin/main
- **Working tree at snapshot time:** clean

---

## Tests

**4599 tests collected** at 31 August 2026 00:42 BST, HEAD `e766935` (`python3 -m pytest bench/tests/ --co -q`)

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

- `e766935 Pre-push privacy scan: remove 2 new personal-detail additions`
- `11ad4a9 Three more rulings applied: truncation fixed, Gemini tooled and PAID-tested, 133 pairs folded in`
- `1631202 Backlog TTS pair: two older decisions, currency verified first`
- `8b73653 Rulings 3, 4 and 5: tools enforced without exception, bar one recorded gap`
- `5be7584 Founder rulings 1 and 2 applied: option B, and option A`
- `a6559fe One consolidated decisions document, replacing three`
- `6f111d6 Actually apply the error-tail fix (the previous commit's edit never ran)`
- `2a6187d Disarm the sim ask pending a ruling; stop truncating panel errors at the red herring`
- `75cb00d Report pair, retitled: not a green light yet`
- `7380736 CC2's third pass said NOT a green light, and it was right on 9 of 10 counts`
