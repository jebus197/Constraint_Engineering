# CDSFL Current State

Generated: 20 April 2026 02:20 BST (2026-04-20T02:20:11+01:00)

---

## Git

- **Branch:** exp39-experimental
- **Last commit:** `04bc286` sv: broader documentation staleness sweep — 6-batch pass (FOUNDERS_NOTES + SHORTCUTS + ARCHITECTURE + topology_formal + EXTENDED_RATIONALE + EXPERIMENTAL_RESULTS + PAPER) with paired TTS + experimental_notes mirrors
- **Committed:** 2026-04-19 13:48:19 +0100
- **Remote:** ahead by 66
- **Working tree:** DIRTY — uncommitted changes present

Uncommitted files:
- `M PAPER.md`
- `M README.md`
- `M docs/EXPERIMENTAL_RESULTS.md`
- `M docs/EXTENDED_RATIONALE.md`
- `M docs/FOUNDERS_NOTES.md`
- `M resources/ONBOARDING.md`
- `M resources/RECOVERY.md`
- `?? docs/COMPLIANCE_FRAMEWORK.md`
- `?? experimental_notes/Founders_Notes_Revisions_2026-04-20.md`
- `?? experimental_notes/README_Promotion_2026-04-20.md`
- `?? experimental_notes/Regulatory_Compliance_Framework_2026-04-20.md`

---

## Tests

**1250 tests collected** (`python3 -m pytest bench/tests/ --co -q`)

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

- `04bc286 sv: broader documentation staleness sweep — 6-batch pass (FOUNDERS_NOTES + SHORTCUTS + ARCHITECTURE + topology_formal + EXTENDED_RATIONALE + EXPERIMENTAL_RESULTS + PAPER) with paired TTS + experimental_notes mirrors`
- `145e9e2 sv: README v3 13-point corrections + rg MC command introduction`
- `7334e49 sv: README v3 draft + novelty-synthesis gap closure + apply-drafted-edits directive`
- `ef50d4e sv: expert-encoding framing correction + quote/synthesis standing directives + README v2 draft`
- `7326a04 sv: Exp 40 Stage 3 closure — Phase A + B landed, 1250 tests, residual items gated`
- `6580737 docs: sync Exp40 progress doc with Phase A + B commit state`
- `bdfc93a exp40: Phase B fixes 1D.3/1E.3/1E.4/1E.5/1E.8/1E.9/1E.11/1E.12 (200+ tests)`
- `8b8682d exp40: Phase A fixes 1D.5/1D.6/1E.6/1E.7/1E.10 (98 tests)`
- `834e65c sv: Exp 40 runner v2 - γ-alt convergence + Macrophage fallback + DeepSeek parser + round-context helpers + diversity metric + Exp 40 config/launcher (57 new tests)`
- `54d956e sv: Exp 40-54 execution plan + runner v2 scaffold + shadow-log audit`
