# CDSFL Current State

Generated: 9 June 2026 23:27 BST (2026-06-09T23:27:34+01:00)

---

## Git

- **Branch:** exp39-experimental
- **Last commit:** `375236d` Convergence landmark: code-location novelty trigger — Exp 42 converges live at R6, 0 residual HIL
- **Committed:** 2026-06-09 22:14:05 +0100
- **Remote:** ahead by 162
- **Working tree:** DIRTY — uncommitted changes present

Uncommitted files:
- `M bench/fingerprints/CC2.json`
- `M bench/fingerprints/ChatGPT.json`
- `M bench/fingerprints/Codex.json`
- `M bench/fingerprints/DeepSeek.json`
- `M bench/fingerprints/Gemini.json`
- `M bench/launcher_core.py`
- `M bench/logs/immune_pipeline.log`
- `M bench/ouroboros_cell.py`
- `M bench/reference_runner_v2.py`
- `M bench/tests/test_finding_id_structural_validation.py`
- `M resources/ONBOARDING.md`
- `M resources/RECOVERY.md`
- `?? bench/convergence_location.py`
- `?? bench/exp42_configs/42_composer_locationkey_live.json`
- `?? bench/logs/exp42_composer_locationkey_live_20260609T165146Z/`

---

## Tests

**1575 tests collected** (`python3 -m pytest bench/tests/ --co -q`)

---

## Latest Experiment

- **Experiment:** exp42_composer_locationkey_live (#42)
- **Status:** CONVERGED
- **Topology:** star
- **Target:** `bench/cdsfl_registry/composer.py`
- **Rounds:** 7
- **Total findings:** 80
- **Gamma:** 0.5327
- **Models:** CC2, ChatGPT, Codex, DeepSeek, Gemini
- **Per model:**
  - Gemini: 34
  - Codex: 15
  - DeepSeek: 12
  - ChatGPT: 11
  - CC2: 8
- **Logs:** `/Users/georgejackson/Developer_Projects/Constraint_Engineering/bench/logs/exp42_composer_locationkey_live_20260609T183659Z`

---

## Recent Commits

- `375236d Convergence landmark: code-location novelty trigger — Exp 42 converges live at R6, 0 residual HIL`
- `00dc15f sv: Exp 42 clean rerun (routing wired+live, 0 HIL) + DEFINITIVE non-convergence root cause = cross-round dedup failure + active-vs-dormant audit + complete session ledger + LaunchPad install. Next gated: fix dedup, re-run.`
- `2aedf39 ledger: capture tool capability-awareness / graceful-degradation directive + LaunchPad install`
- `f15ea87 session audit: complete ~17h ledger (done/established/active-vs-dormant/outstanding/corrections)`
- `c9dcf51 tracker: DEFINITIVE Exp-42 non-convergence root cause = cross-round dedup failure + pr`
- `a9b2366 tracker: Exp 42 clean-rerun verdict + audit-first post-pause plan`
- `041faaa fix take-up-slack wiring test: first rung is Codex (ordering change), not CC2`
- `d134e8f wire take-up-slack into runner round loop + clean-rerun config`
- `ec7f3c7 notes + tracker: capability-aware falsifier routing design, validation, resume pointer`
- `d383a6e take-up-slack: capability-aware falsifier routing (validated, unit-tested)`
