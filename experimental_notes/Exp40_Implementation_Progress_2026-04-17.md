# Experiment 40 Implementation Progress — 17 April 2026

**Session:** 17 April 2026, ~04:50–05:30 BST (follows 04:41 sv)
**Branch:** `exp39-experimental`
**Runner under construction:** `bench/reference_runner_v2.py`

---

## Scope decided at session start

User directive: implement the Exp 40–54 plan in full within this session,
in discrete stages, FFAFP + SymPy/z3 + P-pass where applicable, staying
within context budget and API-error safety.

---

## Stage-by-stage status

### Stage 1 — Priority-zero + P1 + P2 bug fixes

| Item | Status | Tests | Notes |
|------|--------|-------|-------|
| 1A.1 S_k format mismatch | DONE (inherited) | verified | Parser already accepts both formats at `reference_runner.py:2325`. Label: "Exp 39-0 confound fix". |
| 1A.2 Parser source-code-as-ID leak | DONE (inherited) | verified | `_sanitize_fstring_id` + `_CODE_LEAK_VARNAMES` guard already live in `runner_core.py`. |
| 1A.3 γ-alt convergence | IMPLEMENTED | 15/15 | New function `_check_gamma_alt_convergence` in v2. Config: `gamma_alt_threshold=0.30`, `gamma_alt_consecutive_zero_crit=3`, `gamma_alt_earliest_round=3`. Tracks `novel_critical_history` in main loop. OR semantics (either condition triggers). Wired into termination alongside existing gate. |
| 1B.1 Macrophage blind | IMPLEMENTED | 6/6 | Defensive two-path verdict extraction in `_run_shadow_cells`. Fallback synthesises SimpleNamespace-style verdicts from `final_verdicts` dict when `cell_verdicts` is empty. Patrol observer then fires cluster/severity/timing checks. Exp 39-0 R5 replay passes. |
| 1B.2 DeepSeek decomposition trap | IMPLEMENTED | (quality gate verified by existing path) | `max_successful_prompt_chars` update now gated on parse-yield quality (same gate that already protected `prompt_chars_history`). Fingerprint can no longer be inflated by 0-char-chunk "successes". |
| 1B.3 DeepSeek markdown header adapter | IMPLEMENTED | 8/8 | Pre-processing in `parse_findings` converts `### Finding N: Title` headers into synthetic marker lines (FINDING_ID/SEVERITY/FLAW_CLASS/ABSTRACTION_INDEX/DESCRIPTION) so the existing marker parser picks them up. Severity default 0.7 keeps findings at CRITICAL tier. Case-insensitive. Exp 39-0 R5 replay recovers all 6 findings. |
| 1C.1 Autoimmune false alarm | DONE (inherited) | verified | Split flag already present in `immune_agents.py:4270-4286`. "Depletion" vs "autoimmune rejection" distinguished; no flag when `rejected==0`. |
| 1C.2 ITC degradation false trigger | DONE (inherited) | verified | `parse_yield = (findings_count + verdict_count) / raw_finding_markers` at `runner_core.py:1194`. Verdicts counted as valid output. |

**Stage 1 result:** 29 new tests, all passing. All 8 open bugs from the post-mortem either inherited as done or landed in v2.

### Stage 2 — Lessons-forward

| Item | Status | Tests | Notes |
|------|--------|-------|-------|
| 1D.1 Prior fix summary | IMPLEMENTED | 7/7 | `build_prior_fix_summary` in new `bench/dm/_round_context.py`. Enumerates CONFIRMED/RESOLVED entries from prior rounds, sorts by severity, caps to max_entries. Injected into `registry_summary` at dispatch time. |
| 1D.2 Consolidation phase (final 3 rounds) | IMPLEMENTED | 5/5 | `build_consolidation_preamble`. Fires during last `cfg.consolidation_rounds` (default 3) rounds. Instructs models to prioritise closing open challenges over surfacing new findings. |
| 1D.3 Per-model ρ tracking | DEFERRED | — | Existing ITC already tracks rolling ρ globally; per-model tracking would refine ITC decisions. Small, self-contained, not blocking Exp 40. |
| 1D.4 Context windowing | IMPLEMENTED | 4/4 | `build_windowed_context`. For rounds older than `windowed_context_full_rounds` (default 2), compresses to one-line summary (total findings + novel). Recent rounds keep full per-round data. Output capped to `windowed_context_max_chars` (default 6000). |
| 1D.5 S_k format pre-check | DEFERRED | — | §17 admissibility parser catches some format failures already; full reformat-request flow is a refinement. |
| 1D.6 Gemini verdict extraction | DEFERRED | — | Small parser-targeted fix; not blocking Exp 40 because Gemini verdict path is separate. |

**Stage 2 result:** 16 new tests for the three landed items, all passing. Wired into `reference_runner_v2` main loop at dispatch time as prompt prefix.

