# CDSFL: a revised mathematical core for evidence, revision, and scientific enquiry

**Version 1.1 proposal — 10 September 2026 (London).** Prepared for George Jackson. This is a completed mathematical revision proposal, with exact checks and a prospective validation plan. It is not a deployment, an empirical certification, or a claim of a new probability theorem.

**Assessment:** CDSFL can retain a compact, human-comprehensible core while correcting the observation/repair confusion and the coupling of publication novelty to evidential strength. The resulting core is mathematically sound under explicit definitions. Its accuracy as an operational scientific instrument depends on separately testable observation models, action models, and parameter estimates.

The source examined is Constraint Engineering at commit 9e3dfe9d68b428acb98e65c0ad3800ec571a4da4. The [preceding review](./CDSFL_mathematical_review_2026-09-09.md) records the original objections. This proposal addresses the central coverage, residual-risk, repair, and novelty interpretation; it does not certify every cognitive or emergence metric elsewhere in the project. The [work record](./CDSFL_revision_plan_and_log.md) preserves decisions and corrections.

## 1. The human-comprehensible collapsed form

**Human-comprehensible account of the whole framework:**

> Capable repeated examinations progressively reduce the opportunity for an existing error to remain undetected. Their returns can diminish. Repairs can remove errors and introduce others. Discovery curves help us understand whether further investigation is productive.

The first sentence concerns an unchanged target and a consistently defined error. Each further examination must retain some ability to detect an error that earlier examinations could have missed; duplication alone need not add coverage. If the target or criterion changes, the revised state must be assessed explicitly.

The mathematical account can be stated and assessed independently of the CDSFL harness. Its definitions, conditional derivations, testable observation models, and empirical predictions apply to appropriately specified human, instrument, or computational investigations. CDSFL is one implementation and possible experimental vehicle for that account.

The standalone contribution proposed here is a framework relating repeated attempted refutation, corroboration, intervention, and the productivity of enquiry. Its mathematical ingredients include established probability laws. Whether their organization and operationalization make a distinct and useful scholarly contribution requires comparison with prior work and tests against external outcomes; the existence of software neither establishes nor is required for that assessment.

For a stated failure criterion on an identified target:

\[
\boxed{\displaystyle R_{\mathrm{next}}=
\frac{(1-s)LR+b(1-R)}{LR+(1-R)}}
\]

| Symbol | Meaning |
|---|---|
| \(R\) | Probability that the current target fails the stated criterion, before the new observation. |
| \(L\) | How much more likely the actual observation would be if that failure existed than if it did not. |
| \(s\) | Probability that the chosen action leaves an initially failing target free of the specified failure, accounting for all effects of that action. |
| \(b\) | Probability that the action leaves an initially non-failing target with the specified failure. |

**Plain reading: use the evidence to reassess the risk, then account for failures the action removes and failures it introduces.**

The same equation can be taught in two steps:

\[
B=\frac{LR}{LR+1-R},
\qquad
R_{\mathrm{next}}=(1-s)B+b(1-B).
\]

\(B\) is the assessed risk after observing the evidence and before changing the target. Evidence with \(L<1\) weighs against the failure; \(L>1\) weighs for it; \(L=1\) leaves the odds unchanged. An observation alone uses \(s=b=0\).

The word “failure” is deliberately scoped. It can mean an invalid step in a derivation, a numerical routine violating a defined property, or a design failing a stated performance requirement. “Free of the specified failure” does not mean flawless in every conceivable respect.

This gives the wider project a defensible organizing principle: **enquiry should change our beliefs according to discriminating evidence; revisions should be assessed according to their effects; further work should be chosen according to its expected scientific and practical value.** These are connected operations with different mathematical meanings.

## 2. Definitions that must survive the collapse

Let \(H\) denote the specified pre-action failure event. Let \(\mathcal I\) contain the target version, criterion, relevant history, test-selection procedure, evidence provenance, and assumptions. Then \(R=P(H\mid\mathcal I)\).

For the actual observation \(e\), define likelihoods

\[
\ell_1=P(e\mid H,\mathcal I),\qquad
\ell_0=P(e\mid\neg H,\mathcal I).
\]

For continuous observations these may be densities against the same reference measure. The canonical formula is

