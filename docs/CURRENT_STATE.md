# CDSFL Current State

Generated: 16 April 2026 02:50 BST (2026-04-16T02:50:13+01:00)

---

## Git

- **Branch:** exp39-experimental
- **Last commit:** `d11457b` docs: add refresh-sweep summary note (third-party voice + plain-English + AI-gender-neutrality)
- **Committed:** 2026-04-16 01:08:37 +0100
- **Remote:** ahead by 55
- **Working tree:** DIRTY — uncommitted changes present

Uncommitted files:
- `M bench/cdsfl_registry/schema.toml`
- `M bench/cdsfl_registry/universal.toml`
- `M bench/directives/universal/cdsfl_operational.md`
- `M bench/dm/_divergence.py`
- `M bench/logs/immune_pipeline.log`
- `M bench/tests/test_divergence_directive.py`
- `M resources/ONBOARDING.md`
- `M resources/RECOVERY.md`
- `?? bench/confer_divergence_round3_final.py`
- `?? bench/logs/confer_divergence_round3_final/`
- `?? bench/verify_round2_implementation.py`
- `?? experimental_notes/Divergence_Round2_Implementation_2026-04-16.md`
- `?? experimental_notes/Session_Summary_2026-04-16.md`

---

## Tests

**935 tests collected** (`python3 -m pytest bench/tests/ --co -q`)

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

- `d11457b docs: add refresh-sweep summary note (third-party voice + plain-English + AI-gender-neutrality)`
- `0651974 docs: reformat 7-day notes for third-party voice + plain English, remove AI-gendered pronouns`
- `4580465 sv: §17+§18 panel review and round-2 mathematical convergence — 5/5 unanimous on channel reassignment (R_k → η_int + FFAFP admissibility), 2×2 factorial for D3, ν_k prohibition explicit, three founder decisions pending`
- `71ab374 sv: §18 divergence directive — CDSFL's bold-conjectures arm (invention engine)`
- `81cfb97 sv: sv-script auto-staging fix + plain-English feedback channel docs`
- `52391aa fix: add missing feedback-channel artefacts referenced by f29d0e9`
- `f29d0e9 sv: feedback channel (Phase 10) — measurement-to-correction loop closed`
- `a6ee7b4 sv: Stage 6 + FFAFP admissibility set now in model-facing directives`
- `8da9551 sv: Tranches A/B/C recovery state — B-Cell manifest, CLAUDE.md staleness patch`
- `2f22a8a Tranche C: manifest-driven B-Cell dispatch (TOML registry + loader refactor)`
