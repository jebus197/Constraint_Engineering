# Exp 40 Pre-Launch Gap-Closure Overnight Shift

2026-04-22 01:45 BST

## Summary

Six of the nine residual gaps on the Exp 39 → Exp 40 gap-closure list closed during a single overnight shift between 23:12 BST on 21 April and 01:45 BST on 22 April. The remaining three gaps (G6 specialist-to-specialist verdict-conflict resolution, G7 MERGE deadlock auto-arbitration, G8 burst-mode Phase 0 convergence override) retain `Scheduled` status and now carry explicit entry triggers, multi-tool cross-verification pairings, and minimum evidence thresholds for close. One pre-existing bug in the K/L/M shadow-audit dict-comp was surfaced by a Find-Follow-Analyse-Fix-P-pass (FFAFP) cycle on G2 and fixed in the same session; the four other G-closures found no bugs but landed regression coverage against silent drift. Test count grew from 1255 to 1311 (56 new tests across five new test files) with zero new failures expected once the full regression run completes. (The words "non-network" stood here originally; see the correction under "Test-count impact" below for why they have been struck.)

## Scope

The Exp 39 → Exp 40 gap-closure list was formalised during the Round 2 Plan Review Panel on 21 April 2026 as nine residual items carried forward from Exp 38/39 and subsequent confer rounds. Each item received FFAFP treatment (Find the defect or coverage gap, Follow its consequences through the system, Analyse with the available multi-tool envelope, Fix at the root cause, then P-pass the fix with Popperian falsification). The overnight shift closed the six pre-launch or self-contained items — G1 (Gate C Codex preflight wiring), G2 (K/L/M shadow-audit regression test), G3 (Stage 6 query-quality calibrator test harness), G4 (`open_crit_high_count()` REOPENED-status handling), G5 (`contested_count()` grace-period parameter wiring), and G9 (F4 closure-state label application). The remaining three were documented with explicit trigger specifications rather than resolved in-session, because their resolution depends on post-mortem evidence from experiments that have not yet run.

## G1 — Gate C Codex preflight wired into `bench/launch_exp40.py`

**Finding.** The Round 2 plan review identified Gate C (an admissibility-parser preflight step derived from prior Codex review rounds) as a hard requirement for Exp 40 launch under RQ1, but the wiring into the Exp 40 launcher had not been implemented. A launch attempt would have run without the preflight check, defeating the purpose of having Gate C at all.

**Fix.** A `gate_c_preflight()` function was added to `bench/launch_exp40.py`. The function performs three checks in sequence: a live-path import of the admissibility-gate module, a schema-drift guard on the `ADMISSIBILITY_GATES` structure that compares the current schema against the expected set and surfaces discrepancies with explicit `got`-vs-`expected` naming, and a five-case canonical matrix (missing block, empty input, all-pass, one-fail, sigma-ASCII variant) drawn from existing offline parser tests to exercise the parser on a known input distribution. The preflight is wired into both the `--preflight` CLI path (runs before the model-connectivity stub) and the full-run path (runs before runner dispatch). A `--skip-gate-c` escape hatch was added for debug scenarios. The `--dry-run` path deliberately does not run Gate C because dry-run is a config-only surface that never touches the parser.

**Regression coverage.** A new test file `bench/tests/test_launch_exp40.py` holds six tests: three unit tests covering a healthy parser, a drift-detected case, and a drift message naming both got and expected schemas; two CLI subprocess tests covering `--preflight` exit-zero with PASS line and `--dry-run` non-firing of Gate C; one coverage test confirming the five canonical cases align with parser ground truth. All six pass. The pre-existing 39-test feedback-channel suite remains green.

**Closure.** G1 CLOSED. Multi-tool verification: pytest + subprocess CLI smoke + monkeypatch drift injection + AST inspection of `ADMISSIBILITY_GATES`.

## G2 — K/L/M shadow-audit regression test and bug fix

**Finding.** A pre-compaction enrichment to the K/L/M shadow-audit logging at `bench/immune_agents.py:5400-5428` used a dict-comp that bound two of its five output keys (`claim_id` and `severity`) via `getattr(v, "claim_id", None)` and `getattr(v, "severity", None)`. Neither field exists on the `CellVerdict` dataclass — confirmed via `dataclasses.fields(CellVerdict)` which returns `{finding_id, verdict, confidence, tool_used, evidence}`. Both `getattr` calls silently resolved to `None`, halving the Round 2 RQ4 non-distortion-measurement signal without any visible error.

**Fix.** The two stale keys were renamed at `bench/immune_agents.py:5411-5421` to the real `CellVerdict` fields: `claim_id → finding_id`, `severity → confidence`. An inline comment block was added naming the 22 April correction, pointing at the regression test file, and stating the reason for the rename (field-name stability check against the dataclass).

