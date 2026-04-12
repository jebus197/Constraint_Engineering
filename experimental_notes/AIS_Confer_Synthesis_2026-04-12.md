# AIS Integration Confer Synthesis

**Date:** 12 April 2026  
**Models consulted:** Gemini 3.1 Pro, Codex GPT-5.4 (via OpenRouter)  
**Protocol:** CDSFL + FFAFP (Find, Follow, Analyse, Fix, P-pass)  
**Raw logs:** `bench/logs/confer_ais_integration/`

## Background

A literature assessment identified five gaps where Artificial Immune System research, Holland's Complex Adaptive Systems work, and Kohonen's Self-Organising Map lineage could inform improvements to the CDSFL immune pipeline. Two external models were consulted independently under the full CDSFL structured falsification protocol. Each model received the assessment document, the source code for `immune_agents.py` and `runner_core.py`, and the CDSFL core directives as system prompt. Both were required to produce explicit FFAFP analysis per gap.

---

## Gap-by-Gap Synthesis

### Gap 3: Embedding-Based Similarity

| | Gemini 3.1 Pro | Codex GPT-5.4 |
|---|---|---|
| **Verdict** | GO | GO |
| **Model** | `all-MiniLM-L6-v2` | `all-MiniLM-L6-v2` |
| **LOC** | ~15 | ~40–90 |
| **Key risk** | OOM if model loaded per subprocess | O(n²) recomputation without cache |
| **Mitigation** | Single global instance | Lazy-load + embedding cache + lexical fallback |

**Synthesis:** Both models agree this is the highest-leverage, lowest-risk improvement and should be implemented first. Shared infrastructure change behind a stable function signature — no downstream API breakage. Key engineering constraint: single-instance model loading with cached embeddings.

**Verdict: GO. Implement first.**

---

### Gap 2: Continuous Suppression Function (Idiotypic Network-Inspired)

| | Gemini 3.1 Pro | Codex GPT-5.4 |
|---|---|---|
| **Verdict** | NO-GO | GO (with safeguards) |
| **Falsifier** | Geometric decay masks systemic issues | Same concern, but resolvable |
| **Mitigation** | None proposed | Clip sim to [0, 0.95], floor on weight, restrict to neighbours ≥ 0.2 sim |
| **LOC** | — | ~65–140 |

**Disagreement resolution:** Gemini's falsifier (geometric decay crushing valid clusters) is real. Codex's mitigation (clipped similarity, floor, weighted synthesis rather than binary drop) addresses that falsifier directly. The implementation must ensure the downstream pipeline consumes weights rather than treating duplicates as boolean.

**Verdict: Conditional GO. Implement with Codex's safeguards, after Gap 3.**

---

### Gap 1: Persistent Immune Memory Across Experiments

| | Gemini 3.1 Pro | Codex GPT-5.4 |
|---|---|---|
| **Verdict** | GO | GO |
| **Storage** | SQLite in registry dir | JSON initially, no DB dependency |
| **LOC** | ~50 | ~200–340 |
| **Key risk** | Stale memory if code changes | Memory poisoning from incorrect rejections |
| **Mitigation** | File-hash scoping | Advisory-only, domain-scoped, outcome-gated writeback |

**Synthesis:** Both agree. Key architectural constraint: persistent memory must function as an advisory prior, never as an unconditional rejection authority. Code-state grounding (Gemini) and outcome-gated writeback (Codex) are complementary safeguards.

**Verdict: GO. Implement third, after Gaps 3 and 2.**

---

### Gap 5: Credit Assignment Loop (LCS-Inspired)

| | Gemini 3.1 Pro | Codex GPT-5.4 |
|---|---|---|
| **Verdict** | GO | DEFER |
| **Approach** | Direct `v_bar` update via moving average | Separate empirical scorecard first |
| **LOC** | ~25 | ~110–240 |
| **Key risk** | CT Cell mechanical verification is coarse | Unknown fingerprint semantics in management layer |
| **Mitigation** | High-confidence verdicts only (>0.8) | Inspect `dynamic_management.py` before touching fingerprints |

**Synthesis:** Codex's caution is well-founded. The `runner_core.py` comment says updates happen in the management layer, which neither model was given to inspect. A separate scorecard is safer than mutating fields whose operational semantics are not fully visible.

**Verdict: DEFER. Inspect management layer before implementation.**

---

### Gap 4: Anticipatory Dispatch (Holland's Internal Models)

| | Gemini 3.1 Pro | Codex GPT-5.4 |
|---|---|---|
| **Verdict** | NO-GO | DEFER |
| **Concern** | Invalidates capability metrics | Core dependency not in supplied source |
| **Falsifier** | Model blinding — steering constrains attention | Prompt anchoring suppresses opportunistic findings |

**Synthesis:** Both agree this carries the highest policy risk. CDSFL convergence depends on measuring what models find naturally. Steering prompts corrupts that measurement.

**Verdict: DEFER. Highest policy risk. Requires metric isolation design.**

---

## Implementation Order

Both models converge on the same sequence:

| Phase | Gap | Rationale |
|-------|-----|-----------|
| 1 | **3 — Embedding similarity** | Foundational shared primitive, highest leverage |
| 2 | **2 — Continuous suppression** | Depends on quality similarity from Phase 1 |
| 3 | **1 — Persistent memory** | Depends on embedding similarity for cross-experiment matching |
| 4 | **5 — Credit assignment** | Inspect `dynamic_management.py` first; start with scorecard |
| 5 | **4 — Anticipatory dispatch** | Highest policy risk; requires metric isolation |

---

## Composition Dependencies

```
Gap 3 (embeddings)
  ├── Gap 2 (suppression) — depends on quality similarity scores
  └── Gap 1 (persistent memory) — depends on embedding matching

Gap 5 (credit assignment) → Gap 4 (anticipatory dispatch)
  Credit signals should stabilise before steering dispatch
```

The two chains (3→2→1 and 5→4) are largely independent.

---

## Extension Opportunities (Beyond the 5 Gaps)

**From Gemini:**
- Regulatory T-Cell feedback loop: feed CT Cell mechanical failure reasons back into LLM context in subsequent rounds

**From Codex:**
- Intrinsic semantic convergence metric from embedding-space cluster compactness
- Confidence calibration for CT evidence aggregation (file diversity, line specificity)
- Domain-scoped memory and routing (using existing `ImmuneResponse.domain`)
- Embedding cache persistence across experiments
- Target-file-aware similarity boosting

---

## Confer Protocol Note

This was the first confer conducted under the revised protocol (12 April 2026). All model consultations now operate under full CDSFL directives as system prompt with explicit FFAFP structure required per item under review. Results are subject to P-pass falsification. This protocol applies to all future `cc2`, `cx`, `ge`, `cgpt`, `ds` dispatches.

---

## Raw Response Metadata

| Model | Time (s) | Response length (chars) |
|-------|----------|------------------------|
| Gemini 3.1 Pro | 63.6 | 11,186 |
| Codex GPT-5.4 | 89.2 | 38,083 |
