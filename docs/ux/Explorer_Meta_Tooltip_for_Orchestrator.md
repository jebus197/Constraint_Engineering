# Explorer meta-tooltip (first-time researchers)

**UI placement:** Explorer tab — e.g. “What is this?” next to the title, or an onboarding spotlight. This is the **layer-2** explanation (longer than parameter `?` tips; shorter than the Read more technical note / Mathematical Appendix).

**Register:** plain formal English. No schema key names.

---

## What this view is

Science and engineering rarely finish in one shot. You test, you change something, you test again. Each cycle can **find** problems, **fix** them, and also **introduce** new ones.

This view is the project’s **risk-dynamics explorer** (Stage 5 in the formal development). It shows how the **risk that something material is still wrong** moves from pass to pass under that loop:

1. **Detection** — a pass attacks the claim set or apparatus; belief that a problem remains is updated.  
2. **Resolution** — fixes are attempted, with imperfect success.  
3. **Re-injection** — changing the system can put **new** risk back in.

So the vertical axis is not “number of bugs in code.” It is closer to: **remaining risk that something material is still wrong (or becomes wrong again) after another cycle of severe testing and repair.**

That pattern appears across STEM whenever work is **iterative, fallible, and interventionist**. Software review is one instance, not the definition.

- **Retrospective Mode** (default) binds to a **named experiment** (the last run unless you select another) and shows what the recorded passes actually bought.  
- **Predictive Mode** is **fully predictive**: you set the assumptions; the graphic explores consequences. It is **not** tied to the last run and **not** a forecast of the next real measurement in the lab.

The **large charts** are the point: at a glance, is remaining risk falling, stalling, or being put back by the way you intervene? Parameters support the graphic; they do not replace it.

---

## What it is not

- It does **not** settle experimental claims. Evidence from checks, and human decisions when checks cannot finish, do that.  
- It does **not** replace domain measurement, clinical judgement, or formal proof.  
- It does **not** “see the future.” Predictive Mode only models the enquiry loop under **your** stated assumptions.  
- Live decisions about whether a real experiment stops still depend on that experiment’s checks and on any human review the system escalates — not on this graphic alone.

---

## How to read it in three fields outside software

### 1. Experimental physics / instrumentation

**Situation:** You commission a measurement chain (sampling, filtering, calibration) and claim it meets a resolution or stability requirement after successive lab iterations.

| Loop element | Meaning here |
|--------------|----------------|
| “Something material is still wrong” | The setup still systematically mis-measures, aliases, drifts, or fails a bound |
| Detection | How well each test campaign finds those problems (new diagnostics vs repeating the same check) |
| Fix | How completely a recalibration or redesign removes the fault |
| Re-injection | Touching the apparatus introduces new drift, cable noise, thermal paths, or DAQ-side errors |

**What the explorer tells you:** whether further lab nights are still buying down **risk of a wrong physical conclusion**, or whether you are in a **leaky-fix / high re-injection** regime where more “passes” mostly rearrange the apparatus.

- **Retrospective:** After five campaigns, did residual risk of an invalid measurement actually fall?  
- **Predictive:** If detection stays mediocre and every fix disturbs the setup, will remaining risk floor out above what we can tolerate?

### 2. Chemistry / process or formulation

**Situation:** A synthesis or process is iterated—batch after batch—claiming purity, yield, or a safety envelope after each process change.

| Loop element | Meaning here |
|--------------|----------------|
| “Something material is still wrong” | Out-of-spec impurity, runaway risk, incomplete conversion, unstable intermediate |
| Detection | Analytics (e.g. chromatography, spectra, in-process tests)—including whether each batch’s tests are **new information** or ritual repetition |
| Fix | Recipe, temperature, or catalyst change intended to clear the failure mode |
| Re-injection | Process changes that clear one impurity but create another, or that destabilise scale-up |

**What the explorer tells you:** whether the campaign is **converging toward trustworthy process claims** or cycling (futile fixing when repairs do almost nothing; or fixes that always re-inject). That supports “one more batch” vs “stop and redesign the assay or process” — not a prediction of the next chromatogram’s exact peaks.

### 3. Biology / assay or protocol claims

**Situation:** An assay or protocol is refined across rounds—claiming sensitivity, specificity, or a pathway effect after successive protocol revisions and re-tests.

| Loop element | Meaning here |
|--------------|----------------|
| “Something material is still wrong” | False positive/negative structure, batch effect, confounder, unreproducible effect |
| Detection | Replication design, controls, blinding, orthogonal assays |
| Fix | Protocol amendment intended to remove the failure mode |
| Re-injection | Amendments that add operator dependence, new reagents, or selection effects |

**What the explorer tells you:** how **risk of a still-wrong biological claim** moves under repeated “test → amend → re-test.” High re-injection means every “fix” keeps the risk of a misleading claim high; a healthy loop means that residual risk is actually falling.

*(Engineering control and safety claims—the project’s own demo targets—fit the same pattern: residual risk that a stability or envelope claim is still false after design–test–patch cycles.)*

---

## Why you should care

Grant panels, safety boards, and careful experimenters already ask, in prose:

> Are further passes still reducing the chance we are wrong, or are we mostly rearranging the problem?

This calculator makes the **structure** of that question inspectable—as dynamics and regimes (for example healthy improvement versus leaky or futile repair)—so you can decide whether another cycle is worth it and explain that decision to others.

In software, people often phrase the same idea as “risk that a flaw class remains after *n* review passes.” That is a useful special case. It is **not** the limit of what this view is for.

---

## Read more

For the underlying Stage-5 recursion, formal parameter roles, regimes, and worked technical detail:

**Read more →** Risk dynamics explorer — technical note (maths and parameters)

That note leads into the Mathematical Appendix. Parameter `?` tips on the sliders remain short definitions of π, p, η, σ, ν, θ, and related controls.
