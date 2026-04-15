# CDSFL Current State

Generated: 15 April 2026 22:49 BST (2026-04-15T22:49:28+01:00)

---

## Git

- **Branch:** exp39-experimental
- **Last commit:** `81cfb97` sv: sv-script auto-staging fix + plain-English feedback channel docs
- **Committed:** 2026-04-15 21:13:27 +0100
- **Remote:** ahead by 51
- **Working tree:** DIRTY — uncommitted changes present

Uncommitted files:
- `M bench/cdsfl_registry/schema.toml`
- `M bench/cdsfl_registry/universal.toml`
- `M bench/directives/universal/cdsfl_core_formal.md`
- `M bench/directives/universal/cdsfl_operational.md`
- `M bench/logs/immune_pipeline.log`
- `M resources/ONBOARDING.md`
- `M resources/RECOVERY.md`
- `?? bench/dm/_divergence.py`
- `?? bench/tests/test_divergence_directive.py`
- `?? experimental_notes/Divergence_Directive_Implementation_2026-04-15.md`
- `?? experimental_notes/Invention_Engine_Divergence_Directive_2026-04-15.md`

---

## Tests

**912 tests collected** (`python3 -m pytest bench/tests/ --co -q`)

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

- `81cfb97 sv: sv-script auto-staging fix + plain-English feedback channel docs`
- `52391aa fix: add missing feedback-channel artefacts referenced by f29d0e9`
- `f29d0e9 sv: feedback channel (Phase 10) — measurement-to-correction loop closed`
- `a6ee7b4 sv: Stage 6 + FFAFP admissibility set now in model-facing directives`
- `8da9551 sv: Tranches A/B/C recovery state — B-Cell manifest, CLAUDE.md staleness patch`
- `2f22a8a Tranche C: manifest-driven B-Cell dispatch (TOML registry + loader refactor)`
- `0c1de8e Tranche B: 5 new B-Cell specialist wrappers + dispatch + 4 TOML updates`
- `6838160 Tranche A: housekeeping — crosshair note fix + sv sequential-reading protocol`
- `d9f8f82 chore: commit Stage 6 confer residuals from prior session`
- `00abd52 sv: Domain tool wiring — 9 B-Cell specialist wrappers, 5 TOMLs, 793 tests green (inc. residual Stage 6 runner/ouroboros diagnostics)`
