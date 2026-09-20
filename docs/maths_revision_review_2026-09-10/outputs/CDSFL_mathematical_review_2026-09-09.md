# CDSFL mathematical review — 9 September 2026

**Scope:** the mathematical claims in Constraint Engineering at commit `9e3dfe9d68b428acb98e65c0ad3800ec571a4da4`. This is an assessment of the written model, its probabilistic interpretation, and the evidence described in the repository. It is not a full source-code audit or an empirical reproduction of the benchmark programme. No project files were changed.

**Verdict:** the independent coverage identity and the Bayesian update after non-detection are sound under explicit assumptions. The complete current model cannot receive an unqualified endorsement as a sound general account of scientific enquiry. In particular, the repair extension conflates conditioning on evidence with changing the object being assessed, and the literature-novelty extension conflates originality with evidential contribution. These are questions about the mathematical model's meaning, separate from harness faults. There are also smaller, reproducible algebraic and scope errors. The possibility of a valuable scientific contribution remains open.

This review used separate algebraic, probabilistic, and evidential review passes. The conclusions rest on the definitions, derivations, and counterexamples below, rather than on a vote among reviewers. Numerical checks were independently executed using exact rational arithmetic. The companion [Python script](./CDSFL_math_counterexamples.py) uses only the standard library and reproduces the main examples.

**1. The valid core and its scientific meaning**

Let H mean a specified flaw exists in an unchanged target. Let D_i mean review i detects that flaw. If

q_i = P(D_i | H, all earlier reviews missed),

then the chain rule gives

P(all reviews miss | H) = product_i(1 − q_i).

Therefore C = 1 − product_i(1 − q_i) is the probability this review procedure would detect the flaw if it existed. With independent reviews of constant sensitivity p, this becomes C(n) = 1 − (1 − p)^n.

This is valid probability mathematics. It formalises a meaningful aspect of enquiry: failing to find an error is informative to the extent that the examination could have exposed it. Independence is sufficient for substituting constant marginal probabilities. More generally, correctly specified conditional probabilities can handle adaptive reviews. Fixed diversity discounts are not automatically those probabilities.

C(n) is a property of detection coverage conditional on an existing flaw. It is not, by itself, the posterior probability that a claim is true. The project's separate risk equation addresses that distinction.

Let R = P(H), q = P(D | H), and suppose there are no false positive detections. After a negative result,

R_minus = P(H | no detection) = R(1 − q)/(1 − qR).

This is exactly Bayes' theorem. In odds form,

R_minus/(1 − R_minus) = (1 − q)R/(1 − R).

Sequential updating and the batch posterior consequently agree. The prior is retained in the running posterior; it does not cease to matter.

If false positives occur with probability f, the denominator becomes R(1 − q) + (1 − R)(1 − f). The simple recursion therefore needs either the zero-false-positive assumption or an appropriate observation model.

