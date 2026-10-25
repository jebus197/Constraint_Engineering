# CDSFL Current State

Generated: 25 October 2026 01:48 BST (2026-10-25T01:48:52+01:00)

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
- **Last commit (the PARENT of the commit containing this file):** `161f7ae5` His duplicate taxonomy built MERGED-last, and the joint round discharges its debt
- **Committed:** 2026-10-24 03:27:16 +0100
- **Remote (as of the snapshot, before the sv push):** up to date with origin/sim/shakedown-2026-09-29
- **Working tree at snapshot time:** DIRTY — snapshot-time working tree listed below (NOT the sv commit's file list)

Uncommitted files at snapshot time — the working tree as it stood before the sv commit, NOT that commit's file list:
- `M  .claude/CLAUDE.md`
- `A  bench/tests/test_depth_before_breadth_is_gated_2026-10-25.py`
- `A  bench/tests/test_his_words_may_not_sit_unread_2026-10-25.py`
- `M  bench/tests/test_pre_verdict_sweep_shadow_2026-10-06.py`
- `A  bench/tests/test_the_stamp_goes_at_the_foot_2026-10-25.py`
- `M  bench/tickets/tickets.jsonl`
- `M  bench/tickets/tickets_searches.jsonl`
- `M  docs/CURRENT_STATE.md`
- `A  hooks/his_responses_freshness_gate.py`
- `M  hooks/local_resource_budget.py`
- `M  resources/MEMORY_EXCLUSIONS.md`
- `M  resources/ONBOARDING.md`
- `M  resources/RECOVERY.md`
- `A  scripts/depth_and_breadth_are_measurable_2026-10-25.py`
- `A  scripts/do_issues_feed_back_into_the_harness_2026-10-25.py`
- … and 1 more, not shown (list capped at 15 of 16 — run `git status --porcelain` for the full set)

---

## Tests

**12926 tests collected** at 25 October 2026 01:48 BST, HEAD `161f7ae5` + uncommitted working tree (`python3 -m pytest bench/tests/ --co -q`)

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

- `161f7ae5 His duplicate taxonomy built MERGED-last, and the joint round discharges its debt`
- `4aeecf95 UX backend built as a read-only projection, and the pack's 2 rules are enforced rather than decorated`
- `e42183a1 sv: Word rewrote his files, 30 panel requests reached nothing, and 2 guards read prose instead of state`
- `f0794ad3 B35 and B36: the severity gate was never altered, and the 300s timeout is why no full suite ran for 382 commits`
- `cfb7c970 C4 panel ran, C18 second clause built, C12 premise corrected, B34 raised, and Rule 30 now honours the verbatim region`
- `c1249e8c B32: each declared mode now records what it DID, and the 5th turns out to have no consumer`
- `94810c13 B30: a latent-control verdict is decided from the syntax tree, not from a line distance`
- `037bd078 Note: the review stop fires on evidence, declared modes are reconciled, B26 was already built`
- `0ba6149a sv: B27 and B28 built, B26 withdrawn as already built, B29 to B32 raised`
- `5a7d7e76 B26 WITHDRAWN: it was already built, and my audit missed it by breaking a rule I wrote the day before`
