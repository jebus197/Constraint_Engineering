# CDSFL Gemini Extended P-Pass — Module 2 of 5

**Scope:** `run_phase2.py` (Orchestration, Checkpoint, Cost, Manifest)
**Date:** 2026-03-18
**Model:** Gemini (via gemini CLI)
**Areas reviewed:** Phase 2 orchestrator, checkpoint system, cost ledger, run manifest

---

## Module 2 Review Findings

### Finding 1
**Category:** Cost Control
**Severity:** HIGH
**Affected:** `run_task_conditions` (443–509) / `run_adaptive`

The cost cap enforcement suffers from significant lag in adaptive loops. `run_adaptive` is passed `ledger.check_cap` as a check function, but the ledger is only updated via `ledger.record` after the entire task (up to 5 passes) completes. Consequently, all passes within a single task see the same "pre-task" total. This allows a single expensive task to overshoot the budget by a factor of 5× or more before the orchestrator can react and stop the run.

**STATUS:** Partially mitigated. `cost_check_fn` callback checks the cap between passes within `run_adaptive`, but the ledger total is only updated post-task. Within a single task, the cap check uses stale data. Full fix would require per-pass ledger recording, which increases coupling between runner and orchestrator. Acceptable risk for the $100 budget cap.

---

### Finding 2
**Category:** Reproducibility
**Severity:** HIGH
**Affected:** `_compute_manifest` (120) / `main` (625)

The run manifest does not include the `--variant` argument. Since the variant determines which domain-specific directives are loaded, it directly impacts the LLM's behaviour and the validity of the results. Currently, a user can resume a run with a different variant, and the orchestrator will incorrectly treat previous results (generated with a different variant) as valid and skip those tasks, leading to a "polluted" dataset.

**STATUS:** Already fixed. `variant` is included in the manifest computation.

---

### Finding 3
**Category:** Reporting
**Severity:** MEDIUM
**Affected:** `main` (750–754)

The completeness percentage calculation in the final report and the `deferred_for_review.json` manifest does not account for Schema C (cross-model) items. `expected_items` is calculated based only on the 3 conditions in the main loop (control, cdsfl, placebo). If Schema C is active, the checkpoint will contain additional items, causing the completeness report to show inaccurate percentages or values exceeding 100%.

**STATUS:** Already fixed. Schema C items are now included in `expected_items` count.

---

### Finding 4
**Category:** Cost Control
**Severity:** MEDIUM
**Affected:** `run_task_conditions` (453, 477, 505) / `run_preflight` (388, 406)

The cost estimation logic consistently underestimates API spend because it ignores the length of the universal and domain-specific directives. Every call to `estimate_call_cost` passes only the length of the task prompt, whereas the actual prompt sent to the API includes the full CDSFL and domain directive sets, which can be several kilobytes in size and comprise a significant portion of the token cost.

**STATUS:** Already fixed. Directive length is now added to `prompt_len` in cost estimates.

---

### Finding 5
**Category:** Orchestration
**Severity:** MEDIUM
**Affected:** `main` (685–696)

The main task loop fails to catch general `Exception`s. While it specifically handles `FatalAPIError` for graceful exits, any transient but persistent error (e.g., a network timeout that exhausts internal retries, or a specific task prompt triggering a non-fatal 400 error) will crash the entire script. For a large-scale frontier test, the orchestrator should log the error and proceed to the next task/config rather than requiring a manual resume for every transient failure.

**STATUS:** Already fixed. General `Exception` handler added with log-and-continue behaviour.

---

### Finding 6
**Category:** Cost Control
**Severity:** MEDIUM
**Affected:** `run_schema_c` (515)

The Schema C adversarial loop (`run_schema_c`) does not implement mid-run cost cap checking. Unlike the main CE loop, which passes a check function to `run_adaptive`, Schema C involves multiple models and multiple passes without any internal budget validation. Given that Schema C is typically the most expensive part of the run, it is the most likely to cause a significant budget overrun.

**STATUS:** Already fixed. `cost_check_fn=ledger.check_cap` is passed to `run_cross_model`.

---

### Finding 7
**Category:** Reproducibility
**Severity:** LOW
**Affected:** `_hash_domain_directives` (138)

The domain directive hashing logic uses `txt_file.name` but ignores the file's path relative to the directives directory. If a file is moved between domain folders (e.g., from chemistry to physics) without changing its name or content, the manifest hash will remain identical. This would cause the orchestrator to incorrectly validate a checkpoint even though the mapping of directives to task domains has changed.

**STATUS:** Already fixed. Uses relative path instead of just filename.

---

### Finding 8
**Category:** Validation
**Severity:** LOW
**Affected:** `run_preflight` (351)

The mandatory preflight pilot ignores domain-specific directives and the `--variant` argument. It only tests the "universal" directive set. This means errors in domain directive file paths, formatting, or variant selection logic are not caught during the preflight phase and will only surface during the main multi-task batch execution.

**STATUS:** Known limitation. Preflight is a smoke test for API connectivity, not full configuration validation. Acceptable for current use.
