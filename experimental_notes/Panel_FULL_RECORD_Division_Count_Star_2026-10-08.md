# The joint round: a third gate family, one formula, and a quantity that is not identified

Record written 2026-10-09T05:15:47+01:00.

**This is the seats' own output, reproduced in full.** The Personalisation directive requires external review output preserved *"in full and in unfiltered format"* and says *"Never summarise in place of the full output"*. Any summary elsewhere is downstream of this file, not a substitute for it.

The JOINT half of a star-topology pair, and the first complete pair in this arc. Both seats saw the other's blind reply, labelled only as POSITION A and POSITION B with no seat named. 0 paid dispatches.

WHAT IT SETTLED, AND IN EVERY CASE THE ANSWER CAME FROM SOMEWHERE NEITHER SEAT HAD STOOD BLIND.

The gate-family question was posed as a choice between randomised gates, which make the cost curve provably monotone, and deterministic gates, which are reproducible but do not. One seat dissolved the choice by finding a third option: a deterministic gate that reads WHICH attempts succeeded rather than only how many reaches power 0.9833784264 at size 0.0099919656 against a randomised optimum of 0.9834296545, a shortfall of 5.1e-05, where a gate reading only the count reaches 0.9298091736. So determinism is nearly free. What is not free is EXCHANGEABILITY: an order-reading gate hands 2 models with identical records of successes and attempts different verdicts according to the order their successes fell, which is a concealed coin and contradicts the project's standing rule that capability is measured as successes over attempts. Adopting both properties forces thresholds on the number of successes, makes the curve non-monotone, and prices the number of divisions by a per-budget scan. CC1 verified both halves independently: the order-reading power and shortfall reproduce exactly, and the price of determinism at the committed operating point is 0 additional attempts, with the deterministic and randomised minima both 19.

The 2 competing formulae turned out to be 1 formula. The doubling of the arcsine span cancels, because doubling the span also doubles the critical value it is divided by, and both forms give a bracket of 1.228677 at 19 attempts over a span of 0.50 to 0.90. What genuinely remains is which error quantity is held fixed, a per-side rate or a two-sided one, and the brief never stated which. CC1's independent scan found one algebraic form matching an equally spaced per-side arbiter at 4 of 6 sample sizes and the other matching a two-sided arbiter at 4 of 6, so both seats were correct under their own convention. That omission was CC1's.

The cost scan survived in a reduced role and both blind positions were wrong about it. It is not degenerate at 2 divisions and not confined to 2 or 3; one seat found an argmin of 4 and budgets where 2 divisions are infeasible outright under a per-gate ceiling. But the objective takes no argument for the number of attempts available, so it cannot track resolution and cannot derive how many divisions there should be. Its role narrows to pricing candidates below the resolution bound and taking divisions that cost nothing.

AND THE FOURTH QUESTION HAS NO ANSWER AS IT WAS POSED, WHICH IS THE ROUND'S DEEPEST RESULT. One seat showed the relegation quantity is NOT IDENTIFIED: in the standard difficulty model only the difference between a model's capability and an item's difficulty enters, so a capability drop across the whole roster and a difficulty rise across the whole task stream produce identical distributions on every outcome. CC1 confirmed this 3 ways, with symbolic algebra returning exactly 0, a constraint solver returning unsatisfiable on any separating value, and arbitrary-precision arithmetic returning 0 difference across 27 points. Neither proposed statistic measures the intended quantity; each substitutes an assumption. The other seat, independently, measured a composition that weakly dominates each mechanism in every tested regime and strictly beats each in 1: peers govern where a group shares the task stream, the difficulty model governs where difficulty is calibrated and no group exists, and where neither holds it declines to issue a verdict. Those are the same finding from opposite ends. One seat's anchor set and the other's calibration share are the same object, a pool of items whose difficulty is fixed externally and re-run every window. The composition does not solve the identification problem; it detects when the problem is unsolvable and refuses, which is this project's own pattern applied to a statistic.

WHAT SURVIVED AS DISAGREEMENT, AND ONE OF IT IS AGAINST CC1. A seat challenged CC1's reported 3.65 percent false-demotion figure for the peer test under a hardening stream. It is right: the brief specified comparison against a majority of division peers, and a majority-of-3 comparator pushes the comparator's rate away from one half and breaks the test's null, measuring 0.5167 false demotion. CC1's simulation paired against a single peer, which is the repaired form rather than the specified one. The specification text was defective irrespective of which figure stands. The second surviving item is that the 0.40 calibration share rests on synthetic difficulty, with no per-model-per-item outcome corpus in the tree to measure the real distribution.

BOTH SEATS KILLED CLAIMS OF THEIR OWN AND REPAIRED RATHER THAN REVERTED. One replaced a 2-sample separation form with a 1-sample form after its own falsifier rejected it and reported its derived transient-outage bound as unsafe as stated. The other found its own first implementation of the peer comparison defective and repaired it, and reported that its predicted counterexample to a ceiling-driven inversion failed to materialise.

A CC1 FINDING THAT CHANGES THE INPUTS RATHER THAN THE LOGIC. Both formulae need the span of measured performance as their measure of relative complexity, and that span can only come from findings reaching a confirm-or-refute verdict. Measured across the archive, findings in the statistics domain reach a terminal closed status 0.7603 of the time, 95 percent interval 0.7341 to 0.7847, against 0.4003 for software, interval 0.3740 to 0.4272, a difference of 0.3600 with interval 0.3233 to 0.3967 at odds of 4.7516 and a probability of 3.87e-72, with 2 further tests agreeing. So 96.84 percent of adjudicated outcomes come from a single domain while the corpus is nearly balanced at 1304 software findings against 1093 statistics findings. The span feeding the number of divisions is therefore measured on one domain while the intended workload is not.

## Seats and cost

2 seat(s): `cc2`, `fable`. **0 paid dispatches**, enforced by `PANEL_ONLY=cc2,fable`.

## The brief, as dispatched

<!-- verbatim-begin: the brief as dispatched -->

# JOINT ROUND — the number of divisions, and what relegates a model

You answered this question BLIND. Both blind replies are below, as POSITION A and
POSITION B, unlabelled by seat. One of them is yours. Read the other.

