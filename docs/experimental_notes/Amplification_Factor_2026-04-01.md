# Amplification Factor — Extended P-Pass on Input Complexity

**Date:** 1 April 2026
**Context:** Founder falsification of pure input-complexity dispatch model
**Status:** Hypothesis extended — 3D dispatch model, testable predictions

## The Falsification

The [input complexity proposal](Input_Complexity_Decay_Curves_2026-04-01.md) suggested
routing dispatch by γ_input (Heaps β on input text). The founder immediately falsified
this by example: a short, lexically simple question produced a full P-pass with new
mathematical framework, four testable predictions, and architectural implications.

**If routed by γ_input alone:** "simple, single-turn, basic FFF" — catastrophically wrong.

## The Amplification Factor

**Definition:** A = β_output / β_input

| A value | Meaning | Example |
|---------|---------|---------|
| A >> 1 | Simple question, complex answer | Founder's complexity question |
| A ≈ 1 | Complexity proportional | Standard code review finding |
| A << 1 | Complex input, simple answer | "Is this syntactically valid?" → "Yes" |

## P-Pass: Three Falsification Attempts

### 1. Can A be known before dispatch?

Not at cold start. After Round 0, the system has (input, output) pairs per model.
After Round 1, enough data to estimate A per model per task type.

- **Round 0:** Two-dimensional dispatch (length × γ_input)
- **Round 1+:** Three-dimensional dispatch (length × γ_input × estimated A)

**Verdict:** Learnable but not available at cold start. Fallback covers the gap.

### 2. Does A vary by model?

Run 5 Round 0 evidence — identical input (122K chars, immune task area):

| Model | Findings | Implied A |
|-------|----------|-----------|
| CC2 | 16 | High |
| CX | 5 | Medium |
| Gemini | 4 | Medium-low |
| ChatGPT | 1 | Low |
| DeepSeek | pending | — |

**Verdict:** A is per-model. Demands per-model calibration.

### 3. The "from nowhere" problem

Novel conjectures (Popper) have low input complexity but potentially infinite output
complexity. No metric on the text can predict this.

**Counter:** The system doesn't need perfect prediction — it needs to be *better than
the current approach* (no complexity signal). Fallback (multi-turn) handles novel cases.

**Verdict:** Acknowledged boundary. Not fatal.

## Three-Dimensional Dispatch Model

| Dimension | Signal | Measurement | Available |
|-----------|--------|-------------|-----------|
| Length | Token count | `len(prompt) // 4` | Always |
| Input complexity | γ_input | Heaps β on input windows | Always |
| Amplification | A = β_out/β_in | Learned from (input, output) pairs | After R0 |

## Extrapolation

**(a) Generalises to:** Any iterative LLM pipeline (RAG, multi-agent, orchestration).
A per-model amplification profile could be a model card metric. [SPECULATIVE]

**(b) Boundary conditions:**
- A is learnable within session/domain, not transferable across domains
- A is prompt-sensitive (CDSFL vs vanilla system prompts → different A)
- Novel conjectures are inherently unpredictable (handled by fallback)

**(c) Falsifiable predictions:**
1. A is more stable per-model-per-domain than per-model-global
2. A-based timeouts reduce both failures AND wasted wait time
3. "From nowhere" cases correlate with high referential density + low lexical density
4. FFF mode selected by (γ_input, A) outperforms γ_input alone on finding density

## The Popper Connection

A good hypothesis is simple but has rich, falsifiable consequences (Popper).
The amplification factor A measures exactly this: **how productive a question is.**

- High A = the question punches above its weight
- Low A = the question is proportional to its answer

CDSFL can now measure the productivity of its own questions — not just detect when
answers converge, but evaluate whether the *right questions* are being asked.
