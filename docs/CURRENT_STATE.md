# CDSFL Current State

Generated: 15 May 2026 23:24 BST (2026-05-15T23:24:08+01:00)

---

## Git

- **Branch:** exp39-experimental
- **Last commit:** `553d41d` sv-followup: operational tracker HEAD 3bbf2c7->7ecbf26 post-sv
- **Committed:** 2026-05-15 23:13:44 +0100
- **Remote:** ahead by 99
- **Working tree:** DIRTY — uncommitted changes present

Uncommitted files:
- `M experimental_notes/CDSFL_Agent_Operational_Plan.md`
- `M resources/RECOVERY.md`
- `?? bench/confer_exp40_architectural_2026-05-15.py`
- `?? bench/logs/confer_exp40_architectural_2026-05-15/`
- `?? experimental_notes/Exp40_Architectural_Confer_Outcome_2026-05-15.md`
- `?? experimental_notes/Exp40_Architectural_Confer_Outcome_Plain_English_2026-05-15.md`

---

## Tests

**1404 tests collected** (`python3 -m pytest bench/tests/ --co -q`)

---

## Latest Experiment

- **Experiment:** exp40_gate (#40)
- **Status:** INCOMPLETE
- **Topology:** star
- **Target:** `bench/dm/_feedback.py`
- **Rounds:** 17
- **Total findings:** 280
- **Gamma:** 0.0342
- **Models:** CC2, ChatGPT, Codex, DeepSeek, Gemini
- **Per model:**
  - Gemini: 94
  - DeepSeek: 86
  - ChatGPT: 45
  - CC2: 33
  - Codex: 22
- **Logs:** `/Users/georgejackson/Developer_Projects/Constraint_Engineering/bench/logs/exp40_gate_20260514T020550Z`

---

## Recent Commits

- `553d41d sv-followup: operational tracker HEAD 3bbf2c7->7ecbf26 post-sv`
- `7ecbf26 sv: Exp 40 continuation + post-continuation fix tranche (1a-1e parser/classifier/RT-v2/ITC/reformat), G7 merge-arbitration module (default-disabled), DeepSeek Phase-1 reasoning_content fix, gamma-input triple-cross-verification, codex false-positive resolution; 229 tests pass; paired post-mortems`
- `3bbf2c7 feat: launcher_core shared infrastructure + G7 merge-deadlock design`
- `7f3066b fix: ITC CAPABILITY_MISMATCH false positive on verdict-heavy rounds`
- `a8a33c2 feat: make Bugzilla paradigm explicit to the panel`
- `b2f3444 fix: parse_admissibility_block — FINDING_ID terminator regression`
- `9891bda fix: Stage 6 calibrator int-flaw_class crash + regression tests`
- `26b28f8 fix: gamma input — use post-reconciliation novelty, not pre-`
- `8cb1fbe feat: integrate Bugzilla CLOSED-loop into runner v2 state machine`
- `12ad362 feat: Bugzilla CLOSED-loop module + Exp 40 validation`
