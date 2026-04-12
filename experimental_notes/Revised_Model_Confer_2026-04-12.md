# Revised Mathematical Model — Confer Results and Synthesis

**Date:** 12 April 2026  
**Models consulted:** Gemini 3.1 Pro, Codex GPT-5.4 (via OpenRouter)  
**Protocol:** CDSFL + FFAFP (Find, Follow, Analyse, Fix, P-pass)  
**Raw logs:** `bench/logs/confer_revised_model/`

## Background

Three modifications to the CDSFL mathematical model were proposed based on AIS literature assessment. Two external models reviewed the complete revised model under structured falsification protocol. The review identified three critical errors and several engineering issues, all correctable before implementation.

## The Three Proposed Modifications

### Modification 1: Embedding Similarity (Gap 3)

Replace unigram/bigram Jaccard in `_finding_similarity()` with sentence-transformer embeddings (`all-MiniLM-L6-v2`) + cosine similarity. Drop-in replacement behind stable interface. `ConvergenceDetector` already accepts pluggable `similarity_fn`.

### Modification 2: Continuous Suppression (Gap 2)

Replace hard `tau_sim` threshold (currently 0.33) with proportional mutual suppression weight. Each finding receives a weight in [w_floor, 1] reflecting its marginal information contribution.

### Modification 3: Persistent Memory (Gap 1)

Replace fixed prior pi_k with evidence-backed Beta-Binomial prior from cross-experiment immune memory. Memory counts decay exponentially with experiment age.

## Critical Errors Found

### Error 1: Bayesian Corroboration Collapse

**Proposed (wrong):**

```
q_eff = η · w(f) · d · p
```

**Problem:** If 5 independent models find the same bug, confirmations 2–5 are suppressed to w_floor=0.05. The Bayesian update barely moves. Independent corroboration is penalised because text is similar.

**Both models identified this independently.**

- Gemini: "The model artificially penalizes the epistemic weight of independent corroboration just because the text is similar."
- Codex: "This can cause triple use of the same evidence... overconfident in 'nothing new here.'"

**Fix:** Remove w(f) from q_eff entirely. Detection stays as Stage 5: `q = η · d · p`. Suppression applies only to kappa_set numerator, report ordering, and triage.

### Error 2: Order Dependence

**Proposed (wrong):**

```
N(f) = {g : sim(f,g) >= s_min, g precedes f in ordering}
```

**Problem:** Permutation invariance violated. Different arrival orders produce different weights.

**Both models flagged this.**

**Fix (Codex, preferred):** Top-k exponential suppression:

```
w(f) = max(exp(-λ_s · Σ_{g ∈ TopK(f)} sim(f,g)), w_floor)
```

Order-invariant, smooth decay, no collapse cascade. k=3 or 5.

### Error 3: kappa_set Denominator Weighting

**Proposed (wrong):**

```
kappa_set(r) = 1 - Σ(w_j · S_j^novel) / Σ(w_k · S_k^cum)
```

**Problem:** Denominator represents total discovered severity mass — should monotonically increase. Weighting it by suppression makes it shrink artificially. Can cause fraction > 1.0.

**Both models agreed.**

**Fix:**

```
kappa_set(r) = 1 - Σ(w_j · S_j^novel) / (Σ S_k^cum + ε)
```

Numerator-only weighting.

## Additional Issues

| Issue | Source | Fix |
|---|---|---|
| Cosine similarity can be [-1,1], additive class bonus can exceed 1.0 | Codex | Bounded convex combination: `s = (1-β)·cos01 + β·b_class` |
| tau_sim=0.33 not portable to embeddings | Both | Dual threshold: `tau_sim_equiv` for clustering, `tau_sim_dup` for fingerprints |
| Manager uses `_finding_similarity` directly, detector uses pluggable fn | Both | Shared similarity backend refactor |
| Memory decay unit undefined (wall-clock vs experiments) | Both | Define as experiment count |
| Single-linkage clustering chains worse with dense embeddings | Codex | Consider complete-linkage or centroid-based with max-radius guard |
| Shadow credit `novelty_yield` ignores `is_novel` parameter | Codex | Bug fix: condition confirmed increment on `is_novel` |

