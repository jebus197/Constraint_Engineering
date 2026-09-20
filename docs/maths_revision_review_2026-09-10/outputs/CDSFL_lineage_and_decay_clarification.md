# CDSFL lineage and decay: clarification of the revision

**10 September 2026 (London).** Companion to the version 1.1 mathematical proposal. This records a clarification requested by George Jackson; the core specification and equations are unchanged.

**Conclusion:** the proposal is a revision of CDSFL's model with explicit mathematical lineage. It is not a wholesale replacement. The valid coverage and observation mathematics survives exactly. Discovery-rate models can remain central empirical companions. The repair interpretation and novelty–validity coupling require replacement, and some universal interpretations of decay require correction.

## Human explanation and standalone status

The founder clarified the cumulative wording to:

> Capable repeated examinations progressively reduce the opportunity for an existing error to remain undetected. Their returns can diminish. Repairs can remove errors and introduce others. Discovery curves help us understand whether further investigation is productive.

The first sentence concerns an unchanged target and a consistently defined error. Each further examination must retain some ability to detect an error that earlier examinations could have missed; duplication alone need not add coverage. If the target or criterion changes, the revised state must be assessed explicitly.

This is an independently assessable account of scientific enquiry, with CDSFL as a possible implementation and testing vehicle. The revision makes that prospect better specified and easier to challenge: it preserves the valid original dynamics, removes identified semantic errors, and separates formal derivation from empirical adequacy. It does not establish historical novelty, usefulness across all STEM, or experimental success by definition.

## 1. The collapsed form recovers the original recursion exactly

The revised core is

\[
R_{\rm next}=\frac{(1-s)LR+b(1-R)}{LR+1-R}.
\]

For an unchanged target, set \(s=b=0\). After a clean review with sensitivity \(p\) and zero false positives, \(L=1-p\). Substitution gives

\[
R_{n+1}=\frac{R_n(1-p)}{1-pR_n},
\]

the original valid CDSFL residual-risk recursion.

Starting from \(R_0=\pi\), repeated clean reviews give

\[
R_n=\frac{\pi(1-p)^n}{1-\pi+\pi(1-p)^n}.
\]

The elementary proof is in odds: each clean result multiplies the previous odds by \(1-p\), so after n results the multiplier is \((1-p)^n\). Conversion back to probability yields the displayed expression.

Assumptions: the same scoped failure and unchanged target; actual negative results; constant sensitivity conditional on preceding misses; zero false positives; a supported observation history. Independent constant-sensitivity reviews are a sufficient special case. Ordinary illustrations use \(0<\pi<1\), \(0<p<1\); impossible boundary observations remain undefined.

## 2. The original decay curve survives

| Quantity | Expression | Meaning |
|---|---|---|
| Conditional miss probability | \(m_n=(1-p)^n\) | Probability every review misses, if the specified flaw exists. |
| Coverage | \(C_n=1-(1-p)^n\) | Probability at least one review would detect that flaw. |
| Next increment in coverage | \(C_{n+1}-C_n=p(1-p)^n\) | The diminishing additional detection opportunity. |
| Posterior odds | \(R_n/(1-R_n)=[\pi/(1-\pi)](1-p)^n\) | The same geometric decay expressed as evidential odds. |

The factor driving the original curve is literally retained. It was not replaced by an unrelated law.

Coverage and residual risk report different quantities. With a fixed prior,

\[
R_n=\frac{\pi(1-C_n)}{1-\pi+\pi(1-C_n)}.
\]

This is a change of reported quantity, not a claim that risk and coverage are numerically identical. In particular, high coverage is conditional detection ability, not automatically the probability that a target is correct.

The posterior probability R is not itself an exponential. Its absolute decreases also need not diminish from the first review onward. For example, prior 0.99 and sensitivity 0.5 produce initial decreases about 0.009802, 0.019033, and 0.035931. This corrects an overgeneralization about R; it does not refute geometric miss-probability decay or diminishing coverage increments.

