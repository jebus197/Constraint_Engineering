# Morning report, 21 September 2026

21 September 2026 01:42 BST (Europe/London)

## The short answer to the founder's question

He asked: *"as we identified the core of the model itself remains largely unchanged? These are just corrections and qualifications? Correct?"*

**Yes, with one amendment that arrived overnight.** Across this review arc exactly **1 line** of `docs/MATHEMATICAL_APPENDIX.md` had changed before tonight — commit `8a0952a`, the inverse sign at line 169, which the proposed revision named first. The free panel then found a **second genuine correction**: the stated substrate ceiling is true but loose by a factor of 1/q. That is a tightening of a bound, not a change to any equation, and the equations remain untouched.

So the answer is still yes — corrections and qualifications — but there are now **3** corrections rather than 1, and 2 of them matter operationally. All 3 are tightenings of statements *about* the equations. **No equation changed.**

The night's deepest challenge was mounted by the assistant against the model itself, and the model won. Every other finding is an implementation defect or a property derived from the unchanged equations.

| What it looked like | What it turned out to be |
|---|---|
| Phase 2 wrongly reverts to the prior | **REFUTED.** It is the tower property. The appendix is right. |
| A new critical re-injection rate | The appendix's **own** break-even rate, read at R = 1 |
| A new bounded-recursion theorem | A theorem **about** the unchanged model, derived from it |
| The scoring gate was broken | Implementation, not model |
| Containment, record-keeping | Implementation, not model |
| The stated substrate ceiling `lim R ≥ ν` | **TRUE BUT LOOSE BY 1/q.** A real correction, the second. |
| The stopping-rule gloss on ΔR | **ΔR is unimodal, not monotone.** A third correction. |

So "corrections and qualifications" is right, with one honest amendment: it undersells what happened. The core did not merely survive unchanged; it survived a tool-executed attempt to refute it and came out with a stronger warrant than it went in with.

## The assistant was wrong about Phase 2, and both free seats caught it

The assistant proposed that the appendix's Phase 2 discards evidence. `R_det` is the posterior given no detection; at σ = 0 the appendix returns risk to `R_old`, and the assistant argued that a failed fix does not un-observe the pass that produced `R_det`.

**The premise was right and the conclusion was wrong.** `R_det` is only the non-detection posterior under `P(detect|flaw) = q` and `P(detect|no flaw) = 0`, and those assumptions force a second branch: detection, probability `q·R_old`, posterior 1, risk `1 − σ` after repair. The mixture is `R_old·(1 − q·σ)` — exactly `R_old` at σ = 0. The observation happens on **both** branches, sometimes reporting "clean" and sometimes "flaw found", and unrepaired they average back to the prior. That is `E[posterior] = prior`.

The appendix does not discard the observation. **The proposed revision discards the unfavourable half of it**, keeping only the branch where nothing was found.

Two free seats reached this independently, by different derivations, in one round. Verified again afterwards on SymPy and z3 rather than taken on trust.

**A second defect in the revision, which the assistant missed entirely.** At σ = 1, ν = 0 the revision returns identically 0 for every state — one successful fix asserting certainty of no residual risk, contradicting the appendix's own substrate ceiling. And at σ = 0 it returns `R_det < R_old`, understating risk exactly when fixes fail, which is the worst direction for a verification framework.


**WITHDRAWN 2026-09-21, MIS-SCOPED.** Executed against the revision's own `expected_binary_review`, the procedure returns **1/10** on its worked example, not 0: it averages BOTH observation branches. The `returns 0` result is true of `update()`, the single-branch action step, and false of the revision's §4 procedure. CC1 adopted it from the seats without running the revision's own code. The revision also already carries a `false_positive` parameter, so the φ gap CC1 reported as missing is **already specified there**.

**A methodological criticism worth keeping.** One seat observed that the assistant's 200,000-point sweep, maximum-gap and satisfiability analysis were all correct and all beside the point: they established that the two maps differ, which was never in dispute, and were silent on which is right. The deciding evidence was a 3-line identity the sweep cannot see. Volume of cross-verified numerics is not a substitute for the right derivation.

## What changed in the appendix, and it is documentation only

**43 lines added, 1 line removed** — and the 1 removal is a false table row replaced by 2 correct ones. **No equation was touched.**

