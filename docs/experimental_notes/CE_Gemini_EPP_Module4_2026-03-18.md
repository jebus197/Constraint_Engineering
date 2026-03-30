# CDSFL Gemini Extended P-Pass — Module 4 of 5: Cross-Module Integration Review

**Date:** 2026-03-18
**Model:** Gemini (via gemini CLI)
**Scope:** Imports, data flow, state consistency between `run_benchmark.py` and `run_phase2.py`

---

## Module 4 Review Findings

### 1. Hardcoded Paths in `confer_diminishing_returns`

- **Category:** Environment Consistency
- **Severity:** HIGH
- **Affected Functions:** `run_benchmark.confer_diminishing_returns`

**Description:** The confer mechanism (used by `run_adaptive`) relies on absolute paths in the user's home directory for both the project root (`proj_dir`) and the Project Genesis IM service (`_IM_SERVICE`).

**Impact:** If `run_phase2.py` is executed on a system with a different user name or directory structure (for example, in a CI environment or by a different developer), the `subprocess.run` calls will fail with `OSError`. While caught and converted to `INFRA_FAIL`, this effectively disables the intelligent termination feature of the Phase 2 experiment.

**STATUS:** Known limitation. Flagged across multiple review rounds. The experiment is single-developer on a known machine. Distribution would require environment variable configuration.

---

### 2. Cost Cap Bypass in `run_cross_model`

- **Category:** State Synchronization / Safety
- **Severity:** MEDIUM
- **Affected Functions:** `run_benchmark.run_cross_model` (called by `run_phase2.run_schema_c`)

**Description:** Unlike `run_adaptive`, the `run_cross_model` function does not accept a `cost_check_fn`. It executes its full 5-pass sequence without checking for budget depletion between calls.

**Impact:** `run_phase2.py` only checks the cost ledger before and after the `run_schema_c` call. A single Schema C task using frontier models (for example, GPT-5.4 plus Sonnet 4.6) could significantly overshoot the user-defined cost cap before the orchestration loop can intervene.

**STATUS:** Already fixed. `cost_check_fn` parameter added to `run_cross_model` and passed through from `run_schema_c`.

---

### 3. Inaccurate Cost Estimation for Schema C

- **Category:** Data Format Assumptions
- **Severity:** MEDIUM
- **Affected Functions:** `run_phase2.run_schema_c`

**Description:** The cost estimation for Schema C tasks uses a fixed multiplier (`len(task["prompt"]) * 3`) for both Model A and Model B.

**Impact:** This ignores the actual pass asymmetry (Model A produces 2 responses; Model B produces 3) and the cumulative nature of the prompt chain. This results in inaccurate ledger entries for Schema C, potentially causing premature or late cost-cap triggers.

**STATUS:** DEFER FOR HUMAN REVIEW. Per-pass cost attribution is available in the raw data for post-hoc analysis. The rough estimate is adequate for cap enforcement within the $100 budget. Precise per-model costing would require significant refactoring.

---

### 4. Adaptive Termination Bias in `run_placebo`

- **Category:** Logic / Experimental Design
- **Severity:** LOW
- **Affected Functions:** `run_benchmark.run_placebo`

**Description:** `run_placebo` calls `run_adaptive` using default parameters, which include `confer_after=3`.

**Impact:** The placebo calibration baseline (which uses generic instructions) is subject to the same CC/CX adversarial confer mechanism as the CDSFL group. Because the CC/CX prompts were specifically tuned to look for CDSFL-style constraint classification and falsification, they may produce erratic "STOP" or "CONTINUE" verdicts when evaluating generic placebo output, confounding the calibration.

**STATUS:** Partially fixed. Confer prompt language has been made condition-neutral (removed CE-specific references). Confer mechanism now assesses "iterative methodology output" generically, which is appropriate for both CDSFL and placebo conditions.

---

### 5. `confer_after` Shadowing in `run_phase2` Preflight

- **Category:** Configuration Consistency
- **Severity:** LOW
- **Affected Functions:** `run_phase2.run_preflight`

**Description:** The preflight check calls `run_adaptive` with `confer_after=99` to avoid overhead.

**Impact:** While logical for a smoke test, this means the preflight pilot successfully validates API connectivity but fails to validate the confer CLI infrastructure (`claude`/`codex`). If the confer CLIs are missing, the preflight will still pass, only to have the main experiment degrade to `INFRA_FAIL` hours later.

**STATUS:** Already fixed. Preflight now explicitly smoke-tests both `claude` and `codex` CLI availability.
