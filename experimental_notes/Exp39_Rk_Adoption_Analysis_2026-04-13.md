# Experiment 39 — R_k Adoption Analysis

**Date:** 13 April 2026
**Experiments compared:** 37 (~100% adoption) vs 39-0 (oscillating, partial adoption)
**Method:** 4-agent forensic investigation — prompt path tracing (×2), raw output comparison, context budget analysis

R_k(i) below denotes the iterative residual-risk self-assessment after round i. CC2 denotes the Claude Opus 4.6 CLI instance.

---

## 1. The Core Question

Experiment 37 achieved 88–100% R_k self-assessment adoption across all five frontier models over 16 rounds. Experiment 39-0, run four days later with identical operational directives and the same composer pipeline, achieved stochastic oscillating adoption:

| Model | R1 CORR | R2 CORR | R3 CORR | Pattern |
|-------|---------|---------|---------|---------|
| CC2 | 5 | 3 | 0 | Declining → zero |
| Codex | 0 | 1 | 8 | Delayed → surge |
| ChatGPT | 0 | 3 | 0 | Spike → zero |
| Gemini | 0 | 0 | 3 | Late onset |
| DeepSeek | — | — | — | 3 findings total (budget exhaustion) |

No model sustained CORROBORATION across all post-fix rounds. R0 was pre-fix (0% expected).

---

## 2. Three Root Causes (Compound Multiplicatively)

### Cause 1 — User Prompt Does Not Mandate R_k (PRIMARY)

**Exp 37** (`run_exp37_evidence.py` lines 2850–2867) — 9 mandatory per-finding fields:
```
FINDING_ID, SEVERITY, FLAW_CLASS, ABSTRACTION_INDEX,
FIND, FOLLOW, ANALYSE, FIX,
FALSIFICATION: (MANDATORY) ...will be rejected
CORROBORATION: (MANDATORY) compute R_k...show working
```

**Exp 39** (`reference_runner.py` lines 3024–3041) — 7 fields:
```
FINDING_ID, SEVERITY, FLAW_CLASS, ABSTRACTION_INDEX,
DESCRIPTION, FOLLOW, PROPOSED_FIX, VERIFIED
```

No ANALYSE. No FALSIFICATION. No CORROBORATION. The R_k mandate exists **only** in the system prompt (operational directive appended to composer phenotype) — thousands of tokens earlier in context.

Models attend most strongly to recent instructions. The user prompt defines the output schema. When it omits CORROBORATION, models treat R_k as optional regardless of system prompt mandates.

### Cause 2 — Context Budget Exhaustion (SECONDARY)

| Metric | Exp 37 | Exp 39 | Ratio |
|--------|--------|--------|-------|
| Test article | 23K chars (evidence.py) | 163K chars (reference_runner.py) | **7×** |
| System prompt | ~21K chars | ~21K chars | 1× |
| Total input | ~44K chars | ~184K chars | 4.2× |
| ChatGPT utilisation | ~73% | ~306% | **4.2× overbudget** |

Under context pressure, models compress output by dropping sections not demanded in the user prompt. **Gemini demonstration:** 13.5K chars with full numerical R_k in Exp 37 → 3.6K chars of JSON verdicts (zero R_k) in Exp 39 R1. Same model, same directives, same composer.

### Cause 3 — No Structural Enforcement (TERTIARY)

The runner accepts findings identically whether CORROBORATION is present or absent. No rejection gate, no scoring penalty, no feedback signal. The Exp 37 user prompt stated "Findings without this section will be rejected" — a credible proximate threat. The Exp 39 prompt contains no such threat.

Even with the decomposed dispatch fix (which added per-chunk CORROBORATION mandates for Codex and DeepSeek), compliance oscillated rather than stabilising. Instruction without consequence produces stochastic compliance.

---

## 3. Why Experiment 37 Worked

All three factors aligned:

1. **High salience** — User prompt explicitly demanded CORROBORATION with `(MANDATORY)` tag and rejection threat
2. **No compression pressure** — 23K article left ample output headroom for full FFAFP+R_k
3. **Redundant enforcement** — Operational directive reinforced the same mandate from system prompt

Exp 39 had **none** of these for monolithic models (CC2, ChatGPT, Gemini) and only partial coverage for decomposed models (Codex, DeepSeek got per-chunk fix mid-experiment).

---

## 4. Evidence Quality

### Exp 37 Sample — Gemini R5 (13,516 chars)
- Full FFAFP: FIND → FOLLOW → ANALYSE → FIX → FALSIFICATION → CORROBORATION
- Numerical R_k: `R_k = 0.463 × 0.99 + 0.01 = 0.468` with all parameters (p=0.9, d=0.8, η=0.2, q=0.144)
- Explicit falsification: "Falsifier: … Attempt: [logical trace]. Result: Falsification destroyed."

### Exp 39 Sample — Gemini R1 (3,615 chars)
- JSON verdict array: `[{"model": "DeepSeek", "verdict": "CONFIRM", "finding_id": "C0005"}, ...]`
- Zero FFAFP sections, zero FALSIFICATION, zero CORROBORATION
- Finding count explodes but analytical depth collapses

### Exp 39 Sample — CC2 R1 (18,934 chars)
- Split format: verdicts section (no R_k) + discoveries section (R_k present)
- Format fragmentation: R_k appears in discoveries but not verdicts
- Partial compliance from redundant operational directive, but structurally inconsistent

---

## 5. The Fix

### Immediate (Cause 1) — ~15 LOC

Add ANALYSE, FALSIFICATION, and CORROBORATION to `reference_runner.py` `_build_prompt()` at line 3041, matching the Exp 37 format:

```python
"  ANALYSE: classify constraint as HARD or SOFT, state CONFIRMED/UNCERTAIN/REJECTED\n"
"  FIX: the simplest sufficient correction (for CONFIRMED findings only)\n"
"  FALSIFICATION: (MANDATORY) state the falsifier, the attempt to satisfy it, "
"and the result. Findings without this section will be rejected.\n"
"  CORROBORATION: (MANDATORY) compute residual risk R_k using the "
"self-assessment equation in the operational directive. Show R_old, "
"numerical estimates for η, d, p, σ, ν, and the resulting R_k. "
"Qualitative-only assessment will be flagged.\n\n"
```

### Medium-term (Cause 2)

Add Gemini to `pre_decompose_models` for articles > ~50K chars. Investigate DeepSeek reasoning budget (max_tokens=4096 consumed by chain-of-thought, 0 chars output).

### Structural (Cause 3)

Runner-side validation gate: flag or downgrade findings missing CORROBORATION. This moves enforcement from instruction-level (stochastic) to structural (deterministic).

---

## 6. Broader Implication

This analysis confirms the 0–13% falsification compliance problem empirically across two experiments. When R_k is a system-prompt suggestion, compliance is stochastic. When it is a user-prompt mandate with explicit format and rejection threat, compliance approaches 100%. The gap between instruction-level and structural enforcement is the gap between hoping models comply and making non-compliance structurally costly.

---

## Appendix: R_k Adoption — Exp 37 (Reference)

| Model | Total | Rate |
|-------|-------|------|
| CC2 | 15/16 | 94% |
| ChatGPT | 13/16 | 81% |
| Codex | 16/16 | 100% |
| DeepSeek | 14/16 | 88% |
| Gemini | 16/16 | 100% |

Quality: 6.9–7.0/7 average across all models. Full numerical computation with intermediate working shown.
