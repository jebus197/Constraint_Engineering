# Capability Ladder As A Measured Statistic, blind round, second seat

Record written 2026-10-06T07:04:35+01:00.

**This is the seats' own output, reproduced in full.** The Personalisation directive requires external review output preserved *"in full and in unfiltered format"* and says *"Never summarise in place of the full output"*. Any summary elsewhere is downstream of this file, not a substitute for it.

WHAT WAS REVIEWED. The same 6 design questions put to the fable seat on a byte-identical brief: what the capability routing ladder should rank on now that the founder has ruled it must become a measured statistic, how to handle the selection effect created by routing firing only on unresolved criticals, what bounds spend once the rung cap is removed, whether routing should be resource-aware, who performs reproducibility checking, and what the brief had missed.

WHY A SEPARATE BLIND ROUND. Star topology, on the founder's standing ruling: a blind round for each seat, then a joint round once every blind round is in. Blindness was verified by measurement on the sandbox this seat actually ran in, not inferred from the configuration flag. 0 files carried any of 4 distinctive phrases from the other seat's reply, and the other round's directory was purged from this seat's copy of the evidence tree while the live tree carried it in 4 files. The check was repeated after a re-dispatch, because a dispatcher retry builds a fresh sandbox from the live tree at retry time and by then the other seat's whole reply had been mirrored into that tree. 0 paid dispatches.

THIS ROUND TOOK 3 DISPATCHES AND THE FIRST 2 PRODUCED NOTHING. Both ended as timeouts at the 1800 second ceiling during a period of intermittent network loss, the second having made 88 tool calls without reaching an answer. The successful dispatch made 49 tool calls and answered in 1020 seconds. The per-call rate was stable throughout, at 20.455 and 20.816 seconds, so the seat was never slowed; the call count nearly doubled because the calls themselves were failing and being retried. That is a diagnostic signature worth keeping: a seat on a degraded route keeps working at normal speed and never converges.

THE CENTRAL FINDING, AND IT IS BLOCKING. The seat predicted that resolving criticals by exhausting the ladder would RAISE the critical gamma value, measured it against the archive, and was refuted by its own measurement. Over 14 archived runs of at least 3 rounds, flipping every unresolved critical to confirmed moves the critical gamma DOWN in 9 runs, up in 3 and leaves it unchanged in 2, and 2 of the 14 cross the 0.30 convergence arm DOWNWARD: run exp40_gate from 0.3018 to 0.2328, and commissioning_arm1_panel from 0.3236 to 0.1883. That is 14.29% of runs, Wilson 95% interval 4.0094% to 39.9414%, with statsmodels, an independent closed form and Wolfram Language all agreeing to 7 significant figures.

The reason the curve steepens is visible in the data the script prints: the flipped criticals carry a LATER mean round than the registry mean, 18.00 against 13.31 in the first run and 6.50 against 3.19 in the second. An unresolved critical is one the ladder has not yet reached, which places it late, and adding mass to the late end of a cumulative curve steepens it, raising beta and lowering gamma.

This matters because the founder's ruling to remove the rung cap, and the routing module's own comment, both frame exhaustion as a question of spend. It is not only that. Exhaustion moves one arm of the two-sided convergence gate in the direction that makes convergence harder, so a run that converges today can stop converging. The rung budget is therefore an undeclared input to the convergence gate.

VERIFIED INDEPENDENTLY RATHER THAN ACCEPTED. The seat's script was re-run against the live archive by the operator and reproduced every figure exactly: 14 runs measured, 9 down, 3 up, 2 unchanged, 2 crossings downward and 0 upward. A first attempt to run it reported 0 runs measured, which was an operator path error and not a fault of the seat's; the correction is recorded because the figures would otherwise read as unreproduced.

ONE DEFECT WAS FOUND IN THE SEAT'S OWN SCRIPT during that verification, and it is the shape this project documents repeatedly: at 0 runs measured the script printed its entire conclusion narrative unchanged and exited 0. It cannot distinguish having measured nothing from having measured and found nothing.

