# CDSFL Current State

Generated: 14 May 2026 06:34 BST (2026-05-14T06:34:18+01:00)

---

## Git

- **Branch:** exp39-experimental
- **Last commit:** `ae1de45` fix: launch_exp40.py — load .env at import time so API keys reach the runner
- **Committed:** 2026-05-14 03:05:15 +0100
- **Remote:** ahead by 87
- **Working tree:** DIRTY — uncommitted changes present

Uncommitted files:
- `M bench/exp40_configs/40_gate.json`
- `M bench/fingerprints/CC2.json`
- `M bench/fingerprints/ChatGPT.json`
- `M bench/fingerprints/Codex.json`
- `M bench/fingerprints/DeepSeek.json`
- `M bench/fingerprints/Gemini.json`
- `M bench/logs/immune_pipeline.log`
- `?? bench/logs/exp40_gate_20260514T020550Z/`
- `?? bench/logs/exp40_launch_20260514T015600Z.log`
- `?? bench/logs/exp40_launch_20260514T020001Z.log`
- `?? bench/logs/exp40_launch_20260514T020219Z.log`
- `?? bench/logs/exp40_launch_20260514T020550Z.log`
- `?? bench/logs/exp40_resume_20260514T032658Z.log`
- `?? experimental_notes/Exp40_PostMortem_2026-05-14.md`
- `?? experimental_notes/Exp40_PostMortem_Plain_English_2026-05-14.md`

---

## Tests

**1311 tests collected** (`python3 -m pytest bench/tests/ --co -q`)

---

## Latest Experiment

- **Experiment:** exp40_gate (#40)
- **Status:** WALL_CLOCK_CAP
- **Topology:** star
- **Target:** `bench/dm/_feedback.py`
- **Rounds:** 10
- **Total findings:** 207
- **Gamma:** 0.1433
- **Models:** CC2, ChatGPT, Codex, DeepSeek, Gemini
- **Per model:**
  - DeepSeek: 68
  - Gemini: 61
  - ChatGPT: 37
  - CC2: 26
  - Codex: 15
- **Logs:** `/Users/georgejackson/Developer_Projects/Constraint_Engineering/bench/logs/exp40_gate_20260514T020550Z`

---

## Recent Commits

- `ae1de45 fix: launch_exp40.py — load .env at import time so API keys reach the runner`
- `2fdecbd fix: launch_exp40.py — pass test_article, context_files, domain to RunnerConfig`
- `22adc0b fix: launch_exp40.py — correct run_experiment call signature`
- `d1dba7f fix: bench panel rotation — orchestrator + runner v2 model IDs updated to current frontier`
- `cf24f6d sv: Exp 40 pre-launch docs sweep + two-version note standard (v1.2) + plain-English retrofits`
- `7601985 sv: Exp 40 pre-launch focused Round 3 + three-round synthesis — full convergence, all fold-ins applied`
- `4d4d4f1 sv: Exp 40 pre-launch focused Round 2 outcome — 5/5 clean returns, high-confidence fold-ins applied, paired notes landed`
- `38398fb sv: Exp 40 pre-launch — residuals (a)(b)(c)(d) closed + panel rotation to current frontier + Round 2 confer script built`
- `7cdf846 docs: operational plan — correct sv-prep completed-log dates (22 April → 23 April) after post-compaction resume; add 23 April 05:01 BST sv-landing entry for commit 7c9df2b`
- `7c9df2b sv: founder oversight Q&A debrief post-overnight-shift — honest gap catalogue recorded (5 of 9 G-items fully closed, 3 of 9 specification-only, 1 of 9 partial; four residuals identified beyond the G-list — Exp 39-0 gate contradiction not personally verified, per-finding R_k time-series not addressed, scientific-notation sub-rule not amended into locked cdsfl_note_standard_v1.md, full retroactive F4 closure-state labelling not performed); integration semantics clarified (fold-in-and-test vs Exp 54 factorial run); panel-review status mapped (F1/F2/F3 + Gate C step + Stage 6 design + scope/ordering + RQ6b + K/L/M non-distortion + shadow-promotion-now already reviewed; G2 code correctness + section 2a scope briefs + section 6b trigger specs + G3/G4/G5 coverage + G9 lexicon wording NOT reviewed); three founder decisions now pending (focused confer round scope proposal, G6/G7/G8 path, residuals disposition); new memory file feedback_fix_all_scope_split.md captures lesson that autonomous fix-all windows must decompose target lists into bounded-fix / specification-only / full-sweep at start of window not at debrief; ONBOARDING + RECOVERY + ce_state + operational plan (Desktop + repo mirror) + MEMORY.md index updated; no runtime code changes; HEAD at debrief entry 991cde0 + follow-up 42b737f; documentary-state commit on top`
