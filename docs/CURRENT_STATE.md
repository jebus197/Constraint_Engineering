# CDSFL Current State

Generated: 17 October 2026 07:47 BST (2026-10-17T07:47:50+01:00)

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
- **Last commit (the PARENT of the commit containing this file):** `88cb5cf1` sv: the ticket store plus 4 of his rulings, and the store's own checks found 3 defects in it
- **Committed:** 2026-10-17 07:41:50 +0100
- **Remote (as of the snapshot, before the sv push):** up to date with origin/sim/shakedown-2026-09-29
- **Working tree at snapshot time:** DIRTY — snapshot-time working tree listed below (NOT the sv commit's file list)

Uncommitted files at snapshot time — the working tree as it stood before the sv commit, NOT that commit's file list:
- `M resources/RECOVERY.md`

---

## Tests

**11858 tests collected** at 17 October 2026 07:47 BST, HEAD `88cb5cf1` + uncommitted working tree (`python3 -m pytest bench/tests/ --co -q`)

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

- `88cb5cf1 sv: the ticket store plus 4 of his rulings, and the store's own checks found 3 defects in it`
- `d21cc047 B10 built, and the ticket store had 3 defects of its own, the worst one mine`
- `a4e32982 B16 built: one fingerprint scope, declared once, honoured by both loaders`
- `eebbe7b8 all 12 session hooks are now one file, reachable from the repo and unlosable`
- `4bc7dc4c B19 built: the budget guard now tells a command from a prohibition`
- `d55890c5 B18 built: his 2026-10-11 ruling is 2 of 2, and a third condition it never stated`
- `d43c180c his proposed marker `pr` was already his panel-review command, so the fix marker is `pf``
- `3049ae97 the harvester, the subject narrowing, and the Stop gate that prods until done`
- `609407b8 the ticket store: settled is now a recorded field, and the subject tier is what works`
- `95299314 the 94 blockers block nothing that matters, and the figure itself is withdrawn`
