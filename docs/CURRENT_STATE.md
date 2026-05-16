# CDSFL Current State

Generated: 16 May 2026 05:49 BST (2026-05-16T05:49:37+01:00)

---

## Git

- **Branch:** exp39-experimental
- **Last commit:** `626f5e4` sv: neutral timing re-confer (no presupposed answer) — G7 enablement DEFER to Exp 41 (reverses CC1), UUID-namespace DEFER+collision-detector-evidence-gate, in-round dispatch DEFER; observation-only collision detector implemented (10 tests); canonical plan §6c binding timing decisions + Exp 41 actions; 210 tests pass; paired confer notes
- **Committed:** 2026-05-16 03:31:35 +0100
- **Remote:** ahead by 102
- **Working tree:** DIRTY — uncommitted changes present

Uncommitted files:
- `M bench/exp40_configs/40_gate.json`
- `M bench/fingerprints/CC2.json`
- `M bench/fingerprints/ChatGPT.json`
- `M bench/fingerprints/Codex.json`
- `M bench/fingerprints/DeepSeek.json`
- `M bench/fingerprints/Gemini.json`
- `M bench/logs/exp40_gate_20260514T020550Z/checkpoint.json`
- `M bench/logs/exp40_gate_20260514T020550Z/completion_signal.json`
- `M bench/logs/exp40_gate_20260514T020550Z/exp40_gate_report.json`
- `M bench/logs/exp40_gate_20260514T020550Z/runner_state.json`
- `M bench/logs/exp40_gate_20260514T020550Z/stage6_calibration_summary.json`
- `M bench/logs/immune_pipeline.log`
- `M experimental_notes/CDSFL_Agent_Operational_Plan.md`
- `?? bench/logs/exp40_R17R21_20260516T023253Z.log`
- `?? bench/logs/exp40_gate_20260514T020550Z/macrophage_shadow_r17.json`

---

## Tests

**1414 tests collected** (`python3 -m pytest bench/tests/ --co -q`)

---

## Latest Experiment

- **Experiment:** exp40_gate (#40)
- **Status:** CONVERGED
- **Topology:** star
- **Target:** `bench/dm/_feedback.py`
- **Rounds:** 24
- **Total findings:** 370
- **Gamma:** 0.0477
- **Models:** CC2, ChatGPT, Codex, DeepSeek, Gemini
- **Per model:**
  - Gemini: 140
  - DeepSeek: 100
  - ChatGPT: 54
  - CC2: 46
  - Codex: 30
- **Logs:** `/Users/georgejackson/Developer_Projects/Constraint_Engineering/bench/logs/exp40_gate_20260514T020550Z`

---

## Recent Commits

- `626f5e4 sv: neutral timing re-confer (no presupposed answer) — G7 enablement DEFER to Exp 41 (reverses CC1), UUID-namespace DEFER+collision-detector-evidence-gate, in-round dispatch DEFER; observation-only collision detector implemented (10 tests); canonical plan §6c binding timing decisions + Exp 41 actions; 210 tests pass; paired confer notes`
- `9071025 sv-followup: tracker HEAD -> b13dd6d (confer-closed terminal state)`
- `b13dd6d sv: live 5-model architectural confer CLOSED — 5/5 unanimous YES (resume R17-R21 G7-disabled + enable G7 at Exp 41 as designed, no blockers); confer script + logs + paired outcome notes; ONBOARDING/RECOVERY/tracker updated`
- `553d41d sv-followup: operational tracker HEAD 3bbf2c7->7ecbf26 post-sv`
- `7ecbf26 sv: Exp 40 continuation + post-continuation fix tranche (1a-1e parser/classifier/RT-v2/ITC/reformat), G7 merge-arbitration module (default-disabled), DeepSeek Phase-1 reasoning_content fix, gamma-input triple-cross-verification, codex false-positive resolution; 229 tests pass; paired post-mortems`
- `3bbf2c7 feat: launcher_core shared infrastructure + G7 merge-deadlock design`
- `7f3066b fix: ITC CAPABILITY_MISMATCH false positive on verdict-heavy rounds`
- `a8a33c2 feat: make Bugzilla paradigm explicit to the panel`
- `b2f3444 fix: parse_admissibility_block — FINDING_ID terminator regression`
- `9891bda fix: Stage 6 calibrator int-flaw_class crash + regression tests`