WHAT WAS DONE WITH THE FINDINGS. Nothing the seat delivered was merged; fixes are suggested to the human in the loop and never applied automatically, and the seat's files are preserved under the seat evidence directory. The gamma coupling is raised to the founder as the first item requiring his ruling, because exhaustion was enabled in the simulated launcher earlier the same night on his instruction. The seat's own recommendation is recording-only: log the critical gamma a second way so the coupling is visible per round while the gate continues to read exactly what it reads today.

WHERE THE 2 SEATS AGREED WITHOUT CONTACT. Both independently rejected the brief's use of the heterogeneity figure, chi-square 280.0138 on 4 degrees of freedom, p = 2.213221e-59, on the ground that it measures per-round finding rate rather than falsification capability. Agreement reached blind is information; agreement reached after contact would not have been.

WHERE THEY DIFFERED. The fable seat proposed a verification-probability statistic credited to the falsifier's author with a minimum sample before it may rank. This seat derived that no minimum sample is needed, because under exhaustion every rung is tried regardless of its estimate, so a poor estimate can only misorder cost and never exclude a rung. Both retain the frozen vendor ordering as a tie-break rather than deleting it, and this seat states plainly that this is weaker than the founder's ruling and says so rather than pretending otherwise.

## Seats and cost

1 seat(s): `cc2`. **0 paid dispatches**, enforced by `PANEL_ONLY=cc2,fable`.

## The brief, as dispatched

<!-- verbatim-begin: the brief as dispatched -->

# Design brief — what should decide which model is asked to do the hardest work?

This is a BLIND round. Answer independently. A joint round follows once every blind
reply is in. Your task is to find what is WRONG and to propose what should be built,
not to confirm what exists.

## The situation, measured

`bench/routing.py` routes an unresolved critical finding to progressively stronger
models. It ranks on `DEFAULT_FALSIFIER_STRENGTH = ("Codex","CC2","ChatGPT","Gemini",
"DeepSeek")` — a frozen 5-tuple of VENDOR NAMES derived from Exp 42 in June 2026 and
never re-derived. Its own docstring says it orders "by capability fingerprint"; the
word `fingerprint` appears exactly ONCE in that file, in that docstring, and the code
reads no fingerprint.

Separately `_update_observed_fingerprint` writes a live per-model profile every round,
consumed by `burst_planner.py`. The glossary defines that profile as (D, v-bar, A, C)
including a VERIFICATION score. The 15 fields actually written contain **no
verification score and no coverage dimension** — only context capacity and raw
productivity.

Measured facts you may rely on (verify any you doubt; producers named):
- Real panel finding rates differ: chi-square 280.0138, df 4, p = 2.213221e-59.
  Simulated panel does not: chi-square 3.0084, df 5, p = 0.6987.
  `scripts/the_sim_panel_is_not_heterogeneous_2026-10-05.py`
- `routing_max_rungs` defaults to 2; 0 of 288 config files pin it. `resolve_via_routing`
  STOPS at the first CONFIRMED, so rung 3 runs only when rungs 1 and 2 both failed.
- `competence_provenance.py` credits a confirmation to the model that REPORTED the
  finding, not the one that WROTE the falsifier: 1370 of 16500 archived entries carry
  `resolved_by_routing`, 8.3% credited to the model that failed to write a working test.
- On Exp 55 one model scored 2 of 2 CONFIRMED with falsifiers that opened nothing and
  restated the document from memory; another scored 0 of 2 with genuine readers that
  ERRORed. A naive confirm-rate ranking inverts the correct order.

## The founder's ruling, verbatim

*"The routing ladder should be a measured statistic, not simply a list of named vendors
based on what you, or I may have read about them on the internet. In that sense, our
runners shouldn't care if a particularly named vendor model is available or not. It
should just shunt data around the system based on the performance of all models
(regardless if they are simulated or real) that may be available to the system."*

*"The system shouldn't care at all what a model is called, only what it can be
statistically demonstrated to have done, as per its capability fingerprint. So it
shouldn't matter if all the models are different, or all the models are the same, or if
they are all models from a single vendor, or even a single model operating on its own
(in which case the ladder would just route the issue back to itself and would have
another go at resolving it by using the rest of the machinery of the harness.)"*

*"I don't think there should be a cap at all. If it's a measured statistic, along with
capability fingerprinting then the problem should run until it is either resolved, or
the ladder is exhausted. (No more models to try.)"*

