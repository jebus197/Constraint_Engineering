# Morning report, 8 October 2026: gamma gates everywhere, and 6 of my own figures were wrong

2026-10-08 04:34 BST

## Summary: what changed, what the panels found, and what needs a ruling

Overnight work ran from the ladder-allocation question through to a repair of the convergence gate. 3 free panel rounds were dispatched, 0 paid, every one landing both seats on the first or second attempt. 11 commits, all on `sim/shakedown-2026-09-29`; `main` untouched.

The single most consequential change is that **gamma now gates in every case where a decay curve exists**, and where no curve exists the 2 proven guards from the sibling gate apply, one of which refuses convergence outright. That took 3 attempts and 2 corrections from the founder, and the final form is the one he forced rather than the one first offered.

The most uncomfortable fact in this report is that **6 figures carried to a panel in briefs written overnight were wrong**, and in every case a seat found the error rather than the author. They are listed in full below, because the founder decides what matters, not the summariser.

## What was fixed and is now live

**Gamma gates wherever a curve exists.** `_check_hardened_convergence` previously made gamma "reported-not-gated" whenever the cumulative critical pool fell below `gamma_crit_min_cumulative`, which defaults to 8 and is set by only 4 of the 47 experiment configs. So the gate described throughout the project as two-sided went one-sided in precisely the endgame regime, and the surviving half — the zero-novel-critical window — is the half a shrinking roster attacks. Found by the fable seat.

The founder ruled: gamma remains active in all cases. The first attempt gated gamma wherever it was estimable and labelled the rest "unestimable", and he rejected that as the demotion renamed. He was right: in that branch gamma still did not gate. The final form separates the estimator's 4 reasons for returning 0.0 — too few rounds, an all-zero series, fewer than 2 usable log points, a degenerate fit — gates gamma wherever a slope genuinely exists, and routes the no-curve case to the vacuous-curve logic already proven in `_check_gamma_alt_convergence`, which carries 2 guards: cumulative critical over the whole history must be zero, and the panel must have produced findings of some severity. The second guard **refuses** convergence, which is what makes this a narrowing of the estimator's domain rather than a demotion of gamma.

Reachability was measured, because a change that bites nowhere is an unwired addition and this project has 11 confirmed defects of that shape. An exhaustive sweep found `[1, 3, 0, 0, 0]` at gamma 0.1783 and `[1, 4, 0, 0, 0]` at 0.0461 — both sparse, both with the window met, both converging before and refused now.

**The gate's mode is now on the round record.** It previously reached the log file and nothing else: a scan of every report under `bench/logs` for a record carrying a mode returned 0, so no archived run says which mode closed it. The ruling would have been unauditable even once implemented.

**Recovery survives an unreachable network.** `git_state` fetched unconditionally, so `rs`, `sv` and `qc` all crashed when the link was down — 11 of the 25 failures on the 2026-10-07 board were this single cause. A call that cannot run now reports what a failed call reports. The P-pass then caught a worse defect the fix would have widened: `git status --porcelain` prints nothing for a clean tree, so "I cannot see the tree" was rendering as "the tree is clean". The return code is now read rather than inferred, and `cdsfl_recover` reads that direct signal in place of a proxy that missed the case where `git log` works and only `git status` fails.

**Fable is the 6th rung on the falsifier ladder**, placed last because its lower confidence bound on resolve-rate is 0.0000 on 0 attempts. The position is derived from evidence, not chosen by name. Verified by execution that a capped run still dispatches exactly the same 2 seats, so nothing was displaced. The other half is not done and is a ruling: no config declares Fable, so the rung is unreachable in those runs, and changing 23 routed configs alters what real experiments dispatch.

**A standing offline-recovery resource exists** at `experimental_notes/OFFLINE_RECOVERY.md`, with a 10-step sequence whose every command was confirmed to make no network call. It says plainly not to run `rs`, `sv` or `qc` while the link is down.

## What the 3 panels established

**Round 1, ladder allocation.** Both seats overturned the brief's own evidence. `competence_provenance.falsifier_style` misclassifies 740 of 1078 archived falsifiers, 68.6456%, Wilson [65.8141%, 71.3448%], as detached because it tests for file-opening while the directive requires an import. Only 20 are genuinely detached.

**Round 2, dynamic roster and derived ladder.** Both seats: sound with repairs. The sharpest finding was the endgame one-sidedness above. The second sharpest was a number nobody had: the gate's absolute false-quiet rate at FULL roster is 0.1159, which no roster-aware fix addresses.

**Round 3, earned rungs and opaque identifiers.** Both seats: sound with repairs on all 3 pillars. Both independently named the missing third seat state a circuit breaker and both found the term is already the project's own, in the user-interface vision sketch from March. Both rejected randomly assigned identifiers in favour of a digest over the output-affecting configuration, which contradicts the founder's wording while serving his intent: measured, 2 instances of 1 configuration under split records need 21 rounds to separate 0.8 from 0.4 where pooling needs 11, so random keys double the cold-start price for no benefit.

