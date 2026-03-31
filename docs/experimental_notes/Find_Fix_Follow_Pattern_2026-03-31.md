# Find-Fix-Follow Pattern Analysis

**Date:** 31 March 2026
**Source:** Founder's informal Gemini interaction (17-page exported conversation)
**Context:** Founder asked CC to analyse the interaction pattern that led to several
significant project discoveries, and assess whether CDSFL captures it.

## The Pattern

A three-step intra-model cycle that produces scope expansion:

1. **Find:** Model identifies an issue
2. **Fix:** Model is required to propose a specific resolution
3. **Follow:** Model examines what the resolution implies for the rest of the model

This cycle repeats within a single model's turn. Each fix opens new analytical
territory. The cumulative effect is that scope expands with depth — the model
discovers things it would never have found in a single-pass review.

## Evidence from the Gemini Conversation

Seven iterations of the cycle produced five coupled mathematical operators:
- **Duane Intensity (λ):** Discovery rate (from finding: static decay model fails)
- **Mayo Severity (V):** Test strength (from finding: need to formalise p-pass strength)
- **KL Divergence (IG):** HIL impact measurement (from finding: framing bias = manifold collapse)
- **Seeded Sensitivity (S_H):** Calibration (from finding: flat decay is ambiguous)
- **NMI (δ):** Adversarial independence audit (from finding: substrate bullying risk)

Each operator emerged from the fix of a preceding finding. None would have been
discovered in a single-pass review.

## Founder's Interaction Constraints

All constraints are process-directed, never content-directed:
- "Don't churn" → eliminates repetition
- "Check your workings" → demands self-verification
- "Avoid pseudomaths" → demands rigour
- "Think very hard" → demands depth
- "If no further work is required, simply say so" → prevents false discovery

Content emerges from process. This is the CDSFL philosophy at a finer grain than
our current round structure captures.

## Gap in Current CDSFL Model

| What we have | What it provides |
|---|---|
| Inter-model confer rounds | Breadth + adversarial rigour |
| P-pass | Self-falsification (accuracy) |
| Convergence detection | Stopping criterion |
| Tight math/problem box | Output constraint |

| What we lack | What it would provide |
|---|---|
| Resolution obligation within model's turn | Depth + scope expansion |
| Consequence analysis of own fixes | Cross-section issue discovery |
| Intra-model iterative deepening | Reduced rounds to convergence |

## Proposed Addition

Change round instructions from:
> "Identify issues in this mathematical model"

To:
> "Identify issues, propose a specific fix for each, and examine what your fix
> implies for the rest of the model"

This is an output format constraint, not a structural change. The fix is proposed,
not applied — it still goes through confer review.

## Evidence from Coherence Audit

Round 6 partially implemented this. Gemini was told to produce exact replacement
text for all outstanding issues. That single round resolved all 5 items. Earlier
rounds (findings-only) required multiple iterations for the same conclusions.

## Falsifiable Predictions

If resolution-and-consequence obligation is added to CDSFL rounds:
1. Higher finding severity per round (measurable from existing telemetry)
2. Fewer rounds to convergence (measurable from round counts)
3. More cross-section issues discovered (measurable from finding classifications)

## Risk

Models may produce poor fixes that contaminate subsequent rounds. Mitigated by:
the fix is proposed, not applied; confer cycle still reviews; SymPy verifies claims.

The substrate ceiling (identified by Gemini in the same conversation): the cycle
amplifies model capability but cannot create it. A model that lacks domain
reasoning will produce increasingly elaborate wrong fixes. Multi-model review +
SymPy verification provides the defence.

## Additional Items from Gemini Conversation

Two constructs warrant evaluation against existing mechanisms:
- **Seeded Sensitivity (S_H):** Inject known defects to calibrate detection power.
  Compare with existing immune layer detection. If S_H drops as rounds progress,
  models are going blind.
- **NMI Sycophancy Trigger:** S_sync = (1-δ̄)·(1-S_H). Distinguishes genuine
  consensus (low diversity + high seeded recall) from sycophantic collapse (low
  diversity + low seeded recall). Compare with existing S_sync in §7.5.

## Test Plan

Include as condition in Experiment 19 or as variant in Bench Run 2.
