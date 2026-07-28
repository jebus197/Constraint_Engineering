# Round-2 CDSFL/FFAFP Convergence — §17 Feedback + §18 Divergence Directive

**Date:** 15 April 2026, 23:50 BST
**Dispatch:** 22:45Z (parallel, ThreadPoolExecutor max_workers=5)
**Protocol:** CDSFL (Constraint-Driven Synthesis and Falsification) + FFAFP (Find, Follow, Analyse, Fix, P-pass), Stage 6 (the current mathematical framework) math as arbiter
**Logs:** `bench/logs/confer_divergence_round2_convergence/combined_20260415T224529Z.json`

---

## Panel (round 2)

| Model | Route | Time | Chars |
|---|---|---|---|
| Codex GPT-5.4 | OpenRouter | 53.3s | 9251 |
| Gemini 3.1 Pro | Google GenAI native | 56.1s | 6841 |
| ChatGPT GPT-5.4 | OpenRouter | 57.5s | 9924 |
| CC2 Opus 4.6 | Claude CLI | 151.5s | 9733 |
| DeepSeek R1-0528 | OpenRouter | 248.5s | 7849 |

Wall-time: ~4 min 10s parallel (bottlenecked by DeepSeek). All responses succeeded first-try.

---

## The round-2 charge

Round 1 surfaced three genuine divergences (Jaccard (a token-overlap similarity metric) threshold, penalty tiers, experimental design). Round 2 put Stage 6 math — R_k(i) (the iterative residual-risk self-assessment after round i) recursive form, η_combined = η_int (the internal novelty score) · (1 − c_ext · (1 − ν_k (the literature-novelty score))), continuous suppression w(f) (the continuous suppression weight for finding f), similarity backend, kappa_set (the set-level convergence metric), orthogonality C1 — as the arbiter, and asked each model to converge on a single definitive answer per divergence. Answer could be a synthesis of existing positions OR an entirely novel solution.

Binding constraints:
- **C1** — ν_k / c_ext / R_k orthogonality must be preserved
- **C2** — w(f) must NOT enter q_eff (Error 1, 12 April 2026)
- **C3** — detectability of genuine novelty must be preserved
- **C4** — scientific rigour must be preserved (FFAFP admissibility set, 0–13% empirical base-rate)

Structural question posed first: where in Stage 6 does the divergence multiplier actually belong? Six-way choice: (i) R_k pre-factor (current spec) / (ii) η_int modulator / (iii) ν_k modulator / (iv) w(f) modulator / (v) admissibility gate / (vi) combination.

---

## Unanimous convergence (5/5)

| Finding | Consensus |
|---|---|
| Multiplier is **NOT** on R_k (current spec is a category error) | **5/5** |
| Primary channel = η_int (novelty, internal) | **5/5** |
| Admissibility gate = FFAFP S_min for structural violations | **5/5** |
| **2×2 factorial** is the correct D3 answer | **5/5** |
| ν_k must NEVER be modulated by §18 (the Divergence Directive) | **5/5** explicit |
| Sibling alt-vs-alt check ship-blocker (round-1 carryover) | **5/5** |
| Rename Jaccard role to "lexical near-duplicate heuristic" | **5/5** |
| Gemini's "§18-only is invalid" self-falsified in round 2 | **5/5** (incl. Gemini) |

## Residual divergence (narrow, two axes)

**R1: Does any scalar tier survive on η_int?**
- Abolish entirely (Gemini, CC2): math self-enforces — η_int_alt = 1 − max s(alt, g), w(f) handles quality continuously
- Retain tiers on η_int (Codex, ChatGPT, DeepSeek): different tier structures (Codex 3, ChatGPT 4, DeepSeek 5)

**R2: Keep Jaccard-at-0.85 MVP or replace immediately with Stage 6 similarity backend?**
- Keep 0.85 MVP + sibling check + contrast statement (Codex, ChatGPT, CC2)
- Replace now (Gemini continuous-deflation / DeepSeek τ=0.75)

---

