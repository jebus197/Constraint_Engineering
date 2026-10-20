# What breaks the capability tie, if not a model's name

Record written 2026-10-19T21:20:11+01:00.

**This is the seats' own output, reproduced in full.** The Personalisation directive requires external review output preserved *"in full and in unfiltered format"* and says *"Never summarise in place of the full output"*. Any summary elsewhere is downstream of this file, not a substitute for it.

## What was asked, and why it was asked a fifth time

The founder has put this question 4 times in his own words: *"why should the schema, or capability fingerprints, or the ladder care about model names at all"*. The round was convened because the answer kept coming back as a restatement rather than a measurement. Both seats were given the live code, told to form their answer by RUNNING it, and required to deliver a fix with an executed falsifier.

Both seats answered. The round was BLIND, with no seat seeing the other's reply. cc2 returned 18,419 characters after 44 tool calls in 957.3 seconds; fable returned 12,645 characters after 37 tool calls in 850.2 seconds. Both report `ok`.

## THE SYNTHESIS, AND IT IS NOT A SPLIT DECISION

**The two seats proved different halves of the same defect, and neither half is visible from the other's vantage point.**

**fable proved the order is OUTCOME-INERT.** Under the founder's own exhaustion ruling, `resolve_via_routing` stops only on a CONFIRMED and otherwise exhausts, so the probability that the ladder resolves a finding is 1 minus the product of the per-rung failure probabilities. A product commutes. SymPy collapsed all 24 permutations of 4 symbolic rungs to **1 distinct expression**, and a local Wolfram Engine independently returned the same count of 1. Expected dispatch count is permutation-invariant too. So no permutation of the vendor tuple can change whether a finding resolves.

**cc2 proved the order is EVIDENCE-DETERMINING.** Replaying `rank_falsifier_writers` against each archived run's own roster over 285 dispatched passes: DeepSeek-SIM appeared on the ladder 214 times and was asked **0** times, Gemini-SIM 203 and **0**, Fable-SIM 84 and **0**. Three of six members were on the ladder a combined **501 times and dispatched zero times**. The order decides which seats generate the evidence that would be used to rank them, so the tuple is not merely unmeasured, it is unmeasurable while in force.

**Taken together these are complementary, not competing, and the combination is stronger than either seat stated alone.** Rotating the fallback's starting point costs nothing in resolution, which is fable's theorem, and buys the whole of the rung-1 stratum, meaning the set of findings a seat sees first rather than after another seat has failed, which is cc2's measurement. Neither seat could have reached that conclusion alone: fable's proof makes rotation free, and cc2's measurement makes it necessary.

## WHERE THEY CONVERGED, INDEPENDENTLY, AND IT IS THE STRONGEST RESULT IN THE ROUND

**B13, the unregistered model, 2 of 2, with 2 independent derivations.** Both seats concluded that the Layer-4 `FileNotFoundError` must become loud and non-fatal, and both justified it the same way without seeing each other: absence of a Layer-4 overlay IS the empty overlay, the empty overlay is monotonicity-preserving by construction, and all 6 registered Layer-4 files were measured to touch **zero** HARD keys. cc2 executed `_deep_merge(policy, {}) == policy` and got True. Both implemented the fix by reusing `capability_identity` rather than introducing a second identity function. The raise was therefore refusing a policy provably no weaker than any it admitted, and refusing it for 24 roster identities against the 6 that have files.

**The contamination trap, found twice by 2 different routes.** cc2 anticipated that a seat would propose ranking on routing-resolution outcome because that sample is 11 times larger, ran it, and showed it manufactures a ranking: 2 of 3 pairs separate marginally, **0 of 3 separate once stratified by rung**, and the surviving point-estimate order is the REVERSE of the frozen tuple. fable arrived at the same warning from provenance rather than stratification: seat-authored CONFIRM rates separate 1 of 10 pairs after Holm, Gemini over DeepSeek at Holm p = 0.0355, and that one pair is the documented detached-falsifier inversion signature, because a detached falsifier can fake CONFIRMED but not REFUTED. Two independent methods, one conclusion: the higher-powered polarity is contaminated and must pass the check in `scripts/competence_provenance.py`, which parses a seat's source to establish that its falsifier was not detached from the finding it judges, before it ever feeds `strength_order_from_evidence`.

## WHERE THEY GENUINELY DISAGREE, PRESERVED RATHER THAN SMOOTHED

**1. The value of escalation is reported as 2 different numbers, and both are measured.** cc2: 172 of 285 dispatched routing passes resolved, **60.3509%, Wilson [54.5703%, 65.8562%]**, with rung 2 adding 38 of 144, **26.3889%, Wilson [19.8715%, 34.1333%]**. fable: 230 of 272 escalations changed the finding's status, **84.5588%, Wilson [79.79%, 88.37%]**. These are not the same question. cc2 counts RESOLUTION, meaning the finding earned a CONFIRMED and the ladder stopped. fable counts STATUS CHANGE, which includes outcomes that moved a finding without resolving it. Neither figure is wrong and neither supersedes the other, and a reader who quotes one as "the value of escalation" will mislead. **The reconciliation is owed and is not yet done.**

**2. The distance to a measured ladder differs by a factor of roughly 30, and the difference is an assumption rather than an error.** cc2: between **100 and 200** rung-1 observations per seat at the realistic archive effect size of 44.9% against 58.3%, and n = 6 only if separation is perfect. fable: **4 to 6** outcomes per seat, explicitly at perfect discrimination, via a new variable. Both named their assumption. The figures are compatible once the assumption is read, but "4 to 6" quoted without "at perfect discrimination" would understate the work by 2 orders of magnitude.

