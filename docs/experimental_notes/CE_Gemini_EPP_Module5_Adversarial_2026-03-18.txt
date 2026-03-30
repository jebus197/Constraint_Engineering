# CDSFL Gemini Extended P-Pass — Module 5 of 5: Isolated Adversarial Review

**Date:** 2026-03-18
**Model:** Gemini (via gemini CLI)
**Scope:** Full codebase adversarial review (fresh context, no prior findings)
**Protocol:** This pass was run in isolation per the Extended P-Pass protocol. The reviewer was given only the codebase and the adversarial brief, without any findings from Modules 1–4.

---

## Module 5 Adversarial Findings

### 1. Batch Process Fragility Due to Unhandled Non-Fatal Exceptions

- **Severity:** CRITICAL
- **Affected:** `run_phase2.py` (lines 807–810) and `run_benchmark.py` (lines 104–129)

**Defect:** The main orchestration loop in `run_phase2.py` exclusively catches `FatalAPIError`. However, `run_benchmark.py`'s retry logic raises standard exceptions (or specific API errors) when `max_retries` is exhausted for transient errors (for example, persistent timeouts, 5xx errors). These non-fatal exceptions are not caught by the orchestrator, causing the entire batch experiment to crash upon a single task failure.

**Impact:** Operational fragility; a single stubborn task aborts the entire run, requiring manual intervention to resume, defeating the purpose of an autonomous batch runner.

**STATUS:** Already fixed. General `Exception` handler added with log-and-continue behavior for non-fatal errors.

---

### 2. Cost Ledger Data Loss on Process Interruption

- **Severity:** HIGH
- **Affected:** `run_phase2.py` (`run_task_conditions` lines 681–744) and `run_benchmark.py` (`run_adaptive`)

**Defect:** API costs are metered and committed to the ledger strictly transactionally, only after `run_adaptive` returns successfully. If the process is interrupted (OOM, kill signal, power loss) or crashes during the execution of a multi-pass task (which can take minutes), the costs incurred during that partial run are never recorded.

**Impact:** The cost cap mechanism is leaky. A loop of crashes or interruptions allows the system to drain the API budget indefinitely without the ledger reflecting the wasted spend.

**STATUS:** DEFER FOR HUMAN REVIEW. Fixing requires either per-pass ledger callbacks (increasing coupling between runner and orchestrator) or periodic ledger snapshots (adding complexity). The $100 budget cap provides a natural ceiling. For the current single-run experiment, this is an acceptable risk. For production use, per-pass cost recording would be needed.

---

### 3. Redundant Execution and Double Billing of Pilot Tasks

- **Severity:** MEDIUM
- **Affected:** `run_phase2.py` (`run_preflight` vs main loop)

**Defect:** The mandatory `run_preflight` executes a full adaptive run for the first task to validate infrastructure but does not return or save the execution artifacts (result dict) to the checkpoint. The main loop subsequently re-executes the same task-config combination from scratch.

**Impact:** Inefficiency and financial waste; the first task of every run is billed twice.

**STATUS:** DEFER FOR HUMAN REVIEW. Could be fixed by saving preflight results to checkpoint, but this adds complexity to the preflight/main-loop boundary. At current API prices, the duplicate cost is negligible (under $1). Worth fixing for a production system but not for the Phase 2 experiment.

---

### 4. Environment-Specific Hardcoded Path Dependency

- **Severity:** MEDIUM
- **Affected:** `run_benchmark.py` (line 617)

**Defect:** `_IM_SERVICE` is defined using `Path.home()` joined with a specific directory structure (`Developer_Projects/Project_Genesis/...`). This path structure is specific to the developer's machine.

**Impact:** On any other environment (CI/CD, other developers), the confer mechanism will trigger `FileNotFoundError` or similar, leading to consistent `INFRA_FAIL` in the adaptive termination logic, forcing all tasks to run to the hard cap (`max_passes`) and degrading benchmark validity.

**STATUS:** Known limitation. Same as Module 1 finding 6 and Module 4 finding 1. Flagged across all review modules. Not fixable without environment abstraction.

---

### 5. Reporting Logic Ignores Schema C Tasks

- **Severity:** LOW
- **Affected:** `run_phase2.py` (lines 872 and 830–866)

**Defect:** The `deferred_report` calculates `expected_items` based solely on `len(tasks) * len(configs) * 3`. It fails to account for Schema C (cross-model) tasks, even when they are executed and added to the checkpoint.

**Impact:** Misleading progress reporting; running Schema C will result in "completed" counts exceeding "expected" counts, and progress tracking for the cross-model phase is effectively missing from the summary.

**STATUS:** Already fixed. Schema C items are now included in `expected_items` count.

---

### 6. Adaptive Throttle State Fragmentation

- **Severity:** LOW
- **Affected:** `run_phase2.py` (lines 790 and 855)

**Defect:** `AdaptiveThrottle` instances are scoped to the inner loops (per-config and per-Schema-C-pair). Rate limit backoff state is lost when the runner transitions between configs using the same provider (for example, `gpt-5.4` to `o4-mini`) or from the main loop to Schema C.

**Impact:** Reduced API stability; the runner may hammer a provider immediately after a rate-limit backoff simply because it switched to a new configuration using the same underlying provider.

**STATUS:** DEFER FOR HUMAN REVIEW. Fixing requires a shared throttle registry keyed by provider rather than per-config instantiation. Low impact given the existing retry logic with exponential backoff. Worth considering for multi-provider production runs.

---

## Summary of Deferred Items for Human Review

1. Cost ledger data loss on process interruption (Finding 2)
2. Preflight double billing (Finding 3)
3. Throttle state fragmentation across configs (Finding 6)
4. From Module 3: Compound variable confound (control vs methodology)
5. From Module 3: Placebo naming and construct validity
6. From Module 4: Schema C cost estimation accuracy
