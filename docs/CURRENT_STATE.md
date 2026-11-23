# CDSFL Current State

Generated: 23 November 2026 18:47 GMT (2026-11-23T18:47:56+00:00)

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
- **Last commit:** `40b00160` batch 11: the joint panel round, and 2 of this project's own recorded claims refuted by it
- **Committed:** 2026-11-23 15:35:06 +0000
- **Remote:** ahead of origin/sim/shakedown-2026-09-29 by 6
- **Working tree:** DIRTY — uncommitted changes present

Uncommitted files:
- `M  .claude/CLAUDE.md`
- `M  bench/tests/test_help_never_acts_2026-09-11.py`
- `M  bench/tests/test_the_risked_guards_come_from_the_diff_2026-11-22.py`
- `M  bench/tests/test_todays_producers_run_2026-11-22.py`
- `M  bench/tickets/tickets.jsonl`
- `M  experimental_notes/CDSFL_MASTER_TASK_LIST.md`
- `A  experimental_notes/Panel_B12_FULL_RECORD_2026-11-23.md`
- `M  experimental_notes/data/morning_report_decisions.json`
- `M  experimental_notes/data/output_hashes.json`
- `A  experimental_notes/evidence/panel_records_2026-11-23/panel_b12_20261123T170728Z/BRIEF.md.txt`
- `A  experimental_notes/evidence/panel_records_2026-11-23/panel_b12_20261123T170728Z/cc2.json`
- `A  experimental_notes/evidence/panel_records_2026-11-23/panel_b12_20261123T170728Z/cc2.tools.attempt1.json.txt`
- `A  experimental_notes/evidence/panel_records_2026-11-23/panel_b12_20261123T170728Z/completion_barrier.json`
- `A  experimental_notes/evidence/panel_records_2026-11-23/panel_b12_20261123T170728Z/dispatch.log`
- `A  experimental_notes/evidence/panel_records_2026-11-23/panel_b12_20261123T170728Z/fable.json`
- … and 21 more, not shown (list capped at 15 of 36 — run `git status --porcelain` for the full set)

---

## Tests

**18542 tests collected** at 2026-11-23T20:26:26+00:00 GMT, HEAD `fa687fda` + uncommitted batch-13 working tree (`python3 -m pytest bench/tests/ --co -q`)

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

- `40b00160 batch 11: the joint panel round, and 2 of this project's own recorded claims refuted by it`
- `7e1cbb0b batch 9: B211 closed across all 3 surfaces`
- `58aeab06 batch 8: B211's checker had a false positive on first use, now fixed`
- `a45ebbee batch 7: B208 closed -- its falsifier was RUN and it found a live defect`
- `99852130 batch 6: B211 built -- the pre-board evidence now knows if the tree moved`
- `2141c1a8 batch 5: B207 and B210 closed across all 3 surfaces, B211's status corrected`
- `41352fac sv: batches 1-4 landed, the panel chose B209's key, 5 instrument defects recorded`
- `d99c6360 batch 4: B207 fed its reader, B209's guard corrected, B211 raised`
- `7dd07521 batch 3: B209 recorded, B210 found by a refused board, the census validated`
- `ca0320ba Batch 2: the panel's second round found 2 defects neither seat saw, and the pre-board check found 1 the new test could not`
