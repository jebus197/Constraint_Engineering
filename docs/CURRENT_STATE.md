# CDSFL Current State

Generated: 10 November 2026 18:52 GMT (2026-11-10T18:52:43+00:00)

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
- **Last commit (the PARENT of the commit containing this file):** `b0c32e02` He gave 2 routing rulings on 2026-11-10 that nothing implements, they lived in 1 paragraph of another entry, and the figure cited for them had no producer
- **Committed:** 2026-11-10 13:41:23 +0000
- **Remote (as of the snapshot, before the sv push):** up to date with origin/sim/shakedown-2026-09-29
- **Working tree at snapshot time:** DIRTY — snapshot-time working tree listed below (NOT the sv commit's file list)

Uncommitted files at snapshot time — the working tree as it stood before the sv commit, NOT that commit's file list:
- `M  .claude/CLAUDE.md`
- `A  bench/logs/tonights_build_review_b22_b88_b105_2026-11-10/sandbox_harvest/cc2/attempt-1/files/experimental_notes/data/morning_report_decisions.json`
- `A  bench/logs/tonights_build_review_b22_b88_b105_2026-11-10/sandbox_harvest/fable/attempt-1/files/experimental_notes/data/morning_report_decisions.json`
- `A  bench/tests/test_a_mid_turn_message_is_still_his_2026-11-10.py`
- `M  bench/tests/test_a_response_is_not_a_ruling_2026-11-09.py`
- `A  bench/tests/test_a_timeout_reaps_the_board_it_abandons_2026-11-10.py`
- `A  bench/tests/test_an_entry_code_never_travels_alone_in_chat_2026-11-10.py`
- `A  bench/tests/test_prose_mentioning_raises_is_not_an_assertion_2026-11-10.py`
- `AM bench/tests/test_what_is_owed_survives_interior_bold_2026-11-10.py`
- `AM bench/tests/test_what_is_still_owed_is_quoted_whole_2026-11-10.py`
- `A  bench/tests/test_what_v_bar_counts_is_measured_2026-11-10.py`
- `M  bench/tests/test_work_not_narrate_hook_2026-09-10.py`
- `M  bench/tickets/tickets.jsonl`
- `M  bench/tickets/tickets_searches.jsonl`
- `M bench/ux_backend_2026-10-20.py`
- … and 49 more, not shown (list capped at 15 of 64 — run `git status --porcelain` for the full set)

---

## Tests

**17030 tests collected** at 10 November 2026 18:52 GMT, HEAD `b0c32e02` + uncommitted working tree (`python3 -m pytest bench/tests/ --co -q`)

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

- `b0c32e02 He gave 2 routing rulings on 2026-11-10 that nothing implements, they lived in 1 paragraph of another entry, and the figure cited for them had no producer`
- `012323bc The P-pass the Stop gate demanded found that B105's header-split fix was unguarded: reverting it left all 15 tests green, because 4 marks was the number the defect itself produced`
- `a443012c The only tool that closes an entry could not parse 7 of 248 markers, 4 of them decisions in his own queue, and a wider pattern alone would have deleted the field it could not see`
- `4565e0c3 B104's build half is done everywhere I control, and its residue is 1 word from him rather than work: the note standard's own amendment clause reserves the version bump to him`
- `8045f04e B105 is closed, and the 2 defects found while closing it are why it stayed open: the asterisk convention reached 1 of 2 spoken generators, and a single-element header list hid 4 of my own paragraphs from the marker`
- `ff4433f2 B22's claim-pattern decision now has its evidence, measured in shadow with the live configuration proved untouched, and the decision is still his`
- `8c9bdf08 The FFAFP Follow step found a second live copy of the invisible-row defect that neither panel seat named, and the guard now pins the property over every reader instead of the one instance`
- `1aba1fcf B105's spent ask is retired, which takes his queue from 8 decisions to 7, and B81 gains the gate cost measured twice tonight plus an orphaned-board leak that needs no ruling to be a defect`
- `cd8021b5 The panel refuted 2 of my claims and both reproduced; acting on the second found my own committed fix had destroyed a live admission, and the corrected rule is derived from the measurement rather than named by hand`
- `637fcd87 A reply is not a ruling, and the 554 was a line count`
