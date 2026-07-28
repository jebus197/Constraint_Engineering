# DC v2 3-Layer Classification Fix: Codex Confer Record

**Date**: 2026-04-10T23:45:25+01:00
**Confer**: CC1 (Claude Opus 4.6, the interactive Anthropic instance) and CX (Codex GPT-5.4, OpenAI via OpenRouter)
**Subject**: Post-implementation review of the 3-layer DC v2 (Dendritic Cell version 2) classification fix
**File**: `bench/immune_agents.py` (lines 2149-2248, 2824-2958, 3641-3677)
**Tests**: `bench/tests/test_immune_agents.py` (24 new tests)

## Context

Experiment 38 Round 0 (R0): the DC v2 regex classifier misrouted 17/26 code findings to MATHEMATICAL and left 3/26 as UNCATEGORISED (a dead-end label that no immune cell processes). A 3-layer fix was implemented:
- Layer 1: Domain-aware code-context regex applied before the math pattern
- Layer 2: LLM (large language model) classifier for UNCATEGORISED residue only
- Layer 3: Hard verification gate plus domain wiring

Five prior confer findings (F1-F5) were addressed. This confer reviews the implementation.

## Codex Empirical Test Results

Codex ran the regex patterns against 7 adversarial samples in a read-only sandbox. Results were reproduced independently by CC1:

| Sample | code_context | strong_math | Would misroute in SW? |
|--------|-------------|-------------|----------------------|
| "the function f(x) = x^2 is bounded below by 0" | True | False | YES |
| "the variable n must satisfy n > 0" | True | False | YES |
| "this method runs in quadratic time" | True | False | YES |
| "the attribute of a relation is symmetric" | True | False | YES |
| "if x > 0 then f(x) is increasing" | False | False | no |
| "the method f returns x^2 and the proof is trivial" | True | True | no |
| "for every variable x, x + 1 > x" | True | False | YES |

CC1 additional samples:
| "this function has O(n log n) complexity" | True | True | no |
| "the convergence rate of this method is linear" | True | True | no |

5 of 7 Codex samples show over-match. The guard (`_STRONG_MATH_SIGNAL`) catches "proof" and "O(n)" but misses "bounded", "satisfy n > 0", "quadratic time", "symmetric", and "for every x".

## Findings

### CX-F1: _CODE_CONTEXT_PATTERN over-matches mathematical language (Q1) — CONFIRMED

**FIND**: Line 2163: `\bmethod\b|\bfunction\b|\battribute\b|\bvariable\b` matches mathematical uses of these words. "The function f(x)" matches `\bfunction\b`. "The variable n" matches `\bvariable\b`. "This method converges" matches `\bmethod\b`. "The attribute of a relation" matches `\battribute\b`. These are standard mathematical vocabulary.

**FOLLOW**: In the software domain, any description containing "function", "variable", "method", or "attribute" in a mathematical context will be routed to CODE_BEHAVIORAL (0.65 confidence) instead of MATHEMATICAL or LOGICAL. CT cells (Cytotoxic T cells, the code-investigation specialists) investigate code bugs, not mathematical claims. The finding will receive a CT verdict but no B-Cell verdict (B-Cell, the mathematical/logical/statistical specialist, only processes those three classes). The CT cell will likely produce UNCERTAIN (no code to investigate), and Stage 6 (the current mathematical framework) hard gate will escalate to HIL (human-in-the-loop). So the misroute does not cause silent failure — it causes unnecessary HIL escalation and wasted CT cycles.

**FIX**: Two options:
1. **Conservative**: Remove `\bmethod\b|\bfunction\b|\battribute\b|\bvariable\b` from `_CODE_CONTEXT_PATTERN`. These words are too ambiguous between code and math. The remaining patterns (def, class, self., import, __dunder__, return, raises, Error/Exception, dict access, status mutation, bug language, foo()) are all unambiguously code-specific.
2. **Refined**: Replace the bare-word matches with code-qualified variants: `\bmethod\s+(?:of|on|in|for)\s+(?:the|a|this)?\s*(?:class|object|instance)` etc. Higher precision but more complex regex.

