# Dynamic roster and derived-capability routing: the free panel in full

Record written 2026-10-08T01:00:03+01:00.

**This is the seats' own output, reproduced in full.** The Personalisation directive requires external review output preserved *"in full and in unfiltered format"* and says *"Never summarise in place of the full output"*. Any summary elsewhere is downstream of this file, not a substitute for it.

WHAT WAS REVIEWED. The design for allocating falsification work across an arbitrary number of models: removing the cap on ladder depth, ordering by a derived key over measured capability and cost, and using a lower confidence bound rather than a point estimate. Four committed artefacts carried the analysis, all runnable: why_one_ordering_cannot_serve_both_objectives_2026-10-07.py, allocation_by_measured_capability_2026-10-07.py, a_shrinking_roster_converges_sooner_2026-10-07.py, and the live ladder in routing.py.

WHY. The founder had observed that 3 successive proposals each dissolved half of the try-order tension and left the other half standing, and he set 9 requirements the design must meet. The 9th was his correction of this brief's own first draft, which had asserted a contradiction between 2 of his rulings that does not exist: benching is a permanent policy choice and is forbidden, while a technical fault or a network outage is transient and the model may return. The code conflates the 2 conditions in its own words.

HOW THE ROUND RAN. 2 free seats, 0 paid, star topology, blind round. Attempt 1 of the round was WITHDRAWN before any seat answered, because the brief stated a spurious-convergence factor of 8.49986 as a property of the convergence gate when it is an upper bound holding only under independent seats; ABANDONED_ATTEMPT_1.md in the round directory records that withdrawal. The re-dispatched brief states the bound as a bound, carries the correlation sweep, tells the seats the first version overstated it, and asks them how the correlation could be measured from the archive. 13 figures were declared in the brief and every one re-executed and reproduced before dispatch.

cc2 answered with 14,564 characters, 2,178 words and 70 tool calls, taking 3421.4 s across 2 attempts after attempt 1 was killed at the 1800 s cap. fable answered with 8,142 characters, 1,104 words and 62 tool calls in 955.0 s on its first attempt.

WHAT WAS DONE WITH THE FINDINGS. Nothing is merged into the canonical tree; both seats' work is a proposal with evidence. cc2 wired its roster-aware quiescence fix into the live runner at 3 sites, with the roster argument defaulting to None so today's behaviour is reproduced exactly, and 119 routing and gate tests plus 435 convergence tests pass. It left its circuit breaker, capability ledger and roster registry unwired by choice, on the ground that wiring the breaker changes what every live experiment does on a dead seat, which is the founder's ruling to make. fable delivered 6 fixes with falsifiers passing, including edits flipping the no-cap default and updating 3 superseded assertions from 2026-09-24 to the founder's ruling.

5 items are carried to the founder and named in the synthesis note: the endgame one-sidedness at reference_runner_v3.py:9207-9215, where a sparsity fallback makes gamma reported-not-gated whenever cumulative criticals fall below 8; the absolute full-roster false-quiet rate of 0.1159, which no roster-aware fix addresses; flipping the cap default to exhaust, which changes what 23 routing-enabled configs dispatch; the degraded-convergence policy both seats recommend and neither can authorise; and whether the runner's caps and retry budget are reset from the measured distribution.

THE DISAGREEMENT IS PRESERVED RATHER THAN RESOLVED. The seats split on whether cost can be a single scalar. cc2 constructed an instance whose budget-constrained optimum is not optimal for any latency weight across 4001 tested values, concluding a hard-capped resource needs a constraint. fable proved with z3 that the exchange rule survives any fixed non-negative linear combination, concluding a scalar suffices. Both results are correct because they answer different questions, one about ordering and one about feasibility, and the synthesis is a scalar for the order with a separate constraint for the cap.

THE BRIEF WAS REFUTED ON BOTH PARAMETERS BEHIND ITS HEADLINE FIGURE, and that refutation is the round's most useful output after the 2 findings above. The assumed per-seat-per-round critical rate of 0.3 is rejected by the archive at p = 5.6e-11; the correlation the brief called unmeasured had been measured; and the quoted span of 7.7915 covers a correlation of 0 to 0.8 rather than the 0.1 to 0.5 the brief called plausible, where the correct value is 6.053.

## Seats and cost

2 seat(s): `cc2`, `fable`. **0 paid dispatches**, enforced by `PANEL_ONLY=cc2,fable`.

## The brief, as dispatched

<!-- verbatim-begin: the brief as dispatched -->

# Derived-capability routing with a dynamic roster: review the design and fix what is broken

## What you are reviewing

A design, not yet built, for how CDSFL should allocate falsification work across an arbitrary number of models. Four artefacts carry the analysis, all committed and all runnable:

- `bench/why_one_ordering_cannot_serve_both_objectives_2026-10-07.py`
- `bench/allocation_by_measured_capability_2026-10-07.py`
- `bench/a_shrinking_roster_converges_sooner_2026-10-07.py`
- `bench/routing.py`, which holds the live ladder and `rank_falsifier_writers`

Run each of them. Do not take the figures below on trust; they are reproducible and several of them were wrong on their first attempt.