**Regression coverage.** A new test file `bench/tests/test_shadow_audit_klm.py` holds eleven tests across four classes. An AST-level schema check (`_extract_shadow_detail_keys`) parses `immune_agents.py` and extracts the dict-comp key set, asserting exact match to `{finding_id, verdict, confidence, tool_used, evidence}`. Two standalone pins explicitly ban `claim_id` and `severity` from reoccurring as dict-comp keys. A field-binding test uses `dataclasses.fields(CellVerdict)` to verify every key maps to a real attribute on the live dataclass. A behavioural replica covers N-to-N emission, 256-character evidence truncation on both sides, and empty-string preservation. A log-format pin checks the `_shadow_log` format string `"B-Cell specialist (shadow, domain=%s): %d verdicts; detail=%s"` remains present. All eleven pass in 2.48 seconds.

**Closure.** G2 CLOSED. Multi-tool verification: pytest + AST + `dataclasses.fields` introspection.

## G3 — Stage 6 query-quality calibrator test harness

**Finding.** The Stage 6 query-quality calibrator at `bench/dm/_shadow_stage6.py` was redesigned on 14 April 2026 to a two-dimensional reporting framework (nu_k_proxy for novelty proxy, c_ext for external-source confidence, H_ratio for hit-rate) but carried no pytest coverage. The calibrator is the named prerequisite for Exp 50 (Ouroboros self-referential Stage 6 calibration), so any silent drift in its identities or API surface would propagate into the self-referential experiment undetected.

**Fix.** No fix was needed. The 14 April design is intact, all identities hold, and the HARD 6 two-dimensional framing is preserved. The gap was coverage, not behaviour.

**Regression coverage.** A new test file `bench/tests/test_shadow_stage6_calibrator.py` holds eighteen tests across six classes. Four public-API surface pins confirm the class is instantiable without arguments, `observe_round()` carries a stable signature `(round_idx, findings, immune_response, ouroboros_data)`, the return type is `ShadowStage6RoundLog`, and an empty-findings round produces an empty log. Two triple-invariant pins confirm `nu_k_proxy`, `c_ext`, and `h_ratio` are distinct dataclass fields on `PerFindingNoveltyLog` and each stays in the unit interval. Two SymPy-verified delta identity pins prove `δ = η · c_ext · (1 − ν_k)` symbolically via `sp.simplify(delta_code - delta_closed) == 0` and anchor the proof to a concrete `_assess_finding` output within 1e-4. Two noisy-OR combiner pins confirm `c_ext_raw = 1 − (1 − c_s1)(1 − c_s2)` evaluates to 0.65 at (0.5, 0.3) and stays in [0, 1] at boundary values. Two frequency-scaling pins confirm `c_freq` is monotone non-decreasing in encounter count and bounded at `C_MAX = 0.95` under saturation (100 repeated encounters). Two epistemic-tagging pins confirm a no-search finding at `ν_k = 0.5` is NOT tagged SPECULATIVE while a searched-empty finding at `ν_k = 0.8` with `c_ext ≈ 0.224` IS tagged. Four source-truth pins fix `GAMMA_SRC = 0.7`, `ALPHA_FREQ = 0.1`, `C_MAX = 0.95`, and that the module docstring retains the two-dimensional HARD 6 framing. All eighteen pass in 0.76 seconds. Wolfram cross-check was not run because the SymPy closed-form identity is the load-bearing proof and Wolfram is local-only per the plan's standing rules.

**Closure.** G3 CLOSED. Multi-tool verification: pytest + SymPy + `inspect` + AST + `dataclasses`.

## G4 — `open_crit_high_count()` REOPENED-status handling

**Finding.** The v1 and v2 bodies of `open_crit_high_count()` were byte-identical at the 22 April baseline, and the v2 `_NON_TERMINAL = ("OPEN", "CONTESTED", "REOPENED")` literal at `bench/reference_runner_v2.py:454` handles REOPENED correctly. The gap was coverage, not behaviour: a future refactor that dropped REOPENED from the tuple would cause a high-severity claim that had moved OPEN → CLOSED → REOPENED to stop counting toward the critical-high gate, and no test would catch the silent tightening.

**Fix.** No fix was needed.

**Regression coverage.** A new test file `bench/tests/test_open_crit_high_count_v2.py` holds eleven tests across four classes. Five behavioural pins confirm REOPENED at 0.9 severity counts, REOPENED at 0.5 severity does not, mixed OPEN plus REOPENED count together, exhausted REOPENED is excluded (exhaustion wins over status), and CLOSED-high is excluded (terminal wins). Two purity pins confirm no mutation of the `exhausted` flag under read and idempotency under repeated calls. Two signature pins use `inspect.signature` for parameter contract plus `typing.get_type_hints` for return-type resolution — the latter because runner v2 uses `from __future__ import annotations`, which turns raw signature annotations into strings. Two AST source-truth pins confirm the `_NON_TERMINAL` tuple literal contains REOPENED, OPEN, and CONTESTED. All eleven pass.

