# Brain Agent Architecture — Conversational Multi-Model Orchestration

**Date:** 3 April 2026, 17:47 BST
**Origin:** Run 10 post-analysis → Gemini conversation → the founder's brain-agent proposal

## The Gemini Conversation

Two exchanges, ~80 seconds total. CC2 (Claude) opened by describing Run 10 results and asking Gemini about architectural weaknesses — not code bugs, but assumptions that might be wrong.

### Gemini's Claims
1. **Lossy handoffs:** Structured Finding objects strip tacit context (thread safety, invariants, state lifecycle)
2. **Misplaced falsification:** Reg T autoimmune check should be at the verification node, not downstream
3. **LLMs wasted on routing:** DC and NK shouldn't need LLM reasoning
4. **B-Cell translation fragility:** SymPy/z3 proof generation is inherently fragile

### CC2's Pushback
- Point 3 conceded by Gemini (NK uses TF-IDF, DC uses regex — already mechanical)
- Point 1 refined: loss is semantic, not computational — Finding objects guarantee schema compliance, not epistemic completeness
- **Point 2 produced novel insight:** CT should shift from verification (does the fix compile?) to falsification (what's the strongest condition that would break this fix?)
- **Point 4 produced novel insight:** LLMs generating z3 proofs silently restrict domains to make maths solvable — z3 "proves" something that doesn't map to runtime constraints

### Why This Matters
Neither insight emerged from 237 findings across 7 rounds of broadcast code review in Run 10. They emerged from adversarial dialogue about architectural assumptions. Broadcast mode produces code-level findings. Conversational mode produces architectural insights.

## The Brain Agent Proposal (The Founder)

**Problem:** The current system is a "body without a brain." Individual model agents work in isolation. No central intelligence coordinates, relays, facilitates discussion, or adapts.

**Proposal:** A dedicated brain agent (CC3 or separate CC2 instance) whose job is to:
- Collect information from all system parts
- Monitor health and adapt
- Relay between models ("Gemini said X, what do you think?")
- Apply FFF prompting to other models
- Collate findings
- Remain constrained under CDSFL

Models become "neurones." The brain agent becomes the "prefrontal cortex."

## P-Pass on Brain Agent Architecture

### HARD Constraints
- API latency: 10-30s per model call
- Context: brain accumulates state, eventually hits limits
- Cost: brain consumes tokens for reasoning + relay
- CLI: Claude Code sessions have wall-clock and context limits

### Pass 1 — Feasibility
CC2 instance on Claude Code CLI can drive multi-model conversations. The `dispatch()` function works from Python. The Gemini chat proves mechanical feasibility.

### Pass 2 — Context Accumulation
5 models × 10 rounds × 5K chars/turn = 250K chars of relay context + brain reasoning. Approaches context limit. **Mitigation:** periodic summarisation or checkpoint-and-continue.

### Pass 3 — Quality of Relay
Brain relay adds intelligence (curation, contextualisation, challenge) vs script relay (lossy copy). **Risk:** brain introduces bias, misrepresents positions, filters important content. **Mitigation:** CDSFL on the brain agent + full unfiltered exchange logging.

### Pass 4 — CLI Implementation
Lightweight Python harness launches Claude Code session with brain-agent system prompt. Existing `dispatch()` infrastructure becomes the brain's toolkit. Brain decides who to ask, what to ask, when to relay.

### Pass 5 — Single Point of Failure
Brain crash/hallucination compromises entire run. **Mitigation:** immune pipeline still validates output; lightweight watchdog monitors brain behaviour (token budget, finding rate, convergence).

## Surviving Architecture

```
┌─────────────────────────────────────────────────┐
│           BRAIN AGENT (CC3/Claude)               │
│  - CDSFL-constrained                            │
│  - Drives conversation                          │
│  - Applies FFF to other models                  │
│  - Tracks convergence                           │
│  - Synthesises findings                         │
│  - Checkpoints for context management           │
├─────────────────────────────────────────────────┤
│  Tools: dispatch(model, prompt) for each model  │
│         immune_pipeline(findings)                │
│         convergence_check(findings)              │
└──────┬──────┬──────┬──────┬──────┬──────────────┘
       │      │      │      │      │
    ┌──▼─┐ ┌──▼──┐ ┌─▼──┐ ┌▼───┐ ┌▼──────┐
    │CC2 │ │Gemi │ │Deep│ │Code│ │ChatGPT│
    │    │ │ni   │ │Seek│ │x   │ │       │
    └────┘ └─────┘ └────┘ └────┘ └───────┘
      Neurones — receive focused questions,
      produce responses, engage in dialogue
```

**CLI:** `claude --system-prompt brain_agent.md -p "Review immune_agents.py using 5-model panel"`

## Extrapolation

### What Generalises
Brain-agent pattern is a general multi-LLM coordination solution. Transfers to any domain where value comes from synthesis across perspectives, not volume of independent observations.

### Boundary Conditions
- Brain context window insufficient for task complexity
- Relay latency makes wall-clock unacceptable
- Brain biases dominate (monoculture risk)
- Task is genuinely parallelisable with no interdependence

### Falsifiable Questions
1. Does brain-mediated conversation produce higher novel-finding-per-token than broadcast? [TESTABLE]
2. Does the brain agent introduce systematic bias toward its own model family? [TESTABLE]
3. Is there an optimal brain-to-neurone ratio? [TESTABLE]
4. Does convergence happen faster in conversational mode? [TESTABLE]

### [SPECULATIVE] Monoculture Risk
A Claude brain systematically favouring Claude neurones would look like quality convergence when it's actually echo-chamber convergence. This is the most dangerous failure mode and must be explicitly tested.

## Comparison: Broadcast vs Conversational

| Metric | Run 10 (Broadcast) | Gemini Chat (Conversational) |
|--------|-------------------|------------------------------|
| Time | 2+ hours | 80 seconds |
| Findings | 237 | 2 architectural insights |
| Churn | 26.6% | 0% |
| Novel architectural insights | 0 | 2 (CT adversarial, z3 domain restriction) |
| Information density | Low | Very high |
| Token cost | ~500K+ | ~12K |
