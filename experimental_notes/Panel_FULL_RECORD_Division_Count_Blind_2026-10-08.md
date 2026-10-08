# Both seats refute the brief, and the division count turns out to be derivable

Record written 2026-10-08T14:49:38+01:00.

**This is the seats' own output, reproduced in full.** The Personalisation directive requires external review output preserved *"in full and in unfiltered format"* and says *"Never summarise in place of the full output"*. Any summary elsewhere is downstream of this file, not a substitute for it.

The BLIND half of a star-topology pair. Both seats answered without seeing each other; the joint round follows. 0 paid dispatches.

WHAT IT ASKED. Three things the founder raised on 2026-10-07 and 2026-10-08. Whether the number of promotion divisions can be DERIVED at the start of an experiment from the relative complexity of the task and the available resources. Whether cost monotonicity in the number of divisions is a theorem or a scan result. And how a model is RELEGATED on sustained degradation, with his standing guard that a run of failures on hard problems must not demote a capable model, and that a tally of successes must never be mistaken for improved capability.

BOTH SEATS REFUTED THE BRIEF, AND ON THE SAME POINT. The brief had already withdrawn one CC1 claim (that the cost curve is not monotone) and replaced it with another: that "as few divisions as possible" is right on the attempts metric and a single gate is the floor. Both seats falsified the replacement with executed witnesses at budgets the brief had not examined. At capable 0.90 against weak 0.30 with budget (0.95, 0.01), 3 divisions cost 10 attempts where 2 cost 11. At capable 0.90 against weak 0.50 with floor 0.85 and ceiling 0.26, 3 divisions cost 4 where 2 cost 5. One seat measures the inversion rate at 9 of 48 feasible budgets, 0.1875, Wilson (0.1019, 0.3194); the other finds 3 inversions and 5 free divisions over a 48-setting grid. CC1 reproduced one witness exactly, scipy against mpmath agreeing to 0.000e+00.

SO THE ORIGINAL CONCLUSION WAS RIGHT FOR THE WRONG REASON. The producer CC1 withdrew concluded that the division count must be SCANNED. That conclusion survives; the identical-gate reasoning behind it did not. The correct justification is a per-budget scan, which is cheap and deterministic.

AND ONE SEAT RESOLVED THE MONOTONICITY QUESTION IN BOTH DIRECTIONS AT ONCE, which is the round's deepest result. The brief asked whether monotonicity is a theorem or a scan result and offered "arbitrary tests" as the modelling liberty a proof would need. That framing conceded too much and asked too little. Under DETERMINISTIC success-count thresholds monotonicity is not unproven, it is FALSE. Under RANDOMISED thresholds it is a THEOREM by Karlin-Rubin, because the binomial family has a monotone likelihood ratio and the most powerful test of a given exact size is a randomised threshold on the total success count -- and the AND of two separate gates is itself a test of that size on the concatenated sample, so it cannot beat the optimum. A randomised threshold is the standard completion of the binomial test family, far narrower than arbitrary tests. The brief's own measurement of 801 merge failures in 4000 pairs was the clue and was read as a negative result: all 801 are repaired by randomisation alone. CC1 verified this independently and reproduced the seat's own residuals to the digit, 801 of 801 repaired, worst power slack -4.441e-16 and worst size excess 8.674e-19, with SymPy giving log(9) for the likelihood-ratio slope and z3 returning unsat on the search for a capable rate above a weak one with non-positive slope.

THE FOUNDER'S QUESTION HAS TWO ANSWERS AND THEY DISAGREE, which is preserved rather than resolved here. Both seats derive the number of divisions from RESOLUTION rather than from cost, and both identify relative complexity with an arcsine span -- 0.4636476090 over the interval 0.5 to 0.9 in one seat's form, 0.9272952180 in the other's, which doubles it -- and available resources with the number of attempts of evidence available per model per window. They differ in the constant and the exponent: one gives T as 1 plus the floor of the arcsine gap times the square root of the sample over a fixed critical value; the other doubles the gap, makes the critical value depend on the division count, and raises the whole bracket to a power that differs between pooled and serial accounting. One seat additionally reports that the ATTEMPTS objective is degenerate, returning 2 divisions always, so it cannot derive the count at all -- which makes the brief's section 3 the answer rather than a caveat. The joint round must reconcile the two formulae.

RELEGATION PRODUCED TWO DIFFERENT MECHANISMS, BOTH ANSWERING THE FOUNDER'S GUARD. One seat proposes an exact one-sided sign test over discordant pairs against the division-peer majority on the same scored attempts, with the pairing itself as the hard-problem guard: when the task stream hardens, model and peers fall together, parity holds and nobody is demoted. CC1 simulated it: with the stream hardening under an equally capable peer, an absolute floor demotes a capable model 98.35 percent of the time, Wilson (0.9791, 0.9870), against 3.65 percent for the sign test, Wilson (0.0311, 0.0428), while on genuine decline the sign test fires 99.68 percent against the floor rule's 96.27 percent. The other seat proposes a one-sided CUSUM on Rasch residuals against measured item difficulty, with no window at all, the demotion threshold solved from a target average run length, and promotion as the mirror CUSUM at the same threshold so that symmetry is structural rather than a second mechanism. It also reports that the OBVIOUS stratified statistic violates the founder's guard outright: under escalation the stratum varies only when the model succeeds, so 228 of 400 observations drop as degenerate and every survivor carries the identical residual, making the statistic a success count in disguise with a correlation to skill of not-a-number. Repaired on measured difficulty the correlation is 0.991.

AND ONE SEAT PRICED A PRECONDITION NOBODY HAD ASKED FOR. Escalated items carry about 14 times less relegation information than calibrated ones, because Fisher information per observation collapses as the success probability falls; a 1.5-logit decline goes undetected at calibration shares up to 0.20 and is caught only from 0.40. So relegation has a derived resource requirement that the attempts-optimal ladder does not price.

BOTH SEATS FALSIFIED CLAIMS OF THEIR OWN AND REPAIRED THEM RATHER THAN REVERTING. One replaced a two-sample separation gap with a one-sample form after its own falsifier rejected it, and replaced a peer-conditioned Bernoulli model with a paired one for the same reason. The other reports its derived transient-outage bound as UNSAFE as stated, holding only while the residual standard deviation stays below one half, and safe only with the increment Winsorised.

