# CDSFL Current State

Generated: 8 November 2026 10:47 GMT (2026-11-08T10:47:29+00:00)

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
- **Last commit (the PARENT of the commit containing this file):** `39507bbe` 11 errors in 1 session, all 1 shape: I reasoned where reading was available, and the evidence was in a field or a comment I never opened
- **Committed:** 2026-11-08 10:34:25 +0000
- **Remote (as of the snapshot, before the sv push):** ahead of origin/sim/shakedown-2026-09-29 by 53
- **Working tree at snapshot time:** clean

---

## Tests

**16086 tests collected** at 8 November 2026 10:47 GMT, HEAD `39507bbe` (`python3 -m pytest bench/tests/ --co -q`)

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

- `39507bbe 11 errors in 1 session, all 1 shape: I reasoned where reading was available, and the evidence was in a field or a comment I never opened`
- `42f3b92d The reader reads both marker forms, so the inline-marker ticket closes: 0 of 568 annotations lose a trailing marker`
- `15660820 Rule 6 is enforced for the first time, 1 ticket closes on tonight's own boards, and a command substitution that did not expand ran the whole suite on his machine`
- `d958d735 3 tickets triaged against the live tree: 1 raised, 1 INVALID because it read an exit code as a count, and 1 whose premise holds and now carries its verification`
- `cf707e57 The surfaces he reads were a commit behind, because regenerating them is not implied by committing the entries they derive from`
- `7cd932c9 B21's 2 untracked artefacts are ignored by design and its seats' work verifies 7 of 7, so the reason I gave for leaving it at TESTED is withdrawn and the entry's own reason stands`
- `f8518ade B102's queue-operation repair had no test reaching it, B135's recommended fix reaches 0 of its own 13 targets, and B122 closes -- a closure that refused its own commit twice, correctly both times`
- `beb806f3 B20's recommended option now carries the execution that verifies it, and regenerating the deliverable took 2 builders rather than 1 because both default to not writing`
- `d71d3f1f fb4462c4's headline figure is withdrawn and the ticket it raised is INVALID: I fed blocker_triage an entry body where it expects an obstacle, and its advice works exactly as written`
- `fb4462c4 The Stop gate's own remediation advice is structurally guaranteed to return PARK, measured at 0 of 18, and raised as a ticket rather than fixed because the file is under ~/.claude/hooks`
