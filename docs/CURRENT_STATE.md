# CDSFL Current State

Generated: 24 August 2026 02:17 BST (2026-08-24T02:17:48+01:00)

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
- **Last commit (the PARENT of the commit containing this file):** `8c57b11` Handover: eight decisions waiting, three of which need the founder's key or judgement and cannot be done by an assistant.
- **Committed:** 2026-08-24 01:06:48 +0100
- **Remote (as of the snapshot, before the sv push):** ahead of origin/main by 33 [no upstream configured]
- **Working tree at snapshot time:** DIRTY — snapshot-time working tree listed below (NOT the sv commit's file list)

Uncommitted files at snapshot time — the working tree as it stood before the sv commit, NOT that commit's file list:
- `M bench/fingerprints/CC2.json`
- `M bench/fingerprints/ChatGPT.json`
- `M bench/fingerprints/Codex.json`
- `M bench/fingerprints/DeepSeek.json`
- `M bench/fingerprints/Gemini.json`
- `M bench/logs/immune_pipeline.log`
- `M experimental_notes/Handover_Decisions_2026-08-24.md`
- `M resources/MEMORY_EXCLUSIONS.md`
- `M resources/ONBOARDING.md`
- `M resources/RECOVERY.md`
- `?? .cdsfl_tmp/`
- `?? bench/logs/exp55_v3_control_20260823T144624Z/`
- `?? bench/logs/exp55_v3_control_20260823T153955Z/`

---

## Tests

**3874 tests collected** at 24 August 2026 02:17 BST, HEAD `8c57b11` + uncommitted working tree (`python3 -m pytest bench/tests/ --co -q`)

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

- `8c57b11 Handover: eight decisions waiting, three of which need the founder's key or judgement and cannot be done by an assistant.`
- `cefe165 Runway 1.7: the replay's delta half, built and run. No convergence decision moves — and the rho third of the item is not measurable from the archive at all.`
- `95c9d36 RUNWAY: withdraw the 'targets not on this machine' claim — it was a search failure, and the blocker is a ruling not a file.`
- `3ef50d4 MANIFEST: the articles are not lost and the public leak is closed — both halves of the 8 August correction re-measured.`
- `fa4a86b RUNWAY: the arc is blocked on missing target files, not on code — and the 23 August work did not advance this list.`
- `bd9584d Three record-only instruments: the defect-rate curve, the competence-provenance check, and a vagueness linter that fails on its own motivating sentence.`
- `4ed783a ONBOARDING: Exp 55 and the gate inversion. QC stale count 1 -> 0.`
- `dcbcf68 Absolute paths only: the prompt was telling models to use the one path form the machinery cannot handle.`
- `66de417 Exp 55: the control halted at round 0, the alarm diagnosed itself correctly, and the relative-path fix it demanded is in.`
- `5690203 The co-discovery wiring was in a function with no registry, and its NameError vanished into a handler. Caught live by the cy monitor.`