## The founder's requirements, verbatim where possible

He has stated 9. The first 7 are from earlier today, the last 2 from tonight.

1. Roster size is arbitrary: *"It could be 5, or 6, or 70, or 500, or 1."*
2. No cap on ladder depth: *"I don't think there should be a cap at all ... the problem should run until it is either resolved, or the ladder is exhausted."*
3. Allocation by measured capability, never by name: *"the only thing that should impact on capability is measured capability. A models name should have little to do with it, beyond recording this."*
4. Never hand a model work it cannot do: *"there is still no point handing a cheaper model work it is unlikely to be able to do."*
5. Bidirectional: *"A ladder is bidirectional. It goes both up and down ... if a weaker model gets better at doing a job ... it should be able to climb the routing ladder, based on its demonstrated improvement in capability. Conversely if a stronger model proves less able ... it should be able to climb down."*
6. A success is not a capability gain: *"what we need to guard against is simply counting when a model is successful as an 'improvement in capability'. The only measure of improved capability is actual observed capability."*
7. Efficiency with the researcher waiting: *"problem in (by the researcher, who then waits) -> problem computed efficiently by the models -> solution out."*
8. Any model dropping out must not block the run: *"if a model drops off the list (say due to my Max subscription limits, or a technical issue with that model), it should not block an experimental run until completion, or convergence. The system should be able to adapt dynamically in those circumstances."* And, correcting the scope: *"Not just 'that' model, but 'any model'."*
9. Readmission, which is his correction of this brief's first draft: *"Benching a model is setting it aside permanently. A model might come back if it recovers from a technical issue, or a network outage. They are different conditions."*

Requirement 9 is the one to read most carefully, because the first draft of this brief got it wrong. It asserted a contradiction between requirement 8 and his standing rule against benching. There is no contradiction. Benching is a permanent policy choice and is forbidden. A technical fault or a network outage is transient and the model may return. The code conflates the two, in its own words: `refusal_for` in `bench/seat_aliveness_2026-10-06.py` documents itself as returning *"a REFUSAL rather than a filtered roster, because dropping a seat is benching it and the standing rule forbids that."*

## The proposed design

Three parts, each with its justification.

**Part A, remove the cap.** With no limit on depth every seat is eventually reached, so the probability that nobody resolves a finding is taken over the whole roster and becomes a constant. The question "which seats do we try" then has no content. This is the founder's own ruling and `max_rungs=0` is already wired to mean exhaust.

**Part B, order by a derived key.** Expected cost to the first CONFIRMED verdict is the sum over j of c_j times the product over i before j of (1 minus p_i). Seat i belongs before seat j exactly when p_i times c_j is at least p_j times c_i. Because this is a comparison over 2 measured numbers rather than a stored list, it is roster-size agnostic and bidirectional by construction: raise a seat's measured capability and it rises, lower it and it falls, with no tuple to edit.

**Part C, use a lower confidence bound rather than a point estimate.** A seat with 1 success from 1 attempt has a point estimate of 1.0 and outranks a seat at 60 of 70. Its Wilson lower bound is 0.206549 against 0.756616, and a newcomer needs 12 consecutive successes before its lower bound can pass. A seat with no measurements has a lower bound of 0 and sorts last, then climbs on evidence, so no placement decision is needed for a new model.

## What the design does NOT yet solve, and what you must fix

Two requirements fail, and a third hazard was found while measuring them. The founder asked specifically what the unsolved ones are and how to repair them. Answer that.

**Unsolved 1, requirement 7.** Cost in Part B is money alone, while the researcher pays in time. On a hard finding with 4 weak cheap seats at a 2 percent resolve rate and 1 strong seat at 80 percent costing 100, ordering by money puts the strong seat last: 4.80396 expected dispatches against 1.776318, to save spend by a factor of 1.0485. Pricing each dispatch in waiting as well as money reorders the same key with no new rule, crossing to capability-first at a latency weight of 2. Is that the right repair? Is a single scalar weight sufficient, or must cost be a vector the researcher sets per task?

**Unsolved 2, requirement 6.** The guard belongs to the estimator, not the ordering, and nothing in the repository currently estimates capability this way. State what the estimator must record per attempt, and what happens on the first attempt a new model ever makes.

**The hazard, and it is the serious one.** Adapting dynamically to a dropped seat makes spurious convergence more likely, and the two-sided gate cannot see it. The gate requires gamma_critical at or above 0.30 AND K consecutive rounds with 0 new criticals. The second condition gets easier as the roster shrinks, because fewer seats generate fewer findings.

**READ THE NEXT PARAGRAPH BEFORE THE NUMBERS. THE FIRST VERSION OF THIS BRIEF OVERSTATED THIS HAZARD AND WAS WITHDRAWN BEFORE ANY SEAT ANSWERED IT.** It reported a single factor as though it were a property of the gate. That figure assumes the seats are INDEPENDENT, which is the most favourable possible case for the claim, and the seats in a round are not independent: every one of them receives a byte-identical brief and the same target, so a round is plausibly productive or barren for all of them together.

