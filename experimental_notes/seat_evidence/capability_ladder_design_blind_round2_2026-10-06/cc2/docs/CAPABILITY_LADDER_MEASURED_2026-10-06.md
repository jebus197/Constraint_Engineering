<!-- PRESERVED SEAT EVIDENCE. Written by seat 'cc2' during panel round 'capability_ladder_design_blind_cc2_2026-10-06', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: bb6463aaed8543fc92cfa7dddc93f463a7c63fe6609c59323c94f0dd66dc60cc
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited. -->
# The routing ladder as a measured statistic — design, with the derivation

**Seat:** fable (blind round, 2026-10-06). **Status:** design + 3 executable measurement
scripts. **No runtime behaviour is changed by this document.**

A note on vocabulary, per the panel's naming directive. The central quantity below has
no name in `docs/GLOSSARY.md` and I have deliberately **not coined one**. Where it must
be referred to, it is described in full: *the probability that a falsifier written by
model m for a finding at ladder depth d is re-executed by
`bench.falsifier_verify.reverify_falsifier` with verdict `CONFIRMED`*. The symbols
`p`, `c` below are the standard symbols of the sequential-search literature, not project
labels. It is **not** `rho` (discovery efficiency, novel/raw per round) and **not**
`S_k` (which classifies a FIX, not a claim); neither is reused and neither is suitable —
`rho` measures a round's yield, not a writer's success, and `S_k` is downstream of a
patch that does not exist at routing time.

---

## 0. The result that reorganises the whole question

Derived in `scripts/ladder_order_is_cost_only_2026-10-06.py`; SymPy symbolic,
exhaustive NumPy permutation enumeration, and Wolfram Language (local Wolfram Engine)
all agree.

**R1 — order-invariance under exhaustion.** `resolve_via_routing` stops at the first
`CONFIRMED`. With the cap removed (`max_rungs=0`), the probability a finding is resolved
is

    P(resolve) = 1 - prod_i (1 - p_i)

which is **symmetric in the rungs**. Checked symbolically over all 4! orderings
(0 of 24 change it) and numerically over all 5! = 120 orderings of the Exp-42 quoted
rates (1 distinct value, 0.998812000000, equal to the closed form to 1e-12). With the
current default `max_rungs=2`, 20 of 24 orderings **do** change it, numerically spanning
P(resolve) in [0.7624, 0.9800].

> **Therefore: once the cap is removed, ladder ORDER cannot change WHICH findings get
> resolved. It can only change what they COST.** Under the cap, order *is* a correctness
> question. The founder's two rulings — measure the ladder, and remove the cap — are
> not independent: removing the cap is what makes getting the measurement imperfectly
> right *safe*.

**R2 — the cost-minimising order is the index rule.** With per-rung dispatch cost `c_i`
and stop-at-first-success, `E[cost] = sum_i c_{s(i)} prod_{j<i} (1 - p_{s(j)})` is
minimised by sorting on `p_i / c_i` descending. Derived by adjacent transposition: for
two adjacent rungs reached with probability `Q`,

    E[cost](a,b) - E[cost](b,a) = Q*(c_a*p_b - c_b*p_a)

(SymPy residual 0; Wolfram residual 0), which is `<= 0` exactly when
`p_a/c_a >= p_b/c_b`; and the surviving-miss factor `(1-p_a)(1-p_b)` is symmetric, so
the suffix is unchanged. `p/c` induces a total order, so the sorted sequence is the
global optimum. Brute-forced over 4000 random 5-rung rosters with a 200x token-cost
spread: worst relative gap from the true optimum **0.000e+00**, while
**strongest-first is suboptimal in 3637/4000** rosters and **cheapest-first in
3525/4000**. Both naive policies lose; the ratio does not.

**Honest limit, probed rather than hidden.** R2 needs *position-independent* cost. The
same script shows the index rule losing 1.6393% to the optimum once cost grows with
depth — which is exactly what happens if a later rung is handed the earlier rung's
falsifier and traceback (the aid proposed in §3 for a single-seat roster). So R2 is an
exact optimum for the ladder as it dispatches **today**, and a heuristic for the ladder
I propose. Stated, not claimed away.

