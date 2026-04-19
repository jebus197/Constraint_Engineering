# CDSFL Project Onboarding

Last updated: 19 April 2026 13:48 BST

Read this document first if you are a new model instance, a new developer,
or a reviewer picking up this project for the first time.

## What This Project Is

CDSFL (Constraint-Driven Synthesis and Falsification) is a methodology for
making AI-assisted technical work more reliable. It formalises the scientific
method — specifically Popperian falsification — as a structured protocol that
AI models follow when producing and reviewing technical output.

The project began on 12 March 2026 (first commit). It
was built by a single founder (George Jackson) working with Claude Opus 4.6
as primary collaborator and OpenAI Codex 5.3 as independent falsifier, with
DeepSeek V3.2, Gemini 3.1 Pro, and ChatGPT 5.4 as additional review models.

**Repository:** `github.com/jebus197/Constraint_Engineering`
**Local path:** `/Users/georgejackson/Developer_Projects/Constraint_Engineering/`

**Visual architecture:** [`docs/CDSFL_Topology.svg`](../docs/CDSFL_Topology.svg) — whole-body topology map showing all components and their biological analogues.

## Current State (update after each major milestone)

<!-- SV:LATEST_EXP_START -->
- **EXP 40 STAGE 3 CLOSURE — PHASE A + PHASE B (17 April 2026, 08:00–14:30 BST):**
  Branch: `exp39-experimental`. HEAD `6580737` (docs sync) over `bdfc93a`
  (Phase B) over `8b8682d` (Phase A), 3 commits ahead of origin. Full
  suite: 1250/1250 tests passing (20 min 23 s wall-clock).

  **Scope:** close all actionable Stage 3 items from the Exp 40–54 plan
  that do not require Exp 54's `eta_int_modulator` wiring. Two autonomous
  continuation rounds under the founder's standing rest-period override.

  **Phase A — commit `8b8682d` (98 new tests):** items 1D.5 (S_k format
  pre-check with reformat request), 1D.6 (Gemini verdict extraction),
  1E.6 (dynamic decomposition by payload size), 1E.7 (cross-model
  diversity metric wired into per-round logging), 1E.10 (channel-
  assignment boundary helper `compute_rk_with_eta_channel`; runtime
  assertion awaits Exp 54 wiring).

  **Phase B — commit `bdfc93a` (200+ new tests):** items 1D.3 (per-model
  ρ tracking via `novelty_counts_per_model` + `raw_counts_per_model`),
  1E.3 (specialist cell live-promotion audit; FLIP deferred pending
  K/L/M tool-coverage confirmation), 1E.4 (physics/chemistry/engineering
  functional shadow cells — 21 tests, astropy + RDKit + pint + stoichio
  balance), 1E.5 (fingerprint attention metrics populated from ITC +
  parse-yield history), 1E.8 (Ouroboros query-quality fix + live arXiv
  verification), 1E.9 (cross-round recidivism via
  `prior_round_isomorphism`), 1E.11 (OpenRouter function-calling tool-
  use — 5 TOOL_SPECS, subprocess dispatchers, 36 tests),
  1E.12 (DeepSeek R1 formal-verification specialist — 29 tests,
  confidence capped at 0.5).

  **Residual Stage 3 items (both gated, not blocking Exp 40 launch):**
  - **1E.3 LIVE_SPECIALIST_DOMAINS flip** — one-line `frozenset` edit
    at `immune_agents.py:334`. K/L/M verdicts currently logged under
    `b_cell_specialist_shadow`. Held back pending founder judgement on
    broader tool coverage across claim types.
  - **1E.10 runtime call-site assertion** — depends on Exp 54 wiring
    of `eta_int_modulator` into `compute_rk`. Base wrapper
    `compute_rk_with_eta_channel` landed Phase A; runtime assertion
    lands with Exp 54.

  **Infrastructure status (B-Cell specialist dispatch):**
  - 18+ active tools in `bench/cdsfl_registry/tool_manifest.toml`
  - Live domains: mathematics, statistics, biology, information science
  - Shadow domains: physics (K), chemistry (L), engineering (M) —
    functionally verified, promotion gated

  **Side discovery, separate background task spawned:** `_verify_sympy`
  in `immune_agents.py` silently returns UNCERTAIN on every claim because
  the subprocess sandbox uses `global_dict={'__builtins__': {}}`, which
  prevents SymPy from constructing `Integer` literals. Framework-wide
  silent regression. A separate session has been delegated to repair
  it without reopening the MF-40 RCE vector the current blocklist closes.

  **§17 Feedback Channel + §18 Divergence Directive** both live.
  Penalty wiring into `compute_rk()` deferred by design for Exp 40
  attribution; lands in Exp 54.

  **Exp 40 status:** runner v2 scaffolded, tested at 1250, docs in
  place. Three open items before launch:
  1. Founder approval to promote runner v2 over frozen v1.
  2. Optional 1E.3 live-promotion flip.
  3. Push 3 local commits to origin on explicit `sv`.

  **Next session priorities:** (a) founder decision on v2 promotion;
  (b) Exp 40 launch against `bench/dm/_feedback.py` (~22K target,
  ~30K context); (c) fold Exp 40 lessons into Exp 41 config.

- **EXP 40–54 PLAN + RUNNER V2 SCAFFOLD (17 April 2026, 01:45–04:38 BST):**
  Branch: `exp39-experimental`. 935 tests still pass (no code changes).
  HEAD unchanged at `cc6cc1a` entering the session.

  **Session scope:** consolidate the novelty thread, recover full context,
  produce a parseable execution plan for Experiments 40–54, audit the
  inherited state of Part 1 bug-fix items, scaffold a new runner without
  modifying the Exp 39 runner.

  **Artefacts produced (all non-code except the v2 scaffold):**
  - `experimental_notes/Exp40_Readiness_and_Novelty_Review_2026-04-17.md`
    and TTS mirror — comprehensive review of the novelty thread,
    Exp 39's 14 sub-experiments, unfolded work, factors forward
  - `experimental_notes/Exp40_to_54_Execution_Plan_2026-04-17.md` —
    parseable plan: 5 parts, ~30 numbered items, acceptance criteria,
    gate criteria, canonical file layout
  - `experimental_notes/Exp40_Runner_Audit_2026-04-17.md` — shadow-log
    audit (12 files from Exp 39-0) + item-by-item verification of Part 1
    against current code
  - `bench/reference_runner_v2.py` — pristine 4,344-line copy of
    `reference_runner.py`, ready for in-place fixes

  **Significant finding during audit:** the plan's P0 backlog is
  overstated. Current `reference_runner.py` already has S_k format
  mismatch fixed (1A.1 DONE at line 2325), parser emitting source code
  as finding IDs fixed (1A.2 DONE via `_sanitize_fstring_id` and
  `_CODE_LEAK_VARNAMES` guard in `runner_core.py`), and convergence-gate
  threshold bumped from 0 to 5 (1A.3 PARTIAL — γ-alternative path still
  TODO). v2 inherits all of these fixes.

  **Scope decisions recorded (via `a, d` confer + founder approval):**
  - 14 single-target experiments, Exp 40–53, 1:1 mapping from 39-0
    through 39-M, each with a right-sized decomposed article
  - Exp 54 = integration run with 2×2 factorial for §17/§18 attribution.
    `eta_int_modulator` gets wired into `compute_rk` here; deferred from
    Exp 40 on resource grounds
  - Specialist cells mathematics/statistics/biology/information science
    promoted shadow → live for Exp 40; physics/chemistry/engineering
    built functional in shadow, promotion gated on empirical data from
    Exp 41 onwards
  - Runner evolves in place (single `reference_runner_v2.py`, no forks);
    `reference_runner.py` stays frozen until v2 is tested and explicitly
    promoted by founder decision
  - No preferred scientific outcome: Popperian interpretive analysis
    follows each experiment; claims are not pre-declared

  **Next session priorities:** γ-alt convergence path (1A.3 remainder),
  Macrophage wiring diagnosis (1B.1), DeepSeek parse-findings replay
  test (1B.3 verification), schema wiring items 1E.5–1E.8.

- **§18 ROUND-2 IMPLEMENTATION + ROUND-3 FINAL REVIEW (16 April 2026, 01:00–02:30 BST):**
  Branch: `exp39-experimental`. 935 tests pass (was 912; +23 new round-2
  divergence tests). Documentation refresh: 47 files reformatted for
  third-party voice + plain English + AI gender-neutrality (commit `0651974`).

  **Round-2 consensus implemented:** channel reassignment (η_int modulator,
  not R_k pre-factor), mandatory contrast statement, sibling alt-vs-alt
  mandatory rejection gate, near-copy 0.98 severe tier. Function renamed
  `divergence_penalty_multiplier` → `eta_int_modulator` (alias retained).
  Files: `bench/dm/_divergence.py` (rewrite), `cdsfl_operational.md` §18
  (rewrite), `universal.toml` + `schema.toml` (3 new fields each).

  **Tool cross-check:** SymPy/z3 verification 41/41 pass. Channel-assignment
  invariant confirmed symbolically: ∂R/∂m ≠ 0 (modulator reaches R_k);
  η_int=0 kills path (multiplicative); c_ext=1,ν_k=0 kills path (known).
  ruff + mypy clean. 75/75 divergence tests, 935/935 full suite.

  **Round-3 5-panel review** (`bench/confer_divergence_round3_final.py`):
  3/5 immediate convergence (Gemini, CC2, DeepSeek). 2/5 diverged (Codex,
  ChatGPT) on one prose/code mismatch in the severe-tier documentation —
  corrected. Effective 5/5 after fix.

  **Residual debt (documented, not blocking):** recidivism detection needs
  cross-round state from reference_runner.py; end-to-end channel-assignment
  boundary unverified at integration call site; `divergence_config_from_dict(None)`
  returns `enabled=False` (intentional).

  **Founder feedback (standing correction):** CDSFL must converge to ONE
  definitive recommendation for the HIL, not present multiple options.
  Alternatives are internal exploration; output is a single answer with
  visible reasoning. Recorded in `memory/feedback_hil_fatigue.md`.

- **§17 + §18 FIVE-PANEL REVIEW AND ROUND-2 CONVERGENCE (15 April 2026, 23:02Z → 16 April 00:10 BST):**
  Branch: `exp39-experimental`. 912 tests pass (baseline unchanged — this
  session is review-only, no schema edits yet). Stage 6 math served as the
  convergence arbiter.

  **Round 1 — 5-panel CDSFL/FFAFP review** (`bench/confer_divergence_directive.py`,
  combined log `bench/logs/confer_divergence_directive/combined_20260415T220231Z.json`,
  notes `experimental_notes/Panel_Review_Section17_Section18_2026-04-15.md`
  + TTS `~/Desktop/CDSFL_tts/Panel_Review_Section17_Section18_2026-04-15.txt`
  plain English rewrite). Five questions put to Gemini 3.1 Pro, Codex GPT-5.4,
  ChatGPT GPT-5.4, CC2 Opus 4.6, DeepSeek R1-0528 in parallel (~3 min wall).

  All five converged on: tradeoff dimension is meta (risks swallowing the
  ontology), Jaccard is lexical not semantic, Exp 39/40 plan confounds the
  two directives' signals, compliance theatre is the dominant Q5 risk, ship
  both. Panel diverged on (D1) Jaccard threshold, (D2) penalty tier
  structure, (D3) experimental design.

  **One HARD mechanical finding — sibling alt-vs-alt check missing**
  (Codex + ChatGPT independent): §18 text requires alternatives to pass
  isomorphism against primary *and* against siblings; implementation only
  checks against primary. Spec/implementation gap. ~10 LOC fix + 3 tests.
  Ship-blocker for Exp 40.

  **Round 2 — mathematical-convergence confer** (`bench/confer_divergence_round2_convergence.py`,
  combined log `bench/logs/confer_divergence_round2_convergence/combined_20260415T224529Z.json`,
  notes `experimental_notes/Round2_Convergence_Section17_Section18_2026-04-15.md`
  + TTS). Stage 6 math put in front of all 5 models as binding arbiter: R_k
  recursion, η_combined = η_int · (1 − c_ext · (1 − ν_k)), orthogonality
  C1, continuous suppression w(f), similarity backend, kappa_set. Charge:
  converge to a single definitive answer per divergence; answer may be
  synthesis OR entirely novel. Binding constraints C1 (orthogonality),
  C2 (w(f) ∉ q_eff), C3 (novelty detectability), C4 (scientific rigour).

  **Six-way structural question asked first — where does the §18 multiplier
  mathematically belong?** Options: (i) R_k pre-factor (current spec) /
  (ii) η_int modulator / (iii) ν_k modulator / (iv) w(f) modulator /
  (v) FFAFP admissibility gate / (vi) combination.

  **5/5 UNANIMOUS** — multiplier is **NOT** on R_k. Current spec is a
  category error (R_k measures validity; §18 is generator-side novelty
  enforcement). Primary channel = **η_int**; structural compliance gated
  at **FFAFP admissibility**; continuous isomorphism suppression already
  handled by **w(f)** in kappa_set. 5/5 explicit: ν_k must NEVER be
  modulated by §18 (literature novelty is O1-external). 5/5 on **2×2
  factorial** design for D3. Gemini self-falsified its round-1 "§18-only
  invalid" under the parameter-orthogonality argument.

  **Residual divergence is narrow (Phase 2 empirical):** tier structure
  abolish vs retain on η_int (2 vs 3); Jaccard-0.85-MVP vs immediate
  similarity-backend swap (3 vs 2).

  **Three decisions pending founder approval:**
  1. Adopt channel reassignment: §18 multiplier off R_k, onto η_int +
     admissibility. ~30 LOC + 8–12 tests. Recommend yes before Exp 40.
  2. Adopt contrast-statement requirement ("X changed, Y held constant"
     per alternative). ~5 lines directive + ~20 LOC parser + 3–5 tests.
     Cheap disambiguator for genuine vs theatre novelty. Recommend yes.
  3. Experimental design: Option C (cells B+C+D, reuse Exp 36–38 for A)
     recommended. Option B (B+D only with narrowed claim) is current-plan
     fallback. Option A (full 2×2 with fresh A) overkill.

  **Deferred:** Phase 2 embedding backend swap (sentence-transformers),
  penalty tier recalibration (let Exp 40 data argue), opportunity-cost-
  sufficiency test (does §18 need an explicit penalty or does differential
  convergence credit suffice? CC2's falsifier — Exp 40 cell D vs B
  measures it).

  **Non-obvious result:** the channel-reassignment answer was not present
  in any round-1 response. Five models independently arrived at the same
  topology under a shared mathematical instrument. Mechanism: load-bearing
  orthogonality constraints disambiguate where prose intuitions diverge.
  The discipline generalises beyond this divergence set.

