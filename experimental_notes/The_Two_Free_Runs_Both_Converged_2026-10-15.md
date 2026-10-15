# The 2 free runs both converged, and the pair bought more than the contrast it was designed for

2026-10-15 09:54 BST. Audience: a reproducing engineer. The plain-English companion is `The_Two_Free_Runs_Both_Converged_Plain_English_2026-10-15.md`.

## The result

Both runs converged cleanly on the hardened two-sided gate. That is 2 of the 3 consecutive clean convergences the programme's success criterion requires.

| | run 1 — specification RECORDED | run 2 — specification DECIDING |
|---|---|---|
| convergence | `HARDENED_CONVERGED` at round 3 | `HARDENED_CONVERGED` at round 4 |
| rounds run | 4 | 5 |
| per-round findings | 14, 2, 5, 1 | 14, 0, 2, 3, 0 |
| total findings | 22 | 19 |
| gamma_critical | 1.000, sustained 2 rounds, loo_min 1.000 | 1.000, sustained 2 rounds, loo_min 1.000 |
| gamma_all (diagnostic) | 0.652 | 0.820 |
| cumulative criticals | 12 | 12 |
| unresolved criticals at close | 0 | 0 |
| contested at the gate | 0 | 1, settled by round 4 |
| final statuses | CLOSED 18, CORROBORATED 2, REFUTED 2 | CLOSED 17, REFUTED 2 |
| wall clock | 82.4 min | 57.2 min |
| runner | v3.2 | v3.2 |

The contrast was verified at the DECIDING LAYER rather than assumed from the command line, because a flag in `argv` proves the launch and not the deciding layer. `bench/reference_runner_v3.py:16935` makes the deciding layer state its own mode: run 1 logs `Severity: asserted (specification recorded only)` and run 2 logs `Severity: SECTION 7.7 SPECIFICATION (deciding)`, 1 line each and 0 of the other. The wiring runs `--severity-spec` → `RunnerConfig.severity_spec_enabled` → `_SEVERITY_SPEC["on"]` → the early return in `effective_severity`.

## What is identical, and it is more than the design asked for

Round 0 produced exactly 14 findings in both runs. Cumulative criticals ended at 12 in both. `critical_asserted` equalled `critical_spec` at 12 in both, `crossed_downward` was empty in both, and `key_property_violations` was empty in both. So with the section 7.7 severity DECIDING rather than merely recorded, **nothing changed and nothing broke** — which is the question run 2 was able to answer.

## What differs, and what may NOT be attributed to the flag

Rounds 1 and 2 differ (2 and 5 against 0 and 2), and run 2 carries 19 findings against 22. **None of that is attributable to the severity specification**, which governs release decisions at the A4 door and cannot cause a seat to report fewer findings in a round. The seats are simulated subagents and are non-deterministic. With n = 2 the run-to-run variance cannot be estimated from the pair itself, so the pair can only detect a LARGE effect — and the archive replay has already measured the effect as small, 7 releases changing across 2,994 findings. Run 2's value is therefore a MACHINERY test, not an effect measurement, and reporting its 19 findings as the effect measurement would substitute an under-powered instrument for an adequate one that has already run.

The same bound applies to the HIL flags: 3 seats were flagged for consecutive ITC interventions in run 2 (CC2-SIM, ChatGPT-SIM, Codex-SIM, all `CAPABILITY_MISMATCH`) against 1 in run 1. Recorded as an observation needing a larger sample.

## Run 2 exercised a gate path run 1 could not reach

Run 2 did not converge at round 3. The gate refused: *"hardened REFUSED at R3: 1 contested finding(s) still in dispute, so the critical picture is not settled"*, in mode `contested_blocked`, with every other condition already satisfied — gamma_critical 1.000, `zero_crit_ok` true, the location-keyed series tail `[0, 0, 0]`, 0 unresolved criticals. The contested finding settled and the gate passed at round 4. **That is correct behaviour and it is coverage 1 run could not have bought.** The `cy` watchdog labelled the refusal TROUBLE, which is a false positive in its severity labelling; recorded, not chased.

