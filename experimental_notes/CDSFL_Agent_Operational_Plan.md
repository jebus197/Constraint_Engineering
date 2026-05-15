# CDSFL Agent Operational Plan

**Audience.** AI agent self-consumption. Terse, actionable, and dynamically updated. Not a human-facing narrative. If a reader is looking for prose explanation, see the detail plan under "Canonical anchors" below.

**Function.** Authoritative operational tracker for the Exp 40–54 arc and the subsequent Bench Run 2 (27 frontier STEM problem sets). First resource to read after any compaction or long break.

**Last updated.** 15 May 2026 22:30 BST. Post-continuation 12-item fix tranche executed under full MC discipline (cc2 cx ge cgpt ds sq f sy p t). 9 engineering items complete; architectural confer completed via mandated local-P-pass fallback (Codex CLI unstable in env); Exp 40 R17–R21 resume + live confer surfaced as founder decisions (cost/supervision gates). 229 regression tests pass across the tranche + 8 pre-continuation fixes + adjacent suites. New module `bench/merge_arbitration.py` (G7, default-disabled). 6 new test files. Paired fix-tranche post-mortem written: technical `experimental_notes/Exp40_Fix_Tranche_Postmortem_2026-05-15.md`, plain-English `..._Plain_English_2026-05-15.md`, TTS `~/Desktop/CDSFL_tts/Exp40_Fix_Tranche_Postmortem_2026-05-15.txt`. HEAD `3bbf2c7` (working tree regression-clean, sv pending founder direction).

**Prior update.** 15 May 2026 05:30 BST. Experiment 40 continuation run completed (ran 03:15:48 → 05:20:26 BST, 7,478 seconds, exit code 0). Wall-clock cap fired at Round 17 boundary. Seven rounds completed in this leg (R10–R16); 17 rounds total across both legs of Exp 40. γ-decay reached 0.034 (deep converged regime); γ-alt boolean not met. Seventeen BUGZILLA verified CLOSED transitions. Six D4 MERGE DEADLOCK escalations to HIL — G7 evidence cluster now in hand. Paired post-mortem written: technical at `experimental_notes/Exp40_Continuation_Postmortem_2026-05-15.md`, plain-English at `experimental_notes/Exp40_Continuation_Postmortem_Plain_English_2026-05-15.md`, TTS at `~/Desktop/CDSFL_tts/Exp40_Continuation_Postmortem_2026-05-15.txt`. HEAD prior to post-mortem write: `3bbf2c7`. Working tree carries the run's untracked log files + the three new post-mortem documents.

---

## Recovery-first card

After compaction or a long break, read in this order:
1. **This file, end to end.**
2. `git log --oneline -10 && git status` in `Constraint_Engineering/`.
3. `python3 -m open_brain.cli session-context --agent cc`.
4. The "Active work queue" section below — top item is the resume point.
5. The "Completed in current window" log — most recent entry identifies what just landed.

Do **not** re-read the consolidated plan before this file; the consolidated plan is for detail, this file is for state.

---

## Canonical anchors

| Resource | Path |
|---|---|
| This file (self-consumption tracker) | `~/Desktop/CDSFL_Agent_Operational_Plan.md` |
| Repo mirror of this file | `Constraint_Engineering/experimental_notes/CDSFL_Agent_Operational_Plan.md` |
| Detail plan (prose, for human + mixed audience) | `~/Desktop/CDSFL_Consolidated_Plan_2026-04-21.md` and `Constraint_Engineering/experimental_notes/Exp40_to_54_Consolidated_Plan_2026-04-21.md` (byte-identical) |
| Note standard (locked 21 April 2026) | `~/.claude/projects/-Users-georgejackson-Developer-Projects/memory/cdsfl_note_standard_v1.md` |
| Global CLAUDE.md (user-level directives) | `~/.claude/CLAUDE.md` |
| Project CLAUDE.md | `Constraint_Engineering/.claude/CLAUDE.md` |
| MEMORY.md index | `~/.claude/projects/-Users-georgejackson-Developer-Projects/memory/MEMORY.md` |
| Project state file | `~/.claude/projects/-Users-georgejackson-Developer-Projects/memory/ce_state.md` |
| RECOVERY.md (repo-level recovery protocol) | `Constraint_Engineering/resources/RECOVERY.md` |
| ONBOARDING.md (repo-level project context) | `Constraint_Engineering/resources/ONBOARDING.md` |
| Mathematical appendix | `Constraint_Engineering/docs/MATHEMATICAL_APPENDIX.md` |
| Architecture doc | `Constraint_Engineering/docs/ARCHITECTURE.md` |
| Glossary | `Constraint_Engineering/docs/GLOSSARY.md` |
| Canonical 4-phase execution plan (Phase C = BR2) | `Constraint_Engineering/experimental_notes/Exp36_Ground_Truth_Reference_2026-04-08.md` Section XI |
| Runner v2 (active Exp 40–54) | `Constraint_Engineering/bench/reference_runner_v2.py` (4922 lines) |
| Runner v1 (frozen Exp 38/39 baseline) | `Constraint_Engineering/bench/reference_runner.py` |

---

## Current state snapshot (update at each commit)

- **Branch.** `exp39-experimental`
- **HEAD at debrief entry.** `991cde0` — *sv: overnight gap-closure G1+G2+G3+G4+G5+G9 closed + G6/G7/G8 trigger specs* (pushed to origin 22 April 2026 02:14 BST). Follow-up `42b737f` — *docs: operational plan mark E4 + E5 done post-991cde0 sv*. Documentary-state sv on top of that is in progress.
- **Working tree at debrief entry.** Clean. This sv stages ONBOARDING + RECOVERY + ce_state + operational plan + `memory/feedback_fix_all_scope_split.md` (new) + `memory/MEMORY.md` index update. No runtime code changes.
- **Test count.** 1311 collected. 56 new tests from overnight shift pass in 2.33 s. Fast non-network sweep (excluding five long-running or CLI-blocking files) 907/907 pass in 342.12 s. No regression-relevant changes in this documentary sv.
- **Current experiment.** Exp 40, pre-launch CLOSED on runtime code. Founder oversight Q&A surfaced 3 pending non-code decisions (focused confer round scope, G6/G7/G8 path, residuals disposition). Five of nine G-items closed fully (G1/G2/G3/G4/G5); three specification-only (G6/G7/G8); one partial (G9). Four residuals outside the G-list identified (Exp 39-0 gate contradiction, R_k time-series, scientific-notation amendment to locked note standard, full F4 retroactive sweep). Gate C preflight wiring complete and regression-pinned.

---

## Standing rules (non-negotiable, every turn)

1. **sq — strictly sequential tool use.** One tool call per message. No parallel batches. Sub-agents inherit.
2. **Multi-tool cross-verification.** Every computational claim verified with at least two relevant tools where available. Pairings:
   - Math: **SymPy + Wolfram** (Wolfram via MCP, local-only, not part of CDSFL infrastructure).
   - Stats: **scipy.stats + statsmodels**.
   - Symbolic / constraint logic: **SymPy + z3**.
   - Dimensional analysis: **pint + astropy.units**.
   - Chemistry structure: **rdkit + regex-based parser cross-check** (no second equivalent tool installed).
   - Biology sequence: **biopython + (regex for sequence-validity subset)** (no second equivalent tool installed).
   - Optimisation: **PuLP + scipy.optimize**.
   - Behavioural code: **crosshair + pytest**.
   - Numerical precision: **NumPy + mpmath** (for precision cross-check).
   - Code structure: **AST + inspect + dis** (stdlib).
