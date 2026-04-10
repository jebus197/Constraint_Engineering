# CDSFL Current State

Generated: 10 April 2026 01:02 BST (2026-04-10T01:02:31+01:00)

---

## Git

- **Branch:** main
- **Last commit:** `0cf2977` Cell type architecture for CDSFL domain generalisation
- **Committed:** 2026-04-09 22:47:32 +0100
- **Remote:** up to date
- **Working tree:** DIRTY — uncommitted changes present

Uncommitted files:
- `M bench/directives/software/software_python_sk.txt`
- `M bench/directives/universal/cdsfl_operational.md`
- `M bench/directives/universal/expert_encoding_template.md`
- `M bench/logs/immune_shadow.log`
- `M bench/reference_runner.py`
- `?? bench/confer_exp38_plan.py`
- `?? bench/logs/confer_exp38_plan/`
- `?? experimental_notes/Exp38_Confer_Synthesis_2026-04-09.md`
- `?? experimental_notes/Exp38_Plan_2026-04-09.md`

---

## Tests

**690 tests collected** (`python3 -m pytest bench/tests/ --co -q`)

---

## Latest Experiment

- **Experiment:** exp37_evidence (#37)
- **Status:** CONVERGED
- **Topology:** star
- **Target:** `bench/evidence.py`
- **Rounds:** 16
- **Total findings:** 257
- **Gamma:** 0.4667
- **Models:** CC2, ChatGPT, Codex, DeepSeek, Gemini
- **Per model:**
  - Gemini: 87
  - ChatGPT: 51
  - DeepSeek: 48
  - CC2: 40
  - Codex: 31
- **Logs:** `/Users/georgejackson/Developer_Projects/Constraint_Engineering/bench/logs/exp37_evidence_20260409T050932Z`

---

## Recent Commits

- `0cf2977 Cell type architecture for CDSFL domain generalisation`
- `2737fd3 Expert encoding template, Python S_k gates, and two confer rounds`
- `647f1e2 S_k solution reliability confer: Codex + Gemini under CDSFL/FFAFP`
- `9d2ac85 Exp 37 forensic analysis, exp36 late-round logs, new modules`
- `f528314 Enhance sv script: auto-update ONBOARDING.md and RECOVERY.md`
- `944ec3e Exp 37 converged: 6 fixes, mathematical lineage, brain signal wiring`
- `9c2ee82 Guard all choices[0] access against empty upstream 500 responses`
- `d848863 Merge remote-tracking branch 'origin/claude/debug-api-500-error-AFfcu'`
- `d773f12 Fix unguarded choices[0] access in OpenRouter and DeepSeek API handlers`
- `e9ee3e3 Fix mark_verified() call signature — takes 1 arg not 2`
