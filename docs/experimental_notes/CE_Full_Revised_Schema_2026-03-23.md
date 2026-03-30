# CDSFL Full Revised Schema Explanation

**Date:** 23 March 2026

---

## Overview

This document explains the complete revised CDSFL bench test architecture as built on 23 March 2026. It covers what changed, how the system works end to end, and what this means for performance.

---

## The Old Schema

Previously, the entire review protocol ran through natural language. CC wrote a prompt, sent it to each model, and each model wrote a natural language response. CC read the responses and tried to extract findings by parsing free text. CC decided if the models should keep going by looking for the word `CONVERGED` in their output. SymPy verification happened sometimes, when CC remembered to check. Everything was natural language from start to finish.

This was slow, brittle, and allowed models to defer by saying "I agree with everything." Churn was invisible until you looked at the data afterwards.

---

## The New Schema

The entire infrastructure is now code. **The models only do one thing: they reason about the problem.** Everything else — validation, verification, convergence, deference detection, and policy enforcement — is handled programmatically.

---

## Step-by-Step: How a Single Task Runs

### Step 0: Before Anything Starts

The **Registry** loads. It is a four-layer configuration hierarchy, like Windows Group Policy:

- **Layer 1 — Universal rules** (can never be broken): Every finding must attempt falsification. Every model must contribute independently. All mathematical claims get checked by SymPy.
- **Layer 2 — Domain-specific rules:** Maths tasks require proof structure checks. Engineering tasks require unit consistency checks.
- **Layer 3 — Task-specific requirements:** This particular task has specific HARD constraints that must all be addressed.
- **Layer 4 — Model-specific settings:** CX gets explicit format instructions (it tends to write essays instead of structured findings). DeepSeek gets a lower churn detection threshold (it is prone to flat output curves).

These layers merge top-down. A lower layer can add requirements but can never weaken a higher layer. If someone tried to set `anti_deference = false` at the model level, the system would refuse to start. This is enforced by code, not by a prompt.

### Step 1: CC Generates a Solution

CC (Opus 4.6) produces a solution to the task using decomposed generation: solve the problem, attack the answer, classify issues by severity, revise in batches with per-batch contradiction checks. Each batch is small enough that no single prompt exceeds approximately 12,000 characters.

For **CDSFL + HIL**, CC also does external research first: searches arXiv for relevant papers, uses SymPy to verify mathematical claims, and reads web pages for known results. Then it generates expert guidance incorporating the research.
- For **HIL alone:** a brief 500-character hint from training knowledge only.
- For **Control and CDSFL alone:** no guidance is provided.

### Step 2: All Five Models Review Independently

All five models — CC, CX, DeepSeek, Gemini, and ChatGPT 5.4 — receive the solution and produce findings. They must output **structured JSON**, not free text. Each finding has mandatory fields:

- What the claim is
- Why it is wrong
- What constraint class it falls under (HARD or SOFT)
- Their confidence
- A verifiable mathematical expression (if one exists)

The **anti-deference gate** is structural. The schema rejects any response that does not contain at least one independent observation or a scoped justification for why nothing was found. "I agree with everything" is not valid JSON under this schema. The system will not accept it.

### Step 3: Automatic Verification

This is new and entirely computational. Every finding that includes a verifiable expression gets sent to **SymPy in a sandboxed subprocess**. SymPy checks whether the mathematical claim is true or false. The result comes back as:
- `verified` — SymPy confirms the finding is correct
- `refuted` — SymPy shows the finding is wrong
- `unverifiable` — SymPy cannot parse or evaluate it

This happens automatically on every finding. No model decides whether to check. No prompt asks CC to remember to verify. The code does it every time. This applies to **CDSFL and CDSFL+HIL conditions only** — Control and HIL do not get computational verification because that is part of the methodology being tested.

### Step 4: Convergence Computation

The old way was to parse the word `CONVERGED` from model output and count rounds with zero new findings. The new way computes **three non-compensatory gates**:

1. **v_comp:** What fraction of mathematically verifiable findings were confirmed by SymPy. This must be above threshold.
2. **v_struct:** What fraction of structural findings (not checkable by SymPy) were independently identified by models from at least two different vendor families. An Anthropic model and an OpenAI model finding the same structural issue is peer support. Two OpenAI models finding it is not independent enough.
3. **hard_coverage:** Have all HARD constraints listed in the task registry been addressed by at least one reviewer? If any HARD is unassessed, convergence is blocked. **The system fails closed.** It assumes unassessed means missed, not irrelevant.

All three gates must pass simultaneously. High `v_comp` cannot compensate for low `hard_coverage`. This is **non-compensatory** — every dimension must be satisfied independently.

### Step 5: Decay Curve Monitoring

After each round, the code computes **D** (the decay rate) for each model — measuring how quickly their finding rate is declining:

- A model doing genuine analysis produces a decaying curve: 5, 3, 2, 1, 0
- A model churning produces a flat line: 2, 2, 2, 2, 2

The code flags flat curves. For now this is advisory only — it logs the flag but does not automatically change model policy.

Once calibration data exists from the full bench test, **Layer 5 — the Active Policy Engine** — will adjust model policies automatically based on observed D and v̄ scores. A model that consistently churns gets elevated scrutiny. A model that consistently produces verified findings gets full convergence weight. The system learns which models are trustworthy and adjusts accordingly.

---

## What This Means for Performance

**Speed:** CX estimates 25–45% wall clock reduction per round. Less natural language overhead, less parsing, less repair of malformed output. The models spend their tokens on reasoning, not on formatting.

**Quality:** SymPy catches false findings automatically. The old test counted all findings equally — ten churn findings scored the same as ten verified findings. Now the verification score separates signal from noise.

**Reliability:** No more format mismatches. CX producing 5,632 characters of brilliant analysis that the extractor could not parse is fixed by the structured JSON schema. The extractor does not need to guess the format — the format is defined.

**Anti-gaming:** Deference is structurally impossible. Churn is computationally detectable. The models cannot game the protocol because the protocol is code, not prompts.

---

## Prediction

**CDSFL + HIL should now cleanly outperform all other conditions** because the full methodology — including structure, verification, research, and expert guidance — is actually being executed as designed for the first time.
