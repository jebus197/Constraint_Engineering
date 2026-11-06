# CDSFL Current State

Generated: 6 November 2026 02:45 GMT (2026-11-06T02:45:02+00:00)

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
- **Last commit (the PARENT of the commit containing this file):** `e2a87dac` The complete board's largest failure cluster was one interval helper, and the detector that found it is blind to 43% of the same algebra
- **Committed:** 2026-11-06 01:39:39 +0000
- **Remote (as of the snapshot, before the sv push):** ahead of origin/sim/shakedown-2026-09-29 by 18
- **Working tree at snapshot time:** DIRTY — snapshot-time working tree listed below (NOT the sv commit's file list)

Uncommitted files at snapshot time — the working tree as it stood before the sv commit, NOT that commit's file list:
- `A  bench/tests/test_an_authored_ruling_date_cannot_override_the_marker_2026-11-06.py`
- `M bench/tests/test_open_brain_assessment_2026-09-10.py`
- `A  bench/tests/test_the_brief_stamps_its_artefacts_2026-11-06.py`
- `A  bench/tests/test_the_census_producer_actually_runs_2026-11-04.py`
- `M bench/tickets/tickets.jsonl`
- `M bench/tickets/tickets_searches.jsonl`
- `M  experimental_notes/CDSFL_MASTER_TASK_LIST.md`
- `M  experimental_notes/Decisions_Awaiting_You_2026-11-04.md`
- `M experimental_notes/Similarity_Function_External_Benchmarking_2026-08-16.md`
- `MM experimental_notes/data/morning_report_decisions.json`
- `A  scripts/_mut_stamper.py`
- `M  scripts/build_period_joint_brief_2026-11-04.py`
- `A  scripts/did_the_hash_ids_stop_2026-11-06.py`
- `A  scripts/falsifier_the_census_producer_tracks_the_fixed_state_2026-11-04.py`
- `A  scripts/how_many_verdicts_really_await_him_2026-11-06.py`
- … and 6 more, not shown (list capped at 15 of 21 — run `git status --porcelain` for the full set)

---

## Tests

**15683 tests collected** at 6 November 2026 02:45 GMT, HEAD `e2a87dac` + uncommitted working tree (`python3 -m pytest bench/tests/ --co -q`)

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

- `e2a87dac The complete board's largest failure cluster was one interval helper, and the detector that found it is blind to 43% of the same algebra`
- `e0feed27 A resume pointer's git facts were unreachable by the guard written to check them, and the FOLLOW that found it took 3 passes`
- `da38d9ac The independent check he ordered never ran: a 2-seat pair stood in for a 5-seat panel, and the cause is the dispatcher's own default`
- `4d363c52 The figure withdrawn from B120 now has a producer, and it says the withdrawn number overstated the evidence by 9 orders of magnitude`
- `ee1f89df The second complete board found 20 failures my own repairs had introduced, and the canonical interval helper carried a crash that no test could reach`
- `c4553e95 The mypy question deferred for machine cost takes 1.1 seconds, and the figure it yields is half config noise and a third one idiomatic line`
- `8c1ba3e9 Both mechanisms that keep the memory index inside its limits are exhausted at once, and I nearly rebuilt one of them before tracing its callers`
- `88f30053 His blinkered-depth hypothesis measured for the first time: not supported on this budget, and the decision rule he wrote has a missing third category`
- `03e675b8 A declaration whose purpose is to be checkable had 2 drifted citations and a function that does not exist, and the test written to catch exactly that was too weak to see it`
- `e9c5d587 A panel seat found the weighted risk is not a probability, 3 surfaces said it was, and the detector I wrote to count them matched its own remedy 3 times`
