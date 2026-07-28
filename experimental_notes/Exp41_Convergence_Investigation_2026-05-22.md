# Experiment 41 — Convergence Investigation (technical)

2026-05-22 (BST). Constraint Engineering / CDSFL.

## Summary of the claim

Experiment 41 (target: `bench/dm/_convergence.py`, 438 lines, static; 12 rounds, hardened gate enabled) terminated **NOT CONVERGED** at the wall-clock cap. The non-convergence is not a one-off: convergence has been effectively unreachable since the γ-based experiment gate replaced the state-based gate at Experiment 40. Root cause is a **panel over-producing low-validity "critical" findings at a steady rate**, feeding a **rate-based gate (γ_crit ≥ 0.30) whose pass mark was never recalibrated/validated** (a confer legitimacy condition that was specified and skipped). γ_crit ≥ 0.30 is reachable in principle; it requires discovery to decelerate, which over-production prevents.

## Convergence history (by record, not memory)

| Experiment | Date | Converged? | Mechanism |
|---|---|---|---|
| exp29_persistence | 2026-04-04 | yes (R8) | `kappa_converged(0.960)` — state/count |
| exp36_evidence | 2026-04-08 | yes (R45) | `STATE_CONVERGED` (2 consecutive passes, all conditions) |
| exp37_evidence | 2026-04-09 | yes (R15) | `STATE_CONVERGED` |
| exp38 / exp39 | 2026-04 | **no record found** | runner v1 (`reference_runner.py`), pre-γ-alt |
| exp40_slice_admissibility | 2026-05-18 | "yes" (R7) γ-alt | `GAMMA_ALT_CONVERGED gamma=0.305` — **live-γ artefact**; settled γ=0.231 (the 0.305-vs-0.231 flip the F4 fix targeted) |
| exp40_slice_collision (Unit B) | 2026-05-18 | yes (R3) | `HARDENED_CONVERGED (sparsity fallback)` cum_critical=4<8; γ_crit=1.000 reported-not-gated |
| exp41_convergence | 2026-05-22 | **no** | hardened gate; γ_crit pinned 0.0 |

**Last genuine natural convergence: Exp 36/37 (state-based).** No Exp 38/39 convergence record exists. The founder's recollection of "Exp 39" is close in spirit (pre-γ-gate era) but the confirmed last natural convergences are 36/37.

## The mechanism shift

- **γ-alt gate introduced:** commit `834e65c` (2026-04-17), "runner v2 — γ-alt convergence". This is the dividing line; Exp 39 and earlier used runner v1 with no γ gate.
- **Hardening:** commit `ffc88fe` (2026-05-18), "F6 pre-reg + F4 settled-registry + conjunction gate". Default-off; enabled for Exp 40 plan-D units and Exp 41.

## What the hardened gate is

`_check_hardened_convergence` (`bench/reference_runner_v2.py:1437`). Converged iff **all** of:
- (A) `g_crit = _estimate_gamma(crit_s) ≥ θ` (θ=0.30), on the **settled** critical series (`_settled_novelty_series`, :1408 — strips MERGED/DUPLICATE/UNCONFIRMED/REFUTED, severity ≥ `CRITICAL_SEVERITY_THRESHOLD`=0.7);
- (B) sustained over `gamma_crit_sustain_rounds`=2 recomputes AND leave-one-round-out robust within `gamma_crit_loo_tol`=0.05;
- (C) `gamma_alt_consecutive_zero_crit`=3 consecutive settled zero-novel-critical rounds.
- Sparsity fallback: cum_critical < `gamma_crit_min_cumulative`=8 → γ reported-not-gated, closure on (C) alone.

This replaced the legacy **OR** (γ-alt) with a **conjunction**, moved γ from all-novelty to critical-only, and from live to post-reconciliation.

`_estimate_gamma` (`:823`): γ = `max(0, min(1, 1 − β))`, β = OLS log-log slope of cumulative novelty vs round. Flat curve → β=0 → γ=1.0; linear → β=1 → γ=0; super-linear → γ clamped 0.

## Empirical telemetry (from `exp41_convergence_report.json`)

- Settled critical series: `crit_s = [2,1,4,4,5,1,1,1,1,2,2,0]` (sum 24). Cumulative grows ~linearly (2→24 over 12 rounds), **β=1.07 → γ_crit=0.0**.
- All-severity series: `all_s = [2,1,5,5,6,2,3,2,1,10,6,3]` (sum 46), γ_all=0.0.
- `gamma_history = [0,0,0.2488,0.1431,0.037,0,0,0,0,0,0,0]` — peaked **0.2488 at R2**, decayed to 0.
- Per-round hardened telemetry: γ_crit_settled hit 0.0971 at R3, then 0.0 R4–R11 as cum_critical climbed 14→28 (settled recompute 24).

