# CDSFL as an AI Interaction Design Bench — Live Analysis from Experiment 36

**Date:** 7 April 2026, ~02:55 BST. Experiment 36 is running live while this analysis is written.

## The Claim

CDSFL has evolved from a code review methodology into a functioning bench for designing better AI interaction patterns. Over Exp 29–36, the system has been iteratively redesigning how AI models communicate, deliberate, and converge — and each design change was driven by observed model behaviour in prior experiments rather than theoretical prediction.

## P-Pass (Falsification)

**Premises:**
1. Over eight experiments we have changed: prompt patterns (FFF→FFAF), topology (relay→star→configurable), inter-model communication (none→directed→blackboard), ITC adaptation (none→change_focus→restart_fresh escalation), convergence mechanics (simple→5-condition gate + stall detector), verification (none→CC2v).
2. Each change was driven by observed model behaviour, not theoretical prediction.
3. The changes improved measurable outcomes: false positive rate (9%→~100% genuine), convergence detection (failed→functional), churn (232 duplicate fixes in Exp 30 → 31 merges resolving 15 findings in a single round via change_focus).

**Falsification attempt 1:** Could improvements be artifacts of changing test articles? Exp 33–36 review different files, so article difficulty varies. However, the same pathological patterns (churn, convergence failure, duplicate generation) appeared across all articles and were addressed by interaction changes, not article changes. The ITC and change_focus improvements respond to model behaviour, not code content.

**Falsification attempt 2:** Could improvements be overfitting to specific model versions? The 5-model panel has been stable since Exp 29. If we swapped models, the patterns might not transfer. **This is the strongest counterargument.** However, the interaction patterns (FFAF, change_focus, CC2v verification) are designed to be model-agnostic — they respond to behavioural signals (duplicate rate, verdict activity, finding status), not model-specific quirks.

**Verdict:** Survives P-pass with the caveat that model-agnosticism is untested with different model panels.

## Dispassionate Analysis

CDSFL started as a code review methodology. Over 36 experiments it has become an adaptive system that modifies its own interaction patterns in response to observed model behaviour.

**Key transition points:**
- **Exp 29:** Insect brain relay proved models can engage in genuine cross-model reasoning.
- **Exp 30:** Fix-level churn revealed models prefer debating solutions over finding bugs → change_focus design.
- **Exp 32:** Meta-experiment showed models self-optimise toward convergence rather than rigour → founder overrides.
- **Exp 35:** Convergence gate failure revealed open_ch permanent blocker → stability-window fix.
- **Exp 36 (live):** FFAF's ANALYSE step producing proper CONFIRMED/UNCERTAIN/REJECTED verdicts from R0. change_focus triggered massive merge activity within one round.

Each experiment is simultaneously a code review AND a test of the interaction patterns. The code review findings are real and useful. The interaction pattern data is equally real and often more valuable.

## Extrapolation

**(a) What generalises:** The principle that structured multi-agent review with explicit state machines (FindingRegistry), adaptive recovery (ITC), and meta-cognitive prompting (FFAF) produces better outcomes than naive "ask multiple models" approaches. This generalises to any task where multiple AI agents collaborate — not just code review.

**(b) Boundary conditions:** The approach requires a well-defined artifact that multiple models can independently examine. It requires a decomposable quality metric (findings → verdicts → convergence). It breaks down for tasks that are inherently subjective or where "correctness" can't be iteratively refined.

**(c) New falsifiable questions:**
- Would FFAF produce the same CONFIRMED/UNCERTAIN/REJECTED distribution on a non-code artifact (e.g., a scientific paper review)?
- Does the change_focus → restart_fresh escalation chain produce faster convergence than always using restart_fresh from the start?
- Is the 5-condition convergence gate transferable to domains beyond code review?

**[SPECULATIVE]** The most significant long-term implication: CDSFL may be demonstrating that the bottleneck in multi-agent AI systems is not model capability but interaction design. The models haven't changed between experiments — only how they talk to each other, what they're told about their own output, and how the system responds to their behaviour.

## Experiment 36 Live Data (as of Round 7)

| Round | Novel | Canon | CONFIRM | CHALLENGE | MERGE | CONFIRMED | OPEN | γ | CC2v |
|-------|-------|-------|---------|-----------|-------|-----------|------|------|------|
| R0 | 30 | 30 | — | — | — | 0 | 30 | 0.000 | — |
| R1 | 10 | 40 | 46 | 6 | 0 | 18 | 40 | 0.000 | — |
| R2 | 5 | 45 | 27 | 8 | 31 | 9 | 17 | 0.626 | — |
| R3 | 4 | 49 | 23 | 3 | 0 | 8 | 15 | 0.645 | — |
| R4 | 1 | 50 | 8 | 10 | 1 | 8 | 12 | 0.675 | — |
| R5 | 6 | 56 | 13 | 9 | 0 | 7 | 14 | 0.671 | — |
| R6 | 7 | 63 | 15 | 2 | 0 | 9 | 18 | 0.651 | 4C/0R/2E |
