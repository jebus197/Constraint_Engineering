# Anti-cooking condition (b) — reachability artefact

**2026-09-05.** This is the recalibration artefact whose absence has been recorded as an open integrity condition since **2026-05-17 — 111 days**.

## The condition, verbatim

From `experimental_notes/Exp41_Convergence_Investigation_2026-05-22.md`:

> "(b) thresholds recalibrated on held-out corpus or null-distribution, allowed to fail. `bench/exp40_baseline/` contains the F6 critical-definition pre-registration but **no recalibration artefact**. The 0.30 threshold was *frozen/pre-registered* (anti-cooking) but **never validated as reachable**. Completing this is integrity-restoring, not bar-lowering."

## Why it mattered

Freezing a threshold in advance is correct practice — it stops the bar being moved to fit the result. But **a frozen bar nobody can clear is not a conservative choice, it is a broken instrument**, and the two are indistinguishable without measuring. Nobody had measured. `gamma_alt_threshold = 0.30` has gated convergence on every run since.

## Result — MEASURED, 2026-09-05

Reproduce with `python3 scripts/recalibrate_gamma_threshold_reachability.py`.

| Population | Reached 0.30 | Rate | Wilson 95% |
|---|---|---|---|
| **LIVE runs** | **10 of 13** | 76.9% | [49.7%, 91.8%] |
| LIVE, excluding runs halted before a series could form | **10 of 11** | 90.9% | [62.3%, 98.4%] |
| SIMULATED (reported separately, **never pooled**) | 7 of 11 | 63.6% | [35.4%, 84.8%] |

**Verdict on the reachability half of condition (b): REACHABLE.** The threshold is not a bar nobody clears. Live peaks among runs that reached it span **0.3357 to 0.8847**.

The 3 live runs that did not reach it are informative rather than contrary:

| Peak | Rounds | Run | Note |
|---|---|---|---|
| 0.0000 | 1 | `exp55_v3_control_20260823T144624Z` | `HALTED_IRREDUCIBLE_QUEUE_ALARM` at round 0 |
| 0.0000 | 1 | `exp55_v3_control_20260823T153955Z` | same |
| 0.0000 | 2 | `exp42_composer_confirm_20260606T184941Z` | 2 rounds, retained in the headline figure |

A run stopped at round 1 has no opportunity to develop a gamma series, so counting it as a failure to reach the threshold measures **the halt, not the threshold**. Both figures are given; neither is substituted for the other.

## What this does NOT establish

Condition (b) offers two routes — a **held-out corpus** or a **null distribution** — and this is neither. It is a post-hoc reachability check on runs that already happened, which is strictly weaker: it can say the bar is not unreachable; it **cannot** say it is well calibrated. Discharging (b) fully still requires one of the two named routes.

The "allowed to fail" clause is honoured in the only way that means anything: the answer was not known before the script ran, and the script reports whatever it finds.

## Two defects found while producing this

1. **A first pass pooled simulated with live runs** and reported 17 of 24. The 5 highest peaks were all `sim45_*` at or near 1.0000. Pooling them would have leaned a reachability claim on simulated data — the provenance failure this project has a standing rule against. They are now separated and never pooled.
2. **The early-halt exclusion was silently vacuous.** It read `closed_by` / `close_reason`; archived reports carry `halted`, `halted_at_round` and `convergence_reason`. The guard matched nothing while printing a figure identical to the headline, *as though it had excluded something*. Fixed; the exclusion now moves the figure from 10 of 13 to 10 of 11.

Written under CDSFL note standard v1.7 (26 August 2026).
