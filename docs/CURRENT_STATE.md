# CDSFL Current State

Generated: 16 May 2026 03:31 BST (2026-05-16T03:31:35+01:00)

---

## Git

- **Branch:** exp39-experimental
- **Last commit:** `9071025` sv-followup: tracker HEAD -> b13dd6d (confer-closed terminal state)
- **Committed:** 2026-05-15 23:24:40 +0100
- **Remote:** ahead by 101
- **Working tree:** DIRTY — uncommitted changes present

Uncommitted files:
- `M bench/dm/_feedback.py`
- `M bench/logs/immune_pipeline.log`
- `M bench/reference_runner_v2.py`
- `M experimental_notes/CDSFL_Agent_Operational_Plan.md`
- `M experimental_notes/Exp40_to_54_Consolidated_Plan_2026-04-21.md`
- `?? bench/confer_exp40_timing_neutral_2026-05-16.py`
- `?? bench/logs/confer_exp40_timing_neutral_2026-05-16/`
- `?? bench/tests/test_finding_id_collision_detector.py`
- `?? experimental_notes/Exp40_Timing_Reconfer_Outcome_2026-05-16.md`
- `?? experimental_notes/Exp40_Timing_Reconfer_Outcome_Plain_English_2026-05-16.md`

---

## Tests

**1414 tests collected** (`python3 -m pytest bench/tests/ --co -q`)

---

## Latest Experiment

- **Experiment:** exp40_gate (#40)
- **Status:** INCOMPLETE
- **Topology:** star
- **Target:** `bench/dm/_feedback.py`
- **Rounds:** 17
- **Total findings:** 280
- **Gamma:** 0.0342
- **Models:** CC2, ChatGPT, Codex, DeepSeek, Gemini
- **Per model:**
  - Gemini: 94
  - DeepSeek: 86
  - ChatGPT: 45
  - CC2: 33
  - Codex: 22
- **Logs:** `/Users/georgejackson/Developer_Projects/Constraint_Engineering/bench/logs/exp40_gate_20260514T020550Z`

---

## Recent Commits

- `9071025 sv-followup: tracker HEAD -> b13dd6d (confer-closed terminal state)`
- `b13dd6d sv: live 5-model architectural confer CLOSED — 5/5 unanimous YES (resume R17-R21 G7-disabled + enable G7 at Exp 41 as designed, no blockers); confer script + logs + paired outcome notes; ONBOARDING/RECOVERY/tracker updated`
- `553d41d sv-followup: operational tracker HEAD 3bbf2c7->7ecbf26 post-sv`
- `7ecbf26 sv: Exp 40 continuation + post-continuation fix tranche (1a-1e parser/classifier/RT-v2/ITC/reformat), G7 merge-arbitration module (default-disabled), DeepSeek Phase-1 reasoning_content fix, gamma-input triple-cross-verification, codex false-positive resolution; 229 tests pass; paired post-mortems`
- `3bbf2c7 feat: launcher_core shared infrastructure + G7 merge-deadlock design`
- `7f3066b fix: ITC CAPABILITY_MISMATCH false positive on verdict-heavy rounds`
- `a8a33c2 feat: make Bugzilla paradigm explicit to the panel`
- `b2f3444 fix: parse_admissibility_block — FINDING_ID terminator regression`
- `9891bda fix: Stage 6 calibrator int-flaw_class crash + regression tests`
- `26b28f8 fix: gamma input — use post-reconciliation novelty, not pre-`
