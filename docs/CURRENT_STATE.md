# CDSFL Current State

Generated: 12 July 2026 02:19 BST (2026-07-12T02:19:37+01:00)

---

## Git

- **Branch:** exp39-experimental
- **Last commit:** `b656549` Fix 5 findings from the A2/A3 adversarial verification pass
- **Committed:** 2026-07-12 02:12:15 +0100
- **Remote:** ahead by 182
- **Working tree:** DIRTY — uncommitted changes present

Uncommitted files:
- `M experimental_notes/CDSFL_Agent_Operational_Plan.md`
- `M resources/RECOVERY.md`
- `?? experimental_notes/CDSFL_Overnight_Phase1_2026-07-12.md`
- `?? experimental_notes/CDSFL_Overnight_Phase1_Plain_English_2026-07-12.md`

---

## Tests

**1605 tests collected** (`python3 -m pytest bench/tests/ --co -q`)

---

## Latest Experiment

- **Experiment:** exp42_composer_locationkey_live (#42)
- **Status:** CONVERGED
- **Topology:** star
- **Target:** `bench/cdsfl_registry/composer.py`
- **Rounds:** 7
- **Total findings:** 80
- **Gamma:** 0.5327
- **Models:** CC2, ChatGPT, Codex, DeepSeek, Gemini
- **Per model:**
  - Gemini: 34
  - Codex: 15
  - DeepSeek: 12
  - ChatGPT: 11
  - CC2: 8
- **Logs:** `/Users/georgejackson/Developer_Projects/Constraint_Engineering/bench/logs/exp42_composer_locationkey_live_20260609T183659Z`

---

## Recent Commits

- `b656549 Fix 5 findings from the A2/A3 adversarial verification pass`
- `349951f A3: rename take_up_slack -> routing (code-only; behaviour byte-identical)`
- `ef1fe7b A1: guarded directive-pruning panel (pr) — script + 4/5 model responses`
- `df18201 A2: ouroboros shadow real-work loop — fetch+parse+read+brief real OA papers`
- `dfc475d sv: discussion phase closed + agreed action list; founder rulings (retire compelled-convergence §10, rename routing now, calculator-analogy goal); pre-Exp-43 verification 250 tests green; .env locked. Phase 1 = pruning panel + ouroboros shadow build (parallel) + rename + §10 retire -> Exp 43`
- `f15bfe4 Close discussion phase: founder corrections + agreed action list (Phase 1/2/3)`
- `5b7a76f Ouroboros + self-improvement assessment (founder-ordered, pre-Exp-43)`
- `cc71be5 ★ RETRACTION: the API keys were NEVER lost — the checker itself was the bug`
- `de709a2 API-key incident root-caused + founder decision register D1-D12 + key preflight`
- `d522e66 sv: pre-restart save (3 July 00:25) — recovery docs current to the full-rs + assessment session; MEMORY.md compacted 26.3K->17.6K (session entries -> topic files, zero loss); resume = keys -> Exp 43`
