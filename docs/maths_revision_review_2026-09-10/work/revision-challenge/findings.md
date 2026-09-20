# Independent challenge of the proposed CDSFL observation/action revision

**Scope:** bounded adversarial review of the candidate received from the root agent on 9 September 2026. This is a separate derivation and counterexample pass by another instance of the same model, not an independent empirical validation or human review. No upstream files were changed. Exact checks are in `checks.py`.

## Verdict

The proposed equation is a correct one-step probability identity when all its event definitions and conditioning are satisfied. It repairs the principal observation/intervention confusion in the previous recurrence. It is not by itself a closed scalar model of scientific enquiry, a calibrated predictor of unknown flaws, or a new mathematical law. Its compactness is defensible only if the accompanying history and state requirements remain explicit.

The strongest qualification concerns the action conditioning. Let F be recorded pre-action history including the actual observation. If an action is externally fixed, or chosen from F using randomisation independent of the hidden state conditional on F, then z=P(H|F) is the appropriate pre-action probability. With s=P(not H'|H,F,action) and b=P(H'|not H,F,action), total probability yields r'=(1-s)z+b(1-z). If observed action selection itself carries unrecorded information about H, z must condition on that information/action too. Alternatively define action kernels interventionally and distinguish policy evaluation from observational records.

## Exact counterexamples and required restrictions

### 1. A scalar risk is not sufficient state

In world A, the target is clean with probability 1/2 and contains only flaw A with probability 1/2. In world B, it is clean with probability 1/2 and contains only flaw B with probability 1/2. Both have r=P(any flaw)=1/2. A perfect test for flaw A returns negative. In world A the posterior is zero; in world B it remains 1/2. Their different conditional likelihoods, which depend on retained subtype information, rescue the proposed equation. The scalar r alone cannot determine them.

Even a list of marginal flaw probabilities need not suffice. Two flaws each with marginal probability 1/2 can be perfectly correlated, giving P(any)=1/2, or mutually exclusive, giving P(any)=1. Similarly, net complete-removal efficacy for an "any flaw" event depends on the distribution of simultaneous flaws. A general compact interface therefore needs a structured state/history provider; it must not imply that the scalar stores everything necessary for subsequent updates.

### 2. Action choice can itself be evidence

Let r=1/2 and let the recorded observation be uninformative. A controller privately sees whether the target is flawed and chooses idle only when it is clean. Conditional on observing idle, the correct risk is zero. Using z=1/2 and an idle transition s=b=0 gives 1/2. This failure is avoided by retaining the controller's information, conditioning on action selection, or evaluating an explicitly fixed intervention. It is not a defect in total probability.

### 3. Detection-dependent repair requires outcome-dependent kernels

With r=1/2, sensitivity 4/5, no false positives, and perfect repair only after a positive detection, the positive branch has probability 2/5 and post-repair risk zero; the negative branch has probability 3/5 and risk 1/6. The expected post-cycle risk is 1/10. The candidate reproduces this exactly with s_positive=1 and s_negative=0. Inserting perfect repair s=1 on the negative branch would incorrectly assume an undetected flaw was repaired. Thus a single advertised repair score cannot be silently shared between all evidence outcomes.

### 4. Marginal means do not preserve uncertain dependencies

Suppose two equally likely posterior parameter worlds have (z,s,b)=(4/5,4/5,0) and (1/5,1/5,0). The final risk is 4/25 in either world. Substituting separate means z=1/2, s=1/2, b=0 yields 1/4. Integrate the joint posterior expression or use correctly event-weighted marginal conditional probabilities. Ordinary averages of estimated skill and risk do not have those meanings. In this example, the correctly marginalised net removal conditional on a flawed target is 17/25, not 1/2.

This does not require that every deployment use a complex hierarchical model. A valid alternative is a clearly labelled range under disclosed assumptions, or an unestimated probability. But uncertainty bands obtained by independently varying impossible combinations of dependent parameters need corresponding qualification.

