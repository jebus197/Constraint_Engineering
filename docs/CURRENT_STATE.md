# CDSFL Current State

Generated: 12 April 2026 13:05 BST (2026-04-12T13:05:22+01:00)

---

## Git

- **Branch:** exp39-experimental
- **Last commit:** `42779ad` sv: Exp 39 sub-experiment structure. 36 schema elements → 13 sub-experiments (0-M). 2 confer rounds (CX+GE). One variable at a time, maths first.
- **Committed:** 2026-04-12 03:25:33 +0100
- **Remote:** ahead by 11
- **Working tree:** DIRTY — uncommitted changes present

Uncommitted files:
- `M bench/cdsfl_registry/schema.toml`
- `M bench/dm/_types.py`
- `M bench/experiment_11_orchestrator.py`
- `M bench/immune_agents.py`
- `M bench/logs/immune_pipeline.log`
- `M bench/reference_runner.py`
- `M bench/runner_core.py`
- `M resources/ONBOARDING.md`
- `M resources/RECOVERY.md`
- `?? bench/cdsfl_registry/domains/immune/statistics.toml`
- `?? bench/cdsfl_registry/domains/statistics.toml`
- `?? bench/exp39_config.json`
- `?? bench/exp39_configs/`
- `?? bench/launch_exp39.py`

---

## Tests

**762 tests collected** (`python3 -m pytest bench/tests/ --co -q`)

---

## Latest Experiment

- **Experiment:** exp38_ouroboros (#38)
- **Status:** WALL_CLOCK_CAP
- **Topology:** star
- **Target:** `bench/reference_runner.py`
- **Rounds:** 24
- **Total findings:** 545
- **Gamma:** 0.5097
- **Models:** CC2, ChatGPT, Codex, DeepSeek, Gemini
- **Per model:**
  - Gemini: 181
  - ChatGPT: 133
  - Codex: 102
  - DeepSeek: 99
  - CC2: 30
- **Logs:** `/Users/georgejackson/Developer_Projects/Constraint_Engineering/bench/logs/exp38_ouroboros_20260411T041938Z`

---

## Recent Commits

- `42779ad sv: Exp 39 sub-experiment structure. 36 schema elements → 13 sub-experiments (0-M). 2 confer rounds (CX+GE). One variable at a time, maths first.`
- `c522468 sv: Exp 39 fixes built + scope refinement. 22+ fixes, 3 confer rounds, 762 tests pass. Dynamic budgets, adaptive ITC, DRY fix, ARCHITECTURE.md trade-offs. Scope: Expert Encodings, HIL gate, Gemini switch, Macrophage shadow.`
- `491b08d sv: sv script fix — correct report parsing + manual content preservation`
- `d7fc4db Fix sv auto-generated sections: restore qualitative Exp 38 terminal state`
- `a710306 sv: Exp 38 complete — 24 rounds, 169 canonical, gamma 0.510, wall clock cap. Findings + sv fix + Exp 39 plan`
- `84d2c96 sv: Exp 38 R12 state — Phase 0 override bug identified, 6 runner bugs found`
- `b78bc6a sv: Exp 38 live run state save — R0-R6 complete, R7 in progress`
- `bcd1914 Fix 6 confer-verified bugs: getter purity, merge floor, panel size, exhaustion`
- `96a1b1c Confer Round 3: CX+GE review of contextual implementations`
- `83480b1 Exp 38 contextual decision logic: 4 evidence-based replacements for static rules`
