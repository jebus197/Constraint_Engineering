# CDSFL Gemini Extended P-Pass — Module 3 of 5

**Scope:** Scientific Validity Review
**Date:** 2026-03-18
**Model:** Gemini (via gemini CLI)
**Areas reviewed:** Experimental design threats, confounds, bias, reproducibility

---

## Module 3 Review Findings

### Finding 1
**Category:** Experimental Design
**Threat Type:** Internal Validity
**Severity:** High

**Compound Variable Confound (Control vs. Methodology)**

The "Control" condition is implemented as a single-pass, zero-shot prompt (`run_control`). In contrast, the "Experimental" (CDSFL) and "Calibration" (Placebo) conditions are iterative P-Pass loops with system prompts. This design conflates the methodology (the specific CDSFL directives) with the mechanism (iteration and system instructions).

**Impact:** Superior performance in the Experimental condition cannot be cleanly attributed to the CDSFL directives; it could simply be the result of the model having multiple "thinking" passes compared to the Control's single attempt.

**STATUS:** DEFER FOR HUMAN REVIEW. This is a deliberate experimental design choice. The experiment tests whether CE (including its iterative nature) produces better outcomes than a single-pass baseline. The placebo condition controls for iteration. The control provides the zero-CE baseline. Changing the control to multi-pass-without-CE would test a different hypothesis.

---

### Finding 2
**Category:** Confer Mechanism
**Threat Type:** Bias
**Severity:** High

**Social Anchoring Bias in Confer Mechanism**

In the original CX confer prompt, the second assessor (CX) was explicitly instructed to "Read the most recent CC message" and was asked "Do you agree with CC's verdict?" This destroys the independence of the two assessors. CX is heavily anchored to CC's opinion, leading to a "hallucinated consensus" rather than a robust inter-rater reliability measure.

**Impact:** The "RESOLVED" status (consensus to stop) is scientifically unreliable as a measure of diminishing returns.

**STATUS:** Already fixed. CX prompt now gives independent STOP/CONTINUE verdict without seeing CC's assessment.

---

### Finding 3
**Category:** Confer Mechanism
**Threat Type:** Internal Validity / Bias
**Severity:** High

**Criterion Contamination in Adaptive Termination**

The `confer_diminishing_returns` function is used for both CDSFL and Placebo conditions. However, the CC confer prompt told the assessor they are "assessing... for a Constraint Engineering (CE) benchmark." The Placebo condition explicitly lacks CE markers (HARD/SOFT classification).

**Impact:** Assessors may penalise the Placebo condition for not following the methodology it wasn't given, or conversely, "stop" CE runs early because they see the "correct" markers. This creates a systematic bias where the presence of the methodology is used as the quality metric for the termination of the methodology.

**STATUS:** FIXED in this round. Confer prompt now uses condition-neutral language ("methodology benchmark" instead of "Constraint Engineering benchmark").

---

### Finding 4
**Category:** Execution Logic
**Threat Type:** Internal Validity
**Severity:** Moderate

**Systematic Attrition Bias (Fixed Execution Order)**

`run_task_conditions` executes conditions in a fixed sequence: Control then CDSFL then Placebo. Because the `CostLedger` cap is checked before each condition, the "Placebo" baseline is disproportionately likely to be truncated or skipped as the budget is exhausted.

**Impact:** The final calibration data will be skewed toward "cheap" tasks or early-experiment samples, making a direct statistical comparison with the (more complete) CDSFL data-set invalid.

**STATUS:** FIXED in this round. Task order is now randomised with a reproducible seed derived from the manifest hash.

---

### Finding 5
**Category:** Prompt Construction
**Threat Type:** Confound
**Severity:** Moderate

**History Deletion Confound (Extended/Schema C Mode)**

The "Extended" and "Schema C" modes conclude with an "isolated adversarial pass" where the model is given only the task and the final draft, with all prior P-Pass history removed.

**Impact:** Any performance improvement in the final pass conflates the benefit of adversarial scrutiny with the benefit of contextual cleaning (noise reduction). The design does not isolate whether the model got "smarter" or just "less distracted" by the long prior chain.

**STATUS:** Already documented as a code comment. Known confound, documented in the analysis. Interpreting Extended vs. Standard comparison requires this caveat.

---

### Finding 6
**Category:** Data Integrity
**Threat Type:** Confound
**Severity:** Moderate

**Draft Pollution on Extraction Failure**

In `run_adaptive`, if the regex-based `_extract_section` fails to find a `REVISED_ANSWER`, the logic falls back to using the raw response.

**Impact:** This raw response includes meta-headers (`ISSUES_FOUND`) and the model's own self-criticism. This text is then injected into the "current draft" block of the next pass. The model on the subsequent pass may treat its previous meta-commentary as part of the technical problem description, leading to "recursive noise" that invalidates the iteration.

**STATUS:** Already fixed across all execution modes. Fallback now preserves previous draft instead of using raw response.

---

### Finding 7
**Category:** Cost Modelling
**Threat Type:** Confound
**Severity:** Minor

**Arbitrary Cost Attribution (Schema C)**

`run_schema_c` records costs by taking the total response length and splitting it 50/50 between Model A and Model B.

**Impact:** In an adversarial setup, the falsifier often produces significantly different token counts than the generator. This arbitrary split masks the true cost-efficiency profile of different model combinations, which is a key goal of Schema C.

**STATUS:** DEFER FOR HUMAN REVIEW. Fixing requires per-pass cost attribution, which is available in the pass records (each pass records which model produced it). Post-hoc analysis can reconstruct accurate per-model costs from the raw data. The ledger split is for cap enforcement, not analysis.

---

### Finding 8
**Category:** Statistical Design
**Threat Type:** Internal Validity
**Severity:** Minor

**Selection/Order Effects**

Tasks are processed in a fixed alphabetical order based on filenames. Lack of randomisation means any temporal factors (API latency drift, provider-side caching, or rate-limit "bucket" depletion) will consistently affect the same tasks, potentially introducing a selection bias into the performance metrics of specific domains.

**STATUS:** FIXED in this round. Task order is now randomised with a reproducible seed.

---

### Finding 9
**Category:** Baseline Definition
**Threat Type:** Construct Validity
**Severity:** Minor

**Construct Validity of "Placebo"**

The `PLACEBO_DIRECTIVES` are actually a very strong "Best Practices" or "Chain of Thought" prompt.

**Impact:** While this provides a high-quality baseline, it is not a "Placebo" in the medical/scientific sense (an inert treatment). Labelling it as such misrepresents the comparison; the experiment is actually a "Methodology A vs. Methodology B" test, not "Methodology vs. Null."

**STATUS:** DEFER FOR HUMAN REVIEW. This is by design: the placebo controls for "having good instructions" vs "having CDSFL-specific instructions." A truly inert placebo (no instructions) would conflate methodology benefit with instruction benefit. The naming is acknowledged as imprecise but the experimental design is defensible. Documentation should clarify this is a "calibration baseline" not a medical placebo.
