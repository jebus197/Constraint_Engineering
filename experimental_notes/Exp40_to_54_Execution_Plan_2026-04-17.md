# Execution Plan — Experiments 40 through 54

**Date:** 17 April 2026
**Source document:** [Exp40_Readiness_and_Novelty_Review_2026-04-17.md](Exp40_Readiness_and_Novelty_Review_2026-04-17.md) (canonical review; this plan derives its ordering and acceptance criteria from that review)
**Branch:** `exp39-experimental`
**HEAD at plan creation:** `cc6cc1a`

---

## Purpose

This is the operative implementation checklist for building the sequence Experiments 40 through 54. It derives its content from the readiness review of 17 April but adds ordering, acceptance criteria, file-level targets, and gate checkpoints.

Each item is independently addressable. A compliant implementation ticks items in order, runs the specified acceptance check, and folds any lessons into the plan as the work proceeds. The plan is the operative artefact during runner construction; the readiness review is its rationale layer.

---

## Standing constraints (apply to every experiment)

- **S1.** The Experiment 39 runner at `bench/reference_runner.py` must NOT be overwritten. The new runner is constructed as `bench/reference_runner_v2.py`, with `bench/launch_exp40.py` as its entry point. Promotion to `reference_runner.py` is a subsequent founder decision after Exp 40 has run and been studied.
- **S2.** The Ouroboros principle governs. Each experiment's runner is the previous experiment's runner plus its own post-experiment lessons. The runner evolves in-place; it does not fork.
- **S3.** CDSFL directives are live. §17 feedback channel and §18 round-two divergence directive are default-on in every experiment. `eta_int_modulator` remains library-exposed but NOT wired into `compute_rk` for Experiment 40 — this is the design-deferred state, preserved for baseline measurement.
- **S4.** Specialist cells for mathematics, statistics, biology, and information science are promoted from shadow to live before Experiment 40 runs. The single-line flip at `reference_runner.py:~3741` moves from shadow to live in `reference_runner_v2.py`.
- **S5.** Shadow cells for physics, chemistry, and engineering are built functional in shadow mode, not placeholder. Promotion to live is gated on empirical data from experiments 41 through 53.
- **S6.** The 2×2 factorial for §17/§18 attribution is deferred to Experiment 54 (integration). Cells A (reuse Exp 36–38 baseline), B (§17 on, §18 off), C (§17 off, §18 on), D (both on) run in Exp 54 on a chosen integration target. Coverage sweep runs 40–53 as single-cell D.
- **S7.** No preferred scientific outcome. Each experiment is run to produce empirical data. Interpretation follows the data; claims are not pre-declared.
- **S8.** Commit at natural milestones. The plan defines these as: plan artefact landing; shadow-log audit complete; each bug fix landed with tests; specialist cells live-promoted; shadow cells functional; per-experiment runner frozen; experiment results landed.

---

## Part 1 — Runner fixes (to fold into `reference_runner_v2.py` before Exp 40)

### 1A. Priority-zero bugs from 39-0 post-mortem

Three items. All blockers for any fix-verification or convergence claim.

#### Item 1A.1 — S_k format mismatch
- **Source:** TTS §Layer 1 bug 1; `Exp39_0_Gate_PostMortem_2026-04-14.md` P0 #1
- **Symptom:** 0% S_k ADMISSIBLE rate across all six rounds of 39-0
- **Root cause:** prompt advertises format A (`====` separator, `>>>> REPLACE` closer); parser at `reference_runner.py:2094` in `parse_search_replace_blocks()` reconstructs format B; evaluator checks format C
- **Fix site:** `parse_search_replace_blocks()` in `reference_runner_v2.py` around line 2094; align parser, prompt, and evaluator on a single canonical format
- **Acceptance:** smoke test produces S_k ADMISSIBLE > 0 on a hand-crafted finding-with-fix input. Unit test covers A/B/C format variants and confirms parser returns the canonical form
- **Status:** TODO

