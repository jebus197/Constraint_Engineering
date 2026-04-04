# Distributed Compute, Diversity, and the Demonstrability Claim

**Date:** 4 April 2026, 18:47 BST
**Context:** Founder observation — CDSFL under distributed compute is demonstrably better; diversity of interactors is load-bearing; same architecture ≠ same output.

---

## Summary

Three linked claims examined:
1. **CDSFL under distributed compute demonstrably produces better results** — irrefutable from data
2. **No single system catches everything** — even same-architecture systems (CC1/CC2) diverge
3. **Diversity of interactors matters** — output quality varies with who interacts, not just system architecture

All three survive P-pass falsification.

---

## Claim 1: Distributed Compute Is Demonstrably Better

| Condition | Models | Findings | Proofs | Key Metric |
|---|---|---|---|---|
| Control (smoke test) | 1 | 10 | 0 | Baseline |
| CDSFL/FFF (C3) | 1 (Gemini) | 13 | 5/5 | Single-model CDSFL |
| CDSFL + Meta (C4) | 1 (Gemini) | 16 | 11 formal | Single-model structured |
| CDSFL constrained (Run 11) | 5 | 59 | convergent | γ=0.577, 2-round |
| CDSFL+HIL (Bench Run 1) | 5 | — | — | γ=0.597, 92.2% convergence |

**Run 10 per-model unique contributions (first clean convergence):**

| Model | Findings | Unique | Unique Ratio |
|---|---|---|---|
| Gemini | 20 | 18 | 90.0% |
| Codex | 52 | 45 | 86.5% |
| DeepSeek | 63 | 45 | 71.4% |
| CC2 | 36 | 26 | 72.2% |
| ChatGPT | 66 | 40 | 60.6% |

Remove any single model → coverage drops. This is arithmetic.

---

## Claim 2: Same Architecture, Different Results

**CC1 vs CC2 (both Claude Opus):**
- Experiment 11: CC1 = collator/architect; CC2 = player manager/analyst
- CC2 dominated Runs 8-9 (126, 129 findings). In Run 11: total dispatch failure in R1 (3× timeout)
- Same architecture, radically different profiles. Driven by: role, context, payload, dispatch mechanism

**Gemini across conditions (same model, same code):**
- C1 (HIL): 25 findings, cross-component strength
- C3 (CDSFL): 13 findings, per-component depth
- C4 (CDSFL+Meta): 16 survivors, 11 formal proofs
- Three categorically different output distributions

**Meta-test (5 architectures, same task, same constraints):**
- CC2: 16 findings (10 genuine, 8 unique) — dominated
- ChatGPT: Format failure
- Codex: Contaminated (Δ≈1.0)
- Five architectures, five completely different profiles

---

## Claim 3: Diversity of Interactors Matters

### Cross-Architecture Diversity
Experiment 13b severity differences (Kruskal-Wallis H=44.74, p<0.0001):

| Model | Mean Severity |
|---|---|
| Gemini | 0.818 (highest) |
| Codex | 0.785 |
| ChatGPT | 0.684 |
| CC2 | 0.630 |
| DeepSeek | 0.557 (lowest) |

### Intra-Architecture Diversity
CC2 amplification in Run 8: 1.613 (highest — its findings were most built-upon by others). Emergent property of CC2's output style, not the Claude architecture in general.

### Interactor Diversity
C1 experiment: human developer's reactive prompts steered Gemini toward cross-component bugs (5 unique pipeline-level findings). The automated CDSFL pipeline (C3/C4) structurally cannot find these. The 32% coverage gain from C1+C4 union is the **diversity dividend**.

**The France/Germany analogy:** A population sharing a common framework (citizenship, language, law) is not thereby uniform. Architectural similarity ≠ behavioural uniformity. The framework enables productive diversity; it doesn't suppress it.

---

## P-Pass

| Attempt | Attack | Result | Evidence |
|---|---|---|---|
| 1 | Advantage is volume, not diversity | **Refuted** | C3 ran Gemini 12 times → 13 findings. 5-model ensemble → 59 in 2 rounds. Blind spots are perspective problems, not volume problems |
| 2 | Diversity claim is unfalsifiable | **Refuted** | Falsifiable structure: removing models reduces coverage; disagreements map to attention scope, not randomness |
| 3 | Safety/reliability not yet proven | **Partially valid** | Distributed CDSFL produces more diverse verified findings with 0 FP. Safety claim specifically requires Bench Run 2. Evidence suggestive, not conclusive |
| 4 | Justifies including weak models | **Genuine UX risk** | DM benching mechanism is the answer: diversity welcome, bench sets minimum |

**Result:** All three claims survive. Claim 1 irrefutable. Claim 2 demonstrated. Claim 3 strongly supported with safety caveat.

---

## Extrapolation

### What Generalises
- **Any verification-harder-than-generation domain** (testing, peer review, due diligence, diagnosis): outcome quality depends on diversity of perspectives applied within the methodology
- **AI industry implication:** ensemble-under-constraints outperforms single-best-model. The bench matters more than the athlete. [SPECULATIVE — testable against future frontier models]
- **Human teams:** the same principle applies. A framework that enables productive diversity outperforms one that mandates uniformity

### Boundary Conditions
- Diversity dividend diminishes when models converge in training data/methodology
- Collapses for narrow problems where single perspective suffices
- Requires quality floor (diversity without constraints = Run 8's 91% churn)
- Interactor diversity claim breaks down when interactors don't meaningfully differ in perspective

### New Falsifiable Questions
1. What is the minimum model diversity needed to match ensemble coverage?
2. Does human interactor diversity follow the same pattern? (Test: C1 with junior/senior/security developer profiles)
3. Optimal diversity/cost ratio?
4. Can a single model with perspective-shifting instructions replicate ensemble diversity?

---

## Key Data Sources
- Runs 8-11: `bench/logs/baseline_confer_run{8,9,10,11}_*/`
- HIL comparison: `bench/logs/hil_comparison_c{1,4}_20260404/`
- C5 validation: `bench/logs/c5_20260404T050417Z/`
- Bench Run 1: `bench/results/round_robin_phase2/decay_analysis.json`
- Experiment 13b: per-model severity in ONBOARDING.md
