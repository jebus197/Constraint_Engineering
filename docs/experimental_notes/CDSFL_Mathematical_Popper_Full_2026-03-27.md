# Mathematical Formalisation of Popper's Falsification and Domain Expert Configurations — Full Treatment

**27 March 2026**

---

## The Question

Can Karl Popper's philosophy of falsification be mathematically modelled? Is it already implicitly expressed in the CDSFL decay curve mathematics? If so, could mathematical models of domain-specific falsification processes become the basis for domain expert configurations? What would this mean for the efficiency of CDSFL and for AI systems more broadly?

---

## Popper the Philosopher, Not the Mathematician

Popper expressed falsification in natural language. A theory is scientific if and only if it makes predictions that could be shown false. Theories gain corroboration by surviving severe tests. Bolder theories that predict more are more falsifiable and therefore more scientific. These are powerful ideas, but they are verbal, not mathematical.

For modern AI systems, verbal instructions leave significant scope for interpretation. A chatbot told to "try to disprove your conclusions" interprets this as "add a caveat." A capable reasoning model interprets it as "genuinely attack the weakest claims." The instruction is the same. The interpretation varies by model.

---

## Three Prior Attempts at Mathematical Popper

**Popper himself** attempted a mathematical formulation. His degree of corroboration formula C(h,e,b) relates hypothesis h, evidence e, and background knowledge b:

```
C = [P(e|h) - P(e)] / [P(e|h) - P(e,h) + P(e)]
```

This measures the outcome of testing — how corroborated is this hypothesis after this evidence? But it does not model the process. It tells you where you ended up, not how the journey unfolded.

**Deborah Mayo**, in work published in 1996 and expanded in 2018, went further. Her severity criterion states that a hypothesis passes a severe test when the test had a high probability of detecting the error if the error were present. Formally, the severity of a passing result is the probability that, if the hypothesis is false, a test would have produced evidence less favourable to the hypothesis than the evidence actually obtained. This IS computable. Mayo explicitly built on Popper while correcting his lack of statistical sophistication. Her criterion maps directly to the CDSFL verification score v-bar multiplied by coverage C: if the product v-bar × C is high, the test was severe in Mayo's sense.

**Kevin Kelly** at Carnegie Mellon University went furthest in the mathematical direction. He proved that Occam's razor — the preference for simpler and more falsifiable theories — is mathematically necessary for efficient convergence to truth. Not just useful. Necessary. Any method that converges reliably to the right answer must incorporate a simplicity bias. This connects Popper's preference for falsifiability directly to computational convergence bounds. Kelly's work maps to CDSFL's HARD and SOFT classification, which directs attention to the most constrained and therefore most falsifiable claims first.

But none of these three modelled the process of falsification as it unfolds over iterative rounds. Popper's formula gives a snapshot after testing. Mayo's criterion evaluates a single test. Kelly's theory describes long-run convergence. **None of them describe what happens round by round as falsification proceeds iteratively. That is what the decay curve does.**

---

## The Decay Curve as Mathematical Popper

Consider what actually happens in each round of the CDSFL protocol. The solution being reviewed contains F falsifiable claims. Each claim has a detection probability p_i — the probability that a reviewer spots it in a single round. Claims are naturally ordered by detectability: p_1 >= p_2 >= ... >= p_F. The easiest to falsify have high p values. The hardest have low p values.

- **Round 1:** reviewers find the easy-to-falsify claims. The boldest conjectures, in Popper's language, fail first because they are the most exposed. The expected number of findings is approximately the sum of all p_i values.
- **Round 2:** the easy falsifications are done. Those claims are eliminated from consideration. The remaining claims survived round 1 and are now partially corroborated in Popper's sense. The reviewers must find subtler issues. The rate of discovery drops.
- **Round n:** the solution has survived n-1 rounds of attempted falsification. What remains is maximally corroborated. The decay toward zero IS the mathematical expression of approaching corroboration.

The formula is:

```
f(n) = F * p_bar * (1 - p_bar)^(n-1)
```

This is geometric decay. The decay parameter `(1 - p_bar)` is determined by three things:
1. The reviewer's expertise (E* in CDSFL notation)
2. The domain's characteristic difficulty distribution of errors
3. The methodology applied — structured or unstructured

This is Popper expressed as a measurable dynamic function. Not the outcome (like Popper's C). Not the criterion (like Mayo's severity). But the process — how falsification actually unfolds over iterative rounds of testing.

---

## Why Different Domains Produce Different Curves

The detection probability distribution — the spread of p_i values across all falsifiable claims in a typical artifact — differs by domain.

