# Experiment 36 — Mathematical Model Audit (Pre-Execution)

**Date:** 7 April 2026, 08:40 BST
**Status:** SCOPED AND DISCUSSED — execution pending next session
**Trigger:** Founder identified narrow-test error in churn signal verification (ρ Pearson test asked wrong question). Asked for broad mathematical model review to check for systemic "mathematical myopia."

## Context

The churn signal (Claim 7) was originally classified UNCERTAIN based on a Pearson correlation of ρ = novel/raw against round number (r=−0.31, p=0.16). The founder pointed out this was logically incoherent: the exponential decay of novel findings was CONFIRMED (R²=0.985) and raw output was observably stable, so the divergence between them IS the churn signal by definition. The narrow test measured the smoothness of a derived ratio rather than the existence of the underlying divergence.

This raised the question: does the same narrow-test pattern exist elsewhere in the mathematical framework?

## Source Document

`docs/MATHEMATICAL_APPENDIX.md` — 1081 lines, §0.1 through §8.6. Declared mathematically coherent 31 March 2026 after 8-round audit (6 models, 39 SymPy checks, all passing).

## Assessment After Full Read

The appendix is internally coherent. The algebra is sound. The reduction properties are correct. The 39 SymPy checks verified what they claimed to verify.

The problem is not internal consistency. The problem is that the appendix models components, while experiments 29–36 revealed system-level behaviours that emerge from component interactions. The appendix has no metrics for those emergent operational behaviours.

## Five Identified Gaps

### Gap 1: γ Classifies Wrong at the System Level

**What the appendix says:** §7.1 — γ > 0 means "genuine convergence — error space exhausting." γ ≈ 0 means "churn." γ < 0 means "divergence."

**What Exp 36 showed:** γ = 0.411 (firmly positive, classified as "convergence"), but the system was churning at a 17:1 dedup ratio. γ correctly measures that the *novel discovery space* is decelerating. It does NOT measure whether the *operational system* is churning, because it cannot see raw output volume.

**Root cause:** γ is computed from cumulative novel findings only. The raw-to-novel divergence — the churn signal — is invisible to γ. The ITC keeps restarting models, raw stays high, novel collapses, and γ reports "convergence" while the operational reality is churn.

**This is the same narrow-component error as the churn signal test:** a single derived quantity (γ) is used to classify the whole system, when the classification depends on the interaction between two quantities (novel rate AND raw rate) that γ only sees one of.

**Proposed test:** Compute γ from Exp 29–36 data. For each experiment, classify system state using γ alone vs using (γ, ρ) jointly. Check whether ρ changes the classification in any experiment. If it does, γ alone is insufficient.

### Gap 2: ρ (novel/raw) Fills a Real Hole But Isn't Formalised

**What the appendix has:** §7.9 capability fingerprint (D_decay, v̄, A, C). §7.1 Duane NHPP for discovery rate. §7.3 Cognitive Yield Y(t) = N(t) · H̄(t). None of these capture the raw-to-novel pipeline.

**What Exp 36 needed:** A metric for discovery efficiency — what fraction of operational output is genuinely novel. We invented ρ = novel/raw during the experiment because the existing framework had no way to express this.

**The gap is structural:** The appendix assumes that the finding pipeline is: models produce findings → findings are deduplicated → deduplicated findings are verified. The raw-to-canonical ratio is treated as a parsing/format problem (φ_fmt in §2). But the real problem isn't format yield — it's that models genuinely produce redundant findings that pass format validation but fail semantic deduplication. φ_fmt captures "parser can't read it." ρ captures "parser reads it fine, but it's the same bug for the 17th time."

**Proposed test:** Compute ρ per round and per model for Exp 29, 30, 34, 35, 36. Fit ρ decay curves. Check whether ρ adds predictive power beyond γ for convergence gate decisions.

### Gap 3: ITC Feedback Loop Not Modelled

**What the appendix has:** §7.1 error re-injection ν · Δ_{n−1} (new defects introduced by fixes). §7.12 FFF contraction condition ε_n < D_n · (1 − ν).

**What Exp 36 showed:** The ITC's restart_fresh creates a different kind of re-injection — not new defects, but rediscoveries of known defects from fresh model contexts. This is stochastic, model-dependent (DeepSeek churns gradually at 55.6% of extension output; Gemini spikes episodically at 0–16 per round), and context-dependent (restart_fresh temporarily resets context, but accumulated registry re-inflates immediately).

