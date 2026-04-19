# Extended Rationale Update — 19 April 2026

This note documents the April 2026 additions to the general-audience
companion document `docs/EXTENDED_RATIONALE.md`. The document had been
updated in late March 2026 with the three-architecture review section.
Since then, five substantive developments had occurred that the
general-audience document did not yet reflect. The refresh adds five
new sections, written in the same reflective journalistic register as
the rest of the document, each tied to a dated milestone in April
2026.

## The Unified State Equation (8 April 2026)

The first new section covers the derivation of the unified recursive
state equation `R_k(i)`, completed on 8 April 2026. The section
explains why the earlier two-level presentation — `C(n)` for the lay
reader and `F_n` for the technical reader — had a gap. `C(n)` treated
flaws as uniform. `F_n` addressed that but described a single round
rather than a running state. Neither produced a single scalar that a
working system could compute, audit, and update.

The new section describes `R_k(i)` as the closure of that gap:

```
R_k(i) = R_det · (1 − ν_k) + ν_k
R_det  = R_k(i−1) · (1 − q_ik) / (1 − q_ik · R_k(i−1))
ν*     = q · R        (critical re-injection equilibrium)
```

The section names `ν*` as the equilibrium that prevents the procedure
from mistaking repetition for corroboration, and explains why the
retirement of the `C(n)` notation was functional rather than
aesthetic. It closes with a note that the equation is itself
falsifiable by the framework's own prescription — the minimum
consistency condition the methodology imposes on itself.

## Cells With Teeth (9–14 April 2026)

The second new section covers the B-Cell Complex and the 18 active
specialist domains (plus 2 delegated) declared in the manifest at
`bench/cdsfl_registry/tool_manifest.toml`. The section names each
active domain:

| Domain | Tool |
|--------|------|
| Symbolic mathematics | SymPy |
| Constraint satisfaction / formal verification | z3 |
| Chemistry / molecular structure | RDKit |
| Biological sequence analysis | Biopython |
| Graph theory | NetworkX |
| Machine learning metrics | scikit-learn |
| Astronomical / physical constants | astropy |
| Dimensional analysis | pint |
| Measurement uncertainty | uncertainties |
| Arbitrary-precision arithmetic | mpmath |
| Code structure | AST |
| Test execution | pytest |
| Linting | ruff |
| Static typing | mypy |
| Security scanning | bandit |
| Symbolic execution | CrossHair |
| Linear programming | PuLP |
| Statistical inference | statsmodels |

The section describes the uniform composition law:

```
S_k = A · E
A   = Π g_j            (product of gate values)
E   = Σ w_m · e_m      (weighted evidence aggregate)
```

It explains the distinction between **active** domains (contributing
to `R_k`) and **shadow** domains (collecting telemetry until they pass
their calibration bar). The narrow but important point: the set of
cells whose outputs determine whether a claim stands is a calibrated
set, not a default configuration.

## Two Arms, Not One (14–16 April 2026)

The third new section covers the dual Popperian arms framing that
emerged from the §17 and §18 additions in mid-April 2026. The section
locates the framing against the Popper-versus-Kuhn dispute, noting
that a methodology that treats falsification as the only work and
leaves generation unstructured is answering half the question.

- **§17 — Feedback channel** is described as the severe-testing arm:
  a bounded, scoped, precedence-ordered feedback loop with ordering
  `REFUTED > ADMISSIBILITY FAIL > NEAR-DUPLICATE > R_k INCONSISTENT`.
- **§18 — Divergence directive** is described as the bold-conjecture
  arm, naming the five divergence dimensions (mechanism, assumption,
  scope, timescale, tradeoff) and the four channel assignments with
  their `eta_int_modulator` values:

| Channel             | eta_int_modulator |
|---------------------|-------------------|
| Compliant           | 1.00              |
| Engaged but failed  | 0.85              |
| No engagement       | 0.70              |
| Isomorphic-only     | 0.60              |

The section gives particular attention to the design decision that
took longest to get right. Earlier drafts applied the divergence
modulator to `R_k` itself. That conflated the severity of a test with
the boldness of a claim — a model proposing a bold but wrong
conjecture would see `R_k` directly degraded by its intellectual
courage. Applying the modulator to `η_int` instead keeps the two arms
independent. A brave but refuted conjecture is punished for being
refuted, not for being brave. A compliant but isomorphic one is
punished for its isomorphism, not rewarded for its agreement. The
asymmetry is load-bearing, and the design iterated until it was
right.

## Substrate Agnosticism, Extended (mid-April 2026)

The fourth new section extends the language of model-agnosticism to
full substrate-agnosticism. Four valid configurations are named:

1. **Heterogeneous frontier model panel** — the original case.
2. **All-human expert panel** operating under the same constraint
   set.
3. **Hybrid panel** combining humans and models at separate
   admissibility tiers.
4. **Non-human biological intelligences** (insect brains, cephalopods)
   interfaced through tool use, provided they satisfy the same
   admissibility and composition-law constraints.

The section makes the practical corollary explicit. Once substrate
agnosticism is properly stated, the locus of expertise ceases to be a
property of *who or what* produced a claim. It becomes a property of
whether the claim *survived the discipline*. A brilliant human expert
whose output cannot satisfy the admissibility constraints is, for the
purposes of the framework, not acting as an expert on that claim. A
cephalopod whose tool-use produces admissible output is contributing
expertise on that claim. The framing is deliberately severe, on the
grounds that locking expertise to substrate rather than to discipline
is the failure mode the methodology was built to resist.

## Experiment 40 and Operational Closure (17–19 April 2026)

The fifth new section records the substantial closure of Experiment
40 Stage 3 during 17–19 April 2026. The section names:

- Phase A commit: `8b8682d`
- Phase B commit: `bdfc93a`
- Documentation synchronisation: `6580737`
- Test count: **1250 tests passing**
- Residual items: a gated value-flip assertion and a runtime
  assertion deferred to Experiment 54.

The section is careful to separate what Stage 3 closure does and does
not establish. It establishes that the formal documents, the
mathematics, and the code now describe the same object without drift.
It does not establish empirical validation of the framework's
underlying hypothesis. That validation, if it occurs, will come from
Experiments 41–54, particularly the 2×2 factorial design that will
test whether the §17 and §18 additions produce the improvements the
derivation predicts.

The section closes with a note on the framework's relation to its own
limits: a passing test suite is a minimum condition for the
measurements that follow, not a substitute for them.

## Summary

The five new sections bring the general-audience document into line
with the April 2026 state of the project. The register matches the
existing document. Technical terms are introduced with inline glosses
on first use. The sections preserve the existing structure, appearing
between the 27 March 2026 section on the method applied to itself and
the closing references block. No existing claims were removed. The
mathematical notation `C(n)` is preserved in context as the
pedagogical introduction and then shown to have been superseded by
the unified equation, rather than being deleted from the earlier
narrative. The refresh was additive and preserved the reflective
journalistic voice that distinguishes the extended rationale from the
formal specification and the white paper.
