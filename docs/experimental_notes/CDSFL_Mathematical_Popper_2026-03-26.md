# Mathematical Formalisation of Popper's Falsification and Domain Expert Configurations

**26 March 2026**

---

## The Question

Has anyone previously attempted to mathematically model Karl Popper's falsification process? If so, could such a model become the basis for domain expert configurations under the CDSFL schema? And does the CDSFL decay curve framework already contain a mathematical expression of Popper's philosophy, even if this was not explicitly recognised?

---

## Existing Mathematical Approaches to Popper

Three significant bodies of work exist that attempt to mathematically formalise falsification.

**First, Popper's own degree of corroboration formula.** Popper himself proposed a mathematical measure: C(h,e,b), a formula relating hypothesis h, evidence e, and background knowledge b. This formula captures how well a hypothesis is corroborated by evidence, given what we already know. However, Popper was emphatic that corroboration is not a probability. The formula is mathematical but limited. It does not model the process of falsification itself, only the outcome of having survived a test.

**Second, Deborah Mayo's severe testing framework**, published in 1996 and expanded in 2018. Mayo formalised Popper's insight as a statistical criterion. A hypothesis passes a severe test when the test had a high probability of detecting the error if the error were present. More formally, the severity of a passing result is the probability that, if the hypothesis is false, a test would have given results which match the hypothesis less well than the ones actually obtained. This IS a mathematical formalisation of falsification, expressed as a probability function. Mayo explicitly built on Popper while correcting his lack of statistical sophistication.

**Third, Kevin Kelly's formal learning theory** at Carnegie Mellon University. Kelly applied computational learning theory to the philosophy of science, studying when and how inquiry converges on truth. His work shows that a fixed simplicity bias — the preference for simpler and more falsifiable theories — is necessary if inquiry is to converge to the right answer efficiently, whatever the right answer might be. This connects Popper's preference for falsifiability directly to mathematical convergence theory.

---

## The CDSFL Decay Curve as Implicit Mathematical Popper

The founder's insight is that the CDSFL decay curve framework already contains a mathematical expression of Popper's philosophy, even though it was not designed with this connection in mind.

Consider what the decay curve measures:

- **D (decay rate)** measures how quickly a review process exhausts the falsifiable claims in a solution. In Popper's terms, this is the rate at which a hypothesis survives successive attempts at refutation. A steep decay means the easy-to-refute claims were found and eliminated quickly. A gradual decay means the falsification process required sustained effort. A flat line means no genuine falsification occurred at all.
- **v-bar (verification score)** measures how reliably the falsified claims are confirmed as genuine errors. In Mayo's terms, this is the severity of the tests. A high v-bar means the tests had a high probability of detecting the errors that were present.
- **A (total verified findings)** measures how much of the hypothesis was actually falsified. A high A means many claims were refuted. A low A means the hypothesis was largely corroborated.
- **C (coverage)** measures what fraction of the falsifiable content was actually tested. In Kelly's terms, this relates to convergence. Full coverage means the inquiry has tested everything testable.

Together, the D, v-bar, A, C fingerprint is a mathematical characterisation of the falsification process applied to a specific artifact by a specific reviewer under specific conditions. This IS Popper expressed as a measurable function, even though it was derived from empirical observation of AI model behaviour rather than from philosophical analysis.

---

## Domain-Specific Falsification Curves

Different domains produce different types of errors, and therefore different falsification dynamics:

- A **mathematics proof** has errors that are either present or absent, typically found quickly, producing steep decay.
- An **engineering design** has interdependent constraints that must be checked sequentially, producing gradual decay.
- **Software** has surface bugs found fast and deep logic errors found late, producing multi-modal curves.

If these domain-specific patterns are consistent — meaning mathematics always produces steep curves and engineering always produces gradual curves — then the expected curve shape becomes a mathematical signature of the domain's falsification dynamics. This signature can be encoded as a domain expert configuration.

A structural engineering domain expert config might specify: expected decay rate D between 0.3 and 0.6, expected coverage requiring 4 to 5 rounds, primary HARD constraints are load path integrity and safety factors, falsification order is connections first then members then foundations. This is Popper's falsification process, mathematically parameterised for a specific domain.

---

## Implications for Domain Expert Configurations

If this connection holds, domain expert configs evolve from natural language instruction sets to mathematically grounded models of domain-specific falsification. The config does not just tell the model what to check. It tells the model what the falsification process should look like in this domain.

This has several consequences:

1. **Configs become verifiable.** If a config predicts D between 0.3 and 0.6 for structural engineering, and the observed D is 0.1, either the config is wrong or the model is not performing genuine analysis.
2. **Configs become transferable with quality metrics.** A domain expert's config can be tested against the predicted curve. If it produces the expected falsification dynamics across multiple tasks, it works. The bench test becomes the verification mechanism for configs.
3. **Machines may respond better to mathematical formulations.** A prompt that says "check the boundary conditions carefully" is vague. A config that specifies expected HARD constraint density and falsification order is precise and measurable.
4. **This connects CDSFL to established mathematical philosophy of science.** The decay curve is a computational implementation of Mayo's severity criterion applied to iterative review. The G-n formula is a specific instance of Kelly's convergence theory applied to multi-reviewer falsification.

---

## Novelty Assessment

The individual components exist:
- Popper's corroboration formula (since 1934)
- Mayo's severity criterion (since 1996)
- Kelly's formal learning theory (since the 1990s)
- Decay curves in defect discovery (software reliability engineering)

What appears to be novel is the specific combination: using empirically measured falsification decay curves as both a diagnostic of AI analytical capability and a parameterised model for domain-specific expert configurations, grounded in the mathematical philosophy of science tradition from Popper through Mayo to Kelly.

This connection was not designed. It emerged from observing AI model behaviour under the CDSFL protocol and recognising that the observed patterns correspond to established mathematical descriptions of the scientific method.

Whether this connection is genuine or a coincidence of superficial similarity requires further testing. The bench test data, once analysed with domain-specific curve fitting, will show whether different domains consistently produce different falsification dynamics.

---

## Falsifiable Predictions

1. Different STEM domains will produce statistically distinguishable decay curve shapes on the bench test. Mathematics tasks will show steeper D than engineering tasks. Code tasks will show intermediate D. Cross-domain tasks will show the most gradual D.
2. A domain expert config that includes expected falsification dynamics will produce better analytical results than a config with natural language instructions alone.
3. Mayo's severity criterion maps to v-bar × C. If this product is high, the test was severe. Computationally verifiable from existing bench test data.
4. Kelly's convergence result predicts that CDSFL's HARD/SOFT classification should produce faster convergence than unstructured review. The D values under CDSFL should be systematically higher than under Control.

---

## Sources

- Popper's degree of corroboration and its statistical interpretations. Published in various forms from 1934. See: https://arxiv.org/pdf/2007.00238 and https://link.springer.com/chapter/10.1007/978-3-030-67036-8_7
- Deborah Mayo. Statistical Inference as Severe Testing. Cambridge University Press, 2018. See: https://www.cambridge.org/core/books/statistical-inference-as-severe-testing/D9DF409EF568090F3F60407FF2B973B2
- Kevin Kelly. Formal Learning Theory. Carnegie Mellon University. See: https://www.andrew.cmu.edu/user/kk3n/homepage/kelly.html and https://plato.stanford.edu/archives/spr2017/entries/learning-formal/
- Stanford Encyclopedia of Philosophy entry on Popper: https://plato.stanford.edu/entries/popper/
- Wikipedia overview of falsifiability: https://en.wikipedia.org/wiki/Falsifiability
