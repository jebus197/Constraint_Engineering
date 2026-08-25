# CDSFL Current State

Generated: 25 August 2026 22:44 BST (2026-08-25T22:44:22+01:00)

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

- **Branch:** build-experiment-2026-08-22
- **Last commit (the PARENT of the commit containing this file):** `931827a` sy and the missing half of FFAFP: two hand-picked points do not prove a gate implements what it says.
- **Committed:** 2026-08-25 22:32:18 +0100
- **Remote (as of the snapshot, before the sv push):** diverged from origin/main (ahead 53, behind 3) [no upstream configured]
- **Working tree at snapshot time:** DIRTY — snapshot-time working tree listed below (NOT the sv commit's file list)

Uncommitted files at snapshot time — the working tree as it stood before the sv commit, NOT that commit's file list:
- `M  bench/tests/test_documentation_drift_guards_2026-08-25.py`
- `M docs/CURRENT_STATE.md`
- `M experimental_notes/data/instrument_inventory.json`
- `MM resources/MEMORY_EXCLUSIONS.md`
- `MM resources/ONBOARDING.md`
- `MM resources/RECOVERY.md`
- `M  scripts/cdsfl_sv.py`
- `?? .cdsfl_tmp/`

---

## Tests

**3905 tests collected** at 25 August 2026 22:44 BST, HEAD `931827a` + uncommitted working tree (`python3 -m pytest bench/tests/ --co -q`)

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

- `931827a sy and the missing half of FFAFP: two hand-picked points do not prove a gate implements what it says.`
- `9fa21e4 Commission the four stopping components, guard the drift class, and fix the instrument that measures instruments.`
- `f375ade explorer/index.html: mirror the caveat trim (see the explorer repo commit for the reasoning).`
- `115b731 docs/WORKING_DIRECTIVES.md: the portable two-thirds of the working configuration, published because a run cannot be understood without it.`
- `c6b06ea Merge origin/main: reconcile the fork created by publishing through the API.`
- `e831ffb README 6.8: seven sliders, not five (mirrors main; see that commit for the root cause and the two further instances).`
- `95e6a67 README 6.8: seven sliders, not five. Reported by Fable, confirmed by counting, and it was in three places rather than one.`
- `4e4b32d RUNWAY 7.3: a second small result for the appendix -- the crossing is transcritical, and my saddle-node description was wrong.`
- `08feb00 README 6.8: bifurcation diagram, named and not disclaimed (mirrors the main-branch publish; see that commit message for the full account and the transcritical verification).`
- `f4967c5 README 6.8: name the figure for what it is -- a bifurcation diagram -- and stop disclaiming it.`
