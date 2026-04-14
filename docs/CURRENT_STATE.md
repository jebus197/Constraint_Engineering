# CDSFL Current State

Generated: 14 April 2026 11:30 BST (2026-04-14T11:30:53+01:00)

---

## Git

- **Branch:** exp39-experimental
- **Last commit:** `00f5bd2` sv: Full STEM tool access for CC1+CC2, ν_k novelty metric designed, CDSFL self-assessed at 0.807
- **Committed:** 2026-04-14 09:10:10 +0100
- **Remote:** ahead by 40
- **Working tree:** DIRTY — uncommitted changes present

Uncommitted files:
- `M bench/logs/immune_pipeline.log`
- `M bench/ouroboros_cell.py`
- `M bench/reference_runner.py`
- `M docs/MATHEMATICAL_APPENDIX.md`
- `M experimental_notes/Novelty_Scoring_nu_k_Design_2026-04-14.md`
- `M resources/ONBOARDING.md`
- `M resources/RECOVERY.md`
- `?? bench/confer_stage6_model.py`
- `?? bench/confer_stage6_r2.py`
- `?? bench/dm/_shadow_stage6.py`
- `?? bench/logs/confer_stage6_model/`
- `?? bench/logs/confer_stage6_r2/`
- `?? experimental_notes/Stage6_Confer_Synthesis_2026-04-14.md`
- `?? experimental_notes/Stage6_R2_Confer_Synthesis_2026-04-14.md`

---

## Tests

**793 tests collected** (`python3 -m pytest bench/tests/ --co -q`)

---

## Latest Experiment

- **Experiment:** exp39_0_gate (#39)
- **Status:** INCOMPLETE
- **Topology:** star
- **Target:** `bench/runner_core.py`
- **Rounds:** 6
- **Total findings:** 111
- **Gamma:** 0.4612
- **Models:** CC2, ChatGPT, Codex, DeepSeek, Gemini
- **Per model:**
  - CC2: 28
  - Codex: 25
  - ChatGPT: 25
  - Gemini: 21
  - DeepSeek: 12
- **Logs:** `/Users/georgejackson/Developer_Projects/Constraint_Engineering/bench/logs/exp39_0_gate_20260413T193320Z`

---

## Recent Commits

- `00f5bd2 sv: Full STEM tool access for CC1+CC2, ν_k novelty metric designed, CDSFL self-assessed at 0.807`
- `f5e73ab sv: Exp 39-0 gate complete, 10 bugs fixed, 793 tests green, morning report ready`
- `5814760 Exp 39-0 gate: 10 bugs found, all fixed, 793 tests green`
- `252cf9b sv: Exp 39-0 confounded — user prompt R_k fix, lessons-forward audit (11 lost, 7 remaining), fingerprint gap, test article design error`
- `d54a8e6 sv: Exp 39-0 complete (4 rounds, 78 findings, γ=0.798), FFAFP+R_k decomposed dispatch fix, provider fix, oscillating R_k compliance identified`
- `2f8f8bc Fix burst_mode config override + atomic runner checkpoint + monitoring`
- `e64bb14 Fix 4 deferred non-blocking items from CC2 runner review`
- `cb8a936 Fix 4 additional blockers from delayed sub-agent results (10-stream review complete)`
- `2279adb Fix all pre-launch review blockers — 11 fixes from 10-stream review`
- `83dd7ab HIL gate, domain TOMLs, PE FFAFP+Meta SRP HARD constraints, FFAFP naming fix`
