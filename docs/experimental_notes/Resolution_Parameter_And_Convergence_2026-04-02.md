# Resolution Parameter, Convergence Validity, and Gemini χ Comparison

**Date:** 2026-04-02
**Origin:** Founder insight (microscope analogy) + P-pass on compound objective + Gemini churn guard proposal

---

## 1. Convergence Validity of Ω

The compound objective Ω = A × γ_out = (β_out/β_in) × (1 − β_out) is a genuine convergence measure, not an arbitrary cutoff.

**SymPy-verified properties:**
- dΩ/dβ_out = (1 − 2β_out)/β_in → optimal at β_out = 0.5 (Occam peak)
- Ω → 0 as β_out → 0: vocabulary exhaustion (nothing new to find)
- Ω → 0 as β_out → 1: pure churn (all new words, no convergence)
- Both boundaries represent legitimate stopping conditions

When Ω → 0, the information yield has genuinely been exhausted. This formalises the stopping intuition that a human researcher has when they "keep finding the same things."

---

## 2. The Resolution Parameter S

**Founder insight:** In science, resolution is tuneable. An optical microscope, electron microscope, and scanning tunnelling microscope give increasingly different degrees of resolution. The system needs a tuneable parameter that controls what level of detail the models focus on.

### Formal Definition

Let S ∈ [0, 1] be the **resolution threshold** (severity floor).

- F(r, S) = findings in round r with severity ≥ S
- γ_out(r, S) = Duane gamma computed on F(r, S) vocabulary only
- A(r, S) = amplification factor at resolution S
- **Ω(r, S) = A(r, S) × γ_out(r, S)**

**Convergence at resolution S:** Ω(r, S) < τ for 2+ consecutive rounds

### Resolution Levels

| S Value | Analogy | Behaviour |
|---------|---------|-----------|
| 0.8 | Optical microscope | Only critical/structural bugs count |
| 0.5 | Electron microscope | Important bugs count (default) |
| 0.3 | Scanning tunnelling | Everything including style |
| 0.0 | Unbounded | May never converge on complex code |

### How S Constrains the Problem Box

S constrains the problem box **mechanically**. Models cannot break out of it:
- At S = 0.8, medium-severity restatements are invisible to Ω
- Models can find whatever they want; sub-threshold findings just don't count as evidence of continued productivity
- "If you build a house, you don't keep adding bricks until you build a skyscraper" — S defines what "house" means

**S controls WHAT the system looks at. Ω controls WHEN it stops looking.**

---

## 3. Comparison: Ω vs Gemini's χ

Gemini proposes: **χ = cos(θ) / max(ε, ΔFindings)**

| Property | Ω (Heaps-Duane) | χ (Gemini) |
|----------|----------------|------------|
| Dependencies | None (tokenize + count) | sentence-transformers |
| Compute cost | Milliseconds | ~1–5s per round |
| Already running | Yes (Run 6 passive data) | No |
| Per-model granularity | Yes | No (round-level only) |
| Resolution parameter | Yes (via S) | No |
| Tuneable parameters | S + τ | τ_χ only |
| Framework fit | Heaps-Duane (same as γ) | New dependency |
| Tested on data | Yes (Run 6 confirms churn detection) | No |

**χ is not wrong** — cosine similarity of embeddings is a valid similarity measure. But Heaps β on output vocabulary captures the same signal without the dependency. Low β_out = repeating vocabulary = high cosine similarity. Same information, lighter machinery.

### Genuine Blind Spot

Synonym-based churn: a model introduces new vocabulary while saying the same thing with different words. β_out registers novelty; cos(θ) catches repetition.

**Mitigation:** The severity threshold S. Rephrased findings of known issues achieve lower severity (models are told not to duplicate). Low kappa from non-corroboration by other models also catches this.

---

## 4. P-Pass Falsification

| Attempt | Question | Verdict |
|---------|----------|---------|
| 1 | Can Ω miss churn that χ catches? | Partially survives (synonym blind spot, mitigated by S) |
| 2 | Can Ω trigger false convergence? | Survives (input change spikes β_out) |
| 3 | Does S constrain the problem box? | Survives (cross-model kappa detects severity inflation) |
| 4 | Is this just "pulling the plug with maths"? | Survives (information-theoretic grounding in Heaps' law) |

---

## 5. Extrapolation

**What generalises:** S + Ω is a general solution to "when do I stop iterating?" for any iterative analysis system. Applicable to RAG pipelines, research agents, multi-model workflows. Publishable as standalone finding.

**Boundary conditions:** S depends on model-assigned severity (game-able in adversarial scenarios; bounded by kappa). Breaks when domain has no natural severity ordering (pure creative tasks).

**Falsifiable predictions:**
1. Ω(r, S=0.8) reaches τ=0.10 within 5 rounds for the immune layer task
2. Convergence round correlates positively with 1/S (lower resolution → later convergence)
3. There exists a minimum S_min below which convergence is never achieved for a given codebase size
4. Per-model Ω ordering is stable across S values (ChatGPT highest amplifier regardless of resolution)

---

## 6. Implementation

```python
# In DynamicManagementConfig
resolution_threshold: float = 0.5  # User-tuneable: 0.8=fast/critical, 0.3=thorough
convergence_omega_tau: float = 0.10  # Compound objective threshold
convergence_omega_window: int = 2  # Consecutive rounds below tau to declare convergence
```

Findings with severity < `resolution_threshold` are excluded from:
- γ_output computation
- Amplification factor A computation
- Compound objective Ω computation
- Per-model benching decision

They are **not** excluded from the findings log or the report — only from the convergence calculation.

---

*Generated by CC (Claude Opus 4.6), 2026-04-02. Founder insight (microscope analogy) originated the resolution parameter.*
