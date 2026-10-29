# CDSFL Current State

Generated: 29 October 2026 09:43 GMT (2026-10-29T09:43:01+00:00)

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
- **Last commit (the PARENT of the commit containing this file):** `96aec301` sv: state save 29 October 2026 06:27 GMT
- **Committed:** 2026-10-29 06:27:38 +0000
- **Remote (as of the snapshot, before the sv push):** up to date with origin/sim/shakedown-2026-09-29
- **Working tree at snapshot time:** DIRTY — snapshot-time working tree listed below (NOT the sv commit's file list)

Uncommitted files at snapshot time — the working tree as it stood before the sv commit, NOT that commit's file list:
- `M  bench/tests/test_precommit_gate_cost_2026-09-10.py`
- `M  bench/tests/test_sv_rulings.py`
- `M  bench/tests/test_task_list_markers_2026-09-09.py`
- `M  bench/tests/test_the_chat_source_is_retired_not_deleted_2026-10-29.py`
- `A  bench/tests/test_the_durations_mode_sums_the_phases_2026-10-29.py`
- `M  bench/tests/test_the_evidence_must_go_red_2026-10-17.py`
- `M  bench/tests/test_the_morning_report_is_generated_2026-10-12.py`
- `A  bench/tests/test_the_reported_runway_respects_both_budgets_2026-10-29.py`
- `M  bench/tickets/tickets.jsonl`
- `M  bench/tickets/tickets_searches.jsonl`
- `M  docs/CURRENT_STATE.md`
- `MM experimental_notes/CDSFL_MASTER_TASK_LIST.md`
- `MM experimental_notes/Overnight_Progress_2026-10-29.md`
- `M  experimental_notes/Perplexity_Revised_Assessment_2026-04-10.md`
- `M  experimental_notes/data/morning_report_decisions.json`
- … and 13 more, not shown (list capped at 15 of 28 — run `git status --porcelain` for the full set)

---

## Tests

**13355 tests collected** at 29 October 2026 09:43 GMT, HEAD `96aec301` + uncommitted working tree (`python3 -m pytest bench/tests/ --co -q`)

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

- `96aec301 sv: state save 29 October 2026 06:27 GMT`
- `2ee91196 sv: 12 entries closed, the programme of study closed, and 3 claims of mine withdrawn`
- `4ad786ff C1 deferred with its reason, its real question registered, and the chat-half question closed`
- `60ac54dd sv: T1 to T3 done; the panel refused tonight's severity promotion, the joint round found any-of-empty-is-False, and one seat is the critical path in 5 of 5 rounds`
- `14e1a5c5 T3 closed and marked DONE; 2 questions left for his ruling rather than decided`
- `5be94c2f T3 converged, and the barrier his ruling asked for is measured: one seat is the critical path in 5 of 5 rounds`
- `479fbfb9 B24 closed with its verification, and marked DONE`
- `c5f681b0 B24 built: Rule 27 enforced in full going forward, on his ruling of 2026-10-19`
- `31ba2157 The previous commit message was eaten by the shell: the corrected text, and the lesson generalised`
- `c6930ab5 T4: the chat source is RETIRED on his ruling, with the condition tested rather than assumed`
