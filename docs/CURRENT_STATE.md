# CDSFL Current State

Generated: 8 April 2026 04:53 BST (2026-04-08T04:53:51+01:00)

---

## Git

- **Branch:** main
- **Last commit:** `2016073` Add mathematical model audit: 25 internal checks pass, 5 gaps confirmed against Exp 33-36 data
- **Committed:** 2026-04-08 04:53:42 +0100
- **Remote:** ahead by 1
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
  0b. PROMOTE LLM classifier + formalisation agent from shadow to primary
      (v2 immune IS already primary — DC, NK, Helper T, Reg T. Corrected 8 April.)
  0c. CONNECT fix-application pipeline (extract fix → sandbox → Stage 4 → CLOSED)
  0d. RESUME Exp 36 from R22 checkpoint as validation run (expect 3–5 rounds)
  0e. IMPLEMENT CC2 closed-constraint sub-agents 1–3 for Exp 37
      - Agent 1 (Citation Verifier): does finding accurately describe cited code?
      - Agent 2 (Fix Extractor): can NL fix be expressed as applicable code change?
      - Agent 3 (Dedup Assessor): does new finding describe same bug as existing?
      - Agent 4 (CC2v): confirm/reject/duplicate/escalate — already operational
      - All agents: closed constraint space, mechanical only, no generative function
      - Do NOT add to resumed Exp 36 (changes experimental conditions)
  1. Manual dedup COMPLETE (programmatic: 153 → ~9 unique, see verification analysis)
  2. Implement full 13 design improvements for fresh Exp 37:
     Original 7 (from Session Findings):
     - Contested → HIL escalation (5-round threshold)
     - Discovery efficiency metric (ρ = novel/raw)
     - Consolidation phase (ITC change_focus only in final 3 rounds)
     - Decay-rate convergence criterion
     - Meta-cognitive decay feedback in star topology prompt
     - v2 already primary (DC, NK, Helper T, Reg T) — promote LLM classifier + formalisation agent
     - Classifier/timeout fixes
     Deep analysis additions (6):
     - Per-model ρ tracking with targeted ITC intervention (HIGH)
     - Gamma-aware ITC DEGRADATION threshold (HIGH)
     - Dynamic stall detector terminate threshold
     - Pre-filter findings before CC2v queue (HIGH)
     - Dedup-aware CC2v (check prior confirmations) (HIGH)
     - Context windowing for long runs (HIGH)
  3. CC2 closed-constraint sub-agents 1–3 (Citation/Fix/Dedup) — see 0e above
  4. BUILD reference runner for Exp 37+ (parameterised, UX-callable entry point)
  5. WRITE Mathematical Model Companion (plain English walkthrough of appendix)
  6. Meta-cognitive feedback implementation (Exp 37 only, data-only, constrained response)

---

## Recent Commits

- `2016073 Add mathematical model audit: 25 internal checks pass, 5 gaps confirmed against Exp 33-36 data`
- `3b6d9f5 Update Exp 36 ground truth: convergence detection failure, CC2 closed-constraint design, 6-item task sequence`
- `4296dba sv: correct immune status, settle CC2 sub-agent design, update forward path`
- `ebb50d4 Add Exp 36 ground truth reference — consolidated findings, immune corrections, forward path`
- `9b16013 sv: update state snapshot, timestamps — working tree clean, MC commands in place`
- `acdaddd Add metacognitive command reference to project CLAUDE.md, REPRODUCING.md, and onboarding script`
- `613ef9b Fix QC reference checker (85→3), add interactive onboarding installer, fix stale TTS paths`
- `f72fca8 Add automation scripts, layered documentation, and project CLAUDE.md`
- `ddc8f87 Add metacognition microscope, model revision plain English, and MIDCA reassessment analyses`
- `4d448aa Fix Agent 2 ≠ semantic layer in design analysis, correct evidence.py line count`
