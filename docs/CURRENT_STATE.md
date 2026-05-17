# CDSFL Current State

Generated: 17 May 2026 01:22 BST (2026-05-17T01:22:17+01:00)

---

## Git

- **Branch:** exp39-experimental
- **Last commit:** `111a098` sv: Exp 40 remediation build E->F complete (autonomous 'just do it all'). Root cause (sandbox-only fix application -> re-injection non-convergence) fixed: E collate+cleaned-baseline (C0001 CLOSED!=correct finding), A collision-overwrite fix, B in-round re-ask, C apply-fixes-back (full-suite gated), D slice+config, launcher --config; F decomposed convergence re-run LAUNCHED under live FFAFP guard. Paired build post-mortem; ONBOARDING/RECOVERY/tracker updated; morning-review pointers set
- **Committed:** 2026-05-16 23:45:00 +0100
- **Remote:** ahead by 112
- **Working tree:** DIRTY — uncommitted changes present

Uncommitted files:
- `M bench/fingerprints/CC2.json`
- `M bench/fingerprints/ChatGPT.json`
- `M bench/fingerprints/Codex.json`
- `M bench/fingerprints/DeepSeek.json`
- `M bench/fingerprints/Gemini.json`
- `M bench/logs/exp40_slice_20260516T223952Z.log`
- `M bench/logs/exp40_slice_admissibility_20260516T223952Z/working/_feedback_slice.py`
- `M bench/logs/immune_pipeline.log`
- `M experimental_notes/CDSFL_Agent_Operational_Plan.md`
- `M resources/ONBOARDING.md`
- `M resources/RECOVERY.md`
- `?? bench/logs/exp40_slice_admissibility_20260516T223952Z/checkpoint.json`
- `?? bench/logs/exp40_slice_admissibility_20260516T223952Z/completion_signal.json`
- `?? bench/logs/exp40_slice_admissibility_20260516T223952Z/exp40_slice_admissibility_report.json`
- `?? bench/logs/exp40_slice_admissibility_20260516T223952Z/macrophage_shadow_r00.json`

---

## Tests

**1440 tests collected** (`python3 -m pytest bench/tests/ --co -q`)

---

## Latest Experiment

- **Experiment:** exp40_slice_admissibility (#40)
- **Status:** CONVERGED
- **Topology:** star
- **Target:** `bench/logs/exp40_slice_admissibility_20260516T223952Z/working/_feedback_slice.py`
- **Rounds:** 7
- **Total findings:** 58
- **Gamma:** 0.2670
- **Models:** CC2, ChatGPT, Codex, DeepSeek, Gemini
- **Per model:**
  - DeepSeek: 19
  - Gemini: 13
  - Codex: 10
  - CC2: 9
  - ChatGPT: 7
- **Logs:** `/Users/georgejackson/Developer_Projects/Constraint_Engineering/bench/logs/exp40_slice_admissibility_20260516T223952Z`

---

## Recent Commits

- `111a098 sv: Exp 40 remediation build E->F complete (autonomous 'just do it all'). Root cause (sandbox-only fix application -> re-injection non-convergence) fixed: E collate+cleaned-baseline (C0001 CLOSED!=correct finding), A collision-overwrite fix, B in-round re-ask, C apply-fixes-back (full-suite gated), D slice+config, launcher --config; F decomposed convergence re-run LAUNCHED under live FFAFP guard. Paired build post-mortem; ONBOARDING/RECOVERY/tracker updated; morning-review pointers set`
- `654a4c8 exp40: add --config to launch_exp40 (enables plan-F slice run)`
- `42da873 exp40 plan-D: decomposition slice + plan-F config`
- `58a4efa exp40 plan-C: apply verified fixes back to a per-run working copy (the structural cure)`
- `c2dd4ef exp40 plan-B: in-round re-ask (dispatch-phase, bounded, idempotent)`
- `6e63169 exp40 plan-A: fix the silent finding-ID collision-overwrite (real fix, not gated)`
- `6838e58 exp40 plan-E: collate all past Exp 40 CLOSED fixes; build test-gated cleaned baseline`
- `096c697 sv: Exp 40 COMPLETE — R24-R28 clean convergence test (G7 ON) FALSIFIES the mechanical-blocker hypothesis for this target: G7 cleared all deadlocks (C0023 21-round record resolved 5/5, zero cycles) yet γ stayed flat ≈0.05 (vs 0.048 G7-off); full γ peaked 0.2967@R3 then diverged to a 0.05 plateau for 25 rounds. Convergence real in general (Exp 37) but target-specific divergence here; candidate = novelty-regen/γ-gate mis-calibration. Bounded exactly R24-R28 (overrun corrective confirmed). Paired post-mortem v1.2; guard FFAFP'd 3x (monitor-side only, redesigned to not auto-freeze healthy runs); ONBOARDING/RECOVERY/tracker updated`
- `c304032 exp40: enable G7 + bound R24-R28 for founder-directed clean convergence test`
- `3152f6e sv: Exp 40 R17-R23 resume complete (7 rounds, clean stop) — full fix tranche validated in production (16 reasoning recoveries, Fix-1c windowing fired correctly 3/3→6r, 0 collisions → UUID-namespace deferral evidence-justified); paired R17-R23 post-mortem; extension_cap round-count deviation + modified-target confound documented; Exp 41 actions evidence-backed`