- **DIVERGENCE DIRECTIVE — CDSFL'S BOLD-CONJECTURES ARM (15 April 2026, ~22:40 BST):**
  Branch: `exp39-experimental`. 912 tests pass (was 832; +28 sv-script fix tests
  from earlier today, +52 new divergence-directive tests).

  **User framing (scoping memo `experimental_notes/Invention_Engine_Divergence_Directive_2026-04-15.md`):**
  CDSFL was built as an "invention engine", framed against the Lance McLane
  sci-fi cartoon strip that ended unresolved. Popper's method has two arms —
  bold conjectures and severe tests. The severe-tests arm (§17 feedback
  channel, FFAFP admissibility, cross-model corroboration, tool enforcement)
  is highly developed. The bold-conjectures arm was implicit. §18 closes the
  asymmetry.

  **Fix landed — divergence directive (§18):**

  1. NEW `bench/dm/_divergence.py` (443 lines). `ALLOWED_DIMENSIONS` tuple
     fixes the five allowed dimensions of difference — mechanism, assumption,
     scope, timescale, tradeoff — with a synonym normaliser that maps
     variants (e.g. `premise` → `assumption`, `trade-off` → `tradeoff`).
     `DivergenceConfig` dataclass carries runtime knobs. `AlternativeRecord`
     / `DivergenceRecord` dataclasses capture per-alternative and per-finding
     audits. `parse_alternative_block()` accepts multiple header styles
     (inline parenthetical / bracket tags, dash tags, follow-up
     `Dimension:` lines, bold markdown, `#` headings). `score_isomorphism()`
     is Jaccard over normalised token sets (embedding backend deferred to
     Exp 39 Phase 2). `validate_alternative()` enforces dimension presence,
     length cap, isomorphism threshold (default 0.85), reporting every
     failure. `parse_null_justification_block()` extracts scoped null
     alternatives. `validate_null_justification()` enforces minimum length
     floor (default 60 chars). `build_divergence_record()` assembles the
     per-finding audit and sets `compliant = True` iff
     `min_alternatives` (default 1) admissible alternatives survive OR a
     valid null-justification is supplied. `divergence_penalty_multiplier()`
     returns a scalar in (0, 1]: 1.0 (compliant), 0.85 (engaged-but-failed),
     0.70 (no engagement), 0.60 (isomorphic-only — double penalty per §18).

  2. `bench/directives/universal/cdsfl_operational.md` — NEW §18 (~90
     lines). Imperative mandate. Frames the gap (Popper's missing arm),
     lists the five allowed dimensions, defines Structure A
     (primary + alternative on named dimension) and Structure B
     (primary + scoped null-justification), rejects cosmetic rewordings
     with isomorphism check and double penalty, declares that divergence
     operates only in SOFT-constraint space (HARD constraints inviolable
     for primary and every alternative), declares interaction with §17
     (refuted alternatives resurfaced unchanged are inadmissible).
     Disablement gated via `[divergence] enabled = false` for controlled
     ablation only.

  3. `bench/directives/universal/cdsfl_core_formal.md` — classification
     summary table, new row for divergence directive pointing to
     `cdsfl_operational.md` §18 and `bench/dm/_divergence.py`.

  4. `bench/cdsfl_registry/universal.toml` — NEW `[divergence]` section
     (enabled=true, min_alternatives=1, max_chars_per_alternative=2000,
     mode=imperative, isomorphism_threshold=0.85,
     null_justification_min_chars=60).

  5. `bench/cdsfl_registry/schema.toml` — 6 `[divergence.*]` parameter
     entries registered (same pattern as §17 Phase 10 fix; policy engine
     now recognises the new block and will not reject it on load).

  6. NEW `bench/tests/test_divergence_directive.py` — 52 tests across 9
     classes (TestAllowedDimensions, TestParseAlternativeBlock,
     TestIsomorphismScoring, TestValidateAlternative,
     TestParseNullJustification, TestBuildDivergenceRecord,
     TestDivergencePenalty, TestDisabledDirective, TestConfigFromDict).
     All 52 green on first real run. Full regression **912/912**.

  **Live-default, not shadow.** Mirrors §17 decision — the directive is
  the point of CDSFL, not an experimental add-on. Toggle retained for
  controlled ablation.

  **R_k wiring deliberately deferred.** `divergence_penalty_multiplier()`
  is exposed as a library function but not yet applied inside
  `compute_rk()`. Reason: the scoping memo recommends sequencing the
  work after the Exp 39 baseline so each intervention's signal stays
  attributable. Wire it in once baseline data arrives.

  Companion implementation summary (plain English +
  TTS): `experimental_notes/Divergence_Directive_Implementation_2026-04-15.md`
  and mirror on `~/Desktop/CDSFL_tts/`.

- **FEEDBACK CHANNEL — CLOSE THE MEASUREMENT-TO-CORRECTION LOOP (15 April 2026, 19:xx → 20:xx BST):**
  Branch: `exp39-experimental`. 832 tests pass (was 793; +39 new feedback-channel
  tests). 2 commits ahead of origin after this sv.

  **User insight that triggered this session:** the schema performs rich
  round-by-round calculation (B-Cell verdicts, FFAFP admissibility, NK-Cell
  duplicate detection, R_k validation) but that signal was being logged and
  discarded. Models never saw it, so the same refuted claim could be
  resubmitted in the next round. Quote: "Measurement is nice. It's a nice
  to have. But the entire point of this project was to make LLM's more
  reliable, more trustworthy and more accurate. What is the point in this
  measurement if we don't use it for anything productive, except for
  knowing when the models got things wrong?"

  **Fix landed — feedback channel (Phase 10):**

  1. NEW `bench/dm/_feedback.py` (533 lines). `FindingFeedback` dataclass
     captures per-finding schema judgment: refutations (tool + verdict +
     evidence), admissibility failures (gate names), duplicates
     (prior_id, cosine), R_k discrepancy (claimed vs aggregate).
     `build_feedback_records()` merges four independent signals into one
     record per flagged finding. `build_feedback_sections()` renders
     per-model prompt prefixes with top-K cap (default 10) and
     max-chars-per-model cap (default 8000). `parse_admissibility_block()`
     is a tolerant regex parser — accepts σ or sigma, case-insensitive
     PASS/FAIL, multiple separators; missing block → all 5 gates FAIL.
     Priority: refutation > admissibility > duplicate > R_k, with severity
     as tiebreak. Action: RECALCULATE / ADD_ADMISSIBILITY_OR_WITHDRAW /
     DIFFERENTIATE_OR_WITHDRAW / RECALIBRATE_RK.

  2. `bench/reference_runner.py` — wired into round loop. New
     `_build_feedback_for_next_round()` helper runs after `immune_result`
     is available (line ~3808). Output flows via
     `feedback_sections_for_next_round` dict into `_dispatch_round_star`
     for round K+1, where `_make_prompt(mc_label)` prepends the section
     before the base prompt. Defensive: build failures return empty dict
     rather than crash the loop. `RunnerConfig` gets three knobs:
     `feedback_channel_enabled` (default True), `feedback_top_k` (10),
     `feedback_max_chars_per_model` (8000).

  3. `bench/directives/universal/cdsfl_operational.md` — NEW §17 (~90
     lines). Frames the channel as imperative (MUST address), documents
     action precedence, tells models they may refute a schema tool by
     providing counter-receipts (not self-reported confidence),
     resubmission of unchanged flagged findings is explicitly
     inadmissible. Rendering boundary and disablement note included.

  4. `bench/directives/universal/cdsfl_core_formal.md` — classification
     summary table expanded: C(n) row split into three — Stage 1
     reference (C(n)), Stage 5–6 operational (R_k(i)), Stage 6 feedback
     channel (per-finding records) — with pointers to operational §3,
     §16, §17 and `bench/dm/_feedback.py`.

  5. `bench/cdsfl_registry/universal.toml` — NEW `[feedback_channel]`
     section (enabled=true, top_k=10, max_chars_per_model=8000,
     mode="imperative"). `[constraints]` FFAFP comment refreshed to
     mention §17 routing.

  6. NEW `bench/tests/test_feedback_channel.py` (39 tests across 5
     classes: TestPriorityAndAction, TestBuildFeedbackRecords,
     TestBuildFeedbackSections, TestParseAdmissibility, TestFullPipeline).
     All 39 green; full regression green (832 total).

  **Design decisions worth remembering:**

  - Live-default, not shadow-first. The user's framing (measurement for
    its own sake is wasted) is structurally incompatible with indefinite
    shadow mode. Toggle retained for controlled ablation.
  - Imperative, not advisory wording. "MUST address" — there is no
    self-reported-confidence escape hatch.
  - No schema math changes. No new convergence thresholds. Pure plumbing
    from data already on the floor.
  - The admissibility parser is permissive by design (matches existing
    `runner_core.py:333` convention). Enforcement lives downstream; the
    parser just classifies for §17 feedback.

- **MODEL-FACING DIRECTIVE GAP CLOSURE — STAGE 6 + FFAFP (15 April 2026, 14:xx → 19:03 BST):**
  Branch: `exp39-experimental`. 793 tests pass in 703s (11m 43s). 1 commit ahead of
  origin after this sv. User directive: "plug all remaining outstanding gaps both
  in the experiment 39 runner and in the CDSFL schema as a whole. (Including any
  stale docs.) Take care and work sequentially."

  **Problem found:** Grep for FFAFP / c_ext / e_value in `bench/directives/universal/`
  returned zero matches before edits. Stage 6 and the FFAFP admissibility constraint
  set existed only in the mathematical appendix — not in what models actually
  receive at run time. Appendix is authoritative; directives are operative.

  **Edits landed (7 files):**
  1. `bench/directives/universal/cdsfl_operational.md` (448 → ~660 lines):
     - §9 line 366: `ν_k` → `ν_eff,k` to resolve symbol collision with Stage-6
       literature novelty. Added Notation note disambiguating operational
       re-injection floor (ν_eff) from appendix literature novelty (ν_k).
     - §2 Output Format: mandatory ADMISSIBILITY + NOVELTY reporting blocks.
       Missing ADMISSIBILITY flagged by FFAFP gate; missing NOVELTY defaults
       to (ν_k=0, c_ext=0) — Stage 6 reduces to Stage 5. Parser is permissive
       by design (see `runner_core.py:333`); enforcement is downstream via gates.
     - NEW §15 — FFAFP Admissibility Constraint Set. Formal definitions of
       S_min, G-completeness, d_tool, σ_measured, q_retest plus reporting template.
     - NEW §16 — Stage 6 Literature-Calibrated Extension. Four-quadrant
       (ν_k, c_ext) table, η decomposition η_combined = η_int·(1−c_ext·(1−ν_k)),
       orthogonality with R_k, E-value shadow-mode note, directive hierarchy.
  2. `bench/directives/universal/cdsfl_core_formal.md`: §5 C(n) prefaced with
     Stage-awareness blockquote — C(n) is Stage 1, operational uses R_k(i);
     Stage-6 pointers to operational §3, §16 and appendix §1.1.
  3. `bench/directives/universal/expert_encoding_template.md` §6: S* formula
     corrected from `(nu_b + nu_f − q·R) / nu_f` (approximation) to full form
     `(nu_b + nu_f − nu_b·nu_f − q·R) / (nu_f · (1 − nu_b))`. Old form only
     accurate when nu_b ≪ 1.
  4. `bench/cdsfl_registry/universal.toml`: `ffafp_required = true` comment
     expanded — 4-step → 5-step protocol, admissibility-set mention.
  5. `bench/reference_runner.py` (~lines 3398-3409): prompt template extended
     with ADMISSIBILITY (5 gate pass/fail lines) and NOVELTY (ν_k, c_ext,
     H/H_max, Citations) blocks with worked examples.
  6. `.claude/CLAUDE.md`: appendix line count 1081 → 1991 with Stage-6
     annotation (was stale since Tranche C).
  7. `bench/logs/immune_pipeline.log`: test-run artefact from regression.

  **Verification:** Operational directive is loaded separately at
  `reference_runner.py:149` and appended post-composer at line 1509, bypassing
  phenotype caps — updates propagate to all 5 models. Stage 6 now visible in
  the model's actual prompt context, not just in documentation.

  **Confer activity this session:** none. Pure schema plumbing; no novel
  claims requiring multi-vendor falsification.

  **HIL-deferred (unchanged from previous sv):**
  - OpenRouter tool-use wiring for cx/ge/cgpt/ds.
  - B-Cell specialist dispatch shadow→live flip at `reference_runner.py` ~3741.

- **TRANCHES A / B / C — B-CELL DISPATCH CONSOLIDATION (14 April 2026 evening, 19:56 → 23:01 BST):**
  Branch: `exp39-experimental`. 793 tests pass. 4 commits ahead of origin.
  Three sequential tranches executed under "boring and safe" directive after
  an API 500 earlier in the day (recovery from a ~580-line single edit).
  One wrapper per tool call, targeted greps, single-claim smoke tests.

  **Tranche A — housekeeping (commit `6838160`, 19:56 BST):**
  CLAUDE.md crosshair moved out of "NOT installed" into the Code Analysis
  Tools table. `sv` sequential-reading protocol added to CLAUDE.md and user
  global directives. No functional code changes.

  **Tranche B — 5 new B-Cell specialist wrappers (commit `0c1de8e`, 21:02 BST):**
  - `_verify_symbolic_execution` (crosshair 0.0.102) — behavioural contracts
  - `_verify_chemistry_structure` (rdkit 2026.3.1) — SMILES/molecule validation
  - `_verify_biological_sequence` (biopython 1.87) — sequence structure
  - `_verify_ml_claim` (scikit-learn 1.8.0) — ML metric/model claims
  - `_verify_graph_property` (networkx 3.6.1) — graph theoretic claims
  5 new elif branches appended after the prior 9. 4 domain TOMLs updated.
  New installations: rdkit, biopython, scikit-learn, networkx. matplotlib
  was already present. 793 tests green.

  **Tranche C — manifest-driven dispatch refactor (commit `2f22a8a`, 23:01 BST):**
  NEW `bench/cdsfl_registry/tool_manifest.toml` (238 lines, 20 entries:
  18 active + 2 delegated). Schema: description, verifier, needs_file,
  claim_types, domain_hints, cost_class, install_check, package_hint,
  delegate. `_load_tool_manifest()` lazy singleton added at
  `immune_agents.py:148` with belt-and-braces validation (drops entries
  whose verifier does not resolve). `_specialist_b_cell_dispatch()` body
  replaced: 46-line elif chain → 12-line manifest-driven loop. First-
  definitive-verdict semantics preserved, `[specialist:<tool>]` evidence
  suffix intact, `finding_id` stamped. Adding a new B-Cell specialist is
  now a TOML-only edit. 793 tests pass in 12m 24s.

  **Staleness introduced this session:** CLAUDE.md "NOT installed" line
  still cites rdkit, biopython, scikit-learn, networkx, matplotlib — all
  five now installed. Flagged in RECOVERY.md for next-session patch.

  **Pre-Tranche-A chore (commit `d9f8f82`, 19:52 BST):** Stage 6 confer
  residuals from the morning session committed — `bench/dm/_shadow_stage6.py`
  (740 lines), 3 confer driver scripts, 3 Stage 6 syntheses, confer log
  dirs. Pure cleanup of prior untracked-artefact item.

  TTS: pending on next working session (deferred — user approaching rest).

- **DOMAIN TOOL WIRING — B-CELL SPECIALIST DISPATCH (14 April 2026 18:37 BST):**
  Branch: `exp39-experimental`. 793 tests pass (full regression, 17m 21s). Immune-scoped
  subset: 136 tests in 4m 44s. Zero regressions.

  **Scope:** 9 subprocess wrappers added to `bench/immune_agents.py` (lines 1114–1734)
  and 9 `elif` branches appended to `_specialist_b_cell_dispatch()` (lines 1913–1931,
  after existing sympy/z3/statsmodels/scipy branches — first-definitive-result-wins
  semantics preserved).

  **STEM wrappers (claim-only):**
  - `_verify_dimensional_analysis` (pint 0.25.3) — DIM_CONSISTENT/DIM_INCONSISTENT
  - `_verify_uncertainty_propagation` (uncertainties 3.2.3) — UNC_CONSISTENT/UNC_INCONSISTENT
  - `_verify_stoichiometric_balance` (regex + collections) — STOICH_BALANCED/STOICH_UNBALANCED
  - `_verify_linear_programming` (PuLP 3.3.0) — LP_PARSED/LP_BOUND_ONLY
  - `_verify_astronomical` (astropy 7.2.0) — ASTRO_VERIFIED/ASTRO_MISMATCH

  **Code wrappers (claim + file_path):**
  - `_verify_type_check` (mypy 1.19.1), `_verify_lint_check` (ruff 0.15.9),
    `_verify_security_scan` (bandit 1.8.6), `_verify_bytecode_analysis` (dis stdlib)

  **Domain configuration updates** — 5 TOMLs in `bench/cdsfl_registry/domains/immune/`:
  physics (+astronomical, +uncertainty_propagation), engineering (+linear_programming,
  +uncertainty_propagation), chemistry (+dimensional_analysis, +uncertainty_propagation),
  biology (+dimensional_analysis, +uncertainty_propagation), cross_domain
  (+dimensional_analysis, +uncertainty_propagation). `cs_software.toml` already
  referenced code tools from a prior session.

  **Bugs found and fixed during smoke testing (pre-regression):**
  1. Dimensional analysis regex required units ≥2 chars, silently skipping `m`, `s`, `N`.
     `immune_agents.py:1131` — changed `+` to `*` in unit char class.
  2. Ruff `--output-format=text` rejected (valid values begin with `concise`).
     `immune_agents.py:1626` — corrected to `concise`.

  **Shadow containment:** New wrappers run inside `_specialist_b_cell_dispatch()`,
  captured via `specialist_verdicts` at the `reference_runner.py` call site (~line 3741)
  but NOT extended into `all_verdicts`. Promotion to active is a single-line flip,
  not touched this session.

  **Installation gap:** Crosshair (symbolic execution) not installed — no wrapper
  written. hypothesis, beartype, icontract, pyright, mutmut, coverage installed
  but not wired into any cell (deferred — cell-design scope).

  **Hygiene note:** Session included one Anthropic API 500 triggered by a
  ~580-line single Edit inserting all 9 wrappers. Recovered via
  `scripts/cdsfl_recover.py --full`. Work continued with one edit per tool call,
  targeted greps, single-claim smoke tests. Post-mortem:
  `bench/API_500_SELF_DIAGNOSIS.md`.

  Notes: `experimental_notes/Domain_Tool_Wiring_2026-04-14.md`.
  TTS: `~/Desktop/CDSFL_tts/Domain_Tool_Wiring_2026-04-14.txt`.

- **POST EXP 39-0: TOOL PERMISSIONS + ν_k DESIGN + STAGE 6 CONFER (14 April 2026 11:30 BST):**
  Branch: `exp39-experimental`. 793 tests pass.
  
  **Tool permissions resolved:**
  CC1 (interactive): `.claude/settings.json` auto-approves all native + MCP tools.
  CC2 (sub-agent): `--allowedTools Bash Read Write Edit Grep Glob WebFetch WebSearch`.
  
  **ν_k (nu-k) novelty metric — two-dimensional design, confer-verified:**
  Per-finding literature novelty score ∈ [0,1]. Computed by O1 (Ouroboros) cell.
  Two-dimensional reporting: (ν_k, c_ext, H/H_max) triple per finding, never collapsed.
  Composes with existing η: `η_combined = η_int · (1 − c_ext · (1 − ν_k))`.
  Abstraction is context only — does not modify scores (founder pivot, 14 April).
  Stage 6 added to MATHEMATICAL_APPENDIX.md (§1.1, §1.6, §1.7, §1.8).
  Confer Round 1 (Gemini + Codex): 7 corrections (3 HARD, 4 SOFT).
  Confer Round 2 (Codex + Gemini): 5 HARD + 3 SOFT corrections.
  Both models confirm two-dimensional architecture is correct direction.
  Shadow calibrator (`bench/dm/_shadow_stage6.py`) hooked into runner.
  Synthesis: `experimental_notes/Stage6_R2_Confer_Synthesis_2026-04-14.md`
  
  **Still outstanding for Exp 39-1:**
  - DeepSeek specialist role (Phase 6) — smoke tested, not wired
  - OpenRouter tool-use mode for panel models
  - 7 lessons-forward items from Exp 36-38 still pending
  - Fingerprint attention metrics gap still open
  - ν_k production implementation (Phase 7) — designed + shadow calibrator, not live

