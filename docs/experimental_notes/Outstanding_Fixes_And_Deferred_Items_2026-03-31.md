# Outstanding Fixes and Deferred Items

**Date:** 2026-03-31T21:56:36+01:00
**Context:** Post-compaction audit of all TTS files and experimental notes from 2026-03-30 and 2026-03-31. Cross-referenced against current codebase (HEAD `842053c`, 351 tests passing).

**Purpose:** Persistent record of every unimplemented actionable item so nothing is lost to context compaction. Status tags: `PENDING`, `DEFERRED`, `BLOCKED`, `SUPERSEDED`.

---

## 1. CX Dispatch Configuration

### 1a. Disable MCP servers in `call_codex()` — `PENDING`
- **Source:** CX Prompt Efficiency Confer (2026-03-30)
- **Problem:** CX spends 78 tool calls investigating the repo instead of analysing the briefing. 155K tokens wasted per dispatch.
- **Fix:** Add `--no-mcp-servers` flag to `codex exec` invocation in `bench/run_benchmark.py` (lines 605-672).
- **Verification:** Confirm flag exists in CX CLI (`codex exec --help`). If not available, investigate alternative.
- **File:** `bench/run_benchmark.py`, function `call_codex()`

### 1b. Disable plugins in `call_codex()` — `PENDING`
- **Source:** CX Prompt Efficiency Confer (2026-03-30)
- **Problem:** Same token waste as 1a.
- **Fix:** Add `--no-plugins` flag if CX CLI supports it.
- **File:** `bench/run_benchmark.py`, function `call_codex()`

### 1c. Reasoning effort — `SUPERSEDED`
- **Source:** CX Prompt Efficiency Confer (2026-03-30)
- **Original proposal:** Change from `"xhigh"` to `"medium"` in `codex_5_3.toml`.
- **Founder decision (2026-03-31):** Rejected. Maximum reasoning stays as default. Tasks are too complex to throttle. If reasoning effort should be user-configurable, that is a separate feature — not a default downgrade.
- **File:** `bench/cdsfl_registry/models/codex_5_3.toml` (line 8) — no change.

### 1d. Make reasoning effort user-configurable — `DEFERRED`
- **Source:** Founder observation (2026-03-31)
- **Rationale:** Users who want less capable models should be able to select that. But the default must remain maximum capability.
- **Trigger:** When CDSFL has external users beyond the founder.

---

## 2. Parallel Dispatch (Gemini Proposal)

### 2a. Parallel blind-round dispatch — `IMPLEMENTED (1 April 2026)`
- **Source:** Gemini 9-page proposal, P-passed 2026-03-31. Survived as genuinely useful.
- **Change:** `_dispatch_round` refactored: per-model work extracted into `_dispatch_single_model()`, blind rounds dispatch via `ThreadPoolExecutor(max_workers=N)`. FFF-verified thread safety: _log (stderr, GIL-safe), DynamicManager (read-only during dispatch), save_output (unique filenames), _record_throughput (dict.setdefault+append, GIL-safe). Immune failure reports deferred to main thread (DynamicManager.apply_diagnosis not thread-safe).
- **Expected gain:** T_async = max(t_i) instead of T_sync = Σt_i. ~44% wall-clock reduction for 5 models (Run 6 R0: 825s sequential → ~465s parallel, Codex bottleneck).
- **File:** `bench/run_baseline_confer.py` (`_dispatch_single_model`, `_dispatch_round`)

