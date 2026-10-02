<!-- PRESERVED SEAT EVIDENCE. Written by seat 'cc2' during panel round 'falsifier_root_cause_2026-09-30', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 10902b069619d44a57e585ce872bcda225303f9533e5ef6462c45ca2002c6cf5
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited. -->
# Falsifier-supply root cause, prose targets, the round limit — one seat's verdict

**Seat:** Claude (Opus) panel seat · **Date:** 2026-09-30 · **Passes run:** 4
**Status:** design review, before implementation. Recommendations, not ratifications.

Every number below was produced by executing the project's own code in this
sandbox. Commands and verbatim output are in the panel reply that accompanies
this note. Two falsifiers were written and run:

* `scripts/falsify_prose_falsifier_supply_2026-09-30.py` — the root cause (F1)
* `scripts/falsify_e2_inherits_default_2026-09-30.py` — the constant gate (F4)

One code fix was applied: `bench/tools/commissioning_arms_2026-09-21.py`.

---

## F1 — The root cause is falsifier SUPPLY. It is none of the three names offered.

**Claim.** The recurring "no runnable falsifier" failure is not absent
capability, not absent routing, and not absent instruction-in-the-prompt. It is
an **unwired artefact**: the project already owns a proven, committed,
bidirectionally-validated prose-falsifier pattern, and it is reachable from **0**
modules on the live review path. This is fixable once, by wiring, within the
existing specification. The holes do **not** have to keep being plugged.

**Evidence, executed.**

1. **The supply works, both ways.** All 5 fixtures in
   `bench/tests/fixtures/stem/stem_fixtures.py` (29 ground-truth claims, 24 TRUE
   / 5 FALSE; planted-false 17.2414%, Wilson [7.5979%, 34.5484%]) were run
   through the project's own decider `falsifier_verify.reverify_falsifier`:
   **CONFIRMED on the pristine document, REFUTED on the corrected document,
   5/5** (Wilson [56.5518%, 100%]). That is a discriminator, not a rubber stamp —
   it distinguishes a live defect from a repaired one, which is the property a
   falsifier must have and the property `UNTOOLABLE` findings lack entirely.

2. **The supply is unreachable.** 0 of `reference_runner_v3.py`,
   `runner_core.py`, `immune_agents.py`, `bench/cdsfl_registry/`,
   `bench/directives/` mention the corpus. Its only importers are
   `bench/tools/simulated_bench.py`, 2 test files and 3 A19 scripts. The brief's
   reachability claim is **re-verified and holds**. By the project's own additive
   standard this is the 12th instance of "an addition that nothing reaches" —
   and the most expensive, because it is the one artefact that would have closed
   the gap.

3. **Routing cannot substitute for supply.** Driving the live
   `routing.resolve_via_routing` (2 rungs, ranked ladder
   `['Codex-SIM','CC2-SIM','Gemini-SIM','DeepSeek-SIM']`) with a `resolve_fn`
   that supplies nothing — today's seat, which reasons in prose and attaches
   `UNTOOLABLE` — resolved **0/5**, every rung returning `ERROR`. The same
   routing call with the corpus pattern supplied resolved **5/5**
   (Fisher exact p = 7.936508e-03).

**This is the part that attacks the brief's framing.** The brief poses teaching
and routing as rivals and cites the measurement that routing won (7/7 against
1/3). That measurement is real but it does not generalise the way the brief uses
it, because **both arms of it had supply**. Routing climbs a ladder of *writers*;
it cannot manufacture a *pattern*. My 0/5 shows routing's floor is set by supply:
with nothing to route, more rungs add cost and resolve nothing. Routing is a
**multiplier on supply, not a substitute for it** — and a multiplier on zero.

The 2026-06-07 teaching result (1/3, "a marginal booster, not a cure") is also
not evidence against wiring, because what was tested there was *teaching by
prompt* — and the brief's own `feedback_no_qualitative_escape` explains why that
decays: models do not learn across calls. The corpus is categorically different
from a prompt lesson. It is a **reusable executable artefact** with a path-binding
seam (`Fixture.falsifier(doc_path)` substitutes `<<DOC_PATH>>` at call time). A
seat does not have to *remember* it; it has to *reach* it. Wiring survives the
across-call amnesia that defeated teaching.

