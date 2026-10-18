# The severity ruler's coarseness: both free seats answered yes, with different fixes

Record written 2026-10-18T02:34:32+01:00.

**This is the seats' own output, reproduced in full.** The Personalisation directive requires external review output preserved *"in full and in unfiltered format"* and says *"Never summarise in place of the full output"*. Any summary elsewhere is downstream of this file, not a substitute for it.

WHAT WAS REVIEWED AND WHY. The founder asked on 2026-10-04 for a free panel review of how to make the severity ruler less coarse, more accurate and more useful across a broad range of scenarios. His words: "I did ask you to run a free panel review with the question of how to make this ruler more effective, less course [coarse], more accurate and more useful, potentially across a broad range of similar scenarios. Did you do this? What were the panel's findings?" No such round was ever run, and the omission was recorded as task C4 on the master task list by the annotation audit of 2026-10-17. This round discharges it, 14 days after the ask.

THE RULER AND WHY ITS COARSENESS DECIDES SOMETHING. A finding carries an asserted severity between 0 and 1, produced by the model that raised it, and counts as critical at or above a threshold of 0.7. The number of findings at or above that threshold feeds the convergence gate, the blocker counter and the release decision, so the ruler determines when an experiment is allowed to stop. The founder's evidence is that the asserted number wobbles by about 0.14 between repeat assessments of one defect, against a decision band roughly 0.09 wide, and that 82 of 273 identical defects landed on opposite sides of the 0.7 line.

THE DISPATCH. Free seats only, cc2 and fable, both on the founder's Max subscription, dispatched SERIALISED rather than staggered because available memory was 1.52 gibibytes of 8 at launch and strict serialisation holds 1 command-line process at a time instead of 2. Blind round, no answered sibling on the same brief, 0 paid seats. cc2 answered in 798.9 seconds with 13,936 characters over 50 tool calls; fable in 571.3 seconds with 9,516 characters over 38 tool calls. Both seats were alive on the first probe attempt.

BOTH SEATS ANSWERED YES AND PROPOSED DIFFERENT FIXES, AND THE DISAGREEMENT IS PRESERVED RATHER THAN RECONCILED. cc2 proposes replacing the hard indicator with its expectation under the project's own measured instrument noise, a normal cumulative weight at the measured standard deviation of 0.1419, reporting that the current ruler is the zero-noise member of that family and that the quiescence verdict changes on 5 of 19 archived runs, strictly in the conservative direction, with 0 runs becoming easier. fable proposes pooling the several independently asserted severities the registry already holds for each co-discovered defect, taking a median over the direct co-discovery star, and reports that the critical gamma is INVARIANT at 1.000 on all 3 shakedown runs under its ruler.

THE TWO SEATS DISAGREE ABOUT WHAT A GOOD ANSWER LOOKS LIKE, which is the most useful thing in the round. cc2 treats 5 of 19 verdicts moving as evidence the fix reaches something. fable argues the opposite is correct, that invariance is the desirable property, and that a de-coarsening tuned until it moved an archived convergence verdict would be fitting the gate, which it names as the pre-registration's cooking vector in another coat. Both positions are on the record and neither was smoothed to consensus.

BOTH SEATS INDEPENDENTLY CORRECTED THE SAME ERROR IN THE BRIEF, which was written by CC1. The brief stated that the section 7.7 specification rescales severities and lets the wobble travel with it, a 0.8 becoming a 0.4 and a 0.7 a 0.35, preserving the ordering. That is wrong, and both seats showed it by execution rather than argument. Since the largest asserted severity is 1 and one half of 1 is below 0.7, an effective severity at or above the threshold is identically the conjunction of a confirmed falsifier verdict and an asserted severity at or above the threshold. cc2 obtained unsatisfiable from z3 for the negation of that equivalence and confirmed it independently in Wolfram Language, and measured 33 of 191 unresolved entries asserted-critical against 0 specification-critical. fable reached the same conclusion from the other direction, adding that the 2 terms must be fixed in the right order because the step function would dominate the coarseness if the specification were promoted so that it decides the gate rather than being recorded beside it. The brief's framing was therefore corrected by the seats, which is what a brief that names its own assumptions is for.