### 2b. Hybrid async-then-sync round structure — `IMPLEMENTED (1 April 2026)`
- **Source:** Same Gemini proposal.
- **Change:** Blind rounds dispatch in parallel; adaptive/confer rounds remain sequential (models need to see each other's findings). Implemented as `parallel = round_type == "blind"` gate in `_dispatch_round`.
- **Maps to:** Existing `blind_first` → adaptive round structure in `DynamicManagementConfig`.

### 2c. Gemini's SI formula — `SUPERSEDED`
- **Source:** Gemini proposal, SymPy-verified as INCORRECT (2026-03-31).
- **Problem:** SI = (Σ NMI(π) · (1 - C_ij))^{-1} inverts the relationship between contradictions and instability. Should be NMI · C_ij, not NMI · (1 - C_ij).
- **Action:** Do not implement. Formula is mathematically wrong. Gemini notified via findings.

### 2d. Epistemic Mesh / Sovereign Shards — `DEFERRED`
- **Source:** Gemini proposal.
- **Status:** Marked as promising direction but math needs rework. Far-future architecture.
- **Trigger:** Post-Bench Run 2, after parallel dispatch and FFF are validated.

---

## 3. Whole Body Architecture

### 3a. Phase 1 — Attributed findings — `PENDING`
- **Source:** Whole Body Architecture TTS (2026-03-30)
- **Change:** Each finding carries `source_model` field through the data structures passed between rounds, not just in logs.
- **Rationale:** Adaptive rounds need model attribution to weight findings properly. Currently findings are attributed in log output but not in the `Finding` dataclass.
- **Implementation:** Add `source_model: str` field to `Finding` dataclass, populate during `parse_findings()`, preserve through aggregation.
- **Files:** `bench/dynamic_management.py` (Finding class), `bench/run_exp17_immune.py` (`parse_findings`), `bench/run_round_robin.py`

### 3b. Phase 2 — Sequential dispatch pipeline — `DEFERRED`
- **Trigger:** After Phase 1 validated.

### 3c. Phase 3 — Multi-step dispatch with pacing signals — `DEFERRED`
- **Trigger:** After Phase 2 validated.

### 3d. Phase 4 — Closed-loop feedback (streaming) — `DEFERRED`
- **Trigger:** After Phase 3, requires streaming API support.

---

## 4. Founder's Three Strategic Observations

### 4a. γ unification — `IMPLEMENTED (1 April 2026)`
- **Source:** Founder observation (2026-03-31), recorded in `Founders_FFF_Observations_2026-03-31.md`
- **Insight:** Decay curve γ already measures what the diminishing-returns stop signal (vocabulary saturation + novelty window + abstraction guard) measures via proxies.
- **SymPy verification (1 April 2026):** Heaps' law dV/dn = K·β·n^{β−1} has identical form to Duane λ(n) = α·γ·n^{γ−1}. Vocabulary saturation and novelty window are discretized approximations of γ monitoring. Abstraction guard is independent (γ measures count, not depth).
- **Implementation:** `run_baseline_confer.py` — replaced `_check_convergence()` with γ threshold (0.5) + Y(t) cognitive yield monotonicity guard. Subsumes τ_vocab_growth and novelty_window. Keeps abstraction guard. 3 params → 1 γ threshold + 1 Y(t) check.
- **Validation:** Synthetic test: 20→10→5→3 findings → γ=0.537 → converged. Ascending abstraction (10 shallow → 3 deep) → γ=0.621 but Y(t) ascending → NOT converged. Both correct.

### 4b. Deep FFF (multi-turn FFF within single model) — `DEFERRED`
- **Source:** Founder observation (2026-03-31)
- **Concept:** Keep dispatching to same model with cumulative context until model declares convergence. Decomposed dispatch infrastructure already supports multi-turn.
- **Testing:** Could be third condition in Experiment 19, or separate experiment.
- **Trigger:** After single-turn FFF validated in controlled experiment (Exp 19).

### 4c. Insight propagation mechanism — `DEFERRED`
- **Source:** Founder observation (2026-03-31)
- **Concept:** Formalise how knowledge propagates (human → CC → models → codebase). Allow all models to learn from humans and each other. Natural selection on methodology.
- **Trigger:** Post-web-layer, when signal pipeline exists. Genesis `InsightSignal` protocol is the eventual home.

---

## 5. Mathematical Appendix

### 5a. Ising bounded ψ — not wired into composer code — `DEFERRED`
- **Source:** MATHEMATICAL_APPENDIX.md §0.1, SymPy-verified.
- **Formula:** Σψ ≤ −Σlog(1−q_i)
- **Status:** Proven and documented. Not enforced in `composer.py`.
- **Reason for deferral:** Coupling constants need empirical calibration from experiment data before enforcement is meaningful. Enforcing uncalibrated bounds would be cargo-cult mathematics.
- **Trigger:** Post-Bench Run 2, when sufficient (D, v̄, A, C) fingerprint data exists to fit ψ values.

### 5b. Namespace refactor — code variable alignment — `DEFERRED`
- **Source:** Commit `c7f9e7a`, 17 symbol collisions resolved in documentation.
- **Status:** Appendix uses new symbols. Code still uses old variable names in places.
- **Risk of immediate change:** Rename-refactor across `dynamic_management.py` (6,354 lines) risks regressions.
- **Trigger:** Next major code refactor cycle. Low urgency — the code works, the docs are correct, the mapping is documented.

### 5c. Appendix §9 (attention dynamics) — `DEFERRED`
- **Source:** Round 8 construct evaluation (2026-03-31)
- **Status:** Section designed but not written into document.
- **Trigger:** Next appendix editorial pass.

### 5d. Appendix §10 (networked corroboration) — `DEFERRED`
- **Source:** Round 8 construct evaluation (2026-03-31)
- **Status:** Section designed but not written into document.
- **Trigger:** Next appendix editorial pass.

### 5e. Two CX minor modifications — `DEFERRED`
- **Source:** Mathematical Coherence Audit (2026-03-31)
- **Items:** (1) q_i terminology clarification (baseline Bernoulli vs post-coupling marginals), (2) piecewise weight definition for null-vector case.
- **Status:** Editorial refinements, not code-affecting.
- **Trigger:** Next appendix editorial pass. Bundle with 5c/5d.

---

## 6. Composer Enhancements

### 6a. Pre-digestion bias mitigation (tier 2) — `PENDING`
- **Source:** CX Prompt Efficiency Confer (2026-03-30)
- **Problem:** CC1 pre-selecting code for CX briefings creates blind spots for omitted adjacent code.
- **Fix (tier 2):** Periodic full-repo access rounds for CX to independently verify extraction completeness.
- **Status:** Tier 1 (skeletal signatures of adjacent code) implemented. Tier 2 not yet done.
- **Priority:** Low — safeguard, not primary fix.

### 6b. Coherence budget empirical calibration — `PENDING`
- **Source:** Composer Review Confer (2026-03-31)
- **Status:** Calibration function exists in composer.py but has no experiment data to calibrate against.
- **Trigger:** After Bench Run 2 produces sufficient per-model quality data at different instruction densities.

---

## 7. Experiment Design

### 7a. Experiment 19 — FFF controlled hypothesis test — `PENDING`
- **Runner:** `bench/run_exp19_fff.py` (1,078 lines, fully built)
- **Status:** Code complete, not yet executed.
- **Conditions:** A (standard CDSFL) vs B (CDSFL + FFF)
- **Blocked by:** Nothing. Ready to run.

### 7b. Experiment 20 — Sequential confer — `PENDING`
- **Runner:** `bench/run_exp20_confer.py` (renamed from exp18)
- **Status:** Code complete, not yet executed.

### 7c. Composable Directives Experiment — `DEFERRED`
- **Source:** CDSFL Composable Directives Confer (2026-03-31)
- **Hypothesis:** Do N configurations of one model produce finding diversity equivalent to N different models?
- **Status:** Design complete (5 proposed arms, kill criteria defined). Ready for execution after current work phase.

---

## Execution Sequence (Founder-Approved)

1. ✅ Write this tracking file (this document)
2. ✅ γ unification implemented + C(H,E) Popper corroboration added (1 April 2026)
3. **NEXT:** Run 4 — standard CDSFL confer with CC2 + CX + Gemini on immune task area. γ-unified stop signal. C(H,E) reporting. FFF via situation layer. Clean baseline.
4. **AFTER BASELINE:** Layer in changes one at a time, measured against baseline:
   - First: CX MCP/plugin flags (items 1a, 1b)
   - Then: Parallel blind dispatch (item 2a)
   - Then: Finding attribution (item 3a)
   - Each measured independently

---

*This file is the single source of truth for outstanding work. Update status tags as items are completed or reclassified.*
