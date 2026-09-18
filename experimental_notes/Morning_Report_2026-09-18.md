# Morning report, 18 September 2026

2026-09-18, 02:02 BST, Europe/London. Markdown companion to `~/Desktop/CDSFL_tts/Morning_Report_2026-09-18.txt`.

## Summary

The founder's sequence is recorded and nothing in the codebase blocks it: Zenodo key rotation, then the study of the revised mathematical model and the other resources, then a panel review of the model, then a simulated run if it checks out, then back to the runway.

The revised model was read and checked overnight at a first-impressions level. **It does not demote the decay curve and it does not demote gamma.** It states that the original residual-risk recursion is recovered exactly as a special case, and that claim was verified 3 independent ways. It also names an error in `docs/MATHEMATICAL_APPENDIX.md`, and the error is real and still present.

5 open items were classified with `scripts/blocker_triage.py`, the founder's own criterion as code. All 5 returned PARK.

## The revised model, after a first check

`CDSFL_Mathematical_Review_Suite_2026-09-10` verifies its own integrity against a SHA-256 manifest: **PASS on all 41 files**. Its 3 check scripts run clean on exact `Fraction` arithmetic, import only the standard library, contact nothing, and write nothing without a `--report` path. The package states that adoption is undecided, and reports one of its own weaknesses: `free_parameters_can_fit_any_desired_risk: true`.

The core is a Bayesian update on flaw risk followed by a 2-state action with net removal `s` and introduction `b`. Every property below was checked by EXECUTING the package's own `update()`, not by reading it.

| Property | SymPy | z3 | Wolfram | Executed |
|---|---|---|---|---|
| `risk_after = (1-s)z + b(1-z)` | holds | — | holds | 7,776 exact cases, 0 mismatches |
| no action returns the prior exactly | holds | — | holds | 0 violations |
| `risk_after` stays in [0, 1] | — | **unsat** | `Reduce` returns True | 0 violations |
| more removal never raises risk | — | **unsat** | — | — |
| collapses to the original recursion | holds | — | holds | 7-step decay, 0 mismatches |

The 3rd and 4th are proved over the whole valid domain rather than sampled. The 5th is the one that matters most: with `s = b = 0` and a clean review of sensitivity `p`, the revised form becomes `R(1-p)/(1-pR)`, the original CDSFL recursion, and repeated clean reviews multiply the odds by `(1-p)` each time. Wolfram confirms the limit tends to 0 under repeated capable review. **The decay curve survives, derived rather than assumed.**

What the revision replaces is narrow: the repair interpretation of the 3-phase extension, the novelty-validity coupling, and some universal readings of decay. Coverage, weighted class coverage, residual risk, the discovery curves and the tool gates are all retained at their stated scope.

Wolfram results above are computed with Wolfram Language on the local Wolfram Engine via `wolframscript`, through `bench/tools/wolfram_gate/serial`, which is its first real use since the founder enabled it.

## The error it found in our own appendix, confirmed

`docs/MATHEMATICAL_APPENDIX.md` gives the inverse of the coverage-to-risk map **twice, and the 2 disagree**.

- **Line 119**: `C = (π−R)/(π−πR)`. Correct; round-trips.
- **Line 169**: `C_k = (π_k−R_k)/(π_k(R_k−1))`. Exactly the NEGATIVE of the correct form. It does not round-trip, and at `π = 1/2, R = 1/5` it returns `C = −3/4`, which is not a coverage. The same line claims "round-trip residual exactly 0", which is false for the formula it writes.

Confirmed by SymPy and by Wolfram independently. The fix is 1 character class and is NOT applied: the founder asked to discuss before proceeding.

## What needs a word from the founder

1. **The appendix correction at line 169.** A minute's work once approved.
2. **Arm C of the simulated run.** Its designed form needs the `codex_exec` route, now dropped for cost, so it cannot be restored. Run it in weak form, re-register it as a 2-model contrast, or retire it. `launch_blocked` is read by a test, not by a runner, so nothing is mechanically prevented either way. Default: stays flagged, and the simulated run uses arms A and B.
3. **The Codex seat question.** Not urgent: a simulated run uses stand-ins, so it only matters for a paid run. Default: unchanged.
4. **The injection plan.** Recommended for retirement, because runway entry `0C.59` retracted its premise on 2026-09-02: the historic difference was AGENCY, a shell in the working directory, not instruction framing. Default: stays recorded as approved and never built.
5. **The founder's own 2 actions:** drop the 2 stashes, and push, now 32 commits.

## Already in hand

V9 open and scheduled after the model review; the drift detector on the runway at Stage 4 row 4.5 and on the post-revision list; the skip-versus-repair fix delivered at `48487c4`; Wolfram enabled as the second falsifier for every seat and agent, queued against 1 kernel; a fresh working tree per panel attempt with nothing deleted at the end; the full suite green at 8,011 passed under `--netguard-strict`.

**Ordering note.** Zenodo was previously ruled last. The founder has now placed it first, and the record follows the new order.

Written under CDSFL note standard v1.7 (26 August 2026).