## ★ The sharpest finding: the severity specification's KEY PROPERTY was never exercised

Section 7.7 is `Sev(f) = W(class) × confidence × V(verification)` with `V(True)=1.0, V(None)=0.5, V(False)=0.0`. The appendix's own stated KEY PROPERTY is that a DISPROVED finding scores ZERO regardless of the model's confidence — a tool outcome annihilates the model's number — and that annihilation is what makes the specification structurally unlike a vote.

**Across both runs, 0 of 41 findings carried a disproved verification**, Wilson [0.0000%, 8.5668%], Clopper-Pearson [0.0000%, 8.6044%], the upper bound cross-verified by the closed form $1 - 0.025^{1/41}$ and by mpmath at 40 digits, all three agreeing to 1e-9. So the annihilating input never arose and the specification's distinguishing term could not bite.

**The claim was re-checked against the final reports because it looked contradicted.** Both runs show 2 findings with status REFUTED, and a reader could take that as disproving `V_false = 0`. It does not: `spec_verification_factor` reads `entry["falsifier_verdict"]`, not `entry["status"]`, and a finding's status can be REFUTED by routes that are not a falsifier returning a refutation. Measured on exactly those findings — run 1's C0020 and C0021 carry no `falsifier_verdict` at all; run 2's C0016 carries `CONFIRMED` and C0017 carries `INTEGRITY_VIOLATION`. An independent recomputation from the final reports gives run 1 V_true 18, V_none 4, V_false 0 and run 2 V_true 17, V_none 2, V_false 0, against the round-3 telemetry's 15/7/0 and 14/5/0. The V_true and V_none splits move because the post-convergence settle confirmed more falsifiers after the telemetry was written; **V_false is 0 at both moments in both runs**, so the figure holds under the runner's own census and under an independent route.

So `crossed_downward` being empty has 2 causes rather than 1: the low base rate already measured over the archive, AND the absence of any disproved verification.

## The severity arm is now answered in 3 parts, by 3 different instruments

- **The EFFECT**: answered by the archive replay at n = 2,994. Promoting the specification changes 7 A4 releases, small because the release test's other half — a proven calculation — holds for only 295 of 2,994 findings, 9.8530%, Wilson [8.8364%, 10.9726%].
- **THE SWITCH'S OWN BEHAVIOUR**: answered by run 2. The switch computes, agrees with the asserted critical count, records 0 key-property violations, exercises the contested-blocked path correctly, and still converges.
- **The KEY PROPERTY**: answered by NEITHER run, and gated on the staging defect below.

A zero would need 688 findings before it carried information at the archive's measured rate, so the 2-run contrast is under-powered by a factor of 31.27 — cross-verified by a scipy loop, the SymPy closed form $\lceil \ln(1/5)/\ln(1-7/2994) \rceil$ and mpmath at 40 digits.

## 2 defects found during the runs are FIXED; 2 remain open

**B9 — FIXED. The confinement guard refused the falsifier its own review target.** 18 refusals per run, every one reading `bench/logs/<run>/working/prose_with_computable_listings.md`, which is the copy every round is pointed at. Neither component was wrong alone: `_is_evidence` refuses any `bench/logs` path even inside an allowed root — correct, closed 2026-10-12 by `e8ee2e18` after both free seats found that hole — while the runner staged the target there, as it had since `ce08914c` on 2026-09-01. The date is established by the refused paths rather than the commit dates: `study_run1b_2026-10-03` carries 81 refusals of which 0 are a target, Wilson [0.0000%, 4.5278%], against 18 of 18 that ARE in both free runs, Wilson [82.4121%, 100.0000%], Fisher exact p = 3.976950e-20 and a chi-square with Yates correction at p = 7.110490e-22. The copy is now staged under `falsifier_verify.STAGED_TARGET_ROOT`, already allowed and documented for this purpose, and MIRRORED into `logs_dir / "working"` on every write so nothing leaves the run's archive. Verified sound before a line of it was written, by extracting the guard's own `_denied` from the observer it ships and calling it. 15 executing tests, 4 mutations each turning them red, and `test_a_falsifier_cannot_read_the_evidence_2026-10-12.py` still returns 13 passed, so the hole `e8ee2e18` closed is not reopened.

