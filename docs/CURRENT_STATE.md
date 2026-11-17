# CDSFL Current State

Generated: 17 November 2026 07:03 GMT (2026-11-17T07:03:40+00:00)

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
- **Last commit (the PARENT of the commit containing this file):** `725ec976` A board fix that was half a fix, and the 1-line completion that would have turned the gate into a rubber stamp
- **Committed:** 2026-11-17 06:01:58 +0000
- **Remote (as of the snapshot, before the sv push):** ahead of origin/sim/shakedown-2026-09-29 by 1
- **Working tree at snapshot time:** DIRTY — snapshot-time working tree listed below (NOT the sv commit's file list)

Uncommitted files at snapshot time — the working tree as it stood before the sv commit, NOT that commit's file list:
- `M bench/tests/test_desktop_mirrors_stay_current_2026-09-10.py`
- `M bench/tests/test_the_nineteen_producers_run_2026-11-17.py`
- `M bench/tickets/sv_completions.jsonl`
- `M bench/tickets/tickets.jsonl`
- `M experimental_notes/CDSFL_MASTER_TASK_LIST.md`
- `M experimental_notes/data/morning_report_decisions.json`
- `M experimental_notes/data/output_hashes.json`
- `?? experimental_notes/A_Fix_That_Would_Have_Disabled_The_Gate_2026-11-17.md`
- `?? scripts/the_mirror_ordering_mutations_2026-11-17.py`
- `?? scripts/what_a_cheap_preflight_is_worth_2026-11-17.py`

---

## Tests

**17925 tests collected** at 17 November 2026 07:03 GMT, HEAD `725ec976` + uncommitted working tree (`python3 -m pytest bench/tests/ --co -q`)

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

- `725ec976 A board fix that was half a fix, and the 1-line completion that would have turned the gate into a rubber stamp`
- `bb315555 The full suite ran against a committed tree, and 8 of its 10 new failures were invisible to the board that passed it`
- `6304f771 The 3 panel rounds he ordered, run blind and joint, and every round refuted something in my own brief`
- `4a802768 One batch, as he instructed: his 16 verdicts worked through, the encoding layer built, and a sentence every seat is given that was false`
- `84fd2253 B169: the permission predicate under-reported a residue, and composing was measured rather than asserted`
- `665a4b41 B165: the clean-tree full-suite measurement, and what it caught doing`
- `846c4ffe fix: 21 anchored corrections, 4 entries raised, 7 guards repaired`
- `e37fed9d sv: the Stop hook was overactive on his report, 4 faults fixed, 7 of 7 mutations red, and re-armed only after a green board -- plus 5 errors of my own caught before any of them shipped`
- `b18b397f sv: the steering fix built on his lift, 11 of 11 source-text assertions resolved, my own orphan figure corrected from 33 to 6, and 6 new defects found by trying to carry out his instructions`
- `3cb05d66 sv: the hook fix is installed on his word, a --help could have edited the tree, and the figure telling him he owes 8 rulings rests on a proxy no sibling predicate agrees with`
