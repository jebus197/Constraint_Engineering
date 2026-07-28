# Experiment 40 R24–R28 — Clean Convergence Test (G7 enabled): Post-Mortem

2026-05-16 19:34 BST

## Summary

The R24–R28 leg of Experiment 40 was the first leg run with the merge-deadlock
resolver (internally G7 — a panel-majority arbitration that resolves a finding
stuck in a merge deadlock by a ≥3/5 vote) **enabled**, with the review target
held stable and the round count bounded to exactly five rounds. Its purpose was
to test a specific hypothesis: that the persistent non-convergence of this
experiment is caused by a mechanical blocker (the recurring merge deadlocks),
and that removing that blocker would let the system converge.

**The hypothesis is falsified for this target.** G7 removed the blocker
completely and correctly — it resolved eight to ten deadlocks by proper
majority, including C0023 (a single finding stuck in deadlock for 21 rounds,
the longest in the project's history), cleared 5/5. Convergence still did not
occur. γ (gamma, the depletion estimate whose rise signals convergence) in the
G7-enabled leg was flat at ≈0.047–0.051, statistically indistinguishable from
the preceding G7-disabled R17–R23 leg (≈0.048). The merge deadlocks were not
what was preventing late-round convergence.

A second, sharper observation comes from the full 29-round γ trajectory: γ
**peaked at 0.2967 at Round 3 — within ≈1.1% of the 0.30 convergence
threshold — then declined monotonically and stabilised on a non-converged
plateau ≈0.05 for the remaining twenty-five rounds.** The system reached the
threshold of convergence early and then diverged from it and never returned.

## Run parameters and outcome

- Resume: `python3 bench/launch_exp40.py --resume` from the R23 checkpoint
  (260 canonical entries restored; start_round = 24).
- Config (`bench/exp40_configs/40_gate.json`): `merge_arbitration_enabled=true`
  (G7 ON), `max_rounds=29`, `extension_cap=29` (set equal per the standing
  bounded-resume corrective), `wall_clock_cap_s=28800`. Target
  `bench/dm/_feedback.py` (the §17 feedback-channel module) unmodified this
  leg — the modified-target confound of R17–R23 is therefore absent here.
- Rounds executed: R24, R25, R26, R27, R28 — exactly five. `total_rounds=29`
  (the cumulative R0–R28 count). `budget_extended=true` fired, but because
  `extension_cap == max_rounds == 29` it created no runway: the loop bound
  held at exactly five rounds. **The R17–R23 round-count overrun is fixed.**
- Elapsed 5,533 s (~92 min), far below the 28,800 s wall-clock cap. The stop
  cause was the round-cap, not wall-clock; the runner's "ended without
  convergence (likely wall-clock)" line is its known-inaccurate generic
  non-convergence string (already documented in the R17–R23 post-mortem).
- Outcome: **not converged.** Runner verdict: `Convergence: Gate failed:
  open_ch=12 > max=5, novel=13, gamma=0.051 (hard)`; `γ-alt not met:
  gamma=0.051 < 0.3; novel_crit_recent=[3, 1, 6]`.
- Final registry: 417 total findings; 296 canonical entries
  (UNCONFIRMED 108, CONFIRMED 91, MERGED 53, CLOSED 44); 33 HIL
  (human-in-the-loop) escalation flags.

## The γ trajectory — the central evidence

γ across R0–R28 (gamma rises toward convergence; gate threshold 0.30):

```
R0–R8 :  0.000 0.000 0.256 0.2967 0.2891 0.2838 0.2746 0.2614 0.2321
R9–R16:  0.1433 0.0936 0.0633 0.0446 0.0349 0.0316 0.0310 0.0342
R17–R23: 0.0402 0.0454 0.0485 0.0494 0.0499 0.0498 0.0477
R24–R28: 0.0472 0.0479 0.0488 0.0501 0.0507   (this leg, G7 ON)
```

Two facts:

1. **Early near-convergence then sustained divergence.** Peak γ = 0.2967 at
   R3, ≈1.1% below the 0.30 gate. From R4 onward γ declined every regime and
   settled at a ≈0.05 plateau. The capacity to approach convergence existed
   early; the system moved away from it and did not recover across 25 rounds.

2. **G7 had no convergence effect.** G7-disabled R23 γ = 0.0477; G7-enabled
   R24–R28 γ = 0.0472, 0.0479, 0.0488, 0.0501, 0.0507. The slope is flat and
   the level is unchanged from the G7-off leg. Removing the deadlock blocker
   did not move the convergence metric.

## Falsification analysis

Hypothesis under test (H): late-round non-convergence in Exp 40 is caused by
the recurring merge deadlocks; resolving them (G7 on) yields convergence.

Prediction of H: with G7 on and deadlocks cleared, γ rises toward 0.30 and/or
novel-critical findings fall to three consecutive zero rounds (the γ-alt gate).

Observation: G7 cleared the deadlocks completely (8–10 resolved by ≥3/5
majority; C0023 at 21 rounds resolved 5/5; alias map shows 296 merge/alias
records; 53 entries reached MERGED status; zero G7 cycles — every merged
source-ID appears exactly once). γ remained flat at ≈0.05; novel_crit_recent
ended [3, 1, 6] (never three consecutive zeros); open challenges 12 > max 5.

Conclusion: the prediction fails. **H is falsified for this target.** The
deadlocks were a genuine mechanical defect and G7 is the correct fix for them,
but they were not the cause of the late-round non-convergence. Removing them
was necessary housekeeping, not the convergence lever.

Scope discipline: this is one target (the §17 feedback-channel module) and one
five-round leg. The falsification is of the *simple mechanical-blocker*
explanation for *this target's* late-round plateau. It does not bear on
whether convergence is achievable in general — see next section.

## Convergence is real; this is a target-specific divergence

Convergence has been demonstrated cleanly in the project record. Exp 37
reached STATE_CONVERGED with the convergence gate passing on two consecutive
rounds (R14, R15), 16 rounds, γ final 0.467. Exp 31 converged at the
inter-rater level (κ ≈ 0.619) but a dead-code defect masked detection (the
Exp 32 panel was unanimous on this). Multiple shorter runs converged in 2–7
rounds. The phenomenon is real and instrument-sensitive.

The R24–R28 result is therefore not "convergence is impossible". It is: on
this target, the system approaches the gate early (R3, γ 0.2967) and then
diverges, and that divergence is not the deadlocks.

## Candidate explanation (marked candidate, not established)

[SPECULATIVE] The leading candidate for the late-round plateau is the
novelty-regeneration dynamic and/or mis-calibration of the γ metric and the
convergence gate on this target — not any single mechanical jam. Two
independent pointers support investigating this:

- The Exp 36 mathematical-model audit recorded: "γ classifies wrong at system
  level — reports convergence during churn because it only sees novel rate,
  not raw-to-novel divergence." The early R3 peak at 0.2967 is consistent with
  the metric briefly reading a churn regime as near-convergence, then
  correcting downward as raw-to-novel divergence grew.
- This run's own log raised: `gamma: 0.051 (hard, BLOCKED) — Gamma disagrees
  with state closure — recommend HIL audit`. The runner itself flagged an
  internal inconsistency between γ and state closure.

This is a hypothesis generator, not a finding. It predicts a testable next
step: instrument raw-vs-novel divergence directly and re-examine whether the
gate threshold and the γ definition are appropriate for a rich target where
the panel keeps generating new findings.

## Monitoring record (FFAFP, monitor-side only)

A 60-second guard supervised the run. Three guard iterations were required;
**all three corrections were to the monitoring tool, never to the
experiment**, which ran healthy throughout.

- v2: a convergence regex matched the negative line "γ-alt not met" because
  the alternative `(met|reached)` matched "not met". Fixed with
  source-grounded tokens (`GAMMA_ALT_CONVERGED:` / `STATE_CONVERGED at
  round`) read directly from the runner source.
- v3→v4: a G7 line-count heuristic misread 8 legitimate distinct merges as a
  "merge storm" (it counted two log lines per merge, cumulatively, against a
  per-round cap) and wrongly froze a healthy run via SIGSTOP. The run was
  unfrozen via SIGCONT with no loss (it resumed cleanly and completed). The
  fix was structural, not cosmetic: brittle heuristics no longer take
  autonomous destructive action. v4 freezes the run **only** on unambiguous
  corruption-in-progress (cross-model finding-ID collision, round runaway,
  a genuine G7 merge cycle) and is alert-only on every softer signal, with
  the operator adjudicating the pause.
- The final guard signal was an alert-only PROCESS_DIED at R28: the v4 policy
  correctly took no destructive action on an ambiguous end-of-run string; the
  experiment had completed normally. Minor label imprecision (the completion
  regex did not anticipate "29 ROUNDS COMPLETE / ended without convergence"),
  zero impact on the run.

The experiment was never paused for an experiment fault; the brief wrongful
freeze cost no rounds and no wall-clock of consequence.

## Where things stand and path forward

- Exp 40 is complete (R0–R28). The five-round G7-on test the leg was built
  for is done and its result is recorded here as the headline: the
  mechanical-blocker hypothesis is falsified for this target.
- G7 is validated in production (correct ≥3/5 arbitration, the 21-round
  C0023 deadlock resolved, zero cycles). It remains a correct fix for the
  deadlock defect and is sound to keep enabled.
- The open question moves: late-round non-convergence on this target is a
  novelty-regeneration / metric-calibration question, not a deadlock
  question. Recommended next step: a targeted study instrumenting
  raw-vs-novel divergence and re-examining the γ definition and gate
  threshold against a rich target, before any further single-mechanism fix.
- The bounded-resume corrective (`extension_cap == max_rounds`) is confirmed
  working: exactly five rounds, no overrun.

## Cross-references

- Experiment 40 R17–R23 Resume Post-Mortem (2026-05-16) — the preceding
  G7-disabled leg and the round-count overrun this leg corrected.
- Experiment 40 Timing Re-Confer Outcome (2026-05-16) — the deferral
  decisions this test was run to put to evidence.
- Exp 36 Mathematical Model Audit (2026-04-07) — the γ "classifies wrong at
  system level during churn" finding cited above.
- Exp 40–54 Consolidated Plan §6c — timing decisions and Exp 41 actions.
- Run log: `bench/logs/exp40_R24R28_20260516T165641Z.log`
- Report: `bench/logs/exp40_gate_20260514T020550Z/exp40_gate_report.json`
- Plain-English companion: Experiment 40 R24–R28 Clean Convergence Test —
  Plain English (2026-05-16); TTS mirror in the CDSFL TTS folder.

Written under CDSFL note standard v1.2 (14 May 2026).
