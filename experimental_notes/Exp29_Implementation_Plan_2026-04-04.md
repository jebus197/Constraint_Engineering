# Experiment 29 Implementation Plan

**Date:** 4 April 2026
**Purpose:** Fold all verified findings from C1–C5 into codebase, build missing components, prepare for first full integration test of target architecture.

## Overview

46 distinct verified findings (40 from Master Finding Registry + 6 novel from C5) plus 5 novel architectural constructs. Implementation organised into 6 work packages, ordered by dependency.

---

## WP1: Immune Pipeline Bug Fixes (Pre-v2 Code)

Fix the 40 MF findings in `bench/immune_agents.py`. These are the bugs in the quality gate itself. 8 are already V2-FIXED; 28 UNFIXED; 4 PARTIAL/MITIGATED. MF-28 likely false positive (C5 retracted with proof) — verify and remove.

### P0 Critical (fix first — 7 findings)

| ID | Bug | Fix | Type | Status |
|----|-----|-----|------|--------|
| MF-01 | MATH_PATTERN overbroad regex | Activate `_MATH_PATTERN_V2` | PATCH | V2 FIXED |
| MF-22 | Silent error swallowing (B Cell subprocess) | Check `returncode`, capture `stderr` | PATCH | UNFIXED |
| MF-23 | Proof by n=100 fallacy | Remove numeric fallback, emit UNCERTAIN | PATCH | UNFIXED |
| MF-24 | Substring injection (VERIFIED_TRUE) | Exact match `output.strip() == "VERIFIED_TRUE"` | PATCH | UNFIXED |
| MF-34 | Autoimmune amnesia (Reg T ignores dupes) | Include duplicates in rejection metric | PATCH | UNFIXED |
| MF-36 | Fail-open illusion | Reg T flag >30% UNCERTAIN as failure | PATCH | UNFIXED |
| MF-40 | Unsafe parse_expr (DoS → **RCE per C5-09**) | AST blocklist: reject `__`, `import`, `eval`, `getattr` | PATCH | UNFIXED |

### P1 Normal (15 findings)

| ID | Bug | Fix | Type | Status |
|----|-----|-----|------|--------|
| MF-02 | Extraction asymmetry (T ⊄ E) | Align trigger and extraction sets | PATCH | UNFIXED |
| MF-03 | Context erasure | Extract all backtick expressions + preserve context | PATCH | UNFIXED |
| MF-04 | First-match fallacy | Multi-match extraction | PATCH | UNFIXED |
| MF-05 | Missing re.DOTALL | Add re.DOTALL + lazy quantifiers | PATCH | V2 FIXED |
| MF-06 | Natural language hijack | Structural bounds on pattern matching | PATCH | UNFIXED |
| MF-07 | Net positive contradiction (HT thresholds) | Bayesian log-odds synthesis | ARCHITECTURAL | UNFIXED |
| MF-09 | Certainty inversion paradox | Cap confidence by absolute weight | PATCH | UNFIXED |
| MF-11 | Verdict spam | Deduplicate verdicts by cell type | PATCH | UNFIXED |
| MF-13 | Rejection rate discrepancy | Consistent metric across all cells | PATCH | UNFIXED |
| MF-14 | Continue bypass (NK FP check skipped) | Remove `continue`, check FP after dup | PATCH | V2 FIXED |
| MF-20 | Race condition on shared state | Deep-copy inputs to parallel cells | PATCH | UNFIXED |
| MF-21 | Intra-round duplicate blindness | Include current batch in dedup index | PATCH | UNFIXED |
| MF-29 | Dropped correlations | Match STRONG_CORRELATION string | PATCH | UNFIXED |
| MF-30 | SymPy substitution wrong variable | Auto-generate symbols from expression | PATCH | UNFIXED |
| MF-31 | Statistical regex missing leading zero | Fix regex to match `.05` | PATCH | UNFIXED |

### P2 Edge Condition (11 findings)

