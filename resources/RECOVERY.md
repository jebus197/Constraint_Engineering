# Recovery Protocol

Last updated: 15 April 2026 20:21 BST

How to rebuild full working context from the repository alone after a
session loss, compaction event, or fresh start with a new model instance.

## Minimum Recovery (2 minutes)

1. Read `resources/ONBOARDING.md` — current project state, architecture,
   key concepts
2. Run `git log --oneline -10` — what changed recently
3. Run `git status` — any uncommitted work
4. Check if bench test is running: `ps aux | grep run_round_robin`
5. If resuming Experiment 12 fixes: read `bench/logs/experiment_12/experiment_12_report.json`
6. If resuming meta-test fix work: read `~/.claude/plans/agile-wondering-hejlsberg.md`
7. For Exp12 analysis: read `~/Desktop/CDSFL_tts/Exp12_Final_Analysis_2026-03-29.txt`
8. For UX vision context: read `~/Desktop/CDSFL_tts/CDSFL_UX_Vision_Sketch_2026-03-28.txt`
9. **For Exp 36 ground truth and forward path:** read `experimental_notes/Exp36_Ground_Truth_Reference_2026-04-08.md` — canonical reference consolidating all findings, immune status corrections, 13 design improvements, mathematical model gaps, and resumption plan.

This is enough to resume most tasks.

<!-- SV:PENDING_START -->
## Current Pending Work (15 April 2026 ~20:xx BST)

832 tests pass (793 existing + 39 new feedback-channel tests). Branch:
`exp39-experimental`. 2 commits ahead of origin pending this sv. Latest
landed commit: `a6ee7b4` (sv: Stage 6 + FFAFP admissibility set now in
model-facing directives, 15 April 19:06 BST).

**SESSION 15 APRIL EVENING — FEEDBACK CHANNEL (PHASE 10):**

User insight: the schema already computes a rich per-finding signal each
round (B-Cell verdicts, FFAFP admissibility, near-duplicate, R_k
validation) but that signal was logged and discarded — models never saw
it, so the same refuted claim could be resubmitted unchanged. User quote:
"Measurement is nice. It's a nice to have. But the entire point of this
project was to make LLM's more reliable, more trustworthy and more
accurate. What is the point in this measurement if we don't use it for
anything productive?"

**Fix landed — feedback channel:**
- NEW `bench/dm/_feedback.py` (533 lines) — `FindingFeedback` dataclass,
  `build_feedback_records()`, `build_feedback_sections()`, tolerant
  `parse_admissibility_block()`. Priority ordering: refutation >
  admissibility > duplicate > R_k. Actions: RECALCULATE /
  ADD_ADMISSIBILITY_OR_WITHDRAW / DIFFERENTIATE_OR_WITHDRAW /
  RECALIBRATE_RK.
- `bench/reference_runner.py` — wired into round loop (post-immune_result
  at ~line 3808), feedback dict carries to next round's dispatch.
  `RunnerConfig` gets 3 knobs. Defensive — build failures yield empty
  dict, never crash the main loop.
- `bench/directives/universal/cdsfl_operational.md` — NEW §17 (imperative
  feedback-channel directive).
- `bench/directives/universal/cdsfl_core_formal.md` — classification
  summary table split: Stage 1 C(n), Stage 5–6 R_k(i), Stage 6 feedback
  channel — with pointers to `_feedback.py`.
- `bench/cdsfl_registry/universal.toml` — NEW `[feedback_channel]`
  section (enabled=true, top_k=10, max_chars=8000, mode=imperative).
- NEW `bench/tests/test_feedback_channel.py` — 39 tests across 5 classes,
  all green. Full regression 832/832.

Live-default, not shadow. The user's framing was structurally
incompatible with indefinite shadowing. Toggle retained for controlled
ablation via `[feedback_channel] enabled = false`.

**LESSONS-FORWARD RELATED TO FEEDBACK CHANNEL:**
- #4 (semantic novelty feedback) — NOW SUBSUMED. §17 carries duplicate
  similarity back to the emitting model as imperative signal.
- #6 (prior fix summary) — NOT yet subsumed. Feedback carries schema
  judgment on findings, not the "here's what we fixed last round"
  narrative. Separate work.
