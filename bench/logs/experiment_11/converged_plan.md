# Converged Architecture Plan: Dynamic Management & Load-Balancing Formalisation

## 0. Executive Summary

This plan directs five models to independently formalise six areas of the CDSFL management and load-balancing layer. The six areas are: (1) Role Assignment, (2) Load Balancing, (3) Round Progression, (4) Convergence Detection, (5) Diminishing Returns Detection, (6) Failure Handling. Each model produces all six formalisations independently. The interface contracts below are BINDING — they ensure cross-model composability. Internal mathematics are independent.

**Key constraints:**
- Interface type signatures (§2.2) are fixed. Do not redefine them.
- Notation prefixes (§3) prevent symbol collision with the existing 729-line Mathematical Appendix.
- Every formalisation must show reduction properties for K=1 (single model), homogeneous (all identical), and no-failures (nominal).
- Classify every formalisation as HARD or SOFT.
- PM role is STATIC for the duration of a run (HARD constraint).
- Area 2 (load balancing) formalises how a DEPLOYED FRAMEWORK INSTANCE allocates verification tasks, not how this formalisation exercise is structured.

---

## 1. Dependency Graph

```
                    ┌──────────────┐
                    │ 1. Role      │──────────────────────┐
                    │  Assignment  │                      │
                    └──────┬───────┘                      │
                           │ ρ (role map)                  │ ρ(m) (role for
                           │ ≽_ρ (capability order)       │  performance
                           ▼                               │  expectations)
                    ┌──────────────┐                      │
                    │ 2. Load      │◄──────────────┐      │
                    │  Balancing   │                │      │
                    └──────┬───────┘                │      │
                           │ A (allocation)         │      │
                           │ J(A) (cost)            │      │
                           ▼                        │      │
                    ┌──────────────┐                │      │
                    │ 3. Round     │                │      │
                    │  Progression │                │      │
                    └──┬───────┬───┘                │      │
                       │       │                    │      │
                       ▼       ▼                    │      │
              ┌────────────┐ ┌─────────────┐       │      │
              │4. Converg- │ │5. Diminish- │       │      │
              │  ence Det. │ │  ing Returns│       │      │
              └────────────┘ └─────────────┘       │      │
                                                   │      │
                    ┌──────────────┐                │      │
                    │ 6. Failure   │────────────────┘      │
                    │  Handling    │◄───────────────────────┘
                    └──────────────┘
```

Cross-references:
| Producer | Consumer | Interface |
|----------|----------|-----------|
| Area 1 | Area 2 | ρ (role map) determines participant pool for load balancing |
| Area 1 | Area 6 | ρ(m) determines performance expectations for underperformance detection |
| Area 2 | Area 3 | A (allocation) determines pending work; completion is a transition event |
| Area 2 | Area 6 | A (current allocation) needed for recovery/reallocation decisions |
| Area 4 | Area 3 | converged(r) is a guard on ROUND_k → TERMINAL |
| Area 5 | Area 3 | stop(r) is an alternative guard on ROUND_k → TERMINAL |
| Area 6 | Area 2 | failure(m,r) triggers reallocation |
| Area 6 | Area 3 | Certain failure types are transition events |

---

## 2. Fixed Interface Contracts

These are BINDING on all models. No model may redefine these types.

### 2.1 Shared Universe (from existing schema — immutable)

| Symbol | Type | Source | Meaning |
|--------|------|--------|---------|
| M = {m_1, ..., m_K} | finite set | New | Set of available models |
| (D_decay, v̄, A, C)_m | ℝ⁴ | §7 | Per-model capability fingerprint |
| Sev(f) | [0,1] | §7 | Finding severity |
| S_v(f) | ℝ | §7 | Multi-verifier Bayesian severity |
| Y(t) | ℝ≥0 | §7 | Cognitive yield |
| V̂(t,T) | ℝ | §7 | Online total value estimator |
| Δ | [0,1] | §7 | Adoption delta (independence) |
| D(n) | [0,1] | Part XIII | Distributed coverage |
| λ(t) | ℝ≥0 | §7 | Finding rate (Duane NHPP) |
| γ | ℝ | §7 | Convergence parameter (= 1 − β) |

### 2.2 New Interface Types

