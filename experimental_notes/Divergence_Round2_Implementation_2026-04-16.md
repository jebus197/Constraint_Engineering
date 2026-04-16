# §18 Divergence Directive — Round-2 Consensus Implementation and Final Review

**Date:** 16 April 2026
**Branch:** `exp39-experimental`
**Scope:** Channel reassignment, contrast statement, sibling mandatory rejection gate, near-copy severe tier

---

## Background

The §18 divergence directive, CDSFL's bold-conjecture arm, underwent two rounds of 5-panel model confer (Gemini 3.1 Pro, Codex GPT-5.4, CC2 Opus 4.6, ChatGPT GPT-5.4, DeepSeek R1-0528) on 15-16 April 2026. Round 1 identified three axes of genuine divergence (D1: Jaccard threshold, D2: penalty tiers, D3: experimental design). Round 2 converged unanimously (5/5) on all three, plus a structural question: where in the Stage 6 math does the divergence multiplier belong?

This note documents the implementation of the round-2 consensus and its verification.

---

## Round-2 Unanimous Consensus (5/5)

### Structural question: channel assignment

The divergence modulator multiplies eta_int (the internal-novelty channel). It is forbidden from acting as a direct pre-factor on R_k, forbidden from entering q as a free factor outside eta_int, and forbidden from crediting nu_k. The effect on R_k flows exclusively through the Stage 6 decomposition:

    eta_int_modulated = m_div * eta_int
    eta_combined      = eta_int_modulated * (1 - c_ext * (1 - nu_k))
    q                 = eta_combined * d * p
    R_k(i)            = R_k(i-1) * (1 - q) / (1 - q * R_k(i-1))

This is the channel-assignment invariant that all five models converged on. The three channels (R_k for validity, nu_k for literature novelty, c_ext for search quality) are assignment-orthogonal: a divergence penalty affects R_k through eta_int, not directly.

### D1: Isomorphism metric and threshold

- Jaccard threshold stays at 0.85 as a lexical near-duplicate heuristic, not semantic equivalence.
- Every alternative now requires a mandatory contrast statement naming how it differs from the primary on the declared dimension.
- A new sibling alt-vs-alt isomorphism check is a mandatory rejection gate: when two alternatives for the same finding are lexically near-duplicate (Jaccard at or above 0.85), the later-occurring sibling is flipped inadmissible.
- Embedding backend (sentence-transformers) is a follow-up, not a blocker.

### D2: Penalty tiers

Four tiers on eta_int, renamed from "divergence penalty multiplier" to "eta_int modulator":

| Tier | Value | Trigger |
|------|-------|---------|
| Compliant | 1.00 | All gates passed (dimension, contrast, primary iso, sibling iso) |
| Soft | 0.85 | Model engaged (parsed alternative) but failed at least one gate |
| Hard | 0.70 | Model ignored the directive (no alternative, no null justification) |
| Severe | 0.60 | Near-copy (Jaccard at or above 0.98), all-isomorphic, or recidivism |

The 0.60 tier is reserved for the most egregious compliance failures.

### D3: Experimental design

2x2 factorial (feedback x divergence) is the correct design for signal isolation. Deferred to Experiment 40 planning.

---

## Implementation

### Files changed