#### Item 1A.2 — Parser emitting source code as finding IDs
- **Source:** TTS §Layer 1 bug 2; post-mortem P0 #2
- **Symptom:** `CC2_full_id,` and `DeepSeek_f"{model_id}_UNSTRUCTURED"` leaked as finding IDs; two phantom canonical entries (C0023, C0038) in 39-0
- **Root cause:** fallback path in `parse_findings()` in `runner_core.py` treats Python variable names and unevaluated f-string templates as valid IDs
- **Fix site:** `parse_findings()` regex / fallback path in `runner_core.py`; add reject-patterns for Python identifier patterns and f-string templates
- **Acceptance:** unit test feeds adversarial strings (variable names, f-strings, JSON fragments) and confirms parser rejects them rather than treating them as finding IDs
- **Status:** TODO

#### Item 1A.3 — Convergence gate structurally unreachable
- **Source:** TTS §Layer 1 bug 3; post-mortem P0 #3
- **Symptom:** `max_open_crit_high` defaults to 0; with 41 canonical entries and 6 closures, the gate cannot trigger. Documented alternative (γ ≥ 0.30 OR three consecutive rounds with zero novel CRITICAL) was prose only, not code
- **Fix sites:** two-part fix. Default threshold bumped to 3–5 in runner config; gamma-based alternative path implemented in `bench/dm/_convergence.py` and wired into the round-loop convergence check
- **Acceptance:** unit test confirms gate triggers when γ ≥ 0.30 AND three consecutive rounds with zero novel CRITICAL, independent of `max_open_crit_high`. Integration test confirms runner terminates cleanly on synthetic convergent data
- **Status:** TODO

### 1B. Priority-one bugs

#### Item 1B.1 — Macrophage blind (verdict wiring broken)
- **Source:** TTS §Layer 1 bug 4; post-mortem P1 #4; shadow log `macrophage_shadow_r00.json` through `r05.json` all report zero observations
- **Root cause:** `immune_result.cell_verdicts` attribute does not exist, or extracted objects lack `.verdict` / `.confidence`; three monitoring capabilities (provenance, gate_stats, ouroboros_metrics) are implemented but unwired
- **Fix:** audit `immune_result` structure; align Macrophage's verdict consumers with the actual attribute names; add diagnostic log when the verdict list is empty (so this failure mode is loud, not silent, in future)
- **Acceptance:** on a synthetic immune_result containing two B-Cell verdicts and one NK verdict, Macrophage produces non-zero observations. Three monitoring capabilities emit measurable output
- **Status:** TODO