**Recommendation**: Option 1 (conservative removal). The other 12 branches in `_CODE_CONTEXT_PATTERN` cover the Exp 38 misroute cases (they all had `self.`, `entry[`, `def`, `status ... mutate`, etc.). The 4 bare-word branches are not needed for the Exp 38 fix and introduce false positives for future non-software experiments.

**Severity**: Medium. Does not cause silent misverification (Stage 6 catches it), but wastes CT cycles and inflates HIL escalation count.

### CX-F2: _STRONG_MATH_SIGNAL missing coverage (Q2) — CONFIRMED

**FIND**: `_STRONG_MATH_SIGNAL` (line 2171) does not cover: "bounded/bound" (without "convergence" prefix), "quadratic/cubic/polynomial/exponential" (complexity without O() notation), "for all/for every" (universal quantification), "inequality" (already in _MATH_PATTERN_V2 but not in strong-math guard), "satisfies/satisfy" (constraint language), "symmetric/transitive/reflexive" (relation properties).

**FOLLOW**: When `_CODE_CONTEXT_PATTERN` matches (which it does too broadly per CX-F1), the only escape hatch is `_STRONG_MATH_SIGNAL`. Gaps in the guard compound the over-match. Even with CX-F1 fixed (removing bare words), future domains or mixed-context findings could hit this gap.

**FIX**: Add to `_STRONG_MATH_SIGNAL`:
```python
r"|\bbounded?\b"                              # bounded below, upper bound
r"|\b(?:quadratic|cubic|polynomial|exponential|logarithmic|linear)\s+(?:time|complexity|growth)"
r"|\bfor\s+(?:all|every)\b"                   # universal quantification
r"|\binequality\b"                            # already math-routed, but guard should match
r"|\bsatisf(?:y|ies)\b"                       # constraint satisfaction language
r"|\b(?:symmetric|transitive|reflexive)\b"    # relation properties
```

**Severity**: Low if CX-F1 is fixed (bare words removed). Medium if CX-F1 is not fixed (compounding effect).

### CX-F3: No lock contention between Layer 2 and Stage 2 (Q3) — NO ISSUE

**FIND**: Stage 1.7 (Layer 2 LLM active classifier, line 3357-3367) runs sequentially BEFORE Stage 2 (parallel verification, line 3375+). The pipeline flow is: Stage 1 to 1.5 to 1.7 to Stage 2. Within Stage 2, CT v1 (line 651) and CT v2 (line 1763) both acquire `_CLAUDE_CLI_LOCK`, but they run in the same ThreadPoolExecutor and contend only with each other — not with Stage 1.7.

**FOLLOW**: The only contention path would be if Stage 1.5 (shadow, 45s timeout per finding, iterates all findings) were still running when Stage 1.7 starts. But Stage 1.5 completes before Stage 1.7 begins (sequential in pipeline). The shadow classifier (Stage 1.5) does iterate all findings serially under the lock (45s timeout each), which could take 45s * N_findings before Stage 1.7 even starts. With 26 findings that is up to 1170s of shadow classification time. But this is a pre-existing latency issue with the shadow classifier, not a new issue introduced by Layer 2.

**FIX**: None needed for lock contention. The shadow classifier latency (Stage 1.5 serialisation over all findings) is a separate performance concern not introduced by this fix.

### CX-F4: Stage 6 hard gate — correct escalation on CT timeout (Q4) — DESIGN CORRECT, MINOR GAP

**FIND**: If CT times out on a CODE_BEHAVIORAL finding (line 1421-1433), it returns `verdict="UNCERTAIN", tool_used="ct_mechanical"` with `cell_type=CellType.CYTOTOXIC_T`. This IS a tool-grounded verdict (CYTOTOXIC_T is in `_TOOL_GROUNDED_CELLS`). Stage 6 checks for findings with zero tool-grounded verdicts, so a CT timeout finding will NOT be escalated by Stage 6 — it has a CT verdict.

**FOLLOW**: The timeout finding passes Stage 6 with an UNCERTAIN verdict from CT, then gets synthesised by Helper T. If no other cell produced a verdict (B-Cell skips CODE_BEHAVIORAL, NK only dedup), the finding may exit as UNCERTAIN from Helper T. Stage 5.5 (B-Cell UNCERTAIN escalation) would not apply (no B-Cell verdict at all). Stage 5 (auto-escalation) requires a prior-round match. So a novel CODE_BEHAVIORAL finding where CT times out and no other cell produces a verdict exits as UNCERTAIN — not escalated, not confirmed, not rejected.