**What is actually established.** With a per-seat-per-round new-critical probability of 0.3 and K of 3, the chance of K consecutive quiet rounds arising by chance alone rises as the roster shrinks, and the size of that rise depends on the intra-round correlation. Under independence the factor going from 6 seats to 4 is 8.49986 and from 6 to 2 is 72.247616; SymPy, mpmath and exact rational arithmetic agree, and Wolfram Language independently returns 8.49985975231408 for the first. With a shared per-round latent factor the same 6-to-4 factor falls to 3.8236 at a correlation of 0.1, 1.9200 at 0.3 and 1.4043 at 0.5, by exact integration, with a Monte Carlo simulation agreeing to within 10 percent at the midpoint.

**So the direction is robust and the magnitude is not.** The factor exceeds 1 at every correlation tested, so a shrinking roster always goes quiet sooner, and independence is the upper bound so no correlation can inflate it. But the magnitude moves by a factor of 7.7915 across a plausible range, on a parameter this project has never measured.

**The correlation is measurable and nobody has measured it.** Per-round, per-seat findings are recorded, so the intra-round correlation is an empirical quantity rather than one anyone has to assume. Treat its absence as one of the findings, and say how you would measure it from the archive.

**Note carefully what this does NOT weaken.** The reason to record the live roster beside the quiet-round count does not depend on the magnitude at all, because the two causes are indistinguishable from the count whatever the correlation is. The factor sets how urgent the repair is, not whether it is needed. If you think that reasoning is wrong, say so — it is the load-bearing step.

Dropout is not an edge case. At a per-seat-per-round failure probability of 0.01 over a 10-round 6-seat run, the chance of losing at least 1 seat is 0.452843, and at 0.02 it is 0.702447; a simulation, a closed form and scipy's binomial agree.

z3 establishes that the observed count alone cannot separate the 2 causes: 0 new criticals from a healthy panel and 0 from a depleted one are the same integer, and the search for a distinguishing value returns unsat. Recording the live roster beside the count makes them formally separable, because a round cannot be both intact and degraded.

## What the repository actually does today, measured

Verify each of these by execution before accepting it.

- The aliveness probe runs ONCE, before round 1, and `_refuse_if_a_route_is_dead` makes the runner return without starting. There is no re-probe anywhere, so a seat that drops out at one moment and recovers minutes later can never rejoin.
- Mid-run the system already adapts in 2 places: a failed ladder rung is logged and the ladder advances, and in the post-convergence sweep *"a dead model just skips its turn"*.
- Per-round responders ARE recorded as `models_responded`, and the per-round response files are described in the code as the ground truth of who answered.
- A RESUME refuses on a partial round, a guard added after an OpenRouter-402 cascade left a checkpoint holding responses from 2 of 5 models.
- The convergence gate consults none of this. `active_models` appears exactly once in the whole active runner, inside that resume guard, so the dynamic-roster hook exists as a field name that nothing maintains.
- `rank_falsifier_writers` already appends models absent from the strength tuple AFTER the ranked ones, so the tuple is a priority prefix rather than an allowlist. A new model is therefore already tried, just last.
- The 47 experiment configuration files declare 5 display names and 0 Fable. Fable was added to the ladder tonight at the last position, on evidence, and no config reaches it yet.

## Required: fixes, not only findings

For each problem you raise, propose a fix. A finding without a repair is half a contribution. Specifically:

1. Name the third state the design needs between "available" and "benched", and say how a transiently unavailable seat is re-probed and readmitted mid-run without that becoming benching by another name.
2. Say what the convergence record must carry so a degraded convergence cannot be reported as a clean one, and whether a degraded run should converge at all.
3. Decide whether the derived key should replace `DEFAULT_FALSIFIER_STRENGTH` entirely or sit beside it, and what happens on the very first run when no seat has any measurement.
4. Say what a researcher adding or removing a model must do, given that a design brief for the user interface already exists at `experimental_notes/CDSFL_UX_Vision_Sketch_2026-03-28.md`.
5. Kimi K3 is wired against the Moonshot endpoint and is expensive; the founder wants it held in reserve for the hardest work. Say how "hardest" is decided without a human classifying every finding by hand.

Write and EXECUTE a falsifier for each fix you propose, and deliver each fix as a file in your sandbox repository tree at its real path. A fix you have not run is a hypothesis.

## Output

Return these fields by name.

- VERDICT on the design as a whole: sound, sound with repairs, or unsound.
- FINDINGS, each with the file and the line, and each marked OBSERVED with the command that shows it, or HYPOTHESISED with what would settle it.
- FIXES, one per finding, each delivered as a file and each with the falsifier you executed and its output.
- YOUR STRONGEST DISAGREEMENT with this brief's own framing. The brief has been wrong twice today already: it asserted a contradiction between 2 of the founder's rulings that does not exist, and an earlier version reported 49 configuration files where there are 47. Assume it is still wrong somewhere and say where.
- WHAT WOULD REFUTE YOUR OWN POSITION, stated as a measurement someone else could run.
- CONFIDENCE, with the evidence that sets it.

## Termination

Stop when every requirement above has either a fix with an executed falsifier or an explicit statement that it cannot be met and why. Stop early if 2 consecutive passes over your own answer produce no new finding above the threshold of real-world consequence. Do not pad: a short answer with executed evidence beats a long one without.