#### Item 1B.2 — DeepSeek decomposition trap
- **Source:** TTS §Layer 1 bug 5; post-mortem P1 #5
- **Symptom:** DeepSeek decomposed in 6 of 6 rounds of 39-0; 67% of chunks returned zero characters; parser captured only 55% of actual findings; self-confirmation loop on monolithic payload
- **Root causes:** fingerprint bootstrapping trap (chunk successes don't prevent future decomposition), parser format incompatibility on chunked output, no feedback to model that findings were registered, reasoning token capture incomplete
- **Fix (multi-part):** (a) fingerprint override so chunk-successful payload sizes update `max_successful_prompt_chars` persistently; (b) parser accepts DeepSeek's bold-heading format (see Item 1B.3); (c) feedback injection confirms prior-round findings registered; (d) reasoning token capture corrected
- **Acceptance:** on replay of 39-0's DeepSeek outputs, decomposition rate drops below 50% and parser yield rises above 80%
- **Status:** TODO

#### Item 1B.3 — DeepSeek parser for markdown bold headers
- **Source:** TTS §Layer 1 bug 6; post-mortem P1 #6
- **Symptom:** DeepSeek uses `**Finding:**` format; parser doesn't handle it; R5 captured 1 of 6 findings (parser catastrophe); 9 novel findings lost across the experiment
- **Fix site:** extend `parse_findings()` to accept markdown bold headers as a valid finding-marker format
- **Acceptance:** parser test suite includes DeepSeek's actual R5 output sample and extracts all 6 findings
- **Status:** TODO

### 1C. Priority-two bugs

#### Item 1C.1 — Autoimmune false alarm in late rounds
- **Source:** TTS §Layer 1 bug 7; post-mortem P2 #7
- **Symptom:** RT v2 flags 100% removal rate as AUTOIMMUNE every round from R1; all removals are legitimate duplicates (rejected=0, duplicated=N)
- **Fix:** split flag into `AUTOIMMUNE_REJECTION` (ill-founded removal) and `DEPLETION_EXPECTED` (legitimate late-round duplication)
- **Acceptance:** on synthetic late-round data with 100% duplicate rejection and 0% content rejection, `DEPLETION_EXPECTED` fires; `AUTOIMMUNE_REJECTION` does not
- **Status:** TODO

#### Item 1C.2 — ITC degradation false trigger
- **Source:** TTS §Layer 1 bug 8; post-mortem P2 #8
- **Symptom:** Codex and CC2 hit five consecutive DEGRADATION flags in 39-0; caused by verdict-heavy output deflating `parse_yield`
- **Fix:** count verdicts as valid output in the `parse_yield` calculation
- **Acceptance:** on synthetic verdict-heavy output, `parse_yield` reflects verdicts correctly and DEGRADATION does not fire
- **Status:** TODO

### 1D. Lessons-forward items (6 still open from Exp 37→38→39 audit)

#### Item 1D.1 — Prior fix summary context
- **Source:** TTS §Layer 2 item 6; confound analysis §2 lesson 6
- **Implementation:** port `_build_prior_fix_summary()` from Exp 37 (`run_exp37_evidence.py`) into `reference_runner_v2.py` as a first-class method; call on each round K, inject into round K+1 prompt as a context block
- **Acceptance:** unit test confirms that on a synthetic round-1 with three applied fixes, round-2's prompt contains a "prior fixes this experiment:" block naming the three fix IDs
- **Status:** TODO

#### Item 1D.2 — Consolidation phase (final three rounds)
- **Source:** TTS §Layer 2 item 7; Exp 36 Ground Truth HIGH priority
- **Implementation:** add a consolidation mode to the round-loop; triggered for the last three rounds of any run; consolidation prompt template emphasises closing open challenges over surfacing new findings
- **Acceptance:** on a synthetic 8-round run, rounds 6, 7, 8 operate in consolidation mode; consolidation round produces zero or few novel findings and non-zero challenge-closures
- **Status:** TODO

#### Item 1D.3 — Per-model ρ tracking with targeted ITC
- **Source:** TTS §Layer 2 item 8
- **Implementation:** extend `itc_model_state` to track per-model ρ (novel-to-raw finding ratio) history; ITC degradation decisions use per-model ρ thresholds rather than only per-model `parse_yield`
- **Acceptance:** unit test with two synthetic models of different ρ decay rates confirms ITC targets each correctly
- **Status:** TODO

#### Item 1D.4 — Context windowing for long runs
- **Source:** TTS §Layer 2 item 9
- **Implementation:** for runs exceeding six rounds, dispatch prompts include a summarised context window (latest two rounds full, older rounds summarised); aligns with the ChatGPT overflow fix documented in `PRIVATE_NOTES.md`
- **Acceptance:** on a synthetic 10-round run, round-10 dispatch payload remains below the 80K LENGTH_THRESHOLD without losing correct round-8/9 content
- **Status:** TODO

#### Item 1D.5 — S_k format pre-check with reformat request
- **Source:** TTS §Layer 2 item 10; partially addressed by §17 admissibility parser
- **Implementation:** before submitting a fix to the S_k evaluator, validate format; if malformed, issue a reformat request to the emitting model with specific guidance on the canonical format
- **Acceptance:** on a synthetic malformed fix, runner issues reformat request; on the reformatted response, S_k evaluation proceeds
- **Status:** TODO

#### Item 1D.6 — Parser fixes P2/P3 (CC2 leak FIXED; Gemini verdict extraction pending)
- **Source:** TTS §Layer 2 item 11; Exp 38 findings
- **Implementation:** CC2 leak was fixed previously; Gemini verdict extraction still pending — extend `parse_findings()` to recognise Gemini's verdict-only round format
- **Acceptance:** parser test suite includes a Gemini verdict-only output sample and extracts the verdicts correctly
- **Status:** PARTIAL (CC2 done; Gemini pending)

### 1E. Schema wiring (§17, §18, specialist cells, shadow cells, fingerprints)

#### Item 1E.1 — Feedback channel directive live in the runner
- **Source:** TTS §Layer 3 item 1
- **State:** live-default since 15 April; 39 tests pass; never exercised in a running experiment
- **Implementation:** confirm `reference_runner_v2.py` wires `build_feedback_records()` output into round K+1 dispatch as a prompt-prefix section
- **Acceptance:** on a two-round synthetic run, round-2 dispatch contains the feedback section derived from round-1 findings
- **Status:** VERIFY (already wired in reference_runner.py; confirm carries over to v2)

#### Item 1E.2 — Divergence directive (round-two) live in the runner
- **Source:** TTS §Layer 3 items 2, 3
- **State:** live-default; 75 tests pass; never exercised live. `eta_int_modulator` exposed but NOT wired into `compute_rk` (deferred by design)
- **Implementation:** confirm §18 prompt directive is appended to every model prompt; confirm `build_divergence_record()` is called on every finding; confirm `eta_int_modulator` is NOT called from `compute_rk` (preserve design deferral for Exp 40 baseline)
- **Acceptance:** on synthetic findings, §18 directive text appears in the prompt; divergence records are built for each finding; R_k values are unaffected by the modulator function
- **Status:** VERIFY / CONFIGURE

#### Item 1E.3 — B-Cell specialist dispatch live-promotion
- **Source:** TTS §Layer 3 item 5; standing constraint S4
- **State:** 14 active verifiers via TOML manifest; shadow mode at `reference_runner.py:~3741`
- **Implementation:** flip specialist dispatch from shadow to live for mathematics, statistics, biology, information science in `reference_runner_v2.py`. Keep physics, chemistry, engineering in shadow (per S5)
- **Acceptance:** on synthetic math-domain claim, B-Cell specialist SymPy verifier produces a verdict that enters the immune pipeline; on synthetic physics claim, the specialist remains shadow-mode (logs verdict but does not affect pipeline)
- **Status:** TODO

#### Item 1E.4 — Specialist cells K, L, M built functional in shadow
- **Source:** standing constraint S5; Exp 39 sub-experiments 39-K/L/M
- **Implementation:** `bench/cdsfl_registry/domains/` has physics/chemistry/engineering configs; each specialist cell implementation must be built out to functional shadow (not placeholder). K uses `pint` and `astropy.units` for dimensional analysis; L uses `rdkit` for stoichiometry and molecular validity; M uses safety-factor calculations appropriate to structural engineering
- **Acceptance:** on a synthetic dimensional claim, physics specialist logs a shadow verdict; on a synthetic molecular claim, chemistry specialist logs a shadow verdict; on a synthetic safety-factor claim, engineering specialist logs a shadow verdict. None of these verdicts affect the pipeline
- **Status:** TODO

#### Item 1E.5 — Fingerprint attention metrics wired
- **Source:** TTS Other Factors §Measured-vs-advertised; confound analysis §3
- **State:** infrastructure exists (`decay_analysis.py` fits Duane curves, `burst_planner.py` has `D_decay` trigger); fingerprint JSON fields all null
- **Implementation:** at end of each round, compute per-model `measured_attention_span`, `compression_threshold`, `quality_at_capacity`, `decomposition_recommended`, `attention_ratio`, `D_decay` from the available ITC and parse-yield history; write to the fingerprint JSON
- **Acceptance:** after a two-round synthetic run, every non-null fingerprint field is populated with a numeric value; `burst_planner.py` successfully reads `D_decay` and makes a decomposition decision based on it
- **Status:** TODO

#### Item 1E.6 — Dynamic decomposition based on payload size
- **Source:** confound analysis §4 C3; TTS Other Factors
- **Symptom:** in 39-0, `pre_decompose_models` was a static list; CC2, ChatGPT, Gemini received 369K monolithic payload because they weren't on the list, despite payload being 4.6× threshold
- **Implementation:** replace the static list with a dynamic check: if dispatch payload exceeds `LENGTH_THRESHOLD` (80K) for any model, decompose that model's payload
- **Acceptance:** on a synthetic 400K payload to a panel of five models, all five decompose; on a synthetic 40K payload, none decompose
- **Status:** TODO

#### Item 1E.7 — Cross-model diversity metric (logging only)
- **Source:** TTS Other Factors §Compliance theatre
- **Implementation:** compute per-round mean pairwise Jaccard across all alternatives across all five models; log to the round JSON as `cross_model_diversity`
- **Acceptance:** on a synthetic round with five identical alternatives, metric reports 1.0; on a synthetic round with five disjoint alternatives, metric reports close to 0
- **Status:** TODO

#### Item 1E.8 — Ouroboros cell query-quality fix
- **Source:** TTS §Layer 3 item 7; shadow log `ouroboros_shadow_r00.json` confirms queries use internal finding IDs
- **Symptom:** queries issued to arxiv were literal strings like "uncertain finding Gemini_F002"; arxiv package not installed, all results status "shadow_mock"
- **Implementation:** Ouroboros cell query construction uses finding description text, not finding ID. Install `arxiv` package. Add source rotation (Semantic Scholar, Unpaywall, CORE, OpenAlex) once their adapters land
- **Acceptance:** on a synthetic finding with description "Bayesian recursive self-assessment for LLM output", Ouroboros issues a query using that text, not the ID. `pip show arxiv` returns installed
- **Status:** TODO

#### Item 1E.9 — Recidivism detection (cross-round)
- **Source:** TTS §Residual debt; Divergence_Round2_Implementation_2026-04-16.md
- **State:** §18 currently checks isomorphism within a single round only
- **Implementation:** carry divergence records forward from round K to round K+1 in `reference_runner_v2.py`; `check_sibling_admissibility()` extended to check against prior-round alternatives, not only current-round siblings
- **Acceptance:** on a synthetic two-round run where round-2 resubmits a round-1 alternative unchanged, the round-2 finding is flagged as recidivism and incurs the 0.60 severe tier
- **Status:** TODO

#### Item 1E.10 — Channel-assignment boundary verification at call site
- **Source:** TTS §Residual debt
- **State:** invariant proven locally and symbolically (41/41 SymPy/z3), not observed at the integration call site
- **Implementation:** add assertion in `compute_rk` that confirms `m_div` is passed only as an `eta_int` multiplier, never as an R_k pre-factor; invariant fail raises explicit channel-violation error
- **Acceptance:** assertion passes on every call in a synthetic run; if the invariant is violated (manually in a test), the call raises `ChannelViolationError`
- **Status:** TODO

#### Item 1E.11 — OpenRouter tool-use mode
- **Source:** TTS §Layer 3 item 8
- **State:** CC2 has Bash; other four panel models need OpenRouter function-calling
- **Implementation:** extend `call_openrouter()` with a `tools` parameter; wire SymPy, z3, pytest, ruff, mypy as callable tools; test per-model tool invocation
- **Acceptance:** on a synthetic mathematical claim, Codex/Gemini/ChatGPT/DeepSeek each successfully invoke SymPy via function-calling and receive structured results
- **Status:** TODO

#### Item 1E.12 — DeepSeek specialist role (Phase 6)
- **Source:** TTS §Layer 3 item 9
- **Implementation:** design and wire DeepSeek as a specialist role (not generic panel member) alongside the other specialists; specifically, DeepSeek's long-reasoning strengths fit formal-verification style claims. Fingerprint override (Item 1B.2) is prerequisite
- **Acceptance:** on synthetic formal-verification claim, DeepSeek produces a specialist verdict that enters the immune pipeline distinct from its generic panel role
- **Status:** TODO

---

## Part 2 — Shadow-log audit (FFAFP on Exp 39 shadow outputs)

Apply FFAFP (Find, Follow, Analyse, Fix, P-pass) to each Exp 39 shadow log. If the cell generated meaningful data, fold the behaviour into `reference_runner_v2.py`. If it didn't, find root cause, fix, test.

### Item 2.1 — Ouroboros shadow audit
- **Logs:** `bench/logs/exp39_0_gate_20260413T193320Z/ouroboros_shadow_r00.json` through `r05.json`
- **Known symptom (from R0):** queries used internal finding IDs as search terms; arxiv package returned "shadow_mock" status with zero results for all queries
- **FFAFP:** Find (query-quality failure), Follow (all downstream claims are phantoms built from placeholder descriptions), Analyse (root causes are query construction + missing arxiv package + no source rotation), Fix (per Item 1E.8), P-pass (does the fix survive adversarial abstract claims? does it survive bad API responses?)
- **Acceptance:** after fix, Ouroboros on the same six rounds of 39-0 data produces queries that are semantically relevant to findings (no literal "uncertain finding Gemini_F002" strings) and returns at least one meaningful match on at least one finding
- **Status:** TODO

### Item 2.2 — Macrophage shadow audit
- **Logs:** `bench/logs/exp39_0_gate_20260413T193320Z/macrophage_shadow_r00.json` through `r05.json`
- **Known symptom (from R0):** mode "patrol", anomaly_count 0, pipeline_modified false, observations empty (confirmed across all six rounds)
- **FFAFP:** Find (wiring failure per Item 1B.1), Follow (Macrophage's three monitoring capabilities never fired), Analyse (root cause is `immune_result.cell_verdicts` attribute missing or malformed), Fix (per Item 1B.1), P-pass (does the fix survive edge cases — empty verdicts, single-verdict rounds, verdicts with missing `.confidence`?)
- **Acceptance:** after fix, Macrophage on the same six rounds of 39-0 data produces non-zero observations and at least one anomaly detection if any anomaly is present
- **Status:** TODO

### Item 2.3 — Stage 6 calibrator shadow audit
- **Logs:** `bench/logs/exp39_0_gate_20260413T193320Z/stage6_calibration_r*.json` and `stage6_calibration_summary.json` (if present)
- **Expected data:** per-finding (ν_k_proxy, c_ext, H_ratio) triples; per-tool fail fraction; shadow η deltas
- **FFAFP:** Find (calibrator depended on Ouroboros data via `_last_shadow_log`; if Ouroboros query-quality was broken, calibrator inputs were garbage), Follow (ν_k_proxy and c_ext will be derived from invalid Ouroboros output), Analyse (if calibrator wrote any files, check they contain sensible ranges), Fix (tied to Item 1E.8), P-pass (does the fix produce ν_k_proxy values that span a reasonable range rather than collapsing to a single value?)
- **Acceptance:** after fix, calibrator produces (ν_k_proxy, c_ext, H_ratio) triples with at least two distinct values across the six rounds of 39-0 replay
- **Status:** TODO

---

## Part 3 — Test article decomposition (14 targets)

Each of the 14 sub-experiments maps to one experiment (40 through 53) and targets a natural discrete element, sized to fit through the dispatch pipeline without triggering pre_decompose.

### Mapping

| Exp | Maps from | Name | Domain | Target proposal | Size check |
|---|---|---|---|---|---|
| 40 | 39-0 | Infrastructure Gate | software | `bench/dm/_feedback.py` (§17 module, 533 LOC, ~20K) | ✓ |
| 41 | 39-A | Mathematics Specialist | mathematics | `bench/dm/_convergence.py` or `bench/dm/_suppression.py` (bounded math module) | to measure |
| 42 | 39-B | Expert Encodings S_k | software | `bench/cdsfl_registry/composer.py` (expert encoding composer) | to measure |
| 43 | 39-C | Macrophage Admissibility | software | `bench/immune_agents.py` macrophage subsection (extracted natural unit) | to measure |
| 44 | 39-D | Composition Test | software | synthetic composition of 41+42+43 outputs (mechanical interface check) | N/A |
| 45 | 39-E | Statistics Specialist | statistics | `bench/dm/_memory.py` (beta-binomial memory, CUSUM drift) | to measure |
| 46 | 39-F | CS/Software Specialist | software | `bench/dm/_divergence.py` (§18 module, 443 LOC, ~20K) | ✓ |
| 47 | 39-G | Biology Specialist | biology | a right-sized biology-analogous module (candidate TBC) | to determine |
| 48 | 39-H | Information Science | info_science | `bench/evidence.py` (641 LOC, 23K — already right-sized) | ✓ |
| 49 | 39-I | Cross-domain Synthesis | software | synthetic integration of 41+45+46 outputs | N/A |
| 50 | 39-J | Microglia | software | `bench/dm/_shadow_stage6.py` (self-referential calibration module) | to measure |
| 51 | 39-K | Physics Shadow | physics | a right-sized physics claim module | to determine |
| 52 | 39-L | Chemistry Shadow | chemistry | a right-sized chemistry claim module | to determine |
| 53 | 39-M | Engineering Shadow | engineering | a right-sized engineering claim module | to determine |

**[Correction 2026-08-05.]** The Exp 41 row above proposes `bench/dm/_suppression.py` as an alternative to `bench/dm/_convergence.py`. **`bench/dm/_suppression.py` was never created**, and it is not a moved or deleted file: no path of that name exists at any commit in this repository's history (`git log --all --name-only --format="" | grep -i suppress` returns nothing), so there is no live path to redirect to. Exp 41 ran against `bench/dm/_convergence.py` — the three Exp 41 configs (`bench/exp41_configs/41_convergence.json`, `41b_first_principles.json`, `41c_first_principles_run.json`) name that module and no suppression module. Suppression logic lives inside existing files (`bench/dm/_convergence.py`, `bench/dm/_immune.py`), never in one of its own. The row is left intact: on 2026-04-17 it recorded an open target proposal, not a claim that the file existed.

### Selection criteria
- Target file under 80,000 characters (LENGTH_THRESHOLD). If the natural unit is larger, select a bounded sub-module
- Target exercises the cells and directives the sub-experiment is designed to test
- Target has enough internal complexity to produce non-trivial findings (avoid trivial modules that generate fewer than ~10 findings across a run)

### Item 3.1 — Finalise target selection
- **Acceptance:** each of the 14 targets is named, its size measured in characters, and its expected finding yield estimated from prior-experiment density (rough heuristic: ~1 finding per 500 characters in prior runs)
- **Status:** PARTIAL (Exp 40, 46, 48 proposed; others require target-selection session)

### Item 3.2 — Regenerate sub-experiment configs
- **Implementation:** for each experiment 40 through 53, write an `exp{N}_config.json` under `bench/exp40_configs/` through `bench/exp53_configs/` (one directory per experiment for cleanliness) with the updated target, round cap, wall-clock cap, convergence criteria, and any experiment-specific directive toggles
- **Acceptance:** all 14 configs lint-clean against `cdsfl_registry/schema.toml`; smoke test loads each config successfully
- **Status:** TODO

---

## Part 4 — Experiment sequence

### Exp 40 build and run

#### Item 4.0.1 — Build `reference_runner_v2.py`
- **Implementation:** copy `reference_runner.py` to `reference_runner_v2.py`; fold in all of Part 1 (items 1A, 1B, 1C, 1D, 1E); do NOT modify `reference_runner.py`
- **Acceptance:** `python3 -m pytest bench/tests/ -v` reports the prior green count plus new tests passing; `ruff check` and `mypy` clean on the new file
- **Status:** TODO

#### Item 4.0.2 — Build `bench/launch_exp40.py`
- **Implementation:** entry script that loads `bench/exp40_configs/40_gate.json`, wires `reference_runner_v2.py`, dispatches the five-model panel
- **Acceptance:** `--dry-run` produces a valid execution plan; `--preflight` confirms connectivity to all five models
- **Status:** TODO

#### Item 4.0.3 — Run Exp 40
- **Target:** `bench/dm/_feedback.py` (the §17 module — fitting choice for a live-directive infrastructure gate)
- **Panel:** CC2, Codex, Gemini, ChatGPT, DeepSeek under full CDSFL + FFAFP directives
- **Acceptance:** Exp 40 terminates on a convergence signal (not wall-clock), produces a non-confounded report, and yields measurable data on §17 and §18 under live conditions
- **Status:** TODO (requires Items 1A through 3.2 complete)

#### Item 4.0.4 — Exp 40 post-mortem
- **Implementation:** per-model finding counts, γ trajectory, R_k adoption rate, §17 admissibility rate, §18 compliance rate, cross-model diversity metric, specialist cell verdict counts, shadow cell observations, any bugs surfaced
- **Acceptance:** post-mortem document lands in `experimental_notes/Exp40_PostMortem_{DATE}.md`; plan's Part 1 is updated with any new bugs found, reclassified as 1A/1B/1C; TTS mirror lands on Desktop
- **Status:** TODO

### Exp 41 through Exp 53 — repeat the pattern

Each experiment follows the same shape:

1. Fold lessons from prior experiment into the runner (the runner evolves; `reference_runner_v2.py` is updated in place; do NOT fork into `_v3.py` etc.)
2. Build `bench/launch_exp{N}.py` with the target from the Part 3 mapping
3. Run
4. Post-mortem in `experimental_notes/Exp{N}_PostMortem_{DATE}.md`
5. TTS mirror on Desktop
6. Commit at milestones; update this plan's status fields

#### Item 4.{N}.1 through 4.{N}.4 for N in 41..53
- **Status:** PENDING (see per-experiment detail in post-Exp-40 plan updates)

### Exp 54 — integration run

#### Item 4.54.1 — Build integration runner
- **Implementation:** the same `reference_runner_v2.py` after Exp 53's lessons; 2×2 factorial configured (cells A reused from Exp 36–38 archives, B = §17 on §18 off, C = §17 off §18 on, D = both on)
- **Acceptance:** 2×2 factorial config lints clean; `eta_int_modulator` is now wired into `compute_rk` for cells C and D (the deferred wiring lands here, after the 40–53 sweep has produced empirical tier-calibration data)
- **Status:** PENDING

#### Item 4.54.2 — Integration target selection
- **Implementation:** chosen based on 40–53 outcomes; likely a module that integrates cross-cell behaviour cleanly (candidate: `bench/reference_runner_v2.py` itself, testing the runner against itself as a meta-test)
- **Status:** PENDING

#### Item 4.54.3 — Run Exp 54
- **Acceptance:** all four 2×2 cells complete; attribution statistics computed (§17 main effect, §18 main effect, interaction); schema coherence verified across the integrated run
- **Status:** PENDING

#### Item 4.54.4 — Exp 54 post-mortem and final integration report
- **Implementation:** `experimental_notes/Exp54_Integration_Final_{DATE}.md` with 2×2 attribution statistics, coherence findings, any residual debt; TTS mirror
- **Acceptance:** report stands as the empirical complement to the round-two mathematical convergence; final schema-stability assessment produced
- **Status:** PENDING

---

## Part 5 — Gate criteria between experiments

Before launching Exp N+1, the following must be true.

### Gate A — runner clean
- All unit tests pass
- `ruff` and `mypy` clean
- Post-mortem of Exp N is written and in `experimental_notes/`
- All new bugs from Exp N are classified into the plan's Part 1 (1A/1B/1C) and either fixed or explicitly deferred with reason

### Gate B — lessons folded
- Every P0 and P1 bug from Exp N is folded into `reference_runner_v2.py` before Exp N+1 launches
- P2 bugs may be deferred one experiment if they do not affect the next experiment's target domain
- Schema wiring items (1E) have no outstanding TODOs that block Exp N+1's target

### Gate C — target ready
- Exp N+1's target article is confirmed under 80,000 characters
- Exp N+1's config is lint-clean against `cdsfl_registry/schema.toml`
- Smoke test of Exp N+1's launch script `--dry-run` and `--preflight` pass

### Gate D — founder sign-off
- Exp N post-mortem reviewed
- Any scope change for Exp N+1 explicitly approved (e.g. if target needs reselection)
- Fail-fast behaviour of the dependency DAG verified (if Exp N failed in a way that would invalidate downstream experiments, those downstream experiments must be reassessed)

---

## Plan maintenance

This plan is a living document. As experiments run and lessons accrue:

- **Status fields update** (TODO → IN PROGRESS → DONE → VERIFIED)
- **New items append** under the appropriate Part when discovered
- **Deferred items** are marked DEFERRED with reason and target experiment
- **Archived items** are moved to a "Done" section at the end after VERIFIED

The plan is committed at every gate checkpoint, alongside the runner state. The TTS review of 17 April remains the rationale source; any plan addition that extends beyond the review's scope should get its own TTS note before being added here.

---

## Appendix — canonical file layout

| Artefact | Path |
|---|---|
| Experiment 39 runner (frozen, do not modify) | `bench/reference_runner.py` |
| Experiment 40+ runner (evolves in place) | `bench/reference_runner_v2.py` |
| Experiment 40 launcher | `bench/launch_exp40.py` |
| Experiment N launcher (N ≥ 40) | `bench/launch_exp{N}.py` |
| Experiment N config | `bench/exp{N}_configs/*.json` |
| Experiment N logs | `bench/logs/exp{N}_*/` |
| Experiment N post-mortem (repo) | `experimental_notes/Exp{N}_PostMortem_{DATE}.md` |
| Experiment N post-mortem (TTS) | `~/Desktop/CDSFL_tts/Exp{N}_PostMortem_{DATE}.txt` |
| This plan | `experimental_notes/Exp40_to_54_Execution_Plan_2026-04-17.md` |
| Readiness review (rationale source) | `experimental_notes/Exp40_Readiness_and_Novelty_Review_2026-04-17.md` |