On resources: *"cost in terms of tokens required and tokens that will be used over any
given problem set. That then becomes an issue of load balancing... Problems then get
routed to models with enough capability, AND sufficient resources given the opening
problem set, rather than risking exhausting models due to poor resource/problem
allocation."*

On reproducibility: the project's goal is a STEM calculator — problem in, definitive
repeatable answer out. He asks whether reproducibility should be a separate step
performed by the models, by the human, or both.

## Answer these, each explicitly

1. **What should the ladder rank on?** Name the quantity, its estimator, its minimum
   sample, and what happens to a model with no history. It must be vendor-agnostic and
   must degrade sensibly to a 1-model panel.
2. **The selection effect.** The ladder sends HARD findings to strong models, so their
   success rate is depressed by being trusted. Earlier proposals: measure first attempts
   only (rejected — populations differ at p = 2.2e-59); randomise an audit fraction
   (right identification, but routing fires rarely — is it deployable?); keep the frozen
   order as decider with the rate only as a drift alarm. Which, or what else?
3. **Removing the rung cap.** The founder wants exhaustion, not a fixed budget. What
   stops that becoming unbounded spend, and what is the correct stopping rule?
4. **Resource-aware routing.** Should token budget enter the routing decision alongside
   capability? If so, how, without making a cheap model the default answer?
5. **Reproducibility.** Should it be a separate verification step? Whose?
6. **What have we missed?** Anything in this design that cannot work, or that conflicts
   with the project's additive standard or its no-model-voting rule.

## Deliver your proposal as a FILE

Write any design or repair INTO the sandbox repository tree at its real path, plus any
script you used to check a claim, so it can be re-run. Prose left in the reply is
destroyed at teardown.

## State what would REFUTE you

For each position, name the measurement, file or command whose output would change
your answer. A position with no refutation condition is an opinion.

## Termination

Stop when further work produces no new above-threshold findings — a finding is above
threshold if missing it could cause a real-world failure or a wrong experimental
conclusion. An early stop with a stated reason beats padding.

Include a section headed `## Disagreement` with a real body.

## The mathematical instruments this question touches, and what they should tell you

**gamma** is the decay curve and is LOAD-BEARING — an active convergence condition, not
a report. The two-sided gate requires BOTH `gamma_critical >= 0.30` AND K consecutive
zero-new-critical rounds. A routing change that alters which findings get resolved
alters the critical series, so it moves gamma. Say what your design does to gamma.

**severity** decides in 22 distinct functions across 33 live sites and weights L_n. The
A4 fail-safe now exempts a sub-critical finding ONLY when `severity_is_proven` holds —
the model reproduced its own R_k from its own stated inputs. Any capability statistic
you propose must say whether it is gated the same way, because an UNPROVEN number
opening a gate is the model vote this project forbids.

**Wilson** intervals are required on every proportion you report, and every computed
claim must be cross-verified with at least 2 tools. A capability estimator built on
small per-model samples lives or dies on its interval width — state it.

**rho** is discovery efficiency and **S_k** classifies a FIX, not a claim. If your
estimator reuses either, say which and why it is the right construct.

## Output shape — return exactly these fields

- `## Position` — one paragraph per numbered question, 1 through 6, each answered
  explicitly and separately.
- `## The quantity` — the estimator in full: formula, inputs, minimum sample, cold-start
  behaviour, and its behaviour on a 1-model panel.
- `## What it does to gamma` — the effect on the critical series and the two-sided gate.
- `## Measurements` — every figure with its Wilson interval and the 2 tools that agree.
- `## Delivered files` — paths written into the sandbox tree.
- `## What would refute me` — per position.
- `## Disagreement` — a real body; "none" only if you genuinely have none, said so.


<!-- verbatim-end -->

## Seat: cc2

Route `claude_cli`, 49 recorded tool call(s).

<!-- verbatim-begin: cc2 (panel capability_ladder_design_blind_round2_2026-10-06) -->

All four scripts execute and answer `--help`. Written to the sandbox tree.

## Position

