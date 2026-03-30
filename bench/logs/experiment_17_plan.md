# Experiment 17 Plan: Immune Response Layer Validation

**Status:** APPROVED — reviewed by 5 models under CDSFL (Experiment 16, `837e48e`)
**Test article:** `bench/dynamic_management.py` — full file, analytical boundary = immune subsystem
**Predecessor:** Experiment 15 (286 findings, 204 from rounds 1-7, 170 with proposed fixes)
**Experiment 16:** 5/5 models produced reviews. 11 convergent themes identified, all resolved below.

---

## 1. Objective

Evaluate and stress-test the self-adaptive immune response layer in `dynamic_management.py` against:
- The mathematical model in `docs/MATHEMATICAL_APPENDIX.md`
- The 204 round-level findings from Experiment 15
- The 6 convergent findings where multiple models independently identified the same issue
- Prospective fault discovery via induced-failure scenarios (Exp 16 improvement)

## 2. Scope

### Test article delivery

**Full file, bounded analytically** (Exp 16 convergent: all 5 models). Do NOT extract
lines into a fragmented file. Provide the complete `dynamic_management.py` to all models.
The system prompt defines the analytical boundary as the immune subsystem components below.
This avoids missing dependencies, shared state, and implicit contracts.

### Analytical boundary (immune layer components)

| Component | Approx. Lines | Purpose |
|-----------|--------------|---------|
| `DetectorDiagnosis` | ~2428-2500 | Diagnosis data structure |
| `DetectorHealthMonitor` | ~2469-4112 | System-level health detection + self_diagnose() |
| `FailureHandler` | ~4143-4600 | Model failure detection and recovery |
| `_REMEDIATION_CHAINS` | ~5567+ | Remediation chain definitions |
| `DynamicManager.process_round()` | ~4997-5250+ | Immune feedback loop integration |
| `_apply_transform()` / `apply_diagnosis()` | ~5640+ | Diagnosis-to-action mapping |
| `immune_feedback_enabled` / `immune_damping_rounds` | Config (~145-172) | Immune tuning parameters |

**Note:** Line numbers are approximate and may shift after fixes. Use function/class names
as primary references.

### Dependency interface summary

Provide all models with a 1-2 page interface summary listing:
- Every function the immune subsystem calls outside the analytical boundary (signature + contract)
- Every piece of shared mutable state (`capability_scores`, `pre_decompose_models`, etc.)
- Every config parameter affecting immune behaviour defined elsewhere

### Out of scope (with interface contracts)
- Role assignment (Area 1) — out of scope, but include interface contract tests for immune-triggered reassignment
- Load balancing (Area 2) — out of scope, but include explicit interaction scenarios (bench/unbench, feasibility block then decomposition, role reassignment after immune-triggered failures)
- Convergence detection (Area 4) — tested separately, interfaces only
- Diminishing returns (Area 5) — tested separately, interfaces only

## 3. Pre-applied Fixes (Layer 1 engineering)

Before Experiment 17 runs, these fixes are already in place:

1. **Parser fix:** Triple-backtick fence stripping + tuple-format parser with `[A-Z0-9_]*` ID pattern, escaped-quote-safe regex (no DOTALL), indented fence handling, `proposed_fix` field stored
2. **Process resilience:** httpx timeouts on all API clients + multiprocessing watchdog (wall-clock kill)
3. **Dynamic experiment numbering:** Auto-increment from `bench/logs/experiment_*` directory scan

**Preflight revalidation** (Exp 16 convergent: ChatGPT, DeepSeek): Before live execution,
run acceptance checks for all Layer 1 fixes: parser fixture corpus, watchdog kill test,
timeout propagation test, experiment-numbering test.

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
| CC2 (Opus 4.6) | Player-Manager | OpenRouter |
| Codex (GPT-5.4) | Player | `codex exec` |
| ChatGPT (GPT-5.4) | Player | OpenRouter |
| Gemini (3.1 Pro) | Player | Google API |
| DeepSeek (R1-0528) | Player (decomposed) | DeepSeek API |

CC1 (this instance) = oversight/collator.

