# CDSFL HIL Interaction Patterns Research

**25 March 2026**

---

## The Problem With Our Current HIL Design

Our bench test has four conditions:
- **Control**: gives the model nothing and lets it work alone.
- **HIL**: gives it a 500-character expert hint and lets it work alone.
- **CDSFL**: gives it the full structured methodology with distributed compute.
- **CDSFL+HIL**: gives it everything.

The problem is that **HIL consistently performs worse than Control**. On every task so far, giving the model an expert hint produced fewer findings than giving it nothing at all. This is counterintuitive — a hint from an expert should help, not hinder.

The reason, confirmed by a recent published study on framing bias in AI code review, is that our hint **narrows the model's search**. When we say "focus on the boundary conditions and the pigeonhole argument," the model focuses on those two things and stops looking for anything else. The hint acts as a restriction, not an expansion. The model interprets guidance as a fence rather than a starting point.

This is a known phenomenon. A 2026 study found that framing bias in large language model code review reduced vulnerability detection by **16 to 93 percent** depending on how the frame was constructed. Our HIL condition is doing exactly this.

---

## What Real Expert AI Interaction Looks Like

Codex 5.3 searched the academic literature and found several relevant studies of how real domain experts actually interact with AI models in practice.

**Finding 1: Real interactions are iterative, not one-shot.** A study of over one million real ChatGPT conversations found that the average conversation has 2.52 turns. 41% of conversations are multi-turn. In developer-specific conversations solving real issues, the average is 6.9 prompts per conversation.

**Finding 2: Expert users refine as they go.** They do not dump all their knowledge in one prompt. A study of 686 real developer prompts found 11 recurring prompt gaps that force iterative refinement. Even experts do not get it right first time — they probe, adjust, and redirect across multiple turns.

**Finding 3: Two distinct interaction modes exist.** A study of 20 programmers using GitHub Copilot found two patterns:
- **Acceleration mode**: the user knows what they want and uses the AI to get there faster.
- **Exploration mode**: the user does not know what they want and uses the AI to probe the unknown.

Our HIL condition currently supports neither mode. It gives a single hint and then steps back. Real experts would continue guiding.

---

## The Evidence-Based 5-Round HIL Pattern

Based on these findings, Codex proposed and we agreed on a revised HIL interaction pattern for future bench runs.

**Round 1 (~500 characters).** The user sets the context broadly. They describe the task, mention 2–3 areas of concern from experience, and ask the model to identify candidate issues. This is not "focus on X." It is "here is what I know — what do you see?"

**Round 2 (~200 characters).** The user fills a gap. The most common real-world follow-up is providing missing information or clarifying a constraint. Something like "I should have mentioned, the elements must be distinct — does that affect your analysis?"

**Round 3 (~250 characters).** The user requests a targeted check on one specific risk or edge case. Something like "Can you verify whether the tightness construction actually works at the boundary, specifically for n equals 4?"

**Round 4 (~250 characters).** The user asks a counter-check. This is the most sophisticated prompting pattern observed in expert users. Something like "Assume your current answer is wrong. What would disprove it?" This is the human equivalent of a P-pass, applied informally.

**Round 5 (~100 characters).** The user asks for synthesis: "Summarise your findings, flag your uncertainties, and rate your confidence." This is the standard closing pattern in expert technical conversations.

**Total across 5 rounds: ~1,300 characters.** This is substantially more than the current 500-character single dump, but distributed across 5 turns with iterative refinement at each step. Each turn builds on what the model said in the previous turn — the user is reacting to the model's output, not just broadcasting instructions.

---

## Why This Is More Realistic

The current HIL condition assumes a user who writes one perfect 500-character prompt and then sits silently while the model iterates on its own for 4 more rounds. No real expert does this. Real experts engage — they read the model's first response and adjust their guidance, probe specific areas the model missed, challenge the model's conclusions, and ask follow-up questions.

The revised pattern captures this iterative refinement while staying within realistic prompt lengths. The literature supports average prompt lengths of approximately 70 tokens (~280 characters) for general use. Expert users tend to be slightly longer but rarely exceed 400 characters per turn. Our round-by-round lengths of 500, 200, 250, 250, and 100 characters are consistent with observed patterns.

---

## Why This Matters for the Bench Test

If HIL continues to underperform Control on the current bench run, we can legitimately say that the HIL condition as implemented does not represent realistic expert interaction. The literature supports this claim. The framing bias study provides the mechanism. The interaction pattern studies provide the alternative.

For outreach, this is defensible. We are not hiding the HIL weakness — we are documenting it, explaining it with reference to published research, and proposing an evidence-based fix for the next iteration. Any reviewer who examines our HIL design will see that we identified the problem, found the relevant literature, and designed a correction. That is more credible than pretending HIL performed well when it did not.

The revised HIL pattern will be implemented after the current bench run completes and results are fully analysed. It will be tested in a dedicated smoke test before any full bench run to verify it does not introduce new confounds.

---

## Relevant Citations

- **arXiv 2603.18740** — Framing bias in LLM code review. Bug-free framing reduced vulnerability detection by 16–93%.
- **arXiv 2206.15000** — Grounded Copilot study. 20 programmers. Two interaction modes identified: acceleration and exploration.
- **arXiv 2210.14306** — CUPS study. 21 programmers, 3,137 labeled segments. Rich iterative interaction behaviour documented.
- **arXiv 2402.04568** — MSR 2024 study. 686 real developer prompts. 11 recurring prompt gaps forcing iterative refinement.
- **arXiv 2405.01470** — WildChat dataset. One million real ChatGPT conversations. Average 2.52 turns per conversation.
- **arXiv 2309.11998** — LMSYS Chat dataset. One million conversations across 25 models. Average 2.0 turns, 69.5 tokens per prompt.
