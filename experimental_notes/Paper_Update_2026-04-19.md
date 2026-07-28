# Paper Update — 19 April 2026

`PAPER.md` was updated in April 2026 from version 1.0 to version 1.1. Three changes were made:

1. Version line and date updated.
2. Abstract extended to record the April 2026 developments.
3. New **Addendum: April 2026 Developments** section added before the
   References block, in seven subsections.

## Version and Date Update

The version line was updated from *v1.0 dated March 2026* to
*v1.1 dated April 2026*. The trailing attribution line at the end of
the main body was updated to match.

## Abstract Extension

The abstract was extended to add:

- The unified recursive state equation `R_k(i)`, derived during the
  8 April mathematical audit, now supersedes `C(n)` as the canonical
  claim-state representation.
- The two Popperian arms were named: §17 (feedback channel, severe
  testing) and §18 (divergence directive, bold conjecture), with
  their source files.
- Stage 6 literature-calibrated extension and the second novelty
  dimension `c_ext` introduced, along with the manifest-driven B-Cell
  Complex of 18 active specialist domains.
- Experiment 40 Stage 3 closure recorded with test count 1250/1250
  passing; 2×2 factorial scheduled as Experiments 41–54 named as the
  empirical validation path.

## Addendum Structure

The Addendum is placed before References, in seven subsections.

### A.1 The Unified Recursive State Equation

Records the derivation, presents the equation in canonical form, and
explains the relationship between `R_k(i)` and the earlier `C(n)`.
`C(n)` is preserved as the pedagogical introduction — the degenerate
limit of `R_k(i)` under uniform flaw detection, independent passes,
and no novelty injection. The feedback and divergence channels
operate on `R_k(i)` and on `η_int`, not on `C(n)`.

```
R_k(i) = R_det · (1 − ν_k) + ν_k
R_det  = R_k(i−1) · (1 − q_ik) / (1 − q_ik · R_k(i−1))
ν*     = q · R
```

### A.2 Stage 6 — Literature-Calibrated Extension

Presents the combined efficacy equation:

```
η_combined = η_int · (1 − c_ext · (1 − ν_k))
```

Records: ν_k design iterated over 2 confer rounds, 12 corrections.
Mathematical appendix now stands at 1991 lines.

### A.3 The Two Popperian Arms — §17 and §18

**§17 — Feedback Channel.** Presents the six-tuple rendering and
action precedence:

```
REFUTED > ADMISSIBILITY FAIL > NEAR-DUPLICATE > R_k INCONSISTENT
```

**§18 — Divergence Directive.** Five divergence dimensions
(mechanism, assumption, scope, timescale, tradeoff), Jaccard
threshold 0.85. Channel assignment table:

| Channel             | η_int_modulator |
|---------------------|-----------------|
| Compliant           | 1.00            |
| Engaged but failed  | 0.85            |
| No engagement       | 0.70            |
| Isomorphic-only     | 0.60            |

The subsection gives particular attention to the design decision
that took longest to get right: the choice of where the modulator
acts. Earlier drafts applied it to `R_k` directly, which would have
conflated the severity of a test with the boldness of a claim.
Applying the modulator to `η_int` instead preserves arm
independence.

### A.4 The B-Cell Complex and the Composition Law

Presents:

```
S_k = A · E
A   = Π g_j              (product of gate values)
E   = Σ w_m · e_m        (weighted evidence aggregate)
```

Names 18 active specialist domains wired across Tranches A and B,
organised by category (symbolic/constraint, numerical, statistical,
dimensional/physical, chemistry/biology, graph theory, optimisation,
code analysis). Tranche C domains held in shadow until they pass
their calibration bar.

### A.5 Substrate Agnosticism, Extended

Four valid configurations:

1. Heterogeneous frontier model panel.
2. All-human expert panel.
3. Hybrid panel.
4. Non-human biological intelligences interfaced through tool use.

Expertise is a property of whether the claim survived the discipline,
not of who or what produced it.

### A.6 Experiment 40 and Operational Closure

- Phase A commit: `8b8682d`
- Phase B commit: `bdfc93a`
- Documentation sync: `6580737`
- Tests passing: **1250 / 1250**
- Residual: `1E.3` (gated), `1E.10` (deferred to Exp 54)

Stage 3 closure establishes drift-freedom between documents,
mathematics, and code. It does not establish empirical validation of
the §17 and §18 hypotheses — that comes from the 2×2 factorial in
Experiments 41–54.

### A.7 Addendum Summary of Falsifiable Claims

Seven new falsifiable claims, each with its refutation condition:

1. **`R_k(i)` as canonical claim-state** — falsified if a fundamentally
   different update rule predicts trajectories more accurately.
2. **Stage 6 two-dimensional novelty** — falsified if `c_ext` provides
   no measurable improvement over `ν_k` alone.
3. **§17 severe-testing arm** — falsified if §17 feedback shows no
   measurable reduction in repeat-finding rate.
4. **§18 bold-conjecture arm** — falsified if the channel assignment
   produces no measurable divergence effect on conjecture quality.
5. **Arm independence** — falsified if the `η_int` modulator design
   produces `R_k` degradation indistinguishable from a direct-to-`R_k`
   modulator.
6. **B-Cell composition law** — falsified if a simpler aggregation
   rule predicts per-cell output with equal accuracy.
7. **Extended substrate agnosticism** — falsified if the additional
   configurations cannot produce admissibility-conformant outputs on
   frontier-difficulty tasks.

## Summary

The Addendum is appended rather than replacing any prior content. The existing *Invitation to Falsify* block and the *References* block are unchanged. The Addendum closes with an explicit set of falsifiable claims that the 2×2 factorial in Experiments 41–54 is designed to test.