CC1's OWN STANDING. Three of CC1's claims are withdrawn by this round: the non-monotonicity conclusion as originally reasoned, its replacement that fewer divisions are always cheaper, and the assertion that some rate pairs are infeasible at any division count -- which was CC1's own per-gate attempts ceiling binding, not a property of the task. One seat gives that last one a correct form: infeasibility is real for a FIXED evidence budget and has a formula, which reconciles the two positions by quantifier rather than by preference.

PROCEDURAL NOTE, because it cost a round. CC1 killed an earlier cc2 retry after inspecting its sandbox and finding the co-seat's reply in it. The sandbox was mid-build: the copy had completed and the purge had not yet run. The purge ran 37 seconds later and the sandbox afterwards held only the brief. The containment control had worked; the observation was taken too early, and the build-completion marker was absent at the time and was explained away as output buffering.

## Seats and cost

2 seat(s): `cc2`, `fable`. **0 paid dispatches**, enforced by `PANEL_ONLY=cc2,fable`.

## The brief, as dispatched

<!-- verbatim-begin: the brief as dispatched -->

# Can the number of divisions be DERIVED from task complexity and available resources?

You are one seat of a 2-seat panel, answering BLIND. You cannot see the other seat's
reply and it cannot see yours. A joint round follows once both blind replies are in,
and in it each of you will see the other's answer. Disagreement between you is the
output this round exists to produce, not a problem to be smoothed away: a round that
agrees by deference has produced nothing.

Work in the sandbox repository tree you have been given. RUN things. Every figure
below names the script that produces it, and you are expected to execute those
scripts and contradict them where they are wrong. The tool output is the evidence.

**A previous attempt at this round was discarded, and you should know why.** It was
dispatched as a lone blind round with no joint round planned — which is not star
topology — and one seat's retry was handed the other seat's landed reply because the
sandbox builder had no way to purge a co-seat's artefacts. Both faults are fixed and
held by tests. Nothing from that round is in your tree.

---

## 1. The founder's framing, in his own words

**Capability is a MEASURED RATE. Model names are not a measure of anything.** He has
said this 4 times. The roster size is arbitrary and the schema must not care:

> "the system should be able to cope with 5, or 6, or 70, or 700 models (or whatever),
> and that the only goal is to use all the available resources efficiently to effect
> the best outcome in all cases."

**The divisions are FINITE:**

> "we clearly don't have infinit[e] divisions, we have division 1, division 2,
> division 3, the Premier League. So the number of possible leagues is finite. The
> position each team or player operate[s] in within these bou[nd]s is also finite."
> ... "We also have the Vauxhall conference and the other lower leagues. But either
> way the number is bounded, not infinite."

**THE QUESTION HE IS NOW ASKING, 2026-10-08, and it is the centre of this round:**

> "I get that doesn't settle how many leagues there should be, and if that can be
> mathematically derived at the start of an experiment, based on the relative
> complexity of the task, and the available resources? That is probably a question you
> should ask the next panel."

**AND THE SYMMETRIC HALF, which is unbuilt:**

> "just as teams and players can be promoted over time through a period of sustained
> performance, clearly they can be demoted by the opposite framing. If they demonstrate
> sustained degradation, they can face relagation to a lower league, and a lower rung
> on the ladder."

With his standing guard on what may count as evidence of change:

> "what we need to guard against is simply counting when a model is successful as an
> 'improvement in capability'. The only measure of improved capability is actual
> observed capability (and the converse.)"

And on seat timeouts: "A full response is always preferable", and results should be
harvested when a model is done rather than at an arbitrary wall-clock limit.

---

## 2. Where the arithmetic actually stands, including a claim of mine that is WITHDRAWN

`bench/the_division_count_is_bounded_and_the_cost_is_not_monotone_2026-10-08.py` prices
the climb. Climbing T divisions means clearing T-1 promotion gates in series; the
end-to-end budget is held fixed across the scan — a model whose true resolve rate is
0.90 reaches the top with probability at least 0.95, one at 0.50 with probability at
most 0.01 — so the comparison is about division count and nothing else.

**ITS HEADLINE CONCLUSION WAS WRONG AND IS WITHDRAWN.** That file claims the cost curve
is not monotone and therefore that the division count must be scanned. The claim is an
artefact of its own `smallest_gate`, which forces every gate in a ladder to the SAME
(attempts, successes) pair. The budget constrains only the PRODUCTS of per-gate pass
probabilities, so heterogeneous gates are admissible and the identical-gate costs are
upper bounds rather than optima. Optimised properly over heterogeneous threshold gates
the curve is monotone non-decreasing:

    divisions  2   3   4   5   6   7   8   9  10  11  12  13  14
    attempts  19  21  22  25  28  30  33  36  38  41  42  45  48

against the identical-gate figures 19, 28, 30, 36, 40, 48, 49, 56, 63, 70, 66, 72, 52.
**0 downward steps, 0 inversions.** A concrete witness: for 4 divisions the ladder
[(2,1), (2,1), (18,14)] costs <!-- figure: four divisions optimum | scripts/the_division_count_is_derivable_2026-10-08.py | optimum: 22 --> 22 attempts with end-to-end capable 0.9524672012 and weak 0.0086860657, both inside the budget, against the committed 30. scipy and mpmath agree to 0.000e+00 and Wolfram Language (local Wolfram Engine) returns the same 2 values to 10 digits.

**So "as few divisions as possible" IS right on the attempts metric, and a single gate
at 19 attempts is the floor.** That inverts what the previous brief asked you to assess.

**AND ONE SUPPORT FOR THAT RESULT DOES NOT SURVIVE, which is a live disagreement rather
than a settled point.** The monotonicity can be argued from a merge construction:
collapse 2 adjacent gates into 1 composite rule on the concatenated attempts and total
attempts and end-to-end error are preserved, so cost(T) <= cost(T+1). Tested over 4000
random gate pairs, **801 of them have NO single threshold gate on a1+a2 attempts that
dominates the AND of the 2 separate gates on both criteria** — so the merge is not a
lemma within the threshold family. It holds only if a ladder's gates may be arbitrary
tests rather than success-count thresholds, which is a modelling decision nobody has
made. Monotonicity therefore currently rests on a SCAN, not a proof.

