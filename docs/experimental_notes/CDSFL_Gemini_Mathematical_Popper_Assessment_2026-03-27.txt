# Assessment of Gemini's Mathematical Popper Framework

**27 March 2026**

---

## What Gemini Produced

Over three iterations, Gemini 3.1 Pro produced a mathematical formalisation of the CDSFL review process. It proposed five operators that together form what it called "a complete epistemic dashboard for the team manager."

**Operator 1: The Duane Intensity lambda.** Measures the rate of discovery across review rounds. Based on the Non-Homogeneous Poisson Process from reliability engineering. This has been independently verified against our bench data and is already built into the decay analysis sidecar. CX confirmed it fits the data better than simple geometric decay on 17 of 18 CDSFL runs.

**Operator 2: Net Severity V-net.** Measures the probability of error detection using Mayo's severity criterion. A finding that passed a severe test (one with a high probability of detecting the error if it existed) is more corroborated than one that passed a weak test. The concept is sound but the specific computation of per-finding severity is not fully defined.

**Operator 3: KL Divergence I-G.** Measures the impact of human expert guidance by computing the information-theoretic divergence between the finding distribution with and without guidance. This quantifies the expert's contribution in bits rather than in finding counts.

**Operator 4: Seeded Sensitivity S-H.** Measures calibration by checking whether models find deliberately planted known defects. It provides ground truth validation. However, our frontier bench tasks do not have seeded defects, so this operator cannot currently be computed on our main test data.

**Operator 5: Normalised Mutual Information and sycophancy score S-sync.** Measures adversarial independence between models. If two models produce highly overlapping findings, one may be deferring to the other rather than analysing independently. The sycophancy score combines diversity with calibration (S-H) to distinguish genuine consensus from groupthink.

---

## CC P-Pass Findings

**Claim that the framework is complete.** Overclaimed. Five operators covering five dimensions is a useful structure, but our own mathematical appendix already extends beyond this framework. Missing dimensions include: residual risk (what remains unfound), uncertainty bands on all estimates, severity weighting of individual findings, and directional influence after exposure (does seeing one model's work change another's analysis in a measurable direction).

**Claim that NMI measures sycophancy.** Partially correct but imprecise. Static NMI measures redundancy between finding sets, not deference. CX identified that the blind-to-confer adoption delta (how much a model's findings change after seeing others' work) is a better sycophancy measure. A model that produces 5 findings blind and then produces 5 identical findings after seeing the captain's work is not deferring. A model that produces 5 findings blind and then abandons all 5 and adopts the captain's findings is deferring. Static NMI cannot distinguish these cases. The adoption delta can.

**Claim that S-sync works without seeded defects.** It does not. Without S-H, the formula collapses to a pure conformity score that cannot distinguish "agreeing because correct" from "agreeing because deferring." This is the central limitation for frontier task application.

**Claim that no further mathematical work is needed.** Premature closure. The temporal dynamics (how these metrics evolve across rounds), the severity computation for V-net, and the seeded defect requirement for S-sync are all unresolved.

---

## CX P-Pass Findings

- CX confirmed that proper binary-label mutual information IS computable from our existing data using `scikit-learn`, with re-canonicalisation via the refinements module. But set-overlap (Jaccard) is **NOT** a valid NMI approximation — they are different mathematics measuring different things.
- CX confirmed that S-sync is effectively dead without S-H on frontier tasks. We have seeded-fault bench tasks separately, but transferring that calibration to frontier tasks is speculative.
- CX confirmed the dashboard is overclaimed as complete. Our own mathematical appendix already contains extensions (residual risk, class-specific correlation, parameter uncertainty, severity-weighted loss) that Gemini's framework does not include.

---

## What Is Genuinely Useful

**The Duane model (lambda).** Already verified and built. Provides the core diagnostic for the decay curve framework.

**The NMI concept adapted as adoption delta.** Measures how much a model's output changes after seeing others' work. Computable from our existing blind vs. confer finding data. Better than static NMI for detecting deference.

**The five-operator dashboard structure.** Provides a framework for the analysis pipeline even if individual operators need refinement. Discovery rate, test severity, human impact, calibration, and independence are the right dimensions to measure — even if the specific formulas are incomplete.

**The role-based insight.** Gemini produced these mathematical formalisations while CC and CX did not. This confirms Gemini's position as the mathematical specialist in the team architecture. It is not strong at practical review (flat decay curves on bench tasks) but is strong on theoretical framework development.

---

## What Is Not Useful

- **The completeness claim.** The framework is a good start, not a finished product.
- **S-sync on frontier tasks.** Dead without seeded defects.
- **V-net without severity computation.** The concept is sound but the implementation is undefined.

---

## Overall Assessment

Not bunk. Not churn. **Genuine mathematical contribution with overclaimed self-assessment.**

Gemini produced the theoretical framework that the practical reviewers (CC and CX) needed but could not produce independently. This is the distributed compute system working as designed: each model contributing according to its strengths. The mathematical specialist produced mathematics. The code specialists identified practical implementation issues. The team captain flagged what was computable and what was not.

The framework should be incorporated into the analysis pipeline with the corrections identified by CC and CX:
- The five-operator structure provides the dashboard.
- The Duane model provides the core diagnostic.
- The adoption delta replaces static NMI for sycophancy detection.
- The seeded sensitivity and severity computation remain open research questions for future work.
