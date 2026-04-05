# CDSFL Multi-Model Topology — Formal Specification

This document specifies the star/blackboard topology for multi-model review
under CDSFL. It extends the core directives (`cdsfl_core_formal.md`) with
formal definitions for finding management, status transitions, convergence
gating, and durability.

The core directives govern individual model reasoning. This document governs
how multiple models coordinate through a shared canonical record.

**Provenance:** Derived from runner fitness confer (5 April 2026) where
implementation bugs in Exp 34/35/36 revealed specification gaps. Each section
addresses a gap where correct implementations could diverge because the
specification was silent or ambiguous.

---

## T1. Star/Blackboard Topology

**Natural language:**
All models communicate through a single canonical record (the blackboard).
No model communicates directly with another. The runner owns the blackboard.
Models emit proposals; the runner decides what becomes canonical state.

**Formal:**
```
Let M = {m_1, m_2, ..., m_n} be the set of participating models.
Let B be the blackboard (canonical state).
Let R be the runner (coordinator).

Communication constraint:
  ∀ m_i, m_j ∈ M, i ≠ j:
    direct_channel(m_i, m_j) = ∅

All communication is mediated:
  m_i → R → B → R → m_j

State ownership:
  write(B) is exclusive to R
  read(B) is available to all m_i via R-provided summaries

Models emit proposals P_i = {findings, verdicts}.
R validates, deduplicates, and applies P_i to B.
```

---

## T2. Finding Status Model

**Natural language:**
Every finding begins as OPEN. It can transition to CONFIRMED (2+ independent
models agree), MERGED (subsumed into another finding), or UNCONFIRMED (experiment
ends without confirmation). A CONFIRMED finding can be reopened to CONTESTED if
new evidence arrives via a CHALLENGE verdict after the most recent CONFIRM. A
CONTESTED finding must be resolved before convergence can be declared.

**Formal:**
```
Status ∈ {OPEN, CONFIRMED, CONTESTED, MERGED, UNCONFIRMED}

State machine transitions:

  OPEN → CONFIRMED
    when: |{m ∈ M : confirmed(m, f)}| ≥ 2 ∧ independent(m_source, m_confirmer)
    where: independent(a, b) ≡ vendor_family(a) ≠ vendor_family(b)
           ∨ (a ≠ b ∧ vendor independence not required)

  OPEN → MERGED
    when: merge_verdict(f, target) accepted
    effect: f.merged_into = target.canonical_id

  OPEN → UNCONFIRMED
    when: experiment terminates ∧ f.status = OPEN

  CONFIRMED → CONTESTED
    when: ∃ challenge(m_c, f) at round r_c
          ∧ r_c > max({r : confirm(_, f) at round r})
    note: the challenge must be LATER than the most recent confirm

  CONTESTED → CONFIRMED
    when: challenge is resolved (new confirm after the challenge)

  CONTESTED → UNCONFIRMED
    when: experiment terminates ∧ f.status = CONTESTED

  MERGED is terminal (no outgoing transitions)

Invariants:
  ∀ f: f.status = MERGED → ∃ target: f.merged_into = target ∧ target.status ≠ MERGED
  ∀ f: f.status = UNCONFIRMED → experiment_terminated
  At experiment end: ∀ f: f.status ∈ {CONFIRMED, MERGED, UNCONFIRMED}
    (no OPEN or CONTESTED findings survive termination)
```

---

## T3. Merge Contract

**Natural language:**
A MERGE verdict declares that one finding (the source) is a duplicate of
another (the target). The source is subsumed; the target survives. The
verdict `MERGE target <- source` means: mark the source as MERGED with a
pointer to the target. Never mark the target as MERGED unless it is itself
being subsumed by a third finding.

**Formal:**
```
MERGE(target, source):
  Preconditions:
    target ∈ B.entries ∧ target.status ∈ {OPEN, CONFIRMED, CONTESTED}
    source ∈ B.entries ∧ source.status ∈ {OPEN, CONFIRMED, CONTESTED}
    target ≠ source

  Effect:
    source.status ← MERGED
    source.merged_into ← target.canonical_id
    target.status is UNCHANGED

  Directionality rule:
    The syntax "MERGE C0001 <- F002" means:
      target = C0001 (the survivor)
      source = the canonical entry corresponding to the model's F002

  Resolution of source identity:
    Given model m issuing "MERGE C_target <- F_local":
      source_canonical = alias_map[m, F_local]
      If source_canonical is undefined: treat as CONFIRM on target

  Anti-loop invariant:
    ∀ f: f.merged_into ≠ f.canonical_id
    The merge graph must be acyclic (a DAG, not a cycle)
```

