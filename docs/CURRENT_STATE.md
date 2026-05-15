# CDSFL Current State

Generated: 15 May 2026 23:12 BST (2026-05-15T23:12:29+01:00)

---

## Git

- **Branch:** exp39-experimental
- **Last commit:** `3bbf2c7` feat: launcher_core shared infrastructure + G7 merge-deadlock design
- **Committed:** 2026-05-15 03:22:07 +0100
- **Remote:** ahead by 97
- **Working tree:** DIRTY — uncommitted changes present

Uncommitted files:
- `M bench/decomposed_dispatch.py`
- `M bench/dm/_sk_format.py`
- `M bench/exp40_configs/40_gate.json`
- `M bench/fingerprints/CC2.json`
- `M bench/fingerprints/ChatGPT.json`
- `M bench/fingerprints/Codex.json`
- `M bench/fingerprints/DeepSeek.json`
- `M bench/fingerprints/Gemini.json`
- `M bench/immune_agents.py`
- `M bench/insect_brain.py`
- `M bench/launch_exp40.py`
- `M bench/launcher_core.py`
- `M bench/logs/exp40_gate_20260514T020550Z/checkpoint.json`
- `M bench/logs/exp40_gate_20260514T020550Z/completion_signal.json`
- `M bench/logs/exp40_gate_20260514T020550Z/exp40_gate_report.json`

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

- `3bbf2c7 feat: launcher_core shared infrastructure + G7 merge-deadlock design`
- `7f3066b fix: ITC CAPABILITY_MISMATCH false positive on verdict-heavy rounds`
- `a8a33c2 feat: make Bugzilla paradigm explicit to the panel`
- `b2f3444 fix: parse_admissibility_block — FINDING_ID terminator regression`
- `9891bda fix: Stage 6 calibrator int-flaw_class crash + regression tests`
- `26b28f8 fix: gamma input — use post-reconciliation novelty, not pre-`
- `8cb1fbe feat: integrate Bugzilla CLOSED-loop into runner v2 state machine`
- `12ad362 feat: Bugzilla CLOSED-loop module + Exp 40 validation`
- `35c44b6 fix: decomposed-dispatch synthesis empty-response fallback`
- `f3684a3 sv: Exp 40 launch + complete — first experiment in arc closed, post-mortem written`