| ID | Bug | Fix | Type | Status |
|----|-----|-----|------|--------|
| MF-08 | Dead else block | Remove unreachable code | PATCH | UNFIXED |
| MF-10 | Micro-total discontinuity | Floor denominator consistently | PATCH | UNFIXED |
| MF-12 | DUPLICATE semantic handling | Remove orphaned dup-voting code | PATCH | UNFIXED |
| MF-15 | Falsy fallback bug (NK) | `is None` checks instead of truthy | PATCH | UNFIXED |
| MF-16 | Vacuous truth (phantom duplicates) | Assert `best_match is not None` | PATCH | UNFIXED |
| MF-17 | Toothless anomaly detection | Anomalies emit REJECTED, not UNCERTAIN | PATCH | UNFIXED |
| MF-18 | Multiline regex in FP database | Add re.DOTALL to FP patterns | PATCH | UNFIXED |
| MF-25 | Tautological if-then Z3 logic | Remove regex Z3; use AST solver | ARCHITECTURAL | UNFIXED |
| MF-26 | Scientific notation blindness | Support `[eE]` in numeric regex | PATCH | UNFIXED |
| MF-27 | Z3 requires 2+ numbers | Handle single-bound comparisons | PATCH | UNFIXED |
| MF-35 | Autoimmune inconsistent state | Immutable state transitions | PATCH | UNFIXED |

### P3 Defence-in-Depth (7 findings)

| ID | Bug | Fix | Type | Status |
|----|-----|-----|------|--------|
| MF-19 | O(N×M) scaling bottleneck | Index-based lookup or early termination | PATCH | UNFIXED |
| MF-28 | Regex empty string match | **LIKELY FALSE POSITIVE** — C5 retracted. Verify and remove. | — | — |
| MF-32 | Hardcoded stubs / dead code | Remove `_verify_uncertainty` | PATCH | UNFIXED |
| MF-33 | Class-switching contradiction | Remove SymPy→Z3 fallback chain | PATCH | UNFIXED |
| MF-37 | Batch timeout timebomb | Decouple executor lifecycle | ARCHITECTURAL | MITIGATED |
| MF-38 | Fuzzy match exploit (CT) | Enforce `len(snippet_tokens) >= 3` | PATCH | UNFIXED |
| MF-39 | Typo bypass (HT) | Pass findings by index, not ID string | PATCH | UNFIXED |

---

## WP2: C5 Novel Findings (6 new bugs not in registry)

These were discovered by C5's conversational + constrained approach. All are in the Cytotoxic T Cell or Pipeline layer.

| C5 ID | Bug | Fix | Type | Severity |
|-------|-----|-----|------|----------|
| C5-01 | Arbitrary file read via path traversal (CT) | Constrain paths to `source_paths` dirs; remove leaked content from error messages | ARCHITECTURAL | P0 |
| C5-02 | Empty string substring bypass (CT) | Guard: `if actual_normalised and (snippet in actual)` | PATCH | P0 |
| C5-03 | Prompt injection via finding descriptions (CT) | Wrap untrusted input in XML boundary tags | ARCHITECTURAL | P0 |
| C5-05 | Schema blindness on nested JSON (CT) | Extract via markdown code block regex, not brace balancing | PATCH | P2 |
| C5-23 | OOM exhaustion via `readlines()` | Bounded line streaming with configurable limit | PATCH | P1 |
| C5-26 | Confident Hallucination Highway (cascade) | Addressed by fixing MF-01 + MF-24 + MF-09 individually; Epistemic Routing Layer prevents recurrence | NOVEL CONSTRUCT | P0 |

---

## WP3: C5 Novel Constructs (5 new architectural components)

These do not exist in the codebase. They emerged from C5's cross-component analysis.

### 3a. Epistemic Routing Layer
**What:** Replaces regex-based claim classification with a typed classifier that understands the epistemic status of claims (mathematical, empirical, logical, behavioural).
**Why:** MF-01/MF-02/C5-06 show regex routing misclassifies 30% of inputs. The cascade in C5-26 depends on this misclassification.
**Where:** New module or significant rewrite of `_classify_claim()` in Dendritic Cell.
**Scope:** NOVEL CONSTRUCT. Medium effort.

