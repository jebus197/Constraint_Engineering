# Maths Revision Review: Synthesis of 6 Paid Panel Rounds

**20 September 2026, 23:05 BST**

## What Was Decided

A proposed revision to the project's mathematical model, produced by an unbounded frontier model asked to improve it, was reviewed across 6 paid panel rounds by 7 seats. The founder's question was whether the project needs the revision, or whether it is unbounded model churn.

**The answer is neither, and the review's own framing was wrong.** The revision is largely a correction list, as every returning seat concluded from round 3 onward. But the falsifiability defect the review spent 5 rounds charging to the revision **is already in this project's own appendix**, at §7.12, and has been since 31 March 2026. The revision did not introduce it. It made it visible.

## The Rounds

| round | seats returning | seat output |
|---|---|---|
| 1 | 6 of 7 | 69,131 chars |
| 2 | 5 of 7 | 67,500 |
| 3 | 5 of 7 | 78,653 |
| 4 | 7 of 7 | 101,895 |
| blind | 7 of 7 | 103,307 |
| open | 7 of 7 | 118,234 |
| **total** | | **538,720** |

Rounds 1 to 3 lost seats to defects in this project's dispatch machinery, all since repaired: the paid seats had no tool that could read a file; the empty-content retry existed in one tool loop and not in the one the paid seats ran; and a forced-synthesis call hardcoded a temperature that one seat's endpoint refuses.

Seats: `cc2` and `fable` on the founder's existing subscription, `cx`, `cgpt`, `ge` and `ds` through OpenRouter, `kimi` on Moonshot credits. Authorised ceiling 12 pounds; spend across all 6 rounds remained well inside it.

## Finding 1: The Degeneracy Was Ours

The `cc2` seat, working **blind**, established that appendix §7.12 carries the identical degeneracy the review had been charging to the revision. Under the substitution `ν = 1−s`, `ε = b(1−z)`, §7.12's recursion is the revised action step term for term, and the fixed points coincide exactly at `b/(b+s)` with a SymPy residual of 0.

The seat's own words: *"they are one object in two coordinate systems"*, and *"rejecting the revision on T1 grounds requires rejecting §7.12 on identical grounds. The revision does not introduce the degeneracy; it makes visible one the project already shipped. That is an argument for adoption, not against."*

**5 further seats adopted this in the open round, and every one re-derived it rather than taking it on trust.** `fable` confirmed the substitution is an exact identity before accepting it; `kimi` adopted the conclusion while attacking the proof in the same finding.

## Finding 2: CC1's Headline Claim Was False

CC1 reported to the founder, and wrote into a paid brief, that 191 archived fixes had been refused on the strength of a constant nobody measured.

**Measured on both refusal paths, the unmeasured constants decided nothing.** All 191 refusals are structural, refused at `sk == 0` before any constant is read (`reference_runner_v3.py:10896`). Of the 902 scored fixes that reached the gate, **0 were refused**, Wilson [0.0000%, 0.4241%].

**The repository already recorded this**, pinned by a committed test, at `reference_runner_v3.py:11820`: *"passes_threshold reads false 0 times under every method and every corpus tried. The gate has never rejected a fix."* CC1 contradicted a test-pinned measurement without consulting it. The `kimi` and `cc2` seats both caught it first.

Worse: the producing script `sk_verdict_never_fired_2026-09-20.py` continued printing the withdrawn claim on a clean exit-0 run until `kimi` found it by executing a figure the brief itself declared.

## Finding 3: The Founder's Framing Holds, 7 of 7

All 7 blind seats agreed that treating gamma as a ruler rather than a verdict dissolves 3 of the 4 tensions the review had uncovered. They are not concessions but correct descriptions of a measuring instrument:

- a gate reading observations cannot fire on a class never observed — a scope boundary, not a defect;
- a discovery curve flat at a small constant, such as the 2, 2, 2, 2, 2 series one seat produced in March 2026, is indistinguishable from exhaustion at any realistic noise floor — a researcher's judgement under bounded recursion;
- residual risk behind a flat curve is the model reporting the introduction rate, not concealing it.

