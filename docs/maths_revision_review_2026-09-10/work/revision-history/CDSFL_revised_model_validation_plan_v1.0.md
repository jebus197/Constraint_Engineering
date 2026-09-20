# CDSFL revised model: prospective validation and refutation plan

**Version 1.0 proposal — 9 September 2026.** Companion to the [revised mathematical specification](./CDSFL_revised_model_specification.md). The structural mathematical checks have passed. No empirical calibration or deployment experiment was performed in this revision exercise.

This plan is designed to begin on a small scale after the current build work permits it. A successful first task family would support a bounded usefulness claim. Broader STEM and substrate generality require additional evidence.

## 1. Make the empirical claim capable of failing

The core equation is a probability identity when its quantities have the stipulated meanings. An operational model also claims that its **chosen states, estimated observation likelihoods, action transitions, and decision policy** describe a real task family. Those commitments make prospective predictions.

Before each evaluation, freeze:

- The target family and sampling procedure.
- The failure event, acceptance criterion, and independently available outcome check.
- The model version, parameter-estimation procedure, and allowed adaptation.
- The comparison models and policies.
- The practical improvement sought, tolerated regressions, sample-size rationale, and analysis plan.

Do not choose removal or introduction parameters after seeing the answer. The general equation can fit any desired result if those are left unconstrained.

Maintain separate claims for mathematical correctness, predictive adequacy, useful decisions, transfer, and originality. A stochastic forecast is not logically refuted merely because a low-probability event occurs. A predeclared predictive test can reject adequacy at its stated error rate; a practical discrepancy can also justify changing a model without pretending it was a deductive contradiction.