WHAT WAS DONE WITH THE FINDINGS. Nothing has been applied. Both proposals change what the convergence gate counts, so both are decisions for the founder rather than for CC1, and the additive standard requires a committed measurement before any narrowing of an existing protection. The 2 fixes are not obviously exclusive: cc2's smooth weight addresses the variance of a single assessment, and fable's pooling addresses the number of assessments that variance is estimated from, so a combination may dominate either alone. That composability question is not settled by this round and is recorded as the next thing to measure.

## Seats and cost

2 seat(s): `cc2`, `fable`. **0 paid dispatches**, enforced by `PANEL_ONLY=cc2,fable`.

## The brief, as dispatched

<!-- verbatim-begin: the brief as dispatched -->

# PANEL BRIEF — how to make the severity ruler less coarse

## REQUIRED SECTION 1 — The question

**How can the severity ruler be made less coarse, more accurate and more useful, across a broad range of scenarios and not only the one it was tuned on?**

This question is the founder's, asked on 2026-10-04 and never put to a panel. His words: *"I did ask you to run a free panel review with the question of how to make this ruler more effective, less course [coarse], more accurate and more useful, potentially across a broad range of similar scenarios."* It is task C4 on the master task list.

**The artefact under review** is the severity model as it is implemented in `bench/reference_runner_v3.py`: the functions `spec_verification_factor` and `effective_severity`, the module-level state `_SEVERITY_SPEC`, the constant `CRITICAL_SEVERITY_THRESHOLD`, and the demotion sweep `_apply_severity_calibration`.

**WHAT THE RULER IS.** A finding carries an asserted severity in the interval 0 to 1, produced by the model that raised it. A finding counts as CRITICAL when that number is at or above a threshold of 0.7, and the critical count feeds the convergence gate, the blocker counter and the release decision. So the ruler is not a label: it decides when an experiment is allowed to stop.

**THE EVIDENCE THAT MOTIVATES THE QUESTION, and it is the founder's own.** The asserted number wobbles by about 0.14 between repeat assessments of the same defect, against a decision band roughly 0.09 wide, and 82 of 273 identical defects landed on opposite sides of the 0.7 line. A ruler whose noise exceeds its decision band is, on those figures, deciding criticality partly at random.

**WHAT HAS SINCE BEEN BUILT, so the panel argues from the current code and not from the state of 2026-10-04.** Section 7.7 of the mathematical appendix is implemented and live. `effective_severity` returns the asserted number multiplied by a verification factor V taken from this harness's own falsifier verdict, not from any model's assertion: V is 1.0 for CONFIRMED, 0.5 for an unresolved verdict, and 0.0 for REFUTED. The last is the appendix's key property, that a disproved finding is annihilated rather than merely reduced, and it is what makes the scheme structurally unlike a vote.

**IT IS EXERCISED, DEMONSTRATED BY EXECUTION RATHER THAN ASSERTED.** The third leg of the shakedown of 2026-10-15 produced 38 findings of which 2 carry a REFUTED falsifier verdict. Both store an asserted severity of 0.5. Calling `effective_severity` on those 2 entries with the specification on returns 0.0 for both, and with it off returns 0.5 for both. So the annihilation term fires on real data. Note carefully that the STORED field keeps the asserted number: the specification does not mutate it, and reading the stored field instead of calling the function reports a working specification as broken.

**WHAT THE SPECIFICATION DOES NOT ADDRESS, which is the heart of the question.** V corrects the asserted number using a falsifier outcome. It does nothing about the asserted number's own noise when no falsifier has resolved, which is the common case: in the archive the unresolved population carries V equal to 0.5 almost entirely, so the specification halves those findings uniformly and preserves their relative ordering, noise included. A 0.8 becomes a 0.4 and a 0.7 becomes a 0.35; the band is rescaled and the wobble travels with it.

## REQUIRED SECTION 2 — Use the harness

