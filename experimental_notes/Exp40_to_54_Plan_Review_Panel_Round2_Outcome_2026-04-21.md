# Exp 40-54 Consolidated Plan — Panel Review Round 2 Outcome

**Date:** 2026-04-21 17:32-17:34 BST (dispatch 2026-04-21T16:32:49Z)
**Plan under review:** `experimental_notes/Exp40_to_54_Consolidated_Plan_2026-04-21.md`
**Round 1 outcome:** `experimental_notes/Exp40_to_54_Plan_Review_Panel_Round1_Outcome_2026-04-21.md`
**Dispatch script:** `bench/confer_exp40to54_plan_review_round2_2026-04-21.py`
**Logs:** `bench/logs/confer_exp40to54_plan_review_round2_2026-04-21/`

## Configuration

- **Topology:** Star (each of 5 models talks only to CC1; no cross-model leakage).
- **Models:** Gemini 3.1 Pro, Codex GPT-5.4, CC2 (Opus 4.6), ChatGPT GPT-5.4, DeepSeek R1-0528.
- **Prompt size:** 40,881 chars (system 11,821 + user 29,060, including full Round 1 outcome).
- **System prompt:** `bench/directives/universal/cdsfl_core_formal.md` (full CDSFL directive).
- **Framing corrections applied:** cell-type ≠ tool correction (Correction B), 15-experiment arc correction (Correction A), compelled-convergence no-menu-for-hub (Correction C).

## Dispatch artefacts

Codex and ChatGPT (both via OpenRouter) disclaimed model-specific Round 1 identity — the dispatch script did not include per-model persona framing, so they answered as convergence assessors rather than as named panel members. Gemini adopted a "DeepSeek R1-0528" persona. CC2 answered from the hub perspective. DeepSeek answered as itself. Positions are evaluated by dispatch label, not claimed persona. All five produced valid, argument-engaged responses.

## Per-model timing and token count

| Model | Response chars | Time (s) |
|-------|----------------|----------|
| Codex GPT-5.4 | 5,577 | 31.3 |
| ChatGPT GPT-5.4 | 6,034 | 34.3 |
| CC2 Opus 4.6 | 6,151 | 57.1 |
| Gemini 3.1 Pro | 4,365 | 58.2 |
| DeepSeek R1 | 4,085 | 83.7 |

---

## Per-RQ convergence results

### RQ1 — Unaddressed fix against 40_gate.json

| Model | Round 1 | Round 2 | Movement |
|-------|---------|---------|----------|
| Gemini | NO | YIELD to Codex YES (Gate C preflight) | Shifted to preflight |
| Codex | YES (preflight) | YIELD to Codex YES (Gate C preflight) | Held as Gate C step |
| CC2 | NO | YIELD to NO (F1-F4 sufficient) + retain Codex preflight as Gate C | Clarified |
| ChatGPT | NO | YIELD to Codex YES (Gate C preflight) | Shifted to preflight |
| DeepSeek | YES (flag handling) | YIELD to NO (F1-F4 sufficient) | Yielded |

**✅ CONVERGED:** F1-F4 are sufficient for the 40_gate.json pass_condition. No new F-item is required. Codex's live-path admissibility-parser preflight on `bench/dm/_feedback.py` is retained as a Gate C pre-launch verification step (not an F-item). DeepSeek's Round 1 proposals (epistemic flag handling, cosmetic-rewrite suppression) are withdrawn as speculative without evidence of current misclassification.

### RQ2 — Cross-experiment interaction missed

| Model | Round 1 | Round 2 | Movement |
|-------|---------|---------|----------|
| Gemini | YES | YIELD to YES (threshold-freeze) | Held |
| Codex | YES | YIELD to YES (threshold-freeze) | Held |
| CC2 | NO | YIELD to YES (threshold-freeze) | Yielded |
| ChatGPT | YES | YIELD to YES (threshold-freeze) | Held |
| DeepSeek | NO | REFUTE NO, hold YES (threshold-freeze) | Yielded |

**✅ CONVERGED (5/5 YES):** Pre-Exp-54 threshold-freeze is required. CC2 yielded on the specific ground that Exp 44/Exp 49 detect specialist-specialist inconsistency but do not freeze the learned thresholds — detection and prevention are different guarantees. DeepSeek yielded on the ground that the S_k–Microglia interaction was a different concern that did not address the threshold-drift mechanism.