**B7 — FIXED, and the credit is not this session's.** A simulated run restamped all 5 real paid seats' fingerprints at its convergence moment, in both runs. 0 of 5 observed values moved, so it was record-only, and what kept the records apart was the mandatory `-SIM` suffix making `CC2-SIM` a different dict key from `CC2` — a naming rule turning out to be the sole guard on the real seats' accumulated counters, 3 of which feed live routing. **The `fable` seat found this on 2026-10-05** and named that load-everything-then-save-everything asymmetry exactly under its own heading, *"THE FINGERPRINT STORE ERASES RUN PROVENANCE ON EVERY SAVE"*; its producer sat only inside a sandbox harvest, absent from `scripts/` and named nowhere in the task list, and the defect survived 10 days. `_save_fingerprints` now writes a seat only when its payload differs from what was loaded, fable's producer is promoted unchanged beneath a header naming it as the author, and **that producer now reports the repair from its own output**: *"2 distinct stamps across 11 files: REPAIR VISIBLE"*, where before the fix all 11 carried one stamp.

**B8 — OPEN.** The coherence-budget recalibration is inert on 3 independent layers, each sufficient alone: 0 AST call sites and 0 imports; no persistence past the Python interpreter, since `MODEL_COHERENCE_BUDGETS` is a source literal at `composer.py:69` and a mutation to 0.123456 reads back as 0.02 in a fresh process; and 0 of run 1's 61 JSON entries carry both `model` and `chars`, Wilson [0.0000%, 5.9244%], so on real logs it returns its own defaults byte-identically. The algorithm is sound — on a correctly shaped fixture it moves `opus_4_6` from 0.02 to 0.0571 — so the gap is a schema mismatch and the repair belongs at the log-emission end. The coherence pruner's lean-versus-full ablation arm, the gate on every proposed cut since 2026-07-18, stays un-runnable until it is closed.

**B6 — OPEN**, 3 defects recorded and deliberately unfixed, unchanged by these runs.

## 2 more programme arms answered from the runs' own logs

**`guard_reach`**, in 2 halves. The invariance probe's population is nearly empty and that is GOOD NEWS: 40 corrected copies were accepted of 57 offered, 70.1754%, Wilson [57.3357%, 80.4674%], so the real discrimination control could act on nearly everything and the synthesised side was needed for 1 falsifier across 2 runs — 0 in run 1, 1 in run 2. But that single probe, run 2's C0017, returned `INTEGRITY_VIOLATION → indeterminate` and could not speak, **because of B9**. So B9 blocked the post-run sweep as well as in-run verification, and 2 programme measurements were gated on the same staging fix: this arm and the key property. Both are unblocked by the B9 repair and are re-runnable on the next run.