1. **The σ = 0 endpoint is now derived rather than asserted.** The old gloss stated the endpoint without showing it, and that is what invited the misreading. The total-probability derivation is now in the text.
2. **Phase 2's conservatism is recorded.** The blend interpolates between a quantity conditional on non-detection and a marginal expectation, so it is exact only at σ = 0. The gap is `R_old²·q·σ·(q−1)/(R_old·q−1) ≥ 0`, with z3 returning unsatisfiable for any point where the blend falls below the exact mixture. **It never understates risk.** For a gate deciding when it is safe to stop looking, that is the correct bias, and `R_k` should be read as a conservative bound rather than a calibrated probability.

## A second real correction: the stated floor is loose by 1/q

The appendix states the substrate ceiling as `lim R ≥ ν_k`. That is a valid lower bound and it is **not the floor the recursion actually reaches**. At σ = 1 the composite map has exactly 2 fixed points, `{1, ν/q}`, and the attracting one is **ν/q**. Since q < 1 the true floor is strictly higher, so the appendix has been **optimistic about how far a review loop can drive residual risk down**.

| q | ν | stated floor | true floor ν/q | orbit of the shipped `compute_rk`, 20,000 cycles |
|---|---|---|---|---|
| 0.2 | 0.05 | 0.05 | 0.25 | 0.2500000000 |
| 0.1 | 0.02 | 0.02 | 0.20 | 0.2000000000 |
| 0.5 | 0.10 | 0.10 | 0.20 | 0.2000000000 |

At q = 0.2, ν = 0.05 the reachable floor is **5 times** the stated one. The implementation was already doing the right thing; only the documented bound was loose.

**And an operational hazard that follows from it.** The interior fixed point leaves the unit interval above `ν_c = qσ/(qσ − q + 1)`, which is **exactly the appendix's own break-even ν\* at R = 1** — so the "new second condition" the earlier review reported is a coherence result, not an addition. At σ = 1 it reduces to ν_c = q, and **exactly at ν = q the fixed point is parabolic**: the derivative at R = 1 is 1, so approach to certain failure is O(1/n) rather than geometric. A run there converges to R = 1 so slowly that successive differences look like a flattening curve. The Hard Exit fires on ΔR_n = 0 over successive passes, so **it will read approach-to-certain-failure as a substrate ceiling reached** — the opposite conclusion. A seat found this by having its own falsifier fail: an assertion of 1e-6 after 4,000 iterations returned 0.9953.

Both are now recorded in the appendix. 28 lines added, 0 removed, no equation touched.

## A third correction, and it bears on stopping decisions

The appendix glosses the per-cycle gain with *"the less risk remains, the less there is to gain"*, and derives the stopping rule *"continue while Σ w·ΔR > θ"* from it. **ΔR is not monotone in R.** SymPy locates a maximum at `R* = (1 − √(1−q))/q`, second derivative −2q/√(1−q) < 0 there, with z3 unsatisfiable for any R that beats it. Above that peak the relationship inverts: as risk falls towards R*, the gain **rises**.

The consequence bites at the worst moment. At q = 0.3 the peak gain is 0.088933 at R = 0.544467, but at R = 0.99 it is only 0.004225. With θ = 0.05 the greedy rule says **STOP across R ∈ [0.855089, 0.999999]** — a band 0.144910 wide, at the highest-risk states in the interval, where continuing a few cycles would reach a gain 21 times larger. **The rule tells you to stop precisely when the artefact is most likely flawed.**

The formula is unchanged and correct; the sentence attached to it needed qualifying, and now carries it. A practitioner should either start the rule once R is below R*, or read a low ΔR at high R as "not past the peak yet" rather than as exhaustion.

## The scorer: fixed, then found wanting, then fixed again

**The defect.** `compute_sk` produced the number `compute_rk` uses as σ. Appendix line 214 defines σ as *"Does the proposed fix actually resolve the detected flaw?"* and line 377 admits it only as a comparison of pre-fix against post-fix output. All 3 effect gates measured absence of harm instead.

Executed: a real repair, a no-op leaving the bug untouched, a fix swapping division for multiplication, and one gutting the function to `return None` all scored **sk = 1.0 ADMISSIBLE**, identical to 4 decimal places.

Measured over the 135 archived entries carrying both a verdict and a probe result, `sk` is statistically independent of whether the fix worked: 104 that cure their own falsifier mean 0.950140, 31 that do not mean 0.950206 — higher — identical medians at 0.978200. Mann-Whitney p = 0.746836, Welch p = 0.421469, Kolmogorov-Smirnov p = 0.900813, seeded permutation p = 0.627119. 4 tests, none rejecting. 31 of 31 ineffective fixes admitted, Wilson [88.9745%, 100.0000%].

