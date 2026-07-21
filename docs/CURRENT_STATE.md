# CDSFL Current State

Generated: 22 July 2026 00:26 BST (2026-07-22T00:26:22+01:00)

---

## Git

- **Branch:** exp39-experimental
- **Last commit:** `a7c69e7` Lock in the confirmed remaining-experiment plan (20 July)
- **Committed:** 2026-07-21 21:19:14 +0100
- **Remote:** ahead by 186
- **Working tree:** DIRTY — uncommitted changes present

Uncommitted files:
- `M experimental_notes/CDSFL_Agent_Operational_Plan.md`
- `M resources/RECOVERY.md`
- `?? experimental_notes/Persistent_Immune_Memory_Explained_2026-07-22.md`

---

## Tests

**1605 tests collected** (`python3 -m pytest bench/tests/ --co -q`)

---

## Latest Experiment

- **Experiment:** exp43_macrophage_locationkey_live (#43)
- **Status:** INCOMPLETE
- **Topology:** star
- **Target:** `bench/macrophage_cell.py`
- **Rounds:** 14
- **Total findings:** 95
- **Gamma:** 0.3874
- **Models:** CC2, ChatGPT, Codex, DeepSeek, Gemini
- **Per model:**
  - DeepSeek: 27
  - Gemini: 24
  - ChatGPT: 17
  - Codex: 15
  - CC2: 12
- **Logs:** `/Users/georgejackson/Developer_Projects/Constraint_Engineering/bench/logs/exp43_macrophage_locationkey_live_20260719T014326Z`

---

## Recent Commits

- `a7c69e7 Lock in the confirmed remaining-experiment plan (20 July)`
- `a3d01a7 sv: Exp 43 DONE — location-keyed two-sided gate GENERALISED to macrophage_cell.py (over-production solved: crit [0,0,0] R6-11, gamma ~0.57, gate passed R4+R11); formal convergence blocked by ONE mechanical artifact (sub-critical UNCONFIRMED findings, falsifier-error/absent, mis-counted as contested — NOT model disagreement). Fix designed + sy/z3-verified (FIX 1 -> converges R6), not yet coded. Arc reorder recommended (no re-run; next Exp 45 shake-out; defer 44/49; keep 54). Notes: Desktop TTS Exp43_Overnight + Exp44_Fix_Design; resources/RECOVERY.md 20-July block. Founder: finish efficiently.`
- `3ab3404 A1 panel: complete to 5/5 — add CC2 (Opus 4.8) verdict (post CLI re-auth)`
- `ec99b84 sv: Phase 1 (A1-A4) executed overnight + adversarial-pass fixes; Exp 43 READY + PAUSED for founder review + CLI re-login. Report experimental_notes/CDSFL_Overnight_Phase1_2026-07-12.md (+ Plain_English + Desktop TTS); resources/RECOVERY.md + experimental_notes/CDSFL_Agent_Operational_Plan.md resume pointers advanced to 12 July. Adversarial pass caught+fixed the RunnerConfig.from_dict routing-alias gap.`
- `b656549 Fix 5 findings from the A2/A3 adversarial verification pass`
- `349951f A3: rename take_up_slack -> routing (code-only; behaviour byte-identical)`
- `ef1fe7b A1: guarded directive-pruning panel (pr) — script + 4/5 model responses`
- `df18201 A2: ouroboros shadow real-work loop — fetch+parse+read+brief real OA papers`
- `dfc475d sv: discussion phase closed + agreed action list; founder rulings (retire compelled-convergence §10, rename routing now, calculator-analogy goal); pre-Exp-43 verification 250 tests green; .env locked. Phase 1 = pruning panel + ouroboros shadow build (parallel) + rename + §10 retire -> Exp 43`
- `f15bfe4 Close discussion phase: founder corrections + agreed action list (Phase 1/2/3)`
