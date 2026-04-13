# CDSFL Current State

Generated: 13 April 2026 02:10 BST (2026-04-13T02:10:27+01:00)

---

## Git

- **Branch:** exp39-experimental
- **Last commit:** `2488fa1` sv: Exp 39 readiness assessment — 39-0 ready to run, provenance + launch fixes
- **Committed:** 2026-04-13 01:26:11 +0100
- **Remote:** ahead by 29
- **Working tree:** DIRTY — uncommitted changes present

Uncommitted files:
- `M bench/dm/_types.py`
- `M bench/immune_agents.py`
- `M bench/insect_brain.py`
- `M bench/logs/immune_pipeline.log`
- `M bench/reference_runner.py`
- `M resources/RECOVERY.md`

---

## Tests

**793 tests collected** (`python3 -m pytest bench/tests/ --co -q`)

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

- `2488fa1 sv: Exp 39 readiness assessment — 39-0 ready to run, provenance + launch fixes`
- `a8fb729 Fix launch path: --test-article no longer blocks --config-only invocation`
- `f57d6ce Fix provenance pipeline: origin_type on all findings, registry capture, macrophage_cell.py committed`
- `bd09f88 sv: Macrophage/Ouroboros cell type split — 793 tests, 4 confer rounds, provenance schema`
- `996ec52 sv: Gap analysis confer (3 rounds), domain-agnostic gate redesign, execution order agreed`
- `89b6a05 sv: Gemini confer round 2 (PE 3-gate + O1 calibration design), recovery docs updated`
- `e59dedd sv: Exp 39 phases 0-8 complete, 784 tests, Gemini confer O1+FFAFP, appendix expanded`
- `401e475 Phase 8: Mathematical appendix expansion — 7 new sections`
- `8355215 Phase 7: O1 ouroboros cell shadow prototype`
- `23bff05 Phase 6: Specialist B-Cell dispatch wiring (shadow mode)`