**Action:** Freeze admissibility, severity, and tier thresholds before Exp 54 factorial runs. Apply identical frozen thresholds across all four cells A/B/C/D.

### RQ3 — Exp 54 factorial attribution sufficiency

| Model | Round 1 | Round 2 | Movement |
|-------|---------|---------|----------|
| Gemini | NO (fresh run) | YIELD to Gemini NO (fresh run) | Held (via persona) |
| Codex | YES conditional | YIELD to YES-conditional (expanded integrity) | Held with refinement |
| CC2 | YES conditional | YIELD to YES-conditional (expanded integrity) | Held with refinement |
| ChatGPT | YES conditional | YIELD to Gemini NO (fresh run) | Yielded |
| DeepSeek | YES conditional | YIELD to Gemini NO (fresh run) | Yielded |

**RESIDUAL SPLIT: 3 Gemini-NO / 2 YES-conditional.**

- **Gemini-NO position (3 models: ChatGPT, Gemini, DeepSeek):** Fresh Cell A run at Exp 54 codebase is required unconditionally. Archive integrity ≠ version-confound immunity. Cell A's archived v1 data intrinsically embeds 14 experiments of runner evolution.
- **YES-conditional position (2 models: Codex, CC2):** Expand "archive integrity" to explicitly include runner-version confound testing (re-run Cell A scoring at the Exp 54 codebase with §17+§18 both off and compare trajectories against archive). If the test fails, Gemini's fresh-run proposal activates as fallback. The conditional path is strictly more informative: it tests the confound rather than assuming it.

**Assessment (hub, non-synthesising):** The split is narrow. Both positions agree that runner-version confound is a real concern and that a fresh Cell A run may be needed. They disagree on whether to bother testing whether the archived data is usable first (Codex/CC2) or to skip straight to a fresh run (majority). This is an operational scheduling question, not a methodological disagreement. The majority position (fresh run unconditionally) is the conservative choice.

**Declared divergence for Round 3 if needed:** YES-conditional vs Gemini-NO on whether to attempt archive-version comparison before committing to a fresh Cell A run.

### RQ4 — Shadow-promotion-now offsetting risk

| Model | Round 1 | Round 2 | Movement |
|-------|---------|---------|----------|
| Gemini | POLICY SAFE | YIELD to CONDITIONALLY SAFE | Yielded |
| Codex | CONDITIONALLY SAFE | YIELD to CONDITIONALLY SAFE | Held |
| CC2 | CONDITIONALLY SAFE | YIELD to CONDITIONALLY SAFE | Held |
| ChatGPT | CONDITIONALLY SAFE | YIELD to CONDITIONALLY SAFE | Held |
| DeepSeek | POLICY SAFE | REFUTE POLICY SAFE, hold CONDITIONALLY SAFE | Yielded |

**✅ CONVERGED (5/5 CONDITIONALLY SAFE):** Shadow-promotion-now is safe subject to a non-distortion check against the 40_gate.json pass_condition for each promoted component. The unconditional SAFE position was refuted by the specific counterexample: an activated component could silently alter the "3 consecutive rounds with 0 novel CRITICAL findings" clause through unintended channel coupling. The non-distortion check is practically definable using existing shadow-audit logging: compare pass_condition evaluation with and without the promoted component active.

**Action:** Update `feedback_shadow_promotion_now.md` memory and the plan's policy section with the bounding condition. F2 satisfies the bounding condition via its 1e-9 regression gate.

### RQ5 — Ordering of Exp 41-53

| Model | Round 1 | Round 2 | Movement |
|-------|---------|---------|----------|
| Gemini | YES (46 first) | YIELD to NO (current ordering) | Yielded |
| Codex | NO | YIELD to NO (current ordering) | Held |
| CC2 | NO | REFUTE YES proposals (hold NO) | Held |
| ChatGPT | YES (swap 46/48) | YIELD to NO (current ordering) | Yielded |
| DeepSeek | YES (45 after 41) | REFUTE YES proposals (hold NO) | Yielded |

**✅ CONVERGED (5/5 NO):** Retain current ordering. All three YES proposers yielded. The three mutually incompatible reordering proposals did not converge on a single alternative, and none was shown to tighten stated hard dependencies. Codex and CC2's dependency-optimal argument (Exp 50 requires Ouroboros fix; Exp 49 requires Exp 41/45/46; Exp 44 requires Exp 41/42/43) is accepted as the binding rationale.

