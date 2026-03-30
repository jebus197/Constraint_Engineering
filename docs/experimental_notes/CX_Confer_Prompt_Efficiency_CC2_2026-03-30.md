# CX Confer Prompt Efficiency Analysis

**CC2 Player Manager P-Pass Findings**
**30 March 2026**

---

## Problem Summary

When CX (Codex 5.3) receives a confer prompt via `codex exec`, it spends most of its context budget investigating the codebase instead of producing findings. In one recent round, CX ran 78 shell commands to read files before producing 5 findings at the end. Those findings were good, with severity scores between 0.84 and 0.98. The problem is that the confer prompt describes the problem and references file paths, but does not embed the actual code CX needs to review. So CX goes and finds it itself.

---

## Finding 1: Stdin Piping — Severity 0.95

The code currently passes the full prompt as a command line argument to `codex exec`. macOS has a 1 megabyte argument size limit. But `codex exec` supports reading from standard input using a dash argument. Switching to stdin removes the argument size constraint entirely, allowing prompts up to CX's full context window of roughly 500,000 characters.

**Fix:** Change the subprocess call from passing the prompt as a positional argument to piping it via stdin using the `input` parameter.

---

## Finding 2: Briefing Document Pattern — Severity 0.92

This is the core finding. Compare two existing approaches. The experiment 12 confer prompt embeds focused code extracts of about 20 lines each, states the problem, and asks specific questions. CX responds with structured verdicts without needing to investigate. The experiment 17 and 18 approach embeds the entire 260,000 character artifact and tells CX to focus on a named boundary. CX still needs to read surrounding context to understand interactions.

The efficient pattern is for CC1 to extract the relevant code sections, not full files, state what the code does, identify the specific question, and embed it all directly. The inefficient pattern is naming a boundary and dumping the whole file.

**Fix:** Implement a CX briefing document pattern with three sections:

1. Context in 2 to 3 sentences.
2. Focused code limited to the boundary region plus direct call sites, aiming for 15 to 30 thousand characters.
3. The specific question CX should falsify.

---

## Finding 3: Pre-Digestion Bias Risk — Severity 0.78

If CC1 extracts only the code it thinks is relevant, CX cannot find bugs in code CC1 did not include. This is the unknown unknowns problem. However, the current alternative where CX reads the full file does not fully solve this either. CX spent 78 calls investigating and still only produced 5 findings, meaning it was already making extraction choices under time pressure.

**Fix:** Use a two-tier approach:

- **Default tier:** CC1 prepares a focused briefing with extracted code plus skeletal signatures of adjacent code showing function names, parameters, and return types but no bodies.
- **Periodic tier:** Every third confer round, give CX repo access with an explicit instruction to spend up to 10 tool calls verifying the extract is not missing critical context.

---

## Finding 4: Artifact Persistence Across Rounds — Severity 0.85

The `CXReviewChat` class accumulates CX's prior responses to simulate multi-turn conversation, but it does not carry forward the embedded code artifact between rounds. Each round's prompt is built fresh. If round 2 does not re-embed the code, CX loses the artifact context and must re-investigate.

**Fix:** Structure multi-round prompts as:

1. Briefing document (stable across rounds).
2. Prior findings (growing, compressed).
3. This round's question (new).

The briefing document does not change between confer rounds for the same task.

---

## Finding 5: Decomposition Threshold Adjustment — Severity 0.70

The existing decomposition threshold for Codex is set at 60,000 characters. The 78-tool-call problem occurs when the prompt is above this threshold but below the context window. CX can technically process it but wastes budget investigating rather than analysing.

**Fix:** Lower the Codex threshold from 60,000 to 30,000 characters and change the decomposition strategy from area rotation to the briefing document pattern described in Finding 2.

---

## Finding 6: Output Schema Constraint — Severity 0.88

The `codex exec` command accepts an `--output-schema` flag that constrains CX's output to a JSON Schema. This is not used anywhere in the codebase. If the output were constrained to the CDSFL finding format, CX would be structurally forced to produce findings rather than investigation narration.

**Fix:** Create a JSON Schema file for CDSFL findings and pass it via the `--output-schema` flag. This forces structured output and makes parsing deterministic.

---

## Implementation Priority

1. **Finding 1 — stdin piping.** Mechanical fix, 5 minutes of work.
2. **Finding 2 — briefing document pattern.** The core fix, eliminates most CX investigation.
3. **Finding 6 — output schema.** Constrains output format.
4. **Finding 4 — persistent briefing across rounds.** Prevents re-investigation in multi-turn.
5. **Finding 5 — threshold adjustment.** Parameter tuning, secondary to the structural fix.
6. **Finding 3 — bias mitigation.** Important safeguard but not blocking.

---

## Key Insight

The experiment 12 confer fixes script already demonstrates the correct pattern. Embedded focused extracts plus specific questions equals efficient CX. The experiment orchestrators for experiments 17 and 18 reverted to dumping the whole file plus naming a boundary for automated dispatch. The solution is to systematise what experiment 12 did manually.
