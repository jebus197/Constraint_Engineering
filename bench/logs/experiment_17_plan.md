# Experiment 17 Plan: Immune Response Layer Validation

**Status:** DRAFT — to be reviewed and improved by models under CDSFL (Experiment 16)
**Test article:** `bench/dynamic_management.py` — specifically the immune response subsystem
**Predecessor:** Experiment 15 (286 findings, 204 from rounds 1-7, 170 with proposed fixes)

---

## 1. Objective

Validate the self-adaptive immune response layer in `dynamic_management.py` against:
- The mathematical model in `docs/MATHEMATICAL_APPENDIX.md`
- The 204 round-level findings from Experiment 15
- The 6 convergent findings where multiple models independently identified the same issue

## 2. Scope

### In scope (immune layer components)

| Component | Lines | Purpose |
|-----------|-------|---------|
| `DetectorDiagnosis` | ~2428 | Diagnosis data structure |
| `DetectorHealthMonitor` | ~2437 | System-level health detection |
| `FailureHandler` | ~4143 | Model failure detection and recovery |
| `DynamicManager.process_round()` | ~5050-5250 | Immune feedback loop integration |
| `DynamicManager.apply_diagnosis()` | ~5640+ | Diagnosis-to-action mapping |
| `immune_feedback_enabled` / `immune_damping_rounds` | Config | Immune tuning parameters |

### Out of scope
- Role assignment (Area 1) — unless immune response interacts with it
- Load balancing (Area 2) — unless immune response triggers rebalancing
- Convergence detection (Area 4) — tested separately, interfaces only
- Diminishing returns (Area 5) — tested separately, interfaces only

## 3. Pre-applied Fixes (Layer 1 engineering)

Before Experiment 17 runs, these fixes are already in place:

1. **Parser fix:** Triple-backtick fence stripping + tuple-format parser with `[A-Z0-9_]*` ID pattern, escaped-quote-safe regex (no DOTALL), indented fence handling, `proposed_fix` field stored
2. **Process resilience:** httpx timeouts on all API clients + multiprocessing watchdog (wall-clock kill)
3. **Dynamic experiment numbering:** Auto-increment from `bench/logs/experiment_*` directory scan

## 4. Experiment 15 Convergent Findings — Resolution Status

These findings were independently reported by 2+ models in Experiment 15 rounds 1-7.

### 4.1 Ascending abstraction guard not enforced — FIXED
**Models:** Codex R5, Gemini R5, ChatGPT R5 | **Severity:** 0.85-0.93
**Fix applied:** `stop()` now includes `abstraction_ok` as a conjunctive condition. `_abstraction_dropping()` uses `<=` (flat or dropping = ok to stop; ascending = keep going). Permissive at rounds 0-1 (insufficient data). 350 tests pass.

### 4.2 `reassign()` capability score persistence — FIXED
**Models:** DeepSeek R1, Gemini blind | **Severity:** 0.90-0.95
**Fix applied:** COL scores computed in `reassign()` are now persisted back to `self.capability_scores[mid][Role.COL.value]`.

### 4.3 Redundancy target uses total pool not admissible models — NO FIX NEEDED
**Models:** ChatGPT R2, Codex R2 | **Severity:** 0.88-0.92
**Resolution:** By design. `_redundancy_target()` uses total pool `K` as the theoretical maximum. The greedy solver already handles infeasibility via force-assign fallback. The new feasibility pre-check (4.4) surfaces when this becomes degraded.

### 4.4 `_solve_greedy()` missing feasibility check — FIXED
**Models:** Codex R2 | **Severity:** 0.92
**Fix applied:** Upfront feasibility check counts admissible models with capacity before allocation. Warnings logged to `_allocation_warnings` when target cannot be met. Force-assign fallback preserved for coverage.

### 4.5 Recovery actions not communicated — FIXED
**Models:** Gemini R6 | **Severity:** 0.88
**Fix applied:** `recovery_actions: Dict[str, str]` added to `RoundResult`. Populated in `process_round()` from `FailureHandler.get_recovery()` results.

