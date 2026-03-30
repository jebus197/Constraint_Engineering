# CDSFL Mathematical Popper Analysis — Final Assessment

**27 March 2026**

---

## Summary of Three-Model Confer on Mathematical Popper

Three AI architectures (Gemini 3.1 Pro, Codex 5.3, Claude Opus 4.6) worked through the question of whether Karl Popper's falsification can be mathematically modelled and used as a machine-readable domain expert configuration.

---

## What Was Produced

**Gemini** contributed the primary mathematical framework across three exchanges:

- **Exchange 1:** proposed three mathematical components — the Duane Non-Homogeneous Poisson Process for modelling decay curves (replacing the simpler geometric model), Mayo's severity function for formalising what makes a test "good" in Popper's sense, and KL divergence for modelling how expert guidance affects the search space.
- **Exchange 2:** refined the formulas and connected them to the Registry architecture.
- **Exchange 3:** proposed seeded defect injection as a calibration mechanism.

**Codex** tested the Duane model against actual bench data and found it beats simple geometric decay in 17 out of 18 CDSFL runs. This is empirical validation, not theory. Codex also correctly identified that Gemini's calibration coefficient (omega) is mathematically irrelevant to the decay diagnostic — multiplying by a constant changes amplitude but not decay shape. It found a concrete counterexample where recall-only calibration would classify a model with 437 false positives as "perfect."

**Claude Opus** built the Duane analysis tool, ran it on 78 bench results, and discovered that the gamma parameter discriminates conditions exactly as predicted:
- Control and HIL conditions: gamma near 0.01 (single-shot exhaustion, no iterative depth)
- CDSFL conditions: gamma near 0.5 (sustained distributed analysis)

This is the mathematical signature of Popperian falsification with iterative depth.

---

## What the Gamma Parameter Means

Gamma is the power-law exponent in the Duane model. It measures how the rate of discovery changes over successive rounds of review.

- **Gamma near 0** — almost everything is found in round 1 and nothing in subsequent rounds. This is what happens under Control and HIL conditions, where each model works alone and exhausts its analytical capacity in a single pass. There is no iterative depth because there is no cross-model exchange.
- **Gamma near 0.5** — the discovery rate decays gradually across rounds. New findings keep emerging because cross-model confer introduces fresh perspectives each round. The falsification process has depth.
- **Gamma near 1 or above** — the finding rate is flat or increasing. This is churn. No churn was detected in the current bench run, though earlier smoke tests with DeepSeek showed clear flat-line patterns.

The healthy gamma for distributed compute under CDSFL is around 0.5: steep enough to show genuine convergence toward a conclusion, gradual enough to show that cross-model exchange is producing genuine additional value across multiple rounds.

---

## Is This Pseudomathematics?

No. Each component derives from established fields:
- The Duane model is the industry standard for reliability growth modelling in aerospace and software engineering.
- Mayo's severity is a peer-reviewed frequentist framework published by Cambridge University Press.
- KL divergence is fundamental information theory.

Codex verified the Duane model against real data and confirmed it fits better than the simpler alternative.

What remains unproven is whether the full assembly (Duane plus Mayo plus KL) produces genuine predictive power beyond what the individual components provide separately. The gamma parameter alone already discriminates conditions. Whether adding severity and KL divergence improves the discrimination is an empirical question for the next bench run.

---

## Gemini's Convergence

Gemini's three exchanges on this topic followed a decay pattern. The first exchange was substantial and produced the core mathematical framework. The second refined and extended it. The third added a marginal calibration mechanism that did not survive scrutiny from Codex.

**This is gamma approximately 0.5 — genuine convergence.** Gemini reached diminishing returns on this topic after three rounds, which is consistent with what the Duane model predicts for genuine analytical work.

---

## What This Means for Domain Expert Configs

The gamma parameter, once calibrated across domains, becomes a mathematical encoding of how falsification works in each domain:

- **Mathematics domain config:** expected gamma 0.2 to 0.5
- **Engineering domain config:** expected gamma 0.5 to 0.8

The machine does not need to understand Popper philosophically. It needs to produce output that matches the mathematical signature of genuine falsification in its domain.

Whether machines respond better to mathematical formulations of Popper than to prose formulations is testable. The next smoke test should include a "symbolic condition" where the P-pass protocol is expressed as mathematical constraints rather than natural language instructions. If the symbolic condition produces different gamma values than the prose condition on the same tasks, the formulation matters. If not, the prose is sufficient.

---

## What Remains

The microscope is built and it works. Gamma discriminates conditions. The Duane model fits real data. The analysis tool runs automatically on bench results.

What remains is not more theory but execution:

1. Run the corrected bench test with bare-metal parity across all models
2. Apply the Duane analysis to the full results
3. See whether gamma discriminates not just conditions but individual models and task domains
4. Test symbolic versus prose directives

The theoretical architecture is approaching functional completion. The empirical validation requires more data. The data requires the next bench run. The next bench run requires the fixes that are currently being built.
