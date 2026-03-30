# Experiment 17 — Mathematical Appendix to Code Traceability Table

**Purpose:** Cross-reference for Experiment 17 models. Maps each relevant formula in
`docs/MATHEMATICAL_APPENDIX.md` to its implementation in `bench/dynamic_management.py`.

---

## Fully Implemented

| Appendix Section | Formula | Code Location | Notes |
|---|---|---|---|
| §7.3 | Y(t) = N(t) · H̄(t) (total cognitive yield) | `DiminishingReturnsDetector._cumulative_yields` (~2033) | Cumulative yield tracked |
| §7.4 | V̂ remaining value estimate | `DiminishingReturnsDetector.remaining_value_estimate()` (~2319) | Exponential decay model |
| §7.9 | (D_decay, v̄, A, C) capability fingerprint | `CapabilityFingerprint` class (~271) | Full dataclass + normalisation |
| Convergence | κ(r) = min(κ_set, max(0, κ_rate), κ_adopt) | `ConvergenceDetector.kappa()` (~1750) | Three-component min |
| Convergence | κ_set(r) = 1 - Σ(novel Sev) / Σ(cum Sev) | `ConvergenceDetector.kappa_set()` (~1700) | Set-theoretic stability |
| Convergence | κ_rate(r) = 1 - λ̂(r) / λ̂(1) | `ConvergenceDetector.kappa_rate()` (~1715) | Rate-based stability |
| Convergence | κ_adopt(r) = clamp(1 - Δ_r, 0, 1) | `ConvergenceDetector.kappa_adopt()` (~1737) | Adoption stabilisation |
| Convergence | converged(r) iff κ ≥ τ_κ ∧ r ≥ min_rounds ∧ ¬veto | `ConvergenceDetector.converged()` (~1772) | Full predicate |
| Convergence | veto(r) iff ∃f: Sev_agg ≥ η_veto | `ConvergenceDetector._veto()` (~1763) | Severity veto |
| DR | μ(r) = ΔY / c_r (marginal value) | `DiminishingReturnsDetector.marginal_value()` (~2023) | VCR formula |
| DR | μ_m(r) per-model marginal value | `DiminishingReturnsDetector.per_model_mu()` (~2083) | Independent of other models |
| DR | aggregate max(μ_m) | `DiminishingReturnsDetector.aggregate_per_model_mu()` (~2109) | |
| DR | smoothed μ(r) over window W | `DiminishingReturnsDetector.smoothed_marginal_value()` (~2133) | |
| DR | novelty_rate(r) = novel/new | `DiminishingReturnsDetector.novelty_rate()` (~2159) | |
| DR | smoothed novelty rate | `DiminishingReturnsDetector.smoothed_novelty_rate()` (~2172) | |
| DR | vocab_growth_rate(r) | `DiminishingReturnsDetector.vocab_growth_rate()` (~2184) | |
| DR | vocab_saturated(r) | `DiminishingReturnsDetector.vocab_saturated()` (~2193) | Per-area + global |
| DR | stop(r) = exhaustion ∧ abstraction_ok | `DiminishingReturnsDetector.stop()` (~2271) | Conjunctive with guard |
| Immune | Multi-metric pathology detection | `DetectorHealthMonitor.record_round()` (~2582) | Kappa stuck, mu pathology, etc. |
| Immune | Remediation chains with outcome verification | `_REMEDIATION_CHAINS` (~5567); `_verify_remediation_outcomes()` (~3053) | Full chain escalation |
| Immune | Adaptive sensitivity adjustment | `DetectorHealthMonitor.effective_window()` (~2615) | Window decay/growth |
| Role | cap_ρ(m) = α^ρ · q̃_m | `RoleAssignment._capability_score()` (~414) | Normalised fingerprint dot product |
| Allocation | Feasibility P(task fits) = Φ((L - load) / L_std) | `LoadBalancer.feasibility_probability()` (~1041) | Normal approximation |

## Partially Implemented

| Appendix Section | Formula | Code Location | Gap |
|---|---|---|---|
| §2 | f_del(i) delivery feasibility | `LoadBalancer.feasibility_probability()` (~1041) | Conceptually mapped but not formally parameterised as f_del |
| §7.1 | λ(t) Duane NHPP intensity | `ConvergenceDetector.estimate_gamma()` (~1789) | γ diagnostic computed; full intensity function not used |
| §7.2 | H(x) = c·F(x)·ρ_info(x)·G(x) | `Finding.abstraction_index` (~364) | Stored as scalar, not computed from components |
| §7.3 | Ascending abstraction guard (bipartite) | `_abstraction_dropping()` (~2253) | Simplified to h_curr <= h_prev; full bipartite condition not implemented |
| §7.7 | Sev(f) = W(class)·confidence·V(verification) | `Finding.severity` (~363) | Stored as scalar, not computed from components |

## Not Implemented

| Appendix Section | Formula | Notes |
|---|---|---|
| §2 | d_ik class-specific diversity discount | Not needed for immune layer validation |
| §2 | η_dec decomposition yield | Treated as binary feasibility, not yield ratio |
| §2 | φ_i format/parser yield | Monitored empirically, not modelled |
| §7.5 | O_A objective alignment (sycophancy) | Deferred — A-D4 in math model plan |
| §7.6 | Δ_adopt / Δ_drop asymmetric rates | Deferred — A-D1 in math model plan |
| §7.8 | S_v multi-verifier Bayesian severity | Deferred — requires real verification data |
| §7.11 | selected(f) manager selection predicate | Defined but not wired into decision logic |
| §8 | Y_comp > max(Y_i) + k·σ̂ emergence | Not applicable to single-experiment scope |

## Implementation Extensions (code with no appendix counterpart)

| Code Location | Feature | Notes |
|---|---|---|
| `DetectorHealthMonitor._self_diagnosis_history` (~2577) | Self-diagnosis audit trail | Level 3 immune — self-calibration |
| `DetectorHealthMonitor._false_positive_history` (~2572) | False positive tracking | Immune specificity monitoring |
| `_apply_transform()` "add_synthesis_directive" (~5639) | Per-model directive injection | Operational mechanism, not mathematical |
| `_apply_transform()` "add_to_pre_decompose" (~5658) | Decomposition policy mutation | Operational mechanism |
| `FailureHandler._realloc_depth` (~4221) | Reallocation depth tracking | Escalation bookkeeping |