\[
\boxed{\displaystyle R_{\mathrm{next}}=
\frac{(1-s)\ell_1R+b\ell_0(1-R)}
{\ell_1R+\ell_0(1-R)}}.
\]

The ratio form uses \(L=\ell_1/\ell_0\) when \(\ell_0>0\). The likelihood-pair form also handles decisive evidence without representing an infinite ratio. Require a positive denominator. A zero denominator makes this conditional update undefined. For discrete outcomes, the supplied model assigns the observation zero probability; with densities, the representation and null-set conventions also matter. Record the issue and examine the model/data rather than substituting a clipped posterior.

The selected action \(a\) produces a new target version, whose failure event is \(H'\):

\[
s=P(\neg H'\mid H,e,\mathcal I,a),\qquad
b=P(H'\mid\neg H,e,\mathcal I,a).
\]

Three conditions are essential:

1. **The event remains clear.** Repairing a proof produces a new proof. It does not make the old invalid inference valid. Revising a scientific hypothesis creates a different hypothesis; it does not change the truth of the original claim. Changed criteria require an explicit mapping or a new assessment.
2. **Action selection is accounted for.** The policy must choose \(a\) from recorded information, allowing randomization independent of the hidden state conditional on that information. If a person or model chooses using additional private evidence, incorporate that evidence or its selection mechanism into \(B\). Observational repair rates do not automatically identify the effects of a different intervention policy.
3. **The probabilities share their conditioning.** \(s\) and \(b\) apply to this evidence, context, and action. An unconditional success rate from unrelated tasks is not automatically appropriate.

For an “any flaw in class K” event, \(s\) means removal of **all** failures needed to make that event false. Fixing one reported issue does not establish this probability. Binary risk also omits flaw count, severity, and unlisted failure classes.

Conditional transition entries on zero-weight branches need not be estimated: any valid kernel value there gives the same result. A zero total observation denominator still makes the update undefined.

The core is a compact update interface to a potentially richer model. A single \(R\) does not contain the history needed to supply its next likelihoods. The claimed simplicity is in the arithmetic and explanation, not in pretending all relevant evidence fits into one number.

## 3. Derivation and boundaries

Bayes' theorem gives \(B=P(H\mid e,\mathcal I)\). Under the action-selection condition, choosing \(a\) adds no omitted information about \(H\). Partitioning the post-action event over the two pre-action states gives

\[
\begin{aligned}
P(H'\mid e,\mathcal I,a)
&=P(H'\mid H,e,\mathcal I,a)B\\
&\quad+P(H'\mid\neg H,e,\mathcal I,a)(1-B)\\
&=(1-s)B+b(1-B).
\end{aligned}
\]

Substituting Bayes' expression yields the collapsed equation. This is an application of established probability laws. NIST describes the underlying prior–likelihood–posterior calculation in its [Bayesian reliability handbook](https://www.itl.nist.gov/div898/handbook/apr/section2/apr1a.htm).

Consequences follow directly:

- For \(R,s,b\in[0,1]\), nonnegative likelihoods, and positive denominator, the answer lies in \([0,1]\): it is a weighted average of \(1-s\) and \(b\).
- No action recovers Bayes exactly. No action and uninformative evidence leave \(R\) unchanged.
- A confirmed failure gives \(B=1\), hence \(R_{\mathrm{next}}=1-s\). Confirmed absence gives \(B=0\), hence \(R_{\mathrm{next}}=b\).
- A net perfect action \(s=1,b=0\) leaves zero risk for the specified event.
- There is no requirement that \(s+b\leq1\). An action can cure flawed targets and damage clean ones. With \(s=b=1\), the state flips; the equation remains valid.
- Certain priors cannot be overturned by ordinary finite likelihood ratios. Reserve exact zero and one for declared logical or modelling commitments, not small samples or high confidence.
- Neither risk nor the marginal improvement must decline on every pass. Evidence can correctly reveal greater risk.

The no-action reductions assume the target remains unchanged during the interval. Environmental change requires its own transition even when no repair is attempted.

Successive observations on an unchanged target use **history-conditional** likelihoods. Their ratios multiply by the chain rule. Independence is a sufficient simplification; it is not a consequence of different model names, architectures, or prompts.

## 4. Observation and repair: worked cases

Let a binary review have sensitivity \(q=P(D\mid H,\mathcal I)\) and false-positive rate \(f=P(D\mid\neg H,\mathcal I)\). The actual observed branches give

\[
B_+=\frac{Rq}{Rq+(1-R)f},
\qquad
B_-=\frac{R(1-q)}{R(1-q)+(1-R)(1-f)}.
\]

Timeout, abstention, and unresolved output require separate observation categories when they occur; they are not automatically negative findings.

With \(f=0\), the negative branch becomes

\[
B_-=\frac{R(1-q)}{1-qR},
\]

preserving the valid original CDSFL recurrence. It describes a clean review of the old target.

### The repair counterexample, resolved

Assume one scoped flaw, \(R=1/2\), \(q=4/5\), no false positives, and perfect repair only after a positive result.

| Outcome | Branch probability | Risk after observation | Risk after the prescribed action |
|---|---:|---:|---:|
| Positive | \(2/5\) | \(1\) | \(0\) |
| Negative | \(3/5\) | \(1/6\) | \(1/6\) |

The expected post-cycle risk is \(1/10\). The negative-branch risk is \(1/6\). The positive branch after its perfect repair has risk zero. The revised model preserves all three quantities without conflating them.

A clarification to the preceding review: zero remaining risk for a confirmed flaw assumes the perfect repair actually occurs. If an additional detector still gates repair with sensitivity \(q\), the ex-ante risk is instead \(1-q\). The earlier recurrence returning one is incorrect under either of those repair policies when \(q>0\).

For general result-dependent actions with parameters \((s_+,b_+)\) and \((s_-,b_-)\), enumeration gives

\[
\mathbb E[R_{\mathrm{next}}]
=R\{q(1-s_+)+(1-q)(1-s_-)\}
 +(1-R)\{fb_++(1-f)b_-\}.
\]

With observation alone, \(\mathbb E[B]=R\). Learning does not manufacture an expected reduction in the probability of a fixed proposition.

### Repair followed by new errors

To retain the project's repair/reinjection vocabulary, suppose raw repair removes the specified failure with probability \(\sigma\), followed by introduction probability \(\nu\) on each intermediate clean path. Assume that conditional introduction rate is the same for initially clean and successfully repaired paths. Then

\[
s=\sigma(1-\nu),\qquad b=\nu,
\qquad
R_{\mathrm{next}}=\nu+(1-\nu)(1-\sigma)B.
\]

Raw efficacy \(\sigma\) and net removal \(s\) must not be interchanged. Different introduction rates on those paths can instead use \(s=\sigma(1-\nu_1)\), \(b=\nu_0\).

The action schedule matters. In the numerical example above, let \(\nu=0.1\). New errors possible only on the positive-result repair branches give expected risk \(0.14\). An additional process that can introduce errors after every cycle gives \(0.19\). Neither schedule should silently stand in for the other.

After an action, verification supplies evidence about the **new** target. Passing the tests used to optimize the repair is not automatically independent confirmation.

### Dependence, false alarms, and replication

The executable checks also establish these constructed examples:

| Case | Correct result |
|---|---|
| Prior \(0.1\), sensitivity \(0.8\), false-positive rate \(0.2\), positive result | Posterior \(4/13\), not certainty. |
| Prior \(1/2\), a negative \(q=0.8,f=0\) review | Posterior \(1/6\). |
| Copy exactly that already recorded observation on the unchanged target | Still \(1/6\): conditional likelihood ratio is one. |
| Collect a genuinely conditionally independent replication with the same operating characteristics, also negative | Posterior \(1/26\). Publication originality is irrelevant to this calculation. |

A tool rerun on a changed target may supply new evidence; the duplicate rule concerns the same already-conditioned information. Literature provenance and publication-selection effects can legitimately affect an observation model. A generic novelty score is not a substitute for that model.

## 5. Preserve the valid lineage, correct the interpretations

| Existing component | Proposed treatment |
|---|---|
| Coverage \(C=1-\prod_i(1-q_i)\) | Retain with \(q_i=P(D_i\mid H,\text{all earlier misses, relevant context})\) on supported histories. Replacing conditional sensitivities by marginal ones requires a justified factorization; conditional independence given the flaw is sufficient. |
| Weighted class coverage \(F\) | Retain as a defined process measure. It is not automatically a fraction of all possible scientific failure modes. Estimated coverage needs calibration too. |
| Bayesian residual risk \(R\) | Retain, add false-positive and other observation channels, and state the event and conditioning explicitly. |
| Three-phase repair extension | Replace its repair interpretation with the observation-plus-transition derivation above. Do not preserve an incorrect reduction merely for compatibility. |
| Literature novelty and search coverage | Report separately, with scoped searches and provenance. They may influence discovery priorities; they do not automatically suppress corroborating evidence. |
| Diversity discounts and Ising dependence | Keep as candidate fitted approximations where useful. Pairwise structure is a restricted family, not a representation of all dependence. |
| Human/machine combination | Use conditional incremental detection. For detections \(M,J\), \(P(M\cup J\mid H)=P(M\mid H)+P(\neg M\mid H)P(J\mid\neg M,H)\). Retain other context throughout. |
| Tool gates and solution scores | Retain auditable admissibility checks. A bounded score or fraction of chosen tests passed is not automatically a calibrated sensitivity or repair probability. |
| Duane discovery-rate and convergence telemetry | Retain reported findings at their stated telemetry scope. Validate any link to unknown residual flaws separately. |
| Stopping and substrate-ceiling rules | Treat as policies or hypotheses with stated assumptions. A low-yield pass does not establish exhaustion of all useful methods. |

For a fixed prior \(0<\pi<1\), the no-false-positive all-miss coverage relation remains

\[
R=\frac{\pi(1-C)}{(1-\pi)+\pi(1-C)},
\qquad
C=\frac{\pi-R}{\pi(1-R)}.
\]

This fixes the isolated inverse sign error and preserves the distinction between coverage and posterior risk. The map is not an invertible relation between arbitrary weighted aggregates.

The original definitions and extensions are in the [pinned appendix](https://github.com/jebus197/Constraint_Engineering/blob/9e3dfe9d68b428acb98e65c0ad3800ec571a4da4/docs/MATHEMATICAL_APPENDIX.md). The preceding review provides detailed line references. Any future implementation must change the documentation, forecasts, and dependent stopping rules together; a symbol-only substitution would conceal changed semantics.

## 6. Parameter uncertainty and limits of compression

The equation cannot turn unspecified inputs into knowledge. Record a prior's source and uncertainty. A default \(R=0.5\) is a symmetric assumption, not a universally conservative estimate. Seeded defects can help measure sensitivity to those seeds; their prevalence does not establish the natural prevalence of unknown defects.

Marginalize uncertain parameters using their **joint, correctly conditioned distribution**. Do not independently average every parameter and insert the averages. For example, after the evidence suppose two equally plausible parameter settings are

\[
(B,s,b)=(0.8,0.8,0),\qquad (0.2,0.2,0).
\]

Both yield risk \(0.16\), so the joint average is \(0.16\). Separate means give \((0.5,0.5,0)\), incorrectly yielding \(0.25\). Conditioning removal on the initially flawed state instead gives marginal \(s=0.68\), which correctly recovers \(0.16\) at \(B=0.5\).

In general, with latent parameters \(\theta\),

\[
R_{\mathrm{next}}
=\mathbb E_\theta[(1-s_\theta)B_\theta+b_\theta(1-B_\theta)
 \mid e,\mathcal I,a],
\]

under the same declared policy. Before the evidence, the likelihoods also require the appropriate state-conditional parameter distribution.

A practical initial implementation can use a low-dimensional calibrated model with uncertainty intervals and sensitivity bounds. When the necessary inputs are unsupported, return **unestimated**, together with evidence and scope, instead of presenting a precise probability.

Scalar insufficiency has an elementary counterexample. Two targets each have probability \(1/2\) of “some flaw.” In one population the only possible flaw is A; in the other it is B. A perfect negative test for A yields risk zero in the first and \(1/2\) in the second. Equal initial risk does not imply equal future evidential response.

## 7. Applicability beyond a binary flaw

For several mutually exclusive states exhaustive within the declared model, use probabilities \(p_i\), observation likelihoods \(\ell_i\), and a transition matrix \(T_{ij}=P(\text{new state }j\mid\text{old state }i,e,\mathcal I,a)\), with each row summing to one:

\[
p'_j=\frac{\sum_i T_{ij}\ell_i p_i}{\sum_i\ell_i p_i}.
\]

Require nonnegative state probabilities summing to one, nonnegative likelihoods, a positive denominator, and the same action-selection conditions as in the binary construction. The binary equation is its two-state projection. For competing claims about an unchanged world, no target-changing action means \(T\) is the identity. Scientific hypothesis revision changes the candidate description or state space and must be recorded explicitly.

For overlapping flaw classes, \(\sum_k c_kR_k\) is expected additive loss when the consequences \(c_k\) are defined appropriately. It does not generally equal \(P(\text{any flaw})\). Independence is unnecessary for linear expectation, but a union probability needs joint information; with only marginal risks,

\[
\max_k R_k\leq P\left(\bigcup_kH_k\right)
\leq \min\left(1,\sum_kR_k\right)
\]

for the included classes. Interacting consequences require a richer loss function.

Scientific discovery can introduce a previously absent hypothesis or mechanism. A catch-all “other” category has no useful numerical prediction without an observation law. Record excluded possibilities, model misfit, and sensitivity to alternatives; do not invent a number claimed to quantify every unknown unknown.

The construction is substrate agnostic in its definitions: a human, an AI model, an instrument, or a team can produce evidence or take actions. This does not make their estimated parameters interchangeable. Shared data, correlated errors, complementary capabilities, selection, and cost determine whether a collective outperforms an individual. Neither “more agents always help” nor a universal single-agent capability ceiling follows from this equation.

## 8. Choosing actions, experiments, and stopping

After evidence has been collected, the expected reduction in this binary failure probability from an action is

\[
\Delta_a=B-R_{\mathrm{next}}=sB-b(1-B).
\]

It is positive precisely when \(B>b/(s+b)\), provided \(s+b>0\). With \(s=b=0\), it is zero. This is a scoped risk comparison before adding costs or other consequences.

Experiment value is different. For a fixed hypothesis, expected information gain is

\[
I(H;E\mid\mathcal I)
=\mathcal H(R)-\mathbb E_E[\mathcal H(B_E)]\geq0,
\]

where \(\mathcal H\) is binary entropy. A particular observation can increase uncertainty even though the expected information gain is nonnegative.

For decisions, define the loss of a final decision \(d\) in state \(h\), \(C(d,h)\). When an experiment \(j\) only supplies information, its one-step net decision value is

\[
V(j)=
\min_d\mathbb E[C(d,H)\mid\mathcal I]
-\mathbb E_e\!\left[\min_d\mathbb E[C(d,H)\mid e,\mathcal I,j]\right]
-c_j.
\]

Costs must use compatible utility units, or be handled as explicit budget constraints. If a subsequent decision physically changes the target, evaluate its consequences through the transition model. If the experiment itself changes the target, model the actual action/observation order rather than treating it as passive evidence.

This is a one-step policy criterion, not a global optimum. Complementary experiments defeat naive greedy stopping: two independent fair bits individually reveal nothing about their XOR, but together determine it. Where such dependencies matter, consider experiment bundles or limited lookahead, and label any heuristic.

The usable human rule is: **continue when an available investigation or sequence is worth its expected cost under the declared objectives; otherwise state the residual uncertainty and why work stopped.** Distinguish resolved acceptance conditions, a discovered counterexample, economical stopping, budget exhaustion, and unresolved blockage.

No general zero-risk limit is implied. With uninformative evidence and fixed action parameters, \(R_{t+1}=b+(1-s-b)R_t\). When \(0<s+b<2\), its limit is \(b/(s+b)\), since the deviation is multiplied by \(1-s-b\). At \(s=b=0\) nothing changes; at \(s=b=1\) the state generally alternates. These are conditional properties of that fixed process, not a law of scientific progress.

## 9. What would refute this proposal?

Separate a probability identity from a deployable model.

| Claim | Evidence required | Failure or revision trigger |
|---|---|---|
| The compact equation follows from the definitions. | Written derivation and independent calculation. | A valid counterexample satisfying the definitions, or a flaw in the derivation. |
| The observation and action models describe a specified task family. | Prospective predictions and independently resolved outcomes. | Predeclared predictive discrepancies, drift, hidden selection, or omitted mechanisms. |
| Its numerical risks are useful probabilities. | Held-out calibration and forecast skill versus simple comparators. | Material calibration failure or no useful predictive advantage at stated precision. |
| Its policy improves research outcomes. | Matched-budget comparisons using external task outcomes. | No meaningful benefit, harmful changes, or unacceptable missed failures. |
| The richer model generalizes across STEM and substrates. | Transfer to new task families, domains, and participants. | Transfer failure; narrow the claimed scope. |
| CDSFL makes an original contribution. | A precise contribution statement and scoped literature comparison. | Prior work establishing the claimed contribution; revise attribution. |

The broad core is intentionally flexible. For any posterior \(B\) and desired output \(y\), choosing \(s=1-y,b=y\) forces \(R_{\mathrm{next}}=y\). Therefore fitting those quantities after seeing outcomes can explain anything and tests nothing. The empirical claim must freeze or prospectively specify how parameters are obtained.

An unlikely event is not automatically a logical refutation of a stochastic model. Use predeclared predictive tests and practical discrepancy criteria. “No counterexample found” must not become “established true in all applications.” Model criticism and revision are central parts of applied Bayesian work, as discussed by [Gelman and Shalizi](https://arxiv.org/abs/1006.3868).

The accompanying [validation plan](./CDSFL_revised_model_validation_plan.md) provides a staged path that can begin before a distributed build-out.

### 9.1 Guard against conclusions hidden in assumptions

The supplied [Hossenfelder transcript](../work/math-review/Sabine_Maths_and_Circular_Reasoning_transcript.txt), especially 03:05–03:52, describes the risk of a proof that assumes a condition containing the result it claims to establish. This review uses that methodological warning; it does not assess the transcript's claims about any particular current proof.

For each substantive claim, record its exact conclusion, dependencies, and the support for each dependency. Expand important lemmas far enough to ask whether an assumption simply restates the conclusion in different language. A dependency diagram without a visible cycle is insufficient if the conclusion is concealed inside a premise.

For this proposal the dependency audit is:

| Claim | Permitted starting point | What would make the argument circular or unsupported |
|---|---|---|
| The update identity is correct. | Probability axioms, explicit conditional-event definitions, and the stated selection condition. | Treating the identity as proof that supplied empirical inputs are calibrated. |
| A test could expose the specified failure. | Independently resolved reference cases, a justified analytical operating characteristic, or clearly labelled uncertainty. | Inferring high test sensitivity merely because the current target passed or because the reviewer agreed with itself. |
| A repair reduces real failure risk. | Scoped before/after outcomes under the relevant selection policy. | Calling a repair successful because the model assigned it a high success parameter. |
| CDSFL improves research. | Prospective external outcomes against fair comparators. | Defining success as a decrease in the very score the procedure is designed to decrease. |
| A theoretical result is proved. | Independent premises and valid deduction over the stated domain. | Assuming an unproved regularity, existence, solvability, or error bound that already contains the desired conclusion. |

Definitions of \(s,b,\ell_1,\ell_0\) do not establish their numerical values. The mathematical claim is only the conditional update. No assumption that CDSFL works appears in its derivation, and no conclusion that CDSFL works follows from that derivation alone.

Constructed outcome trees check the calculation within supplied worlds. They cannot establish that those worlds describe actual research. A simulation designed to follow the equation is therefore an implementation test, never the sole empirical validation of the model.

### 9.2 Connect severe tests to the original coverage model

One operational requirement of a severe test is that it would seldom **accept** a target containing the specified failure. Let

\[
\beta=P(\text{pass}\mid H,\mathcal I),\qquad
\gamma=P(\text{pass}\mid\neg H,\mathcal I).
\]

Pass must be a predefined observed outcome on an unchanged target. It is distinct from timeout, abstention, or an unresolved investigation. Suppose external calibration or a justified analytical argument supports \(\beta\leq\beta_{\max}\) and \(\gamma\geq\gamma_{\min}>0\). For \(0<R<1\),

\[
\boxed{
R_{\text{pass}}
=\frac{R\beta}{R\beta+(1-R)\gamma}
\leq
\frac{R\beta_{\max}}
{R\beta_{\max}+(1-R)\gamma_{\min}}
}.
\]

The proof is short: posterior odds equal prior odds multiplied by \(\beta/\gamma\), which is at most \(\beta_{\max}/\gamma_{\min}\); conversion from odds to probability preserves order.

For a **completed binary protocol**, pass and failure detection are exhaustive. Then original coverage is \(C=1-\beta\), and if the false-alarm probability is \(\alpha\), \(\gamma=1-\alpha\). History-conditional coverage retains \(C=1-\prod_i(1-q_i)\). This explicitly preserves the original insight: survival is informative according to the examination's ability to expose a relevant error.

As an illustration only, bounds \(\beta\leq0.05\), \(\gamma\geq0.95\), and prior \(R=0.5\) imply \(R_{\text{pass}}\leq0.05\). These are stipulated numbers, not estimates obtained for CDSFL.

A hidden partition assumption would invalidate that calculation. Suppose flawed targets have probabilities (pass, fail, abstain) = (0.05, 0.95, 0), while clean targets have (0.05, 0.05, 0.90). The miss and false-alarm rates are both 0.05, but \(\gamma=0.05\), not 0.95. A pass leaves prior 0.5 unchanged. This case was found during the additional challenge and is included in the checks.

Calibration evidence must apply to the actual target family, test-selection process, and available information. Statistical confidence bounds are not infallible assumptions: propagate their uncertainty and joint coverage. Two separate 95% bounds do not automatically supply a joint 95% guarantee. Average detection across a benchmark also does not establish the same power for every failure subtype. A universal claim requires suitable control across the stated alternatives, or a narrower conclusion.

This operational connection is not a claim to encode every philosophical meaning of severity. It supplies a concrete quantity that experiments can estimate and contradict. The original paper already demands serious attempted refutation, distinguishes corroboration from proof, and permits replacing its equation when another predicts outcomes better. See [P-Pass](https://github.com/jebus197/Constraint_Engineering/blob/9e3dfe9d68b428acb98e65c0ad3800ec571a4da4/PAPER.md#L40) and [Invitation to Falsify](https://github.com/jebus197/Constraint_Engineering/blob/9e3dfe9d68b428acb98e65c0ad3800ec571a4da4/PAPER.md#L1237).

## 10. Applying the revised framework to this revision

The requested self-check is rational as an examination of consistency and evidence. It is not independent validation of the framework's own assumptions.

| Review claim | Evidence and action recorded | Present status |
|---|---|---|
| The earlier repair semantics fail in the elementary example. | Explicit positive/negative outcome tree; old and revised calculations compared. | Counterexample established under the stated repair policy. |
| The new core has a valid probability interpretation. | Bayes plus total probability; separate derivation; exact outcome enumeration. | Established within the definitions and conditioning requirements. |
| Valid original coverage and clean-review results survive. | Algebraic reductions and exact regression cases. | Established within their original valid assumptions. |
| The proposal handles the identified selection and dependence failures. | Private-selection, duplicate-evidence, state-insufficiency, and joint-uncertainty counterexamples; explicit conditions added. | Those failures addressed; no claim of exhaustive discovery. |
| The severe-test bound remains valid with unresolved outputs. | An initially binary-only formulation failed on an abstention counterexample. Replaced it with explicit pass probabilities under flawed and clean states. | Corrected conditional bound derived and checked; empirical rates still unestablished. |
| The inputs are calibrated for real CDSFL work. | No prospective calibration dataset analysed in this revision. | Unestablished. |
| The revision improves actual STEM research or collective performance. | No matched-budget deployment experiment performed. | Unestablished. |
| The equation is historically novel. | It is derived from standard probability identities. No exhaustive priority review performed. | No new-theorem claim; application-level contribution remains to be assessed. |

The old model's useful principles were applied: state claims and constraints, search for disproof, preserve evidence, revise after counterexamples, and distinguish external anchoring from internal coherence. Applying the revised version added explicit target versions, observed branches, action semantics, dependent evidence, and unestimated quantities.

Three delegated passes supplied derivation, adversarial challenge, and validation design. These were instances of the same model and shared context or assumptions. They are separate checks, not independent empirical samples. Reviewer agreement was not multiplied into a confidence estimate.

The reference suite passed **5,600 conditional outcome-tree cases, 650 impossible-observation rejections, 2,000 branch-policy expectations, 125 sequential-repair cases, and 125 reduction/expectation cases**. Eight deliberately incorrect alternatives were rejected. These are constructed exact-arithmetic checks, not 8,500 independent scientific experiments. The general derivation supplies the proof; the finite cases check consequences and implementation.

Files: [reference arithmetic](./CDSFL_revised_core.py), [reproducible checks](./CDSFL_revised_model_checks.py), and [recorded results](./CDSFL_revised_model_check_results.json). Separate supporting scripts also passed overlapping checks; their counts are not added to the main suite. No formal proof assistant or real-world benchmark reproduction was used.

Revision 1.1 adds [severe-test checks](./CDSFL_severe_testing_checks.py) and [their results](./CDSFL_severe_testing_check_results.json): 450 constructed bound cases passed, and three misleading alternatives were rejected, including the newly identified abstention error. These test the stated bound and its limits; they do not estimate real test sensitivity.

No numerical “probability that this model is sound” is reported. Its requisite priors and reviewer error likelihoods have not been calibrated. This is the revised discipline applied to our own claims.

## 11. Keep only components that earn their place

The mandatory core contains the scoped event/history, actual-evidence update, and an action transition only when the target can change. Every further component needs a stated job:

| Component | Job | When to use it |
|---|---|---|
| Coverage/severe-test bound | Explain how a passed test bears on a specified failure. | When its operating characteristics can be justified or estimated. |
| Joint parameter uncertainty | Prevent false precision and incorrect averaging. | Whenever uncertain inputs materially affect the conclusion. |
| Multiple states or flaw classes | Represent distinctions that alter predictions or consequences. | When the binary projection loses decision-relevant information. |
| Expected loss and experiment value | Decide between actions or further investigation under resource constraints. | When making that decision, with stated objectives and costs. |
| Information gain | Compare learning about a fixed hypothesis. | When learning is an explicit objective; it is not a substitute for practical outcomes. |
| Fixed-process limit | Check or refute a claimed convergence/floor property. | Only for a process satisfying the fixed-rate assumptions. |
| Ising or other richer dependence model | Predict dependencies missed by a simpler calibrated model. | After a relevant failure or comparative result justifies the complexity. |

No optional equation is a compulsory implementation layer. An extension that adds neither a necessary correctness condition nor demonstrated explanatory, predictive, or decision value should be omitted from deployment.

## 12. Recommended next work, when the existing build is ready

1. **Adopt the mathematical specification as a candidate revision.** Preserve the old equations and objections as versioned history. Have a probability/statistics reviewer and a domain researcher challenge the definitions and the worked cases.
2. **Create a small compatibility layer.** Store evidence updates, target-changing actions, provenance, and versioned events separately. Keep unestimated parameters visible. Do not silently compare old and new risk values as the same metric.
3. **Run a cheap diagnostic pilot, then lock one task family.** Separate observing frozen targets from repairing cloned targets. Use independently resolved outcomes and simple baseline models.
4. **Evaluate predictive value before complexity.** Add richer dependence, latent states, and adaptive policies only where they improve held-out performance or address demonstrated failure.
5. **Test transfer and collective benefit.** Only then claim broader STEM usefulness or a measured advantage from coordinating more capable and less capable participants.

A compact public statement could be:

> CDSFL organizes scientific enquiry around explicit claims, discriminating evidence, auditable revisions, and testable stopping decisions. Its tests must be capable of exposing the failures they claim to exclude. Its mathematical core updates belief about a defined failure and predicts how an action changes that failure. Its reliability in any application is measured against external outcomes within a stated scope.

This preserves a meaningful claim about scientific enquiry while leaving the system open to refutation. The sound conditional identity can survive changes in the machinery around it. The estimated probabilities, scientific scope, and demonstrated usefulness must remain revisable.