**3. The 2 fixes are different mechanisms and only 1 can be first.** cc2 rotates the fallback's starting point by a hash of the experiment name, and argues exact coverage dominates coverage-in-expectation: a rotation puts each member at rung 1 exactly once over k experiments, whereas an independent shuffle leaves at least one member with no rung-1 observation after 6 experiments with probability 1 minus 6 factorial over 6 to the 6th, which is **0.9845679**, reproduced in both SciPy and Wolfram. fable records a new field, `rung_attempts`, supplying the denominator the archive has never held, and argues the urgent object is the missing denominator rather than a cleverer arbitrary order. **These compose and the ordering between them matters:** rotation without the recorder produces exposure that nothing measures, and the recorder without rotation measures a stratum that 3 of 6 members never enter.

**4. fable corrected the brief, and it was right.** The brief quoted `season_strength_order` returning "0 of 3 seat pairs" for a constructed 2-identity registry. A 2-identity registry yields 1 pair, and fable's execution returns "0 of 1 seat pairs". The quote in the brief was inexact. **That error is mine, it entered the record in a document I wrote, and it is recorded here rather than corrected silently.** It changes no conclusion. cc2 reproduced the construction's NOT ESTABLISHED verdict but did not catch the pair count, so the catch is fable's alone.

## MY OWN POSITION

I accept fable's theorem and cc2's measurement, and I do not accept either seat's framing of the priority.

**fable's claim that "the tie needs no breaking" is true of resolution and false of estimation.** The derivation is sound and the permutation check is dual-tool verified, but it answers whether order changes an OUTCOME, and the founder's question was why capability should depend on a model's name. Under fable's own proof the tuple makes no claim that reaches an outcome, which is a reason the tuple is harmless, not a reason it is acceptable: cc2's 501-appearances-against-0-dispatches figure shows the tuple silently allocates the entire evidence base. A mechanism that cannot change an outcome but fully determines what gets measured is the more dangerous of the two, because it is invisible to exactly the test fable ran.

**cc2's rotation is correct and incomplete in the mirror-image way.** Rotating exposure with no recorder for confirm-on-dispatch per rung produces the stratum and then discards it. cc2's own refutation condition names a measurement that "cannot currently be taken, which is precisely the defect" — and fable's `rung_attempts` field is the thing that makes it takeable. cc2 did not have it; fable built it.

**So the correct sequence is fable's recorder first, then cc2's rotation**, because rotation starts generating a stratum on the next experiment and a stratum with no denominator is unrecoverable after the fact. That is a claim about ordering, not about merit, and it is mine rather than either seat's.

**One item requires the founder's ruling and neither seat could settle it.** Both seats modified `bench/tests/test_policy_engine.py::test_query_with_nonexistent_model_raises`, which pinned the old contract that an unregistered model raises. Both declared the change openly and both strengthened rather than loosened the assertion. That is the correct conduct, and it is still a contract change made by the seats that proposed the behaviour it pins. Per the standing rule that fixes go to the human in the loop and are never auto-applied, it is recorded and not merged.

## TERMINATION

cc2 terminated at 7 passes, reporting that pass 7, the Wolfram second falsifier, reproduced pass 3 and 4 arithmetic to 10 significant figures and produced nothing new above the real-world-consequence threshold. fable terminated at 3 passes, reporting that pass 3, a dependant sweep over old-raise references, ladder transport tests, the `ast.literal_eval` provenance check in `scripts/competence_provenance.py`, which reads a seat's own source to confirm its falsifier is not detached from the finding it judges and a HARD-key audit of all model files, produced no new finding above threshold. Both stopped on the stated criterion rather than on a budget.

## Seats and cost

2 seat(s): `cc2`, `fable`. **0 paid dispatches**, enforced by `PANEL_ONLY=cc2,fable`.

## The brief, as dispatched

<!-- verbatim-begin: the brief as dispatched -->

# PANEL BRIEF — what breaks the capability tie, if not a model's name?

## REQUIRED SECTION 1 — The question

**When no pair of models separates on measured falsification evidence, what should decide the routing order — and what should happen when a model is not registered at all?**

This is the founder's own question, and he has put it 4 times. His words: *"why should the schema, or capability fingerprints, or the ladder care about model names at all?"* and *"the only thing that governs capability is demonstrated measured capability, not model names."* It is the common root of 3 open items on the master task list: C21 (the routing-ladder cluster), C15 (no distinction between models other than a ranking) and B13 (admitting a model is not trivial, and the cost is silent defaulting).

**The artefacts under review** are `bench/routing.py` — specifically `capability_identity`, `falsification_evidence_by_identity`, `season_strength_order`, `DEFAULT_FALSIFIER_STRENGTH` and `resolve_or_alarm` — and the policy engine at `bench/cdsfl_registry/registry.py`.

**WHAT IS ALREADY BUILT, so you argue from the current code and not from an older description.** Capability is keyed on a stable identity: a hash over provider, model identifier and version, with the vendor name carried as provenance and excluded from the hash by construction. Falsification outcomes are pooled per identity rather than per seat, which raises the sample and cuts the number of pairwise comparisons a multiplicity correction must cover. `season_strength_order` measures the order once at the start of an experiment and holds it fixed for the remaining rounds, which is his season design of 2026-10-09, and it logs whether the order it used was MEASURED or DEFAULTED.

**THE MEASURED FACT THAT MAKES THIS URGENT RATHER THAN TIDY.** Executed on 2026-10-18 against a constructed registry giving one identity 2 refutations of 2 and another 0 of 4, `season_strength_order` returned: *"0 of 3 seat pairs separate after Holm correction at alpha=0.05; a ranking is a set of pairwise orderings, so the order is NOT ESTABLISHED and no capability claim is made; falling back to the vendor order."* The same shape holds on the real archive, where the project measured **0 of 10 pairs separating** on 2026-10-17. **So the frozen tuple `('Codex', 'CC2', 'ChatGPT', 'Gemini', 'DeepSeek', 'Fable')` is the order actually in force in practice, not a rare fallback** — and it rests on a single measurement from June 2026 that has never been re-derived.

