# CDSFL Current State

Generated: 12 April 2026 03:25 BST (2026-04-12T03:25:32+01:00)

---

## Git

- **Branch:** exp39-experimental
- **Last commit:** `c522468` sv: Exp 39 fixes built + scope refinement. 22+ fixes, 3 confer rounds, 762 tests pass. Dynamic budgets, adaptive ITC, DRY fix, ARCHITECTURE.md trade-offs. Scope: Expert Encodings, HIL gate, Gemini switch, Macrophage shadow.
- **Committed:** 2026-04-12 02:03:56 +0100
- **Remote:** ahead by 10
- **Working tree:** DIRTY — uncommitted changes present

Uncommitted files:
- `A  experimental_notes/Exp39_Revised_Scope_2026-04-12.md`
- `M resources/ONBOARDING.md`
- `M resources/RECOVERY.md`

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

- `c522468 sv: Exp 39 fixes built + scope refinement. 22+ fixes, 3 confer rounds, 762 tests pass. Dynamic budgets, adaptive ITC, DRY fix, ARCHITECTURE.md trade-offs. Scope: Expert Encodings, HIL gate, Gemini switch, Macrophage shadow.`
- `491b08d sv: sv script fix — correct report parsing + manual content preservation`
- `d7fc4db Fix sv auto-generated sections: restore qualitative Exp 38 terminal state`
- `a710306 sv: Exp 38 complete — 24 rounds, 169 canonical, gamma 0.510, wall clock cap. Findings + sv fix + Exp 39 plan`
- `84d2c96 sv: Exp 38 R12 state — Phase 0 override bug identified, 6 runner bugs found`
- `b78bc6a sv: Exp 38 live run state save — R0-R6 complete, R7 in progress`
- `bcd1914 Fix 6 confer-verified bugs: getter purity, merge floor, panel size, exhaustion`
- `96a1b1c Confer Round 3: CX+GE review of contextual implementations`
- `83480b1 Exp 38 contextual decision logic: 4 evidence-based replacements for static rules`
- `1703ed1 Exp 38 experimental: 17 fixes, 3-layer DC v2 classification, promotion gate`