The original equations are in [PAPER §2.1](https://github.com/jebus197/Constraint_Engineering/blob/9e3dfe9d68b428acb98e65c0ad3800ec571a4da4/PAPER.md#L59) and the [appendix's recursive derivation](https://github.com/jebus197/Constraint_Engineering/blob/9e3dfe9d68b428acb98e65c0ad3800ec571a4da4/docs/MATHEMATICAL_APPENDIX.md#L183).

## 3. Expanded-form heritage

The relationships should be named accurately:

| Original element | Relationship to the proposal |
|---|---|
| C(n), single-class coverage | Preserved exactly under its valid assumptions. |
| F, weighted multi-class coverage | Retained as a defined coverage report; its inputs require justified conditional detection probabilities or calibrated approximations. |
| R, residual risk after clean evidence | An exact special case of the revised observation update. |
| Human/machine coverage | Retained through conditional incremental detection; statistical independence is not inferred merely from different sources. |
| Actual positive results and false alarms | The observation model is extended to include them explicitly. |
| Repair and reinjection | Replaced by a derived state transition separating what was learned from what was changed. |
| Literature novelty | Retained as a separate scientific/reporting dimension, without automatically suppressing valid replication evidence. |
| Discovery-rate and convergence curves | Retained as testable empirical models and decision inputs, with their meanings distinguished from residual risk. |

Some links are exact special cases, some are transformations between quantities, and some are empirical companion models. Claiming that every original formula is a parameter setting of a single collapsed scalar would misstate the lineage.

## 4. Duane decay is preserved at its proper scope

The original appendix uses

\[
\lambda(t)=\frac{\beta}{\eta}(t/\eta)^{\beta-1}.
\]

For \(\eta>0\) and \(0<\beta<1\), this describes a declining power-law discovery intensity. It remains available for modelling verified findings, comparing observed trajectories, predicting near-term yield, and informing resource decisions. It is not displaced by the revised risk update, which answers a different question.

The power-law NHPP has an established reliability-modelling basis; see [NIST's Duane model](https://www.itl.nist.gov/div898/handbook/apr/section4/apr452.htm). Its application to CDSFL finding counts is an empirical modelling choice. The [project appendix §7.1](https://github.com/jebus197/Constraint_Engineering/blob/9e3dfe9d68b428acb98e65c0ad3800ec571a4da4/docs/MATHEMATICAL_APPENDIX.md#L872) reports a better AICc fit than geometric decay in 17 of 18 runs. This clarification preserves that reported result at its stated scope; it does not reproduce or independently confirm the fit.

The required corrections concern inference from shape:

- A declining finding rate can reflect depletion, but also reduced sensitivity, narrowing attention, or loss of useful context.
- A constant finding rate can reflect continuing genuine discoveries; it is not by itself proof of churn.
- A later increase can reflect a better method or newly opened line of investigation, not necessarily a deterioration in reasoning.
- The standard-error relation proportional to \(1/\sqrt n\) for suitable repeated measurements does not establish a universal law for the rate of discovering new defects.

The project's separate verification, novelty, rediscovery, and efficiency measures are useful precisely because one curve does not identify its own cause.

A count-rate model can supply evidence to the revised core if its observation likelihoods are justified under the competing failure states. A fitted curve alone does not supply those two likelihoods. This is a possible calibrated connection, not permission to equate falling counts with falling risk.

## 5. What the correction establishes

The original model had real merit: its coverage calculation, Bayesian clean-review interpretation, explicit attention to test capability and dependence, intelligible decay behaviour, and commitment to external falsification provide a substantive foundation.

Parts survive unchanged; other parts are corrected or replaced. That is successful revision of a research framework, not confirmation of every earlier claim. Mathematical preservation does not itself corroborate the empirical claim that a particular fitted decay law describes all STEM enquiry.

The appropriate description is: **CDSFL's existing mathematical foundation, revised to separate evidence, intervention, and discovery dynamics, while preserving valid decay relationships and their human-comprehensible interpretation.**

## Work record for this clarification

- Re-read the original coverage, structured model, recursive risk, Duane, and discovery-efficiency passages in the frozen repository snapshot.
- Compared them with version 1.1, especially its retained-lineage section.
- Requested a bounded independent lineage derivation; it confirmed the recursion, closed form, odds decay, and diminishing coverage increment using exact arithmetic.
- Checked NIST's primary description of the Duane/NHPP power-law model.
- No empirical benchmark was rerun, and no upstream or core-specification files were edited. The exact identities and the scope of reported empirical findings remain distinct.
