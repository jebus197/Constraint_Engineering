# Decisions awaiting the founder, 30 October 2026

Written 2026-10-30 19:05 GMT. Branch `sim/shakedown-2026-09-29`, commit `37b14e5a`.

This document replaces `experimental_notes/All_Verdicts_Consolidated_2026-10-30.txt`, written at 10:05 the same day, which the founder judged impossible to rule on. The spoken companion is `Decisions_Awaiting_You_2026-10-30.txt`, mirrored byte-identically to `~/Desktop/CDSFL_tts/`.

## Why the earlier file failed, measured

The 4 charges the founder made were turned into predicates and measured rather than accepted. Producer: `scripts/why_the_consolidated_file_was_unusable_2026-10-30.py`. Guard: `bench/tests/test_the_file_diagnosis_producers_2026-10-30.py`, 42 tests, against 9 deliberate mutations of the producers. 7 turned it red immediately. 1 stayed green and exposed a hollow test, whose single trigger word carried the whole assertion; that test was replaced by 1 case per trigger plus a floor, and the mutation is now red. 1 stayed green and exposed a branch that changed 0 outputs on both real documents and on a synthetic document, which was removed as an addition nothing reached.

| measure | file of 10:05 | this file |
|---|---|---|
| open entries named by bare identifier only | 6 of 6 | 6 of 6, each with a plain-English description beside it |
| entries sharing no 3-word phrase with their canonical title | 4 of 6 | 3 of 6 |
| mentions of additive / composability / simplest sufficient | 0 / 0 / 0 | 11 / 10 / 11 |
| entries whose section carries a recommendation | 1 of 6 | 6 of 6 |
| near-duplicate sentence pairs, both measures agreeing | 2 of 16,653 | 0 of 15,753 |
| sentences about instruments rather than the decision | 48 of 224 = 0.2143 | 15 of 219 = 0.0685 |
| longest paragraph, characters | 1,098 | 735 |
| paragraphs over 400 characters | 22 of 67 | 11 of 82 |
| Flesch reading ease / Coleman-Liau grade | 59.33 / 9.58 | 57.87 / 10.10 |

**Readability was never the defect.** Both files score easier than the dense task-list entries they draw on (Flesch 37.59, Coleman-Liau 11.60), and the 2 indices share no intermediate quantity — the first counts syllables and the second counts characters — so their agreement on the direction is informative. The defect was referents: every sentence was readable and the reader still could not tell what `B41` was. This is what the note standard already states, that the failure mode is never "too technical" but "too vague to identify what is being discussed".

**2 of these figures are corrections to what was reported in chat earlier today.** The recommendation count for the earlier file was given as 0 of 6; with the paragraph-ownership defect in the checker repaired it is 1 of 6. And the subject-naming measure is a proxy that penalises exactly the improvement asked for: it tests whether the canonical title's vocabulary is reproduced, and plain English deliberately paraphrases it. `B50` scores 0 shared phrases and a content-word share of 0.3750 in both files while carrying a full plain-English explanation in the second, so the instrument cannot see that charge being met.

## The founder's rulings from the earlier file, recorded

| ruling | effect |
|---|---|
| Free panels and simulated runs need no additional permission beyond his instruction to run them | `qs:9be924df11ed` closes. No free dispatch is launched without his instruction. |
| The paid-dispatch gate's widened noun set is accepted | `panel`, `review`, `arm`, `experiment` now caught after `paid`; 5 paid phrasings caught, 3 unpaid still ignored, reverting turns 3 tests red |
| An unmarked annotation ending in `?` is a question | Reaches about 180 of 752 annotations. `tid_of` digests the kind, so re-filing moves identities. |
| A brief is updated before dispatch | B21's brief was validator-refused at 10:30 and now passes all 5 required checks |

## Where the founder was right and the earlier file was wrong

He recalled that several panel requests on the master task list had simply not been done. The earlier file called the backlog stale recording, measured from ticket labels — the wrong instrument.

Producer: `scripts/which_panel_briefs_were_never_run_2026-10-30.py`. Of **134** directories under `bench/logs/` holding a `BRIEF.md`, **8** hold a brief and no seat reply and no sandbox harvest. A census of the whole tree, so no interval attaches.

| unrun brief | concerns | entry state |
|---|---|---|
| `the_role_layer_b21_2026-10-30` | B21 | OPEN |
| `stem_generality_b22_2026-10-29` | B22 | OPEN |
| `is_this_yet_a_general_purpose_stem_calculator_2026-10-29` | B22 | OPEN |
| `general_purpose_stem_calculator_2026-10-18` | B22 | OPEN |
| `how_should_the_claim_channel_be_promoted_2026-10-20` | the claim channel, C1's subject | OPEN |
| `three_mechanism_repairs_2026-10-18` | B29, B31, B32, B33 | all DONE |
| `the_required_quiet_run_2026-10-18` | C12 | DONE |
| `panel_todays_fixes_20260906T175435Z` | A4 | DONE |

**5 of the 8 belong to questions still open, and 3 of those 5 are 3 briefs on the same question** with nothing on disk recording which is canonical. The remaining 3 belong to entries since completed, so their reviews are probably moot — a judgement, not a measurement.

## The 6 open entries

Each is set out in the spoken companion as what it is, what it affects, what is to be decided, and a recommendation tested against the additive standard, composability and the simplest sufficient fix. The technical anchors are collected here.

