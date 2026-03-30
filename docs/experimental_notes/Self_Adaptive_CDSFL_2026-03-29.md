# Self-Adaptive CDSFL: From Static Methodology to Living System

**Date:** 29 March 2026
**Protocol:** P-pass, analyse, extrapolate, discuss.

---

## The Core Insight

CDSFL is currently a static document. The models read it, follow it, and produce findings. The dynamic management layer adapts the orchestration — adjusting which model gets what work, tracking convergence, detecting pathologies. But the methodology itself, the actual instructions the models receive, never changes. Every model gets the same CDSFL text from `cdsfl_core_formal.md` on every round, regardless of what the system has observed about that model's behaviour.

This is wrong. Or rather, it is incomplete.

We have already demonstrated that CDSFL can improve its own operational infrastructure. Experiment 12 found broken detectors. Post-Experiment 12 fixes repaired them. Experiment 13b verified the repairs and found new issues. Each cycle improved the system's capacity to run the next cycle. That feedback loop is real and measured.

But the loop currently operates through human intervention. A human reads the findings, writes the fixes, commits them, and runs the next experiment. The immune layer detects pathologies and emits recommendations, but nothing acts on those recommendations automatically. The system tells itself what is wrong and then waits for a human to fix it.

The natural extension is to close that loop. When the immune layer detects that a model is underperforming, or falsely reporting its own results, or being unnecessarily blocked from participating, the system should be able to adapt — dynamically and per model — to fix the problem.

---

## Two DeepSeek Pathologies That Prove the Need

DeepSeek has two problems that the current system cannot address.

**First, it gets blocked in the blind round.** The feasibility checker calculates zero probability that DeepSeek can handle the full 3,800-line artifact. It then succeeds via decomposed dispatch in the next round. The blocking was a false positive. Nothing in the system learns from this.

**Second, and more seriously, DeepSeek reports every single one of its 15 findings as VERIFIED FALSE.** Cross-referencing against other models shows that 6 of those 15 findings are independently corroborated by models that report them as VERIFIED TRUE. DeepSeek's self-assessment is systematically wrong. Its findings are valid. Its self-report says they are not.

Any downstream system that trusts the VERIFIED field would silently discard every DeepSeek finding. This is not a minor calibration issue. It is a signal integrity failure. The immune layer should detect it, and the system should adapt its instructions to that model to correct it.

---

## Three Tiers of Self-Adaptation

The architecture proposed here has three tiers, ordered by risk and ambition.

### Tier 1: Parameter Adaptation

The immune layer detects a pathology and adjusts a numerical parameter within bounded limits. For example, when the vocabulary saturation threshold fires too early because of decomposed dispatch, the immune layer lowers the threshold from 10% to 4%. When DeepSeek's feasibility check is a false positive, the immune layer lowers the feasibility threshold for that model.

Every adjustment is bounded, so the system cannot set a threshold to zero or infinity. Every adjustment is logged with a timestamp, the triggering diagnosis, the old value, the new value, and the evidence. Every adjustment is reversible. A damping rule prevents the same parameter from being adjusted more than once every two rounds, eliminating oscillation.

### Tier 2: Prompt Adaptation

The immune layer detects a model-specific behavioural pathology and modifies the CDSFL instructions for that model only. The infrastructure for this already exists but is not connected. The CDSFL registry has a four-layer hierarchy: universal constraints (always enforced), domain-specific overrides, task-specific overrides, and per-model tuning. Layer 4 — the per-model layer — has TOML files for every model but they are never loaded during experiments. Wiring them in is a minimal change.

For DeepSeek's verification problem, the system would prepend a per-model instruction: "Your self-verification output has been consistently miscalibrated in prior rounds. For each finding, re-examine the actual code location cited and explicitly confirm whether the issue exists before marking VERIFIED TRUE or FALSE."

This does not change the core methodology. It adds a model-specific correction for a model-specific defect.

The safety constraint here is already built into the registry architecture. Per-model modifications cannot weaken HARD constraints from the universal layer. The registry enforces monotonicity: lower layers can only tighten constraints, not loosen them.

### Tier 3: Structural Adaptation

The system modifies its own code to fix structural issues. For example, instead of just adjusting the vocabulary threshold, it generates a code patch that adds area-level vocabulary tracking.

This is genuinely dangerous and should be reserved for the future, after Tiers 1 and 2 have proven reliable. Tier 3 would require sandbox execution, full test suite verification before adoption, a human approval gate or an automated P-pass, and automatic rollback on test failure.

---

## P-Pass: What Could Go Wrong?

Five failure modes were identified and falsified.

**Failure mode 1 — Oscillation.** The immune layer adjusts a threshold down, the next round produces too many findings, the immune layer adjusts it back up, and the system oscillates between two states. Fix: a damping factor combined with a minimum of two rounds between adjustments to the same parameter. Bounded parameter ranges prevent extreme values.

