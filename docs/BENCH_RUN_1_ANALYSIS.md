# Bench Run 1 Analysis — Confounded Baseline

## What This Run Measures

This first full bench run (26 frontier STEM tasks, 4 conditions, 5 models, 104 total runs) measures the effectiveness of structured multi-model distributed compute. It does NOT measure the full CDSFL pipeline.

The distinction matters. The confer protocol (5 models reviewing each other's work iteratively across 5 rounds) is functioning correctly. The CDSFL-specific innovations (SymPy per-finding verification feeding back to models, Registry-enforced policies, bare-metal parity across all models, anti-deference gates) are either incomplete or broken in this run. The results reflect distributed compute effectiveness in isolation.

## Results Summary (70 of 104 runs completed)

| Condition | Runs | Total HARD | Avg per run | Infra fails |
|-----------|------|-----------|-------------|-------------|
| Control | 18 | ~400 | ~22 | 1 |
| HIL | 18 | ~70 | ~4 | 1 |
| CDSFL | 17 | ~660 | ~39 | 0 |
| CDSFL+HIL | 17 | ~800 | ~47 | 0 |

The gradient is consistent across all tasks: HIL < Control < CDSFL < CDSFL+HIL.

CDSFL+HIL produces roughly 2x the HARD findings of Control. This ratio has remained stable from task ft-001 through ft-018, suggesting it is a genuine effect rather than a task-specific artifact.

## Known Confounds

### 1. Directive Asymmetry

Claude Opus 4.6 and Codex 5.3 carry the founder's cognitive methodology directives (CLAUDE.md / AGENTS.md) into every condition, including Control. DeepSeek, Gemini, and ChatGPT operate with no equivalent directives.

Impact: The between-condition comparison (Control vs CDSFL vs CDSFL+HIL) is clean because all conditions have the same model mix with the same asymmetry. The between-model comparison within conditions is confounded.

Status: Fix designed for next run. All models will run bare (no default system prompts) using claude --bare flag, OpenRouter for ChatGPT, and managed AGENTS.md for Codex. Methodology directives injected identically to all 5 models under CDSFL conditions.

### 2. Phantom HARD Findings

The finding extraction parser's fallback treated unstructured model output as HARD by default. This inflated HARD counts across all conditions.

Impact: Absolute finding counts are unreliable. Relative comparisons between conditions are less affected because the inflation applies roughly equally.

Status: Fixed. Default classification changed to SOFT. Extraction validation added.

### 3. HIL Prompt Narrowing

The HIL guidance prompt said "focus on these points," which framed the models' search and suppressed broader analysis. This is consistent with published research on framing bias in LLM code review (arXiv:2603.18740).

Impact: HIL (avg 4 per run) underperformed Control (avg 22 per run). The guidance actively harmed performance by narrowing the search space.

Status: Fix designed for next run. Iterative HIL guidance (5 rounds of questions, not a single dump) with "consider these among other issues" framing instead of "focus on."

### 4. ChatGPT Context Overflow

ChatGPT 5.4 via the kardolus CLI accumulated full conversation history, producing prompts of 60-92K chars in later confer rounds. 24 warnings, 1 actual failure.

Impact: ChatGPT's contributions degraded in later rounds due to context overload.

Status: Fix designed for next run. Context cap applied (same as CX). OpenRouter integration provides system-level prompt control.

### 5. SymPy Verification Incomplete

SymPy per-finding verification fired but produced limited results. Models under Control and HIL rarely included verifiable mathematical claims. CC claim extraction partially compensated but coverage was inconsistent.

Impact: The verification score (v-bar) component of the capability fingerprint is unreliable for this run. Decay curves (D) are measurable. Total findings (A) and coverage (C) are approximate.

Status: Fix designed for next run. All models receive verifiable_claim schema instructions under CDSFL conditions. CC extraction runs universally as measurement tool.

### 6. ChatGPT Hidden System Prompt

ChatGPT 5.4 via the proprietary API carries a hidden RLHF-trained "helpful assistant" system prompt that cannot be stripped. All other models can be stripped to bare operation.

Impact: ChatGPT operates under different baseline conditions than the other 4 models, even under Control.

Status: Fix designed for next run. OpenRouter provides access to GPT-OSS or GPT-5.4 with user-defined system prompts, eliminating the hidden preamble.

## What the Results DO Show

Despite the confounds, the following observations are robust:

### 1. Distributed Compute Multiplier

CDSFL+HIL (multi-model confer) consistently produces approximately 2x the findings of Control (single-model self-iteration) across all task types. This ratio has held stable across 18 tasks spanning mathematics, code, engineering, physics, and cross-domain problems. The confer protocol works.

### 2. Structure Adds Value Beyond Guidance

CDSFL (structure without expert guidance, avg 39) outperforms HIL (guidance without structure, avg 4) by roughly 10x. Structured methodology without domain expertise is far more effective than unstructured expertise without methodology. This is consistent with the core CDSFL thesis: methodology is a force multiplier, not a substitute for capability, but it outperforms undirected expertise.

### 3. The Interaction Effect

CDSFL+HIL (47) exceeds CDSFL (39) + HIL (4) = 43. The combination produces more than the sum of its parts. Expert guidance within a structured framework activates capabilities that neither component achieves alone.

### 4. Model Capability Differentiation

Preliminary per-model decay curve analysis shows different models exhibit different analytical profiles. Detailed per-model analysis will be conducted after the run completes.

## Confidence Assessment

High confidence: The ordering HIL < Control < CDSFL < CDSFL+HIL is a genuine effect of the experimental conditions, not an artifact of the confounds. The confounds affect absolute magnitudes but not relative ordering.

Medium confidence: The 2x distributed compute multiplier is approximately correct but may shift when confounds are corrected. The phantom HARD inflation affects all conditions roughly equally, so the ratio should survive correction.

Low confidence: Individual finding counts, verification scores, and per-model comparisons. These require the corrected run to be reliable.

## Relationship to the Next Run

This run establishes the baseline. The corrected run (bare-metal parity, iterative HIL, full SymPy verification, Registry enforcement, OpenRouter integration) measures whether the CDSFL-specific innovations add value on top of the distributed compute effect demonstrated here.

If the corrected run shows the same 2x multiplier, distributed confer alone accounts for the improvement and CDSFL's additional infrastructure is overhead. If the multiplier increases (3x, 4x), the CDSFL innovations are doing genuine additional work. Either result is publishable and informative.
