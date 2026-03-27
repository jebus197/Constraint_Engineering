# CDSFL Meta-Test: Agreed Game Plan

**Date:** 27 March 2026, 13:02 UTC
**Status:** Game plan agreed (CC1 × CX/ChatGPT). Blind passes not yet started.
**HEAD:** c2066de (guards formalised)

## Prior-Art Classification (CX/ChatGPT research, CC1 P-passed)

### Standard Formalisations (a) — Low Risk
| # | Component | Nearest Prior Art |
|---|-----------|-------------------|
| 1 | C(n) = 1-(1-p)^n | Bernoulli independent trials |
| 2 | F_n multi-class detection | Standard multi-class detection models |
| 3 | R_n Bayesian residual risk | Bayesian reliability / zero-failure posterior |
| 5 | L_n severity-weighted loss | Decision theory / risk analysis |
| 7 | p_H HIL detection probability | Human reliability analysis (HRA) |
| 9 | kappa calibration metric | Expected Calibration Error (ECE, Naeini 2015) |
| 10 | Duane NHPP | Duane 1964 / Crow-AMSAA |
| 16 | Sev(f) per-finding severity | Safety/risk severity scoring |

### Novel Combinations (b) — Medium Risk
| # | Component | Known Ingredients |
|---|-----------|-------------------|
| 4 | d_ik class-specific diversity | Diversity modelling × per-class parameterisation |
| 6 | G_n combined machine-HIL detection | Human reliability × automated detection × priming correlation |
| 8 | E*(t) Bayesian posterior expertise | Beta-Binomial updating × self-declared expertise |
| 13 | V_hat Online Estimator | Standard online estimation + ascending abstraction guard (novel) |
| 14 | O_A sycophancy detection | Emerging AI eval literature × SymPy verification proxy |
| 17 | S_v multi-verifier Bayesian severity | Naive Bayes log-odds × multi-rater aggregation |
| 19 | D(n) multi-architecture coverage | Coverage models × cross-architecture diversity |
| 20 | Metacognitive feedback protocol | MIDCA (Cox 2005) × reliability metrics fed back |
| 21 | Emergence condition | Superadditive performance × formal threshold |
| 24 | stop_valid(t) predicate | Standard stopping rules × abstraction guard |
| 25 | O_A domain guard | Domain restriction × cardinality threshold |
| 15 | Delta Adoption Delta | Normalised symmetric difference (Jaccard-adjacent) × belief-set dynamics |

### Genuinely Novel (c) — Highest Risk
| # | Component | Why Novel |
|---|-----------|-----------|
| 11 | H(x) Abstraction Index | No standard formal analogue for finding-depth measurement |
| 12 | Y(t) Total Cognitive Yield | No standard systems-level metric combining count × depth |
| 18 | Capability Fingerprint (D, v̄, A, C) | Four-dimensional analytical profile is bespoke |
| 22 | Second-order cognitive system (4 criteria) | Novel formal definition, philosophically adjacent to metareasoning |
| 23 | Substrate agnosticism | Architectural principle, not a standard formal model term |

## Top 5 Blind Pass Priority Targets

1. **Y(t) Total Cognitive Yield** — Broad claim, underdefined boundaries, ascending abstraction condition needs stress-testing
2. **H(x) Abstraction Index** — Calibration parameters arbitrary (confirmed soft), but operational identifiability needs examination
3. **Capability Fingerprint** — Useful but may lack canonical grounding; inter-component independence assumptions
4. **Second-order cognitive system** — Strong conceptual claim inviting empirical and philosophical challenge
5. **Adoption Delta** — Confound risk, organisation-dependent, normalisation by symmetric difference needs justification

## Analytical Direction

**Attack the novel constructs' mathematical foundations.** The standard formalisations (Layer 1-2) are well-grounded and unlikely to contain genuine errors. The novel constructs (Layer 5-6) are where genuine weaknesses hide.

Specific focus areas:
1. **Reduction properties:** Do all richer models actually reduce to simpler predecessors under stated conditions? Test every claimed reduction computationally.
2. **Hidden assumptions in H(x):** The multiplicative structure assumes independence of formality, density, and scope. Is this justified?
3. **Y(t) ascending abstraction:** Is the dH̄/dt > 0 condition well-defined when N(t) is discrete (findings arrive in integer counts)?
4. **Emergence condition:** Y_composite > max(Y_i) is a threshold. Is it the right threshold? What about Y_composite > sum(Y_i)?
5. **Notation consistency:** The §7.8 ambiguity (fixed in d639311) suggests more notation issues may exist.

## Team Deployment for Blind Pass

| Model | Position | Focus Area |
|-------|----------|------------|
| Gemini 3.1 Pro | Mathematical specialist | H(x), Y(t), reduction properties, SymPy-verifiable claims |
| CX (GPT-5.4) | Captain + player | Top 5 priority targets, inter-component wiring |
| ChatGPT 5.4 | Generalist forward | Full model scan, notation consistency, hidden assumptions |
| DeepSeek V3.2 | Volume screener | Surface scan of all 25 components |
| CC2 (Opus 4.6) | Defender | Independent second opinion on novel constructs |

CC1 (Opus 4.6) manages: does NOT participate in blind pass. Scores, verifies, computes metrics.