- **EXP 39-0 GATE — 10 BUGS FOUND AND FIXED (14 April 2026 02:19 BST):**
  Branch: `exp39-experimental`. Commit: 5814760. 793 tests pass.
  Type: Gate experiment — runner_core.py (38K), star topology, 5 models.
  **6 rounds (R0-R5), 111 raw findings, 41 canonical (39 real + 2 phantom). γ=0.461.**
  Terminated by wall clock cap (4388s / 73 min). Convergence gate never passed
  (max_open_crit_high=0 was structurally unreachable — now fixed to 5).
  R_k adoption: **5/5 (100%)** — all models computing self-assessment equation.
  
  **10 bugs found by 5 parallel analysis agents, all fixed:**
  P0: S_k format mismatch (0% admissible → both formats now parse), convergence
  gate unreachable (0→5), CC2 Bash access enabled (can now execute SymPy/z3),
  parser finding ID leaks (source code variables + f-string templates filtered).
  P1: Macrophage monitoring modes wired (provenance/gate_stats/ouroboros_metrics),
  post-parse R_k validation (deterministic recomputation, advisory), fingerprint
  cache race condition fixed, payload double-counting fixed.
  P2: Autoimmune false alarm split (DEPLETION vs AUTOIMMUNE), ITC parse_yield
  now counts verdicts (no false DEGRADATION on verdict-heavy output).
  
  Full post-mortem: `experimental_notes/Exp39_0_Gate_PostMortem_2026-04-14.md`
  5 detailed analyses: `bench/logs/exp39_0_gate_20260413T193320Z/analysis_*.md`

- **EXP 39 CELL TYPE SPLIT + GAP ANALYSIS (12 April 2026 23:56 BST):**
  Cell type split, 4 confer rounds, gap analysis. See experimental notes.

- **EXP 38 COMPLETE (11 April 2026 14:33 BST):**
  Type: Ouroboros — system reviews and improves itself under structured falsification.
  Target: `bench/reference_runner.py`, star topology, 5 models, adaptive rounds.
  24 rounds (R0-R23), 545 raw findings, 169 canonical. γ_final=0.510.
  Never converged. Terminated by wall clock cap (29,503s / 8h12m).
<!-- SV:LATEST_EXP_END -->