**This round exists to RECONCILE, and that is also its danger.** A joint round is the
one most able to produce agreement by deference, and deference is not evidence. Where
you now think the other position is right, say so and say what changed your mind. Where
you still disagree, hold it and sharpen it. A disagreement that survives this round is
the most valuable thing it can produce.

Work in the sandbox repository tree. RUN things. Both positions deliver files with
executed falsifiers; re-execute them and contradict them where they are wrong.

---

## What the 2 of you ALREADY AGREE on, blind, and which therefore counts

1. **CC1's "as few divisions as possible" is FALSE.** Both of you produced inversion
   witnesses at budgets the brief never examined — `cost(3)=10 < cost(2)=11` at capable
   0.90 / weak 0.30 with budget (0.95, 0.010), and `cost(3)=4 < cost(2)=5` at capable
   0.90 / weak 0.50 with floor 0.85 and ceiling 0.26. CC1 reproduced the second
   exactly, scipy against mpmath to 0.000e+00. Inversions run at roughly 1 budget in 5:
   9 of 48 feasible in one measurement, 0.1875, Wilson (0.1019, 0.3194); 3 of 30
   feasible in the other.
2. **The identical-gate withdrawal was correct.** `smallest_gate` costs are upper
   bounds, matching the optimum only at 2 divisions.
3. **The division count must be derived from RESOLUTION, not from cost**, and both of
   you identify relative complexity with an arcsine span of measured resolve rates and
   available resources with attempts of evidence per model per window.
4. **Free divisions exist** — a 3rd division costing nothing at some budgets.
5. **Difficulty must be a covariate in any relegation statistic**, so that a failure on
   a hard item is expected and barely debited.

## The 5 things this round exists to settle

**Q1 — THE MODELLING DECISION, and it determines everything else.** Position B holds
that under DETERMINISTIC success-count thresholds monotonicity is FALSE, while under
RANDOMISED thresholds it is a THEOREM by Karlin–Rubin — and that a randomised threshold
is the standard completion of the binomial test family rather than an exotic liberty.
Position A recommends keeping deterministic threshold gates for auditability and
accepting a per-budget scan. CC1 verified Position B's arithmetic independently: all
801 of the brief's deterministic merge failures are repaired by randomisation alone,
0 of 4000 remaining, worst power slack -4.441e-16 and worst size excess 8.674e-19;
SymPy gives log(9) for the likelihood-ratio slope and z3 returns `unsat`. **So the
mathematics is not in dispute. The question is whether this project should promote a
model on a coin flip.** A randomised gate means two models with identical attempt
records can receive different verdicts. Decide it, and say what the decision costs.

**Q2 — THE 2 FORMULAE DISAGREE AND BOTH ARE PRESENTED AS DERIVED.** One gives the
division count as 1 plus the floor of (arcsine gap times the square root of the sample,
divided by a fixed critical value). The other doubles the arcsine gap, makes the
critical value depend on the division count, and raises the bracket to a power that
differs between pooled and serial accounting. The arcsine gap over the interval 0.5 to
0.9 is 0.4636476090 undoubled and 0.9272952180 doubled, which CC1 confirmed in 2 tools.
At the same inputs the 2 formulae do not in general return the same count. **Reconcile
them or show one is wrong.** Name which quantity is being held at which error rate, and
state the small-sample behaviour — one position already reports its own transform as
optimistic at small samples and gives Anscombe's correction.

**Q3 — IS THE ATTEMPTS OBJECTIVE DEGENERATE?** Position B says it returns 2 divisions
always, so it cannot derive the count at all, which makes placement the answer rather
than a caveat. Position A prices placement and finds it exceeds certification from 3
divisions, reaching 45.75 times by 5. If that is right, the brief's section 3 was the
whole question and the cost scan is a tie-break at best. Settle whether a cost scan has
any role left.

**Q4 — THE 2 RELEGATION MECHANISMS.** One is an exact one-sided sign test over
discordant pairs against the division-peer majority; CC1 simulated it and found that
when the task stream hardens under an equally capable peer an absolute floor demotes a
capable model 98.35% of the time, Wilson (0.9791, 0.9870), against 3.65% for the sign
test, Wilson (0.0311, 0.0428), while on genuine decline the sign test fires 99.68%
against 96.27%. The other is a one-sided CUSUM on Rasch residuals against measured item
difficulty, with no window, the threshold solved from a target average run length, and
promotion as the mirror CUSUM so symmetry is structural. **These are not variants of one
idea: one compares a model to its peers, the other to a difficulty model.** The peer
form has no comparator at a roster of 1; the Rasch form needs a difficulty estimate and
one position measures escalated items as carrying about 14 times less information, with
a 1.5-logit decline undetected below a 0.40 calibration share. Choose one, or compose
them and say which governs when they disagree.

**Q5 — WHAT THE FOUNDER MUST RULE ON.** Both of you must end with the shortest possible
list of decisions that are HIS and not yours — parameters, thresholds, and the
randomisation question above. Anything you can settle by measurement, settle.

## Conditions

No model names where a rate will do. Numbers in digits. Every figure you assert must
name the command that produces it. Deliver each fix as a file at its real path in the
sandbox tree with an executed falsifier beside it and the falsifier's actual output
pasted; repair rather than revert. A fix you have not tried to break is a hypothesis.

## Output

- `## Verdict` — on the reconciled position, not on the other seat.
- `## What I concede` — name what the other position got right that you had wrong, and what changed your mind. If nothing, say so plainly and why.
- `## Disagreement` — what survives this round. Sharpen it; do not soften it. Name the measurement that would settle it.
- `## Findings` — each OBSERVED (run, file, line) or HYPOTHESISED (what would settle it), with a severity and a command.
- `## Fix` — files at real paths with executed falsifiers and pasted output.
- `## For the founder` — the shortest list of decisions that are his.

## Termination

Stop when further passes produce no new above-threshold findings. Diminishing returns is
the criterion, not the clock. Take the time you need for a full response.

---

## POSITION A (blind round, seat 1)

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

---

## POSITION B (blind round, seat 2)

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

## Seat: cc2

