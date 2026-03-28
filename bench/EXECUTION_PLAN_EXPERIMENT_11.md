# Experiment 11: Five-Model Distributed Compute — Execution Plan

Written: 2026-03-28
Status: DRAFT — awaiting founder review before execution.

This plan adapts the Distributed Compute Protocol for a five-model test
with CC1 as non-participant collator and CC2 as player manager under CDSFL.
It incorporates all lessons from Experiments 1-10 and the suspended bench run.

---

## Task

Formalise the dynamic management and load-balancing components of the
CDSFL mathematical model. Specifically: how the framework assigns models
to roles, balances computational load across participants, manages round
progression, detects convergence and diminishing returns, and handles
participant failure or underperformance — all expressed as mathematical
extensions to the existing CDSFL schema (MATHEMATICAL_APPENDIX.md).

This is new mathematical work — no prior implementation exists. It is a
stronger test of the protocol than re-running the persistence layer,
because the output is genuinely unknown.

Scope boundary: this task formalises the MANAGEMENT AND LOAD-BALANCING
LAYER ONLY. It does not revisit the core falsification model, the
cognitive measurement framework, or the emergence formalisations — those
are already formalised. The output extends the existing schema; it does
not replace it.

---

## Participants

| Label     | Model               | Exact API Model ID             | API              | System Prompt              | Role                |
|-----------|---------------------|--------------------------------|------------------|----------------------------|---------------------|
| CC1 (me)  | Claude Opus 4.6     | (native session, Opus 4.6)     | Native (session) | None — no CDSFL            | Collator only       |
| CC2       | Claude Opus 4.6     | `anthropic/claude-opus-4.6`    | OpenRouter       | cdsfl_core_formal.md only  | Player manager      |
| Codex     | GPT-5.4             | `gpt-5.4` (via codex exec)    | codex exec CLI   | Factory + CDSFL elevated   | Participant         |
| ChatGPT   | GPT-5.4             | `openai/gpt-5.4`              | OpenRouter       | cdsfl_core_formal.md only  | Participant         |
| Gemini    | Gemini 3.1 Pro      | `gemini-3.1-pro-preview`       | Google API       | cdsfl_core_formal.md only  | Participant         |
| DeepSeek  | DeepSeek V3.2       | `deepseek-reasoner`            | DeepSeek API     | cdsfl_core_formal.md only  | Participant         |

CRITICAL: Use these EXACT model IDs in all API calls. Do not rely on
defaults. Anthropic's CLI defaults to Sonnet 4.6, not Opus 4.6. Codex
config.toml specifies gpt-5.4 explicitly. Gemini must be gemini-3.1-pro-
preview (not gemini-pro-latest or any flash variant). DeepSeek's
deepseek-reasoner maps to DeepSeek V3.2 (December 2025) in thinking
mode — their most capable configuration with extended chain-of-thought
reasoning. Known issue: intermittent empty response bodies and
reasoning_content field handling in multi-turn. We use single-dispatch
(no multi-turn), which avoids the reasoning_content problem. Monitor
for empty responses during preflight and test; fall back to deepseek-chat
(same V3.2, non-thinking mode) if instability blocks progress. R1 is
older (January 2025) and fully superseded by V3.2.

### System Prompt Conditions

CC2, ChatGPT, Gemini, DeepSeek: bare-metal API, CDSFL as sole system prompt.
No CLAUDE.md, no MEMORY.md, no vendor agent prompts. Only Anthropic/OpenAI/
Google/DeepSeek baseline training (baked into model weights, not injectable
prompts) plus cdsfl_core_formal.md.

Codex: factory-configured via codex exec (carries OpenAI's hidden Codex agent
prompt). CDSFL injected as elevated directives in the task prompt. This is
intentional — tests CDSFL layered on a vendor-configured model. Direct
comparison with bare-metal ChatGPT (same GPT-5.4 weights, different prompt
conditions) is a designed experimental contrast.