3. **1E.10 catch (standing).** "1E.10" in the CDSFL plan is **Plan Item 1.E.10**, NOT scientific notation `1e10`. A 21 April 2026 misreading propagated "ten billion" language through multiple notes. Treat every "1E.n" token as an item reference unless proven otherwise.
4. **Scientific notation in plain-English notes.** When a genuine large number appears, use `1×10^N (number-words)` format, e.g. `1×10^10 (ten billion)`. Verify exponent–word correspondence before writing (10^7 = ten million, 10^10 = ten billion).
5. **Note standard v1.** Every TTS and experimental-notes markdown ends with the foot-line `Written under CDSFL note standard v1 (21 April 2026).` 10 rules summarised in project CLAUDE.md; full text in `cdsfl_note_standard_v1.md`.
6. **FFAFP for any untested claim.** Find → Follow → Analyse (with available tools) → Fix → P-pass. Applies to every proposed fold-in of an Exp 39 / confer-round outstanding item.
7. **Multi-tool is for computational claims specifically.** Rhetorical or stylistic choices do not get tool-verified; aesthetic fitness review, prose precision review, or design review applies (per user CLAUDE.md `rigour-universal`).

---

## Per-experiment target-article matrix (nailed down)

Status legend: FIXED (specific, stable, ready) | PROVISIONAL (specified, scope TBC) | UNDECIDED (no target yet).

| Exp | Target article / module | File location | Status | Notes |
|---|---|---|---|---|
| 40 | §17 feedback directive (base for Gate A, first live exercise) | `bench/dm/_feedback.py` | FIXED | Pre-launch F1–F4 closed. Gate C preflight wiring pending. Founder launch approval pending. |
| 41 | Bounded mathematics module | `bench/dm/_convergence.py` (or `_suppression.py`; size confirmed post-Exp-40) | FIXED (conditional size) | Mathematics calibration target. |
| 42 | Expert encodings S_k | `bench/cdsfl_registry/composer.py` | FIXED | S_k admissibility across vendor encodings. |
| 43 | Macrophage admissibility (bounded ~20K char unit) | `bench/immune_agents.py` macrophage section | FIXED | Verdict-wiring confirmation under live load. |
| 44 | Composition test (no new target) | Synthetic, combines Exp 41 + 42 + 43 outputs | FIXED | Mechanical interface check. |
| 45 | Statistics specialist | `bench/dm/_memory.py` (beta-binomial memory + CUSUM) | FIXED (conditional size) | `statsmodels + scipy + uncertainty_propagation` per `domains/immune/statistics.toml`. |
| 46 | §18 divergence directive | `bench/dm/_divergence.py` | FIXED | §18 live since Exp 39; module is also the test article (self-referential). |
| 47 | Synthesised native biology module | To be drafted; ~15–25K chars | FIXED target-strategy (panel 21 April) | **Scope brief below.** Biology specialist routes: `sympy + biological_sequence + dimensional_analysis`; `z3` for logical; `statsmodels + scipy + uncertainty_propagation` for statistical. Per `domains/immune/biology.toml`. |
| 48 | Information-science specialist | `bench/evidence.py` (641 LOC, ~23K chars) | FIXED | Information-science B-Cell specialist. |
| 49 | Cross-domain synthesis (no new target) | Synthetic, combines Exp 41 + 45 + 46 outputs | FIXED | Mathematics + statistics + CS integration. Post-mortem watch-item: three alternative orderings (Gemini §18-first, ChatGPT swap 46/48, DeepSeek stats adjacent 41) if tier inconsistencies surface. |
| 50 | Microglia / Stage 6 calibrator (self-referential) | `bench/dm/_shadow_stage6.py` | FIXED | Ouroboros query-quality fix prerequisite — cross-verified at entry gate. |
| 51 | Synthesised native physics module (K, shadow) | To be drafted; ~15–25K chars | FIXED target-strategy (panel 21 April) | **Scope brief below.** DeepSeek composer.py candidate withdrawn (lacks dimensional density). Physics B-Cell (K, shadow) routes: `sympy + dimensional_analysis + astronomical`. Per `domains/immune/physics.toml`. |
| 52 | Synthesised native chemistry module (L, shadow) | To be drafted; ~15–25K chars | FIXED target-strategy (panel 21 April) | **Scope brief below.** Chemistry B-Cell (L, shadow) routes: `chemistry_structure` (RDKit) + `dimensional_analysis`. Per `domains/immune/chemistry.toml`. |
| 53 | Synthesised native engineering module (M, shadow) | To be drafted; ~15–25K chars | FIXED target-strategy (panel 21 April) | **Scope brief below.** Engineering B-Cell (M, shadow) routes: `sympy + uncertainty_propagation + dimensional_analysis`. Per `domains/immune/engineering.toml`. |
| 54 | Integration run with 2×2 factorial | Candidate: `bench/reference_runner_v2.py` self-test (runner-tests-runner meta) | PROVISIONAL | 2×2 factorial design locked. Cells A/B/C/D defined: A = §17 off + §18 off (Exp 36–38 baseline archive); B = §17 on + §18 off; C = §17 off + §18 on; D = both on. Cell A entry-method decision open (RQ3, 3–2 split persists; founder decides at Exp 54 entry). |

### Target-article scope briefs (Exp 47, 51, 52, 53)

Each of the four synthesised native modules must embed **falsifiable** claims that exercise the routed tools. The 15–25K character budget allows 4–6 distinct claim clusters per module.

**Exp 47 — Biology (~15–25K chars, native synthesis).** Claim clusters:
1. **Sequence-validity claims.** DNA/RNA/protein sequences with assertions about validity, GC content, open reading frames, stop-codon positions. Falsifiable via `biopython` `Seq` operations + regex cross-check.
2. **Dimensional claims.** Molar mass, concentration, reaction-rate kinetics with explicit units. Falsifiable via `pint` dimensional analysis.
3. **Statistical-distribution claims.** Allele frequency, Hardy-Weinberg equilibrium, χ² goodness-of-fit. Falsifiable via `scipy.stats` + `statsmodels` cross-check.
4. **Mathematical claims.** Logistic-growth ODE with specific parameters, population-dynamics fixed points. Falsifiable via `sympy` + optional `scipy.integrate` numerical cross-check.
5. **At least one intentionally false claim** so the specialist has something to reject (e.g. a sequence labelled "protein" that contains invalid codons).

**Exp 51 — Physics (~15–25K chars, native synthesis).** Claim clusters:
1. **Kinematics claims.** Projectile motion, orbital period, free-fall timing with specific numerical values. Falsifiable via `sympy` symbolic + `pint` dimensional + `astropy.constants` cross-check.
2. **Conservation laws.** Energy conservation in elastic collisions, momentum in two-body scattering, charge invariance. Falsifiable via `sympy` + numerical bounds via `scipy`.
3. **Dimensional consistency.** Force = mass × acceleration verification, power = work / time, specific relativistic-limit sanity checks. Falsifiable via `pint` + `astropy.units` cross-check.
4. **Special-function claims.** Specific integrals, series expansions of physical quantities. Falsifiable via `sympy` + `mpmath` (arbitrary precision cross-check).
5. **At least one intentionally false claim** (e.g. a kinetic-energy formula missing the ½ factor).

**Exp 52 — Chemistry (~15–25K chars, native synthesis).** Claim clusters:
1. **SMILES validity.** Valid and invalid SMILES strings with assertions about parse success and molecular identity. Falsifiable via `rdkit.Chem.MolFromSmiles` + regex structural cross-check.
2. **Stoichiometry.** Balanced-equation claims with coefficient-sum assertions. Falsifiable via `rdkit` + `collections.Counter` atom-balance cross-check.
3. **Molecular-weight claims.** Specific molecules with stated molecular weights in g/mol. Falsifiable via `rdkit` `Descriptors.MolWt` + `pint` dimensional check.
4. **Functional-group identification.** SMARTS-pattern claims for carbonyl, hydroxyl, amine presence. Falsifiable via `rdkit` substructure matching.
5. **At least one intentionally false claim** (e.g. an unbalanced equation claimed as balanced).

