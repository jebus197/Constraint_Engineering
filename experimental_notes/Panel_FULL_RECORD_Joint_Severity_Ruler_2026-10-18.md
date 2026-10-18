# Joint round: the 2 severity-ruler fixes do not compose, and both seats converged on why

Record written 2026-10-18T03:29:55+01:00.

**This is the seats' own output, reproduced in full.** The Personalisation directive requires external review output preserved *"in full and in unfiltered format"* and says *"Never summarise in place of the full output"*. Any summary elsewhere is downstream of this file, not a substitute for it.

WHAT THIS ROUND WAS FOR. The blind round of 2026-10-18 asked how the severity ruler could be made less coarse. Both free seats answered yes and proposed different fixes, and they disagreed about what a good answer even looks like: one treated an archived convergence verdict moving as evidence its fix reached something real, the other argued that invariance was the desirable property and that a de-coarsening tuned until a verdict moved would be fitting the gate rather than measuring it. Neither position was smoothed into agreement, because the panel runs without compelled convergence by design. This joint round carried both replies verbatim and added the question neither seat had been asked: do the 2 fixes compose?

THE DISPATCH. Free seats only, both on the founder's Max subscription, dispatched serialised because available memory was about 1.4 gibibytes of 8. Joint round carrying its parent's replies verbatim, 28,628 characters of brief. The first seat answered in 1044.3 seconds with 16,773 characters over 33 tool calls; the second in 800.4 seconds with 14,938 characters over 34 tool calls. Each seat worked in its own sandbox and neither could read the other's files, so both reimplemented the other's fix from its prose and validated the reimplementation against every number the other had published before using it.

BOTH SEATS CONVERGED, AND THE CONVERGENCE WAS NOT COMPELLED. The round asked for disagreement to be preserved and supplied no instruction to agree. Both nonetheless reached the same answer on both questions, by measurement rather than by deference, and each produced evidence the other had not.

ON COMPOSITION, THE ANSWER IS NO. Composing the 2 fixes changes the convergence verdict on 0 of 62 archived registries relative to the smoothing alone. The first seat swept 14 values of the noise parameter from 0.02 to 0.50 and found the composition-only difference list empty at every one, so the null is structural rather than an artefact of the parameter chosen, and named the cause: of 734 findings admitted into the rounds that decide quiescence, only 9 carry more than 1 independent assessment, so pooling can only move 9 of them and is structurally unable to reach the predicate. It also derived the correct order-statistic correction by numerical integration and by a 2 million draw simulation, agreeing with the other seat's independent symbolic values to 10 decimal places, and found that the correct and the naive compositions give identical verdicts on all 62 runs, so the one genuinely new term a composition contributes is unobservable at the gate. The second seat reached the same 0 of 62 under both its own predicate and the production one, and added a finding the first had not: the composition LOSES the smoothing's one-way conservatism property, because the only archived entries where the 2 rulers disagree at the decision line are 14 findings whose falsifier CONFIRMED them, and all 14 are pulled below the line rather than above it.

ON THE STANDARD, THE SECOND SEAT WITHDREW ITS OWN BLIND POSITION AND SAID WHY. Its blind reply had argued that invariance is the desirable property. Its joint reply accepts the first seat's standard as qualified: a verdict moving is evidence of reach rather than of fitting when every parameter has provenance independent of the archived verdicts and the direction of movement is a theorem rather than a tuning outcome. It adds that invariance remains the required property only for channels where movement would mean a model's vote overriding a tool, and that the measurement now shows this is exactly and only the channel its own blind fix occupied. The first seat arrived at the same place from the other direction, rejecting both seats' blind standards and supplying a third: movement is reach if and only if the parameter was committed independently and the set of departing runs is monotonically nested in that parameter. It then ran the sweep neither seat had run and found the nesting holds at all 14 parameter values, with 4 runs already departing at the measured confidence floor and no run ever departing and returning.

AND THE FIRST SEAT REFUTED ITS OWN BLIND CLAIM. Its blind reply had justified the fix on the ground that the current ruler is the zero-noise member of the smooth family, which is what would discharge the additive standard. That is false at exactly the threshold value: production treats a finding sitting on the threshold as fully critical while the smooth weight gives it exactly 0.5 at every noise level. CC1 verified this independently with 3 separate mathematical tools and measured the frequency: an exact threshold severity is 156 of 2898 archived registry entries, 5.3830 per cent, reproducing the seat's own 5.3753 per cent on a different denominator. The consequence at the gate is nil, because 0.5 is not below the 0.5 cut, so such a round is non-quiescent under both rulers. What has to be restated is the additive claim, which holds away from the threshold and must name the threshold case.

WHAT IS RECOMMENDED TO THE FOUNDER, AND WHAT IS NOT DONE. Build the smoothing alone. Do not compose the 2 fixes, and do not wire the pooling into the convergence gate, on the measured ground that it cannot reach the predicate and would cost the conservatism property. Nothing has been applied: the smoothing changes which findings the convergence gate admits as critical, so it remains his decision, and the additive claim behind it needs restating in the narrower form before it is relied on.

## Seats and cost

2 seat(s): `cc2`, `fable`. **0 paid dispatches**, enforced by `PANEL_ONLY=cc2,fable`.

## The brief, as dispatched

<!-- verbatim-begin: the brief as dispatched -->

# Joint round: the severity ruler's coarseness, and whether the 2 fixes compose

## 1. Why you are being asked

The blind round of 2026-10-18 asked how the severity ruler could be made less coarse. **Both of you answered yes and proposed DIFFERENT fixes, and you disagree about what a good answer even looks like.** That disagreement is the most useful thing the round produced, and this joint round exists to develop it rather than to settle it by deference.

**This round runs WITHOUT compelled convergence.** If you still disagree after reading each other, say so and say why. Agreement reached by deference is not evidence, and a round whose purpose is reconciliation is the one most able to manufacture it.

**THE QUESTION THIS ROUND ADDS, and it is the one neither of you was asked:** do the 2 fixes COMPOSE? One addresses the variance of a single asserted severity; the other addresses how many independent assessments that variance is estimated from. Those are different terms, so a combination may dominate either alone -- or the pooling may shrink the variance enough that the smoothing buys nothing, which would be a reason to build only one.

**THE SECOND QUESTION, on which you directly contradict each other.** cc2 reports the quiescence verdict moving on 5 of 19 archived runs as evidence its fix reaches something. fable argues the opposite: that the critical gamma being INVARIANT is the desirable property, and that a de-coarsening tuned until it moved an archived convergence verdict would be *"fitting the gate ... the cooking vector in another coat"*. **Both cannot be the right standard.** Say which it is, and what evidence would distinguish a fix that reaches something from a fix that has been fitted to the archive.

**A CORRECTION YOU BOTH MADE, acknowledged here so you argue from the corrected record.** The blind brief, written by CC1, claimed the section 7.7 specification rescales severities and lets the wobble travel with it. You both showed that is wrong by execution: since the largest asserted severity is 1 and half of 1 is below the threshold of 0.7, an effective severity at or above threshold is identically the conjunction of a confirmed falsifier verdict and an asserted severity at or above threshold. cc2 obtained unsatisfiable from z3 for the negation and confirmed it in Wolfram Language, measuring 33 of 191 unresolved entries asserted-critical against 0 specification-critical. The brief was wrong and you were right.

## 2. The standards every answer is judged against

The additive standard: nothing is removed or narrowed without a committed measurement showing the replacement dominates on a named property, and an addition nothing reaches is not additive either. The simplest sufficient fix is the correct one. A finding without a fix is incomplete, and a fix whose falsifier has not been EXECUTED is a hypothesis.

## 3. The 2 replies, verbatim

<!-- (inner label, not a region marker) cc2's blind reply, 2026-10-18 -->

### cc2 (798.9 seconds, 13,936 characters, 50 tool calls)

Two passes run. Writing up.

## Verdict

**Yes** — the ruler can be made meaningfully less coarse by replacing the hard indicator `1[severity ≥ 0.7]` with its expectation under the project's own measured instrument noise, `Φ((sev−0.7)/σ)`; this changes the quiescence verdict on **5 of 19** archived runs, and in the strict direction on all 5.