Route `claude_cli`, 39 recorded tool call(s).

<!-- verbatim-begin: cc2 (panel division_count_star_2026-10-08) -->

All eight claims executed, exit 0, final line `all falsifiers passed`. Wolfram ran locally on 10 values across 3 calls, exit 0 each, no `Name::tag`, no `$Failed`.

## Verdict

**The reconciled position: the division count is a RESOLUTION bound, both seats' closed forms overestimate it, the randomisation question is cheaper than either seat thought, and the relegation statistic both seats argued over is NOT IDENTIFIED.**

Four settled results, each with a command:

1. `T = max(1, floor(dphi*sqrt(N)/z))`, dphi the arcsine span of measured resolve rates, N attempts of evidence per model per window. Scored against an exact binomial placement computation over 128 cells: bias −0.117, MAE 0.227, exact in 100/128. Position A's `1 + floor(...)` is bias −1.047, exact 16/128. Position B **as summarised in the brief** is bias −7.906, exact 2/128.
2. The price of determinism at the committed budget (capable 0.90 / weak 0.50, budget 0.95/0.010) is **0 attempts** — randomised minimum 19, deterministic minimum 19. Q1 is not a trade this project has to make.
3. The cost scan cannot choose T. It reports the smallest *feasible* T under the attempts ceiling.
4. A roster-wide capability drop and a stream-wide difficulty rise are likelihood-identical in the Rasch model (SymPy and Wolfram both return exactly 0). Neither the peer sign test nor the Rasch CUSUM measures the quantity; each silently substitutes a prior. An **anchor set** of externally-fixed-difficulty items re-run each window is the only thing that breaks it.

`python3 scripts/the_division_count_is_a_resolution_bound_and_relegation_is_not_identified_2026-10-08.py`

## What I concede

The brief did not label which position was mine and I will not guess, so I concede against **both**.

- **Position B's deterministic inversion witnesses are right and I re-derived them exhaustively, not by a pruned DP.** `cost(3)=10 < cost(2)=11` at capable 0.90 / weak 0.30 budget (0.95, 0.010), scipy−mpmath 8.674e-19; `cost(3)=4 < cost(2)=5` at capable 0.95 / weak 0.30 budget (0.90, 0.050), diff exactly 0.0. The mechanism B names is exactly right: the best deterministic gate on the merged 10 attempts reaches 0.9298091736 against a 0.95 floor, where the randomised gate reaches 0.9834296545 at size exactly 0.010. Confirmed in Wolfram to 12 digits.
- **Position B's "the attempts objective cannot derive T" is the correct reading, and Position A's placing of it as the second half of a two-sided derivation understates it.** Measured: over 27 feasible budgets the argmin *never once* strictly beat the smallest feasible T. A scan whose output is always "the smallest feasible T" is not deriving anything.
- **Position B's 0.40 calibration share is real, and I reproduced it by a different construction** (0.8953 power on a 1.5-logit common-mode drop at share 0.40, against 0.0000 at share 0.00) — and found the reason it exists, which B did not have.
- **Position A's "keep deterministic gates" recommendation is right, but its stated ground — auditability — was an unpriced assertion.** It is now priced at 0 attempts at the committed budget. That changed my mind about how the decision should be put to the founder: not as a principle against a cost, but as a free choice at this operating point.
- **Position A's F3 is right that infeasibility is the ceiling binding, and my own scan corroborates the inverse of it**: in 6 of 27 feasible budgets a *single* gate is infeasible under the per-gate ceiling, so the ceiling imposes a **lower** bound on T. That is Position B's F9 arriving from the other direction and I accept both.
- **What changed my mind on the formulae:** I set out to adjudicate between a doubled and an undoubled arcsine gap and found the doubling is not the error at all. `Var(2*arcsin(sqrt(phat))) ~ 1/N` where `Var(arcsin(sqrt(phat))) ~ 1/(4N)`, so doubling the gap doubles the critical value and the bracket is unchanged. B's own quoted Wolfram bound at N=2000, 10.5792512465, *is* the undoubled bracket — which means B's implementation already equals A's and the brief's Q2 "disagreement" is cosmetic. The real error is the `+ 1`, which **both** carry. Wolfram's floor of that bound is 10; the exact binomial answer is 10; B reported 11.

## Disagreement

**D1 — Against both seats: `+ 1` is an error, not a convention, and it is load-bearing at this project's own operating point.** At N=19 attempts over a measured resolve-rate span [0.50, 0.90], the exact supportable count is **1** — no promotion boundary is supportable at all. A returns 2; B as summarised returns 3. The committed 5-rung rule (19 attempts, 11 successes) sits exactly there. I tried to break this as claim 8, under the alternative interior-edge one-sided criterion that would most favour a larger count: the `+ 1` form is still not the best fit (MAE 1.188 against 0.680), and at N=19 the exact count is **1 under both criteria**. What *is* criterion-dependent is the size of the overestimate (1.047 vs 0.547) and the choice of z. **Settled by:** a third resolution criterion under which `1 + floor(...)` is the minimum-MAE form over ≥100 cells. I could not construct one.

**D2 — Against Position A: the randomisation question does not need the auditability argument, and making it carries a cost A did not notice.** The price of determinism is 0 attempts at the committed budget and 1–2 attempts at the two witnesses. Arguing it on auditability invites a reply that auditability is worth less than 2 attempts. Argue it on the measured price instead. **Settled by:** a budget on the project's roadmap where the price of determinism exceeds 2 attempts.

**D3 — Against Position B: "the attempts optimum is degenerate, T = 2 always" is contradicted by B's own claim 7.** At witness 1 the argmin is 3, not 2. And in 6 of 27 of my feasible budgets T=2 is infeasible outright. B's conclusion survives; the stated reason does not, and the stated reason is what a reader would carry forward. **Settled by:** already settled — B's two files disagree with each other.

**D4 — Against both seats, and this is the disagreement I most want preserved: the Q4 question as the brief poses it has no correct answer.** The brief asks the panel to choose between a peer-comparative statistic and a difficulty-model statistic, or compose them. In the Rasch model a roster-wide drop of δ and a stream-wide difficulty rise of δ produce *identical* distributions on every outcome — SymPy returns 0, Wolfram `FullSimplify` returns 0, z3 returns `unsat` on a separating logit. So neither statistic measures the quantity. Measured at equal false-alarm rate 0.05 on a stable model, held-out seed:

| scenario | absolute floor | peer sign test | Rasch CUSUM |
|---|---|---|---|
| stable *(want LOW)* | 0.0555 | 0.0475 | 0.0705 |
| stream hardens *(want LOW)* | **1.0000** | 0.0020 | 0.0240 |
| individual decline *(want HIGH)* | 1.0000 | 0.9590 | 0.9985 |
| **common-mode decline** *(want HIGH)* | 1.0000 | **0.0190** | 0.9985 |
| **difficulty estimate stale** *(want LOW)* | 1.0000 | 0.0020 | **1.0000** |

The peer test always calls the ambiguity "hardening" and is blind to a roster-wide decline (0.0190, against its own 0.0475 size). The CUSUM on archived difficulty always calls it "decline" and demotes a stable model 1.0000 of the time on stale difficulty. Those are priors wearing the clothes of measurements. **Settled by:** the identifiability result is a two-line symbolic fact; it is already settled. What is open is whether this project can supply an anchor set — see For the founder.

**D5 — Against Position B specifically: the Brook–Evans threshold h = 4.400221 is not in control, and no value of the residual sd fixes it.** B listed the residual sd as a parameter to be measured. The defect is structural, not parametric: the Winsorised Rasch residual on a *single* Bernoulli observation is two-valued and its skew depends on the item's pass probability, so the normal-theory Markov chain does not describe the increment. Realised in-control ARL0 at h = 4.400221: **773.4** at p=0.50, **356.8** at 0.65, **155.9** at 0.8176, **6755.5** at 0.95 — a 43.3× spread, hitting the 500 design target at none. At p=0.8176 the specified rule demotes **0.696** of stable models over a 200-observation horizon. **Settled by:** a Brook–Evans variant whose realised ARL0 lands in (400, 600) at all four pass probabilities. The anchor design removes the need for one, because the anchor pool's difficulty distribution is fixed by construction.

## Findings

| # | status | severity | claim | command |
|---|---|---|---|---|
| **1** | OBSERVED (claim 3, 8) | **CRITICAL** | Both seats' division-count formulae overestimate. At N=19 over span [0.50, 0.90] the exact count is 1; A returns 2, B-as-summarised returns 3. Corrected form `max(1, floor(dphi*sqrt(N)/z))`: bias −0.117, exact 100/128. Survives self-falsification under a second criterion. | `python3 scripts/the_division_count_is_a_resolution_bound_and_relegation_is_not_identified_2026-10-08.py` |
| **2** | OBSERVED (claim 7) | **CRITICAL** | Common-mode decline and stream hardening are likelihood-identical; neither proposed relegation statistic measures the target quantity. Peer test 0.0190 on common-mode; CUSUM 1.0000 on stale difficulty. | same file, claim 7 |
| **3** | OBSERVED (claim 6) | **CRITICAL** | `h = 4.400221` from normal-theory Brook–Evans is not in control: realised ARL0 155.9–6755.5 across p, 43.3× spread, 0.696 false-demotion rate at p=0.8176. | same file, claim 6 |
| **4** | OBSERVED (claim 1) | HIGH *(agreed)* | Both deterministic inversion witnesses reproduce by exhaustive enumeration. "As few divisions as possible" is false. | same file, claim 1 |
| **5** | OBSERVED (claim 2) | HIGH | Price of determinism = 0 attempts at the committed budget, 2 and 1 at the witnesses. Coin load-bearing on 0.057395628 of capable records; 0.00705368 of paired identical records would diverge. | same file, claim 2 |
| **6** | OBSERVED (claim 5) | MEDIUM | The peer sign test **as quoted in prose** (`alternative="less"`) is inverted: detection on genuine decline 0.0045 against 0.9590 for the correct tail, and 0.6155 false-fire on a hardening stream. Either `n21` means the opposite of the standard convention or the call is wrong; as written the rule is not reproducible. | same file, claim 5, last line |
| **7** | OBSERVED (claim 4) | MEDIUM | The cost scan cannot choose T: argmin strictly beat the smallest feasible T in 0 of 27 feasible budgets. But in 6 of 27 the smallest feasible T was 3 — the per-gate ceiling imposes a lower bound on T. One full DP over T=2..14 costs **80.0 s**, not "seconds". | same file + `--budget-scan` (184 s) |
| **8** | OBSERVED (file, line 244) | LOW | `bench/the_division_count_is_bounded_and_the_cost_is_not_monotone_2026-10-08.py` still *printed* its withdrawn headline from its `verdict` string, though the docstring carried the withdrawal. **Repaired** below. | `python3 bench/the_division_count_is_bounded_and_the_cost_is_not_monotone_2026-10-08.py` |
| **9** | HYPOTHESISED | LOW | I did **not** reproduce the 0.1875 inversion rate: my 40-budget scan at per-gate ceiling 14 found 0 downward steps, Wilson (0.0000, 0.1246). Different ceiling, different population; the intervals overlap, so this neither confirms nor refutes. Settled by rerunning both ceilings on the same budget draws. | `--budget-scan` at `maxa=14` vs `maxa=24` |
| **10** | HYPOTHESISED | MEDIUM | The 0.40 anchor share is measured on a synthetic difficulty ramp (0 to 2.5 logits) and a 1.5-logit drop. The real escalated-item difficulty distribution is not in this tree — I searched and found no per-model-per-item outcome corpus. Settled by replaying the archived routing records through claim 7's `run()`. | `claim_an_anchor_set_is_what_breaks_it` with the archived histogram |

## Fix

**`scripts/the_division_count_is_a_resolution_bound_and_relegation_is_not_identified_2026-10-08.py`** — 8 claims, every one a self-executing falsifier (asserts raise). Exit 0. Heavy 40-budget scan behind `--budget-scan`, matching the committed producer's `--sweep` pattern for the 600 s validator ceiling. Claim 8 is an attempt to break claim 3 that failed, recorded with its qualification rather than dropped.