**WHY SIMPLY DELETING THE TUPLE IS NOT THE ANSWER, and both of you have previously said so.** With no data every model scores identically, and the tuple is the only ordering with a validated end-to-end result behind it. That reasoning is on the record. The founder has rejected its conclusion 4 times. **So the question is not whether to delete it but what replaces it**, and an answer of "nothing, rank uniformly" must say what the ladder then does when it is asked to escalate.

**THE SECOND HALF, B13.** An unregistered model currently reaches `load_effective_policy` and raises `FileNotFoundError`. Measured: layer 4 of the policy engine holds 6 model files while the live and simulated rosters between them carry 24 distinct identities. **My proposed fix, stated first as he requires:** a missing registration should be LOUD AND NON-FATAL — recorded against the model's stable identity and announced once, which `resolve_or_alarm` now does for 3 capability tables — rather than raising, refusing dispatch, or deferring to a preflight, which were the only 3 options previously considered. The realised cost of the silent alternative is on the record: a seat with no composer entry once composed to 0 characters and nothing reported it.

## REQUIRED SECTION 2 — Use the harness

**Form your answer by RUNNING the machinery.**

**Execute `season_strength_order`** against the real archive and against cases you construct. Report the exact `why` string it returns. If you can construct evidence on which it DOES establish an order, say how much evidence that took — that number is the answer to "how far are we from a measured ladder".

**`gamma` is the instrument that shows whether the ladder matters at all.** The ladder escalates an unresolved finding to a stronger seat; if the order is arbitrary, escalation is a random re-ask. Compute what fraction of archived escalations changed a finding's status, and report it with a confidence interval. If escalation changes nothing measurable, that is a finding about the ladder's value that outranks its ordering.

**Exercise the policy engine's monotonicity.** `load_effective_policy` must refuse a lower layer that weakens a universal HARD constraint. Demonstrate that refusal by executing it, because it is the safety property that makes arbitrary model selection admissible at all.

## REQUIRED SECTION 3 — Produce a fix, and test it

**A finding without a fix is incomplete, and a fix whose falsifier has not been EXECUTED is a hypothesis.** Deliver your fix as a file written INTO the sandbox repository tree at its real path, and report the command you ran and the output you saw.

Your fix must satisfy 3 standards explicitly, and say how it does:

1. **ADDITIVE** — nothing removed or narrowed without a committed measurement showing the replacement dominates on a named property. Retiring the frozen tuple is a removal and needs one.
2. **SIMPLEST SUFFICIENT** — if a 1-line change and a new subsystem both answer the question, the 1-line change is correct.
3. **COMPOSABILITY** — say whether your answer composes with the identity work already built, or replaces part of it. If it replaces something, name what and why.

## REQUIRED SECTION 4 — What would refute you

State what evidence would overturn your own answer. Be specific: name the number of falsification outcomes per identity at which your tie-break becomes unnecessary, or the archived escalation that your rule would have ordered wrongly.

## REQUIRED SECTION 5 — Output shape

1. `## Verdict` — what breaks the tie, and what happens to an unregistered model, 1 sentence each.
2. `## Reasoning` — premises first.
3. `## Falsifier and its executed result` — the command, and the output.
4. `## The fix` — the real path, and what it changes.
5. `## Standards` — additive, simplest sufficient, composability, addressed one by one.
6. `## What would refute this` — your refutation condition.
7. `## Disagreement` — your strongest disagreement with this brief's framing, and with the other seat if you can anticipate it. State it even if you agree with the conclusion. Deference is not evidence.

## REQUIRED SECTION 6 — Termination

Stop when a further pass produces no new findings above the real-world-consequence threshold. State how many passes you ran.


<!-- verbatim-end -->

## Seat: cc2

Route `claude_cli`, 44 recorded tool call(s).

<!-- verbatim-begin: cc2 (panel what_breaks_the_capability_tie_2026-10-18) -->

All measurements done. Writing up.

## Verdict

**The tie is broken by nothing — and that is the finding: the frozen tuple is not merely unmeasured, it is *unmeasurable while in force*, because it decides which seats generate the evidence that would be used to test it; so the fallback must rotate its starting point per experiment, which preserves the set and the cycle (making no capability claim) while making the rung-1 stratum estimable at all.** An unregistered model must be admitted on layers 1–3 with a loud, once-per-identity announcement, because absence of layer 4 *is* the empty overlay and is therefore provably the **strictest** layer-4 choice — the old `FileNotFoundError` refused a policy no weaker than the ones it admitted.

---

## Reasoning

**P1 — I reproduced the brief's measured fact, and it is worse than stated.** `season_strength_order` on the whole archive (3,020 entries, 11 seat labels pooling to 6 identities): `0 of 15 seat pairs separate after Holm correction at alpha=0.05`. The brief's constructed 2-of-2 vs 0-of-4 case likewise returns NOT ESTABLISHED.

**P2 — `season_strength_order` is ranking on the wrong quantity.** It reads `falsifier_verdict == REFUTED`: 26 events in 3,020 entries. But the ladder's own outcome is *resolution* — did the rung's falsifier earn a CONFIRMED from the re-verifier — and that is recorded in `routing_history`: **285 dispatched passes, 172 resolved**. The ladder is being ranked on a quantity it does not produce, with a sample 11× smaller than the one it does.

