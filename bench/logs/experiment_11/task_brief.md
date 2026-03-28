# Task Brief: Dynamic Management and Load-Balancing Formalisation

## What You Are Being Asked To Do

Produce mathematical formalisations for the management and load-balancing
layer of a multi-agent analytical framework. The framework (CDSFL) runs
multiple AI models in structured rounds of collaborative falsification.
The core falsification model, cognitive measurement framework, and emergence
formalisations already exist (see context below). What is MISSING is the
formal mathematical treatment of:

1. **Role assignment** — how to assign models to roles (collator, player
   manager, participant) given their capability fingerprints.
2. **Load balancing** — how to distribute computational work across
   participants with heterogeneous response times, token limits, and costs.
3. **Round progression** — when to advance between phases (blind round,
   synthesis, subsequent rounds), formalised as state transitions.
4. **Convergence detection** — a mathematical criterion for when findings
   have stabilised across participants (not just "tests pass" or "it feels
   done").
5. **Diminishing returns detection** — quantifying when additional rounds
   add insufficient value relative to their cost.
6. **Participant failure handling** — what happens mathematically when a
   model fails (empty response, malformed output, timeout), consistently
   underperforms, or produces output that fails structured format compliance.

## Scope Boundary

You are formalising the MANAGEMENT AND LOAD-BALANCING LAYER ONLY.

DO:
- Express all formalisations as mathematical definitions, predicates, and
  functions consistent with the notation in the existing schema.
- Classify every proposed formalisation as HARD (mathematically necessary)
  or SOFT (design choice that could reasonably be different).
- Run internal P-passes on your own formalisations before presenting them.
- Use the structured output format (VERDICT, EVIDENCE, CONSTRAINT_CLASS,
  CONFIDENCE, STRONGEST_OBJECTION, RESPONSE) for each major formalisation.

DO NOT:
- Revisit or modify the core falsification model (C(n), F_n, R_n, G_n).
- Revisit or modify the cognitive measurement framework (§7: decay curves,
  abstraction index, severity, capability fingerprints).
- Revisit or modify the emergence formalisations (§8: composite yield,
  metacognitive feedback, substrate agnosticism).
- Propose changes to the CDSFL core directives.

The output extends the existing schema. It does not replace it.

## Existing Schema Context

The following already exists in the CDSFL mathematical model. Your
formalisations must be consistent with these and reference them where
appropriate.

### Core Models (White Paper Parts II, XII, XIII)

- **C(n) = 1 - (1-p)^n** — simple corroboration after n passes.
- **F_n = Sigma_k w_k [1 - Pi_i (1 - d_ik p_ik)]** — structured
  falsification coverage across flaw classes.
- **D(n) = Sigma_k w_k [1 - Pi_i (1 - p_ik (1 - o_ik))]** — distributed
  compute coverage with inter-architecture overlap.
- **R_n** — Bayesian residual risk after clean run.
- **G_n** — combined machine-HIL detection with cross-correlation.

### Cognitive Measurement (Mathematical Appendix §7)

- **Duane NHPP decay curves** — lambda(t) for finding rate over time.
  Convergence parameter gamma = 1 - beta.
- **H(x)** — Abstraction Index combining formality, information density,
  generalisation scope. Discrimination ratio 33.4x.
- **Y(t) = N(t) . H_bar(t)** — Total Cognitive Yield.
- **V_hat(t,T)** — Online Total Value Estimator with ascending abstraction
  guard (dY/dt, not dN/dt).
- **O_A** — Objective Alignment via verifiable finding concordance.
- **Delta** — Adoption Delta measuring independence between rounds.
- **Sev(f)** — Per-finding severity with veto on disproved findings.
- **S_v** — Multi-verifier Bayesian severity (log-odds fusion).
- **Capability fingerprint (D_decay, v_bar, A, C)** — four-dimensional
  per-model characterisation.

### Manager Selection (Mathematical Appendix §7.11)

- **selected(f) = (Sev(f) > tau_sev) AND (S_v(f) >= 0.5) AND
  (class(f) = HARD OR Sev(f) > tau_soft)** — finding selection predicate.

### Emergence (Mathematical Appendix §8)

- **Y_composite > Y_union + k . sigma_hat** — strong emergence condition.
- **Metacognitive feedback protocol** — strategy adjustments from
  decay/verification/adoption signals.
- **Second-order cognitive system** — formal four-criterion definition.

### Protocol Constants (Registry universal.toml)

- max_rounds = 5
- stop_rule = counting_plus_verify
- blind_first = true
- hard_coverage_threshold = 1.0
- hard_veto = true
- peer_support_min_families = 2

## What Good Output Looks Like

For each of the six areas (role assignment, load balancing, round
progression, convergence detection, diminishing returns, failure handling):

1. State the mathematical definition or predicate clearly.
2. Define all new symbols and show how they relate to existing notation.
3. Show the reduction property — what does the formula reduce to under
   simplifying assumptions? Does it recover known special cases?
4. Identify edge cases and boundary conditions.
5. Classify as HARD or SOFT.
6. State the strongest objection to your own formalisation and respond to it.

The formalisations should be implementable. They will become new sections
of the Mathematical Appendix (tentatively §9 or new subsections of §7).
They must be consistent with the existing notation summary (729 lines of
existing appendix).

## Output Format

Use the CDSFL structured output format for each major formalisation:

```
ITEM: [area being formalised]
VERDICT: [your assessment of your own formalisation]
EVIDENCE: [mathematical justification, reduction properties, edge cases]
CONSTRAINT_CLASS: HARD | SOFT
CONFIDENCE: 0.XX
STRONGEST_OBJECTION: [the best argument against your formalisation]
RESPONSE: [your response to that objection]
```

After all individual items, provide a NOTATION SUMMARY listing every new
symbol introduced and its relationship to existing symbols.
