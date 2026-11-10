# CDSFL Current State

Generated: 10 November 2026 06:47 GMT (2026-11-10T06:47:08+00:00)

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
- **Last commit (the PARENT of the commit containing this file):** `637fcd87` A reply is not a ruling, and the 554 was a line count
- **Committed:** 2026-11-10 00:56:11 +0000
- **Remote (as of the snapshot, before the sv push):** ahead of origin/sim/shakedown-2026-09-29 by 1
- **Working tree at snapshot time:** DIRTY — snapshot-time working tree listed below (NOT the sv commit's file list)

Uncommitted files at snapshot time — the working tree as it stood before the sv commit, NOT that commit's file list:
- `M  bench/domain_immune.py`
- `M  bench/model_catalogue.py`
- `M  bench/reference_runner_v3.py`
- `A  bench/tests/test_a_confirming_tool_must_discriminate_to_admit_2026-11-10.py`
- `A  bench/tests/test_a_heading_is_recorded_not_guessed_2026-11-10.py`
- `A  bench/tests/test_a_prose_fix_is_gated_on_its_falsifier_2026-11-10.py`
- `M  bench/tests/test_a_store_key_is_not_an_identifier_2026-11-07.py`
- `A  bench/tests/test_a_third_class_row_is_visible_to_its_guard_2026-11-10.py`
- `M  bench/tests/test_apply_fixes_back.py`
- `M  bench/tests/test_the_actuator_holds_its_contract_2026-11-03.py`
- `M  bench/tests/test_the_polarity_hazard_reachability_2026-10-31.py`
- `M  bench/tests/test_the_two_decision_surfaces_cannot_diverge_2026-11-01.py`
- `A  bench/tests/test_the_verification_set_comes_from_the_topic_2026-11-10.py`
- `A  bench/tests/test_tonights_producers_are_reached_2026-11-10.py`
- `A  bench/tests/test_what_models_are_in_use_is_derived_2026-11-10.py`
- … and 87 more, not shown (list capped at 15 of 102 — run `git status --porcelain` for the full set)

---

## Tests

**16810 tests collected** at 10 November 2026 06:47 GMT, HEAD `637fcd87` + uncommitted working tree (`python3 -m pytest bench/tests/ --co -q`)

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

- `637fcd87 A reply is not a ruling, and the 554 was a line count`
- `5e15076b A Wilson upper bound was wrong in 6 places, and the figure had no producer`
- `897e0f94 The canonical interval helper, and the correction of my own correction`
- `fc9edaf7 sv: state save 9 November 2026 04:11 GMT`
- `fc0b2e60 104 guard files brought inside the gate, and the last silent admission step closed`
- `2c50cf2d A board I killed by hand recorded as a fast refusal, and it moved the figure I had just quoted him`
- `a76f5f61 The sv gate I added to keep local state fresh reintroduced the misreading sv's own banner exists to prevent, realised twice tonight`
- `a1773584 sv: his 29 rulings worked through -- 13 entries built and closed, 9 of my own ruled dates withdrawn as wrong, and 12 decisions left that are his`
- `675af51e I built 5 of his entries and left all 5 marked OPEN: the 2-surface lesson, applied all night and missed on my own work`
- `655aa815 A stamper with 15 tests and its own mutation harness had stamped 0 of 148 briefs, because it was wired to 1 of 2 builders`
