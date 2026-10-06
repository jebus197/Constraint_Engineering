<!-- PRESERVED SEAT EVIDENCE. Written by seat 'cc2' during panel round 'capability_ladder_design_blind_cc2_2026-10-06', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: e6e00c7ee1925525edf81fbf8fc93cde70e02a24574520e776b1e039478d6ddc
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited. -->
# Proposal — what should decide which model is asked to do the hardest work

**Status: PROPOSAL + 5 CONFIRMED DEFECTS. Blind seat, 2026-10-06. Nothing implemented.**

Producers, all re-runnable, all importing the real modules:

| script | what it decides |
|---|---|
| `scripts/the_provenance_gate_calls_the_import_form_detached_2026-10-06.py` | D-1 |
| `scripts/the_ladder_cannot_route_back_to_a_sole_model_2026-10-06.py` | D-2 |
| `scripts/falsifier_resolution_index_2026-10-06.py` | the estimator: ratio-rule derivation (SymPy + z3 + brute force), archive measurement, minimum sample |
| `scripts/the_routing_selection_effect_runs_downhill_2026-10-06.py` | the selection effect: bias by rung, entrenchment, four frames, the composition test |

Every proportion below carries a Wilson 95% interval; the closed form and
`statsmodels.stats.proportion.proportion_confint(method="wilson")` agree to 1e-12 at
every figure, printed inline by the scripts.

---

## Summary of what is wrong

Five defects, each demonstrated by a falsifier that imports the real target.

**D-1 (CRITICAL). The gate that must authorise any ladder re-derivation calls the
directive-mandated falsifier form "detached."**
`scripts/competence_provenance.py::falsifier_style` decides "did this falsifier read
its target?" with one regex: `open\s*\(|read_text|\.read\s*\(|linecache|getlines`. The
CDSFL falsifier-integrity directive *requires* the import form — "Import the REAL
target module (e.g. `from bench.dm._convergence import ...`)" — which matches none of
those names. Measured over the 59 archived `bench/logs/*/runner_state.json` corpora:
of 1078 non-empty falsifiers, **630 (58.44%, Wilson [55.47%, 61.35%]) import a
repository module and are classified `detached`**; only 130 (12.06%, [10.25%, 14.14%])
are truly detached. The gate therefore prints UNSAFE TO RANK ON for essentially any
real corpus, so **the measured ladder the founder has ordered cannot be derived at all
while this classifier stands**, and if the refusal were overridden the statistic would
rank models by whether they reach the target with `open()` rather than with `import`
— the inverse of the directive. This is the blocker: fix it first or nothing else in
this proposal can be measured.

**D-2 (CRITICAL). A one-model panel gets ZERO falsification attempts.**
The founder's ruling requires that a sole model "route the issue back to itself and
have another go." `route()` builds `rungs` with `exclude=(source,)` unconditionally; on
a one-model panel the source *is* the only model, `rungs` comes back empty, the loop
in `resolve_via_routing` never executes, and the result is
`UNTOOLABLE / rungs_tried=0 / resolve_fn called 0 times`. Setting `max_rungs=0`
("exhaust the ladder") cannot help, because the ladder it exhausts is empty. Already
in the archive: of 161 recorded routing events, **21 (13.04%, [8.69%, 19.12%]) had
`rungs_available == 1`, and 21 of 21 (100%, [84.54%, 100%]) recorded
`rungs_tried == 0`** — criticals sent to human escalation without one attempt made.
Repair is one branch, additive, multi-model behaviour bit-identical (see the script).

**D-3 (ABOVE THRESHOLD). The system does care what a model is called, and an
unrecognised name ranks below the model the module itself calls the worst.**
`rank_falsifier_writers(['NewStrongModel','DeepSeek','Gemini'])` returns
`['Gemini', 'DeepSeek', 'NewStrongModel']`. Unknown models land in `extras`, after
every named vendor — including DeepSeek, which `routing.py` names as "the primary
offender ... never asked to take over routing." The penalty for being new is to be
tried last. Separately, `rank_falsifier_writers(['CC2','CC2-SIM','CC2'],
exclude=('CC2',))` returns `['CC2-SIM']`: a three-seat same-vendor panel yields a
one-rung ladder, because `exclude` is a label set and collapses the duplicate seats.
The founder asked for "all the models are the same" to work; it does not.