So the answer to Q1 is: **yes, there is a single root cause, and yes, it is
fixable once within spec.** It is supply, and the cure is wiring, not new
machinery and not a stronger model.

**Recommended fix (design, not applied — it changes what reaches a verdict).**
Three wiring steps, cheapest first:

* **W1.** Export the corpus as a seat-facing *pattern library* on the live path —
  one directive entry that hands the seat the template shape (open target by
  path → regex the claim → recompute with SymPy → cross-check with a second tool
  → `AssertionError` iff the claim stands → print `NOT FALSIFIED` and exit 0)
  plus one worked example. Wire it into `bench/directives/` so it is in the seat
  prompt on prose targets, and add a test asserting a prose-target prompt
  contains it. This is the step that makes the artefact reachable at all.
* **W2.** Make `UNTOOLABLE` cost something. Today it is a free qualitative exit,
  and the project has measured **28 of 28** `UNTOOLABLE` findings were in fact
  toolable (Wilson [87.9357%, 100%]) — a 0% true-negative rate over 28 trials.
  Require an `UNTOOLABLE` to name the specific computationally-irreducible
  element, and route it to the pattern library once before it is accepted.
* **W3.** Only then add rungs. Routing is the multiplier; apply it after supply
  exists, or it multiplies zero.

**What would refute F1.** (a) A live-path importer of the corpus I missed — my
part-2 check greps 3 named files and 2 directories, so a dynamic/late import, an
import under a different name, or reachability through a file I did not name
would refute the "0 importers" leg. (b) A seat that, given W1, still fails to
produce a runnable falsifier on a prose target at a rate indistinguishable from
today's — that would move the cause from supply to capability. (c) A measurement
showing routing alone resolves prose criticals *without* supply, which would make
supply sufficient-but-not-necessary. Note my 0/5 and 5/5 are **not** a model
measurement: `resolve_fn` was a stub I wrote, so this decides the *mechanism*
(routing cannot create supply) and not the *rate* a real seat would achieve.

---

## F2 — Prose admissibility already works as the founder framed it; the gap is that S_k gives prose nothing, so the falsifier path is the only channel.

**Claim.** The founder's original framing — admit prose that contains
computationally reducible elements, mark purely-prose inadmissible — **is
implemented and behaves correctly**. What has *not* been carried through is the
consequence: on a prose target, `S_k` is structurally incapable of resolving
anything, so the falsifier path is not one channel among several, it is the
**only** channel. That is why a supply gap halts the prose arm at round 0 while
the code arms sail through.

**Evidence, executed.** `compute_sk` over all 5 fixtures × {correct, harmful} ×
{flag off, flag on}, 20 runs:

| flag | correct fix | harmful fix | discrimination |
|---|---|---|---|
| `sk_score_prose_listings=False` | `NO_SCORE` sk=0.0000 | `NO_SCORE` sk=0.0000 | **none** |
| `sk_score_prose_listings=True`  | `ESCALATE` sk=0.0000 | `ESCALATE` sk=0.0000 | **none** |

