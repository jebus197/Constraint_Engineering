# The scorer was measuring the wrong quantity, and the right instrument was already running

20 September 2026 23:58 BST (Europe/London)

## What was found

`compute_sk` in `bench/reference_runner_v3.py:10752` computes the number the mathematical appendix calls sigma. Appendix line 214 defines sigma as *"Does the proposed fix actually resolve the detected flaw?"*, and line 377 admits it only when `sigma = g(V_pre, V_post)` for a mapping that compares pre-fix against post-fix tool output. `compute_rk` fills that slot with `sk` term for term: the code computes `R_base = sk * R_det + (1.0 - sk) * R_old` against the appendix's `R_base = sigma*R_det + (1-sigma)*R_old`.

Every gate feeding `sk` measured absence of harm instead. `e2_regression` asks whether the existing suite still passes. `e3_ruff` asks whether the fix added lint findings. `e4_bandit` asks whether it added security findings. None asks whether the flaw is gone.

The consequence, executed rather than reasoned about: a real repair, a no-op that leaves the bug untouched, a fix that silently corrupts every answer by swapping division for multiplication, and one that guts the function to `return None` all returned **sk = 1.0 ADMISSIBLE**, identical to 4 decimal places. With a regression suite available the corrupting fix drops to 0.7333 and is still ADMISSIBLE; the no-op and the real repair remain identical at 1.0, because a no-op breaks nothing.

## The measurement over the archive

Across the 135 archived entries carrying both an S_k verdict and a fix-efficacy probe result, `sk` is statistically independent of whether the fix worked.

| Group | n | mean sk | median sk |
|---|---|---|---|
| Fix cures its own falsifier | 104 | 0.950140 | 0.978200 |
| Fix does NOT cure its own falsifier | 31 | 0.950206 | 0.978200 |

The failing fixes score higher by 0.000066 in the mean, and the 2 medians are identical at 0.978200. Mann-Whitney p = 0.678, Welch t p = 0.992, Kolmogorov-Smirnov p = 0.852, and a seeded 20,000-resample permutation test p = 0.627. 4 tests, none rejecting. **31 of 31 fixes measured not to cure their own falsifier were admitted**, Wilson [88.9745%, 100.0000%].

Producer for every figure: `scripts/scorer_discrimination_2026-09-20.py`.

## Why the distribution piles at the ceiling

The 7 blind panel seats independently reported that 672 of 902 archived scored fixes are exactly 1.0, which is 74.5011%, Wilson [71.5570%, 77.2374%]. A fix that changes nothing scores 1.0 on all 3 gates by construction, so the pile at the ceiling is the scorer correctly reporting absence of harm and being read as presence of repair.

Two further structural facts fell out of the same measurement.

**`e4_bandit` carries weight 2.0, the heaviest, and took the value 1.0 in 902 of 902 decisions.** Its detail string is byte-identical across every one: `0 HIGH/0 MEDIUM (baseline: 0H/0M, new: 0H/0M)`. The gate is not broken -- executed against a fix injecting `subprocess.call(cmd, shell=True)` it returns 0.5, and against one adding `eval` as well it returns 0.3. It had nothing to catch, at 40% of the weight.

**That puts a structural floor under `sk`.** With all 3 effect gates available, `E = (2*e2 + e3 + 2*e4)/5` and `e4 == 1` give `E >= 0.4`. SymPy minimises to exactly 2/5 and z3 returns unsat on `E < 0.4`, so the floor is proved twice. Of the 2 thresholds disputed across 4 panel rounds, **0.395043 sits below that floor and could never have refused anything, whatever the corpus**; 0.504931 clears it by 0.104931. The observed minimum across 902 decisions is 0.740000.

**The re-injection channel is compressed by the same floor.** `nu_eff = 1 - (1-nu_b)(1-(1-sk)nu_f)` spans 0.190000 as `sk` runs from 1 to 0. The floor caps the reachable span at 0.114000, which is 60.0000% of designed, and the span actually observed across the archive is 0.049400, which is 26.0000%.

## The repair, which adds no apparatus

`bench/fix_efficacy.py` already applies a proposed fix to a disposable copy of the target and re-runs the finding's own falsifier against it. That is precisely the `g(V_pre, V_post)` comparison appendix line 377 requires. It was "contributory, never gating", and its only consumer was a single model-facing feedback line, so the project was already taking the right measurement and then computing sigma from something else.

The fix wires that measurement into the score as a 4th effect gate, `e1_efficacy`, at weight 2.0 -- equal to the heaviest existing gate rather than above it, because "this gate deserves more" is a judgement and the additive standard does not accept a judgement as evidence.