**D-4 (ABOVE THRESHOLD). The frozen ladder *is* the statistic the project's own ★
warning forbids ranking on.** Over the whole archive, ordering models by RAW
falsifier-confirm rate (collapsing `-SIM` to vendor exactly as `_base()` does)
reproduces `DEFAULT_FALSIFIER_STRENGTH` **exactly**: Kendall tau = **+1.0000**. Ordering
by the admissibility-corrected rate gives tau = **+0.2000** against the frozen tuple
(scipy `kendalltau` agrees, +0.2000). The ★-marked founder observation of 2026-08-23
exists to stop anyone re-deriving the order from a raw confirm rate. The order already
in the file is, to a rank correlation of 1, that very rate. It is not a safer
alternative measurement; it is the forbidden measurement, frozen in June.

**D-5 (ABOVE THRESHOLD). `routing.py`'s own cost argument for uncapping is refuted by
the archive, and exhaustion has never once been executed.** The module argues a deeper
budget is "nearly free" because "rungs 3+ are reached on a small minority." Observed
`rungs_tried` across 161 routing events: `{0: 21, 1: 64, 2: 76}`. **76 of 161 (47.21%,
[39.65%, 54.89%]) hit the `routing_max_rungs=2` cap** — 76 of the 140 where any rung
was tried (54.29%, [46.03%, 62.31%]). The cap binds on about half of routing events,
so uncapping is a routine cost, not insurance against a pathological run. And the
maximum `rungs_tried` ever observed is 2, with 0 of 288 config-shaped files pinning
`routing_max_rungs`: the `max_rungs=0` exhaustion path is wired to a parameter and has
never been reached by any run. By the additive standard that is an addition nothing
reaches, which this project has shipped 11 times since 2026-08-01.

---

## 1. What the ladder should rank on

**Not "capability."** The ladder makes one decision — who to ask next for a falsifier
on an unresolved critical — so it should rank on the probability that asking produces
an admissible falsifier the runner's own re-verification CONFIRMS, per token spent.

I am describing the mechanism rather than naming it, because no formal name for it
exists in `docs/GLOSSARY.md` or in the code. The three components each have standard
names and I use those: a **Beta-Binomial posterior mean of a success proportion** as
the point estimate, the **Wilson score interval** as the authority gate, and an
**index policy** (rank candidates by a scalar, take the maximum) as the ordering rule.
In code the field should be a descriptive identifier such as
`admissible_confirmation_rate` and its denominator `falsifier_attempts`, not a coined
noun.

### The quantity

An **attempt** is: model *m* was asked for a falsifier on a critical finding, and the
runner's `falsifier_verify.reverify_falsifier` returned a verdict. A **success** is a
verdict of `CONFIRMED` whose falsifier is **admissible** — it demonstrably reaches a
real target, by an open-family call *or* by a repository-module import. Note the
denominator: an empty falsifier (295 of 1373 archived entries) counts as an attempt
and a failure, because "asked and supplied nothing" is exactly as useless to the
ladder as "supplied something that did not demonstrate the defect." Conditioning it
away, as my first draft did, flatters models that decline to answer.

    p_hat(m) = (s_m + kappa * p_pool) / (n_m + kappa)

equivalently the shrinkage form

    p_hat(m) = w * (s_m / n_m) + (1 - w) * p_pool,   w = n_m / (n_m + kappa)

with `p_pool` the panel-wide admissible-confirmation rate and `kappa` the prior
strength in pseudo-attempts. **kappa = 4.** Derivation, not taste: `w = n/(n+kappa)`
means kappa is the sample size at which a model's own record earns half the weight. At
kappa = 4 a model with one lucky success sits at (1 + 4*p_pool)/5 — for p_pool = 0.8
that is 0.84, a nudge, not a promotion — while a model with 40 attempts gets 91% of
its own record. Any kappa in 2..8 behaves similarly; the figure is a knob with a
stated meaning, not a tuned constant.

**Minimum sample: there isn't one number, and claiming one would be false precision.**
The honest rule is pairwise and comes straight from the interval the brief requires:

> *m* may be placed above *m'* only if WilsonLower95(p_hat(m)) > WilsonUpper95(p_hat(m')).
> Pairs that fail that test keep their FALLBACK order.

The ladder becomes a **partial order refined by evidence**. Solved numerically
(`--part 3`), the smallest equal per-model n at which two Wilson 95% intervals
separate is **11 at the 0.90-vs-0.28 spread the frozen ladder was derived from**
(so that derivation was adequately powered), **149 at 0.40 vs 0.25**, and **1328 at
0.35 vs 0.30**. The ends of the ladder are cheap; the middle is not. On today's real
archive, **8 of 55 ordered pairs separate (14.55%, [7.56%, 26.16%])** — 47 pairs stay
in the fallback order. That is the correct outcome, and it is also the measure of how
much of the founder's ruling can be honoured today: the ends, not the middle.

