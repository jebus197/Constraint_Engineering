# CDSFL Current State

Generated: 28 July 2026 00:44 BST (2026-07-28T00:44:45+01:00)

---

## Git

- **Branch:** exp39-experimental
- **Last commit:** `8510f10` Shadow-observability repairs (audit-mandated): macrophage timing-spike unmasked (median guard -> absolute floor), DUPLICATE counted as redundancy not gate failure, stage-6 per-tool FPR keyed by tool_used not finding-id; stale S5 pins in test_specialist_shadow_cells flipped to live-era
- **Committed:** 2026-07-27 23:56:29 +0100
- **Remote:** ahead by 195
- **Working tree:** DIRTY — uncommitted changes present

Uncommitted files:
- `M bench/fingerprints/CC2.json`
- `M bench/fingerprints/ChatGPT.json`
- `M bench/fingerprints/Codex.json`
- `M bench/fingerprints/DeepSeek.json`
- `M bench/fingerprints/Gemini.json`
- `M bench/logs/immune_pipeline.log`
- `M resources/RECOVERY.md`
- `?? bench/logs/exp45_memory_statistics_live_20260727T225640Z/`
- `?? experimental_notes/Exp45_Convergence_2026-07-28.md`
- `?? experimental_notes/Exp45_Convergence_Plain_English_2026-07-28.md`

---

## Tests

**1630 tests collected** (`python3 -m pytest bench/tests/ --co -q`)

---

## Latest Experiment

- **Experiment:** exp45_memory_statistics_live (#45)
- **Status:** CONVERGED
- **Topology:** star
- **Target:** `bench/dm/_memory.py`
- **Rounds:** 4
- **Total findings:** 41
- **Gamma:** 0.0516
- **Models:** CC2, ChatGPT, Codex, DeepSeek, Gemini
- **Per model:**
  - Gemini: 12
  - DeepSeek: 12
  - Codex: 6
  - CC2: 6
  - ChatGPT: 5
- **Logs:** `/Users/georgejackson/Developer_Projects/Constraint_Engineering/bench/logs/exp45_memory_statistics_live_20260727T225640Z`

---

## Recent Commits

- `8510f10 Shadow-observability repairs (audit-mandated): macrophage timing-spike unmasked (median guard -> absolute floor), DUPLICATE counted as redundancy not gate failure, stage-6 per-tool FPR keyed by tool_used not finding-id; stale S5 pins in test_specialist_shadow_cells flipped to live-era`
- `f0b66b9 Exp 45 config: dm/_memory.py, domain=statistics (first live statistics-specialist run), _ouroboros ENABLED per founder promotion order; both ingestion paths traced PASS`
- `59ffe77 Verdict-reader hygiene (C0025/C0034/C0009 root cause: substring FALSIFIED matched NOT FALSIFIED -> false CONFIRMED; setup-guard AssertionError -> ERROR; negation-aware matching + 4 test pins) + Exp 45 config (dm/_memory.py, domain=statistics, _ouroboros LIVE per founder promotion order, both ingestion paths traced)`
- `9320000 Correct Exp 44 notes: 6 'irreducible' were panel-resolved (stale flags); zero HIL residue; cleanest convergence framing; Gemini parse-loss explanation`
- `84a372b Exp 44 post-run fixes (founder-approved): irreducible_queue_count excludes terminal statuses (6-stale-flags episode read 6 where truth was 0; on the gamma-alt path the stale count would have falsely refused convergence); routing resolution clears stale irreducible/HIL stamps; JSON-path parser maps FIND->description (Gemini C0007-9 empty-description loss — content was present, harvest incomplete). 4 new regression tests; affected suites green`
- `773fb36 sv: ★★ Exp 44 CONVERGED CLEANLY at R12 — zero residue (82 findings: 63 CLOSED/13 CONFIRMED/1 MERGED/5 REFUTED; residual queue EMPTY; 6 guarded irreducible HIL), gamma_critical 0.453>=0.30, location-keyed crit tail [0,0,0,0,0], 3 consecutive full passes R10-12, ~3.7h, first formal-endpoint zero-residue convergence in project history. The blue-water shake-out of the FIX 1-5 tranche performed exactly as pre-registered (Exp-43 blocker class never manifested; C0047 critical handled by designed protection->routing->guarded queue; location key caught an R10 re-find live). Notes: Exp44_Clean_Convergence_2026-07-27 (technical + Plain_English + Desktop TTS) + launch TTS. NEXT: founder materiality review (6 HIL + 2 REOPENs), committed shadow audit, funding decision on remaining arc; then Exp 45 = dm/_memory.py domain=statistics.`
- `db29e76 Promote physics/chemistry/engineering B-Cell specialists to LIVE (founder directive 2026-07-27: all specialists live from Exp 44 onwards; supersedes S5 shadow constraint). Inert for Exp 44 (domain=software); engages for synth STEM modules + BR2. Test pins updated to live-era: 20/20 pass incl. live physics dispatch (sympy+z3+astropy engaged)`
- `1cec60d Exp 43 fix tranche + adversarial repairs: FIX 1 (gated sub-critical contested exclusion + challenge conjunct + residual queue/alarm), FIX 2 (ERROR routing once, transport-safe), FIX 3 (fallback review-summary suppression, fence-aware), FIX 5 (residual-clearing directive), FIX 4 via Exp44 config (max_contested_rounds=3 + launcher passthrough gap FIXED), partial-round resume guard (panel-union expected set); Exp 44 evidence.py config, both ingestion paths traced PASS; tests 20 new/updated, targeted suites 81+287 green`
- `41ae6fb sv: dm/_memory.py provenance RESOLVED — Phase 4 of an agreed 8-phase 12-April batch (commits ad53693->e59dedd, after AIS confer 56a3e6e, 'execution order agreed' 996ec52); NOT rogue. It IS a documented maths-model component (appendix S1.5 blended prior -> R_k(0)) so the 'meaningful bearing' recollection is correct; but DORMANT (zero live importers), advisory-only (nudges prior, never overrides a verdict), scale-deferred (does ~nothing over the remaining arc). Plain-English explanation note + Desktop TTS written. Exp 44 target choice (keep _memory.py vs swap to a live target) = open founder decision after restart. Tracker matrix numbering staleness fixed (repo mirror synced to Desktop canonical). No code changed, no experiment run.`
- `a7c69e7 Lock in the confirmed remaining-experiment plan (20 July)`