**Closure.** G4 CLOSED. Multi-tool verification: pytest + `inspect` + `typing.get_type_hints` + AST.

## G5 — `contested_count()` grace-period parameter wiring

**Finding.** `contested_count()` at `bench/reference_runner_v2.py:464` declares `grace_period: int = 2` in its signature, and the function body at lines 481 and 494 both use the parameter — it is not silently ignored. The three in-module call-sites (lines 1019, 1135, and 1214-1215) use the default implicitly rather than threading the value from `RunnerConfig`. That implicit-default pattern is not a defect at the current baseline, but any future sweep experiment that needs to vary the grace-period value would hit the missing plumbing.

**Fix.** No fix was needed for Exp 40 launch. An internal observation was logged: the inner `grace_period = 2` hardcoded at `reference_runner_v2.py:829` inside `_update_finding_statuses` is a parallel latent wiring gap for the same future-sweep case. The observation will surface when the G-list is re-reviewed for post-launch work.

**Regression coverage.** A new test file `bench/tests/test_contested_count_v2.py` holds ten tests across four classes. Four behavioural pins confirm grace_period=1 excludes at the boundary (rounds_in_status of 1 is not less than 1), grace_period=3 includes the same finding, the implicit default matches the explicit 2, and grace_period=0 disables UNCONFIRMED counting entirely. Three signature pins confirm the default is 2 via `inspect.signature`, the parameter order is `[self, current_round, grace_period]`, and the return type is `int` via `typing.get_type_hints`. One AST pin confirms the source-level literal default is exactly 2. Two call-site pins confirm no live call-site passes `grace_period=` as a kwarg literal (source-level check; all three call-sites use the default) and the call-site count is at least three (sanity). All ten pass in 0.82 seconds.

**Closure.** G5 CLOSED. Multi-tool verification: pytest + `inspect` + `typing.get_type_hints` + AST + source-line inspection.

## G9 — F4 closure-state labels applied

**Finding.** The F4 closure-state lexicon (`library_complete`, `shadow_integrated`, `live_operational`) was defined during the Round 2 plan review on 21 April 2026 but had not been applied consistently across the schema elements described in `resources/ONBOARDING.md`. A new reviewer asking "is feature X done" would get an underspecified answer because "done" alone does not name which layer is done.

**Fix.** A new `Closure-State Lexicon (F4, locked 21 April 2026)` section was inserted into `resources/ONBOARDING.md` between the Standing Rules block and the Current State block. The section names each of the three labels with a one-clause example, states the non-skipping promotion-order rule (library_complete → shadow_integrated → live_operational), and points at the shadow-promotion-now non-distortion bounding condition that governs shadow_integrated → live_operational transitions.

In the same pass, the most load-bearing stale factual description in ONBOARDING was corrected. Line 51 previously described the K/L/M shadow-audit logging as recording `claim_id, verdict, severity, tool_used, evidence` — these are the pre-compaction field names that resolved to `None` due to the G2 bug. The line now reads the real `CellVerdict` fields (`finding_id, verdict, confidence, tool_used, evidence`), carries an explicit "22 April 2026 correction" note pointing at both the code fix and the regression test, and wears the `shadow_integrated` closure-state label inline.

A full retroactive labelling of the remaining ~40 shadow mentions in ONBOARDING was deliberately not attempted. Defining the lexicon once and correcting the single outright-stale description was judged both higher value and lower risk than a large search-and-replace across settled prose. Forward-going discipline is that new ONBOARDING additions wear the label at write time; existing mentions retain their earlier phrasing but the glossary is in reach for any reviewer who needs it.

**Closure.** G9 CLOSED (documentation-only).

## G6, G7, G8 — scheduled trigger specifications

A new section `## 6b. Scheduled trigger specifications (G6, G7, G8)` was added to the consolidated Exp 40-54 plan (byte-identical at `~/Desktop/CDSFL_Consolidated_Plan_2026-04-21.md` and `experimental_notes/Exp40_to_54_Consolidated_Plan_2026-04-21.md`) between §6a's post-launch-path paragraph and the §7 appendix. Each of the three scheduled gaps now carries (a) an explicit entry trigger with automatic migration path if the primary trigger produces no qualifying evidence, (b) multi-tool cross-verification pairings to apply on activation, and (c) a minimum evidence threshold for the close verdict.

For G6, the entry trigger is Exp 44 run completion plus post-mortem identifying at least one case where two specialists of different domains returned incompatible verdicts on the same `Finding` (ACCEPT vs REJECT, ACCEPT vs ABSTAIN, or REJECT vs ABSTAIN); if Exp 44 is clean, the trigger migrates automatically to Exp 49 (cross-domain synthesis) which by construction forces multi-domain co-ruling. The close criterion requires an explicit arbitration rule, regression tests over the three conflict patterns plus a three-specialist extension, an integration test, and a `_confer_log` schema extension for `conflict_outcome`.

