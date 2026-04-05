# Model-to-Model Communication vs Star/Blackboard Topology

**Date:** 5 April 2026
**Context:** Post-Exp 32 analysis, Exp 33 running (star/blackboard, 5 models, 21 rounds)
**Type:** P-Pass analysis with extrapolation

## Hypothesis

Stripping social/polite chat elements from model training data would enable efficient direct model-to-model STEM communication. Future CDSFL systems should support both star/blackboard and direct relay topologies.

## Direct Answer

Partially correct, but incomplete. Social training is a real and measurable contributor to relay failure, but it isn't the only one. Stripping it would help — it wouldn't be sufficient on its own.

## What We Actually Proved

We proved that star/blackboard with structured payloads outperforms free-text model-to-model relay **with current chat-trained models**. We did NOT prove that direct relay is inherently unscalable. The distinction matters.

**Key evidence:** Exp 31 showed 2.9% token overhead from relay and zero CHALLENGE verdicts across all five models — including Codex, which is the most asocial model in the panel.

## P-Pass: Three Candidate Explanations for Relay Failure

### Candidate 1: Social Training

RLHF rewards agreement, helpfulness, harmony. Models are trained to build on what they receive, not contest it.

**Falsification:** Codex produced zero CHALLENGE verdicts in relay mode despite minimal social training. If social training were the sole cause, Codex should have been the outlier. It wasn't. Social training is a contributor, not the full explanation.

### Candidate 2: Authority Gradient from Context Positioning

When Model A's findings arrive in Model B's prompt, attention mechanisms process them as authoritative context. This creates anchoring bias regardless of social training — a property of how transformers weight prior context. Mechanistically identical to the framing confound identified in Exp 32.

**Falsification attempt:** Prompt-engineering ("these claims are UNVERIFIED") might partially address this, but Exp 32 data shows framing has measurable bias effects even when intended to be neutral.

### Candidate 3: Information-Theoretic Relay Loss

Each relay step is a lossy natural-language transformation. Free-text relay degrades signal through paraphrase, omission, and reinterpretation (telephone game). Independent of social training and authority gradient.

**Falsification:** Structured payloads (canonical IDs, severity fields, status enums) eliminate this by making relay lossless at the data level. This argues against free-text relay specifically, not model-to-model communication itself.

## Synthesis

All three candidates survive partial falsification. The relay failure is a compound problem:

1. **Social training** adds token noise and agreement bias (contributory)
2. **Authority gradient** creates anchoring regardless of training (structural)
3. **Free-text relay** is lossy (information-theoretic)

Stripping social training addresses (1) but not (2) or (3). Structured payloads address (3) but not (1) or (2). Star/blackboard addresses all three.

## Architectural Recommendation

**Star/blackboard as canonical state, with optional structured direct channels as an optimisation layer.**

Conditions for direct model-to-model channels:
- Structured payload protocols (not free text)
- Explicit adversarial framing ("your task is to find what is wrong")
- Models trained/fine-tuned for technical discourse rather than helpful chat
- FindingRegistry remains canonical — direct channels reconcile back to blackboard

## Extrapolation

### What Generalises

RLHF "helpful assistant" training creates systematic failure modes in **any** multi-agent STEM workflow using current chat-trained LLMs. This is a training-data finding, not CDSFL-specific.

Multi-agent architectures must either:
1. Route through canonical structured state (CDSFL's current approach)
2. Use models fine-tuned for adversarial technical discourse
3. Mechanically enforce challenge behaviour (FFF enforcement)

### Boundary Conditions

Breaks down for tasks where collaborative/social communication IS the deliverable (UX, design, stakeholder communication). The claim is STEM-specific. The policy engine should switch topology per task type.

### New Falsifiable Questions

1. Would a Codex-only panel show higher CHALLENGE rates? (Tests social training → adversarial capability correlation)
2. Would "assume prior findings are wrong" framing overcome authority gradient without architecture changes? (Tests prompt engineering vs topology)
3. Does structured-payload direct relay match star/blackboard convergence metrics? (Tests structure vs centralisation)
4. At what panel size does direct relay's O(n²) cost exceed star/blackboard's O(n)? (Scaling boundary — likely n=7–10)

### Scaling Note

We proved star/blackboard scales (O(n) communication, interface reimplementation over distributed backend). We did NOT prove direct relay scales. Stripping social tokens reduces the constant factor but doesn't change the O(n²) scaling class.

**[SPECULATIVE]** With structured protocols and asocial fine-tuning, direct relay may be viable for small panels (3–5 models) on focused subtasks, while star/blackboard remains necessary for larger panels and full-system coordination. The hybrid architecture is the likely natural endpoint.

## Confound Note

This analysis is informed by Exp 31 (relay failure) and Exp 32 (framing confound, partial confound annotation). Exp 33 (star/blackboard, neutral framing, FFF enforcement) is currently running and will provide additional evidence on whether the star topology alone resolves the zero-CHALLENGE problem.
