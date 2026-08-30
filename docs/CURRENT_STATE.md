# CDSFL Current State

Generated: 30 August 2026 14:09 BST (2026-08-30T14:09:06+01:00)

---

## Git

- **Branch:** main
- **Last commit:** `a2ce923` Wire EXTEND, the only parsed verdict nothing read, and re-verify the rest under sy.
- **Committed:** 2026-08-30 14:04:02 +0100
- **Remote:** ahead of origin/main by 156
- **Working tree:** DIRTY — uncommitted changes present

Uncommitted files:
- `?? experimental_notes/Extend_And_Reverification_2026-08-30.md`

---

## Tests

**4436 tests collected** at 30 August 2026 14:09 BST, HEAD `a2ce923` + uncommitted working tree (`python3 -m pytest bench/tests/ --co -q`)

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

- `a2ce923 Wire EXTEND, the only parsed verdict nothing read, and re-verify the rest under sy.`
- `43896fd Run sv again after a second memory write: 124 -> 125.`
- `38c458f The simulated run already exists: exercise the 2026-08-29/30 repairs in it, 15/15 stages green.`
- `c898988 Extract a reviewer s work BEFORE tearing the sandbox down.`
- `757cea3 Capture reviewer tool calls, and deliver the t artefact pair.`
- `862ff7c Enforce the MC command set with a hook, because marking it in six places has not worked since April.`
- `81bef2e Run sv to derive the memory ledger rather than hand-correct it an eighth time.`
- `9e12f2d Complete the morning TTS: the MC measurement, the five tasks, and the corrected headline.`
- `2a1ca72 Task 5: wire the fix-efficacy probe, and let sy falsify my own headline.`
- `60fa5e0 Tasks 1, 3, 4: lint the notes, sweep the stale ONBOARDING claim, and generalise the audit that missed it.`
