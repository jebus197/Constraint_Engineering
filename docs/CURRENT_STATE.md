# CDSFL Current State

Generated: 8 June 2026 13:40 BST (2026-06-08T13:40:16+01:00)

---

## Git

- **Branch:** exp39-experimental
- **Last commit:** `2aedf39` ledger: capture tool capability-awareness / graceful-degradation directive + LaunchPad install
- **Committed:** 2026-06-08 09:35:39 +0100
- **Remote:** ahead by 160
- **Working tree:** DIRTY — uncommitted changes present

Uncommitted files:
- `M bench/fingerprints/CC2.json`
- `M bench/fingerprints/ChatGPT.json`
- `M bench/fingerprints/Codex.json`
- `M bench/fingerprints/DeepSeek.json`
- `M bench/fingerprints/Gemini.json`
- `M bench/logs/immune_pipeline.log`
- `?? bench/confer_operational_directive_pr_2026-06-06.py`
- `?? bench/logs/confer_operational_pr_2026-06-06/`
- `?? bench/logs/exp42_composer_20260603T110641Z/`
- `?? bench/logs/exp42_composer_20260606T202037Z/`
- `?? bench/logs/exp42_composer_confirm_20260606T184941Z/`
- `?? bench/logs/exp42_composer_takeupslack_20260607T154745Z/`
- `?? bench/logs/falsifier_matrix_2026-06-06/`
- `?? bench/logs/falsifier_matrix_2026-06-06_run1/`
- `?? bench/logs/falsifier_matrix_2026-06-06_run2/`

---

## Tests

**1556 tests collected** (`python3 -m pytest bench/tests/ --co -q`)

---

## Latest Experiment

- **Experiment:** exp42_composer_takeupslack (#42)
- **Status:** INCOMPLETE
- **Topology:** star
- **Target:** `bench/cdsfl_registry/composer.py`
- **Rounds:** 16
- **Total findings:** 150
- **Gamma:** 0.4741
- **Models:** CC2, ChatGPT, Codex, DeepSeek, Gemini
- **Per model:**
  - Gemini: 63
  - DeepSeek: 25
  - ChatGPT: 24
  - Codex: 22
  - CC2: 16
- **Logs:** `/Users/georgejackson/Developer_Projects/Constraint_Engineering/bench/logs/exp42_composer_takeupslack_20260607T154745Z`

---

## Recent Commits

- `2aedf39 ledger: capture tool capability-awareness / graceful-degradation directive + LaunchPad install`
- `f15ea87 session audit: complete ~17h ledger (done/established/active-vs-dormant/outstanding/corrections)`
- `c9dcf51 tracker: DEFINITIVE Exp-42 non-convergence root cause = cross-round dedup failure + pr`
- `a9b2366 tracker: Exp 42 clean-rerun verdict + audit-first post-pause plan`
- `041faaa fix take-up-slack wiring test: first rung is Codex (ordering change), not CC2`
- `d134e8f wire take-up-slack into runner round loop + clean-rerun config`
- `ec7f3c7 notes + tracker: capability-aware falsifier routing design, validation, resume pointer`
- `d383a6e take-up-slack: capability-aware falsifier routing (validated, unit-tested)`
- `5c8a4cb CORRECTION: the 7 'HIL residuals' are all resolvable; HIL floor is ZERO`
- `e839893 tracker: CONFIRM-only runner built + validated; honest 2-gate convergence verdict`
