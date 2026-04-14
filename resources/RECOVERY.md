# Recovery Protocol

Last updated: 14 April 2026 19:27 BST

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
## Current Pending Work (14 April 2026 18:37 BST)

793 tests pass (full regression 17m 21s, immune subset 136/136). Branch: `exp39-experimental`.

**SESSION 14 APRIL (evening) — DOMAIN TOOL WIRING:**
- 9 subprocess wrappers added to `bench/immune_agents.py` (lines 1114–1734)
  covering pint, uncertainties, stoichiometry (regex+collections), PuLP, astropy,
  mypy, ruff, bandit, dis. Additive only — no existing functions modified.
- 9 new `elif` branches appended to `_specialist_b_cell_dispatch()`
  (lines 1913–1931) AFTER existing sympy/z3/statsmodels/scipy branches.
  First-definitive-result-wins semantics preserved.
- 5 TOMLs in `bench/cdsfl_registry/domains/immune/` extended with new tool names
  (physics, engineering, chemistry, biology, cross_domain). `cs_software.toml`
  already referenced code tools from a prior session.
- 2 bugs found in smoke tests and fixed before regression:
  - `immune_agents.py:1131` regex `+` → `*` (single-letter units `m`, `s`, `N`
    were being silently skipped by the 2+-char regex).
  - `immune_agents.py:1626` ruff `--output-format=text` → `concise` (ruff
    rejects `text` and returns rc=2).
- Full regression green: 793/793 passing, zero regressions vs. prior commit.
- Shadow containment verified: wrappers run inside `_specialist_b_cell_dispatch()`
  which runs in shadow mode in Exp 39. Verdicts captured via `specialist_verdicts`
  but NOT extended into `all_verdicts`. Promotion is a single-line flip at
  `reference_runner.py` ~3741, not touched.
- Verified this session did NOT alter:
  - reference_runner.py (11-line Macrophage diagnostic diff is from prior Stage 6
    session, mtime 16:42 predates my first edit at 17:23)
  - ouroboros_cell.py (27-line HARD FIXes also from prior Stage 6 session,
    mtime 16:40)
  - dm/_convergence.py, dm/_types.py, dm/_manager.py, dm/_shadow_extensions.py
    (the ge/cx 2-model and 5-panel review fixes all live here — untouched)
  - docs/MATHEMATICAL_APPENDIX.md
- Notes: `experimental_notes/Domain_Tool_Wiring_2026-04-14.md`
- TTS: `~/Desktop/CDSFL_tts/Domain_Tool_Wiring_2026-04-14.txt`
- Hygiene: one API 500 mid-session (triggered by ~580-line single Edit).
  Recovery via `cdsfl_recover.py --full` clean. Resumed with one edit per
  tool call, targeted greps, single-claim smoke tests.
- CLAUDE.md stale note fixed: `pint`, `astropy`, `pulp` moved from
  "NOT installed" list into STEM tools table with correct versions.

**SESSION 14 APRIL (earlier) — TOOL PERMISSIONS + ν_k DESIGN + STAGE 6 APPENDIX:**

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
1. Wire OpenRouter tool-use (add `tools` parameter to `call_openrouter()`)
2. Wire DeepSeek specialist role (Phase 6) into pipeline
3. Implement ν_k metric in O1 (Phase 7) — design complete, code pending
4. Add Unpaywall + CORE + OpenAlex source adapters to O1
5. Re-run Exp 39-0 gate test with all fixes in place
6. Carry forward remaining 7 lessons from Exp 36-38

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
   **DONE 14 April 2026 (evening session).** 9 wrappers + 9 dispatch branches + 5 TOML
   updates landed. 793 tests green. Shadow mode preserved. Promotion (single-line flip
   at `reference_runner.py` ~3741) still pending HIL decision.
5. Severity fusion (§7.7) for gate output synthesis
6. Sycophancy detection (§7.5)
7. O1 calibration: sensitivity dial, circuit breaker, semantic clustering
8. MC command sync across all reference locations
9. Phase 9 (research write-up) — deferred post-Exp 39
10. Implementation plan: `~/.claude/plans/effervescent-watching-platypus.md` — Phase 6
    (B4 specialist dispatch) complete this session. Phases 1–5, 7, 8 still pending.
11. Prompt schema as first-class tested artefact (not string literal in 3700-line file)
12. OpenRouter tool-use mode for panel models (CC2 has Bash, others need function calling)
13. Wire hypothesis / beartype / icontract / pyright / mutmut / coverage into cells
    (installed but not routed — depends on cell design decisions)
14. Install crosshair if symbolic execution becomes needed for a domain
15. **Prior session uncommitted artefacts** (not from my session — flagged for review):
    `bench/dm/_shadow_stage6.py` (imported by `reference_runner.py` via try/except —
    missing from fresh clone), `bench/confer_stage6_{full,model,r2}.py`,
    three `experimental_notes/Stage6_*_2026-04-14.md` syntheses,
    `bench/logs/confer_stage6_*/`. All untracked since commit 532a890.

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
