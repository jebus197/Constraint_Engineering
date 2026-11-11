# CDSFL Current State

Generated: 11 November 2026 00:57 GMT (2026-11-11T00:57:12+00:00)

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
- **Last commit (the PARENT of the commit containing this file):** `a7fca3f3` He challenged 4 claims in my own report and was right about all 4, including 1 where I re-presented 5 decisions he had already ruled on inside the report whose subject was that exact defect
- **Committed:** 2026-11-10 21:46:14 +0000
- **Remote (as of the snapshot, before the sv push):** up to date with origin/sim/shakedown-2026-09-29
- **Working tree at snapshot time:** DIRTY — snapshot-time working tree listed below (NOT the sv commit's file list)

Uncommitted files at snapshot time — the working tree as it stood before the sv commit, NOT that commit's file list:
- `A  bench/credential_store.py`
- `M bench/tests/conftest.py`
- `M  bench/tests/test_precommit_gate_cost_2026-09-10.py`
- `A  bench/tests/test_the_asking_predicate_measurement_is_reproducible_2026-11-11.py`
- `AM bench/tests/test_the_credential_store_holds_nothing_in_plaintext_2026-11-10.py`
- `M  bench/tests/test_the_two_decision_surfaces_cannot_diverge_2026-11-01.py`
- `M  bench/tickets/sv_completions.jsonl`
- `M  bench/tickets/tickets.jsonl`
- `M  bench/tickets/tickets_searches.jsonl`
- `M  bench/ux_backend_2026-10-20.py`
- `M  docs/CURRENT_STATE.md`
- `M  docs/GLOSSARY.md`
- `M  experimental_notes/CDSFL_MASTER_TASK_LIST.md`
- `M  experimental_notes/RUNWAY_to_BR2_2026-08-18.md`
- `M  experimental_notes/data/morning_report_decisions.json`
- … and 9 more, not shown (list capped at 15 of 24 — run `git status --porcelain` for the full set)

---

## Tests

**17092 tests collected** at 11 November 2026 00:57 GMT, HEAD `a7fca3f3` + uncommitted working tree (`python3 -m pytest bench/tests/ --co -q`)

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

- `a7fca3f3 He challenged 4 claims in my own report and was right about all 4, including 1 where I re-presented 5 decisions he had already ruled on inside the report whose subject was that exact defect`
- `64b22872 sv: state save 10 November 2026, after the free round's 4 defects were folded back`
- `371f55cc A free panel attacked the one change that puts derived prose in front of him and found 4 defects, one of which had inverted B81's meaning in the file he decides from`
- `b0c32e02 He gave 2 routing rulings on 2026-11-10 that nothing implements, they lived in 1 paragraph of another entry, and the figure cited for them had no producer`
- `012323bc The P-pass the Stop gate demanded found that B105's header-split fix was unguarded: reverting it left all 15 tests green, because 4 marks was the number the defect itself produced`
- `a443012c The only tool that closes an entry could not parse 7 of 248 markers, 4 of them decisions in his own queue, and a wider pattern alone would have deleted the field it could not see`
- `4565e0c3 B104's build half is done everywhere I control, and its residue is 1 word from him rather than work: the note standard's own amendment clause reserves the version bump to him`
- `8045f04e B105 is closed, and the 2 defects found while closing it are why it stayed open: the asterisk convention reached 1 of 2 spoken generators, and a single-element header list hid 4 of my own paragraphs from the marker`
- `ff4433f2 B22's claim-pattern decision now has its evidence, measured in shadow with the live configuration proved untouched, and the decision is still his`
- `8c9bdf08 The FFAFP Follow step found a second live copy of the invisible-row defect that neither panel seat named, and the guard now pins the property over every reader instead of the one instance`