<!-- figure: spurious_convergence_6_to_4 | bench/a_shrinking_roster_converges_sooner_2026-10-07.py | 8.49986 -->
<!-- figure: dropout_probability_1pc | bench/a_shrinking_roster_converges_sooner_2026-10-07.py | 0.452843 -->
<!-- figure: newcomer_wilson_lower_bound | bench/allocation_by_measured_capability_2026-10-07.py | 0.206549 -->
<!-- figure: veteran_wilson_lower_bound | bench/allocation_by_measured_capability_2026-10-07.py | 0.756616 -->
<!-- figure: expected_calls_money_order | bench/allocation_by_measured_capability_2026-10-07.py | 4.80396 -->
<!-- figure: expected_calls_capability_order | bench/allocation_by_measured_capability_2026-10-07.py | 1.776318 -->
<!-- figure: money_fold_worse | bench/allocation_by_measured_capability_2026-10-07.py | 1.0485 -->
<!-- figure: spurious_convergence_6_to_2 | bench/a_shrinking_roster_converges_sooner_2026-10-07.py | 72.247616 -->
<!-- figure: dropout_probability_2pc | bench/a_shrinking_roster_converges_sooner_2026-10-07.py | 0.702447 -->
<!-- figure: ratio_at_correlation_0p1 | bench/the_spurious_convergence_ratio_depends_on_correlation_2026-10-07.py | 3.8236 -->
<!-- figure: ratio_at_correlation_0p3 | bench/the_spurious_convergence_ratio_depends_on_correlation_2026-10-07.py | 1.9200 -->
<!-- figure: ratio_at_correlation_0p5 | bench/the_spurious_convergence_ratio_depends_on_correlation_2026-10-07.py | 1.4043 -->
<!-- figure: ratio_collapse_across_correlation | bench/the_spurious_convergence_ratio_depends_on_correlation_2026-10-07.py | 7.7915 -->


<!-- verbatim-end -->

## Seat: cc2

Route `claude_cli`, 70 recorded tool call(s).

<!-- verbatim-begin: cc2 (panel dynamic_roster_and_derived_ladder_2026-10-07) -->

All five falsifiers pass; 435 convergence/routing tests pass.

---

# VERDICT

**Sound with repairs.** Parts A, B and C are correct: I brute-forced the exchange rule against all permutations of 3000 random instances (0 misses), z3 returns `unsat` on its counterexample search, and the Wilson figures reproduce exactly (0.206549, 0.756616, 12 attempts). The two unsolved requirements are repairable without new rules, and the hazard is real but ~29× smaller than the brief states.

---

# FINDINGS

**F1 — No mid-run re-probe; a transient fault is benching by another name. OBSERVED.**
`bench/seat_aliveness_2026-10-06.py:refusal_for` (~line 108); call site `bench/reference_runner_v3.py:15109`, invoked once at `15231`.
`python3 bench/falsify_no_midrun_readmission_2026-10-07.py` → four defects fire: `refusal_for` refuses the run for 1 of 2 dead seats; its codomain is `{None, str}` so no third state exists; `_refuse_if_a_route_is_dead` appears twice (definition + one call site); and there is **no seat readmission path** — 0 `readmit`/`half_open` tokens. (My first check passed for the wrong reason: `_reprobed` at `18407` *does* exist but counts fix-efficacy probes on **findings**. I tightened the check rather than keep a green that measured nothing.)

**F2 — The convergence gate has no roster argument. OBSERVED.**
`bench/reference_runner_v3.py:8070`. `python3 bench/falsify_roster_aware_quiescence_2026-10-07.py` → params are `['round_idx','gamma','novel_critical_history','cfg','unresolved_critical','contested','rho_churn','irreducible_queue','gamma_critical','total_findings']` — no roster term. The real gate returns `True` with an identical reason string for a 6-seat and a 2-seat quiet window, because **the inputs are literally indistinguishable**.

**F3 — No capability estimator exists. OBSERVED.**
`bench/routing.py:118`. `rank_falsifier_writers` returns the hand-written tuple verbatim; its params `['labels','strength_order','exclude']` admit no measurement; `routing.py` contains no `wilson`/`successes`/`lower_bound`. A seat with 0 successes in 40 admissible attempts would still be returned at rung 1 — the ranker cannot express the fact.

**F4 — Cost is money-only. OBSERVED.** Money order costs 4.803960 expected dispatches against 1.776318 — the researcher waits **2.7044×** longer to save spend by 1.0485.

**F5 — The roster is declared twice and the mismatch only logs. OBSERVED.**
`bench/reference_runner_v3.py` ~15180–15200. 47 configs; **0 declare Fable** (an addition nothing reaches — rung 6 of a 6-rung ladder); 2 of 47 declare a roster differing from the hardcoded counted default `['CC2','ChatGPT','Codex','DeepSeek','Gemini']`; and on `PANEL MISMATCH` the runner calls `_log` and proceeds with no raise and no refusal dict.