### 3b. Reconciliation Gate
**What:** Final immutable state transition check before pipeline output. Once a finding is rejected/confirmed, that verdict cannot be overridden by autoimmune recovery or state desync.
**Why:** MF-34/MF-35/C5-25 show autoimmune override rescues known garbage. Dict key desync corrupts state.
**Where:** New function called after `helper_t_cell_synthesize()` and before final `ImmuneResponse` assembly.
**Scope:** NOVEL CONSTRUCT. Low-medium effort.

### 3c. Formalisation Agent
**What:** Translates natural language preconditions into formal Z3 invariants before B Cell verification.
**Why:** MF-03/MF-04/C5-07 show context erasure strips preconditions, causing false rejections.
**Where:** New preprocessing step between Dendritic Cell extraction and B Cell verification.
**Scope:** NOVEL CONSTRUCT. Medium-high effort. May defer to post-Exp 29 if complex.

### 3d. Typed LLM Classifier (for Dendritic Cell)
**What:** Replace `_MATH_PATTERN` regex with a lightweight LLM call that classifies claim type.
**Why:** Regex fundamentally cannot distinguish mathematical notation from natural language containing operators.
**Where:** Replace `_classify_claim()` internals. Keep interface identical.
**Scope:** NOVEL CONSTRUCT. Medium effort. Requires LLM API call in the triage path — adds latency.

### 3e. Lazy Tool Discovery
**What:** Deferred tool initialisation that retries failed imports on each verification call, not just at module load.
**Why:** MF-36/C5-24 show static initialisation permanently locks to fallback if first import fails.
**Where:** Replace module-level tool detection in B Cell with per-call lazy discovery + caching.
**Scope:** NOVEL CONSTRUCT. Low effort.

---

## WP4: CC2 Dispatch Fix + Cell-Level Decomposition

Not an immune pipeline issue — this is the model dispatch architecture.

### 4a. CC2 Timeout Fix (immediate)
- Change timeout 300s → 900s in `experiment_11_orchestrator.py` line 114
- Change retries 3 → 1 (avoid 3× timeout cascade)
- **Effort:** 2 lines. Testable immediately.

### 4b. Cell-Level Decomposition (Exp 29 architecture)
- New dispatch mode: fresh model instance per immune cell (~2K payload each vs 340K monolithic)
- Parallel dispatch (not sequential chunking which accumulates context)
- Insect brain relay layer carries cross-cell findings as pointers
- **Effort:** Medium. Builds on existing `decomposed_dispatch.py` patterns but fundamentally different approach.