**`haiku_extended`**, measured from run 1's own log and needing no new run, since `immune_agents.py:4967` sets `_CLASSIFIER_MODEL = "haiku"`. 22 classifications in batches of 14, 2, 5 and 1, and the 3-way accounting closes exactly: 9 agreed with the regex, 10 overrode it, 3 had the override refused by the MATHEMATICAL guard. Agreement at 40.9091%, Wilson [23.2558%, 61.2652%], beats a 1-in-6 chance baseline at p = 0.006131 and is indistinguishable from a coin flip at p = 0.523467 — unsurprising on a target whose planted defects are a variance estimator and a confidence interval, where 7 of the 10 overrides are exactly `statistical → mathematical`. Confidence 0.70 to 0.90, mean 0.8238, every value at or above threshold; latency 10.6 to 36.5 s, mean 18.61 s, 241.9 s total. Of the founder's 3 clauses, *Haiku decides* and *never blocks* both HOLD — the 3 lines reading "BLOCKED by MATHEMATICAL guard" are Haiku's OVERRIDE being refused, so the guard blocks Haiku rather than Haiku blocking anything, and 0 findings were withheld — and *syntax raises confidence* is NOT MEASURABLE from a run log, because the classifier records 1 confidence per classification and no pre-syntax value. Filed as a MEDIUM instrumentation gap. Bounded to SEMI-ACTIVE: `llm_primary = (domain == "software")` and both runs are mathematics, so PRIMARY mode is not established.

## A tension in the programme's own design, which is a decision and not a repair

`in_round_clearance` asks whether the UNRESOLVED section elicits the id-addressed `FALSIFIER: Cxxxx` form at all, against an archived baseline of 0 in 3,473 round replies. Run 1 gives 0 of 29 seat replies, Wilson [0.0000%, 11.6970%], Fisher exact p = 1.0000 — and **that zero carries no verdict**, because the form can only be supplied if an UNCONFIRMED critical was rendered for a seat to address, and run 1's maximum unconfirmed-critical count was 0. The success criterion is 3 consecutive CLEAN convergences, a clean convergence leaves no unresolved criticals, and that is precisely the state in which this arm cannot be read. The better the runs go, the less measurable it becomes. 3 options are recorded: accept it as unreadable on clean runs and read it only from runs that stall; seed a run with a known unconfirmable critical; or replay the archive's 175 attributed blockers through the repaired `build_summary` and measure elicitation against the corrected prompt rather than a live run.

## The programme went from 5 outstanding measurements to 1

`directive_delivery`, `severity_promotion`, `coherence_budget_recalibration`, `guard_reach`, `in_round_clearance` and `haiku_extended` all now carry results, and 4 of the 6 were answered from the runs' own completed logs with no additional dispatch. **Only `arm5` remains, and its cost has doubled**: its core confound still holds, because `bench/BUILD_BOT_TEST_BENCH_FIX_SPEC.md` is byte-identical at `a2a0197` and HEAD at 3,498 bytes with the same SHA-1, but its design names `study_run1b_2026-10-03` as the HEAD arm because that run WAS HEAD when the design was verified, and HEAD has since moved 141 commits, 3 touching the composer and 24 the runner, including the directive repair arm5 exists to evaluate. So it is 2 free runs rather than 1 to speak about current machinery.

## The board, and why it is red by arithmetic

The pre-fix board was 1 failed, 11,278 passed, 18 skipped in 3497.35 s, from `python3 -m pytest bench/tests/ -q`. The single failure is `test_task_list_burndown_2026-09-11.py::TestTheConvergenceArgumentRestsOnTheRightThing::test_closure_outpaced_discovery_on_the_latest_full_day`, and it is red for the right reason: *"on 2026-10-15 the list gained 6 entries and closed 2; the convergence argument no longer holds and any ETA resting on it must be withdrawn."* Today created B4 through B9 and has closed B4, B5, B7 and B9, so the day stands at 6 gained against 4 closed. **The test requires closures to OUTPACE discovery, and that cannot be reached today by honest means**: it would need 7 closures against 6 entries created, and closing an item that is not done is exactly the dishonesty the test exists to prevent. A post-fix board is running at the time of writing.

## Cost

Neither run spent money. `bench/tools/sim_dispatch_shim.py` patches `_dispatch_single_model`, the single point at which a paid model would be called, every seat label carries the `-SIM` suffix at source, and the spending limit is 0.00. No archived run can be replayed against the current composer and expected to reproduce, which is the price the directive repair was parked for and which the founder accepted in terms.

Written under CDSFL note standard v1.7 (26 August 2026).
