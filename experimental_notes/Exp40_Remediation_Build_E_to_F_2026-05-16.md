# Experiment 40 — Remediation Build (plan items E→F): Post-Mortem

2026-05-16 23:46 BST

## Summary

The founder-approved remediation plan for Experiment 40's intermittent
non-convergence was built and committed in full during one autonomous
session. Root cause (established in the preceding root-cause note):
verified fixes were only ever applied in a throwaway sandbox, so the
panel re-reviewed the same defects every round and the error space never
exhausted — the re-injection-dominated regime the decay model predicts.
Six work items (E, A, B, C, D, F) address this. E through D are landed,
tested, and committed; F (the decomposed convergence re-run) is running
under live supervision at the time of writing.

A significant methodological finding surfaced during E and is recorded
prominently below: a finding marked CLOSED at run time does **not** mean
its fix is correct — it means the fix's S_k aggregate cleared the
admissibility threshold, which tolerates a partial regression. This is a
second, independent convergence-relevant defect and it shaped the design
of the structural cure (C).

## What was built (commit trail)

- **E — collation** (`6838e58`). `bench/exp40_fix_collation.py` collates
  all 44 CLOSED findings from the consolidated Exp 40 registry across
  four legs: 40 artefact fixes (to `_feedback.py`), 0 runner/methodology
  (the methodology tranche was already committed separately), 4 stale
  (no parseable fix block). A cleaned baseline
  (`bench/exp40_baseline/_feedback_cleaned.py`) was built by cumulative
  application under a strict gate (AST + py_compile + the full
  `test_feedback_channel.py` suite per patch): 11 accepted, 29 skipped
  (28 SEARCH-not-found = competing/drifted fixes for the same regions —
  the documented fix-churn; 1 = C0001, see below). Cleaned baseline
  passes 40/40, ruff clean.

- **A — collision-overwrite fix** (`6e63169`). The
  `{f.finding_id: f for f in findings}` last-wins comprehension in
  `build_feedback_records` silently dropped a finding when two shared an
  id, mis-routing the dropped model's corrective feedback to the
  surviving model (records route per-model). Replaced with
  collision-safe accumulation: per-id finding list, records keyed by
  `(finding_id, model_origin)`, all four record-building blocks
  iterate per-id findings so every model gets its own routed record.
  Blast radius FFAFP'd (sole consumer; only caller runner:2345). Stale
  comprehension-site test updated to pin the fix; 2 behavioural tests
  added; 106 tests pass across all `_feedback` consumers.

- **B — in-round re-ask** (`c2dd4ef`). On a structural parse failure
  (≥2 finding-declaration markers, 0 parsed, real response), the runner
  re-dispatches once to that model in the dispatch phase with a
  STRUCTURE_VIOLATION corrective prompt. Bounded (1 retry/model/round),
  idempotent (retry replaces the round's output on recovery; original
  kept on failure), config-gated (default-on), module-mirror pattern.
  8 isolation unit tests; regression sweep 90 pass.

- **C — apply-verified-fixes-back** (`58a4efa`). The structural cure.
  When a finding reaches full BUGZILLA close, its patch is promoted
  into a per-run working copy that the next round reviews — gated on
  the **full canonical suite** passing cumulatively, not the run-time
  S_k score (the C0001 lesson). Loop-top hook only (avoids the many
  mid-body exit paths); per-run working copy, repo file never written,
  pristine kept; idempotent across rounds; default-off (changes the
  experiment from static-stimulus to iterative repair-and-reconverge —
  an intended, recorded change). 5 unit tests; sweep 95 pass.

- **D — decomposition slice** (`42da873`). Smallest self-contained
  seam of the cleaned baseline: the admissibility parser
  (`bench/exp40_baseline/_feedback_slice.py`, ~110 lines, pure
  `str→List[str]`, zero coupling). Focused suite
  `test_feedback_slice.py` (11/11). Plan-F config
  `40_slice_admissibility.json`. `--config` added to the launcher
  (`654a4c8`).

- **F — convergence re-run** (running). Launched
  `python3 bench/launch_exp40.py --config 40_slice_admissibility.json`.
  Confirmed live at start: apply-fixes-back ENABLED (working copy
  seeded from the pristine slice), in-round re-ask ENABLED, G7
  ENABLED, Gate C preflight PASS, target 5,596 chars, 20-round cap
  (R0–R19). Collision fix (A) is a runner-pipeline change, active
  automatically. Supervised by a 60-second FFAFP guard (freeze only on
  unambiguous corruption; alert-only on soft signals — the R24–R28
  lesson) with a Terminal window for morning review.

The maths re-audit (old plan item 1) was declined by the founder and
not built; convergence is taken as real and bounded.

## Key methodological finding (recorded, not buried)

`C0001` was marked CLOSED at run time with `sk=0.9897` while its own
`e2_regression` gate scored `0.974 = "38/39 passed (sandbox)"` — i.e.
the fix already failed one test in its own sandbox, yet the weighted
S_k aggregate cleared the admissibility threshold and the finding was
recorded as verified/CLOSED. **CLOSED means "scored above threshold",
which over-counts regressing fixes as fixed.** This compounds the
unfixed-artefact root cause (some "fixed" bugs were fixed with
regressing patches) and is why C gates apply-back promotion on the full
canonical suite, not the S_k score. The strict collation gate correctly
excluded C0001 (`feedback_tests_fail: 1 failed`).

## Verification posture

Every landed item carries its own tests and a regression sweep; ruff
delta checked at each step (zero new errors introduced — 53 pre-existing
runner / 3 pre-existing launcher errors are unrelated import debt, out
of scope). Milestone commits were made at each item so the morning
review has a bisectable trail rather than one large changeset.

## Open / watch items for the morning review

1. **F outcome is unknown at writing.** It is running. Check, in order:
   the guard sentinel `/tmp/exp40_slice_DONE` (terminal: convergence /
   stall / R19-complete) or `/tmp/exp40_slice_ALERT` (anomaly — the run
   is frozen only if unambiguous corruption was detected, otherwise
   alert-only and still running); the heartbeat log
   `/tmp/exp40_slice_ffafp.log`; the Terminal window; the run log named
   in the tracker. This is the founder's core question — does the
   system converge once the error space can actually exhaust — and the
   answer is whatever F produces; it must be reported straight,
   converged or not.
2. **Not an escalation, a caveat:** the slice is small and already
   test-clean, so genuine novel-critical findings may be few; a fast
   γ-alt convergence would be a real positive signal, a continued
   plateau would indicate the non-convergence is not purely the
   error-space-exhaustion mechanism and the investigation continues on
   the novelty dynamics. Either outcome is informative; neither should
   be spun.
3. Nothing in E→D was left unresolved or papered over. The one
   substantive surprise (C0001 / CLOSED≠correct) was handled in-design,
   not deferred.

## Cross-references

- Experiment 40 Root Cause and Remediation Plan (2026-05-16) — the
  approved plan this build executes.
- Experiment 40 R24–R28 Clean Convergence Test Post-Mortem
  (2026-05-16) — the falsification that motivated the plan.
- `bench/exp40_baseline/collation_report.json` — the E audit record.
- Commit trail: `6838e58` `6e63169` `c2dd4ef` `58a4efa` `42da873`
  `654a4c8` on `exp39-experimental`.
- Plain-English companion: Experiment 40 Remediation Build — Plain
  English (2026-05-16); TTS mirror in the CDSFL TTS folder.

Written under CDSFL note standard v1.2 (14 May 2026).
