# CDSFL Current State

Generated: 28 July 2026 13:27 BST (2026-07-28T13:27:08+01:00)

---

## Git

- **Branch:** exp39-experimental
- **Last commit:** `71d00be` Sweep hardening from Exp 46 first in-run use: per-item dispositions recorded in stats + post-sweep registry persisted to runner_state.json (the round checkpoint predates the sweep — Exp 46's per-item audit trail was lost at exit, counts survived in the report). 33 tests green
- **Committed:** 2026-07-28 13:19:07 +0100
- **Remote:** ahead by 202
- **Working tree:** DIRTY — uncommitted changes present

Uncommitted files:
- `M bench/logs/exp46_stage6_locationkey_live_20260728T103151Z/sweep_replay_audit_20260728.json`
- `M resources/RECOVERY.md`
- `?? experimental_notes/Exp46_Convergence_2026-07-28.md`
- `?? experimental_notes/Exp46_Convergence_Plain_English_2026-07-28.md`

---

## Tests

**1638 tests collected** (`python3 -m pytest bench/tests/ --co -q`)

---

## Latest Experiment

- **Experiment:** exp46_stage6_locationkey_live (#46)
- **Status:** CONVERGED
- **Topology:** star
- **Target:** `bench/dm/_shadow_stage6.py`
- **Rounds:** 6
- **Total findings:** 48
- **Gamma:** 0.3040
- **Models:** CC2, ChatGPT, Codex, DeepSeek, Gemini
- **Per model:**
  - Gemini: 13
  - DeepSeek: 11
  - Codex: 9
  - ChatGPT: 8
  - CC2: 7
- **Logs:** `/Users/georgejackson/Developer_Projects/Constraint_Engineering/bench/logs/exp46_stage6_locationkey_live_20260728T103151Z`

---

## Recent Commits

- `71d00be Sweep hardening from Exp 46 first in-run use: per-item dispositions recorded in stats + post-sweep registry persisted to runner_state.json (the round checkpoint predates the sweep — Exp 46's per-item audit trail was lost at exit, counts survived in the report). 33 tests green`
- `24760b3 Repo doc inventory (read-only, 3-agent): classification report for founder pre-BR2 hygiene ruling — record verified clean (0 dupes/strays in 207-file notes dir); 6 delete + 17 archive candidates + 4 rulings; execution deferred to post-arc single commit`
- `3b11d5d ImmuneMemory staged wiring (founder-approved): immune_memory_enabled/path config + run-end recording hook (per-flaw-class confirmed/rejected tallies -> record_experiment -> save; pi_mem logged) + launcher passthrough; blended-prior CONSUMPTION deliberately deferred to a later declared delta. Default off = byte-identical; 2 tests`
- `5cdb353 Ouroboros 1E.8 query fix (backtick/operator sanitisation, verified on the Exp 45 live-failure case; 29 tests green) + Exp 46 config (dm/_shadow_stage6.py, sweep enabled as declared delta, both ingestion paths traced, 19 location symbols) + Exp 45 sweep smoketest script`
- `907e8c2 Sweep smoke test on Exp 45 residuals: 6/6 cleared in one panel round (Codex falsifiers, runner-reverified), 0 remaining, 0 withdrawals — founder hypothesis confirmed; Exp 45 now 39/39 terminal. Notes postscripted`
- `600eba9 Post-convergence sweep (founder-approved 2026-07-28): bounded epilogue rounds after the terminal verdict is recorded — panel clears residual non-terminal findings via labelled falsifier re-attachment (reverified by the runner) or reasoned withdrawal (sub-critical only; criticals stay CONFIRM-only). Malady-proofed: runs strictly post-verdict (can never block/reverse convergence), registers zero new findings, bounded rounds, leftovers reported honestly. Config post_convergence_sweep_rounds (default 0 = byte-identical) + launcher passthrough; 6 regression tests`
- `bfca5aa sv: ★★ Exp 45 CONVERGED R3 via the two-sided gamma-alt gate (gamma_critical 0.621, tail [0,0,0]); 45 min; $5.62; all 12 criticals falsifier-CONFIRMED; ledger born clean under the fixed verdict-reader (NOT-FALSIFIED audit=0). Firsts: statistics specialist LIVE all rounds; ouroboros LIVE with 4 real paper briefs (query flaw exposed + contained; fix 1E.8 scheduled). 6 OPEN sub-criticals to standing review. Notes: Exp45_Convergence_2026-07-28 triple. NEXT: founder review + ImmuneMemory-enable + merge-to-main decisions; then Exp 46 stage6.`
- `8510f10 Shadow-observability repairs (audit-mandated): macrophage timing-spike unmasked (median guard -> absolute floor), DUPLICATE counted as redundancy not gate failure, stage-6 per-tool FPR keyed by tool_used not finding-id; stale S5 pins in test_specialist_shadow_cells flipped to live-era`
- `f0b66b9 Exp 45 config: dm/_memory.py, domain=statistics (first live statistics-specialist run), _ouroboros ENABLED per founder promotion order; both ingestion paths traced PASS`
- `59ffe77 Verdict-reader hygiene (C0025/C0034/C0009 root cause: substring FALSIFIED matched NOT FALSIFIED -> false CONFIRMED; setup-guard AssertionError -> ERROR; negation-aware matching + 4 test pins) + Exp 45 config (dm/_memory.py, domain=statistics, _ouroboros LIVE per founder promotion order, both ingestion paths traced)`