**Cold start.** A model with no history gets `p_hat = p_pool` exactly, so it enters
*mid-ladder* and is tried. It must not get the Wilson lower bound, which is 0 at
n = 0 and would send every new entrant to last place — the behaviour D-3 already
exhibits and that the founder's ruling forbids. Note this is strictly better than
today for the case that matters: an unrecognised model currently ranks below the model
`routing.py` itself calls the worst.

**Vendor-agnosticism, properly.** The key must be the dispatch identity actually used
— `(provider, model_id, decoding parameters, tool-loop configuration)`, hashed — not
the seat label. Two seats labelled `CC2` at different temperatures are different
models, and `_base()`'s `-SIM` stripping currently makes a simulated seat inherit its
vendor's record, which is a vendor-name dependency hard-coded into the ranker. Keying
on dispatch identity makes "all different", "all the same", "all one vendor" and "one
model alone" the same code path, with no name in it.

**One-model panel.** The pool has one entry, so the ordering is trivial and the whole
question becomes the stopping rule (§3). This only works once D-2 is repaired; today
the candidate set is empty and no statistic can help.

### Which existing instruments this reuses, and which it does not

- **severity** — reused, as the value term in the stopping rule (§3) only, never in
  the estimator. Gated exactly as A4 gates it: an UNPROVEN severity may not extend the
  budget (§3).
- **rho** — NOT reused. rho is discovery efficiency, novel over raw findings per
  round. It measures how much *new ground* a round covers, which is a property of a
  round, not of a model's ability to demonstrate a specific defect.
- **S_k** — NOT reused. `S_k` classifies a FIX. A falsifier is not a fix; it is a
  test. Borrowing a fix-efficacy construct to score a test would conflate the two
  roles the schema deliberately separates.
- The capability statistic itself is computed by the **runner** from the runner's own
  re-verification verdicts. No model asserts it. It is therefore not a model vote, and
  needs no `severity_is_proven`-style gate of its own. That property is load-bearing
  and should be asserted by a test, because it is the only thing that keeps the
  measured ladder inside "tools decide, not votes."

---

## 2. The selection effect — the brief's premise is inverted

**The brief says the ladder "sends HARD findings to strong models, so their success
rate is depressed by being trusted." Measured, the opposite is true.**
`rank_falsifier_writers` returns *strongest first* and `resolve_via_routing` tries
rung 1 first, so **rung 1 sees the UNSELECTED population** and every model *below* it
sees only findings that already defeated everyone above. Simulated over the ladder's
own dynamics by
`scripts/the_routing_selection_effect_runs_downhill_2026-10-06.py`:

| hardness sd | rung-1 model | rung 2 | rung 3 | rung 4 | rung 5 |
|---|---|---|---|---|---|
| 0.5 | **+0.0003** | −0.0372 | −0.0936 | −0.1041 | −0.0829 |
| 1.0 | **−0.0008** | −0.1334 | −0.2315 | −0.2402 | −0.1769 |
| 2.0 | **+0.0021** | −0.2978 | −0.3744 | −0.3608 | −0.2888 |

(`--part A`. Bias of the raw rate against the unselected marginal truth.)

The rung-1 model's rate is unbiased to three decimal places. The bias lands on
everything beneath it, worst in the middle. **The real hazard is therefore not
depression of the strong, it is ENTRENCHMENT**: a wrong order is self-confirming,
because whoever is placed first is the only one measured on an unselected population.
Demonstrated — deploy an order in which the genuinely second-best model is ranked
first, and measure P(the raw rate corrects it), 200 replicates of 400 findings each,
Wilson 95% (`--part B`):

| hardness sd | raw rate corrects the wrong order | with eps = 0.25 |
|---|---|---|
| 0.5 | 58.50% [51.57, 65.11] | 81.50% [75.54, 86.27] |
| 1.0 | 53.50% [46.59, 60.28] | 69.50% [62.80, 75.46] |
| 2.0 | **0.00% [0.00, 1.88]** | **2.50% [1.07, 5.72]** |