- #10 (S_k format pre-check) — COMPLEMENTARY. Format-level pre-check
  still pending; admissibility parser catches some of it.

**SESSION 15 APRIL AFTERNOON — DIRECTIVE GAP CLOSURE (STAGE 6 + FFAFP):**

User directive: "Yes and plug all remaining outstanding gaps both in the
experiment 39 runner and in the CDSFL schema as a whole. (Including any stale
docs.) Take care and work sequentially."

**Problem diagnosis:** Grep for FFAFP, c_ext, e_value in
`bench/directives/universal/` returned zero matches. Stage 6 and the FFAFP
admissibility constraint set existed only in the mathematical appendix — not in
what models actually receive at run time. Appendix is authoritative; the
directive is operative. Models were being asked to comply with Stage 5 while
the codebase was silently evolving toward Stage 6 evaluation.

**Edits landed (7 files, no confer this session — pure schema plumbing):**

1. `bench/directives/universal/cdsfl_operational.md` (448 → ~660 lines):
   - §9 line 366: symbol collision resolved — Stage-5 re-injection floor
     renamed to `ν_eff,k`; appendix `ν_k` reserved for literature novelty.
     Notation note added.
   - §2 Output Format: ADMISSIBILITY and NOVELTY reporting made mandatory.
     Softened from "parser rejects" to "flagged by FFAFP gate" / "defaults
     to Stage 5 reduction" — parser in `runner_core.py:333` is permissive
     by design; enforcement is downstream.
   - NEW §15 (FFAFP Admissibility Constraint Set) — formal S_min,
     G-completeness, d_tool, σ_measured, q_retest definitions + reporting
     template. ~80 lines.
   - NEW §16 (Stage 6 Literature-Calibrated Extension) — η decomposition
     η_combined = η_int·(1−c_ext·(1−ν_k)), four-quadrant table,
     orthogonality with R_k, E-value shadow-mode note, directive hierarchy.
     ~100 lines.
2. `bench/directives/universal/cdsfl_core_formal.md` §5: Stage-awareness
   blockquote prefacing C(n) — C(n) is Stage 1; operational uses R_k(i);
   Stage 6 extends. Pointers to operational §3, §16 and appendix §1.1.
3. `bench/directives/universal/expert_encoding_template.md` §6: S* formula
   corrected from `(nu_b + nu_f − q·R) / nu_f` (approximation) to full form
   `(nu_b + nu_f − nu_b·nu_f − q·R) / (nu_f · (1 − nu_b))`. Old form only
   accurate when nu_b ≪ 1 — fixed so encodings produced from template carry
   the right formula.
4. `bench/cdsfl_registry/universal.toml`: `ffafp_required = true` comment
   expanded from 4-step to 5-step protocol with admissibility-set mention.
5. `bench/reference_runner.py` (~lines 3398-3409): prompt template extended
   with ADMISSIBILITY (5 gate pass/fail lines) + NOVELTY (ν_k, c_ext,
   H/H_max, Citations) blocks with worked examples.
6. `.claude/CLAUDE.md`: appendix line count 1081 → 1991 with Stage-6
   annotation. Previously stale since Tranche C's 14-line discrepancy.
7. `bench/logs/immune_pipeline.log`: regression-run artefact.

**Propagation verified:** Operational directive is loaded separately at
`reference_runner.py:149` and appended post-composer at line 1509, bypassing
phenotype caps. Updates reach all 5 models in the panel.

**Process errors caught and corrected mid-session:**
- First §2 draft claimed "parser rejects" — incorrect; parser is permissive.
  Softened to "flagged by FFAFP gate" after reading `runner_core.py:333`.
- First NOVELTY default wrote "degrades η_combined and increases R_k" — wrong;
  with c_ext=0, η_combined = η_int (no degradation). Corrected to "defaults
  to (ν_k=0, c_ext=0), reduces Stage 6 to Stage 5".
- Attempted a ScheduleWakeup with `<<autonomous-loop-dynamic>>` while waiting
  for pytest background — user never requested a loop. Ended by not
  rescheduling.
- Tried `sleep 30` in Bash; blocked by the 2s cap. Switched to background-
  task notifications.