**1 — What the ladder should rank on.** The probability that a falsifier written by model *m* for a finding at ladder depth *d* is re-executed by `reverify_falsifier` with verdict `CONFIRMED`, counted **per attempt** (not per entry), restricted to falsifiers that actually read the target (`competence_provenance.falsifier_style == "reads"`), and **stratified on ladder depth**. It has no glossary name and I have not coined one — it is described in full, and it is neither `rho` (a round's novel/raw yield, not a writer's success) nor `S_k` (which classifies a fix that does not exist at routing time). Estimator, minimum sample, cold start and the 1-model case are in `## The quantity`. The prior question is settled first by derivation: `resolve_via_routing` stops at the first `CONFIRMED`, so with the cap removed `P(resolve) = 1 − ∏(1−p_i)` is **symmetric in the rungs** — order cannot change *which* findings resolve, only what they cost. The founder's two rulings are coupled: removing the cap is what makes an imperfect measurement safe.

**2 — The selection effect.** Condition on ladder depth; neither of the three earlier proposals. The selection is *fully observed* — a finding reaches a model at depth *d* because *d* rungs already failed, and `routing_history.rungs_tried` records it. Selection on observables means conditioning removes the bias, so randomisation buys nothing. The audit-fraction proposal also isn't deployable (routing fires on unresolved criticals only; single-digit *n* per model per run). Keeping the frozen order as decider is the status quo plus a dashboard, and keeps exactly what the founder ruled against. And the stated rejection of *first-attempts-only* **does not follow from its citation**: p = 2.213221e-59 comes from a chi-square on the 5 real models' per-round *finding counts*; it is not a comparison of first-attempt vs routed populations. I reproduced the figure — it is right, the inference drawn from it is not. The real reason to reject it is that it discards the routed trials, which are the population the decision concerns.

**3 — Removing the rung cap.** What bounds spend is not a cap but a **finite attempt lattice plus non-repetition**: a rung is a `(model, aid_level)` pair, each pair attempted at most once *per finding across the whole run*, so the remaining set strictly decreases and the process terminates. Stopping rule: **CONFIRMED, or the lattice is exhausted. No count.** Worst case `3 × |roster|` dispatches per finding *for the run* — against today's cap of 2 *per round, re-paid every round*, so the capped design is not obviously cheaper. Two guards, both loud: a global token ledger that **halts with a named reason** (as `HALTED_IRREDUCIBLE_QUEUE_ALARM` does) rather than silently capping, and `rung_unfunded` recorded as an outcome that leaves the finding unresolved and in the irreducible queue — never a skip that looks like a failure.

**4 — Resource-aware routing.** Yes, and as the *denominator of one objective*, not a second competing input. I derive that the expected-cost-minimising order for stop-at-first-success is `p_i/c_i` descending — so capability and budget are already one ratio and it is an optimum, not a compromise. A cheap model does not become the default **because the ladder exhausts**: first means *cheapest place to look first*, and the strong rung still runs when the probe fails. That guarantee is structural (order-invariance), not a tuning choice, so it cannot be tuned away. Load balancing falls out free: a model near its ceiling has its effective `c_m` raised and drifts down the order, degrading smoothly.

**5 — Reproducibility.** A separate step, performed by the harness. Not the models — a model attesting its own falsifier reproduces is a vote, and is the shape of the Exp 48 failure. Not primarily the human — 6194 archived entries across 131 artefacts; a control that doesn't run isn't a control. `reverify_falsifier` already gives one independent execution; what is missing is small: **execute twice in two fresh processes, record `sha256` of target and falsifier bytes with both verdicts, and treat disagreement as `NONDETERMINISTIC` — an instrument fault, not a finding verdict — routed to HIL.** The human's role is that residue plus `rung_unfunded`. That is the "both", correctly apportioned.