**Mathematics:** errors are bimodal. A proof step is either correct or incorrect. If incorrect, it is usually detectable by anyone competent (high p value) or it is extremely subtle (low p value). This produces steep initial decay followed by a long flat tail. The curve looks like a cliff.

**Engineering:** errors are more uniformly distributed. Constraints range smoothly from obvious (missing load path) to subtle (thermal expansion under cyclic loading interacting with fatigue). Each successive check reveals a slightly harder issue. This produces gradual smooth decay — the curve looks like a gentle slope.

**Code:** errors are multi-modal. Syntax errors have p near 1 and are found immediately. Logic errors have p around 0.5 and are found with moderate effort. Design flaws have p around 0.1 and are found only with deep analysis. This produces a stepped curve with plateaus.

These domain-specific distributions are mathematical signatures. They can be measured empirically from bench test data and encoded as domain parameters.

---

## Mathematical Popper as Domain Expert Configuration

If you know the expected difficulty distribution for a domain, a domain expert config evolves from "check these things" (verbal) to a mathematical model. The config would specify:

- The expected decay model (exponential or power law)
- The expected decay rate range (e.g. 0.3 to 0.6)
- The difficulty distribution type (bimodal, uniform, or multi-modal)
- The expected total number of falsifiable claims
- The minimum number of rounds required for corroboration
- The severity threshold from Mayo's criterion
- The expected order of falsification (e.g. boundary conditions first, then proof structure, then edge cases)

This config does not tell the model what to think. It tells the model what genuine falsification looks like in this domain. The model can then compare its own behaviour against the mathematical template. If its curve is flat but the domain expects steep decay, it is probably churning. The mathematical model becomes self-diagnostic.

---

## Efficiency Implications

Currently the CDSFL directives say "try to disprove your conclusions." This is Popper in words. The model interprets this however its training disposes it to.

A mathematical config says: produce findings at a rate that decays geometrically with parameter between 0.3 and 0.6. If your rate is flat, your findings are not genuine. The model does not need to understand Popper philosophically. It needs to match a mathematical signature empirically. This is more efficient because it is measurable, not interpretable.

**The prediction:** mathematical configs will improve weaker models more than stronger models. Stronger models already interpret "try to disprove" correctly. Weaker models do not. A mathematical config that says "your curve must decay with parameter > 0.3" gives the weaker models a concrete target that verbal instructions do not provide.

---

## Modelling Domain Experts Themselves

If different experts produce different decay curves on the same tasks, the curve IS their cognitive signature for that domain:

- An expert who produces steep decay is a rapid scanner who finds obvious issues fast but may miss subtle ones.
- An expert who produces gradual decay is methodical, finding issues at a steady rate across difficulty levels.
- An expert whose curve matches the domain's expected distribution is well-calibrated for that domain.

Encoding this as a config means encoding not just what the expert knows, but how they apply it. This makes the domain expert config genuinely novel as an intellectual asset. It is not a knowledge dump. It is a mathematically characterised cognitive strategy that produces measurably different analytical results when applied.

---

## Novelty Assessment

The individual components exist:
- Popper's corroboration formula (1934)
- Mayo's severity criterion (1996)
- Kelly's convergence theory (1990s)
- Defect discovery curves in software engineering (1970s onward)

**The specific assembly** — using mathematical models of falsification dynamics as domain-specific AI review configurations, measured via empirically observed decay curves, grounded in the Popper-Mayo-Kelly tradition — does not appear to have prior art. The closest is Mayo's work, which explicitly operationalises Popper as a statistical criterion but applies it to experimental design, not to AI review protocols.

The assembly is what appears to be new. Not the components. The integration.

---

## Falsifiable Predictions

1. Different STEM domains will produce statistically distinguishable decay curve shapes on the bench test.
2. A domain expert config that includes expected falsification dynamics will produce better analytical results than a config with natural language instructions alone.
3. Mayo's severity criterion maps to v-bar × C. Computationally verifiable from existing bench test data.
4. Kelly's convergence result predicts that CDSFL's HARD/SOFT classification should produce faster convergence than unstructured review.
5. Mathematical configs will improve weaker models more than stronger models. Testable by comparing the change in D values with vs without mathematical configs.
6. Domain experts with different cognitive styles will produce measurably different decay curves on the same tasks.

---

## Sources

- Popper's degree of corroboration and statistical perspectives: arXiv 2007.00238. Also at Springer.
- Deborah Mayo. Statistical Inference as Severe Testing. Cambridge University Press, 2018.
- Kevin Kelly. Formal Learning Theory. Stanford Encyclopedia of Philosophy. Also Carnegie Mellon publications.
- Karl Popper. Stanford Encyclopedia of Philosophy entry.