**SESSION 14 APRIL EVENING — TRANCHES A/B/C (B-CELL DISPATCH CONSOLIDATION):**

**SESSION 14 APRIL EVENING — TRANCHES A/B/C (B-CELL DISPATCH CONSOLIDATION):**

User directive: "Do 1. Boring and safe. Slowly, slowly wins the race! Doit all."
Three tranches executed sequentially, one-wrapper-at-a-time hygiene to avoid
API overload after the ~580-line-edit 500 earlier in the day.

**Tranche A — housekeeping (commit `6838160`, 19:56 BST):**
- `.claude/CLAUDE.md`: crosshair moved from "NOT installed" list into the
  Code Analysis Tools table (crosshair 0.0.102 present, imports clean).
- `sv` sequential-reading protocol added to CLAUDE.md and user global directives
  (absorb one large doc chunk at a time, not parallel load).
- No functional code changes.

**Pre-Tranche-A chore (commit `d9f8f82`, 19:52 BST):**
- Committed Stage 6 residuals left untracked from the morning session:
  `bench/dm/_shadow_stage6.py` (740 lines), three confer driver scripts,
  three Stage 6 synthesis writeups, confer log directories. Pure cleanup of
  flagged item #15 in the previous Deferred list.

**Tranche B — 5 new B-Cell specialist wrappers (commit `0c1de8e`, 21:02 BST):**
- `_verify_symbolic_execution` (crosshair 0.0.102) — behavioural code contracts
- `_verify_chemistry_structure` (rdkit 2026.3.1) — SMILES/molecule validation
- `_verify_biological_sequence` (biopython 1.87) — DNA/RNA/protein sequences
- `_verify_ml_claim` (scikit-learn 1.8.0) — ML metric/model claims
- `_verify_graph_property` (networkx 3.6.1) — graph theoretic claims
- 5 new elif branches appended to `_specialist_b_cell_dispatch()` after the
  prior 9 branches. Dispatch semantics preserved.
- 4 domain TOML updates in `bench/cdsfl_registry/domains/immune/`.
- New packages installed (CLAUDE.md "NOT installed" line now stale — see
  Staleness Flags below): rdkit 2026.3.1, biopython 1.87, scikit-learn 1.8.0,
  networkx 3.6.1. matplotlib 3.10.8 was already present.
- 793 tests pass.

**Tranche C — manifest-driven dispatch refactor (commit `2f22a8a`, 23:01 BST):**
- NEW: `bench/cdsfl_registry/tool_manifest.toml` (238 lines, 20 entries).
  Schema per tool: description, verifier (fn name), needs_file (bool),
  claim_types, domain_hints, cost_class (fast/medium/slow), install_check,
  package_hint (PEP508), delegate (optional).
- 18 active verifiers: sympy, z3, statsmodels, scipy, dimensional_analysis,
  uncertainty_propagation, stoichiometric_balance, linear_programming,
  astronomical, chemistry_structure, biological_sequence, ml_claim,
  graph_property, type_checker, lint_check, security_scan, bytecode_analysis,
  symbolic_execution.
- 2 delegates: ast_analysis → b_cell_v2, test_runner → ct_cell.
- `_load_tool_manifest()` lazy singleton loader added at `immune_agents.py:148`.
  Drops manifest entries where the verifier name does not resolve in-module
  (belt-and-braces validation — stderr warning, silent skip at dispatch time).
- `_specialist_b_cell_dispatch()` body replaced: 46-line elif chain collapsed
  into 12-line manifest-driven loop. First-definitive-verdict wins, UNCERTAIN
  falls through, `[specialist:<tool>]` evidence suffix preserved, finding_id
  stamped. Adding a new B-Cell specialist is now a TOML-only edit.
- Regression: 793/793 pass, 12m 24s.

**SESSION 15 APRIL — RECOVERY AFTER RESET (00:15 BST):**
- Post-compaction recovery initiated via `rs`. First attempt was a skim read;
  user rebuked and demanded deep sequential reading per CLAUDE.md protocol.
- Five parallel Explore subagents launched (ag, a, d). Two rejected mid-flight
  (Git archaeology + Code reality check). Remaining 3 returned comprehensive
  reports on RECOVERY/ONBOARDING state, TTS notes last 72h, memory files.
