# The Complete CDSFL Mathematical Model Explained in Plain English

**Date:** 27 March 2026

This document explains every mathematical component in the CDSFL framework, from the simplest building block to the most complex. Each formula is stated, then explained in plain English.

---

## Layer One: The Core Models

These are the foundation. Everything else builds on them.

### 1. Simple Corroboration

```
C(n) = 1 - (1 - p)^n
```

Each test of a claim has some probability `p` of catching a flaw if one exists. After `n` tests, the probability the flaw survived all of them is `(1 - p)^n`. Corroboration is the complement — it tells you how much trust the claim has earned.

Four properties follow directly:
- Zero tests give zero trust.
- Trust approaches but never reaches 100%.
- Each additional test adds less than the one before.
- A model that cannot reason adversarially (`p = 0`) gains nothing from any number of passes. A thousand empty tests produce zero corroboration.

### 2. Structured Operational Model

```
F_n = weighted sum across flaw classes k of
      [1 - product across passes i of (1 - d_i * p_ik)]
```

This extends the simple model to handle reality. Different types of flaws (logic errors, arithmetic mistakes, physical impossibilities) have different detection probabilities. Different passes have different levels of independence. The **diversity discount** `d_i` captures how correlated each pass is with previous ones:
- Same model rechecking itself: ~0.2 (highly correlated, same blind spots)
- Completely different architecture: ~0.9 (genuinely independent)

The weights `w_k` reflect how much each flaw type matters. Under uniform assumptions (one flaw type, one detection probability, full independence), `F_n` reduces to `C(n)`. The simple model is a special case of the structured model.

### 3. Anchor States

A classification of how much independence backs a claim:
- **A0**: self-assessed only
- **A1**: another AI has verified it
- **A2**: a human expert has reviewed it
- **A3**: independent replication

Not a formula — a ladder of epistemic confidence.

---

## Layer Two: The Extensions

These extend the core models to handle specific real-world needs.

### 4. Residual Risk

```
R_n = weighted sum across flaw classes k of
      (prior_flaw_rate * miss_probability)
      / (1 - prior_flaw_rate + prior_flaw_rate * miss_probability)
```

After a clean run where nothing was found, what is the probability a flaw still exists? This uses Bayes' theorem. High prior plus high miss probability means substantial residual risk even after clean passes. Testing mature, well-tested code leaves much less residual risk than testing suspect code, even at the same coverage level.

### 5. Class-Specific Diversity Discounts

`d_ik` replaces scalar `d_i` with per-flaw-class values. A reviewer might be highly independent for logic flaws but correlated for arithmetic flaws because they use similar calculation methods.

### 6. Severity-Weighted Expected Loss

```
L_n = sum across flaw classes k of
      expected_harm * posterior_probability(flaw remains)
```

Same Bayesian posterior as residual risk but weighted by damage rather than consequence weight. Converts residual risk into expected real-world harm.

---

## Layer Three: The Combined Detection Model

This brings the human inside the formula.

### 7. Combined Machine-HIL Model

```
G_n = weighted sum across flaw classes k of
      [1 - (1 - C_M_k) * (1 - C_H_k * (1 - rho_MH))]
```

Two independent detection streams: machine passes (`C_M`) and human expert passes (`C_H`). The **priming correlation** `rho_MH` captures how much the human's analysis was influenced by seeing the machine's output first:
- If the human worked independently before seeing machine output, `rho ≈ 0` and their contribution is maximised.
- If they read the machine's work first, `rho` increases and their effective contribution shrinks.
- At `rho = 1`, the human adds nothing — they are just agreeing with the machine.

When no human passes exist, `G_n` reduces to `F_n`. When priming is zero (full independence), the two streams combine multiplicatively. Every simpler model is a special case of `G_n`.

### 8. Human Detection Probability

```
p_H = E * (alpha + (1 - alpha) * M) * product of domain_variables V_s
```

- `E` = domain expertise (0 to 1)
- `M` = methodology formality (0 = informal gut feeling, 1 = fully formal method)
- `alpha` = floor coefficient (what expertise alone achieves without a formal method)
- `V_s` = pluggable domain-specific variables (time pressure, equipment access, regulatory familiarity, etc.)

The key insight: methodology is a **multiplier** on expertise, not independent. A formal method without expertise produces nothing. The same expert working with a formal method catches roughly **2.5× what they catch working informally**. Rigour is a procedure, not a personality trait.

### 9. Bayesian Posterior Expertise

