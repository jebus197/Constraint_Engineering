# CDSFL Current State

Generated: 13 April 2026 17:36 BST (2026-04-13T17:36:55+01:00)

---

## Git

- **Branch:** exp39-experimental
- **Last commit:** `2f8f8bc` Fix burst_mode config override + atomic runner checkpoint + monitoring
- **Committed:** 2026-04-13 06:12:33 +0100
- **Remote:** ahead by 35
- **Working tree:** DIRTY — uncommitted changes present

Uncommitted files:
- `M bench/decomposed_dispatch.py`
- `M bench/exp39_configs/39_0_gate.json`
- `M bench/fingerprints/CC2.json`
- `M bench/fingerprints/ChatGPT.json`
- `M bench/fingerprints/Codex.json`
- `M bench/fingerprints/DeepSeek.json`
- `M bench/fingerprints/Gemini.json`
- `M bench/logs/immune_pipeline.log`
- `M bench/reference_runner.py`
- `M bench/run_benchmark.py`
- `M resources/ONBOARDING.md`
- `M resources/RECOVERY.md`
- `?? bench/CLAUDE_CODE_PROVIDER_FIX.md`
- `?? bench/logs/confer_exp39_prelaunch/prelaunch_cc2_20260413T050230Z.json`
- `?? bench/logs/confer_exp39_prelaunch/prelaunch_cc2_20260413T050230Z.txt`

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

- `2f8f8bc Fix burst_mode config override + atomic runner checkpoint + monitoring`
- `e64bb14 Fix 4 deferred non-blocking items from CC2 runner review`
- `cb8a936 Fix 4 additional blockers from delayed sub-agent results (10-stream review complete)`
- `2279adb Fix all pre-launch review blockers — 11 fixes from 10-stream review`
- `83dd7ab HIL gate, domain TOMLs, PE FFAFP+Meta SRP HARD constraints, FFAFP naming fix`
- `0f7c553 sv: Fix all Codex/Gemini confer observations — domain plumbing, enum serialization, round detail, provenance, resume, shadow parity, regulatory structure`
- `2488fa1 sv: Exp 39 readiness assessment — 39-0 ready to run, provenance + launch fixes`
- `a8fb729 Fix launch path: --test-article no longer blocks --config-only invocation`
- `f57d6ce Fix provenance pipeline: origin_type on all findings, registry capture, macrophage_cell.py committed`
- `bd09f88 sv: Macrophage/Ouroboros cell type split — 793 tests, 4 confer rounds, provenance schema`