```
AREA 1 — Role Assignment
  Input:   M (model set), capability fingerprints {(D_decay, v̄, A, C)_m}
  Output:  ρ : M → {PM, COL, PAR}            — role map (ρ not R, to avoid R_n collision)
           ≽_ρ : partial order on M           — capability ordering used

AREA 2 — Load Balancing
  Input:   ρ (role map), task set T, per-model constraints
           {(τ_m, L_m, c_m)} where τ = response time, L = token limit, c = cost
  Output:  A : T → 2^M                        — task allocation (possibly multi-model)
           J(A) ∈ ℝ                            — cost of allocation
           balanced(A) : predicate             — whether allocation meets balance criteria

AREA 3 — Round Progression
  Input:   Current state s ∈ S, convergence predicate, diminishing returns predicate
  Output:  S = {BLIND, SYNTHESIS, ROUND_k, TERMINAL} — state space (use calligraphic S)
           δ : S × Σ → S                      — transition function
           Σ                                   — alphabet of transition events
           termination_reason ∈ {CONVERGED, DIMINISHED, MAX_ROUNDS, FAILURE}

AREA 4 — Convergence Detection
  Input:   Finding sets {F^(r)}_r across rounds, severity function Sev
  Output:  converged(r) : predicate            — whether round r has converged
           conv_metric(r) ∈ [0,1]              — continuous convergence measure
  NOTE:    Your formalism MUST explicitly define how findings from multiple models
           are aggregated into the unified finding set F^(r) that convergence is
           measured over. This is the result aggregation step — define it.

AREA 5 — Diminishing Returns
  Input:   {Y(t_1), ..., Y(t_r)} (discrete yield samples at round boundaries),
           {c_1, ..., c_r} (per-round costs)
  Output:  marginal_value(r) ∈ ℝ              — value of round r
           stop(r) : predicate                 — whether to stop after round r

AREA 6 — Failure Handling
  Input:   Model response x_m, expected format spec, timeout threshold,
           current state s ∈ S (from Area 3),
           current allocation A (from Area 2),
           role assignment ρ(m) (from Area 1)
  Output:  failure(m, r) : predicate           — whether model m failed in round r
           failure_type(m, r) ∈ {EMPTY, MALFORMED, TIMEOUT, UNDERPERFORM, FORMAT}
           recovery(m, r) : action             — what to do about it
```

---

## 3. Notation Conventions (Binding)

### 3.1 Immutable Symbols

No model may redefine: C(n), F_n, D(n), R_n, G_n, Y(t), V̂(t,T), Δ, Sev(f), S_v(f), λ(t), γ, H(x), O_A, or any symbol from §7–§8 of the existing Mathematical Appendix.

### 3.2 New Symbol Prefixes by Area

| Area | Prefix | Example |
|------|--------|---------|
| Role Assignment | ρ (exclusively, not R) | ρ(m) = role of model m |
| Load Balancing | ℓ or L (calligraphic) | ℓ(t_j, m_i) = load of task j on model i |
| Round Progression | δ, S (calligraphic), Σ | δ(s, σ) = next state |
| Convergence | κ or conv | κ(r) = convergence metric at round r |
| Diminishing Returns | μ or MV | μ(r) = marginal value of round r |
| Failure Handling | φ or fail | φ(m,r) = failure predicate |

**Important:** Use calligraphic S for state space to avoid collision with S_v(f). Use ρ exclusively for role map to avoid collision with R_n. μ is conventionally used for statistical mean — use with care and define explicitly.

### 3.3 Subscript Conventions

- Model index: m or i
- Round index: r (exclusively, to avoid ambiguity with flaw-class k)
- Task index: j
- Flaw-class index: k (consistent with existing w_k in F_n)

### 3.4 Time Convention

Continuous time t for within-round dynamics (consistent with λ(t), Y(t)). Discrete round index r for between-round dynamics. New formalisations should maintain this convention unless deviation is explicitly justified.

### 3.5 Predicate Naming

Boolean predicates are lowercase with parenthesised arguments: converged(r), stop(r), failure(m,r). Consistent with selected(f) in §7.11.

### 3.6 Set Naming

Calligraphic for sets: M (models), T (tasks), F^(r) (findings in round r).

### 3.7 Constraint Classification

Every formalisation must be tagged HARD (mathematically necessary) or SOFT (reasonable design choice). This mirrors CDSFL core directive §1.

### 3.8 Reduction Property Requirement (HARD)

Every formula must show what it reduces to when:
- K = 1 (single model — should recover trivial behaviour)
- All models identical (homogeneous — should recover symmetric solutions)
- No failures occur (nominal — failure handling terms vanish)

---

## 4. HARD Constraints (Binding on All Models)

1. Interface contracts (§2.2) are binding. (HARD — mathematical necessity for composability.)
2. PM role is static for the duration of a run. ρ_PM is assigned once. Other roles (COL, PAR) may be reassigned between rounds. (HARD — eliminates ambiguity about Area 1 → Area 3 interface.)
3. Reduction property requirement. (HARD — standard mathematical practice for verification.)
4. Six-area decomposition. (HARD — the dependency graph shows completeness.)
5. Area 2 scope: formalises task allocation in a DEPLOYED framework instance, not in this formalisation exercise. All five models address all six areas independently. (HARD — scope clarity.)

---

## 5. Required Output Structure Per Model