---

## 1. What the ladder should rank on

**The quantity.** The probability that a falsifier written by model `m`, for a finding
at ladder depth `d`, is re-executed by `reverify_falsifier` with verdict `CONFIRMED`,
restricted to falsifiers whose provenance is clean. Three restrictions, each load-bearing:

1. **Attempt-level, not entry-level.** Each `(model, finding, round)` dispatch is one
   Bernoulli trial. A filer whose falsifier failed and whose finding was routed away
   keeps that **failure** in its denominator.
2. **Provenance-clean only.** Counted only when
   `competence_provenance.falsifier_style(code) == "reads"`. This is the existing gate,
   reused rather than re-invented; without it Exp 55 ranks models by willingness to
   ignore the document.
3. **Stratified on ladder depth `d`** = number of rungs that already failed on this
   finding. See §2.

**The estimator.** Jeffreys posterior mean of a binomial rate:

    p_hat(m,d) = (k(m,d) + 1/2) / (n(m,d) + 1)

`k` = CONFIRMED re-executions, `n` = clean attempts. Jeffreys (Beta(1/2,1/2)) rather
than Laplace because it is the reference prior for a binomial, it is the prior whose
interval behaviour matches the Wilson interval this project requires, and it yields
`p_hat = 1/2` at `n = 0` without asserting anything.

**Cost.** `c_m` = mean total tokens per routing dispatch for `m`, from the same archive;
`c_m = ` roster median at `n = 0`.

**Ranking.** `p_hat(m,d) / c_m`, descending. Ties, and the all-cold-start case, break on
position in `DEFAULT_FALSIFIER_STRENGTH` — see §6 on why that tuple is **kept**.

**Minimum sample: none, and that is a derived conclusion, not a concession.** A minimum
sample is required of a statistic that **gates**. This one does not gate: by R1, under
exhaustion every rung is tried regardless of its estimate, so the estimate can only
misorder cost. The config comment at `RunnerConfig.routing_max_rungs` names its own
blocker as "0 of 10 model pairs separate (all Fisher p >= 0.306)" and defers the whole
design on it. **That blocker is dissolved by R1, not by better data.** It is also
partly dissolved by data: on the pooled archive's provenance-clean critical cell,
43 of 55 model pairs separate at 95% (Wilson non-overlap), 78.18%, Wilson
[65.63%, 87.05%].

**Cold start.** `n = 0` gives `p_hat = 1/2` and `c_m` = roster median, so an unknown
model enters at the median `p/c` and is ordered among equals by cost. A brand-new model
is therefore tried as a **cheap probe**, early if cheap and later if expensive, and is
never excluded. This replaces `rank_falsifier_writers`'s current behaviour, which
appends unknown models in **roster order** — an arbitrary tiebreak masquerading as a
ranking.

**One-model panel.** This is where the current code contradicts the founder's ruling
outright, and I verified it by execution rather than by reading:

```
rank_falsifier_writers(['CC2'],        exclude=('CC2',))  ->  []
rank_falsifier_writers(['CC2','CC2'],  exclude=('CC2',))  ->  []
rank_falsifier_writers(['Codex','ChatGPT'], exclude=('Codex',)) -> ['ChatGPT']
```

The founder's ruling: *"even a single model operating on its own (in which case the
ladder would just route the issue back to itself and would have another go at resolving
it by using the rest of the machinery of the harness.)"* The code instead stamps
`routing_deferred` with reason "routing ladder empty by construction". Note the second
line above: the ladder is empty for **any roster whose every seat shares the finding's
source label**, which is the founder's *"all the models are the same"* case, not only
the 1-seat case.

**The fix, and it is the simplest sufficient one.** A rung is not a model; it is a pair
`(model, aid_level)`, and `exclude` drops *pairs already attempted on this finding*,
not models. Three aid levels, ordered, each already supported by machinery that exists:

| `aid_level` | what the rung is given | evidence it is not a no-op |
|---|---|---|
| 0 | the finding + target, as today | the current path |
| 1 | plus the previous rung's falsifier source and its traceback | `routing_history.last_falsifier_code_full` already records exactly this, for 221 records |
| 2 | plus worked falsifier examples | `routing.py`'s own docstring: teaching lifted the weak model 0/5 -> 1/3 |

A 1-seat roster therefore has a 3-rung ladder, not a 0-rung one, and it exhausts.
`p_hat` is estimated per `(model, aid_level)`, so aid level 1 and 2 earn their position
rather than being assumed better.

---

## 2. The selection effect

**My answer: condition on ladder depth. Do not randomise, and do not keep the frozen
order as the decider.**

The selection is **fully observed**. A finding reaches model `m` at depth `d` because
`d` rungs ahead of it failed — `d` is the ladder's own counter, already recorded in
`routing_history.rungs_tried`. When assignment depends only on observed covariates,
conditioning on them removes the bias; this is selection on observables, and it needs no
randomisation. `p_hat(m, d)` compares models **at the same depth**, i.e. on findings of
the same demonstrated difficulty. The strong model's depressed marginal rate is a
mixture artefact of being used at high `d`; the conditional rates are not depressed.

On the three earlier proposals:

- *First attempts only* — rejected, but **the stated reason does not support the
  rejection.** The cited `p = 2.213221e-59` comes from
  `scripts/the_sim_panel_is_not_heterogeneous_2026-10-05.py`, which tests whether one
  finding-rate explains the 5 real models' per-round finding **counts**. It is not a
  comparison of the first-attempt and routed populations and says nothing about them.
  I reproduced that script: the figure is right, the inference drawn from it is not.
  The correct reason to reject first-attempts-only is simpler: it discards every routed
  trial, and routed trials are precisely the population the ladder's decision concerns.
  It answers a different question accurately.
- *Randomised audit fraction* — right identification of the problem, **not deployable
  and not needed.** Not deployable: routing fires on unresolved criticals only, so the
  audit stratum would accrue single-digit `n` per model per run. Not needed: there is
  nothing left for randomisation to buy once you condition on `d`, because `d` is the
  entire assignment mechanism.
- *Frozen order as decider, rate as drift alarm* — rejected. It is the status quo with a
  dashboard bolted on, and by R1 the rate is safe to decide with once the cap is gone.
  Worse, it keeps the thing the founder specifically ruled against: *"our runners
  shouldn't care if a particularly named vendor model is available or not."*

**Gating, and the A4 question asked explicitly.** `p_hat` **opens no gate.** It permutes
a sequence whose outcome is permutation-invariant (R1). It therefore does **not** need
`severity_is_proven`-style proof, because it is not a number that admits or exempts
anything — and that is the whole reason the design is built around exhaustion. The one
place a number here *could* open a gate is cost: a rung skipped for want of budget is a
gate. So, normatively: **cost may reorder a rung and may never remove one.** §4.

---

## 3. Removing the rung cap

**What stops unbounded spend is not a cap, it is a finite lattice plus a
non-repetition rule.** The attempt lattice for a finding is
`{(model, aid_level) : model in roster} x {0,1,2}`, of size `3 * |roster|`. Record every
attempted pair in `routing_history` (which already carries `model_used` and
`rungs_tried`) and **never repeat one, across rounds as well as within a round**. The
remaining set is then strictly decreasing, so the process terminates. That is the
stopping rule:

> **A finding stops routing when it is CONFIRMED, or when its attempt lattice is
> exhausted. There is no count.**

Per finding the worst case is `3 * |roster|` dispatches *over the whole run*, not per
round — today's cap of 2 is per `route()` call and is therefore re-paid every round,
which is worth noticing: the capped design is not obviously the cheaper one.

Two guards, and both must be loud:

