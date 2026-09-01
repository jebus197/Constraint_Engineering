# Experiment run ledger — derived from the artefacts, never typed

**DERIVED.** Every figure below is read from `bench/logs/*/` at generation time by
`scripts/experiment_run_ledger.py`. Nothing here is transcribed by hand, because the
counts this replaces were transcribed by hand and drifted.

## The order is already correct

Sorted by start time, the experiment number is **monotonic** across
all 44 non-empty run directories — **0 violations**. A renumber by run order
would change nothing. What is actually wrong is stated in the two sections after the table.

## Every run, in the order it started

| # | started | exp | run name | rounds | signal | report says |
|---:|---|---:|---|---:|---|---|
| 1 | 2026-04-04 19:31 | 29 | `persistence` | 9 | CONVERGED | `converged_at=8` — kappa_converged(0.960) |
| 2 | 2026-04-04 23:51 | 30 | `endocrine` | 15 | CONVERGED | `converged_at=14` — max_rounds_reached(15) |
| 3 | 2026-04-05 04:17 | 31 | `postfix` | 15 | BUDGET_EXHAUSTED | `converged_at=14` — BUDGET_EXHAUSTED(15) |
| 4 | 2026-04-05 08:56 | 32 | `meta` | 10 | BUDGET_EXHAUSTED | `converged_at=9` — BUDGET_EXHAUSTED(10) |
| 5 | 2026-04-05 10:50 | 33 | `endocrine` | 1 | — | — |
| 6 | 2026-04-05 11:03 | 33 | `endocrine` | 24 | INCOMPLETE | — |
| 7 | 2026-04-05 22:16 | 34 | `endocrine` | 5 | — | — |
| 8 | 2026-04-05 22:50 | 34 | `endocrine` | 0 | — | — |
| 9 | 2026-04-05 22:52 | 34 | `endocrine` | 24 | INCOMPLETE | — |
| 10 | 2026-04-06 15:21 | 35 | `pe` | 23 | INCOMPLETE | `converged_at=22` — EXTENSION_STALLED |
| 11 | 2026-04-07 00:49 | 36 | `evidence` | 46 | INCOMPLETE | `converged_at=45` — STATE_CONVERGED at round 45 (2 consecutive passes): All… |
| 12 | 2026-04-09 05:09 | 37 | `evidence` | 16 | INCOMPLETE | `converged_at=15` — STATE_CONVERGED at round 15 (2 consecutive passes): All… |
| 13 | 2026-04-10 10:44 | 38 | `ouroboros` | 1 | — | — |
| 14 | 2026-04-10 12:20 | 38 | `ouroboros` | 1 | — | — |
| 15 | 2026-04-11 04:19 | 38 | `ouroboros` | 24 | INCOMPLETE | — |
| 16 | 2026-04-13 05:13 | 39 | `0_gate` | 1 | — | — |
| 17 | 2026-04-13 05:46 | 39 | `0_gate` | 4 | INCOMPLETE | — |
| 18 | 2026-04-13 19:32 | 39 | `0_gate` | 0 | — | — |
| 19 | 2026-04-13 19:33 | 39 | `0_gate` | 6 | INCOMPLETE | — |
| 20 | 2026-05-14 02:05 | 40 | `gate` | 29 | INCOMPLETE | — |
| 21 | 2026-05-16 22:39 | 40 | `slice_admissibility` | 8 | INCOMPLETE | `converged_at=7` — GAMMA_ALT_CONVERGED: gamma=0.305 >= 0.3 at round 7 |
| 22 | 2026-05-18 13:07 | 40 | `slice_collision` | 4 | INCOMPLETE | `converged_at=3` — HARDENED_CONVERGED (sparsity fallback): cum_critical=4 … |
| 23 | 2026-05-18 16:05 | 40 | `slice_records` | 12 | INCOMPLETE | — |
| 24 | 2026-05-18 19:01 | 40 | `slice_admissibility_hardened` | 12 | INCOMPLETE | — |
| 25 | 2026-05-22 02:10 | 41 | `convergence` | 12 | INCOMPLETE | — |
| 26 | 2026-06-02 23:00 | 42 | `composer` | 1 | — | — |
| 27 | 2026-06-03 11:06 | 42 | `composer` | 1 | — | — |
| 28 | 2026-06-06 18:49 | 42 | `composer_confirm` | 2 | INCOMPLETE | — |
| 29 | 2026-06-06 20:20 | 42 | `composer` | 12 | INCOMPLETE | — |
| 30 | 2026-06-07 15:47 | 42 | `composer_takeupslack` | 16 | INCOMPLETE | — |
| 31 | 2026-06-09 16:51 | 42 | `composer_locationkey_live` | 5 | — | — |
| 32 | 2026-06-09 18:36 | 42 | `composer_locationkey_live` | 7 | CONVERGED | `converged_at=6` — CRITICAL_QUIESCENCE_CONVERGED: 3 consecutive rounds wit… |
| 33 | 2026-07-18 21:28 | 43 | `macrophage_locationkey_live` | 6 | — | — |
| 34 | 2026-07-19 01:43 | 43 | `macrophage_locationkey_live` | 14 | INCOMPLETE | — |
| 35 | 2026-07-27 00:27 | 44 | `evidence_locationkey_live` | 13 | CONVERGED | `converged_at=12` — STATE_CONVERGED at round 12 (3 consecutive passes): All… |
| 36 | 2026-07-27 22:56 | 45 | `memory_statistics_live` | 4 | CONVERGED | `converged_at=3` — CRITICAL_QUIESCENCE_CONVERGED (two-sided gate): gamma_c… |
| 37 | 2026-07-28 10:31 | 46 | `stage6_locationkey_live` | 6 | CONVERGED | `converged_at=5` — CRITICAL_QUIESCENCE_CONVERGED (two-sided gate): gamma_c… |
| 38 | 2026-07-28 23:00 | 47 | `divergence_locationkey_live` | 14 | CONVERGED | `converged_at=13` — CRITICAL_QUIESCENCE_CONVERGED (two-sided gate): gamma_c… |
| 39 | 2026-07-29 04:41 | 48 | `chemistry_exam_live` | 6 | CONVERGED | `converged_at=5` — STATE_CONVERGED at round 5 (3 consecutive passes): All … |
| 40 | 2026-07-29 06:23 | 49 | `engineering_exam_live` | 7 | CONVERGED | `converged_at=6` — STATE_CONVERGED at round 6 (3 consecutive passes): All … |
| 41 | 2026-07-29 22:24 | 53 | `control_zero_live` | 3 | — | — |
| 42 | 2026-08-01 00:56 | 53 | `control_zero_live` | 4 | — | — |
| 43 | 2026-08-23 14:46 | 55 | `v3_control` | 1 | INCOMPLETE | HALTED_IRREDUCIBLE_QUEUE_ALARM |
| 44 | 2026-08-23 15:39 | 55 | `v3_control` | 1 | INCOMPLETE | HALTED_IRREDUCIBLE_QUEUE_ALARM |

