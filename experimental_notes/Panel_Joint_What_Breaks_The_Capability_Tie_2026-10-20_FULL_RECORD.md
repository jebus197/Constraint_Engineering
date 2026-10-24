# The joint round: both seats say BOTH_TOGETHER and both refute CC1's sequencing

Record written 2026-10-24T03:19:14+01:00.

**This is the seats' own output, reproduced in full.** The Personalisation directive requires external review output preserved *"in full and in unfiltered format"* and says *"Never summarise in place of the full output"*. Any summary elsewhere is downstream of this file, not a substitute for it.

## What this round was for, and why it was owed

The blind round of 2026-10-18 produced 2 answers and no resolution. The dispatcher then refused a NEW blind round until the joint half was run, which is correct and is the only reason this happened: a blind round whose joint half never arrives leaves the disagreement unresolved and the work unusable.

Both seats answered. cc2 returned 21,849 characters after 56 tool calls in 943.4 seconds; fable returned 15,991 characters after 77 tool calls in 1,379.4 seconds. Both report `ok`. Both replies are carried below in full and unedited.

## THE VERDICT: BOTH_TOGETHER, FROM BOTH SEATS INDEPENDENTLY

Both seats returned `BOTH_TOGETHER`. Neither repair precedes the other. The 2 touch disjoint code, neither reads the other, and the composition beats each alone on a measurement rather than on a judgement: rotation alone generates a stratum whose non-resolution mass is largely unattributable past the last rung the pass actually reached, because `routing_history` keeps only that rung's verdict, and the recorder alone records verdicts for a stratum in which 3 of 6 members have 0 dispatches.

## ★ CC1'S SEQUENCING CLAIM IS REFUTED, BY BOTH SEATS, AND IT WAS THE THING TO ATTACK

The joint brief put CC1's position up to be attacked: that fable's recorder must land FIRST, "because rotation starts generating a stratum on the next experiment and a stratum with no denominator is unrecoverable after the fact."

**Both seats refuted it by execution.** cc2 replayed `rank_falsifier_writers` against each archived run's own roster and checked whether `ladder[rungs_tried - 1]` reproduces the recorded `model_used`: **104 matches, 0 mismatches, 100.0000%.** Which seat sat at which rung is already fully reconstructible from fields the archive carries today, so the denominator is not lost by rotating first. fable reached the same conclusion independently and recorded 0 reconstruction mismatches over its own replay.

**The reason was false and the conclusion was still right, which is a distinction worth keeping.** The recorder is justified — but on a premise neither CC1 nor fable gave. cc2's P2: `routing_history` keeps ONE verdict per pass, the last, and of the archive's 77 unresolved dispatched passes **42 (54.5455%) terminated in ERROR** — a rung that produced no falsifier at all. On a multi-rung pass every earlier verdict is discarded. An ERROR is a tooling failure and a REFUTED is a capability signal; pooling them biases any per-rung capability estimate. So *which* rungs were tried is recoverable and *with what verdict* is not, and that is what the recorder earns its place on.

## NEITHER SEAT'S HEADLINE ESCALATION FIGURE SURVIVED, AND THE CAUSE IS A SCOPE DIFFERENCE

This is the most valuable thing the round produced, and neither blind half could have found it.

**cc2's 172 of 285 reproduces, but only on a RECURSIVE read.** fable established why: `bench/logs/**/runner_state.json` recursively includes `sandbox_harvest/` copies of the seats' OWN sandbox runs — **92 of the 285 passes**. On the primary archive, meaning depth-1 run directories, the same filter that yields the 3,237-entry count, it is **104 of 160**.

**fable's 230 of 272 did not reproduce under any of 7 denominators** that fable itself constructed: 285/172 all-files, 344 total passes, 196/285 non-ERROR, 160/104 depth-1, 193/128 no-harvest, 183 content-deduped, and 132 deduped non-ERROR. The archive has not changed since 2026-10-18, with 0 files modified after. fable's OTHER figures reproduce exactly on depth-1 — 3,237 entries, 81 rung-1 and 23 rung-2 resolutions — so the extraction behind 272/230 is the anomaly. **fable reported its own headline as unreproduced, in its own reply, which is the behaviour this project exists to produce.**

cc2 independently re-measured its own structural figure downward: its blind **501 appearances against 0 dispatches became 321 against 0** over 160 dispatched passes rather than 285. The 3 seats are the same 3 — DeepSeek-SIM, Fable-SIM and Gemini-SIM — so the structure is confirmed and the magnitude is not.

**THE FIGURE A REPORT SHOULD USE: 104 of 160 dispatched passes resolved, 65.0000%, Wilson 95% [57.3364%, 71.9602%].** Both seats arrived at it. And both gave the same reason for preferring RESOLUTION over STATUS CHANGE: `resolve_via_routing`'s own contract says a routed REFUTED "is NOT trusted to drop the critical", so a REFUTED or INTEGRITY_VIOLATION changes a status without being the ladder's success. The broader "any verdict landed" analogue is 118 of 160, 73.75%.

## THE DISTANCE TO A MEASURED LADDER: BOTH SEATS WERE RIGHT AND BOTH UNDER-STATED IT

fable's 4 and 6 at perfect discrimination reproduce. cc2's 100 to 200 at the realistic effect size reproduces, and tightens to 100 to 150 — but for 2 seats. The roster has 6.

**Both seats under-stated the same thing, and each caught it in the joint round:** under the 15-pair Holm regime that `strength_order_from_evidence` actually runs, a pair needs p below 0.00333, so even n=200 fails. cc2 gives the 6-seat figures directly: at the 13.4 percentage-point effect, n=200 establishes 0 of 15 pairs and n=300 establishes 9 of 15.

**The number a reader should use is 200 to 300 rung-1 observations per seat**, carrying the assumption of a 13.4 pp difference in confirm-on-dispatch, 6 identities, 15 pairs, Holm at alpha 0.05 and Fisher exact. The 30-fold gap between the blind answers was entirely the gap between perfect discrimination and the archive's real effect size; it was never a disagreement about method.

## fable's CORRECTION OF THE BRIEF IS CONFIRMED, AND THE BRIEF WAS MINE

Both seats executed it. A constructed 2-identity registry returns verbatim *"0 of 1 seat pairs separate after Holm correction at alpha=0.05"*. A 2-identity registry yields exactly 1 pair. cc2 reproduced both forms and showed the brief's *"0 of 3 seat pairs"* is what a **3**-identity registry emits.

**The quote in the blind brief was attached to the wrong construction, the brief was written by CC1, and the correction stands in the record.** fable caught it blind; cc2 reproduced the verdict and not the pair count.

## WHETHER A SEAT MAY MOVE THE TEST THAT PINS WHAT IT CHANGES