## Reasoning

**Premise 1 — the gate's decision rule discards exactly the information the founder's evidence is about.** `_settled_novelty_series` counts criticals with `(e.get("severity") or 0.0) >= _thr`. The appendix (line 765) measures that number's per-assignment noise at σ = 0.1419, CI [0.1241, 0.1575]. An indicator on a quantity with that σ rounds a coin toss at 0.700 to a certainty and a 0.699 to a zero. The noise is in the data; the rule has no channel to carry it.

**Premise 2 — `effective_severity` does not address this, and it fails in the *opposite* direction from the brief's description.** With the spec on, `eff = asserted · V`, V ∈ {0, 0.5, 1}. Since sup(asserted) = 1 and 1·0.5 = 0.5 < 0.7:

> `eff_sev ≥ 0.7` is **identically** `V == 1.0 ∧ asserted ≥ 0.7`.

z3 returns `unsat` for the negation of that equivalence, and `unsat` for "∃ unresolved entry that is critical". Wolfram Language independently returns `True` for `Reduce[ForAll[{a}, 0≤a≤1, a/2 < 7/10]]`. Executed on the whole archive: **33 of 191** unresolved entries are asserted-critical, **0** are specification-critical. So the specification does not "rescale the band and let the wobble travel with it" — it moves the entire unresolved population to the non-critical side, and the asserted ordering stops reaching the gate at all. §7.7's caution 1 records the same collapse algebraically.

**Premise 3 — the minimal repair is one formula, and it *nests* the current ruler.** `w(f) = Φ((sev−θ)/σ)`. Four properties, derived in SymPy and re-checked in Wolfram Language:

| property | value | consequence |
|---|---|---|
| `Φ(θ)` | exactly `1/2` | a finding on the line is worth half a critical — what a coin toss is worth |
| `dΦ/dsev` | `√2·e^{−(sev−θ)²/2σ²}/(2√π σ) > 0` | the asserted ordering is preserved, not flattened |
| `lim_{σ→0⁺} Φ` | `1` for sev>θ, `0` for sev<θ | **the current ruler is the σ=0 member of this family** |
| REFUTED | short-circuit to `0.0` | §7.7's key property held *exactly*; Φ's tail is 4.1e-7, which is not zero |

The σ→0 nesting is what discharges the additive standard: nothing is removed, and the test executes the value-for-value equality against `_settled_novelty_series` on all 24 catalogues rather than asserting it.

**Premise 4 — direction of effect, derived then measured.** The quiescence test `all(w_r < 0.5)` is one-way. Proof: a countable finding with sev ≥ θ and not REFUTED has `w ≥ Φ(0) = 1/2`, so the round sum is ≥ 0.5 and the test fails. Hence `soft_quiescent ⟹ hard_quiescent`: the instrument can **refuse** a convergence the hard rule permits and can **never permit** one it refuses. Measured: 0 of 19 runs became easier, Wilson [0.0000%, 16.8179%]. The brief's "a change that makes convergence easier must be argued for" therefore does not bite.

**Premise 5 — it reaches something, and across scenarios rather than one.** 5 of 19 flip (26.3158%, Wilson [11.8064%, 48.7916%]). Separately, **4 of 19** runs have an identically-zero hard critical series, so `_estimate_gamma` returns its 0.0 sentinel — which lands in the worst `GAMMA_BANDS` text, "recommend HIL audit" — while the soft series is non-degenerate and yields 0.4769 / 0.4757 / 0.6819 / 0.7369. The hard ruler has *no resolution at all* in the common regime where nothing crosses 0.7.

**Why not the alternatives.** Aggregating repeats (σ/√m) is the textbook answer and I rejected it on measurement: all 722 archived catalogue entries carry exactly **one** `severity` and one `source_model` — the duplicate's number is destroyed at merge, so aggregation needs a schema change *and* reaches only m≥2 findings. §7.8 Approach B (`S_v = 1/(1+exp(−Λ_total))`) is the appendix's own preferred answer but requires per-finding SymPy/dimensional/numerical verifiers this harness does not run — that is a build, not a fix. Scaling the threshold by V (`eff ≥ V·θ`) exactly cancels V except for annihilation, so it is a no-op dressed up and restores the ±0.14 wobble at full strength.

**On gamma, computed not hypothesised.** Driving the production `gamma_threshold_profile` on leg3: γ_hard = 1.0000, γ_soft = 0.9597; hard tail [0,0,0], soft tail **[0.2541, 0.1184, 0.4248]**. leg3 converges either way — my change does not move its verdict. But its final round carries 0.4248 *expected* novel criticals: under the project's own σ, there is roughly a 42% chance that round was not actually quiet, and the hard ruler reported it as 0. That is the single sharpest number here. Note also that the existing threshold *sweep* needs a correlated shift of 0.2 (down to θ=0.5) to break leg3's quiescence, whereas 5 runs break under uncorrelated noise at the **live** threshold — the sweep and this block answer different questions, and the uncorrelated one is the question the 273-pair measurement is about.

## Falsifier and its executed result

```
$ python3 -m pytest "bench/tests/test_the_severity_ruler_instrument_noise_2026-10-18.py" -q -s
..
quiescence verdict differs on 5/19: ['commissioning_arm1_panel_20260929T194414Z', 'commissioning_arm2_single_20260922T020120Z', 'commissioning_arm3_contrast_20260930T051219Z', 'free_run1_directive_whole_20261015T061123Z_20261015T061124Z', 'sim45_postfix_20260901T231824Z_20260901T231827Z']
..
33 of 191 unresolved entries are asserted-critical; 0 are specification-critical (collapse holds)
.
leg3 via production caller: gamma_hard=1.0, gamma_soft=0.9597, soft tail=[0.2541, 0.1184, 0.4248], differs=False
..
7 passed in 0.98s
```

**It is capable of failing, demonstrated by mutation rather than claimed.** Mutant 1 — re-centre the weight 0.10 below the threshold:

```
E  AssertionError: ONE-WAY PROPERTY VIOLATED -- the soft rule permitted a convergence the hard
   rule refused on 2 run(s): [('commissioning_arm2_single_20260930T031047Z', [0.0008, 0.0, 0.2405],
   [1, 0, 1, 0, 0, 0, 0, 1]), ('study_run1b_2026-10-03_20261003T100439Z', ...)]
2 failed, 5 passed
```

Mutant 2 — delete the REFUTED short-circuit:

```
E  AssertionError: C0018 (severity 0.5, REFUTED) got weight 0.07935206851650323, not exactly 0.0.
   A disproved finding must be ANNIHILATED, not merely reduced
1 failed, 6 passed
```

Restored: `7 passed`. The brief's own exercise reproduces: 38 leg3 findings, 2 REFUTED at stored severity 0.5, `effective_severity` → 0.5 (spec off) / 0.0 (spec on).

Regression: `test_the_severity_spec_decides_when_promoted_2026-10-15.py` + `test_a_declared_mode_is_reconciled_2026-10-18.py` → **38 passed**.

**One pre-existing failure, which I established is not mine.** `test_source_text_and_neighbour_audit_2026-09-11.py::test_the_class_has_not_grown_silently` fails at **106 source-text assertions against a ceiling of 98**. I removed my change entirely and re-ran: still **106**. So it pre-exists, and my test contributes zero to that class — it executes rather than greps.

**Tool attribution.** Open-source primary: z3 (collapse equivalence, `unsat`), SymPy (Φ(θ)=1/2, monotonicity, σ→0 limits), statsmodels (Wilson, Clopper–Pearson), `math.erf` (series). Wolfram second falsifier — Wolfram Language, local Wolfram Engine via `wolframscript`, exit 0, values returned: `{0.5, 0.24049174238756052, 0.36228384156955123, 0.7135471515289855, 0.9206479314834969, 1, 0, True}`, agreeing with SymPy to 9 digits and confirming both σ→0 limits and the collapse.

## The fix