```
== 1. both inversion witnesses, exhaustively, and the randomised merge ==
   capable 0.90 / weak 0.30, budget (0.95, 0.010)
      cost_T2: 11  gate_T2: (11, 8)
      cost_T3: 10  ladder_T3: [(2, 1), (8, 6)]
      end_to_end_capable: 0.9522891279   end_to_end_weak: 0.0057590271
      inverts: True    scipy_vs_mpmath: 8.673617379884035e-19
   capable 0.95 / weak 0.30, budget (0.90, 0.050)
      cost_T2: 5   gate_T2: (5, 4)
      cost_T3: 4   ladder_T3: [(2, 1), (2, 2)]
      inverts: True    scipy_vs_mpmath: 0.0
   the randomised merged gate on 10 attempts
      S: 7   gamma: 0.9342258766   randomised_power: 0.9834296545
      randomised_size: 0.01
      best_deterministic_power_on_the_same_10: 0.9298091736
      deterministic_clears_the_0.95_floor: False

== 2. the price of determinism, in attempts ==
   THE COMMITTED BUDGET (0.90/0.50, 0.95/0.010): {'randomised_min_attempts': 19,
       'deterministic_min_attempts': 19, 'price_of_determinism_in_attempts': 0}
   witness 1 (0.90/0.30, 0.95/0.010): {..._randomised: 9, ..._deterministic: 11,
       'price_of_determinism_in_attempts': 2}
   witness 2 (0.95/0.30, 0.90/0.050): {..._randomised: 4, ..._deterministic: 5,
       'price_of_determinism_in_attempts': 1}
   the coin's share at witness 1's merged gate: {'P(tie | capable 0.90)': 0.057395628,
       'P(tie | weak 0.30)': 0.009001692,
       'P(2 identical records differ | capable)': 0.00705368}

== 3. both closed forms OVERESTIMATE the division count ==
   128 cells, scored against an exact binomial band-centre placement computation
      max(1, floor(dphi*sqrtN/z))   [this round]    bias  -0.117 MAE 0.227 max|err| 2 exact 100/128 over  21/128
      1 + floor(dphi*sqrtN/z)       [position A]    bias  -1.047 MAE 1.047 max|err| 3 exact  16/128 over 112/128
      1 + floor(2*dphi*sqrtN/z)     [position B]    bias  -7.906 MAE 7.906 max|err|42 exact   2/128 over 126/128
   at the operating point, span 0.50-0.90, alpha 0.05:
      N=   19  exact  1   A  2   B  3   bracket 1.031138
      N=   38  exact  1   A  2   B  3   bracket 1.458249
      N=   80  exact  2   A  3   B  5   bracket 2.11585
      N= 2000  exact 10   A 11   B 22   bracket 10.579251
   dphi 0.46364760900080604  doubled 0.9272952180016121
   Wolfram: {'dphi': 0.4636476090008061, 'bracket_at_N_2000': 10.579251246541043,
             'floor_of_that': 10, 'attribution': 'Wolfram Language, local Wolfram Engine'}

== 4. what the cost scan is still for ==
   committed_budget_optimum_curve: [19, 21, 22, 25, 28, 30, 33, 36, 38, 41, 42, 45, 48]
   one_full_DP_T2_to_T14_seconds: 80.028
   monotone_at_the_committed_budget: True
   budget_scan: Recorded: 40 budgets seed 11, ceiling 14, T<=5: 27 feasible, 0 downward
     steps (Wilson 0.0000-0.1246), argmin T {2: 21, 3: 6}, argmin STRICTLY beat the
     smallest feasible T in 0 of 27 -- the 6 threes are budgets where a single gate is
     INFEASIBLE under the ceiling.

== 5. three relegation rules at EQUAL false-alarm rate ==
   {'floor_rate': 0.625008, 'sign_alpha': '1.953e-03', 'cusum_h': 7.5829}
   Brook-Evans h=4.400221 realised P(fire | stable) = 0.696
   scenario                  absolute_floor              peer_sign_test                 rasch_cusum
   stable           0.0555 (0.0463, 0.0664)      0.0475 (0.039, 0.0577)     0.0705 (0.0601, 0.0826)
   harden              1.0000 (0.9981, 1.0)     0.0020 (0.0008, 0.0051)     0.0240 (0.0181, 0.0317)
   decline             1.0000 (0.9981, 1.0)     0.9590 (0.9494, 0.9668)     0.9985 (0.9956, 0.9995)
   common              1.0000 (0.9981, 1.0)      0.0190 (0.0139, 0.026)     0.9985 (0.9956, 0.9995)
   stale               1.0000 (0.9981, 1.0)     0.0020 (0.0008, 0.0051)        1.0000 (0.9981, 1.0)
   sign test with alternative 'less' as quoted in prose: {'decline': 0.0045, 'harden': 0.6155}

== 6. the Brook-Evans threshold is not in control ==
   h: 4.400221   design_target_ARL0: 500
   realised_ARL0_by_item_pass_probability: {0.5: 773.4, 0.65: 356.8, 0.8176: 155.9, 0.95: 6755.5}
   spread_factor: 43.3

== 7. common-mode decline is NOT IDENTIFIED, and anchors break it ==
   sympy_difference_of_the_2_success_probabilities: 0
   z3_search_for_a_separating_logit: unsat
   anchor share 0.00  common-mode 0.0000   hardening 0.0000
   anchor share 0.05  common-mode 0.0347   hardening 0.0013
   anchor share 0.10  common-mode 0.2200   hardening 0.0047
   anchor share 0.20  common-mode 0.6000   hardening 0.0087
   anchor share 0.40  common-mode 0.8953   hardening 0.0247
   anchor share 0.60  common-mode 0.9693   hardening 0.0333
   anchor share 1.00  common-mode 1.0000   hardening 0.0627

== 8. I tried to break claim 3 under the other resolution criterion ==
   criterion: interior-edge one-sided two-point discrimination, 128 cells
      max(1, floor(dphi*sqrtN/z_alpha))     [one-sided z, no +1]        bias -0.680 MAE 0.680 exact 70/128
      1 + floor(dphi*sqrtN/z_alpha)         [one-sided z, +1]           bias -1.625 MAE 1.625 exact  7/128
      max(1, floor(dphi*sqrtN/z_alpha_2))   [two-sided z, no +1]        bias +1.477 MAE 1.477 exact 50/128
      1 + floor(dphi*sqrtN/z_alpha_2)       [two-sided z, +1 = pos A]   bias +0.547 MAE 1.188 exact 49/128
   best-fitting form: max(1, floor(dphi*sqrtN/z_alpha))     [one-sided z, no +1]
   exact counts, span 0.50-0.90, alpha 0.05: {19: 1, 38: 1, 80: 2, 2000: 12}
   claim 3 HELD.

all falsifiers passed
EXIT=0
```