**12 aborted invocations** wrote an empty directory and are excluded above: exp32 2026-04-05 08:53, exp34 2026-04-05 22:15, exp35 2026-04-06 15:20, exp36 2026-04-08 07:21, exp37 2026-04-09 03:03, exp37 2026-04-09 03:04, exp38 2026-04-10 12:19, exp40 2026-05-14 02:00, exp42 2026-06-03 09:57, exp36 2026-08-07 04:32, exp35 2026-08-07 04:32, exp36 2026-08-07 05:31.

## Hole 1 — numbers that never ran

Experiments with a run directory: **[29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 53, 55]**.

Numbers inside that span with **no run directory at all**: **[50, 51, 52, 54]** (4 of 27).

Of those, **[50, 51, 52]** have a config and were never launched, and **[54]** has no config either — planned in prose only.

A reader counting the span `exp29`–`exp55` infers 27 experiments. **23 numbers produced a directory** and **22 produced a report**. The gap is not a numbering error; it is 4 numbers that were planned and never executed.

## Hole 2 — status is recorded twice and the two disagree

`completion_signal.json` carries a status and a reason. **20 of 31 signals carry an EMPTY reason.**

In **7** of those the run report DOES name an outcome, so the two artefacts
disagree and a tool reading only the signal draws the wrong conclusion:

| exp | started | signal | but the report says |
|---:|---|---|---|
| 35 | 2026-04-06 15:21 | INCOMPLETE (reason empty) | EXTENSION_STALLED |
| 36 | 2026-04-07 00:49 | INCOMPLETE (reason empty) | STATE_CONVERGED at round 45 (2 consecutive passes): All conditions met: open_ch= |
| 37 | 2026-04-09 05:09 | INCOMPLETE (reason empty) | STATE_CONVERGED at round 15 (2 consecutive passes): All conditions met: open_ch= |
| 40 | 2026-05-16 22:39 | INCOMPLETE (reason empty) | GAMMA_ALT_CONVERGED: gamma=0.305 >= 0.3 at round 7 |
| 40 | 2026-05-18 13:07 | INCOMPLETE (reason empty) | HARDENED_CONVERGED (sparsity fallback): cum_critical=4 < 8; γ_crit=1.000 reporte |
| 55 | 2026-08-23 14:46 | INCOMPLETE (reason empty) | HALTED_IRREDUCIBLE_QUEUE_ALARM |
| 55 | 2026-08-23 15:39 | INCOMPLETE (reason empty) | HALTED_IRREDUCIBLE_QUEUE_ALARM |

The runner's own source names this at `bench/reference_runner_v3.py:12275` and dates a
partial fix to 2026-05-18: *"the hardened / gamma-alt gate previously set only the result
dict, so post-mortem tooling read every hardened convergence as INCOMPLETE."* Runs after
that date still show it, so the fix did not close the class.

Regenerate with `python3 scripts/experiment_run_ledger.py > experimental_notes/EXPERIMENT_RUN_LEDGER.md`.
`--check` fails if the committed copy no longer matches the artefacts.

Written under CDSFL note standard v1.6 (24 August 2026).