```
E*(t) = (prior_successes + observed_catches)
        / (prior_successes + prior_failures + total_trials)
```

Self-correcting. The human claims a certain expertise level. After enough reviews where the system can observe their actual detection rate, the claimed value is replaced by the observed value. By approximately five reviews, overclaiming is statistically falsifiable. An expert who consistently overclaims is detected not by administrative judgment but by their own track record.

### 10. Calibration Metric

```
Kappa = 1 - |claimed_expertise - observed_expertise|
```

The asymmetric variant penalises overconfidence more heavily than underconfidence. A bluffer scores negative. An honest novice scores almost as well as a well-calibrated expert. The metric rewards self-knowledge, not raw ability.

---

## Layer Four: Distributed Compute Coverage

This models what happens when multiple different AI architectures review the same work.

### 11. Multi-Architecture Coverage

```
D(n) = weighted sum across flaw classes k of
       [1 - product across architectures i of (1 - p_ik)]
```

The simplified single-class form introduces inter-architecture correlation `rho`. Each additional architecture's effective contribution decays by the correlation factor. Key properties:

- **Diminishing returns**: early architectures add the most coverage; later ones contribute progressively less.
- **Heterogeneity premium**: low correlation (genuinely different architectures) reaches a higher ceiling than high correlation.
- **Monoculture collapse**: when `rho = 1`, adding architectures does nothing. A room full of the same model, however capable, leaves its blind spots permanently unexamined.
- **Orchestration matters**: good orchestration preserves genuine independence, keeping effective correlation low. Poor orchestration allows convergence toward consensus, raising effective correlation and reducing coverage.

### 12. Marginal Gain and Optimal Stopping

The marginal gain from adding the next architecture is the probability it catches defects that **all** prior architectures missed. The optimal number of architectures is the smallest `n` where the marginal gain drops below a cost-benefit threshold:
- Safety-critical work demands a lower threshold (more architectures).
- Routine work tolerates a higher one.

---

## Layer Five: The Cognitive Measurement Framework

This is the instrumentation layer. It measures the quality of analysis, not just the coverage.

### 13. Duane NHPP Model

```
lambda(t) = (beta/eta) * (t/eta)^(beta-1)
```

The finding rate across review rounds follows a Non-Homogeneous Poisson Process originally developed for hardware reliability growth (Duane, 1964). The convergence parameter `gamma = 1 - beta`:
- `gamma > 0`: genuine convergence (exhausting the error space)
- `gamma ≈ 0`: churn (generating content on demand)
- `gamma < 0`: divergence (problem is expanding)

This is the built-in diagnostic for distinguishing real analysis from chatbot behaviour. Empirically, the Duane model fits 17 out of 18 bench test runs better than geometric decay.

### 14. Abstraction Index

```
H(x) = confidence * formality * information_density * generalisation_scope
```

Not all findings are equal. H(x) scores each finding on three dimensions:
- **Formality**: does the finding contain verifiable claims and HARD constraint violations?
- **Information density**: evidence-to-claim word ratio — short dense findings score higher than verbose restatements.
- **Generalisation scope**: does the finding affect multiple components or just one?

Verified discrimination ratio: **33.4×**. A deep structural finding with formal claims, dense evidence, and cross-cutting scope scores 33.4 times higher than a shallow verbose local observation.

### 15. Total Cognitive Yield

```
Y(t) = N(t) * H_bar(t)
```

The crucial insight is the **ascending abstraction condition**: when finding count decreases but depth increases, total yield can still rise. An analyst finding fewer things but each one deeper is not exhausted — they are deepening. The decay curve alone would classify this as non-convergent. Y(t) correctly recognises it as a distinct and valuable cognitive mode.

### 16. Online Total Value Estimator

A running prediction of total analytical value while analysis is still ongoing. Used for continue-or-stop decisions during the analysis. The remaining estimate uses the current finding rate and empirical decay rate to project how much value remains.

**Convergence guarantee:** as the analysis approaches completion, the estimate converges to the true total. This enables early stopping for efficient analysts who capture most value quickly, while allowing systematic processors to continue when their best findings come late.

### 17. Objective Alignment

```
O_A = verified_findings_in_converged_set / total_converged_set
```

Sycophancy detector. When two models confer and agree on something they did not both find independently, is that agreement genuine or are they just converging for the sake of converging? O_A checks by looking at whether the converged findings are computationally verified. If they are, convergence is genuine. If not, it may be sycophantic.