- Replacement Explore agent ran combined Git archaeology + code-state check;
  confirmed Tranches A/B/C landed cleanly, 793 tests collected, all files
  present. Flagged CLAUDE.md "NOT installed" staleness (5 packages actually
  installed), 14-line gap between claimed and actual appendix length, and
  the 4 unpushed commits.
- User deferred plan approval to morning with fresh eyes. sv requested before
  sleep to preserve state.

**SESSION 14 APRIL (morning) — TOOL PERMISSIONS + ν_k DESIGN + STAGE 6 APPENDIX:**

**SESSION 14 APRIL — TOOL PERMISSIONS + ν_k DESIGN + STAGE 6 APPENDIX:**
- CC1 tool permissions: `.claude/settings.json` created, all native + MCP tools auto-approved
- CC2 tool access: `--allowedTools Bash Read Write Edit Grep Glob WebFetch WebSearch`
- ν_k (nu-k) novelty metric designed, SymPy + Wolfram verified, all boundary conditions pass
- CDSFL self-assessed at ν_k = 0.807 (genuinely novel) against literature
- Nearest competitor: Stanford POPPER (Feb 2025) — different mechanism, narrower scope
- **Stage 6 added to MATHEMATICAL_APPENDIX.md** (2005 lines, +354 from 1651):
  - §1.1: Stage 6 in model evolution table + full derivation
  - §1.6: Literature Novelty Score (ν_k)
  - §1.7: Source Diversity and Corroboration Confidence (c_ext)
  - §1.8: E-value Verification Gate (proposed, POPPER attribution)
  - §1.4: Holland/Jerne idiotypic lineage added
  - §1.5: Frequency-scaled confidence added
  - Intellectual Lineage section added
  - Notation Summary expanded
- **Confer Round 1:** Gemini 3.1 Pro + Codex GPT-5.4 FFAFP review
  - 7 corrections applied (3 HARD, 4 SOFT)
  - Critical fix: β_abs cap on abstraction adjustment (both models flagged)
  - Critical fix: E-value mapping changed to 1/FPR_tool
  - All corrections SymPy verified
  - Synthesis: `experimental_notes/Stage6_Confer_Synthesis_2026-04-14.md`
- **Founder pivot:** Two-dimensional (ν_k, c_ext) reporting — never collapse into single score
  - OSF analogy: "highly novel content with low corroboration" is a meaningful state
  - Abstraction is context only, not adjustment — removed β_abs entirely
  - Shadow calibration hooks added to Exp 39 runner
- **Confer Round 2:** Codex + Gemini review of revised 2D design
  - 5 HARD corrections applied: fpr_estimate→fail_fraction, stale §1.6 confound, §1.8 e-value text, q_s for live_empty, openalex typo
  - 3 SOFT corrections: "Unverified known"→"Weakly assessed", "orthogonal"→"distinct", scalar projection note
  - Both models confirm 2D architecture is correct direction
  - Gemini novel finding: abstraction laundering via bad queries → q_s is critical calibration target
  - Synthesis: `experimental_notes/Stage6_R2_Confer_Synthesis_2026-04-14.md`
  - TTS: `~/Desktop/CDSFL_tts/Stage6_R2_Confer_Synthesis_2026-04-14.txt`
- Shadow Stage 6 calibrator: `bench/dm/_shadow_stage6.py` hooked into `reference_runner.py`
  - Per-finding (ν_k_proxy, c_ext, H_ratio) triples, per-tool fail fraction, shadow η deltas
  - Writes per-round JSON + cumulative summary to disk
  - 793 tests pass
- Analysis: `experimental_notes/Novelty_Scoring_nu_k_Design_2026-04-14.md`
- TTS: `~/Desktop/CDSFL_tts/Novelty_Scoring_nu_k_Design_2026-04-14.txt`

