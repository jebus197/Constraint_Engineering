# Session Report and Outstanding Decisions — 2026-09-05 01:25 BST

## A CORRECTION TO THE PROTOCOL, BECAUSE IT MATTERS MORE THAN IT LOOKS

The five step cycle is FFAFP, not FFFAP, and the order is Find, Follow, Analyse, Fix, P-pass. Analyse comes BEFORE Fix. The canonical statement is in the reproducing document at line 368 and the reasoning is in the global instruction file: the point of the five step form is that tool assisted analysis happens before the fix and falsification happens after it. Reversing Analyse and Fix would mean fixing on a hunch and then gathering evidence to justify a decision already taken. Follow comes before Fix for the same reason. Find without Follow produces shallow patches; Fix without Follow produces regressions.

HAVE I BEEN FOLLOWING IT FULLY? NO, AND THE RECORD SAYS WHERE

Of 6 fixes put to the panel this session, 2 survived first review unchanged. That is 33 percent, with a confidence interval from 9.7 to 70.0 percent. The interval is wide because the sample is small, but the direction is not in doubt.

The failures cluster in one step. Analyse is strong: tools were used throughout and every computational claim was cross checked with at least 2 of them. P-pass is the weak step. In 4 of the 6 cases the fix was right in direction and wrong in a case that had not been tried. And Follow failed once, decisively: the overlap record was wired into the merge path without tracing that the tool only enforcement sat below it in the same function, so a merge the runner refused still wrote the record. That is exactly what Follow exists to prevent.

## WHAT WAS BUILT TONIGHT

The mathematical appendix carried many statements that something had been verified with symbolic algebra, and 18 statements of the form X reduces to Y under condition Z. Exactly 1 test file in the whole suite imported the symbolic algebra library, and it tested a calibrator rather than any appendix claim. The model's verification lived entirely in prose, which is the same defect as a test that reads source text, one level up: a sentence saying a thing was verified is a claim about evidence, not evidence.

A test module was built to execute those claims. Both reviewers refuted it within the hour, and both were right.

## THE WORST FINDING WAS MINE

Three of the 15 assertions were substitution tautologies. Subtracting an expression from itself after a substitution gives zero for any expression whatsoever, so the test passed with the model replaced by the constant 42, by a sine function, and by an arctangent. It asserted nothing at all about the model. This was reproduced before acting on it.

The accompanying falsification pass could not detect this, because it perturbed the substitution point rather than the expression. One reviewer demonstrated it certifying a deliberately meaningless model as sound. And the falsification pass itself existed only as prose in a commit message, with no committed script, one day after this project adopted the rule that a measured result must travel with the code that produced it, and inside the very commit written to abolish claims about evidence.

The fix is structural rather than another script. Every test now asserts two things: that the residual is exactly zero under the appendix's stated condition, and that it is non zero for at least one wrong model. The discrimination lives inside the test, so there is nothing separate to lose or forget to commit. The module now holds 30 tests. The suite stands at 4907 passed, 0 failed, 0 errors.

## OTHER REFUTATIONS ACTED ON

One test checked the wrong index entirely, collapsing the pass index inside a single class when the claim was about collapsing the class index. One reduction was excluded as untestable and is not: the Duane intensity is exactly proportional to the inverse square root of time at a shape parameter of one half. The enumeration missed 3 statements that carry the label Reduction property but state an equation rather than using the word reduces, so the true count is at least 21 rather than 18. And a table of reductions was dismissed as table rows when it contained the strongest identities in the appendix. All of these are now tested.

## TWO DEFECTS FOUND IN THE APPENDIX ITSELF, PINNED RATHER THAN PATCHED

These are recorded as tests that assert the true state, because amending the mathematics is a founder decision.

The first is a constraint on coupling constants, stated as necessary to keep all state probabilities non negative, and attributed to symbolic verification in March. It is false. Every state weight is a product of non negative factors multiplied by an exponential, and an exponential is strictly positive for every real input, so no coupling can make a weight negative. Measured at a detection probability of 0.9, where the stated bound is 4.6052, the minimum state weight is 0.01 at zero coupling, at the bound, and at a coupling of 1000 alike. The second reviewer reproduced this independently at 36 times the bound. The constraint may be needed for numerical conditioning, since the exponential overflows at large values, but not for the reason given, and the claim contradicts a statement 2 lines above it.

The second is a row in the reduction table which omits its necessary condition. The reduction to the simple corroboration model holds only when there are no human passes; with a human stream present it does not hold.

## DECISIONS AWAITING YOUR ADJUDICATION

1. The fix acceptance gate. It has never rejected anything, 0 times in 3816. Repair is provably inert, because the lowest fix quality score in the archive is 0.74 and the corrected threshold would reject none of them. The choice between repairing and removing is not binary: repairing the formula, removing the call from the decision path, and correcting the appendix touch 3 disjoint artefacts, so composing all 3 has a residual of zero against 1 for either alone. The composed action is not applied and needs your ruling.

2. Where the reduction work belongs. One reviewer proposes a rule with teeth rather than a definition: reductions must be discharged, not sampled. A sampled agreement may be recorded as refuted or as undischarged, never as confirmed. That is a change to the verdict vocabulary and needs your decision.

3. The execution based duplicate matcher, approved but not started. It changes how findings are matched, so it is behavioural.

4. The single model against single model with agents experiment, approved but not started, together with restoring the seat contrast as its diversity arm.

5. The mechanically generated seeded defect catalogue, approved but not started.

6. Commissioning the 2 settings that are switched off by design and reachable by no configuration: severity calibration and stall based termination.

7. The rubric adjudication. Both reviewers measured that roughly 82 percent of the disputed band is already settled by tool, leaving a genuine human queue of 4 items out of 33 rather than 259. The separating test is a lookup in the existing schema rather than a judgement.

8. The 2 appendix defects above.

9. The unpushed work. The main branch is 78 commits ahead of the public remote and has not been pushed. That remains yours to run.

## ONE OPERATIONAL NOTE

The remote session dropped earlier tonight. The cause was memory exhaustion on the machine at home, and you identified it correctly: a leak in the browser or one of its extensions. Quitting it released 5295 megabytes of swap and the swap pool itself shrank from 9216 to 4096 megabytes, which the operating system only does when pressure genuinely falls. My own workload of full test suite runs and panel dispatches was additive on an already exhausted machine, not the origin. A compaction detector was built and wired in, so from now on a compaction announces itself on every turn until the restore command is run.


---

## References

| Claim | Where |
|---|---|
| FFAFP order, Analyse before Fix | `docs/REPRODUCING.md:368` |
| 2 of 6 fixes survived first review, CI [0.097, 0.700] | panel records `panel_verify_20260904T203042Z`, `panel_appendix_20260904T234405Z` |
| 3 substitution tautologies, pass with `step = 42` | reproduced before acting; commit `5739cd9` |
| Duane at β=½ is the inverse-square-root law | `bench/tests/test_appendix_reduction_properties_2026-09-05.py` |
| L38 coupling bound false as justified | same file, `TestSection0_1_TheBoundednessConstraintIsMisjustified` |
| Gate fire rate 0 of 3816, CI [0.0000, 0.0010] | commit `33ef614` |
| Suite 4907 passed, 0 failed | `--netguard-strict`, 352.45 s |

Commits this session: `d7b3285`, `5739cd9`, `8de9883`, `59af19b`, `1928de4`, `5a0f20c`.
