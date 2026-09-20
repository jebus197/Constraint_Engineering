# Proposed validation and falsification plan

Author: independent validation-design pass, 9 September 2026. Scope: proposal only. Read the prior mathematical review and revision plan. No empirical calibration has been run; no repository code has been changed. This plan does not presume that the proposed revision has passed the mathematical checks.

## 1. State what kind of claim can fail

Maintain four distinct registers:

- **Identity/theorem:** an equation follows from stated probability laws and definitions. A valid counterexample within those assumptions defeats the claim; passing a finite test set does not prove the theorem.
- **Generative assumption:** the selected states, observation law, repair transition, and retained history describe the process well enough. Test these through outcome predictions and deliberately omitted mechanisms.
- **Estimated probability:** numerical parameters and forecasts apply to a defined population, policy, target version, and time period. Assess them prospectively against independently resolved outcomes.
- **Decision and originality claim:** a specified policy achieves useful outcomes at a specified resource cost; a result is new relative to a stated search. Utility weights express purposes, and literature novelty does not supply a likelihood.

A stochastic model that assigns nonzero probability to an adverse outcome is not logically refuted by one such outcome. Predeclared predictive tests can reject its adequacy at a stated error rate; otherwise record the degree and practical consequence of discrepancy. Avoid using “not refuted” as equivalent to “verified.”

## 2. Freeze the event before measuring it

Every forecast must name the event H, the target and version, the acceptance conditions, the population from which the target was sampled, and the evidence available at prediction time. “Some unknown flaw remains anywhere” is usually not resolvable enough for direct calibration. Start with “this numerical routine violates this property on this defined input distribution” or “this derivation contains one of these independently checkable invalid steps.”

Keep complete task families, source artifacts, and their mutations together when splitting development and held-out data. A hundred mutations of one artifact are not a hundred independent task families. A repair creates a new target version; an unchanged scientific proposition does not become true because its advocate revises a different proposition.

Essential prediction log: target hash; event definition; source family; method/policy/model versions; evidence identifiers and dependencies; history available; parameter provenance and uncertainty; forecast before observation; actual positive, negative, or unresolved observation; intervention and new target hash; external outcome label and its limitations; cost and wall time. Timeouts and missing labels are unresolved, not clean reviews.

## 3. Separate observation calibration from action calibration

**Observation cohort:** use frozen targets with independently established positive and negative labels. Run review without changing the targets. Estimate sensitivity and false-positive rates in the relevant history contexts, and score the posterior forecasts against the hidden labels. Seeded defects permit controlled sensitivity experiments, but seeded prevalence cannot establish natural-world priors or the probability of all unseeded defects.

**Action cohort:** apply repair policies to cloned snapshots, retain a no-action comparison where practical, and resolve the post-action target independently. Include initially clean targets to measure damage from interventions. Estimate transition probabilities conditional on the actual selection rule and evidence. A repair selected after a positive review need not have the same success distribution as an unconditional repair attempt.

**Verification cohort:** use fresh checks on the changed target, with evidence reuse explicitly tracked. The test a repair was optimised to pass cannot by itself be the independent outcome oracle.

Self-reported findings alone generally cannot identify the prior defect rate, sensitivity, and false-positive rate separately. Independently labelled targets or additional defensible identifying assumptions are required.

## 4. Small-founder progression across STEM

1. **Zero-API structural suite:** exact finite-state enumeration and boundary cases. Require agreement between the proposed equation and a separately implemented outcome tree. Include positive evidence, false positives, failed repairs, harmful changes, impossible observations, perfect duplicate evidence, adaptive selection, and evidence that refutes the favoured hypothesis. Mutated incorrect equations must fail the suite. This tests implementation and algebra under supplied worlds, not empirical validity.
2. **Cheap diagnostic pilot:** roughly 12 distinct oracle-resolvable tasks, covering valid and invalid inputs and the difficult cases above. Its purpose is to uncover logging, oracle, and parameter-identifiability problems and measure runtime/cost. It is not a certification sample. Pilot results may change the protocol; they then remain development data.
3. **First locked family:** mathematical or numerical artifacts with symbolic, exhaustive, or independently computed outcomes. Fit a deliberately low-dimensional model on development targets; freeze it before evaluating new targets. Choose sample size from a prespecified practical calibration tolerance, comparison effect, and available budget using pilot variability. If adequate precision is unaffordable, publish wider uncertainty and a narrower claim.
4. **Mechanistic-inference transfer:** synthetic data from known physical or statistical mechanisms, including a true alternative absent from the candidate list, correlated observations, measurement noise, and newly collected independent data. Resolve simulated truth from the independent generator; call this closed-world or controlled-misspecification evidence, not confirmation about all real scientific enquiry.
5. **Real STEM transfer:** an independently reproducible scientific-computing or experimental-replication task with held-out observations and a domain-appropriate reference procedure. Later repeat in another domain and with human participants if claiming substrate generality. Existing published agreement is evidence, not automatically a truth oracle. When truth remains unsettled, score observable predictions and leave the truth claim unresolved.