### 4c. Per-Model Context Budgets
- Add `context_char_budget` to MODEL_SPECS in `runner_core.py`
- Auto-truncate `findings_for_context` when exceeding per-model budget
- CC2: cap at 30K chars (matching DeepSeek's proven limit)
- **Effort:** Low. Configuration + one guard clause.

---

## WP5: Insect Brain (CRITICAL PATH — Not Yet Built)

Designed but not implemented. Required for Exp 29 integration test.

### Core Functions (from design doc)
- `relay()` — pass model output between rounds, mechanical formatting only
- `persist()` — write round data to external storage (JSON logs)
- `read_context()` — retrieve windowed context for relay
- `compute_metrics()` — convergence signals (γ_novel, γ_ids, C(H,E))
- `check_convergence()` — threshold comparison
- `run_immune_pipeline()` — hand findings to pipeline
- `signal_complete()` — emit convergence or failure signal

### Design Principles
- Reactive, not deliberative. No content evaluation.
- Mechanical relay: parse → store → relay with pointers (no editorial changes)
- Persistence-as-memory: external storage, not in-prompt accumulation
- Constraint box sealed: brain cannot modify CDSFL constraints or model behaviour

### Implementation Target
- New module: `bench/insect_brain.py` (or `bench/dm/_brain.py` in DM layer)
- Integration: called by orchestrator between rounds, replaces current monolithic context assembly
- **Effort:** Medium-high. Design exists. Implementation is the critical path.

---

## WP6: V2 Immune Activation + Integration Testing

### 6a. Activate V2 Components
- NK v2: production mode (disable v1). Shadow data from Run 11 validates.
- B-Cell v2: production mode. 42 SMT-LIB checks validated in shadow.
- Helper T v2: production mode. Hybrid log-odds scoring.
- Regulatory T v2: shadow mode initially (no production data yet).
- **Effort:** Low. Flag changes only.

### 6b. Integration Test Script
- New: `bench/tests/test_exp29_integration.py`
- Dispatch to all 5 models in parallel
- Feed findings through relay (not monolithic)
- Run immune pipeline on each round
- Verify convergence detection triggers correctly
- Assert CC2 completes all rounds (0 timeouts)
- **Effort:** Medium.

---

## Implementation Order

### Phase 1: Foundation (immune fixes + dispatch)
1. **WP1 P0 fixes** — 7 critical immune bugs. Fix first, they affect everything.
2. **WP2 P0 fixes** — 4 novel critical bugs (C5-01, C5-02, C5-03, C5-26 cascade components).
3. **WP4a** — CC2 timeout fix (2 lines, immediate).
4. **WP1 P1 fixes** — 15 normal-operation bugs.
5. **WP3e** — Lazy tool discovery (low effort, high impact on MF-36/C5-24).

### Phase 2: Architecture (novel constructs + brain)
6. **WP3b** — Reconciliation Gate (prevents autoimmune state corruption).
7. **WP3a** — Epistemic Routing Layer (prevents classification cascades).
8. **WP5** — Insect brain implementation (CRITICAL PATH).
9. **WP4b** — Cell-level decomposition.
10. **WP4c** — Per-model context budgets.

### Phase 3: Activation + Testing
11. **WP6a** — Activate v2 immune components.
12. **WP1 P2/P3 fixes** — Edge conditions and defence-in-depth.
13. **WP2 remaining** — C5-05, C5-23.
14. **WP6b** — Integration test script.
15. **WP3c/3d** — Formalisation Agent and Typed LLM Classifier (defer if complex).

### Phase 4: Exp 29 Execution
16. Run Exp 29 with full architecture active.
17. Evaluate against integration test success criteria.
18. Feed results into Bench Run 2 preparation.

---

## Estimated Scope

| Work Package | Findings | Effort | Priority |
|-------------|----------|--------|----------|
| WP1: Immune P0 | 7 | Low-Medium | Immediate |
| WP1: Immune P1 | 15 | Medium | Phase 1 |
| WP1: Immune P2/P3 | 18 | Medium | Phase 3 |
| WP2: C5 Novel | 6 | Low-Medium | Phase 1 |
| WP3: Novel Constructs | 5 | Medium-High | Phase 2 |
| WP4: Dispatch | 3 items | Low-Medium | Phase 1-2 |
| WP5: Insect Brain | 1 module | Medium-High | Phase 2 (critical) |
| WP6: Activation + Tests | 2 items | Low-Medium | Phase 3 |

**Total: 46 bug fixes + 5 novel constructs + 1 new module + 1 dispatch fix + integration tests.**

---

## Notes

- MF-28 should be verified and removed from registry if C5's retraction is correct.
- WP3c (Formalisation Agent) and WP3d (Typed LLM Classifier) add LLM calls to the triage/verification path. This increases latency and API cost. May be better suited for post-Exp 29 optimisation once the base architecture is proven.
- The insect brain (WP5) is the single biggest blocker. Everything else can proceed in parallel. WP5 must be complete before Exp 29 can run.
- V2 activation (WP6a) should happen AFTER WP1 P0/P1 fixes, since v2 components inherit some v1 code paths.