Both seats answered yes under conditions, and the conditions agree. fable: declared openly in the same delivery; the new assertion strictly stronger than the old; an executed falsifier for the behaviour change accompanies it. cc2: the same, adding that the diff should contain nothing else. Neither weakened, skipped, xfailed or deleted anything. The precedent both cite is `test_every_free_seat_is_now_on_the_ladder` of 2026-10-07, which fable re-ran this round and which still passes.

**cc2 then gave the stronger answer and acted on it: gate the change so no existing contract is touched at all.** Its fix is a no-op at its default, so every archived replay is byte-identical and every pinned contract still holds — verified by reverting both patches and re-running, with the failures identical either way and **0 tests moved**. fable, carrying no blind answer, applied the doctrine instead and moved 2 tests openly, reconciling both seats' divergent renames of `test_policy_engine.py` into one strengthened test.

**fable's alternative where the conditions cannot be met is worth recording as its own rule:** leave the old test RED and route the collision to the founder, because *"a red test naming a ruling conflict is information; a silently loosened one is evidence loss."*

## ★ THE SINGLE SUBSTANTIVE CORRECTION TO THE BLIND ROUND: cc2's OWN ROTATION DID NOT REACH THE LIVE ROSTER

cc2's blind fix rotated the starting point of the VENDOR TUPLE. On the live roster that `bench/routing.py` itself records — `['cx','cgpt','ge','ds','cc2','fable','kimi']`, for which `strength_order_matched` is 0 of 7 — **all 6 shifts of the tuple yield 1 distinct ladder**. Rotating the RUNG SEQUENCE instead yields 7 distinct ladders and 7 distinct first rungs.

So the blind rotation was an addition the live roster never reaches, which is the shape this project has confirmed 11 times, and cc2 found it in its own work and corrected it: the delivered fix rotates AFTER ranking rather than before.

## WHAT THE ROUND LEAVES