**The repair adds no apparatus.** `bench/fix_efficacy.py` already applied each fix to a disposable copy and re-ran the finding's own falsifier — precisely the comparison line 377 requires — and was "contributory, never gating". It is now a 4th effect gate `e1_efficacy` at weight 2.0. Same entries after: gap +0.285672, Mann-Whitney p = 1.428e-18, Welch p = 9.274e-50, Kolmogorov-Smirnov p = 6.295e-31.

**Then a seat broke it.** Dropping the "probe could not return a verdict" case from the weighted mean created a gradient that **pays for destroying the instrument**: letting the falsifier run and fail scored 0.6, crashing it scored 1.0, a premium of **+0.4000**, and downstream that turned risk-up 0.516729 into risk-**down** 0.441176. All **18 of 18** archived records of that case are the post-baseline one, Wilson [82.4121%, 100.0000%] — the fix broke a working instrument, not an instrument that was never there.

**Repaired.** That case now carries its own outcome name rather than sharing one, and `compute_sk` returns ESCALATE on it: no verdict, no reward, `R_k` unmoved, a human looks. Not scored 0, because the 18 detail strings do not separate a patch that broke the test from a timeout that broke it, and 0 would assert something unmeasured. Crashing the probe now costs −0.6000 instead of paying +0.4000.

## The scorer repair improves the defect and does not close it

A seat established this and declined to propose a fix, which was the right call. A fix **measured not to cure its own falsifier** still scores 0.714286 with all 3 harm gates clean, and that number is handed to `compute_rk` as σ.

**No finite weight can close it.** For such a fix, `sk = 5/(5 + w)`: at w = 2 it is 0.714286, at w = 8 it is 0.384615, at w = 100 it is 0.047619, reaching 0 only in the limit. **The dilution is a property of the arithmetic mean, not of the weight**, so re-arguing 2.0 against 4.0 cannot close it.

**And while `e4_bandit` is a constant there is a hard floor under σ itself.** With e1 = e2 = e3 = 0 and e4 = 1, `E = 2/7 = 0.285714`, and z3 returns unsatisfiable below it. `compute_rk` can never be told "this fix resolved nothing."

**What the repair did achieve, measured.** It lowered that structural floor from 0.400000 to 0.285714, a reduction of 0.114286, and it separated curing from non-curing fixes where nothing separated them before. It is a genuine improvement that does not close its stated defect, and saying otherwise would overstate it.

The only route inside existing apparatus is the one the code's own comment names: *"If a gate is genuinely non-negotiable, it belongs in the hard gates"*, because that term is multiplicative and would make the efficacy gate decisive. That changes what reaches a verdict, so it is decision 1 below rather than something done overnight.

## Three smaller defects, all found by execution

1. **`e4_bandit` has zero variance across 902 decisions at the heaviest weight.** It is not broken — fed `shell=True` it returns 0.5, fed `eval` as well 0.3 — it had nothing to catch at 40% of the weight. That floors `sk` at 0.4 (SymPy minimum 2/5, z3 unsatisfiable below), so the disputed threshold **0.395043 was unreachable by construction** and could never have refused anything.
2. **A rejection could never name the gate that failed.** `_rejection_lines` compared gate records to the number 0, and every record is a small structure, so the list was always empty and every rejection read "hard gate returned 0" while the record held `ParseError: '(' was never closed`.
3. **A round with a brief and no replies was required to publish a full record of them.** `holds_review_output` is true for a brief alone. 2 such rounds exist, and one postdates the ruling — it escaped only because the guard reads the live directory and that copy sits in the mirror. Fixed with a separate `was_dispatched` predicate; the mirror still preserves briefs, because narrowing the inclusive predicate would have fixed a guard by removing a preservation.

## Astra's revisions: the premise was wrong, and the founder's caution was right

He warned: *"Be careful with Astra's revisions to our docs. They may no longer fully hold."* Correct, and measurably so.

**There is no revised explorer anywhere on this machine.** `explorer/index.html` and the standalone copy are byte-identical, same md5. What the review package's own math-review folder holds — outside this repository, under the Responses directory — are the **input copies Astra was given**, not revisions: across README, the appendix, PAPER and EXPERIMENTAL_RESULTS the only substantive difference from today's repo is the line-169 sign, plus trailing blank lines. Astra read the repository as it stood on 2026-09-10; it has moved 11 days since.