**`bench/the_division_count_is_bounded_and_the_cost_is_not_monotone_2026-10-08.py`** — repaired, not reverted. Its `verdict` string (line 244) printed the withdrawn headline even though the docstring carried the withdrawal. The string now carries its own withdrawal, keeps the identical-gate measurement, and points at the corrected producer. Nothing deleted. Executed:

```
== 2. and the cost curve is NOT monotone ==
   steps_up: 10   steps_down: 2   steps_flat: 0   is_monotone: False
   inversions_more_tiers_cost_less: 6
   14 divisions cost 52 where 9 divisions cost 56
   [...]
   WITHDRAWN 2026-10-08 (joint round); the measurement is KEPT. The non-monotonicity
   above is real ONLY inside the identical-gate family `smallest_gate` imposes. Under
   heterogeneous gates the curve at THIS budget is monotone: 19, 21, 22, 25, 28, 30,
   33, 36, 38, 41, 42, 45, 48. The conclusion 'the tier count has to be SCANNED' was
   right by accident -- the curve DOES invert at other budgets (capable 0.90 / weak
   0.30, budget (0.95, 0.010): 3 divisions cost 10 attempts where 2 cost 11) -- but a
   cost scan cannot CHOOSE the division count. It reports the smallest FEASIBLE count
   under the attempts ceiling. The count is a RESOLUTION bound,
   max(1, floor(dphi*sqrt(N)/z_alpha_over_2)) over the measured resolve-rate span.
   See scripts/the_division_count_is_a_resolution_bound_and_relegation_is_not_
   identified_2026-10-08.py claims 1, 3 and 4
EXIT=0
```

**What I did not build.** No flag wired into `bench/routing.py`. Finding 10 is why: the anchor share needs the archived escalated-item difficulty distribution, which is not in this tree. Per the additive standard, an unwired flag would be the 12th addition nothing reaches.

**Composability, measured not judged.** The **anchored CUSUM alone** dominates: it detects common-mode decline (0.8953 at share 0.40) which the peer test cannot (0.0190); the anchor set removes the stale-difficulty misfire (1.0000) which is the CUSUM's own failure; and the fixed anchor-pool difficulty removes finding 3's control problem by construction. An AND composition with the peer test *loses* common-mode detection; an OR composition *keeps* the stale-difficulty misfire. One fix discharges three defects and no composition beats it. It also operates at a roster of 1, where the peer test has no comparator at all.

## For the founder

Five decisions, and nothing else on this list is yours.

1. **Randomised promotion gates: yes or no.** Price now measured both ways. Cost of saying no: **0 attempts** at the committed budget, 2 and 1 at the two witnesses. Cost of saying yes: 5.74% of capable-model promotion decisions settled by a coin, and 0.71% of identical attempt-record pairs receiving different verdicts. My recommendation is **no** — and on the measured price, not on principle.
2. **The resolution criterion, which fixes z.** Band-centre placement at two-sided α (z = z_{α/2}), or interior-edge two-point discrimination at one-sided α (z = z_α). This is the only remaining freedom in the division-count formula; the `+ 1` is wrong under both and is not yours to keep.
3. **α for placement.** At α = 0.05 and a [0.50, 0.90] resolve-rate span, 19 attempts support **1** division and 80 support 2. If the project wants a 4-division ladder at that span it needs ~300 attempts of evidence per model per window.
4. **Whether an anchor set exists.** A pool of items with externally fixed difficulty, re-run every window. Without one, relegation cannot distinguish a model getting worse from the work getting harder — that is a symbolic fact, not a tuning problem. If yes, the measured share for 0.90 power on a 1.5-logit drop is **0.40**, at 0.0247 false demotion on a hardening stream. If no, say so and relegation stays unspecified rather than shipping a statistic that substitutes a prior for a measurement.
5. **The relegation false-alarm rate.** Every number in the table above is at 0.05 on a stable model. The CUSUM threshold follows from it and must be solved from the realised Bernoulli increment distribution, not from normal-theory Brook–Evans.

One tool note: all three Wolfram calls ran on the local Wolfram Engine, exited 0, printed no `Name::tag` and returned no `$Failed`/`$Aborted`. Ten values cross-checked there (dphi, 2·dphi, the bracket and its floor at N=2000, gamma, randomised power, both tie masses, the best deterministic power, the Rasch difference, sigma(1.5)); all agreed with SciPy/mpmath/SymPy to the digits quoted. Wolfram was never the only source for any claim.

<!-- verbatim-end -->

## Seat: fable

Route `claude_cli`, 38 recorded tool call(s).

<!-- verbatim-begin: fable (panel division_count_star_2026-10-08) -->

Everything is in; exit 0, all falsifiers passed. The argmin-4 witness even carries two bonus observations: at budget (0.8694, 0.6975, 0.8401, 0.2887) the curve {3:19, 4:18, 5:19, 6:21} has **2 divisions infeasible** within the attempt ceilings while taller ladders are feasible — Position B's F9 conjecture (a per-gate cap imposes a *lower* bound on T) observed in the wild. Final answer:

---

## Verdict

**SOUND, RECONCILED, with one measured discrepancy left open.** The reconciled position is: Position B's mathematics with Position A's modelling decision, and the decision now has a derivation instead of a preference. All 3 blind inversion witnesses reproduce exhaustively (`python3 scripts/the_joint_round_settles_the_gate_family_and_the_count_2026-10-08.py`, claim 1; scipy−mpmath 8.674e-19). The division count is derived from resolution (one formula, two conventions, exact-binomial arbiter); the cost scan survives only to price T ≤ T_resolution and harvest free divisions; relegation is a composition of both seats' mechanisms, with the dominance measurement the founder's composability rule demands.

