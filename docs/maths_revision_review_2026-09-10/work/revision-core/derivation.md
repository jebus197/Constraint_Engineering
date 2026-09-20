# Independent candidate core: observation followed by intervention

Status: derived independently on 2026-09-09; mathematical proposal, not empirically calibrated. No repository edits. Read alongside the archived prior review, not as certification of the whole CDSFL system.

## 1. Precisely define the event

Let H mean that a specified target version fails a specified requirement, or contains at least one flaw in a specified class. Let F be the recorded history, including scope, target version, evidence-selection procedure, and prior observations. Start with r=P(H=1|F).

Observe actual evidence e using a specified procedure. Write L1=P(e|H=1,F), L0=P(e|H=0,F), using likelihood densities where appropriate. Then

z = r L1 / [r L1 + (1-r)L0].

Now execute action a, possibly selected in response to e. For the new target version H', define

- s=P(H'=0 | H=1,e,F,a): net removal of the scoped failure.
- b=P(H'=1 | H=0,e,F,a): introduction of the scoped failure into an initially clean target.

The collapsed equation is

r' = [(1-s)L1 r + b L0(1-r)] / [L1 r + L0(1-r)].

Equivalently, r'= (1-s)z+b(1-z)=b+(1-s-b)z.

Human reading: **Use the evidence to update what you believe; use the action's measured effects to predict what remains wrong and what might become wrong.**

## 2. Proof and exact scope

Bayes' theorem gives z. Partitioning on the pre-action state H gives r'=P(H'=1|H=1,e,F,a)z+P(H'=1|H=0,e,F,a)(1-z). This is exactly the displayed expression. It requires no independence between reviewers, observations, or action success if the likelihoods and transitions are correctly conditioned on the available history.

However, an observational estimate conditioned on actions people happened to choose does not automatically identify what would happen under a different chosen action. Predictive deployment requires appropriate intervention data or a justified causal model. Selection of an action by policy should itself introduce no unrecorded informative evidence; if it does, incorporate that evidence into z.

This equation is an exact binary projection of a richer model. It does not establish that r is a sufficient state for predicting future likelihoods or transition rates. Maintaining a single scalar while discarding history is an additional, generally false assumption.

## 3. Boundaries and reductions

- For r,s,b in [0,1] and nonnegative likelihoods with positive denominator, r' is in [0,1]. It is a mixture of 1-s and b. No extra s+b<=1 constraint is needed for validity.
- With no action, s=b=0, recover Bayes exactly.
- With uninformative evidence L1=L0>0, z=r, leaving the two-state transition.
- With no evidence and no action, r'=r.
- A confirmed scoped failure gives z=1; r'=1-s. A confirmed clean target gives z=0; r'=b.
- A verified perfect net repair s=1, b=0 gives r'=0 regardless of z. An action that always leaves the target failed, s=0,b=1, gives r'=1.
- If s+b>1, r' decreases as z increases. This is valid: the action could cure failed objects while damaging clean ones. Such a transition may be undesirable but is not a probability violation.
- If the denominator is zero, the observed outcome was impossible under the model. Return an explicit contradiction/undefined state and investigate model or data; do not manufacture a probability.
- Priors exactly 0 or 1 cannot be overturned by ordinary finite likelihood ratios. Reserve such priors for declared logical/model assumptions. An impossible observation challenges the model, rather than producing an automatic Bayesian update outside it.

## 4. Binary tests, false positives, and the original core

For sensitivity q=P(D|H=1,F) and false-positive probability f=P(D|H=0,F):

- Positive result: z+=rq/[rq+(1-r)f].
- Negative result: z-=r(1-q)/[r(1-q)+(1-r)(1-f)].

With f=0, the negative-result branch is exactly r(1-q)/(1-rq), the valid original Bayesian identity. It remains the negative-result branch, never the generic detection-and-repair outcome.

On an unchanged target, conditional likelihood ratios multiply over sequential evidence by the chain rule. Independent constant-sensitivity examinations of an existing flaw recover coverage C(n)=1-(1-q)^n. More generally, history-conditional sensitivities along the all-miss path give C=1-product(1-q_i). Fixed discounts need empirical justification if used to approximate these q_i.

Perfectly duplicated evidence has likelihood ratio 1 conditional on already having seen it. It contributes no new information; merely coming from a differently named agent does not change this.

## 5. Net removal is different from repair then reinjection

Suppose a repair removes an existing failure with probability sigma. After repair, each clean state becomes failed with probability nu, equal for initially clean and successfully repaired paths. Then

r' = nu + (1-nu)(1-sigma) z.

This is the general transition with b=nu and s=sigma(1-nu), NOT s=sigma. A successful repair followed by reinjection is not a net removal. If reinjection differs on initial-clean and repaired-clean paths, use b=nu_0 and s=sigma(1-nu_1), or retain the general transition.

Concrete boundary: z=1, sigma=1, nu=0.2 gives r'=0.2. Substituting s=sigma and b=nu incorrectly gives 0.

The quoted nu may be defined as a clean-state conditional probability; global independence is a sufficient special assumption, not necessary. Reinjection into a target that remains failed has no additional effect on the binary event, although it matters for flaw counts and severity, which this scalar does not represent.

## 6. Ex ante planning must average actual branches

Before observing a binary test result, let actions have rates s_D,b_D on detection and s_N,b_N on non-detection. Then

E[r'] = r[q(1-s_D)+(1-q)(1-s_N)] + (1-r)[f b_D+(1-f)b_N].

This follows by enumerating the four initial-state/test-result branches. It avoids confusing posterior reassurance with actual risk reduction.

With observation only, E[z]=r. Helpful evidence can reveal that risk is higher; investigation is not defined by lowering the probability of an unwelcome hypothesis.

With no false positives, repair of detected flaws only, no damage, and efficacy sigma, expected remaining risk is r(1-q sigma). For r=1/2,q=4/5,sigma=1, this is 1/10. On the no-detection branch alone, posterior risk is 1/6. On the perfect-repair detection branch, it is 0.

If reinjection nu occurs after every cycle, expected remaining risk is nu+(1-nu)r(1-q sigma). If reinjection can occur only when a repair action is executed, do not use that expression. Under the sequential mechanism on detection branches only, it is r[1-q sigma(1-nu)]+(1-r)f nu. The action schedule is part of the model.

## 7. Useful deductions, with their assumptions

Conditional expected benefit of the action relative to leaving the observed target unchanged is z-r'=s z-b(1-z). Benefit is positive precisely when s z>b(1-z), or z>b/(s+b) if s+b>0. This is not a universal scientific-progress metric: discovering falsehood, improved prediction, or learning a mechanism may be valuable without physical repair.

For repeated identical transitions with no intervening informative evidence, fixed point is b/(s+b) when s+b>0. The recurrence converges when 0<s+b<2. At s=b=1 it alternates, and at s=b=0 nothing changes. Sequential repair/reinjection has nonnegative slope (1-sigma)(1-nu), and fixed point nu/[sigma+nu-sigma nu] whenever the denominator is positive.

These deductions concern stipulated fixed transition rates; adaptivity, changing targets, and updated parameter distributions require recalculation.

## 8. What must survive the human-facing collapse

Keep a compact equation and plain definitions visible, but retain:

1. Target/event definition and version; a proposition's truth is not changed by revising its wording or accepting a repair.
2. Evidence provenance and conditioning history; dependence, selection, censoring, and reused data.
3. Parameter uncertainty and calibration population, including unknown false-positive and false-negative rates.
4. Action definition, relevant intervention data, and post-action verification.
5. Multiple hypothesis/state structure when a binary projection is inadequate.

Do not replace the posterior of uncertain parameters by arbitrary means inside nonlinear functions. Integrate over the joint latent-state/parameter distribution, or report sensitivity bounds. A two-state display can remain comprehensible without claiming the world has only two states.

The collapse is a computational and explanatory interface. The evidence trail makes its numbers challengeable. General scientific relevance comes from using explicit hypotheses, informative observations, and transparent decisions, not from asserting that one probability exhausts scientific enquiry.