**Exp 53 — Engineering (~15–25K chars, native synthesis).** Claim clusters:
1. **Load-factor calculations.** Beam deflection, column buckling, stress-strain with specific numerical values. Falsifiable via `sympy` + `pint` + `uncertainties` propagation.
2. **Material-tolerance claims.** Stated tolerance ranges for yield strength, fatigue limit, with uncertainty propagation. Falsifiable via `uncertainties` package + `scipy` for confidence bounds.
3. **Safety-factor routing.** Nominal load vs. worst-case load with specific safety-factor values. Falsifiable via manual formula re-derivation (`sympy`) + dimensional check (`pint`).
4. **Dimensional consistency.** Units across mechanical, thermal, electrical domains. Falsifiable via `pint` + `astropy.units` cross-check.
5. **At least one intentionally false claim** (e.g. a safety factor stated as dimensionless but computed with non-cancelling units).

Each module: draft ahead of its experiment's entry, not at entry. Keep as separate Markdown files under `bench/cdsfl_registry/targets/` (directory to be created when first module drafts).

---

## Exp 39 → Exp 40 gap-closure list

Eight gap items carried forward from Exp 38/39 and subsequent confer rounds. Each gets FFAFP and multi-tool verification. Fold-in status and scheduled close marked below. **Closed** = fix applied, tests added, committed.

| # | Gap | Current state | Pre-Exp-40 blocker? | Scheduled close | FFAFP status |
|---|---|---|---|---|---|
| G1 | Gate C Codex preflight wiring into Exp 40 launcher | `gate_c_preflight()` wired into `--preflight` + full-run paths; 6 tests in `test_launch_exp40.py` all green | **Yes** (blocks Exp 40 launch) | Pre-launch (this session) | CLOSED |
| G2 | K/L/M shadow-audit regression test | 11-test file pins schema + field binding + behaviour + log format; bug fix applied (claim_id/severity → finding_id/confidence) | No | Pre-launch (this session) | CLOSED |
| G3 | Ouroboros query-quality calibrator test harness | 18-test harness on Stage 6 calibrator; SymPy-verified delta + noisy-OR identities; monotone frequency scaling; epistemic tagging + API surface pinned | No (Exp 50 blocker) | This session | CLOSED |
| G4 | `open_crit_high_count()` REOPENED status handling | 11-test regression pin on v2; behaviour + purity + signature + AST source-truth; no fix needed (existing body correct) | No (v2 correctness) | This session | CLOSED |
| G5 | `contested_count()` grace_period parameter wiring | 10-test regression pin on v2; behaviour + signature + AST default + call-site purity; parameter is respected, no fix needed | No (v2 correctness) | This session | CLOSED |
| G6 | Specialist-to-specialist verdict-conflict resolution | No mechanism in v2; Exp 49 assumes one | No (Exp 49 blocker) | Exp 44 post-mortem → Exp 49 prep | Scheduled |
| G7 | MERGE deadlock auto-arbitration | D2 escalation only; no auto-merge | No (Exp 44 boundary) | Exp 44 post-mortem | Scheduled |
| G8 | Burst-mode Phase 0 convergence override | Not folded; burst disabled for Exp 40 | No | Future burst experiment | Scheduled |
| G9 | F4 closure-state labels applied across all schema elements | Lexicon section added to ONBOARDING; stale K/L/M description corrected in situ with `shadow_integrated` label; remaining mentions left for forward-going discipline rather than retroactive sweep | No (documentation) | This session (ONBOARDING sweep) | CLOSED |

---

## Active work queue (overnight shift, 22 April)

Top item = resume point after compaction.

### Phase A — Plan and memory infrastructure
- [x] **A1.** Create this file at `~/Desktop/CDSFL_Agent_Operational_Plan.md`.
- [x] **A2.** Mirror this file at `Constraint_Engineering/experimental_notes/CDSFL_Agent_Operational_Plan.md`.
- [x] **A3.** Link from global CLAUDE.md under new `Project Operational Trackers` section (three new directives).
- [x] **A4.** Link from project CLAUDE.md as the first `Key Documentation` item.
- [x] **A5.** Link from MEMORY.md index as first item under `Project State`.
- [x] **A6.** Link from `Constraint_Engineering/resources/RECOVERY.md` as first-read block before the Minimum Recovery numbered list.
- [x] **A7.** Captured as `memory/feedback_1e10_catch.md` and indexed in MEMORY.md.
- [x] **A8.** Captured as `memory/multi_tool_crossverify.md` and indexed in MEMORY.md.

### Phase B — Factual corrections to four broken notes
- [x] **B1.** Rewrote F1–F4 paragraph in Round 2 Plain-English markdown. F1/F2/F3 descriptions now match runtime behaviour; F4 identified as closure-state lexicon, not exception-handling tightening.
- [x] **B2.** Reframed Cell A paragraph in the Round 2 markdown: Exp 36–38 baseline archive; ouroboros standing framing with version-confound retained as the panel's measurement-level label.
- [x] **B3.** Mirrored B1 and B2 in the Round 2 TTS file.
- [x] **B4.** Rewrote F1/F2/F3 bullets in the Section 8 Decision Register markdown. F4 noted as documentation-only, landed earlier in arc. 1E.10 clarified as Plan Item 1.E.10 reference, not numerical magnitude.
- [x] **B5.** (a) Rewrote Decision 2 Cell A paragraph in the register markdown with Exp 36–38 baseline spec + ouroboros reframe. (b) Corrected K/L/M graduation line (was wrongly scoped to decision 2; now correctly bound by Round 2 non-distortion check, K/L/M flip at Exp 51/52/53 respectively).
- [x] **B6.** Mirrored B4 and B5 in the Section 8 Register TTS file.

### Phase C — Consolidated plan augmentation
- [x] **C1.** Appended `2a. Target-article scope briefs (Exp 47, 51, 52, 53)` section to `experimental_notes/Exp40_to_54_Consolidated_Plan_2026-04-21.md`. Inserted between §2 (15-experiment arc table + factorial cells list) and §3 (fold-in consolidation). Each of the four domain subsections lists 4–5 claim clusters with explicit falsifiability route and a terminal intentionally-false-claim requirement; section closes with drafting-cadence + storage-path direction (`bench/cdsfl_registry/targets/exp{47,51,52,53}_{biology,physics,chemistry,engineering}.md`).
- [x] **C2.** Appended `## 6a. Exp 39 → Exp 40 gap-closure list` to the consolidated plan between §6 (Round 2 outcome) and §7 (Appendix A). Section carries G1–G9 table with cross-references to §6 RQ items, §4 shadow-element rows, and §2 per-experiment rows. Table columns: #, Gap, Current state, Pre-Exp-40 blocker?, Scheduled close trigger, FFAFP status, Cross-reference. Section closes with per-gap multi-tool cross-verification pairings, pre-launch path (G1/G2/G4/G5/G9), and post-launch path (G3/G6/G7/G8).
- [x] **C3.** Mirrored `experimental_notes/Exp40_to_54_Consolidated_Plan_2026-04-21.md` → `~/Desktop/CDSFL_Consolidated_Plan_2026-04-21.md`. `diff -q` confirms byte-identity (exit code 0, no differing-bytes output). Both copies now include §2a (target-article scope briefs) and §6a (Exp 39 → Exp 40 gap-closure). Phase C closed.

