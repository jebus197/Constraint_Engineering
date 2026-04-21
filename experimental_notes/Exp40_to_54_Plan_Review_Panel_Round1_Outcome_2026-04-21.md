# Exp 40-54 Consolidated Plan — Panel Review Round 1 Outcome

**Date:** 2026-04-21 11:14-11:17 BST (dispatch 2026-04-21T10:14:09Z)
**Plan under review:** `experimental_notes/Exp40_to_54_Consolidated_Plan_2026-04-21.md` (19,856 chars)
**Dispatch script:** `bench/confer_exp40to54_consolidated_plan_review_2026-04-21.py`
**Logs:** `bench/logs/confer_exp40to54_consolidated_plan_review_2026-04-21/`

## Configuration

- **Topology:** Star (each of 5 models talks only to CC1; no cross-model leakage).
- **Models:** Gemini 3.1 Pro, Codex GPT-5.4, CC2 (Opus 4.6), ChatGPT GPT-5.4, DeepSeek R1-0528.
- **Prompt size:** 40,722 chars (system 11,821 + user 28,901, including full plan).
- **System prompt:** `bench/directives/universal/cdsfl_core_formal.md` (full CDSFL directive).
- **Framing anchors:** `bench/exp40_configs/40_gate.json` pass_condition + Stage 6 orthogonality (`R_k` / `nu_k` / `c_ext` independent).
- **Compelled convergence:** Single position per question, no menu-for-founder.
- **Scope guardrail:** Exp 40-54 arc only; post-Exp-54 proposals ignored.
- **Round budget:** 1, unless genuine split surfaces.

## Per-model timing and token count

| Model | Response chars | Time (s) |
|-------|----------------|----------|
| Codex GPT-5.4 | 9,532 | 55.7 |
| ChatGPT GPT-5.4 | 10,404 | 59.2 |
| Gemini 3.1 Pro | 8,019 | 62.3 |
| DeepSeek R1 | 5,558 | 171.6 |
| CC2 Opus 4.6 | 11,073 | 227.0 |

All five models answered under CDSFL + FFAFP. No model drifted back to the refuted "v1 preservation" framing.

---

## Per-question synthesis

### RQ1 — Unaddressed fix against 40_gate.json

| Model | Position |
|-------|----------|
| Gemini | NO — F1-F4 sufficient |
| Codex | YES — add live-path preflight for §17 admissibility parser |
| CC2 | NO — F1-F4 sufficient (codebase-grounded analysis citing line numbers) |
| ChatGPT | NO — F1-F4 sufficient |
| DeepSeek | YES — §17 `[VERIFY:current]` flag handling + §18 cosmetic-rewrite suppression |

**Vote: 3 NO / 2 YES.**

**Consensus: NO.** F1-F4 are sufficient for the 40_gate.json pass_condition. CC2's analysis is the most codebase-grounded (confirms that admissibility/divergence signal generation is independent of F2 wrapper wiring, and that the γ-alt convergence path via `_check_gamma_alt_convergence` at `reference_runner_v2.py:1064` reads thresholds already present in 40_gate.json).

**Fold-in (downgraded from F item to Gate C preflight):** Add Codex's proposed check to Gate C — a live-path preflight for the §17 admissibility parser on `bench/dm/_feedback.py`, verifying that the live parsing behaviour matches offline-tested behaviour. This is not a new fix in F1-F4; it is a pre-launch verification step. DeepSeek's proposed fixes (epistemic flag handling, cosmetic rewrite suppression) are speculative without evidence of current misclassification and are not folded in at this round.

### RQ2 — Cross-experiment interaction missed

| Model | Position | Interaction named |
|-------|----------|-------------------|
| Gemini | YES | Exp 46 (§18 target) alters modulation engine, invalidating Exp 41-45 calibrations |
| Codex | YES | Treatment-conditioned tier-calibration drift crossing 40-49 into 54 |
| CC2 | NO | Math↔stats overlap is subcase of routing imbalance, caught at Exp 44/49 integration |
| ChatGPT | YES | Threshold-calibration drift across 40-53 under co-live §17+§18, reused in Exp 54 B/C cells |
| DeepSeek | NO | S_k–Microglia interaction (different concern) already gated by Exp 42 |

**Vote: 3 YES / 2 NO.**

