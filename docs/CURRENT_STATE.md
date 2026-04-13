# CDSFL Current State

Generated: 13 April 2026 18:51 BST (2026-04-13T18:51:57+01:00)

---

## Git

- **Branch:** exp39-experimental
- **Last commit:** `d54a8e6` sv: Exp 39-0 complete (4 rounds, 78 findings, γ=0.798), FFAFP+R_k decomposed dispatch fix, provider fix, oscillating R_k compliance identified
- **Committed:** 2026-04-13 17:36:57 +0100
- **Remote:** ahead by 36
- **Working tree:** DIRTY — uncommitted changes present

Uncommitted files:
- `M bench/logs/immune_pipeline.log`
- `M bench/reference_runner.py`
- `M resources/ONBOARDING.md`
- `M resources/RECOVERY.md`
- `?? bench/CLAUDE_CODE_PROVIDER_FIX.md`
- `?? bench/logs/confer_exp39_prelaunch/prelaunch_cc2_20260413T050230Z.json`
- `?? bench/logs/confer_exp39_prelaunch/prelaunch_cc2_20260413T050230Z.txt`
- `?? bench/logs/confer_exp39_prelaunch/prelaunch_chatgpt_20260413T050230Z.json`
- `?? bench/logs/confer_exp39_prelaunch/prelaunch_chatgpt_20260413T050230Z.txt`
- `?? bench/logs/confer_exp39_prelaunch/prelaunch_codex_20260413T050230Z.json`
- `?? bench/logs/confer_exp39_prelaunch/prelaunch_codex_20260413T050230Z.txt`
- `?? bench/logs/confer_exp39_prelaunch/prelaunch_deepseek_20260413T050230Z.json`
- `?? bench/logs/confer_exp39_prelaunch/prelaunch_deepseek_20260413T050230Z.txt`
- `?? bench/logs/confer_exp39_prelaunch/prelaunch_gemini_20260413T050230Z.json`
- `?? bench/logs/confer_exp39_prelaunch/prelaunch_gemini_20260413T050230Z.txt`

---

## Tests

**793 tests collected** (`python3 -m pytest bench/tests/ --co -q`)

---

## Latest Experiment

- **Experiment:** exp39_0_gate (#39)
- **Status:** INCOMPLETE
- **Topology:** star
- **Target:** `bench/reference_runner.py`
- **Rounds:** 4
- **Total findings:** 78
- **Gamma:** 0.7980
- **Models:** CC2, ChatGPT, Codex, DeepSeek, Gemini
- **Per model:**
  - Gemini: 36
  - Codex: 16
  - ChatGPT: 13
  - CC2: 10
  - DeepSeek: 3
- **Logs:** `/Users/georgejackson/Developer_Projects/Constraint_Engineering/bench/logs/exp39_0_gate_20260413T054642Z`

---

## Recent Commits

- `d54a8e6 sv: Exp 39-0 complete (4 rounds, 78 findings, γ=0.798), FFAFP+R_k decomposed dispatch fix, provider fix, oscillating R_k compliance identified`
- `2f8f8bc Fix burst_mode config override + atomic runner checkpoint + monitoring`
- `e64bb14 Fix 4 deferred non-blocking items from CC2 runner review`
- `cb8a936 Fix 4 additional blockers from delayed sub-agent results (10-stream review complete)`
- `2279adb Fix all pre-launch review blockers — 11 fixes from 10-stream review`
- `83dd7ab HIL gate, domain TOMLs, PE FFAFP+Meta SRP HARD constraints, FFAFP naming fix`
- `0f7c553 sv: Fix all Codex/Gemini confer observations — domain plumbing, enum serialization, round detail, provenance, resume, shadow parity, regulatory structure`
- `2488fa1 sv: Exp 39 readiness assessment — 39-0 ready to run, provenance + launch fixes`
- `a8fb729 Fix launch path: --test-article no longer blocks --config-only invocation`
- `f57d6ce Fix provenance pipeline: origin_type on all findings, registry capture, macrophage_cell.py committed`