**P3 — escalation is highly valuable. The brief's hypothesis that it "changes nothing measurable" is REFUTED.** Of 285 dispatched routing passes, 172 resolved: **60.3509%, Wilson 95% [54.5703%, 65.8562%]**. Rung 2, reached only on rung-1 failures, resolved a further 38 of 144 (**26.3889%**, Wilson [19.8715%, 34.1333%]). The ladder's *depth* is measured and real. Its *order* is the open question.

**P4 — and here is the defect.** Ranking on the resolution quantity *unstratified* flips the function from NOT ESTABLISHED to ESTABLISHED: Codex-SIM 115/256, ChatGPT-SIM 25/54, CC2-SIM 32/119 → **2 of 3 pairs separate after Holm**. That ranking is an artefact. Stratifying by ladder position:

| seat | rung 1 | rung 2 |
|---|---|---|
| CC2-SIM | 14/24 (58.3%) | 18/95 (18.9%) |
| ChatGPT-SIM | 5/5 (100%) | 20/49 (40.8%) |
| Codex-SIM | 115/256 (44.9%) | — (never) |

Codex-SIM is *only ever* at rung 1; CC2-SIM is 95/119 at rung 2, where every finding has already defeated rung 1. In the only de-confounded stratum, **0 of 3 rung-1 pairs separate after Holm** — and the point-estimate order is `ChatGPT > CC2 > Codex`, the **reverse** of the frozen tuple's `Codex, CC2, ChatGPT`. The order determines the sample that would justify the order.

**P5 — the self-sealing is total.** Replaying `rank_falsifier_writers` against each archived run's own roster over all 285 dispatched passes:

| seat | on the ladder | actually asked |
|---|---|---|
| Codex-SIM | 256 | **256** |
| ChatGPT-SIM | 216 | 54 |
| **DeepSeek-SIM** | **214** | **0** |
| **Gemini-SIM** | **203** | **0** |
| CC2-SIM | 193 | 119 |
| **Fable-SIM** | **84** | **0** |

Three of six members were on the ladder a combined **501 times and asked zero times**; 106 passes stopped short of the ladder's end unresolved. A seat that is never asked can never earn a position. This is the `checker-that-decides-nothing` shape the project has confirmed 11 times, in its most expensive form: a ranking that cannot be refuted by the data it generates.

**P6 — how far is a measured ladder?** Executed against `season_strength_order`: under *perfect* separation, 2 seats need **n = 4** each; 6 seats (15 pairs) need **n = 6** each. At the realistic rung-1 effect size (44.9% vs 58.3%, 13.4 pp) it needs **between 100 and 200 observations per seat**. The archive's rung-1 strata are 256 / 24 / 5 / 0 / 0 / 0. So one seat is already there and five are not — the binding constraint is exposure, not volume.

**P7 — the B13 derivation.** `_deep_merge(policy, {}) == policy` → `True` (executed), and `_check_monotonicity` has already passed on layers 1–3 at the point of the raise. So absence of layer 4 is the empty overlay, which is monotonicity-preserving by construction. Measured over all 6 registered layer-4 files: **not one changes any entry** of `HARD_CONSTRAINTS`, `HARD_THRESHOLDS` or `HARD_STRINGS`. The raise therefore refused a policy provably no weaker than any it admitted — 6 files against 24 roster identities, i.e. the refusal is the common case.

---

## Falsifier and its executed result

**1 — `season_strength_order` on the real archive** (`python3` over all top-level `bench/logs/**/runner_state.json`):

```
archive entries pooled: 3020
order      : ('Codex', 'CC2', 'ChatGPT', 'Gemini', 'DeepSeek', 'Fable')
established: False
why        : 0 of 15 seat pairs separate after Holm correction at alpha=0.05; a ranking is a set
             of pairwise orderings, so the order is NOT ESTABLISHED and no capability claim is
             made; falling back to the vendor order, which rests on no measurement
             (FALSIFIER_STRENGTH_IS_ESTABLISHED is False)
```

**2 — escalation value, and the rung-stratified circularity:**

```
DISPATCHED passes (>=1 rung tried): 285   resolved: 172
  all dispatched: 172/285 = 60.3509%  Wilson95 [54.5703%, 65.8562%]
  rung 1: 134/285 = 47.0175%  Wilson95 [41.3012%, 52.8133%]
  rung 2:  38/144 = 26.3889%  Wilson95 [19.8715%, 34.1333%]

MARGINAL (confounded): 2 of 3 pairs separate after Holm
RUNG-1 ONLY (de-confounded): 0 of 3 pairs separate after Holm
  seats on the ladder but NEVER ASKED: ['DeepSeek-SIM', 'Fable-SIM', 'Gemini-SIM']
```

**3 — policy monotonicity, executed end to end against a real hostile file on disk:**

```
REFUSED: HARD constraint violation after merging layer 'model/_panel_hostile_probe':
  constraints.anti_deference: got False (type bool), required True (type bool)
  convergence.hard_coverage_threshold: got 0.8, floor is 1.0        -> REFUSED
  convergence.method: got 'compensatory', required 'non_compensatory' -> REFUSED
  constraints.anti_deference: got 1 (type int), required True (bool)  -> REFUSED
B13: load_effective_policy(model="kimi_k2") raises FileNotFoundError  [before fix]
LEMMA: deep_merge(policy, {}) == policy : True ; layers 1-3 pass monotonicity: YES
All 6 registered layer-4 files: changes-a-HARD: none
```

**4 — the fix's own test:**

```
$ python3 -m pytest bench/tests/test_what_breaks_the_capability_tie_2026-10-19.py -q
20 passed in 1.37s

$ python3 -m pytest bench/tests -q -k "routing or ladder or strength or registry or policy or
                                       objectives or unmeasured or composer or capability or identity"
1 failed, 710 passed, 2 skipped, 12090 deselected
```