**Consensus: YES.** Three models converge on the same mechanism: tier/threshold calibration drift learned under co-live §17+§18 during Exp 40-53, then reused when evaluating Exp 54 single-channel Cells B and C. CC2's argument that Exp 49 catches this is partially correct — Exp 49 surfaces specialist-specialist inconsistency, but does not freeze the thresholds. The specific distortion is that severity thresholds learned under combined treatment are applied to single-treatment cells at Exp 54, contaminating main-effect attribution.

**Fold-in:** Add pre-Exp-54 threshold-freeze requirement. Before Exp 54 launches, freeze admissibility, severity, and tier thresholds; apply identical frozen thresholds across all four cells A/B/C/D. Add this as a new item on the Exp 54 Gate C checklist.

### RQ3 — Exp 54 factorial attribution sufficiency

| Model | Position | Key reservation |
|-------|----------|-----------------|
| Gemini | NO | Cell A confounded by 14 experiments of runner evolution; propose fresh Cell A run at Exp 54 codebase |
| Codex | YES (conditional) | Two-way ANOVA sufficient IF archive comparability holds |
| CC2 | YES (conditional) | Two-way ANOVA on round-level metrics; requires Gate C Cell A integrity check |
| ChatGPT | YES (conditional) | Two-way GLM with interaction; frozen scoring rules across cells |
| DeepSeek | YES | Linear mixed model; if Cell A corrupt, use Cell B/C early rounds as proxy baseline |

**Vote: 4 YES conditional / 1 NO.**

**Consensus: YES (conditional).** The 2×2 factorial design is mathematically identifiable for §17 main effect, §18 main effect, and §17×§18 interaction via two-way ANOVA or equivalent GLM. Standard contrasts: §17 main = `(B + D)/2 − (A + C)/2`; §18 main = `(C + D)/2 − (A + B)/2`; interaction = `(D − C) − (B − A)`.

Gemini's NO raises a substantive concern that the other four models under-weight: Cell A's archived v1 data confounds §17/§18 absence with ALL runner evolution, not just directive absence. The four YES-conditional votes treat "archive integrity" as sufficient, but Gemini argues integrity is not the issue — confound-by-runner-version is.

**Fold-in (strengthen Gate C for Exp 54 with three layers):**

1. **Primary:** Cell A archive integrity check — γ trajectory from Exp 36-38 archive reproduces within tolerance.
2. **Fallback 1:** If integrity fails, Gemini's proposal — fresh run at Exp 54 codebase with §17 and §18 both off. This replaces archived Cell A.
3. **Fallback 2:** If both above fail, DeepSeek's proposal — sensitivity analysis bounding β₁, β₂ via Cell B/C early-round data as ad-hoc baseline; report interaction-only and flag main effects as confounded.

Also fold in the frozen-thresholds requirement from RQ2, applied across all four cells.

### RQ4 — Shadow-promotion-now offsetting risk

| Model | Position | Bounding condition |
|-------|----------|---------------------|
| Gemini | POLICY SAFE | (none; policy affirmed unconditionally) |
| Codex | CONDITIONALLY SAFE | Promoted channels auditable against Stage 6 orthogonality; F3 debug assertion catches hidden coupling in q |
| CC2 | CONDITIONALLY SAFE | F2's 1e-9 regression gate + Exp 49 cross-domain recalibration checkpoint |
| ChatGPT | CONDITIONALLY SAFE | Promoted component must be pipeline-neutral w.r.t. pass_condition before live |
| DeepSeek | POLICY SAFE | Noise contained to logs; calibration uses late-session data |

**Vote: 2 SAFE / 3 CONDITIONALLY SAFE.**

**Consensus: POLICY CONDITIONALLY SAFE.** Three models converge on a single bounding condition: each promoted component must pass a non-distortion check against the 40_gate.json pass_condition before going live — specifically, must not silently alter the "3 consecutive rounds with 0 novel CRITICAL findings" clause through unintended channel coupling.

