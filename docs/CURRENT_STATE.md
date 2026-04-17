# CDSFL Current State

Generated: 17 April 2026 05:12 BST (2026-04-17T05:12:08+01:00)

---

## Git

- **Branch:** exp39-experimental
- **Last commit:** `54d956e` sv: Exp 40-54 execution plan + runner v2 scaffold + shadow-log audit
- **Committed:** 2026-04-17 04:41:45 +0100
- **Remote:** ahead by 57
- **Working tree:** DIRTY — uncommitted changes present

Uncommitted files:
- `M bench/logs/immune_pipeline.log`
- `M bench/reference_runner_v2.py`
- `M bench/runner_core.py`
- `M resources/RECOVERY.md`
- `?? bench/dm/_diversity.py`
- `?? bench/dm/_round_context.py`
- `?? bench/exp40_configs/`
- `?? bench/launch_exp40.py`
- `?? bench/tests/test_deepseek_header_adapter.py`
- `?? bench/tests/test_diversity_metric.py`
- `?? bench/tests/test_gamma_alt_convergence.py`
- `?? bench/tests/test_macrophage_fallback.py`
- `?? bench/tests/test_round_context.py`
- `?? experimental_notes/Exp40_Implementation_Progress_2026-04-17.md`

---

## Tests

**992 tests collected** (`python3 -m pytest bench/tests/ --co -q`)

---

## Latest Experiment

- **Experiment:** exp39_0_gate (#39)
- **Status:** INCOMPLETE
- **Topology:** star
- **Target:** `bench/runner_core.py`
- **Rounds:** 6
- **Total findings:** 111
- **Gamma:** 0.4612
- **Models:** CC2, ChatGPT, Codex, DeepSeek, Gemini
- **Per model:**
  - CC2: 28
  - Codex: 25
  - ChatGPT: 25
  - Gemini: 21
  - DeepSeek: 12
- **Logs:** `/Users/georgejackson/Developer_Projects/Constraint_Engineering/bench/logs/exp39_0_gate_20260413T193320Z`

---

## Recent Commits

- `54d956e sv: Exp 40-54 execution plan + runner v2 scaffold + shadow-log audit`
- `cc6cc1a sv: §18 round-2 implementation + round-3 5-panel review + documentation refresh`
- `d11457b docs: add refresh-sweep summary note (third-party voice + plain-English + AI-gender-neutrality)`
- `0651974 docs: reformat 7-day notes for third-party voice + plain English, remove AI-gendered pronouns`
- `4580465 sv: §17+§18 panel review and round-2 mathematical convergence — 5/5 unanimous on channel reassignment (R_k → η_int + FFAFP admissibility), 2×2 factorial for D3, ν_k prohibition explicit, three founder decisions pending`
- `71ab374 sv: §18 divergence directive — CDSFL's bold-conjectures arm (invention engine)`
- `81cfb97 sv: sv-script auto-staging fix + plain-English feedback channel docs`
- `52391aa fix: add missing feedback-channel artefacts referenced by f29d0e9`
- `f29d0e9 sv: feedback channel (Phase 10) — measurement-to-correction loop closed`
- `a6ee7b4 sv: Stage 6 + FFAFP admissibility set now in model-facing directives`