This is arguably correct: UNCERTAIN means "the pipeline could not determine the truth of this finding" and it passes through for the human to see in the round output. However, there is no explicit log or flag that says "this finding was UNCERTAIN because CT timed out and no other cell could check it." The finding just appears in filtered_findings with an UNCERTAIN verdict.

**FIX**: Optional improvement — add a log line in the CT timeout handler noting that the finding's only tool-grounded verdict is a timeout-driven UNCERTAIN. Not a bug, but aids debugging.

**Severity**: Informational. The behaviour is correct — UNCERTAIN exits visible to HIL. No silent failure.

### CX-F5: Prior confer coverage (Q5) — ALL 5 ADDRESSED

Prior findings:
- **F1** (code-context before math): Implemented at line 2226. Working for Exp 38 cases.
- **F2** (UNCATEGORISED fallback): Implemented at line 2246 (software → CODE_BEHAVIORAL@0.40) and line 2942 (Layer 2 LLM fail-open → CODE_BEHAVIORAL).
- **F3** (LLM return format): Implemented at line 2824 (`_ACTIVE_CLASSIFIER_PROMPT` returns two lines: category + confidence).
- **F4** (domain wiring): Implemented at line 1217 (InsectBrain passes domain), line 3262 (run_immune_pipeline accepts domain).
- **F5** (hard verification gate): Implemented at line 3641-3677 (Stage 6).

All 5 are addressed. No gaps from the prior confer.

### CX-F6 (NEW): `_apply_llm_reclassification` counts fall-back as reclassified

**FIND**: Line 2956 increments `reclassified += 1` in the software-domain fallback branch (LLM failed/low-confidence → CODE_BEHAVIORAL). The return value is used in logging (line 3368) as "Layer 2 reclassified N findings" but this conflates LLM-driven reclassification with domain fallback. If all 3 UNCATEGORISED findings fall back rather than being LLM-classified, the log says "Layer 2 reclassified 3 findings" which implies LLM success.

**FOLLOW**: The logged count overstates LLM classifier effectiveness. During post-experiment analysis, "Layer 2 reclassified 3" would be interpreted as "the LLM successfully classified 3 findings" when in fact it may have failed on all 3 and the fallback did the work.

**FIX**: Track `reclassified_by_llm` and `reclassified_by_fallback` separately. Log both counts. Return a named tuple or dict instead of a single int.

**Severity**: Low. Logging accuracy, not functional correctness.

## Summary

| Finding | Status | Severity | Action Required |
|---------|--------|----------|-----------------|
| CX-F1: CODE_CONTEXT over-match | CONFIRMED | Medium | Remove bare-word branches (method/function/attribute/variable) |
| CX-F2: STRONG_MATH_SIGNAL gaps | CONFIRMED | Low-Medium | Add bounded, quadratic, for all, inequality, satisfy, relation properties |
| CX-F3: Lock contention | NO ISSUE | — | None |
| CX-F4: Stage 6 timeout handling | CORRECT | Informational | Optional: add timeout-specific log line |
| CX-F5: Prior confer coverage | ALL ADDRESSED | — | None |
| CX-F6: Reclassification count | NEW | Low | Separate LLM vs fallback counts in logging |

**Actionable fixes**: CX-F1 and CX-F2. Both are regex changes in `_CODE_CONTEXT_PATTERN` and `_STRONG_MATH_SIGNAL`. CX-F1 is higher priority because it removes false positives that affect the current software domain. CX-F2 hardens the guard for future mixed-context findings.

## Codex Session

- Model: GPT-5.4 (OpenAI)
- Session: 019d798c-0b97-7a60-ba40-8a640ea67e60
- Sandbox: read-only
- Note: Codex output was truncated before final analysis due to output length limits. Empirical regex test results (lines 5074-5121 of raw output) were captured and independently verified by CC1. All findings above are supported by both Codex tool calls and CC1 independent verification.
