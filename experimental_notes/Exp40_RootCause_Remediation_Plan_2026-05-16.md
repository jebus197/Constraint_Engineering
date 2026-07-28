# Experiment 40 — Root Cause of Intermittent Convergence, and the Remediation Plan

2026-05-16 22:57 BST

## Summary

The persistent, intermittent non-convergence of Experiment 40 has a single
dominant root cause, confirmed by code inspection, git history, and a prior
documented audit: **verified fixes are never applied back to the artefact the
panel reviews.** The runner verifies a proposed fix in a throwaway sandbox,
marks the finding CLOSED in the registry, and discards the sandbox. The real
target file is unchanged, so every round the five-model panel re-reads the
same defects and legitimately re-reports them. Convergence cannot complete
because the error space never exhausts.

This note records the evidence, states the mathematical framing (the model
predicts this failure; it does not cast doubt on convergence), and sets out
the approved six-part remediation plan with its design decisions and
sequencing. One consequence is flagged explicitly: the structural fix changes
Experiment 40 from a static-stimulus panel-agreement test into an iterative
repair-and-reconverge test. That change is intended.

## Root cause (evidence, not hypothesis)

- **Target.** `bench/dm/_feedback.py` — 621 lines, 27 KB — plus
  `bench/dm/_types.py` (683 lines, 30 KB, read-only context). Monolithic
  single dispatch to all five models.
- **Sandbox-only verification.** `_run_regression_suite`
  (`bench/reference_runner_v2.py` ~L3088–3116) copies the repo into a
  `tempfile.TemporaryDirectory()`, overlays the modified source, runs
  ruff/mypy/bandit/tests inside it, and lets the temp directory be destroyed
  on context exit. `apply_fix_blocks` (L3018, called L3342) produces the
  modified source in memory; it is written only into that sandbox.
- **No write-back.** No code path in the runner writes to `bench/dm/`; the
  only `write_text` targets are fingerprints, logs, calibration, checkpoint,
  and reports. Git history of `_feedback.py` shows zero runner-driven commits
  across all 29 rounds (R0–R28).
- **Consequence.** A finding reaching CLOSED means its fix passed in the
  sandbox; the defect remains physically in the file the panel re-reads next
  round. The only forces opposing re-discovery are de-duplication and a
  prompt-level "do not re-report closed issues" summary capped at 20 entries
  / 4,000 characters (`prior_fix_summary_max_entries=20`,
  `prior_fix_summary_max_chars=4000`); once findings exceed that cap,
  suppression coverage decays.
- **Prior documentation.** The Exp 36 ground-truth audit already recorded
  "CONFIRMED ≠ CLOSED — findings never reach CLOSED because the runner
  doesn't extract/apply/verify fixes … 17:1 dedup churn." The verify half was
  subsequently built; the apply half was not. CLOSED-in-registry is not
  fixed-in-artefact.

## Mathematical framing (the model predicts this; it does not doubt convergence)

The appendix defines the convergence parameter γ = 1 − β (Duane form): γ > 0
with a decreasing finding rate denotes "genuine convergence — error space
exhausting", and the Duane model empirically fits 17 of 18 prior bench runs.
Convergence is real and the decay-curve logic is sound; Exp 37 reached a clean
STATE_CONVERGED (γ 0.467). The appendix also states the divergence condition:
when the re-injection term ν·Δ exceeds the decay rate, the system "transitions
from convergence to entropy generation." An artefact whose defects are never
removed forces exactly that regime — re-injection cannot fall because the
defects are perpetually re-present.

The Exp 40 γ trajectory across R0–R28 matches this precisely: a rise to a peak
of 0.2967 at R3 (early de-duplication clears the easy repeats; depletion
appears high), then a monotonic decline to a ~0.05 plateau, flat for 25
consecutive rounds (R4–R28). γ is reporting the system correctly; it is not
mis-calibrated. The earlier suggestion that the metric might be mis-measuring
is withdrawn — the evidence points to the unfixed artefact, and the metric is
accurately detecting the resulting re-injection-dominated state.

## Remediation plan (approved scope)

The forensic maths-model audit originally proposed as plan item 1 was declined
as unnecessary; the framing above is sufficient and convergence is taken as a
real, bounded phenomenon for a proof-of-concept in a constrained problem
space. The remaining items A–F are approved.