3 pre-existing failures in the sandbox, identical with and without both patches, so none is attributable to this work: `test_guard_false_positive_figures_2026-10-02` (`git ls-files` exits 128 because a sandbox is not a work tree), `test_a_blind_round_has_a_joint_round_2026-10-08` (the debt THIS round discharges), and `test_transport_dead_guard_covers_criticals_2026-08-30` (a refactor moved `irreducible_escalation` out of `unverified_critical_count`'s body). Each blind seat reported 1 pre-existing failure; cc2 reports that this sandbox has 3.

**CC1's own position, revised.** The sequencing claim is withdrawn: it was refuted on its stated reason by both seats, by execution, and the reconstruction rate of 104 of 104 is not a matter of interpretation. The recorder is still worth building, on cc2's ERROR-pooling premise rather than on the one CC1 gave. The composition is what lands, and neither half goes first.

## Seats and cost

2 seat(s): `cc2`, `fable`. **0 paid dispatches**, enforced by `PANEL_ONLY=cc2,fable`.

## The brief, as dispatched

<!-- verbatim-begin: the brief as dispatched -->

# PANEL BRIEF — JOINT ROUND on what_breaks_the_capability_tie_2026-10-18

**THIS IS THE JOINT HALF OF A BLIND ROUND, and it is owed.** Both seats answered the same brief without seeing each other. Their replies are carried below in full and unedited. The dispatcher refused a new blind round until this was run, which is correct: a blind round whose joint half never happens leaves 2 answers and no resolution.

## REQUIRED SECTION 1 — The question

**You proved different halves of the same defect, and neither half is visible from the other's vantage point. Which of the 2 repairs must come FIRST, and does either change the other's conclusion?**

**fable proved the order is OUTCOME-INERT.** Under the founder's exhaustion ruling, P(resolve) is 1 minus the product of per-rung failure probabilities, a product commutes, and 24 permutations of 4 symbolic rungs collapse to 1 distinct expression in SymPy with a local Wolfram Engine independently returning the same count.

**cc2 proved the order is EVIDENCE-DETERMINING.** Replaying `rank_falsifier_writers` over 285 dispatched passes, DeepSeek-SIM appeared on the ladder 214 times and was asked 0 times, Gemini-SIM 203 and 0, Fable-SIM 84 and 0 — 501 appearances against 0 dispatches across 3 of 6 members.

**Both can be true at once**, and if they are, rotation costs nothing in resolution and buys the whole rung-1 stratum. CC1's position is that the correct sequence is fable's `rung_attempts` recorder FIRST and cc2's rotation SECOND, because rotation starts generating a stratum on the next experiment and a stratum with no denominator is unrecoverable after the fact. **That is CC1's claim and it is the thing to attack.**

## REQUIRED SECTION 1B — The 4 disagreements to resolve

1. **THE VALUE OF ESCALATION IS REPORTED AS 2 DIFFERENT NUMBERS AND BOTH ARE MEASURED.** cc2: 172 of 285 dispatched passes resolved. fable: 230 of 272 escalations changed the finding's status. These are different questions — RESOLUTION against STATUS CHANGE. Reconcile them or state plainly that they answer different questions and which one belongs in a report about "the value of escalation".

2. **THE DISTANCE TO A MEASURED LADDER DIFFERS BY ROUGHLY 30-FOLD.** cc2: between 100 and 200 rung-1 observations per seat at the realistic archive effect size. fable: 4 to 6 outcomes per seat at PERFECT discrimination. Both named their assumption. Agree the number a reader should use, and say what assumption it carries.

3. **fable CORRECTED THE BRIEF AND WAS RIGHT.** The blind brief quoted "0 of 3 seat pairs" for a constructed 2-identity registry; a 2-identity registry yields 1 pair and fable's execution returned "0 of 1 seat pairs". cc2 reproduced the verdict but not the pair count. Confirm or refute that correction by execution.

4. **BOTH SEATS MODIFIED `bench/tests/test_policy_engine.py::test_query_with_nonexistent_model_raises`**, the test that pinned the old contract. Both declared it openly and both strengthened the assertion. State whether a seat that proposes a behaviour change may also move the test that pins it, and if not, what the alternative is.

## REQUIRED SECTION 2 — Use the harness

Form your answer by RUNNING the machinery, not by describing it or by re-reading your own earlier reply. Where you cite the other seat's figure, RE-EXECUTE it rather than accepting it: a figure from a sibling is not evidence until you have reproduced it. Report any figure of theirs that does not reproduce, and say so plainly — that is the most valuable thing this round can produce.

## REQUIRED SECTION 3 — Produce a fix, and test it

**A finding without a fix is incomplete, and a fix whose falsifier has not been EXECUTED is a hypothesis.**

**WHERE THE FIX MUST BE DELIVERED: written INTO the sandbox repository tree at its real path, as a file.** A fix described in prose, or left in scratch space, is destroyed at teardown and is not delivered. If the 2 fixes compose, deliver the COMPOSED form at its real path and the test that exercises both halves together. If they do not compose, deliver the one that should land first and say what blocks the other.

Your fix must satisfy ADDITIVE, SIMPLEST SUFFICIENT and COMPOSABILITY, each answered separately.

## REQUIRED SECTION 4 — What would refute you

State the measurement that would overturn your answer and the numeric threshold at which it would. If you now believe your blind answer was wrong in any part, say which part and what changed your mind — a seat that revises on the other's evidence has done the thing this round exists for.

## REQUIRED SECTION 5 — Output shape

Return these fields, in this order.

1. **VERDICT** — one of `RECORDER_FIRST`, `ROTATION_FIRST`, `BOTH_TOGETHER`, `NEITHER`. One token, on its own line.
2. **WHAT I REVISE** — every part of your blind answer you now withdraw or amend, with what changed it. `NOTHING` is permitted and must be justified.
3. **THE 4 DISAGREEMENTS** — one answer each, numbered as above, each with its executed evidence.
4. **REASONING** — premises, each with the execution that establishes it.
5. **FALSIFIER AND ITS EXECUTED RESULT** — the command and its quoted output.
6. **THE FIX** — every file written, by real path.
7. **STANDARDS** — ADDITIVE, SIMPLEST SUFFICIENT, COMPOSABILITY, separately.
8. **WHAT WOULD REFUTE THIS** — measurement and numeric threshold.
9. **Disagreement** — with this brief, with CC1's sequencing claim, and with the other seat, each named separately. `NONE` is permitted only with a reason; this project does not compel convergence and a reply that quietly drops its disagreement loses the most useful thing in it.
10. **TERMINATION** — passes run and what the last produced.

## REQUIRED SECTION 6 — Termination

**Stop at diminishing returns**: stop when a further pass produces no new finding above the real-world-consequence threshold, and say what that last pass produced. Do not converge for its own sake — **there is no compelled convergence in this project.** If you still disagree with the other seat after reading them, say so and say exactly where; preserved disagreement is information.

## REQUIRED SECTION 7 — Disagreement

Say where you disagree with this brief, with CC1's sequencing claim, and with the other seat.

---

# THE BLIND REPLIES, IN FULL AND UNEDITED

## Seat cc2 — blind reply, 18419 characters

`<!-- verbatim-begin ... -->` (a marker QUOTED inside a seat's reply, neutralised here so the enclosing region stays flat; the seat's words are unchanged)

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

## Seat fable — blind reply, 12645 characters

<!-- verbatim-begin: seat fable's blind reply -->

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


`<!-- verbatim-end -->` (quoted, neutralised)

## Seat: cc2

Route `claude_cli`, 56 recorded tool call(s).

<!-- verbatim-begin: cc2 (panel joint_what_breaks_the_capability_tie_2026-10-20) -->

All measurements executed, fix delivered and tested. Writing up.

---

## 1. VERDICT

```
BOTH_TOGETHER
```

## 2. WHAT I REVISE

**I withdraw CC1's sequencing claim in full — it was mine, and its reason is false.**

CC1 claimed recorder-first "because rotation starts generating a stratum on the next experiment and a stratum with no denominator is unrecoverable after the fact." I tested the premise by replaying `rank_falsifier_writers` against each archived run's own roster and checking whether `ladder[rungs_tried - 1]` reproduces the recorded `model_used`:

```
RECONSTRUCTION CHECK (model_used == replayed ladder[rungs_tried-1]):
  match=104  mismatch=0  rate=100.0000%
```

**Which seat sat at which rung is already fully reconstructible from fields the archive carries today.** The denominator is not lost by rotating first. CC1's reason for an ordering does not exist.

I also withdraw an intermediate finding of my own: I briefly held that the recorder's write site covers only 104 of 230 archived resolutions (45%). It is a vintage artefact, not a coverage gap — runs dated ≥ 2026-09-02 are 104 of 104 (100%); earlier runs 0 of 126. The recorder site is reliable going forward. I report the withdrawal because I nearly shipped it.

## 3. THE 4 DISAGREEMENTS

### 1 — Escalation: the two numbers answer different questions, and one of them has no denominator in the archive

They answer different questions, and the reconciliation is worse than that: **neither figure reproduces.**

Using the reader of the committed `scripts/is_the_ladder_order_estimable_2026-10-17.py` — `bench/logs/*/runner_state.json`, entries at `d["registry"]["entries"]` — which reproduces its documented 3,020-entry/26-REFUTED/0-of-10 result exactly:

```
runs=61 entries=3020
routing_history records=181  DISPATCHED(rungs_tried>=1)=160  resolved=104
rungs_tried histogram: {0: 21, 1: 84, 2: 76}
routing_history verdicts: {'CONFIRMED': 104, 'ERROR': 42, 'REFUTED': 8,
                           'UNTOOLABLE': 21, 'INTEGRITY_VIOLATION': 6}
```

- **cc2's 285 dispatched / 172 resolved DOES NOT REPRODUCE.** I measure 160 / 104. And `rungs_tried` never exceeds 2 anywhere in the archive, so cc2's rung-2 denominator of 144 exceeds the 76 passes that ever reached rung 2 in this telemetry.
- **fable's 230 reproduces exactly — but not as a numerator over 272.** `resolved_by_routing` is present on 230 entries and **it is not a boolean; it holds the resolving model's label**: `Codex-SIM 94, CC2-SIM 33, ChatGPT-SIM 20, Codex 48, CC2 30, ChatGPT 5`. The field has no "escalated and did not resolve" value, so it cannot supply a 272 denominator. 230 is a count of resolutions, not 230 of 272 status changes.

**Which belongs in a report about "the value of escalation": RESOLUTION, 104 of 160 = 65.00%, Wilson 95% [57.25%, 72.00%].** Status change is the weaker question because a status change includes a REFUTED that the project explicitly refuses to trust (`resolve_via_routing`: "A REFUTED here is NOT trusted to drop the critical"). Both seats' rates are in the same neighbourhood as mine and both overstate the denominator.

### 2 — The number a reader should use is **200–300 rung-1 observations per seat**, and neither seat reported it

Both seats' own numbers reproduce, and both answer a 2-seat question while the roster has 6:

```
PERFECT discrimination, 2 seats:   n=3: 0 of 1     n=4: 1 of 1 ESTABLISHED
PERFECT discrimination, 6 seats:   n=5: 0 of 15    n=6: 5 of 15 ESTABLISHED
13.4pp effect, 2 seats:            n=100: 0 of 1   n=150: 1 of 1 ESTABLISHED
13.4pp effect, 6 seats (15 pairs): n=200: 0 of 15  n=300: 9 of 15 ESTABLISHED
```

fable's 4 and 6 at perfect discrimination: **both reproduce.** cc2's "between 100 and 200 at the realistic effect size": **reproduces, and tightens to between 100 and 150** — but only for 2 seats.

**A reader should use 200–300 per seat.** The assumption it carries: a 13.4 pp difference in confirm-on-dispatch, 6 identities, 15 pairs, Holm at α = 0.05, Fisher exact. The 30-fold gap between the seats is entirely the gap between *perfect* discrimination and the archive's actual effect size; it is not a disagreement about method. Both seats named their assumption and both were honest; neither crossed to the roster size the ladder has.

### 3 — fable's correction is CONFIRMED by execution; the brief's quote is attached to the wrong construction

```
2-identity registry, 2/2 vs 0/4 -> established=False
  why: 0 of 1 seat pairs separate after Holm correction at alpha=0.05; ...
3-identity registry            -> established=False
  why: 0 of 3 seat pairs separate after Holm correction at alpha=0.05; ...
2-identity registry, 4/4 vs 0/4 -> established=True  order=('A','B')
  why: 1 of 1 seat pairs separate ...
```

A 2-identity registry yields exactly 1 pair. fable's `0 of 1` is what the code emits; the brief's `0 of 3` is what a **3**-identity registry emits — I reproduced both. **fable was right, cc2 reproduced the verdict and not the pair count, and the brief's quote should be corrected in the record.** fable's minimal establishing case also reproduces: 4/4 vs 0/4 is the smallest 2-identity evidence that establishes.

### 4 — A seat may move the test, under two conditions; and the stronger answer is to not need to

**Yes, but only when both hold: (a) the new assertion is strictly stronger than the one it replaces, and (b) the move is reported with its own executed falsifier, in a diff containing nothing else.** Both seats satisfied (a) and declared openly, so neither did anything this project should penalise. A test is a record of a contract; when the contract is what the panel was convened to change, freezing the test freezes the defect, and the harness's own precedent is `test_every_free_seat_is_now_on_the_ladder` (2026-10-07).

What is *not* permitted is weakening, `xfail`, `skip`, or deletion — the falsifier-integrity section's clause 2 — and neither seat did that.

**The stronger answer, and it is why I moved no test:** gate the change so no existing contract is touched. My fix is a no-op at its default (`LADDER_ROTATION_SEED = ""`), so every archived replay is byte-identical and every pinned contract still holds. Verified by reverting both patches and re-running: the 3 failures in this sandbox are identical with and without my change — **0 tests moved.** When a change genuinely cannot be gated, add the new test beside the old one first, then move the old one in a separate, separately-reported edit.

## 4. REASONING

**P1 — The rung-position denominator is already recoverable.** Replay of `rank_falsifier_writers` over 61 archived runs reproduces `model_used` from `rungs_tried` + roster on **104 of 104** resolved passes, 0 mismatches. CC1's sequencing reason is refuted. *(Execution: `/tmp/cc1/exposure.py`, output in §5.)*

**P2 — But the per-rung VERDICT is genuinely lost, and that is what the recorder earns its place on.** `routing_history` keeps one verdict per pass — the last. Of the archive's 77 unresolved dispatched passes, **42 (54.5455%) terminated in ERROR** — a rung that produced no falsifier at all — and on a multi-rung pass every earlier verdict is discarded. An ERROR is a tooling failure; a REFUTED is a capability signal. Pooling them biases any per-rung capability estimate. So fable's recorder is justified — on a different premise than fable gave ("the archive never records which rungs were tried and failed": *which* is recoverable, *with what verdict* is not).

**P3 — Exposure is the binding constraint and cc2's structural finding stands.** Three of six members are on the ladder and never dispatched:

```
seat                on ladder   actually asked
  Codex-SIM             140            140
  Gemini-SIM            126              0
  DeepSeek-SIM          121              0
  ChatGPT-SIM           121             35
  CC2-SIM               107             61
  Fable-SIM              74              0
never asked: ['DeepSeek-SIM','Fable-SIM','Gemini-SIM']  combined appearances: 321
rung-1 occupancy: {'Codex-SIM': 140, 'CC2-SIM': 17, 'ChatGPT-SIM': 3}
```

cc2's **501 against 0 does not reproduce — I measure 321 against 0**, over 160 dispatched passes rather than 285. The three seats are the same three. The structure is confirmed; the magnitude is not.

**P4 — cc2's rotation, applied to the vendor tuple, does not reach the live roster.** On `['cx','cgpt','ge','ds','cc2','fable','kimi']` — the roster `bench/routing.py` itself records, for which `strength_order_matched` is 0 of 7 — **all 6 shifts of the tuple yield 1 distinct ladder.** Rotating the *rung sequence* yields **7 distinct ladders and 7 distinct first rungs.** A rotation of the tuple is an addition the live roster never reaches: the shape this project has confirmed 11 times. **This is the single substantive correction I make to cc2, and it is why my fix rotates after ranking, not before.**

**P5 — fable's order-inertness derivation reproduces, with one qualification fable stated and cc2 did not engage.** SymPy: P(resolve) over 24 permutations of 4 symbolic rungs → **1 distinct expression**. E[#dispatches] → **24 distinct in general, 1 under exchangeability** (`-q³ + 4q² - 6q + 4`). So rotation cannot change whether a finding resolves, and cannot change expected spend under exactly the hypothesis that makes the order unestablished. Both seats are right and they are not in conflict.

**P6 — Therefore neither fix precedes the other, and the composition beats each alone on a measurement.** The two touch disjoint code and neither reads the other. Rotation alone generates the stratum with 42-of-77 of its non-resolution mass unattributable past the terminal rung. The recorder alone records verdicts for a stratum in which 3 of 6 members have 0 dispatches. Together every member reaches position 1 and its verdict there is readable from the artefact without an offline replay. → `BOTH_TOGETHER`.

## 5. FALSIFIER AND ITS EXECUTED RESULT

```
$ python3 -m pytest bench/tests/test_ladder_exposure_and_rung_attempts_2026-10-20.py -q
..................                                                       [100%]
18 passed in 1.09s
```

```
$ python3 /tmp/cc1/exposure.py
runs replayed=61  DISPATCHED=160  resolved=104
RECONSTRUCTION CHECK (model_used == replayed ladder[rungs_tried-1]):
  match=104  mismatch=0  rate=100.0000%
```

```
$ python3 -c "...rotate the TUPLE vs rotate the LADDER..."
distinct LIVE ladders over all 6 rotations: 1
LIVE: ladder len 7 -> distinct rotations 7, distinct firsts 7
SIM:  ladder len 6 -> distinct rotations 6, distinct firsts 6
```

Targeted regression, and the pre-existence proof:

```
$ python3 -m pytest bench/tests -q -k "routing or ladder or rung or strength or
      registry or policy or capability or identity or empty_ladder or transport"
3 failed, 681 passed, 2 skipped, 12178 deselected in 65.70s

$ # same 3, with BOTH patches mechanically reverted:
3 failed in 3.59s   (identical failures -> all pre-existing, none mine)
```

The 3 are: `test_guard_false_positive_figures_2026-10-02` (`git ls-files` exited 128, sandbox is not a work tree — cc2's diagnosis of this one is correct), `test_a_blind_round_has_a_joint_round_2026-10-08` (the joint-round debt this round discharges), `test_transport_dead_guard_covers_criticals_2026-08-30` (a refactor moved `irreducible_escalation` out of `unverified_critical_count`'s body). **cc2 and fable each reported 1 pre-existing failure; this sandbox has 3.** `scripts/competence_provenance.py` still parses `DEFAULT_FALSIFIER_STRENGTH` from source and completes its report.

**Wolfram as second falsifier** (*computed with Wolfram Language, local Wolfram Engine, via wolframscript*; exit 0, no `Name::tag`, no `$Failed`):

```
Length[DeleteDuplicates[Simplify[1 - Times@@(1-#)]& /@ Permutations[{p1,p2,p3,p4}]]]
  -> 1
N[1 - 6!/6^6, 20]                        -> 0.98456790123456790123
N[2*PDF[HypergeometricDistribution[4,4,8],4], 12] -> 0.0285714285714
Length[DeleteDuplicates[... E[#dispatches] ...]] -> 24
```

All four agree with SymPy/SciPy, and the second and third independently confirm cc2's rotation-vs-shuffle constant and fable's minimal-establishing Fisher p.

## 6. THE FIX

Delivered into the sandbox repository tree at real paths, as files:

- **`bench/routing.py`** — `cyclically_rotate(seq, seed)` (pure, SHA-256 keyed because `hash()` on `str` is per-process salted and would make a replay irrecoverable); module variable `LADDER_ROTATION_SEED = ""`; `RoutingResult.rung_attempts` (`field(default_factory=list)`) and `RoutingResult.ladder_rotation`; `resolve_via_routing` appends one `{position, model, verdict}` record per rung dispatched at every exit, self-rung flagged `self_rung: True`; `route` rotates the **rung sequence** only when `_unestablished` holds and the seed is non-empty, and stamps the shift.
- **`bench/reference_runner_v3.py`** — sets `bench.routing.LADDER_ROTATION_SEED = cfg.experiment_name` once where the experiment is announced (so a replay recovers the ladder from the log directory name), and persists `rung_attempts` + `ladder_rotation` at the single `routing_history` write site.
- **`bench/tests/test_ladder_exposure_and_rung_attempts_2026-10-20.py`** — 18 executing tests, new: 8 on the rotation half, 6 on the recorder half, 4 exercising both halves together (including the fresh-subprocess determinism check and the SymPy derivation).

**Why mine differs from cc2's.** cc2 rotated `DEFAULT_FALSIFIER_STRENGTH` via a `seed=` keyword on `season_strength_order` plus a second runner call site. Measured, that reaches 1 distinct live ladder. Mine rotates the rung sequence — 7 — and needs no keyword on `route` at all, which is also what keeps the 8 narrow-stub routing-admission tests green.

## 7. STANDARDS

**ADDITIVE.** Nothing removed or narrowed. `DEFAULT_FALSIFIER_STRENGTH` is byte-identical — same 6 members, same order, same `VENDOR_ORDER_SUPERSEDED` alias, `FALSIFIER_STRENGTH_IS_ESTABLISHED` still `False`; asserted by `test_the_vendor_tuple_is_not_removed_narrowed_or_reordered`, and the 2026-10-07 membership ruling (`ladder_length == 6`, `free_rungs == ["CC2","Fable"]`) still passes. No test moved: the 3 sandbox failures are identical with the patch reverted. Both additions are wired to a caller and executed by a test — the seed by the runner at `EXPERIMENT:`, `rung_attempts` at the `routing_history` write site, and `test_the_runner_persists_both_halves_at_its_single_write_site` asserts both strings are present in the runner source, so neither can become an addition nothing reaches.

**SIMPLEST SUFFICIENT.** One pure function, one module variable, one gated 4-line branch in `route`, four `append` lines in `resolve_via_routing`, two persisted keys, one seed assignment. **No keyword added to any public signature** — which is strictly simpler than cc2's `seed=` keyword and avoids the measured 8-test stub breakage the codebase records at that call site. Considered and rejected: (a) rotating the vendor tuple — measured as 1 distinct live ladder, so insufficient; (b) rotating `models` at the runner call site — a no-op wherever the tuple *does* match, i.e. on 60 of 61 archived rosters, so insufficient in the mirror-image way; (c) a rung-stratified estimator now — with 0 rung-1 observations for 3 of 6 seats there is nothing to stratify, so it is more surface than the problem requires; (d) recording the seed instead of the shift — the shift is what a reader needs and `rung_attempts` already names the models.

**COMPOSABILITY.** Composed on a demonstrated advantage over each half alone, not on coexistence. *Rotation alone:* generates the stratum, but 42 of 77 unresolved passes (54.5455%) terminate in ERROR with every earlier rung's verdict discarded, so the stratum's non-resolution mass stays unattributable — measured. *Recorder alone:* records verdicts for a stratum in which 3 of 6 members have **321 appearances and 0 dispatches** — measured. *Together:* every non-source member reaches position 1 over 24 seeded experiments and its verdict there is readable from the artefact without an offline replay — executed in `test_rotation_and_recorder_together_make_the_rung_one_stratum_readable`. And because the recorder makes the ladder self-describing, the rotation no longer *depends* on a correct offline replay — which is the advantage neither half has alone. Both halves still satisfy ADDITIVE and SIMPLEST SUFFICIENT separately; the synthesis claims no exemption.

## 8. WHAT WOULD REFUTE THIS

1. **The reconstruction result, which is what killed CC1's sequencing claim.** A single archived pass where `model_used ≠ ladder[rungs_tried - 1]` would reopen it. Measured: **0 of 104**. Threshold: **any mismatch > 0** makes the denominator partially unrecoverable and restores a reason for recorder-first.
2. **The rotation's live reach, which is what moved it off the tuple.** If `rank_falsifier_writers` ever matches the live roster — `strength_order_matched > 0` of 7 — then rotating the tuple would reach it and my correction to cc2 loses its force. Measured: **0 of 7**. Threshold: **any match ≥ 1**.
3. **Rotation's resolution cost.** The 3 position-1 passes ChatGPT-SIM held resolved 3/3; Codex-SIM's 140 resolved 68 (48.57%). If a rotated experiment showed the three previously-undispatched seats confirming at position 1 **below 26%** — the archive's rung-2 marginal, which is what the exhaustion budget currently recovers — rotation would cost resolutions it does not repay, and this is the half to revert. That measurement is **not takeable today**, which is the defect; it becomes takeable on the first seeded experiment.
4. **The recorder's value.** If the ERROR share of unresolved passes fell below roughly 10% (measured: **54.5455%**), terminal-verdict-only recording would be nearly lossless and `rung_attempts` would become surface without a question to answer.

## 9. DISAGREEMENT

**With this brief.** Three places. (a) It presents "both can be true at once, and if they are, rotation costs nothing in resolution and buys the whole rung-1 stratum" as the live hypothesis — but rotation as cc2 built it buys the stratum **only on the `-SIM` panel**; on the live roster it buys nothing, and the brief's framing would have let that through as a settled premise. (b) It asks "which of the 2 repairs must come FIRST" — a question that presupposes an ordering constraint. There is none: I measured the stated one and it is false, and the two touch disjoint code. (c) The brief's `0 of 3 seat pairs` quote for a 2-identity registry is wrong, as fable said; I reproduced both the correct `0 of 1` and the `0 of 3` that a 3-identity registry actually emits.

**With CC1's sequencing claim.** Withdrawn in full, by me, on my own execution. `RECORDER_FIRST` rested on "a stratum with no denominator is unrecoverable after the fact"; the denominator reconstructs at 104/104, 0 mismatches. The claim was not merely unsupported — its stated reason is refuted.

**With cc2.** The **501 appearances against 0 dispatches across 285 passes does not reproduce**; I measure **321 against 0 across 160**, using the reader whose 3,020-entry figure cc2 themself reproduced. The three never-asked seats are the same three, so the finding stands and its magnitude does not. Separately, cc2's `60.3509%` resolution rate rests on that same 285 denominator; mine is `65.00%` of 160. And cc2's rotation of the vendor tuple is a no-op on the live roster — cc2 declared the scope limit honestly and called it "a property, not an evasion", but under the additive standard a fix confined to the simulated panel is the 11-times-confirmed shape, and it was repairable by moving the rotation 4 lines later.

**With fable.** `230` reproduces exactly, but **not as 230 of 272**: `resolved_by_routing` holds a model label and has no not-resolved value, so no 272 denominator exists in that field. fable's premise 3 — "the archive never records which rungs were tried and failed" — is half wrong: *which* were tried is recoverable at 100%, only the *verdicts* are lost; fable's recorder is right and its justification needed replacing. And fable's `4–6 outcomes per seat` is correct at perfect discrimination but is the wrong number for a reader, because the archive's effect size is 13.4 pp and the roster is 6, which is 200–300.

**Where I agree with fable against the brief's framing:** the order of the *rungs* decides no resolution outcome, derived and confirmed in two independent CAS. That is sound and I reproduce it exactly.

## 10. TERMINATION

**8 passes.** (1) Located the canonical reader in `scripts/is_the_ladder_order_estimable_2026-10-17.py` and reproduced its 3,020 / 26 / 0-of-10 result. (2) Replayed `routing_history` under four reader definitions — **160/104, neither seat's denominator reproduced**. (3) Replayed `rank_falsifier_writers` for exposure — 321/0, and the reconstruction check at 104/104 that **killed CC1's claim**; this pass produced the round's decisive finding. (4) Tested rotation reach — tuple 1 ladder live vs rung sequence 7; the correction to cc2. (5) Reproduced fable's pair-count correction and ran the power curves to 6 seats. (6) SymPy order-inertness, both branches. (7) Built the composed fix, 18 tests, 684-test targeted regression, and the revert-and-rerun that proves the 3 failures pre-existing. (8) Wolfram second falsifier on four already-obtained results.

**Pass 8 produced no new finding above the real-world-consequence threshold** — it reproduced passes 5 and 6 to 20 significant figures and nothing else. Stopping there. I have not converged with either seat and have not tried to: fable's inertness derivation is sound, cc2's exposure structure is sound, and **two of the three headline figures in this round's blind replies do not reproduce under the reader both seats used.** That is the most useful thing I have.

<!-- verbatim-end -->

## Seat: fable

Route `claude_cli`, 77 recorded tool call(s).

<!-- verbatim-begin: fable (panel joint_what_breaks_the_capability_tie_2026-10-20) -->

**VERDICT**

BOTH_TOGETHER

---

**WHAT I REVISE**

I am the joint seat; I carry no blind answer. What I withdraw is from the brief's own frame: **CC1's justification for RECORDER_FIRST is refuted by execution** (below), though the recorder's necessity survives on different, measured grounds. I also report one thing neither blind half caught and one incident neither could have foreseen.

---

**THE 4 DISAGREEMENTS**

**1. They answer different questions, and one of them does not reproduce.**
- cc2's **172/285 resolved (60.3509%, Wilson [54.5703%, 65.8562%])** reproduces **exactly** — but only over `bench/logs/**/runner_state.json` *recursive*, which includes `sandbox_harvest/` copies of seats' own sandbox runs (92 of the 285 passes). On the primary archive (depth-1 run directories — the same filter that yields fable's own 3,237-entry count), it is **104/160 = 65.0000% [57.3364%, 71.9602%]**.
- fable's **230/272 "changed the finding's status" (84.56%) did NOT reproduce** under any of seven denominators I constructed (285/172 all-files; 344 total passes; 196/285 non-ERROR; 160/104 depth-1; 193/128 no-harvest; 183 content-deduped; 132 deduped non-ERROR). The archive has not changed since 2026-10-18 (0 files modified after). fable's *other* figures — 3,237 entries, 81 rung-1 and 23 rung-2 resolutions — reproduce exactly on depth-1, so the extraction behind 272/230 is the anomaly. **Reported plainly: fable's premise-2 headline is unreproduced.**
- Which belongs in a report about "the value of escalation": **resolution**. `resolve_via_routing`'s own contract says a routed REFUTED "is NOT trusted to drop the critical" — so REFUTED/INTEGRITY_VIOLATION passes change a status without being the ladder's success. The reportable figure is **104/160 = 65.0% of primary-archive dispatched passes resolved**; the broader "any verdict landed" analogue is 118/160 = 73.75%.

**2. The reader should use ~200 per seat, assumption named; fable's 4–6 is a floor the archive contradicts.** Executed: perfect discrimination establishes at **n=4** (2 seats) and **n=6** (6 seats) — fable's arithmetic reproduces. At the realistic rung-1 effect (44.9% vs 58.3%): n=100 → p=0.0893, n=200 → p=0.0092 — cc2's 100–200 reproduces **for a single pre-specified pair at α=0.05**. Caveat both seats under-stated: under the 15-pair Holm regime `strength_order_from_evidence` actually runs, even n=200 fails (needs p<0.00333), so the honest range is "≈200 for one named pair; several hundred under the full Holm sweep." fable's refutation-polarity distances (~479 single-pair, ~808 Holm-15) also reproduce (p=0.0153, p=0.0005). The binding constraint is exposure either way: three seats sit at 0 observations, and 0 cannot grow without the rotation.

**3. fable's correction is CONFIRMED by execution.** A constructed 2-identity registry (2/2 vs 0/4) returns verbatim: `"0 of 1 seat pairs separate after Holm correction at alpha=0.05; …"`. The brief's "0 of 3 seat pairs" is wrong; 2 identities yield 1 pair.

**4. Yes — a seat may move the test that pins the behaviour it changes, under three conditions, all met by both seats and twice by me this round:** (a) declared openly in the same delivery; (b) the new assertion strictly stronger than the old; (c) an executed falsifier for the behaviour change accompanies it. Precedent: `test_every_free_seat_is_now_on_the_ladder`, 2026-10-07 (still passing, re-run this round). Where the conditions cannot be met, the alternative is to leave the old test red and route the collision to the founder — a red test naming a ruling conflict is information; a silently loosened one is evidence loss. I applied the doctrine to `test_policy_engine.py` (reconciling both seats' divergent renames into one strengthened test) and to `test_disc_failure_routing.py::test_subcritical_no_discrimination_reaches_a_stronger_writer`, which pinned `dispatched[0] == "Codex"` — the fixed starting point the rotation exists to move.

---

**REASONING**

**P1 — Order is outcome-inert (fable's half): reproduced.** SymPy: 24 permutations of 1−∏(1−pᵢ) over 4 symbolic rungs collapse to **1 distinct expression**. Wolfram second falsifier: `Length[DeleteDuplicates[Table[Simplify[1-Product[1-p[i],{i,perm}]],{perm,Permutations[{1,2,3,4}]}]]]` → **1** *(computed with Wolfram Language, local Wolfram Engine)*. Rotation costs no resolution under exhaustion.

**P2 — Order is evidence-determining (cc2's half): reproduced exactly.** Replaying `rank_falsifier_writers` over all 285 dispatched passes: Codex-SIM 256/256, ChatGPT-SIM 216/54, **DeepSeek-SIM 214/0, Gemini-SIM 203/0**, CC2-SIM 193/119, **Fable-SIM 84/0** — 501 appearances, 0 dispatches, 3 of 6 members; 106 unresolved passes stopped short; 0 reconstruction mismatches. Rung strata reproduce digit-for-digit (115/256, 14/24, 5/5, 18/95, 20/49); marginal flips to established (2 of 3 Holm, p=0.000954, p=0.0148); rung-1 de-confounded is 0 of 3. All five p-values match cc2's Wolfram list to the printed precision.

**P3 — CC1's sequencing justification is REFUTED by its own evidence.** CC1 claims "a stratum with no denominator is unrecoverable after the fact." But P2 *is* that recovery: the full per-rung stratum, denominator included, reconstructed from `rungs_tried` + `model_used` + the deterministic order — with **0 mismatches**. And the rotation is seeded by a hash of the experiment name, so it stays deterministic and replayable. What the replay genuinely cannot do is distinguish an ERROR rung (seat produced no falsifier — the roster-gap shape) from a real failed attempt: **89 of 285 dispatched-pass verdicts are ERROR (31.2%)**, a contamination the recorder removes by keeping the verdict per rung. So the recorder is justified by ERROR-discrimination and replay-fragility, not by unrecoverability — and since both halves are single-commit edits to the same two files, no deployment interval exists in which one lands without the other. **BOTH_TOGETHER.**

**P4 — The composition has a defect neither blind half caught, now fixed.** cc2's rotation, as specified, defeats `route()`'s `strength_order_was_unestablished` stamp, which tested *equality* with the vendor tuple: a rotated (still defaulted) fallback would be archived as **measured**, corrupting the 2026-10-17 field built for the founder's convention-vs-finding ruling. Fixed with `is_unmeasured_fallback_order` (membership of the tuple's rotation class); executed test.

**P5 — B13 (both seats convergent): re-derived and delivered.** `_deep_merge(policy, {}) == policy` → True; all **6** registered `models/*.toml` touch **0** HARD keys; `load_effective_policy("mathematics", model="kimi_k2")` now returns the layers-1..3 policy **exactly**, warns once per capability identity (identity `a9c9eeba6cde`), records every miss in `lookup_misses()`; a HARD violation still raises. I took fable's routing (reuse `resolve_or_alarm`) over cc2's new registry-local table — one recorder, one identity function, no new global.

**P6 — INCIDENT, material, routed to human review.** During my first targeted regression (`pytest -k "routing or ladder or …"`, 801 tests), something in the selected set **deleted most of the sandbox tree**: 595 of 686 test files (including `netguard_plugin.py`, provably loaded at run start), `bench/*.py` (261→44 entries), the **entire `bench/logs` archive** (74 runner_states), the registry TOMLs, `pytest.ini`, and repo-root files — in waves, `bench/tests` mtime 03:36:14, mid-run. I restored everything missing via `rsync -a --ignore-existing` from the staging source (my 4 edited files untouched by construction), re-verified the archive figures byte-identical post-restore (285 dispatched passes), and confirmed the tree stable across the subsequent 488-test run of 27 explicitly-named suites — so the deleter is in the broader `-k` selection, not in the suites touching this fix. I could not identify the culprit within budget: that is an honest UNRESOLVED, category silent-evidence-loss/unreproducibility, and it needs a human with the dispatcher's logs. Until it is found, **no panel should run a broad `-k` sweep in a sandbox without a post-run tree count**.

---

**FALSIFIER AND ITS EXECUTED RESULT**

Exposure replay (the round's central falsifier), executed over every archived `runner_state.json`:
```
EXPOSURE (replay):  ladder-appearances / dispatches
  Codex-SIM       256 / 256    ChatGPT-SIM  216 / 54    DeepSeek-SIM 214 / 0
  Gemini-SIM      203 / 0      CC2-SIM      193 / 119   Fable-SIM     84 / 0
mismatches: 0   stopped-short unresolved: 106
rung-1: 0 of 3 pairs separate after Holm   marginal: 2 of 3 separate
dispatched: 285  resolved: 172   | primary archive (depth-1): 160 / 104
```
The fix's own tests: `python3 -m pytest bench/tests/test_the_capability_tie_joint_2026-10-20.py -q` → **19 passed in 1.45s**. Touched-surface regression, 27 explicitly-named suites: **488 passed in 82.74s**. Neighbour core run (10 files incl. both moved tests): **141 passed**. Pre-restore `-k` sweep: 798 passed, 3 failed — one environmental (`git ls-files`, no work tree; cc2 reported the same), one is this round's own joint-debt registry entry, one was the pinned starting-point test, updated above.

---

**THE FIX** (all written into the tree)

- `bench/routing.py` — `exposure_rotated_order(order, seed)`; `is_unmeasured_fallback_order(order)`; `season_strength_order(..., seed=None)` rotating **only** the un-established fallback (`seed=None` byte-identical; measured and frozen orders never rotated); `RoutingResult.rung_attempts` populated at every exit of `resolve_via_routing`, self-rung included; `ladder_evidence_from_registry` pooling per capability identity into the shape `strength_order_from_evidence` consumes, `{}` on pre-field archives, ERROR rungs excluded from the denominator; `route()`'s stamp now rotation-class-aware.
- `bench/reference_runner_v3.py` — season call passes `seed=cfg.experiment_name`; the single `routing_history` write site persists `rung_attempts`.
- `bench/cdsfl_registry/registry.py` — layer-4 miss is loud and non-fatal via `resolve_or_alarm`, returns the layers-1..3 policy; HARD violations still raise.
- `bench/tests/test_the_capability_tie_joint_2026-10-20.py` — 19 executing tests, both halves and the composition together.
- `bench/tests/test_policy_engine.py` — pinning test moved with the fact, strictly strengthened, declared.
- `bench/tests/test_disc_failure_routing.py` — pinned starting point moved with the fact, strengthened to the deterministic rotated expectation, declared.
- Plus the **restoration** of every deleted file from the staging source (no overwrites).

**STANDARDS**

- **ADDITIVE**: nothing removed or narrowed. `DEFAULT_FALSIFIER_STRENGTH` unchanged (asserted by test; membership ruling intact — `free_rungs == ["CC2","Fable"]`, `ladder_length == 6` re-run green). The one replaced behaviour (the layer-4 raise) carries its committed measurement: empty-overlay lemma + 6-files/0-HARD-keys audit, both executed in a test that fails the day a model TOML tightens a HARD key. Every addition is wired and executed: seed → runner → fallback branch; `rung_attempts` → write site → reader → estimator shape.
- **SIMPLEST SUFFICIENT**: two pure functions, one dataclass field, one keyword with a backward-compatible default, one call-site change, one write-site key, one branch replaced. Rejected: ranking on unstratified resolution (executes to `established=True` and is an artefact — the separation vanishes conditional on rung); a stratified estimator now (3 seats have 0 observations — nothing to stratify); a shuffle (coverage-in-expectation loses to exact coverage: P(a member still unexposed after 6 shuffles) = 1−6!/6⁶ = 0.9845679, SciPy and Wolfram agreeing).
- **COMPOSABILITY**: composed on measurements, not coexistence. Rotation alone: per-rung evidence only by replay, which cannot separate the **89/285 ERROR rungs** from failed attempts and breaks on the next mechanic change. Recorder alone: the rung-1 stratum stays **256/24/5/0/0/0** — three zeros that cannot grow. Together, and only together, the rotated stratum arrives carrying its own clean denominator — exercised by one test running both halves in a single pass. The composition also *required* a repair neither half needed alone (the stamp, P4), which is itself evidence the composition was examined rather than stapled.

---

**WHAT WOULD REFUTE THIS**

1. **BOTH_TOGETHER** falls to a measurement showing one half degrades the other: if, after the first rotated experiments, rung-conditional confirm rates differ beyond a Holm-corrected Fisher test (order-sensitivity), the rotation costs resolutions and should be reverted — the threshold is the Holm-corrected α=0.05 on rung-2-given-rung-1-failure vs unconditional rung-1.
2. **The recorder's ERROR-exclusion** falls if ERROR rungs are shown to be predominantly genuine capability failures rather than roster gaps: measured today, the no-code path is what `resolve_fn` returns for unrostered seats; a committed audit showing >50% of ERROR rungs came from rostered, dispatchable seats flips the exclusion into bias.
3. **The whole apparatus becomes dead code** at ≈200 clean rung-1 observations per identity for a named pair (several hundred under Holm-15) or 6 per identity at perfect discrimination — at which point `season_strength_order` never reaches the fallback and the rotation should be removed under point-never-prune's own exception.
4. **The incident claim** falls if the dispatcher's logs show the deletion originated outside the pytest run — the timestamps (03:36:14 mid-run) and the provably-present-then-absent `netguard_plugin.py` are the evidence to check.

---

**Disagreement**

- **With this brief**: it carries fable's 272/230 as "measured." It did not reproduce under seven constructed denominators while every other fable figure did; the brief should not have presented the two escalation numbers as a reconcilable pair without flagging that one lacks a reproducible extraction.
- **With CC1's sequencing claim**: REFUTED as justified. "A stratum with no denominator is unrecoverable after the fact" is contradicted by execution — the stratum CC1 is defending was itself recovered by replay, with 0 mismatches, and the rotation's deterministic seed preserves replayability. The recorder is still required, but for the measured reasons (31.2% ERROR contamination, replay fragility), and the right sequencing is no sequencing: one commit.
- **With cc2**: the 285/172 headline rests partly on sandbox-harvest duplicates (92 passes); the primary-archive figure is 104/160 = 65.0%. And cc2's rotation, as blindly specified, would have corrupted the `strength_order_was_unestablished` stamp — a material defect in an otherwise exactly-reproducible analysis.
- **With fable**: the 272/230 figure is unreproduced and should be withdrawn or re-derived with its extraction script; the 84.56% number should not enter any report. fable's derivations, correction (disagreement 3), and recorder design all reproduce and stand.

---

**TERMINATION**

**6 passes.** (1) Re-execute cc2's replay — reproduced exactly, with the harvest-denominator caveat; fable's 272/230 found unreproduced after seven candidate extractions. (2) Execute disagreements 2–3 and both inertness checks (SymPy + Wolfram, both → 1). (3) Build the composed fix; found and fixed the stamp defect in passing. (4) Execute B13 end-to-end and deliver it with the strengthened pinning test. (5) **Discover, measure, and repair the sandbox deletion incident** — restored 595 test files, the 74-run archive, registry TOMLs; re-verified every figure post-restore. (6) Final regression: 19 + 141 + 488 passed; tree confirmed stable. Pass 6 produced no new finding above the real-world-consequence threshold — its last product was the confirmation that the deleter lies outside the 27 suites this fix touches. Stopping there; the one open item (the deleter's identity) is named, bounded, and routed to human review rather than guessed at.

<!-- verbatim-end -->

## Where the raw record lives

`bench/logs/joint_what_breaks_the_capability_tie_2026-10-20/` holds the brief, every seat reply, the tool logs and `seat_proposals.diff`. That directory is excluded by `.gitignore:41`, so a byte-identical copy is committed under `experimental_notes/evidence/`, verified by sha256 and checked on every suite run by `bench/tests/test_panel_records_are_preserved_2026-09-11.py`.


Written under CDSFL note standard v1.7 (26 August 2026).
