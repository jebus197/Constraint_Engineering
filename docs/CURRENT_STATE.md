# CDSFL Current State

Generated: 4 November 2026 02:21 GMT (2026-11-04T02:21:12+00:00)

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
- **Last commit (the PARENT of the commit containing this file):** `a08c184a` The joint round resolved both disagreements, each seat withdrew a round-1 claim, my "opposite failure modes" synthesis was superseded, and I had hand-rolled a record the project already had a tool for
- **Committed:** 2026-11-04 02:03:11 +0000
- **Remote (as of the snapshot, before the sv push):** ahead of origin/sim/shakedown-2026-09-29 by 4
- **Working tree at snapshot time:** DIRTY — snapshot-time working tree listed below (NOT the sv commit's file list)

Uncommitted files at snapshot time — the working tree as it stood before the sv commit, NOT that commit's file list:
- `M experimental_notes/CDSFL_MASTER_TASK_LIST.md`
- `M experimental_notes/PARKED_FOR_THE_FOUNDER.md`
- `M resources/MEMORY_EXCLUSIONS.md`
- `M resources/RECOVERY.md`
- `?? bench/logs/joint_severity_spec_is_uncomputable_2026-11-04/`

---

## Tests

**15332 tests collected** at 4 November 2026 02:21 GMT, HEAD `a08c184a` + uncommitted working tree (`python3 -m pytest bench/tests/ --co -q`)

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

- `a08c184a The joint round resolved both disagreements, each seat withdrew a round-1 claim, my "opposite failure modes" synthesis was superseded, and I had hand-rolled a record the project already had a tool for`
- `4931586f A panel's own evidence-preservation step had inflated the figure a later panel was convened to measure: 88.0952 per cent triple-counted 5 findings and the true rate is 84.3750`
- `eb90d92d He DID ask what v-bar is, and the instrument written to check whether a summary had invented his question was itself blind to 206 of his 1,421 messages`
- `36fd3ec9 A guard tested UNCONFIRMED where it meant NOT SETTLED, so it refused his own reopen, and 7 reds had accumulated in the 54 guards the commit gate never runs`
- `e4b83b25 3 of his questions answered in plain English and closed with an executable verification, and the honest scale of what is left: 49 distinct questions, not 1 complaint repeated`
- `1f4b4181 An 11 MB PNG wearing a .md extension was being read as 780 of his rulings, and the 300 s test timeout it caused was masking them`
- `791dda90 A commit that measures the register and adds to it cannot have both be true: the note said 3,383 and its own producer now returns 3,384`
- `3f6bc8cc A token regex matching across a word boundary inverted its own verdict, and the stale comment beside the fix nearly had a rule added against his explicit ruling`
- `b41ab9e1 The sim branch being 1 commit behind main is a merge-graph fact, not a content gap: merging would REGRESS 5 lines to superseded text`
- `acc3fc50 A parked decision's premise inverted: splitting the grouped index lines cost 6 of 10 remaining lines when he was asked and now costs 7 of 102`