**DeepSeek decomposition** (Exp 16 convergent: all 5 models): DeepSeek receives per-area
decomposition of the immune subsystem: (a) Detection structures (DetectorDiagnosis +
DetectorHealthMonitor), (b) Response (FailureHandler), (c) Integration (process_round +
apply_diagnosis + config). Other models receive the full file.

### 5.2 Test article preparation

The test article is the complete `bench/dynamic_management.py` file. The system prompt
defines the analytical boundary as the immune response subsystem (see §2).

All models also receive:
- The dependency interface summary (§2)
- The mathematical appendix cross-reference table (§5.4.3)

### 5.3 Round structure

**Round 0A (blind discovery):** Each model receives the immune subsystem code only.
Task: independently identify issues, propose specific fixes. No prior findings provided.
(Exp 16 convergent: CC2, Codex, ChatGPT, Gemini — 4/5 agree blind round must not
include prior findings.)

**Round 0B (seeded validation):** Models receive the 6 convergent findings from Experiment 15.
Task: validate whether fixes are correct, challenge no-fix-needed rationales, identify
what Round 0A missed. Compare overlap with 0A for independence evidence.

**Rounds 1-N (adaptive):** Standard CDSFL adaptive rounds with the DynamicManager
controlling allocation, convergence detection, and stop decisions. Models receive prior
findings and must produce novel findings or validate/challenge existing ones.

**Stop conditions** (Exp 16 convergent: CC2, ChatGPT, Codex — 3/5):
- **Primary:** DynamicManager's `stop()` predicate fires (with ascending abstraction guard enforced)
- **Independent safety caps:** Hard round cap = 10 rounds. Wall-clock cap = 4 hours.
  DM's `stop()` remains primary, but independent caps prevent circular self-judgment.
- Log `stop()` inputs/outputs (exhaustion, abstraction_ok) every round for external audit.

### 5.4 Verification

Each proposed fix is verified by:
1. **Code review:** Does the fix address the stated issue without introducing regressions?
2. **Unit test:** Can a test be written that fails before the fix and passes after?
3. **Mathematical model consistency:** Does the fix maintain consistency with `MATHEMATICAL_APPENDIX.md`?
4. **Cross-model corroboration:** Do 2+ models independently agree the fix is correct?
   (Exp 16 convergent: CC2, Codex, ChatGPT — 3/5. Agreement is corroborative evidence,
   not verification. At least one independent artifact — test, trace, code path proof —
   must also confirm the fix.)
5. **SymPy verification** for mathematical operations (Exp 16 convergent: CC2, ChatGPT, Gemini — 3/5):
   Any fix altering mathematical operations, score calculations, thresholds, or decay
   functions must be SymPy-verified against `MATHEMATICAL_APPENDIX.md`.

#### 5.4.1 Behaviour-driven simulation (Exp 16 convergent: CC2, ChatGPT, Gemini, DeepSeek — 4/5)

Before live execution, run induced-failure scenarios:
- **Canary test:** Inject simulated empty responses for 3 consecutive rounds. Verify
  immune response detects, waits for damping, and takes correct action.
- **False positive test:** Inject benign low-severity finding. Verify immune layer does
  not over-trigger.
- **Cascade test:** Simulate 2/5 models failing simultaneously. Verify graceful degradation.
- **Oscillation test:** Alternate good/bad responses. Verify damping prevents thrashing.

#### 5.4.2 Appendix-to-code traceability table (Exp 16: Codex IMP003, DeepSeek PF006)

Before execution, produce a cross-reference table mapping each mathematical appendix
formula to the corresponding code section (function:line). Flag any code with no
mathematical counterpart as "implementation extension."

#### 5.4.3 Round-level telemetry (Exp 16 convergent: ChatGPT, DeepSeek, CC2 — 3/5)

Log every immune-layer decision per round:
- Detection events (what triggered, signal values)
- Diagnosis (classification, severity)
- Action taken (reassign, bench, recover, none)
- Damping state (rounds remaining, escalation level)
- `stop()` inputs and outputs (exhaustion, abstraction_ok)
- Per-model failure classifications
- Allocation decisions and warnings