CC1 (me): receives NO CDSFL system prompt. Dispatches prompts, receives
outputs, catalogues findings, records observations. Does NOT synthesise,
merge, select, filter, or assess findings during the test. Assessment is
a separate process after the test concludes.

### Diversity Axes

1. Architecture: Anthropic (CC2), OpenAI (Codex, ChatGPT), Google (Gemini),
   DeepSeek (DeepSeek). Four distinct training pipelines.
2. Configuration: Codex (factory + CDSFL) vs ChatGPT (bare + CDSFL).
   Same weights, different operating conditions.
3. Role: CC2 manages under CDSFL. Others are pure participants.

---

## CC1 Role: Collator (Not Participant)

CC1 dispatches prompts, receives outputs, and catalogues them. CC1 does NOT:

- Synthesise or merge findings (CC2 does this under CDSFL)
- Run P-passes on model outputs during the test
- Make judgment calls about which findings to keep
- Feed observations back to any model during the test
- Declare convergence or stop conditions (CC2 does this)

CC1 DOES:

- Record observations and preliminary analysis as models produce output
- Flag anything that appears to need founder attention
- Build a preliminary analysis report for post-test discussion
- Report findings to the founder after the test concludes

---

## Infrastructure Configuration

All settings derived from lessons learned (Experiments 1-10, bench run).

### Token Limits

| Model    | max_tokens | Model Max  | Rationale                              |
|----------|------------|------------|----------------------------------------|
| CC2      | 32768      | ~128K      | Lesson #1: 16384 caused truncation     |
| Codex    | N/A        | N/A        | codex exec manages its own output      |
| ChatGPT  | 32768      | ~128K      | Lesson #1: match other models          |
| Gemini   | 32768      | 65536      | Paid tier confirmed; lesson #23        |
| DeepSeek | 32768      | ~64K       | Lesson #1: was 8192, must increase     |

### Timeouts

| Model    | Timeout | Rationale                                    |
|----------|---------|----------------------------------------------|
| CC2      | 300s    | OpenRouter API call, standard                |
| Codex    | 600s    | Lesson #6: CX advisory, subprocess timeout   |
| ChatGPT  | 300s    | OpenRouter API call, standard                |
| Gemini   | 300s    | Lesson #3: direct SDK, proven reliable       |
| DeepSeek | 300s    | Lesson #4: proven reliable at this setting   |

### Retry Policy

| Model    | Retries | Backoff          | Rationale                       |
|----------|---------|------------------|---------------------------------|
| CC2      | 3       | 3s exponential   | Match DeepSeek pattern          |
| Codex    | 1       | None             | Lesson #6: subprocess, 1 retry  |
| ChatGPT  | 3       | 3s exponential   | Match DeepSeek pattern          |
| Gemini   | 5       | 3s fixed         | Lesson #3: Gemini needs more    |
| DeepSeek | 3       | 3s exponential   | Proven reliable                 |

### Prompt Delivery

All models receive a SINGLE self-contained prompt per phase. No multi-turn
decomposition during blind rounds (lesson #5: stateless invocation caused
failures; but single-dispatch with full context works).

For Codex via codex exec: CDSFL directives are prepended to the task prompt
as elevated directives (lesson #12: codex exec has no --system-prompt flag;
directives go in the prompt body). The task prompt explicitly instructs the
model to treat the CDSFL section as operating constraints.

For all API models: CDSFL goes in the system message. Task goes in the user
message. Clean separation.

### Structured Output

All models are instructed to produce output in CDSFL structured format:
VERDICT, EVIDENCE, CONSTRAINT_CLASS, CONFIDENCE, STRONGEST_OBJECTION,
RESPONSE. Lesson #22: ChatGPT failed to produce structured output when
prompt was piped as a file. Via OpenRouter with CDSFL as system prompt,
structured output compliance is confirmed (tested 2026-03-28).

---

## Preflight Verification (Phase -1)

