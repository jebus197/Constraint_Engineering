# CDSFL Current State

Generated: 8 April 2026 02:16 BST (2026-04-08T02:16:10+01:00)

---

## Git

- **Branch:** main
- **Last commit:** `acdaddd` Add metacognitive command reference to project CLAUDE.md, REPRODUCING.md, and onboarding script
- **Committed:** 2026-04-08 02:13:50 +0100
- **Remote:** up to date
- **Working tree:** clean

---

## Tests

**690 tests collected** (`python3 -m pytest bench/tests/ --co -q`)

---

## Latest Experiment

- **Experiment:** exp36_evidence (#36)
- **Status:** INCOMPLETE
- **Topology:** star
- **Target:** `bench/evidence.py`
- **Rounds:** 23
- **Total findings:** 452
- **Gamma:** 0.4111
- **Models:** CC2, ChatGPT, Codex, DeepSeek, Gemini
- **Per model:**
  - DeepSeek: 119
  - ChatGPT: 107
  - Codex: 92
  - Gemini: 92
  - CC2: 42
- **Logs:** `/Users/georgejackson/Developer_Projects/Constraint_Engineering/bench/logs/exp36_evidence_20260407T004931Z`

---

## Pending Work

NEXT STEPS:
  0. EXECUTE mathematical model audit (5 gap tests, see audit doc)
  0a. IMPLEMENT 3 minimum runner fixes for Exp 36 resumption:
      - Contested → HIL escalation (5-round threshold)
      - Gamma-aware ITC DEGRADATION threshold
      - Dedup-aware CC2v (check prior confirmations before re-verifying)
  0b. ACTIVATE v2 immune as primary (remove v1, enable LLM classifier, skin barrier)
  0c. CONNECT fix-application pipeline (extract fix → sandbox → Stage 4 → CLOSED)
  0d. RESUME Exp 36 from R22 checkpoint as validation run (expect 3–5 rounds)
  0e. IMPLEMENT CC2 Option A Agents 1–3 (structural/semantic/integration) for Exp 37
      - Agent 1 (Structural): code structure, dependencies, architectural patterns
      - Agent 2 (Semantic): semantic correctness, type safety — code discovery agent (NOT the semantic layer)
      - Agent 3 (Integration): cross-component interactions, API contracts
      - Agent 4 (CC2v): already implemented, operational since Exp 35
      - Do NOT add to resumed Exp 36 (changes experimental conditions)
  1. Manual dedup COMPLETE (programmatic: 153 → ~9 unique, see verification analysis)
  2. Implement full 13 design improvements for fresh Exp 37:
     Original 7 (from Session Findings):
     - Contested → HIL escalation (5-round threshold)
     - Discovery efficiency metric (ρ = novel/raw)
     - Consolidation phase (ITC change_focus only in final 3 rounds)
     - Decay-rate convergence criterion
     - Meta-cognitive decay feedback in star topology prompt
     - v2 shadow activation (Helper T v2, B Cell v2)
     - Classifier/timeout fixes
     Deep analysis additions (6):
     - Per-model ρ tracking with targeted ITC intervention (HIGH)
     - Gamma-aware ITC DEGRADATION threshold (HIGH)
     - Dynamic stall detector terminate threshold
     - Pre-filter findings before CC2v queue (HIGH)
     - Dedup-aware CC2v (check prior confirmations) (HIGH)
     - Context windowing for long runs (HIGH)
  3. CC2 Option A Agents 1–3 (structural/semantic/integration) — see 0e above

---

## Recent Commits

- `acdaddd Add metacognitive command reference to project CLAUDE.md, REPRODUCING.md, and onboarding script`
- `613ef9b Fix QC reference checker (85→3), add interactive onboarding installer, fix stale TTS paths`
- `f72fca8 Add automation scripts, layered documentation, and project CLAUDE.md`
- `ddc8f87 Add metacognition microscope, model revision plain English, and MIDCA reassessment analyses`
- `4d448aa Fix Agent 2 ≠ semantic layer in design analysis, correct evidence.py line count`
- `61f4bb6 Fix Agent 2 ≠ semantic layer conflation in recovery docs`
- `510d902 Add CC2 Option A four-agent model to design analysis and next steps`
- `c5fae42 Design analysis: Bugzilla gap, fix pipeline, v2 immune, resumption plan`
- `71d9a98 Scope mathematical model audit: 5 gaps in appendix vs Exp 29–36 data`
- `e2177df Fix churn signal verification: CONFIRMED, not UNCERTAIN`
