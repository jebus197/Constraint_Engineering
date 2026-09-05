# CDSFL Current State

Generated: 5 September 2026 13:10 BST (2026-09-05T13:10:58+01:00)

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
- **Last commit (the PARENT of the commit containing this file):** `3377e67` I reported 9 open decisions; the record holds 122, and a phantom one has stood 110 days
- **Committed:** 2026-09-05 13:10:45 +0100
- **Remote (as of the snapshot, before the sv push):** ahead of origin/main by 2
- **Working tree at snapshot time:** clean

---

## Tests

**5162 tests collected** at 5 September 2026 13:10 BST, HEAD `3377e67` (`python3 -m pytest bench/tests/ --co -q`)

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

- `3377e67 I reported 9 open decisions; the record holds 122, and a phantom one has stood 110 days`
- `94f5035 Revised morning report: decisions first, and the 55-item list carries a staleness caveat`
- `55d02eb sv: the panel was never tool-enabled, and 3 of 4 red guards were wrong`
- `b6a2032 The stop was right: I built a 488-agent runaway, and nothing was lost`
- `99cc5bb Morning report Part 4: suite green at 5153, and 3 of 4 red guards were wrong`
- `6026732 3 of the 4 guards that went red were wrong, and acting on 1 would have voided Exp 56`
- `2e7ffb1 The matcher says the repo is never written to; it is, and the hole is the runner's`
- `cfed25d Morning report Part 2: the ruling list worked, and 7 of my own claims refuted`
- `341885d D13: the human queue is 4 of 33, and all 4 were confirmed by model vote`
- `11255d9 "Repair is provably inert" was wrong: it flips 3.2% of decisions, all to REJECT`
