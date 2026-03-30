# Experiment 16 Collation Report

**Date:** 30 March 2026
**Collator:** CC1, Opus 4.6
**Test article:** Experiment 17 plan — the immune response layer validation plan
**Result:** All 5 models succeeded: CC2, Codex, ChatGPT, Gemini, and DeepSeek.

---

## Response Summary

| Model | Characters | Time (s) | Findings | Open Q Responses | Improvements |
|-------|-----------|----------|----------|-----------------|-------------|
| CC2 | 23,955 | 146 | 12 | 4 | 8 |
| Codex | 7,904 | 380 | 8 | 4 | 7 |
| ChatGPT | 19,702 | 88 | 24 | 4 | 20 |
| Gemini | 6,332 | 39 | 4 | 4 | 3 |
| DeepSeek | 9,713 | 167 | 6 | 4 | 7 |
| **Total** | **67,606** | — | **54** | **20** | **45** |

- **ChatGPT** was the most thorough review.
- **Gemini** was fastest and most focused.

---

## Convergent Themes

Themes where 3 or more models independently agreed on the same issue.

### Theme 1 — Blind round contradicts providing findings

4 of 5 models agreed (CC2, Codex, ChatGPT, Gemini). Providing the 6 convergent findings in Round 0 contradicts calling it a blind round.

**Resolution:** Split Round 0 into:
- **Round 0A** — truly blind, no prior findings
- **Round 0B** — seeded validation with the convergent findings

DeepSeek dissented, preferring to provide them for calibration, but was overruled by the majority.

---

### Theme 2 — Self-orchestration circularity

3 of 5 models agreed (CC2, ChatGPT, Codex). DynamicManager both controls the test and is the test article, creating a circular dependency. The stop predicate is part of the system under test.

**Resolution:**
- Add independent stop caps: hard round cap at 10, wall clock cap at 4 hours
- Mandatory round-level telemetry for external audit
- A full shadow controller was suggested by ChatGPT but deferred as disproportionate

---

### Theme 3 — Code extract scope insufficient

**All 5 models agreed.** This was the strongest convergence. Every model said the 1,200-line extract would be incomplete and miss dependencies.

**Resolution:**
- Provide the full `dynamic_management.py` file to all models, with the analytical boundary defined in the system prompt
- Add a dependency interface summary

---

### Theme 4 — Success criteria weak or circular

4 of 5 models agreed (CC2, Codex, ChatGPT, Gemini). "3 models surviving to round 3" is a poor criterion because it conflates infrastructure issues with immune quality, and a correct immune system might legitimately remove models.

**Resolution:** Reframed as behaviour validation. The criterion now asks whether immune actions are justified, not whether specific events occur.

---

### Theme 5 — Cross-model agreement is not verification

3 of 5 models agreed (CC2, Codex, ChatGPT). Models may agree for wrong reasons due to shared training data.

**Resolution:** Downgraded cross-model agreement to corroborative evidence. Require at least one independent artifact such as a test, trace, or code path proof.

---

### Theme 6 — SymPy is partially applicable

3 of 5 models agreed (CC2, ChatGPT, Gemini). Mathematical operations in the immune code — decay functions, thresholds, score calculations — are verifiable with SymPy.

**Resolution:** SymPy verification now required for any fix altering mathematical operations.

---

### Theme 7 — Fix ordering should be dependency-aware

3 of 5 models agreed (CC2, ChatGPT, Gemini). Severity-only ordering is brittle when fixes interact.

**Resolution:** Build a fix dependency graph first. Apply prerequisites before dependents.

---

### Theme 8 — Missing telemetry

3 of 5 models agreed (ChatGPT, DeepSeek, CC2). The plan lacked specification for round-level logging.

**Resolution:** Mandatory round-level logging of all immune decisions, including:
- Detection events
- Diagnoses
- Actions taken
- Damping state
- Stop inputs and outputs

---

### Theme 9 — Need fault injection

4 of 5 models agreed (CC2, Gemini, ChatGPT, DeepSeek). Passive testing is unreliable.

**Resolution:** Added induced-failure scenarios:
- Canary test with simulated empty responses
- False positive test with benign findings
- Cascade test with simultaneous failures
- Oscillation test with alternating good and bad responses

---

### Theme 10 — DeepSeek decomposition

**All 5 models agreed.** Decompose into 3 sub-areas for DeepSeek.

---

### Theme 11 — Load balancing separate with interface contracts

**All 5 models agreed.** Test separately but include interface contracts.

---

## Open Question Consensus

| Question | Result |
|----------|--------|
| Should DeepSeek get per-area decomposition? | All 5 said yes. Decompose into detection, response, and integration sub-areas. |
| Should convergent findings be provided in the blind round? | 4 said no, DeepSeek said yes. Resolution: split into blind discovery plus seeded validation. |
| What should immune damping rounds be set to? | CC2 and Codex: 2. ChatGPT and Gemini: 1. DeepSeek: 3. Resolution: set to 2 (median), instrument for observability. |
| Should load balancing be included? | All 5 said test separately but include interface contracts. |

---

## Notable Non-Convergent Findings

- **ChatGPT** proposed running baseline, induced-failure, and stress runs as separate experiment passes. Not adopted — disproportionate for current scope.
- **Gemini** flagged model version strings as potentially hallucinated. This is a false alarm. The versions GPT 5.4, Opus 4.6, and Gemini 3.1 Pro are the actual current model identifiers.
- **ChatGPT** proposed a full shadow or external controller for experiment orchestration. Deferred. Telemetry plus independent caps are the simplest sufficient mitigation.

---

## Top Findings by Severity

The highest severity finding was **Codex PF001 at 0.99**, about scope truncation. All of the top 10 findings by severity related to either:

- Scope truncation
- Self-orchestration circularity
- Missing telemetry

All of these were addressed in the convergent theme resolutions above.

---

## Plan Updates

The Experiment 17 plan has been updated to incorporate all 11 convergent themes:

- **Status:** changed from DRAFT to APPROVED
- **All 4 open questions:** resolved
- **New sections added:**
  - Behaviour-driven simulation
  - Appendix-to-code traceability
  - Round-level telemetry
  - Post-experiment protocol