**F6 — The gate's absolute false-quiet rate at *full* roster is 0.1159, which the brief never mentions. OBSERVED.** At archive-measured q and rho, `P(3 consecutive quiet rounds | 6 seats) = 0.1159`. My fix holds that baseline; it does **not** improve it. Lowering it needs a higher global K or more seats — the founder's call, not mine. Bounded claim: this is the marginal probability of the quiet-window condition alone; the gate is a conjunction, so joint false convergence is *at most* this.

---

# FIXES

Each delivered at its real path, each with an executed falsifier (outputs above).

**1. `bench/seat_circuit_breaker_2026-10-07.py`** — the third state is **the seat's breaker is OPEN**. This is not a coined label: `CLOSED / OPEN / HALF_OPEN` is the standard circuit-breaker pattern (Nygard), *and* the term is already this project's vocabulary — `CDSFL_UX_Vision_Sketch_2026-03-28.md` specifies a **"Circuit Breaker Display"** and already offers *"proceed without the failed model"*. Benching is distinguished **structurally, not by documentation**: `__post_init__` raises on any non-CLOSED state without a `reprobe_at`, `open_breaker` has no parameter that can suppress the deadline, and backoff is capped at `MAX_BACKOFF_S` — an unbounded re-probe interval *is* benching and the module cannot express it. Falsified: a transient fault keeps 5 of 6 seats running, the dead seat is readmitted mid-run, and a deadline-free OPEN state is not constructible.

**2. `bench/roster_aware_quiescence_2026-10-07.py` + 6 wiring sites in `reference_runner_v3.py`** — derived: `P_spurious(n,K) = Q(n)^K`, so holding it at the declared value gives `K(n) = ⌈K₀·log Q(n₀)/log Q(n)⌉`. I evaluate `Q(n) = B(a,b+n)/B(a,b)` in **closed form**, an independent derivation of the committed artefact's `mp.quad`, agreeing to <1e-9. Wolfram Language (local Wolfram Engine) independently returns 1.9200365774162 for the rho=0.3 ratio and 8.49985975231408 for independence. Result: K goes 3→4→4→5→6→9 as the roster falls 6→1, holding P at or below 0.1159 at every size, **costing a healthy run nothing** (full roster keeps K=3).

**Should a degraded run converge?** Yes. Requirement 8 forbids blocking, and refusing would hand the researcher a run that can never finish. It converges against the raised K and is **labelled** `CONVERGED_DEGRADED_ROSTER`. A 0-live-seat round does not converge — no evidence at all.

**Composability, demonstrated not asserted:** record-only still stops too soon (P stays 2.4796× target); K-only holds P but reports identically to a full-roster run. Each cures a failure the other provably cannot.

**3. `bench/capability_ledger_2026-10-07.py`** — requirement 6 is an **estimator** property, with two guards. (a) Capability is a Wilson *lower bound*, so 1/1 cannot promote. (b) **An inadmissible CONFIRMED is not a success** — the Exp 55 inversion recorded at `routing.py:44` (Gemini 2/2 CONFIRMED with detached falsifiers) buys **0.0**, counted as attempts with zero successes. Without (b) the ledger would rank seats by willingness to ignore the evidence.