| entry | the decision | key anchor |
|---|---|---|
| **B50** | 1 of 3 options for 6 re-armed immune-memory assertions | `bench/state/immune_memory.json` holds 1 experiment; `immune_memory_20261017T095236Z.why.json` records the reset reason verbatim. Partition corrected from 2-and-4 to 1-and-5: filtering `_RECORDING_RUNS` to post-reset runs repairs 1 assertion and breaks a 7th that passes today. Option 2 needs about 17 live runs. |
| **C1** | 2 prerequisites, then a weight | `bench/claim_ledger.py:195` `CLAIM_CHANNEL_WEIGHT = 0.0`; ceiling `CLAIM_CHANNEL_MAX_WEIGHT = 0.5` proved by SymPy and z3. `apply_claim_channel` has **no caller** in the harness — the live computation is at `bench/reference_runner_v3.py:15774` and `:15848` and reaches it from neither. Archived claim coverage over the 6 runs carrying a ledger: mean 0.797109, median 0.830144, range [0.552632, 0.894737], so at the ceiling the channel would cut residual risk by about 41 per cent. **0 of those 6 reports record the residual risk the weight acts on**, so the weight cannot yet be chosen on evidence. |
| **B21** | one role vocabulary or two | `bench/experiment_11_orchestrator.py:59` declares `Role = Literal["collator", "player_manager", "participant"]`; read live at `bench/reference_runner_v3.py:13189` and `:13269`. Reconciling touches 63 quoted values across 24 files; a second layer touches none. Same answer removes the last football term from the ranking code. |
| **B22** | which of 3 briefs, then whether to dispatch | All 3 shakedown legs of 2026-10-15 ran as `domain=mathematics` and converged, so reviewing non-code material is demonstrated. The open question is whether a *resolved* finding survives when no executable repair exists. |
| **B41** | go-ahead on a panel dispatch | 6 of 8 lines discharged with evidence. 2 corrections: a cited test path that has never existed in this history, and ladder failures that no longer fail, 33 of 33 passing. |
| **R1** | authorisation and spend | Ruled 2026-08-07 and again 2026-09-06, so 84 and 54 days carried. The A1–A10 engineering gate is closed, 0 of 10 outstanding. 2 run directories exist and both predate the ruling. |

## The demotion false-alarm rate, measured

The founder asked whether a 1-in-20 chance of demoting a healthy model could be improved. Producer: `scripts/can_we_do_better_than_one_in_twenty_2026-10-30.py`, which imports the relegation panel's own instrument from `experimental_notes/seat_evidence/division_count_star_2026-10-08/cc2/scripts/`.

The 0.05 was never an operating point: it is the common size the 3 candidate rules were calibrated to for a fair comparison, and the producer the panel's findings table cites was never committed to the path it names.

3000 replications per cell, calibrated on seed 101 and evaluated on seed 202:

| target | wrongly demotes a healthy model | catches a real decline | whole roster declining |
|---|---|---|---|
| 0.05 | 0.0350 [0.0290, 0.0422] | 0.9353 [0.9260, 0.9436] | 0.0147 |
| **0.02** | **0.0157 [0.0118, 0.0208]** | **0.8890 [0.8773, 0.8997]** | 0.0063 |
| 0.01 | 0.0037 [0.0020, 0.0066] | 0.7793 [0.7641, 0.7938] | 0.0020 |
| 0.001 | 0.0010 [0.0003, 0.0029] | 0.6037 [0.5860, 0.6210] | 0.0010 |

The 0.05 → 0.02 step reduces wrong demotions by 0.019333, 95% CI [0.011396, 0.027270], Fisher exact p = 2.171e-06 and a 2-proportion z test p = 1.887e-06 — a factor of 2.2340. It costs 0.046333 of detection, 95% CI [0.032057, 0.060609], Fisher p = 2.500e-10, with mpmath reproducing the interval exactly. The trade is 2.3966 points of detection per point of false demotion avoided.

**An earlier 400-trial run was reported in chat with overlapping intervals and the recommendation withdrawn; at 3000 trials the intervals separate and the recommendation stands.** The whole-roster column stays near 0 at every size, which is the identifiability limit the 2026-10-08 panel established symbolically, not a tuning failure. All 4 rows come from the panel's simulated degradation model, not from this project's seats.

## The reach of the pre-commit board

The pre-commit board runs 73 of 729 test files on every commit, so 656 are never reached — 0.8999, a census of every test file and not a sample. Adding the 6 newest guards costs 18.88 seconds against 312.45, which is 0.060426 — about 19 seconds, cross-checked in SymPy as the exact rational 1888/31245 and in mpmath.

## Open with the founder

1. Whether an unmarked annotation that is **not** a question should default to a discussion label rather than a proposed fix. He proposed `ds` for a discussion request; the category list in `bench/ticket_store.py` currently holds `fr`, `pf`, `qs`, `wr`.
2. A cut-off date for harvesting annotations written before the ticket store existed. Suggested: 2026-10-17, the day it was built. Of 6 tickets checked by execution today, 5 were already done, which is the over-reporting he named.
3. Which of the 3 B22 briefs is canonical.

## Attribution

The detection difference from the earlier 400-replication run was cross-checked in Wolfram Language, which returned a two-sided normal-approximation p of 0.0034500106131332142 against statsmodels' pooled 0.003626 for the same pair; the difference is pooled against unpooled standard error and the verdict is identical. Figures derived with Wolfram Language carry this attribution as that service's terms require.

Written under CDSFL note standard v1.8 (17 October 2026).