**6 — What we missed.** Nine items in the document; the four that matter most: the empty ladder is wider than the 1-seat case (executed: a roster of two identical labels also yields `[]`, which is the founder's *"all the models are the same"* case); **`gamma_critical` is not invariant to routing depth**, so `routing_max_rungs` is an undeclared input to the convergence gate; the 2026-10-06 provenance repair is correct but still loses the filer's **failure** from the denominator, inverting 5 of 11 ranks; and `rank_falsifier_writers._base` strips `-SIM`, which would pool a simulated model's history into a live run's estimate.

## The quantity

**Formula.** `p̂(m,d) = (k(m,d) + ½) / (n(m,d) + 1)` — Jeffreys (Beta(½,½)) posterior mean. `k` = CONFIRMED re-executions, `n` = provenance-clean attempts at depth `d`. Jeffreys, not Laplace: it is the binomial reference prior, its interval behaviour matches the Wilson interval this project mandates, and it returns ½ at `n=0` without asserting anything.

**Inputs.** `routing_history` (`model_used`, `verdict`, `rungs_tried` — present since 2026-10-03, 294 rung records today, which is thin and I say so), `falsifier_code` / `last_falsifier_code_full` for the provenance filter, and `resolved_by_routing` for authorship. Cost `c_m` = mean tokens per routing dispatch; roster median at `n=0`.

**Ranking.** `p̂(m,d)/c_m` descending; ties and all-cold-start break on position in `DEFAULT_FALSIFIER_STRENGTH`.

**Minimum sample: none — derived, not conceded.** A minimum sample is required of a statistic that *gates*. This one does not: under exhaustion every rung is tried regardless of its estimate, so a bad estimate can only misorder cost. That dissolves the blocker `RunnerConfig.routing_max_rungs` names for itself ("0 of 10 model pairs separate, all Fisher p ≥ 0.306"). **It also answers the A4 question directly: `p̂` opens no gate, so it needs no `severity_is_proven` analogue — it is not a number that admits or exempts anything.** The one place a number here *could* gate is cost, so: **cost may reorder a rung and may never remove one.**

**Cold start.** `n=0` → `p̂=½`, `c_m` = roster median → an unknown model enters at median `p/c` and is ordered among equals by cost, i.e. tried as a cheap probe, never excluded. This replaces today's behaviour, which appends unknown models in *roster order*.

**1-model panel.** A rung is `(model, aid_level)`, and `exclude` drops *pairs already attempted on this finding*, not models. Three levels: 0 = as today; 1 = plus the previous rung's falsifier source and traceback (`last_falsifier_code_full` already records exactly this, 221 records); 2 = plus worked examples (`routing.py`'s own docstring: 0/5 → 1/3, so not a no-op). A 1-seat roster gets a 3-rung ladder that exhausts, which is what the founder's ruling asks for and what the code currently refuses.

## What it does to gamma

**I predicted the wrong sign and my own measurement refuted me. The true direction is the dangerous one.** `_settled_novelty_series` skips `UNCONFIRMED` (it is in `_NON_NOVEL_TERMINAL_STATUSES`) and does not skip `CONFIRMED`, so a critical the ladder resolves *enters* the critical novelty series at its `open_since_round`. I expected back-fill at early rounds to raise `gamma_critical`. Over 14 archived runs with ≥3 rounds, flipping every unresolved critical to CONFIRMED moves it **down in 9, up in 3, unchanged in 2**, and **2 of 14 cross the `gamma_critical ≥ 0.30` arm downward** — `exp40_gate` 0.3018 → 0.2328, `commissioning_arm1_panel` 0.3236 → 0.1883. The mechanism is in the data: unresolved criticals skew **late** (9 of 14 runs), because an unresolved critical is one the ladder has not reached yet, and adding mass to the late end of a cumulative curve steepens it, raising β and lowering γ = 1 − β.

So: **removing the cap is not a pure spend question**, which is how both the founder's ruling and `routing.py`'s own comment frame it. It moves one arm of the two-sided gate in the direction that makes convergence *harder* — a run that passes today can stop passing — while the count arm does not move, because the resolution lands in an earlier bucket. I am **not** proposing to change `_NON_NOVEL_TERMINAL_STATUSES`: that would alter gamma for every archived run on my judgement, and the additive standard wants a committed measurement first. The simplest sufficient step is **recording-only** — log `gamma_critical` a second way with `UNCONFIRMED` treated as novel, so the coupling is visible per round while the gate keeps reading exactly what it reads today.

## Measurements

Every proportion with its Wilson 95% interval; every computed claim with ≥2 agreeing tools.