## Composition Risk: Premature Convergence

Both models identified the same emergent failure mode:

1. Embeddings merge more findings as similar (Mod 1)
2. Suppression reduces marginal value of related findings (Mod 2)
3. kappa_set novelty mass drops faster
4. Memory says "historically reliable" (Mod 3)
5. System stops earlier — potentially missing real defects

This risk is strongest when many genuinely distinct bugs share similar vocabulary (e.g., auth/token/session vulnerability cluster). Does not exist in any single modification alone.

## Extensions Proposed

### From Gemini

- **Re-injection modulation:** w(f) should modulate Phase 3 (ν), not Phase 1 — repeated antigen after treatment raises concern
- **Hybrid similarity:** 0.5 × Jaccard + 0.5 × embedding cosine (lexical safety net)
- **Adaptive λ:** Memory decay rate as function of code churn (git lines modified)

### From Codex

- **Blended prior:** `π = (1-ρ)·π_base + ρ·π_mem` with ρ increasing with evidence
- **Drift detection:** CUSUM/ADWIN on confirmation outcomes to accelerate decay on distribution shift
- **Hierarchical memory keys:** per-model, per-flaw-class, per-benchmark
- **Effective sample size cap:** prevent historical volume from dominating
- **Severity-aware floor:** `w_min(f) = w_floor + γ·Sev(f)` — critical repeats not treated as near-zero information
- **Separate novelty from corroboration:** maintain `novelty_weight` and `support_count` as distinct statistics

### Additional AIS/CAS Principles (Both)

- Clonal expansion / exploitation control with entropy floor
- Negative selection for recurring false-positive patterns
- Danger theory: weight by operational consequence, not just severity
- Idiotypic diversity pressure in dispatch

## Verification Status

### Verified (SymPy + Wolfram)

- All algebraic reduction properties
- Boundary conditions
- Domain constraints
- Monotonicity of marginal gain in suppression weight

### Not Verified (requires empirical testing)

- Calibration transfer from Jaccard to embedding cosine
- Appropriate suppression parameters for actual finding distributions
- Memory decay rate vs environmental change rate
- Composition behaviour under realistic workloads

## Corrected Formulation Summary

### Detection (unchanged from Stage 5)

```
q = η · d · p
R_det = R_old · (1-q) / (1-q·R_old)
```

### Suppression (for utility only, not epistemics)

```
w(f) = max(exp(-λ_s · Σ_{g ∈ TopK(f)} sim(f,g)), w_floor)
```

Applies to: kappa_set numerator, report ordering, triage priority.
Does NOT apply to: q_eff, R_k(i) update, Bayesian detection.

### Weighted kappa_set

```
kappa_set(r) = 1 - Σ_{j ∈ novel}(w_j · S_j) / (Σ_{k ∈ cum} S_k + ε)
```

### Memory Prior

```
π_k = (1-ρ) · π_base + ρ · π_k^(mem)
π_k^(mem) = (n_conf + α) / (n_conf + n_rej + α + β)
n_eff = n · exp(-λ · age_experiments)
```

With effective sample size cap and drift-triggered decay acceleration.

## Implementation Order

1. **Embedding similarity** — shared backend, bounded output, dual threshold calibration
2. **Continuous suppression** — top-k exponential, numerator-only kappa, separate corroboration
3. **Persistent memory** — blended prior, hierarchical keys, drift detection
4. **Shadow extensions** — fix novelty_yield bug, collect baseline data
5. **Calibration** — offline against historical experiment data before live deployment

## Current State

Nothing committed. Shadow code in working tree. Confer logs saved. Corrected formulation requires formal write-up before implementation.

## Raw Response Metadata

| Model | Time (s) | Response length (chars) |
|-------|----------|------------------------|
| Gemini 3.1 Pro | 62.5 | 8,647 |
| Codex GPT-5.4 | 154.6 | 39,594 |