---

## T4. Convergence Gate

**Natural language:**
Convergence requires ALL conditions to hold for N consecutive rounds (where
N = CONSECUTIVE_ROUNDS_REQUIRED, typically 2). Each condition is evaluated
per round. The per-round conjunction is stored as a boolean. Convergence is
declared only when the last N stored booleans are all true. No single
condition is windowed independently — the conjunction as a whole must be
stable.

**Formal:**
```
Let G(r) be the gate evaluation at round r.

G(r) = g_1(r) ∧ g_2(r) ∧ g_3(r) ∧ g_4(r) ∧ g_5(r)

where:
  g_1(r) ≡ r ≥ EARLIEST_STOP_ROUND
  g_2(r) ≡ |{f ∈ B : f.status ∈ {OPEN, CONTESTED} ∧ f.severity ≥ 0.7}| = 0
  g_3(r) ≡ novel_count(r) ≤ MAX_NOVEL_FINDINGS
  g_4(r) ≡ contested_count(r) = 0
  g_5(r) ≡ gamma_gate(γ(r), r) = PASS

Gate history:
  H = [G(r_start), G(r_start+1), ..., G(r_current)]

Convergence predicate:
  converged(r) ≡ |H| ≥ N ∧ ∀ i ∈ [|H|-N, |H|-1]: H[i] = true

  where N = CONSECUTIVE_ROUNDS_REQUIRED

Budget exhaustion:
  If r = r_max ∧ ¬converged(r):
    convergence_debt > 0
    Output carries the same epistemic status as a P-pass terminated
    by budget exhaustion (see core spec §3).

Extension trigger:
  If r = MAX_ROUNDS ∧ ¬converged(r) ∧ extension_conditions_met(r):
    r_max ← EXTENSION_CAP
```

---

## T5. Reliability Growth Estimation (Duane Gamma)

**Natural language:**
Gamma measures the rate at which novel discoveries are declining — the
system's approach to saturation. It is estimated from the cumulative novel
discovery series using log-log regression. The input series is canonical
novel findings per round (deduplicated), not raw parsed findings.

**Formal:**
```
Let n_r = novel canonical findings registered in round r.
Let N_r = Σ_{i=0}^{r} n_i  (cumulative novel count at round r)

Estimation method: ordinary least squares on log-transformed data.

  For all rounds r where N_r > 0:
    x_r = ln(r + 1)       (use r+1 to avoid ln(0))
    y_r = ln(N_r)

  Fit: y = α + β·x   via OLS

  Duane gamma: γ = 1 − β

  where β is the growth exponent (slope in log-log space)

Properties:
  γ → 1 as discovery rate → 0 (saturation)
  γ → 0 as discovery rate remains constant (no saturation)
  γ < 0 is possible (accelerating discovery — investigation needed)

Input constraint:
  n_r MUST be canonical novel findings (post-deduplication,
  post-alias-resolution), NOT raw parsed findings.
  Using raw findings inflates the series with rediscoveries and
  cross-model echoes, producing a γ that does not correspond to
  the Duane reliability growth model.

Scale-dependent gates:
  Rounds [0, T_telemetry):     γ is telemetry only (no gate)
  Rounds [T_telemetry, T_hard): γ_soft gate (advisory, flags HIL review)
  Rounds [T_hard, ∞):           γ_hard gate (blocks convergence)

  T_telemetry, T_hard, γ_soft_threshold, γ_hard_threshold are
  experiment parameters, not schema constants.
```

---

## T6. Round Taxonomy

**Natural language:**
Not all rounds produce new findings. In the star/blackboard topology, later
rounds often consist primarily of verdicts on existing findings rather than
new discoveries. The protocol must distinguish between finding-producing
responses and verdict-only responses to avoid treating verdict text as
spurious findings.