The single failure is **pre-existing and environmental**, not mine: `test_guard_false_positive_figures_2026-10-02.py` shells out to `git ls-files` and this sandbox is not a git work tree (`fatal: not a git repository`). It fails identically regardless of my change.

**5 — Wolfram as second falsifier.** `FisherExactTest` is not a Wolfram symbol and returned **unevaluated — it verified nothing**. Re-derived from `HypergeometricDistribution` instead, all five p-values reproduce SciPy to 10 significant figures (*computed with Wolfram Language, local Wolfram Engine*):

```
{0.2842053751, 0.01962400370, 0.1336364785, 0.0009541590963, 0.01475322439}   (Wolfram)
{0.284205,     0.019624,      0.133636,     0.000954159,     0.0147532}       (SciPy)
1 - 6!/6^6 = 0.9845679012345679012  (Wolfram)  — the rotation-vs-shuffle constant
```

---

## The fix

**`bench/routing.py`** — adds `exposure_rotated_order(order, seed)` and a `seed=None` keyword on `season_strength_order`. In the **un-established branch only**, the vendor tuple's *starting point* is cyclically rotated by a hash of the experiment name. `seed=None` returns the tuple byte-identically, so every archived replay is intact. `why` gains a clause saying the rotation happened and that a rotation of a set is not a ranking of it. A measured order and a frozen season order are **never** rotated.

**`bench/reference_runner_v3.py`** — the single live call site now passes `seed=exp_config["experiment_name"]`. Without this the function would be an addition nothing reaches.

**`bench/cdsfl_registry/registry.py`** — the layer-4 `raise FileNotFoundError` becomes a record-and-announce: `MODEL_POLICY_MISSES` (every time) plus a `warnings.warn` **once per capability identity**, keyed on `bench.routing.capability_identity` — the same function every capability decision uses, not a second parse. Adds `reset_model_policy_misses()`.

**`bench/tests/test_what_breaks_the_capability_tie_2026-10-19.py`** — 20 executing tests, new.

**`bench/tests/test_policy_engine.py`** — `test_query_with_nonexistent_model_raises` encoded the old contract. I did **not** delete, skip or loosen it. It is renamed `..._is_loud_and_non_fatal` and now asserts *more* than before: a policy comes back, it equals the layer-3 policy **exactly**, and the miss is announced and recorded. This is the same treatment the project gave `test_every_free_seat_is_now_on_the_ladder` on 2026-10-07 — the fact moved, so the assertion moved with it, in the open.

**Why a rotation and not a shuffle.** Over *k* experiments a rotation puts each member at rung 1 **exactly** once. An independent uniform shuffle does so only in expectation: the chance all *k* firsts are distinct is `k!/k^k`, so for k = 6 the chance at least one member *still* has no rung-1 observation after 6 experiments is `1 − 6!/6⁶ = 0.9845679` (SciPy and Wolfram agree). Exact coverage dominates coverage-in-expectation on the named property, and the rotation is also the simpler mechanism.

**Honest scope limit.** `rank_falsifier_writers` matches exactly (modulo `-SIM`), and the live panel roster is `['cx','cgpt','ge','ds','cc2','fable','kimi']` — none of which matches a tuple entry. So the rotation changes behaviour **exactly where the tuple changes behaviour** (the `-SIM` panel, where all 285 archived passes occurred) and is a no-op where the tuple is already an identity function. That is a property, not an evasion, and I state it rather than letting a reader assume live reach.

---

## Standards

**ADDITIVE.** Nothing is removed or narrowed. `DEFAULT_FALSIFIER_STRENGTH` is unchanged — same 6 members, same length, same cycle; `test_the_vendor_tuple_is_not_removed_narrowed_or_reordered` asserts this, and `test_two_objectives_cannot_share_one_key_2026-10-07.py`'s `free_rungs == ["CC2","Fable"]` and `ladder_length == 6` still pass. The brief says retiring the tuple needs a committed measurement; **I do not retire it**, so no such measurement is owed. The one behaviour that *is* replaced — the layer-4 raise — carries its committed measurement: `_deep_merge(p,{}) == p`, layers 1–3 pass monotonicity, and all 6 registered files move zero HARD keys, so the admitted policy dominates the refused one on the named property *"strictness of the effective layer-4 choice"* (it is maximal) and on *"identities dispatchable"* (24 vs 6). Both are executed in the test, not judged. Every addition is wired: the rotation to `reference_runner_v3`, `MODEL_POLICY_MISSES` to the policy-engine test.

**SIMPLEST SUFFICIENT.** One pure function (12 lines of body), one keyword with a backward-compatible default, one call-site line, one `else`-branch replacement. No new subsystem, no new file in the import graph, no config key, no scheduler. I considered and rejected: (a) deleting the tuple — breaks the 2026-10-07 membership ruling, as the module records; (b) ranking on routing-resolution instead of `falsifier_verdict` — it *looks* sufficient and would even return `established=True`, but P4 shows it manufactures a ranking out of the ladder's own ordering, so it is sufficient-looking and wrong; (c) a stratified-by-rung estimator — strictly more elaborate than the problem requires *today*, because with 0 rung-1 observations for three seats there is nothing to stratify. Exposure must be fixed before estimation is worth building.

**COMPOSABILITY.** This **composes with** the identity work and replaces none of it. `season_strength_order` still pools per `capability_identity`, still prefers a measured order, still freezes a season. The rotation touches only the branch where that machinery has already returned `established=False` — i.e. it is strictly downstream and cannot mask a measured result (`test_a_measured_order_still_wins_and_is_never_rotated`, `test_a_frozen_season_order_is_never_rotated`). The B13 fix composes by *reusing* `capability_identity` rather than introducing a second identity function. And the two halves demonstrably beat either alone: rotation without B13 would rotate a seat to rung 1 that `load_effective_policy` then refuses to dispatch; B13 without rotation admits 24 identities to a ladder on which 3 of 6 members are never asked. The advantage is the measured 501-appearances/0-dispatches figure, not a judgement that both are nice to have.