**A. Collision-overwrite fix.** `_feedback.py:228`
`finding_by_id = {f.finding_id: f for f in findings}` silently overwrites one
finding with another on a shared ID — a real, separate, still-open
silent-data-loss defect that corrupts the novelty count (the quantity the
convergence test measures). Approach: collision-safe accumulation — on a
genuine collision (different model or content), retain both under
disambiguated keys and log it rather than dropping one. Five consumers, all
`.get(fid)` lookups (L235, 263, 280, 300), are FFAFP-audited before commit;
full suite re-run. UUID-namespace is escalated only if a consumer cannot be
satisfied by the composite approach (reported, not silently substituted). The
observation-only detector stays as a tripwire. This replaces the
detector-gated deferral with an actual fix.

**B. In-round re-ask.** On a structural parse failure, re-dispatch to that
model only, in the dispatch phase (not the reconciliation close path —
that was the loop/ordering risk), with an explicit corrective template.
Bounded to one retry per model per round, idempotent, every attempt logged,
no double-count. Fix 1e (next-round strengthened reformat) remains the
fallback. This is the active error-correction the founder specified.

**C. Apply verified fixes back to the artefact (structural cure).** When a
finding passes the full BUGZILLA close (sandbox ruff+mypy+bandit+test all
green), promote its SEARCH/REPLACE patch into a per-run working copy that the
next round reviews. Design decisions: (1) write target is a per-run working
copy under the run's log directory, not the repo file — reproducible, source
control stays clean, pristine original retained for provenance; (2) the next
run starts from a working copy that already has every previously-verified
CLOSED patch applied (this is the literal "fold all past fixes in, once and
for all"); (3) a patch is promoted only if the cumulative working copy still
passes all gates, so a fix valid alone but breaking in combination cannot
corrupt the artefact.

**D. Decompose the target.** Run against the smallest self-contained
functional unit of `_feedback.py` first — recommended: the admissibility/parse
group, the most isolated and implicated in the persistent parser-failure
problem. The exact seam is shown before any run. Short, monitorable runs by
design.

**E. Collate, cross-verify, and FFAFP all past Exp 40 fixes.** Programmatic
extraction of every CLOSED finding and its fix block from the registry/report
across all four legs (296 canonical, 44 CLOSED). Classify: runner/methodology
fix → fold into `reference_runner_v2` if valuable and not already; artefact
fix → cumulatively apply through the gate to build C's seeded baseline;
stale/duplicate → discard, logged. Multi-tool cross-verified per the standing
pairings.

**F. Re-run.** Decomposed slice, seeded clean baseline, apply-back loop,
collision fix, in-round re-ask, G7 enabled. Generous cap (≤ ~20 rounds is now
appropriate because the design is fixed; the earlier objection was only to 20
rounds on the broken design). Active 60-second monitoring with pause and
fix-on-the-fly.

## Sequencing and dependencies

E → A and B (parallel) → C → D → F. E first because it produces C's seeded
baseline and surfaces which runner fixes still require folding. A and B are
bounded and independent. C depends on E. D's seam is selected alongside C.
F runs last under live monitoring.

## Consequence flagged explicitly

C changes Experiment 40 from a static-stimulus panel-agreement test into an
iterative repair-and-reconverge test. This is a real change in what the
experiment measures and is recorded as a conscious design decision, not
introduced silently. It is the correct change: it is the precondition the
decay model requires for termination, and it matches the proof-of-concept
intent of converging on one definitive working artefact rather than
re-reviewing an unchanging one.

## P-pass risk on the plan

Seeding the baseline with 44 individually-verified patches risks cumulative
conflict (a patch valid in isolation may fail in combination). Mitigation:
E applies them cumulatively through the full gate; the seeded baseline must
pass the entire suite before F uses it; any patch failing in combination is
excluded and logged, not forced.

## Cross-references

- Experiment 40 R24–R28 Clean Convergence Test Post-Mortem (2026-05-16) —
  the falsification that motivated this analysis.
- Exp 36 Ground Truth Reference (2026-04-08) — the original
  CONFIRMED ≠ CLOSED / fixes-not-applied finding.
- Mathematical appendix, Part X-A — Duane γ, divergence condition,
  churn-blindness.
- Run report: `bench/logs/exp40_gate_20260514T020550Z/exp40_gate_report.json`.
- Plain-English companion: Experiment 40 Root Cause and Remediation Plan —
  Plain English (2026-05-16); TTS mirror in the CDSFL TTS folder.

Written under CDSFL note standard v1.2 (14 May 2026).