### Phase D — Gap-closure FFAFP pass
- [x] **D1 (G1).** Wired Gate C preflight into `bench/launch_exp40.py`. Added `gate_c_preflight()` function (live-path import + schema-drift guard on `ADMISSIBILITY_GATES` + 5-case canonical matrix drawn from existing offline tests) + `--skip-gate-c` escape hatch. `--preflight` path now runs Gate C before model-connectivity check; full-run path runs Gate C before runner dispatch; `--dry-run` deliberately skips Gate C (config-only surface). New test file `bench/tests/test_launch_exp40.py` with 6 tests: 3 unit (healthy parser; schema drift detected; drift message names got + expected); 2 CLI subprocess (`--preflight` exit 0 with PASS line; `--dry-run` does not fire Gate C); 1 coverage (canonical cases align with parser truth). All 6 new + 39 existing feedback-channel tests green. **G1 CLOSED.**
- [x] **D2 (G2).** Wrote `bench/tests/test_shadow_audit_klm.py` — 11 tests across 4 classes. FFAFP surfaced a bug: the 21 April enrichment used `claim_id` + `severity` as dict keys bound via `getattr(v, ..., None)`, but neither is a `CellVerdict` field; both always resolved to None, silently losing 2 of 5 audit slots. Fix applied at `bench/immune_agents.py:5411-5421` — renamed keys to the real CellVerdict fields `finding_id` + `confidence`. Regression pins: AST-level schema check enforces exact 5-field set `{finding_id, verdict, confidence, tool_used, evidence}`; two standalone pins explicitly ban `claim_id` and `severity` from reoccurring; field-binding test uses `dataclasses.fields(CellVerdict)` to verify every key maps to a real attribute; behavioural replica covers N→N emission, evidence truncation at 256 chars, empty-string preservation; log-format pin checks the `_shadow_log` format string. All 11 pass. **G2 CLOSED.**
- [x] **D3 (G4).** Wrote `bench/tests/test_open_crit_high_count_v2.py` — 11 tests across 4 classes. FFAFP outcome: **no fix needed** to `bench/reference_runner_v2.py:447` — the existing `_NON_TERMINAL = ("OPEN", "CONTESTED", "REOPENED")` literal already handles REOPENED correctly; the gap was coverage, not behaviour. New pins: (i) five behavioural tests — REOPENED at 0.9 severity counted, at 0.5 severity excluded, mixed OPEN+REOPENED counted together, exhausted REOPENED excluded, CLOSED-high excluded; (ii) two purity tests — no `exhausted` flag mutation, idempotent under repeated call; (iii) two signature pins using `inspect.signature` + `typing.get_type_hints` (the latter because runner v2 uses `from __future__ import annotations` and raw signature returns strings); (iv) two AST source-truth pins — `_NON_TERMINAL` tuple literal contains REOPENED, OPEN, and CONTESTED. Multi-tool: pytest + inspect + typing + ast. 61 pass (D1+D2+D3+existing). **G4 CLOSED.**
- [x] **D4 (G5).** Wrote `bench/tests/test_contested_count_v2.py` — 10 tests across 4 classes. FFAFP outcome: **no fix needed** to `bench/reference_runner_v2.py:464` — the parameter is not silently ignored, the three call-sites simply use the default. Pins landed: (i) four behavioural — grace_period=1 excludes at boundary, grace_period=3 includes, implicit default matches explicit 2, grace_period=0 disables UNCONFIRMED counting; (ii) three signature — default is 2, params `[self, current_round, grace_period]`, return `int` (resolved via `typing.get_type_hints` for deferred annotations); (iii) one AST — the literal default in the source is exactly 2; (iv) two call-site — no call-site passes `grace_period=` as a kwarg literal (source-level check; all three call-sites at lines 1019/1135/1214-1215 use default), call-site count ≥ 3 sanity. Multi-tool: pytest + inspect + typing + ast + source-read. 10 pass in 0.82 s. **G5 CLOSED.**
- [x] **D5 (G3).** Wrote `bench/tests/test_shadow_stage6_calibrator.py` — 18 tests across 6 classes. FFAFP outcome: **no fix needed** to `bench/dm/_shadow_stage6.py` — the 14 April design is intact, two-dimensional reporting preserved, identities hold. Pins: (i) four public-API surface — class instantiable, `observe_round` signature `[self, round_idx, findings, immune_response, ouroboros_data]`, returns `ShadowStage6RoundLog`, empty findings yields empty log; (ii) two triple invariants — `nu_k_proxy`/`c_ext`/`h_ratio` are distinct dataclass fields, each in [0, 1]; (iii) two SymPy-verified delta identities — `sp.simplify(delta_code - delta_closed) == 0` symbolic proof that `δ = η · c_ext · (1 − ν_k)`, plus concrete anchor test comparing `_assess_finding` output to the closed form within 1e-4; (iv) two noisy-OR combiner — SymPy-verified `c_ext_raw = 1 − (1−c_s1)(1−c_s2)` → 0.65 at (0.5, 0.3), unit-interval boundedness at c_s=0 and c_s=1; (v) two frequency-scaling monotonicity — c_freq non-decreasing in encounter count, bounded at C_MAX=0.95 even after 100 repeated encounters; (vi) two epistemic tagging — no-search finding with `nu_k_proxy=0.5 < 0.6` NOT tagged SPECULATIVE, searched-empty finding with `nu_k_proxy=0.8 + c_ext≈0.224` IS tagged SPECULATIVE; (vii) four source-truth pins — GAMMA_SRC=0.7, ALPHA_FREQ=0.1, C_MAX=0.95, module docstring retains HARD 6 two-dimensional framing. Wolfram cross-check skipped (local-only per plan standing rules; SymPy closed-form proof is the HARD identity). Multi-tool: pytest + SymPy + inspect + ast + dataclasses. 18 pass in 0.76 s. **G3 CLOSED.**
- [x] **D6 (G9).** ONBOARDING closure-state label sweep — glossary + targeted-label approach. Added `## Closure-State Lexicon (F4, locked 21 April 2026)` section to `resources/ONBOARDING.md` between Standing Rules and Current State, defining `library_complete` / `shadow_integrated` / `live_operational` with one-clause examples and the shadow-promotion-now non-distortion bounding condition. Corrected the most load-bearing stale description in situ: the K/L/M shadow-audit line on line 51 incorrectly described the pre-compaction bug (`claim_id, severity`) and has been rewritten to the real `CellVerdict` fields `finding_id, confidence` with a "22 April 2026 correction" note pointing to both the fix at `bench/immune_agents.py:5411-5421` and the regression test `bench/tests/test_shadow_audit_klm.py`; line now carries the `shadow_integrated` closure label inline. Remaining ~40 shadow mentions across ONBOARDING not individually labelled — a full text sweep is judged lower value and higher risk than defining the lexicon once + correcting the one stale factual description. Any future reader of ONBOARDING has the definitions in reach; the discipline migrates forward from this point rather than rewriting history. **G9 CLOSED (documentation-only).**
- [x] **D7.** G6, G7, G8 scheduled-close trigger specifications — added new section `## 6b. Scheduled trigger specifications (G6, G7, G8)` to the consolidated plan (repo + Desktop mirror, byte-identical post-edit) immediately after §6a's post-launch path paragraph. Each gap now carries (a) explicit entry trigger with migration path if the primary trigger produces no qualifying evidence, (b) multi-tool pairings to apply on activation, (c) minimum evidence threshold for the close verdict. Table status-column updates: G1/G2/G3/G4/G5/G9 flipped from `Pending` to `CLOSED` in the same pass; G6/G7/G8 remain `Scheduled`. Section closes with a Popperian note that the arbitration rules are deliberately left unspecified — they must emerge from post-mortem evidence rather than being pre-registered.

### Phase E — Commit and continuation
- [x] **E1.** Full pytest regression run post-changes. **Result:** 56 new tests pass in 2.33 s (standalone run of the five new files); fast non-network sweep excluding five long-running or CLI-blocking files (`test_openrouter_tools.py`, `test_deepseek_specialist.py`, `test_dynamic_management.py`, `test_ouroboros_query_quality.py`, `test_exp29_integration.py`) returns 907/907 pass in 342.12 s. Zero regressions. `test_exp29_integration.py::test_three_round_flow` confirmed hanging on Claude CLI Haiku LLM classifier (14.4 s per call, pre-existing, unrelated to overnight edits — `bench/logs/immune_pipeline.log` at 02:05:51 BST shows the overnight `finding_id`/`confidence` rename emitting correctly). Longer non-ignore sweep deferred to daylight window.
- [x] **E2.** Update `ce_state.md` with the overnight shift results. Line 16 updated with final pass counts + pre-existing-hang provenance note.
- [x] **E3.** Update `ONBOARDING.md` and `RECOVERY.md` with the 22 April session block. Both files updated with final pass counts replacing the "TBD at sv" placeholder.
- [x] **E4.** `sv` with descriptive commit message; push to origin. Committed 991cde0 on `exp39-experimental`; 17 files committed via `scripts/cdsfl_sv.py --commit --push`, atomic push to origin succeeded at 02:14 BST.
- [x] **E5.** Final pass on this file — mark all completed items, set next resume point for morning review.