The 4th, that the model can be parameterised to hit any target risk, does **not** dissolve. It becomes a calibration requirement.

## Finding 4: CC1 Was Refuted on the 4th Tension by 4 of 7 Seats

On 4 independent grounds. `ge`: fixing one parameter leaves the other free, so the claim is *"mathematically false"*. `fable`: the calculation used an invalid domain — under the settled parameter map the band is `z(1−ν)` with a floor at `ν`, not width `z`. `cx`: parameters fitted on the outcomes they explain remain unfalsifiable; calibration must be ex ante. `ds`: *"a calibration requirement that has never been executed ... is a promissory note, not a defence."*

CC1's own script had printed *"measuring b does NOT shrink the width; it TRANSLATES it"* before CC1 told the founder it *"restores the model's power to forbid outcomes"*.

## Finding 5: The Scorer Is the Live Problem

All 7 blind seats independently found that the fix score does not discriminate inside the band it guards.

- **672 of 902 scored fixes are exactly 1.0 — 74.5011%, Wilson [71.5570%, 77.2374%]**
- the admissibility term is **binary across all 1,247 archived decisions**: 902 at 1 and 345 at 0, never intermediate
- `cc2` measured roughly 2.93 effective levels across the whole score, standard deviation 0.0288

Consequently the entire over-refusal debate, which consumed most of 3 rounds and produced 3 competing figures, is **operationally inert**: the lowest observed score is 0.740000, both disputed thresholds are 0.504931 and 0.395043, and **0 of 902** archived fixes fall below either. Moving the threshold between them changes 0 archived decisions.

## Finding 6: Bounded Recursion Is a Theorem, and CC1's Sketch Was Wrong

CC1 put a 3-step sketch into the open brief. **2 of the 3 steps are false**, confirmed by SymPy and z3 independently:

- *"the floor is strictly positive whenever the novel-defect rate or the re-injection rate is positive"* — false. At a novel-defect rate of 0 the floor is 0 for any re-injection rate. z3 returns unsat on the conjunction. The disjunct does no work.
- *"marginal gain tends to 0 as risk approaches the floor"* — false at a positive floor. At the stated parameters it equals 4/45, and z3 shows it is strictly positive throughout the open unit square. CC1 substituted the detection-phase gain for the composite map's net per-cycle change.

**The theorem that survives is stronger.** The appendix's own Stage-5 composition is a strictly increasing continuous self-map of the unit interval, so every orbit is monotone and bounded and therefore convergent, with no contraction argument needed. Per-cycle gains telescope to at most 1, giving a **finite bound on the number of worthwhile cycles**.

And it inverts the premise: the load-bearing assumption is that marginal value is bounded by a constant times the gain. With no re-injection and log utility, every cycle is worth the same fixed amount forever and the theorem fails. **A positive re-injection rate is not needed for convergence; it is what makes the economic step robust.**

A second condition emerged that nobody held: above a critical re-injection rate the only fixed point in the unit interval is certain failure, and no number of rounds helps.

## Finding 7: The Optimal Round Count Is Calculable and Was Calculated

From the project's own decay law and its own stopping rule, the optimal round count is `n* = (a/θ)^(1/γ)` — the round-1 finding rate as a proxy for complexity, the decay parameter, and the researcher's own stopping threshold. At a decay of 1/2 this is the inverse square root law stated in March 2026.

Fitted to the project's own March data the parameters are 4.89 and 0.709, and at a threshold of 1 finding per round this gives **9.37 rounds**. The founder recorded that runs were capped at around 9 to 15. CC1 called that a coincidence; the founder corrected it, and the founder was right — it had been calculated.

**The gap is that nothing uses it.** The fit runs every round and feeds only the convergence gate; the round budget remains a typed integer.

## Finding 8: Containment, and Why It Kept Failing

