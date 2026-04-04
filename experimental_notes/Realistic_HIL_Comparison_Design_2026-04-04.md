# Realistic HIL vs CDSFL/FFF: Experimental Design

**Date:** 4 April 2026, 00:30 BST
**Context:** User correction — prior proposed comparison gave non-CDSFL conditions CDSFL-exclusive features. Redesigned with evidence-based realistic HIL as control.

---

## The Problem with the Previous Design

The 4-condition comparison proposed in the Constraint Box Confirmation note was flawed. All four conditions gave the model CDSFL-exclusive features:

| Feature | CDSFL-exclusive? | Given to non-CDSFL conditions? |
|---------|------------------|-------------------------------|
| Cell-level decomposition | Yes (constraint box routing) | ✗ Should not have been |
| Fresh model instances | Yes (IT Crowd principle) | ✗ Should not have been |
| Multi-turn conversation mode | Yes (FFF iteration) | ✗ Should not have been |
| Structured falsification | Yes (FFF protocol) | ✗ Correctly withheld |

The founder's correction: if you give the control condition the constraint box, fresh instances, and multi-turn conversation, you are testing FFF in isolation — not testing CDSFL as a system. The comparison must use what developers **actually do** as the baseline.

## What Developers Actually Do (Evidence Base)

### Interaction Patterns (6 empirical studies)

| Metric | Finding | Source |
|--------|---------|--------|
| Average prompt length | ~15 words (~70 tokens, ~280 chars) | LMSYS Chat (arXiv 2309.11998) |
| Average conversation length | 2.52 turns (general), 6.9 (developer) | WildChat (arXiv 2405.01470) |
| Token ratio (LLM:developer) | 14:1 | CodeChat (arXiv 2509.10402) |
| Knowledge gaps in prompts | 54% (11 recurring gap types) | MSR 2024 (arXiv 2402.04568) |
| Re-prompts (struggle signal) | 7% | MSR 2024 |
| Interaction modes | Acceleration (known goal) + Exploration (unknown) | Grounded Copilot (arXiv 2206.15000) |
| Multi-turn conversations | 41% of all conversations | WildChat |

### Framing Bias (confirmation bias in LLM code review)

| Finding | Source |
|---------|--------|
| Bug-free framing reduces vulnerability detection by 16–93% | arXiv 2603.18740 |
| Injection flaws most susceptible to framing | arXiv 2603.18740 |
| Debiasing via metadata redaction restores detection in 94% of autonomous cases | arXiv 2603.18740 |

### Best Available Structured Prompting (Non-CDSFL)

| Approach | Baseline | With structure | Source |
|----------|----------|----------------|--------|
| Meta semi-formal reasoning (patch verification) | 78% | 93% | arXiv 2603.01896 |
| Meta semi-formal (fault localization, Top-5) | +5–12 pp improvement | | arXiv 2603.01896 |
| Meta semi-formal (code QA) | — | 87% | arXiv 2603.01896 |

Meta's approach: structured checklist requiring explicit premises, execution path tracing, formal conclusions. No model training required. Code-execution free. 2.8x more execution steps than unstructured.

## Experimental Design: Three Conditions

### Condition 1: Realistic Developer HIL (Baseline)

Represents what a competent developer actually does when using an LLM for code review, based on empirical evidence.

**Setup:**
- Same model (Gemini 2.5 Pro)
- Same code (full immune pipeline — NOT decomposed into cells)
- Single session, accumulated context
- No structured protocol, no FFF, no SymPy verification

**Interaction pattern (evidence-based):**
- **Round 1** (~300 chars): Broad review request. "Review the immune cell pipeline code for bugs, edge cases, and correctness issues. Focus on the voting logic and mathematical operations." This reflects the typical developer prompt: task description + 1–2 areas of concern.
- **Round 2** (~150 chars): Gap-fill or redirect based on R1 output. "What about the boundary conditions — what happens when all scores are zero or when there's only one model responding?"
- **Round 3** (~200 chars): Follow-up on something the model raised. E.g., "Can you verify that specific claim mathematically? Show your working."

Total: ~650 chars across 3 turns. This is generous — the median developer interaction is 2.52 turns at ~280 chars each (~700 chars total). We are giving the baseline condition the benefit of the doubt.

