# Recovery Protocol

Last updated: 15 April 2026 00:47 BST

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
## Current Pending Work (15 April 2026 00:43 BST)

793 tests pass. Branch: `exp39-experimental`. 4 commits ahead of origin.
Latest commit: `2f22a8a` (Tranche C, 14 April 23:01 BST).

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
0. **Push 4 local commits to origin** (trivial, zero-risk; branch is ahead)
1. Wire OpenRouter tool-use (add `tools` parameter to `call_openrouter()`)
2. Wire DeepSeek specialist role (Phase 6) into pipeline
3. Implement ν_k metric in O1 (Phase 7) — design complete, code pending
4. Add Unpaywall + CORE + OpenAlex source adapters to O1
5. Re-run Exp 39-0 gate test with all fixes in place (18 specialists now wired)
6. Carry forward remaining 7 lessons from Exp 36-38
7. Promote specialist dispatch from shadow to live — single-line flip at
   `reference_runner.py` ~3741. HIL decision; recommend one shadow-run
   divergence review first.

**LESSONS-FORWARD AUDIT — 7 STILL MISSING:**
4. Semantic novelty feedback (3 graduated signals from Exp 37)
6. Prior fix summary context (`_build_prior_fix_summary()` from Exp 37)
7. Consolidation phase for final 3 rounds (Exp 36 Ground Truth, HIGH)
8. Per-model ρ tracking with targeted ITC (Exp 36 Ground Truth, HIGH)
9. Context windowing for long runs (Exp 36 Ground Truth, HIGH)
10. S_k format pre-check with reformat request (Exp 38) — PARTIALLY ADDRESSED (format now accepted)
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

**STALENESS FLAGS (identified during 15 April recovery, pending fix):**
- `.claude/CLAUDE.md` § "What Is NOT Installed" still lists rdkit, biopython,
  scikit-learn, networkx, matplotlib as not installed. All five are present
  (verified via `pip show`). Misleading for fresh instances.
- `docs/MATHEMATICAL_APPENDIX.md` is 1991 lines on disk; prior commit messages
  cite ~2005. 14-line discrepancy, likely minor later trims. Low priority.
- `configs/README.md`, `bench/cdsfl_registry/universal.toml` not yet re-read
  against the 14-tool manifest expansion.

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