Per attempt the estimator records: `seat, finding_id, round_idx, task_class, rung_depth, verdict` (from the runner's re-execution, never model prose), `admissible, wall_clock_s, money`. **First attempt ever:** 0 attempts → lower bound exactly 0.0 → sorts last, climbs on evidence, no human places anything.

**Replace `DEFAULT_FALSIFIER_STRENGTH`? No — keep it beside, as the tie-break.** Measured: on run 1 every lower bound is 0.0, so the derived key is a total tie; 12 shuffled inputs gave **12 distinct orders** without the tuple and **1** with it. The tuple is the only ordering information that exists at that moment.

**4. Latency — is a scalar enough?** `cost = money + λ·seconds` reorders the same key with no new rule, crossing to capability-first at λ=2 (reproduced). But **a scalar is not sufficient in general**, and I measured rather than judged it: I found an instance where the budget-constrained optimum is not λ-optimal for **any** λ across 4001 values. So the scalar is right for a *trade-off*; a **hard-capped** resource (the Max subscription in requirement 8) needs a constraint, not a weight.

**5. Kimi K3 — "hardest" needs no human classifier, and no new mechanism.** It is an **emergent property of Part B**: an expensive seat has large `c`, so the derived key places it late by itself, and `probability_reached` shows it dispatched on 3.61% of findings — exactly those where all 6 seats with a better measured p/c ratio already failed. That *is* "hardest", measured per finding as `Attempt.rung_depth`.

**6. `bench/roster_registry_2026-10-07.py`** — adding a model is **exactly one edit**: `models` in the config. Verified: `rank_falsifier_writers(['Codex','BrandNewModel','DeepSeek'])` → `['Codex','DeepSeek','BrandNewModel']`, so an unknown model is already tried, last; no ladder edit, no estimator edit. `validate_roster` turns the two-roster mismatch from a log line into a refusal. Removal is a **policy act** requiring a recorded reason, and is explicitly forbidden as a response to a seat not answering — that is the breaker's job.

**Wiring (the additive standard).** This project has confirmed 11 defects that were additions nothing reached, so I wired fix 2 into the live runner rather than leaving it offered: `live_roster_history` initialised at `15649`, appended from `responses` beside `novel_critical_history.append` at `16565`, passed at the gate call site `17602`. `live_by_round=None` reproduces today's behaviour exactly — **119 existing routing/gate tests and 435 convergence tests pass**. A broken estimator prints `ROSTER-AWARE WINDOW UNAVAILABLE` rather than silently reverting to the blind window. The 10 failures in the wider sweep are **pre-existing**: they reproduce on the pristine backup and those files don't import the runner.

Fixes 1, 3 and 6 remain **unwired** — honest statement, not an omission: wiring the breaker means changing what `_refuse_if_a_route_is_dead` returns, which changes what every live experiment does on a dead seat. That is the founder's ruling to make, not mine.

---

# YOUR STRONGEST DISAGREEMENT WITH THIS BRIEF'S FRAMING

**The correlation has been measured, it is committed and runnable, and both parameters behind the headline hazard figure are wrong.**

The brief says *"The correlation is measurable and nobody has measured it. Treat its absence as one of the findings, and say how you would measure it from the archive."* But `bench/the_intra_round_correlation_measured_2026-10-07.py` is committed and runs: 64 reports, 395 usable rounds, 1968 seat-rounds, rho = **0.405989**, bootstrap [0.332313, 0.476821], with two estimators agreeing to 0.0457. There is nothing to treat as absent and nothing for me to propose — it is done.

Worse, the brief's **q is rejected by its own archive**. It assumes q = 0.3; the measured q is **0.233740**, Wilson95 [0.215572, 0.252945]. An exact binomial test of H₀: q = 0.30 gives **p = 5.6 × 10⁻¹¹**. The brief's headline figure is therefore non-conservative twice over — wrong q *and* rho = 0:

| | brief | measured (q=0.2337, rho=0.4060) | overstatement |
|---|---|---|---|
| 6→4 factor | 8.49986 | **1.4291** | 5.9× |
| 6→2 factor | 72.247616 | **2.4796** | **29.1×** |

The brief says the magnitude *"moves by a factor of 7.7915 across a plausible range, on a parameter this project has never measured."* Two errors in one sentence: the parameter has been measured, and 7.7915 is the span from rho=0 to rho=**0.8**, not across the 0.1–0.5 range the brief calls plausible.

**But the load-bearing step is correct, and I am not weakening it.** The brief asks me to say if the reasoning that the repair's necessity is magnitude-independent is wrong. It is not wrong. z3 returns `unsat` on separating 0 from a healthy panel from 0 from a depleted one — they are the same integer at every correlation — and `unsat` on a round being both intact and degraded once the roster is recorded. Necessity follows from indistinguishability, not from magnitude. The brief is right that the factor sets urgency; it is wrong about the factor, by 29×.

Two smaller framing objections. First, the brief frames the hazard entirely as a *ratio*, which hides that the absolute full-roster rate is already 0.1159 (F6) — the more alarming number, and one no roster-aware fix addresses. Second, "remove the cap" plus requirement 4 ("never hand a model work it cannot do") reads as a tension the brief doesn't name; it dissolves because ordering, not exclusion, honours requirement 4 in expectation — a weak seat is reached only when everything better has failed, which is the correct time to ask it.

---

# WHAT WOULD REFUTE MY OWN POSITION

1. **My rho is contaminated by pooling.** I take rho = 0.406 from 64 heterogeneous reports. Re-run `the_intra_round_correlation_measured_2026-10-07.py` stratified by domain, roster size and era; if per-stratum rho falls below ~0.1, my `K(n)` under-corrects and the brief's urgency is closer to right than mine. The per-report loop at line 129 already discards reports with <3 rounds — that filter's effect on rho is unmeasured, including by me.
2. **q is not stationary across rounds.** I treat q as constant; it almost certainly decays as a target is exhausted. Fit q by round index and recompute `quiet_rounds_required` with a round-varying q. If late-round q is much lower, quiet rounds are mostly *genuine* and my raised K burns the researcher's time for nothing — which would make my fix a requirement-7 violation.
3. **The beta-binomial is the wrong dependence model.** Fit a logistic-normal or a seat-pair-specific copula to the same 8088 within-round pairs and compare by AIC. A better-fitting model with different tail behaviour changes every K I derived.
4. **The scalar-vs-vector counterexample may be practically empty.** Mine is synthetic. Measure real per-seat money and wall-clock from the archive, and if no hard cap ever binds at realistic values, the vector is an addition nothing reaches — my own worst failure class.
5. **`len(responses)` may not be the live roster.** I wired the gate to `len(responses)`. If `responses` can hold an entry for a seat that answered with an error string, my roster count is inflated and the degradation is undercounted. Settle it by comparing `len(responses)` against `models_responded` per round across the archive.

---

# CONFIDENCE

**High on the findings, high on fixes 2–6, moderate on fix 1, moderate-to-low on the calibration.**

High on the findings because each is an executed observation against the real modules, not a reading: the gate's parameter list, the ranker's return value, 47 configs with 0 Fable, and the pre-existing-failure check that proves my patch caused none of the 10 unrelated failures.

High on fix 2's mathematics: the exchange rule is brute-force-optimal over all permutations of 3000 instances with z3 `unsat` on the counterexample search, my closed form agrees with the committed `mp.quad` to <1e-9, and Wolfram Language independently confirms both ratios. High on fixes 3–6 because the Wilson figures reproduce the committed artefact exactly and the scalar-insufficiency result is a constructed counterexample rather than an argument.

Moderate on fix 1 because it is unwired — a module with a passing falsifier is not yet a working system, and this project's record says that distinction matters 11 times over.

Moderate-to-low on the calibration, and this bounds my own repair: K(n) depends on rho = 0.406 and q = 0.2337 pooled across 64 heterogeneous reports. I have shown the brief's parameters are wrong; I have **not** shown mine are right for any particular future run. Refutations 1 and 2 are the measurements that would settle it, and neither has been run — by the brief, or by me.

<!-- verbatim-end -->

## Seat: fable

Route `claude_cli`, 62 recorded tool call(s).

<!-- verbatim-begin: fable (panel dynamic_roster_and_derived_ladder_2026-10-07) -->

All six falsifiers pass against the finished tree. Final answer.

---

## VERDICT

**Sound with repairs.** Parts A, B and C are each independently verified: I re-derived the exchange rule (adjacent-swap algebra via SymPy gives `a before b ⟺ p_a·c_b ≥ p_b·c_a`), the Wilson figures (0.206549, 0.756616, 12 consecutive successes from `n/(n+z²) > lo(60,70)`), the dispatch expectations (4.80396 / 1.776318), the λ=2 crossover (`0.8(1+λ) ≥ 0.02(100+λ) ⟺ λ ≥ 1.538`), the quiet-window folds ((10/7)⁶ = 8.49986; 72.2476), and the dropout probabilities (1−0.99⁶⁰ = 0.452843; 1−0.98⁶⁰ = 0.702447). Wolfram Language (local Wolfram Engine) independently returned 8.49985975231409 and 0.7566158. The repairs below are delivered, wired, and falsified.

## FINDINGS

1. **The gate is one-sided, not two-sided, exactly where the hazard lives.** `bench/reference_runner_v3.py:9207–9215`: when `cum_critical < gamma_crit_min_cumulative` (8), γ is "reported-not-gated" and closure rests on the zero-critical window **alone** — the condition roster shrinkage attacks. OBSERVED: `sed -n '9207,9215p' bench/reference_runner_v3.py`.
2. **The quiet window ignores the roster.** `bench/reference_runner_v3.py:9201` counts rounds, not seat-rounds; `models_responded` is recorded (line 17818) but never consulted by the gate; `active_models` appears once (line 15662, the resume guard only). OBSERVED: `grep -n active_models bench/reference_runner_v3.py`.
3. **No capability estimator exists** — nothing records attempts, nothing computes a bound, and `DEFAULT_FALSIFIER_STRENGTH` (routing.py:85) is the only ordering. OBSERVED: no module matched `wilson|capability.*estimat` outside the 2026-10-07 artefacts.
4. **No third seat state exists.** The probe runs once, pre-round-1 (`_refuse_if_a_route_is_dead`, line 15231; `probe_models` has exactly 1 call site); `refusal_for` (seat_aliveness:108–125) conflates transient outage with benching, exactly as requirement 9 says. OBSERVED.
5. **Requirement 2 failed in practice.** `max_rungs=0` meant exhaust but defaulted to 2 (routing.py:176, 295; `routing_max_rungs: int = 2` at runner:1475) and **0 of 47 configs pinned it** — the founder's ruling was an entry point nothing reached, the project's confirmed 11-fold defect class. OBSERVED: the first artefact prints `configs_pinning_the_cap: 0`, `rungs_never_tried_under_the_cap: {5: 3}`.
6. **ρ was unmeasured — now it isn't.** Over 516 archived rounds (75 reports): **ICC(1) = 0.4903, pairwise φ = 0.5095** (live-only, excluding sim/harvest: 0.4581 / 0.4821), and the per-seat-per-round critical rate is **0.1994, not the assumed 0.3**. OBSERVED: `python3 scripts/measure_intra_round_correlation.py`. The estimator recovers known ρ ∈ {0, 0.3, 0.5} within 0.003 on synthetic exchangeable data.

## FIXES (each file delivered, each falsifier executed, all PASS)

| Fix | File | Falsifier (executed, output above) |
|---|---|---|
| 1. Estimator (req 6, req 7, Q3, Q5) | `bench/capability_estimator.py` | `bench/test_capability_estimator_2026-10-08.py` — detached/unchecked CONFIRMED never counts; 1/1 doesn't pass 60/70; 12 needed; λ=2 restores capability-first; cold start falls back to the measured Exp-42 tuple; ladder bidirectional |
| 2. Hazard | `bench/degradation_aware_convergence.py` | `bench/test_degradation_aware_convergence_2026-10-08.py` — seat-round window holds P_spurious ≤ design point at every roster size 1–6 (exact rationals); record separates intact/degraded for every count 0–10; full-roster behaviour byte-identical |
| 3. Third state (Q1, reqs 8–9) | `bench/seat_circuit_breaker.py` | `bench/test_seat_circuit_breaker_2026-10-08.py` — no terminal state, no removal API, round proceeds, re-probed every boundary, auto-readmitted, never touches capability |
| 4. ρ measurement | `scripts/measure_intra_round_correlation.py` | `scripts/test_measure_intra_round_correlation_2026-10-08.py` — known-ρ recovery |
| 5. Add/remove workflow (Q4) | `docs/adding_or_removing_a_model_2026-10-08.md` | `bench/test_add_remove_model_workflow_2026-10-08.py` — tuple is a prefix not an allowlist; moonshot probeable; UX sketch quote verified |
| 6. No-cap default (req 2) | edits to `bench/routing.py`, `bench/reference_runner_v3.py` (+ the 3 superseded 2026-09-24 assertions updated to the ruling) | `bench/test_no_cap_default_2026-10-08.py` — default tries all 6 rungs + self-rung; opt-in cap still honoured. Targeted suites: 7/7 and 86/86 pass |

**Answers the brief demanded.** *Unsolved 1*: the latency-weighted scalar is the right repair and a **single scalar suffices** — z3 proves the exchange rule survives any fixed non-negative linear combination, a vector adds a dimension the one-scalar-per-seat key cannot consume, and the latency term additionally cures the free-seat degeneracy (money-only is provably vacuous there: `distinct_expected_spends: 1`). *Unsolved 2*: per attempt record seat, finding, the **re-verifier's** verdict, provenance-check result (None ⇒ not a success — the Exp 55 inversion), latency, money, timestamp; a new model's first attempt starts at bound 0.0, last place, reached under exhaustion. *Q2*: a degraded run **should converge** (req 8) but never silently — on proportionally more quiet seat-rounds (`ceil(n₀K₀/n_live)`), with per-round `n_live` in the record and a `_DEGRADED_ROSTER` verdict suffix. *Q3*: derived key orders; the tuple stays as the cold-start tie-break — it is itself a committed measurement, and on run 1 the key demonstrably does not dominate it. *Q5*: "hardest" = survived every seat with a better measured p/c; Kimi's depth is arithmetic (P(reach) = Π(1−pᵢ) = 0.0287 in the falsified example) — and when the rest of the roster measures near-useless, the key correctly promotes Kimi rather than waste the researcher's wait, which is requirement 3, not a bug.

## STRONGEST DISAGREEMENT

The brief calls the gate "two-sided." It is **one-sided in precisely the endgame regime**: the sparsity fallback (runner:9207) gates on the zero-critical window alone whenever cumulative criticals < 8 — so the brief *understates* its own hazard structurally while *overstating* it numerically: the 7.7915 "collapse" is a ratio of two Monte-Carlo point estimates (8.5616/1.0988) spanning ρ ∈ [0, 0.8], though the brief presents exact values only on [0.1, 0.5]; the exact collapse over that stated range is 8.49986/1.4043 = **6.053**. And with ρ now measured at ≈ 0.46–0.51 and q at 0.1994 (not 0.3), the operative 6→4 fold sits near **1.4** — the headline 8.49986 overstates it by ~6×. The load-bearing step survives all of this, as the brief predicted: recording the roster is necessary at any ρ (z3 unsat), and my falsifier re-proves separability by exhaustion.

## WHAT WOULD REFUTE MY OWN POSITION

(1) Re-run `scripts/measure_intra_round_correlation.py` with novelty-deduplicated criticals (registry-settled, not raw per-round severity ≥ 0.7): if ICC falls below ~0.1, the urgency I downgraded returns toward 8.5-fold. (2) A committed measurement on ≥ 2 live runs showing the seat-round window converges materially later than K rounds with **no** spurious convergence prevented would show my rescaling over-demands and recording alone was the simplest sufficient fix. (3) A run where `resolve_via_routing` at the new exhaust default produces a measured spend pathology would reinstate a positive default cap.

## CONFIDENCE

**High** on findings 1–6 (each OBSERVED by an executed command) and on the mathematics (every figure derived independently; two checked by Wolfram Language as second falsifier). **Moderate** on three policy choices that are the founder's to ratify: the degraded-convergence policy (converge, declared, on seat-round-conserved evidence), keeping the tuple as cold-start tie-break, and flipping the cap default — the last changes what 23 routing-enabled configs dispatch, which is exactly why the ruling, not my judgement, is its justification. The ρ estimate carries a known caveat: it counts raw critical-severity findings per seat-round, not registry-settled novel criticals, so it bounds rather than pins the gate-relevant correlation — the refutation measurement above is the check.

<!-- verbatim-end -->

## Where the raw record lives

`bench/logs/dynamic_roster_and_derived_ladder_2026-10-07/` holds the brief, every seat reply, the tool logs and `seat_proposals.diff`. That directory is excluded by `.gitignore:41`, so a byte-identical copy is committed under `experimental_notes/evidence/`, verified by sha256 and checked on every suite run by `bench/tests/test_panel_records_are_preserved_2026-09-11.py`.


Written under CDSFL note standard v1.7 (26 August 2026).