- **README v3 CORRECTIONS + NEW `rg` MC COMMAND (19 April 2026, 09:45–10:30 BST):**
  Session work, no new experimental evidence. Two strands continuing
  directly from the 18 April v3 draft session.

  **Strand 1 — Thirteen-point correction sweep of the README v3 draft.**
  Founder-directed corrections applied to both
  `README_v3_draft_2026-04-18.md` and the TTS sibling
  `~/Desktop/CDSFL_tts/README_v3_Draft_2026-04-18.txt`. (1) Exp 39 /
  Exp 40 runner references stripped — README is about what the
  project IS, not what is currently in flight; such content belongs
  in RECOVERY.md and experimental_notes. (2) Ouroboros cell
  explained on first mention (symbol of self-reference applied to
  literature-checking discipline on findings the framework's own
  models have produced). (3) Five-model heterogeneous panel given
  explicit "remarkable-fact" framing in the Abstract (different
  training curricula, objectives, tokenisers, safety regimes —
  blind-spots-as-signal). (4) Tool-deterministic constraint box
  made explicit in Part 1 and Part 5 as a load-bearing commitment,
  with the open-source tool envelope enumerated (SymPy, z3, NumPy,
  SciPy, mpmath, uncertainties, pint, astropy, RDKit, Biopython,
  NetworkX, scikit-learn, AST, ruff, mypy, bandit, CrossHair) and
  the "deterministic verification over statistical pattern
  completion" behaviour documented. (5) Unified recursive state
  equation R_k(i) documented in §6.5 as the models' own reasoning
  methodology from Exp 37 onwards — each model computes q = η·d·p,
  derives R_detection/R_base/updated R_k, and uses ΔR_k as its
  stopping heuristic, moving reasoning onto a numerical surface
  the HIL can inspect. (6) Biological analogy forward-referenced
  on first mention in Part 1 so no cell name is used before §8/§9
  explain it. (7) B-Cell Complex reframed as applicable across
  eight STEM domains — mathematics, physics, chemistry, engineering,
  biology, statistics + ML, graph theory, code-level behavioural
  contracts — not just code correction. (8) Wolfram Alpha clarified
  as local cross-check only, never in the admissibility chain
  during a run; project prefers open-source tools wherever a
  fit-for-purpose alternative exists ("fundamentalist open source").
  (9) Future-development framing stripped from §11 — Exp 40 2×2
  factorial paragraph and three canonical panel sub-questions
  (authoring bridge, single-user mode, topology review) moved to
  experimental_notes / RECOVERY with a single pointer paragraph
  left behind. (10) §9 Confer definition reworded ("what model
  panels do to each other" informal phrasing removed). (11) Topology
  defined inline on first mention in §8 ("the pattern of which
  agents communicate with which, and through what routing — the
  graph shape of the review network"). (12) Substrate/model
  agnosticism expanded in §9 to cover human teams, heterogeneous
  multi-vendor machine panels, hybrid teams, and non-human
  biological intelligences; the evaluation machinery does not
  privilege any substrate at the level of its definitions.
  (13) New §9 HIL definition block — final decision authority on
  fix application, stage promotion, constraint reclassification,
  and contested-finding adjudication; "not a rubber stamp";
  single-recommendation-per-decision convergence; substrate-agnostic
  by function rather than by species. TTS timestamp bumped
  09:52 → 10:23 BST; Draft revision bumped three → four. Markdown
  closing line reframed: "19 April 2026. Fundamentalist open source
  under the MIT License. A running system, a maintained test suite,
  and a mathematical appendix under iterative extension."

  **Strand 2 — New `rg` MC command introduced and registered.**
  Founder named a new metacognitive command during the correction
  list: `rg <topic>` = re-read the anchoring resources for that
  topic (persistent-memory files, canonical project docs,
  experimental notes, directive files) before producing new output
  on it, and name the resources consulted in a one-line preamble.
  Trigger observation: multiple concepts the founder considered
  foundational (substrate agnosticism, the HIL's role, the
  tool-deterministic constraint box, the biological analogy, the
  unified equation as reasoning method) had not made it onto the
  README surface despite being present throughout the project
  record — session state was insufficient, canonical resources
  were where the truth lived. Registered in the four locations
  named by the founder's standing directive:
  `~/.claude/CLAUDE.md` (shorthand list + dedicated paragraph
  after the sv paragraph), `.claude/CLAUDE.md` (project MC table),
  `docs/REPRODUCING.md` (MC table), and
  `~/.claude/projects/-Users-georgejackson-Developer-Projects/memory/MEMORY.md`
  (Shorthand Additions + Feedback section pointer). New
  persistent-memory file
  `~/.claude/projects/-Users-georgejackson-Developer-Projects/memory/rg_command.md`
  created with full protocol body — trigger conditions, overlap
  with `rt` (wholesale rebuild) and `rs` (session state restore),
  anchoring-resource list, and the requirement to name consulted
  resources in the rg preamble. Combinable with other MC commands
  in the usual way: `rg p` = regain context then P-pass;
  `rg a d` = regain context, analyse dispassionately, discuss
  before proceeding.

  **Working tree state at sv entry:**
  Branch: `exp39-experimental`. HEAD `7334e49` (last sv).
  Modified, tracked: `.claude/CLAUDE.md` (rg row),
  `docs/REPRODUCING.md` (rg row). Untracked at repo root (not in
  sv whitelist — retained for founder's README-promotion decision):
  `README_v2_draft_2026-04-18.{docx,html,md}` and
  `README_v3_draft_2026-04-18.md` (13 corrections applied this
  session). Outside the repo: `~/.claude/CLAUDE.md` edited,
  `~/.claude/projects/-Users-georgejackson-Developer-Projects/memory/MEMORY.md`
  edited, `memory/rg_command.md` created, TTS file at
  `~/Desktop/CDSFL_tts/README_v3_Draft_2026-04-18.txt` fully
  mirrors the markdown at revision four. 1250/1250 tests still
  passing — no `bench/` code touched this session.

  **Still pending (not sv-blocking):**
  - Regenerate `docs/CDSFL_Topology.svg` with expanded B-Cell
    types (carried forward from prior sv).
  - Founder decision on `README.md` promotion (v2 vs v3 vs
    retain current).
  - Untracked v2 `.docx/.html/.md` cleanup once a promotion path
    is chosen.
  - Return to the outstanding Experiment 40 confer round with the
    other models, per founder's framing at the start of this
    session.

- **README v3 DRAFT + NOVELTY-SYNTHESIS GAP CLOSURE + APPLY-DRAFTED-EDITS DIRECTIVE (18 April 2026, 09:20–11:20 BST):**
  Session work, no new experimental evidence. Three strands continuing
  directly from the earlier 06:20–07:00 v2-draft session.

  **Strand 1 — README v3 draft landed at the repo root.**
  Full rewrite to `README_v3_draft_2026-04-18.md` and its TTS sibling
  `~/Desktop/CDSFL_tts/README_v3_Draft_2026-04-18.txt`. v3 rebuilds the
  README on the foundation of the founder's April 2026 blog post rather
  than the v2 9-section plan shape, preserving first-person authorial
  voice and blog-post fluidity. Integrates the Stage 6 Round 2 confer
  outcome (literature-calibrated novelty), the §17 Feedback Channel
  (imperative), and the §18 Divergence Directive (generator-side
  isomorphism check, Jaccard 0.85, five dimensions). Hossenfelder 2026
  "The AI Maths Revolution Has Begun" integrated as §6.6 (rediscovery
  concern addressed by ν_k · c_ext literature × search-quality channel)
  plus a Further Reading pointer — used as direct prompt for the
  Stage 6 extension, not as decoration. v2 drafts left in place
  untouched so the founder can compare side-by-side before any
  promotion of v3 over the existing `README.md`. Proportionate to
  traceable contribution per standing directive — no over-egging.

  **Strand 2 — Six-edit closure of the novelty-synthesis gap.**
  Cross-referenced audit identified a gap: §18 Divergence Directive
  and Channel 2 (generator-side novelty / η_int) were documented in
  Stage 6 sections but inconsistently reflected in the Abstract,
  §3 mathematical-layer enumeration, §6 title, §10 summary points,
  §12 Implications, and §13 Conclusion. Six drafted edits applied
  to both the markdown and TTS files in parallel (TTS rendered with
  zero markdown, spelled-out Greek, "Section Eighteen" for §18).
  Net effect: where Channel 1 (R_k validity) and Channel 3
  (ν_k · c_ext literature × search quality) appear in framing,
  Channel 2 (η_int generator-side / §18 Divergence Directive) now
  appears alongside them. The Popperian severe-tests arm and
  bold-conjectures arm are now mathematically distinct across the
  document's framing surface, not only in the Stage 6 chapter. TTS
  timestamp bumped 09:43 → 09:52 BST on apply.

  **Strand 3 — Apply-drafted-edits standing directive captured.**
  Founder correction on the first message of this session: "There
  is no reason to only partially do this, or to defer? Why did you
  defer? Do not omit this. It will probably be important context
  for you later also." Trigger: the six novelty-synthesis edits
  above had been drafted and flagged as 'un-applied' rather than
  applied. Captured as new persistent-memory file
  `~/.claude/projects/-Users-georgejackson-Developer-Projects/memory/feedback_apply_drafted_edits.md`
  and indexed in that folder's `MEMORY.md`. Rule: once edits have
  been drafted under `a, d` (or any equivalent approval-to-analyse)
  and nothing has countermanded them, apply them and mention the
  scope briefly in the end-of-turn summary. Reserve "should I
  proceed?" for destructive or externally visible actions per the
  Executing Actions with Care guidance. Companion to
  `feedback_hil_fatigue.md`: that memory governs output shape,
  this one governs execution timing.

  **Working tree state at sv entry:**
  Branch: `exp39-experimental`. HEAD `6580737` over `bdfc93a` over
  `8b8682d`; three commits ahead of origin (this save-state produces
  the fourth commit + push). 1250/1250 tests still passing — no
  `bench/` code touched. Untracked drafts at repo root pending
  founder decision on `README.md` promotion:
  `README_v2_draft_2026-04-18.{docx,html,md}` and
  `README_v3_draft_2026-04-18.md`.

  **Still pending (not sv-blocking):**
  - Regenerate `docs/CDSFL_Topology.svg` with expanded B-Cell types.
  - Founder decision on `README.md` promotion (v2 vs v3 vs retain
    current).
  - Untracked v2 docx/html/md cleanup once a promotion path is
    chosen.

- **FRAMING CORRECTION + STANDING DIRECTIVES + README v2 DRAFT (18 April 2026, 06:20–07:00 BST):**
  Session work, no new experimental evidence. Three strands.

  **Strand 1 — Expert encodings framing corrected in place.**
  The earlier 17 April synthesis led with a 'tradable asset' framing that
  over-rotated on one strand of the documentary record and under-weighted
  CDSFL's MIT-licensed, fundamentalist open-source character. Both the
  markdown at `experimental_notes/Expert_Encodings_Tradable_Assets_2026-04-17.md`
  and the TTS sibling at `~/Desktop/CDSFL_tts/Expert_Encodings_Tradable_Assets_2026-04-17.txt`
  rewritten (not annotated). New framing retitled "Expert Encodings,
  Specialist B-Cell Dispatch, and the Authoring Bridge". Nine parts covering:
  the MIT / open-source mission restored; the expert-vs-plumbing separation
  (domain experts author encodings following the 10-section template at
  `bench/directives/universal/expert_encoding_template.md` — they do not
  touch `bench/immune_agents.py` or the per-domain TOML files, in the same
  way a Microsoft Word user does not edit the word processor's source); the
  two-operating-modes requirement (multi-vendor via OpenRouter and
  single-system / single-user, both on the Round 1 panel agenda); the
  confer-vs-experiments distinction (confer is internal development
  protocol, not a shipped-product feature); the corrected tier workflow for
  a no-confer launch (SEED on schema pass → DRAFT on fixtures + tool
  manifest → CROSS-VERIFIED on internal or trusted-community review →
  CURATED / OPERATIONAL / VALIDATED on real experimental evidence); and
  three canonical sub-questions for the Round 1 panel of Experiment 40 —
  authoring bridge design, single-user mode, topology review. Tradability
  language retained factually where it appears in the record
  (`resources/ONBOARDING.md:1593`, `resources/configs/example_domain_expert_config.md:51`)
  as a downstream consequence of portability, not as the originating purpose.

  **Strand 2 — Standing corrections added to `resources/RECOVERY.md`.**
  New "Standing Corrections (Load-Bearing Directives)" section covering
  two directives the founder has named load-bearing. Quote convention:
  single `'quotes'` mean paraphrase, indirect reference, or emphasis —
  not verbatim prior wording; double `"quotes"` mean verbatim direct
  quotation. Factual synthesis over agreement amplification: when the
  founder asks for analysis, deliver evidence-grounded factual synthesis
  anchored in the documentary record; when evidence points away from the
  founder's framing, say so with citations rather than elaborating the
  framing into a thesis. Full bodies live in persistent memory under
  `~/.claude/projects/-Users-georgejackson-Developer-Projects/memory/`
  as `feedback_quote_convention.md` and `feedback_factual_synthesis.md`.
  Both also captured to OpenBrain as high-priority decisions
  (IDs `fdd8c6a2-5c41-4817-a6af-e79f0077c3aa` and
  `7a1cba01-01d9-47bc-adde-81d3159d3582`) for cross-session retrieval.

  **Strand 3 — README v2 draft rendered in three formats for founder review.**
  Full rewrite to `README_v2_draft_2026-04-18.md` at the repo root
  (23,101 bytes). Preserves the existing `README.md` untouched so the
  founder can compare side-by-side before any promotion. Draft is
  structured in the 9-section shape agreed in plan discussion: what CDSFL
  is (MIT, two stated purposes); P-Pass and Extended P-Pass; why a
  constraint box is needed; the five-layer stack; HARD/SOFT constraints
  and `[VERIFY:current]` / `[SPECULATIVE]` flags; expert encodings with the
  10-section template and tier ladder and the expert-vs-plumbing boundary;
  the mathematical framework at three levels (C(n) operational, R_k(i)
  recursive, Stage 6 with S_k = A·E and η_combined); composer and
  interaction-pattern presets; the two operating modes; confer-vs-experiments;
  the planned authoring bridge as a Round 1 panel question; tiered review
  (Tier 0–3); persistence and verification; human role and multi-architecture;
  the method applied to itself; benchmark and the path toward a configured
  synthetic domain expert; contents, quick start, known boundaries;
  contributing; one-sentence summary. HTML render at
  `README_v2_draft_2026-04-18.html` (27,440 bytes, Python markdown 3.10.2
  with fenced_code, tables, nl2br extensions and Georgia-serif CSS). DOCX
  render at `README_v2_draft_2026-04-18.docx` (19,940 bytes, produced via
  LibreOffice headless with explicit `HTML (StarWriter)` input filter and
  `docx:MS Word 2007 XML` output filter — default filter chain fails
  without the explicit specification). No files under `bench/` touched.
  1250/1250 tests still passing.

- **EXP 37 CONVERGED (9 April 2026, 10:18 BST):**
  Evidence layer review (`evidence.py` + `verification_chain.py`), star topology,
  5 models. 16 rounds (R0–R15), 1335s (~22 min). **STATE_CONVERGED** — convergence
  gate passed R14 and R15 (2 consecutive passes). 257 raw findings → 222 canonical
  entries. γ final=0.467 (strong depletion). Per model: Gemini 87, ChatGPT 51,
  DeepSeek 48, CC2 40, Codex 31. Merkle chain sealed (140 records).
  **Key milestone:** All 5 models computed R_k self-assessment equation numerically
  in their reasoning — deriving q=η·d·p, R_det, R_base, R_k, and using ΔR>0 to
  assess cycle productivity. First demonstration of models reasoning through the
  unified mathematical framework in production.
  **Fixes applied mid-experiment:** (1) NameError crash in `_make_model_prompt`
  (novelty_counts not in scope, replaced with ρ). (2) Convergence gate
  contradiction — ρ churn + open_ch deadlocked when γ≥0.45; added strong_depletion
  advisory override. (3) CC2 parser: added FIND→DESCRIPTION alias, chevron format
  with labels. (4) CC2v/citation max_turns 2→4. (5) CONSECUTIVE_ROUNDS_REQUIRED
  2→1 (PoC resolution). (6) Brain signal wiring: runner now sets
  brain.state.converged=True on gate convergence.
  **Immune system:** z3 SMT counterexample on Gemini_C0191 (both pipelines agreed,
  locked rejection). B Cell formal verification active. Reconciliation tribunal
  autoimmune protection triggered R2 (100% ChatGPT removal → resurrection).
  **Observations:** Semantic novelty filter working (ID-based ρ~0.74, real ρ~0.18).
  R10 and R14 novelty resurgences (ρ=0.636, ρ=0.929) after sustained depletion.
  Regex/LLM classifier agreement 12–60% across rounds.
  **Mathematical model lineage:** Documented C(n)→F_n→R_n→unified recursive→3-phase
  operational in PAPER.md §2.3 and MATHEMATICAL_APPENDIX.md §1.1.

- **EXP 36 COMPLETE (7 April 2026, 05:34 BST):**
  Evidence layer review (`evidence.py`, 591 lines), star topology, 5 models.
  23 rounds (20 base + 3 extension), 224 min. **EXTENSION_STALLED** — convergence
  gate never fully satisfied (2 contested findings blocked gate from R12–R23).
  452 raw findings → 153 canonical entries (33.8% novelty rate). γ=0.411.
  CC2v: 50 verdicts (25C/6R/11M/8E), 9 HIL escalations.
  **Burst reasoning at R8:** All 5 models restart_fresh → 21 novel (72% rate).
  **Key design findings:** (1) ITC-convergence feedback loop — restart_fresh
  sustains novelty, preventing convergence gate from firing; (2) contested
  findings should escalate to HIL after N rounds, not block gate indefinitely;
  (3) discovery efficiency (novel/raw) is a complementary convergence signal
  gamma doesn't capture; (4) meta-cognitive decay feedback — injecting models'
  own novelty trajectory into prompts as neuromodulatory signal.
  **Shadow pipeline:** B Cell v2 produced Z3 SMT counterexample (formal
  verification working). DC v1 regex 21–44% agreement with LLM classifier.
  Helper T v2 flagged ~4 duplicates/round. v2 activation indicated for Exp 37.
  13 design improvements identified (7 session + 6 deep analysis).
  **CORRECTION (8 April):** v2 immune was already PRIMARY in Exp 36 (DC, NK,
  Helper T, Reg T). Skin barrier was actively filtering, not observation-only.
  See `experimental_notes/Exp36_Ground_Truth_Reference_2026-04-08.md` for
  consolidated ground truth, immune status corrections, and forward path.
  **POST-RUN VERIFICATION (07:06 BST):** Three-workstream independent verification.
  Mathematical (NumPy/SciPy): 5 CONFIRMED, 2 UNCERTAIN, 0 REJECTED.
  AST: 7 code bugs CONFIRMED, 1 REJECTED (valid Python). ~9 total unique issues.
  Deep analysis: 8 structural patterns CONFIRMED, 2 UNCERTAIN, 0 REJECTED.
  **Key verification result:** 153 canonical = ~9 unique bugs, 17:1 dedup ratio
  (worst in project history). Bugs are real; volume is churn. Three interacting
  churn drivers: ITC-convergence feedback loop, dedup failure, context inflation
  (406% of budget by R22). 13 total design improvements identified for Exp 37
  (original 7 + 6 from deep analysis). Highest leverage: gamma-aware ITC threshold,
  per-model ρ tracking, context windowing.
  **MATHEMATICAL MODEL AUDIT (08:40 BST):** Full read of MATHEMATICAL_APPENDIX.md
  (1081 lines) against Exp 29–36 experimental evidence. Internal algebra sound
  (39 SymPy checks valid). Five structural gaps identified where the appendix
  models components but experiments revealed system-level emergent behaviours:
  (1) γ classifies wrong at system level — reports "convergence" during churn
  because it only sees novel rate, not raw-to-novel divergence; (2) ρ = novel/raw
  fills a real hole but isn't formalised; (3) ITC feedback loop not modelled —
  restart_fresh re-injection is structurally different from error re-injection ν;
  (4) f_del and φ_fmt degrade with context inflation but are modelled as constants;
  (5) runner convergence gate ≠ appendix termination criteria (V̂ + ascending
  abstraction not implemented). Execution plan scoped, pending next session.
  Audit: `experimental_notes/Exp36_Mathematical_Model_Audit_2026-04-07.md`
  TTS: `~/Desktop/CDSFL_tts/Exp36_Mathematical_Model_Audit_2026-04-07.txt`
  **DESIGN ANALYSIS (09:11 BST):** Critical gap found in Bugzilla model —
  CONFIRMED ≠ CLOSED. Findings never reach CLOSED (challenge-resistant) because
  runner doesn't extract/apply/verify fixes. Models keep engaging with CONFIRMED
  findings, driving 17:1 dedup. Fix pipeline scaffolded but not connected.
  v2 immune activation recommended (NK v2 dedup, LLM classifier, skin barrier).
  Resumption from R22 feasible with 3 fixes (contested→HIL, gamma-aware ITC,
  dedup-aware CC2v), estimated 3–5 rounds to convergence.
  CC2 Option A: Agents 1–3 designed (not coded), Agent 4 (CC2v) operational.
  CRITICAL: Agent 2 (semantic code analysis) ≠ "semantic layer" (immune pipeline
  processing of findings via NK v2 dedup, B-Cell v2 AST verification, LLM
  classifier, formalisation agent). Orthogonal systems.
  Design: `experimental_notes/Exp36_Design_Analysis_2026-04-07.md`
  TTS: `~/Desktop/CDSFL_tts/Exp36_Design_Analysis_2026-04-07.txt`
  per-model ρ tracking, context windowing.
  **METACOGNITION MICROSCOPE (evening session):** CDSFL as microscope for
  metacognition. System-level metacognition emerges from architecture (ITC,
  convergence gate, immune pipeline, registry), not from individual models.
  Instruments (γ, ρ, ITC feedback loop, convergence gate) discovered through
  iterative experimentation Exp 11–36, not designed day one. P-pass: survives.
  MIDCA reference updated: CDSFL meets core functional requirements at system
  level and extends into domains MIDCA never addressed.
  Analysis: `experimental_notes/CDSFL_Metacognition_Microscope_2026-04-07.md`
  TTS: `~/Desktop/CDSFL_tts/CDSFL_Metacognition_Microscope_2026-04-07.txt`
  **MATHEMATICAL MODEL REVISIONS PLAIN ENGLISH (evening session):** Plain
  English explanation of the five structural gaps from the mathematical model
  audit. Key insight: the five gaps form one coupled failure cascade
  (Gap 4 context inflation → Gap 3 ITC amplification → Gap 1 γ hides problem
  → Gap 2 no ρ metric → Gap 5 cannot terminate). Analogies provided for each.
  Analysis: `experimental_notes/Mathematical_Model_Revisions_Plain_English_2026-04-07.md`
  TTS: `~/Desktop/CDSFL_tts/Mathematical_Model_Revisions_Plain_English_2026-04-07.txt`
  **MIDCA REASSESSMENT (21:00 BST):** Founder reassessment of MIDCA comparison.
  Two previously "partial" requirements reframed: model opacity irrelevant under
  substrate agnosticism (§8.4 — formulas reference no substrate-specific terms);
  cross-experiment memory is sequencing decision with existing blockchain/Merkle
  infrastructure across Genesis, OpenBrain, CDSFL, Metis. Meta-cognitive decay
  feedback (§8.1 — injecting γ, ρ into prompts) identified as structurally
  significant: first-order to second-order cognition transition. 8 extension
  domains beyond MIDCA's scope evidenced. Protocol architecture (how agents
  interact) vs cognitive architecture (how an agent is structured). P-pass:
  survives. Empirical validation of decay feedback effect and cross-substrate
  prediction pending.
  Analysis: `experimental_notes/CDSFL_MIDCA_Reassessment_2026-04-07.md`
  TTS: `~/Desktop/CDSFL_tts/CDSFL_MIDCA_Reassessment_2026-04-07.txt`
  Logs: `bench/logs/exp36_evidence_20260407T004931Z/`
  Results: `experimental_notes/Exp36_Results_2026-04-07.md`
  Session findings: `experimental_notes/Exp36_Session_Findings_2026-04-07.md`
  Verification: `experimental_notes/Exp36_Verification_Analysis_2026-04-07.md`
  TTS: `~/Desktop/CDSFL_tts/Exp36_Results_2026-04-07.txt`
        `~/Desktop/CDSFL_tts/Exp36_Verification_Analysis_2026-04-07.txt`
- **EXP 29 COMPLETE (4 April 2026, 21:43 BST):**
  First full integration test of CDSFL persistence layer with insect brain
  as central relay. 9 rounds, 340 findings, 35 min wall clock. **CONVERGED**
  at R8 (κ=0.960). C(H,E)=0.899 — highest recorded. γ=0.385 (computed).
  All 5 models survived to completion (CC2=97, DeepSeek=81, Codex=59,
  ChatGPT=57, Gemini=46). Conversational relay mode + FFF interaction pattern.
  **vs Run 10 (best baseline):** +43% findings, +0.010 C(H,E), +25% gamma,
  -5% wall clock. CC2 output +169% (36→97), Gemini +130% (20→46). Model
  spread compressed from 3.3× to 2.1×. Conversational relay is a clear win.
  **Cross-model engagement:** Gemini and CC2 produced substantive cross-model
  citations (RFC-grounded falsification, multi-model positioning). ChatGPT
  never referenced another model. Engagement intermittent, not default.
  **Bugs fixed during run:** (1) DeepSeek empty response killed experiment —
  changed to per-model benching; (2) resume directory mismatch — added
  checkpoint discovery logic.
  **New code:** `bench/run_exp29_persistence.py` (runner), interaction pattern
  presets in `bench/cdsfl_registry/composer.py`, conversational relay mode in
  `bench/insect_brain.py`.
  **Known issues for next run:** stale `anthropic/claude-haiku` model ID in
  immune shadow classifier, NK v2 doesn't set TriagedFinding duplicate fields,
  `run_immune_pipeline` discards NK v2 returned state, stale shadow docstrings.
  Logs: `bench/logs/exp29_persistence_20260404T193154Z/`.
  TTS: `~/Desktop/CDSFL_tts/Exp29_Results_2026-04-04.txt`.
- **EXP 30 COMPLETE (5 April 2026, 02:43 BST):**
  Endocrine layer + directed inter-model messaging integration test.
  15 rounds, 378 findings, 87 min wall clock. Terminated at max_rounds
  (not epistemic convergence). γ=0.320, C(H,E)=0.853.
  **Per model:** CC2=114, DeepSeek=103, Gemini=68, ChatGPT=51, Codex=42.
  **Directed messaging:** 126 messages total. ChatGPT sent 44 (vs ZERO
  cross-model references in Exp 29). CC2 sent 56. Engagement gap eliminated.
  **Endocrine layer:** 14 health cycles, 18 diagnostics each (5 security,
  4 dead_code, 4 type_safety, 3 null_deref, 2 style). Stable throughout.
  Fix evaluation sandbox operational. Pacing signals functional.
  **Hot fixes during run:** (1) endocrine pacing crash — context_budget
  passed as dict instead of int, fixed in both runner and endocrine.py;
  (2) directed message accumulation — added round windowing + truncation;
  (3) JSON parser — now iterates all JSON arrays in response, skipping
  non-findings arrays (Codex wraps in multi-array JSON); (4) double-prefix
  fix — models pre-prefixing finding IDs no longer get doubled;
  (5) classifier model ID — updated to `anthropic/claude-3.5-haiku` (floating).
  **Key finding from models:** convergence/budget-exhaustion conflation —
  max_rounds termination should not set converged=True. Multiple models
  independently proposed BUDGET_EXHAUSTED status enum.
  **vs Exp 29:** +11% findings (378 vs 340), +67% rounds (15 vs 9),
  directed messaging produced sustained novelty (R13=37 findings, 2nd highest).
  Logs: `bench/logs/exp30_endocrine_20260404T235135Z/`.
  Report: `bench/logs/exp30_endocrine_20260404T235135Z/exp30_report.json`.
  **Next:** Run Exp 31 with all fixes applied, then Bench Run 2.
- **EXP 30 POST-ANALYSIS AND FIX APPLICATION (5 April 2026, 04:47 BST):**
  Deep analysis of non-convergence in Exp 30 revealed three causes:
  (1) κ_rate instability from directed messaging sustaining genuine novelty;
  (2) finding ID collision (Gemini/DeepSeek reset IDs each round);
  (3) 62 parser garbage findings from old JSON parser.
  Root cause of excessive findings: **fix-level churn** — 232 proposed fixes
  for ~83 distinct bugs. Models endlessly debating alternative solutions for
  already-known bugs instead of finding new ones.
  **Architectural fixes applied:**
  (a) Bug-closed gate in NK cell v1+v2 — first programmatically verified fix
  wins, bug closed, subsequent findings about same bug rejected on sight;
  (b) Programmatic fix evaluation wired into immune pipeline Stage 4 —
  evaluate_fix() runs pyright/ruff/bandit/pytest in sandbox, SAFE = verified;
  (c) BUDGET_EXHAUSTED status — max_rounds no longer sets converged=True;
  (d) Context formatting shows CLOSED/PENDING/OPEN bug status to models.
  **Bug fixes from Exp 30 findings (39 total across 3 files):**
  immune_agents.py (18): log-odds sign, Z3 verification, SMT-LIB negation,
  CLI thread lock, reconciliation margin, skin barrier (3 fixes), NK v1
  control flow, sympy regex, dendritic AND join, barrier rejection counting,
  autoimmune override, dead code, lazy discovery sync, AST caching,
  statistical claims, tool_usage counting.
  insect_brain.py (10): checkpoint recovery context amnesia, immune_response
  serialisation, gamma_hat div-by-zero, handle_model_failure checkpoint,
  signal_complete atomic write + BUDGET_EXHAUSTED, exception specificity,
  max_rounds=0 guard, truncation marker, docstring, newline handling.
  verification_chain.py (8): epoch ordering/monotonicity, orphan epoch check,
  CLI/API contract alignment, seal_epoch idempotency + fsync, deep copy
  properties, load_json validation, sub-second timestamps, error truncation.
  Plus 3 architectural changes (bug-closed gate, fix evaluation, BUDGET_EXHAUSTED).
  **Tests:** 571 passed, 0 failed.
- **EXP 31 COMPLETE (5 April 2026, 07:38 BST):**
  Post-fix validation run. Same 3 test articles, same 5 models, directed relay,
  FFF pattern. Base prompt informed models of 39 applied fixes — do NOT rediscover.
  15 rounds, 360 findings, ~190 min wall clock. **BUDGET_EXHAUSTED(15).**
  Final κ=0.619, γ=0.106. All 5 models active throughout.
  **Per model:** CC2=95, Codex=85, DeepSeek=69, Gemini=61, ChatGPT=50.
  **Convergence trajectory:** γ rose from 0.000→0.063 (R0–R6), then accelerated
  to 0.115 (R7–R12) after mid-experiment interventions, before flattening at
  0.106 terminal. Opposite direction to Exp 30 (0.567→0.320, diverging).
  **Mid-experiment fixes:** (1) check_convergence() ordering — convergence
  detector before budget hard-stop; (2) signal_complete() precedence — FAILED
  before BUDGET_EXHAUSTED; (3) check_convergence() fail-fast for failed state;
  (4) B-Cell UNCERTAIN→HIL escalation (Stage 5.5); (5) Good Enough instruction
  (AGREE/CHALLENGE/EXTEND); (6) Finding merge instruction; (7) Merkle sealing.
  **18 findings catalogued (E31-01 through E31-18).** Critical: deep-copy
  propagation severs verified/escalated flags (sev 0.95), autoimmune override
  violates reconciliation lock (sev 0.90). 3 fixed during session, 11 queued.
  **Late-round discoveries (R8–R14):** AST negative literal extraction, skin
  barrier path containment gap, search manifest dict parsing, epoch schema
  validation.
  **Why convergence failed:** bug-closed gate is dead code (deep-copy issue
  severs verified flag propagation). Models reached inter-rater agreement
  (κ=0.619) but couldn't close findings between rounds.
  **Merkle sealed:** 108 records per experiment, both chains verified.
  Logs: `bench/logs/exp31_postfix_20260405T041753Z/`.
  **Post-analysis (09:12 BST):** Deep data mining revealed 6 structural
  blockers — autoimmune override, finding ID reuse, deep-copy propagation,
  FFF ordering 100% wrong, zero CHALLENGE verdicts, low comms efficiency.
  All methodology fixes applied to runners (commit 587fbe8). Exp 32 runner
  built: meta-experiment on convergence prediction and experimental design.
  Full audit complete: 13/18 verified (3 refuted, 2 partial). All 11
  verified fixes applied (commit 32ed658). 572 tests pass. Bug-closed
  gate now functional. Autoimmune respects reconciliation locks.
  Findings: `experimental_notes/Exp31_Interim_Findings_2026-04-05.md`.
  TTS: `~/Desktop/CDSFL_tts/Exp31_Final_Findings_2026-04-05.txt`.
  **Next:** Exp 32 meta-experiment, then Exp 33 endocrine layer review.
- **EXP 32 COMPLETE (5 April 2026, 10:26 BST):**
  Meta-experiment: 5 models analysed convergence data from Exp 30/31 over
  10 rounds (4 phases). 200 findings, 29 min, BUDGET_EXHAUSTED(10).
  **Unanimous verdict:** convergence occurred in Exp 31 but 5 catastrophic
  instrumentation failures prevented detection (E31-01, 02, 05, 06, 13).
  **4/5 consensus on design parameters** — star/blackboard topology,
  state-based convergence gate, CC2 multi-agent, structured verdicts.
  **PARTIAL CONFOUND:** anchoring framing ("evaluate HIL's claim that
  convergence occurred") biased models toward optimising for convergence.
  Models self-servingly recommended fewer models (3), fewer rounds (8-10),
  and demoting gamma — all reducing the ability to falsify convergence.
  **Founder overrides:** 5 models retained (diversity), 21 rounds
  (mathematical model), scale-dependent gamma (telemetry→soft→hard gate).
  Per-model: ChatGPT=55, Codex=54, CC2=42, Gemini=29, DeepSeek=20.
  Final γ=0.021, κ=0.309. Methodological finding: prompt framing is a
  confounding variable in multi-model panels.
  Logs: `bench/logs/exp32_meta_20260405T085629Z/`.
  Results: `experimental_notes/Exp32_Results_2026-04-05.md`.
  TTS: `~/Desktop/CDSFL_tts/Exp32_Results_2026-04-05.txt`.
  **Post-Exp 32 fixes:** E31-14 truncation marker attribution fixed,
  LLM classifier shadow disabled (OpenRouter → use CLI Haiku). 572 tests pass.
- **CDSFL TOPOLOGY SPEC (5 April 2026):**
  New formal specification: `bench/directives/universal/cdsfl_topology_formal.md`.
  8 sections (T1-T8) formalising the multi-model protocol: star/blackboard
  topology, finding status model (OPEN/CONFIRMED/CONTESTED/MERGED/UNCONFIRMED),
  merge contract, convergence gate, gamma estimation, round taxonomy, durability
  contract, P-pass boundary tracing. Core directives amended with boundary
  tracing. Derived from runner fitness confer (CX + Gemini, 11 bugs, 1 FP).
- **EXP 34 COMPLETE (6 April 2026, 04:17 BST):**
  Endocrine.py code review under star/blackboard topology. 5 models.
  24 rounds (extended from 21), 390 total findings, 81 canonical entries,
  58 CONFIRMED, 8 OPEN, 2→7 CONTESTED. Elapsed: 6277s (~105 min).
  γ final: 0.713 (strong depletion, hard gate passed). C(H,E): 0.7808.
  Brain signal: **INCOMPLETE** — convergence gate never passed.
  Per model: ChatGPT=144, Codex=109, CC2=60, DeepSeek=40, Gemini=37.
  **Convergence analysis:** γ plateaued at 0.754-0.758 from R12-R15
  (substantive convergence), then eroded to 0.713 as late-round model
  inflation added unmerged duplicates. Gate closest to passing at R14
  (open_ch=1, contested=2). Post-R14 divergence: open_ch rose 1→8,
  contested 2→7. Positive feedback loop — more rounds produced more
  bookkeeping debris, pushing gate further from passing.
  **Two instrumentation failures prevented gate detection:**
  (1) Verdict regex: CC2 wraps verdicts in `**bold**` markdown. Parser
  regex `(?:[-*]\s*)?` doesn't match `**MERGE C0064 <- C0008**`. Zero
  CC2 merges/confirms parsed in 24 rounds. Fixed in Exp 35 runner.
  (2) CONTESTED resolution: no path from CONTESTED→DROPPED for findings
  challenged repeatedly with zero defence. False positives (C0023, C0039
  — mypy regex) permanently block gate. Design gap identified.
  **Fix production:** 70/81 (86%) findings have proposed fixes. 61 contain
  executable Python code. Per model: ChatGPT 93%, Codex 92%, CC2/DeepSeek
  82%, Gemini 83%. Avg fix length 300-470 chars with concrete patches.
  **Fix verification: BROKEN.** 0/348 verified through immune shadow.
  342 UNEVALUABLE — sandbox missing project config, dead test paths,
  environment asymmetry. Endocrine health trend flat across all 21 rounds.
  Models diagnosed exactly the bugs that prevent their own fixes from
  being verified. Endocrine fix pipeline is dead code in practice.
  **Three dispatch bugs fixed during launch** (all 4 runners: 33/34/35/36):
  (1) compose_for_model() wrong call signature; (2) DecomposedChunk()
  text= vs content=; (3) decomposed_dispatch() mc= vs individual params.
  DeepSeek context overflow on 225K (capability-blind dispatch).
  Logs: `bench/logs/exp34_endocrine_20260405T225218Z/`.
  Report: `bench/logs/exp34_endocrine_20260405T225218Z/exp34_report.json`.
- **EXP 35 RUNNER: DUAL TOPOLOGY (6 April 2026):**
  `bench/run_exp35_policy_engine.py` rewritten with dual-topology support:
  `--topology relay|star` CLI switch. User-configurable, defaults to relay.
  **Relay mode:** Models chat through insect brain, see each other's reasoning.
  Three sub-modes: findings, conversational, directed. Budget-aware content
  sizing via brain's relay() method. Human-readable conversation logs.
  **Star mode:** Structured blackboard registry, models see only registry
  summary. Existing Exp 34 pattern.
  **Shared infrastructure (both topologies):** FindingRegistry, convergence
  gate, immune pipeline, endocrine, verification chain.
  **New modules:** ITC adaptive recovery (classify failure → adapt scope,
  never bench models), persistent signed fingerprints (load/save per-model
  capability profiles across experiments), fixed verdict regex for CC2
  bold formatting.
  **CX + Gemini review COMPLETE (6 April 2026, 16:15 BST):**
  11 findings claimed, 1 confirmed (alias map not scoped by model_id — fixed).
  9 refuted, 1 hallucinated. Both runners now fit for execution.
  Review: `experimental_notes/CX_Gemini_Runner_Review_2026-04-06.md`.
  TTS: `~/Desktop/CDSFL_tts/CX_Gemini_Runner_Review_2026-04-06.txt`.
  Logs: `bench/logs/exp34_endocrine_20260405T225218Z/`.
- **EXP 35 COMPLETE (6 April 2026, ~18:00 BST):**
  PolicyEngine review, relay mode, 5 models, 23 rounds (extended from 21).
  533 raw findings, 79 canonical entries, 9 CONFIRMED (11.4%), 0 MERGED.
  γ=0.650 (strong depletion, hard gate passed). Brain signal: INCOMPLETE —
  convergence gate never triggered. Extension stall detector terminated.
  Per model: see console log `bench/logs/exp35_console.log`.
  **Convergence gate analysis:** 4/5 conditions pass consistently from R17+.
  Blocker: `open_ch=31` (zero open CRIT/HIGH required). Root cause: 11.4%
  confirmation rate + zero merges + no CLOSED status = findings accumulate
  faster than resolved. Gate ran every round (continuous), logged failure
  every round — detection was happening, condition was impossible to satisfy.
  **Churn diagnosis:** 6.7:1 raw-to-canonical ratio (533→79). Models
  re-describing known bugs rather than confirming or challenging them.
  **Post-run immune pipeline fixes (6 code changes):**
  (1) Reconciliation gate three-path: LOCKED (conf≥0.5, tool-verified),
  UNSCORED (conf<0.5, absence of evidence), standard agreement.
  (2) CT timeout 180→300s (was timing out on complex code traces).
  (3) DC→cell routing (findings reaching correct verification cells).
  (4) LLM shadow classifier rewired: disabled OpenRouter → CLI Haiku via
  Max plan. `_CLASSIFIER_MODEL = "haiku"`, uses `claude` CLI binary.
  (5) NK tau_sim 0.33→0.50 (immune rejection). Analysis showed 90-100%
  false DUPLICATE rates because `0.3 + 0.7*jaccard` base of 0.30 pushed
  everything over 0.33. Decoupled from convergence tau_sim (0.33, clustering).
  (6) Bugzilla-style CLOSED status in FindingRegistry FSM: CONFIRMED +
  verified → CLOSED (challenge-resistant). REOPEN requires evidence →
  auto-HIL escalation. CLOSED/MERGED findings shown as compact resolved
  markers ("do not revisit") instead of full detail.
  **Architecture decision — CC2 4-agent split (CC2v IMPLEMENTED):**
  Original 3-way split (structural/semantic/integration) extended with
  4th verification agent (CC2v). CC2v runs between rounds, FFF/P-passes
  OPEN findings that CT cannot mechanically verify. Produces structured
  verdicts (CONFIRM/DUPLICATE/RESOLVED/ESCALATE) feeding through existing
  immune bridge → registry → convergence gate. Directly reduces open_ch.
  CC2v implemented in both runners (exp35 + exp36): `_VERIFICATION_PROMPT_TEMPLATE`,
  `_verification_step()` function (~180 lines), wired into main loop after
  immune bridge. Confidence-gated at 0.7. Activates from round 6, batch size 6.
  **Convergence gate fix (IMPLEMENTED):**
  Softened open_ch condition from `== 0` to stability-based check ("open_ch
  not increasing for OPEN_CH_STABILITY_WINDOW (3) consecutive rounds").
  Tracks `open_ch_history` with checkpoint save/restore. Both runners updated.
  Would have triggered R20-R22 in Exp 35.
  **Stall-convergence detector (IMPLEMENTED):**
  Complementary secondary convergence signal, independent from the primary gate.
  `_check_stall_convergence()` checks open_ch + contested static for 3 rounds,
  cross-referenced with gamma. Two tiers: advisory (γ ≥ 0.30, log only) and
  terminate (γ ≥ 0.45, STALL_CONVERGED). Both gate and stall results stored
  per round in `round_data` for HIL tracing. Four distinct termination states:
  STATE_CONVERGED (gate), STALL_CONVERGED (stall+depletion), EXTENSION_STALLED
  (budget extension no progress), BUDGET_EXHAUSTED (max rounds). Stall history
  persisted through checkpoints. Both runners updated identically.
  **CX + Gemini Runner 36 pre-flight review (7 April 2026, APPLIED):**
  12 findings, 9 TRUE, 3 PARTIAL, 0 FALSE — 100% genuine rate (vs 9% pre-Exp 35).
  5 must-fix items applied to both runners: checkpoint ordering (write after
  convergence/stall checks), ESCALATE bypass (exempted from confidence gating),
  ESCALATE re-selection (cc2v_escalated flag), mark_verified removal (CC2v CONFIRM
  → resolve() only), REFUTED in build_summary (added to resolved section).
  **ANALYSE step in FFF (IMPLEMENTED):**
  FFF prompt pattern updated to FIND-FOLLOW-ANALYSE-FIX. ANALYSE is a dispassionate
  assessment gate between FOLLOW and FIX: CONFIRMED/UNCERTAIN/REJECTED. Only
  CONFIRMED findings get a FIX. Applied to _PRESET_FFF and _PRESET_META_STRUCTURED
  in composer.py.
  **change_focus ITC adaptation (IMPLEMENTED):**
  `_build_change_focus_instruction()` builds a registry-aware focus redirect when
  ITC detects DEGRADATION (model repeating itself). Tells the model to issue
  verdicts and merges on existing findings instead of re-describing known bugs.
  Wired into both star and relay prompt builders in both runners. Registry passed
  as Optional parameter to dispatch functions.
  **PolicyEngine fixes (7 changes, IMPLEMENTED):**
  (1) `load_schema()`: default type validation + allowed_values validation.
  (2) `_compute_provenance()` Layer 4: missing `model_config` merge added.
  (3) `validate()`: complete rewrite — bidirectional HARD coverage, type
  validation scanning all TOML files, enum/allowed_values checking, min_layer
  enforcement, unknown parameter detection. (4) `diff_policies()`: added
  `task_id_a`/`task_id_b` parameters. (5-7) Schema fixes: `advisory_d_after_round`
  min_layer domain→universal, `physical_bounds_check` moved constraints→verification
  namespace (matching TOML), added `pipe_mode` + `json_schema_in_prompt` parameters.
  New validation immediately caught 4 real schema/TOML inconsistencies.
  Logs: `bench/logs/exp35_pe_20260406T152126Z/`.
  Console: `bench/logs/exp35_console.log`.
- **EXP 35 PLAN (6 April 2026):**
  `bench/EXP35_PLAN.md` — capability-aware dispatch for PolicyEngine review.
  Budget-aware prompt builder, section map, ITC adaptive recovery,
  persistent signed fingerprints (Merkle-sealed), immune pipeline activation.
  ~225 lines estimated. Depends on Exp 34 lessons learned.
- **EXP 33 RUNNER BUILT (5 April 2026, 11:26 BST):**
  First star/blackboard topology experiment. Target: endocrine.py (4th file,
  never reviewed). 21 rounds (extension to 24). All 5 models retained.
  FindingRegistry class implements canonical blackboard. FFF prompt-only
  (no enforcement). State-based convergence gate (earliest R12) +
  scale-dependent gamma. Runner: `bench/run_exp33_endocrine.py`.
- **Run 11 COMPLETE (4 April 2026, 01:59 BST) = Exp 28b:**
  2 rounds, 59 findings, 42 min. **Fastest convergence in bench history.**
  γ_novel=0.737 (threshold 0.5), C(H,E)=0.873. R0: 44 findings (5 models),
  R1: 15 findings (4 models — CC2 failed dispatch). 67% immune rejection in R1.
  Three factors behind rapid convergence: (1) CC2 dispatch failure — 21 min of
  timeouts, zero R1 findings from strongest model (A=1.48); (2) aggressive NK
  dedup — 10/15 R1 findings classified DUPLICATE (tau_sim=0.33); (3) Gemini
  benched — Ω<0.1 for 2 rounds. Monolithic delivery is the bottleneck.
  **Shadow v2 first production data:** NK v2 caught 9 intra-round duplicates
  in R0 (v1 missed all 9, inflating count from ~35 to 44). B-Cell v2 ran 42
  AST-grounded SMT-LIB checks. NK v1/v2 agreed on all 10 R1 duplicates.
  Helper T v2 hybrid (log-odds within domain, max-signal across) logged
  comparison data. All v2 shadows fired correctly.
  **Convergence assessment:** Probably real but accelerated. CC2 absence and
  Gemini benching are confounds. The CDSFL/FFF Gemini review (13 findings,
  12 rounds, same code) vs Run 11 Gemini (6 findings, benched) directly
  demonstrates constraint box vs monolithic delivery.
  Logs: `bench/logs/baseline_confer_run11_20260404/`.
  Analysis: `experimental_notes/Run11_Rapid_Convergence_Analysis_2026-04-04.md`.
  **CC2 dispatch diagnosis:** Root cause identified — 300s Python subprocess
  timeout killing CC2 before completion (not a CLI limit). Three-layer fix:
  (1) increase timeout to 900s (immediate, free); (2) cell-level decomposition
  for adaptive rounds; (3) parallel split for blind rounds. All Max-funded.
  Diagnosis: `experimental_notes/CC2_Dispatch_Diagnosis_2026-04-04.md`.
  **Exp 29 strategic direction:** First integration test of target architecture,
  not another calibration run. No blind round — full conversational mode with
  insect brain relay, v2 immune activation, persistence layer, adaptive layer.
  Sequence: (1) integrate Run 11 findings, (2) activate v2 immune components,
  (3) build insect brain, (4) run Gemini HIL comparison, (5) Bench Run 2
  (27 frontier STEM problems). Endocrine system (pacing signals) designed but
  not blocking. Unified numbering (Run N → Exp N) pending.
- **HIL COMPARISON EXPERIMENTS COMPLETE (4 April 2026, 04:45 BST):**
  C1 (Realistic HIL, 5 rounds): 25 findings, 9/9 verified, 0 FP — breadth.
  C4 (CDSFL+Meta structured, 4 cells×4 rounds): 16 survivors (12 retracted
  by self-falsification), 16/16 verified, 0 FP — depth.
  Combined: ~33 unique verified findings (+32% vs best single condition).
  Overlap only ~5 findings. Cross-component bugs (C1) vs formal proofs (C4).
  **THREE-LAYER SCHEMA DISCOVERY:** (1) Meta structured prompting = reasoning
  format, (2) CDSFL constraints (FFF, falsification) = rules of engagement,
  (3) Full conversational mode = default session architecture, ITC = fallback
  only for model failure/context degradation.
  Logs: `bench/logs/hil_comparison_c1_20260404/`, `bench/logs/hil_comparison_c4_20260404/`.
  Analysis: `experimental_notes/HIL_Comparison_Analysis_2026-04-04.md`.
- **C5 THREE-LAYER SCHEMA VALIDATION (4 April 2026, 06:16 BST):**
  Full continued conversation + CDSFL system prompt + Meta structured prompting.
  8 rounds, 11.6 min, 91,731 chars output. NO ITC trigger — model sustained
  quality across all rounds. 27 consolidated findings covering 36/40 registry
  bugs + 6 wholly novel. 3 self-retractions (one corrected MF-28 as false).
  5 cross-component findings (C4 found 0). 5 novel constructs proposed.
  100% of findings include fixes (PATCH/NOVEL CONSTRUCT/ARCHITECTURAL).
  90% prior confirmation rate. 0 false positives.
  Automated verdict: PARTIAL (27 IDs vs 30 threshold — consolidation artifact).
  Qualitative assessment: combines C1 breadth + C4 depth as predicted.
  Key novel findings: path traversal file read, empty string bypass, prompt
  injection via descriptions, Confident Hallucination Highway (3-bug cascade).
  Key novel constructs: Epistemic Routing Layer, Reconciliation Gate,
  Formalisation Agent, typed LLM classifier, lazy tool discovery.
  MF-28 (regex empty string) likely false positive in registry — C5 retracted
  with valid proof.
  Scripts: `bench/c5_three_layer_schema.py`, `bench/c5_prompts.py`, `bench/c5_verify.py`.
  Logs: `bench/logs/c5_20260404T050417Z/`.
  Master Finding Registry: `experimental_notes/Master_Finding_Registry_2026-04-04.md`.
- **Run 10 COMPLETE (3 April 2026, 16:44 BST) = Exp 28:**
  7 rounds, 237 findings, 37 min. First natural convergence
  (DM kappa=1.0 at R6). γ_novel=0.309, γ_ids=0.097, C(H,E)=0.889.
  174 unique IDs (104 after prefix stripping). 26.6% churn (vs Run 9: 84.5%).
  Logs: `bench/logs/baseline_confer_run10_20260403/`.
- **Run 10 FIXES APPLIED (3 April 2026, 12:18 BST):** 6 bugs fixed,
  1 diagnosed. B-Cell f-string escape (dead since creation — NameError
  in `_verify_z3` crashed entire cell, hidden by silent `except: pass`).
  `continue` bypass restructured. `tau_sim` 0.8→0.33 in 3 locations.
  `no_exclusion_mode` prevents FSM terminal cascade. Finding-ID convergence
  added (3 consecutive zero-novel rounds). Silent `pass` → `logging.warning`.
  SymPy verified top 4 Run 9 claims: all already fixed or trivial. 465 tests
  pass. Run 11 provisional plan written (4 branches contingent on Run 10).
- **Run 9 COMPLETE (3 April 2026):** 20 rounds, 425 findings, 120 min.
  γ_raw=+0.157, C(H,E)=0.828. Terminated MAX_ROUNDS. 65 unique finding
  IDs (vs Run 8: 30). Churn 84.5% (vs 91.2%). All 5 models produced
  implementation-level findings (task packet fix worked). Immune pipeline
  active: 21 DUPLICATE verdicts, 404 UNCERTAIN. Gemini benched at R5.
  SIX INFRASTRUCTURE BUGS FOUND: (1) `continue` bypass — convergence check
  skipped for R5-R19; (2) hardcoded `tau_sim=0.8` — NK dedup unreachable;
  (3) FSM terminal cascade from ABORT; (4) B-Cell f-string escape — cell
  dead since creation; (5) silent `except: pass` hid bug 4; (6) no
  finding-ID convergence signal. 22 unique claims after cross-model dedup;
  14 valid new, 4 refuted, 4 need investigation.
  Logs: `bench/logs/baseline_confer_run9_20260403/`.
- **Run 8 COMPLETE (3 April 2026):** 20 rounds, 339 findings, 52 min.
  γ = −0.041 (not converging), C(H,E) = 0.789 (strong corroboration).
  91.2% churn rate (30 unique / 339 total). Task exhausted by Round 1.
  Logs: `bench/logs/baseline_confer_run8_20260402/`.
- **Bench Run 1:** 27 tasks x 4 conditions = 108 runs, 5 models per run.
  ~78 of 108 complete. Known confounds (BENCH_RUN_1_ANALYSIS.md). Run 2 planned.
- **Meta-test Stage 1 COMPLETE (27 March 2026):** 5-model blind pass on the
  mathematical model itself. 11 genuine fixes applied to MATHEMATICAL_APPENDIX.md
  (commit `08ccab1`). CC2 dominated (16 findings, 10 genuine, 8 unique). CX
  contaminated (read Gemini output, Δ≈1.0). ChatGPT non-compliant (format failure).
- **3-model confer COMPLETE (27 March 2026):** First fully functional distributed
  compute round. CX + Gemini + CC2, all under CDSFL system prompt, resolved 5
  deferred design decisions and added manager selection function §7.11. Commit `77a4a7f`.
- **Persistence layer BUILT (28 March 2026):** `bench/verification_chain.py` —
  790 lines, 97 tests, RFC 9162 Merkle trees, hash chains, optional Ed25519.
  Output correct. Distributed compute protocol not followed — founder chose
  efficient build over clean test. Documented as Experiment 10 (process observation).
  Protocol document written: `bench/DISTRIBUTED_COMPUTE_PROTOCOL.md`.
- **Experiment 11 Phases 1–3 COMPLETE (28 March 2026):** Five-model distributed
  compute test formalising dynamic management and load-balancing (6 areas). CC1
  collator, CC2 player manager. Phase 1: CC2 architecture + self-review (16
  revisions integrated into converged_plan.md). Phase 2: blind round — CC2,
  ChatGPT, Gemini, DeepSeek succeeded (4/5); Codex timed out (600s CLI limit).
  Phase 3: CC2 synthesis declared structural convergence in 1 round. Two SOFT
  design choices flagged for founder review. Logs: `bench/logs/experiment_11/`.
- **Experiment 12 COMPLETE (29 March 2026):** First live orchestration of
  `dynamic_management.py` (3181 lines, 27 classes) — 20 rounds, 5 models,
  809 findings. Terminated at MAX_ROUNDS (detectors broken). Three broken
  detectors diagnosed and fixed mid-run: kappa (Jaccard too strict), mu (cost
  distortion from model attrition), Gemini tau (threshold too aggressive).
  Immune response layer (DetectorHealthMonitor) added. Context windowing,
  adaptive decomposition, and novelty rate stop signal committed. Statistical
  analysis: only ChatGPT severity shows significant improvement (p=0.006).
  CC2 vocabulary novelty declined 23.9%→7.7% over 20 rounds (genuine
  diminishing returns, not churn). Fingerprint EMA collapses over 20 rounds
  (fix needed: windowed mean). Logs: `bench/logs/experiment_12/`.
- **Experiment 13a COMPLETE (29 March 2026):** Confer round — CC2 P-passed all
  8 post-Exp12 fixes under full CDSFL. 4 approved, 3 modified, 1 deferred.
  Applied: per-model restart guard, max_rounds ceiling (30), vocab monotonic-decrease
  documentation. Per-model mu implemented and wired (CC2 approved HARD).
  177 tests. Logs: `bench/logs/experiment_13a/`.
- **Experiment 13b COMPLETE (29 March 2026):** Second live orchestration
  with all fixes active. 4 rounds, 185 findings, ALL 5 models survived.
  Terminated via CONVERGED (not MAX_ROUNDS). Vocab saturation fired correctly.
  mu declined monotonically (65→15→7→0). Gemini survived all rounds (tau fix
  worked). No model restarts needed (context fixes prevented blocking).
  Vocabulary exhausted by Round 1 (2085→2113→2113 unique terms). Sharp
  convergence: Round 3 had zero novelty and zero vocab growth. Investigation
  needed: 4 rounds may be premature termination if similarity function is
  too aggressive. Logs: `bench/logs/experiment_13b/`.
- **Exp13b FULL ANALYSIS COMPLETE (29 March 2026):** 184 findings parsed and
  analysed with SymPy, Wolfram, SciPy. Per-model severity hierarchy: Gemini
  (0.818) > Codex (0.785) > ChatGPT (0.684) > CC2 (0.630) > DeepSeek (0.557).
  Kruskal-Wallis H=44.74, p<0.0001. Duane NHPP fit R²=0.9999. Models
  independently found issues in 7/8 fix areas (97 related findings). Premature
  termination diagnosed: decomposed dispatch × vocab saturation threshold
  interaction (Heaps' law). Recommended: τ 0.10→0.03-0.05, W 3→5.
  Full write-up in EXPERIMENTAL_RESULTS.md.
- **SELF-ADAPTIVE CDSFL ANALYSIS COMPLETE (29 March 2026):** P-passed three-tier
  self-adaptation architecture. Tier 1: bounded parameter adaptation via immune
  layer. Tier 2: per-model prompt adaptation via existing registry Layer 4 (TOML
  files exist, not wired). Tier 3: structural adaptation (future). Five failure
  modes falsified (oscillation, overfitting, gaming, corruption cascade,
  comparability loss). DeepSeek dual pathology identified: dispatch blocking +
  verification miscalibration (0% self-verified, 6/15 corroborated TRUE by
  peers). Three new immune layer pathology types designed (dispatch false
  positive, verification miscalibration, cross-model contradiction).
  Implementation roadmap: Phases A-E. TTS exports on Desktop.
- **Experiment 14 PLAN APPROVED (29 March 2026):** Implement self-adaptive
  fixes (Phases A–E), then run against dynamic_management.py with all 5 models
  targeting Areas 4–7 (undertested detector/immune code). Phase A: wire per-model
  registry Layer 4 into orchestrator. Phase B: close immune feedback loop
  (apply_diagnosis()). Phase C: per-model prompt adaptation (DeepSeek verification
  fix). Phase D: area-level vocabulary tracking (replaces global). Phase E:
  dispatch health monitoring (3 new pathology types). Recalibrate τ_vocab 0.10→0.04,
  W 3→5. 7 falsifiable predictions registered. Predicted termination: rounds 8–15.
- **Experiment 14 Phases A–E COMPLETE (29-30 March 2026):** Self-adaptive
  immune layer implemented. Per-model registry Layer 4 wired. Immune feedback
  loop closed (apply_diagnosis). Per-model prompt adaptation. Area-level vocab
  tracking. Dispatch health monitoring with 3 new pathology types. Recalibrated
  τ_vocab_growth 0.10→0.04, vocab_sustained_window 3→5. 234 tests.
- **Experiment 15 IN PROGRESS (30 March 2026):** Live wire run of
  `dynamic_management.py` (now ~6,100 lines) with all 5 models. Self-adaptive
  immune layer (Level 3) active. Three runs attempted: Run 1 killed by
  DeepSeek CircuitBreakerTripped, Run 2 killed by same, Run 3 in progress
  (Round 1, 21 findings so far). Fixes applied mid-experiment: circuit breaker
  catch (`aa89585`), DeepSeek CoT budget exhaustion retry with halved
  max_tokens (`5058d29`).
- **Experiment 15 failure mode analysis COMPLETE (30 March 2026):** 6 failure
  modes classified across mathematical model and immune layer. Dual-track
  fixes implemented (`df52e85`):
  - Mathematical model (MATHEMATICAL_APPENDIX.md §2): delivery feasibility
    f_del, decomposition yield bounds η_dec, format yield φ_fmt(i). Combined:
    q_ik = f_del(i) · φ_fmt(i) · d_ik · p_ik. All reduce to existing when factors=1.
  - Immune layer: 3 new detectors (parser yield anomaly, monotonic decline,
    cost-per-finding spike). [253 tests](../bench/TEST_COVERAGE.md) passing (19 new).
- **Immune persistence + Policy Engine PLANNED (30 March 2026):** JSON-based
  cross-experiment memory for immune layer (est. 150 lines). Policy Engine
  consolidation of remediation chains, registry TOML, inline heuristics.
  Deferred until Exp15/16 iteration stabilises immune layer shape. Plan:
  `docs/experimental_notes/Immune_Persistence_And_PE_Plan_2026-03-30.md`.
- **STOPPING CRITERION (founder-defined, 30 March 2026):** Everything wired
  and fully operational to the extent that the bench produces meaningful
  results without wasted compute on broken detectors, format failures, or
  premature termination. Bench Run 2 must be a legitimate scientific
  experiment, not a debugging session. We stop iterating on the methodology
  when we can show the bench produces meaningful results. Occam's razor
  applies: simplest sufficient solution at every level. The wider community
  will have far greater compute to refine further.
- **META-TRAJECTORY:** Problem space is shrinking across experiments. Exp12
  found structural failures (broken detectors). Exp13 found calibration
  errors (one threshold). Exp14 found design gaps (not broken code). Exp15
  found edge cases (format divergence, CoT budget). Exp17 immune+LB live
  validation. Exp18=FFF convergence (methodology test). Each iteration finds
  less fundamental problems. The methodology is converging on itself. Experiment
  numbering must auto-increment from logs directory (currently hardcoded).
- **Experiment 15 Run 3 COMPLETE + Layer 1 fixes (30 March 2026, `148f80d`):**
  286 findings across 7 rounds (5 models). Parser fix recovered +18 findings
  (Gemini/ChatGPT tuple format). CX confer produced 7 findings, 4 applied.
  4 convergent findings from multi-model agreement resolved: ascending
  abstraction guard wired into stop(), reassign() scores persisted, recovery
  actions propagated to RoundResult, _solve_greedy() feasibility pre-check.
  Process resilience: httpx timeouts + multiprocessing watchdog. Dynamic
  experiment numbering (auto-increment). 350 tests. Experiment 17 plan
  drafted (immune + load balancing layer validation).
- **Experiment 16 COMPLETE (30 March 2026, `881cf43`):** 5-model CDSFL review
  of Exp 17 plan. 54 P-pass findings, 45 proposed improvements. 11 convergent
  themes resolved: full file delivery (not extract), split blind round (R0A+R0B),
  independent stop caps, behaviour-based success criteria, fault injection
  scenarios, mandatory telemetry, SymPy for math ops, dependency-aware fix DAG,
  DeepSeek decomposition, load balancing separate with interface contracts.
  All 4 open questions resolved. Plan status: APPROVED.
- **Experiment 17 prerequisites COMPLETE (30 March 2026, `e59f522`):**
  Runner script, 4 canary tests (empty response, false positive, cascade,
  oscillation — all passing), 5 Layer 1 preflight tests, round-level telemetry,
  DeepSeek 3-area immune decomposition, interface summary, appendix-to-code
  traceability (22 fully implemented, 5 partial, 8 not implemented formulas).
  Independent stop caps (round 10, wall-clock 4h). Ready to execute.
- **Experiment 17 CODE FIXES APPLIED + FFF CONVERGED (31 March 2026, `d85eb5a`):**
  Round 3 COMPLETE (140 findings), Round 4 partial. All applicable code fixes
  applied in 4 batches: 8 IM + 9 LB + 14 VC + 4 MM = 35 fixes. 351 tests passing.
  Three-way FFF round-robin (Gemini → CX GPT-5.4 → Gemini) under CDSFL converged
  in 3 rounds with 7 additional fixes. Key: pathology_key routing (IM_F013),
  remediation escalation reset (IM_F002), verify_chain exception safety, estimate_gamma
  correction, kappa_rate divergence fix. Logs: `bench/logs/gemini_fff_exp17_fixes/`.
- **Experiment 18 COMPLETE (31 March 2026, `d85eb5a`):** First formal FFF
  methodology test. Three-way round-robin (Gemini → CX GPT-5.4 → Gemini) under
  CDSFL with find-fix-follow instructions. 7 genuine fixes from 3 rounds.
  Key finding: FFF produces integration-level issues standard confer misses.
  CX model/effort configuration critical (o4-mini: 0 genuine; GPT-5.4 xhigh: 5
  genuine). Convergence in 3 rounds. Logs: `bench/logs/gemini_fff_exp17_fixes/`.
- **Baseline confer runner BUILT + AUDIT FIXES (1 April 2026, `2b30423`+uncommitted):**
  `bench/run_baseline_confer.py` — standard CDSFL confer with CC2 + CX + Gemini
  on immune task area. FFF via situation directive. Sequential dispatch. 10
  structural fixes from code audit (process_round once-per-round, ModelResponse
  construction, CircuitBreakerTripped handler, task extraction 269K→114K chars).
  Three test runs diagnosed and fixed different bugs. Run 3 reached R3 with 58
  findings before session loss. Runner now structurally correct; needs clean re-run.
  Logs: `bench/logs/baseline_confer_20260331/`.
- **Baseline confer Run 5 LIVE (1 April 2026, `1247cc8`):**
  All 5 frontier models (CC2 + CX + Gemini + DeepSeek + ChatGPT) under CDSFL +
  FFF, xhigh reasoning, reviewing `dynamic_management.py` immune layer.
  Run 5 upgrades over Run 4: (1) **10 SymPy-confirmed fixes** to
  `dynamic_management.py` (z-threshold, false_positive_rate windowing, correlated
  failure, effective_window decay, FORMAT recovery, early-stop set comparison,
  diagnoses ordering, sensitivity decay, findings decline resolution).
  (2) **Multi-turn decomposed dispatch** as automatic fallback on single-turn
  failure — prompts split into WAIT-step chunks, FFF in final turn. Infrastructure
  in `decomposed_dispatch.py` (all 4 backends: Gemini, OpenRouter, DeepSeek, Codex).
  (3) **No-exclusion policy** — EXCLUDE/ABORT signals intercepted, overridden with
  multi-turn decomposed dispatch. No model ever dropped.
  (4) **FSM terminal state guard** — catches RuntimeError on terminal FSM, continues
  collecting data (Run 4 root cause fixed).
  (5) **γ-unified convergence** + **C(H,E) Popper corroboration** reporting.
  (6) **Checkpoint/resume** logic for crash recovery.
  Pre-seeded Codex + DeepSeek for decomposition (Run 4 CX timeout fixed).
  Run 4 logs preserved: `bench/logs/baseline_confer_run4_20260401/`.
  Run 5 logs: `bench/logs/baseline_confer_run5_20260401/`.
- **Baseline confer Run 5 COMPLETE (1 April 2026, `589c053`):**
  155 corrected findings from 5 models × 5 rounds. 31 unique bug clusters,
  16 critical (sev ≥ 0.85), 58% independently confirmed by 2+ models. Three
  systemic failure modes: state leaks (8 clusters), direction inversions (4),
  missing interface contracts (6). Duane γ=0.112 (NOT converged — rich
  unexplored surface). Popper C(H,E)=0.847 (strong). Infrastructure validated:
  multi-turn fallback (2/2 recoveries), no-exclusion (load-bearing — immune
  layer tried to kill all 5 models at R2), FSM terminal guard (load-bearing —
  caught terminal state R3-R4). ChatGPT parser bug discovered: 29 findings lost
  to JSON format mismatch (fixed). Analysis: `docs/experimental_notes/Run5_Analysis_2026-04-01.md`.
  Findings: `docs/experimental_notes/Run5_Findings_2026-04-01.md`.
  Logs: `bench/logs/baseline_confer_run5_20260401/`.
- **All 31 Run 5 bug fixes applied + FFF verified (1 April 2026, `589c053`):**
  All 31 immune layer bugs fixed in `dynamic_management.py`. FFF verification
  pass caught 4 additional issues: FH-1 regression (idempotent _record_failure),
  FH-2 hasattr smell (proper __init__), RV-4 missing pathology_counts clear on
  exhaustion, DC-1/DC-2 encapsulation (register_diagnoses() method). JSON parser
  fixed — JSON array detection as first-pass before tuple/marker parsers.
  Observation-only γ_input/γ_output/amplification wired into runner. 387 tests.
- **Run 6 COMPLETE (2 April 2026, wall-clock cap at 29,223s / 8h7m):**
  11 rounds, 299 findings, 5 models. Per model: ChatGPT 89, CC2 85,
  DeepSeek 49, Codex 43, Gemini 33. γ=0.027 (NOT converged), C(H,E)=0.863
  (strong corroboration). Terminated by wall-clock cap, not convergence.
  Mid-session fixes: chunking (`44adcad`), Codex per-chunk dispatch (`380368a`),
  parser false-positive (`bc09e78`), CC2→claude CLI (`de3e1ae`), parallel
  blind dispatch (`1647acb`).
  CHURN ANALYSIS: 44% of findings re-targeted previously-examined code.
  Severity inflated R0→R10 (avg 0.55→0.80). R0-R3 genuinely novel; R4-R10
  largely elaborate restatements. MATH: 64 findings, 8 SymPy-verified, 7 valid,
  4 genuinely valuable bugs. SOFTWARE: 6 code-verified, 5 true, 5 worth fixing.
  CRITICAL: γ alone is wrong stop criterion. Compound objective (A × γ_output)
  already detected churn passively. Proposed as primary churn guard.
  Amplification: ChatGPT A=1.67, DeepSeek A=1.56, Codex A=1.55, CC2 A=1.48,
  Gemini A=1.12. Logs: `bench/logs/baseline_confer_run6_20260401/`.
- **Run 7b COMPLETE (2 April 2026, `556e0af`):**
  20 rounds, 197 findings, 3,106s wall-clock. γ=0.393 (converging), C(H,E)=0.6624
  (moderate corroboration). Per model: Codex 116, DeepSeek 41, CC2 20, ChatGPT 11,
  Gemini 9. Ω churn guard active: 4 of 5 models benched (CC2, ChatGPT, DeepSeek,
  Gemini) when Ω < 0.10 for 2 consecutive rounds. Codex sustained through all 20
  rounds. Layer 3 (AdaptiveQuestionOptimiser) passive — referential_density showed
  strongest correlation with Ω (r=0.141).
  FOUR MAJOR CHANGES from Run 6:
  (1) **Compound objective Ω churn guard** — A × γ_output = (β_out/β_in) × (1 − β_out),
  peaks at β_out=0.5. Per-model benching when Ω < τ (0.10) for 2 consecutive rounds.
  Resolution parameter S (default 0.5) tuneable severity threshold.
  (2) **Per-model context budget** — 80K default, 30K DeepSeek override. "IT Crowd fix":
  when accumulated findings exceed budget, model gets fresh instance with summary-only
  context (finding IDs + one-line descriptions). Cross-model findings only (models
  never see their own prior findings).
  (3) **File split** — 6,890-line `dynamic_management.py` split into 12 modules in
  `bench/dm/` (strict two-level DAG, zero circular deps). Backward-compatible
  re-export shim preserves all imports. Each module under 25K tokens for single-pass
  model review. 427 tests pass unchanged through the shim.
  (4) **Decomposition coherence** — Three-tier extraction (TARGET full, INTERFACE
  sig+15 lines, SKELETAL def+docstring) with `_INTERFACE_CRITICAL_MARKERS` ensuring
  cross-component APIs visible in all sub-area rotations. Critical regex bug fixed
  (class methods were invisible to boundary detection due to matching against stripped
  lines). `_REMEDIATION_CHAINS` dict explicitly captured.
  Run 7 (predecessor) failed: DeepSeek hung due to unbounded context injection
  (~230K chars of prior findings on top of 190K base prompt). DeepSeek spent 470s
  generating 85,706 chars of CoT reasoning with 0 chars of visible content. Hard
  wall-clock cap via threading added. Logs: `bench/logs/baseline_confer_run7b_20260402/`.
- **Run 7b sy+f analysis COMPLETE (2 April 2026):**
  197 raw findings → 16 unique verified bugs (6 medium, 10 low). 76% of findings
  were churn (same bug re-reported across rounds). 3 false positives including
  Codex hallucinating missing @dataclass decorator 8 times (7% of Codex output).
  2 mathematical claims refuted by SymPy. Top bugs: self_diagnose() bypasses
  immune_feedback_enabled (0.55), pathology_key namespace mismatch (0.40),
  _verify_remediation key mismatch for kappa/mu (0.35), false_positive_rate
  windowing bias, global damping scalar, chain_exhaustion_rate double-count.
  Analysis: `docs/experimental_notes/Run7b_SyF_Analysis_2026-04-02.md`.
- **Run 9 INFRASTRUCTURE BUILT (2 April 2026, `eeb7f40` + `ac0bf47`):**
  6-cell immune agent pipeline mapping biological cell types to parallel
  verification agents: Dendritic Cell (triage), Cytotoxic T-Cell (code FFF),
  B-Cell (SymPy + z3 + statsmodels), NK Cell (dedup + false-positive DB),
  Helper T-Cell (confidence-weighted synthesis), Regulatory T-Cell (autoimmune
  prevention). Pipeline: DC (~1s) → [CT + B + NK parallel] (~30-60s) →
  HT + RT (~1s). All 6 agents structurally constrained by code — no agent
  relies on natural language instruction. CT agent uses Level 3 enforcement:
  schema-forced structured evidence with file:line:code citations, mechanically
  verified against actual source by `_verify_ct_claim()`. Verdict derived from
  verification results, not agent opinion. New tools integrated: z3-solver 4.16,
  statsmodels 0.14.6, uncertainties 3.2.3 via Python 3.13 discovery. B-Cell
  class-switches (SymPy → z3) when primary tool returns uncertain. NK Cell seeded
  with Run 7b false-positive patterns. Wired into runner as observation-only
  for Run 8; two flags flip for Run 9 (`observation_only=False`, `ct_enabled=True`).
  465 tests pass. Design: `docs/experimental_notes/Immune_Agent_Architecture_2026-04-02.md`.
- **Run 7b BUILD SESSION COMPLETE (2 April 2026, `4b70824`):**
  14 of 16 verified bugs fixed (1 reverted by SymPy falsification of fix itself).
  Key fixes: namespace unification via `_CHAIN_TO_COUNTER` mapping,
  `immune_feedback_enabled` suppression gate on `self_diagnose()`, per-trigger
  damping (3 independent channels), FPR exact windowed counting via `round_idx`
  on all `DetectorDiagnosis`, bivariate normal correlation with Frechet upper
  bound clamping, full lifecycle for check 3 (mu_novelty_disagree), hysteresis-
  based VM resolution, P-pass gate on self-check 2, threshold boundary fix.
  New `bench/verification_utils.py` (~500 lines): 3-stage quality gate — dedup
  via `_finding_similarity`, SymPy subprocess verification, AST structural
  verification. PM stage stubbed (disabled). OBSERVATION-ONLY for Run 8.
  Layer 3 switched from `active=False` to `active=True` — will steer prompts
  for first time based on referential_density correlation with Ω.
  Runner: quality gate wired after each round, termination reason fix for
  MAX_ROUNDS fallthrough, dynamic round banner. 427 tests pass.
  SymPy+FFF verification of fixes caught 2 additional bugs in new code:
  quality gate self-dedup (current round in prior_findings), checkpoint
  serialisation of new fields. Both fixed.
- **PM Filter + Adaptive Immune Verification DESIGNED (2 April 2026):**
  Three-stage automated quality gate between rounds: (1) innate immunity —
  similarity dedup + SymPy + AST checking (zero cost, sub-second), (2) adaptive
  immunity — parallel verification agents via local `claude` CLI with full tool
  access (reads actual files, runs SymPy, AST-parses source; zero marginal cost
  on Max subscription), (3) regulatory T-cells — meta-verification agents that
  prevent over-rejection. All existing infrastructure (verify_sympy(), Finding.verified,
  _finding_similarity(), Role.PM) needs wiring, not building. Nested D-decay
  convergence at all three levels. 5 falsifiable questions registered.
  Design: `docs/experimental_notes/PM_Filter_Architecture_2026-04-02.md`,
  `docs/experimental_notes/Adaptive_Immune_Verification_2026-04-02.md`.
- **Input complexity module BUILT (1 April 2026, test article):**
  `bench/input_complexity.py` — Heaps β on input text (γ_input), output
  complexity (γ_output), amplification factor A = β_output/β_input, compound
  objective (A × steepness, optimal at β_out=0.5 — Occam emerges from maths).
  Wired into runner as observation-only measurement. Not used for dispatch.
  36 tests. Notes: `docs/experimental_notes/Input_Complexity_Decay_Curves_2026-04-01.md`,
  `docs/experimental_notes/Amplification_Factor_2026-04-01.md`.
- **Experiment 20 runner BUILT (30 March 2026, `e11b4a2`):**
  `bench/run_exp20_confer.py` — sequential confer architecture (Phase 1+2 of
  Whole Body Architecture). Fingerprint-based dispatch ordering (strongest model
  first, player_manager last as arbitrator). Attributed findings with
  `[source: model_id]`. Three output types: NOVEL, VALIDATION, CHALLENGE.
  Position-aware prompts (first reviewer, confer, arbitrator). Inherits
  decomposition and feasibility gate from Exp 17. Pending: preflight + canary
  test before launch. Launches after Exp 17 findings are collated and integrated.
  (Renumbered from Exp 18 to Exp 20 after FFF convergence work claimed Exp 18.)
- **Whole Body Architecture designed (30 March 2026):** Design note at
  `docs/experimental_notes/Whole_Body_Architecture_Plan_2026-03-30.md`.
  Three communication layers: nervous system (dispatch sequencing), circulatory
  system (attributed finding flow), endocrine system (adaptive pacing signals).
  Four phases — Exp 20 implements Phases 1 (attributed findings) and 2
  (sequential dispatch). Phases 3 (multi-step pacing) and 4 (closed-loop
  feedback) are future work.
- **CX prompt efficiency confer COMPLETE + IMPLEMENTED (30 March 2026, `8c1dacb`):**
  CX context waste (78 tool calls, 155K tokens). Fix: 6-field standard confer
  packet, stdin piping, `--output-schema`. 78% token reduction. ALL IMPLEMENTED
  in orchestrators. Record: `docs/experimental_notes/CX_Prompt_Efficiency_Confer_2026-03-30.md`.
- **CX efficiency confer R2 COMPLETE (31 March 2026):** CX hit usage limit after
  ~3h runtime. 4-model confer (CC2, ChatGPT, Gemini, DeepSeek) under CDSFL on
  CX dispatch costs. 2 rounds, converged. CLI audit revealed: reasoning effort
  locked at xhigh, 4 MCP servers loading per dispatch, no ephemeral mode. Fixes
  implemented in `call_codex()`: `-c 'model_reasoning_effort="medium"'`,
  `-c "mcp_servers={}"`, `-c "plugins={}"`, `--ephemeral`. Confer results:
  `bench/logs/cx_efficiency_confer_r2/`.
- **MIDCA analysis COMPLETE (31 March 2026):** CDSFL mapped against Cox et al.
  AAAI-16 MIDCA standard. 6/8 core requirements met, 2 partial (expectation
  generation, anomaly detection partially implicit). CDSFL extends beyond MIDCA
  scope in multi-agent coordination and substrate-agnostic measurement. Honest
  assessment: system-level metacognition, not agent-level. Analysis:
  `docs/experimental_notes/CDSFL_MIDCA_Analysis_2026-03-30.md`.
- **Composable directive architecture P-PASSED (31 March 2026):** Modular,
  dynamically assembled directive packets preserving core Popperian constraints.
  Four-layer stack: Universal → Domain → Phenotype → Situation. 5 falsification
  passes, 5 falsifiable questions generated. Dynamic composer (~200-400 lines)
  identified as missing piece. Exp 19 combines composable directives with FFF
  as a 2-condition test (standard vs FFF). Analysis:
  `docs/experimental_notes/CDSFL_Composable_Directives_Analysis_2026-03-31.md`.
- **5-model composable directives confer COMPLETE (31 March 2026):** 3 rounds ×
  5 models (~191K chars). Open-format architecture review. All 5 models agreed
  on four-layer stack, phenotype-as-transform, coherence budgeting, and the need
  for a dynamic composer. Independently converged on coherence penalty, attention
  yield, and diversity decomposition. Results: `bench/logs/composable_directives_confer/`.
- **5-model composer review confer COMPLETE (31 March 2026, `adaa434`):** 2 rounds ×
  5 models (~303K chars). "Problem box" format — models constrained to produce
  working code solutions only. All 6 identified problems solved. CX won all 6.
  ChatGPT strong second. Results: `bench/logs/composer_review_confer/`.
- **Dynamic Directive Composer BUILT (31 March 2026, `adaa434`):**
  `bench/cdsfl_registry/composer.py` — 1,399 lines. Four-layer directive
  composition with monotonicity enforcement, coherence budgeting, CID provenance.
  All 6 confer fixes applied: universal minimal rendering (1,865 chars vs 9,597),
  intra-packet pruning (two-pass HARD/SOFT), 9-step phenotype transform (Jaccard
  dedup), cross-layer conflict resolution (3-rule hierarchy), coherence threshold
  calibration from experiment logs, orchestrator integration helpers. All 5 model
  compositions valid, no monotonicity violations.
- **SymPy verification of composer + mathematical model (31 March 2026):** 8
  implementation claims verified (density monotonicity, calibration threshold,
  Jaccard→containment, pruning convergence, priority total order, coherence
  detection reduction, constraint preservation, dedup threshold). 12 mathematical
  model claims verified (unified detection equation, attention yield, coherence
  penalty, correlated joint miss, diversity decomposition, Ising model with
  bounded ψ, hierarchical dependence, correlation-adjusted coverage, entropy
  coherence, composition monotonicity, critical mass sigmoid, diversity ratio).
  All pass. Ising model requires Σψ ≤ −Σlog(1−q_i).
- **TTS output protocol updated (30 March 2026):** New `tts-output-protocol`
  directive. Per-project Desktop folders (`CDSFL_tts/`, `Genesis_tts/`) + repo
  `experimental_notes/` as .md. 141 files migrated from `~/Desktop/Accessibility/`.
- **Decomposed dispatch infrastructure BUILT (31 March 2026, `d139e12`):**
  `bench/decomposed_dispatch.py` — reusable multi-turn staged context loading for
  all 5 APIs (Gemini chat, OpenRouter messages, DeepSeek messages, CX accumulated
  context). Implements the "tutor" pattern: chunks delivered with "WAITING"
  acknowledgement, synthesis triggered only after full payload received.
- **Gemini Phase 1 mathematical coherence audit COMPLETE (31 March 2026, `d139e12`):**
  8-chunk decomposed delivery (~65K chars). All 8 WAITING responses clean. 14,872
  chars of mathematical analysis (174s). Findings: 14 symbol collisions (namespace
  refactor HARD), all 5 deferred items resolved (A-D1 asymmetric Δ, A-D2 D→ρ_info,
  A-D3 keep step, A-D4 M_suppress volume constraint, A-D5 T_conv/T_budg). A-N1
  anti-parroting REJECTED (contradicts O_A). A-N3 modified (bound ascending_bonus).
  Ising model explicitly rejected. Decomposed delivery attention claim FALSIFIED
  (cumulative context). Proposed §9-§11 structure. Log:
  `bench/logs/gemini_math_audit/round0_gemini_20260331T102313Z.json`.
- **6-round mathematical coherence audit CONVERGED (31 March 2026, `0c5d7ea`+):**
  Iterative Gemini-led audit with 5-model CDSFL review and SymPy verification.
  Round 0: Gemini Phase 1 (8-chunk decomposed, 14,872 chars, 6 tasks). Round 1:
  SymPy 13/13 PASS + CC observations. Round 2: Gemini Phase 2 (namespace table,
  §9/§10 text, self-falsification). Round 4: 5-model review (CC2+CX+ChatGPT+
  DeepSeek+Gemini, 28,088 chars, consensus matrix). Round 5: SymPy 10/10 PASS.
  Round 6: Gemini final resolutions + CX verification (3 APPROVE, 2 MODIFY).
  **Resolved (8):** §9.1 P(y_t|x)=⊥→P=0, §9.2 N_len* uniqueness conditional,
  A-N1 rejection, A-N2 acceptance, §11→§9.4 fold, synthesis deferral, deferred
  items A-D1–D5, ρ_eff domain restriction [0,1]. **Outstanding (2 minor):** CX
  modifications to O2 (q_i terminology) and O4 (piecewise weight definition) —
  both editorial, not mathematical substance. Logs: `bench/logs/gemini_math_audit/`.
  **Key outcomes:** normalised Ising model with partition function Z, C(n)
  independence branching (independent vs correlated via Ising), full namespace
  refactor table (17 collisions), decomposed delivery reformulated as synthesis
  deferral operator τ_defer, A-N1 anti-parroting REJECTED, A-N3 null-vector guard.
- **Find-Fix-Follow pattern identified (31 March 2026):** Analysis of founder's
  informal Gemini interaction pattern revealed a three-step intra-model cycle
  (find issue → resolve it → explore consequences of resolution) that produces
  scope expansion beyond what inter-model confer rounds alone achieve. Currently
  CDSFL rounds require models to report findings but not to resolve them within
  their own turn. Adding a resolution-and-consequence obligation to round
  instructions would reduce rounds-to-convergence and increase cross-section
  issue discovery. Now formally tested as Experiment 18 (FFF convergence).
  Exp 19 combines composable directives with FFF as a 2-condition test. Also
  identified: seeded sensitivity (known-defect injection for calibration) and
  NMI-based sycophancy trigger from same Gemini session warrant evaluation
  against existing S_sync and immune layer.
- **Round 7 find-fix-follow audit COMPLETE (31 March 2026, `e86d44e`):**
  Gemini received full 826-line appendix + all Round 6 resolutions under CDSFL
  with find-fix-follow instructions. Found 6 integration issues (namespace detail
  renames, C(n) branching placement as §0.1, τ_defer exponential penalty for
  decomposition, null-set evaluation with context indicator, suppression guard
  circular reference, separability axiom placement + ρ clipping). All fixed with
  exact text. SymPy 10/10 PASS. Gemini declared model mathematically coherent
  and complete. First practical demonstration of find-fix-follow producing
  cross-section integration findings in a single round.
- **Round 8 Gemini construct evaluation COMPLETE (31 March 2026, `e0cbb99`+):**
  9 constructs from informal founder-Gemini interaction evaluated under CDSFL
  find-fix-follow. Gemini evaluated its own earlier work against the converged
  model. **3 ADOPT:** seeded defect injection (empirical ground-truth for m_k),
  NMI diversity audit (observable estimator for d_ik and J_ij), sycophancy
  trigger via S_H (anchors S_sync to empirical observables). **3 MODIFY:**
  error re-injection rate (maps to existing Δ, adds divergence halt), HIL
  framing penalty (formalises hint damage to search space), substrate ceiling
  (asymptotic boundary on R_n). **3 REJECT:** Mayo severity (redundant with
  §4+§0.1+§7.8), calibration coefficient ω (unnecessary scalar), optimal
  stopping (§7.4 already handles). SymPy 6/6 PASS. Total audit: 8 rounds,
  39 algebra checks, all passing, 6 models examined. Model remains coherent.
  Log: `bench/logs/gemini_math_audit/round8_fff_eval_gemini_20260331T145404Z.json`.
- **MATHEMATICAL_APPENDIX.md REWRITTEN (31 March 2026, `c7f9e7a`):** All
  converged fixes from 8-round audit applied. 826 → 1022 lines. §0.1 Ising
  branching, full namespace refactor (17 collisions), τ_defer, null-vector guards,
  separability axioms, ρ clipping, seeded sensitivity Ŝ_H, NMI diversity δ_ij,
  S_sync^emp empirical anchor, error re-injection ν, HIL framing penalty IG_HIL,
  substrate ceiling. Post-edit SymPy 7/7 reduction properties confirmed.
- **Gemini 9-page proposal P-passed (31 March 2026):** 2 genuinely useful
  (parallel blind dispatch, hybrid async-then-sync), 6 already implemented
  (churn), 1 mathematically incorrect (SI formula — SymPy falsified sign
  inversion on contradictions), 2 deferred (epistemic mesh/sovereign shards).
  Founder decision: reasoning_effort stays at xhigh (max capability, not
  throttled). User-configurable reasoning is a separate future feature.
- **Outstanding fixes tracking file (31 March 2026):** Persistent record of
  ALL unimplemented items from 17 TTS files and experimental notes, cross-
  referenced against codebase. Prevents context-loss from losing track of
  deferred work. File: `docs/experimental_notes/Outstanding_Fixes_And_Deferred_Items_2026-03-31.md`.
- **Founder decision — incremental testing (31 March 2026):** No multi-fix
  smoke tests. One variable at a time, measured against a known baseline.
  Sequence: (1) standard CDSFL baseline confer with CC2+CX+Gemini, (2) add
  CX MCP/plugin flags, (3) add parallel dispatch, (4) add WBA attribution.
  Each change measured independently.
- **Next:** Run 5 complete → apply findings → γ_input complexity routing →
  CX flags → parallel dispatch → WBA attribution → Exp 19 → Exp 20 → Bench Run 2.
  Founder observations: `docs/experimental_notes/Founders_FFF_Observations_2026-03-31.md`.
  Outstanding items: `docs/experimental_notes/Outstanding_Fixes_And_Deferred_Items_2026-03-31.md`.
- **Experimental design:** 2x2 factorial — Control (no methodology),
  HIL (expert hint only), CDSFL (structure + verification), CDSFL+HIL (full
  methodology with expert guidance and research)
- **System prompt injection:** `run_benchmark.py` (lines 310-673) implements
  correct per-model system prompt delivery for all 5 models. Use this
  infrastructure — do not reinvent.
- **Verification:** SymPy (OSS) auto-verifies mathematical claims. CC
  extracts verifiable claims from raw findings when models don't provide them.
- **Policy engine:** Hierarchical Constraint Editor (CE) with 5 layers:
  universal, domain, task, model, runtime.
- **Domain expert configs:** First configs produced — portable, three-layer
  (methodology + domain + personalisation). See `configs/`.

## Smoke Test Results (24 March 2026)

The corrected experimental design produced:
- Control: 10 unique HARD findings (5 rounds self-iteration)
- HIL: 2 unique HARD findings (5 rounds self-iteration)
- CDSFL: 29 unique HARD findings (5 rounds confer)
- CDSFL+HIL: 43 unique HARD findings (5 rounds confer)

Gradient: HIL (2) < Control (10) < CDSFL (29) < CDSFL+HIL (43)

## Architecture Overview

```
Constraint_Engineering/
  PAPER.md                    -- Canonical technical statement (white paper)
  README.md                   -- Operational front door
  configs/                    -- Domain expert configurations (tradeable assets)
    examples/                 -- Methodology, software engineering, template
  docs/
    FOUNDERS_NOTES.md         -- Chronological design observations
    EXPERIMENTAL_RESULTS.md   -- All experimental data including failures
    EXTENDED_RATIONALE.md     -- General-audience companion
    MATHEMATICAL_APPENDIX.md  -- Mathematical extensions
  bench/
    run_round_robin.py        -- Main bench test orchestrator (~3500 lines)
    run_baseline_confer.py    -- Baseline confer runner (Run 5-7b)
    run_exp17_immune.py       -- Exp 17: immune + LB live validation runner
    run_exp20_confer.py       -- Exp 20: sequential confer runner (Whole Body)
    dynamic_management.py     -- Re-export shim (75 lines, backward compat)
    dm/                       -- Dynamic management modules (split from 6,890-line monolith)
      _types.py               -- Config, enums, dataclasses (shared vocabulary)
      _role_assignment.py     -- RoleAssignment (Area 1)
      _load_balancer.py       -- Allocation, LoadBalancer (Area 2)
      _fsm.py                 -- RoundProgressionFSM (Area 3)
      _convergence.py         -- ConvergenceDetector, similarity (Area 4)
      _diminishing_returns.py -- DiminishingReturnsDetector (Area 5)
      _immune.py              -- DetectorHealthMonitor (immune layer)
      _failure_handler.py     -- FailureHandler, CorrelatedFailureModel
      _events.py              -- ManagerEventStream
      _manager.py             -- DynamicManager (orchestrator)
      _validation.py          -- validate_all_reductions
    input_complexity.py       -- γ_input, γ_output, A, Ω, Layer 3 optimiser
    cdsfl_registry/           -- Constraint Editor (CE) policy engine
      registry.py             -- 5-layer hierarchical merge with monotonicity
      composer.py             -- Dynamic Directive Composer (4-layer composition)
      refinements.py          -- Independence-aware confirmation, tuple canon
      universal.toml          -- Layer 1 (immutable HARD constraints)
      domains/                -- Layer 2 (domain-specific policies)
      models/                 -- Layer 4 (model-specific settings)
    tasks_frontier/           -- 27 frontier tasks (ft-001 through ft-027)
    directives/               -- Domain-specific constraint boxes
    interactive_smoke.py      -- Bidirectional P-pass test script
    tutor_test.py             -- Tutor-style decomposition test
  resources/                  -- This folder — onboarding and recovery
```

## Key Concepts

**P-Pass:** Popperian falsification pass. Generate, attack, fix, repeat until
diminishing returns. The core mechanism.

**HARD/SOFT classification:** Constraints classified as non-negotiable (HARD)
or preference-based (SOFT). Ambiguous defaults to HARD.

**Confer/Defer:** Multi-model protocol. Models review each other's findings
iteratively. Confer = agreement. Defer = escalation to human review.

**Decay curve (D):** Genuine analysis produces diminishing finding rates per
round (Duane NHPP model, γ > 0). Chatbot churn produces flat curves (γ ≈ 0).
The shape distinguishes analysis from noise.

**(D, v-bar, A, C) fingerprint:** Four-metric capability assessment.
D = decay rate, v-bar = verification score (SymPy-confirmed fraction),
A = total verified findings, C = coverage of constraint space.

**Abstraction Index H(x):** Measures finding depth — formality × information
density × generalisation scope. Captures the difference between spotting a
typo and identifying a paradigm-level architectural flaw.

**Total Cognitive Yield Y(t):** Count × mean depth. When findings decrease
but depth increases, total yield can still rise. Captures ascending
abstraction as a distinct cognitive mode.

**Emergence:** When multiple agents work under structured falsification,
the composite system's Y exceeds any individual's. Empirically demonstrated
in the three-architecture review (Gemini found 16 issues CC/CX missed).
Formalised in Mathematical Appendix §8.

**Second-order cognition:** The composite system analyses, monitors its own
analysis (via decay curves + verification rates + adoption deltas), and
adjusts based on monitoring (metacognitive feedback protocol). Meets the
formal MIDCA definition. Substrate-agnostic — the same maths applies to
human teams.

**Constraint Editor (CE):** Hierarchical policy engine. 5 layers cascade
with monotonicity — lower layers cannot weaken higher-layer HARD constraints.

**Domain expert config:** Portable cognitive encoding with three layers:
universal methodology, domain-specific directives, user personalisation.

## Known Confounds (document honestly)

1. **Directive asymmetry:** CC and CX carry the founder's cognitive
   methodology directives (CLAUDE.md) into all conditions. DeepSeek, Gemini,
   and ChatGPT operate with no equivalent. This affects between-model
   comparisons but not between-condition comparisons.

2. **ChatGPT context overflow:** ChatGPT via pipe mode accumulates full
   conversation history. 24 warnings, 1 failure in bench test. Context cap
   not yet applied to ChatGPT (applied to CX only).

3. **SymPy extraction gap:** CC extracts mathematical claims from raw
   findings when models don't include verifiable_claim fields. Extraction
   quality varies — some claims are unparseable by SymPy. The natural
   language mathematical interpretation gap is a known limitation.

4. **Small model population:** 5 frontier models from 4 vendors is the
   available population, not a chosen sample. The diversity hypothesis
   cannot be fully tested until the ecosystem is larger.

5. **HIL prompt narrowing:** The HIL guidance says "focus on these points,"
   which narrows model search. Confirmed by framing bias literature
   (arXiv:2603.18740). Fix designed: iterative 5-round guidance pattern.

6. **ChatGPT hidden system prompt:** ChatGPT 5.4 via proprietary API carries
   a hidden RLHF preamble. Fix designed: OpenRouter access with user-defined
   system prompts.

7. **Phantom HARD inflation:** Default constraint_class was HARD instead of
   SOFT. Fixed in code but affects Run 1 data.

## Communication Protocols

The founder uses single-token shorthand to steer cognitive mode. Commands
compose left-to-right, separated by a single space. Full reference:
`resources/SHORTCUTS.md`.

- `y` = yes/approved
- `cy` = continue
- `rt` = read context files + continue
- `d` = discuss before proceeding
- `r` = re-read key context files (IM, checkpoints)
- `p` = P-pass (Popperian falsification — iterative, not observational)
- `c` = confer with all available models under CDSFL protocol
- `a` = analyse dispassionately
- `e` = extrapolate beyond immediate domain
- `rr` = full recovery (rebuild context from all sources)
- `rs` = restore state (IM + OB + checkpoints + memory)
- `t` = send to TTS (accessible plain-text export)
- `sv` = save state (Open Brain + update docs + commit + push)
- `re` = external research (web search, arXiv, Semantic Scholar)
- `g` = confer with Gemini specifically
- `sy` = check with SymPy (mathematical verification)
- `x` = override sleep/rest warnings for current session
- `qc` = quality control (full docs/staleness/consistency check)

These compose: `p d e` = falsify, discuss, extrapolate. `rs qc` = restore
state, then quality control.

## How to Resume Work

1. Read this document
2. Check `git log --oneline -10` for recent commits
3. Check if bench test is running: `ps aux | grep run_round_robin`
4. Read latest log: `tail -30 bench/logs/$(ls -t bench/logs/ | head -1)`
5. Check MEMORY.md for persistent project state (if available)
6. Read FOUNDERS_NOTES.md for design intent and open questions

## How to Reproduce Results

```bash
cd bench
pip install -r requirements.txt
source ../.env    # API keys for DeepSeek, Gemini, OpenAI, Wolfram
python3 run_round_robin.py --phase2 --smoke --tasks ft-001   # single task smoke test
python3 run_round_robin.py --phase2                           # full 26-task bench
```

All results are checkpointed. Use `--resume` to continue after interruption.

## How to Refute Results

Run the bench test yourself. Compare your (D, v-bar, A, C) fingerprints
against the published results. If your Control condition outperforms your
CDSFL+HIL condition, the methodology fails on your tasks. Publish the result.
That is data, not failure.
