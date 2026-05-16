# CDSFL Current State

Generated: 16 May 2026 19:38 BST (2026-05-16T19:38:55+01:00)

---

## Git

- **Branch:** exp39-experimental
- **Last commit:** `c304032` exp40: enable G7 + bound R24-R28 for founder-directed clean convergence test
- **Committed:** 2026-05-16 17:56:09 +0100
- **Remote:** ahead by 104
- **Working tree:** DIRTY — uncommitted changes present

Uncommitted files:
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
- `M resources/ONBOARDING.md`
- `M resources/RECOVERY.md`
- `?? bench/logs/exp40_R24R28_20260516T165641Z.log`

---

## Tests

**1414 tests collected** (`python3 -m pytest bench/tests/ --co -q`)

---

## Latest Experiment

- **Experiment:** exp40_gate (#40)
- **Status:** INCOMPLETE
- **Topology:** star
- **Target:** `bench/dm/_feedback.py`
- **Rounds:** 29
- **Total findings:** 417
- **Gamma:** 0.0507
- **Models:** CC2, ChatGPT, Codex, DeepSeek, Gemini
- **Per model:**
  - Gemini: 153
  - DeepSeek: 116
  - ChatGPT: 60
  - CC2: 50
  - Codex: 38
- **Logs:** `/Users/georgejackson/Developer_Projects/Constraint_Engineering/bench/logs/exp40_gate_20260514T020550Z`

---

## Recent Commits

- `c304032 exp40: enable G7 + bound R24-R28 for founder-directed clean convergence test`
- `3152f6e sv: Exp 40 R17-R23 resume complete (7 rounds, clean stop) — full fix tranche validated in production (16 reasoning recoveries, Fix-1c windowing fired correctly 3/3→6r, 0 collisions → UUID-namespace deferral evidence-justified); paired R17-R23 post-mortem; extension_cap round-count deviation + modified-target confound documented; Exp 41 actions evidence-backed`
- `626f5e4 sv: neutral timing re-confer (no presupposed answer) — G7 enablement DEFER to Exp 41 (reverses CC1), UUID-namespace DEFER+collision-detector-evidence-gate, in-round dispatch DEFER; observation-only collision detector implemented (10 tests); canonical plan §6c binding timing decisions + Exp 41 actions; 210 tests pass; paired confer notes`
- `9071025 sv-followup: tracker HEAD -> b13dd6d (confer-closed terminal state)`
- `b13dd6d sv: live 5-model architectural confer CLOSED — 5/5 unanimous YES (resume R17-R21 G7-disabled + enable G7 at Exp 41 as designed, no blockers); confer script + logs + paired outcome notes; ONBOARDING/RECOVERY/tracker updated`
- `553d41d sv-followup: operational tracker HEAD 3bbf2c7->7ecbf26 post-sv`
- `7ecbf26 sv: Exp 40 continuation + post-continuation fix tranche (1a-1e parser/classifier/RT-v2/ITC/reformat), G7 merge-arbitration module (default-disabled), DeepSeek Phase-1 reasoning_content fix, gamma-input triple-cross-verification, codex false-positive resolution; 229 tests pass; paired post-mortems`
- `3bbf2c7 feat: launcher_core shared infrastructure + G7 merge-deadlock design`
- `7f3066b fix: ITC CAPABILITY_MISMATCH false positive on verdict-heavy rounds`
- `a8a33c2 feat: make Bugzilla paradigm explicit to the panel`