### Phase F — Bench Run 2 (deferred until Exp 40–54 complete)
- [ ] **F1.** Read `experimental_notes/Exp36_Ground_Truth_Reference_2026-04-08.md` Section XI end-to-end.
- [ ] **F2.** Consolidate the 27 frontier STEM problem sets into this file.
- [ ] **F3.** Nail down per-task: domain, claim-cluster, expected tool routing, falsifiability criterion.

---

## Completed in current window (append at each task close)

- **22 April 2026, 00:17 BST.** A1 — created `~/Desktop/CDSFL_Agent_Operational_Plan.md`. First version of the self-consumption operational tracker. Scope: Exp 40–54 + Bench Run 2. Includes recovery-first card, canonical anchors, standing rules, per-experiment target-article matrix with scope briefs for Exp 47/51/52/53, Exp 39 gap-closure list, active work queue, multi-tool cross-verification pairings.
- **22 April 2026, 00:24 BST.** A2 — mirrored the operational plan at `Constraint_Engineering/experimental_notes/CDSFL_Agent_Operational_Plan.md` (byte-identical to the Desktop copy at write time). Canonical copy is the Desktop file; the repo copy exists for version-controlled recoverability and for agents whose first action on recovery is `git status`.
- **22 April 2026, 00:45 BST.** A3 — added three `operational-tracker-*` directives to `~/.claude/CLAUDE.md` under a new `Project Operational Trackers` section immediately after `Recovery Resource Strategy`. Directives name Desktop canonical + repo mirror, update policy, and post-compaction read order.
- **22 April 2026, 00:48 BST.** A4 — linked the operational plan as the first `Key Documentation` item in `Constraint_Engineering/.claude/CLAUDE.md` (project CLAUDE.md).
- **22 April 2026, 00:52 BST.** A5 — linked the operational plan as the first item under `Project State` in `MEMORY.md`, above the current-state entry.
- **22 April 2026, 00:55 BST.** A6 — added a `First read` block to the top of `Constraint_Engineering/resources/RECOVERY.md`'s `Minimum Recovery` section, pointing to the operational plan before the numbered list.
- **22 April 2026, 01:01 BST.** A7 — created `memory/feedback_1e10_catch.md` with the standing rule (1E.n is a hierarchical item reference, not scientific notation) and companion scientific-notation format rule. Indexed in MEMORY.md under Feedback.
- **22 April 2026, 01:08 BST.** A8 — created `memory/multi_tool_crossverify.md` with the full pairing matrix, scope, Wolfram caveat, and FFAFP integration. Indexed in MEMORY.md under Feedback. Phase A closed.
- **22 April 2026, 01:22 BST.** B1 — rewrote the F-paragraph in the Round 2 markdown note (Question 1, "What this means in practice"). F1/F2/F3 now describe actual runtime behaviour; F4 identified as closure-state lexicon landed earlier in arc, documentation-only.
- **22 April 2026, 01:29 BST.** B2 — rewrote Question 3 Cell A paragraph in the Round 2 markdown. Cell A archive is Exp 36–38 baseline (§17 off, §18 off), not Exp 38/39. Ouroboros framing introduced; "version confound" retained as the panel's measurement-level label but positioned as a consequence of the ouroboros evolution, not a standalone concern.
- **22 April 2026, 01:35 BST.** B3 — mirrored B1+B2 in the Round 2 TTS file. TTS format preserved: no markdown symbols, § → "section", `backticks` → plain text.
- **22 April 2026, 01:42 BST.** B4 — rewrote F1/F2/F3 bullet descriptions in the Section 8 Decision Register markdown. F1 = SymPy sandbox allow-list (not SMT sandbox); F2 = compute_rk_with_eta_channel wrapper activation with explicit "Item 1.E.10 is a plan-item reference, not a numerical magnitude" gloss; F3 = debug-time assertion addition (not removal). F4 noted in preamble as documentation-only from earlier in arc.
- **22 April 2026, 01:48 BST.** B5a — rewrote Decision 2 Cell A paragraph in the register markdown: Exp 36–38 baseline archive + ouroboros principle framing.
- **22 April 2026, 01:52 BST.** B5b — corrected adjacent K/L/M graduation line in the same register (pre-launch section): was wrongly scoped to "decision 2 below"; now correctly bound by the Round 2 non-distortion check, with K/L/M flip at Exp 51/52/53.
- **22 April 2026, 02:00 BST.** B6 — mirrored B4 + B5a + B5b in the Section 8 Register TTS file. Phase B closed.
- **22 April 2026, 01:04 BST.** C1 — appended new subsection `## 2a. Target-article scope briefs (Exp 47, 51, 52, 53)` to the consolidated plan, between the §2 experiment table + factorial cells block and §3 fold-in consolidation. Each domain (biology / physics / chemistry / engineering) gets a dedicated sub-subsection naming: the routing specialist and its `domains/immune/*.toml` entry, 4 falsifiable claim clusters with per-cluster tool routing, and a mandatory intentional-false-claim for rejection-test coverage. Section closes with drafting cadence (draft ahead of experiment entry, not at entry) and storage-path direction. Opening paragraph introduces the c_ext / target-module-validity orthogonality argument that the panel used to reject adapters.
- **22 April 2026, 01:06 BST.** C2 — appended `## 6a. Exp 39 → Exp 40 gap-closure list` between §6 (Round 2 outcome) and §7 (Appendix A). Table of G1–G9 with cross-references into §6 RQ items, §4 shadow-element rows, §2 per-experiment rows. Multi-tool cross-verification pairings named per computational gap (G1: AST + pytest; G2: pytest + AST schema check; G3: pytest + SymPy + mpmath; G4: pytest + inspect; G5: pytest + inspect + dis; G6–G8 scheduled; G9 documentation-only). Pre-launch path = G1/G2/G4/G5/G9. Post-launch path = G3/G6/G7/G8.
- **22 April 2026, 01:07 BST.** C3 — mirrored repo consolidated plan to Desktop canonical. `cp` followed by `diff -q` exit code 0, zero differing bytes. Both copies carry §2a + §6a. Phase C closed.
- **22 April 2026, 01:12 BST.** D1 (G1 Gate C wiring) — added `gate_c_preflight()` to `bench/launch_exp40.py`; wired into `--preflight` path (before model-connectivity stub) and full-run path (before runner dispatch). `--dry-run` unchanged (no Gate C; config-only surface). `--skip-gate-c` flag added for debug. Preflight covers: import check; `ADMISSIBILITY_GATES` schema-drift detection; 5-case canonical matrix (missing block, empty input, all-pass, one-fail, sigma-ASCII variant) drawn from offline test truth. New test file `bench/tests/test_launch_exp40.py` (6 tests, all passing). `test_feedback_channel.py` still 39 green. Multi-tool verification: pytest (45 tests); subprocess CLI smoke; monkeypatch-driven drift injection for schema guard. **G1 CLOSED.**
- **22 April 2026, 01:18 BST.** D2 (G2 shadow-audit regression test) — wrote `bench/tests/test_shadow_audit_klm.py` (11 tests, 4 classes, all passing). FFAFP on the 21 April enrichment surfaced a bug: the pre-compaction `shadow_detail` dict-comp bound `claim_id` and `severity` via `getattr(v, ..., None)`, but neither key is a `CellVerdict` dataclass field (confirmed via `dataclasses.fields`) — both silently resolved to None, halving the audit's Round 2 RQ4 non-distortion signal. Fix applied at `bench/immune_agents.py:5411-5421` with explanatory comment block: `claim_id → finding_id`, `severity → confidence`. Regression pins (multi-tool AST + pytest): `_extract_shadow_detail_keys` parses `immune_agents.py` and extracts the dict-comp key set, asserting exact match to `{finding_id, verdict, confidence, tool_used, evidence}`; two standalone pins explicitly ban `claim_id` and `severity` from reoccurring; `test_all_shadow_detail_keys_bind_to_cellverdict_attributes` uses `dataclasses.fields(CellVerdict)` for binding verification; behavioural replica covers N→N emission, 256-char truncation edge cases (both sides), empty-string preservation; log-format pin checks the `_shadow_log` format string `"B-Cell specialist (shadow, domain=%s): %d verdicts; detail=%s"` is present. Run: 11 passed in 2.48 s. **G2 CLOSED.**
- **22 April 2026, 01:22 BST.** D3 (G4 `open_crit_high_count()` REOPENED regression) — wrote `bench/tests/test_open_crit_high_count_v2.py` (11 tests, 4 classes, all passing). FFAFP outcome: **no fix needed** — the existing `_NON_TERMINAL = ("OPEN", "CONTESTED", "REOPENED")` literal at `bench/reference_runner_v2.py:454` already handles REOPENED correctly; v1 and v2 bodies are byte-identical at the 22 April baseline. The gap was coverage, not behaviour. Pins landed: (i) five behavioural — REOPENED at 0.9 severity counted, at 0.5 severity excluded, mixed OPEN+REOPENED counted together, exhausted REOPENED excluded, CLOSED-high excluded; (ii) two purity — no `exhausted` mutation, idempotent; (iii) two signature — `inspect.signature` for parameter contract plus `typing.get_type_hints` for return-type resolution (v2 uses `from __future__ import annotations` so raw signature returns the annotation as a string); (iv) two AST source-truth — `_NON_TERMINAL` literal contains REOPENED + OPEN + CONTESTED. Adjacent regression: 61 tests pass across D1 + D2 + D3 + existing `test_runner_status_transitions.py` + `test_confer_verification.py` in 1.78 s. **G4 CLOSED.**
- **22 April 2026, 01:25 BST.** D4 (G5 `contested_count()` grace_period regression) — wrote `bench/tests/test_contested_count_v2.py` (10 tests, 4 classes, all passing). FFAFP outcome: **no fix needed** to `bench/reference_runner_v2.py:464` — the parameter is respected by the function body (lines 481 + 494 both use it); the three in-module call-sites (1019, 1135, 1214-1215) use the default `grace_period=2` implicitly rather than threading from config. That implicit-default pattern is not itself a defect for Exp 40 launch, but any future sweep experiment will need a `RunnerConfig.grace_period` field; the call-site purity pin will surface the change when it happens. Pins: (i) four behavioural — `grace_period=1` excludes at boundary (rounds_in_status=1 not < 1), `grace_period=3` includes, implicit default equals explicit 2, `grace_period=0` disables UNCONFIRMED counting entirely; (ii) three signature — default 2 via `inspect.signature`, param order `[self, current_round, grace_period]`, return `int` via `typing.get_type_hints`; (iii) one AST — source default literal is exactly 2; (iv) two call-site — no live call-site passes `grace_period=` kwarg literal, call-site count ≥ 3 sanity. Multi-tool: pytest + inspect + typing + ast + source-read. 10 pass in 0.82 s. **G5 CLOSED.** (Separate observation: the inner `grace_period = 2` hardcoded at `reference_runner_v2.py:829` inside `_update_finding_statuses` is a parallel latent wiring gap — logged internally, not a G5 blocker, will surface when G-list is re-reviewed.)
- **22 April 2026, 01:28 BST.** D5 (G3 Stage 6 calibrator test harness) — wrote `bench/tests/test_shadow_stage6_calibrator.py` (18 tests, 6 classes, all passing). FFAFP outcome: **no fix needed** — the 14 April two-dimensional design at `bench/dm/_shadow_stage6.py` is intact, identities hold, HARD 6 preserved. Pins landed: (i) four public-API — class instantiable without args, `observe_round` signature stable, returns `ShadowStage6RoundLog`, empty-findings clean; (ii) two triple invariants — `nu_k_proxy`/`c_ext`/`h_ratio` are distinct dataclass fields on `PerFindingNoveltyLog`, each ∈ [0, 1]; (iii) two SymPy delta identities — symbolic `sp.simplify(delta_code − delta_closed) == 0` proof that `δ = η · c_ext · (1 − ν_k)`, concrete anchor at known finding matching to 1e-4; (iv) two noisy-OR — SymPy value 0.65 at (c_s1=0.5, c_s2=0.3), unit-interval bounds at c_s=0 and c_s=1; (v) two frequency-scaling — c_freq monotone non-decreasing in encounter count N, bounded at C_MAX=0.95 under saturation (100 repeats); (vi) two epistemic tagging — no-search (ν_k=0.5) NOT tagged, searched-empty (ν_k=0.8, c_ext≈0.224) tagged SPECULATIVE; (vii) four source-truth — GAMMA_SRC=0.7, ALPHA_FREQ=0.1, C_MAX=0.95, module docstring retains two-dimensional HARD 6 framing. Wolfram cross-check skipped (local-only per plan standing rules; SymPy closed-form identity is the load-bearing proof). Multi-tool: pytest + sympy + inspect + ast + dataclasses. 18 pass in 0.76 s. **G3 CLOSED.**
- **22 April 2026, 01:33 BST.** D6 (G9 ONBOARDING closure-state label sweep) — added `## Closure-State Lexicon (F4, locked 21 April 2026)` section to `resources/ONBOARDING.md` between the Standing Rules and Current State blocks, naming `library_complete` / `shadow_integrated` / `live_operational` with one-clause examples for each, promotion-order rule, and pointer to the shadow-promotion-now non-distortion bounding condition. In the same pass, corrected the most load-bearing stale factual description on ONBOARDING line 51: the K/L/M shadow-audit entry previously described the pre-compaction bug (`claim_id` + `severity`) as the live schema. It now reads the real `CellVerdict` field set (`finding_id, verdict, confidence, tool_used, evidence`), carries an explicit "22 April 2026 correction" note pointing at `bench/immune_agents.py:5411-5421` for the fix and `bench/tests/test_shadow_audit_klm.py` for the 11-test regression pin, and wears the `shadow_integrated` closure label inline. A full retroactive labelling of the remaining ~40 shadow mentions in ONBOARDING is NOT attempted — the decision (documented in-row and here) is that defining the lexicon once + fixing the one outright-stale description is both higher value and lower risk than a large search-and-replace across settled prose. Forward-going discipline is: new ONBOARDING additions wear the label at write time; existing mentions retain the earlier phrasing but the glossary is in reach. **G9 CLOSED (documentation-only).**
- **22 April 2026, 01:37 BST.** D7 (G6/G7/G8 scheduled-close trigger specifications) — added new `## 6b. Scheduled trigger specifications (G6, G7, G8)` subsection to the consolidated plan (both repo and Desktop mirror, byte-identical post-edit per `diff -q`). Each of the three gaps now carries an entry trigger with automatic migration path (Exp 44 → Exp 49 → Exp 54 for G6/G7; external authorisation for G8), the multi-tool cross-verification pairings that apply on activation (pytest + AST + inspect + trace-log parsing), and the minimum evidence threshold for a close verdict. In the same edit pass, updated the §6a status column for G1/G2/G3/G4/G5/G9 from `Pending` to `CLOSED` via a single `replace_all=true` on the distinctive `| Pending |` cell pattern (safely non-overlapping with the `Pending activation` string on line 18 used by the S3 shadow-element entry). Added a paragraph under §6a acknowledging the overnight-shift closures with explicit test-file references. Popperian framing preserved: the §6b section closes by noting that the arbitration rules for G6 and G7 are deliberately unspecified — they must emerge from post-mortem evidence rather than being pre-registered. Phase D closed. Next: Phase E (regression run → state-file updates → sv → final pass).
- **22 April 2026, 02:08 BST.** E1 (regression run) — two-part pytest evidence captured. Part one: standalone run of the five new test files (`bench/tests/test_launch_exp40.py` + `test_shadow_audit_klm.py` + `test_shadow_stage6_calibrator.py` + `test_open_crit_high_count_v2.py` + `test_contested_count_v2.py`), 56 collected, **56/56 pass in 2.33 s**. Part two: fast non-network regression sweep excluding five long-running or CLI-blocking files (`test_openrouter_tools.py` 36, `test_deepseek_specialist.py` 29, `test_dynamic_management.py` 283, `test_ouroboros_query_quality.py` 11 non-network, `test_exp29_integration.py` 44), 907 collected, **907/907 pass in 342.12 s** (5m 42s), exit code 0, zero failures. The test_exp29_integration.py::test_three_round_flow hang reproduced under a dedicated 120 s run — confirmed hanging on `Claude CLI Haiku` LLM classifier invocations (14.4 s per call, 3 rounds × N findings per round) plus the fact that it sits on the non-network code path despite doing real CLI dispatch. Log evidence at `bench/logs/immune_pipeline.log` 02:05:51 BST shows the overnight `finding_id`/`confidence` rename emitting correctly under the live path: `detail=[{"finding_id": "sf1", "verdict": "CONFIRMED", "confidence": 0.85, "tool_used": "rdkit", ...}]`. The hang is therefore pre-existing (pre-compaction), unrelated to overnight edits, and the overnight fix is demonstrably working in production pipeline traces. A longer non-ignore sweep is deferred to the daylight review window.
- **22 April 2026, 02:10 BST.** E2 (ce_state update) — `memory/ce_state.md` line 16 updated with the final pass counts (56/56 new, 907/907 fast non-network) and the pre-existing-hang provenance note replacing the "TBD at sv" placeholder.
- **22 April 2026, 02:12 BST.** E3 (ONBOARDING + RECOVERY updates) — both files' 22 April 2026 session blocks updated with the final pass counts replacing the "TBD at sv" placeholder. The `bench/logs/immune_pipeline.log` at 02:05:51 BST evidence line is now cross-referenced in both files as proof that the overnight rename is operational under the real pipeline, not only under unit tests.
- **22 April 2026, 02:14 BST.** E4 (sv commit + push) — `python3 scripts/cdsfl_sv.py --commit --push -m "<long descriptive message>"` succeeded. Commit **991cde0** on `exp39-experimental` (previous HEAD `be6d13a`). Seventeen files committed in total: seven modified and ten staged-from-untracked (five new test files + operational plan repo mirror + four new experimental notes). `docs/CURRENT_STATE.md` auto-regenerated by the sv script. Atomic push to `origin/exp39-experimental` succeeded in the same subprocess invocation. Working tree clean post-commit.
- **22 April 2026, 02:18 BST.** E5 (final operational-plan pass) — Current-State-Snapshot HEAD updated `be6d13a → 991cde0`, working-tree-status note updated from "Dirty, 2M + 2U" to "Clean post-commit, 17 files committed", test-count line updated with the 56/56 new + 907/907 fast-sweep figures, shift-level description updated to reflect six-of-nine gap closure. Morning-review resume pointer set: the next action is a waking review of this shift's paired output + founder decision on Exp 40 launch approval; no outstanding automated task remains. Phase E closed.
- **22 April 2026, 02:15–02:30 BST.** Founder oversight Q&A (debrief of overnight shift). Two founder questions: (1) `test_exp29_integration.py` naming + Exp 40 scope — clarified as pre-Exp-40 regression coverage for real-dispatch path, not an arc artefact; (2) completeness + misses + panel-review worth. Honest gap catalogue recorded: 5 of 9 G-items fully closed (G1-G5), 3 of 9 specification-only (G6/G7/G8), 1 of 9 partial (G9). Four residuals identified beyond the G-list: Exp 39-0 gate contradiction not personally verified; per-finding R_k time-series not addressed; scientific-notation sub-rule not amended into locked `cdsfl_note_standard_v1.md`; full retroactive F4 closure-state labelling not performed. Clarification recorded: "integration" has two senses — fold-in-and-test (overnight directive) vs Exp 54 factorial (the arc's integration experiment). Panel-review status mapped: F1/F2/F3 strategy + Gate C step + Stage 6 design + scope/ordering + RQ6b + K/L/M non-distortion + shadow-promotion-now already reviewed; G2 code correctness + §2a scope briefs + §6b trigger specs + G3/G4/G5 coverage + G9 lexicon wording NOT reviewed. Self-assessment clause recorded: "fix all" was interpreted on a spectrum (bounded-fix / specification-only / full-sweep) and the split should have been flagged at write time, not at debrief.
- **23 April 2026, 04:50 BST.** Documentary-state sv prep (post-compaction resume of the 22 April `sv` directive) — new memory file `feedback_fix_all_scope_split.md` created capturing the lesson that autonomous "fix all" windows must decompose the target list into bounded-fix / specification-only / full-sweep at start of window and announce the split in the shift note. Indexed in MEMORY.md under Feedback.
- **23 April 2026, 04:55 BST.** Documentary-state sv prep — ONBOARDING.md new oversight-Q&A block inserted at top of Current State (before overnight shift block); RECOVERY.md parallel block inserted at top of Current Pending Work; ce_state.md Key Facts prepended with oversight-Q&A summary; this operational plan Last-Updated header + Current-State snapshot + Completed-log + Resume-point updated.
- **23 April 2026, 05:01 BST.** Documentary-state sv commit `7c9df2b` landed via `scripts/cdsfl_sv.py --commit --push`. Four files committed: `docs/CURRENT_STATE.md` (auto-regenerated by sv script), `experimental_notes/CDSFL_Agent_Operational_Plan.md` (repo mirror), `resources/ONBOARDING.md`, `resources/RECOVERY.md`. Pushed to `origin/exp39-experimental`. Working tree clean post-commit. Memory file + Desktop canonical not in repo (per design); new memory file `feedback_fix_all_scope_split.md` lives in `~/.claude/projects/…/memory/`.
- **15 May 2026, 02:15 BST.** Pre-continuation post-mortem fix tranche landed across nine commits on `exp39-experimental` (HEAD `3bbf2c7`): (1) `35c44b6` decomposed-dispatch synthesis empty-response fallback; (2) `12ad362` Bugzilla CLOSED-loop module `bench/bugzilla_loop.py`; (3) `8cb1fbe` Bugzilla CLOSED-loop runner integration; (4) `26b28f8` gamma input post-reconciliation novelty fix; (5) `9891bda` Stage 6 calibrator `int`-flaw-class crash fix; (6) `a8a33c2` explicit Bugzilla paradigm in panel prompt; (7) `b2f3444` parse-admissibility-block FINDING_ID terminator regex fix; (8) `7f3066b` ITC CAPABILITY_MISMATCH false-positive guard; (9) `3bbf2c7` launcher_core shared infrastructure + G7 design (paired notes at `experimental_notes/G7_Merge_Deadlock_Resolution_Design_2026-05-15.md` + `_Plain_English_2026-05-15.md`, TTS at `~/Desktop/CDSFL_tts/G7_Merge_Deadlock_Resolution_Design_2026-05-15.txt`). Config bump: `bench/exp40_configs/40_gate.json` max_rounds 8→18, extension_cap 10→20.
- **15 May 2026, 03:15:48 BST.** Exp 40 continuation run launched via `python3 bench/launch_exp40.py --resume`. Resumed from Round 10 of the original 2026-05-14 run; registry restored with 146 entries. Background-task ID `bdqum45ab`; monitor task ID `b9hwsq8tn` (later re-armed as `bhfiygnhd` after timeout).
- **15 May 2026, 03:15:48 → 05:20:26 BST.** Run executed seven additional rounds (R10–R16). Wall-clock elapsed 7,478 seconds (cap was 7,200s; runner finished round close before exit). Final γ 0.034; final ρ 0.6; novel_critical_history last 10 rounds `[1, 0, 1, 0, 3, 2, 1, 0, 4, 2]` — γ-alt not met. Total canonical entries 179; 280 raw findings; status distribution OPEN 68 / CONFIRMED 42 / CLOSED 26 / UNCONFIRMED 23 / MERGED 19 / CONTESTED 1. Seventeen verified BUGZILLA CLOSED transitions during the continuation alone. Five D4 MERGE DEADLOCK distinct entries on the HIL queue (C0008, C0023, C0023 at fourteen rounds is the longest unresolved merge in project history, C0032, C0035, C0044, C0147). Three D2 HIL escalations (C0052, C0071, C0044). All five panel members hit DEGRADATION classification by Round 14; Gemini hit TRANSIENT_FAILURE twice. Active monitoring ran continuously across all heartbeats (~80 monitor events received and assessed); no FFAFP-grade halts triggered.
- **15 May 2026, 05:20:26 BST.** Runner exited cleanly (exit code 0). Final report saved to `bench/logs/exp40_gate_20260514T020550Z/exp40_gate_report.json`; final state at `runner_state.json`; per-round model outputs at `round{10..16}_{model}_*.json`. Monitor process detected Python gone and emitted termination notice.
- **15 May 2026, 05:25–05:30 BST.** Paired post-mortem written under CDSFL note standard v1.2 (locked 14 May 2026): technical version at `experimental_notes/Exp40_Continuation_Postmortem_2026-05-15.md` (~310 lines), plain-English companion at `experimental_notes/Exp40_Continuation_Postmortem_Plain_English_2026-05-15.md` (~200 lines), TTS plain-text at `~/Desktop/CDSFL_tts/Exp40_Continuation_Postmortem_2026-05-15.txt` (mirrors plain-English in TTS-safe formatting). Post-mortem assesses all seven fixes against live behaviour (all functioned as designed), records five anomalies for next-experiment attention (DeepSeek 0-char Phase-1 sections; parser code-fragment finding-IDs; LLM classifier sub-threshold OVERRIDE logs; RT v2 AUTOIMMUNE flag noise on Gemini per-round; ITC DEGRADATION-in-convergence false positive), and catalogues the G7 deadlock evidence cluster for the founder's implementation decision.

---

## Resume point (update after each task)

**Next action — founder review of the fix-tranche post-mortem (15 May 2026, evening).**

The post-continuation 12-item fix tranche is complete (9 engineering items
+ local architectural P-pass; 229 tests pass; HEAD `3bbf2c7`, working tree
regression-clean, sv pending). Read in this order:
   a. Plain-English `experimental_notes/Exp40_Fix_Tranche_Postmortem_Plain_English_2026-05-15.md`
      (or TTS `~/Desktop/CDSFL_tts/Exp40_Fix_Tranche_Postmortem_2026-05-15.txt`).
   b. Technical `experimental_notes/Exp40_Fix_Tranche_Postmortem_2026-05-15.md`
      — per-item outcomes, test ledger, files changed, deferral rationale.
   c. The 15 May 22:30 entries in the Completed log below.

**Two open items are founder DECISIONS, not unfinished work:**
   - **Live five-model architectural confer** — local P-pass covered the
     substance (found+fixed 2 issues). Live confer remains the founder's
     go/no-go gate before G7 *enablement*. Trigger: Codex CLI stability +
     founder available to supervise API spend.
   - **Exp 40 R17–R21 resume** — multi-hour run, significant OpenRouter
     spend, founder's established practice is close monitoring. Full fix
     tranche folded in + regression-clean; ready when the founder elects
     to start it, at the preferred monitoring cadence.

**sv** is also pending founder direction — the whole tranche is one
coherent regression-clean changeset ready to commit (new module
`bench/merge_arbitration.py`, 6 new test files, 10 modified files,
3 post-mortem docs, tracker).

---

### Superseded resume pointer (continuation post-mortem review — retained for trail)

1. Read the Experiment 40 continuation paired post-mortem in this order:
   a. Plain-English companion at `experimental_notes/Exp40_Continuation_Postmortem_Plain_English_2026-05-15.md` (or TTS mirror at `~/Desktop/CDSFL_tts/Exp40_Continuation_Postmortem_2026-05-15.txt`) — entry point for the narrative.
   b. Technical version at `experimental_notes/Exp40_Continuation_Postmortem_2026-05-15.md` — file paths, registry counts, commit hashes, fix-effectiveness assessment per fix, five anomalies catalogue, G7 deadlock evidence cluster.
   c. G7 design (pre-run) at `experimental_notes/G7_Merge_Deadlock_Resolution_Design_2026-05-15.md` and its plain-English companion — the rule that the continuation produced evidence for.
   d. The 15 May entries in this file's "Completed in current window" log — chronological summary of the pre-continuation fix tranche, the run itself, and the post-mortem write.

2. Four founder decisions now actionable:
   a. **G7 implementation decision.** Continuation produced the deferral-evidence cluster the G7 design was waiting for: six distinct findings hit D4 MERGE DEADLOCK escalation, including a fourteen-round marathon (C0023) and a twenty-way ambiguity (C0008). Decide: (i) proceed with implementation against the design at the path above, (ii) adjust design first, (iii) defer pending more evidence.
   b. **Five anomalies disposition.** Five anomalies identified for next-experiment attention (DeepSeek 0-char Phase-1 sections; parser code-fragment finding-IDs; LLM classifier sub-threshold OVERRIDE logs; RT v2 AUTOIMMUNE flag noise on Gemini per-round; ITC DEGRADATION-in-convergence false positive). None blocks Exp 41 entry. Decide: fix all before Exp 41, fix some, or defer to inline-fix-as-needed.
   c. **Resume Exp 40 vs advance to Exp 41.** Continuation reached deep convergence by γ-decay (terminal 0.034) but γ-alt boolean was not met. Two more rounds (R17, R18) within `max_rounds=18` are possible via `--resume` with a `wall_clock_cap_s` bump. Alternatively advance to Exp 41 (bounded mathematics module) per the planned arc. The post-mortem flags Exp 41 as the natural place to introduce G7 if implementation is approved.
   d. **sv timing.** Three new post-mortem documents are untracked + run produces many untracked log files. Decide: sv now (atomic post-run state preservation), or defer until after G7 implementation decision.

3. After founder decisions land, the resume pointer advances accordingly — either to G7 implementation surface (`bench/merge_arbitration.py` + runner integration around line 870–900 per the design's §Implementation Surface), to anomaly fixes, to Exp 40 R17–R18 resume, or to Exp 41 launch prep.

**Blocker on autonomous advance.** Founder decisions a–d above. The post-mortem captures all data needed for those decisions; no further automated work is outstanding.

**Context for the waking review.** HEAD `3bbf2c7` on `exp39-experimental` (pushed to origin pre-continuation). Working tree dirty: three new post-mortem documents (two markdown + one TTS), one updated tracker (this file + repo mirror not yet synced), many untracked per-round model output JSON files under `bench/logs/exp40_gate_20260514T020550Z/`, run log at `bench/logs/exp40_continuation_20260515T021531Z.log`, runner state + final report. Pre-continuation test count was 1255 (1121 non-network pass); the continuation did not run additional tests. The runner exited cleanly (exit code 0) at 05:20:26 BST after 7,478 seconds. No FFAFP-grade halts triggered across approximately eighty monitor events captured during the run.

**Phase E closed. Phase F remains gated on Exp 40–54 completion. Exp 40 is in a clean stopping state but neither γ-alt nor max-rounds convergence was reached; the founder's decision on resume-vs-advance determines whether Phase F advances to Exp 41 immediately or after a brief Exp 40 R17–R18 leg.**

---

## Notes on audience and format (non-content)

This file deliberately breaks some of the note-standard rules that apply to TTS and third-party-facing documentation:
- It uses process-adjacent headers ("Active work queue", "Phase A / B / C / …") because those headers are load-bearing for navigation by the agent.
- It uses short internal labels (G1–G9, A1–A8, etc.) without inline glossing on every reoccurrence, on the basis that the tracker is the label's own context.
- It uses first-person reference-frame ("resume point", "next action") because the intended reader is the agent continuing the work.

The foot-line is still applied per the standard's discoverability requirement.

---

Written under CDSFL note standard v1 (21 April 2026).
