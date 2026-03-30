# CDSFL Revised Experiment Plan — Full Discussion and P-Pass Results

**17 March 2026**

---

## The Problem with the Original Plan

The original experiment — still running as Phase 1 — plants known faults in constrained STEM problems and asks models to find them. The results so far show 90–100% detection rates even without CDSFL. This means the tasks are too easy for frontier models, and the maximum improvement CDSFL can show is compressed to 0–10 percentage points.

This is a floor test, not a ceiling test. CDSFL was designed to break the frontier window — meaning it should help most when models are working at the limits of their capability, on novel problems where there is no pre-existing answer key, and where errors are emergent rather than planted.

The original plan proposed a Phase 2 to fix this, but a P-pass against that Phase 2 design found several serious problems.

---

## What the P-Pass Found (5 passes against the plan)

### Pass 1 — Structural Soundness

**Problem 1 — Expert blind evaluation is infeasible at this scale.** The plan called for domain experts to score final outputs. But 25 tasks × 3 schemas × 7 models = 525 outputs. The founder is one person and cannot blind-evaluate hundreds of technical outputs across 10 domains.

**Problem 2 — The per-pass delta measurement had no concrete methodology.** The plan said to track what each pass found that the previous pass missed, but did not specify how to compute this comparison. Human scoring does not scale. Using a language model as judge is circular if it is the same model being evaluated. Automated text diffing misses semantic meaning.

**Problem 3 — Who designs the 25 frontier tasks?** If I design them, they carry my biases. If the founder designs them, he would need domain expertise across all 10 domains. Task design is the hardest unsolved problem in the plan.

### Pass 2 — Schema Applicability

**Problem 4 — Schema B requires tasks with 3 or more distinct modules with independent constraint sets.** Not all frontier tasks are naturally modular. The plan implied all schemas apply to all tasks, but they do not.

**Problem 5 — Schema C is underspecified and costs 3× as much as Schema A.** It needs 3 different models per task at 5 passes each, giving 15 API calls per task versus 5 for Schema A. But the plan did not specify which model pairs to use.

**Problem 6 — Schema A's description contradicted the P-pass protocol.** The plan said Pass 2 uses a fresh context, but the actual P-pass protocol from CLAUDE.md is iterative, where each pass builds on prior findings. These are two different experimental conditions and the plan conflated them.

### Pass 3 — The Fundamental Measurement Problem

**Problem 7 — Phase 2 has no ground truth (most severe).** Phase 1 works because planted faults have known correct answers. Phase 2 deliberately removes this. Without ground truth, improvement becomes a judgment call rather than a measurement.

**Resolution:** use tasks where correctness is objectively verifiable even though faults are not pre-planted. Five categories:
- Mathematical proofs that can be machine-checked
- Code solutions that must pass a test suite
- Engineering designs that must satisfy quantifiable physical constraints
- Chemical syntheses that must obey conservation laws
- Reasoning-about-reasoning tasks where internal consistency is the ground truth

You do not need to pre-plant faults if you can verify outputs. The faults reveal themselves through verification.

### Pass 4 — Confounds and Controls

**Problem 8 — Prompt-length confound.** CDSFL prompts are longer than control prompts. Some improvement might come from prompt quality (better instructions) rather than from the falsification methodology itself. To control for this, we need a **placebo condition** with equally long but non-CDSFL prompts (generic "be careful, check your work, think step by step" instructions of similar length). Without this control, a critic can dismiss any CDSFL improvement as just better prompting.

**Problem 9 — The scale is enormous without scoping.** 7 models × 3 schemas × 25 tasks × 5 passes = 2625 API calls. Needs a core set of 3–4 models for full testing and an extended set for selective validation.

### Pass 5 — What Is Missing

**Problem 10 — The plan ignores Genesis case-study evidence.** The founder has months of documented CDSFL usage where the framework caught real errors. CX finding test design flaws, constitution issues, and so on. This is legitimate case-study evidence and should be presented as complementary data.

**Problem 11 — Adaptive termination needs an algorithm.** "Diminishing returns" is vague. Concrete proposal: if pass N produces zero findings categorised as moderate or severe, terminate. Maximum 5 passes regardless.

**Problem 12 — Diminishing returns from this P-pass itself reached.** Stopping.

---

## What the Revised Plan Looks Like

Three phases remain:
- **Phase 1** — floor test, already running
- **Phase 2** — ceiling test, redesigned
- **Phase 3** — adversarial review with CX

### Phase 2 Changes

1. **Tasks must be verifiable, not just hard.** Correctness can be checked after the model responds, without pre-planting faults.

2. **Scoring uses verification, not expert judgment.** Proofs are machine-checkable. Code solutions get test suites. Designs have computable constraint satisfaction. Scoring is objective and scalable.

3. **A placebo control condition is added.** Three conditions per task:
   - Bare prompt (control)
   - Full CDSFL with P-passes
   - Placebo: equally long generic instructions, same number of passes, without CDSFL's specific falsification method

   If CDSFL beats placebo, the improvement is from the method, not just from longer prompting.

4. **Schema applicability is per-task, not universal.** Schema A (monolithic 5-pass) applies to all tasks. Schema B (modular 4+1) applies only to tasks with 3 or more identifiable subsystems, tagged at design time. Schema C (cross-model adversarial) applies to ~10 of 25 tasks with 3 model pairs chosen to maximise training-bias diversity.

5. **Core versus extended model split.** Core models for full testing: Sonnet 4 with thinking, GPT-4o, and Gemini Pro (one reasoning-capable model per provider family). Extended models for validation only: Sonnet 4 standard, o3-mini, Gemini Flash, and Llama 3.3.

6. **Adaptive termination algorithm.** Pass N terminates if it produces zero findings categorised as moderate or severe. Maximum 5 passes regardless.

7. **A Genesis case-study appendix** documenting 5–10 specific real-world instances where CDSFL caught genuine errors.

---

## Revised Cost Estimate

- Phase 2 revised scope: approximately 1875 API calls total
- Estimated cost: £50–80 at frontier model pricing
- Phase 1 cost so far: approximately £15

---

## The Three P-Pass Schemas Explained

### Schema A — Standard Monolithic

The model generates a solution in pass 1. In passes 2 through 5, it iteratively falsifies its own output, each pass building on the findings of the previous pass. The full prior chain is visible. Tests whether structured iterative self-checking improves output quality.

### Schema B — Extended Modular

For problems with 3 or more distinct subsystems. Passes 1 through 4 each focus on one module in isolation, falsifying that module's constraints, interfaces, and assumptions. Pass 5 runs in a completely isolated context with only the original problem and the current draft, using the adversarial brief. No prior P-pass analyses are visible. Tests whether modular decomposition plus isolated adversarial review outperforms monolithic self-checking.

### Schema C — Cross-Model Adversarial

Model A generates the solution. Model B falsifies it. Model A responds to the findings. Model B re-checks. A third model or fresh instance runs the isolated adversarial pass. Tests whether epistemic friction between models with different training biases produces better falsification than self-checking.

**Hypothesis:** Schema C should produce the strongest results because different models have different blind spots. Schema B should outperform Schema A on modular problems because isolation prevents anchoring on prior conclusions. Schema A is the baseline for comparison.

---

## Immediate Next Steps

1. Complete Phase 1 — score all 7 configurations, write the ceiling-effect analysis
2. Design 25 verifiable frontier tasks — this is the critical path
3. Implement the placebo control, Schema C, and adaptive termination in the benchmark code
4. Run Phase 2
5. Prepare the CX handoff for Phase 3
