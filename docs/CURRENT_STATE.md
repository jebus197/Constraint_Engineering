# CDSFL Current State

Generated: 16 May 2026 23:45 BST (2026-05-16T23:45:00+01:00)

---

## Git

- **Branch:** exp39-experimental
- **Last commit:** `654a4c8` exp40: add --config to launch_exp40 (enables plan-F slice run)
- **Committed:** 2026-05-16 23:39:26 +0100
- **Remote:** ahead by 111
- **Working tree:** DIRTY — uncommitted changes present

Uncommitted files:
- `M experimental_notes/CDSFL_Agent_Operational_Plan.md`
- `M resources/ONBOARDING.md`
- `M resources/RECOVERY.md`
- `?? bench/logs/exp40_slice_20260516T223952Z.log`
- `?? bench/logs/exp40_slice_admissibility_20260516T223952Z/`
- `?? experimental_notes/Exp40_Remediation_Build_E_to_F_2026-05-16.md`
- `?? experimental_notes/Exp40_Remediation_Build_E_to_F_Plain_English_2026-05-16.md`
- `?? experimental_notes/Exp40_RootCause_Remediation_Plan_2026-05-16.md`
- `?? experimental_notes/Exp40_RootCause_Remediation_Plan_Plain_English_2026-05-16.md`

---

## Tests

**1440 tests collected** (`python3 -m pytest bench/tests/ --co -q`)

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

- `654a4c8 exp40: add --config to launch_exp40 (enables plan-F slice run)`
- `42da873 exp40 plan-D: decomposition slice + plan-F config`
- `58a4efa exp40 plan-C: apply verified fixes back to a per-run working copy (the structural cure)`
- `c2dd4ef exp40 plan-B: in-round re-ask (dispatch-phase, bounded, idempotent)`
- `6e63169 exp40 plan-A: fix the silent finding-ID collision-overwrite (real fix, not gated)`
- `6838e58 exp40 plan-E: collate all past Exp 40 CLOSED fixes; build test-gated cleaned baseline`
- `096c697 sv: Exp 40 COMPLETE — R24-R28 clean convergence test (G7 ON) FALSIFIES the mechanical-blocker hypothesis for this target: G7 cleared all deadlocks (C0023 21-round record resolved 5/5, zero cycles) yet γ stayed flat ≈0.05 (vs 0.048 G7-off); full γ peaked 0.2967@R3 then diverged to a 0.05 plateau for 25 rounds. Convergence real in general (Exp 37) but target-specific divergence here; candidate = novelty-regen/γ-gate mis-calibration. Bounded exactly R24-R28 (overrun corrective confirmed). Paired post-mortem v1.2; guard FFAFP'd 3x (monitor-side only, redesigned to not auto-freeze healthy runs); ONBOARDING/RECOVERY/tracker updated`
- `c304032 exp40: enable G7 + bound R24-R28 for founder-directed clean convergence test`
- `3152f6e sv: Exp 40 R17-R23 resume complete (7 rounds, clean stop) — full fix tranche validated in production (16 reasoning recoveries, Fix-1c windowing fired correctly 3/3→6r, 0 collisions → UUID-namespace deferral evidence-justified); paired R17-R23 post-mortem; extension_cap round-count deviation + modified-target confound documented; Exp 41 actions evidence-backed`
- `626f5e4 sv: neutral timing re-confer (no presupposed answer) — G7 enablement DEFER to Exp 41 (reverses CC1), UUID-namespace DEFER+collision-detector-evidence-gate, in-round dispatch DEFER; observation-only collision detector implemented (10 tests); canonical plan §6c binding timing decisions + Exp 41 actions; 210 tests pass; paired confer notes`