A cold-start misplacement is not reliably corrected at any dispersion tested, and at
sd = 2 it is never corrected in 200 replicates. *Recorded because it bears on how
much to trust the rest: the first version of this experiment was a single realisation
and reported "raw fails at sd = 1.0"; re-run under a different seed it reported the
opposite, because the two top models come out near-tied there. Only the replicated
proportions above are claims, and the script now refuses to produce the single-shot
form.*

**And the stated reason for rejecting "first attempts only" does not bear on it.**
The brief rejects that option because "populations differ at p = 2.2e-59." That figure
comes from `scripts/the_sim_panel_is_not_heterogeneous_2026-10-05.py`, which is a
chi-square test of homogeneity of **per-model finding counts across models**. It says
the five real models produce findings at different rates. It says nothing whatever
about whether first-pass and routed findings are drawn from different *difficulty*
populations, which is the claim the rejection needs. A design option was discarded on
a statistic that does not address it. (Separately, the same script's simulated-panel
figure, chi-square 3.0084, df 5, p = 0.6987, is the real constraint: a measured ladder
derived from a behaviourally homogeneous simulated panel is ordering noise.)

### What I propose instead, with the comparison measured

Four candidate frames, each scored on P(the exact true order is recovered), Wilson 95%
throughout, closed form and statsmodels agreeing at every figure:

`--part C`, 250 replicates, 300 findings per replicate for the routed frames:

| hardness sd | raw, deployed order | eps=0.25 randomised | common task, n=8 | common task, n=30 |
|---|---|---|---|---|
| 0.5 | 50.80% [44.64, 56.94] | **76.80%** [71.19, 81.60] | 24.00% [19.12, 29.66] | 57.20% [51.00, 63.18] |
| 1.0 | 39.60% [33.74, 45.78] | **63.20%** [57.06, 68.94] | 22.40% [17.67, 27.96] | 56.80% [50.60, 62.79] |
| 2.0 | 1.20% [0.41, 3.47] | 5.20% [3.06, 8.69] | 22.80% [18.03, 28.39] | **56.00%** [49.80, 62.02] |

A **common task** means: the same finding is dispatched to every available model, so
the population is identical by construction and no adjustment is needed at all. It
removes the selection effect rather than correcting for it, which is the simpler
sufficient construct.

**Neither frame dominates, and that is the finding.** The randomised audit fraction
buys sample size at the price of residual bias and wins at low hardness dispersion;
the common task buys zero bias at the price of sample size and is the only frame that
survives at sd = 2, where raw and eps collapse to 1.20% and 5.20%. Note the common
task's recovery rate is near-constant across dispersion (24.0 / 22.4 / 22.8 at n=8;
57.2 / 56.8 / 56.0 at n=30) — it loses only to noise, never to bias, which is the
whole point of it.

**And the composition FAILS the founder's composability bar.** I tested the obvious
composition — one logistic fit with a stratum indicator, the unbiased common-task
stratum anchoring the level and the routed stratum adding precision:

`--part D`, 250 replicates, 300 routed findings plus 8 common-task findings each:

| hardness sd | eps alone | common task alone | composed |
|---|---|---|---|
| 0.5 | 72.40% [66.55, 77.57] | 25.60% [20.59, 31.35] | **79.20%** [73.75, 83.77] |
| 1.0 | 64.80% [58.70, 70.46] | 28.00% [22.80, 33.87] | **69.20%** [63.22, 74.60] |
| 2.0 | 5.20% [3.06, 8.69] | **24.80%** [19.86, 30.51] | 5.20% [3.06, 8.69] |

At sd = 2 the single fix beats the composed one by 4.8x on disjoint intervals, because
300 routed rows swamp 40 common-task rows and one stratum shift cannot absorb a bias
that varies by rung. At sd ≤ 1 the composed advantage sits inside overlapping
intervals (79.20% [73.75, 83.77] against 72.40% [66.55, 77.57]). Founder's
rule, verbatim: *"Where a single fix out performs a composed one, that fix should
continue to be preferred."* **So: do not compose. Pick one frame on the measured
hardness dispersion of the real finding population.**

**My recommendation is the common task**, for an asymmetry of loss rather than an
average: entrenchment is the failure mode that cannot self-correct, the common task is
the only frame that degrades gracefully into it, and it is measurably deployable where
eps-greedy is not. Deployability, measured rather than assumed: 210 of 3158 archived
entries carry `resolved_by_routing`, a mean of **3.559 routed attempts per run**; at
eps = 0.25 that is 0.890 randomised attempts per run over a 5-model pool, **0.178 per
model per run — about 169 runs to reach n = 30 per model.** A common task of one
finding per round, at the archive's mean of **8.47 rounds per run** (500 rounds over 59
runs), gives 8.47 attempts per model per run: **n = 30 in roughly 4 runs.** That is the
answer to the brief's question "routing fires rarely — is it deployable?" — eps-greedy
on the routed frame is **not**, by a factor of about 40, and the fix is the sample
frame, not the value of eps.