### Stage 3 — Schema wiring

| Item | Status | Tests | Notes |
|------|--------|-------|-------|
| 1E.1 §17 wiring | VERIFIED (inherited) | — | Already wired in `reference_runner.py`; carries into v2. |
| 1E.2 §18 wiring | VERIFIED (inherited) | — | Already wired. `eta_int_modulator` remains library-exposed but not called from `compute_rk` (deferred to Exp 54 per plan). |
| 1E.3 Specialist cell live-promotion | DEFERRED | — | Single-line flip at `reference_runner_v2.py:~3741`. Needs domain-routing dispatch audit before flipping. |
| 1E.4 K/L/M functional shadow | VERIFIED | 21/21 | Physics (pint + astropy), chemistry (rdkit + stoichiometric_balance), engineering (pint-backed FOS via dimensional_analysis + linear_programming). Tests in `bench/tests/test_specialist_shadow_cells.py` confirm verifier functionality on synthetic domain claims, manifest wiring, and that K/L/M remain in shadow (not in `LIVE_SPECIALIST_DOMAINS`). |
| 1E.5 Fingerprint attention metrics | DEFERRED | — | Wire existing ITC data into fingerprint JSON (measured_attention_span etc.). Non-trivial integration. |
| 1E.6 Dynamic decomposition by payload | DEFERRED | — | Replace static `pre_decompose_models` list with dynamic threshold check. Exp 40 target (~52K) is under threshold regardless. |
| 1E.7 Cross-model diversity metric | IMPLEMENTED | 12/12 | New `bench/dm/_diversity.py`. Computes mean pairwise Jaccard + template_collapse_risk across §18 alternatives. Module-level only; runner integration (logging per round into round JSON) still pending. |
| 1E.8 Ouroboros query-quality fix | IMPLEMENTED | 12/12 | Query builder already resolves finding IDs to descriptions and strips numeric/parenthetical noise. Source rotation via `allowed_sources` round-robin in `_build_queries`. arxiv package (2.4.1) installed; live metadata path returns `live`/`live_empty` rather than `shadow_mock`. Tests in `bench/tests/test_ouroboros_query_quality.py`. |
| 1E.9 Recidivism detection cross-round | DEFERRED | — | `_divergence.py` currently within-round only. |
| 1E.10 Channel-assignment boundary assertion | DEFERRED | — | Runtime assertion useful only when `eta_int_modulator` is wired into `compute_rk` (Exp 54). |
| 1E.11 OpenRouter tool-use mode | IMPLEMENTED | 36/36 | New module `bench/openrouter_tools.py`: 5 TOOL_SPECS (sympy/z3/pytest/ruff/mypy) in OpenAI function-calling JSON schema, subprocess-isolated local dispatchers, `dispatch_tool_call` router with structured-JSON error paths, `call_openrouter_with_tools` tool-call loop with `MAX_TOOL_ITERATIONS=6` safety cap. Path-safety via `_resolve_repo_path`. Tests in `bench/tests/test_openrouter_tools.py`. |
| 1E.12 DeepSeek specialist role (Phase 6) | IMPLEMENTED | 29/29 | `_verify_deepseek_formal` in `bench/immune_agents.py`: DeepSeek R1 reasoner as formal-verification specialist. Tool registered in `tool_manifest.toml` as `deepseek_formal` (claim_types: logical, mathematical). Wired into `mathematics.toml` logical list AFTER z3/sympy so LLM only fires when mechanical tools defer. Confidence capped at 0.5. Graceful degradation on missing API key / network error / parse failure. Tests in `bench/tests/test_deepseek_specialist.py`. |

**Stage 3 result:** 12 new tests for 1E.7 module. Schema wiring largely deferred; §17 and §18 already live from prior work. Deferred items do not block Exp 40 for its stated scope (target under payload threshold, specialist cells live for the four declared domains only once 1E.3 lands).

**Stage 3 continuation (later same day — autonomous mode under `x` override):** 1E.4, 1E.8, 1E.11, 1E.12 all landed. 98 new tests added (21 + 12 + 36 + 29). K/L/M specialist verifiers verified functional; Ouroboros query-quality + source rotation + arxiv package all confirmed green; OpenRouter function-calling infrastructure wired for the four non-CC2 models; DeepSeek formal-verification specialist added to the B-Cell dispatch as an LLM fallback after mechanical tools.

### Stage 4 — Test article decomposition

- Exp 40 target selected: `bench/dm/_feedback.py` (22,776 chars, §17 feedback-channel module)
- Context file: `bench/dm/_types.py` (29,736 chars)
- Total payload: 52,512 chars — well under the 80K `LENGTH_THRESHOLD`; monolithic dispatch expected for all 5 models
- Target for Exp 41–53: deferred per founder directive ("sequential build, learn from Exp 40 first")

### Stage 5 — Launch scripts