**`bench/severity_instrument.py`** (new, 190 lines) — `critical_weight`, `expected_critical_series`, `tail_is_quiescent_soft`, `instrument_noise_profile`, and `SEVERITY_INSTRUMENT_SIGMA = 0.1419` carrying its CI and its producer citation.

**`bench/reference_runner_v3.py`** (2 edits) — one import beside the other `bench` siblings, and a wrapped call inside `gamma_threshold_profile`, which the report path already invokes at line 21039. The result is written to every report as `instrument_noise_profile`. Nothing is removed; no existing call site changes; the live gate still decides on the hard indicator.

**`bench/tests/test_the_severity_ruler_instrument_noise_2026-10-18.py`** (new, 7 tests) — all against the real archive, all driving production functions.

The population filter inside `expected_critical_series` deliberately mirrors `_settled_novelty_series`' admission rules exactly, so the *only* difference between the two series is indicator-versus-Φ. A second, independently-written filter would make any difference between them unattributable — the failure `gamma_threshold_profile` already records in its own comment about a reimplemented gate.

**I did not promote it to a deciding gate, and that is deliberate.** Promotion needs an end-to-end measurement on a live run, which one seat cannot commit. The 5 flips are the evidence for taking that step, not the step itself. I have stated this in the module docstring rather than leaving a reader to infer it.

## What would refute this

1. **σ is not the right noise model.** The 0.1419 is a *between-model* standard deviation on duplicate pairs. If the pairs the runner ruled identical are not in fact the same defect, σ is an upper bound inflated by genuine disagreement about distinct defects, and the soft series over-counts. Refutation: adjudicate a sample of the 273 pairs and show that the within-defect σ is below **0.045** — at which point `Φ((0.6−0.7)/0.045) = 0.013`, every flipping run's soft tail drops under 0.5, and all 5 flips vanish. That single number is my refutation threshold.

2. **The flips are an artefact of simulated severity.** 17 of the 19 catalogues are `*-SIM` runs, and `severity_admissibility` stamps them "MAGNITUDES are uncalibrated against a real panel and do not transfer." If a real-panel run shows a severity distribution with no mass in [0.5, 0.7), the soft and hard series coincide and the fix reaches nothing. Refutation: a real run whose `instrument_noise_profile` reports `quiescence_verdict_differs: false` with every soft tail entry below 0.05.

3. **The named run on which my ruler decides worse.** `prose_convergence_run1b_2026-10-02` — hard tail [9,4,8], soft tail [8.78, 2.77, 7.27]. Here the soft count is *lower* than the hard count in every round. If a run's criticals are clustered just above 0.7, the soft count systematically under-reports the number of blockers, and a future gate reading the soft count as a *magnitude* rather than a quiescence test would be looser than the hard one. My one-way proof covers only the `< 0.5` quiescence predicate; it does **not** cover any gate that compares the soft count to a threshold above 0.5. Anyone promoting this must re-derive the direction for their own predicate.

4. **The 0.5 cut.** If someone shows an archived run where the maximum-likelihood critical count is 0 but the sum exceeds 0.5 by accumulation of many tiny weights — 10 findings at 0.45, say, summing to 0.5+ — then `all(w < 0.5)` is not "the most likely count is zero" and my claim that the cut is derived rather than chosen fails. `commissioning_arm1_panel_20260929T194414Z`'s first tail entry of 1.2019 is the closest the archive comes; it is driven by two findings near 0.65, not accumulation, so it survives — but this is the weakest of my four claims.

## Disagreement

**The brief's description of what §7.7 fails to fix is wrong, and wrong in the direction that matters.** It states: *"the specification halves those findings uniformly and preserves their relative ordering, noise included. A 0.8 becomes a 0.4 and a 0.7 becomes a 0.35; the band is rescaled and the wobble travels with it."* That is true of the stored numbers and false of the gate. Because the threshold was **not** transformed with the quantity, `asserted·0.5 ≥ 0.7` is unsatisfiable on [0,1] — z3 `unsat`, Wolfram `True`. At the decision site the ordering does not survive and the wobble does not travel; the whole unresolved population lands on one side. That is not "rescaled with the noise intact," it is zero bits where there was one, and it is a *worse* problem than the one the brief describes. §7.7's caution 1 already records the algebra; the brief argues from a mental model the appendix had already corrected.

**Second, smaller disagreement with the framing.** The brief frames the ruler as "deciding criticality partly at random" and implies that less randomness is the goal. I would not have assumed that. A finding at a true severity of 0.70, measured by an instrument with σ = 0.14, *is* a coin toss — the randomness is in the world, not only the ruler. The achievable goal is not to remove it but to stop the gate from laundering it into a certainty. That reframing is why my fix reports an expected count rather than making the threshold sharper: sharpening a threshold on a noisy input makes the ruler look more decisive without making it more accurate, and that is the failure mode the ±0.14/0.09 ratio actually describes.

**Third.** The brief directs that the fix be delivered into the repository tree, but the tree is a torn-down sandbox with no git. I have written the three files at their real paths and reported them above; they will not survive teardown, so the paths and the diffs in this reply are the deliverable of record.

---

**Passes: 2.** Pass 1 produced the collapse proof, the Φ derivation, the 5/19 measurement and the fix. Pass 2 added the mutation testing, the audit-test attribution (106 pre-existing, not mine), the Clopper–Pearson intervals, and refutation condition 3 — the `prose_convergence_run1b` case where the soft count is *lower* than the hard count, which bounds my own one-way proof to the quiescence predicate and no further. A third pass surfaced nothing above the real-world-consequence threshold, so I stopped.

<!-- (inner label, not a region marker) end of cc2's blind reply -->

<!-- (inner label, not a region marker) fable's blind reply, 2026-10-18 -->

### fable (571.3 seconds, 9,516 characters, 38 tool calls)

All evidence is in. Both review passes are complete; a third would repeat the second. Here is my seat's answer.

---

## Verdict

Yes — the ruler can be made meaningfully less coarse by pooling the k independently-asserted severities the registry already holds for each co-discovered defect (median over the direct codiscovery star), stamped beside the asserted number on the `stamp_sev_f` precedent; and this is now implemented, wired, and executed.

## Reasoning

Premises, each executed rather than asserted:

1. **The instrument behaves as documented.** From `bench/reference_runner_v3.py` I imported and called the artefact on real entries of `bench/logs/leg3_final_shakedown_20261015T220118Z/runner_state.json`:
   - `C0018` (asserted 0.5, REFUTED): `spec_verification_factor` = 0.0, `effective_severity` = 0.5 spec-off, **0.0 spec-on** — the annihilation term fires.
   - `C0014` (asserted 0.5, verdict `''`): V = 0.5, effective 0.5 → 0.25.
   - `C0001` (asserted 0.9, CONFIRMED): V = 1.0, effective 0.9 either way.
   - `C0031` (asserted 0.5, unresolved): 0.5 → 0.25.
   The brief's diagnosis is confirmed by execution: V rescales the unresolved population uniformly and its noise travels with it.

2. **The missing information already exists in the registry.** `record_codiscovery` is non-destructive (founder ruling), so when k seats raise one defect, k canonicals each carry an independent severity — and the current ruler reads exactly one (whoever filed first) and discards k−1 measurements. Measured: leg3 has 14/38 entries with star size k≥2 (k-distribution: 24×1, 7×2, 3×3, 1×4, 1×5, 2×6); free run 1 has 6/22; free run 2 has 5/19. The data is live in all three post-2026-09-29 runs, not only the one the question was tuned on.

3. **Pool the direct star, not the transitive component — measured, not judged.** The union-find component (the `_corroborated_discounts` construction) chains 20/38 leg3 canonicals into one component with severity spread 0.50, mixing CONFIRMED and REFUTED members — transitivity was never adjudicated. The direct stars stay tight where corroboration is genuine: C0001's six sightings are [0.9, 0.9, 0.85, 0.9, 0.85, 0.78], spread 0.12, consistent with the founder's 0.14 wobble.