### 5. General actions need not preserve the ordering of prior risks

The derivative of the action map with respect to z is 1-s-b. The candidate permits s=b=1: an action deterministically flips flawed/clean status, so r'=1-z. This is a valid transition and reverses ordering. Claims such as "higher current flaw risk always means higher post-action flaw risk" require s+b<=1; they are not universal properties of the corrected equation. The proposed sequential repair/reinjection special case does satisfy that restriction because s+b=σ+ν-σν<=1.

### 6. Free parameters can make empirical fitting vacuous

For any desired output y in [0,1], setting s=1-y and b=y yields r'=y for every z. A post-hoc fit therefore cannot refute the identity if the transitions remain unrestricted. An empirical CDSFL model must precommit to how inputs are estimated, when they may change, which reference classes they concern, and which held-out forecasts test them. The mathematical identity cannot establish those quantities itself.

### 7. Greedy stopping can miss complementary investigations

Let X and Y be independent fair bits and let H=X XOR Y. Observing either bit alone leaves P(H)=1/2 and supplies no information about H. Observing both determines H. Stopping whenever each individual next action has zero expected information gain can therefore stop before a valuable two-step investigation. One-step value is a transparent heuristic, not a general optimality theorem. Limited look-ahead, task dependency structure, or explicit exploratory budget may be needed.

## Further boundaries the final specification should state

- **Impossible observations:** if rL1+(1-r)L0=0, the update is undefined. Flag model/data inconsistency; do not quietly clamp a number into existence. Probability-zero dogmatic priors cannot generally learn contrary events within the same model. For continuous observations, use a consistently defined density/mass or likelihood, not the literal probability of an exact real-valued reading.
- **Dependence and adaptivity:** correctly conditioned likelihoods can handle dependent or adaptively selected tests; this is an identity, not a recipe for estimating those likelihoods. A duplicate report conditional on its original normally adds no evidence about the same underlying event. Selection of a winning result and omission of failed attempts changes the relevant likelihood. Known stopping based on the fully retained observations is different from selective reporting.
- **Version and criterion integrity:** the state transition must concern the same acceptance criterion on a new target version. Weakening a bridge's load requirement from 100 kg to 1 kg cannot count as successful repair of the original requirement. Changes in scientific claims or scope require an explicit mapping or a new event; they must not manufacture apparent progress through target redefinition.
- **Scope is unavoidable:** a probability of no flaw in a named class is not a probability of unrestricted correctness. Correlated flaws, unknown flaw classes, shifting instruments, and new operating regimes require explicit limits. Scientific discovery often changes which hypotheses are under consideration; the binary identity can be applied locally, but it does not replace a richer hypothesis space.
- **Probability is not severity or value:** event probability, consequence, decision utility, originality, and attribution answer different questions. A major scientific refutation can increase the probability that a favoured claim is false while constituting valuable progress.
- **Calibration labels:** no known flaw found is not a verified negative label for "any flaw exists." Flaw injection can calibrate detection on the injected reference class, not automatically on unknown natural flaws. Labels and unexamined cases need their own uncertainty and selection records.
- **Self-audit:** checking bounds, reductions, and enumerated outcome trees shows conditional mathematical consistency. Agreement from this reviewer is not a calibrated sensitivity estimate, and should not be converted to a numerical residual-risk claim about the proposal. Useful self-application can mark which claims have proofs, counterexample searches, or still-unestimated empirical inputs.

## Recommended final positioning

Present the collapsed equation as a human-readable **evidence-and-action accounting identity**, backed by an explicit state/conditioning contract. Present calibration, scientific credit, and allocation as separately testable models or policies. The scientific contribution, if established, would lie in operational definitions, useful estimators, dependable cross-domain performance, and the integration of these components; the one-step identity itself is familiar probability theory.

The candidate passes the prior detection/repair counterexample and withstands the attacks above when these restrictions are included. Removing those restrictions would reintroduce misleading generality even though the displayed algebra remained correct.