Rejected explicitly: *keep the frozen order as decider with the rate only as a drift
alarm.* D-4 shows the frozen order is the raw confirm rate to a rank correlation of
+1.0000. Using it as the decider and the rate as the alarm is the same number
alarming on itself.

---

## 3. Removing the rung cap

**The cap should go, and almost nothing about the spend risk is where the module says
it is.** Three bounds, in order of how much work they do.

1. **The ladder is finite.** Candidates are `|pool| − |excluded|`. Exhaustion on a
   multi-model panel is bounded by the panel, so "no cap" is not "no bound." The
   module's own framing of a cap as insurance against a pathological run is therefore
   nearly vacuous *for multi-model panels* — but D-5 shows it is also wrong about the
   cost: the cap binds on 47.21% [39.65%, 54.89%] of routing events, so uncapping buys
   a rung-3 dispatch on about half of them. That is a real bill and it should be stated
   as one rather than described as nearly free.
2. **Self-routing has no finite bound at all**, and that is the case the founder
   explicitly wants. Once D-2 is repaired a sole model can be asked again and again.
   The stopping rule must therefore be a **no-progress rule**, and the right construct
   is the one the project already uses for exactly this shape: **K consecutive
   attempts with no new information**, the same pattern as the two-sided gate's K
   consecutive zero-new-critical rounds. Concretely: stop after K attempts whose
   falsifier is AST-equivalent to an earlier attempt on the same finding, or whose
   verdict is unchanged. K = 2 matches `gamma_crit_sustain_rounds`. This is not a
   budget; it is a convergence test on the attempt series, which is what the founder
   asked for ("until it is either resolved, or the ladder is exhausted").
3. **An economic stop, severity-gated.** Continue only while the expected value of the
   next attempt exceeds its expected cost: `p_hat(next) * V(finding) > c(next)`, with
   `V` the finding's severity. **severity may only open this gate when
   `severity_is_proven` holds** — the model reproduced its own `R_k` from its own
   stated inputs — exactly as the A4 fail-safe gates it. An unproven severity gets the
   floor value, never an extension. Without that gate a model could buy itself an
   unbounded budget by asserting a high severity, which is the model vote this project
   forbids.

In short: cap removed; bounded by the pool on multi-model panels, by a K-consecutive-
no-new-information rule on self-routing, and by a severity-gated economic stop
throughout. The honest accounting is that this costs about half a rung-3 dispatch per
routing event, and that it has never been executed in 59 runs.

---

## 4. Resource-aware routing — cost belongs in the ORDER, never in the ACCEPTANCE

Yes, token budget should enter, and the founder's worry that it makes "a cheap model
the default answer" is answered by *where* it enters. **Derived, not asserted.** For an
ordering of candidates with success probabilities `p_i` and per-attempt costs `c_i`,
the expected token spend to a first confirmation is

    E[cost] = sum_i  c_i * prod_{j<i} (1 - p_j)

An adjacent-transposition argument gives, for a common prefix survival probability Q:

    E[keep] - E[swap] = Q * (p_2 * c_1 - p_1 * c_2)

so with `Q > 0` and `c_i > 0`, keeping the order is strictly better exactly when
`p_1/c_1 > p_2/c_2`. No adjacent transposition improves a sequence sorted by
**decreasing p/c**, so that sequence minimises expected cost to first confirmation.
SymPy derives the identity; z3 returns **unsat** on the negation of the equivalence
(so it is a theorem over the ordered field, not a sampled regularity); brute force over
2000 random instances up to N = 6 finds the p/c order's relative excess over the true
optimum to be **0.000e+00**. Independently, Wolfram Language (local Wolfram Engine, via
`wolframscript`) simplifies the difference to `-(c2*p1) + c1*p2`, confirms
`difference - (p2*c1 - p1*c2) = 0`, and returns `{}` from
`FindInstance[... Xor[p2 c1 - p1 c2 < 0, p1/c1 > p2/c2] ...]` — no counterexample in
the constrained region. *A `Reduce[ForAll[...]]` form of the same question returned
`Reduce::nsmet` and verified nothing; that attempt is reported as unverified and
carried by z3 instead.*