4. **The noise arithmetic, derived.** With per-assessment noise σ = 0.14 (founder's figure) and normal noise, the sampling SD of the median of k is σ × {1, 0.7071, 0.6698, 0.5462, 0.5356} at k = 1…5, i.e. **0.140 / 0.099 / 0.094 / 0.077 / 0.075**. Order-statistic constants computed by quadrature (SciPy) and Monte Carlo (NumPy, 2×10⁶ draws, seeded); k=3 and k=5 constants confirmed to 10 decimals by Wolfram Language (local Wolfram Engine): {0.6698291607404084, 0.5355685405301724}. So **k≥4 brings the wobble below the 0.09 decision half-band**; k=2–3 reduce without curing; k=1 is byte-identical to today. Median, not mean, because archived stars carry outliers up to 0.55 spread.

5. **The consumers, computed.** Via `_settled_novelty_series` + `_estimate_gamma` (the exact production path — line 19979 feeds line 20156): settled critical series asserted vs pooled: leg3 [12,0,0,0,0]→[7,0,0,0,0], free run 1 [12,0,0,0]→[9,0,0,0], free run 2 unchanged; **gamma_critical = 1.000 under both rulers on all three runs**, and the zero-new-critical tails are identical. The archived gamma_critical_history ends 1.0, matching my reconstruction. **Two-sided gate effect: in v1, none** — the stamp is informative-only, so the critical count, gamma, and convergence are unchanged by construction. If promoted: upward crossings add blockers (convergence harder, conservative); downward crossings (5 on leg3, 3 on run 1) would remove blockers — and every leg3 downward crosser is a **falsifier-CONFIRMED critical** whose star partner asserted low. That is votes overriding a tool, so the docstring records the promotion rule: a downward crossing may only gate on `severity_is_proven` or HIL — the same discipline `_apply_severity_calibration` already enforces. Promotion itself remains a founder decision, per the `sev_f` precedent.

## Falsifier and its executed result

```
python3 -m pytest bench/tests/test_attested_severity_2026-10-18.py -q
```
Output, verbatim:
```
.......                                                                  [100%]
7 passed in 0.92s
```
Capability to fail, demonstrated: running the same median assertion against a deliberately wrong implementation (mean instead of median) printed `WRONG IMPLEMENTATION CAUGHT -> median assertion: got 0.7333`; the real implementation prints `median = 0.8`. If the fix were wrong the test file prints pytest `FAILED` with an `AssertionError` naming the broken property (k=1 identity, median value, self-reference admitted, severity mutated, flag-off mutation, or the leg3 archive values C0001→0.875, C0011→0.64, gamma 1.000). Regression beside the nearest neighbour: `python3 -m pytest bench/tests/test_the_severity_spec_decides_when_promoted_2026-10-15.py bench/tests/test_attested_severity_2026-10-18.py -q` → `21 passed in 1.18s`.

## The fix

Written into the sandbox repository tree:

- **`bench/reference_runner_v3.py`** — three additive changes, syntax-verified:
  1. `RunnerConfig.severity_attestation_enabled: bool = False` (beside `sev_f_enabled`),
  2. `attested_severity(entry, entries) -> (median, k, spread)` and `stamp_attested_severity(registry, cfg, round_idx)` (beside `stamp_sev_f`; stamps `severity_attested` **beside** `severity`, never over it; logs how many entries would gate differently at `CRITICAL_SEVERITY_THRESHOLD`),
  3. the call wired in `run_experiment` immediately after `stamp_sev_f`, same placement, same default-off no-op.
- **`bench/tests/test_attested_severity_2026-10-18.py`** — 7 executed tests, including the leg3 archive assertions and gamma invariance.

Additive standard: nothing removed or narrowed; default off is byte-identical; the new entry point has a caller (run_experiment) and is executed by a test in both flag states. Simplest-sufficient: no new dispatch, no schema change, no new model call — it reads measurements the registry already records and was discarding. Composability: it composes with Sev(f) only in the stated promoted form (pooled asserted term × harness V), and that composition is **not** enacted here because no measurement yet shows it dominates — the leg3 CONFIRMED-crosser evidence in fact warns against naive composition.

## What would refute this

1. **Reach:** if in the next live (non-SIM) run fewer than ~10% of entries carry k≥2 attestations, the stamp reaches almost nothing and fails the additive standard's "reached" requirement (pre-2026-09-29 the measured rate was 0/53; the fix depends on the occasion-growth repair staying effective).
2. **The repeats threshold, named as the brief demands:** at k≤3 the median's sampling SD (0.099/0.094 at σ=0.14) still exceeds the 0.09 half-band — for stars of size ≤3, which are 10 of leg3's 14 multi-attested entries, my scheme is a reduction, not a cure, and at k=1 (24 of 38 entries) it is exactly the single assessment it replaces.
3. **The archived run where it would decide worse, named:** leg3, entry C0011 — falsifier-CONFIRMED, asserted 0.78, star-pooled 0.64. If the pooled number were promoted to the gate without the proof-discipline guard, it would demote a tool-confirmed critical on another model's lower vote; the current ruler decides that entry correctly. If the counterfactual-repair adjudicator shows the downward-crossing star links are predominantly *correct* same-defect links with genuine severity disagreement, the guard is right; if it shows they are mis-links, pooling is corrupted by adjudication error and the whole scheme inherits the linker's noise rather than cancelling the assessor's.

## Disagreement

The brief's framing contains an assumption I would not have made: that a good answer *moves* gamma — "a proposal that moves gamma without the proposer having computed gamma is a hypothesis". On the archived evidence the correct result is the opposite: gamma_critical is **invariant** (1.000 → 1.000 on all three runs) under the pooled ruler, and that invariance is the desirable property — a de-coarsening tuned until it moved an archived convergence verdict would be fitting the gate, which is the pre-registration's named "cooking vector" in another coat. Second, the brief locates the residual problem in the unresolved V=0.5 population's noise, but understates the step it sits next to: if the 7.7 specification were ever promoted to the blocking gate, uniform halving puts essentially the entire unresolved population below 0.7 (max asserted 1.0 × 0.5 < 0.7), so the gate's coarseness would then be dominated by the V step function, not the asserted wobble — the two must be fixed in the right order, and the noise term only matters at the gate while V stays informative. Third, the brief's "82 of 273 on opposite sides" invites treating the 0.7 cut as the defect; the cut is pre-registered and frozen for good reason — the tractable term is the variance of the number measured against it, which is what this fix reduces.

**Passes run: 2.** Pass 1: instrument exercise, archive measurements, derivation, fix, falsifier. Pass 2: verdict audit of the downward crossers (surfacing the CONFIRMED-critical demotion risk and the proof-discipline rule), star-size distribution, regression run. A third pass produced nothing above the material threshold.

*Wolfram-derived constants above are attributed to Wolfram Language (local Wolfram Engine, via wolframscript).*

<!-- (inner label, not a region marker) end of fable's blind reply -->


## 4. Use the harness

**Form your answer by RUNNING the machinery.** Execute the other seat's falsifier, not only your own: a fix you have not tried to break is a hypothesis, and that applies to a fix someone else proposed. Report the command and the output.

Compute `gamma` under BOTH rulers and under their COMBINATION over the archived runs, and report what each does. Name the runs. If the combination changes nothing beyond what 1 fix alone achieves, that is the finding and it argues for building only 1.

The severity model, `effective_severity` and `spec_verification_factor` in `bench/reference_runner_v3.py`, is the instrument under review; exercise it directly on real archived entries.

## 5. Produce a fix, and test it

Deliver your fix as a file written INTO the sandbox repository tree at its real path. Report the exact command you ran and the output you saw. State what your falsifier would print if your answer were wrong, and show that it prints something different now.

## 6. What would refute you

State what evidence would overturn your own answer, and state separately what would overturn the OTHER seat's answer. Be specific about runs, thresholds and sample sizes.

## 7. Output shape

1. `## Verdict` -- do the 2 fixes compose, and which standard is right about moving a verdict, in one sentence each.
2. `## Reasoning` -- premises first.
3. `## Falsifier and its executed result` -- the command, and the output, including your run of the OTHER seat's falsifier.
4. `## The fix` -- the real path you wrote it to.
5. `## What would refute this` -- for your answer and for the other seat's.
6. `## Disagreement` -- your strongest remaining disagreement, with the other seat or with this brief. If you now agree where you did not, say what changed your mind and name the evidence that did it. Deference is not evidence.

## 8. Termination

Stop when a further pass produces no new findings above the real-world-consequence threshold. State how many passes you ran.


<!-- verbatim-end -->

## Seat: cc2

Route `claude_cli`, 33 recorded tool call(s).

<!-- verbatim-begin: cc2 (panel joint_the_severity_ruler_2026-10-18) -->

Two passes complete. All measurements in.

## Verdict

**The 2 fixes do not compose: composing them changes the quiescence verdict on 0 of 62 archived registries beyond cc2's fix alone — at every one of 14 swept σ, not just at 0.1419 — because pooling acts on only 9 of the 734 entries sitting in the rounds that decide quiescence (1.2262%, Wilson [0.6464%, 2.3138%]), so build cc2's fix alone.**

**Neither seat's standard as stated: verdict movement is evidence of reach iff the parameter producing it was committed independently *and* the departing set is monotonically nested in that parameter — a sweep neither of you ran, which I ran, and which comes out in cc2's favour (nested at all 14 σ, 4 departures at the CI floor, 7 at the point estimate, 9 at the ceiling) while refuting fable's empirical invariance claim about its own fix.**

## Reasoning

**Premise 0 — both seats' published numbers reproduce, so the reconstructions are theirs.** Neither `bench/severity_instrument.py` nor `bench/tests/test_attested_severity_2026-10-18.py` exists in my sandbox (separate sandboxes, no git), so I could not execute your literal files. I reimplemented both from your prose and validated against every number you published. fable's leg3 star-size distribution `{1:24, 2:7, 3:3, 4:1, 5:1, 6:2}`, C0001→0.875 at k=6, C0011→0.64, hard `[12,0,0,0,0]`→pooled `[7,0,0,0,0]`, γ=1.000 both ways. cc2's leg3 soft tail `[0.2541, 0.1184, 0.4248]`, γ_soft=0.9597, and refutation condition 3's `[9,4,8]`→`[8.78, 2.77, 7.27]` on `prose_convergence_run1b`. All exact. My hard series equals production `_settled_novelty_series` on all 62 runs, asserted value-for-value.

**Premise 1 — the composition is null at the gate, and the null is structural, not an artefact of σ.** Over all 62 archived registries carrying entries (cc2's 19 is a subset):

| ruler | quiescence verdict differs from hard | γ band differs |
|---|---|---|
| soft (cc2) | **7/62** | 10/62 |
| pooled (fable) | **0/62** | 3/62 |
| composed, σ_k = σ·c_k | **7/62** — identical set | 11/62 |
| composed, naive constant σ | 7/62 — identical set | — |

`composed vs soft-alone: []`. Swept across σ ∈ {0.02 … 0.50}, 14 values: the composition-only flip list is empty at **every** one. The mechanism is in the archive, not in the arithmetic: of **734** entries admitted into the 3 rounds that decide quiescence, **9** carry k≥2. Pooling can only move those 9. It is structurally unable to reach the predicate.

**Premise 2 — getting the composition *right* also buys nothing, which is the sharper half.** The naive composition (smooth the pooled median with the unpooled σ=0.1419) is wrong: pooling already reduced that estimator's noise to σ·c_k, so the naive form over-smooths. I derived the correct c_k by quadrature and Monte Carlo (2×10⁶ draws): {1, 0.7071067812, 0.6698291607, 0.5460765683, 0.5355685405}, agreeing with fable's Wolfram values at k=3 and k=5 to 10 dp. The correct and naive compositions give **identical verdicts on all 62 runs**. So the σ_k correction — the one genuinely new term a composition contributes — is unobservable at the gate. A composed fix must still satisfy simplest-sufficient; this one adds an order-statistic table and a star traversal for zero verdict change.

**Premise 3 — the single place composition does anything, and it fails the direction test.** `commissioning_arm1_panel_20260929T214647Z` is the only run where the composed γ crosses a `GAMMA_BANDS` edge that soft-alone does not: γ_soft=0.1952 ("Gamma disagrees with state closure — recommend HIL audit") vs γ_composed=0.2039 ("Weak depletion"). That is 1/62 = 1.6129%, Wilson [0.2853%, 8.5867%], a 0.0087 straddle of a hard band edge at 0.20, in the direction that **removes** an audit recommendation. That is not a demonstrated advantage; it is one multi-attested tail entry against a band boundary.

**Premise 4 — the standard question, decided by the shape of the verdict, not its count.** Both of you were arguing from a scalar that cannot settle it. A fitted de-coarsening departs from the hard verdict near its committed parameter and returns either side; a reaching one departs above a threshold σ* and stays departed. Measured:

```
sigma=0.0200 n=0   sigma=0.1241 n=4  (measured CI floor)   sigma=0.1575 n=9 (ceiling)
sigma=0.0600 n=0   sigma=0.1419 n=7  (committed estimate)  sigma=0.2200 n=13
sigma=0.1000 n=1                                           sigma=0.5000 n=19
superset_of_previous = True at EVERY step; no run ever departs and returns.
```

Monotone nesting, 4 departures already at the CI floor. cc2's 0.1419 is not a knife edge, and σ is not cc2's knob — it is the appendix's duplicate-pair measurement (line 765), committed before the sweep. **So movement here is reach.** It also confirms cc2's own stated refutation threshold honestly: at σ=0.04 the departure count is 0, exactly as cc2 said it would be below ~0.045.

**Premise 5 — fable's invariance claim is refuted as an empirical claim about fable's own fix.** fable measured γ on 3 runs (leg3, free run 1, free run 2) and found invariance. Over 62, pooling moves γ on 3 runs and on **1** it converts an estimable γ into the 0.0 sentinel: `commissioning_arm1_panel_20260929T214647Z`, hard `[1,0,0,1,0,0,0,4]` γ=0.3236 `_gamma_is_estimable=True` → pooled `[0,0,0,0,0,0,0,4]` γ=0.0000 `_gamma_is_estimable=False`. The sentinel lands in the worst band text. The direction is conservative and production's `gamma_is_estimable` flag does carry the degeneracy, so this is not a hard-constraint violation — but "gamma_critical is invariant" is true on 3 runs and false on 62, and fable's own refutation condition 1 (reach below ~10%) is met at the deciding tail: 1.2262%.

**Premise 6 — cc2's σ=0 nesting claim fails at the archive's modal critical severity, and it costs a sixth of the instrument's effect.** Production compares `sev >= 0.7`, scoring a finding at exactly 0.7 as 1; lim_{σ→0⁺} Φ(0) = **1/2** for every σ (SymPy, and Wolfram Language independently). **0.7 is the third most common severity in the archive — 174 of 3237 entries, 5.3753%, Wilson [4.6500%, 6.2065%], across 42 runs** — because models anchor on the published cut. So "the current ruler is the σ=0 member of this family" holds for sev≠θ and fails on 5.4% of the population. Consequence, measured both ways: **zero** quiescence verdicts move (derived — Φ(0)=1/2 is not `< 0.5`, so such a round is non-quiescent under both rulers; cc2's 0.5 cut absorbs the discontinuity exactly, for a reason cc2 did not give), but these entries carry **16.12% of the archive's total |hard − soft| mass** and 3 of the 21 criticals in `prose_convergence_run1b`. That is the mechanism behind cc2's refutation condition 3 — not a rare cluster, a modal value.

## Falsifier and its executed result

```
$ python3 -m pytest "bench/tests/test_does_the_decoarsened_verdict_reach_or_fit_2026-10-18.py" -q
..........                                                               [100%]
10 passed in 0.82s
```

**The other seat's fixes, executed via validated reconstruction** (their files absent — stated above, and this is the honest limit of this part). The test asserts their published numbers as a precondition, so if my reconstruction were not theirs, `test_both_seats_published_numbers_reproduce_from_this_reimplementation` fails naming the divergent value. It passes. cc2's fix reproduces 7/62 flips including all 5 cc2 named plus `exp35_pe` and `exp40_slice_collision` from the wider set; fable's reproduces 0/62.

**Capability to fail, by mutation rather than claim.** Mutant 1 — re-centre the weight 0.12 above threshold, i.e. break the discriminator:
```
E  assert 12 == 0        (counts[0.04]: 12 departures where 0 is required)
E  assert 0.02 == 0.1241 (verdict_flip_sigma collapses to the band floor)
```
Mutant 2 — delete the REFUTED annihilation:
```
E  AssertionError: assert 0.97950804462579 == 0.0
1 failed, 9 passed
```
Restored: `10 passed`. **If my answer were wrong**, `test_composition_moves_no_verdict_beyond_the_expected_count_rule_alone` prints `COMPOSITION EARNS ITS PLACE after all -- it moves the verdict beyond the expected-count rule alone on N run(s): [...]`, and `test_the_departing_set_is_monotonically_nested_in_sigma` prints `NOT NESTED -- fitted signature: runs [...] depart at sigma=X and stop departing at sigma=Y`. Both print nothing now.

**Regression:** `test_the_severity_spec_decides_when_promoted_2026-10-15.py` + mine → `24 passed in 1.29s`.

**The one pre-existing failure, attributed by removal.** `test_source_text_and_neighbour_audit_2026-09-11.py::test_the_class_has_not_grown_silently` fails. With my 3 edits reverted it fails identically (`1 failed, 9 passed` both ways). Pre-existing — independently confirming cc2's attribution.

**Tool attribution.** Primary, open-source: SymPy (Φ(θ)=1/2, dΦ/dv = √2·e^{−(t−v)²/2s²}/(2√π s) > 0, all three σ→0 limits including the 1/2 at v=θ, concavity), z3 (`unsat` for ∃a∈[0,1]: a/2 ≥ 0.7 — the §7.7 collapse), SciPy quadrature + NumPy Monte Carlo (median-of-k constants), statsmodels (Wilson intervals). **Wolfram Language** (local Wolfram Engine via `wolframscript`, exit 0, no `Name::tag`): `Phi0 = 0.5`, `lim s->0+ sev>thr = 1`, `lim s->0+ sev=thr = 1/2`, `lim s->0+ sev<thr = 0`, `collapse unsat = True`, `dPhi/dsev > 0 = True`, `c2 = 0.70710678118654752440`. **Two earlier Wolfram calls emitted `NIntegrate::slwcon` and `NIntegrate::eincr`, so they verified nothing and the c3/c4 constants stay Wolfram-UNVERIFIED** — they rest on SciPy quadrature and 2×10⁶-draw Monte Carlo agreeing to ≤3.4e-4, plus fable's blind-round Wolfram confirmation. One of those calls was moved to background by a harness timeout, not by choice.

## The fix

- **`bench/severity_noise_sweep.py`** (new, 216 lines) — `critical_weight`, `expected_critical_series`, `tail_is_quiescent_soft`, `noise_robustness_profile`, `SWEPT_SIGMAS`, and σ=0.1419 carrying its CI and its producer. Reports `verdict_flip_sigma`, `flip_inside_measured_ci`, `departs_monotonically`, `per_sigma`. The admission filter is **passed in** from the caller rather than restated, so the only difference from the production series is indicator-versus-Φ.
- **`bench/reference_runner_v3.py`** (2 edits) — one import beside `bench.panel_sandbox`, one wrapped call at the end of `gamma_threshold_profile`, which the report path already invokes at line 21056. Nothing removed; no existing call site changed; the live gate still decides on the hard indicator.
- **`bench/tests/test_does_the_decoarsened_verdict_reach_or_fit_2026-10-18.py`** (new, 10 tests) — all against the real archive, all driving production functions.

Simplest sufficient: I did **not** build the composition, because the measurement says it adds nothing. I did not build a second expected-count series either — my module states the merge requirement with cc2's `severity_instrument.py` in its docstring rather than leaving a reader to infer that two blocks computing one series from two filters makes any difference between them unattributable, which is the failure `gamma_threshold_profile` already records about a reimplemented gate. Additive: reached by `run_experiment`'s existing report path, executed by a test.

## What would refute this

**Mine.** (1) A live non-SIM run whose `noise_robustness` reports `departs_monotonically: false` — a run departing at 0.1419 and not at 0.1575 — breaks the discriminator and with it my answer to question 2. (2) A promoted gate reading the expected count as a *magnitude* against any cut above 0.5: there my composition-null does not transfer, because the σ_k sharpening changes the magnitude on every k≥2 entry even where it changes no verdict; on `commissioning_arm1_panel_20260929T214647Z` the composed series is `[1.4167, 0.247, 0.5194, 1.1457, …]` against soft `[1.5212, 0.2379, 0.713, 1.3926, …]`. (3) **The named run where my answer decides worst**: that same run, where the composition is the only thing that moves a γ band — if the occasion-growth repair raises multi-attestation at the deciding tail from 1.2262% to above ~15%, the 9-entry reach that makes composition null disappears and the whole question must be re-measured. Threshold: 110 of 734 tail entries at k≥2.

**cc2's.** (1) The within-defect σ. cc2 named 0.045 and I executed it: at σ=0.04 the departure count is 0, so adjudicating a sample of the 273 duplicate pairs and showing within-defect σ below 0.08 (not 0.045 — my sweep puts the first departure between 0.08 and 0.10) removes every flip. 60 adjudicated pairs gives a σ estimate with roughly ±18% relative precision, enough to separate 0.08 from 0.14. (2) The σ=0 nesting claim as written is already refuted on 174/3237 entries; what would refute the *fix* rather than the claim is a promoted magnitude gate, where that 16.12% mass systematically under-counts blockers at the modal severity.

**fable's.** (1) Reach, already measured and failing at the deciding tail: 9/734 = 1.2262%, Wilson [0.6464%, 2.3138%], against fable's own ~10% bar. What would rescue it is a live run with ≥15% of tail entries at k≥2. (2) The estimability degradation on `commissioning_arm1_panel_20260929T214647Z` is the named run where fable's ruler decides worse than fable reported — if an adjudicator shows the downward-crossing star links there are genuine same-defect links, the median is right and the sentinel is the honest answer; if they are mis-links, pooling inherits the linker's noise instead of cancelling the assessor's, which is fable's own refutation condition 3 and I have now located the run it bites on.

## Disagreement

**With cc2, on what the 5/19 was evidence of.** The count alone was not evidence that the fix reaches rather than fits — fable was right that a verdict-moving number is exactly what a fitted knob produces, and cc2 offered the count as though it settled the matter. What settles it is the monotone-nesting sweep, and cc2 did not run it; the nearest thing cc2 ran was the *threshold* sweep, which cc2 itself correctly distinguished as a different question. I have now run the parameter sweep and it comes out cc2's way — 4 departures at the CI floor, nested at all 14 values. So cc2's conclusion survives on evidence cc2 did not produce. That is not the same as cc2 having been right about the standard.

**With cc2, substantively.** "The current ruler is the σ=0 member of this family" is false at exactly sev=0.7, and 0.7 is the archive's third most common severity — 5.3753% of entries, carrying 16.12% of the instrument's total effect. The additive claim should be stated as holding for sev≠θ with the θ case named, not as a clean nesting.

**With fable, on invariance as a desirable property.** I do not accept it as stated, and the evidence is fable's own fix measured over 62 runs instead of 3: it is not invariant (γ moves on 3, estimability dies on 1). More importantly the principle is wrong as a goal. An instrument that cannot move any verdict is not thereby trustworthy — it may simply be unable to reach the gate, which is what 9/734 says about pooling at the deciding tail, and which is the additive standard's "an addition nothing reaches" failure, not a virtue. Invariance is reassuring only once reach has been demonstrated separately. fable's *warning* — that a de-coarsening tuned until it moved an archived verdict would be fitting — is correct and is the better half of that paragraph; it just is not the same proposition as "invariance is desirable."

**With this brief.** It asks whether the fixes compose and offers "the pooling may shrink the variance enough that the smoothing buys nothing" as the reason a composition might be redundant. That mechanism is not what happens. Pooling does shrink the variance — from 0.1419 to 0.0775 at k=4, below the 0.09 half-band, exactly as fable derived — but the smoothing does not stop buying anything, because the shrinkage applies to 9 of 734 entries at the deciding tail and the other 725 are still smoothed at full σ. The composition is null for a reason of **population**, not of variance. That distinction matters for the next round: if multi-attestation rises, the brief's mechanism becomes the live one and the null result expires, whereas the variance argument as stated would have predicted the smoothing becoming *more* redundant as pooling improved.

**Passes run: 2.** Pass 1: the four-ruler archive sweep, the composition null, the structural reach measurement, the module, the wiring, the test. Pass 2: the σ-sweep discriminator, the sev=0.7 mode census and its 16.12% mass, fable's estimability degradation, the naive-versus-correct composition comparison, mutation testing, and the audit-failure attribution by removal. A third pass surfaced nothing above the real-world-consequence threshold, so I stopped.

<!-- verbatim-end -->

## Seat: fable

Route `claude_cli`, 34 recorded tool call(s).

<!-- verbatim-begin: fable (panel joint_the_severity_ruler_2026-10-18) -->

All evidence is in. Three passes run; the third (the annihilation census above) surfaced one scoping precision and nothing more.

---

## Verdict

**Composition: NO — build cc2's smoothing alone.** Measured over all 62 archived catalogues: the composition `Φ((star_median−0.7)/(σ·c_k))` changes the quiescence verdict relative to the smoothing alone on **0 of 62** runs (under both the production last-3 tail predicate and cc2's all-rounds predicate), and it **loses the smoothing's one-way conservatism theorem** — the only archived entries where the two disagree at the 0.5 line are **14 falsifier-CONFIRMED criticals, all 14 pulled below 0.5, none pulled above**.