**Limitation:** O_A can only be computed for findings that SymPy can verify. For non-mathematical claims, the metric has low statistical power. This is documented, not hidden.

### 18. Adoption Delta

```
Delta = (findings_adopted + findings_dropped) / symmetric_difference_of_blind_sets
```

Measures how much a model changed its mind after seeing another model's work:
- **Delta = 0**: complete independence
- **Delta = 1**: complete capitulation

Healthy engagement falls in between — a model that genuinely considers new evidence and selectively incorporates what survives scrutiny.

### 19. Per-Finding Severity

```
Severity = constraint_weight * confidence * verification_status
```

Multiplicative. HARD constraint violations get weight 1.0, SOFT gets 0.5. Verified findings get 1.0, unassessed 0.5, disproved 0.0.

The key property: **disproved findings ALWAYS receive zero severity**, regardless of confidence. This prevents hallucinated findings from inflating scores.

### 20. Multi-Verifier Bayesian Severity

```
S_v = 1 / (1 + e^(-L_total))
```

Where `L_total` is the weighted sum of log-likelihood ratios from each verifier (SymPy, dimensional analysis, numerical spot-checking). Each contributes evidence weighted by its empirical true positive rate and false positive rate.

**SymPy has a veto.** Its negative weight magnitude (4.60) exceeds the sum of all other positive weights (3.62). If SymPy says a finding is wrong, that verdict overwhelms all other verifiers saying it is right. Mathematically grounded veto power.

### 21. Capability Fingerprint

Four numbers per model per task:
- `D` = decay rate (how fast it exhausts the problem)
- `v_bar` = mean verification score (fraction confirmed correct)
- `A` = total novel verified findings (raw quantity of real issues)
- `C` = coverage (`A` divided by estimated total real findings)

No single number tells the whole story.

---

## Layer Six: Emergence and Metacognition

This is where the framework measures properties of the composite system that no individual component possesses.

### 22. Metacognitive Feedback Protocol

After each round, each model receives its own performance measurements and a structured protocol prescribing adjustments:
- Flat decay → shift from surface scanning to structural analysis
- Low verification rate → increase use of formally verifiable claims
- High adoption delta → reassert independent analysis before engaging with others' input

This maps to the **MIDCA architecture** from cognitive science: first cycle = analysis, second cycle = monitoring analysis.

### 23. Composite System Emergence

```
Y_composite = composite_finding_count * composite_mean_abstraction_depth
```

The emergence condition: `Y_composite > max(Y_i)` for all individual agents `i`.

This exceeds aggregation. The confer protocol forces agents into analytical territory none explored alone. A finding from one agent provokes investigation by another, which surfaces a structural issue that a third formalises. The resulting insight exists because of the interaction.

The Adoption Delta and Objective Alignment jointly distinguish emergence from groupthink:
- Low adoption delta + high objective alignment = genuine independence
- High adoption delta + low objective alignment = sycophantic convergence

### 24. Second-Order Cognitive System

A system is second-order cognitive if and only if it:
1. Analyses problems
2. Monitors its own analytical performance
3. Adjusts its behaviour based on that monitoring
4. The adjustment produces measurable improvement

The CDSFL composite system satisfies all four criteria. This is **functional metacognition**, not a claim about consciousness or sentience.

### 25. Substrate Agnosticism

None of the formulas in the cognitive measurement framework or the emergence formalisations reference the terms "model," "machine," or "AI." Every quantity is computable from structured analytical findings across multiple rounds, regardless of source.

**Testable prediction:** a team of human researchers working under the CDSFL protocol will exhibit measurable decay curves, ascending abstraction, and emergent findings beyond individual capability. If this holds, the framework is validated across substrates. If it does not, the framework describes machine cognition only, and the substrate-agnostic claim fails.

---

## How the Layers Connect

Every layer reduces to the one below it under simplifying assumptions:
- `G_n` reduces to `F_n` when there are no human passes.
- `F_n` reduces to `C(n)` when there is one flaw class, one detection probability, and full independence.
- `D(n)` reduces to `C(n)` under the same assumptions.
- Layer Five measures the **quality** of the analysis that layers one through four quantify the **coverage** of.
- Layer Six measures what happens when you put multiple instrumented agents together under structured falsification.

The entire framework is falsifiable. Each component makes testable predictions. If any component fails to predict better than a simpler alternative, it should be discarded. The methodology does not depend on any specific equation — it depends on the principle that **corroboration is earned through survived falsification**.
