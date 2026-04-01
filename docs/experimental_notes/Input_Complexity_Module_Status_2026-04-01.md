# Input Complexity Module — Status

**Date:** 1 April 2026, 10:29 UTC
**Status:** TEST ARTICLE — not wired into dispatch. Observation-only.
**Files:** `bench/input_complexity.py`, `bench/tests/test_input_complexity.py`
**Tests:** 36/36 passing (387/387 full suite)

## What It Is

Implementation of the γ_input / amplification factor / compound objective
hypothesis. Computes Heaps' law vocabulary growth on input text and output
findings, derives amplification A = β_output/β_input, and recommends
dispatch strategy via a 2D/3D routing table.

All mathematical claims SymPy-verified (8/8). One FFF cycle applied
post-implementation (5 findings, 5 fixes, all tested).

## What It Is NOT

- **Not wired into any runner.** No dispatch decisions are influenced by
  this module. It exists purely as a testable, reviewable artefact.
- **Not validated against real data.** The tests use synthetic text.
  Real-world validation requires wiring as observation-only logging in a
  live run, then comparing recommendations against actual outcomes.

## Pending Decisions (Founder)

1. **Wire as observation-only logging** in baseline runner? (Log γ_input
   and dispatch recommendation alongside actual dispatch, change nothing.)
2. **Wire as active dispatch** in a future run? (Let γ_input influence
   routing decisions.)
3. **Submit to CDSFL model review?** (Package for 5-model confer as a
   code review target.)

## FFF Findings Applied

| # | Finding | Fix |
|---|---------|-----|
| 1 | R² computed with unclamped β, returned with clamped β | Recompute R² and K after clamping |
| 2 | `compute_gamma_output` accepted 2 findings (degenerate OLS) | Minimum raised to MIN_WINDOWS (3) |
| 3 | No R² quality gate on dispatch routing | Added `r_squared` param; bad fit → assume complex |
| 4 | Docstring usage example wrong (tuple vs HeapsResult) | Corrected |
| 5 | Window size parameter ambiguous (chars vs tokens) | Renamed to WINDOW_SIZE_CHARS, documented conversion |

## Key Mathematical Results (SymPy-Verified)

- Compound objective: `obj = (β_out/β_in) × (1 − β_out)`
- Optimal β_output: `β_out* = 0.5` (half-converged)
- Maximum objective: `obj* = 1/(4·β_in)`
- Occam emergence: simpler input → higher compound (mathematical consequence, not external constraint)
