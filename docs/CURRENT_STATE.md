# CDSFL Current State

Generated: 30 October 2026 23:37 GMT (2026-10-30T23:37:45+00:00)

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
- **Last commit (the PARENT of the commit containing this file):** `ca7c0f5c` Recovery block for the rewrite, and the gate-reach figure was stale by my own hand
- **Committed:** 2026-10-30 19:42:51 +0000
- **Remote (as of the snapshot, before the sv push):** up to date with origin/sim/shakedown-2026-09-29
- **Working tree at snapshot time:** DIRTY — snapshot-time working tree listed below (NOT the sv commit's file list)

Uncommitted files at snapshot time — the working tree as it stood before the sv commit, NOT that commit's file list:
- `M  bench/tests/test_a_reset_memory_is_not_a_regression_2026-10-17.py`
- `M  bench/tests/test_a_ruled_item_is_not_a_decision_2026-10-16.py`
- `M  bench/tests/test_immune_memory_evaluation.py`
- `M  bench/tests/test_the_chat_half_raises_only_real_markers_2026-10-28.py`
- `A  bench/tests/test_the_ds_kind_is_confined_to_his_annotations_2026-10-30.py`
- `M  bench/tests/test_ticket_store_2026-10-17.py`
- `M  bench/ticket_store.py`
- `M  bench/tickets/tickets.jsonl`
- `M  bench/tickets/tickets_searches.jsonl`
- `M  docs/CURRENT_STATE.md`
- `MM experimental_notes/CDSFL_MASTER_TASK_LIST.md`
- `A  experimental_notes/Your_Rulings_Built_2026-10-30.md`
- `A  experimental_notes/Your_Rulings_Built_2026-10-30.txt`
- `M  experimental_notes/data/annotation_verdicts_2026-10-17.json`
- `M  experimental_notes/evidence/panel_records_2026-10-30/the_role_layer_b21_2026-10-30/BRIEF.md.txt`
- … and 12 more, not shown (list capped at 15 of 27 — run `git status --porcelain` for the full set)

---

## Tests

**13818 tests collected** at 30 October 2026 23:37 GMT, HEAD `ca7c0f5c` + uncommitted working tree (`python3 -m pytest bench/tests/ --co -q`)

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

- `ca7c0f5c Recovery block for the rewrite, and the gate-reach figure was stale by my own hand`
- `c2db457a The verdicts file named 6 items by identifier and explained none of them`
- `37b14e5a sv: his question was never mis-marked, the pf default did it, and his inline markers were invisible to the reader`
- `671b9133 His inline markers were invisible to the reader, including 2 rulings I acted on`
- `686e08a8 sv: the board held the prediction, the triage could not see 72 of 186 entries, and 5 of 6 tickets checked were already done`
- `9f8003dd 2 more tickets discharged, and 1 of his questions was filed as a proposed fix`
- `2f98fcfa 3 gate tickets were stale recording, not undone work, and are closed`
- `8643fbd3 The paid-dispatch gate missed the plainest phrasing of a paid dispatch`
- `04a89609 6 figures about the panel backlog had no producer, and the split is withheld`
- `044b2c75 Correct the consolidated file: it called a validator-refused brief ready`