**Formal:**
```
Response classification:
  Let resp(m, r) be the response from model m in round r.

  has_findings(resp) ≡ structured_findings_parsed(resp) ∧ |findings| > 0
  has_verdicts(resp) ≡ verdict_patterns_matched(resp)

  Response types:
    FINDING_RESPONSE:  has_findings(resp)
    VERDICT_RESPONSE:  ¬has_findings(resp) ∧ has_verdicts(resp)
    MIXED_RESPONSE:    has_findings(resp) ∧ has_verdicts(resp)
    EMPTY_RESPONSE:    ¬has_findings(resp) ∧ ¬has_verdicts(resp)

  VERDICT_RESPONSE is valid and expected in adaptive rounds (r > 0).
  It MUST NOT trigger fallback finding generation.

  EMPTY_RESPONSE may trigger fallback or anti-deference gate depending
  on response length and experiment policy.

Round types:
  BLIND (r = 0):    Models have no blackboard context. All responses
                    should be FINDING_RESPONSE.
  ADAPTIVE (r > 0): Models receive blackboard summary. Responses may
                    be FINDING_RESPONSE, VERDICT_RESPONSE, or MIXED.
```

---

## T7. Durability Contract

**Natural language:**
The canonical blackboard and all convergence state must survive interruption.
If the experiment resumes after a crash or pause, the resumed run must be
mathematically equivalent to the run that would have continued without
interruption. This means the full blackboard state — not just the model's
internal memory — must be persisted and restored.

**Formal:**
```
Let S(r) be the complete experiment state after round r.

S(r) = {B(r), H(r), N(r), Γ(r), Ctx(r)}

where:
  B(r) = blackboard state (FindingRegistry: entries, aliases, next_id)
  H(r) = gate history [G(0), ..., G(r)]
  N(r) = novelty counts [n_0, ..., n_r]
  Γ(r) = gamma history [γ_0, ..., γ_r]
  Ctx(r) = cumulative context budget consumed

Durability invariant:
  ∀ r: persist(S(r)) after round r completes
  On resume at round r+1: load(S(r)) before dispatching round r+1

Correctness criterion:
  Let run_continuous be the experiment without interruption.
  Let run_resumed be the experiment interrupted after round r and resumed.

  ∀ r' > r: S_continuous(r') = S_resumed(r')
    (given identical model responses — the runner's state must be
    deterministically reconstructable)

What must NOT be lost on resume:
  - Canonical finding IDs and their status history
  - Alias mappings (model-local ID → canonical ID)
  - Verdict history (all CONFIRM/CHALLENGE/EXTEND/MERGE records)
  - Convergence gate history
  - Novelty and gamma series

What MAY be reconstructed from logs:
  - Round timing data
  - Token counts
  - Model response text (if logged)
```

---

## T8. P-Pass Boundary Tracing (Amendment to Core Spec §3)

**Natural language:**
When falsifying a claim about a system, trace the claim to the system
boundary before accepting or rejecting it. A claim about component A that
depends on the behaviour of component B is not falsified by examining A
alone. The P-pass must follow the claim's dependency chain to wherever the
truth value is actually determined.

This directive was added after a confer in which a reviewing model
repeatedly asserted that finding IDs would collide across models, without
checking the shared parser that prefixes model IDs before the IDs reach
the component under analysis. The claim was locally plausible but globally
false. Three independent reviews reproduced the same error because none
traced the claim to the system boundary.

**Formal:**
```
Amendment to §3 (Falsification Loop), added condition:

For each claim c_i about system component A:
  Let deps(c_i) = {B_1, ..., B_k} be components whose behaviour
    determines the truth value of c_i

  boundary_traced(c_i) ≡ ∀ B_j ∈ deps(c_i):
    examined(B_j) ∧ behaviour_of(B_j) incorporated into
    evaluation of c_i

  ¬boundary_traced(c_i) → c_i carries unresolved dependency risk
    (equivalent to residual falsification debt)
```

---

## Classification Summary (Extension)

| Section | Formal Structure | Formalisable |
|---------|-----------------|:---:|
| T1. Star/blackboard topology | Communication graph with ownership | Yes |
| T2. Finding status model | Finite state machine with guard conditions | Yes |
| T3. Merge contract | Directed operation with preconditions | Yes |
| T4. Convergence gate | Temporal conjunction over boolean history | Yes |
| T5. Gamma estimation | Log-log regression specification | Yes |
| T6. Round taxonomy | Response classifier | Yes |
| T7. Durability contract | State persistence invariant | Yes |
| T8. P-pass boundary tracing | Dependency-chain completeness predicate | Yes |