The maths review does mention the explorer, and clears it: it records that the explorer already distinguishes the achieved floor from the ν bound and does not treat that as a defect.

## A read-only audit of the whole revision package, and what it found

An 8-document audit ran over Astra's unreviewed outputs, with every claim checked against the **live** repository rather than the one Astra read, and staleness treated as a first-class verdict. 25 claims reached a verdict: **21 actionable, 1 wrong, 2 already done, 1 stale.** Every verdict was reached with SymPy *and* a second independent tool, as the brief required.

**I have applied 1 of the 21 and reported the rest.** They are changes to what the model says about its own assumptions, and that is your call, not a thing to do at 2am while you are asleep.

**The one I applied, because the appendix contradicted itself.** The Reduction Properties table read *"η = 0 | q = 0, R unchanged"* with no condition on ν, while the 2 rows above it already qualify σ = 0 by ν. At η = 0 detection vanishes so resolution is a no-op — but re-injection is not, and §1.1 says so explicitly: *"A failed fix that modifies code still carries re-injection risk."* The cycle returns `R(1−ν) + ν`, strictly greater than R for every R < 1 and ν > 0. SymPy confirms and z3 returns unsatisfiable for any point where it does not. The row is now split, matching the table's own pattern. A redundant finding is not free.

**The strongest theme across the rest, and several findings converge on it independently.** The appendix's observation model presupposes **no false positives** — that a report is never produced for a clean artefact. That is exactly the assumption the free panel's two-branch derivation leaned on in the same night, arrived at from the other direction. Adding a false-alarm rate φ would change the negative update to `(1−q)/(1−φ)` and stop the positive branch implying certainty. This is the single most consequential item in the set, and it is a modelling decision rather than a correction.

**I verified that theme myself, and it has a direction worth knowing.** The general posterior given no report, with a false-alarm rate φ, is `R(1−q) / (R(1−q) + (1−R)(1−φ))`. SymPy reduces it to the appendix's `R_det` exactly at φ = 0 and **only** at φ = 0. So the appendix's detection posterior is the no-false-alarms special case, and the assumption is nowhere stated. A non-zero φ makes the true posterior **higher** than the appendix reports — at R = 0.5, q = 0.3 the gap is +0.012478 at φ = 0.05 and +0.070994 at φ = 0.25 — and z3 returns unsatisfiable for any point where the appendix exceeds the general form.

**So the appendix carries 2 biases and they point in opposite directions.** Phase 2 is conservative: it never understates risk. The detection posterior is optimistic: it treats a clean report as stronger evidence than it is whenever false alarms are possible. Neither is a defect on its own, both are now measured, and which dominates in practice depends on a false-alarm rate nobody has estimated. That is worth knowing before either is called a safety margin.

**Other recurring items, reported not applied.** The stopping-rule gloss at line 205 attaches a greedy "continue while" reading to a quantity that is unimodal in R, peaking at `R* = (1 − √(1−q))/q`, so the rule misbehaves either side of that peak. The exact asymptotic limit `R* = ν/(q(σ + ν(1−σ)))` should be stated rather than left as an inequality — **which is the same correction I derived independently tonight and have already made.** Several claims ask for assumptions to be named that the appendix relies on and nowhere states.

One claim was judged outright **wrong**, and one **stale** — the second being precisely the category you warned about.

## The largest finding of the night, and it is latent

**Detecting and correctly fixing a real flaw that happens to be published can only raise modelled risk.** Never lower it.

The mechanism. `η_combined = η_int·(1 − c_ext·(1 − ν_k))`, so at ν_k = 0 with full literature coverage c_ext = 1 the combined novelty is 0. Since `q = η·d·p` enters the Bayesian update, q = 0, the detection phase is a no-op and `R_det = R_old`. Phase 3 is not a no-op, so the full cycle returns `R_old·(1 − ν) + ν`, and

> R_new − R_old = ν·(1 − R_old) ≥ 0

Verified on 3 independent tools: SymPy gives the identity, z3 returns unsatisfiable for any point where such a cycle reduces risk, and 200,000 NumPy samples produce 0 counterexamples with a maximum residual of 1.1e-16.

**Why that is uncomfortable.** A detection's evidential weight ought to depend on whether the flaw is really there and on how good the detector is — not on whether somebody else published it first. A replication is evidence. Under the current coupling, a reviewer who finds a genuine defect in your artefact makes your modelled risk **worse** if the defect is well documented elsewhere.

