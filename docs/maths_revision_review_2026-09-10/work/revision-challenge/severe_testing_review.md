# Bounded review: test-strength posterior bound

**Date:** 10 September 2026. **Scope:** the proposed severe-testing connection and its assumptions, without a broader research audit. Three illustrative posterior values were checked using exact fractions.

**Accepted correction:** the root agent confirmed that the final addition will use beta/gamma as the general form, retain alpha only for exhaustive binary outcomes, add the abstention counterexample to the exact checks and self-audit, and restrict the stated C=1-beta reduction to a completed binary protocol whose pass means no detection. No further broad review was undertaken.

## Verdict and one essential correction

The proposed bound is correct **when pass and fail are exhaustive binary outcomes**. This restriction must be explicit. Otherwise the identity P(pass | not H, I)=1-alpha need not hold, and the proposed numerical bound can be false even when the stated beta and alpha bounds are true.

Counterexample with an abstention channel:

| Target state | Pass | Fail | Abstain |
|---|---:|---:|---:|
| H | .05 | .95 | 0 |
| not H | .05 | .05 | .90 |

Here beta=.05 and alpha=.05, yet a pass at R=.5 has posterior .5, rather than .05. Passing is equally likely under either state. This matters because the main specification already permits timeout, abstention, and unresolved channels.

A general formulation uses gamma=P(pass | not H,I) directly. If beta<=beta_max and gamma>=gamma_min>0, then

    R_pass <= R*beta_max / [R*beta_max + (1-R)*gamma_min].

In an exhaustive binary protocol, gamma=1-alpha and gamma_min=1-alpha_max, recovering the proposed expression. Do not silently classify abstentions as successful negative results to obtain this reduction.

## Proof and numerical check

For binary outcomes, set D=R*beta+(1-R)*(1-alpha). With 0<R<1 and alpha_max<1, D is positive throughout the admissible region. The posterior R*beta/D is nondecreasing in beta and alpha:

    derivative w.r.t. beta  = R*(1-R)*(1-alpha)/D^2 >= 0
    derivative w.r.t. alpha = R*beta*(1-R)/D^2 >= 0.

Substitution of both upper bounds therefore gives a valid upper bound. The equivalent gamma formulation is nondecreasing in beta and nonincreasing in gamma.

Sensitivity q>=.95 and false-positive rate f<=.05 imply beta<=.05 and alpha<=.05 for the binary protocol. At R=.5 the bound is exactly 1/20=.05. These are assumed bounds, not empirical measurements from this review. With the same bounds and R=.99, the upper bound is instead 99/118, approximately .839. Thus .95 sensitivity and .95 specificity do not imply .95 posterior confidence regardless of the prior.

## Calibration and scope conditions

1. **Bounds, not point estimates.** An empirical estimate q_hat=.95 does not establish q>=.95. If calibration supplies statistical confidence bounds, the posterior inequality holds on the event that the bounds are simultaneously correct. Two separate 95% intervals are not automatically a joint 95% statement; without stronger information, their simultaneous coverage is at least 90% by the union bound. Do not reinterpret confidence coverage as the posterior probability that this particular conclusion is true.
2. **Shared conditioning.** Include calibration information, the test protocol and threshold, relevant selection/stopping rules, and the target/reference class in I. Independent calibration reduces leakage; it does not itself establish that deployment targets have the same conditional operating characteristics.
3. **Average versus uniform sensitivity.** beta can be an average over a specified distribution of failure subtypes. For example, perfect detection on 95% of flawed cases and zero detection on the remaining 5% gives aggregate beta=.05. It supplies no .05 upper bound on the undetectable subtype's miss rate. Uniform control requires a bound for every allowed subtype, or a supported worst-case bound. A prior mixture over subtypes is itself part of the model and can change after earlier misses.
4. **Prior uncertainty.** The illustration deliberately fixes R=.5. If R is only bounded above, the same expression is nondecreasing in R and can use that supported upper bound. An unspecified prior cannot produce a supported numerical posterior bound.

## Coverage and circularity

If pass means the complete unchanged-target protocol produced no detection, then aggregate coverage C=P(at least one detection | H,I)=1-beta. For a sequence, beta is the product of supported conditional miss probabilities along the all-miss history. This does not require independent examinations. Replacing these conditional quantities with marginal sensitivities requires an additional justified factorization.

With additional outcome categories, the complement of detection includes them; it is not automatically the specific pass event. Keep the protocol-level definition consistent between C, beta, and the evidence actually observed.

The bound is not circular if its substantive premises—the scoped prior and independently supported observation-error bounds—are obtained without using the desired posterior conclusion. It would become uninformative or circular if sensitivity were assigned because the model agreed with the conclusion, if the same assessment supplied its own truth labels, or if operating characteristics were fitted after selecting a successful observation and presented as prospective calibration.

The result expresses the legitimate role of a test's ability to expose a specified failure in interpreting a pass. It is a conditional Bayesian consequence of test-strength bounds. It does not establish a universal measure of scientific enquiry, implement a named philosophical severity statistic, or prove that the specified testing assumptions hold in real CDSFL deployments.
