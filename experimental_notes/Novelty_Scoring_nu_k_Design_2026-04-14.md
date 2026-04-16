# Novelty Scoring (ν_k) Design and CDSFL Self-Assessment

**Date:** 14 April 2026  
**Prompted by:** Sabine Hossenfelder, "The AI Maths Revolution Has Begun"

---

## Context

Hossenfelder demonstrated that OpenAI's claimed solutions to ten Erdős problems were rediscoveries of existing literature. Two key insights: (1) AI is currently best understood as a discovery tool — excellent at "finding the PDF" but weak at genuine logical reasoning; (2) novelty without falsifiability is scientifically worthless.

This raised the question: can the CDSFL (Constraint-Driven Synthesis and Falsification) pipeline distinguish genuinely novel findings from rediscoveries?

## ν_k Metric Design

Per-finding novelty score, ν_k (the literature-novelty score), in the interval [0, 1]:

| Range | Interpretation |
|-------|---------------|
| 0.0–0.2 | Known result — direct restatement of published work |
| 0.2–0.4 | Known synthesis — combines documented techniques |
| 0.4–0.6 | Novel application — known technique, new context |
| 0.6–0.8 | Novel synthesis — undocumented combination |
| 0.8–1.0 | Genuinely novel — no published precedent |

Computed by O1 (Ouroboros) cell via literature search. Sources: arXiv, Semantic Scholar, Unpaywall, CORE, OpenAlex (proposed). Source list is user-configurable.

## Composition with Existing Mathematics

### η Decomposition

The existing three-phase R_k(i), the iterative residual-risk self-assessment after round i, model (Stage 5, the prior mathematical framework) includes η (the novelty coefficient). η decomposes into:

- **η_int** (the internal novelty score): within-session, from `_finding_similarity()`
- **ν_k** (= η_ext): external novelty (against-literature, from O1, the Ouroboros literature-search cell)

**Composition formula:**

```
η_combined = η_int · (1 − c_ext · (1 − ν_k))
```

Where `c_ext` (the literature-search quality coefficient), in [0, 1], is the coverage confidence of the literature search.

### Boundary Conditions (SymPy + Wolfram verified)

| Condition | Result | Interpretation |
|-----------|--------|---------------|
| ν_k = 1 (novel) | η_int | External doesn't penalise |
| ν_k = 0, c = 1 (known, full coverage) | 0 | Known results contribute nothing |
| ν_k = 0, c = 0 (known, no search) | η_int | No penalty without evidence |
| c = 0 (no search done) | η_int | Degrades gracefully |

**Monotonicity (Wolfram confirmed):**
- d(η)/d(ν_k) > 0 ✓
- d(η)/d(c) < 0 when ν_k < 1 ✓ (more coverage penalises non-novel findings)

### Abstraction-Adjusted Novelty

Prior neurodiversity work provides structural solution to the boundary problem ("is absence of matches genuine novelty or poor coverage?"):

```
confidence = c_ext + (1 − c_ext) · (H / H_max)
ν_k_final = ν_k_raw · confidence
```

At high abstraction (H → H_max), absence of literature matches is expected — theory-level findings operate above published literature. At low abstraction, absence is suspicious.

**Boundary conditions (SymPy verified):**

| Condition | Result |
|-----------|--------|
| H = H_max, any c | ν_k_raw |
| c = 1, any H | ν_k_raw |
| H = 0, c = 0 | 0 |
| H = H_max, c = 0 | ν_k_raw |

## CDSFL Self-Assessment

### Component Scores (Literature Search Evidence)