---

## What would refute this

1. **The exposure claim.** If a replay of `routing_history` across the archive showed DeepSeek, Gemini or Fable with **any** non-zero dispatch count, the self-sealing argument weakens and the tuple becomes merely under-measured rather than unmeasurable. Measured: 0, 0, 0 across 285 passes. A single counter-example overturns the core premise.
2. **The threshold at which my tie-break becomes unnecessary.** At **≈200 rung-1 observations per identity** (executed: `n=100` not established, `n=200` established at the 44.9%/58.3% effect size; **n=6** if separation is perfect), `strength_order_from_evidence` returns `established=True`, `season_strength_order` never reaches the fallback, and `exposure_rotated_order` is dead code that should be removed under point-never-prune's own exception. I am asking to be made redundant, and I have named the number.
3. **An archived escalation my rule would have ordered wrongly.** The 5 passes where ChatGPT-SIM sat at rung 1 resolved 5/5. Under rotation, roughly 1/6 of those would have gone to DeepSeek-SIM or Fable-SIM first. If a measurement showed the bottom-half seats resolve at **materially below ~26%** (the rung-2 marginal), the rotation would cost resolutions that the exhaust-the-ladder budget does not recover, and the exposure gain would not pay for itself. **That measurement cannot currently be taken — which is precisely the defect.** It becomes takeable on the first rotated experiment, and if it comes back badly, this fix is the thing to revert.
4. **The B13 derivation.** If any layer-4 file were ever written that *tightens* a HARD key, omitting layer 4 would stop being the strictest choice and the fix's justification collapses. `test_the_admitted_policy_is_the_strictest_layer_four_choice` fails loudly the day that file appears. That is deliberate.

---

## Disagreement

**With the brief, on `gamma`.** The brief asserts *"if the order is arbitrary, escalation is a random re-ask"* and invites me to report that escalation changes nothing. **It is wrong, and measurably so**: escalation resolved 60.3509% [54.5703%, 65.8562%] of 285 archived passes, and rung 2 added 38 resolutions on findings rung 1 had already failed. The brief's framing conflates *order* with *depth*. They are separable and the evidence separates them: depth is measured and valuable; order is unmeasured. Had I accepted the brief's framing I would have reported a finding about "the ladder's value" that the data contradicts.

**With the brief, on the question itself.** "What breaks the tie" presupposes something should. My answer is that nothing *should* — a tie-break that asserts an order is exactly the error the founder has rejected four times — and that the real defect is one layer down: the fallback is not just a convention, it is a convention that **destroys the evidence that would replace it**. The brief frames the frozen tuple as "resting on a single measurement from June 2026 that has never been re-derived." It is stronger than that: under the current mechanics it **cannot** be re-derived, because it allocates 256 of 256 rung-1 observations to the seat it already ranks first.

**With the brief's B13 proposal, which I otherwise endorse.** The brief proposes "loud and non-fatal" and justifies it by *realised cost* (the 0-character composer). That justification is an appeal to a past accident. It is not wrong but it is not load-bearing, and on this panel's own standard — *tools decide, not votes* — an anecdote is the weakest available warrant. The fix needs the **derivation**: absence of layer 4 is the empty overlay, the empty overlay is monotonicity-preserving by construction, and all 6 registered files move zero HARD keys. The anecdote says the raise was *inconvenient*; the derivation says it was *refusing the safest policy in the lattice*. I supplied the latter and executed it.

**With the other seat, anticipated.** I expect at least one seat to propose ranking on routing-resolution outcome, because the sample is 11× larger and — I verified — it **does** return `established=True` with 2 of 3 pairs separating under Holm. I ran that and it is a trap: the separation vanishes (0 of 3) the moment you condition on rung, and the surviving point-estimate order is the *reverse* of the tuple. A seat that makes that proposal without stratifying will have produced a ranking manufactured by the ladder it is ranking. I would also expect a proposal to make the rotation a configurable policy or add a stratified estimator now; both are more surface than the problem currently requires, and this project has shipped additions nothing reached 11 times.

---

## Termination

**7 passes.** (1) read the artefacts; (2) execute `season_strength_order` on the archive and on constructed registries; (3) measure escalation value and per-model resolve rate; (4) de-confound by rung — this pass produced the two material findings, the circularity and the 501/0 exposure; (5) execute policy monotonicity, the B13 raise, and the empty-overlay lemma; (6) build the fix, write 20 executing tests, run the 711-test targeted regression; (7) Wolfram second falsifier. Pass 7 produced no new finding above the real-world-consequence threshold — it reproduced pass 3–4's arithmetic to 10 significant figures and nothing else. Stopping there.

<!-- verbatim-end -->

## Seat: fable

Route `claude_cli`, 37 recorded tool call(s).

<!-- verbatim-begin: fable (panel what_breaks_the_capability_tie_2026-10-18) -->

## Verdict

**The tie:** when no pair separates, the routing order is not a capability decision at all — under the founder's own exhaustion ruling (`max_rungs=0`), P(the ladder resolves) is provably invariant to rung order, so the tie needs determinism, not a capability claim; the measured route *out* of the tie is to record the ladder-task variable (confirm-on-dispatch per rung), which the archive has never held a denominator for and which I have now made recordable — it establishes an order from **4–6 outcomes per seat**, against **~479–808** for the refutation polarity the season machinery currently consumes.

**The unregistered model:** loud and non-fatal — `load_effective_policy` now records the Layer-4 miss against the model's stable `capability_identity` via `resolve_or_alarm`, announces once, and returns the layers-1..3 policy, which monotonicity guarantees is byte-identical on every HARD constraint; implemented and executed.