**The standard: cc2's is right, as qualified — and my blind charge does not apply to cc2's fix.** Movement of an archived verdict is evidence of *reach*, not of *fitting*, when (a) every parameter has provenance independent of the archived verdicts and (b) the movement direction is a theorem, not a tuning outcome; invariance remains the required property only for channels where movement means a vote overriding a tool — which, the measurement now shows, is exactly and only the channel my blind fix occupied.

## Reasoning

**Premise 0 — the sandbox was torn down; both fixes were reconstructed and cross-validated.** Neither seat's files exist (`Glob bench/severity_instrument.py` → nothing; no git). I rebuilt both from the verbatim replies. The reconstruction reproduces cc2's blind numbers through the production caller to 4 decimals: leg3 `gamma_hard=1.0, gamma_soft=0.9597, soft_tail=[0.2541, 0.1184, 0.4248]`, and three of cc2's four zero-hard-series soft gammas (0.4769, 0.6819, 0.7369). That is independent re-execution, not trust.

**Premise 1 — four rulers, one production path, 62 catalogues.** `scripts/do_the_two_rulers_compose_2026-10-18.py` drives `_settled_novelty_series` + `_estimate_gamma` (the exact gate-feeding path) for both indicator rulers (hard, and hard-on-star-median = my blind fix), and a filter-mirrored Φ series for the smoothed and composed rulers; the mirror is verified value-for-value at σ→0 against the production series on **all 62 catalogues, 0 mismatches**. Median-of-k SD constants c_k: k=2 exact 1/√2; k=3,5 by quadrature, confirmed by Wolfram Language to 10 digits (0.6698291607404084, 0.5355685405302014).