**A robustness sweep over other rate pairs and budgets is available and is NOT quoted
here, deliberately.** `scripts/the_division_count_is_derivable_2026-10-08.py --sweep`
runs it; it is slow, so it is off by default. Run it and report what you find rather
than taking a number from this brief. Two things worth looking for: whether any
setting produces an inversion, which would settle question 2 immediately; and whether
any setting makes an extra division FREE, because the price of a division depends on
the gap between the capable and weak rates and a free division should be taken. Note
also that some rate pairs are INFEASIBLE at any division count — below a certain
separation no ladder meets the budget — which is itself part of the answer to his
question.

---

## 3. What the attempts metric does not price, and why that is the crux

Total attempts treats every attempt as overhead. It is not. A model sitting in a lower
division is DOING THAT DIVISION'S WORK while it climbs, and that work has value; a model
in front of a single gate performs 19 attempts of pure qualification and produces nothing
a researcher can use. Nothing in the repository measures the value of work done during
the climb. Relatedly, the attempts-optimal ladders concentrate all discrimination in one
strong gate and make the rest formalities, which buys end-to-end certification and
near-zero intermediate PLACEMENT — and placement is what a routing ladder exists for.

Two committed producers price a 5-level ladder at 95, 36 and 25 attempts respectively
under the same end-to-end budget, because they price different quantities. Run
`bench/what_several_tries_has_to_mean_2026-10-08.py` and the scan above and compare.

---

## 4. Figures previously carried to a panel that are WITHDRAWN

Reason from the corrected values. Several were found by seats.

1. The per-seat-per-round critical rate was assumed 0.3; measured it is **0.233740**, Wilson [0.215572, 0.252945], exact binomial p = 5.6e-11 against the assumption.
2. A spurious-convergence factor of **8.49986** was stated as a gate property; it is an upper bound under independence. At the measured intra-round correlation 0.4060 the 6-seat-to-4-seat factor is **1.4291**.
3. A sensitivity span of **7.7915** spans correlation 0 to 0.8; over the quoted 0.1 to 0.5 it is 6.053.
4. "Rotation costs identical dispatches" is **WITHDRAWN**: 579 dispatches for 270 resolved against 444 for 396.
5. Pooled correlation is confounded **1.7202x** by between-experiment variation; simulated runs give 0.681 against 0.275 live.
6. The tier-cost figures "52 to 182 attempts", "7 tiers cost 91 where 5 cost 95" and "4 divisions a local optimum at 68" **do not reproduce**. The scan gives 19 to 72; 7 divisions cost 48 and 5 cost 36; 4 cost 30 and are not a local minimum because 3 cost 28. They were computed with no committed producer.

---

## 5. Also live, since you may reason from the convergence gate

- **Gamma gates wherever a slope exists**, including the sparse branch where it previously went reported-only. Gamma is load-bearing in this project and is NOT up for demotion.
- **The gate's 2 arms are positively DEPENDENT, measured.** The real gate, called on all 23 archived premature quiet windows, fired on **23 of 23**, Wilson [0.856883, 1.0], with gamma above 0.30 in every one. Gamma is systematically higher inside a quiet run, median 0.45905 against 0.3975, Mann-Whitney one-sided p = 0.025542, because quiet rounds are what flatten the curve gamma measures. Producer: `bench/the_false_quiet_rate_is_not_the_gates_rate_2026-10-08.py`. A dependent second arm is still a second arm; what it cannot do is cover the other arm's false-positive rate.
- **The ladder-depth default is exhaust**, `routing.DEFAULT_MAX_RUNGS = 0`. Over 305 archived routing records 143 hit the old cap of 2 and 103 were abandoned unresolved.

---

## 6. What to decide

1. **Can the division count be DERIVED at the start of an experiment from task complexity and available resources?** This is his question and it is the one that matters. If it can, give the derivation: name what "relative complexity" is as a measurable quantity, name what "available resources" bounds, and produce T as a function of them. If it cannot be derived, prove that and say what must be measured first.
2. **Is monotonicity a theorem or a scan result?** Either supply a proof valid within the threshold family, or show a counterexample, or establish that gates may be arbitrary tests and justify that modelling choice.
3. **RELEGATION, which is unbuilt.** Name the statistic, the window and the decision rule by which sustained degradation demotes a model — and the mechanism that distinguishes sustained decline from a transient outage, remembering that no model is ever benched and a transient fault is a different condition. State what stops a run of failures on hard problems from demoting a capable model, given that a model high on the ladder is handed the problems everything below it failed.
4. **What stops a success count being mistaken for improved capability?** His explicit guard, and it needs a mechanism.
5. **Does the structure survive a roster of 700? And of 1?**

## 7. Output

Return these fields, each with a real body. A heading with nothing under it is not an answer.

- `## Verdict` — SOUND, SOUND WITH REPAIRS, or UNSOUND, on the position set out above.
- `## Findings` — each labelled OBSERVED (name the run, file and line) or HYPOTHESISED (say what would settle it), each with a severity, each with the command that shows it.
- `## Fix` — deliver each fix as a file at its real path in the sandbox repository tree, with an executed falsifier beside it and the falsifier's actual output pasted. A fix you have not tried to break is a hypothesis, not a fix. Repair rather than revert where both are available.
- `## Disagreement` — your strongest disagreement with this brief's own framing, named as a disagreement. If a figure above is wrong, say which and show the command.
- `## What would refute me` — the measurement or command that would overturn your own verdict, stated so someone else could run it and defeat you.

## 8. Termination

Stop when further passes produce no new above-threshold findings — above threshold means
missing it could cause real-world failure. Do not nitpick, do not generate findings for
their own sake, do not police style. Diminishing returns is the stop criterion, not the
clock. Take the time you need for a full response.

Numbers in digits, never in words. No model names where a rate will do.


<!-- verbatim-end -->

## Seat: cc2

Route `claude_cli`, 46 recorded tool call(s).

<!-- verbatim-begin: cc2 (panel division_count_blind_2026-10-08) -->

## Verdict

**UNSOUND** on the brief's headline arithmetic; sound on its §3 framing and on the withdrawal it already made.

Three parts of the brief's position stand: the `smallest_gate` withdrawal is correct (identical-gate costs *are* upper bounds); §3's crux is correct (attempts price certification, not placement); and the committed-figure withdrawals in §4 reproduce. Two parts fail with executed witnesses:

1. **"0 downward steps, 0 inversions … so 'as few divisions as possible' IS right on the attempts metric"** — false. At capable 0.90 / weak 0.30, end-to-end budget (0.95, 0.01), per-gate cap 14: **3 divisions cost 10 attempts, 2 cost 11.** Exhaustive enumeration, not a pruned DP. The brief's 0 inversions is a single-rate-pair result at (0.90, 0.50).
2. **"Monotonicity currently rests on a SCAN, not a proof"** — false in both directions at once. In the deterministic threshold family it is not unproven, it is **false**. In the randomised threshold family it is a **theorem**, and the modelling step is not "arbitrary tests" but the standard completion of the binomial test family that Neyman–Pearson is stated over.

And the derivation the founder asked for exists: **T is derivable in closed form**, validated 6/6 against the brief's own exact binomial DP.

---

## Findings

**F1 — The deterministic division-cost curve inverts. (OBSERVED, CRITICAL)**
`scripts/the_merge_lemma_is_neyman_pearson_2026-10-08.py` claim 7. Two witnesses by exhaustive enumeration of all 1-gate and 2-gate ladders:

| rates | budget | cost(T=2) | cost(T=3) |
|---|---|---|---|
| 0.90 / 0.30 | (0.95, 0.010) | 11 — `[(11,8)]` | **10** — `[(2,1),(8,6)]` |
| 0.95 / 0.30 | (0.90, 0.050) | 5 — `[(5,4)]` | **4** — `[(2,1),(2,2)]` |

Witness 1 end-to-end: capable 0.9522891279, weak 0.0057590271, both inside budget. scipy vs mpmath 8.674e-19. Wolfram Language (local Wolfram Engine, exit 0) returns 0.9522891279 and 0.0057590271 to 12 digits.
`python3 scripts/the_merge_lemma_is_neyman_pearson_2026-10-08.py`

A third inversion and 5 free divisions appear over a 48-setting grid (3 inversions total, 30 feasible / 18 infeasible). **A division is better than free at witness 1** — which refutes "as few divisions as possible" on the brief's own metric.

**F2 — Monotonicity is a theorem under randomised threshold gates. (OBSERVED, CRITICAL)**
Same file, claims 2–4. The merge lemma holds at **0 of 4000** pairs failing (worst power slack −4.44e-16, worst size excess 8.67e-19), and **all 801** of the brief's deterministic failures are repaired by randomisation alone. The Neyman–Pearson premise is checked: `d/dS log L = log(9)` at the brief's rates (SymPy), and z3 returns `unsat` on the search for capable > weak with non-positive log-ratio slope — so the family has monotone likelihood ratio and the most powerful test of size exactly α is a randomised threshold on the total success count. Proof of both lemma and theorem is in the file's docstring.

The mechanism is visible in F1: at witness 1 the merged randomised gate on n=10 achieves power 0.9834296545 at size exactly 0.01, while the best **deterministic** gate on n=10 reaches only 0.9298091736 — short of the 0.95 floor. That gap *is* the inversion. Wolfram confirms γ = 0.9342258766 and power 0.9834296545 to 12 digits.

**F3 — T is derivable; the attempts objective cannot derive it. (OBSERVED, CRITICAL)**
`scripts/the_division_count_is_derived_from_resolution_2026-10-08.py`. On the attempts objective the optimum is degenerate — T = 2 always — so it can only ever return "as few as possible". The derivation is resolution:

- **Relative complexity** = the span the task set induces in the roster's measured resolve rates, in arcsine coordinates: Δφ = 2(arcsin√p_hi − arcsin√p_lo). Measurable before the ladder exists, from the resolve-rate records promotion already uses. A task set everyone solves and one nobody solves both give Δφ → 0 and support exactly 1 division.
- **Available resources** = N, attempts of evidence per model = B/R. No other roster term enters.
- **T** = 1 + max{t : t ≤ (Δφ√N / z(t+1))^κ}, κ = 1 pooled, 2/3 serial.

Δφ = 0.927295218002 at the brief's rates (Wolfram Language, local Wolfram Engine). **Validation: 6/6 agreement with the brief's exact binomial DP** on all its sweep settings including both it marks infeasible — "some rate pairs are infeasible at any division count" now has a formula: Δφ√N < z_sum(2). **Tightness: at N = 2000 the derived T = 11 holds the per-boundary error at 0.04475 ≤ 0.05 and T = 12 fails at 0.06625.** Wolfram independently gives the bound 10.5792512465 → T = 11.

**F4 — Certification and placement have different error algebras, and the brief prices the one that does not bind. (OBSERVED, HIGH)**
Same file, claim 4. The scan curve rises 2.4615 attempts per division — linear. Placement needs N ∝ (T−1)³ serial. Placement exceeds certification **from T = 3**, and by T = 5 the ratio is 45.75× (25 attempts against 1143.7). Certification lets per-gate error be loose because the weak model need fail only one gate, so z_sum *shrinks* with T (3.971 at T=2 → 1.962 at T=22); placement gets no such help.

**F5 — The natural relegation statistic violates the founder's guard. (OBSERVED, CRITICAL)**
`scripts/relegation_is_a_cusum_on_stratified_residuals_2026-10-08.py` claims 3–4. Per-item stratification (Cochran–Mantel–Haenszel / conditional logit) is the obvious statistic and it fails: escalation sends a division only the items everything below it failed, so the stratum varies **iff the model succeeds**. Measured: 228 of 400 observations dropped as degenerate, and every survivor carries the identical residual **2.236068 = √5**. Correlation with skill is `nan` across skills [0,1,2,3] — the statistic is literally a success count. Repaired with the Rasch (1-parameter item-response) residual on measured difficulty: residuals [0.0098, 0.3846, 1.2046, 1.8272], correlation **0.991**.

**F6 — Escalated items carry ~14× less relegation information than calibrated ones. (OBSERVED, HIGH)**
Same file, claim 6. Fisher information per Rasch observation is p(1−p), which collapses as p → 0; at the division floor, escalated items sit at p = 0.017986, information 0.017663 against 0.25 at p = ½ — a **14.15× penalty**. Measured consequence: a 1.5-logit decline is undetected at calibration shares 0.00, 0.05, 0.10 and 0.20, and detected only from **0.40** (crossing at observation 60). A stable model is never demoted at any share. So relegation has a derived resource precondition the attempts-optimal ladder does not price.