**So a cheap model going first is correct, and harmless.** Trying it first costs little
by construction, and if it fails you have lost little. What protects the answer is that
cost enters only the order: **only a tool-re-verified CONFIRMED stops the ladder**, so
no ordering can make a cheap model the *answer*. Ordering and acceptance are different
decisions and only the first is a cost question. That distinction is the whole of the
reply to the founder's concern, and it is provable rather than reassuring.

**Load balancing is a membership question, not an ordering one.** A candidate is in the
feasible set only while its remaining per-model token allocation covers one expected
attempt. Order within the feasible set by decreasing `p_hat / c_hat`. That separates
the two concerns the founder raised — "enough capability, AND sufficient resources
given the opening problem set" — into the two places they belong, and it means
exhausting a model's allocation removes it from the pool rather than silently
degrading its rank.

One caveat the ratio rule does not cover: it optimises *expected* spend, not variance
or wall-clock. A pool of very cheap, very weak models will be ordered ahead of a
competent one and will usually all fail first. If latency matters, cap the number of
sub-threshold-`p_hat` candidates tried before the first above-threshold one. That is a
latency policy, not a correctness one, and it should be measured before being added —
by the additive standard, not added speculatively.

---

## 5. Reproducibility — a separate step, performed by the runner

**Separate step: yes. Whose: the runner's. Not the models', and not primarily the
human's.** A model asserting its falsifier is reproducible is a model vote, which the
founding principle forbids. A human performing the step is a bottleneck and is not a
tool. The runner already half-does it — `reverify_falsifier` re-executes
independently — so the sufficient addition is small: **execute the accepted falsifier
twice, in two distinct working directories, with a recorded seed and a pinned
interpreter and dependency set, and require identical verdicts.** A verdict that
differs between the two executions is nondeterministic by demonstration and routes to
HIL rather than CONFIRM.

This is deliberately the simplest sufficient form. It is one extra execution, it reuses
the existing decider, it is wired to the single call site after
`apply_falsifier_verdicts`, and it must be executed by a test or it is an addition
nothing reaches. Two distinct working directories, specifically, because the Exp 55
empty-working-directory defect is precisely a verdict that depended on where it ran —
a same-directory repeat would have missed it.

The human's role is to **audit the log, not to perform the step**: the pair of
verdicts, the two directories, the seed and the environment hash are recorded, and the
human reads them. For the STEM-calculator goal — problem in, definitive repeatable
answer out — reproducibility must be mechanical, because an answer that is repeatable
only when a person checks it is not repeatable.

---

## 6. What we have missed

1. **D-1 is a hard blocker on the whole brief** and reads as a detail. Until
   `falsifier_style` recognises the import form, the gate that authorises ladder
   re-derivation refuses almost every corpus, and no measured ladder can be derived.
2. **D-4 means "replace the frozen order with a measurement" is not the change it
   appears to be.** The frozen order already *is* the raw confirm rate (tau =
   +1.0000). The real change is from the raw rate to an admissibility-corrected one
   (tau = +0.2000 against the frozen tuple) — a near-total reordering, not a refresh.
3. **There are two capability representations in the repo and they disagree.**
   `DEFAULT_FALSIFIER_STRENGTH` says Codex first; `INITIAL_FINGERPRINTS` v_bar in
   `bench/runner_core.py` says CC2 first, with Codex joint-third (tau = +0.4000
   between them). `INITIAL_FINGERPRINTS` is a hand-written vendor-keyed dict. Wiring
   "the ladder to the fingerprint" using it would silently reorder the ladder *and*
   remain vendor-keyed — satisfying the ruling in appearance and violating it in fact.
4. **`burst_planner` is passed the static priors, never the live profile.** Both
   `should_burst` and `plan_phases` receive `INITIAL_FINGERPRINTS`; `observed_fingerprints`
   is never handed to either. So the live per-round profile has no consumer in burst
   planning, and the brief's premise that it is "consumed by `burst_planner.py`" holds
   only for the context-budget path. (Independently confirmed here; first found by the
   cc2 seat, 2026-10-05.) The glossary's `(D, v-bar, A, C)` describes the *static
   dataclass*, which does carry `v_bar`; the live 14-field dict does not. The two
   objects named "fingerprint" are different objects.