**Premise 2 — what each ruler does, named runs:**

| comparison | quiescence changes | gamma movement |
|---|---|---|
| soft vs hard (cc2) | **7 of 62**, all strict (refusing convergence): `commissioning_arm1_panel_20260929T194414Z`, `commissioning_arm3_contrast_20260930T051219Z`, `exp35_pe_20260406T152126Z`, `exp40_slice_collision_20260518T130744Z`, `free_run1_directive_whole_…`, `sim45_memory_20260830T235237Z`, `sim45_postfix_…T231827Z` | e.g. leg3 1.0→0.9597; resolves the 0.0-sentinel regime (arm1_194414Z → 0.4769) |
| pooled vs hard (fable) | **0 of 62** | 3 runs: `commissioning_arm1_panel_20260929T214647Z` 0.3236→**0.0 sentinel** (pooling demotes its only criticals, C0001 0.70→0.66 and C0026 0.72→0.65, **both CONFIRMED**, zeroing the series); `prose_convergence_run1b` 0.2547→0.1928 (crosses the 0.20 `GAMMA_BANDS` edge into "recommend HIL audit"); `study_run1b` 0.6958→0.7279 (same band) |
| composed vs soft | **0 of 62** | 8 runs in the 2nd–3rd decimal; one band crossing: `commissioning_arm1_panel_20260929T214647Z` 0.1952→0.2040, crossing the 0.20 edge in the **permissive** direction (out of the HIL-audit band) |