### 5.5 Fix application protocol

Fixes are applied in **dependency-aware severity order** (Exp 16 convergent: CC2,
ChatGPT, Gemini — 3/5). Build a small fix DAG first; apply prerequisites before
dependents, then sort remaining independent fixes by severity.

After each fix:
1. Run immune-layer-specific regression tests (see §5.4.1)
2. Run full test suite (`python3 -m pytest bench/tests/`)
3. Verify no regression
4. If regression: retain fix in staging branch with dependency notes. If a later fix
   resolves the regression, apply both together. Otherwise flag for human review.

### 5.6 Success criteria

1. All 6 convergent findings validated (reconfirmed as fixed, or challenged with evidence)
2. Immune response subsystem passes all existing + new immune-specific tests after fixes
3. **Immune actions are justified** (Exp 16 convergent: CC2, Codex, ChatGPT, Gemini — 4/5):
   If models are removed/benched, the immune response provides documented justification
   consistent with the mathematical model. Test whether actions are correct, not whether
   specific events occur.
4. **Abstraction guard behaviour validated** (Exp 16: CC2, DeepSeek): Either natural
   firing OR injected scenario demonstrates both fire and non-fire cases with expected
   decisions. Log `abstraction_ok` at each `stop()` call.
5. Findings curve shows genuine decay — novelty rate drops below 20% for 2 consecutive
   rounds (Exp 16: CC2 proposed threshold). Independent novelty audit by CC1 on a sample
   of findings as secondary check.

## 6. Risk Mitigations

| Risk | Mitigation |
|------|-----------|
| Process hang (Exp 15 PID 39633) | Multiprocessing watchdog (wall-clock kill) |
| Parser undercounting | Tuple + structured parser with CX-reviewed regex |
| DeepSeek empty response | Halved max_tokens retry + reduced-context decomposition fallback |
| Near-total attrition | DynamicManager immune response + independent round/wall-clock caps |
| Fix introduces regression | Dependency-aware DAG + staging branch + immune-specific tests |
| Self-orchestration bias | Independent stop caps + round-level telemetry for external audit |
| Blind-round anchoring | Split into R0A (blind) + R0B (seeded validation) |
| API rate limits / quota exhaustion | Pre-check quotas, exponential backoff, protocol for reduced model count |
| Immune over-triggering | Circuit breaker: if >50% models reassigned in one round, suspend immune for next round |
| Missing telemetry | Mandatory round-level logging (§5.4.3) |

## 7. Open Questions — RESOLVED (Experiment 16)

**Q1: DeepSeek decomposition?** YES — decompose into 3 sub-areas (detection, response,
integration). All 5 models agreed.

**Q2: Provide convergent findings in blind round?** NO — split into R0A blind + R0B
seeded validation. 4/5 models agreed (CC2, Codex, ChatGPT, Gemini). DeepSeek dissented
(provide for calibration). Majority resolution: blind first, seeded second.

**Q3: immune_damping_rounds value?** SET TO 2. CC2 and Codex recommend 2. ChatGPT and
Gemini recommend 1. DeepSeek recommends 3. Median = 2. Instrument for observability;
adjust if oscillation observed.

**Q4: Load balancing in scope?** SEPARATE, with interface contracts. All 5 models agreed.
Include explicit interaction scenarios (bench/unbench, feasibility block, role reassignment).

---

## 8. Post-Experiment Protocol (Exp 16 improvements)

1. **Comparison report:** Which Experiment 15 findings were confirmed/refuted, what new
   findings emerged, whether pre-applied fixes held under focused scrutiny.
2. **Self-protection audit** (CC2 IMP007): Check whether any model removed by immune
   response had been producing findings about the immune response itself. Flag as potential
   self-protective failure mode if so.
3. **Experiment manifest:** Freeze code snapshot (commit hash), prompts, model versions,
   config values by hash before execution. Store with artifacts for reproducibility.

---

*Reviewed by CC2, Codex, ChatGPT, Gemini, and DeepSeek under CDSFL (Experiment 16).
11 convergent themes resolved. Plan approved for execution.*