```
═══════════════════════════════════════════════════════
MODEL: [model name]
DATE: [timestamp]
═══════════════════════════════════════════════════════

For each of the six areas (in order 1–6):

ITEM: [Area N: Name]
─────────────────────────────────────────────────────
DEFINITION:
  [Mathematical definition using the fixed interface types from §2.2]
  [All new symbols defined]
  [Relationship to existing symbols shown]

REDUCTION PROPERTIES:
  K=1:          [what the formula becomes]
  Homogeneous:  [what the formula becomes]
  No failures:  [what the formula becomes]

EDGE CASES:
  [List with mathematical treatment]

CONSTRAINT_CLASS: HARD | SOFT
JUSTIFICATION: [why this classification]

VERDICT: [self-assessment: SOUND | PROVISIONAL | WEAK]
CONFIDENCE: 0.XX
EVIDENCE: [mathematical justification]
STRONGEST_OBJECTION: [best argument against]
RESPONSE: [response to objection]
─────────────────────────────────────────────────────

After all six areas:

NOTATION SUMMARY:
  [Table: Symbol | Type | Area | Definition | Relates to]

CROSS-REFERENCE CHECK:
  [Verify all interface contracts from §2.2 are satisfied]
  [Verify no existing symbol redefined]
  [Verify reduction properties are consistent across areas]

INTERNAL P-PASS LOG:
  [What claims were falsified during drafting]
  [What was revised and why]
═══════════════════════════════════════════════════════
```

Additional sections beyond those specified are welcome. The required sections are the minimum for cross-model comparability.

If token constraints force truncation, prioritise areas in dependency order: Area 1 first (no dependencies), then Area 2, then Areas 4 and 5 (parallel), then Area 3 (depends on 4 and 5), then Area 6. Within each area, DEFINITION and REDUCTION PROPERTIES are mandatory; other sections are best-effort.

---

## 6. Seed Constraints Per Area

These are starting points, not mandates. Models may deviate with justification.

### 6.1 Role Assignment

The capability fingerprint (D_decay, v̄, A, C) already exists in §7. Role assignment should be a function OF this fingerprint, not a parallel system. PM role is static (HARD constraint above). Other roles may be dynamic — formalise both the initial assignment and the between-round reassignment condition if you use dynamic roles. §7.11 defines selected(f) for finding selection; role assignment is the model-level analogue.

### 6.2 Load Balancing

Models have heterogeneous (τ_m, L_m, c_m). Is this a standard assignment problem (one task per model) or a coverage problem (multiple models per task, as in the existing D(n))? The existing D(n) with overlap terms o_ik suggests the latter. Be consistent with D(n)'s assumption structure.

### 6.3 Round Progression

Protocol constants: max_rounds = N (parameterise for generality; current deployment uses N=5), blind_first = true, stop_rule = counting_plus_verify. The state space is finite for any fixed N. The transition guards are the interesting part. The Duane NHPP λ(t) and V̂(t,T) provide the signals that drive transitions.

### 6.4 Convergence Detection

Must not be merely "no new findings." The existing schema has Δ (adoption delta) and λ(t) (finding rate). Is convergence a property of the finding SET (set-theoretic stability) or the finding RATE (statistical stability)? The Duane model suggests rate-based, but set-theoretic is also defensible. γ = 1 − β is already called the "convergence parameter" — connect to it. Your formalism MUST explicitly define how findings from multiple models are aggregated into the unified finding set F^(r).

### 6.5 Diminishing Returns

Must connect to V̂(t,T) and the ascending abstraction guard (dY/dt, not dN/dt). The task brief says "relative to their cost," so this is a value/cost ratio. Diminishing returns is the condition where V̂(t+Δt, T) − V̂(t, T) < c_round for some cost threshold.

### 6.6 Failure Handling

Five failure types: EMPTY, MALFORMED, TIMEOUT, UNDERPERFORM, FORMAT. Each has different implications. Is "underperform" defined relative to the model's own capability fingerprint (doing worse than expected) or relative to others (worst performer)? The fingerprint suggests the former. ρ(m) from Area 1 determines performance expectations (PM vs PAR have different baselines).

---

## 7. Existing Schema Context

The full Mathematical Appendix (§§1–8, 729 lines) is provided separately. Key elements your formalisations must be consistent with:

- C(n) = 1 − (1−p)^n — corroboration after n passes
- F_n = Σ_k w_k [1 − Π_i (1 − d_ik p_ik)] — falsification coverage
- D(n) = Σ_k w_k [1 − Π_i (1 − p_ik (1 − o_ik))] — distributed coverage with overlap
- R_n — Bayesian residual risk
- G_n — combined detection
- λ(t), γ — Duane NHPP decay, convergence parameter
- H(x) — Abstraction Index
- Y(t) = N(t) · H̄(t) — Cognitive Yield
- V̂(t,T) — Online Total Value Estimator with ascending abstraction guard
- O_A — Objective Alignment
- Δ — Adoption Delta
- Sev(f), S_v — Severity (per-finding and multi-verifier)
- Capability fingerprint (D_decay, v̄, A, C)
- selected(f) — finding selection predicate (§7.11)
- Y_composite > Y_union + k·σ̂ — emergence condition (§8)

Protocol constants: max_rounds = 5, stop_rule = counting_plus_verify, blind_first = true, hard_coverage_threshold = 1.0, hard_veto = true, peer_support_min_families = 2.
