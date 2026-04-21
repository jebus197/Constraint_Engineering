# Experiment 40 Implementation Progress — 17 April 2026

**Session:** 17 April 2026, ~04:50–05:30 BST (follows 04:41 sv)
**Branch:** `exp39-experimental`
**Runner under construction:** `bench/reference_runner_v2.py`

---

## Scope

Implement the Exp 40–54 plan in full, in discrete stages, with
FFAFP + SymPy/z3 + P-pass where applicable, within context budget and
API-error safety.

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
| 1D.3 Per-model ρ tracking | IMPLEMENTED (Phase B `bdfc93a`) | — | Per-model `novelty_counts_per_model` + `raw_counts_per_model` history tracked across rounds in `reference_runner_v2.py`. Checkpoint round-trip extended. ITC decisions can now target stuck models rather than applying a global threshold. Tests in `bench/tests/test_per_model_rho_itc.py`. |
| 1D.4 Context windowing | IMPLEMENTED | 4/4 | `build_windowed_context`. For rounds older than `windowed_context_full_rounds` (default 2), compresses to one-line summary (total findings + novel). Recent rounds keep full per-round data. Output capped to `windowed_context_max_chars` (default 6000). |
| 1D.5 S_k format pre-check | IMPLEMENTED (Phase A `8b8682d`) | 18/18 | New `bench/dm/_sk_format.py` detects findings whose `proposed_fix` does not parse as an `S_k` SEARCH/REPLACE block, and builds a reformat-request prompt section for the next round. Wired into `reference_runner_v2.py` for both star and relay topologies. |
| 1D.6 Gemini verdict extraction | IMPLEMENTED (Phase A `8b8682d`) | 40/40 | `_VERDICT_RE` broadened to cover bold-wrapped keywords, underscore/double-underscore italics, bullet prefixes, numbered lists, blockquotes, and colon/period separators. Trailing `**`/`__` stripped from descriptions. Includes Exp 39-0 Gemini regression samples. |

**Stage 2 result (original session):** 16 new tests for 1D.1/1D.2/1D.4, all passing. Wired into `reference_runner_v2` main loop at dispatch time as prompt prefix.

**Stage 2 completion (Phase A + B commits later same day):** 1D.3, 1D.5, 1D.6 all landed. All six Stage 2 items now live.

### Stage 3 — Schema wiring