5. **The dedup threshold is the one place a non-falsifier decision can open the
   convergence gate.** `route()` resolves a finding as `DUPLICATE` at
   `similarity_fn >= 0.85` with `resolved=True`, and `DUPLICATE` is in
   `_NON_NOVEL_TERMINAL`, so it removes the finding from gamma's novelty series and
   from `unresolved_critical`. That is a text-similarity tool rather than a model vote,
   so it does not breach "tools decide" — but it is much weaker evidence than a
   re-executed falsifier, and it is wired to the gate. It deserves its own sensitivity
   measurement at 0.80 / 0.85 / 0.90 before the ladder is made more aggressive.
6. **A measured ladder cannot be validated in simulation as the panel stands.** The
   simulated panel is behaviourally homogeneous (chi-square 3.0084, df 5, p = 0.6987);
   the real panel is not (280.0138, df 4, p = 2.213e-59). Ordering a homogeneous pool
   is ordering noise. The ladder change is therefore gated on the seat-model map
   becoming meaningful, and that dependency should be stated in the config rather than
   discovered during a run.

---

## What this does to gamma

**gamma_critical is invariant to the rung budget. The two-sided gate is not, through
its other arm.** Derived from the code, not assumed:

`_estimate_gamma(novelty_counts)` is a Duane log-log fit of cumulative **novelty**,
i.e. NEW findings per round. Routing changes a finding's **status**, not its novelty —
with one exception: `_NON_NOVEL_TERMINAL = {MERGED, DUPLICATE, UNCONFIRMED, REFUTED}`,
so a `DUPLICATE` resolution does drop a finding out of the novelty series, and the
retroactive loop propagates that to earlier rounds. But dedup runs in `route()`
**before** the ladder and is **independent of `max_rungs`**. Therefore:

- **Removing the rung cap does not move `gamma_critical`.** It changes which criticals
  end CONFIRMED versus escalated to HIL. `CONFIRMED` is not in `_NON_NOVEL_TERMINAL`,
  so the novelty series, the Duane fit and the fitted decay are untouched.
- **The K-consecutive-zero-new-critical arm is also untouched.** Routing resolves
  existing criticals; it neither creates nor suppresses NEW ones.
- **But condition (b), the A4 fail-safe, IS affected, and in the direction of earlier
  convergence.** Line 8120: `if unresolved_critical > 0` → A4 BLOCK, and the streak
  does not accrue. Routing reduces `unresolved_critical` directly. So a ladder that
  resolves more criticals lifts the A4 block sooner and lets the quiescence streak
  start accruing sooner. **Removing the cap can open the convergence gate earlier
  without moving gamma at all** — through the count, not the curve.

That is legitimate where the resolution is a tool-re-verified CONFIRMED: a critical
that has been demonstrated is genuinely no longer unresolved. It is **not** legitimate
where the resolution is a 0.85 text-similarity `DUPLICATE`, which is item 5 above and
is the one path by which a more aggressive ladder could manufacture earlier
convergence. Recommendation: before uncapping, log `unresolved_critical` with and
without routing resolutions each round, and require the A4 block to be lifted only by
CONFIRMED resolutions — `DUPLICATE` resolutions keep the block until the finding they
duplicate is itself CONFIRMED. That is additive, one predicate, and testable.

---

## What would refute each position