Applied Bayesian practice includes model construction, checking, comparison, and revision, not only posterior computation. See [Gelman and colleagues, Bayesian Workflow](https://arxiv.org/abs/2011.01808). The CDSFL-specific programme below is a proposal, not a result from that paper.

## 2. Define events that can actually be resolved

An initial event might be:

> This numerical routine violates property P on input distribution D, within the stated tolerance and evaluation procedure.

“Some unknown flaw exists somewhere” usually cannot receive a complete independent label. If the oracle checks only a defined class or finite domain, restrict the claim to that scope.

Record before observing the result:

| Record | Minimum content |
|---|---|
| Target | Identifier, version/hash, source family, relevant assumptions. |
| Event | Exact failure/acceptance criterion and scope. |
| Prediction | Prior or posterior forecast, parameter provenance, and uncertainty; unestimated where necessary. |
| Evidence | Identifiers, collection/selection procedure, available history, dependencies, and target version examined. |
| Action | Chosen action and policy, relevant selection information, resulting target version. |
| Outcome | Independent resolution, its scope, ambiguous/missing labels, and any oracle limitations. |
| Resources | Actual cost, elapsed time, and why work stopped. |

Keep a source artifact and its mutations in the same development or held-out partition. Many mutations of one target do not supply many independent task families.

A changed proof or design gets a new version. A revised claim does not retroactively become the original claim. A timeout is unresolved rather than a clean review. Missing outcomes must remain visible; otherwise successful-to-verify tasks can dominate the apparent performance.

## 3. Calibrate observation, action, and verification separately

### Observation cohort: what can the review detect?

Use frozen targets whose scoped positive and negative labels are independently established. Run the review without modifying the target. Estimate

\[
q=P(\text{positive result}\mid\text{flaw, context}),\qquad
f=P(\text{positive result}\mid\text{no flaw, context}).
\]

Include both valid and invalid artifacts. A collection containing only planted defects cannot estimate false-positive rate. Seeded defects support claims about detection of those defect types; seeded prevalence does not establish natural-world priors.

For a genuinely comparable Bernoulli cohort, uncertainty about a rate can be represented with a declared binomial model and appropriate interval or prior. The denominator is independently labelled opportunities in the relevant cohort, not an arbitrary count of generated assertions or tests chosen after the result.

Reviewers' self-reported findings alone generally do not identify the natural flaw rate, sensitivity, and false-positive rate separately. Use independently resolved labels or make the additional identifying assumptions explicit.

### Action cohort: what do repairs change?

Use cloned target snapshots and a declared intervention policy. Include initially flawed and initially clean targets to estimate

\[
s=P(\text{post clean}\mid\text{pre flawed, evidence, action}),\qquad
b=P(\text{post flawed}\mid\text{pre clean, evidence, action}).
\]

“Clean” here means passing the scoped independently resolved criterion. Removing one known flaw is not sufficient if the event is “at least one failure in this class remains.”

Retain a no-action comparison where practical. Randomized action assignment within relevant strata makes policy comparisons easier to interpret, where feasible. If actions are selected after positive results, estimate their effects in that population. An unconditional repair rate need not apply.

Initially clean targets selected for repair can be rare false-positive cases. Deliberately enriching those cases can help measure damage, but natural expected policy outcomes still require the correct population and selection weights. Do not mistake the enriched mixture for deployment prevalence.

### Verification cohort: is the changed target acceptable?

Resolve post-action outcomes using a check that is independent of the repair's optimization target as far as the scoped task permits. Retain the dependency record when independence is incomplete. Passing the exact examples a repair was designed to pass cannot by itself serve as a broad correctness oracle.

Reuse of the same checker on a changed target can still produce evidence. The required question is what that result implies under the actual development and selection process.

## 4. A progression suited to a sole founder

| Stage | Work | What success supports |
|---|---|---|
| 0. Structural mathematics | Exact derivation, outcome enumeration, boundaries, and deliberately broken alternatives. **Completed for this revision.** | Internal correctness of the supplied finite-state model and reference arithmetic. |
| 1. Diagnostic pilot | About 12 distinct tasks with independently resolvable outcomes, covering true/false positives, missed flaws, failed repairs, harmful changes, and evidence reuse. | Logging and oracle feasibility, runtime/cost estimates, and protocol corrections. Not certification. |
| 2. First locked family | Mathematical or numerical artifacts with independent symbolic, exhaustive, or reference-computation outcomes; development fit followed by untouched evaluation. | Predictive and decision usefulness within that defined family. |
| 3. Mechanistic inference | Known simulated mechanisms, noise, correlated observations, new data, and a true mechanism deliberately omitted from the initial candidate set. | Controlled transfer and detection of specified model misspecification. |
| 4. Real STEM transfer | A reproducible scientific-computing or experimental-replication task with withheld observations and a domain-appropriate reference procedure. | Evidence about that real domain, including limits of its outcome labels. |
| 5. Broader transfer | Another domain; different models, instruments, and eventually human participation where such claims are intended. | A progressively broader, still bounded generality claim. |

The pilot size is a design suggestion, not a power calculation. Pilot results remain development data. Choose the locked evaluation size from a prespecified practical tolerance, effect size, and uncertainty analysis informed by the pilot. If adequate precision is unaffordable, retain wider uncertainty and narrow the claim.

Some theoretical scientific claims remain unresolved. In that case evaluate observable predictions and decision consequences; do not relabel consensus as known truth.

These early stages do not require building a global distributed platform. They establish whether the mathematical instrument measures anything useful before increasing its operational scale.

## 5. Compare forecast quality and decision quality separately

Use three inexpensive forecast comparators:

1. A base-rate-only prediction.
2. A simple calibrated observation/action model with few parameters.
3. The proposed richer model, adding dependence or latent structure only where specified.

Use the former CDSFL score as a labelled heuristic comparator unless its probability interpretation has been established. Evaluate forecasts using the same unseen evidence; evaluate complete research policies separately under matched resource budgets.

For binary outcomes, a suitable initial primary metric is Brier loss,

\[
\frac{1}{n}\sum_{i=1}^n(p_i-y_i)^2,
\]

where \(p_i\) is the frozen probability of the event and \(y_i\) its independently resolved zero/one outcome. Add log loss and reliability summaries as diagnostics. Proper scoring rules assess probabilistic forecasts, while calibration and useful discrimination need separate attention. See [Gneiting and Raftery (2007)](https://sites.stat.washington.edu/people/raftery/Research/PDF/Gneiting2007jasa.pdf).

A constant base rate can be calibrated yet uninformative. Report forecast skill relative to baselines, predeclared subgroups, and task-family uncertainty. Aggregate performance can hide overconfidence on difficult or unfamiliar targets. For log loss, address exact zero/one forecasts prospectively; do not quietly clip failed predictions after outcomes become known.

For decision policies, measure:

- Independently resolved task outcomes and missed unacceptable failures.
- Unnecessary actions and newly introduced failures.
- Total resource cost and elapsed time.
- Useful replication, discovery, and other declared scientific objectives separately where they are not captured by one loss measure.

A lower internally computed risk is not the success endpoint. Prefer the simpler model if added complexity has no demonstrated practical benefit.

Predeclare a practically meaningful difference and tolerated harms. Use paired comparisons where the same independent task families can support them, with uncertainty at the family level. Treat a wide interval as inconclusive, rather than evidence of equality.

Small samples constrain claims. With independent identically distributed Bernoulli trials and zero observed failures, a one-sided 95% upper confidence bound is \(1-0.05^{1/n}\), about 9.5% at \(n=30\) and 3.0% at \(n=100\). This follows by solving \((1-p)^n=0.05\); it does not transfer to correlated review passes or a different deployment distribution. See [NIST on exact binomial limits](https://itl.nist.gov/div898/software/dataplot/refman2/auxillar/exacbino.htm).

## 6. Stress the assumptions that can make the system overconfident

**Dependence:** repeat exactly the same evidence, use reviews that share the first review's conclusions, and collect genuinely new replication data. The first should add no information once recorded; the last may add evidence even when the result is already published. Different model names do not establish independence.

**Selection:** compare fixed and adaptive policies prospectively. Record the information available to the selector. Log available alternatives and selection probabilities if later counterfactual policy evaluation is intended. A deterministic policy provides no direct outcome data about actions it never chooses.

**State insufficiency:** use targets with equal initial scalar risk but different hidden flaw types. A test aimed at only one type should have different implications. This challenges any claim that one number alone determines the next update.

**Parameter dependence:** compare joint uncertainty propagation with separate parameter averages. Include cases where harder targets also have poorer repair success, and where positive-result selection changes the repair population.

**Unknown alternatives:** deliberately omit the true mechanism in controlled experiments. A model can be confidently wrong within an incomplete candidate set. Maintain discrepancy checks and a route to revise that set; a generic “other” label without predictions does not solve the problem.

**Complementary experiments:** include a task where two individually uninformative measurements are jointly useful. This tests stopping and allocation policies rather than only the probability arithmetic.

**Changed targets:** test whether evidence about the original artifact is improperly carried over as fresh confirmation of a repair, and whether introduced failures in other classes are missed by a narrow repair-success measure.

Changing domain, model version, tools, target family, or selection policy triggers an applicability review. Recalibration may be appropriate, but transfer failure remains in the record.

## 7. Predeclare how to stop and what to publish

For the first empirical study, use a fixed sample and analysis plan. If repeatedly inspecting results to decide when to stop, use a valid time-uniform method under its assumptions or reserve a fresh final evaluation. Do not repeatedly tune against the same holdout until the claim passes. Time-uniform confidence sequences provide one established approach; see [Howard and colleagues](https://arxiv.org/abs/1810.08240).

A tool score called an “e-value” is not thereby an e-value. Any sequential evidence gate requires the actual statistical construction and null-expectation guarantees.

For operational work, record one of the following: acceptance conditions resolved; counterexample found; economical stopping with residual uncertainty; budget exhausted; blocked/unresolved. Budget exhaustion does not mathematically prove or disprove the target claim. It also should not cause a numerical prior inflation without an observation model linking that event to the failure risk.

Publish outcomes, failures, uncertainties, task exclusions, missing labels, costs, and the frozen model version. Distinguish a failed scientific hypothesis from a failed implementation, and both from a study too imprecise to decide. This record is essential when later improvements might otherwise erase the evidence of earlier limitations.

## 8. Current self-audit and next decision

| Claim | Current status |
|---|---|
| Collapsed equation follows from the stated model. | Established by the written derivation; reference calculations passed. |
| Main earlier repair and novelty counterexamples are addressed. | Established for the stated constructed cases. |
| Observation and action probabilities are calibrated for CDSFL deployment. | Unestablished. |
| Revised policy improves STEM research outcomes at a useful cost. | Unestablished. |
| Benefits transfer across domains and substrates. | Unestablished. |
| A distinct scholarly contribution has been demonstrated. | Not established by this review; requires precise comparison and evidence. |

The next empirical decision is whether a small, independently resolvable task family can support meaningful estimates of observation and action behaviour. If it cannot, revise the event definition or measurement plan before increasing model complexity.

The revised framework is applied to this review through explicit claims, evidence provenance, recorded corrections, and honest unestimated quantities. No self-assigned probability of mathematical or scientific soundness is manufactured from agreement among AI reviewers.
