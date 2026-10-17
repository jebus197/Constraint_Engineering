# CDSFL Current State

Generated: 17 October 2026 11:38 BST (2026-10-17T11:38:19+01:00)

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
- **Last commit (the PARENT of the commit containing this file):** `545f9405` Closing report on the overnight task list, paired TTS and markdown
- **Committed:** 2026-10-17 11:32:36 +0100
- **Remote (as of the snapshot, before the sv push):** up to date with origin/sim/shakedown-2026-09-29
- **Working tree at snapshot time:** clean

---

## Tests

**12111 tests collected** at 17 October 2026 11:38 BST, HEAD `545f9405` (`python3 -m pytest bench/tests/ --co -q`)

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

- `545f9405 Closing report on the overnight task list, paired TTS and markdown`
- `bc90f3d6 C15 follow-up: the omit-at-default rule is executed, not restated`
- `24beda17 C15: the season is built and wired; the ladder order is measured, not a vendor tuple`
- `a72c2fb4 C17: the immune memory is reset, the priors are archived, and a promised script existed only in a comment`
- `1d443708 C14: the better way is recovered, verified and built -- incremental stream-json`
- `f50d6ead C13: the required quiet run is 7, and C29 reports that the list may not terminate`
- `65d8a110 Ledger citation repair: runner line numbers moved with the C8 constant`
- `12eca9d4 C8: the hardened gate is on by default, 12 days after he ruled it`
- `45215ee0 C20 CLOSED: all 5 of his corrections discharged, and 2 were faults in the list itself`
- `9b38f66e C28: the commit gate cried wolf twice, and the repair it declined was safe`