| figure | value | Wilson 95% | tools |
|---|---|---|---|
| P(resolve) distinct values over 5! ladder orders, exhausted | 1 (0.998812000000 = closed form) | — | SymPy (24/24 orders), NumPy enumeration, **Wolfram Language** (residual 0) |
| …under cap = 2 | 10 distinct, [0.7624, 0.9800] | — | SymPy (20/24 change), NumPy |
| `E[cost](a,b)−E[cost](b,a)` | `Q(c_a p_b − c_b p_a)`, residual 0 | — | SymPy, **Wolfram Language** |
| `p/c` order vs true optimum, 4000 random 5-rung rosters | worst gap 0.000e+00 | — | NumPy exhaustive permutation search |
| strongest-first suboptimal | 3637/4000 = 90.93% | [89.99%, 91.78%] | NumPy; closed form + statsmodels |
| cheapest-first suboptimal | 3525/4000 = 88.13% | [87.08%, 89.09%] | NumPy; closed form + statsmodels |
| index rule under position-dependent cost | loses 1.6393% (probe fires) | — | NumPy |
| runs crossing the 0.30 gamma arm downward | 2/14 = 14.29% | [4.01%, 39.94%] | repo's own `_estimate_gamma`; closed form + statsmodels |
| unresolved criticals skew later than registry mean | 9/14 = 64.29% | [38.76%, 83.66%] | same |
| rank inversions, entry-level vs attempt-level | 5/11 = 45.45% | [21.27%, 71.99%] | closed form + statsmodels |
| `resolved_by_routing` entries naming a different model | 458/458 = 100% of 6194 entries | [99.17%, 100%] | archive scan, two globs |
| model pairs separating, pooled clean cell | 43/55 = 78.18% | [65.63%, 87.05%] | Wilson non-overlap; closed form + statsmodels |
| DeepSeek 12/16 vs Gemini 1/8 (clean critical cell) | Fisher p = 0.00780724, OR 21.0 | DS [50.50%, 89.82%]; Gem [2.24%, 47.09%] | scipy, independent hypergeometric enumeration, **Wolfram Language** (9 s.f.) |
| CC2 39/41 vs Codex 42/46 | Fisher p = 0.679555 — **no separation** | CC2 [83.86%, 98.65%]; Cx [79.68%, 96.57%] | same three |
| Codex-SIM vs Codex, attempt level | 71.50% vs 27.94%, non-overlapping | [67.04%,75.57%] / [24.97%,31.12%] | closed form + statsmodels |
| SIM/LIVE separating in the *clean* cell | 2 of 5 vendors (3 overlap) | per-vendor in script output | same |

Wolfram ran locally and computed (attribution: Wolfram Language, local Wolfram Engine via `wolframscript`). One Wolfram call **failed to verify** and I am not quoting it: `FisherExactTest` returned unevaluated, so I re-expressed the test as an explicit hypergeometric sum, which did compute and agreed to 9 significant figures.

Executed, not read: `rank_falsifier_writers(['CC2'], exclude=('CC2',)) → []`; `(['CC2','CC2'], exclude=('CC2',)) → []`; `(['Codex','ChatGPT'], exclude=('Codex',)) → ['ChatGPT']`; `resolve_via_routing(..., max_rungs=0)` dispatches all 4 rungs, `max_rungs=2` dispatches 2. 15 fingerprint fields confirmed field-by-field: 9 from the initialiser + 6 from `_compute_attention_metrics`; `D_decay` supplies glossary `D`, `total_findings` plausibly `A`, and **`v̄` (verification) and `C` (coverage) are absent**. The brief's claim that `competence_provenance.py` credits the filer is **stale in this tree** — `falsifier_author` was repaired on 2026-10-06 and now prefers `resolved_by_routing`; the residual defect is the denominator, not the credit.

## Delivered files