`TARGET_KINDS = ('python_module','prose')`; all 5 docs resolve `kind=prose`
(`suffix .md`). **Ever ADMISSIBLE: NONE** — the documented veto-only property
holds, and the A19 flag never admits. With the flag on, hard gates pass
(`g0/g1/g2 = 1`, "gating 1 fenced listing(s) extracted from a non-Python
target") and **all four** effect gates report unavailable, so `E` has no evidence
and the result is `ESCALATE`. The flag changes the *label* of the non-decision
(`NO_SCORE` → `ESCALATE`), not the decision. Reading the two paths and judging
them equivalent would have missed that the harmful fix — `subprocess.call(...,
shell=True)` inside a fenced listing — passes every gate that runs.

So prose has exactly **one** resolution channel, and F1 shows that channel is
unwired. The two findings are the same failure seen from two sides, which is why
one wiring fix addresses both.

**On the natural-language-but-computable case (the founder's Wolfram question).**
The capability is measured absent from a command-line seat (0 MCP tools matching
"olfram" on 2026-09-29), so the connector route is unreachable from the seats
this project actually dispatches, whatever the policy. But the founder's worry —
that offering it only to Wolfram-installed users would confine the project to
natural-language *mathematics* rather than STEM generally — **does not follow**,
and the corpus is the proof. Its 5 documents span structural algebra,
statistics, metrology/stoichiometry, asymptotics + graph structure, and binary64
numerics; their declared `tools` tuples are `sympy/pint`, `scipy.stats/numpy`,
`stdlib(+uncertainties)`, `sympy/networkx`, `stdlib(+numpy/mpmath/sympy)`. Those
are natural-language STEM claims reduced to executable checks **with the
open-source set alone, 5/5**. The natural-language→computation step is being done
by the *model's reading* of the prose and discharged by *open-source tools*; the
connector is a convenience for that first step, not a precondition. Offering it
would be additive; withholding it costs nothing measured.

**On whether a STORED falsifier may call Wolfram** (`bench/falsifier_verify.py:596`,
`PermissionError("Wolfram refused")`). I did not take the brief's word that this
is not the founder's ruling, and I agree it should be argued on merit. **My
engineering judgement: the refusal should STAND**, on its two stated technical
grounds, which I find sufficient on their own:

1. *Re-runnability.* The refusal exists where it does because the runner
   re-executes stored falsifiers as the decider. A falsifier that needs a
   licensed kernel is not re-runnable on a machine without one, so its verdict
   becomes environment-dependent — and an unreproducible accepted result is a
   §10 category-5 material defect by this project's own definition.
2. *Serialisation.* Falsifiers are re-verified in parallel against 1 licensed
   kernel. That is a contention bug waiting to happen, and its failure mode
   (timeout → `ERROR`) is indistinguishable from a broken falsifier.

This is consistent with the founder's actual ruling rather than in tension with
it: "Wolfram… should remain the secondary falsifier ran against any output
produced from the installed Open Source tools and should never be considered the
primary falsifier route." A *stored, scored* falsifier **is** the primary route —
it is the thing that decides. Wolfram belongs where I used it in this very
review: as a second opinion on a result the open-source set already produced, in
the *authoring* seat's hands, on its own PATH. The refusal enforces exactly that
division. I record it as **engineering judgement, not as his ruling**, and note
it has never bitten (0 of 1,006 archived falsifier sources mention Wolfram), so
the cost of keeping it is zero and the cost of removing it is a class of
irreproducible verdicts.

**What would refute F2.** A configuration in which an effect gate returns a real
score on a prose target — that would give prose a second channel and weaken "the
falsifier path is the only channel". I passed `baseline=None`; the runner
supplies a baseline, and the A19 comment claims bandit reaches `e4=0.5` on 1 HIGH
with one. I did **not** reproduce that with a baseline (see *not checked*), so
the strict claim I am entitled to is: *with no baseline, prose S_k discriminates
nothing across 20 runs.* If a baselined run convicts the harmful fix, F2 weakens
to "prose S_k can veto but still cannot resolve", which leaves F1 untouched.

---

## F3 — The round limit should not be set from `n*`, because `n*` is not stable enough to set it. Recommend **10**, with the binding rule moved to novelty.

**Claim.** `n* = (a/θ)^(1/γ)` cannot support a hard-coded integer. Its
sensitivity to γ is catastrophic at exactly the γ values this project's own arms
produce, and two independent problems sit underneath it.

**Evidence, executed** (SymPy, cross-checked by mpmath and by Wolfram Language;
all three agree to every digit shown):

| γ | source | n* | dn*/dγ | a 0.05 γ error moves n* by |
|---|---|---|---|---|
| 0.7090 | March 2026 fit | 9.3805 | −29.6 | 1.48 rounds |
| 0.5301 | arm1 round 3 | 19.9681 | −112.8 | 5.64 rounds |
| 0.2143 | arm1 round 8, my fit | 1646.4943 | −56,904 | **2,845 rounds** |
| 0.1776 | arm1 final (brief) | 7607.5283 | −382,814 | **19,141 rounds** |

`n* = (a/θ)^(1/γ)` reproduces the brief's 9.3805 exactly. (The brief's 19.9645
for γ=0.5301 is slightly off; the value is **19.9681**. Minor, but it is the
number a reader would adopt.)

Two further problems, both found by executing the project's own code:

* **The law drops a factor its own estimator implies.** `_estimate_gamma`
  (`reference_runner_v3.py:3190`) fits the **cumulative** N(n) = a·n^β by OLS on
  log–log and returns γ = 1 − β. The marginal novel rate is therefore
  dN/dn = a·β·n^(−γ) = a(1−γ)·n^(−γ), so setting rate = θ gives
  **n\* = (a(1−γ)/θ)^(1/γ)**, not `(a/θ)^(1/γ)`. At a=4.89, γ=0.709 the stated
  law gives 9.3805 and the estimator-consistent one gives **1.6447** — a factor
  (1−γ)^(−1/γ) = 5.70 apart. Which is right depends on whether a=4.89 is a
  cumulative or a rate coefficient; `decay_analysis.json` carries it under
  `duane/params/alpha`, and Duane's α is conventionally cumulative, which favours
  the corrected form. **I could not settle this** (see *where I could not
  decide*), and I decline to recommend a number that depends on it.
* **The brief's two arm-1 series are mutually inconsistent under the live
  estimator.** Feeding `novel=[8,2,6,5,4,3,3,9]` to the project's own
  `_estimate_gamma` prefix-by-prefix yields
  `[0, 0, 0.4023, 0.2997, 0.2600, 0.2501, 0.2487, 0.2143]`, not the brief's
  `[0, 0, 0.5301, 0.2824, 0.1914, 0.1830, 0.1873, 0.1776]`. They agree only on
  the two structural zeros (`min_rounds=3`). So the γ history and the
  novel-per-round history in this brief did not come from the same series through
  this estimator. A recommendation derived from both jointly would be unsound.

**The datum that actually decides it.** Arm 1's novel-per-round never fell below
**2**, and its last scored round produced **9** — the rate was *rising* at the
cap. Under any θ=1 stopping rule arm 1 had **not** converged at round 8. Today
that cap is silently read as convergence; by the core directive §3 it is
**budget exhaustion carrying residual falsification debt**, which is a different
epistemic object.

**Recommendation.** Set `rounds = 10`, and move the binding decision off the cap.

* **Why 10.** It is `ceil(9.3805)` from the March fit — the only fit with enough
  data across tasks and models to be credible, and the one whose γ=0.709 sits in
  the regime where `n*` is merely *sensitive* (±1.5 rounds per 0.05 γ) rather
  than *useless* (±2,845). It is also the low end of the 9–15 band the founder
  recorded, so it is continuous with practice rather than a new arbitrary number.
* **Cost.** 8 → 10 rounds is +25% dispatch cost per arm, on the round that is
  cheapest in novel findings, and it is the *cap*, reached only when the
  novelty rule has not already stopped the run.
* **The binding rule should be novelty, not the cap.** Stop when novel-per-round
  < θ for 2 consecutive rounds (loop-until-dry, which the project already uses
  elsewhere and which the round-7 surge of 9 vindicates — a single quiet round is
  not convergence). The cap at 10 is a **budget backstop that must declare
  falsification debt**, never convergence. Had that rule been live, arm 1 would
  have hit 10 with debt declared and the surge visible, instead of an 8 that
  reads as done.
* **`n*` should be ADVISORY only**, printed from round 3 with its γ, and never a
  trigger — which is what `CDSFL_MASTER_TASK_LIST.md:171` already proposed. My
  sensitivity table is the quantitative case for why that restraint was right.

**What would refute F3.** (a) Evidence that a=4.89 is a *rate* coefficient, which
would vindicate `(a/θ)^(1/γ)` and move the March n* back to 9.38 as the
estimator-consistent value — it would not change my recommendation of 10, but it
would remove one of my two objections. (b) A γ estimator with a stability
guarantee (shrinkage, a prior, or a floor on n before γ is used), which would
make a formula-set cap defensible. (c) Arms whose novel-per-round genuinely
decays to <1 before round 8 — that would make 8 adequate and 10 waste. **My
sampling caveat:** the sensitivity table is a property of the 4 γ values I chose,
taken from the brief and from my own fit of a single 8-round arm. n=1 arm. The
operationally relevant distribution of γ across real targets is **not known to
me**, and I have not assumed one; the table is a local-derivative argument, which
is why I rest the recommendation on the March fit's regime and on the observed
non-decay, not on an averaged n*.

---

## F4 — CONFIRMED and FIXED: the prose arm's `e2_regression` was faked, not excluded.

**Claim.** `bench/tools/commissioning_arms_2026-09-21.py` sets arm 4
`test_cmd=None` and its purpose string states e2_regression is *"excluded rather
than faked"*, with the field documented *"None where the gate is unavailable by
construction rather than by choice."* **Both are false.** `Arm.argv()` guarded the
flag with a truthiness test, `None` emitted no `--test-cmd`, and argparse in
`run_simulated_experiment.py:189` substituted its own default — the immune-memory
suite tied to `bench/dm/_memory.py`, unrelated to any prose target. The gate ran
against the wrong artefact and returned the constant **52/55 =
0.9454545454545454** on all 4 scored fixes.

**Evidence, executed.** `arm4.argv()` before the fix emitted no `--test-cmd`; the
inherited default is
`python3 -m pytest bench/tests/test_immune_memory_consumption.py bench/tests/test_immune_memory_evaluation.py -q`.
`52/55 == 0.9454545454545454` exactly. Verified by execution that
`_run_effect_regression` returns `(None, 'no test command configured')` for
**both** `None` and `''`.

**Root cause, one line.** A falsy guard cannot express three states. `None`
(operator disabled it), `''` (empty), and *unset* were indistinguishable, so the
most explicit signal available — `None` — was the one silently discarded. This is
the same shape as F1: an intention recorded in a comment with nothing mechanical
carrying it.

**Fix, applied** at `bench/tools/commissioning_arms_2026-09-21.py`: guard changed
to `if self.test_cmd is not None:`, with an explicit `else` emitting
`--test-cmd ""` so the disable propagates and the gate reports UNAVAILABLE —
which is what the purpose string always claimed. Verified: arms 1–3 unchanged
(real command still emitted), arm 4 now emits `''`, module compiles, and
`bench/tests/test_prose_acceptance_stem.py` **226 passed**. The falsifier goes
**red before the fix (exit 1) and green after (exit 0)**, so it is also the
regression test.

**Note on the 3 failures the brief attributes to sandbox blinding.** With the
gate now correctly UNAVAILABLE those 3 failures should disappear *as gate
output*, because the gate no longer runs. I did not re-run the arm to confirm
that (see *not checked*) — and the deeper lesson stands regardless: a gate
reporting a constant should have been caught by variance-checking gate outputs
across fixes, which nothing does. **Recommended addition:** assert in the suite
that every *available* gate's score varies across at least 2 fixes in a scored
run; a zero-variance available gate is a defect, not a result.

**What would refute F4.** A path by which the runner overrides an empty
`--test-cmd` with a default downstream of argparse — that would make my fix
cosmetic. I checked `_run_effect_regression` directly and it honours `''`, but I
did not trace every intermediate that could re-default it.

---

## Q4 — the session's defect record, and the lesson

The mechanised layers found **7 of 13 = 53.8462%**, Wilson [29.1438%, 76.7939%].
Of the 3 defects capable of corrupting a result, CC1 found **0 of 3**, Wilson
[0%, 56.1497%] — an interval so wide it establishes almost nothing, and that is
itself the finding: **3 trials cannot measure a detection rate.** The honest
reading is not "CC1 is blind to result-corrupting defects" but "this project has
no power to tell". 4 of 9 commits refused by a guard is the healthiest number in
the set, because it is the one layer that acts *before* acceptance.

**The lesson I would carry forward, and it unifies F1 and F4.** Both defects have
the identical shape: **an intention recorded in prose with nothing mechanical
carrying it.** F1 is a working falsifier corpus whose reachability lives only in
a README. F4 is a gate exclusion whose disabling lives only in a comment and a
`None` that the next line discarded. The project's additive standard already
names this class — "every new flag, gate or entry point must be wired to a caller
and executed by a test" — and its own record (11 of 13 confirmed defects were
additions that did nothing, 0 were removals of something needed) says this is the
dominant failure mode by a wide margin. The corresponding mechanical control is
narrow and buildable: **a reachability test.** For every declared artefact
(fixture corpus, flag, gate, directive), assert a live-path caller exists and a
test executes it. That control would have caught F1 and F4 both, and it is the
one addition I would prioritise over any new detection machinery.