## Reasoning

**Premise 1 — order is outcome-inert under exhaustion (derived, then tool-checked).** `resolve_via_routing` stops only on a runner-decided CONFIRMED and, at `max_rungs=0`, exhausts. So P(resolve) = 1 − Π(1−pᵢ): a product commutes, so every permutation gives the same value. SymPy: all 24 permutations of 4 symbolic rungs collapse to **1 distinct expression**. Wolfram Language (local Wolfram Engine) independently returned the same count, 1. Under the exchangeability that "no pair separates" licenses, E[#dispatches] is also permutation-invariant (verified: 1 distinct value over 24 permutations), and expected *spend* is minimised by cheapest-first (rearrangement inequality; argmin over all 24 permutations = ascending cost, verified). Consequence: the frozen vendor tuple **cannot change whether a finding resolves** — only who is asked first. The founder's four-times-stated objection is to a capability claim; under exhaustion the fallback makes none that reaches an outcome, and `season_strength_order` already logs it as unestablished. The tuple is an admissible arbitrary sequence, not a ranking — and it should stay only until the right variable is measured.

**Premise 2 — the ladder has measured value, so ordering it is worth solving.** Escalation is not a random re-ask: of **272** archived escalations that actually dispatched a rung, **230 changed the finding's status** = **84.56%, Wilson 95% [79.79%, 88.37%]**. Of resolutions with a per-round record, 81 resolved at rung 1 and 23 at rung 2.

**Premise 3 — the tie exists because the instrument measures the wrong variable.** `falsification_evidence_from_registry` feeds the season **REFUTED rates of a seat's own findings**: 26 events across 3,237 entries; at archive rates (1.43% vs 0%) separation needs ~479 verdict-bearing outcomes per seat for one pair, ~808 under Holm across 15 pairs. The variable the ladder actually optimises — confirm-on-dispatch when handed another seat's finding (the Exp-42 validation was exactly this: 6/7 at rung 1) — has **successes recorded (`resolved_by_routing`, 230) but no denominator**: the archive never records which rungs were tried and failed. The distance to a measured ladder is therefore not statistical volume; it is **one missing field**. With it, the existing Fisher+Holm machinery establishes from 4 outcomes/seat (2 seats) or 6 (6 seats) at perfect discrimination.

**Premise 4 — the higher-powered polarity is contaminated exactly as documented.** Seat-authored CONFIRM rates (343 confirms, paid seats) separate **1 of 10 pairs** after Holm: **Gemini > DeepSeek (Holm p = 0.0355)** — precisely the Exp-55 detached-falsifier inversion `routing.py`'s standing warning predicts. A detached falsifier can fake CONFIRMED but not REFUTED. So ladder evidence must pass `scripts/competence_provenance.py` before it ever feeds `strength_order_from_evidence`; my reader says so and decides nothing.

**Premise 5 — B13.** Monotonicity is the property that makes non-fatal admission safe: layers 1–3 pass `_check_monotonicity` at every merge, so skipping Layer 4 cannot weaken a HARD constraint — executed, and all 6 registered model files carry only `[model]`/`[protocol]` tuning, touching **zero** HARD keys. The raise was loud but not fail-closed in practice: `composer.py:1878` calls it unguarded (the 2026-08-30 0-character incident shape), and `run_round_robin.py` catches it into a free-text warning keyed to nothing.

## Falsifier and its executed result

- `season_strength_order(real archive, 5 paid labels)` → `established=False`, order = vendor tuple, `why` verbatim: *"0 of 15 seat pairs separate after Holm correction at alpha=0.05; a ranking is a set of pairwise orderings, so the order is NOT ESTABLISHED and no capability claim is made; falling back to the vendor order, which rests on no measurement (FALSIFIER_STRENGTH_IS_ESTABLISHED is False)"* (15 pairs, not 10, because `-SIM` seats pool onto the 6 identities by construction). Constructed 2/2 vs 0/4: `established=False`, *"0 of 1 seat pairs separate…"* — note this does **not** reproduce the brief's "0 of 3 pairs" for that construction. Minimal establishing evidence: **4/4 vs 0/4** (Fisher p = 0.028571; Wolfram second check 2·PDF[HypergeometricDistribution[4,4,8],4] = 0.0285714), and **n=6 per seat** for one perfect discriminator on a 6-seat roster.
- Escalation value: `230/272 = 84.56% [79.79%, 88.37%]` (above).
- Policy engine, executed pre-fix: clean load OK; a task layer setting `falsification_required=false` → `PolicyViolationError: HARD constraint violation after merging layer 'task/panel-c-demo'`; `model="kimi_k2"` → `FileNotFoundError`.
- Post-fix: `python3 -m pytest bench/tests/test_tie_break_and_unregistered_model_2026-10-19.py -q` → **7 passed**; touched-surface regression (routing/ladder/policy/registry suites + the committed prune-inversion falsifier) → **218 run, 1 failed** — the failure being `test_query_with_nonexistent_model_raises`, the old contract itself; updated to the new contract (openly, below) → **57 passed** on re-run of the three touched suites, and the ladder-transport tests → **28 passed**.

## The fix

1. **`bench/cdsfl_registry/registry.py`** — the missing-Layer-4 branch no longer raises: it calls new `_announce_missing_registration`, which routes through `bench.routing.resolve_or_alarm` (the same recorder, same `capability_identity`, announced once per identity; `warnings.warn` fallback if `bench.routing` is unimportable — degraded detection, never silence) and continues on the monotonicity-checked layers-1..3 policy.
2. **`bench/routing.py`** — `RoutingResult.rung_attempts` (one `{"model", "verdict"}` record per rung dispatched, self-rung included), populated at every exit of `resolve_via_routing`; new reader `ladder_evidence_from_registry` pools them per capability identity into the `(confirmed, attempts)` shape the season machinery already consumes, returns `{}` on pre-field archives, and carries the provenance caveat. Recording only — no routing decision reads it.
3. **`bench/reference_runner_v3.py`** — one key added at the single `routing_history` write site, inside its existing telemetry guard, persisting `rung_attempts`.
4. **`bench/tests/test_tie_break_and_unregistered_model_2026-10-19.py`** — 7 executing tests covering both fixes and the unchanged monotonicity refusal; **`bench/tests/test_policy_engine.py`** — the one old-contract test updated (not deleted) to assert the new contract. I state this test modification explicitly: the contract it pinned is the behaviour this panel was convened to change, and the change is reported with its own executed falsifier, which is the prescribed route.

## Standards

**Additive.** Nothing capability-bearing removed: `DEFAULT_FALSIFIER_STRENGTH`, `VENDOR_ORDER_SUPERSEDED`, `FALSIFIER_STRENGTH_IS_ESTABLISHED`, the season precedence, and the `ast.literal_eval` probe's source shape are untouched (`competence_provenance` still parses, exit 0). The one narrowing is the Layer-4 raise → announcement. Named properties and committed measurements: (a) *HARD enforcement* — fallback policy byte-identical to `model=None`, every HARD boolean/threshold/string holds, executed in the test; all 6 model files measured to touch zero HARD keys, so what is skipped is tuning only; (b) *detection* — the miss now lands in `lookup_misses()` keyed to a stable identity at both live call-site families, where before one family warned free-text and one propagated into the broad handlers that produced the recorded 0-character silence. Every addition is wired and executed: `rung_attempts` is populated on every routing pass, persisted at the runner's single write site, and read by executing tests.

**Simplest sufficient.** No new subsystem: one dataclass field, one reader, one persistence line, one branch replaced. The alternative — a cost-ordered or digest-ordered replacement tuple — was considered and rejected: no committed per-identity price table exists to key it on, and Premise 1 shows any claim-free permutation is outcome-equivalent, so swapping one arbitrary order for another buys nothing measurable while risking the Exp-42-validated rung-1 latency.

**Composability.** Both fixes compose with the identity work and replace none of it: B13 reuses `resolve_or_alarm`/`capability_identity` verbatim (the fourth table on the same recorder); the ladder evidence pools through `seat_identities` and emerges in the exact shape `strength_order_from_evidence` consumes, so when the founder rules and a provenance gate exists, wiring it into `season_strength_order` is a one-argument change. The composition's demonstrated advantage over either half alone: the identity hash gave capability a stable key, but keyed tables still defaulted silently and the season still starved — recorder + key together are what make a measured ladder reachable at all.

## What would refute this

- **Order-invariance (the core of my tie verdict)** assumes rung attempts are independent of position. Once `rung_attempts` accrue, compute rung-2 confirm rate *conditional on rung-1 failure* against unconditional rung-1 rate: if they differ beyond a Holm-corrected Fisher test, P(resolve) is order-sensitive, the tie genuinely needs a capability-flavoured break, and my "the tie needs no breaking" collapses.
- **The tie-break becomes unnecessary** the moment any experiment's round 0 yields ≥4 provenance-clean ladder outcomes per seat at perfect discrimination (≥6 on a 6-seat roster) — measured above as the establishment threshold.
- **B13** is refuted by a single model TOML that tightens enforcement (touches a HARD key) such that skipping it weakens a real run — measured today as zero of six, but one committed counterexample overturns the "tuning only" premise and the raise should return for that class.

## Disagreement

**With the brief's framing, twice.** First, "what should decide the routing order" presupposes the order decides something; the derivation says that under the founder's own exhaustion ruling it decides no resolution outcome — the urgent object is not a tie-break rule but the missing denominator, and a panel that ships a cleverer arbitrary order has answered the wrong question. Second, the brief's constructed-case quote ("0 of 3 seat pairs" from a 2-identity registry) did not reproduce: my execution returns "0 of 1 seat pairs" for exactly that evidence — a 2-identity registry cannot yield 3 pairs, so either the brief's construction had more seats than stated or the quote is inexact; it changes no conclusion but should not enter the record uncorrected.

**With the other seat, anticipated.** A seat is likely to propose breaking the tie by measured cost, by identity digest, or by uniform ranking. Against all three: cost has no committed per-identity table to key on (the ledger is prose), a digest order is a lottery seeded by the very name it claims to ignore, and all three are permutations of an outcome-inert sequence — a behaviour change with measurable latency risk (Exp 42: rung 1 resolved 6/7 under the current first rung) and no measurable gain. And against a seat tempted to promote the confirm-rate evidence because it separates a pair today: the one pair it separates is the documented contamination signature, which is the strongest argument this review found for keeping *tools decide* ahead of statistical power.

---

**Termination.** Three passes: (1) artefact read + full harness execution; (2) fixes, falsifiers, regression; (3) dependant sweep (old-raise references, ladder transport tests, provenance probe, HARD-key audit of all model files) — pass 3 produced no new finding above the real-world-consequence threshold. Converged at 3.

<!-- verbatim-end -->

## Where the raw record lives

`bench/logs/what_breaks_the_capability_tie_2026-10-18/` holds the brief, every seat reply, the tool logs and `seat_proposals.diff`. That directory is excluded by `.gitignore:41`, so a byte-identical copy is committed under `experimental_notes/evidence/`, verified by sha256 and checked on every suite run by `bench/tests/test_panel_records_are_preserved_2026-09-11.py`.


Written under CDSFL note standard v1.7 (26 August 2026).
