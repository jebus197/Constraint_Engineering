# The discarded blind round whose one reply refuted the brief

Record written 2026-10-08T14:48:56+01:00.

**This is the seats' own output, reproduced in full.** The Personalisation directive requires external review output preserved *"in full and in unfiltered format"* and says *"Never summarise in place of the full output"*. Any summary elsewhere is downstream of this file, not a substitute for it.

This round was DISCARDED and is recorded rather than deleted, because its single landed reply produced the finding that refuted the brief it was answering.

WHAT IT ASKED. Whether the promotion ladder's division count is bounded and what each division costs, under the founder's reframing of 2026-10-07 that a football league has finitely many divisions rather than infinitely many.

WHY IT WAS DISCARDED, and the fault was CC1's, not a seat's. It was dispatched as a LONE BLIND ROUND with no joint round planned, which is not star topology. The founder caught it: *"you don't seem to have been running recent panels under star topology, blind run first?"* Measured afterwards, of 99 archived rounds collecting 2 or more replies only 15 have a joint round, and only 1 of 5 since his 2026-10-06 ruling that the topology be unskippable. Separately, the cc2 seat timed out at the 1800 s ceiling and its retry sandbox was handed the other seat's landed reply, because `panel_sandbox.build`'s `blind_of` names OTHER rounds and had no way to express "blind of my own round's other seats". The round was killed rather than allowed to produce a contaminated comparison, following the precedent set on 2026-10-05.

WHAT THE ONE REPLY ESTABLISHED, and it stands independently of the round being discarded. The fable seat showed that CC1's headline claim -- that the division-cost curve is not monotone and the count must therefore be scanned -- was an artefact of CC1's own `smallest_gate`, which forces every gate in a ladder to the same attempts-and-successes pair. The end-to-end budget constrains only the PRODUCTS of per-gate pass probabilities, so heterogeneous gates are admissible and the identical-gate costs are upper bounds rather than optima. Its witness ladder for 4 divisions costs 22 attempts against the committed 30, with end-to-end capable 0.9524672012 and weak 0.0086860657, both inside budget. CC1 reproduced the whole corrected curve by an independent Pareto dynamic program and agreed at all 13 points.

WHAT CC1 DID WITH IT. The claim was withdrawn, the producer was amended to carry its own withdrawal rather than being deleted, and the guard that defended the conclusion was rescoped rather than removed. Both faults that caused the discard were fixed at source and are held by tests: `bench/tests/test_a_blind_round_has_a_joint_round_2026-10-08.py` and `bench/tests/test_a_blind_round_is_blind_of_its_own_coseat_2026-10-08.py`.

ITS SUCCESSOR is `division_count_blind_2026-10-08`, which asks the same question with the founder's two further additions -- whether the count is derivable at experiment start from task complexity and available resources, and relegation on sustained degradation -- and which carries a joint round.

## Seats and cost

1 seat(s): `fable`. **0 paid dispatches**, enforced by `PANEL_ONLY=cc2,fable`.

## The brief, as dispatched

<!-- verbatim-begin: the brief as dispatched -->

# The promotion ladder has a BOUNDED number of divisions, and nobody has priced them

You are one seat of a 2-seat panel, answering BLIND. You cannot see the other seat's
reply and it cannot see yours. A joint round follows once both blind replies are in.
Disagreement between the 2 of you is the output this round exists to produce; it is
not a problem to be smoothed away, and a round that agrees by deference has produced
nothing.

Work in the sandbox repository tree you have been given. RUN things. Every figure
below names the script that produces it, and you are expected to execute those
scripts and contradict them where they are wrong. The tool output is the evidence;
reasoning selects and interprets it but never substitutes for it.

---

## 1. The founder's framing, in his own words

He has now stated this 4 times and it is the constraint everything else answers to.
**Capability is a MEASURED RATE. Model names are not a measure of anything.** The
roster size is arbitrary and the schema must not care what it is:

> "the system should be able to cope with 5, or 6, or 70, or 700 models (or whatever),
> and that the only goal is to use all the available resources efficiently to effect
> the best outcome in all cases."

> "The simplest understanding of this is, problem in (by the researcher, who then
> waits) -> problem computed efficiently by the models) -> solution out. In between
> that sits all the machinery of the schema, including capability fingerprinting, the
> routing ladder and so on."

**The ladder is BIDIRECTIONAL**, and he is explicit about what must not be allowed to
count as evidence of improvement:

> "A ladder is bidirectional. It goes both up and down. So if a weaker model gets
> better at doing a job (say for example if a vendor releases an updated version, it
> should be able to climb the routing ladder, based on its demonstrated improvement in
> capability. Conversely if a stronger model proves less able, say due to some technical
> glitch or other, it should be able to climb down the ladder to a point where it again
> becomes effective. But what we need to guard against is simply counting when a model
> is successful as an 'improvement in capability'. The only measure of improved
> capability is actual observed capability (and the converse.)"

**Promotion requires demonstrated capability over SEVERAL tries on DIFFERENT problems**,
not one success:

> "I didn't originally intend to say models only needed one successful try. They should
> demostrate their capability over several tries with different problems, before being
> considered for promotion. Perhaps a good analogy is a football team..."

**And this is the part NO SEAT HAS YET BEEN ASKED ABOUT — the division count is finite:**

> "But running with the football analogy, we clearly don't have infinit[e] divisions, we
> have division 1, division 2, division 3, the Premier League. So the number of possible
> leagues is finite. The position each team or player operate[s] in within these bou[nd]s
> is also finite."

> "We also have the Vauxhall conference and the other lower leagues. But either way the
> number is bounded, not infinite."

**Also his, on when to stop waiting for a seat:** "we should harvest results when a model
is done, not by setting an arbitrary wall clock limit", and "A full response is always
preferable."

---

## 2. What has been built since the last round, and what it measures

`bench/the_division_count_is_bounded_and_the_cost_is_not_monotone_2026-10-08.py` takes his
bounded-divisions point and prices it. Climbing T divisions means clearing T-1 promotion
gates in series. Gates multiply, so the per-gate sample size falls as T rises while the
number of gates paid for rises. The error budget is held fixed across the whole scan — a
model whose true resolve rate is 0.90 reaches the top with probability at least 0.95, and
one at 0.50 with probability at most 0.01, END TO END — so the comparison is about division
count and nothing else. Each figure is computed twice, SciPy's binomial tail against an
exact mpmath sum.

The results, every one of which you should re-run and attack:

- The cheapest ladder is **2 divisions**, one gate, at <!-- figure: cheapest ladder | bench/the_division_count_is_bounded_and_the_cost_is_not_monotone_2026-10-08.py | cheapest_total_attempts: 19 --> 19 attempts. The dearest in range is 13 divisions at 72.
- The 4 divisions he named cost <!-- figure: four divisions cost | bench/the_division_count_is_bounded_and_the_cost_is_not_monotone_2026-10-08.py | total_attempts_at_his_count: 30 --> 30 attempts, and are **not** a local minimum: 3 divisions cost 28.
- The cost curve is **not monotone** — 2 downward steps and 6 pairs where more divisions cost strictly less, 14 divisions at 52 against 13 at 72. So the division count must be SCANNED; neither "as few as possible" nor "as many as the bound allows" is right.
- The 5-rung rule derived separately in `bench/what_several_tries_has_to_mean_2026-10-08.py` asks <!-- figure: promotion attempts per rung | bench/what_several_tries_has_to_mean_2026-10-08.py | attempts_per_rung: 19 --> 19 attempts per rung with 11 successes required, giving <!-- figure: capable reaches top | bench/what_several_tries_has_to_mean_2026-10-08.py | 0.967152 --> 0.967152 for a capable rate and 0.00355962 for a weak one.

**The boundary that result does not cross, and it is the question this round is really
about.** Total attempts prices the climb as though every attempt were pure overhead. It is
not: a model sitting in a lower division is DOING THAT DIVISION'S WORK while it climbs, and
that work has value, whereas a model in front of a single gate performs 19 attempts of pure
qualification and produces nothing a researcher can use. Tiers can therefore only be
justified by the value of the work done DURING the climb — which that script does not
measure and does not pretend to.

---

## 3. The dispatch change you are running under, and its figures

The 2 seats on this panel share one subscription. Until today they were dispatched strictly
one after the other. On the founder's ruling they are now **staggered**: both start, 20
seconds apart. Producer: `scripts/serialising_the_free_seats_costs_40_percent_2026-10-08.py`.

- Serialising cost a mean <!-- figure: serialisation saving | scripts/serialising_the_free_seats_costs_40_percent_2026-10-08.py | 0.3969 --> 0.3969 of wall clock, bootstrap CI [0.3801, 0.4126] over 91 archived rounds where both seats answered; median <!-- figure: serial wall clock | scripts/serialising_the_free_seats_costs_40_percent_2026-10-08.py | median_serial_wall_clock_s: 1611.6 --> 1611.6 s serial against 943.8 s staggered.
- 20 s sits inside a window with a floor and a ceiling. The floor is 18.7 s, the one genuinely simultaneous co-failure in the record, which sits at session-establishment time (`scripts/the_contention_evidence_is_cap_confounded_2026-10-07.py`; the other 2 matched co-failures are both seats hitting 1 shared deadline, which is arithmetic rather than contention, and the honest recomputation is 1 of 5, Wilson [0.0362, 0.6245], one-sided exact p = <!-- figure: cap-confound recomputation | scripts/the_contention_evidence_is_cap_confounded_2026-10-07.py | 0.107550 --> 0.107550). The ceiling is the shortest first-seat duration, <!-- figure: shortest first seat | scripts/serialising_the_free_seats_costs_40_percent_2026-10-08.py | 26.7 --> 26.7 s, because SymPy reduces `max(d1, s+d2) <= d1+d2` to exactly `s <= d1` and z3 returns `unsat` on any counterexample under it and `sat` above it.
- `PANEL_STAGGER_S=0` still restores strict serialisation. Nothing was removed.

---

## 4. Figures previously carried to a panel that are WITHDRAWN

Reason from these corrected values, not the originals. Several were found by seats.

1. The per-seat-per-round critical finding rate was **assumed** 0.3; it is **<!-- figure: measured critical rate | bench/the_intra_round_correlation_measured_2026-10-07.py | 0.233740 --> 0.233740**, Wilson [0.215572, 0.252945], exact binomial p = 5.6e-11 against the assumption.
2. A spurious-convergence factor of **8.49986** was stated as a property of the convergence gate. It is an upper bound under independence. At the measured intra-round correlation of 0.4060 the 6-seat-to-4-seat factor is **1.4291**.
3. A sensitivity span of **7.7915** was called plausible. It spans correlation 0 to 0.8; over the 0.1 to 0.5 range actually quoted it is 6.053.
4. "Rotation costs identical dispatches" is **WITHDRAWN**: measured at 579 dispatches for 270 resolved against 444 for 396 — 30% more dispatches and 32% fewer resolved.
5. Pooled correlation is confounded by a factor of **1.7202** by between-experiment variation; simulated runs give 0.681 against 0.275 for live ones, so a simulated arm under-reports this hazard by construction.
6. **New, and this one is mine.** An analysis note of today stated the climb costs "between 52 and 182 attempts across 2 to 14 tiers", that "7 tiers cost 91 attempts where 5 cost 95", and that his 4 divisions land on "a local optimum at 68 attempts". **None of those 5 figures reproduce.** The committed scan gives 19 to 72 attempts; 7 divisions cost 48 and 5 cost 36; and 4 divisions cost 30 and are not a local minimum. They were computed in session with no committed producer. The non-monotonicity survives; the figures carrying it did not.

---

## 5. Also live, since you may reason from the gate

- **Gamma now gates wherever a slope exists**, including the sparse branch where it previously went reported-only below 8 cumulative criticals. `_gamma_is_estimable` in `bench/reference_runner_v3.py` separates the 0.0 sentinel (4 distinct causes, only 1 a slope) from a real slope. Where no curve exists, guarded vacuity applies and a dead panel is REFUSED. Gamma is load-bearing in this project and is not up for demotion.
- **The ladder-depth default is now exhaust**, `routing.DEFAULT_MAX_RUNGS = 0`. Over 305 archived routing records, 143 hit the old cap of 2 and 103 were abandoned unresolved. The resolve rate beyond depth 2 had never been measured because the cap prevented it.
- **The free seat roster is now 6 rungs**, the 6th placed last on 0 recorded attempts — evidence-derived placement, not name-chosen.

---

## 6. What to decide

1. **How many divisions should the ladder have?** Give a number with the budget it meets. If total-attempts-to-top is the wrong objective, say what the right one is and price it. The strongest answer measures the value of work done during the climb, which nothing in the repository does yet.
2. **Is a single gate actually right?** The scan says 2 divisions is cheapest on attempts. Either defend tiers on a metric the scan does not use, or concede the single gate and say what is lost.
3. **How does a model climb DOWN?** Demotion on observed decline is required and unbuilt. Name the statistic, the window, and what stops a transient outage from demoting a capable model — remembering that a transient fault is NOT the same condition as sustained decline, and that no model is ever benched.
4. **What stops a success count being mistaken for improved capability?** This is his explicit guard and it needs a mechanism, not a promise.
5. **Does the division structure survive a roster of 700?** And of 1?

## 7. Output

Return these fields, each with a real body. A heading with nothing under it is not an answer.

- `## Verdict` — SOUND, SOUND WITH REPAIRS, or UNSOUND, on the division-count analysis as it stands.
- `## Findings` — each labelled OBSERVED (name the run, file and line) or HYPOTHESISED (say what would settle it), each with a severity, each with the command that shows it.
- `## Fix` — deliver each fix as a file at its real path in the sandbox repository tree, with an executed falsifier beside it. Paste the falsifier's actual output. A fix you have not tried to break is a hypothesis, not a fix. Repair rather than revert where both are available.
- `## Disagreement` — your strongest disagreement with this brief's own framing, named as a disagreement. If a figure above is wrong, say which and show the command. If the whole tier idea is decoration, say so.
- `## What would refute me` — the measurement or command that would overturn your own verdict, stated so that someone else could run it and defeat you.

## 8. Termination

Stop when further passes produce no new above-threshold findings — a finding is above
threshold if missing it could cause real-world failure. Do not nitpick, do not generate
findings for their own sake, and do not police style. Diminishing returns is the stop
criterion, not exhaustion of the clock. Take the time you need to deliver a full
response; a truncated answer is worse than a slower one.

Numbers in digits, never in words. No model names where a rate will do.


<!-- verbatim-end -->

## Seat: fable

Route `claude_cli`, 21 recorded tool call(s).

<!-- verbatim-begin: fable (panel division_count_and_bidirectional_ladder_blind_2026-10-08) -->

All evidence is in: the falsifier executed FALSIFIED against the real target, the corrected producer passes all checks, and Wolfram independently confirms the key ladder. Final answer.

---

## Verdict

**UNSOUND as it stands** — on its own load-bearing claim. The arithmetic inside `bench/the_division_count_is_bounded_and_the_cost_is_not_monotone_2026-10-08.py` is correct and double-verified (I reproduced every row; scipy and mpmath agree everywhere), but the conclusion it draws — `claim_the_cost_curve_is_not_monotone`, in its own words "THE LOAD-BEARING CLAIM: the optimum must be scanned, not reasoned to" — does not survive optimisation over its own constraint set. `smallest_gate` (lines 122–158) forces every gate in a ladder to the same (attempts, successes) pair. The end-to-end budget constrains only the **products** of per-gate pass probabilities, so heterogeneous gates are admissible. Optimised exactly over them (bi-criteria DP over Pareto frontiers of (log pass_capable, log pass_weak), every optimum re-verified by an mpmath sum at 50 dps), the cost curve is **strictly monotone non-decreasing**: 19, 21, 22, 25, 28, 30, 33, 36, 38, 41, 42, 45, 48 for 2–14 divisions. 0 downward steps, 0 inversions. "As few as possible" IS right on the attempts metric, and this is now a derivation, not a scan result: merging 2 adjacent gates into 1 composite AND-rule on the concatenated attempts preserves total attempts and end-to-end error exactly, so cost(T) ≤ cost(T+1) for all T; the floor is 19 because by the Neyman–Pearson lemma the most powerful single-gate test of rate 0.90 against 0.50 is a threshold on the success count, which is the (19, 15) gate. What **survives**, strengthened: a single gate is cheapest on attempts, and tiers need a justification this metric cannot supply.

## Findings

**F1 — OBSERVED, CRITICAL. The non-monotonicity verdict is an artifact of the identical-gates restriction.**
Run: `python3 bench/tests/falsifier_the_division_scan_costs_are_not_optima_2026-10-08.py` (output pasted under Fix). File: `bench/the_division_count_is_bounded_and_the_cost_is_not_monotone_2026-10-08.py`, `smallest_gate` lines 122–158 and `claim_the_cost_curve_is_not_monotone` lines 184–211. The 72→52 drop from 13 to 14 divisions, the brief's showcase inversion, is a knife edge: 0.01^(1/12) = 0.6813 falls just below the (4,2) gate's weak pass rate 11/16 = 0.6875 while 0.01^(1/13) = 0.7017 clears it. Under exact optimisation there are no inversions, so "the tier count has to be SCANNED; neither 'as few as possible' nor 'as many as the bound allows' is right" is a wrong result in the artefact's specified function (§10 category 1).

**F2 — OBSERVED, MAJOR. Every committed per-T cost above T=2 is an upper bound, not an optimum.** Dearer at every T ≥ 3, maximum excess 29 attempts (T=11: 70 against 41); committed matches the optimum only at T=2. His 4 divisions cost 22, not 30; 3 cost 21, not 28. Run: `python3 bench/the_cost_curve_is_monotone_once_gates_may_differ_2026-10-08.py` (section 1). Wolfram Language (local Wolfram Engine, via wolframscript) independently confirms the 22-attempt ladder: {0.9524672012, 0.0086860657} against the budget {≥0.95, ≤0.01}, matching scipy/mpmath to 10 digits.

**F3 — OBSERVED, MODERATE. Attempts-optimal tiers are nominal tiers.** Every exact optimum concentrates discrimination at exactly 1 strong gate; the rest are (2,1)/(3,1) formalities a 0.50-rate model passes 75–87.5% of the time (producer section 4). So minimising attempts buys end-to-end certification and near-zero intermediate **placement** — which is the thing a routing ladder exists for. This reframes decision 2 below.

**F4 — OBSERVED, MODERATE. What buys divisions is sample size per decision, not the climb budget.** Adjacent division floors are distinguishable at error 0.05 both sides only if the per-decision sample resolves them: n=19 supports 2 divisions in [0.50, 0.95]; 4 divisions need n≈114; 5 need n≈150 (producer section 5). The founder's "football season" analogy is quantitatively apt: his 4 divisions cost roughly 3 seasons' halves of evidence per promotion decision, or they are nominal.

**F5 — OBSERVED, MINOR. A roster of 1 is unrepresentable.** `TIER_RANGE = range(2, 15)` (line 87) cannot express T=1 (0 gates, 0 qualification attempts), which is the correct ladder when no routing choice exists.

**F6 — OBSERVED, MINOR. The two committed producers price a 5-level ladder inconsistently and neither says so.** `what_several_tries_has_to_mean_2026-10-08.py` spends 5 × 19 = 95 attempts (per-rung weak pass 0.324 — real placement per rung); the scan's 5-division row spends 36; the exact optimum is 25 (near-zero placement). Same end-to-end budget, 3 answers, because they price different quantities (placement against certification). Run both; compare `overall_P_weak_model_reaches_top` paths.

**F7 — HYPOTHESISED, MINOR. "Total attempts to climb" counts exactly 1 qualification window per gate.** A capable model fails a window with probability ~0.04 and the retry rule is undefined; expected attempts are higher than gates × a. Settled by: define the retry semantics and compute the expected-attempts sum; the ranking across T is unlikely to change but the figures are floors.

## Fix

**File 1 (producer, written and executed):** `bench/the_cost_curve_is_monotone_once_gates_may_differ_2026-10-08.py` — exact heterogeneous optimum per gate count, mpmath 50-dps re-verification of every optimum, the merge-construction check, the nominal-tiers count, and the rate-resolution scan. Output (abridged; full run exits 0, `ALL CHECKS PASS: True`):

```
 4 divisions: committed  30 -> exact  22 (excess  8)  [capable 0.9525, weak 0.0087, mpmath True]
11 divisions: committed  70 -> exact  41 (excess 29)  [capable 0.9567, weak 0.0085, mpmath True]
committed matches the optimum only at divisions: [2]
costs: {2: 19, 3: 21, 4: 22, 5: 25, 6: 28, 7: 30, 8: 33, 9: 36, 10: 38, 11: 41, 12: 42, 13: 45, 14: 48}
steps_down: 0   inversions_more_tiers_cost_less: 0   is_monotone_non_decreasing: True
mean_increment_per_added_division: 2.417
every optimum has exactly 1 strong gate: True
n= 19: 2 divisions [0.5, 0.853]   n=114: 4 divisions [0.5, 0.658, 0.796, 0.91]
```

**File 2 (falsifier, written and executed):** `bench/tests/falsifier_the_division_scan_costs_are_not_optima_2026-10-08.py` — imports the REAL target module, uses the target's **own** `_sf_mpmath` and budget constants, fails iff the defect is present. Actual output:

```
target reports 4 divisions cost 30 attempts
candidate ladder [(2, 1), (2, 1), (18, 14)]: 22 attempts, e2e capable 0.952467 (need >= 0.95), e2e weak 0.008686 (allow <= 0.01)
feasible under the target's own budget: True; cheaper: True
FALSIFIED
AssertionError: the scan's cost for 4 divisions (30) is not the optimum: ...
exit=1
```

I attempted to break the fix: the gate-menu filter (every gate needs pass_capable ≥ 0.95, since all factors are ≤ 1) is a lemma, not a heuristic, so no feasible ladder is lost; the DP caps (gate ≤ 60 attempts, total ≤ 80) sit far above every optimum found; and the merge check confirms series-equals-composite to 1e-15 at both rates. **Nothing removed:** the committed scan stands as the homogeneous-family producer; the new file corrects the inference, repairing rather than reverting.

**Decisions asked in §6**, each priced:

1. **Division count.** On attempts-to-top: **2**, at 19 attempts, meeting the 0.95/0.01 budget — and that is now a theorem (merge + Neyman–Pearson), so stop scanning this metric. The **right** objective is placement at confidence: the division count the evidence supports equals the number of distinguishable rate bands at the per-decision sample you will pay — 2 at n=19, **4 at n≈114**, 5 at n≈150. The climb-work value the brief says nothing measures has a measurable proxy already in the archive: resolved-per-attempt per rung over the 305 archived routing records; that producer is the next committed script, not something I can conjure here.
2. **Single gate.** On attempts, yes, and what is lost is exactly F3: placement. A 19-attempt single gate yields a 1-bit verdict; routing wants the highest division whose floor a model demonstrably meets. If tiers exist they must use discriminating gates (the 19/11 rule's per-rung weak pass of 0.32, not a (2,1) formality) — and then rate resolution caps meaningful tiers at 2 unless the per-decision budget rises toward 114+.
3. **Climb down.** Statistic: the exact binomial tail on the last *a* **substantive** attempts at the current division against H0: rate ≥ division floor; demote exactly 1 division when the one-sided p < 0.01 (symmetric to the weak-side promotion budget). Window: the division's own gate size *a*, required to span ≥2 distinct problems and ≥2 sessions. Transient guard: infrastructure failures (timeout, session establishment — the classes `scripts/the_contention_evidence_is_cap_confounded_2026-10-07.py` already separates from substantive failure) are **excluded from the window**, so an outage produces excluded attempts, not evidence of decline; sustained decline produces substantive failures across sessions. No benching: the lowest division is the floor and re-promotion is immediately available. I deliberately shipped no code for this: unwired demotion logic in `routing.py` would be an addition nothing reaches — it belongs in the change that wires it to dispatch with its test.
4. **Success count ≠ capability.** Mechanism, not promise: promotion is decided by the **Wilson lower bound** of the success rate over a window of **distinct problem ids** at the target division's difficulty clearing the division floor. A raw count cannot move the lower bound without the rate moving; dedup by problem id blocks repeat-success farming; difficulty stratification blocks easy-work inflation; window expiry makes the same statistic the demotion statistic, which is what "bidirectional" means operationally. The s-of-a gate is already a rate test — the missing pieces are dedup and expiry only.
5. **Roster 700 and 1.** Survives 700 iff divisions are rate bands: the count is a property of the rate axis (F4), evaluation is per-model and embarrassingly parallel, cost linear in roster. At 1 the ladder must degenerate to 1 division and 0 qualification attempts — currently unrepresentable (F5), and the honest test of whether the schema "does not care what the roster size is."

## Disagreement

The brief presents as established: "The cost curve is **not** monotone — 2 downward steps and 6 pairs where more divisions cost strictly less, 14 divisions at 52 against 13 at 72. So the division count must be SCANNED." **Refuted above**, command pasted: those are properties of the identical-gates restriction, not of the division count; the exact curve has 0 downward steps and the dearest ladder in range is 14 divisions at 48, not 13 at 72. Second disagreement, with the framing itself: §2 says tiers "can therefore only be justified by the value of the work done DURING the climb." Half right — the other justification is **placement resolution**, the ladder's routing function, which is measurable now (F4) and is a different quantity from climb-work value. The tier idea is not decoration, but on the brief's own metric it is, provably; its real content lives on a metric the brief did not name.

## What would refute me

Any of, runnable by anyone: (1) exhibit a ladder of g gates, verified feasible by the target's own `_sf_mpmath` under `P_CAPABLE_REACHES_TOP_MIN`/`P_WEAK_REACHES_TOP_MAX`, costing less than my exact figures {1:19, 2:21, 3:22, 4:25, 5:28, 6:30, 7:33, 8:36, 9:38, 10:41, 11:42, 12:45, 13:48} — one counterexample kills the monotonicity claim; (2) rerun my producer with `MAX_GATE_ATTEMPTS` and `MAX_TOTAL_ATTEMPTS` raised (say 120/160) and show any optimum drops — that would mean my caps clipped the search; (3) break the menu lemma: show a feasible ladder containing a gate with pass_capable < 0.95 (the product-of-factors-≤-1 argument says impossible; that is the step to attack); (4) show an operational constraint in the harness that gates must be identical per ladder and single-threshold — then the committed scan's family is the true design space and its figures, though still not division-count properties, stand as the operative costs.

<!-- verbatim-end -->

## Where the raw record lives

`bench/logs/division_count_and_bidirectional_ladder_blind_2026-10-08/` holds the brief, every seat reply, the tool logs and `seat_proposals.diff`. That directory is excluded by `.gitignore:41`, so a byte-identical copy is committed under `experimental_notes/evidence/`, verified by sha256 and checked on every suite run by `bench/tests/test_panel_records_are_preserved_2026-09-11.py`.


Written under CDSFL note standard v1.7 (26 August 2026).
