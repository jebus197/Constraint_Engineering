# CDSFL Current State

Generated: 21 April 2026 18:56 BST (2026-04-21T18:56:23+01:00)

---

## Git

- **Branch:** exp39-experimental
- **Last commit:** `76a6731` sv: Exp 40-54 consolidated plan + panel review round 1 — five-model panel (Gemini 3.1 Pro, Codex GPT-5.4, CC2 Opus 4.6, ChatGPT GPT-5.4, DeepSeek R1-0528) dispatched under star topology with 40_gate.json pass-condition + Stage 6 orthogonality framing, all responses within 227s wall time, no v1-preservation drift; five material fold-ins applied (Gate C preflight for section-17 admissibility parser at Exp 40 launch, Gate C threshold-freeze at Exp 54 launch applied identically across factorial cells, three-layer Cell A integrity strategy for Exp 54 with Gemini fresh-run and DeepSeek sensitivity-analysis fallbacks, shadow-promotion-now bounding condition requiring non-distortion check against pass_condition before live activation, Exp 47/52/53 target synthesis commitment with Exp 51 conditional on composer.py physics content); new artefacts bench/confer_exp40to54_consolidated_plan_review_2026-04-21.py + bench/logs/confer_exp40to54_consolidated_plan_review_2026-04-21/ + experimental_notes/Exp40_to_54_Consolidated_Plan_2026-04-21.md + experimental_notes/Exp40_to_54_Plan_Review_Panel_Round1_Outcome_2026-04-21.md plus plain-English TTS mirrors on Desktop; feedback_shadow_promotion_now.md memory updated with conditionally-safe bounding condition; three new memory files from earlier in this continuation window (feedback_communication_density.md, feedback_no_session_deferral.md, feedback_complete_task_lists.md); resources/ONBOARDING.md and resources/RECOVERY.md updated with 21 April session entry
- **Committed:** 2026-04-21 11:56:27 +0100
- **Remote:** ahead by 73
- **Working tree:** DIRTY — uncommitted changes present

Uncommitted files:
- `M bench/exp40_configs/40_gate.json`
- `M bench/immune_agents.py`
- `M bench/logs/immune_pipeline.log`
- `M bench/reference_runner_v2.py`
- `M bench/tests/test_channel_boundary.py`
- `M bench/tests/test_immune_agents.py`
- `M experimental_notes/Exp40_to_54_Consolidated_Plan_2026-04-21.md`
- `M resources/ONBOARDING.md`
- `M resources/RECOVERY.md`
- `?? bench/confer_exp40to54_plan_review_round2_2026-04-21.py`
- `?? bench/logs/confer_exp40to54_plan_review_round2_2026-04-21/`
- `?? bench/logs/confer_exp40to54_plan_review_round2_2026-04-21_stdout.log`
- `?? experimental_notes/Exp40_PreLaunch_Code_Changes_Round2_Close_2026-04-21.md`
- `?? experimental_notes/Exp40_to_54_Plan_Review_Panel_Round2_Outcome_2026-04-21.md`

---

## Tests

**1255 tests collected** (`python3 -m pytest bench/tests/ --co -q`)

---

## Latest Experiment

- **Experiment:** exp39_0_gate (#39)
- **Status:** INCOMPLETE
- **Topology:** star
- **Target:** `bench/runner_core.py`
- **Rounds:** 6
- **Total findings:** 111
- **Gamma:** 0.4612
- **Models:** CC2, ChatGPT, Codex, DeepSeek, Gemini
- **Per model:**
  - CC2: 28
  - Codex: 25
  - ChatGPT: 25
  - Gemini: 21
  - DeepSeek: 12
- **Logs:** `/Users/georgejackson/Developer_Projects/Constraint_Engineering/bench/logs/exp39_0_gate_20260413T193320Z`

---

## Recent Commits

- `76a6731 sv: Exp 40-54 consolidated plan + panel review round 1 — five-model panel (Gemini 3.1 Pro, Codex GPT-5.4, CC2 Opus 4.6, ChatGPT GPT-5.4, DeepSeek R1-0528) dispatched under star topology with 40_gate.json pass-condition + Stage 6 orthogonality framing, all responses within 227s wall time, no v1-preservation drift; five material fold-ins applied (Gate C preflight for section-17 admissibility parser at Exp 40 launch, Gate C threshold-freeze at Exp 54 launch applied identically across factorial cells, three-layer Cell A integrity strategy for Exp 54 with Gemini fresh-run and DeepSeek sensitivity-analysis fallbacks, shadow-promotion-now bounding condition requiring non-distortion check against pass_condition before live activation, Exp 47/52/53 target synthesis commitment with Exp 51 conditional on composer.py physics content); new artefacts bench/confer_exp40to54_consolidated_plan_review_2026-04-21.py + bench/logs/confer_exp40to54_consolidated_plan_review_2026-04-21/ + experimental_notes/Exp40_to_54_Consolidated_Plan_2026-04-21.md + experimental_notes/Exp40_to_54_Plan_Review_Panel_Round1_Outcome_2026-04-21.md plus plain-English TTS mirrors on Desktop; feedback_shadow_promotion_now.md memory updated with conditionally-safe bounding condition; three new memory files from earlier in this continuation window (feedback_communication_density.md, feedback_no_session_deferral.md, feedback_complete_task_lists.md); resources/ONBOARDING.md and resources/RECOVERY.md updated with 21 April session entry`
- `616ad43 sv: Exp 40 pre-launch panel re-audit + note-discipline rules + full-corpus note audit — four rules locked into memory (no self-reflection, paired technical+plain-English output, inline chat summary, numerical dates); 20 experimental_notes/ files edited to strip self-referential framing and convert word-form dates/numbers; new audit artefacts bench/confer_exp40_reaudit_round1.py + experimental_notes/Exp40_Pre_Launch_Panel_Audit_2026-04-20.md + experimental_notes/Exp40_Reaudit_Verified_Outcome_2026-04-20.md; resources/ONBOARDING.md and resources/RECOVERY.md updated with today's session entry and four standing rules`
- `5c81f33 Revert b3d9420 — Exp 40 pre-launch panel review carried the wrong framing`
- `b3d9420 sv: Exp 40 pre-launch panel review rounds 1-3B convergence — Q3 post-hoc only, Q4 10-field reason-trace schema, Q5 four preservation predicate families with 3 adopted refinements, Q6 star topology; activation-sequence gate now primary blocker for launch`
- `2c966ca sv: housekeeping part 2 — logs two-subfolder policy + Merkle sealing + examples/resources/ READMEs + CC1 memory mirror`
- `742e7aa sv: housekeeping bundle — sq MC command + onboarding script refactor + README topology embed + stale bootstrap cleanup`
- `436f9a0 sv: 20 April README promotion + regulatory-compliance consolidation (FOUNDERS_NOTES revisions + README v3→canonical + PAPER Part V regulatory alignment + EXTENDED_RATIONALE auditable cognitive infrastructure + new docs/COMPLIANCE_FRAMEWORK.md with EU AI Act/GDPR/NIST AI RMF/ISO42001 mapping + 6 supplementary-artefact templates)`
- `04bc286 sv: broader documentation staleness sweep — 6-batch pass (FOUNDERS_NOTES + SHORTCUTS + ARCHITECTURE + topology_formal + EXTENDED_RATIONALE + EXPERIMENTAL_RESULTS + PAPER) with paired TTS + experimental_notes mirrors`
- `145e9e2 sv: README v3 13-point corrections + rg MC command introduction`
- `7334e49 sv: README v3 draft + novelty-synthesis gap closure + apply-drafted-edits directive`
