# CDSFL Current State

Generated: 6 October 2026 03:22 BST (2026-10-06T03:22:28+01:00)

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
- **Last commit (the PARENT of the commit containing this file):** `113d749e` sv: the blockers were shown as settled, the ladder was inert in simulation, and the panel caught 3 faults in my own repairs
- **Committed:** 2026-10-05 23:48:54 +0100
- **Remote (as of the snapshot, before the sv push):** up to date with origin/sim/shakedown-2026-09-29
- **Working tree at snapshot time:** DIRTY — snapshot-time working tree listed below (NOT the sv commit's file list)

Uncommitted files at snapshot time — the working tree as it stood before the sv commit, NOT that commit's file list:
- `M bench/reference_runner_v3.py`
- `M bench/tests/test_severity_calibration.py`
- `M bench/tools/run_simulated_experiment.py`
- `M scripts/cdsfl_recover.py`
- `M scripts/cdsfl_utils.py`
- `?? bench/tests/test_fold_fixes_forward_never_touches_the_live_tree_2026-10-06.py`
- `?? bench/tests/test_recovery_names_what_ran_last_2026-10-06.py`
- `?? scripts/the_recovery_picker_cannot_see_most_runs_2026-10-06.py`

---

## Tests

**10178 tests collected** at 6 October 2026 03:22 BST, HEAD `113d749e` + uncommitted working tree (`python3 -m pytest bench/tests/ --co -q`)

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

- `113d749e sv: the blockers were shown as settled, the ladder was inert in simulation, and the panel caught 3 faults in my own repairs`
- `fe268ecb sv: state save 5 October 2026 23:45 BST`
- `a75382e3 sv: panel round 1 verified locally, the parser envelope delivered on a local branch, and the honest cost of the agent dispatches`
- `83ddb4ac sv: the withdrawal is recorded in-round as a metric, the gate's own series is persisted, and the memory index trims itself`
- `1259b87f the run-end harvest, and a discriminator that was looking for a field that does not exist`
- `10606f0e the barrier was discarding findings for their quoting, and its ambiguity guard was overridden by the branch below it`
- `1d51feeb sv: the adjudicated merge, refused-body visibility, the widened guard as a post-run sweep, and 23 board failures repaired`
- `c62ac5ab The study now carries its own reason, and the compaction alert exists at last`
- `a0a22836 sv: name the commit in the session state so A23 passes`
- `6b3f6897 sv: suite citation for the 2026-10-03 session state block (follow-up to cd19903; memory written at 06:09)`