- `docs/CAPABILITY_LADDER_MEASURED_2026-10-06.md` — the design, with derivations, the nine missed items, and a per-position refutation table.
- `scripts/ladder_order_is_cost_only_2026-10-06.py` — order-invariance and the `p/c` index rule; SymPy + NumPy brute force + live assumption probes. Exit 0.
- `scripts/the_ladder_statistic_loses_the_filers_failure_2026-10-06.py` — entry-level vs attempt-level accounting, Wilson + statsmodels. Exit 1 (inversions found).
- `scripts/routing_exhaustion_raises_gamma_critical_2026-10-06.py` — gamma_critical vs routing depth over 14 archived runs, using the runner's own `_settled_novelty_series` and `_estimate_gamma`. Exit 1 (gate arm crossed). **Its docstring retains my refuted hypothesis rather than editing it out.**
- `scripts/provenance_clean_cell_contradicts_frozen_ladder_2026-10-06.py` — the cell a re-derived ladder must come from; Fisher two ways, SIM vs LIVE. Exit 1.

All four answer `--help` without measuring. **No `bench/` module is added**: an unwired estimator would be the 12th of this project's 11 confirmed additions-that-nothing-reached. The design lands at `routing.py`'s one call site with tests that exercise it, or not at all.

## What would refute me

Per-position table in the document; the load-bearing ones: **order-invariance** falls if `scripts/ladder_order_is_cost_only_2026-10-06.py` exits non-zero, or if any path sets `resolved=True` without a `CONFIRMED` from `reverify_fn`. **The `p/c` rule** falls if the brute force shows a non-zero gap, or if rung cost grows with ladder position — already demonstrated to break it by 1.6393%, so my own aid levels 1–2 must be measured *against* R2, not assumed under it. **The single most falsifiable claim in the design:** a measured run where cheapest-first ordering resolves *fewer* criticals than strongest-first under exhaustion. By order-invariance that is impossible, so such a run refutes the whole design. **The gamma coupling** falls if that script reports 0 crossings in either direction. **The denominator claim** falls at 0 rank inversions. **The 1-model fix** falls if aid levels 1–2 confirm at `p̂` indistinguishable from level 0 — which would make the self-ladder an addition nothing reaches, the failure mode I am warning about. **Keeping the frozen tuple** falls to any committed measurement showing a `p̂`-derived order dominating it on resolutions-per-token in a live run.

## Disagreement

**With the founder, partially, on vendor names.** The ruling is *"the system shouldn't care at all what a model is called."* I am not deleting `DEFAULT_FALSIFIER_STRENGTH` and I think deleting it now would be wrong. At `n = 0` every model has `p̂ = ½` and the ratio ranks purely on cost; something has to break that tie, and the frozen tuple is the only ladder in this project with a validated end-to-end result (Exp 42's hardest residuals, 7/7 across two rungs). The additive standard permits removal only on a committed measurement showing the replacement dominates, and that measurement does not exist: my own contradiction of the tuple (Fisher p = 0.0078) comes from a cell that pools runs, targets and difficulties and is confounded by the very selection effect question 2 is about. So the tuple is demoted to tie-break and cold start, and the system stops caring about names the moment it has data — which is a weaker claim than the ruling, and I'd rather say so than pretend otherwise.

**With the brief, on one cited figure.** The rejection of first-attempts-only is supported by p = 2.213221e-59, which measures something else entirely. The proposal should still be rejected, for a different reason.

**With myself, recorded because the check is the point.** I predicted exhaustion would *raise* `gamma_critical`; the archive says it falls. I also expected the word-overlap duplicate path (`confirmed_duplicate` → `escalated = False` on bare Jaccard ≥ 0.85) to deadlock a finding permanently out of the ladder. It does not — `escalated` is re-set to `True` at several sites including the falsifier-gate path, so a later round can re-escalate. Both were claims that sounded right and one tool call each dissolved.

**Early stop, with reason.** I stopped here rather than extending to the depth-stratified estimate on live data: `routing_history` carries 294 rung records in total, so per-`(model, depth)` cells are single-digit and the estimate would be prior-dominated. That is a measurement to make after a routing-enabled run with the cap removed, not a number to manufacture now.

<!-- verbatim-end -->

## Where the raw record lives

`bench/logs/capability_ladder_design_blind_round2_2026-10-06/` holds the brief, every seat reply, the tool logs and `seat_proposals.diff`. That directory is excluded by `.gitignore:41`, so a byte-identical copy is committed under `experimental_notes/evidence/`, verified by sha256 and checked on every suite run by `bench/tests/test_panel_records_are_preserved_2026-09-11.py`.


Written under CDSFL note standard v1.7 (26 August 2026).
