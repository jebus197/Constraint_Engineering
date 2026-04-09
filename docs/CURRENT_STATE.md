# CDSFL Current State

Generated: 9 April 2026 19:25 BST (2026-04-09T19:25:53+01:00)

---

## Git

- **Branch:** main
- **Last commit:** `f528314` Enhance sv script: auto-update ONBOARDING.md and RECOVERY.md
- **Committed:** 2026-04-09 18:16:35 +0100
- **Remote:** up to date
- **Working tree:** DIRTY — uncommitted changes present

Uncommitted files:
- `M .claude/CLAUDE.md`
- `M bench/cdsfl_registry/composer.py`
- `M bench/dm/_types.py`
- `M bench/evidence.py`
- `M bench/fingerprints/CC2.json`
- `M bench/fingerprints/ChatGPT.json`
- `M bench/fingerprints/Codex.json`
- `M bench/fingerprints/DeepSeek.json`
- `M bench/fingerprints/Gemini.json`
- `M bench/logs/exp36_evidence_20260407T004931Z/checkpoint.json`
- `M bench/logs/exp36_evidence_20260407T004931Z/completion_signal.json`
- `M bench/logs/exp36_evidence_20260407T004931Z/exp36_report.json`
- `M bench/logs/exp36_evidence_20260407T004931Z/experiment_chain.json`
- `M bench/logs/exp36_evidence_20260407T004931Z/runner_state.json`
- `M bench/logs/immune_shadow.log`

---

## Tests

**690 tests collected** (`python3 -m pytest bench/tests/ --co -q`)

---

## Latest Experiment

- **Experiment:** exp37_evidence (#37)
- **Status:** CONVERGED
- **Topology:** star
- **Target:** `bench/evidence.py`
- **Rounds:** 16
- **Total findings:** 257
- **Gamma:** 0.4667
- **Models:** CC2, ChatGPT, Codex, DeepSeek, Gemini
- **Per model:**
  - Gemini: 87
  - ChatGPT: 51
  - DeepSeek: 48
  - CC2: 40
  - Codex: 31
- **Logs:** `/Users/georgejackson/Developer_Projects/Constraint_Engineering/bench/logs/exp37_evidence_20260409T050932Z`

---

## Recent Commits

- `f528314 Enhance sv script: auto-update ONBOARDING.md and RECOVERY.md`
- `944ec3e Exp 37 converged: 6 fixes, mathematical lineage, brain signal wiring`
- `9c2ee82 Guard all choices[0] access against empty upstream 500 responses`
- `d848863 Merge remote-tracking branch 'origin/claude/debug-api-500-error-AFfcu'`
- `d773f12 Fix unguarded choices[0] access in OpenRouter and DeepSeek API handlers`
- `e9ee3e3 Fix mark_verified() call signature — takes 1 arg not 2`
- `6f1de65 Fix CC2 agent model ID: claude-opus-4 → claude-opus-4-6`
- `14fc964 FFAF: fix CC2v all-escalation bug, expand Agent 4 routing, increase CT timeout`
- `9538e81 Exp 36: apply all verified fixes, promote shadow→active, wire CC2 agents, FFAF churn`
- `6abb7d1 Add canonical 4-phase execution plan to ground truth document`