**F7 — My own derived transient-outage bound is unsafe as stated. (OBSERVED, MEDIUM)**
Same file, claim 2. L_min = ⌈h/(2−k_ref)⌉ = 3 holds only while sd ≤ ½. The standardised residual is unbounded below as the cohort grows (worst z = −14.1421 at cohort 200), and a run of L_min−1 observations demotes at cohort 20 and 200. Safe only with z Winsorised at −2.0, where all 5 cohort sizes hold. Reported rather than quoted.

**F8 — The brief's own sweep contains a free division it does not quote. (OBSERVED, MEDIUM)**
`python3 scripts/the_division_count_is_derivable_2026-10-08.py --sweep` completed at ~22 min: 6 settings, 4 feasible, 0 inversions, and **1 free step** — "wide gap, slack budget" gives `[19, 19, 23, 26, 30, 33, 37, 40]`, so a 3rd division costs nothing. The brief says "a free division should be taken"; its own producer found one. My 48-setting grid finds 5.

**F9 — Whether a per-gate ceiling alone breaks monotonicity: HYPOTHESISED, not shown.**
My predicted counterexample failed. Claim 6 scans per-gate ceilings 2–12 at (0.90, 0.50) and finds **0 inversions**. It did surface something else: under a tight ceiling the *low* division counts go infeasible (at ceiling 7, T=2…5 are infeasible and T=6 costs 34) — so a per-gate cap imposes a **lower** bound on T, and "as few as possible" is unavailable there for a second, independent reason. Settled by: find an inversion at a ceiling where a1+a2 exceeds it, or prove monotonicity holds under a cap in the randomised family.

---

## Fix

Three files, all at real paths, all exit 0, each carrying its own falsifier with output pasted above.

| file | fixes | falsifier |
|---|---|---|
| `scripts/the_merge_lemma_is_neyman_pearson_2026-10-08.py` | F1, F2, F9 | reproduces the brief's 801 exactly, then 0/4000 under randomisation; exhaustive 2-gate enumeration for the inversions; SymPy + z3 on the MLR premise; scipy/mpmath to 4.06e-11; Wolfram on 4 values |
| `scripts/the_division_count_is_derived_from_resolution_2026-10-08.py` | F3, F4 | 6/6 against the brief's exact DP; tightness simulation (within at T, over at T+1); Wolfram on Δφ and the T bound |
| `scripts/relegation_is_a_cusum_on_stratified_residuals_2026-10-08.py` | F5, F6, F7 | Brook–Evans ARL Markov chain (ARL0 = 500.0 at h = 4.400221, ARL at −1σ = 9.16); 3 rules on one stream; the calibration-share sweep; Winsorising check |

**Each file falsified one of its own claims and was repaired, not reverted:**
- Claim 1 of the derivation file: plain arcsine spread 0.4955 at N=19 (not stabilised) → Anscombe's small-sample form gives 0.0805, asymptotics give 0.0201 at N=200. The consequence is stated in the file: T_derived is optimistic at small N.
- Claim 6 of the derivation file: v1 sized the per-boundary error from the end-to-end product, giving an 80% target at T=22, and returned `within=False` at both T and T+1 — the tool saying the criterion was wrong. Repaired with `z_place`; now TIGHT.
- Claim 3/4 of the relegation file: F5 above.
- Claim 2 of the relegation file: F7 above.

**Relegation specification, in standard names only:**
- **Statistic** — Rasch residual (y − p)/√(p(1−p)), p = σ(θ_floor − b), difficulty b from `routing.rungs_tried` under exhaustion. That label is exact only under exhaustion (established by `bench/the_promotion_ladder_needs_a_bound_not_a_success_2026-10-08.py` claim 4, which calls `route`), and `routing.DEFAULT_MAX_RUNGS = 0` is exhaust — so relegation is buildable now and was not before the cap lifted.
- **Window** — none. A fixed trailing window must trade detecting a small sustained drop against detecting it soon. Page's CUSUM has no window; the only window is n_min before arming.
- **Rule** — one-sided CUSUM S_k = max(0, S_{k−1} − z_k − k_ref), demote at S_k ≥ h, with h solved from a target ARL0 by Brook–Evans. Promotion is the mirror CUSUM at the same h, so symmetry is structural rather than a second mechanism.
- **Transient vs decline** — excluded by *type*, not threshold: only a resolved-or-refuted dispatch yields a y. A timeout, lapsed licence or empty reply produces no observation, so the CUSUM does not update. This is the founder's "harvest when the model is done" position as a statistical property: a seat that has not finished has not produced a datum. Plus F7's Winsorised increment bound.
- **Hard problems** — difficulty is a covariate, so a failure on a hard item is *expected* and barely debited (0.2231 at difficulty +3 against 4.4817 for a success there; Wolfram: 4.481689070336).
- **Not deployed.** I have not wired a flag into `bench/routing.py`. Two parameters must be measured first and are not in this tree: the residual sd from an archived per-model-per-item outcome corpus, and the empirical outage-length distribution that sets h. Per the additive standard, an unwired flag would be the 12th addition nothing reaches.

**Q4 — success count vs capability, three measured mechanisms:** the decision reads a Wilson *lower bound*, so a perfect 19/19 gives 0.831821 and does not clear a 0.9 floor (50 attempts needed); credit is by surprise (1−p)/sd, so an easy win earns 0.2231 against 4.4817 for a hard one; and the same CUSUM runs both ways. Measured anti-guard: raw success count correlates 0.9939 with skill *only because* my simulation held item selection fixed — under escalation the raw count is what drove the unstratified rule to demote the strongest model at observation 106.

**Q5 — roster 700 and 1:** the formula has no roster term; R enters only via N = B/R. At B = 14000: R=700 → T=2, R=70 → T=3, R=6 → T=6, R=1 → T=10 serial / 28 pooled, R=7000 → T=1 (no ladder). T−1 falls as R^(−1/3) serial. The structure survives both. Relegation does not survive R=1 unchanged: the cohort comparator yields **0 observations of 200** — correct degenerate behaviour, silent rather than wrong — and the Rasch rule survives because difficulty is a recorded number, giving 200 observations, no demotion of a stable model, and crossing at 12 on a genuine decline. The limit at R=1 is intrinsic: a self-referenced comparator cannot separate a capability drop from a task-set shift.

---

## Disagreement