The dispatcher builds a sandbox copy for every seat, 7 for 7 seats in every round. The tool module used by the network-reached seats consulted the panel working directory **0 times**, resolving every path against the live repository, so **5 of the 7 copies were built and never entered**.

In round 4 that let one seat read **4.7945% of another seat's reply verbatim**, Wilson [2.8772%, 7.8858%], by running a recursive search across a directory that accumulates each answer as its seat finishes.

Read-only confinement could never have prevented it: the kernel wrapper governs what a seat may write, and this was entirely about what a seat could read. The repair roots tool paths in the calling seat's own copy, and is held by 7 tests of which 5 fail against the previous code. **Blindness then arrived for free**, because a copy taken before any reply exists cannot contain one.

## Finding 9: What the Blind and Open Rounds Measured About the Panel Itself

The blind brief carried CC1's position and invited attack. Measured afterwards: only 2 of 7 seats worked genuinely independently of it, 4 were mixed, and 1 refuted nothing CC1 had said anywhere. The anchoring bought 4 useful refutations and cost 5 partly-captured seats. The open brief therefore contained no CC1 position at all.

The open round produced **selective incorporation rather than deference**: 2 seats reversed their central blind position on evidence, 5 re-derived an adopted finding rather than accepting it, and 1 seat held alone against 6 with 12 executed symbolic checks and did not fold.

One artefact contaminates the adoption measurement and is recorded rather than hidden. The `cc2` seat **reviewed its own blind reply without recognising it**, treating its own finding as another seat's. That makes 1 of its 2 reported adoptions a self-adoption. It also improved the work: believing the finding external, the seat obeyed the brief's instruction not to verify its own paraphrase, re-derived it with a negative control, and refuted 2 of its own blind claims.

## What Is Open, For the Founder

1. Whether the project should charge itself for the §7.12 degeneracy it has carried unmeasured since 31 March 2026.
2. The scorer repair, which is where 7 seats independently converged and where the threshold debate turns out not to matter.
3. Wiring the optimal round count as an advisory projection from round 3 — proposed, not built, and advisory by design so the ruler reports and does not decide.
4. Whether the bounded recursion theorem, in its corrected form, belongs in the appendix's falsifiable-claims table. 6 seats say yes; 1 dissents.
5. Whether a further round is warranted, decided by the project's own stopping rule rather than pre-committed.

## The founder's derivation hypothesis, answered

The founder proposed that the revision might be derivative of this project's own appendix: *"It would not shock me if Astra essentially 'stole' its finding from our existing appendix ... because our maths is so new, its training data had little else to go on."* That is falsifiable and it was measured rather than judged. Producer: `scripts/panel_value_and_provenance_2026-09-20.py`.

**What supports it.** The revision's action step is identical to the appendix's Phase-3 form under the substitution `s = sigma*(1-nu)`, `b = nu`, with a symbolic difference of exactly 0 — settled with SymPy over exact rationals and cross-checked with mpmath at 40 digits, all 3 forms agreeing. The package carries 3 distinct external scholarly references against 10 citations of this project's own files, and no bibliography section. The appendix already mentions the introduction symbol nu 97 times and the repair symbol sigma 48 times. So the action step adds no mathematics the appendix did not already hold, and the package leans overwhelmingly on this project's own artefacts.

**Where it fails outright, and this is the decisive half.** The SHIPPED recurrence is not the revision's. The shipped Phase 2 interpolates between the posterior and the prior; the revision acts on the posterior. Measured over 4,000 exact-rational samples, **3,959 differ**, with an mpmath worst-case gap of 0.917. That distinction appears nowhere in the appendix, so at least 1 component of the revision is not derivative of it.

**The honest boundary.** Identity with the appendix is not evidence of derivation FROM the appendix. A 2-state Markov transition is a textbook object, and 2 authors reaching the same standard form is convergence rather than copying. No archive can separate those from the text alone, and this note does not claim to.

Every figure in this note is regenerated by `scripts/maths_review_synthesis_figures_2026-09-20.py`.

Written under CDSFL note standard v1.7 (26 August 2026).
