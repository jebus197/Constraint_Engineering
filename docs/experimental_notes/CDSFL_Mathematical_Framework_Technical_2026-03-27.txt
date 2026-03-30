# CDSFL Mathematical Framework — Technical Version

**27 March 2026**

---

## Framework Overview

The CDSFL measurement framework consists of seven mathematical components developed across 13 days by three model architectures (Claude Opus 4.6, Codex 5.3, Gemini 3.1 Pro) under the founder's direction. Each component measures a distinct dimension of multi-model distributed falsification.

---

## Component 1 — The G-n Formula (CC contribution, week 1)

G-n models the marginal information gain from the n-th review round in a multi-reviewer protocol.

```
G-n = f(n, rho, E-star, sigma)
```

where:
- `rho` is the correlation between reviewers (higher rho means less independent)
- `E-star` is the empirically observed expertise (Bayesian posterior from calibration)
- `sigma` is the domain-specific difficulty parameter

G-n predicts geometric decay of novel findings per round. The formula was already present in the CDSFL white paper before the bench tests confirmed the prediction empirically.

---

## Component 2 — The Duane NHPP Model (Gemini contribution, week 2)

The Duane model treats the finding process as a Non-Homogeneous Poisson Process with power-law intensity.

```
lambda(t) = (beta / eta) * (t / eta)^(beta - 1)
```

where:
- `lambda(t)` is the instantaneous finding rate at time t (measured in rounds)
- `beta` is the shape parameter
- `eta` is the scale parameter

The gamma parameter (`gamma = 1 - beta`) measures convergence:
- `gamma > 0` — finding rate is decreasing (genuine convergence)
- `gamma = 0` — finding rate is constant (churn)
- `gamma < 0` — finding rate is increasing (divergence or escalation)

**Empirical validation:** the Duane model fitted 17 of 18 CDSFL runs better than simple geometric decay (by AICc comparison). The gamma values for CDSFL conditions averaged 0.5 to 0.6, indicating moderate convergence. Control conditions showed gamma near 0.01, indicating near-flat output (churn-adjacent).

---

## Component 3 — The (D, v-bar, A, C) Capability Fingerprint (CC contribution, week 2)

- **D** — the decay rate, computed from the half-life of the best-fitting decay model. D equals 0 for flat curves. Higher D means faster convergence.
- **v-bar** — the mean verification score. The fraction of findings confirmed correct by SymPy.
- **A** — the total count of novel verified findings.
- **C** — coverage. A divided by the estimated total real findings across all reviewers and conditions.

Together these form a four-dimensional capability profile per model per condition per task. The fingerprint was proposed by the founder based on observation of a single CX decay curve (5, 3, 2, 2, 0) and subsequently formalised.

---

## Component 4 — Objective Alignment (Gemini contribution, week 2)

O-A replaces Seeded Sensitivity (S-H) for frontier tasks where no seeded defects are available.

```
F-conv = (C-A ∩ C-B) - (B-A ∩ B-B)
```

This is the set of newly converged findings — those that appeared in both models' confer output but were not in both models' blind output.

```
O-A = |SymPy-verified findings in F-conv| / |F-conv|
```

If F-conv is empty, O-A equals 1 by convention (no convergence means no sycophancy).

The sycophancy score becomes:

```
S-sync = (1 - mean_delta) * (1 - O-A)
```

This distinguishes genuine consensus (convergence on verified facts, S-sync near 0) from sycophantic convergence (convergence on unverified claims, S-sync high).

---

## Component 5 — Adoption Delta (Gemini contribution, week 2)

Measures how much Model A's finding set changes toward Model B's perspective after seeing B's work.

```
A-adopt = C-A ∩ (B-B - B-A)     # Findings from B that A adopted
A-drop  = (B-A - B-B) - C-A     # Findings A dropped after seeing B's work

Delta(A→B) = (|A-adopt| + |A-drop|) / |symmetric_difference(B-A, B-B)|
```

- `Delta = 0` — absolute independence
- `Delta = 1` — complete capitulation

The formula is bounded between 0 and 1.

**Edge case:** when blind findings are identical, the symmetric difference is empty and delta equals 0 (nothing to adopt or drop).

---

## Component 6 — Per-Finding Severity (Gemini contribution, week 2)

```
Sev(f) = W(class) * confidence * V(verification)
```

where:
- **W** is the constraint weight: HARD = 1.0, SOFT = 0.5
- **V** is the verification multiplier: True = 1.0, None (unverifiable) = 0.5, False (debunked) = 0.0

A debunked finding has severity 0 regardless of confidence. An unverified finding is discounted by 50 percent. A verified HARD finding with high confidence approaches maximum severity of 1.0.

---

## Component 7 — Normalised Mutual Information (Gemini contribution, week 2)

The diversity discount delta for player P relative to captain C is defined as:

```
delta-cp = 1 - I(X-C ; X-P) / min(H(X-C), H(X-P))
```

where:
- `I` is the mutual information between the two finding streams
- `H` is the Shannon entropy of each stream

- `delta` near 1 — high adversarial friction (models finding different things)
- `delta` near 0 — the player is echoing the captain

This was proposed but not yet fully implemented. CX identified that the blind-to-confer adoption delta (Component 5) is a better practical sycophancy measure than static NMI.

---

## Framework Status

| Component | Status |
|-----------|--------|
| 1 (G-n formula) | Implemented in bench analysis pipeline |
| 2 (Duane NHPP) | Implemented in bench analysis pipeline |
| 3 (Capability fingerprint) | Implemented in bench analysis pipeline |
| 4 (Objective alignment) | Verified computationally, ready for implementation |
| 5 (Adoption delta) | Verified computationally, ready for implementation |
| 6 (Per-finding severity) | Implemented in bench analysis pipeline |
| 7 (NMI diversity) | Theoretical, partially superseded by Component 5 |

The framework requires empirical calibration from the completed bench run to set domain-specific thresholds. The mathematical structure is validated. The parameter values are preliminary.