**Fold-in:** Update `feedback_shadow_promotion_now.md` memory (and the plan's policy section) with the bounding condition. F2 satisfies the bounding condition via its 1e-9 regression gate. K/L/M shadow specialists will need equivalent non-distortion evidence before their post-Exp-53 live promotion.

### RQ5 — Ordering of Exp 41-53

| Model | Position | Proposed change |
|-------|----------|-----------------|
| Gemini | YES | Move Exp 46 (§18 target) to Exp 41 position |
| Codex | NO | Current ordering optimal |
| CC2 | NO | Current ordering optimal |
| ChatGPT | YES | Move Exp 48 (info) before Exp 46 (CS/§18) |
| DeepSeek | YES | Move Exp 45 (stats) immediately after Exp 41 |

**Vote: 2 NO / 3 YES (with three incompatible proposals).**

**Consensus: NO material improvement available.** Three YES votes diverge on the specific reordering. Gemini proposes §18 first; ChatGPT proposes evidence before divergence; DeepSeek proposes stats before composition (which does not actually tighten any stated hard dependency, because Exp 44 depends on 41/42/43, not 45). Codex and CC2 (the two most detailed codebase-grounded analyses) both defend the current ordering as dependency-optimal.

**Fold-in (light — document as carried risk only):** Retain current ordering. Add a note to the plan's §4 per-experiment path: three alternative orderings were proposed in panel review and are carried forward as post-Exp-49 review topics (not pre-launch gate items). Specifically, if the Exp 49 cross-domain synthesis test surfaces specialist tier inconsistencies, revisit ChatGPT's proposal (swap 46 and 48) before committing to the original Exp 50 sequence.

### RQ6 — Target-article candidates for Exp 47, 51, 52, 53

| Model | Bio (47) | Phys (51) | Chem (52) | Eng (53) | Preferred fallback |
|-------|----------|-----------|-----------|----------|---------------------|
| Gemini | NO native | NO native | NO native | NO native | Synthesise minimal modules |
| Codex | NO native | NO native | NO native | NO native | Adapter layer over external content |
| CC2 | NO native | NO native | NO native | NO native | Synthesise (rejects adapter) |
| ChatGPT | NO native | NO native | NO native | NO native | Synthesise (rejects adapter) |
| DeepSeek | NO native | YES (`composer.py` — uses units) | NO native | NO native | Synthesise for 47/52/53 |

**Vote: 5 NO native for bio/chem/eng; 4 NO / 1 YES for physics (DeepSeek's `composer.py` candidate). For fallback method: 3 synthesise / 1 adapter / 1 synthesise with physics exception.**

**Consensus: Synthesise minimal native modules for Exp 47, 52, 53. Verify `composer.py` content for Exp 51 before committing.**

The three models favouring synthesis over adapter converge on the orthogonality argument: an adapter layer adds a failure surface between external content and the runner's parsing expectations, blurring search-quality (`c_ext`) with target-module validity. Codex's adapter recommendation is the minority position; the stronger argument under Stage 6 orthogonality favours synthesis.

**Fold-in:**
- Commit Exp 47, 52, 53 to minimal-native-module synthesis (15-25K char target articles, purpose-built).
- For Exp 51, verify DeepSeek's claim that `bench/cdsfl_registry/composer.py` contains physics-relevant dimensional content of sufficient density. If yes, use as Exp 51 target. If no, synthesise.
- Treat the synthesised modules as Exp 40 post-mortem action items (pre-Exp-47 completion), not as Exp 40 launch blockers.

---

## Summary of fold-ins applied to the consolidated plan

1. **New Gate C preflight (Exp 40 launch):** live-path preflight for §17 admissibility parser on `bench/dm/_feedback.py`.
2. **New Exp 54 Gate C item:** freeze admissibility, severity, and tier thresholds before factorial runs; apply identically across Cells A/B/C/D.
3. **Strengthened Exp 54 Gate C (Cell A):** three-layer integrity strategy — archive integrity check, fresh-run fallback, sensitivity-analysis fallback.
4. **Updated policy statement:** shadow-promotion-now is conditionally safe; each promoted component requires non-distortion evidence against pass_condition before live activation.
5. **Target-article commitment:** Exp 47/52/53 use synthesised minimal native modules; Exp 51 conditional on `composer.py` physics content verification.

## Items NOT folded in

1. **RQ1 DeepSeek additions** (§17 `[VERIFY:current]` handling, §18 cosmetic rewrite suppression) — speculative without evidence of current misclassification; not a blocker.
2. **RQ5 reordering proposals** — three incompatible YES votes; retain current ordering, document alternatives as post-Exp-49 review material.

## Divergences carried forward

- RQ3 Gemini dissent (Cell A confounded by runner evolution, not merely corrupted): folded in as fallback layer. If archive integrity holds at Gate C, the main path proceeds; if it fails, Gemini's fresh-run proposal takes precedence.
- RQ5 incompatible reordering proposals: documented as watch-items for Exp 49 post-mortem.

## Panel verdict

The plan is broadly viable under corrected framing (40_gate.json + Stage 6 orthogonality), with five material fold-ins and two documented-only items. No model drifted back to the refuted v1-preservation framing. A second round is not required.