---

## What I did NOT check, named

* **`compute_sk` with a real baseline.** All 20 runs passed `baseline=None`, so
  `e3_ruff`/`e4_bandit` reported "baseline unavailable". The A19 comment claims
  bandit reaches `e4=0.5` on 1 HIGH when baselined. Unverified by me; it is the
  single most likely thing to qualify F2.
* **Re-running arm 4** to confirm the 3 `e2` failures disappear under the fix.
  Forbidden by the brief (no experiments, no writes to `bench/logs/`).
* **The full suite** — brief-forbidden (>8 min). I ran
  `test_prose_acceptance_stem.py` (226 passed) and targeted checks only, so a
  regression from my fix outside that file is possible though unlikely (arms 1–3
  argv verified byte-identical in behaviour).
* **Whether any of the 29 fixture claims is itself wrong.** I verified the
  falsifiers *discriminate*; I did not independently re-derive all 24 TRUE claims.
* **The other 12 defects** of the session's 13, individually. I assessed only the
  one assigned (F4) plus the aggregate statistics.
* **Live model behaviour.** I dispatched nothing. My 0/5 and 5/5 use stub
  `resolve_fn`s, so they decide a *mechanism*, never a *rate*.

## Where I could not decide

* **Whether a=4.89 is a cumulative or a rate coefficient.** This is a factor of
  5.70 on the March `n*` (9.3805 vs 1.6447) and I could not settle it from the
  repository. `decay_analysis.json` files it under `duane/params/alpha` and
  Duane's α is conventionally cumulative, which favours the corrected form — but
  the fitting code that produced 4.89 is not the `_estimate_gamma` I read, and I
  did not locate it. **This is the one question a founder ruling would resolve
  fastest**, and my round recommendation is deliberately constructed not to
  depend on it.