**What this condition does NOT get:**
- Cell-level decomposition (sees entire pipeline)
- Fresh instances (one session, accumulated context)
- FFF pressure ("press harder", convergence forcing)
- SymPy/z3 verification (model's own analysis only)
- Structured falsification protocol

### Condition 2: Best-Practice Structured HIL (Generous Control)

Represents the most sophisticated non-CDSFL approach currently documented in the literature: Meta's semi-formal reasoning checklist applied to the same code review task.

**Setup:**
- Same model (Gemini 2.5 Pro)
- Same code (full immune pipeline — NOT decomposed)
- Single session, accumulated context
- Meta's structured checklist template (premises → execution trace → formal conclusion)
- No FFF, no SymPy verification, no fresh instances, no cell-level routing

**Interaction pattern:**
- **Round 1** (~500 chars): Provide code + Meta-style structured reasoning template. "For each function in this code, construct a logical certificate: (1) state your premises about what the function should do, (2) trace the execution path through concrete examples, (3) derive a formal conclusion about whether it is correct. Flag any case where your premises and your trace disagree."
- **Round 2** (~250 chars): Based on R1 output, ask for deeper analysis on the weakest areas. "Your analysis of [X] was surface-level. Apply the same certificate structure but with adversarial inputs."
- **Round 3** (~200 chars): Counter-check. "Assume your current conclusions about [specific function] are wrong. What evidence would disprove them?"

Total: ~950 chars across 3 turns. This is MORE than what Meta's paper describes (they use a single structured template). We are being generous to the control.

**What this condition gets that C1 doesn't:**
- Structured reasoning template (semi-formal)
- Explicit instruction to trace execution paths
- Counter-check round

**What this condition still does NOT get:**
- Cell-level decomposition
- Fresh instances
- FFF iteration pressure (no "press harder" until convergence)
- SymPy/z3 mechanical verification
- Multi-round falsification protocol

### Condition 3: CDSFL/FFF (Already Completed)

The immune cell review experiment results we already have.

**Setup:**
- Same model (Gemini 2.5 Pro)
- Code decomposed into individual cells (~2K chars each, not 244K full codebase)
- Fresh instance per cell (zero accumulated context)
- Full CDSFL/FFF protocol with "press harder" until convergence or churn
- SymPy verification of all mathematical claims

**Results (already obtained):**
- 12 rounds across 4 cells
- 13 genuine findings
- 5/5 SymPy-verified mathematical proofs
- Critical architectural flaws found: dead else block, 1.5x veto barrier, orthogonal ganging, state mutation leak, math regex hijack

## Predictions

| Metric | C1 (Realistic HIL) | C2 (Semi-formal) | C3 (CDSFL/FFF) |
|--------|--------------------|--------------------|-----------------|
| Total findings | 3–8 | 6–12 | 13 (actual) |
| Mathematical proofs | 0 | 0–1 | 5 (actual) |
| Dead code detection | 0 | 0–1 | 1 (actual) |
| False positives | 2–5 | 1–3 | 0 (actual) |
| Verification rate | 0% | <20% | 100% (actual) |

**Rationale for predictions:**

- **C1** will produce surface-level findings similar to Runs 8–10 (1,001 findings, 0 proofs). The broad scope and short interaction prevent deep analysis. The Helper T dead else block requires mathematical reasoning that unstructured prompting does not force. Predicted finding types: variable naming, error handling suggestions, style issues, possibly one genuine logic concern if the model happens to focus on it.

- **C2** will outperform C1 because the structured template forces execution tracing. Meta's own data shows ~15 percentage point improvement. But without cell-level decomposition, the model's attention is split across the full pipeline. Without SymPy, mathematical claims remain unverified. Without FFF iteration, the model stops after its first pass — it has no mechanism to push past surface analysis. The structured template improves *quality per finding* but does not solve the *attention routing* problem.

- **C3** results are already in hand. The constraint box — protocol + focus + context — produced qualitatively different output.

**Key discriminating prediction:** If C2 approaches C3, then the constraint box effect is primarily about structured reasoning (Meta's approach captures most of the value). If C2 ≈ C1 ≪ C3, then structured reasoning alone is insufficient — the full constraint box (routing + fresh instances + FFF iteration + mechanical verification) is the load-bearing system.

My prediction: C2 will fall between C1 and C3, closer to C1 than to C3. The constraint box is a system, not a single technique.

## Practical Implementation

**Cost:** Two additional Gemini sessions. ~15 minutes of interaction time. Negligible token cost compared to the 47-round monolithic runs.

**Execution order:** C1 first (to avoid learning effects biasing the structured condition), then C2. C3 already complete.

**Verification:** All findings from C1 and C2 will be independently verified using SymPy (by CC, not by the model under test) to establish ground truth. This ensures the comparison is on *verified correctness*, not *claimed findings*.

**Blind evaluation:** The founder evaluates findings from all three conditions without knowing which condition produced them.

## Analysis

The experiment as designed isolates three levels of structure:

1. **No structure** (C1): Realistic developer interaction. Tests the null hypothesis: does an LLM with good code and a competent user already find critical bugs?

2. **Reasoning structure only** (C2): Meta's semi-formal approach. Tests whether structured prompting without the full constraint box captures the value. This is the strongest available non-CDSFL comparator.

3. **Full constraint box** (C3): CDSFL/FFF. Tests the complete system: protocol + routing + fresh instances + mechanical verification.

The design is fair to the control conditions. C1 gets more interaction than the median developer provides. C2 gets the most sophisticated structured prompting technique currently published. Neither is artificially weakened. If CDSFL/FFF still dominates, the result is meaningful.

The design is also falsifiable. If C2 matches C3, the constraint box thesis is weakened — structured reasoning alone would suffice. If C1 matches C2, Meta's semi-formal approach adds no value beyond what a competent developer already achieves. Both outcomes would be informative.

## Extrapolation

**What generalises:** If the constraint box dominates structured reasoning alone, the implication extends beyond code review. Any analytical domain where attention management matters — legal document review, medical literature synthesis, engineering design verification — would benefit from decomposition + fresh instances + iterative falsification, not just better prompting templates. The mechanism is not "better questions" but "better allocation of cognitive resources."

**Boundary conditions:** This breaks down when (a) the problem genuinely requires holistic system understanding (cross-cell interactions in the immune pipeline), (b) the constraint box is over-specified to the point where the model cannot explore (not observed yet — FFF's "press harder" actively prevents this), or (c) the decomposition itself introduces errors by severing dependencies between components.

**New falsifiable questions:**
1. Does the constraint box advantage scale with problem complexity, or does it converge with structured prompting for simple problems?
2. At what decomposition granularity does the advantage peak? Cell-level for our codebase, but is there an optimal ratio of focus-to-complexity?
3. Does Meta's semi-formal reasoning combined with cell-level decomposition (but without FFF iteration or fresh instances) approach CDSFL performance? This would isolate the contribution of routing from the contribution of protocol.
4. Is SymPy verification load-bearing, or does it merely confirm what FFF already identified? If C3's findings are reproducible without SymPy, the verification step is validation, not discovery.
5. [SPECULATIVE] The 14:1 token ratio (LLM:developer) in typical interactions suggests that developers are massively under-investing in prompt quality relative to model output. CDSFL may work partly because it forces the *operator* to invest proportionally — the constraint box constrains the operator's laziness as much as the model's attention.

## References

- arXiv 2603.01896 — Ugare & Chandra (Meta). Agentic Code Reasoning. Semi-formal reasoning, 78%→93% accuracy.
- arXiv 2603.18740 — Confirmation bias in LLM code review. Framing reduces detection 16–93%.
- arXiv 2509.10402 — Developer-LLM Conversations. 14:1 token ratio, interaction pattern analysis.
- arXiv 2405.01470 — WildChat. 1M conversations, 2.52 avg turns.
- arXiv 2309.11998 — LMSYS Chat. 1M conversations, 69.5 tokens/prompt.
- arXiv 2402.04568 — MSR 2024. 686 developer prompts, 11 recurring gaps.
- arXiv 2206.15000 — Grounded Copilot. 20 programmers, acceleration/exploration modes.
