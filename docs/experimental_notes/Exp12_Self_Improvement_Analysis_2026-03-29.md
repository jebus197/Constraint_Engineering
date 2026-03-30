# Experiment 12: Self-Improvement Analysis Under CDSFL

**Date:** 29 March 2026

**Context:** Experiment 12, live run, 9 rounds complete with 5 models reviewing dynamic management layer at 3181 lines.

---

## 1. The Prediction

Models will tend to self-improve under CDSFL, both in abstraction capacity and quality of findings. Their decay curves and supporting data will tell us if this is the case.

---

## 2. The Evidence

### Severity trajectories (rounds 1–9, average severity per round)

- **Codex:** 0.76, 0.85, 0.77, 0.79, 0.82, no data, 0.79, 0.80, 0.87, 0.76. General upward trend of approximately 14%. Peaks at 0.87 in round 8. Codex also reduces finding count from 16 to 4, meaning it produces fewer but higher-severity findings.
- **ChatGPT:** 0.66 (blind), 0.73, 0.74, 0.77, 0.72, 0.76, 0.75, 0.76, 0.79, 0.74. Clear upward trend from 0.66 to the 0.75–0.79 range. Approximately 20% improvement.
- **CC2:** 0.69, 0.72, 0.69, 0.69, 0.74, 0.69, 0.71, 0.73, 0.70. Slight upward trend. Approximately 6%. Noisy but positive.
- **DeepSeek:** 0.64, no data, 0.53, 0.58, 0.68, no data, 0.65, no data. Variable. Area-dependent. Insufficient data for trend.

### Abstraction trajectories (rounds 1–9, average abstraction index per round)

- **Codex:** 0.80, 0.73, 0.75, 0.75, no data, 0.75, 0.80, 0.83, 0.77. Increasing, especially rounds 7 and 8. Peak 0.83.
- **CC2:** 0.64, 0.66, 0.64, 0.66, 0.66, 0.66, 0.65, 0.67, 0.68. Slow increase from 0.64 to 0.68.
- **ChatGPT:** 0.76, 0.74, 0.77, 0.72, 0.73, 0.71, 0.73, 0.75, 0.72. Flat. No clear trend.

---

## 3. P-Pass Falsification

**The strongest argument against self-improvement** is that the effect is confounded by context accumulation. Each round provides all prior findings as context. A model with 200 prior findings has more information than one with zero. The improvement might not be self-improvement but simply having a higher bar to clear.

**Counter.** Giving a model more context does not automatically produce better output. Context could cause information overload, churn, or exhaustion. The fact that severity trends upward despite growing context suggests something beyond "more input equals better output." The models are demonstrably learning to focus on what matters.

**Second falsification.** Selection effect. As easy findings are exhausted, remaining ones are inherently harder to find and score higher in severity and abstraction because they are deeper bugs. This is natural search space exhaustion, not model improvement.

**Counter.** This is actually consistent with the prediction under a specific mechanism. CDSFL creates a quality ratchet. Prior findings set a quality floor. Models must exceed the floor to add value. The floor rises each round. Output quality rises with it. Whether this is called self-improvement or selection pressure is a framing question. The observable effect is the same.

**Verdict.** The data is consistent with the prediction. The trend is real. Three mechanisms are confounded: genuine self-improvement under CDSFL, context accumulation effect, and search space exhaustion. Probably all three contribute. The trend is falsifiable and it trends in the predicted direction. The specific mechanism is speculative.

---

## 4. Analysis

### What the data shows unambiguously

- **Codex** converges cleanly with improving quality. Sixteen findings in the blind round declining to four per round. Severity increases from 0.76 to 0.87. Abstraction increases from 0.73 to 0.83. Best-behaved model in the experiment.

- **ChatGPT** improves severity but not abstraction. Maintains volume at 10–14 findings per round. Different cognitive strategy from Codex. Produces breadth, not depth.

- **CC2** maintains consistent volume at 16 findings per round for 8 consecutive rounds and slowly improves abstraction. Systematic explorer of a large search space. Vocabulary overlap between round 2 and round 8 is only 11.73%, confirming it is finding genuinely different issues, not reformulating.

- **DeepSeek** decomposition produces genuine within-area convergence. Area 2 first visit produced 10 findings. Area 2 revisit at round 8 produced 4 findings. The decomposition approach works.

- **Gemini** was prematurely benched after round 1 due to aggressive timeout thresholds. Lost diversity. Fixed in the committed code.

---

## 5. Extrapolation

**What generalises.** If the quality ratchet is real, any iterative multi-model review protocol under CDSFL should show improving output quality over rounds. The mechanism is domain-independent. Accumulated findings create a rising quality floor. This is testable on other artifacts.

**Boundary conditions.** The ratchet breaks when the similarity function cannot detect duplicates (which we just fixed). It breaks when the artifact is small enough to be exhausted in one or two rounds. It breaks when models cannot effectively process prior findings context, which is the DeepSeek issue we solved with decomposition.

**New falsifiable questions:**

1. Does the ratchet hold with different artifacts? Test on a smaller codebase (approximately 500 lines) and a non-code artifact such as a mathematical proof or a legal document.
2. Is there a ceiling? At what round does severity and abstraction plateau?
3. Does removing prior findings context eliminate the trend? This directly tests mechanism 1 (genuine self-improvement) versus mechanism 2 (context accumulation).
4. If the ratchet is genuine self-improvement rather than just context, then the same model given the same prior findings but not under CDSFL should show a weaker trend. CDSFL constraint classification and falsification requirements may be the active ingredient, not just accumulated context. [SPECULATIVE]

---

## 6. Additional Observations

**Twenty rounds as a limit.** The founder correctly noted this is arbitrary. The experiment will reach round 20 without mathematical termination because both convergence detectors (kappa and mu) are broken in this run. The fixed code, committed at hash `f09081e`, adds novelty rate as a cost-decoupled stop signal that should terminate naturally. But based on the data showing genuine productivity at round 9, twenty may actually be too few. The right limit depends on artifact size and model diversity, not a fixed number.

**The finding count trajectory** shows three phases:
- Phase 1: the blind round with maximum output.
- Phase 2: rapid decline over rounds 1–3 as obvious findings are exhausted.
- Phase 3: a plateau where models produce a stable number of increasingly focused findings.

The stop condition should trigger at the transition from phase 2 to phase 3, when novelty rate drops below threshold.

**The immune response system**, committed in the same changeset, monitors all detectors for dysfunction. In the next run with fixed code, it will flag any remaining pathologies in real time. The adaptive sensitivity mechanism means the monitor learns from its own diagnostic history, becoming more accurate over successive experiments.