* **Whether the brief's arm-1 γ history came from a different estimator or a
  different series.** I established they are inconsistent; I could not determine
  which is authoritative.
* **Whether W1 (wiring the pattern library) would reach the code arms' 92%.** The
  mechanism is confirmed; the rate is not measurable without a dispatch.

## My strongest disagreement with this brief's own framing

**The brief asks for a root cause and then offers four candidate names — absent
instruction, absent routing, absent capability, or something none of these names
— but its framing of the teaching-versus-routing evidence quietly pre-selects
routing, and that inference does not survive execution.** The 2026-06-07
comparison (teaching 1/3, routing 7/7) is used as though it ranked two rival
cures. It did not: both arms had a falsifier pattern available, so it ranked two
*amplifiers* of an existing supply. Run the live routing function with supply
removed and it returns **0/5, ERROR at every rung** — routing's ceiling is set by
supply, and no number of rungs multiplies zero. Reading that measurement as
"routing beats teaching, so prefer routing" would have produced the wrong fix:
more rungs, more cost, prose still halting at round 0.

The distinction the brief lacks a word for is the one that matters. "Teaching"
failed because it was *prompt-resident* and models do not learn across calls.
Wiring the corpus is not teaching — it is making an **executable artefact
reachable**, and it is immune to the amnesia that killed teaching precisely
because the seat reaches it rather than remembers it. That is the fourth option
the brief left open, and it is the answer: **not instruction, not routing, not
capability — an unwired artefact.**

Two smaller framing objections, both re-verified: the brief's citation of `n* =
(a/θ)^(1/γ)` to "appendix line 205" is **wrong** (line 205 carries the ΔR_k
premature-stop-band material; the law lives at
`CDSFL_MASTER_TASK_LIST.md:171`, which is where the miscitation originates), and
its γ=0.5301 value of 19.9645 should read **19.9681**. Both are inherited rather
than invented — but this brief's own `feedback_rejected_advice_acquires_authority`
is about exactly how an unchecked citation hardens into a fact, and I would apply
that rule to its own arithmetic.

**Where I agree without qualification:** the brief's central statistics are sound.
I reproduced 46/50 = 92.0000% Wilson [81.1618%, 96.8450%], 0/12 Wilson [0%,
24.2494%], and Fisher **p = 8.425329e-10** exactly, under two independent
implementations (statsmodels, and a hand-coded Wilson in mpmath at 25 digits).
The diagnosis that a finding with no runnable falsifier cannot be cleared, so the
gate stays open, is correct and is the whole mechanism.
