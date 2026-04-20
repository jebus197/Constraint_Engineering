# CDSFL Current State

Generated: 20 April 2026 11:33 BST (2026-04-20T11:33:37+01:00)

---

## Git

- **Branch:** exp39-experimental
- **Last commit:** `2c966ca` sv: housekeeping part 2 — logs two-subfolder policy + Merkle sealing + examples/resources/ READMEs + CC1 memory mirror
- **Committed:** 2026-04-20 04:46:46 +0100
- **Remote:** ahead by 69
- **Working tree:** DIRTY — uncommitted changes present

Uncommitted files:
- `M bench/confer_exp40_prelaunch_round1.py`
- `M resources/ONBOARDING.md`
- `M resources/RECOVERY.md`
- `?? bench/confer_exp40_prelaunch_round2a.py`
- `?? bench/confer_exp40_prelaunch_round2b.py`
- `?? bench/confer_exp40_prelaunch_round3.py`
- `?? bench/confer_exp40_prelaunch_round3b.py`
- `?? bench/logs/confer_exp40_prelaunch_round1/`
- `?? bench/logs/confer_exp40_prelaunch_round2a/`
- `?? bench/logs/confer_exp40_prelaunch_round2b/`
- `?? bench/logs/confer_exp40_prelaunch_round3/`
- `?? bench/logs/confer_exp40_prelaunch_round3b/`
- `?? experimental_notes/Exp40_Prelaunch_Round1_Panel_2026-04-20.md`
- `?? experimental_notes/Exp40_Prelaunch_Rounds2_to_3B_2026-04-20.md`

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

- `2c966ca sv: housekeeping part 2 — logs two-subfolder policy + Merkle sealing + examples/resources/ READMEs + CC1 memory mirror`
- `742e7aa sv: housekeeping bundle — sq MC command + onboarding script refactor + README topology embed + stale bootstrap cleanup`
- `436f9a0 sv: 20 April README promotion + regulatory-compliance consolidation (FOUNDERS_NOTES revisions + README v3→canonical + PAPER Part V regulatory alignment + EXTENDED_RATIONALE auditable cognitive infrastructure + new docs/COMPLIANCE_FRAMEWORK.md with EU AI Act/GDPR/NIST AI RMF/ISO42001 mapping + 6 supplementary-artefact templates)`
- `04bc286 sv: broader documentation staleness sweep — 6-batch pass (FOUNDERS_NOTES + SHORTCUTS + ARCHITECTURE + topology_formal + EXTENDED_RATIONALE + EXPERIMENTAL_RESULTS + PAPER) with paired TTS + experimental_notes mirrors`
- `145e9e2 sv: README v3 13-point corrections + rg MC command introduction`
- `7334e49 sv: README v3 draft + novelty-synthesis gap closure + apply-drafted-edits directive`
- `ef50d4e sv: expert-encoding framing correction + quote/synthesis standing directives + README v2 draft`
- `7326a04 sv: Exp 40 Stage 3 closure — Phase A + B landed, 1250 tests, residual items gated`
- `6580737 docs: sync Exp40 progress doc with Phase A + B commit state`
- `bdfc93a exp40: Phase B fixes 1D.3/1E.3/1E.4/1E.5/1E.8/1E.9/1E.11/1E.12 (200+ tests)`