### 4.6 Per-model yield counts raw not novel findings — NO FIX NEEDED
**Models:** Codex R5 | **Severity:** 0.87
**Resolution:** Already fixed in committed code. `add_model_round()` receives only novel findings (filtered through `_novel_classes()`).

## 5. Test Protocol

### 5.1 Models and roles

| Model | Role | Dispatch |
|-------|------|----------|
| CC2 (Opus 4.6) | Player-Manager | Direct (subagent) |
| Codex (GPT-5.4) | Player | `codex exec` |
| ChatGPT (GPT-5.4) | Player | OpenRouter |
| Gemini (3.1 Pro) | Player | Google API |
| DeepSeek (R1-0528) | Player (decomposed) | DeepSeek API |

CC1 (this instance) = oversight/collator.

### 5.2 Test article preparation

The test article for Experiment 17 is the immune response subsystem extracted from `dynamic_management.py`. Specifically:
- Lines 2428-2850 (DetectorDiagnosis, DetectorHealthMonitor)
- Lines 4143-4600 (FailureHandler)
- Lines 5050-5250 (process_round immune integration)
- Lines 5640-5700 (apply_diagnosis)
- Config parameters (lines 145-170)

Total: ~1,200 lines focused on immune behaviour.

### 5.3 Round structure

**Round 0 (blind):** Each model receives the immune subsystem code + the 6 convergent findings. Task: validate whether the convergent findings are correct, identify any the previous round missed, and propose specific fixes.

**Rounds 1-N (adaptive):** Standard CDSFL adaptive rounds with the DynamicManager controlling allocation, convergence detection, and stop decisions. Models receive prior findings and must produce novel findings or validate/challenge existing ones.

**Stop condition:** DynamicManager's `stop()` predicate fires (with ascending abstraction guard enforced — fix 4.1 applied before this experiment).

### 5.4 Verification

Each proposed fix is verified by:
1. **Code review:** Does the fix address the stated issue without introducing regressions?
2. **Unit test:** Can a test be written that fails before the fix and passes after?
3. **Mathematical model consistency:** Does the fix maintain consistency with `MATHEMATICAL_APPENDIX.md`?
4. **Cross-model agreement:** Do 2+ models independently agree the fix is correct?

SymPy verification is not applicable (code review, not mathematical claims). If any finding references mathematical model formulas, those specific claims can be SymPy-verified.

### 5.5 Fix application protocol

Fixes are applied in severity order, highest first. After each fix:
1. Run existing test suite (currently: `python3 -m pytest bench/tests/`)
2. Verify no regression in existing tests
3. If regression: revert and flag for human review

### 5.6 Success criteria

1. All 6 convergent findings resolved (applied, rejected with justification, or deferred with rationale)
2. Immune response subsystem passes all existing tests after fixes
3. At least 3 models survive to round 3+ (no near-total attrition as in early Exp 15 runs)
4. Ascending abstraction guard demonstrably fires during the experiment
5. Findings curve shows genuine decay (not churn) — measured by novelty rate from DiminishingReturnsDetector

## 6. Risk Mitigations

| Risk | Mitigation |
|------|-----------|
| Process hang (Exp 15 PID 39633) | Multiprocessing watchdog (wall-clock kill) |
| Parser undercounting | Tuple + structured parser with CX-reviewed regex |
| DeepSeek empty response | Existing halved max_tokens retry |
| Near-total attrition | DynamicManager immune response should detect and halt |
| Fix introduces regression | Test suite gate before each commit |

## 7. Open Questions for Experiment 16 Review

1. Is the 1,200-line scope manageable for all models, or should DeepSeek get per-area decomposition of the immune subsystem too?
2. Should the 6 convergent findings (now 4 fixed, 2 confirmed no-fix-needed) be provided as context in the blind round, or should models discover issues independently?
3. What is the appropriate immune_damping_rounds value for a 5-model pool? Current default is 2.
4. Should the load balancing layer be included in scope alongside the immune layer, or tested separately?

---

*This plan is the test article for Experiment 16. Models will review and improve it under CDSFL before it becomes the execution plan for Experiment 17.*
