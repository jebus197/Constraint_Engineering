# CE Benchmark Code Review by CX (Codex) — Round 4

**Date:** 2026-03-18T19:28:00Z
**Context:** Review of all 4 Round 3 remediations plus full P-pass of updated code

---

## Round 4 Verdict

Not at diminishing returns yet: **substantive HARD defects remain** (cap integrity plus resume compatibility plus manifest completeness). The next correct action is to harden those three before another CC/CX round.

---

## Constraint Classification

- **HARD:** cost-cap enforcement integrity, checkpoint/manifest compatibility correctness, Schema C execution determinism
- **SOFT:** logging semantics, docstring/type-doc consistency, over-conservative invalidation behavior

---

## Round 3 Fix Verification (4 items)

- **Fix 1** (Schema C env scoping): Correctly implemented via `has_schema_c_tasks` gating and pair-availability filtering in env validation.
- **Fix 2** (Schema C manifest inclusion): Implemented as stated; `manifest_configs` now includes `CX_CONFIGS` when Schema C is active.
- **Fix 3** (pre-call cap guards): Implemented at requested points.
- **Fix 4** (confer return typing): Correctly implemented; signature, returns, and caller align.

---

## Remaining Substantive Defects

**1. HARD: Hard cap is still breachable because multi-call blocks run before metering and checking.**
`run_adaptive` and `run_cross_model` can consume multiple calls after a single pre-check (`bench/run_phase2.py` lines 491, 497, 554, 568; `bench/run_benchmark.py` lines 1247, 1258, 1395, 1410).

**2. HARD: Resume still accepts pre-manifest checkpoints (warning only)**, violating strict compatibility guarantees (`bench/run_phase2.py` lines 248, 256, 258, 732).

**3. HARD: Manifest remains under-specified for true run semantics.**
Hash uses task IDs, not task content, schema flags, or pair map — so incompatible semantic changes can slip through resume (`bench/run_phase2.py` lines 114, 137, 142, 671, 813).

**4. SOFT (introduced tradeoff):** Manifest now includes all `CX_CONFIGS` when Schema C is active, even if only a subset of pairs can run; this can cause unnecessary checkpoint invalidation.

**5. SOFT:** `confer_diminishing_returns` docstring is stale versus current 3-tuple return and no keyword-heuristic fallback.

---

## CC Assessment of Round 4 Findings

**Finding 1 (multi-call cap breach):** Actionable. Add cap checks between passes inside `run_adaptive` and `run_cross_model`. The post-call check is inherent to pay-per-call systems, but between-pass checks are a genuine improvement.

**Finding 2 (pre-manifest checkpoint acceptance):** Actionable. Change from warning to rejection on resume. Pre-manifest checkpoints should not be accepted when strict compatibility is the contract.

**Finding 3 (manifest under-specified for task content):** Diminishing returns. Task IDs are stable unique identifiers. If someone changes task content without changing the task ID, that is a user error, not a manifest deficiency. Hashing all task content would make manifests fragile (any whitespace change invalidates). Schema flags are already captured indirectly via the task selection (task IDs are in the manifest). This is the kind of theoretical defect that produces no real-world failure.

**Finding 4 (SOFT, over-conservative invalidation):** Acknowledged but acceptable. Including all `CX_CONFIGS` when Schema C is active is conservative by design. The alternative (per-pair manifest hashing) adds complexity for a marginal edge case.

**Finding 5 (SOFT, stale docstring):** Trivial fix, will address.