The first two stages can run without building the distributed platform. A limited successful family demonstrates bounded usefulness; generality requires further transfer tests.

## 5. Measure predictive value and decision value separately

Freeze three inexpensive comparators: a base-rate-only forecast, a simple calibrated observation/action model without elaborate dependence features, and the proposed richer model. Use the old score only as a labelled heuristic comparator unless a probability interpretation has been justified. Compare all models on the same unseen evidence when evaluating forecasts; compare complete policies under matched resource budgets when evaluating allocation decisions.

Use Brier loss as an initial primary metric, with log loss and reliability summaries as diagnostics. Report counts and uncertainty for predeclared risk ranges and important subgroups, including hard targets and repeated-review histories. Aggregate calibration alone can hide serious subgroup errors, and a constant base rate can be calibrated yet uninformative. Compare forecast skill as well as calibration. Do not turn a rank score into a probability by merely restricting it to [0,1].

For policy value, measure independently resolved task outcomes, missed unacceptable outcomes, unnecessary or harmful actions, total cost, and elapsed time. A lower fitted residual score is not the success endpoint. Novelty and useful replication are reported separately.

Predeclare the meaningful improvement and tolerated regressions. With independent task-family units, form appropriate paired uncertainty estimates for differences; do not treat every review pass as an independent replicate. Prefer the simple model if extra complexity has no demonstrated practical benefit. An interval too wide to decide means inconclusive, not equivalence.

For perspective, under independent identically distributed Bernoulli trials, zero observed failures in n trials gives a one-sided 95% upper bound of 1 - 0.05^(1/n): about 9.5% at n=30 and 3.0% at n=100. Those figures do not transfer to correlated passes or unknown deployment distributions.

## 6. Adaptation, alternatives, and unmodelled possibilities

History-dependent likelihoods must condition on the evidence and review-selection process available at the time. Test fixed versus adaptive policies prospectively; log available actions, the chosen action, and selection probabilities if later off-policy claims are intended. A deterministic policy supplies no direct evidence about never-selected alternatives. Start with prospective policy comparisons instead of elaborate causal corrections.

A second review reading the first review's answer is not independent just because it uses a different model. Audit common evidence and shared failure mechanisms. Test deliberately repeated evidence: an exact duplicate should add no information once its source is already conditioned on. Independently collected replication can add evidence despite zero literature novelty.

Compare competing hypotheses through their predictions, and preserve a model-misfit channel. A label “other hypotheses” is not a calibrated probability distribution unless its observation law is specified. Unknown unknowns should appear as scope limitations, sensitivity analyses, and challenges from excluded mechanisms. Do not manufacture a numerical risk floor and claim it measures all possibilities.

Changing domain, model version, tools, review policy, or target family triggers an applicability review; previously fitted numbers do not automatically carry over. Recalibration may be warranted, but transfer failure must remain visible in the record.

## 7. Stopping and self-audit

For task work, stop with one of several explicit statuses: resolved within stated acceptance conditions; counterexample found; economical stopping with residual uncertainty; budget exhausted; or blocked/unresolved. A single low-yield pass proves neither completeness nor optimal stopping. Evaluate the available next actions and their uncertainty. If all plausible benefits fall below their costs, stopping can be economically justified under that model, without certifying truth.

For empirical validation, use a fixed sample and analysis plan first. If results are repeatedly inspected to choose when to stop, use a genuinely time-uniform method under its stated assumptions, or reserve a fresh final evaluation. Do not repeatedly reuse the same holdout until the claim passes.

Self-audit claim table:

- **The collapsed equation follows from the explicit state model:** assess by derivation and separately enumerated outcome trees. Status may become mathematically established within assumptions.
- **It includes the valid old identities:** assess by algebraic reductions and regression examples.
- **Its parameters are calibrated:** requires prospective external outcomes; remains unestablished in this revision exercise.
- **It improves STEM research decisions:** requires the policy comparisons above; remains unestablished.
- **It makes a novel contribution:** requires a scoped literature comparison and precise contribution statement; reviewer enthusiasm does not establish priority.

Apply the model to the review by recording claims, assumptions, evidence provenance, dependence, contradictions, and revisions. Do not report a numerical probability that the revised model is sound when reviewer sensitivities and priors are uncalibrated. Agreement among related AI review passes is not an independent ground-truth label. The scientifically defensible present result is a transparent claim-by-claim audit, with empirical questions left open.

## Primary methodological references

- Proper scoring rules and calibration/forecast skill: Gneiting and Raftery (2007), https://sites.stat.washington.edu/people/raftery/Research/PDF/Gneiting2007jasa.pdf .
- Iterative model criticism, prediction, and validation: Gelman et al., Bayesian Workflow, https://arxiv.org/abs/2011.01808 .
- Time-uniform confidence sequences for optional stopping under explicit conditions: Howard et al., https://arxiv.org/abs/1810.08240 .
- Exact binomial confidence bounds: NIST, https://itl.nist.gov/div898/software/dataplot/refman2/auxillar/exacbino.htm .

These support the statistical methods. The proposed CDSFL-specific experiment structure and acceptance decisions above are design recommendations, not results reported by those sources.
