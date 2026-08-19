# Retrospective Renumbering of Exp 39 Landings into Experiments 40 to 52

Date: 16 April 2026
Branch: `exp39-experimental`
Author context: CC1 working under the live plan at `~/.claude/plans/effervescent-watching-platypus.md`

## Why this document exists

The original Exp 39 framing treated a single four-day burst of work as one
experiment with thirteen sub-items. That framing under-represents the work:
each landing had its own scope, its own confer record where applicable, its
own tests, and its own artefact. The founder directed on 16 April that each
completed landing be promoted to its own experiment number, so that the
experimental lineage reads correctly and future work can reference individual
landings without the ambiguous "39_X" shorthand.

This is an administrative renumbering. No code moves. No artefact is
duplicated. Every landing below already exists on disk and in git history.
The renumbering only changes how the lineage is described.

## Numbering convention

- Exp 39 is retained as the umbrella identifier for the thirteen-landing
  burst between 12 and 16 April 2026.
- Each of the thirteen landings is promoted to its own experiment number in
  the order it landed, starting at 40.
- Experiments 53 and later are reserved for forward work — the shadow-data
  audit, the factorial-design choice, embedding backend swap, penalty tier
  recalibration, opportunity-cost-sufficiency test, and the shadow-cell
  promotion gate. Those are covered in the forward-experiments section of
  the live plan and are not listed here.

## The thirteen landings

| # | Landing | Landed | Primary artefact | Status |
|---|---------|--------|------------------|--------|
| 40 | kappa_set denominator preparation | 12 Apr | `bench/dm/_convergence.py`, lines 287-300 | DONE |
| 41 | Embedding similarity scaffold, Jaccard-backed and sentence-transformer-ready | 12 Apr | `bench/dm/_similarity.py` | DONE |
| 42 | Continuous suppression plus order fix, w(f) excluded from q_eff | 12 Apr | `bench/dm/_convergence.py` `_suppression_weight()` | DONE |
| 43 | Persistent memory with blended prior | 13 Apr | `bench/dm/_memory.py` | DONE |
| 44 | FFAFP constraint formalisation | 13 Apr | `docs/MATHEMATICAL_APPENDIX.md` section 1.2 | DONE |
| 45 | Phase B4 specialist dispatch | 13 Apr | `bench/immune_agents.py`, lines 2599-2685 | DONE (shadow) |
| 46 | Ouroboros cell, also known as O1 | 13 Apr | `bench/ouroboros_cell.py` | DONE (shadow) |
| 47 | Mathematical appendix expansion from 1260 to 1991 lines | 14 Apr | `docs/MATHEMATICAL_APPENDIX.md` sections 1.3 through 9 | DONE |
| 48 | Shadow Stage 6 calibrator | 14 Apr | `bench/dm/_shadow_stage6.py` | DONE (shadow) |
| 49 | Macrophage cell, patrol and self-check | 14-15 Apr | `bench/macrophage_cell.py` | DONE (shadow) |
| 50 | Section 17 feedback channel, the critic arm | 15 Apr | `bench/dm/_feedback.py` plus `universal.toml` | DONE |
| 51 | Section 18 divergence directive, the generator arm, with channel reassignment | 15-16 Apr | `bench/dm/_divergence.py` plus operational section 18 | DONE, 5 of 5 panel convergence |
| 52 | Section 18 round-2 implementation plus round-3 review: contrast, sibling, near-copy | 16 Apr | same as 51 plus 75 of 75 divergence tests | DONE |

## Confer panels by landing

- Experiments 40 through 49 landed across individual sessions without a
  dedicated five-model confer round; mathematical and structural checks used
  SymPy, z3, and the standard test suite.
- Experiment 48 has two two-model confer rounds in the log directories
  `bench/logs/confer_stage6_model/combined_20260414T091448Z.json` and
  `bench/logs/confer_stage6_r2/combined_20260414T101259Z.json`, followed by
  a full five-model round in `bench/logs/confer_stage6_full/combined_20260414T111854Z.json`.
- Experiment 51 has a five-model confer round in
  `bench/logs/confer_divergence_directive/combined_20260415T220231Z.json`
  that produced unanimous convergence on channel reassignment.
- Experiment 52 has two five-model confer rounds, in
  `bench/logs/confer_divergence_round2_convergence/combined_20260415T224529Z.json`
  and `bench/logs/confer_divergence_round3_final/combined_20260416T012044Z.json`.
  Round 3 produced effective five-of-five convergence after a documentation
  inconsistency in the severe tier description was corrected.

## Status lineage

Eight of the thirteen landings are DONE and feed the live pipeline. Five are
DONE in shadow mode, meaning they execute, collect observations, and do not
yet alter pipeline decisions. The shadow items are 45, 46, 48, 49, and the
shadow halves of 43 and 50 where applicable. The live plan's section 3
("Shadow-Mode Elements — Keep Running") lists six shadow layers to keep
running through Exp 53 through 57; those shadow layers are the observational
surface of the landings enumerated above.

## What this renumbering does not change

- No file on disk is moved or renamed.
- No test count changes. 935 tests pass at commit `e9c4a80`.
- No mathematical symbol is redefined. The revision ledger in
  `docs/MATHEMATICAL_APPENDIX.md` section 10 captures symbol lineage
  separately.
- No shadow layer is promoted. Promotion waits for Exp 58's gate.
- No CLAUDE.md directive is altered.
- No finding is reclassified. Findings remain confirmed programmatically or
  by the human in the loop.

## Forward pointer

The next forward experiment is Exp 53, the retrospective shadow-data audit.
Exp 53 gates the factorial design choice at Exp 54. Full forward structure
lives in the live plan at `~/.claude/plans/effervescent-watching-platypus.md`
sections 2 through 6.