### RQ6 — Target-article candidates for Exp 47, 51, 52, 53

#### (a) Exp 51 physics — composer.py as target

| Model | Round 1 | Round 2 | Movement |
|-------|---------|---------|----------|
| Gemini | NO native | YIELD to NO native | Held |
| Codex | NO native | YIELD to NO native | Held |
| CC2 | NO native | REFUTE DeepSeek YES (synthesise) | Held |
| ChatGPT | NO native | YIELD to NO native | Held |
| DeepSeek | YES (composer.py) | REFUTE own YES (synthesise) | Yielded |

**✅ CONVERGED (5/5 NO native):** `bench/cdsfl_registry/composer.py` does not contain physics-relevant dimensional content of sufficient density. DeepSeek withdrew the claim, noting that the file handles framework routing and composition, not physics reasoning. Synthesise a minimal native physics target article for Exp 51.

#### (b) Fallback method for Exp 47, 52, 53

| Model | Round 1 | Round 2 | Movement |
|-------|---------|---------|----------|
| Gemini | Synthesise | REFUTE adapter | Held |
| Codex | Adapter | YIELD to synthesise | Yielded |
| CC2 | Synthesise | YIELD to synthesise | Held |
| ChatGPT | Synthesise | YIELD to synthesise | Held |
| DeepSeek | Synthesise | YIELD to synthesise | Held |

**✅ CONVERGED (5/5 synthesise):** Synthesise minimal native modules for all four domain target articles (Exp 47 biology, Exp 51 physics, Exp 52 chemistry, Exp 53 engineering). Codex yielded on the orthogonality argument: an adapter layer introduces parsing variance that conflates `c_ext` (search quality) with target-module validity, violating Stage 6 orthogonality.

---

## Convergence summary

| RQ | Round 1 split | Round 2 outcome | Status |
|----|---------------|-----------------|--------|
| RQ1 | 3 NO / 2 YES | F1-F4 sufficient + Gate C preflight | ✅ Converged |
| RQ2 | 3 YES / 2 NO | YES — threshold-freeze required | ✅ Converged (5/5) |
| RQ3 | 4 YES-cond / 1 NO | 3 Gemini-NO / 2 YES-conditional | ⚠️ Residual split |
| RQ4 | 2 SAFE / 3 COND-SAFE | CONDITIONALLY SAFE | ✅ Converged (5/5) |
| RQ5 | 2 NO / 3 YES (incompatible) | NO — retain current ordering | ✅ Converged (5/5) |
| RQ6a | 4 NO / 1 YES (physics) | NO native — synthesise all four | ✅ Converged (5/5) |
| RQ6b | 3 synth / 1 adapter / 1 mixed | Synthesise minimal native modules | ✅ Converged (5/5) |

## Fold-ins from Round 2

Round 1 fold-ins are confirmed. Round 2 adds or modifies:

1. **RQ1 (confirmed):** Gate C preflight for §17 admissibility parser on `bench/dm/_feedback.py`. Not an F-item.
2. **RQ2 (confirmed, strengthened):** Pre-Exp-54 threshold-freeze now has full 5/5 backing.
3. **RQ3 (narrowed):** The residual split is operational (test archive first vs. skip to fresh run), not methodological. Both sides agree runner-version confound is real and a fresh run may be needed. If Round 3 is called, this is the only item.
4. **RQ4 (confirmed, strengthened):** CONDITIONALLY SAFE now has full 5/5 backing. Non-distortion check is defined: compare pass_condition evaluation with/without promoted component using shadow-audit logs.
5. **RQ5 (confirmed):** Current ordering retained with full 5/5 backing. All three alternative proposals withdrawn.
6. **RQ6 (confirmed):** Synthesise all four domain target articles. DeepSeek withdrew composer.py physics claim. Codex withdrew adapter proposal.

## Round 3 required?

One residual split on RQ3 (3-2, narrow). The disagreement is not about whether runner-version confound matters (all agree it does) but about whether to verify archive usability before committing to a fresh Cell A run. This can be resolved by the founder without a Round 3 panel dispatch — it is an operational decision, not a technical disagreement.

**Recommendation:** Founder decides RQ3. If the Exp 36-38 archived Cell A data is expensive to reproduce (compute, time), the conditional path (test first, fresh-run fallback) is the efficient choice. If a fresh run is cheap, the unconditional path avoids the integrity-check overhead.