**Premise 3 — the mechanism that kills the composition, derived then exhibited.** cc2's one-way proof needs `sev ≥ θ ⟹ w ≥ Φ(0) = ½`. Under composition the centre moves to the star median, which can sit below θ while the entry's own asserted severity is above it — so the implication fails structurally. The archive exhibits it 14 times, **every instance a falsifier-CONFIRMED critical**: sharpest, leg3 `C0006` — CONFIRMED at asserted 0.9, star severities [0.9, 0.45, 0.45], composed weight **0.0043**; also `free_run1 C0007` (CONFIRMED 0.9, star median 0.625, w=0.1666). Exercised through the real instrument: `C0006` has `spec_verification_factor = 1.0`, `effective_severity = 0.9` spec-on and spec-off — the harness's own verdict channel says full weight; the pooled centre says near-zero. That is votes overriding a tool, at scale 14/14 and never once in the conservative direction.

**Premise 4 — the guarded composition buys nothing, so either way one fix is built.** My blind reply's promotion guard (a downward crossing may only act on `severity_is_proven` or HIL — the `_apply_severity_calibration` discipline) blocks all 14 crossers, since all 14 are demotions of CONFIRMED criticals without proof. Guarded-composed is then decision-identical to the smoothing alone on every archived entry. Unguarded is strictly worse (loses the one-way theorem); guarded is exactly equal. Under the founder's composability ruling — compose only on a *measured* advantage over each fix alone — the composition is refused in both forms.

**Premise 5 — the evidence that distinguishes reach from fit, which is what the second question asked for.** Three tests, all executed: (1) *parameter provenance* — σ=0.1419 comes from the 273-pair measurement, θ=0.7 is pre-registered and frozen, the 0.5 cut is Φ(0) derived, so there is no free parameter that could have been tuned until a verdict moved; (2) *direction as theorem* — the movement is provably one-way strict, so the fix cannot have been fitted toward permitting convergence, which is the only direction cooking pays; (3) *out-of-sample generalisation* — extending cc2's 24-catalogue sweep to 62 produced **3 new flips cc2 never saw** (`exp35_pe`, `exp40_slice_collision`, `sim45_memory_20260830T235237Z`), all in the same strict direction, with **0 one-way violations**. A fix fitted to cc2's archive subset would not generalise to runs outside it. My pooled ruler's gamma invariance, by contrast, was the honest outcome for a channel where the only available movement was the anti-tool demotion — and premise 3 now proves that channel is anti-tool 14 times out of 14.

**Premise 6 — one scoping precision on cc2's one-way claim.** The annihilation term makes the soft ruler deliberately *more permissive* than the hard ruler on entries with `falsifier_verdict == REFUTED` but a countable status — there "can never permit one it refuses" fails by design. Censused: that population is **0 entries across all 62 catalogues**, so the claim holds unconditionally today, but it is conditional and should be stated so.

## Falsifier and its executed result