**My strongest disagreement is with the brief's choice to treat monotonicity as an open question about proof technique.** It frames the issue as "monotonicity rests on a SCAN, not a proof" and asks for a proof, a counterexample, or a modelling decision. That framing concedes too much and asks too little, because it never names the gate family precisely — and once named, the question dissolves in opposite directions:

- Deterministic success-count thresholds: monotonicity is **false**, witness above, `cost(3) = 10 < cost(2) = 11`.
- Randomised thresholds: monotonicity is a **theorem**, by Neyman–Pearson in four lines.

The brief's own measurement was the clue and it was read as a negative result. 801 of 4000 failures is not evidence that the AND test is unbeatable; it is the signature of a discrete test family unable to hit the required significance level. All 801 are repaired by randomisation alone, and the repair is not a new modelling liberty — a randomised threshold is the standard completion of the binomial test family, far narrower than the "arbitrary tests" the brief says a proof would need.

**Second disagreement: the brief frames §3 as "what the attempts metric does not price" — a caveat.** It is not a caveat, it is the answer to the founder's question. The attempts objective returns T = 2 for every input; a function constant in its arguments cannot be a derivation. §3's observation is the whole load-bearing content and it is placed in a section headed by what the metric *fails* to do.

**Figures I contradict:**
- "0 downward steps, 0 inversions" — `python3 scripts/the_merge_lemma_is_neyman_pearson_2026-10-08.py` (claim 7), 2 confirmed by exhaustive enumeration, 3 over a 48-setting grid.
- "'as few divisions as possible' IS right on the attempts metric, and a single gate at 19 attempts is the floor" — same command. At (0.90, 0.30) a third division is cheaper than a second.
- "A robustness sweep … Run it and report what you find" — it completed: 0 inversions over its 6 settings, but **1 free division** at "wide gap, slack budget", `[19, 19, 23, …]`. The brief says a free division should be taken and its own producer found one.

**Where I agree against my own interest:** the `smallest_gate` withdrawal is correct, the corrected 13-point curve reproduces exactly, and the 4-division witness `[(2,1),(2,1),(18,14)]` at 22 attempts verifies (capable 0.9524672012, weak 0.0086860657, scipy/mpmath 0.000e+00).

---

## What would refute me

1. **A deterministic-family inversion that randomisation does not repair.** Extend claim 7's exhaustive enumeration to 3-gate ladders over a wider rate grid and find a case where `cost(T) > cost(T+1)` *and* the Neyman–Pearson randomised gate on the summed attempts fails the capable floor. That breaks my theorem, because the merge would then be unavailable even with randomisation. `python3 scripts/the_merge_lemma_is_neyman_pearson_2026-10-08.py`, extend `claim_the_deterministic_curve_ACTUALLY_INVERTS` to `combinations_with_replacement(gates, 3)`.

2. **Randomised promotion gates ruled out on grounds I have not considered.** My theorem needs a gate that may pass a boundary case with probability γ (0.9342258766 at witness 1). If the project rules that a promotion decision must be deterministic given the attempt record — a defensible reproducibility position, and one the falsifier-integrity directive arguably implies — then monotonicity is **false**, not a theorem, and the division count must be scanned exactly as the brief says. This is a modelling decision and I do not get to make it. It is the single most likely way my central claim falls.

3. **The derivation refuted at a setting where it disagrees with the exact DP.** Run `claim_the_closed_form_agrees_with_the_exact_dp` over a larger grid than its 6 settings. Any disagreement cell breaks the closed form. The infeasible cells are the dangerous ones: `python3 scripts/the_division_count_is_derived_from_resolution_2026-10-08.py` — add rate pairs near the feasibility boundary where Δφ√N ≈ z_sum(2).

4. **The tightness result is a seed artefact.** `claim_the_derived_T_is_tight_in_simulation` uses `seed=3`, `trials=4000`, one N. If T = 12 comes in under 0.05 at other seeds, or T = 11 comes in over, the formula is conservative or optimistic rather than tight. Sweep seeds 0–50 and N ∈ {500, 1000, 2000, 5000}.

5. **The 0.40 calibration share is an artefact of my simulated difficulty distribution.** `claim_escalated_items_carry_almost_no_relegation_information` draws difficulty as `gauss(0, 2)` and accepts on 5-model cohort failure. The real escalation distribution is measurable from archived routing records and I did not measure it — I could not find a per-model-per-item corpus in this tree. If the real distribution is less extreme, the required share drops and F6 shrinks from a precondition to a tuning note. `python3 scripts/relegation_is_a_cusum_on_stratified_residuals_2026-10-08.py`, replace the synthetic draw with the archived difficulty histogram.

6. **F5 overstated.** If a real dispatch stream has cohort outcomes that are *not* uniformly 0 on escalated items — because escalation is probabilistic, or cohorts overlap across divisions — the per-item stratified residual recovers variation and is not degenerate. My √5 collapse is exact only when the cohort always fails. Measure the fraction of real escalated dispatches where the cohort outcome is non-constant; if it is well above 0, the CMH statistic is viable and my Rasch repair is unnecessary complexity under the simplest-sufficient standard.