1. **A global token ledger that HALTS, never silently caps.** When the run's routing
   spend crosses a declared bound, halt with a named reason, exactly as
   `HALTED_IRREDUCIBLE_QUEUE_ALARM` does. A silent cap is the defect
   `routing_max_rungs = 2` already was: 23 routing-enabled configs, 0 pinning the value,
   rungs 3+ unreachable by construction in every archived run, and the project's own
   comment admitting "what does rung 3 buy" was unmeasured rather than known.
2. **`rung_unfunded` is an outcome, not a skip.** A rung the budget cannot fund is
   recorded as such and the finding stays unresolved and counts toward the irreducible
   queue. It must never look like a tried-and-failed rung.

---

## 4. Resource-aware routing

**Yes, and it must enter as the denominator of a single objective, not as a second
competing input.** R2 shows the cost-minimising order is `p/c` descending — capability
and budget are already one ratio, and it is the *optimum* of the expected-cost
objective, not a compromise between two.

**Why this does not make a cheap model the default answer.** Because the ladder
exhausts. Putting a cheap weak model first costs one cheap dispatch and, by R1, removes
nothing: the expensive strong rung still runs when the probe fails. "First" under
exhaustion means *cheapest place to look first*, not *the answer*. The structural
guarantee is R1; it is not a tuning choice, so it cannot be tuned away.

**Load balancing** then falls out of the same objective without new machinery: `c_m` is
per-model, so a model near its budget ceiling has its effective `c_m` raised and drifts
down the order — degrading smoothly instead of being cut off. Combined with the
`rung_unfunded` rule, no model is ever silently removed.

---

## 5. Reproducibility

**A separate verification step, performed by the harness. Not by the models, and not
primarily by the human.**

- **Not the models.** A model attesting that its own falsifier reproduces is a vote, and
  the falsifier-integrity directive forbids asserting a verdict you did not compute. It
  is also the exact shape of the Exp 48 failure.
- **Not primarily the human.** The archive I measured holds 6194 registry entries across
  131 artefacts. Per-finding human reproduction does not scale, and a control that does
  not run is not a control.
- **The harness.** `reverify_falsifier` already re-executes independently, which is one
  run. Reproducibility needs **two**, and what is missing is small and concrete:
  1. re-execute the stored falsifier **twice**, in two fresh processes;
  2. record `sha256(target_bytes)`, `sha256(falsifier_bytes)`, and both verdicts;
  3. equal verdicts -> `reproducible: true`; **unequal -> `NONDETERMINISTIC`, which is
     an instrument fault, not a finding verdict**, and goes to HIL.

The human's role is the residue: adjudicating `NONDETERMINISTIC` and `rung_unfunded`.
That is the "both" the founder asked about, correctly apportioned — the tool does the
volume, the human does the irreducible part. This also matters for the STEM-calculator
goal: *problem in, definitive repeatable answer out* is a claim about the pair
(answer, reproduction), and a routing ladder that resolves a critical with a
single-execution verdict has not established the second half.

Note one way routing makes this harder: `resolve_fn` dispatches with
`enable_tools=True`, so a rung's falsifier is authored inside a tool loop that may have
left state. Re-execution must be of the **final falsifier text in a clean process**,
which is what `reverify_falsifier` does — so the existing decider is right and only the
second execution is absent.

---

## 6. What this design, and the brief, have missed

**(a) The empty ladder is wider than the 1-seat case.** Executed:
`rank_falsifier_writers(['CC2','CC2'], exclude=('CC2',)) -> []`. The founder's
*"all the models are the same"* roster has no ladder at all. §1.