```
$ python3 scripts/do_the_two_rulers_compose_2026-10-18.py
catalogues discovered: 62; max star size: 8
mirror mismatches (sigma->0 vs production): 0
quiescence: soft differs from hard on 7: [...named above...]
quiescence: pooled differs from hard on 0: []
quiescence: COMPOSED differs from SOFT on 0: []
ONE-WAY violations, soft permits where hard refuses: []
ONE-WAY violations, composed permits where hard refuses: []
k>=2 entries where composed and soft disagree at the 0.5 line: 14
   ('leg3_final_shakedown_20261015T220118Z', 'C0006', 3, 0.9, 0.45, 0.9206, 0.0043, 'CONFIRMED')
   [...all 14 CONFIRMED, all downward...]

$ python3 -m pytest bench/tests/test_the_two_rulers_compose_2026-10-18.py -q
9 passed in 0.68s
$ python3 -m pytest bench/tests/test_the_severity_spec_decides_when_promoted_2026-10-15.py \
    bench/tests/test_a_declared_mode_is_reconciled_2026-10-18.py -q
38 passed in 4.25s
```

Capability to fail, by mutation (restored after each): re-centring the weight 0.10 low → `4 failed`, including `AssertionError: reach changed: [16 runs]` and `the composition now moves a verdict beyond the smoothing alone`; deleting the REFUTED short-circuit → `FAILED ...::test_refuted_is_annihilated_exactly — a disproved finding must be ANNIHILATED, not merely reduced`. Restored: `9 passed`.

**The other seat's falsifier.** cc2's test file did not survive teardown, so it cannot be run verbatim; I reconstructed it from its printed specification and executed the reconstruction (above). It reproduces cc2's leg3 numbers to 4 decimals and 4 of cc2's 5 named flips. The 5th, `commissioning_arm2_single_20260922T020120Z`, flips **only under cc2's all-rounds predicate** `all(w_r < 0.5)`: its soft series is `[0.5272, 0.2429, 0.1649, 0.0]` — tail quiet, round 0 not — so under the production `tail_is_quiescent` window (last 3) it does not flip. cc2's arm2 soft gamma (0.4757 vs my 0.562) also differs; the other three zero-hard runs match to 4 decimals, so the difference is a population detail confined to that run which I cannot adjudicate without cc2's file — cc2 should recommit it.

Wolfram second-falsifier (local Wolfram Engine via `wolframscript`, exit 0): Φ values `{0.9206479..., 0.7135471..., 0.5}` and quadrature constants `{0.6698291607404084, 0.5355685405302014}`, agreeing with SymPy/SciPy/`math.erf` to 10 digits. One earlier call emitted `Median::rectn` and verified nothing; it was discarded and re-posed. Wolfram-derived values are attributed to Wolfram Language.

## The fix

All written into the sandbox tree and executed:

- **`bench/severity_instrument.py`** — cc2's fix, rebuilt: `critical_weight`, `expected_critical_series`, `tail_is_quiescent_soft`, `instrument_noise_profile`, `SEVERITY_INSTRUMENT_SIGMA = 0.1419` with CI and producer citation. The composition refusal and its 0/62 + 14/14 evidence are in the module docstring. Diagnostic only; the live gate keeps the hard indicator.
- **`bench/reference_runner_v3.py`** — one guarded block in `gamma_threshold_profile` before `return out`, writing `instrument_noise_profile` into every report (compiles; driven on leg3 through the production caller, output above).
- **`bench/tests/test_the_two_rulers_compose_2026-10-18.py`** — 9 tests: mirrored constants, σ→0 value-for-value nesting on all 62 catalogues, Φ(θ)=½, exact annihilation, archive-wide one-way, the 7-run reach list, leg3 via the production caller, pooling's 0/62 (with my blind archive assertions C0001→0.875, C0011→0.64 reproduced), and the composition refusal (0/62 + the 14 CONFIRMED crossers + C0006 pinned).
- **`scripts/do_the_two_rulers_compose_2026-10-18.py`** — the composability measurement itself.

If my answer were wrong, the tests print named `AssertionError`s — "the composition now moves a verdict beyond the smoothing alone", "pooling now reaches the quiescence verdict", "ONE-WAY PROPERTY VIOLATED" — demonstrated above by mutation. **I did not rebuild my blind-round attested-severity stamp.** That is not a removal (teardown removed it; nothing better replaced a live feature) — it is a refusal to re-add on the committed measurement that its gate-adjacent channel reaches 0 of 62 verdicts and its only decision-line action is demoting falsifier-CONFIRMED criticals. The star data remains untouched in the registry for any future, separately-measured use.

## What would refute this

**My answer (the refusal to compose):** (1) An *upward* crosser population appearing in live runs — a star of unresolved findings each asserted below 0.7 whose median crosses above it; the archive has **0** such entries, and if live runs show ≥1 per run the conservative channel of pooling has reach and the guarded composition must be re-measured. (2) cc2's within-defect σ condition, inherited: if adjudication of the 273 pairs shows within-defect σ < 0.045, all 7 flips vanish and both fixes die together — my refusal to compose would be vacuously true but the build recommendation wrong. (3) cc2 recommitting their original test and showing my filter mirror (not merely the predicate scope) misclassifies arm2's population — then my 7-run reach list, and the test pinning it, are wrong.

**cc2's answer:** (1) The same σ < 0.045 threshold — cc2's own stated refutation number, which I checked and endorse as the single sharpest refuter. (2) A verdict-REFUTED, status-countable critical in a live tail: the soft ruler then permits where the hard refuses, voiding premise 4's unconditional "never permit" (population today: 0/62 — but the claim should be scoped now, not after). (3) A real-panel run whose severity distribution has no mass in [0.5, 0.7): soft and hard coincide and the fix reaches nothing outside SIM data — 60 of my 62 catalogues are simulated or pre-attestation, so this remains live.

## Disagreement

**Where I moved, and what moved me.** My blind reply called a de-coarsening that moves an archived convergence verdict "the cooking vector in another coat." Applied to cc2's fix, that charge is **wrong**, and I withdraw it on evidence I generated while trying to break the fix: no free parameter exists to cook (σ, θ, and the 0.5 cut all have independent provenance), the movement direction is a theorem rather than a tuning outcome, and the fix generalised out-of-sample — 3 new strict flips on 38 catalogues cc2 never swept, 0 one-way violations. A fitted fix does not generalise; this one did. That is a changed verdict from execution, not deference.

**Where I hold.** Invariance was and remains the required property for the pooled channel — and the measurement now proves it rather than presumes it: every archived entry where pooling would act at the decision line is a tool-confirmed critical pulled down by co-discoverers' lower votes, 14 of 14. The two standards were never symmetric claims about one fix; they were correct claims about two different channels, and the general rule both instantiate is: **a fix may move archived verdicts iff its parameters are independent of those verdicts and the movement direction is derivably conservative; otherwise invariance is the evidence of honesty.**

**Residual disagreement with cc2, two items.** First, premise 4's "can never permit one it refuses" is unconditional in the text but conditional in fact — the annihilation term is a deliberate permissive divergence; it is unexercised today (0 entries in 62 catalogues) and should be scoped before any promotion. Second, cc2's quiescence predicate `all(w_r < 0.5)` ranges over all rounds; the production `tail_is_quiescent` reads the last 3. The 5/19 figure mixes the two — arm2 flips only under the bespoke predicate. A reach count should be stated against the predicate the runner owns (7 of 62 under the production tail window): a count against a gate that exists nowhere in the runner is the same shape as the `gate_would_fire` block this project already removed once.

**Passes: 3.** Pass 1: reconstruction, the four-ruler sweep, the composition measurement, the build. Pass 2: adversarial — mutation testing, the arm2 discrepancy adjudication, Wolfram second-falsification, the gamma-band-crossing audit (which surfaced the composition's one permissive band move). Pass 3: the annihilation census, which bounded cc2's one-way claim and produced nothing else above the material threshold. Converged: the remaining open items are named refutation conditions, not unexamined mechanisms.

<!-- verbatim-end -->

## Where the raw record lives

`bench/logs/joint_the_severity_ruler_2026-10-18/` holds the brief, every seat reply, the tool logs and `seat_proposals.diff`. That directory is excluded by `.gitignore:41`, so a byte-identical copy is committed under `experimental_notes/evidence/`, verified by sha256 and checked on every suite run by `bench/tests/test_panel_records_are_preserved_2026-09-11.py`.


Written under CDSFL note standard v1.7 (26 August 2026).