**One tool note:** every Wolfram call ran on the local Wolfram Engine, exited 0, printed no `Name::tag`, and returned no `$Failed`/`$Aborted`. Four values were cross-checked there (Δφ, 2z, the T bound at N=2000, and the inversion witness's four quantities); all agreed with SciPy/mpmath to the digits quoted. Wolfram was never the only source for any claim.

<!-- verbatim-end -->

## Seat: fable

Route `claude_cli`, 36 recorded tool call(s).

<!-- verbatim-begin: fable (panel division_count_blind_2026-10-08) -->

All evidence is in except the committed `--sweep` run, which had not returned after ~20 minutes of wall-clock (it buffers until completion); my committed budget scan reuses the same dynamic program and answers both questions the sweep was built for, so I report from that and say so. Final answer:

---

## Verdict

**SOUND WITH REPAIRS.** The withdrawal of the identical-gate non-monotonicity claim is correct and reproduces exactly (`optimum curve: [19, 21, 22, 25, 28, 30, 33, 36, 38, 41, 42, 45, 48]`, witness `[(2,1),(2,1),(18,14)]` at 22 attempts, capable 0.9524672012, weak 0.0086860657, scipy−mpmath diff 0.000e+00, Wolfram concurring to 10 digits). But two of the brief's general conclusions drawn from it are false, and I have executed counterexamples to both: monotonicity is **not** a theorem at other budgets (so "as few divisions as possible" is not right in general, only at the committed budget), and "some rate pairs are INFEASIBLE at any division count" is a resource-ceiling artefact, not a separation property. The founder's question has a positive answer: **T is derivable at experiment start**, from 2 measured quantities, by the formula and scan below.

## Findings

**F1 — OBSERVED, CRITICAL. Monotonicity fails inside the threshold family; the question "theorem or scan" is settled: scan, and per-budget.**
At budget (cap 0.9, weak 0.5, pc_min 0.85, pw_max 0.26): exhaustive enumeration shows **no single threshold gate with ≤ 4 attempts is feasible** (all 10 candidates checked), the cheapest single gate is (5,4) at 5 attempts (capable 0.91854, weak 0.1875), yet the 2-gate ladder **[(1,1),(3,2)] costs 4 attempts** and is feasible (capable 0.8748 ≥ 0.85, weak 0.25 ≤ 0.26). So cost(3)=4 < cost(2)=5. Verified by scipy, exact mpmath at 50 digits, and Wolfram Language (local Wolfram Engine, via wolframscript): `{0.91854, 0.1875, 0.8748, 0.25}` to 10 digits. The brief's own committed DP, pointed at this budget, concurs: `{2: 5, 3: 4, 4: 6, 5: 7, 6: 9, 7: 11}` — one downward step, and **3 divisions is the strict optimum**, so "a single gate is the floor" is budget-specific, not general.
Command: `python3 scripts/the_division_count_derivation_and_a_monotonicity_counterexample_2026-10-08.py` (claim 1).
Why it inverts: the discrete (attempts, successes) grid of a single gate misses the budget box that a product of two gates' operating points can hit — exactly the mechanism the 801/4000 merge failures hinted at. The merge-lemma scan was the right suspicion but understated: not only is that proof route closed, the proposition is false.
The other half of question 2 also closes: **within arbitrary tests monotonicity IS a theorem, trivially** — the AND of two gates on their concatenated attempt blocks is itself an admissible test with identical pass probabilities, so collapsing adjacent gates preserves cost and feasibility exactly, giving cost(T) ≤ cost(T+1). No Neyman–Pearson machinery needed. The modelling decision (threshold-only vs arbitrary gates) therefore fully determines the answer, and under the threshold family actually in use, it is a scan.

**F2 — OBSERVED, HIGH. Inversions are ~1 budget in 5, not a corner case; free divisions exist.**
60 random budgets through the committed DP (`optimal_costs`, unchanged): 48 feasible, **9 with a downward step, rate 0.1875, Wilson (0.1019, 0.3194)**. One example also answers the brief's "free division" question affirmatively: budget (0.943, 0.696, 0.817, 0.312) has curve [(2,8),(3,5),(4,5),(5,5)] — divisions 4 and 5 are **FREE**.
Command: `python3 scripts/the_division_count_derivation_and_a_monotonicity_counterexample_2026-10-08.py --budget-scan` (executed; output above).

**F3 — OBSERVED, MEDIUM. "Infeasible at any division count" is the ceiling binding, not the rate pair.**
(0.85, 0.75) — reported infeasible by the sweep's settings — is feasible at a **single gate of 253 attempts** (s=206; capable 0.950388, weak 0.009481; scipy = mpmath to <1e−12). For any cap > weak the exact minimal single-gate attempts track the sample-size law `A* ≈ ((z_w√(w(1−w)) + z_c√(c(1−c)))/(c−w))²`, worst relative error 0.158 over a 5-pair grid; required attempts scale as (c−w)⁻², so separation **prices** attempts and never forbids them. Infeasibility in the sweep is MAX_ATTEMPTS_PER_GATE=24 / MAX_TOTAL_ATTEMPTS=60 binding (`scripts/the_division_count_is_derivable_2026-10-08.py` lines 50–51) — which is the correct way to say "available resources bound the answer", but it must be said as a ceiling, not as a property of the task. Command: claim 2 of my script.

**F4 — OBSERVED, HIGH (the answer to the founder's question). T is derivable, and from exactly the 2 quantities he named.**
Divisions are difficulty strata, and a stratum boundary is real only if a model's window of attempts can statistically place it on one side. One-sample classification between adjacent rates p₁, p₂ with n attempts separates at per-side error Φ(−z) iff arcsin√p₂ − arcsin√p₁ ≥ z/√n (variance-stabilising transform, Var(arcsin√p̂) ≈ 1/(4n)). Hence:

  **T(n, p_lo, p_hi) = 1 + floor( (arcsin√p_hi − arcsin√p_lo) · √n / z )**

- "Relative complexity" = the measured resolve-rate span [p_lo, p_hi] the task mix induces over the roster — rates, not names, per the founder's standing rule.
- "Available resources" = n, attempts per model per assessment window (total attempt budget ÷ roster ÷ windows).
- Checked with NO normal approximation against an exact-binomial greedy packing: agreement within 1 stratum at every n ∈ {19, 38, 80, 150, 300}, both non-decreasing. At n=19 over [0.5, 0.9]: **T=2**. At n=80: T=3. T grows as √n — finite always, exactly as he requires.
My first draft used the 2-sample gap z/√(2n); **its own falsifier rejected it** (exact separation failed at 4 of 5 n values) and the 1-sample form replaced it. That correction is recorded in the file.
The full derivation is then two-sided: the resolution formula gives the number of *supportable* divisions (the placement value the attempts metric does not price — §3's crux); the per-budget DP scan prices the climb and picks T\* = argmin cost among T ≤ T_resolution. Both halves are computable in seconds at experiment start. What must be measured first: p_lo, p_hi (archived resolve rates on the task mix — the archive's provenance-clean attempt counts are currently the binding constraint, per `scripts/why_a_global_capability_number_fails_2026-10-07.py`'s own note), and the attempt budget.

**F5 — OBSERVED, MEDIUM. Relegation: statistic, window, rule, and the hard-problem guard — built and falsified.**
Rule delivered: **demote iff an exact one-sided sign test over discordant pairs against the division-peer majority, on the SAME last n scored tasks, rejects parity at 0.05** (`binomtest(n21, n12+n21, 0.5, alternative="less")`). Window is attempt-indexed (n=40 scored attempts), never wall-clock — honouring "harvest when done". Transient outage vs sustained decline: an attempt returning no artefact is an aliveness event (`bench/seat_aliveness_2026-10-06.py` channel) and never enters the denominator — an outage produces no evidence, not failures. The hard-problem guard is the pairing itself: when the stream hardens, model and peers fall **together**, parity holds, nobody is demoted. Executed: under a difficulty shift the absolute-floor rule demotes a capable model (the founder's feared defect, demonstrated) while the sign test does not; both demote a genuinely degraded model. My first draft conditioned on peer success with independent Bernoullis; **its own falsifier rejected it** (conditioning carries no information without pairing) and the comparative form replaced it. Command: claim 4 of my script.

**F6 — HYPOTHESISED, LOW. The committed `--sweep` did not return within my turn** (>20 min wall-clock; `tail` buffering hides partial output). Its two questions are answered by F2/F3 with the same instrument; what would settle its own 6 settings is simply letting `python3 scripts/the_division_count_is_derivable_2026-10-08.py --sweep` run to completion — if any of its 4 feasible settings shows a downward or flat step, it corroborates F2 from inside the committed producer.

**F7 — OBSERVED, LOW. `bench/the_division_count_is_bounded_and_the_cost_is_not_monotone_2026-10-08.py` still prints its withdrawn headline** ("the cost curve is NOT monotone … has to be SCANNED", reproduced in my run). By F1 its *conclusion* (scan) is right for the wrong reason (identical-gate artefact). Per the additive standard it should not be deleted; it needs a pointer to the corrected producer. I did not patch a committed producer's conclusions unilaterally in a blind round — flagged for the joint round.

## Fix

File delivered at `scripts/the_division_count_derivation_and_a_monotonicity_counterexample_2026-10-08.py` — 5 claims, each a self-executing falsifier (asserts raise on failure): (1) the inversion counterexample, triple-verified; (2) the no-ceiling feasibility proof and the (c−w)⁻² sample-size law; (3) the T derivation with exact-binomial cross-check; (4) the peer-paired relegation rule with the difficulty-shift demonstration; (5) the 60-budget inversion-rate scan behind `--budget-scan` (same off-by-default pattern as the committed producer's `--sweep`, for the 600 s validator ceiling). Executed output is pasted in full above; final line both runs: `all falsifiers passed`. Two of my own draft claims were **killed by their own falsifiers and repaired** (F4, F5) — the file documents both repairs. Attribution carried in-file for the Wolfram-derived values.

## Disagreement

1. **"So 'as few divisions as possible' IS right on the attempts metric, and a single gate at 19 attempts is the floor" — WRONG as a general claim.** It holds at (0.95, 0.01) and fails at (0.85, 0.26), where the optimum is 3 divisions, and at ~19% of random budgets (Wilson 0.10–0.32). The correct statement: the division count must come from a per-budget scan, which is cheap and deterministic — the brief's withdrawal over-corrected, and the withdrawn file's "has to be SCANNED" conclusion was accidentally right. Command: `python3 scripts/the_division_count_derivation_and_a_monotonicity_counterexample_2026-10-08.py`.
2. **"Some rate pairs are INFEASIBLE at any division count" — wrong framing.** Infeasibility is the attempts ceiling binding; every cap > weak pair is feasible at finite attempts, scaling as (c−w)⁻². Command: claim 2, same file.
3. **"Whether gates may be arbitrary tests … a modelling decision nobody has made" — the decision matters less than the brief implies in one direction and more in the other.** With arbitrary tests, monotonicity is a 2-line theorem (AND-merge is admissible); but choosing threshold gates doesn't merely demote monotonicity to a scan result — it makes it **false** at measurable rates. The joint round should make the modelling decision explicitly; I recommend keeping deterministic threshold gates (auditable, reproducible — "tools decide" favours a gate a tool can re-execute) and accepting the per-budget scan as the derivation.

## What would refute me

- **F1:** exhibit any (a ≤ 4, s) with `scipy.stats.binom.sf(s-1, a, 0.9) ≥ 0.85` and `binom.sf(s-1, a, 0.5) ≤ 0.26` — one line of scipy; my enumeration says none exists. Or show the budget (0.85, 0.26) is outside the admissible budget region by a **committed** constraint, with the committed DP showing 0 inversions over that whole region — that would demote F1 from load-bearing to out-of-scope without falsifying it.
- **F2:** rerun `--budget-scan` with other seeds; if the inversion rate collapses toward 0 outside seed 11's draws, my "not a corner case" claim dies (the fixed-seed assertion `inv >= 1` would still pass — the claim at risk is the rate, not the witness).
- **F4:** show the exact greedy strata count and the formula diverging by ≥ 2 at some (n, p_lo, p_hi) — claim 3's assertion is the command; or show the task mix induces rate spans that are not stable enough between windows for [p_lo, p_hi] to be measurable at experiment start, which would turn "derivable" into "derivable only after a calibration window".
- **F5:** build a shared-task-effect simulation (correlated successes, not iid given rates) where the sign test's false-demotion rate on a capable model exceeds 0.05, or where it misses genuine degradation the absolute rule catches; and for roster 1 the rule has **no comparator** — if the joint round rejects my proposed fallback (archived task-class base rates as the synthetic peer), relegation at M=1 is unspecified and my Q5 answer is incomplete.

On the remaining decision questions: **roster 700** — the structure survives: T is roster-free in the formula; resources enter as n = budget/700 per window, shrinking T as √n automatically; an occupancy cap T ≤ floor(M/min-occupancy) is the only roster-coupled term. **Roster 1** — the ladder degrades gracefully to a measured difficulty rating (strata are task strata, not model strata; promotion by Wilson lower bound still works), with the one comparator gap stated above. **Success-count guard (Q4)** — mechanical, not aspirational: nothing updates capability except (successes, attempts) pairs on a named task class; promotion requires the Wilson **lower** bound to clear the next division's floor, relegation requires the sign test to reject parity against peers; a bare count has no denominator and can clear neither. That is the founder's guard as arithmetic.

<!-- verbatim-end -->

## Where the raw record lives

`bench/logs/division_count_blind_2026-10-08/` holds the brief, every seat reply, the tool logs and `seat_proposals.diff`. That directory is excluded by `.gitignore:41`, so a byte-identical copy is committed under `experimental_notes/evidence/`, verified by sha256 and checked on every suite run by `bench/tests/test_panel_records_are_preserved_2026-09-11.py`.


Written under CDSFL note standard v1.7 (26 August 2026).