## The structural insight that unified the panel

Under Stage 6, §18 is generator-side enforcement. Generator-side enforcement belongs in η_int (its mathematically native channel). The round-1 spec placed it as a pre-factor on R_k — a category error because R_k measures validity (Bayesian posterior of residual risk), not novelty. An isomorphic alternative is not *false*, it is *redundant*. Penalising R_k for redundancy conflates the channels and violates C1 orthogonality.

Once the channel assignment is fixed, every downstream question resolves cleanly:

- **D1** (threshold) becomes a novelty-channel detection problem — threshold calibration matters less because the consequence of error is η_int deflation, not R_k corruption.
- **D2** (tier structure) — numbers matter less than the channel. Tiers if retained go on η_int, never R_k.
- **D3** (experimental design) — §17 (the Feedback Channel directive) acts on R_k / σ / ν, §18 acts on η_int. These are orthogonal channels with potentially nonzero interaction via q = η·d·p. Factorial design is mathematically required, not optional.

## Definitive resolutions

### Structural (load-bearing)

§18 divergence multiplier splits across three channels:
1. **FFAFP admissibility gate (binary)** — malformed blocks → inadmissible, no divergence credit. Finding itself processed at full R_k.
2. **η_int modulator (continuous)** — admissible alternatives scale η_int by m_div ∈ [0,1].
3. **w(f) in kappa_set** — isomorphic alternatives continuously suppressed by existing exponential decay. Automatic, no new code.

**R_k(i) is never touched by §18.**

### D1 — Jaccard + threshold

Ship Jaccard at 0.85 as lexical near-duplicate screen (NOT an isomorphism detector).

Mandatory additions:
- Sibling alt-vs-alt check (ship-blocker from round 1, ~10 LOC)
- Contrast-statement requirement: "changes X while holding Y fixed"
- Log (primary, alt, J_primary, J_sibling_max, m_div) for Phase 2 calibration

Phase 2 (post-Exp 40 empirical): replace Jaccard with Stage 6 similarity backend s(f1,f2) = 0.8·content_sim + 0.2·b_class. Either Gemini's continuous deflation or DeepSeek's τ=0.75 becomes empirically defensible then.

### D2 — penalty tier structure

Four tiers, **η_int-only**:

| Tier | m_div | Condition |
|---|---|---|
| 1.00 | full credit | compliant + not lexically near-duplicate |
| 0.85 | reduced | engaged but weak (borderline duplication, weak contrast, procedural miss) |
| 0.70 | heavily reduced | no meaningful engagement but parsable |
| 0.60 | minimal | extreme near-copy (J ≥ 0.98) OR recidivism |

Inadmissible under FFAFP → gates out upstream of tiers.

ChatGPT's final structure: "Gemini's gating plus Codex's evidence-strength principle, reconciled by channel separation." CC2's no-tiers position is more elegant but less interpretable — retain tiers for HIL visibility, wire to η_int only.

### D3 — experimental design

2×2 factorial, cells A/B/C/D:
- A: §17 off, §18 off (reuse Exp 36–38 baseline)
- B: §17 on, §18 off (Exp 39 / §17 main effect)
- C: §17 off, §18 on (Exp 41 / §18 main effect)
- D: §17 on, §18 on (Exp 40 / joint + interaction)

Budget-constrained fallbacks:
- B + D only → narrow claim to "marginal effect of §18 given §17" (current plan)
- B + C + D → skip A, reuse prior baseline (recommended if possible)

Per-cell: R_k trajectory, η_int distribution, w(f) distribution, kappa_set convergence, admissibility pass rate, resubmission persistence.

---

## Implementation delta (round 1 → round 2 definitive)