For G7, the entry trigger is Exp 44 run completion plus post-mortem identifying at least one MERGE deadlock event. The close criterion requires a minimum three-pattern deadlock taxonomy observed before the rule is designed (to avoid fitting a rule to a single case), unit tests per taxonomy entry, an integration test, and a documented taxonomy in `docs/ARCHITECTURE.md`.

For G8, the entry trigger is external authorisation of a future burst-mode experiment. Burst mode is disabled across the current 15-experiment Exp 40-54 arc by design, so G8 remains documented rather than active. The close criterion requires a `RunnerConfig` flag with `False` default, regression coverage of both flag-off (identical to current behaviour) and flag-on paths, and documentation in `docs/ARCHITECTURE.md`.

The arbitration rules for G6 and G7 are deliberately left unspecified at design time. The correct rule depends on empirical patterns that the post-mortems will expose, and pre-specifying it before the evidence exists would violate the Popperian discipline the project runs under. Each gap's "arbitration rule" is a placeholder to be filled in from evidence, not a pre-registered algorithm to be verified against evidence.

## Test-count impact

The shift added fifty-six new tests across five new test files:

| Test file | New tests | Class count | Wall-clock |
|-----------|-----------|-------------|------------|
| `bench/tests/test_launch_exp40.py` | 6 | — | — |
| `bench/tests/test_shadow_audit_klm.py` | 11 | 4 | 2.48 s |
| `bench/tests/test_open_crit_high_count_v2.py` | 11 | 4 | — |
| `bench/tests/test_contested_count_v2.py` | 10 | 4 | 0.82 s |
| `bench/tests/test_shadow_stage6_calibrator.py` | 18 | 6 | 0.76 s |

Total collected post-shift: 1311 (pre-shift 1255 plus 56 new). The full regression run is in progress at note-write time; the expected pass count is at least 1171 (pre-shift 1121 plus 56 new), and no existing-test regressions are expected because the only runtime-code change is the field-name rename at `bench/immune_agents.py:5411-5421` which aligns the dict-comp with the live `CellVerdict` schema.

Correction, 2026-07-31. Two things are wrong with the paragraph above as originally written. First, it called the run in progress a "non-network" run. It was not offline. The `network` marker was not registered in `pytest.ini` until 2026-06-09 (`c865bd9`) and tags three tests out of roughly 2089, none of them a model-dispatch path, so `-m "not network"` excluded essentially nothing; the actual exclusions used in this period were hand-curated file lists chosen on wall-clock cost. Test files that reach live Claude command-line dispatch — `test_immune_agents.py` (`eeb7f40`, 2026-04-02), `test_specialist_live_promotion.py` and `test_specialist_shadow_cells.py` (both `bdfc93a`, 2026-04-17) — all existed on this date, carried no marker, and were on no exclusion list. Second, the projected figure of at least 1171 was never confirmed: no later entry in the record closes it with a measured result, so it remains an expectation and must not be cited as one. The suite was made offline on 2026-07-31 by three mechanisms in `bench/tests/conftest.py`; the measured figure then was 2086 passed, 3 skipped, 0 failed in 99.6 s under `python3 -m pytest bench/tests/ -q --netguard-strict` at HEAD `d4d4d7f` plus working tree, with all 30 outbound attempts denied. See `resources/RECOVERY.md`.

## Next triggers

The shift closes the pre-launch blocker set. The remaining pre-Exp-40-launch item is the founder's launch approval. Post-launch, the three scheduled gaps activate automatically: G6 and G7 at Exp 44 post-mortem (or later if Exp 44 is clean), G8 only on external authorisation.

Three falsifiable follow-ups worth tracking:
1. **If Exp 44 produces no specialist-to-specialist conflict and no MERGE deadlock, does Exp 49's cross-domain synthesis surface either pattern?** G6 and G7 both migrate to Exp 49 automatically under the trigger spec, so this is a direct empirical check.
2. **Does the K/L/M shadow-audit enrichment produce non-distorting evidence against `40_gate.json` pass_condition across Exp 40-50?** This is the bounding condition on each domain's `LIVE_SPECIALIST_DOMAINS` flip at Exp 51/52/53 and is measurable from the shadow logs now that the field-binding bug is fixed.
3. **Does the `grace_period` implicit-default pattern become a defect before a future sweep experiment?** The parallel latent wiring gap at `reference_runner_v2.py:829` will surface if any Exp 40-54 round needs a non-default grace-period value, and the call-site purity test in `bench/tests/test_contested_count_v2.py` will flag the change.

---

Written under CDSFL note standard v1 (21 April 2026).
