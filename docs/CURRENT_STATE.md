# CDSFL Current State

Generated: 11 April 2026 19:02 BST (2026-04-11T19:02:37+01:00)

---

## Git

- **Branch:** exp38-experimental
- **Last commit:** `84d2c96` sv: Exp 38 R12 state — Phase 0 override bug identified, 6 runner bugs found
- **Committed:** 2026-04-11 11:45:46 +0100
- **Remote:** ahead by 6
- **Working tree:** DIRTY — uncommitted changes present

Uncommitted files:
- `M .claude/CLAUDE.md`
- `M bench/fingerprints/CC2.json`
- `M bench/fingerprints/ChatGPT.json`
- `M bench/fingerprints/Codex.json`
- `M bench/fingerprints/DeepSeek.json`
- `M bench/fingerprints/Gemini.json`
- `M bench/logs/exp38_live_output.log`
- `M bench/logs/exp38_ouroboros_20260411T041938Z/checkpoint.json`
- `M bench/logs/exp38_ouroboros_20260411T041938Z/runner_state.json`
- `M bench/logs/immune_pipeline.log`
- `M experimental_notes/Exp38_Ouroboros_Findings_2026-04-11.md`
- `M resources/ONBOARDING.md`
- `M resources/RECOVERY.md`
- `M scripts/cdsfl_sv.py`
- `?? bench/logs/exp38_ouroboros_20260411T041938Z/completion_signal.json`

---

## Tests

**762 tests collected** (`python3 -m pytest bench/tests/ --co -q`)

---

## Latest Experiment

- **Experiment:** exp38_ouroboros (#38)
- **Status:** UNKNOWN
- **Topology:** star
- **Target:** `bench/reference_runner.py`
- **Rounds:** 24
- **Total findings:** 545
- **Gamma:** 0.0000
- **Models:** CC2, ChatGPT, Codex, DeepSeek, Gemini
- **Logs:** `/Users/georgejackson/Developer_Projects/Constraint_Engineering/bench/logs/exp38_ouroboros_20260411T041938Z`

---

## Recent Commits

- `84d2c96 sv: Exp 38 R12 state — Phase 0 override bug identified, 6 runner bugs found`
- `b78bc6a sv: Exp 38 live run state save — R0-R6 complete, R7 in progress`
- `bcd1914 Fix 6 confer-verified bugs: getter purity, merge floor, panel size, exhaustion`
- `96a1b1c Confer Round 3: CX+GE review of contextual implementations`
- `83480b1 Exp 38 contextual decision logic: 4 evidence-based replacements for static rules`
- `1703ed1 Exp 38 experimental: 17 fixes, 3-layer DC v2 classification, promotion gate`
- `c2f9167 Add Perplexity Computer competitive analysis to experimental notes`
- `76bfdb8 Whole-body topology diagram: biological architecture map`
- `412a5be Exp 38 Round 0: ouroboros results, verification, confer logs`
- `032810b Burst architecture, runner fixes, and Exp 38 infrastructure`
