# Architecture Update — 19 April 2026

Two canonical project documents were refreshed: `docs/ARCHITECTURE.md` and `bench/directives/universal/cdsfl_topology_formal.md`. Both had drifted from the current system state, predating Experiment 40 Stage 3 closure, the Stage 6 literature-calibrated extension of the mathematical model, the §17 feedback channel, the §18 divergence directive, the manifest-driven B-Cell Complex, and the promotion of model agnosticism to full substrate agnosticism (extending to human teams and non-human biological intelligences). Both documents now describe the state at commit `6580737`, 1250 tests passing.

## ARCHITECTURE.md refresh

### Dual Popperian arms

The Overview section was rewritten to foreground the dual Popperian
arms framing. The first arm — severe testing — is operationalised by
the §17 feedback channel working in concert with the FFAFP
admissibility constraint set (S_min, G-completeness, d_tool,
σ_measured, q_retest). The second arm — bold conjecture — is
operationalised by the §18 divergence directive. These two arms are
independent by design. An engaged-but-refuted conjecture receives
partial credit in the channel-reassignment table; a compliant-but-
isomorphic one does not.

### Substrate agnosticism, extended

Substrate agnosticism was extended beyond heterogeneous model panels.
The new language names four valid configurations:

1. Heterogeneous frontier model panels — the original case.
2. Human-only expert panels operating under the same constraint set.
3. Hybrid panels combining human experts and models.
4. Non-human biological intelligences (insect and cephalopod brains)
   interfaced through tool use, provided they satisfy the same
   admissibility and composition-law constraints.

The claim is not that these configurations are empirically
interchangeable, but that the CDSFL constraint set does not require a
particular substrate in order to operate.

### Mathematical framework

The historic C(n) notation has been retired in favour of the unified
recursive state equation R_k(i), derived 8 April 2026:

```
R_k(i) = R_det · (1 − ν_k) + ν_k
R_det  = R_k(i−1) · (1 − q_ik) / (1 − q_ik · R_k(i−1))
```

with critical re-injection rate `ν* = q · R`. The Stage 6
literature-calibrated extension, added 14 April 2026, introduces the
second novelty channel `c_ext` and the combined efficacy term:

```
η_combined = η_int · (1 − c_ext · (1 − ν_k))
```

The mathematical appendix now stands at 1991 lines.

### B-Cell Complex

The B-Cell Complex section was added. The manifest at
`bench/cdsfl_registry/tool_manifest.toml` declares 18 active specialist
domains plus 2 delegated domains. Active domains include SymPy, z3,
RDKit, Biopython, NetworkX, scikit-learn, astropy, pint, uncertainties,
mpmath, AST, pytest, ruff, mypy, bandit, CrossHair, PuLP, and
statsmodels.

The composition law for any cell output is:

```
S_k = A · E
A   = Π g_j          (product of gate values)
E   = Σ w_m · e_m    (weighted aggregate of evidence under confidence w_m)
```

Live domains drive R_k updates. Shadow domains collect telemetry
without contributing to verdicts until they pass their calibration bar.

### §17 feedback channel

The §17 feedback channel section was added. Source:
`bench/dm/_feedback.py` (533 lines). The section documents the action
precedence ordering:

```
REFUTED  >  ADMISSIBILITY FAIL  >  NEAR-DUPLICATE  >  R_k INCONSISTENT
```

Only the first matching action is rendered in the following round's
feedback slot for any given finding. Feedback is scoped per originating
model (not broadcast across the panel) and is bounded by `top_k` and
`max_chars` parameters. This bounding closes the measurement-to-
correction loop of the severe-testing arm.

### §18 divergence directive

The §18 divergence directive section was added. Source:
`bench/dm/_divergence.py` (443 lines). The directive names five
dimensions along which a conjecture may diverge from siblings:
mechanism, assumption, scope, timescale, tradeoff. Isomorphism against
sibling conjectures is assessed using a Jaccard similarity threshold of
0.85. The channel assignment applies an `eta_int_modulator` to that
model's internal efficacy term for the current round:

| Channel             | eta_int_modulator |
|---------------------|-------------------|
| Compliant           | 1.00              |
| Engaged but failed  | 0.85              |
| No engagement       | 0.70              |
| Isomorphic-only     | 0.60              |

Earlier drafts applied the modulator to R_k itself, which would have
conflated the bold-conjecture arm with the severe-testing arm. Applying
the modulator to η_int instead preserves the independence of the two
arms.

### Ouroboros (O1) and Macrophage cells

The Ouroboros cell section was added. O1 handles self-reference cases
and exposes two novelty inputs, ν_k (internal novelty) and c_ext
(external calibration), producing η_combined as the Stage 6 composite.

The Macrophage cell section was added separately, describing its three
operating modes: cleanup of stale findings, integration of retracted
claims, and forensic trace preservation for later adversarial review.

### Data flow

The data flow section was updated end to end. A round now emits a
divergence audit step against prior sibling conjectures and assembles
a feedback section from the preceding round's §17 outputs, scoped to
the originating model. Both additions are pre-composition — they shape
the input each model receives rather than post-hoc filtering of
output.

## cdsfl_topology_formal.md refresh

The companion document is a formal-specification resource, not a
narrative architecture document. The refresh added two new clauses and
extended the Classification Summary table.

### T9 — Feedback Channel Interaction (§17)

For a finding `f` in round `r`:

```
F(f, r) = (flags, verdict, refutations, admissibility_fails,
           near_dup_ids, r_k_discrepancy)
feedback_section(m, r+1) = render(
    { F(f, r) : f.origin = m ∧ F(f, r).flags ≠ ∅ },
    top_k,
    max_chars
)
```

This clause aligns the formal specification with the production
implementation in `_feedback.py`.

### T10 — Divergence Directive Interaction (§18)

A conjecture `k` from model `m` in round `r` receives a channel `c(k)`
in `{Compliant, Engaged but failed, No engagement, Isomorphic-only}`.
The channel assignment function applies a lookup against Jaccard
similarity with prior sibling conjectures, using threshold 0.85. The
modulator values:

```
eta_int_modulator values:
  Compliant:          1.00
  Engaged but failed: 0.85
  No engagement:      0.70
  Isomorphic-only:    0.60
```

The modulator multiplies into η_int for that model and that round, not
into R_k, preserving arm independence.

### Classification Summary table

The Classification Summary table was extended with T9 and T10 rows,
naming their artefact, scope, and evidence source, so that future
consumers of the formal specification can trace each clause to the
production code that realises it.

## Summary

At commit `6580737`, 1250 tests passing, with Experiment 40 Stage 3 substantially closed and residual items gated or deferred to Experiment 54, the canonical architecture document and the formal topology specification both now carry: the dual Popperian arms framing; the unified recursive state equation; the Stage 6 literature-calibrated extension; the §17 feedback channel; the §18 divergence directive with its `eta_int_modulator` table; the manifest-driven B-Cell Complex; and the extended substrate agnosticism. Every added claim traces to production code or to a prior audited mathematical derivation.