**Failure mode 2 — Overfitting.** Per-model prompt adjustments are tuned to one specific artifact and then fail on the next. Fix: reset per-model adjustments when the artifact changes. Only persistent pathology flags (like DeepSeek's verification miscalibration, which persists across experiments) are carried forward.

**Failure mode 3 — Gaming.** A model could theoretically produce findings calibrated to avoid triggering the immune response rather than finding genuine issues. This is a theoretical concern. Current models show no evidence of strategic prompt-gaming. If model behaviour changes across experiments, the immune layer's cross-model contradiction check would detect it: a model that stops finding issues when others still do is a detectable anomaly.

**Failure mode 4 — Corruption cascade.** A bad Tier 2 instruction causes a model to produce worse output, which triggers more immune response, which adds more instructions, which makes output even worse. Fix: a hard cap on per-model instruction budget (500 characters of modifications). Combined with the registry monotonicity rule (cannot weaken universal constraints), this prevents runaway instruction accumulation.

**Failure mode 5 — Loss of comparability.** If models receive different instructions, cross-model statistical comparisons become less valid. Fix: log all per-model modifications and include them as covariates in statistical analysis. The blind round always uses the unmodified universal CDSFL, giving a clean baseline measurement for every model before adaptations kick in.

All five failure modes have bounded mitigations. None are fatal to the architecture.

---

## The Deeper Point: What This Means

You said something worth making explicit. CDSFL should be self-adaptive in the same way that code under CDSFL can become self-improving. That is not an analogy. It is the same principle applied at a higher level of abstraction.

At the code level, CDSFL reviews code, finds problems, the code is fixed, CDSFL reviews the fixed code. The code improves through the methodology.

At the methodology level, CDSFL reviews its own infrastructure, finds problems (broken detectors, miscalibrated models, premature termination), the infrastructure is fixed. The methodology improves through the methodology.

At the self-adaptive level, CDSFL detects model-specific pathologies and adjusts its own instructions to correct them. The methodology adapts itself to the models it works with. The methodology improves itself.

These are three levels of the same recursive structure. Each level applies falsification to the level below it. Code is falsified by CDSFL. CDSFL's infrastructure is falsified by CDSFL applied to itself. CDSFL's instructions are falsified by the immune layer's observation of model behaviour.

The safety properties are the same at every level. Modifications must be bounded. Changes must be auditable. Core constraints cannot be weakened. The system converges (diminishing returns prevent runaway improvement).

What makes this unusual is that it is concrete, not theoretical. We have experimental evidence from three experiments (11, 12, 13b) showing the feedback loop at the infrastructure level. Adding the self-adaptive layer is the natural next step: closing the loop between immune diagnosis and methodology adjustment.

---

## Extrapolation

**What generalises.** Any methodology that operates through a configurable instrument can in principle adapt that instrument based on observed outcomes. Test-driven development could adapt its assertion patterns based on failure modes observed in previous test cycles. Static analysis tools could adjust their rule sets based on which rules produce the most false positives for a given codebase. The principle is: observe the instrument's performance, adapt the instrument's configuration, verify the adaptation improved performance. CDSFL's contribution is making this explicit and bounded by the same falsification framework that governs everything else it does.

**Boundary conditions.** Self-adaptation requires three properties that not all methodologies have:
1. The methodology must produce measurable output (findings with severity, verification status, abstraction indices).
2. The methodology must have configurable parameters (thresholds, prompt instructions, dispatch rules).
3. The methodology must have a mechanism for detecting its own dysfunction (the immune layer).

Without all three, self-adaptation is either unmeasurable, unactionable, or undetectable.

**New falsifiable questions:**
1. Does closing the Tier 1 feedback loop (automatic parameter adjustment) produce measurably better convergence behaviour than manual adjustment? Directly testable by running identical experiments with and without auto-adjustment.
2. Does Tier 2 prompt adaptation improve DeepSeek's verification calibration? Testable in one experiment.
3. What is the convergence rate of the self-adaptive loop? Does it stabilise within three experiments or does it require more? The Duane model can predict this from existing data.

---

## Discussion

The implementation roadmap has five phases:

- **Phase A:** Wire the existing per-model registry into the orchestrator. Minimal change — the infrastructure already exists.
- **Phase B:** Close the Tier 1 feedback loop by adding an `apply_diagnosis` method to `DynamicManager`.
- **Phase C:** Add the verification calibration pathology to the immune layer and write per-model prompt adjustments via the registry.
- **Phase D:** Implement area-level vocabulary tracking as a Tier 1 application.
- **Phase E:** Complete the immune layer's operational scope with dispatch health monitoring.

Phases A and B are the foundation. They could be implemented and tested in Experiment 14 alongside the threshold recalibration. Phase C addresses the DeepSeek verification problem directly. Phases D and E are extensions that build on the earlier phases.

The key architectural decision is that CDSFL's core constraints — the HARD layer — are never modified by self-adaptation. Falsification, constraint classification, precedence ordering: these are fixed. What adapts is the operational parameters and the per-model instructions. The methodology's principles are immutable. Its application is adaptive. This is the difference between a constitution and a policy. The constitution does not change. The policies adapt within constitutional bounds.

This is what makes the self-adaptive claim safe rather than dangerous. The system cannot modify its own foundations. It can only tune its instruments within bounded ranges, logged and reversible, under the same falsification discipline that governs everything else it does.