Sources: [PAPER §2.1](https://github.com/jebus197/Constraint_Engineering/blob/9e3dfe9d68b428acb98e65c0ad3800ec571a4da4/PAPER.md#L59), [appendix residual risk](https://github.com/jebus197/Constraint_Engineering/blob/9e3dfe9d68b428acb98e65c0ad3800ec571a4da4/docs/MATHEMATICAL_APPENDIX.md#L52), [recursive derivation](https://github.com/jebus197/Constraint_Engineering/blob/9e3dfe9d68b428acb98e65c0ad3800ec571a4da4/docs/MATHEMATICAL_APPENDIX.md#L183). The appendix's [intellectual lineage](https://github.com/jebus197/Constraint_Engineering/blob/9e3dfe9d68b428acb98e65c0ad3800ec571a4da4/docs/MATHEMATICAL_APPENDIX.md#L2047) itself acknowledges that this is an application of Bayes' theorem. See also [NIST's account of Bayesian reliability](https://www.itl.nist.gov/div898/handbook/apr/section2/apr1a.htm).

**2. The principal modelling defect: non-detection is not repair**

The three-phase extension defines:

- R_det = R_old(1 − q)/(1 − qR_old)
- R_base = sigma R_det + (1 − sigma)R_old
- R_new = (1 − nu)R_base + nu

Here sigma is described as the probability/efficacy of successfully resolving the detected flaw, and nu as reinjection. The first expression, however, is the posterior conditional on detecting nothing. It cannot simply become the probability after detecting and repairing a flaw because it is renamed “Detection.”

A complete elementary experiment makes the distinction visible. Suppose:

- Before review, a target has probability 1/2 of containing one flaw.
- The review detects an existing flaw with probability 4/5.
- There are no false positives.
- Every detected flaw is repaired perfectly.
- Repairs introduce no other flaws.

| Observed outcome | Probability of outcome | Flaw probability after observation | Flaw probability after repair |
|---|---:|---:|---:|
| Detection | 2/5 | 1 | 0 |
| No detection | 3/5 | 1/6 | 1/6 |

The expected residual flaw probability after the cycle is therefore

(2/5) × 0 + (3/5) × (1/6) = 1/10.

The CDSFL three-phase recurrence returns 1/6. That is correct conditional on the negative-result branch, but it is neither the expected residual across the cycle nor the residual after a confirmed perfect repair.

A second boundary test is even simpler. With a confirmed existing flaw, R=1, q=4/5, sigma=1, nu=0, the written recurrence returns R_new=1. Under its stated perfect-repair meaning, the probability that the target flaw remains should be zero. This example does not use the excluded R=q=1 boundary.

This is a semantic problem in the probability model, not merely a numerical approximation or an uncalibrated parameter. The convex interpolation is a well-defined bounded function and could be assigned another interpretation, such as a scoring heuristic or an explicitly specified latent mixture. Its stated repair interpretation has not been derived.

A possible repair to the formal model would separate:

1. Observation: update the probability of the old target being flawed, conditional on the actual positive or negative result.
2. Intervention: model whether a repair changes that target's state.
3. New errors: model flaws introduced into the new target version.
4. Subsequent verification: collect evidence about the changed target.

For this elementary single-flaw experiment, the ex-ante post-repair probability is R(1 − q sigma). If an independent new flaw is then introduced with probability nu, it is nu + (1 − nu)R(1 − q sigma). This is an illustration under specified assumptions, not a proposed universal replacement equation.

Sources: [appendix three-phase extension](https://github.com/jebus197/Constraint_Engineering/blob/9e3dfe9d68b428acb98e65c0ad3800ec571a4da4/docs/MATHEMATICAL_APPENDIX.md#L209), [operational directive §3](https://github.com/jebus197/Constraint_Engineering/blob/9e3dfe9d68b428acb98e65c0ad3800ec571a4da4/bench/directives/universal/cdsfl_operational.md#L106). The directive substitutes a tool-derived solution score S_k for sigma and splits reinjection into two terms; that does not by itself correct the observation/intervention distinction.

**3. Scientific novelty and evidential strength must remain distinct**

Stage 6 specifies

eta_combined = eta_int [1 − c_ext(1 − nu_lit)]

and uses q = eta_combined d p in the residual-risk update. Here nu_lit denotes literature novelty, to distinguish it from reinjection nu.

At eta_int=1, c_ext=1, nu_lit=0, the effective detection probability is forced to zero. A fully known result then contributes no reduction in the stated residual risk.

This is appropriate only if the quantity being measured is something such as credit for original discovery. It is not generally correct as a rule for scientific corroboration. Independently replicating a published experiment, or applying an established diagnostic to a newly examined target, can supply strong fresh evidence while having no publication novelty. Established mathematics can expose a previously unnoticed flaw in a new derivation without itself becoming a new theorem.

Internal redundancy can matter to conditional information gain. Publication novelty answers a different question. Keeping both dimensions in reports does not remove their mathematical coupling inside q.

At prior R=1/2 and diagnostic sensitivity p=4/5 with d=1, a clean, informative established test gives posterior 1/6. Stage 6's zeroed q leaves it at 1/2.

For a model intended to describe scientific enquiry, replication and the productive application of established knowledge must remain possible sources of corroboration. Literature novelty can be tracked independently or used for discovery-priority decisions without automatically changing the likelihood of detecting a flaw.

Source: [appendix Stage 6 definition and boundary cases](https://github.com/jebus197/Constraint_Engineering/blob/9e3dfe9d68b428acb98e65c0ad3800ec571a4da4/docs/MATHEMATICAL_APPENDIX.md#L265). The critique concerns the written extension; it is not an assertion that every live harness path currently applies it.

**4. Further mathematical findings**

| Claim or mechanism | Assessment | Reproducible example or condition |
|---|---|---|
| Batch posterior equals recursive posterior | Valid under the observation assumptions | The exact-arithmetic script verifies a heterogeneous sequence, in addition to the algebraic derivation. |
| Break-even nu_star = sigma Rq/[1 − qR(1 − sigma)] | Correct for the stipulated three-phase recurrence at interior R<1 | R=2/5, q=3/5, sigma=4/5 gives nu_star=24/119 and R_new=R exactly. Correct algebra does not establish the recurrence's probabilistic meaning. |
| Reinjection floor R_i >= nu | Correct for the stipulated recurrence | Every step is nu+(1−nu)R_base. This is a lower bound, not generally the achieved limit. |
| Posterior risk decreases with diminishing gains on every clean pass | False globally | q=1/2, R_0=.99 produces successive decreases .009802, .019033, .035931: increasing gains. |
| eta=0 implies unchanged R | False as written when reinjection is nonzero | R=.5, q=0, nu=.1 gives R_new=.55. Requires nu=0 or R=1 for unchanged risk. |
| Printed inverse C=(pi−R)/[pi(R−1)] | Sign error | pi=.5, C=.2 yields R=4/9; printed inverse returns −.2. Correct inverse is (pi−R)/[pi(1−R)]. |
| Fixed positive diversity discount fully handles repeated correlated reviews | Not general | A perfectly repeated detector with detection probability p retains coverage p. Any fixed dp>0 in 1−(1−dp)^n instead tends to 1. |
| Pairwise correlations determine all-miss probability | Not general | Three fair binary variables can be pairwise independent yet have all-miss probabilities 0, 1/4, or 1/8 depending on their joint law. |
| First low marginal gain establishes optimal stopping | Requires additional assumptions | Sequential sensitivities .1,.01,.9 give coverage increments .1,.009,.8019. A weak next pass does not establish that later available methods have low value. |

The inverse error is local: [appendix §1](https://github.com/jebus197/Constraint_Engineering/blob/9e3dfe9d68b428acb98e65c0ad3800ec571a4da4/docs/MATHEMATICAL_APPENDIX.md#L113) prints the correct inverse, whereas [the model-evolution paragraph](https://github.com/jebus197/Constraint_Engineering/blob/9e3dfe9d68b428acb98e65c0ad3800ec571a4da4/docs/MATHEMATICAL_APPENDIX.md#L169) prints the incorrect sign. It should not be used to dismiss the underlying Bayesian derivation.

For fixed nondegenerate q, sigma, nu, the stipulated recurrence has fixed points 1 and

R_star = nu/[q(sigma + nu(1 − sigma))].

At q=.5, sigma=1, nu=.1, the interior fixed point is .2, above the valid .1 lower bound. The README explorer already distinguishes the achieved floor from the nu bound; this review does not treat that distinction as a new defect.

The Ising/Boltzmann extension is a valid normalized family of joint distributions. It deserves credit for explicitly addressing dependence. It does not represent every possible higher-order dependence pattern, and architectural diversity does not prove statistical independence. One must either fit an appropriate joint law or estimate history-conditional detection probabilities. [Corroboration branching](https://github.com/jebus197/Constraint_Engineering/blob/9e3dfe9d68b428acb98e65c0ad3800ec571a4da4/docs/MATHEMATICAL_APPENDIX.md#L13), [marginal gains](https://github.com/jebus197/Constraint_Engineering/blob/9e3dfe9d68b428acb98e65c0ad3800ec571a4da4/docs/MATHEMATICAL_APPENDIX.md#L201), [reductions](https://github.com/jebus197/Constraint_Engineering/blob/9e3dfe9d68b428acb98e65c0ad3800ec571a4da4/docs/MATHEMATICAL_APPENDIX.md#L251), [distributed stopping rule](https://github.com/jebus197/Constraint_Engineering/blob/9e3dfe9d68b428acb98e65c0ad3800ec571a4da4/PAPER.md#L1074).

**5. What the existing evidence supports**

Symbolic verification can establish algebra, bounds, reductions, and fixed-point properties of the equations supplied to it. It does not establish that a variable is an accurate probability, that its inputs are calibrated, or that the equations describe the process they name.

The project's own evidence record distinguishes these claims:

- [PAPER §2.1](https://github.com/jebus197/Constraint_Engineering/blob/9e3dfe9d68b428acb98e65c0ad3800ec571a4da4/PAPER.md#L94) explicitly discusses variable sensitivity, adaptive dependence, binary-flaw assumptions, and the limits of the reliability analogy.
- [PAPER §2.2](https://github.com/jebus197/Constraint_Engineering/blob/9e3dfe9d68b428acb98e65c0ad3800ec571a4da4/PAPER.md#L150) leaves the predictive advantage of richer extensions over simpler models open.
- [Appendix §5](https://github.com/jebus197/Constraint_Engineering/blob/9e3dfe9d68b428acb98e65c0ad3800ec571a4da4/docs/MATHEMATICAL_APPENDIX.md#L617) requires training/held-out comparisons and describes data as available for initial risk-model calibration.
- [The April audit](https://github.com/jebus197/Constraint_Engineering/blob/9e3dfe9d68b428acb98e65c0ad3800ec571a4da4/docs/EXPERIMENTAL_RESULTS.md#L1400) says the reported R-squared .985 coverage fit was not reproducible and the z=3.63 diversity significance claim could not be verified from the referenced data.
- [The README explorer](https://github.com/jebus197/Constraint_Engineering/blob/9e3dfe9d68b428acb98e65c0ad3800ec571a4da4/README.md#L332) labels its display a diagram of equation behaviour rather than observations and explicitly identifies parameter estimation and cross-run testing as open work.

There is positive, bounded evidence too. The appendix reports that a Duane discovery-rate model fit 17/18 runs better than geometric decay by AICc; a restart burst term improved a retrospective fit; and discovery-efficiency telemetry improved prediction of convergence-gate satisfaction. Those results concern review telemetry and should be preserved at that scope. They do not by themselves calibrate the probability of unknown flaws remaining. This review did not recompute those statistics. [Discovery and convergence models](https://github.com/jebus197/Constraint_Engineering/blob/9e3dfe9d68b428acb98e65c0ad3800ec571a4da4/docs/MATHEMATICAL_APPENDIX.md#L872). The Duane family has an established reliability-growth lineage, described by [NIST](https://www.itl.nist.gov/div898/handbook/apr/section4/apr452.htm).

No held-out calibration result for the central R_k model was established in the main documents reviewed here. This is a bounded finding about this review, not proof that no additional artifact exists elsewhere.

**6. The model has been tested and revised; it has not been certified by repetition**

The central complement-product and Bayesian ideas have persisted. Other mathematical statements have been corrected. In particular:

- The appendix [explicitly withdraws an earlier Ising coupling bound](https://github.com/jebus197/Constraint_Engineering/blob/9e3dfe9d68b428acb98e65c0ad3800ec571a4da4/docs/MATHEMATICAL_APPENDIX.md#L38), including a false justification previously attributed to symbolic verification.
- The [stage-link explanation](https://github.com/jebus197/Constraint_Engineering/blob/9e3dfe9d68b428acb98e65c0ad3800ec571a4da4/docs/MATHEMATICAL_APPENDIX.md#L163) corrects the claim that every transition was a strict generalisation.
- The [human-machine reduction and numerical table](https://github.com/jebus197/Constraint_Engineering/blob/9e3dfe9d68b428acb98e65c0ad3800ec571a4da4/docs/MATHEMATICAL_APPENDIX.md#L725) document corrected mathematical claims.
- The [earlier meta-review](https://github.com/jebus197/Constraint_Engineering/blob/9e3dfe9d68b428acb98e65c0ad3800ec571a4da4/docs/EXPERIMENTAL_RESULTS.md#L557) records substantive fixes to the mathematical appendix.

These corrections support the usefulness of criticism. They also mean that an endorsement of the overall framework should not be read as a proof of every expression or interpretation.

Review by many AI systems provides evidence only to the extent that the reviews could detect the errors at issue and contribute independent reasoning. An inability to complete an empirical run cannot count as the hypothesis passing that run. Conversely, a harness fault does not invalidate an algebraic theorem.

Human review is valuable for independent perspectives, empirical design, and assessment of novelty. Mathematical validity does not depend on the reviewer being human. The same counterexample should be inspectable by either.

**7. What the model says about scientific enquiry**

The worthwhile scientific proposition is broader than code review: corroboration should depend on the discriminatory capacity of tests, the evidence actually observed, and the dependence among observations. Making those quantities explicit across human and machine enquiry could support a useful research contribution.

The existing formulas cover selected parts of that proposition. Scientific enquiry also requires positive and negative evidence, comparison among hypotheses, changes to the target or theory being assessed, and the possibility that an informative investigation increases the estimated probability that a claim is wrong. Finding a convincing refutation can be scientific progress even when confidence in the original claim falls.

A posterior-risk decrease conditional on a favourable outcome is therefore not a universal measure of scientific progress or of the expected value of an experiment. Before intervention, under a correctly specified Bayesian model, the expected posterior probability of a fixed proposition equals its prior; information gain and decision improvement are distinct from a guaranteed reduction in that probability.

Bayesian and severe-testing accounts of scientific evidence already have a substantial literature. For example, [van Dongen, Sprenger and Wagenmakers, “A Bayesian perspective on severity”](https://pmc.ncbi.nlm.nih.gov/articles/PMC10104935/) develops a Bayesian account involving specific predictions and expected evidential value. Its relevance here is conceptual precedent, not an assertion that it settles all philosophical disputes or subsumes CDSFL's architecture.

The core identities themselves are established mathematics, as the appendix acknowledges. A contribution can reside in a well-founded extension, a coherent formal account spanning previously disconnected mechanisms, an empirical discovery about review processes, or a useful operational synthesis. This review does not certify historical priority or dismiss such contributions because the underlying probability theory is standard.

**8. Future durability and the next mathematical step**

The valid identities will remain true within their assumptions regardless of future model releases. Their empirical applicability, the correct conditional probabilities, dependence structures, and best parameterisations can change with new tools, collaborators, tasks, and scientific domains.

The immediate mathematical priority is to state a generative model: what hidden state exists, what can be observed, what each observation means, when the target changes, and what each parameter measures. Derive the posterior update, repair transition, and decision objective separately from that model. Keep discovery novelty separate from evidential validity. Then measure whether the resulting risk predictions and decisions generalise beyond the data used to tune them.

That work would preserve the valid core while directly addressing the most significant objections identified here. An eventual general model of enquiry needs those distinctions precisely because it aims to say something about science itself.

**Reproduction:** run `python3 CDSFL_math_counterexamples.py`. All exact-arithmetic checks passed during this review. The numerical results establish the examples and identities tested; they are not an empirical validation of the full framework.

