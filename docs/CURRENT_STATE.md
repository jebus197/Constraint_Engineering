# CDSFL Current State

Generated: 12 November 2026 08:41 GMT (2026-11-12T08:41:22+00:00)

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
- **Last commit (the PARENT of the commit containing this file):** `072c038d` sv: the 10 agreed items added to the task list and the registry, 5 of 10 measured DONE, and the instrument that measures them corrected twice in the flattering direction
- **Committed:** 2026-11-12 04:54:01 +0000
- **Remote (as of the snapshot, before the sv push):** up to date with origin/sim/shakedown-2026-09-29
- **Working tree at snapshot time:** DIRTY — snapshot-time working tree listed below (NOT the sv commit's file list)

Uncommitted files at snapshot time — the working tree as it stood before the sv commit, NOT that commit's file list:
- `A  bench/cdsfl_registry/domain_proposer.py`
- `M  bench/confer_maths_panel_2026-09-05.py`
- `M  bench/directives/biomedical/biomedical_clinical.txt`
- `M  bench/directives/biomedical/biomedical_device.txt`
- `M  bench/directives/biomedical/biomedical_pharma.txt`
- `M  bench/directives/chemistry/chemistry_analytical.txt`
- `M  bench/directives/chemistry/chemistry_pharma.txt`
- `M  bench/directives/chemistry/chemistry_process.txt`
- `M  bench/directives/cross-domain/cross_mechanical_electrical.txt`
- `M  bench/directives/cross-domain/cross_software_hardware.txt`
- `M  bench/directives/cross-domain/cross_thermal_electrical.txt`
- `M  bench/directives/hardware/hardware_embedded.txt`
- `M  bench/directives/hardware/hardware_power.txt`
- `M  bench/directives/hardware/hardware_rf.txt`
- `M  bench/directives/industrial/industrial_cnc.txt`
- … and 65 more, not shown (list capped at 15 of 80 — run `git status --porcelain` for the full set)

---

## Tests

**17336 tests collected** at 12 November 2026 08:41 GMT, HEAD `072c038d` + uncommitted working tree (`python3 -m pytest bench/tests/ --co -q`)

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

- `072c038d sv: the 10 agreed items added to the task list and the registry, 5 of 10 measured DONE, and the instrument that measures them corrected twice in the flattering direction`
- `a081b117 sv: one domain vocabulary where there were 2 agreeing on 3 names of 17, 22 expert encodings against current standards, both convergence arms wired, and 3 board refusals fixed at their causes`
- `d41ea210 sv: the 0.7 cut is not a severity measurement -- every CRITICAL call the project has made dies under a re-scaling that reorders nothing; the domain that would supply the units is a flag with no classifier and no record`
- `92ae4a1a A retirement flag was silencing a question 15,438 characters below the marker that could not reach it, a stored verdict was outvoting the live predicate, and his credential store is built`
- `a7fca3f3 He challenged 4 claims in my own report and was right about all 4, including 1 where I re-presented 5 decisions he had already ruled on inside the report whose subject was that exact defect`
- `64b22872 sv: state save 10 November 2026, after the free round's 4 defects were folded back`
- `371f55cc A free panel attacked the one change that puts derived prose in front of him and found 4 defects, one of which had inverted B81's meaning in the file he decides from`
- `b0c32e02 He gave 2 routing rulings on 2026-11-10 that nothing implements, they lived in 1 paragraph of another entry, and the figure cited for them had no producer`
- `012323bc The P-pass the Stop gate demanded found that B105's header-split fix was unguarded: reverting it left all 15 tests green, because 4 marks was the number the defect itself produced`
- `a443012c The only tool that closes an entry could not parse 7 of 248 markers, 4 of them decisions in his own queue, and a wider pattern alone would have deleted the field it could not see`