| Item | Round 1 plan | Round 2 definitive |
|---|---|---|
| Sibling alt-vs-alt check | Ship-blocker | Keep. Ship-blocker. |
| Jaccard threshold | 0.85 MVP with logging | Keep. 0.85, log, Phase 2 backend swap. |
| Penalty tiers on R_k | Deferred wiring | **Abolish on R_k. Move to η_int.** |
| Experimental design | Option B (B+D) | 2×2 factorial preferred. Option C (B+C+D) recommended. |
| Contrast statement requirement | Not present | **NEW. Mandatory in §18 directive.** |
| ν_k modulation by §18 | Not discussed | **EXPLICITLY FORBIDDEN.** |
| correction_source tag | CC2 proposal | Retained if Option B (B+D only) is used. |
| min_alternative_tokens = 15 | Optional | **Admissibility gate, not penalty.** |

---

## Extrapolation

### What generalises

**Mathematical frameworks disambiguate model disagreements that prose cannot.** Round 1 produced five different opinions on each divergence. Round 2 with Stage 6 math as arbiter produced unanimous structural convergence. The load-bearing move was not more deliberation but giving the panel a shared deductive instrument.

**Channel separation is a general antidote to compliance theatre.** Separate validity from novelty, route each signal to its natural channel, and the math itself distinguishes genuine alternatives (high η_int) from theatre (w(f) → w_floor). This generalises beyond CDSFL.

**Self-falsification survives cross-panel pressure when the math is shared.** Gemini reversed its round-1 position when parameter orthogonality made it indefensible. FFAFP reproducibility across vendors — not just within-model.

### Boundary conditions

- Shared training distribution across five transformer LLMs on overlapping corpora. Convergence is weak-but-positive evidence, not proof.
- Framework must be load-bearing. Ornamental equations produce convergence on prose, not derivation.
- Panel size matters. Five models surfaced the channel-reassignment insight. Two likely would not. [SPECULATIVE, testable.]

### New falsifiable questions

1. Does opportunity cost alone suffice as §18 incentive? (CC2's claim; Exp 40 cell D vs B tests it.)
2. Does channel-separated reporting prevent template convergence? (Track mean pairwise Jaccard across models across rounds.)
3. Does cell C (§18 alone) produce interpretable signal? (Tests whether Gemini's original "structurally coupled" fear was real.)
4. Does the Stage 6 arbiter generalise to future multi-model divergences under CDSFL?

---

## P-pass discipline (round 2)

Self-falsification remained active across the panel:
- **Gemini** reversed its round-1 §18-only-invalid position — cleanest cross-round self-falsification
- **CC2** identified the strongest remaining falsifier (opportunity cost may be insufficient, testable in Exp 40)
- **Codex** & **ChatGPT** addressed four falsifiers each against C1–C4
- **DeepSeek** flagged residual FN risk on τ=0.75, logged as residue

Round-2 P-pass survived all panel-internal attacks against C1–C4 after channel reassignment. Residuals are empirical (opportunity-cost sufficiency, compliance-theatre via contrast gaming), not mathematical.

---

## Three decisions pending founder approval

1. **Adopt the structural move** — §18 multiplier off R_k, onto η_int + admissibility. ~30 LOC + 8–12 tests. Recommended before Exp 40.
2. **Adopt the contrast statement requirement** — ~5 lines directive + ~20 LOC parser + 3–5 tests. Recommended before Exp 40.
3. **Experimental design** — Option C (B + C + D, reuse Exp 36–38 baseline) recommended. Option B (B + D with honest claim narrowing) if budget-constrained. Option A (full 2×2) overkill.

Phase 2 embedding backend replacement, penalty tier recalibration, and the opportunity-cost sufficiency test are deferred to Exp 40 empirical data.

---

## Files

- `bench/confer_divergence_round2_convergence.py` — round-2 dispatcher (523 lines)
- `bench/logs/confer_divergence_round2_convergence/` — per-model + combined JSON logs
- `bench/dm/_divergence.py` — target of structural move (div multiplier → η_int + admissibility)
- `bench/directives/universal/cdsfl_operational.md` §18 — contrast statement requirement to add
- `docs/MATHEMATICAL_APPENDIX.md` — Stage 6 arbiter (§1.1 R_k, §1.3 similarity, §1.4 suppression, §1.6 ν_k, §1.7 c_ext)