**(b) gamma_critical is NOT invariant to routing depth — measured, and my own first
hypothesis about it was wrong.** `scripts/routing_exhaustion_raises_gamma_critical_2026-10-06.py`.
`_settled_novelty_series` skips `UNCONFIRMED` (it is in `_NON_NOVEL_TERMINAL_STATUSES`)
and does not skip `CONFIRMED`, so a critical the ladder resolves **enters** the critical
novelty series at its `open_since_round`. I predicted gamma would rise. Over 14 archived
runs with >= 3 rounds, flipping every unresolved critical to CONFIRMED moves
`gamma_critical` **down in 9, up in 3, unchanged in 2**, and **2 of 14 cross the
`gamma_critical >= 0.30` arm downward** (14.29%, Wilson [4.01%, 39.94%]):
`exp40_gate` 0.3018 -> 0.2328 and `commissioning_arm1_panel` 0.3236 -> 0.1883. The
mechanism is in the data: unresolved criticals skew **late** (9 of 14 runs have their
unresolved-critical mean `open_since_round` above the registry mean, 64.29%, Wilson
[38.76%, 83.66%]) because an unresolved critical is one the ladder has not reached yet,
and adding mass to the late end of a cumulative curve steepens it, raising beta and
lowering `gamma = 1 - beta`.

Consequence: **removing the rung cap is not a pure spend question**, which is how both
the founder's ruling and `routing.py`'s own comment frame it. It is a change to one arm
of the convergence gate, in the direction that makes convergence *harder*, so a run that
passes today can stop passing — and the count arm does not move, because the resolution
lands in an earlier bucket. I am **not** proposing to change `_NON_NOVEL_TERMINAL_STATUSES`:
that would alter gamma for every archived run on my judgement, and the additive standard
requires a committed measurement first. The simplest sufficient step is **recording-only**:
compute and log `gamma_critical` a second way, with `UNCONFIRMED` treated as novel, so the
coupling is visible per round while the gate keeps reading exactly what it reads today.
Then rule on it with data.

**(c) The competence statistic still loses the filer's failure.**
`scripts/the_ladder_statistic_loses_the_filers_failure_2026-10-06.py`. The
2026-10-06 repair to `competence_provenance.falsifier_author` is correct and I do not
dispute it. But `analyse()` iterates **entries** and assigns each to exactly one model,
so a routed entry leaves the filer's record entirely — the filer loses a numerator it
should not have had *and* a denominator it should keep. Over 6194 archived entries, 458
carry `resolved_by_routing` and 458 of 458 name a different model from `source_model`.
Entry-level and attempt-level accounting produce **5 rank inversions across the 11
models in both orders** (45.45%, Wilson [21.27%, 71.99%]); at entry level `CC2-SIM`
leads, at attempt level `Codex-SIM` does. The founder's ruling is to rank on "what a
model can be statistically demonstrated to have done", and a model that tried and failed
did something the current statistic cannot see.

**(d) The frozen tuple's last two rungs are in the wrong order, by a separating
measurement.** On the provenance-clean critical cell (`severity >= 0.7`, falsifier reads
the target): `DeepSeek` 12/16 = 75.00% [50.50%, 89.82%] vs `Gemini` 1/8 = 12.50%
[2.24%, 47.09%], Fisher exact **p = 0.00780724** — scipy, an independent
hypergeometric-enumeration recomputation, and Wolfram Language all agreeing to 9
significant figures. `DEFAULT_FALSIFIER_STRENGTH` places Gemini **ahead of** DeepSeek.
Meanwhile the top of the tuple does **not** separate: `CC2` 39/41 vs `Codex` 42/46,
Fisher p = 0.679555 (same three tools). So the measured picture is: the ladder can tell
strong from weak and cannot order within the strong group — which is exactly the regime
R1 says is harmless. **Caveat I am not going to bury:** this cell pools across runs,
targets and difficulties, so it is confounded by precisely the selection effect §2 is
about. It is sufficient to show the frozen order is *contradicted*; it is not sufficient
to install a replacement order. Installing one requires the depth-stratified estimate.