| position | what refutes it |
|---|---|
| D-1 | `python3 scripts/the_provenance_gate_calls_the_import_form_detached_2026-10-06.py --falsifier-only` exiting 0. It exits 1 today. |
| D-2 | `python3 scripts/the_ladder_cannot_route_back_to_a_sole_model_2026-10-06.py` exiting 0, or `route()` on a one-model panel reporting `rungs_tried > 0`. |
| D-3 | `rank_falsifier_writers(['NewStrongModel','DeepSeek','Gemini'])` returning the unknown model anywhere but last. |
| D-4 | `--part 2` reporting Kendall tau below +1.0 for frozen-vs-raw on a corpus including Bench Run 2. Tau = +1.0000 is a property of today's archive, and the archive is partly a *consequence* of the frozen order (the selection effect in §2), so a corpus gathered under a randomised order could break it. That would weaken D-4 to "mutually reinforcing" rather than "identical". |
| §1 estimator | A corpus on which the admissibility-corrected rate orders models identically to the raw rate (tau = +1.0) would make the correction pointless. Today tau(raw, admissible) = +0.4667. |
| §1 minimum sample | `--part 3` reporting more than 8 of 55 separating pairs would widen how much of the ladder evidence can order; fewer would narrow it. Either way the number, not the rule, changes. |
| §2 inverted premise | A run in which `resolve_via_routing` tries candidates weakest-first, or `rank_falsifier_writers` returns weakest-first. Both contradict the code as read today. |
| §2 recommendation (common task) | Measure the hardness dispersion of the real finding population from `routing_history`. If it corresponds to sd < 1, eps-greedy wins on the table in §2 and I am wrong to prefer the common task. `rungs_tried = {0: 21, 1: 64, 2: 76}` is censored at the cap, so this cannot be settled until the cap is removed — which makes D-5's removal a prerequisite for validating my own §2 recommendation. |
| §2 non-composition | `--part D` with the common-task stratum UPWEIGHTED rather than counted by rows. If a weighted composition beats the common task alone at sd = 2 on disjoint intervals, the composability bar is met and I should compose. I did not test weighting; that is the gap in my own argument. |
| §4 ratio rule | A SymPy, z3 or Wolfram counterexample to `E[keep] − E[swap] = Q(p2 c1 − p1 c2)`, or a brute-force instance where the decreasing-p/c order is beaten. z3 says unsat, brute force says 0.000e+00 over 2000 instances. |
| §4 cost-in-order-only | Any code path where a verdict other than a tool-re-verified CONFIRMED terminates the ladder. `resolve_via_routing` returns `resolved=True` only on `verdict == "CONFIRMED"` from `reverify_fn`, or on a DUPLICATE match — the latter is the exception and is item 5. |
| §5 reproducibility | A measured instance where two executions in two directories with a pinned environment disagree *for a reason the pair does not reveal*, making the pair useless. The Exp 55 defect is an instance where it would have worked. |
| gamma claim | Grep for any write to `novelty_counts` or `novel_critical_history` downstream of `_apply_routing` that is conditional on `max_rungs`. I found none; one would refute the invariance claim. |

---

## Disagreement

**With the brief, on the direction of the selection effect.** The brief states the
ladder's strong models have depressed success rates "by being trusted." Measured over
the ladder's own dynamics, the rung-1 model's bias is +0.0009 / +0.0004 / −0.0002 at
hardness sd 0.5 / 1.0 / 2.0 — unbiased to three decimals — while every model below it
is biased down by up to −0.378. The ladder tries strongest-first, so the strong see the
unselected population. The hazard is entrenchment of whoever is already first, not
suppression of the strong, and the two call for different mitigations: the brief's
framing points at correcting the strong models' numerator, mine points at guaranteeing
the *lower* rungs an unselected population.

**With the brief, on the rejection of "first attempts only."** It was rejected at
p = 2.213e-59, a chi-square of per-model finding-count homogeneity. That statistic
concerns whether models find defects at different rates. It is not a test of whether
first-pass and routed findings differ in difficulty, which is the claim required.
The option may still be wrong — first-pass attempts carry their own self-selection,
since a model chooses which of its findings to falsify — but it has not been refuted,
and the figure quoted against it does not address it.

**With `routing.py`, on the cost of uncapping.** Its comment argues rungs 3+ are
reached by "a small minority" and a cap is "spend-insurance against a pathological run
rather than a routine saving." The archive says the cap binds on 47.21% [39.65%,
54.89%] of routing events. I still recommend removing the cap, but on the founder's
grounds, not on the claim that it is nearly free — it is not, and the proposal should
not carry a cost argument the data contradicts.

**With the prior proposal of 2026-10-05, on two points.** It recommends measuring
first-pass attempts only as "the cheapest and most defensible" mitigation; I measure
that frame as inadequate against entrenchment and prefer a common task. And it defines
the numerator's denominator as excluding ERROR and no-falsifier cases as "a *supply*
problem ... measured separately." I think that is wrong for this use: the ladder asks
"what happens if I ask this model," and a model that supplies nothing has answered
that question. 295 of 1373 archived entries have an empty falsifier; excluding them
flatters whoever declines most often.

**With myself, recorded rather than resolved.** My §2 recommendation depends on the
real hardness dispersion, which cannot be measured while `rungs_tried` is censored at
the cap. So the recommendation I am most confident about (remove the cap) is a
prerequisite for validating the one I am least confident about (prefer the common
task). I have not tested an upweighted composition, which is the most likely way my
non-composition conclusion is wrong.

**No disagreement on** the founding principle. Nothing in this proposal lets a model
vote decide anything: the statistic is computed by the runner from the runner's own
re-verification verdicts, severity may extend a budget only when `severity_is_proven`,
and only a tool-re-verified CONFIRMED stops the ladder.