**The gap:** The appendix's ν is a constant re-injection rate for new defects from fixes. The ITC-driven re-injection is: (a) not from fixes but from context resets, (b) not constant but varying per model per round, (c) producing rediscoveries, not new defects. These are structurally different phenomena.

**Proposed test:** Estimate effective ν per model per round from Exp 36 data. Test whether the constant-ν model fits the data or whether a per-model time-varying ν is needed. Specifically: after each restart_fresh event, measure the novelty rate of the subsequent round's output from that model.

### Gap 4: f_del and φ_fmt Degrade With Context Inflation

**What the appendix says:** f_del(i) and φ_fmt(i) are per-model constants. f_del ≈ 0.8 for DeepSeek at 32K tokens (§2, calibration from Exp 15). φ = 0 for DeepSeek format divergence (§2).

**What Exp 36 showed:** Context grew from 95% of 200K budget (R3) to 406% (R22, 811K characters). Both f_del and φ_fmt are functions of context size, not constants. As context inflates, delivery and format quality degrade, the ITC detects the performance drop and classifies it as DEGRADATION, fires restart_fresh, and feeds the feedback loop (Gap 3).

**The gap is about temporal degradation:** The appendix correctly models inter-model diversity (different models have different f_del, φ_fmt, fingerprints). It does not model that these per-model parameters change over time as context grows. The diversity means they change at different RATES, which compounds the problem, but the fundamental issue is that they change at all.

**Proposed test:** From Exp 36 pacing signals, extract context size per round. Correlate context size with per-model output quality metrics (novel rate, format errors, malformed findings). Test whether f_del(i, context_size) is a better predictor than constant f_del(i).

### Gap 5: Runner Convergence Gate ≠ Appendix Termination Criteria

**What the appendix specifies:** §7.4 — stop_valid(t) = (V̂_remaining(t) < ε) ∧ ¬ascending_abstraction(t). This is a value-based criterion with an ascending-abstraction guard.

**What the runners implement:** 5-condition conjunction: round ≥ 12, open_ch stable, recent_novel ≤ 2, contested == 0, gamma_passed. This is a state-based criterion with no value estimation.

**The gap:** These are different frameworks that haven't been reconciled. The deep analysis showed 3 of the runner's 5 conditions are non-contributing in the convergence-relevant window (R12+). We can't tell whether the appendix's criteria would have done better because V̂ and H̄ aren't implemented.

**Proposed test:** Retrospectively compute V̂_remaining and ascending_abstraction from Exp 36 data. Compare: at what round would the appendix's criterion have fired vs when the runner's gate fired (never, in this case). If the appendix's criterion would have terminated earlier and correctly, that's evidence the runner should adopt it.

## Additional Questions to Test

- **Ascending abstraction (§7.3):** Has dH̄/dt > 0 while dλ/dt < 0 ever been observed in any experiment? If not, is it a real phenomenon or a theoretical construct that doesn't manifest in multi-model code review?
- **Ising correlation (§0.1):** Is the ψ_ij coupling testable with available data? The deep analysis (DA-10) noted that cross-model agreement data isn't collected. Without per-model verdict matrices, the Ising model may be unfalsifiable with current telemetry.

## Proposed Execution Plan

1. **Data collection:** Extract round-by-round data from Exp 29, 30, 34, 35, 36 reports (novel, raw, per-model counts, context size, ITC interventions, gamma, convergence gate state).
2. **Gap 1 test:** γ classification vs (γ, ρ) joint classification across all 5 experiments.
3. **Gap 2 test:** ρ decay curves per experiment. Predictive power analysis.
4. **Gap 3 test:** Per-model post-restart novelty rates. Effective ν estimation.
5. **Gap 4 test:** Context size vs output quality correlation.
6. **Gap 5 test:** Retrospective V̂ and ascending_abstraction computation.
7. **Tools:** NumPy/SciPy for statistical tests and curve fitting. SymPy for any new formal quantities (ρ formalisation, f_del(i,c) functional form). Wolfram for analytical verification of closed-form expressions.

## Founder Discussion Notes

- Founder confirmed Gap 4 connects to diversity (different models degrade at different rates). CC clarified: the appendix already models inter-model diversity through per-model parameters. The gap is temporal degradation — those parameters aren't constants, they're functions of context size. Diversity determines the RATE of degradation, not the existence of degradation.
- Founder requested: discuss findings before formalising into appendix. No appendix changes without explicit approval.
- Founder flagged: don't repeat the narrow-test mistake. Test broadly and deeply. Decompose compound claims before testing.