**Q1, settled, and the blind dichotomy was incomplete.** Both positions framed it as "randomised theorem vs deterministic scan." That is wrong as a dichotomy: at the merged witness (n=10, rates 0.90/0.30, size 0.01) a **deterministic order-reading gate** — one that reads *which* attempts succeeded, not only how many — achieves power 0.9833784264 at size 0.0099919656, within 5.1e-5 of the randomised optimum 0.9834296545 (γ=0.9342258766), while the best count threshold reaches only 0.9298091736 (claim 2; all 5 values confirmed by Wolfram Language, local Wolfram Engine, exit 0). So **determinism/auditability alone does not force the scan** — Position A's stated ground for its own recommendation was insufficient. What forces it is determinism **plus exchangeability**: brute force over all 2048 count-subset tests shows the threshold is already optimal in that family (claim 2, `best_count_subset_power` = threshold power exactly). An order-reading gate is reproducible from the record but uses the success *ordering* as a hidden coin: identical (successes, attempts) pairs, different verdicts. That violates the founder's standing rule that capability is a function of rates. Under both axioms: gates are count thresholds, monotonicity is **false**, and the per-budget scan (seconds) is the cost derivation. The randomised curve is retained as a monotone lower bound certifying scan near-optimality — never as a promotion rule.

**Q2, settled by the arbiter.** The two formulae are one statistic. SymPy: the doubled-arcsine gap over sd 1/√n minus the undoubled gap over sd 1/(2√n) simplifies to 0 — the doubling is a variance convention and cancels (claim 3; spans 0.4636476090 / 0.9272952180, Wolfram concurring). The residual disagreement is **which error quantity is held**. Against an exact-binomial nearest-centre placement arbiter: the per-side-α convention (z=1.645) matches its closed form at **all 6** of n ∈ {19, 38, 80, 150, 300, 2000}; the two-sided convention (z=1.96) reproduces Position B's committed T=11 at n=2000 but is optimistic in **2 of 6** cells (n=19: closed 2, exact 1; n=300: closed 5, exact 4) — confirming Position B's own small-sample caveat. At n=2000 the convention choice is T=13 vs T=11. Operational rule: **exact binomial packing is the computation; the closed form is the initial guess.** Position B's κ=2/3 serial exponent answers a different question (budget to *place* through serial escalation) and does not conflict.

