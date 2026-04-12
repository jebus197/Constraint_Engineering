# CDSFL Current State

Generated: 12 April 2026 21:05 BST (2026-04-12T21:05:26+01:00)

---

## Git

- **Branch:** exp39-experimental
- **Last commit:** `e59dedd` sv: Exp 39 phases 0-8 complete, 784 tests, Gemini confer O1+FFAFP, appendix expanded
- **Committed:** 2026-04-12 20:28:19 +0100
- **Remote:** ahead by 23
- **Working tree:** DIRTY — uncommitted changes present

Uncommitted files:
- `M resources/ONBOARDING.md`
- `M resources/RECOVERY.md`
- `?? bench/confer_o1_ffafp.py`
- `?? bench/confer_pe_o1_design.py`
- `?? bench/logs/confer_o1_ffafp/`
- `?? bench/logs/confer_pe_o1_design/`

---

## Tests

**787 tests collected** (`python3 -m pytest bench/tests/ --co -q`)

---

## Latest Experiment

- **Experiment:** exp38_ouroboros (#38)
- **Status:** WALL_CLOCK_CAP
- **Topology:** star
- **Target:** `bench/reference_runner.py`
- **Rounds:** 24
- **Total findings:** 545
- **Gamma:** 0.5097
- **Models:** CC2, ChatGPT, Codex, DeepSeek, Gemini
- **Per model:**
  - Gemini: 181
  - ChatGPT: 133
  - Codex: 102
  - DeepSeek: 99
  - CC2: 30
- **Logs:** `/Users/georgejackson/Developer_Projects/Constraint_Engineering/bench/logs/exp38_ouroboros_20260411T041938Z`

---

## Recent Commits

- `e59dedd sv: Exp 39 phases 0-8 complete, 784 tests, Gemini confer O1+FFAFP, appendix expanded`
- `401e475 Phase 8: Mathematical appendix expansion — 7 new sections`
- `8355215 Phase 7: O1 ouroboros cell shadow prototype`
- `23bff05 Phase 6: Specialist B-Cell dispatch wiring (shadow mode)`
- `a52162a Phase 5: FFAFP calibration protocol formalised in mathematical appendix`
- `d7d87bb Phase 4: Persistent immune memory with blended prior and drift detection`
- `1a30e34 Phase 3: Continuous suppression with permutation-invariant top-k weighting`
- `0dc6ab7 Phase 2: Embedding similarity shared backend`
- `c98720c Phase 1: kappa_set denominator prep — numerator-only weighting`
- `ad53693 Phase 0: sth command, FFAFP update, shadow extensions, crypto signing confer, Exp 39 configs`
