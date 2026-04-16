# CDSFL Experiment 39 — Implementation Summary, 12 April 2026

CDSFL = Constraint-Driven Synthesis and Falsification, the Popperian multi-vendor LLM falsification framework.

## Current State

Nine phases (0–8) have been completed on the `exp39-experimental` branch across **9 commits**. The test baseline stood at **762 tests**. It now stands at **784**, with **22 new tests** added. All tests are passing.

## What Was Built

### Phase 0 — Housekeeping

Housekeeping commit with a novelty yield bug fix in shadow extensions.

### Phase 1 — Kappa Set Denominator Preparation

Refactored the κ-set (kappa_set, the set-level convergence metric) calculation to separate the **weighted numerator** from the **raw denominator**. This prevents the kappa overflow bug, where suppression weights in the denominator caused κ to leave [0, 1].

### Phase 2 — Embedding Similarity Shared Backend

Replaced duplicate Jaccard implementations with a **unified similarity module** supporting sentence-transformer embeddings with Jaccard fallback. Bounded convex combination:

> `similarity = 0.8 × content_similarity + 0.2 × class_bonus`

### Phase 3 — Continuous Suppression with Permutation-Invariant Top-k Weighting

The suppression weight is defined as:

> `w(f) = max(exp(−λ_s × Σ top-k similarities), weight_floor)`

where w(f) is the continuous suppression weight for finding f. This fixes the **order-dependence bug**. Suppression weights are excluded from `q_effective` and the κ-set denominator, preventing corroboration collapse.

### Phase 4 — Persistent Immune Memory

Cross-experiment learning via per-flaw-class confirmation rates with exponential decay:

- **Beta-Binomial** smoothed memory prior
- **Blended prior:** `π = (1 − ρ) × π_base + ρ × π_memory`
- **CUSUM** drift detection
- Advisory only — never overrides verdicts
- JSON persistence with file-hash invalidation

### Phase 5 — FFAFP Calibration Protocol

FFAFP (Find, Follow, Analyse, Fix, P-pass) formalised in mathematical appendix §1.2. Documents the **5-constraint admissibility set**:

1. Minimum evidence standard
2. *G*-completeness
3. Tool-grounded detection
4. Measured fix efficacy
5. Retestable detection probability

Explicitly **not** a separate equation.

### Phase 6 — Specialist B-Cell Dispatch (Shadow Mode)

Routes claims to domain-specific verification tools based on **TOML configuration**. Runs in parallel with the generic B-Cell, logs divergences without affecting verdicts.

### Phase 7 — O1 Ouroboros Cell Shadow Prototype

New cell type with two modes:

- **Macrophage mode** — anomaly hunting
- **Microglia mode** — self-referential pipeline health checks

Detects: verdict clustering, severity concentration, timing spikes, tool monoculture, persistent anomalies, and tool–claim mismatches. Exception-based audit logging surfaces only anomalies to the HIL (human-in-the-loop). Evidence is signed into the verification chain with **L1/L2/L3 separation**. Shadow mode only for Exp 39.

### Phase 8 — Mathematical Appendix Expansion

**7 new sections** adding **317 lines** (1334 → 1651 total):

| Section | Content |
|---------|---------|
| §1.3 | Embedding similarity |
| §1.4 | Continuous suppression — permutation invariance proof, corroboration collapse prevention |
| §1.5 | Persistent memory — blended prior, drift detection |
| §7.13 | Convergence metrics — κ-set rate and adopt formal specification |
| §8.7 | Ouroboros cell specification |
| §9 | Confounds and threats to validity |

Section 9 documents **3 critical errors caught**, embedding bias, memory poisoning, single-operator validation, and statistical power limitations. **17 new notation entries** were added.

## Three Critical Errors Caught

### 1. Corroboration Collapse

Suppression weights feeding into `q_effective` caused a **113× residual risk overestimate**. Fixed by excluding `w(f)` from the Bayesian update entirely.

### 2. Order Dependence

Predecessor-product suppression produced different weights depending on processing order. Fixed by **top-k exponential suppression**, which is permutation-invariant by construction.

### 3. Kappa Overflow

Weighting both numerator and denominator of κ-set caused the metric to leave [0, 1]. Fixed by **numerator-only weighting** with a raw denominator.

## Open Items

- **Phase 9** (research write-up) is deferred until after Exp 39 concludes.
- **FFAFP Policy Engine enforcement** has not yet been built. The appendix documents the constraint set, but the hard PE wiring that rejects non-compliant findings has not been implemented.
- **O1 exception-based auditing** and HIL overload mitigations need further analysis — Gemini confer dispatched.
