# Calibrated Metacognition and the Accidental Discovery

**Date:** 13 April 2026, 07:47 BST
**Context:** Exp 39 operational directive regression → analysis of metacognition vs measurement
**MC:** p, a, e, sth, d, t

---

## Context

During Experiment 39-0, a regression was found: the operational directive (`cdsfl_operational.md`) — which instructs models to compute R_k(i) (the iterative residual-risk self-assessment after round i) on their own output — was not loaded by `reference_runner.py`. The runner still computed R_k externally (scoring findings mathematically), but models themselves had no knowledge of the equation. They produced qualitative severity scores rather than numerical self-assessments.

| Experiment | Operational Directive | R_k Adoption | Outcome |
|-----------|----------------------|-------------|---------|
| Exp 36 | Not present | 0% (0/45+ rounds per model) | Baseline code review |
| Exp 37 | Present | 88–100% (14–16/16 rounds) | 18× improvement in confirmation rate |
| Exp 39 | **Missing (regression)** | 0% | Models revert to qualitative findings |

Same models, same pipeline, same code. The only difference: whether models received the equation.

---

## The Distinction: Measurement vs Metacognition

### When the runner computes R_k (measurement)

- η (the per-finding novelty proxy) from `_finding_similarity()` — algorithmic cosine/Jaccard
- S_k (the severity/stringency tristate gate) from pytest pipeline — tool-verified gates × effect evidence
- ν (the brittleness or literature-novelty parameter) from config constants — static
- **No judgment involved.** Function applied to data.

### When models compute R_k (metacognition)

- η: "Is the finding genuinely novel relative to the registry?"
- d: "Is the analytical approach independent from prior rounds?"
- p: "How capable is the model of catching this flaw class? Be honest."
- ν: "How brittle is this code area?"
- **Judgment required.** Reflected, committed, exposed as falsifiable numbers.

The numbers are what matters. `η=0.8` is falsifiable — another model can respond: "η should be 0.2 because this restates C0034." A qualitative label ("high novelty") is not. The equation forces **legibility**. Legibility enables **falsification**. Falsification is where the value lives.

---

## Three-Layer Architecture (accidental discovery)

The separation reveals three distinct layers:

### Layer 1: R_k as Constraint (metacognition)

Models receive the operational directive. They **must** compute R_k on their own output. This forces:
- Numerical parameter estimates (falsifiable by other models)
- Explicit self-assessment of capability, novelty, diversity
- Transparent reasoning about own reliability

### Layer 2: R_k as Measurement (evaluation)

The runner computes R_k externally using algorithmic inputs. Produces:
- γ (Duane reliability growth) — measures discovery depletion
- ρ (discovery efficiency) — measures novelty rate
- Ground-truth S_k from tool-verified pytest evaluations

### Layer 3: R_k as Calibration (feedback)

The runner feeds γ, ρ, and registry counts back to models. Models adjust:
- High ρ, low γ → productive phase, continue
- Low ρ, high γ → approaching convergence, stop restating known issues
- External measurement calibrates internal judgment

**All three layers are needed.** The accidental discovery is empirical evidence that Layer 2 alone (measurement without metacognition) is insufficient. Models do not calibrate against external scoring they cannot see.

---

## Expert Encoding Enhancement

Current expert encodings define **domain-specific S_k gates**: what tools to run, what constitutes a hard gate vs effect evidence. They do not define **domain-specific R_k parameter priors**.

### Proposed extension

Expert encodings specify parameter calibration alongside tool specification:

**Cryptography domain:**
```
p_baseline = 0.3      # Models weak at concurrency bugs in crypto
nu_b = 0.08           # Crypto code is brittle
S_star_floor = 0.7    # Low-quality fixes dangerous
```

**Mathematics domain:**
```
eta_source = "tool"   # eta must reference SymPy/z3 verification, not self-assessment
d_requirement = "different_technique_per_round"
p_baseline = 0.6      # Models reasonable at formal verification when tooled
```

These priors calibrate **both channels** simultaneously:
- Runner uses them as measurement defaults
- Models use them as starting points for judgment
- Feedback loop becomes domain-tuned

Expert encoding evolves from "what tools to run" to "how to calibrate epistemic self-assessment for this domain."

---

## P-Pass: Can Intelligence Be Scripted?

**Claim:** The runner's external R_k computation scripts intelligence.

**Falsifier:** Is external R_k qualitatively the same as model R_k?

**Result:** No. External R_k is scripted measurement. Internal R_k is judgment-based self-assessment. The intelligence lives in the adversarial scrutiny that happens when multiple models compare parameter estimates and challenge each other's self-assessments. The equation does not make models smarter — it makes their uncertainty **legible and challengeable**.

**Precise claim (P-pass surviving):** An orchestrator and its agents sharing a formal model of epistemic self-assessment, where both compute it independently and calibrate against each other, produces measurably better results than either computing alone. The Exp 37 vs Exp 39 comparison is a natural experiment for this claim.

**What was "accidentally scripted":** Not intelligence. **Epistemic accountability.** The equation creates a shared formal language in which self-assessment can be expressed, compared, and falsified.

---

## Extrapolation

### What generalises

The calibrated metacognition architecture generalises wherever three conditions hold:

1. **Tool-verifiable S_k** — the measurement layer has ground truth
2. **Meaningful cross-model parameter challenge** — the metacognition layer is not self-certification
3. **Specifiable parameter priors** — expert encodings can meaningfully calibrate

### Where it breaks down

- Pure aesthetic judgment: no tool-verifiable S_k, no algorithmic η → degenerates to self-certification
- Shared training bias domains: suspicious convergence rather than independent corroboration
- Single-agent settings: no adversarial scrutiny of parameter estimates

### Falsifiable predictions [SPECULATIVE]

1. **R_k self-computation correlates with finding confirmation rate.** Testable: compare Exp 37 model R_k scores vs immune pipeline verdicts for the same findings.

2. **Domain-specific parameter calibration improves convergence speed.** Testable: generic vs domain-tuned priors in matched experiments.

3. **Minimum panel size for metacognitive R_k.** Testable: single-model R_k self-computation, measure whether self-assessed R_k correlates with actual detection.

---

## Synthesis

The accidental separation of the equation from the models reveals that scripted measurement and metacognitive self-assessment are **complementary, not substitutable**. The equation is not intelligence — it is a constraint that makes intelligence legible. The combination of external measurement, internal judgment, and feedback between them produces calibrated metacognition.

The expert encoding enhancement: domain-specific parameter calibration extends encodings from tool specification to epistemic calibration. This is a falsifiable architectural claim with at least three testable predictions.

The deepest finding: intelligence cannot be scripted, but the conditions under which intelligence becomes visible, challengeable, and self-correcting can be. That is what the operational directive does. Its absence from Exp 39 — and the measurable degradation that followed — is empirical evidence for this claim.