| Item | Status | Tests | Notes |
|------|--------|-------|-------|
| 1E.1 §17 wiring | VERIFIED (inherited) | — | Already wired in `reference_runner.py`; carries into v2. |
| 1E.2 §18 wiring | VERIFIED (inherited) | — | Already wired. `eta_int_modulator` remains library-exposed but not called from `compute_rk` (deferred to Exp 54 per plan). |
| 1E.3 Specialist cell live-promotion | AUDIT LANDED (Phase B `bdfc93a`) | — | `test_specialist_live_promotion.py` verifies the `LIVE_SPECIALIST_DOMAINS` contract and which domains remain in shadow. The actual live-promotion flip is a single-line change deferred until K/L/M tool coverage broadens to more claim types. |
| 1E.4 K/L/M functional shadow | VERIFIED | 21/21 | Physics (pint + astropy), chemistry (rdkit + stoichiometric_balance), engineering (pint-backed FOS via dimensional_analysis + linear_programming). Tests in `bench/tests/test_specialist_shadow_cells.py` confirm verifier functionality on synthetic domain claims, manifest wiring, and that K/L/M remain in shadow (not in `LIVE_SPECIALIST_DOMAINS`). |
| 1E.5 Fingerprint attention metrics | IMPLEMENTED (Phase B `bdfc93a`) | — | New `_compute_attention_metrics()` in `reference_runner_v2.py` populates `measured_attention_span`, `compression_threshold`, `quality_at_capacity`, `decomposition_recommended`, `attention_ratio`, `D_decay` from ITC + parse-yield history. Previously-null fingerprint fields now real, unblocking `burst_planner`'s `D_decay` quality gate. Tests in `bench/tests/test_fingerprint_attention_metrics.py`. |
| 1E.6 Dynamic decomposition by payload | IMPLEMENTED (Phase A `8b8682d`) | 8/8 | New `should_decompose_v2()` adds a fingerprint-agnostic 80K hard floor on top of `_should_decompose()`. Hard floor overrides observed-capacity for payloads above `LENGTH_THRESHOLD`. Tests in `bench/tests/test_decompose_payload_floor.py`. |
| 1E.7 Cross-model diversity metric | IMPLEMENTED (Phase A `8b8682d`) | 12+8 | Module `bench/dm/_diversity.py` (mean pairwise Jaccard + `template_collapse_risk`) PLUS runner wiring: `parse_alternative_block` invoked per-finding on raw responses; pooled alternatives feed `diversity_signal_from_round`; result lands in `round_data` under `cross_model_diversity`. Logging-only, does not gate R_k. |
| 1E.8 Ouroboros query-quality fix | IMPLEMENTED | 12/12 | Query builder already resolves finding IDs to descriptions and strips numeric/parenthetical noise. Source rotation via `allowed_sources` round-robin in `_build_queries`. arxiv package (2.4.1) installed; live metadata path returns `live`/`live_empty` rather than `shadow_mock`. Tests in `bench/tests/test_ouroboros_query_quality.py`. |
| 1E.9 Recidivism detection cross-round | IMPLEMENTED (Phase B `bdfc93a`) | — | `AlternativeRecord.prior_round_isomorphism` added; `check_sibling_admissibility(..., prior_round_alternatives=...)` scores against prior-round alternatives and demotes when Jaccard ≥ `near_copy_threshold`. Runner threads `prior_round_alternatives_by_finding` across rounds. Tests in `bench/tests/test_cross_round_recidivism.py`. |
| 1E.10 Channel-assignment boundary assertion | IMPLEMENTED (Phase A `8b8682d`) | 24/24 | `ChannelViolationError` + `compute_rk_with_eta_channel()` wrapper enforces that `m_div` enters `R_k` only via `eta_int`, never as pre-factor on `R_k` or free factor in `q`. SymPy verified (dq/dm_div > 0; q(m_div=1) = q_unmodulated; channel vs forbidden paths differ by 0.23 at representative values). Runtime assertion at the call site remains gated on `eta_int_modulator` landing in Exp 54. |
| 1E.11 OpenRouter tool-use mode | IMPLEMENTED | 36/36 | New module `bench/openrouter_tools.py`: 5 TOOL_SPECS (sympy/z3/pytest/ruff/mypy) in OpenAI function-calling JSON schema, subprocess-isolated local dispatchers, `dispatch_tool_call` router with structured-JSON error paths, `call_openrouter_with_tools` tool-call loop with `MAX_TOOL_ITERATIONS=6` safety cap. Path-safety via `_resolve_repo_path`. Tests in `bench/tests/test_openrouter_tools.py`. |
| 1E.12 DeepSeek specialist role (Phase 6) | IMPLEMENTED | 29/29 | `_verify_deepseek_formal` in `bench/immune_agents.py`: DeepSeek R1 reasoner as formal-verification specialist. Tool registered in `tool_manifest.toml` as `deepseek_formal` (claim_types: logical, mathematical). Wired into `mathematics.toml` logical list AFTER z3/sympy so LLM only fires when mechanical tools defer. Confidence capped at 0.5. Graceful degradation on missing API key / network error / parse failure. Tests in `bench/tests/test_deepseek_specialist.py`. |

**Stage 3 result (original session):** 12 new tests for 1E.7 module. §17 and §18 already live from prior work.

**Stage 3 continuation 1 (later same day — autonomous mode under `x` override):** 1E.4, 1E.8, 1E.11, 1E.12 all landed. 98 new tests added (21 + 12 + 36 + 29).

**Stage 3 completion (Phase A commit `8b8682d` + Phase B commit `bdfc93a`):** 1D.5, 1D.6, 1E.6, 1E.7-runner-wiring, 1E.10 (Phase A); 1D.3, 1E.3-audit, 1E.5, 1E.9 (Phase B). Full bench suite 1250/1250 passing as of `bdfc93a`. The only substantive open item is **1E.3 live-promotion flip** (a one-line `LIVE_SPECIALIST_DOMAINS` edit held back pending broader K/L/M tool-coverage confirmation), plus **1E.10 runtime call-site assertion** which depends on `eta_int_modulator` being wired into `compute_rk` in Exp 54.

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

### Added during autonomous continuation 1 (same day, `x` override)

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

### Added during autonomous continuation 2 — Phase A commit `8b8682d` (98 tests)

**Code (modifications):**
- `bench/reference_runner_v2.py` — S_k format pre-check wiring for star + relay, `should_decompose_v2` 80K hard floor, diversity-metric per-round logging into `round_data.cross_model_diversity`, `compute_rk_with_eta_channel` wrapper