**(e) A simulated seat's history must not decide a live run's ladder.**
`rank_falsifier_writers._base` strips `-SIM` so a simulated label "ranks as its vendor".
That normalisation is right for *ordering a simulated roster* and wrong for
*estimating `p_hat`*. At attempt level over all entries the two populations separate by
a wide margin — `Codex-SIM` 306/428 = 71.50% [67.04%, 75.57%] vs `Codex` 228/816 =
27.94% [24.97%, 31.12%], non-overlapping by 36 percentage points. **On the narrower
provenance-clean cell the picture is weaker and I report it as measured, not as it
would be convenient:** 2 of 5 vendors separate (`CC2` SIM 97.58% [93.93, 99.05] n=165
vs LIVE 85.11% [72.31, 92.59] n=47; `DeepSeek` SIM 87.76% [75.76, 94.27] n=49 vs LIVE
57.14% [39.07, 73.49] n=28) and 3 overlap, Codex among them. So the hazard is
demonstrated but not uniform. It is still decisive for the design, because pooling is
irreversible once done and the sample sizes are lopsided — 428 simulated trials against
816 live for Codex alone. **`p_hat` must be keyed on the full label, `-SIM` included.**
The fingerprint files already are (`Codex.json` and `Codex-SIM.json` are separate); the
ladder's normalisation is the one place that would pool them.