| File | Change |
|------|--------|
| `bench/dm/_divergence.py` | Rewritten: channel-assignment orthogonality contract in module docstring; DivergenceConfig gains min_contrast_chars, near_copy_threshold, sibling_isomorphism_threshold; AlternativeRecord gains contrast_statement, sibling_max_isomorphism, admissibility_gate_passed; new parse_contrast_statement() function; new check_sibling_admissibility() function; divergence_penalty_multiplier renamed to eta_int_modulator with backward-compatible alias; near-copy 0.98 tier logic added |
| `bench/directives/universal/cdsfl_operational.md` | §18 rewritten: contrast requirement, sibling mandatory rejection gate, near-copy tier, channel-assignment invariant documented, nu_k credit prohibition explicit, Jaccard role renamed to "lexical near-duplicate heuristic" |
| `bench/cdsfl_registry/universal.toml` | [divergence] block: min_contrast_chars=20, near_copy_threshold=0.98, sibling_isomorphism_threshold=0.85 added |
| `bench/cdsfl_registry/schema.toml` | Three new schema entries for the round-2 fields |
| `bench/tests/test_divergence_directive.py` | 23 new round-2 tests: contrast parsing, sibling check, near-copy tier, eta_int_modulator alias, admissibility_gate_passed, config loading |
| `bench/verify_round2_implementation.py` | 38-check SymPy/z3 cross-verification of implementation against Stage 6 math |
| `bench/confer_divergence_round3_final.py` | 5-panel final review confer script |

### Verification

| Metric | Result |
|--------|--------|
| Divergence directive tests | 75 pass (52 legacy + 23 new), 0 fail |
| Full test suite | 935 pass, 0 fail |
| SymPy/z3 cross-check | 38/38 pass |
| ruff | Clean |
| mypy | Clean |
| Channel-assignment invariant (SymPy) | Partial R/partial m != 0 (modulator reaches R_k); eta_int=0 kills the path (multiplicative, not additive); c_ext=1 nu_k=0 kills the path (known-and-corroborated) |
| Near-copy monotone gate (z3) | No iso satisfies near_copy AND NOT isomorphic (unsat) |

### Round-3 final 5-panel review

A round-3 confer dispatched all five models in parallel to review the implemented code against the round-2 consensus. Each model received the full source code of `_divergence.py`, the updated §18 text, the SymPy/z3 verification script, and the Stage 6 math. The charge required CONVERGE or DIVERGE with specific evidence, plus a P-pass of the model's own review.

**Convergence tally: 3/5 CONVERGE (Gemini, CC2, DeepSeek), 2/5 DIVERGE (Codex, ChatGPT).**

The two diverging models identified a single blocking issue: a prose/code mismatch in the severe-tier documentation. The updated §18 text inadvertently implied the 0.60 tier fires only on near-copy (Jaccard at or above 0.98) or recidivism. The code (correctly) also fires 0.60 when ALL alternatives are cosmetically isomorphic (the original §18 double-penalty: compliance theatre is treated as null submission without justification). The prose was corrected to document all three 0.60 triggers: (a) near-copy at 0.98+, (b) recidivism, (c) all-isomorphic.

Additional findings from the panel:

| Finding | Models | Status |
|---------|--------|--------|
| Recidivism detection requires cross-round state external to _divergence.py | All 5 | Acknowledged; deferred to reference_runner.py integration |
| End-to-end channel-assignment verification requires reference_runner.py call-site inspection | Codex, ChatGPT, CC2 | Residual debt; invariant proven locally and symbolically |
| SymPy script should test nu_k=1 boundary | Gemini | Fixed — added to claim 6b |
| All-isomorphic-below-near-copy path untested | CC2 | Fixed — added to claim 6b (Jaccard 0.905, tier 0.60) |
| divergence_config_from_dict(None) returns enabled=False | ChatGPT | Intentional — safe if upstream always provides explicit config |

After prose correction and verification gap closure: **41/41 cross-checks pass, 75/75 tests pass.**

---

## What generalises

The channel-assignment principle applies beyond §18. Any future CDSFL mechanism that modulates a finding's contribution must declare which of the three orthogonal channels (R_k validity, nu_k novelty, c_ext search quality) it targets. The eta_int decomposition is the designated entry point for within-session modulation; nu_k is the designated entry point for literature-grounded modulation; w(f) lives in kappa_set, not in q_eff. Mixing channels is a structural error.

---

## What did not change

No change to the R_k recurrence. No change to the eta decomposition formula. No change to w(f) or kappa_set. No change to nu_k or c_ext computation. The round-2 implementation was a code-level operationalisation of the existing mathematical model, not a modification of it.
