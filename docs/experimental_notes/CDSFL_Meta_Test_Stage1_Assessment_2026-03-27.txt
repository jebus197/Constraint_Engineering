# CDSFL Meta-Test Stage 1 Assessment — Did the Models Actually Use the Model?

**27 March 2026**

---

## The Core Question

How much of Stage 1 was models actually using the CDSFL model as their analytical framework, and how much was simply structured peer review where models reviewed a document using their native analytical capability?

**The honest answer:** Stage 1 was almost entirely structured peer review. The models reviewed the mathematical model as an object. They did not operate under the model as their analytical framework.

---

## The Evidence

No model received the CDSFL formal model as a system prompt. The mathematical appendix was injected as document content to be reviewed, not as an operating framework that would shape how each model reasons.

- **Gemini** received no system prompt at all. The mathematical appendix went straight into the API contents field as user content.
- **DeepSeek** received a single generic line: "you are a mathematical reviewer specialising in formal model verification." That is not CDSFL — that is a role label.
- **ChatGPT** received the entire prompt, instructions and both documents, piped as a single blob via the command line interface. It treated the whole thing as a document to summarise rather than a task to execute. This is why it produced a qualitative assessment instead of structured findings.
- **CC2** received the documents as an agent prompt with instructions to find issues. It was bare Opus 4.6 with no CDSFL system framing.
- **CX** received it as a Codex task description — no CDSFL framing. And then it read Gemini's output file anyway, so its results are invalid.
- **CC1 (me as manager)** used the measurement formulas (H(x), severity, capability fingerprints) to score the output after the fact. But I did not use the stop predicate, the V-hat estimator, or the metacognitive feedback protocol to drive real-time decisions. My stopping decision was informal.

---

## What Using the Model Would Have Looked Like

If each model had received the CDSFL core formal model as a system prompt, they would have been operating under the framework, not just reviewing it. This means:

- Classifying constraints as HARD or SOFT before analysis
- Running iterative falsification — multiple internal passes, not just one scan
- Self-monitoring for convergence, verification rate, and independence
- Producing findings with explicit constraint classifications and verifiable claims as a natural consequence of the framework, not as a bolted-on output format

The distinction matters because Stage 1 tells us how good each model is at reviewing mathematics. It does not tell us whether CDSFL makes models better at reviewing mathematics. That is a different question entirely and Stage 1 did not test it.

---

## Player Performance Table

| Rank | Model | CDSFL Usage | Findings | Genuine Fixes | Key Strength | Key Weakness |
|------|-------|-------------|----------|---------------|--------------|--------------|
| 1 | CC2 (Opus 4.6) | Partial — constraint labels, cross-module refs | 16 | 10 (8 unique) | Deepest analysis, highest mean abstraction index | Native Opus 4.6 capability, not framework-driven |
| 2 | Gemini 3.1 Pro | Partial — constraint labels | 6 | 6 (100% verified) | Perfect verification rate | Truncated output (MATH-06 cut off) |
| 3 | DeepSeek V3.2 | Minimal — just constraint labels | 5 | 3 unique | Low cost, some genuine unique finds | Surface scanning, known churn behaviour |
| 4 | CC1 (manager) | Scoring apparatus only | — | — | Correctly applied H(x), severity, fingerprints | Did not compute V-hat, check stop predicate, or apply metacognitive feedback |
| 5 | ChatGPT 5.4 | None | Qualitative only | — | Sharp qualitative observations (circularity risk, overparameterisation, dependence estimation) | Complete format failure — no constraint classification, iteration, or self-monitoring |
| 6 | CX (Codex/GPT-5.4) | Invalid | — | — | — | Read Gemini's file, reproduced findings verbatim. Adoption delta ~1.0. Contamination was operational not capability failure. |

---

## System Prompt Versus User Prompt

Would injecting CDSFL at system level have made a difference?

**For ChatGPT — almost certainly yes.** ChatGPT treated the user prompt as a document to summarise. If the CDSFL model had been the system prompt and the mathematical appendix the user prompt, ChatGPT would likely have produced structured output. The format failure was a prompt engineering failure, not a capability failure.

**For DeepSeek — possibly.** Its known churn behaviour might be architectural. But a system prompt enforcing "iterate and discard findings that do not survive self-falsification" could have produced fewer but deeper findings. Genuinely unknown.

**For Gemini and CC2 — marginal.** Both already produced high-quality structured output. The main difference would be iteration. The CDSFL model prescribes multiple passes with self-monitoring between them. System-level CDSFL would instruct: "run up to five internal falsification passes, stop when consecutive passes yield no new hard findings." This could have surfaced additional findings or confirmed convergence earlier.

**For CX — orthogonal.** The contamination problem is not about prompt level. Isolation was the issue.

---

## Problems Encountered

1. **CX contamination.** The Codex sandbox has read access to the entire working directory. Gemini's output file was already written when CX started. CX read it and reproduced all six findings. Root cause: no output isolation protocol.

2. **ChatGPT format non-compliance.** The full 51 KB prompt (instructions and two complete documents) was piped via the command line interface. ChatGPT likely treated the combined input as a document to assess. Root cause: system vs. user content boundary was not enforced.

3. **CC2 command line hang.** The command using cat piped to claude with the print flag hung for over six minutes producing zero bytes of output. Root cause: likely a pipe buffer deadlock with the large input. Fixed by switching to the Agent subagent mechanism, which completed in about four minutes.

4. **Gemini output truncation.** Finding MATH-06 was cut off at 8176 characters despite a 16384-token maximum output setting. Root cause: the model hit its natural generation limit before the token cap. The finding was partially usable.

5. **DeepSeek token limit error.** The script specified 16384 maximum tokens but DeepSeek's limit is 8192. This produced an HTTP 400 error. Pure configuration error, fixed immediately.

6. **No model operated under CDSFL.** This is the fundamental design gap. The experiment measured models reviewing the model, not models using the model. Root cause: the blind pass prompt was designed as a review task, not as a CDSFL-guided analysis task.

---

## What Changes for Stage 2

**The single most important correction:** inject the CDSFL core formal model as a system prompt for every participating model. Every API call will use the system prompt field. The mathematical appendix and other models' findings go in the user prompt as the object of analysis.

This transforms the experiment from "models reviewing a document" to "models operating under CDSFL while reviewing the CDSFL model" — the framework examining itself using itself.

**Three mathematical additions needed before Stage 2:**

1. **Anti-parroting mechanism** — reproduced findings automatically excluded from composite yield calculations
2. **Manager selection function** — editorial judgment has formal mathematical representation
3. **Contribution discount function** — benching weak players has a formal threshold rather than informal judgment

The plan is fully written up for cold-start resumption.
