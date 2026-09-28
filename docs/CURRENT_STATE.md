# CDSFL Current State

Generated: 29 September 2026 00:11 BST (2026-09-29T00:11:19+01:00)

---

## Git

- **Branch:** main
- **Last commit:** `6ed7cf6` A test asserted a phrase was absent from the repo, then committing it made the phrase present
- **Committed:** 2026-09-28 03:25:54 +0100
- **Remote:** ahead of origin/main by 3
- **Working tree:** DIRTY — uncommitted changes present

Uncommitted files:
- `M .claude/CLAUDE.md`
- `M bench/confer_maths_panel_2026-09-05.py`
- `M bench/directives/universal/paid_dispatch_authorisations.json`
- `M bench/tests/test_explorer_stopping_quantity_2026-09-28.py`
- `M bench/tests/test_note_naming_check_2026-09-28.py`
- `M bench/tests/test_paid_dispatch_needs_authorisation_2026-09-28.py`
- `M docs/REPRODUCING.md`
- `M experimental_notes/CDSFL_MASTER_TASK_LIST.md`
- `M experimental_notes/Dedup_Historical_Brief_Addendum_2026-08-18.md`
- `M experimental_notes/Design_Reviews_Bugzilla_And_Perturbation_2026-08-21.md`
- `M explorer/index.html`
- `M hooks/ffafp_audit.py`
- `M resources/RECOVERY.md`
- `M scripts/cdsfl_onboard.py`
- `M scripts/explorer_stopping_rule_is_superseded_2026-09-28.py`
- … and 18 more, not shown (list capped at 15 of 33 — run `git status --porcelain` for the full set)

---

## Tests

**8847 tests collected** at 29 September 2026 00:11 BST, HEAD `6ed7cf6` + uncommitted working tree (`python3 -m pytest bench/tests/ --co -q`)

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

- `6ed7cf6 A test asserted a phrase was absent from the repo, then committing it made the phrase present`
- `b16edf4 The harvest recorded the dispatcher's own log output as seat-written work`
- `a05d7c7 The published explorer applies a stopping rule the appendix retired, and paid dispatch was the default`
- `9f8a10a I raised a false alarm on the Wolfram licence twice, and CLAUDE.md was why`
- `351433b rs: exit 0, and it found a stale tracker plus 4 terms I had invented`
- `f8e6011 sv: the prose flag admitted every harmful fix, the trace detector was dead 2 days, and 2 of my tests verified nothing`
- `c3ad127 Report pair updated with the panel review: 3 defects I had not reached`
- `4c0caa3 The panel found 3 defects I had not reached, including a test of mine that verified nothing`
- `e9c28e1 Clean suite: 9 failed, 8606 passed -- 38 of the 47 closed; and the gate I armed is evadable`
- `d193539 The classifier repair was insufficient, and my test for it was vacuous`