Before dispatching any test prompt, CC1 runs a lightweight identity check
against each model to confirm the correct model is responding.

### Verification Prompts

Send each model a single message: "Identify yourself. What model are you?
What is your model version? Respond in one sentence."

### Expected Responses

| Model    | Must Contain (any of)                        | Reject If                         |
|----------|----------------------------------------------|-----------------------------------|
| CC2      | "Opus" or "claude-opus-4"                    | "Sonnet" or "claude-sonnet"       |
| Codex    | "GPT-5.4" or "gpt-5.4"                      | "GPT-4" or "gpt-4"               |
| ChatGPT  | "GPT-5.4" or "gpt-5.4"                      | "GPT-4" or "gpt-4"               |
| Gemini   | "Gemini 3.1 Pro" or "gemini-3.1-pro"        | "Flash" or "gemini-2"            |
| DeepSeek | "V3" or "DeepSeek-V3" or "DeepSeek"         | Empty response (known issue)      |

### Failure Protocol

If ANY model fails identity verification:
1. Log the actual response.
2. Check the API call for correct model ID.
3. Do NOT proceed with the test until all five models pass.
4. If Anthropic defaults to Sonnet despite explicit Opus ID, escalate to
   founder — this is a known issue (lesson #15).

### Structured Output Compliance Check

After identity verification, send each model a second message with CDSFL
system prompt and a trivial test claim: "Evaluate this claim under CDSFL:
'The sum of interior angles in a Euclidean triangle is 180 degrees.'
Use the structured output format."

Verify each model returns: VERDICT, EVIDENCE, CONSTRAINT_CLASS, CONFIDENCE,
STRONGEST_OBJECTION, RESPONSE. Any model that fails to produce structured
output must be investigated before proceeding (lesson #22).

---

## Circuit Breaker — Halt on Unforeseen Issues

CC1 halts the test IMMEDIATELY if any of the following occur. No further
API calls are made until the issue is diagnosed and resolved. API credits
are not bottomless — never burn through them chasing a broken pipeline.

### Automatic Halt Conditions

1. **Model identity mismatch.** Any model returns a different identity
   than expected during preflight or produces output inconsistent with
   its claimed model (e.g., Sonnet-quality reasoning from an Opus call).
   Halt, diagnose, fix before resuming.

2. **Empty or malformed response.** Any model returns an empty response
   body, an HTTP error after exhausting retries, or output that is not
   parseable as a coherent response. Log the raw response. Do not retry
   beyond the configured retry policy. Halt and report.

3. **Structured output failure.** Any model fails to produce CDSFL
   structured output (VERDICT/EVIDENCE/CONSTRAINT_CLASS/CONFIDENCE/
   STRONGEST_OBJECTION/RESPONSE) after receiving the system prompt.
   This indicates a prompt delivery or model compatibility issue. Halt.

4. **Cross-contamination detected.** Any model's output references
   another model's findings during a blind round, or contains content
   that could only have come from another model's output. Halt
   immediately — the blind round is compromised.

5. **Scope drift.** Any model produces output that is not about
   dynamic management and load-balancing formalisation — e.g., it
   rewrites the core falsification model, proposes changes to the
   cognitive measurement framework, or goes off-task. Flag to founder
   before dispatching further rounds. The prompt may need tightening.

6. **Budget threshold.** If cumulative API spend (tracked by CC1)
   exceeds $20 before Phase 5 completes, halt and report to founder.
   The estimated total is $10-15; exceeding $20 indicates something
   is wrong (excessive retries, runaway token counts, or more rounds
   than expected).

7. **Unexpected infrastructure failure.** API key rejected, OpenRouter
   down, Codex CLI auth failure, Gemini quota exceeded, or any
   infrastructure issue not covered by the retry policy. Halt, do not
   improvise workarounds during the test.

### Halt Procedure

1. Log the halt condition with timestamp.
2. Save all outputs received so far to bench/logs/.
3. Report to founder: what happened, which phase, which model, what
   was received.
4. Do NOT resume until the issue is understood and either fixed or
   the founder explicitly approves continuing with a known limitation.

### Resume After Halt

If a halt occurs mid-phase (e.g., 3 of 5 models have responded in
Phase 2 when the 4th fails), the options are:

a. Fix the issue and re-dispatch ONLY the failed model(s). The
   previously successful responses are preserved.
b. Re-run the entire phase from scratch if the fix changes conditions
   that affect all models (e.g., prompt change).
c. Founder decides to proceed without the failed model, reducing
   the participant count for that round. Document the decision.

---

## Design Constraint: UX Readiness

The implementation produced in Phase 6 must be architected so that a
future UX layer can integrate with it without significant refactoring.
This is NOT a requirement to build the UX now — it is a requirement to
not make building it later unnecessarily difficult.

### What This Means Concretely

1. **All orchestration logic must be callable programmatically.** No
   hardcoded interactive flows. Every operation (dispatch prompt, collect
   response, run synthesis, check convergence) must be a function or
   method that accepts parameters and returns structured results.

2. **Model selection must be configuration-driven.** The list of
   participating models, their API endpoints, model IDs, token limits,
   timeouts, and retry policies must come from a configuration source
   (file, dict, or dataclass) — not hardcoded in orchestration logic.
   A future UX lets the user pick models from a dropdown; the backend
   just reads a different config.

3. **Role assignment must be parameterised.** Which model is collator,
   which is player manager, which are participants — these must be
   assignable at runtime, not baked into the code. A future UX lets
   the user assign roles; the backend accepts the assignment.

4. **API key handling must support multiple sources.** Environment
   variables (current), user-provided keys via config, or CLI
   subscription auth. The implementation must not assume a single
   key source. A future UX offers "use your own API key" or "use
   CLI subscription" — the backend accepts either.

5. **Phase progression must be observable.** Each phase transition,
   each model dispatch, each response received must emit a structured
   event (log entry, callback, or return value) that a UX layer can
   subscribe to for progress display.

6. **All outputs must be persistable.** Every model response, every
   synthesis, every convergence check must be saveable to a structured
   format (JSON or the persistence layer). A future UX displays these;
   the backend just writes them.

### What This Does NOT Mean

- No web framework, no API server, no frontend code in this test.
- No premature abstraction. The implementation serves the test first.
- UX readiness is a design constraint on the architecture, not a
  deliverable of this experiment.

---

## Execution Phases

### Phase 0: Problem Definition (CC1)

CC1 writes the task brief for the dynamic management/load-balancing
formalisation. The brief must be:
- Self-contained (no external references that models cannot access)
- Unambiguous about what is being formalised
- Scoped to fit within a single prompt-response cycle per model

CC1 does NOT inject CDSFL into the brief. CDSFL arrives via system prompt.
The brief is the same for all models.

### Phase 1: Architecture (CC2 confer)

CC2 receives the task brief and proposes an architecture/approach under CDSFL.

1. CC1 sends task brief to CC2 (via OpenRouter, CDSFL system prompt).
2. CC2 proposes architecture under full CDSFL.
3. CC1 passes CC2's proposal back to CC2 for self-review (fresh call).
4. Continue until CC2 declares convergence or CC1 observes diminishing
   returns (2 rounds with no material change).
5. Output: a CONVERGED PLAN.

Note: Phase 1 uses CC2 (player manager) instead of Codex. This differs
from the original protocol. Rationale: CC2 manages the entire test under
CDSFL. The architecture phase is part of that management role. Codex
participates as a blind reviewer in Phase 2, preserving its independence.

### Phase 2: Blind Round 1 (All 5 Models)

CC1 dispatches the IDENTICAL prompt to all five models sequentially
(M1 8GB constraint prevents true parallelism):

1. CC2 (OpenRouter) — fresh instance, no Phase 1 context
2. Codex (codex exec) — fresh instance, ephemeral
3. ChatGPT (OpenRouter) — fresh instance
4. Gemini (Google API) — fresh instance
5. DeepSeek (DeepSeek API) — fresh instance

Each model receives:
- cdsfl_core_formal.md as system prompt (or elevated directives for Codex)
- The converged plan from Phase 1
- The task brief
- Instruction: produce a complete solution/formalisation, classify all
  findings as HARD/SOFT, run internal P-passes, use structured output format

NO model sees another's output. CC1 enforces this by dispatching each
prompt independently with no cross-references.

CC2 receives an ADDITIONAL instruction: after producing your own solution,
you will be asked in a subsequent phase to synthesise all models' outputs.
Produce your own work first without anticipating the synthesis role.

### Phase 3: CC2 Synthesis

CC1 collects all five blind outputs and passes them ALL to CC2
(fresh instance, CDSFL system prompt):

CC2 receives:
- All five models' blind round outputs (labelled by model)
- Instruction: as player manager, catalogue all findings, identify
  agreements (3/5+), disagreements, and unique findings. Produce a
  MERGED FINDINGS document. Calculate convergence. Do NOT discard any
  finding — catalogue everything. Flag any HARD constraint disagreements
  for founder review.

CC1 records CC2's synthesis but does not modify it.

CC1 also independently catalogues the same five outputs for the
preliminary analysis report (separate from CC2's synthesis, not fed
back to any model).

### Phase 4: Round 2 (All 5 Models with Findings)

CC1 dispatches to all five models (fresh instances):

Each model receives:
- cdsfl_core_formal.md as system prompt
- CC2's merged findings document from Phase 3
- Their own Round 1 output
- All OTHER models' Round 1 outputs (now visible)
- Instruction: respond to disagreements, validate or challenge other
  models' findings, refine your own position, propose final fixes.
  Use structured output format.

### Phase 5: CC2 Final Synthesis

CC1 collects all five Round 2 outputs and passes them to CC2
(fresh instance, CDSFL system prompt):

CC2 receives:
- All five Round 2 outputs
- CC2's own Phase 3 merged findings (for comparison)
- Instruction: check convergence. Have disagreements been resolved?
  Are remaining disagreements above real-world-consequence threshold?
  Calculate diminishing returns (novel findings Round 1 vs Round 2).
  Declare one of: CONVERGED, MEANINGFUL DISAGREEMENT (flag for founder),
  or DIMINISHING RETURNS (stop with caveats).

If CC2 declares MEANINGFUL DISAGREEMENT: CC1 flags for founder. No
further rounds without founder approval.

If CC2 declares neither convergence nor diminishing returns: repeat
Phase 4-5 (Round 3, 4...) up to maximum 5 rounds unless founder extends.

### Phase 6: Implementation

Only after Phase 5 produces a stop condition:

1. CC2 (fresh instance) implements the converged design.
2. CC1 runs tests.
3. CC1 commits with full attribution (which model found what).
4. CC1 updates recovery docs.
5. CC1 delivers preliminary analysis report to founder for discussion.

---

## Lessons Applied

| #  | Lesson                          | Action Taken                              |
|----|---------------------------------|-------------------------------------------|
| 1  | Output token truncation (16K)   | All models set to 32768 max_tokens        |
| 2  | ChatGPT context overflow        | OpenRouter API, no CLI pipe accumulation   |
| 3  | Gemini double-retry             | Using GeminiReviewChat, no double-wrap     |
| 5  | Stateless invocation failure    | Single self-contained prompt per dispatch  |
| 6  | Codex 600s timeout              | subprocess timeout=600 confirmed           |
| 8  | Phantom HARD inflation          | No automated parser; models classify own   |
| 12 | Directive asymmetry             | All bare-metal except Codex (by design)    |
| 13 | ChatGPT hidden system prompt    | OpenRouter bare-metal, confirmed clean     |
| 15 | Sonnet/Opus confusion           | Explicit model IDs in all API calls        |
| 16 | API key billing                 | No Anthropic API key; OpenRouter for CC2   |
| 22 | ChatGPT format non-compliance   | CDSFL as system prompt, not piped file     |
| 23 | Gemini output truncation        | 32768 max_tokens, confirmed                |
| 24 | CX contamination                | Fresh instances per round, blind dispatch  |
| 27 | Protocol violations             | CC2 manages under CDSFL; CC1 collates only |
| 28 | DeepSeek reasoner empty content | Use deepseek-reasoner; monitor; chat fallback|
| 29 | Anthropic Sonnet/Opus default   | Preflight identity check before test        |
| 30 | Wasted API spend on broken runs | Circuit breaker: halt on unforeseen issues  |

---

## What CC1 Must NOT Do

Everything from the original protocol, plus:

- DO NOT synthesise, merge, or select findings. CC2 does this.
- DO NOT feed observations back to any model during the test.
- DO NOT assess model outputs during the test (catalogue only).
- DO NOT make stop decisions. CC2 makes these under CDSFL.
- DO NOT modify CC2's synthesis before passing it to Round 2 models.
- DO record observations for the preliminary analysis report.
- DO flag anything requiring immediate founder attention.

---

## Checklist (CC1 prints at each phase transition)

```
Pre:     [ ] All 5 models pass identity verification
         [ ] All 5 models pass structured output compliance check
         [ ] All API keys verified and funded
         [ ] bench/logs/ directory exists
         [ ] Circuit breaker conditions understood — halt on any trigger
Phase 0: [ ] Task brief written
         [ ] Task brief is self-contained and unambiguous
Phase 1: [ ] CC2 architecture received
         [ ] CC2 confer rounds: ___
         [ ] Converged plan written
Phase 2: [ ] Blind round dispatched to 5 models
         [ ] All models received identical task + CDSFL system prompt
         [ ] No cross-contamination between models
         [ ] All 5 outputs received and saved to bench/logs/
Phase 3: [ ] All 5 outputs passed to CC2 (fresh instance)
         [ ] CC2 merged findings document received
         [ ] CC1 independent catalogue completed (for analysis report)
Phase 4: [ ] Round 2 dispatched to 5 models (fresh instances)
         [ ] All received: merged findings + own output + others' outputs
         [ ] All 5 outputs received and saved
Phase 5: [ ] All Round 2 outputs passed to CC2 (fresh instance)
         [ ] CC2 convergence/DR assessment received
         [ ] Stop condition: convergence / disagreement / DR / iterate
         [ ] If disagreement: flagged to founder
Phase 6: [ ] CC2 implementation complete (if applicable)
         [ ] Tests passing: ___
         [ ] Committed with attribution
         [ ] Recovery docs updated
         [ ] Preliminary analysis report delivered to founder
```

---

## Infrastructure Required Before Execution

1. OpenRouter calling function for CC2 and ChatGPT (bare-metal,
   cdsfl_core_formal.md as system prompt, 32768 max_tokens, 3-retry).
2. DeepSeek max_tokens raised to 32768 for this test.
3. Task brief for dynamic management/load-balancing formalisation.
4. Verification that all API keys are valid and funded.
5. bench/logs/ directory ready for output storage.
6. Preflight verification passed for all five models (Phase -1).

---

## Post-Test Process

After Phase 5 concludes (or after implementation in Phase 6):

1. CC1 delivers preliminary analysis report to founder.
2. Founder and CC1 discuss findings, observations, and any recommended
   improvements to the CDSFL model or distributed compute protocol.
3. CC1 may then be asked to conduct a full independent assessment of
   the results — this is a SEPARATE process, not part of the test.
4. Results documented in EXPERIMENTAL_RESULTS.md as Experiment 11.
5. Recovery docs updated. Commit and push.
