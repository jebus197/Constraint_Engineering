# CDSFL Current State

Generated: 27 July 2026 05:11 BST (2026-07-27T05:11:14+01:00)

---

## Git

- **Branch:** exp39-experimental
- **Last commit:** `db29e76` Promote physics/chemistry/engineering B-Cell specialists to LIVE (founder directive 2026-07-27: all specialists live from Exp 44 onwards; supersedes S5 shadow constraint). Inert for Exp 44 (domain=software); engages for synth STEM modules + BR2. Test pins updated to live-era: 20/20 pass incl. live physics dispatch (sympy+z3+astropy engaged)
- **Committed:** 2026-07-27 01:19:54 +0100
- **Remote:** ahead by 189
- **Working tree:** DIRTY — uncommitted changes present

Uncommitted files:
- `M bench/fingerprints/CC2.json`
- `M bench/fingerprints/ChatGPT.json`
- `M bench/fingerprints/Codex.json`
- `M bench/fingerprints/DeepSeek.json`
- `M bench/fingerprints/Gemini.json`
- `M bench/logs/immune_pipeline.log`
- `M resources/RECOVERY.md`
- `?? bench/logs/exp44_evidence_locationkey_live_20260727T002705Z/`
- `?? bench/tests/falsify_verify_bundle_anchor.py`
- `?? experimental_notes/Exp44_Clean_Convergence_2026-07-27.md`
- `?? experimental_notes/Exp44_Clean_Convergence_Plain_English_2026-07-27.md`
- `?? falsify_verify_bundle.py`

---

## Tests

**1622 tests collected** (`python3 -m pytest bench/tests/ --co -q`)

---

## Latest Experiment

- **Experiment:** exp44_evidence_locationkey_live (#44)
- **Status:** CONVERGED
- **Topology:** star
- **Target:** `bench/evidence.py`
- **Rounds:** 13
- **Total findings:** 104
- **Gamma:** 0.2533
- **Models:** CC2, ChatGPT, Codex, DeepSeek, Gemini
- **Per model:**
  - Gemini: 50
  - DeepSeek: 19
  - CC2: 17
  - ChatGPT: 12
  - Codex: 6
- **Logs:** `/Users/georgejackson/Developer_Projects/Constraint_Engineering/bench/logs/exp44_evidence_locationkey_live_20260727T002705Z`

---

## Recent Commits

- `db29e76 Promote physics/chemistry/engineering B-Cell specialists to LIVE (founder directive 2026-07-27: all specialists live from Exp 44 onwards; supersedes S5 shadow constraint). Inert for Exp 44 (domain=software); engages for synth STEM modules + BR2. Test pins updated to live-era: 20/20 pass incl. live physics dispatch (sympy+z3+astropy engaged)`
- `1cec60d Exp 43 fix tranche + adversarial repairs: FIX 1 (gated sub-critical contested exclusion + challenge conjunct + residual queue/alarm), FIX 2 (ERROR routing once, transport-safe), FIX 3 (fallback review-summary suppression, fence-aware), FIX 5 (residual-clearing directive), FIX 4 via Exp44 config (max_contested_rounds=3 + launcher passthrough gap FIXED), partial-round resume guard (panel-union expected set); Exp 44 evidence.py config, both ingestion paths traced PASS; tests 20 new/updated, targeted suites 81+287 green`
- `41ae6fb sv: dm/_memory.py provenance RESOLVED — Phase 4 of an agreed 8-phase 12-April batch (commits ad53693->e59dedd, after AIS confer 56a3e6e, 'execution order agreed' 996ec52); NOT rogue. It IS a documented maths-model component (appendix S1.5 blended prior -> R_k(0)) so the 'meaningful bearing' recollection is correct; but DORMANT (zero live importers), advisory-only (nudges prior, never overrides a verdict), scale-deferred (does ~nothing over the remaining arc). Plain-English explanation note + Desktop TTS written. Exp 44 target choice (keep _memory.py vs swap to a live target) = open founder decision after restart. Tracker matrix numbering staleness fixed (repo mirror synced to Desktop canonical). No code changed, no experiment run.`
- `a7c69e7 Lock in the confirmed remaining-experiment plan (20 July)`
- `a3d01a7 sv: Exp 43 DONE — location-keyed two-sided gate GENERALISED to macrophage_cell.py (over-production solved: crit [0,0,0] R6-11, gamma ~0.57, gate passed R4+R11); formal convergence blocked by ONE mechanical artifact (sub-critical UNCONFIRMED findings, falsifier-error/absent, mis-counted as contested — NOT model disagreement). Fix designed + sy/z3-verified (FIX 1 -> converges R6), not yet coded. Arc reorder recommended (no re-run; next Exp 45 shake-out; defer 44/49; keep 54). Notes: Desktop TTS Exp43_Overnight + Exp44_Fix_Design; resources/RECOVERY.md 20-July block. Founder: finish efficiently.`
- `3ab3404 A1 panel: complete to 5/5 — add CC2 (Opus 4.8) verdict (post CLI re-auth)`
- `ec99b84 sv: Phase 1 (A1-A4) executed overnight + adversarial-pass fixes; Exp 43 READY + PAUSED for founder review + CLI re-login. Report experimental_notes/CDSFL_Overnight_Phase1_2026-07-12.md (+ Plain_English + Desktop TTS); resources/RECOVERY.md + experimental_notes/CDSFL_Agent_Operational_Plan.md resume pointers advanced to 12 July. Adversarial pass caught+fixed the RunnerConfig.from_dict routing-alias gap.`
- `b656549 Fix 5 findings from the A2/A3 adversarial verification pass`
- `349951f A3: rename take_up_slack -> routing (code-only; behaviour byte-identical)`
- `ef1fe7b A1: guarded directive-pruning panel (pr) — script + 4/5 model responses`
