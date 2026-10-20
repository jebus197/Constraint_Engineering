# CDSFL Current State

Generated: 20 October 2026 02:44 BST (2026-10-20T02:44:25+01:00)

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
- **Last commit (the PARENT of the commit containing this file):** `f0794ad3` B35 and B36: the severity gate was never altered, and the 300s timeout is why no full suite ran for 382 commits
- **Committed:** 2026-10-18 13:17:48 +0100
- **Remote (as of the snapshot, before the sv push):** up to date with origin/sim/shakedown-2026-09-29
- **Working tree at snapshot time:** DIRTY — snapshot-time working tree listed below (NOT the sv commit's file list)

Uncommitted files at snapshot time — the working tree as it stood before the sv commit, NOT that commit's file list:
- `M  .claude/CLAUDE.md`
- `M  bench/reference_runner_v3.py`
- `M  bench/tests/test_a_foreign_document_is_not_his_annotation_2026-10-17.py`
- `A  bench/tests/test_a_panel_request_is_tracked_2026-10-20.py`
- `A  bench/tests/test_a_question_is_its_own_kind_2026-10-19.py`
- `M  bench/tests/test_every_annotation_verdict_names_its_evidence_2026-10-17.py`
- `A  bench/tests/test_his_marker_is_read_from_its_own_line_2026-10-19.py`
- `A  bench/tests/test_his_responses_have_not_shrunk_2026-10-20.py`
- `A  bench/tests/test_his_ruling_reaches_the_report_2026-10-19.py`
- `A  bench/tests/test_i_can_parse_his_responses_in_full_2026-10-19.py`
- `M  bench/tests/test_precommit_gate_cost_2026-09-10.py`
- `M  bench/tests/test_shared_credential_seats_are_serialised_2026-10-07.py`
- `A  bench/tests/test_the_merged_severity_is_not_its_inputs_2026-10-19.py`
- `M  bench/tests/test_the_morning_report_is_generated_2026-10-12.py`
- `A  bench/tests/test_the_resource_check_never_refuses_on_memory_2026-10-19.py`
- … and 57 more, not shown (list capped at 15 of 72 — run `git status --porcelain` for the full set)

---

## Tests

**12827 tests collected** at 20 October 2026 02:44 BST, HEAD `f0794ad3` + uncommitted working tree (`python3 -m pytest bench/tests/ --co -q`)

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

- `f0794ad3 B35 and B36: the severity gate was never altered, and the 300s timeout is why no full suite ran for 382 commits`
- `cfb7c970 C4 panel ran, C18 second clause built, C12 premise corrected, B34 raised, and Rule 30 now honours the verbatim region`
- `c1249e8c B32: each declared mode now records what it DID, and the 5th turns out to have no consumer`
- `94810c13 B30: a latent-control verdict is decided from the syntax tree, not from a line distance`
- `037bd078 Note: the review stop fires on evidence, declared modes are reconciled, B26 was already built`
- `0ba6149a sv: B27 and B28 built, B26 withdrawn as already built, B29 to B32 raised`
- `5a7d7e76 B26 WITHDRAWN: it was already built, and my audit missed it by breaking a rule I wrote the day before`
- `b0cb254f B28: declared modes are now reconciled against what the run did`
- `cca6cfe5 B27: the human-review stop now fires on evidence, not on a flag`
- `76d2c6e7 sv: B29 raised, the save gate refuses the follow-up that fixes its own postcondition`