**Where I disagree with the audit that found it.** It reported this as the appendix contradicting itself, citing the rule that a suppression weight *"must NEVER enter q_eff"*. That rule governs `w(f)`, the corroboration suppression weight, not `c_ext`, so it is not the same statement and I will not report it as one. The appendix is also explicit that the projection is deliberate: it says the two dimensions are never collapsed *before reporting*, and that `η_combined` *"projects them into a scalar for the state equation — this projection intentionally compresses information"*. That is a stated design choice, not an oversight.

**What does stand is a tension of principle, in the appendix's own words.** Beside that ban it records why it exists: *"Findings confirmed by multiple sources should strengthen the Bayesian update"*, and that breaking the rule once cost a 113-fold residual-risk overestimate in April 2026. External corroboration is confirmation by another source. The coupling makes it weaken the update instead.

**Severity, measured, and it is the reassuring part.** The channel is live in code but armed by no shipped configuration: **0 of 39 archived run files carry `c_ext` at all**, Wilson [0.0000%, 8.9667%], cross-checked against statsmodels. **No archived result is wrong.** This is a question about a rule and about unarmed live code, not a contamination.

It is a model-semantics decision rather than a defect with an obvious repair, so it is yours. It is decision 5 below.

## Decisions for the founder

**1. Should a fix that demonstrably fails its own falsifier be admissible at all?** It still is. The gate informs σ; it does not veto. All 31 archived non-curing fixes remain ADMISSIBLE, now at sk ≈ 0.6 rather than ≈ 0.95 — the repair changed the σ fed to `R_k`, not admission. The code's own comment says where a non-negotiable check belongs: the hard gates. That changes what reaches verdicts, so it is the founder's call.

**2. A second gradient, created by the same gate, and this one has no neutral answer.** Attaching no falsifier leaves the gate unavailable and scores 1.0; attaching one that fails scores 0.6. So a model that doubts its own fix is better off attaching nothing. 29 of 198 archived probe outcomes are exactly that case, 14.6465%, Wilson [10.3954%, 20.2433%], and `falsifier_gate_enabled` defaults to False, so nothing counters it. Closing it means deciding that a missing falsifier should score **below** a present-but-failing one, which is a policy choice rather than a defect with a right answer.

**3. Where the bounded-recursion theorem belongs.** The paid panel said the appendix's falsifiable-claims table, 6 seats to 1. A free seat disagrees with better reasoning: that table holds **empirical** claims with bench failure criteria, and a tool-proved theorem is not one. Its proposal is to put the theorem beside the Reduction Properties table, and to put in the falsifiable-claims table only its testable consequence — that runs with measured ν above ν_c = qσ/(qσ−q+1) fail to converge below certainty, refuted by an archived run above ν_c whose risk series converges to an interior value.

**5. Should external literature coverage be allowed to zero a detection's evidential weight?** The section above. Three options as I see them: leave it (the projection is documented and deliberate), decouple `c_ext` from `q` so literature coverage becomes reporting-only while `ν_k` alone carries novelty into the update, or keep the coupling and add a floor so a real detection can never score zero. Each changes what a run computes, and nothing in the archive is affected either way.

**4. Whether to charge the project for the §7.12 degeneracy** it has carried unmeasured since 31 March 2026. Unchanged from yesterday; still open.

## State

Suite, qc sweep and an 8-document staleness review of Astra's outputs were still running when this was written, and their results are recorded in the session rather than here.

**FIGURE PROVENANCE.** Every percentage, p-value, interval and derived quantity in this report is regenerated by a committed script. Nothing here is a number typed into prose.

| Figures | Producer |
|---|---|
| The archived S_k distribution, per-gate variance, the 0.4 floor, the 4 independence tests | `scripts/scorer_discrimination_2026-09-20.py` |
| The crash gradient, the weight-independent dilution, the 2/7 floor under sigma | `scripts/scorer_gate_limits_2026-09-21.py` |
| Phase 2 against the revision, the two-branch derivation, the false-alarm analysis | `scripts/phase2_prior_vs_posterior_2026-09-21.py` |
| The true floor nu/q and its orbits, the parabolic point, the stopping-rule peak and band, the novelty coupling and its severity bound | `scripts/appendix_corrections_2026-09-21.py` |

Each answers `--help` without running anything, reads only `bench/logs`, writes nothing and dispatches to no model.

Written under CDSFL note standard v1.7 (26 August 2026).