**(f) Keep `DEFAULT_FALSIFIER_STRENGTH`; demote it.** The additive standard permits
removal only on a committed measurement showing the replacement dominates. No such
measurement exists — (d)'s cell is confounded, and the frozen tuple is the only ladder
with a validated end-to-end result (Exp 42's hardest residuals, 7/7 across 2 rungs). So
it stays, as the cold-start and tie-break ordering, where it is doing work no measured
statistic can do at `n = 0`. This is a partial disagreement with the founder's framing,
stated in §Disagreement of the reply.

**(g) What `_update_observed_fingerprint` actually writes, against the glossary.** 15
fields, verified field by field: 9 from the initialiser (`max_successful_context_chars`,
`max_failed_context_chars`, `max_successful_prompt_chars`, `max_failed_prompt_chars`,
`prompt_chars_history`, `failure_modes`, `total_findings`, `rounds_participated`,
`avg_findings_per_round`) plus 6 from `_compute_attention_metrics`
(`measured_attention_span`, `compression_threshold`, `quality_at_capacity`,
`decomposition_recommended`, `attention_ratio`, `D_decay`). The glossary defines the
profile as `(D, v-bar, A, C)` with `v-bar` a **verification score** and `C` a
**coverage** dimension. `D_decay` supplies `D`; `total_findings` is a plausible `A`;
`v-bar` and `C` are **absent**. So the ladder could not read the capability it needs
from the fingerprint even if it tried — this design's `p_hat` *is* the missing `v-bar`,
and `C` remains unbuilt and is out of scope here. The docstring claim "ordered by
capability fingerprint" should be corrected to describe what the code does until the
code does it; a docstring that describes an intention is how this disagreement went
unnoticed from June to October.

**(h) The word-overlap duplicate path.** `confirmed_duplicate` returns `resolved=True`
on a bare Jaccard >= 0.85 and the caller sets `escalated = False`. The merge itself is
correctly withheld with `merge_blocked_reason` "a similarity score is not a tool
verdict". I checked whether this deadlocks the finding out of the ladder permanently and
**it does not**: `escalated` is re-set to `True` at several sites including the
falsifier-gate path, so a later round can re-escalate it. I had expected a deadlock and
there isn't one; recorded because the check is the point.

**(i) What I did not read, deliberately.**
`bench/logs/capability_ladder_design_blind_cc2_2026-10-06/seat_proposals.diff` exists in
this tree and is a prior round's material for **this** exam. Under the falsifier-integrity
directive that is inadmissible and I did not open it. It should not be in a blind round's
sandbox: a blind round whose sandbox contains the other seats' proposals is not blind,
and the next seat may not stop to notice. That is a staging defect in the harness, not
in this design.

---

## Delivered files

| path | what it is | re-run |
|---|---|---|
| `docs/CAPABILITY_LADDER_MEASURED_2026-10-06.md` | this design | — |
| `scripts/ladder_order_is_cost_only_2026-10-06.py` | R1 + R2, SymPy + NumPy brute force + assumption probes | `python3 scripts/ladder_order_is_cost_only_2026-10-06.py` (exit 0) |
| `scripts/the_ladder_statistic_loses_the_filers_failure_2026-10-06.py` | entry-level vs attempt-level accounting, Wilson + statsmodels | `python3 scripts/the_ladder_statistic_loses_the_filers_failure_2026-10-06.py` (exit 1 = inversions found) |
| `scripts/routing_exhaustion_raises_gamma_critical_2026-10-06.py` | gamma_critical vs routing depth over 14 archived runs | `python3 scripts/routing_exhaustion_raises_gamma_critical_2026-10-06.py` (exit 1 = gate arm crossed) |
| `scripts/provenance_clean_cell_contradicts_frozen_ladder_2026-10-06.py` | the cell a re-derived ladder must come from: Wilson + Fisher two ways, SIM vs LIVE | `python3 scripts/provenance_clean_cell_contradicts_frozen_ladder_2026-10-06.py` (exit 1 = frozen order contradicted) |

Each script answers `--help` without measuring, per the project's rule that a `--help`
must never cost anything.

**No `bench/` module is added.** An unwired estimator module would be the project's most
common defect — 11 confirmed additions that nothing reached since 2026-08-01 — and would
be the 12th. The design lands when it lands at `routing.py`'s one call site with the
tests that exercise it, not before.

---

## What would refute each position

| position | what would refute it |
|---|---|
| R1 / order-invariance | `scripts/ladder_order_is_cost_only_2026-10-06.py` exiting non-zero; or any path in `resolve_via_routing` setting `resolved=True` without a `CONFIRMED` from `reverify_fn`; or a cap surviving in config |
| R2 / `p/c` ordering | the same script's brute force showing a non-zero gap; or a rung cost that depends on ladder position — already demonstrated to break R2 at 1.6393%, so aid levels 1-2 must be measured against R2, not assumed under it |
| §1 estimator | a measurement showing depth-stratified cells with `n` so small that the Jeffreys mean is dominated by the prior **and** that the resulting misordering costs more tokens than the ordering saves. Command: the attempt-level script restricted to `routing_history` records (294 today — thin, and I say so) |
| §1 one-model panel | `rank_falsifier_writers(['CC2'], exclude=('CC2',))` returning a non-empty list; or a measurement showing aid levels 1-2 confirm at `p_hat` indistinguishable from aid level 0, which would make the self-ladder an addition nothing reaches |
| §2 condition-on-depth | a measurement showing `p_hat(m,d)` still ordered by marginal usage after conditioning — i.e. that `d` is not the whole assignment mechanism. Any routing path that selects a rung on something other than ladder order and `exclude` refutes it |
| §3 stopping rule | a `routing_history` record showing the same `(finding, model, aid_level)` attempted twice; or a run whose routing spend exceeds `3 * |roster|` dispatches per finding |
| §4 cost in the objective | a measured run where cheapest-first ordering resolves **fewer** criticals than strongest-first under exhaustion. By R1 that is impossible, so such a run refutes R1 and the whole design with it. This is the design's single most falsifiable claim |
| §5 reproducibility | a sweep of `routing_history.last_falsifier_code_full` re-executing every stored falsifier twice and finding 0 verdict disagreements — which would make the second execution an addition nothing reaches |
| (b) gamma coupling | `scripts/routing_exhaustion_raises_gamma_critical_2026-10-06.py` reporting 0 runs crossing the 0.30 arm in either direction |
| (c) denominator | the same script reporting 0 rank inversions between entry-level and attempt-level |
| (d) tuple order | `scripts/competence_provenance.py` marking the pooled cell UNSAFE TO RANK ON; or the depth-stratified cell reversing the DeepSeek/Gemini sign |
| (e) SIM pooling | all 5 vendors' SIM/LIVE Wilson intervals overlapping in the provenance-clean cell — today 2 of 5 separate, 3 overlap, so the claim rests on the lopsided denominators as much as on the gap. Command: `scripts/provenance_clean_cell_contradicts_frozen_ladder_2026-10-06.py` |
| (f) keep the tuple | any committed measurement showing a `p_hat`-derived order dominating the frozen tuple on resolutions-per-token in a live run. That measurement does not exist today; when it does, the tuple should go |
