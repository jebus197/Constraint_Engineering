# CDSFL Current State

Generated: 8 November 2026 06:52 GMT (2026-11-08T06:52:33+00:00)

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
- **Last commit (the PARENT of the commit containing this file):** `59d2cf45` 60 per cent of the DONE claims in the master list rest on verification the commit gate never runs, and decision 17's scope covers a sixth of it
- **Committed:** 2026-11-08 06:39:21 +0000
- **Remote (as of the snapshot, before the sv push):** ahead of origin/sim/shakedown-2026-09-29 by 39
- **Working tree at snapshot time:** DIRTY — snapshot-time working tree listed below (NOT the sv commit's file list)

Uncommitted files at snapshot time — the working tree as it stood before the sv commit, NOT that commit's file list:
- `M experimental_notes/data/morning_report_decisions.json`
- `M experimental_notes/data/output_hashes.json`
- `?? scripts/sv_reports_a_runway_it_will_refuse_2026-11-08.py`

---

## Tests

**16060 tests collected** at 8 November 2026 06:52 GMT, HEAD `59d2cf45` + uncommitted working tree (`python3 -m pytest bench/tests/ --co -q`)

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

- `59d2cf45 60 per cent of the DONE claims in the master list rest on verification the commit gate never runs, and decision 17's scope covers a sixth of it`
- `7d481161 Decision 17 asked what growing the commit gate would cost, and the answer is graduated: 58 per cent of the ungated guards fit in under 2 per cent of the gate`
- `b364191c Adding the 83 ungated guards would double the commit gate, and running them found 3 reds the gate cannot see, 2 of them mine from hours earlier`
- `7aa972d2 B87's figure gains the producer it never had, and 2 claims I made about the commit gate's cost are withdrawn the same morning`
- `150cd478 A figure reached his morning deliverable citing a producer that has never existed, and nothing checked that for 5 days`
- `1035513f Decision 28 told him the memory index was 3 entries from refusing a save when its own producer says 0, and I corrected 3 of its 10 fields before checking how many there were`
- `173867d3 Correcting 2 statuses made the report contradict itself, B20's title claimed nothing was built against a producer measuring 4 of 4, and 3 more entries carried a status their own artefacts refuted`
- `323726f4 The evidence check read a cited line number as part of the filename, so it refused correct citations and would have refused a correct close`
- `38ae4377 Two task-list statuses claimed work was uncommitted when it was in HEAD, and a verification run of 44 guard files ran nothing while reporting as green`
- `fea0d60a A fix applied to 1 of 2 renderers is not applied: the spoken report carried 0 recorded statuses against the written copy's 7`