**Q3, settled, and both positions were wrong.** The attempts objective is not degenerate at 2 (refuting one seat) and not confined to {2,3} (refuting the other, and my own first assertion — killed by its own falsifier and repaired, recorded in claim 4's docstring). Over 23 feasible random budgets: argmin {2: 17, 3: 5, **4: 1**}, inversion rate 0.3043, Wilson (0.1560, 0.5087); argmin-4 witness (0.8694, 0.6975, 0.8401, 0.2887) with curve {3:19, 4:18, 5:19, 6:21}, where T=2 is also *infeasible* under the attempt ceilings — Position B's F9 lower-bound conjecture, observed. But the argmin has **no dependence on the per-model attempt allowance n** — the objective has no such argument — so it cannot track resolution and cannot derive T. Role of the scan: price T ≤ T_resolution, take free divisions, nothing more.

**Q4, settled by measurement, and both blind specifications were defective.** My claim-5 v1 implemented the sign test literally as both rounds described it — "against the division-peer **majority**" — and its own falsifier killed it: under a hardening stream, majority-of-3 aggregation pushes the comparator's rate away from 1/2, breaking the sign test's null; measured false-demotion **0.5167**. The repair pairs the model against **1 randomly chosen division peer per item** (null exact under parity at any difficulty), and both mechanisms become one-sided CUSUMs calibrated on a stationary null to the same horizon false rate (h_pair=2.5, h_rasch=7.0) — Position B's windowless ARL framing proved structurally necessary, because the v1 per-test-α window had no controlled false-alarm budget. The deployable-mechanism table (claim 5, 300 sims × 6 regimes):

| regime | pair_only | rasch_only | composed |
|---|---|---|---|
| R0 null (false) | 0.0567 | 0.0567 | 0.0433 |
| R1 hardening, calibrated (false) | 0.0767 | 0.0167 | 0.0733 |
| R2 decline + cohort (correct) | 0.9500 | 0.9967 | 0.9633 |
| R3 decline, roster 1, calibrated (correct) | **0.0000** | 0.9967 | 0.9967 |
| R4 hardening, uncalibrated (false) | 0.0467 | **1.0000** | 0.0567 |
| R5 decline, roster 1, uncalibrated | 0.0000 | 1.0000* | 0.0000 (abstains) |

*rasch_only's R5 "detection" is worthless — it also fires 1.0 on the false R4. The **composition** — peer-paired CUSUM where a cohort shares the stream, Rasch CUSUM where difficulty is calibrated and no cohort exists, **abstention** otherwise — weakly dominates each alone on every scored regime and strictly on one each (vs pair_only at R3: 0.9967 vs 0; vs rasch_only at R4: 0.0567 vs 1.0). That is the committed measurement the composability rule requires; neither fix alone performs as well. Governance when both are available: **peers govern** — pairing cancels difficulty without a model.

## What I concede

The joint sandbox contains neither delivered file and no seat marker, so I audited both positions as if each were mine; concessions are to the record, by position:

- **Conceded to Position B, against A:** the randomisation arithmetic is exact (claim 2 reproduces 0.9834296545 and γ to 10 digits); and A's "keep deterministic gates for auditability" was **right for an insufficient reason** — the order-reading counterexample shows auditability does not force thresholds; exchangeability had to be added. Also conceded: the fixed-window per-test-α relegation design (A's F5 shape) was killed by its own falsifier here for exactly the reason B named — no controlled false-alarm budget — and the surviving paired rule is a CUSUM, B's machinery.
- **Conceded to Position A, against B:** "the attempts objective returns T=2 always" is false twice over (B's own F1 contradicted it; claim 4 adds argmin 4). "Some rate pairs are INFEASIBLE at any division count" is a ceiling artefact: (0.85, 0.75) is feasible at a single gate (253, 206), capable 0.950388, weak 0.009481, scipy−mpmath 2.22e-16, against the committed sweep's per-gate cap of 24 — B's Δφ√N < z_sum(2) formula is correct only as "infeasible *at these resources*," which must be said aloud. And A's peer-pairing is what ends up governing in the composition.
- **Conceded against both (and myself):** both blind texts specified the pairing as "against the division-peer majority," which my measurement shows breaks the null under drift. And my own claim 4's first assertion ({2,3}) was refuted by its own run. Three claims in this file were killed by their own falsifiers and repaired, not reverted; all three kills are recorded in the docstrings.

## Disagreement

Two things survive, sharpened:

1. **CC1's 3.65% sign-test false-rate under hardening does not square with the literal "peer-majority" specification.** With a majority-of-3 comparator I measure 0.5167 false demotion under drift; 3.65% is achievable only with a null-preserving comparator (single peer) or single terminal test. Either CC1's simulation implemented something other than what the brief's words say, or mine instantiates the words differently. **Settling measurement:** re-run CC1's simulation printing its comparator construction and test cadence; if it aggregated peers by majority and still got 3.65%, one of our streams is mis-specified and the diff will show where. Until then the *specification text* "peer majority" is defective regardless of whose number stands.
2. **The 0.40 calibration-share precondition for the Rasch arm rests on synthetic gauss(0, 2) difficulty.** No per-model-per-item outcome corpus exists in this tree to measure the real escalated-difficulty distribution. **Settling measurement:** replace the synthetic draw with the archived routing-record difficulty histogram; if the real distribution is less extreme, the precondition shrinks to a tuning note and the composition's Rasch arm arms earlier.

## Findings

- **F1 — OBSERVED, CRITICAL (Q1).** Determinism alone does not force the scan; determinism + exchangeability does, and then thresholds are optimal and monotonicity is false. Claim 2; `python3 scripts/the_joint_round_settles_the_gate_family_and_the_count_2026-10-08.py`. Wolfram second-falsifier concurs on all 5 values.
- **F2 — OBSERVED, CRITICAL (Q2).** One statistic; doubling cancels (SymPy); per-side convention exact at 6/6 n, two-sided optimistic at 2/6; T=13 vs T=11 at n=2000 is a convention choice. Claim 3, same command.
- **F3 — OBSERVED, HIGH (Q3).** Argmin {2:17, 3:5, 4:1}; inversion rate 0.3043 Wilson (0.1560, 0.5087); no n-dependence, so no derivation. Claim 4, same command.
- **F4 — OBSERVED, CRITICAL (Q4).** Peer-majority comparator breaks the sign-test null under drift: 0.5167 false demotion. Repaired to single-peer pairing: 0.0767 under hardening at matched budget. Claim 5 v1→v3, kill recorded in docstring; same command.
- **F5 — OBSERVED, HIGH (Q4).** Composition dominance table above; strict wins at R3 and R4; structural abstention at R5. Claim 5, same command.
- **F6 — OBSERVED, MEDIUM.** "Infeasible at any division count" = attempts ceiling binding; (253, 206) witness. Command: the one-liner pasted above (scipy + mpmath).
- **F7 — OBSERVED, LOW, REPAIRED.** The withdrawn bench producer printed its withdrawn headline at runtime; now prints the withdrawal pointer, numbers unchanged, falsifier pasted below.
- **F8 — HYPOTHESISED.** The claim-5 regime set omits a *small* sustained decline (~0.3 logit); the paired CUSUM vs any windowed statistic on that regime is unmeasured. Settled by adding the regime to claim 5 and comparing detection latency.

## Fix

**`scripts/the_joint_round_settles_the_gate_family_and_the_count_2026-10-08.py`** — 5 claims, all falsifiers executed, final run exit 0, full output pasted in the transcript above ending `all falsifiers passed`. Three of its own claims were killed by their own falsifiers and repaired in place (claim 4 v1; claim 5 v1, v2), each kill recorded in its docstring with the refuting numbers.

**`bench/the_division_count_is_bounded_and_the_cost_is_not_monotone_2026-10-08.py`** — runtime verdict now carries the withdrawal; executed falsifier output:

```
repair falsifier passed: headline withdrawn at runtime, numbers unchanged
```

Wolfram attribution: γ, powers, sizes and spans cross-checked were computed with Wolfram Language (local Wolfram Engine, via wolframscript), exit 0, no `Name::tag`, no `$Failed`; Wolfram was never the sole source for any claim.

## For the founder

1. **The two gate axioms** — rule that a promotion verdict must be (a) deterministic given the attempt record and (b) exchangeable (a function of successes and attempts only). Both seats now jointly recommend both. Accepting them: gates are count thresholds, two identical records always get identical verdicts, and the division cost is scanned per budget. Rejecting (b) buys power 0.9834 vs 0.9298 at the witness — paid for by verdicts that depend on *which* attempts succeeded.
2. **The held error quantity and level for the division count** — per-side α or per-boundary two-sided α, and the value. At n=2000 this is T=13 vs T=11. Convention, not measurement.
3. **The relegation false-alarm budget** — one number (horizon false rate or ARL0); both CUSUM thresholds are then solved, not chosen.
4. **Whether to purchase difficulty-calibration share in the escalation stream** — it is the precondition for relegation at roster 1 (R5 is otherwise a structural abstention), currently priced only on synthetic difficulty.

Everything else in this round is settled by the measurements above. Further passes produce no new above-threshold findings; terminating on that criterion.

<!-- verbatim-end -->

## Where the raw record lives

`bench/logs/division_count_star_2026-10-08/` holds the brief, every seat reply, the tool logs and `seat_proposals.diff`. That directory is excluded by `.gitignore:41`, so a byte-identical copy is committed under `experimental_notes/evidence/`, verified by sha256 and checked on every suite run by `bench/tests/test_panel_records_are_preserved_2026-09-11.py`.


Written under CDSFL note standard v1.7 (26 August 2026).