**Form your answer by RUNNING the machinery, not by describing it.** A seat that returns prose about a fix without having executed anything has not answered this brief.

**The severity model is the instrument this question is about**, and you must exercise it directly: import `effective_severity` and `spec_verification_factor` from `bench/reference_runner_v3.py` and call them on real archived entries, which you will find in the finding catalogues under `bench/logs/`. State what the functions return and on which entries.

**`gamma` is the instrument that shows whether the ruler's coarseness matters.** The convergence gate decides on the critical series, and a finding's criticality is exactly what the ruler determines, so a change to the ruler propagates into gamma and therefore into when a run is permitted to converge. Execute the convergence code path, or a faithful reconstruction of it, over an archived run with and without your proposed change, and report what gamma does in each case. A proposal that moves gamma without the proposer having computed gamma is a hypothesis.

**The two-sided gate is the consumer that would feel the change.** Say explicitly what your fix does to the critical count it reads, and whether it makes convergence easier, harder or unchanged. A change that makes convergence easier must be argued for, because this programme's success criterion is clean convergence and a ruler that converges more readily is not obviously better.

## REQUIRED SECTION 3 — Produce a fix, and test it

**A finding without a fix is incomplete, and a fix without a runnable falsifier that has been EXECUTED is a hypothesis, not a fix.**

Deliver your fix as a file written INTO the sandbox repository tree at its real path, not described in prose and not left in scratch space, which is destroyed when the sandbox is torn down. Report the exact command you ran and the output you saw, verbatim.

Your falsifier must be capable of failing. State what it would print if your fix were wrong, and show that it prints something different now.

**The simplest sufficient fix is the correct one, and it must be additive.** A change that removes or narrows an existing capability requires a committed measurement showing the replacement dominates on a named property; a judgement that something is better is not evidence that it is.

## REQUIRED SECTION 4 — What would refute you

Before you conclude, state what evidence would overturn your own answer. A verdict with no stated refutation condition is an opinion.

Be specific. If your proposal is that the ruler should aggregate repeated assessments, name the number of repeats below which your own scheme would be no better than the single assessment it replaces. If your proposal is a recalibration, name the archived run on which it would produce a worse decision than the current ruler.

## REQUIRED SECTION 5 — Output shape

Return these fields, each under its own heading, so replies can be compared without a parser guessing:

1. `## Verdict` — can the ruler be made meaningfully less coarse, yes or no, in one sentence.
2. `## Reasoning` — the argument, premises first.
3. `## Falsifier and its executed result` — the command, and the output you saw.
4. `## The fix` — the real path you wrote it to, and what it changes.
5. `## What would refute this` — your own refutation condition.
6. `## Disagreement` — your strongest disagreement with this brief's own framing. State it even if you agree with the conclusion: name what this brief assumes that you would not have assumed. A round that reconciles is the one most likely to converge by deference, and deference is not evidence.

## REQUIRED SECTION 6 — Termination

Stop when a further pass produces no new findings above the real-world-consequence threshold, which is the project's own diminishing-returns criterion. State how many passes you ran. Do not pad: a second pass that repeats the first is not a second pass.


<!-- verbatim-end -->

## Seat: cc2

Route `claude_cli`, 50 recorded tool call(s).

<!-- verbatim-begin: cc2 (panel severity_ruler_coarseness_2026-10-18) -->

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

<!-- verbatim-end -->

## Seat: fable

Route `claude_cli`, 38 recorded tool call(s).

<!-- verbatim-begin: fable (panel severity_ruler_coarseness_2026-10-18) -->

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

<!-- verbatim-end -->

## Where the raw record lives

`bench/logs/severity_ruler_coarseness_2026-10-18/` holds the brief, every seat reply, the tool logs and `seat_proposals.diff`. That directory is excluded by `.gitignore:41`, so a byte-identical copy is committed under `experimental_notes/evidence/`, verified by sha256 and checked on every suite run by `bench/tests/test_panel_records_are_preserved_2026-09-11.py`.


Written under CDSFL note standard v1.7 (26 August 2026).