Only the 2 outcomes that `fix_efficacy.ProbeResult.is_verdict` already calls verdicts are read as scores. The 5 INDETERMINATE and NOT_PROBED outcomes return `None`, and the gate is dropped from the weighted mean exactly as an unavailable `e2_regression` already is. Scoring them 0 would punish a fix for the instrument's silence and would drive `nu_eff` to its maximum, fabricating re-injection risk. This is the project's `Wolfram: a failed call is NOT a result` rule applied at a second site.

Call ordering was verified by AST rather than assumed: `_update_finding_statuses` runs at line 13867 of `run_experiment` and `_evaluate_sk_for_findings` at line 14376, so the probe outcome is already on the entry when the gate reads it.

## What the repair changes, on the same archived entries

| | Before | After |
|---|---|---|
| Mean sk, fix cures its falsifier | 0.950140 | 0.964375 |
| Mean sk, fix does NOT cure | 0.950206 | 0.678703 |
| Gap in means | -0.000066 | +0.285672 |
| Mann-Whitney p | 6.782e-01 | 1.428e-18 |
| Welch t p | 9.923e-01 | 9.274e-50 |
| Kolmogorov-Smirnov p | 8.523e-01 | 6.295e-31 |

The sigma fed to `compute_rk` for a fix known not to work falls from a mean of 0.9502 to 0.6787.

**The limit is stated rather than glossed.** Those 31 fixes remain ADMISSIBLE. The tristate is `sk > 0`, so only a failed hard gate rejects, and this gate informs sigma rather than vetoing. Whether a fix that demonstrably does not cure its own falsifier should be admitted at all is a separate question and is the founder's.

## One behaviour change, declared rather than discovered

When `e2`, `e3` and `e4` are all unavailable, `compute_sk` previously had no effect gate at all and returned ESCALATE, whose message reads *"the evidence gates went silent (no baseline, no test command)"*. With `e1_efficacy` present that sentence can be false, because an instrument did speak. A probe verdict alone therefore now produces a terminal status: ADMISSIBLE on FIX_CURES, REJECTED on FIX_INEFFECTIVE.

This does not breach T04, the rule that an equipment failure may not write a terminal status. FIX_INEFFECTIVE is a verdict by `fix_efficacy.ProbeResult.is_verdict`'s own definition, and all 5 equipment outcomes return `None` and are excluded from the mean, so the rule holds by construction rather than by care.

**Measured reach: 0 of 1,247 archived records**, Wilson [0.0000%, 0.3071%]. All 154 archived ESCALATE records have every effect gate silent and none carries a probe verdict, so this reclassifies nothing that already exists. It is a latent path, pinned by `test_a_probe_verdict_alone_can_carry_a_terminal_status_and_that_is_deliberate` rather than left to be found later.

## A second, smaller defect in the same path

`_rejection_lines` at `bench/reference_runner_v3.py:12251` builds the message a model receives when its fix is rejected. It selected failed gates with `v is False or v == 0 or v == 0.0`, and every gate is recorded as a dict, which is never equal to 0. The list was therefore always empty and every rejection read "hard gate returned 0" while the details held the exact reason. Executed on an unparseable fix, the details carried `g1_ast score=0` with `ParseError: '(' was never closed` and the model was told none of it. The predicate now reads `score`, and the detail string travels with the gate name.

## A third, found by the suite

`bench/tests/test_citation_content_2026-09-10.py` unpacked 5 fields from a tuple its guard builds with 7. The mismatch is reachable only when the guard finds something, so it passed for as long as nothing drifted and raised `ValueError: too many values to unpack` the first time something did -- reporting a crash instead of the drift it had correctly found. Fixed, and the 6 citations that drifted by this session's line insertions were repaired by the guard's own `--fix`.

## Tests

`bench/tests/test_sk_measures_fix_efficacy_2026-09-20.py`, 14 tests. **12 fail against the parent commit.** The 1 that passes is the SymPy invariant pinning `compute_rk` to the appendix resolution phase, which was correct before and after and exists so that the reason for the gate travels with the equation if it is ever re-derived.

The tests call rather than read. A test asserting on the source text of the scorer would assert only that the scorer describes itself consistently, and this defect was 2 modules each describing itself correctly and disagreeing with the other. `test_the_runner_call_site_actually_passes_the_probe_outcome` drives the real evaluator with 2 registry entries differing only in their recorded probe outcome and requires the scores to differ, because a typo in the keyword would still have grepped green.

## Status

BUILT, TESTED, COMMITTED. Not yet exercised on a live run; that is the next simulated run.

Written under CDSFL note standard v1.7 (26 August 2026).