## Reachability (proven with the runner's own `_estimate_gamma`)

| discovery pattern | β | γ_crit | ≥0.30 |
|---|---|---|---|
| REAL Exp 41 (steady ~2/rd) | 1.07 | 0.00 | no |
| front-loaded then stops | 0.29 | 0.71 | yes |
| graceful decay | 0.36 | 0.64 | yes |
| flat after burst | 0.00 | 1.00 | yes |

Same 24 criticals, concentration sweep: ≥~50% in first 3 rounds → γ_crit ≥ 0.30. **The threshold is reachable; the panel's flat discovery rate is incompatible with it.**

## Findings validity (the over-production)

79 registry entries: 45 CONFIRMED, 27 UNCONFIRMED, 6 MERGED, 1 CLOSED. 39 critical-severity (≥0.7). **verified=True: 0 of 79** — no proposed fix passed close-the-loop (failures: unused `import numpy` (ruff F401), SEARCH blocks absent from source, "Cannot ground claim in source AST"). On a bounded 438-line module, 24 critical novel findings at a steady ~2/round with zero verifiable fixes is over-production, not genuine defect discovery. This is the proximate cause of the linear curve.

## Skipped legitimacy condition

The γ-hardening confer (note: *Experiment 40 γ-Hardening Confer Outcome*, 2026-05-17) set four anti-cooking conditions, including **(b) thresholds recalibrated on held-out corpus or null-distribution, allowed to fail.** `bench/exp40_baseline/` contains the F6 critical-definition pre-registration but **no recalibration artefact**. The 0.30 threshold was *frozen/pre-registered* (anti-cooking) but **never validated as reachable**. Completing this is integrity-restoring, not bar-lowering.

## Authorisation record

Confer note status line: *"requires founder approval before implementation."* Commit `ffc88fe` (next day): *"Founder-directed."* The founder has indicated approval was likely a high-level wave-through without the two consequences surfaced: (i) γ kept as strict pass/fail requiring deceleration; (ii) recalibration skipped. Fair characterisation: **confer-recommended and waved through, not silently inserted, but not approved with full sight of consequences.**

## Secondary concerns

- **Empties:** 3, all Gemini via OpenRouter (`google/gemini-3.1-pro-preview`), empty HTTP bodies after 337.7s/241.6s (circuit-breaker HALT) + 1 synthesis 0-char (R10). `secondary_route_usage=[]`, `persistent_empty_flags=[]` — ITC absorbed all; secondary never required. Root-cause OpenRouter→Gemini empty-body stalls at source (candidate: route Gemini direct, or shorten per-call timeout for faster ITC retry).
- **Shadow immune:** B-Cell specialist verifier (z3/mypy) runs shadow-only; already flags most findings UNCERTAIN/REJECTED (e.g. `z3: VERIFIED_FALSE: 226.0 > 1.0`) and one real `mypy` issue (`bench/dm/__init__.py` source-file-found-twice, confirmed 0.85). Macrophage in patrol/shadow. Promotion would filter over-production. Stage-6 calibrator str-on-int bug (Exp 40) did not fire this run.
- **§10 compelled convergence:** present in all 52 model-round files in prose; CC2 declared at R11 *"Two consecutive passes with no new findings above threshold — terminating."* Not structurally captured; gate kept counting.

## Recommendations (to discuss; not applied)

1. **Complete the skipped recalibration** (confer condition b) — determine the threshold a genuinely-finished review scores; allowed to fail.
2. **Promote the shadow B-cell verifier** to filter UNCONFIRMED/false findings before they count toward the critical series.
3. **Capture §10 sufficiency declarations** structurally and feed them to the gate.
4. **Reconsider the gate shape:** combine the state-test's *resolution* requirement (Exp 36/37 worked, but could plateau with open criticals) with the γ-gate's conservatism; keep γ as the diagnostic the module's §9.2 design intends. (Note: the runner gate ≠ the convergence-detector module; my earlier "γ inverted §9.2" framing conflated the two and is retracted.)
5. **Two real bugs regardless:** `bench/dm/__init__.py` double-module mypy error; Gemini/OpenRouter empty-body stalls.

## Cross-references

- *Experiment 40 γ-Hardening Confer Outcome* (2026-05-17) and its plain-English companion.
- *Experiment 40 Definitional Confer Outcome* (2026-05-18).
- *Experiment 40 Hardened Gate Campaign* (2026-05-18).
- Plain-English companion: *Experiment 41 Convergence Investigation — Plain English* (2026-05-22); TTS mirror in the CDSFL TTS folder.
- Report: `bench/logs/exp41_convergence_20260522T021030Z/exp41_convergence_report.json`.

Written under CDSFL note standard v1.2 (14 May 2026).