## The 6 figures that were wrong, and who found each

1. **q assumed at 0.3.** Measured 0.233740, Wilson [0.215572, 0.252945], and rejected by an exact binomial test at p = 5.6e-11. Found by cc2. A second seat measured 0.1994 on a wider population.
2. **A spurious-convergence factor of 8.49986 stated as a property of the gate.** It is an upper bound holding only under independent seats. At the measured correlation and rate the operative figure is near 1.4, and the 6-seat-to-2-seat overstatement is 29.1-fold. Found by self-audit, then confirmed by both seats.
3. **A sensitivity span of 7.7915 described as spanning a plausible range.** It spans a correlation of 0 to 0.8; over the 0.1 to 0.5 range actually quoted the correct value is 6.053. Found by fable.
4. **A confidence interval placed on exact arithmetic.** A 6-name tuple ordering 6 of 70 seats is 3/35 exactly, with no estimator and no sampling variability. Found by cc2, who put it best: an interval on a quantity with no estimator is nobody's uncertainty.
5. **A difficulty check that scanned field names and never executed the function it claimed to verify.** It would have reported success whatever the recorded values were. Found by cc2. Rewritten to call the real routing function, which then confirmed the censoring it was supposed to detect.
6. **A claim that rotation costs no extra dispatches.** Measured against the real stop-at-first-confirmed semantics: 579 dispatches for 270 resolved under rotation against 444 for 396 under strength order, so rotation costs 30% more dispatches and resolves 32% fewer findings. Found by cc2. This one had been reported to the founder as free, and is withdrawn.

A seventh correction belongs to the founder rather than a seat. A criticism of his rung ladder — that promoting on a single success keeps a genuinely capable model out 40.951% of the time — rested on an absorbing rule he never described. Under his actual reading, where a model stuck at a rung keeps receiving that rung's work, capability sets the rate of climb rather than whether a climb is possible: expected attempts 5.56 at a 0.90 success rate against 50.00 at 0.10, a 9-fold difference. Under a bounded horizon that rate is itself the selection, with no threshold required: at 10 attempts per rung a 0.90 model reaches the top 0.9998 of the time and a 0.10 model 0.0016, a factor of 625.

## What needs a ruling

**The promotion-gate parameters, because 3 derivations give 3 answers and the difference is the targets, not the arithmetic.** 19 attempts per rung with 11 successes, 19 with 14 at a floor of 0.50, and 12 with 8 at an implied floor near 0.39. Each verifies minimality under its own stated error budget. And all 3 assume independent attempts: at the measured intra-round correlation with 3 attempts per finding the design effect is 1.5506, so 19 independent-equivalent attempts need 30 actual ones. 19 is a floor.

**The tier count, which is not a free parameter and is not monotone.** 4 tiers cost 68 attempts to climb, 5 cost 95, 7 cost 91 — fewer than 5 — 11 cost 132 and 20 cost 220. The founder's own four-division instinct lands on a local optimum. Because the cost curve is not monotone, how many tiers to have must be scanned rather than reasoned to.

**Whether the convergence gate should READ the live roster or merely record it.** Recording lets a researcher detect a short-roster convergence afterwards; making the gate read it prevents one. Both seats proposed the second. The founder's framing was the first. His separate instruction to fix the 0.1159 full-roster rate is a gate change either way, since that case arises with every model present.

**The 5 items from yesterday's rulings that are not yet built:** the 0.1159 rate; flipping the ladder-depth default to exhaust, which changes what 23 routed configs dispatch; the order-versus-feasibility split in both runners, where a scalar governs ordering and a separate constraint governs a hard-capped resource; resetting the dispatch caps and retry budget from the measured distribution, where 1800 seconds sits below the 95th percentile of 2426 seconds; and replacing the shared-credential lock with a short stagger, which cost 2505.6 seconds — 41.76 minutes, a 46.15% increase in wall clock — across last night's 3 rounds on evidence recomputed at p = 0.107550.

**One mechanism correction to carry into that last item.** An idle timeout was recommended as strictly better than a fixed cap. fable refuted it with 2 adversaries: a process emitting 1 line every 0.5 seconds is never idle and runs until a total cap, and a working process with buffered output showed 0 bytes at a 2-second idle cap and was wrongly killed, while the same process unbuffered completed at 3.1 seconds. The idle clock can measure the output buffer rather than the model. It needs an unbuffered stream and a generous total backstop; each component alone fails a demonstrated adversary.

## Status

A 4th free panel was dispatched at 04:32 on the gamma fix itself, with both seats alive on the first attempt and 0 paid. Its brief asks the seats to find a path where gamma is excused without a guard, to find a case where a dead panel converges or a clean target is refused, and to widen the shared-input test between the estimability predicate and the estimator. Its result is not in this report.

Every panel round is preserved: records mirrored 124 of 124, seat-written files harvested, and a FULL RECORD note per round carrying both replies unfiltered.

Written under CDSFL note standard v1.7 (26 August 2026).
