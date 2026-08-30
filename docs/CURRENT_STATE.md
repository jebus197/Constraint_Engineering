# CDSFL Current State

Generated: 30 August 2026 09:16 BST (2026-08-30T09:16:55+01:00)

---

## Git

- **Branch:** main
- **Last commit:** `9e12f2d` Complete the morning TTS: the MC measurement, the five tasks, and the corrected headline.
- **Committed:** 2026-08-30 09:15:27 +0100
- **Remote:** ahead of origin/main by 149
- **Working tree:** clean

---

## Tests

**4401 tests collected** at 30 August 2026 09:16 BST, HEAD `9e12f2d` (`python3 -m pytest bench/tests/ --co -q`)

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

- `9e12f2d Complete the morning TTS: the MC measurement, the five tasks, and the corrected headline.`
- `2a1ca72 Task 5: wire the fix-efficacy probe, and let sy falsify my own headline.`
- `60fa5e0 Tasks 1, 3, 4: lint the notes, sweep the stale ONBOARDING claim, and generalise the audit that missed it.`
- `741adfa Version both reviewers in full, and finalise the morning report.`
- `57b8df5 For a ruling: the integrity guard rejects 17 honest falsifiers when run from a worktree.`
- `6c6dd9e Preserve the canary disagreement, and say where I think it resolves.`
- `3197e50 The discrimination overlay was carrying the repository history into itself: the plant at precision 1.000, no key needed.`
- `eeaa0b3 A REAL sandbox escape, which I twice told the founder was a false alarm.`
- `7d7580f Version the repair-loop panel verbatim, and add its findings to the morning report.`
- `657b02c LATENT high-severity: the discrimination control will mint false mechanical faults on BR2.`
