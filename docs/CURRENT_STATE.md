# CDSFL Current State

Generated: 23 May 2026 01:39 BST (2026-05-23T01:39:33+01:00)

---

## Git

- **Branch:** exp39-experimental
- **Last commit:** `4b97be0` fix: restore gamma as load-bearing convergence trigger (not demoted)
- **Committed:** 2026-05-22 20:48:07 +0100
- **Remote:** ahead by 128
- **Working tree:** DIRTY — uncommitted changes present

Uncommitted files:
- `M bench/exp41_configs/41_convergence.json`
- `M bench/fingerprints/CC2.json`
- `M bench/fingerprints/ChatGPT.json`
- `M bench/fingerprints/Codex.json`
- `M bench/fingerprints/DeepSeek.json`
- `M bench/fingerprints/Gemini.json`
- `M bench/logs/exp40_slice_admissibility_20260516T223952Z/checkpoint.json`
- `M bench/logs/exp40_slice_admissibility_20260516T223952Z/completion_signal.json`
- `M bench/logs/exp40_slice_admissibility_20260516T223952Z/stage6_calibration_summary.json`
- `M bench/logs/exp40_slice_admissibility_20260516T223952Z/working/_feedback_slice.py`
- `M bench/logs/immune_pipeline.log`
- `M experimental_notes/CDSFL_Agent_Operational_Plan.md`
- `M resources/ONBOARDING.md`
- `M resources/RECOVERY.md`
- `M scripts/cdsfl_sv.py`

---

## Tests

**1510 tests collected** (`python3 -m pytest bench/tests/ --co -q`)

---

## Latest Experiment

- **Experiment:** exp41_convergence (#41)
- **Status:** INCOMPLETE
- **Topology:** star
- **Target:** `bench/dm/_convergence.py`
- **Rounds:** 12
- **Total findings:** 115
- **Gamma:** 0.0000
- **Models:** CC2, ChatGPT, Codex, DeepSeek, Gemini
- **Per model:**
  - Gemini: 54
  - DeepSeek: 24
  - ChatGPT: 15
  - CC2: 12
  - Codex: 10
- **Logs:** `/Users/georgejackson/Developer_Projects/Constraint_Engineering/bench/logs/exp41_convergence_20260522T021030Z`

---

## Recent Commits

- `4b97be0 fix: restore gamma as load-bearing convergence trigger (not demoted)`
- `86587f4 Step 3: first-principles runner gate (gamma diagnostic; genuine novelty)`
- `0901fd5 convergence-detector fixes + 5-model confer verification (founder-directed)`
- `9117eb6 exp41 setup: static target + compelled convergence + Exp 40 fix harvest`
- `e0272c6 primary/secondary route fallback architecture: every model, no benching`
- `86470a5 remove reconstruction bypasses + route DeepSeek direct (founder-directed)`
- `86234b3 exp40 hardened-gate campaign: synthesis + paired notes (3-unit complete)`
- `5fe9101 exp40 Unit B->C seam: 3 runner-class verification-integrity fixes`
- `a302a2a exp40 plan-D faithful decomposition: Units B + C slices + hardened configs`
- `ffc88fe exp40 gate-hardening: F6 pre-reg + F4 settled-registry + conjunction gate`