| Component | ν_k | Evidence |
|-----------|-----|---------|
| R_k recursive Bayesian self-assessment | 0.85 | No direct match. K&O (2001) exists but not recursive self-assessment for AI |
| Three-phase extension (η, σ, ν) | 0.90 | No match. Unique Bayesian extension |
| Duane NHPP for AI output depletion | 0.95 | Zero results. Novel application domain |
| Multi-cell immune pipeline | 0.75 | Weak match. AIS exists but structurally different |
| Heaps' law for input complexity routing | 0.70 | Partial. Output measurement exists, input routing novel |
| Multi-vendor Popperian falsification | 0.90 | "Emerging direction" — no established work |
| Neurodiversity accommodation | 0.95 | No match in AI code review |
| Abstraction Index H(x) | 0.85 | No direct match |

### Aggregate Score

- **Geometric mean (raw):** 0.852
- **Coverage confidence (c_ext):** 0.65
- **Abstraction ratio (H/H_max):** 0.85
- **Confidence multiplier:** 0.948
- **ν_k(CDSFL) = 0.807** → **Genuinely novel**

### Nearest Competitor: Stanford POPPER (Feb 2025)

| Dimension | POPPER | CDSFL |
|-----------|--------|-------|
| Falsification mechanism | Statistical (p → e-values) | Bayesian recursive (R_k) |
| Model diversity | Single-vendor | 5 frontier models, multi-vendor |
| Verification pipeline | Sequential experiments | 9-cell immune pipeline |
| Novelty measurement | Not addressed | Duane NHPP (γ), semantic (ρ), literature (ν_k) |
| Cognitive diversity | Not addressed | H(x), neurodiversity, Y(t) |
| Self-falsification | Not self-applied | Framework subjects itself to own methodology |

## Hossenfelder Alignment

ν_k (novelty) and R_k (validity) are orthogonal. Both required. High ν_k does not bypass immune pipeline verification. This is structurally enforced, not hoped for.

The framework passes the meta-test: it subjects itself to its own falsification methodology. If a direct precedent is found, ν_k drops. The metric does not protect itself.

## Post-Confer Corrections (14 April 2026, Gemini + Codex review)

1. **Abstraction adjustment capped** with β_abs = 0.5. Original formula allowed H → H_max to fully erase search uncertainty. Capped formula: `confidence = c_ext + β_abs * (1 - c_ext) * (H / H_max)`. At max abstraction, no search: confidence = 0.5, not 1.
2. **E-value mapping corrected** to use 1/FPR_tool (not 1/α). Guarantees E[e|H₀] ≤ 1 for all tool FPR values. Rejection criterion changed from > to ≥.
3. **Source correlation discount** γ_src = 0.7 added. c_ext_adj = γ_src · c_ext.
4. **c_s operationally defined** as c_s = r_s · q_s · a_s (recall, query quality, access completeness).
5. **Frequency-scaled confidence** double-counting guard added. Strict precedence: d_tool > min(d_partial, c_freq) > c_freq.
6. **E-value gate downgraded** to "proposed" pending per-tool e-process calibration.
7. **"Strict generalisation"** softened to "integrated novelty-calibration branch plus auxiliary mechanisms."
8. All corrections SymPy verified.

## Implementation Path (Phase 7)

1. Add Unpaywall + CORE + OpenAlex source adapters to O1
2. Define pluggable source adapter interface for user-configurable UX
3. Implement abstract-level similarity scoring
4. Add full-text similarity for OA papers
5. Compute ν_k per finding, surface in pipeline metrics
6. Add citation formatting to ProvenancePacket
7. Calibrate thresholds retroactively against Exp 37–39

## Sources

- Hossenfelder, S. "How Popper killed Particle Physics" (2017)
- Hossenfelder, S. "Just because it's falsifiable doesn't mean it's good science" (2019)
- Hossenfelder, S. "The AI Maths Revolution Has Begun" (2026)
- Stanford/Harvard POPPER framework (Feb 2025), arXiv:2502.09858
- Meyer (2017), "A Popperian Falsification of AI", arXiv:1704.08111
- Lai (2023), "Heaps' Law in GPT-Neo LLM Corpora", arXiv:2311.06377
- NIST Duane Model handbook, §8.1.9.2