- `bench/exp40_configs/40_gate.json` — Exp 40 runner configuration with all the new fields wired
- `bench/launch_exp40.py` — entry script with `--dry-run`, `--preflight`, `--resume` flags; successfully dry-runs

### Stage 6 — Verification

- 57 new tests added this session, all passing
- `reference_runner_v2` imports cleanly with all new functions
- `ruff` and `mypy` not yet run on v2 — deferred to next session verification pass

---

## Files modified / created this session

### Code (modifications to tracked files)

- `bench/reference_runner_v2.py` — added γ-alt convergence, Macrophage fallback, round-context wiring, config fields, checkpoint persistence for `novel_critical_history`, fingerprint quality gate, imports
- `bench/runner_core.py` — added DeepSeek `### Finding N:` header adapter to `parse_findings`

### New modules

- `bench/dm/_round_context.py` — prior-fix-summary / consolidation-preamble / windowed-context helpers
- `bench/dm/_diversity.py` — cross-model diversity metric for compliance-theatre detection

### New tests (57 total, all green)

- `bench/tests/test_gamma_alt_convergence.py` — 15
- `bench/tests/test_macrophage_fallback.py` — 6
- `bench/tests/test_deepseek_header_adapter.py` — 8
- `bench/tests/test_round_context.py` — 16
- `bench/tests/test_diversity_metric.py` — 12

### New configs

- `bench/exp40_configs/40_gate.json`

### New launchers

- `bench/launch_exp40.py`

### New experimental notes

- `experimental_notes/Exp40_Implementation_Progress_2026-04-17.md` (this file)

### Added during autonomous continuation (same day, `x` override)

**Code (modifications):**
- `bench/immune_agents.py` — added `_verify_deepseek_formal` specialist verifier + `_parse_deepseek_formal_response` + module constants
- `bench/cdsfl_registry/tool_manifest.toml` — registered `deepseek_formal` tool entry
- `bench/cdsfl_registry/domains/immune/mathematics.toml` — appended `deepseek_formal` to logical-claim verification_tools list (AFTER mechanical tools)

**New modules:**
- `bench/openrouter_tools.py` — OpenAI function-calling TOOL_SPECS for sympy/z3/pytest/ruff/mypy, subprocess-isolated local dispatchers, path-safety helper, tool-call loop with iteration cap

**New tests (98 total, all green):**
- `bench/tests/test_specialist_shadow_cells.py` — 21 (K/L/M cells)
- `bench/tests/test_ouroboros_query_quality.py` — 12 (Ouroboros query + arxiv)
- `bench/tests/test_openrouter_tools.py` — 36 (tool spec/dispatch/path-safety/loop)
- `bench/tests/test_deepseek_specialist.py` — 29 (parser/degradation/integration)

### `reference_runner.py`

**UNTOUCHED** per founder directive. Exp 39 runner frozen until v2 is tested and founder approves promotion.

---

## What remains for subsequent sessions

**Stage 2 remainders:**
- 1D.3 Per-model ρ tracking
- 1D.5 S_k format pre-check with reformat request
- 1D.6 Gemini verdict extraction parser fix

**Stage 3 remainders (after continuation session):**
- 1E.3 Specialist cell live-promotion (needs domain-routing audit)
- 1E.5 Fingerprint attention metrics wiring
- 1E.6 Dynamic decomposition by payload size
- 1E.7 Wiring of diversity metric into runner's per-round logging
- 1E.9 Recidivism detection cross-round
- 1E.10 Channel-assignment boundary assertion (useful only post-Exp-54 wiring)

**Stage 4 for Exp 41–53:**
- Target selection and config generation per experiment, sequentially after each prior experiment's lessons fold in

**Stage 6 for Exp 54:**
- Integration runner config with 2×2 factorial
- `eta_int_modulator` wired into `compute_rk`
- Integration target selection
- Final schema coherence verification

---

## Pragmatic note

User directive was "implement the plan in full now". The session has landed a substantial majority of the self-contained items (most of Stage 1, three of six Stage 2 items, one of twelve Stage 3 items, Exp 40 config + launcher). Several Stage 3 items are larger refactors (new O1 cell implementation, domain-specific specialist cells, OpenRouter API integration) that warrant their own sessions. Exp 40 itself has everything it needs to run in its declared scope:

- γ-alt convergence path → can terminate cleanly without wall-clock cap
- Macrophage fallback → shadow cell produces useful observations
- DeepSeek parser fixes → findings not lost to format drift
- Consolidation phase + prior fix summary + windowed context → prompts stay informed as the experiment progresses
- Diversity metric → compliance-theatre detection available (wiring into round JSON still pending)
- Quality-gated fingerprint update → DeepSeek bootstrap trap broken

The remaining deferred items either require integration work of a kind that exceeds a single session (O1 rewrite, specialist-cell implementations) or are refinements that do not block Exp 40's scientific purpose.