**IMMEDIATE NEXT STEPS (consult HIL before proceeding):**
0. **Push 50 local commits to origin** (trivial, zero-risk; branch is ahead
   48 + 2 from this session's directive work + feedback channel)
1. Wire OpenRouter tool-use (add `tools` parameter to `call_openrouter()`)
2. Wire DeepSeek specialist role (Phase 6) into pipeline
3. Implement ν_k metric in O1 (Phase 7) — design complete, code pending
4. Add Unpaywall + CORE + OpenAlex source adapters to O1
5. Re-run Exp 39-0 gate test with all fixes in place (18 specialists
   wired + feedback channel live)
6. Carry forward remaining 6 lessons from Exp 36-38 (was 7; #4 subsumed
   by feedback channel §17)
7. Promote specialist dispatch from shadow to live — single-line flip at
   `reference_runner.py` ~3741. HIL decision; recommend one shadow-run
   divergence review first.

**LESSONS-FORWARD AUDIT — 6 STILL MISSING (was 7):**
4. ~~Semantic novelty feedback (3 graduated signals from Exp 37)~~ ✅
   **SUBSUMED 15 April 2026 evening.** The feedback channel (§17) carries
   per-finding duplicate similarity back to the emitting model as
   imperative signal: "NEAR-DUPLICATE: cosine X.XX to <prior_id>" with
   action `DIFFERENTIATE_OR_WITHDRAW`. 3-tier graduation retained
   implicitly via priority score (similarity × 2.0 contribution).
6. Prior fix summary context (`_build_prior_fix_summary()` from Exp 37)
7. Consolidation phase for final 3 rounds (Exp 36 Ground Truth, HIGH)
8. Per-model ρ tracking with targeted ITC (Exp 36 Ground Truth, HIGH)
9. Context windowing for long runs (Exp 36 Ground Truth, HIGH)
10. S_k format pre-check with reformat request (Exp 38) — PARTIALLY
    ADDRESSED (format accepted; §17 admissibility parser catches some
    structural failures)
11. Parser fixes P2/P3 — CC2 finding leak FIXED, Gemini verdict extraction still pending

**FINGERPRINT GAP:** Attention metrics still null. DeepSeek fingerprint now has
max_successful_prompt_chars (102,942) from decomposed chunks but still decomposes
on monolithic payload (~104K). Bootstrapping trap until specialist role or override.

**DEFERRED (architecture items for 39-A onwards):**
1. Domain-agnostic gate interface (IFalsificationGate protocol + GateResult)
2. Convergence gate: add churn detection (§7.1a) as C6
3. Missing domain configs (biology, info science, engineering immune, cs_software)
4. ~~B-Cell dispatch: route to domain-specific tools from new TOML configs~~ ✅
   **DONE 14 April 2026.** 14 active wrappers + manifest + dispatch loop landed
   across Tranches A/B/C (commits `6838160`, `0c1de8e`, `2f22a8a`). 793 tests green.
   Shadow mode preserved. Promotion (single-line flip at `reference_runner.py`
   ~3741) still pending HIL decision — see Immediate Next Step 7.
5. Severity fusion (§7.7) for gate output synthesis
6. Sycophancy detection (§7.5)
7. O1 calibration: sensitivity dial, circuit breaker, semantic clustering
8. MC command sync across all reference locations
9. Phase 9 (research write-up) — deferred post-Exp 39
10. Implementation plan: `~/.claude/plans/effervescent-watching-platypus.md` —
    Phases 0–8 all complete per archaeology (14 April sequential landing:
    shadow-extensions, kappa prep, similarity, suppression, memory, FFAFP,
    B4 dispatch, O1 shadow, appendix expansion). Phase 9 deferred.
11. Prompt schema as first-class tested artefact (not string literal in 3700-line file)
12. OpenRouter tool-use mode for panel models (CC2 has Bash, others need function calling)
13. Wire hypothesis / beartype / icontract / pyright / mutmut / coverage into cells
    (installed but not routed — depends on cell design decisions)
14. ~~Install crosshair if symbolic execution becomes needed for a domain~~ ✅
    **DONE Tranche A/B.** crosshair 0.0.102 installed and wired as
    `_verify_symbolic_execution` in manifest.
15. ~~Prior session uncommitted artefacts~~ ✅ **DONE** (commit `d9f8f82`,
    19:52 BST). `_shadow_stage6.py`, confer driver scripts, Stage 6 syntheses,
    and confer log dirs all tracked.

**STALENESS FLAGS (tracked across sv cycles):**
- ~~`.claude/CLAUDE.md` § "What Is NOT Installed" still lists rdkit, biopython,
  scikit-learn, networkx, matplotlib as not installed.~~ ✅ **RESOLVED** at the
  00:47 BST sv — NOT-installed list now correctly cites only pylint, radon,
  vulture, pyflakes with a `pip show` ground-truth pointer.
- ~~`docs/MATHEMATICAL_APPENDIX.md` is 1991 lines on disk; prior commit messages
  cite ~2005.~~ ✅ **RESOLVED** this session — CLAUDE.md line-count reference
  updated to 1991 with Stage-6 annotation.
- `configs/README.md`, `bench/cdsfl_registry/universal.toml` not yet re-read
  against the 14-tool manifest expansion. `universal.toml` FFAFP comment was
  touched this session (5-step protocol), but the manifest-expansion cross-check
  is still open. Low priority.
- ~~`bench/directives/universal/cdsfl_core_formal.md` §5 C(n) now carries a
  Stage-awareness blockquote but the downstream classification summary table
  (Section at end) still lists C(n) as the canonical corroboration model —
  consider a table-row edit next pass.~~ ✅ **RESOLVED** this session
  (feedback channel work, evening). Table now has three rows:
  Stage 1 reference (C(n)), Stage 5–6 operational (R_k(i)), Stage 6
  feedback channel — each with pointers to the relevant operational
  section and source file.

**Also pending:** Onboarding script redesign.
<!-- SV:PENDING_END -->

## Standard Recovery (5 minutes)

Everything above, plus:

5. Read `docs/FOUNDERS_NOTES.md` — design intent, chronological observations,
   known confounds, open questions
6. Read the latest bench test log: `tail -50 bench/logs/$(ls -t bench/logs/ | head -1)`
7. Check `docs/EXPERIMENTAL_RESULTS.md` for latest recorded results

## Full Recovery (10 minutes)

Everything above, plus:

8. Read `PAPER.md` — canonical technical statement (Parts I-XIV)
9. Read `docs/MATHEMATICAL_APPENDIX.md` — mathematical extensions including
   the cognitive measurement framework (§7) and emergence formalisations (§8)
10. Read `configs/README.md` — domain expert configuration system
11. Read `bench/cdsfl_registry/universal.toml` — current HARD constraints
12. Read `PRIVATE_NOTES.md` (if it exists locally) — known confounds and
    design decisions not yet public
13. Check Open Brain for session context:
    `python3 -m open_brain.cli session-context --agent cc`
14. Check IM service for inter-model communications:
    `python3 cw_handoff/im_service.py read`

## For the Founder Specifically

After compaction, the continuation summary is what I was thinking — not what
happened. It is never sufficient on its own. The external sources (git log,
bench logs, ONBOARDING.md) always take precedence over the continuation
summary when they conflict.

Your shorthand `rr` triggers full recovery. Your shorthand `r` triggers
IM read only (quick context check).

## For New Model Instances

You are joining a project in progress. Read ONBOARDING.md first. Do not
assume the continuation summary (if provided) is complete or accurate.
Verify against the repository state.

Key files to understand your role:
- If you are CC (Claude Opus 4.6): You are orchestrator, reviewer, and
  arbiter. You generate solutions, review alongside other models, extract
  verifiable claims, and assess convergence. Read `~/.claude/CLAUDE.md`
  for your cognitive directives.
- If you are CX (Codex 5.3): You are independent falsifier. Your primary
  role is to find what CC missed. Read your equivalent directives file.
  The founder values your adversarial precision highly.
- If you are another model: You are a reviewer in the distributed compute
  chain. Produce structured JSON findings. Challenge what you disagree with.
  Do not defer to CC or CX — your independent perspective is why you are here.

## For Human Developers

The project is a methodology research project, not a software product.
The code in `bench/` is experimental infrastructure for testing the
methodology. It has been iteratively improved through P-pass cycles
between CC and CX, with founder oversight on all experimental design
decisions.

Start with ONBOARDING.md, then PAPER.md, then FOUNDERS_NOTES.md. The
code will make more sense after you understand what it is trying to test.
