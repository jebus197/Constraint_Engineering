# CDSFL Current State

Generated: 14 November 2026 08:20 GMT (2026-11-14T08:20:14+00:00)

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
- **Last commit (the PARENT of the commit containing this file):** `4a802768` One batch, as he instructed: his 16 verdicts worked through, the encoding layer built, and a sentence every seat is given that was false
- **Committed:** 2026-11-13 23:29:19 +0000
- **Remote (as of the snapshot, before the sv push):** ahead of origin/sim/shakedown-2026-09-29 by 4
- **Working tree at snapshot time:** DIRTY — snapshot-time working tree listed below (NOT the sv commit's file list)

Uncommitted files at snapshot time — the working tree as it stood before the sv commit, NOT that commit's file list:
- `M  bench/cdsfl_registry/composer.py`
- `M  bench/cdsfl_registry/domain_manifest.toml`
- `A  bench/cdsfl_registry/roles/classifier.toml`
- `A  bench/cdsfl_registry/roles/orchestrator.toml`
- `A  bench/cdsfl_registry/roles/researcher.toml`
- `A  bench/cdsfl_registry/roles/worker.toml`
- `M  bench/directives/universal/cdsfl_core_formal.md`
- `M  bench/directives/universal/cdsfl_topology_formal.md`
- `A  bench/logs/asking_predicate_and_fourth_standard_2026-11-14/sandbox_harvest/cc2/attempt-1/files/experimental_notes/data/morning_report_decisions.json`
- `A  bench/logs/asking_predicate_and_fourth_standard_2026-11-14/sandbox_harvest/fable/attempt-1/files/experimental_notes/data/morning_report_decisions.json`
- `A  bench/logs/severity_proof_and_weight_2026-11-14/sandbox_harvest/cc2/attempt-1/files/experimental_notes/data/morning_report_decisions.json`
- `A  bench/logs/severity_proof_and_weight_2026-11-14/sandbox_harvest/fable/attempt-1/files/experimental_notes/data/morning_report_decisions.json`
- `M  bench/model_catalogue.py`
- `M  bench/tests/conftest.py`
- `A  bench/tests/test_a_decision_reaches_the_file_he_reads_2026-11-14.py`
- … and 170 more, not shown (list capped at 15 of 185 — run `git status --porcelain` for the full set)

---

## Tests

**17832 tests collected** at 14 November 2026 08:20 GMT, HEAD `4a802768` + uncommitted working tree (`python3 -m pytest bench/tests/ --co -q`)

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

- `4a802768 One batch, as he instructed: his 16 verdicts worked through, the encoding layer built, and a sentence every seat is given that was false`
- `84fd2253 B169: the permission predicate under-reported a residue, and composing was measured rather than asserted`
- `665a4b41 B165: the clean-tree full-suite measurement, and what it caught doing`
- `846c4ffe fix: 21 anchored corrections, 4 entries raised, 7 guards repaired`
- `e37fed9d sv: the Stop hook was overactive on his report, 4 faults fixed, 7 of 7 mutations red, and re-armed only after a green board -- plus 5 errors of my own caught before any of them shipped`
- `b18b397f sv: the steering fix built on his lift, 11 of 11 source-text assertions resolved, my own orphan figure corrected from 33 to 6, and 6 new defects found by trying to carry out his instructions`
- `3cb05d66 sv: the hook fix is installed on his word, a --help could have edited the tree, and the figure telling him he owes 8 rulings rests on a proxy no sibling predicate agrees with`
- `75832cda sv: the board refused on 2 faults of mine and both are fixed; B155 owed 2 repairs where I had counted 1; 0 of the 12 open entries are now mine`
- `072c038d sv: the 10 agreed items added to the task list and the registry, 5 of 10 measured DONE, and the instrument that measures them corrected twice in the flattering direction`
- `a081b117 sv: one domain vocabulary where there were 2 agreeing on 3 names of 17, 22 expert encodings against current standards, both convergence arms wired, and 3 board refusals fixed at their causes`