**New modules:**
- `bench/dm/_sk_format.py` — detects malformed `proposed_fix` blocks, builds reformat-request prompt section
- (Verdict-parser broadening in existing Gemini parser path)

**New tests (all green):**
- `bench/tests/test_sk_format_precheck.py` — 18 (1D.5)
- `bench/tests/test_verdict_parser_gemini.py` — 40 (1D.6, includes Exp 39-0 regression)
- `bench/tests/test_decompose_payload_floor.py` — 8 (1E.6)
- `bench/tests/test_cross_model_diversity.py` — (1E.7 module) + 8 new runner-wiring tests
- `bench/tests/test_channel_boundary.py` — 24 (1E.10 base module + SymPy verification)

### Added during autonomous continuation 3 — Phase B commit `bdfc93a` (200+ tests)

**Code (modifications):**
- `bench/reference_runner_v2.py` — `_compute_attention_metrics`, per-model ρ tracking (`novelty_counts_per_model`, `raw_counts_per_model`), `prior_round_alternatives_by_finding` cross-round threading
- `bench/dm/_divergence.py` — `AlternativeRecord.prior_round_isomorphism` + `check_sibling_admissibility(..., prior_round_alternatives=...)` extended

**New tests (all green):**
- `bench/tests/test_per_model_rho_itc.py` (1D.3)
- `bench/tests/test_specialist_live_promotion.py` (1E.3 audit)
- `bench/tests/test_fingerprint_attention_metrics.py` (1E.5)
- `bench/tests/test_cross_round_recidivism.py` (1E.9)

**Verification (as of `bdfc93a`):**
- Full bench suite: 1250/1250 passing, ~20 min wall-clock
- Adjacent regression check (immune_agents, divergence_directive, runner_status_transitions): 183/183
- Ruff clean on all new files; Mypy clean on `bench/openrouter_tools.py` with `--explicit-package-bases`

### `reference_runner.py`

**UNTOUCHED** per founder directive. Exp 39 runner frozen until v2 is tested and founder approves promotion.

---

## What remains for subsequent sessions

**Stage 2 remainders:** none. All six Stage 2 items are committed as of Phase A + Phase B.

**Stage 3 remainders (after Phase A + Phase B):**
- 1E.3 Specialist cell live-promotion flip (audit landed; one-line edit held back pending broader K/L/M tool coverage)
- 1E.10 Runtime call-site assertion (depends on `eta_int_modulator` wiring in Exp 54; base module landed in Phase A)

**Spawned background task:**
- `_verify_sympy` silent regression — sandboxed subprocess uses `global_dict={'__builtins__': {}}` which prevents SymPy from constructing `Integer` literals during parsing. Every SymPy specialist verdict currently returns UNCERTAIN (including trivial identities). Separate background task delegated to fix without reopening the MF-40 RCE vector.

**Stage 4 for Exp 41–53:**
- Target selection and config generation per experiment, sequentially after each prior experiment's lessons fold in

**Stage 6 for Exp 54:**
- Integration runner config with 2×2 factorial
- `eta_int_modulator` wired into `compute_rk`
- Integration target selection
- Final schema coherence verification

---

## Pragmatic note

The original-session directive was "implement the plan in full now". After three autonomous continuations (two commits and one continuation-without-commit stretch), substantially the full Stage 1 + Stage 2 + Stage 3 scope is live:

- γ-alt convergence path → can terminate cleanly without wall-clock cap
- Macrophage fallback → shadow cell produces useful observations
- DeepSeek parser fixes → findings not lost to format drift
- Consolidation phase + prior fix summary + windowed context → prompts stay informed as the experiment progresses
- Diversity metric → compliance-theatre detection available AND wired into per-round `round_data.cross_model_diversity`
- Quality-gated fingerprint update → DeepSeek bootstrap trap broken
- Fingerprint attention metrics → `D_decay` quality gate receives real data
- Per-model ρ tracking → ITC decisions can be targeted
- Cross-round recidivism detection → demotes near-identical alternatives even when they hop rounds
- OpenRouter function-calling → four non-CC2 panel models can now invoke sympy/z3/pytest/ruff/mypy
- DeepSeek formal-verification specialist → logical/mathematical fallback with 0.5 confidence cap

The two residual open items (1E.3 live-promotion flip, 1E.10 runtime call-site assertion) are intentionally gated — the first on K/L/M coverage maturity, the second on Exp 54 wiring. Neither blocks Exp 40's declared scope.
