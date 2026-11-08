# The second complete board, and 5 checks that accused correct prose

2026-11-08, Europe/London. Written under CDSFL note standard v1.9 (1 November 2026).

## Summary

A second complete test board was run on 2026-11-07 against a prediction committed before it, at commit `aea4ec9b`: 15,904 passed, 4 failed, 37 skipped, 8,036.30 s. Both of the prediction's clauses were refuted, and the clause about new failures was refuted for the second time in 1 night by the same cause — the repairing session's own commits. 2 new failures appeared and both were repaired and verified. The remaining 2 are decisions reserved to the founder and were correctly predicted to persist. Separately, an attempt to clean the morning report's prose found 5 distinct categories in which the note linter accuses correct writing, and 1 category in which it is blind; the attempt was stopped rather than extended to a 6th predicate.

## The board, and the partition against its predecessor

The board ran on a tree with 0 uncommitted paths and is recorded in `resources/suite_record.json`. Set against the board of 7 hours earlier at `e796a010`, which carried 11 failures: **9 of 11 fixed** (0.818182, Wilson 95% [0.523019, 0.948632], Clopper-Pearson [0.482244, 0.977169]), **2 of 11 still red** (0.181818, Wilson [0.051368, 0.476981]), and **2 new**. Producer: `scripts/compare_this_board_against_the_record_2026-11-07.py`, run against an explicitly named prior record because the suite wrapper overwrites the live one when a run ends.

**2 of 2 new failures have subjects first committed on 2026-11-07**, in the 2 commits this session itself made — 1.000000, Wilson [0.342380, 1.000000], Clopper-Pearson [0.158114, 1.000000]. 0 came from the product under study. Both guards that caught them already existed, 1 since 2026-11-03 and 1 since 2026-08-15. Producer: `scripts/the_second_board_was_red_for_the_same_reason_2026-11-07.py`.

**That producer's own decision rule is reported as adding nothing.** It was pre-stated as a Wilson lower bound above 0.3400 and the measured bound is 0.342380, passing by 0.002380. A control across every reachable value at this sample size shows 0 of 2 giving 0.000000 and 1 of 2 giving 0.094531, both failing, so the rule is exactly equivalent to asking whether both failures were the session's own. Expressing a yes-or-no question as an interval test adds no information, and the threshold was chosen in knowledge of the only value that could pass it. The provenance finding rests on the per-artefact dating evidence, which is checkable, and not on the interval.

## The 2 new failures, and what each was

**An interval helper carried 1 cross-check and reported it as 2.** `scripts/the_gate_board_serialises_the_tree_2026-11-07.py` computed the Wilson interval by 2 independent routes — a statistics library and a closed form in arbitrary precision — but the Clopper-Pearson interval by a single library call, while the printed disagreement figure compared only the 2 Wilson values. The figure was true of Wilson and silent about the Clopper-Pearson pair printed beside it on the same line. 2 library names had bought 1 cross-check. The repair restores an arbitrary-precision inversion of the regularised incomplete beta function as the second route and widens the disagreement to span all 4 values. **Every printed interval is byte-identical before and after the repair; the only line that moved is the disagreement, from 5.551e-17 to 1.110e-16** — which is simultaneously the evidence that the new terms are reached and the evidence that no citation elsewhere went stale. The detector now reports 0 of 26 producers resting a quantity on a single route.

**2 producers cut a printed list in silence.** `scripts/the_help_matcher_needed_both_halves_2026-11-07.py` and `scripts/who_made_this_board_red_2026-11-07.py` each printed a fixed number of items under a heading that reads as complete. Both now state the remainder. **This is the defect class repaired that same morning in 3 other scripts**: the session fixed the class and then committed 2 fresh instances of it, which is why a guard that outlives its author's attention is worth more than the author's intention.

Verification of both repairs: the 4 test files that reach the 3 repaired producers, established by tracing every reader rather than assumed, return **1,429 passed, 0 failed in 617.15 s**. A third complete board would spend 2 hours 14 minutes of the founder's machine to re-confirm what 617 seconds confirms.

## The 2 failures that remain are decisions, not defects

The blind panel round of 2026-11-06 still owes its joint half, so the liveness check for that debt refuses. The entry covering it predicted this in writing before the run existed, stating that the check reports queue status rather than a regression and will go red again on the next dispatch. It has now done so on 2 consecutive rounds, which strengthens the design question rather than answering it.

The task list's branching measure reports **R = 0.9685 new entries per entry closed, with a 95% interval of [0.8031, 1.1679]** and an exact test against R = 1 at p = 3.870682e-01. The upper bound stands above 1, so the list cannot presently be said to terminate. The check's own refusal text records that the founder asked to be told if that happened. Over the list's history, 222 entries have been closed and 215 added, and 215 of the 274 entries were created after the list was first populated — 78.4672%, Wilson [73.2243%, 82.9229%]. Producer: `scripts/task_list_burndown_2026-09-11.py`. This is the alarm working, not a fault in it, and what to do about an R of 0.9685 is a decision rather than a repair.

## 5 categories in which the note linter accused correct prose

The generated morning report carried 20 reported findings in its written copy and 47 in its spoken copy. 5 were real and were repaired at source; the rest fall into categories where the check fires on writing that is correct.

**Repaired, 5 of them.** 2 instances of an unnamed subject, where the text said "the thing" and "the mechanism" and now names the comfortable listening a spoken file exists for, the termination alarm, and the practice a directive forbids. 2 entry codes cited without their subject, which now name the check that refuses a falsifier's own review target, and the gate that runs before each commit. 1 further unnamed subject in the decisions file. The written copy's findings fell from 20 to 16 and the spoken copy's from 47 to 43, moving by exactly the 4 repaired in each, with nothing else disturbed.

**Not repaired, and the reason differs by category.**

1. **A quantity word in verb position.** The check requires a determiner before the word, which correctly rejects "counts substitutions", but "the half that counts quiet rounds" parses as a determiner, 2 modifiers and a count. 12 findings in the written copy.
2. **A quantity valued in the neighbouring sentence.** The check is sentence-scoped, so a definite reference back to a figure already given reads as a bare quantity.
3. **An entry code separated from its subject by sentence segmentation.** 3 findings name codes whose lines do read "B22. What a fix means outside code, and whether this is yet a general-purpose STEM calculator", with the subject present in the same line. The check splits at the full stop after the code and then reports the orphaned remainder.
4. **A decimal duration read as an entry reference.** 1 finding fired on "1.1" in the sentence "3,243 findings across 998 files in 1.1 seconds". This is the mirror of a confusion already recorded in this project, where an item reference was read as scientific notation.
5. **A spelled number the founder has reserved for his own ruling.** 17 findings in the spoken copy are genuine violations of the digits-only rule, and an existing entry already holds them, states the same count of 17, and reserves to him explicitly whether they should be rewritten at all — because whether digits read better aloud is not measurable from the file. Rewriting them would both take a decision recorded as his and destroy that entry's own quoted evidence, which names 3 of these exact strings as its examples.

**5 over-matching categories on 1 surface is past the point at which writing a 6th predicate is the right move, so none was written.**

## A correction to that entry's stated cause, and a correction to this session's first account of it

The entry above records the written copy as carrying 0 spelled-number findings because the written renderer never emits those sentences. This session first claimed the opposite — that the written copy's 0 was a false negative caused by the linter skipping markdown headings — and committed a decision rule before measuring: the entry's cause would be refuted only if the Wilson lower bound on the share of spoken findings whose sentence also appears in the written copy exceeded 0.5000.

**The measurement refused this session's claim. 4 of 17 = 0.235294, Wilson 95% [0.095550, 0.472618], Clopper-Pearson [0.068108, 0.498993], against a refutation gate of 0.5000.** The entry was right about 13 of the 17. The heading-blindness mechanism is nonetheless real and was established by execution rather than by reading the linter: the identical sentence yields 0 findings presented as a markdown heading and 1 presented as a plain line. So the written copy's 0 is a correct result for 13 and a false negative for 4, and repairing only the spoken renderer would leave those 4 in place and still reported as 0. Producer: `scripts/b96s_cause_was_wrong_2026-11-07.py`.

## 2 further findings, measured and not acted on

**A label that claims the founder's words does not establish them.** Of the register entries recorded as originating in his chat, **27 of 37 refer to him in the third person** — 0.729730, Wilson 95% [0.570218, 0.846025], Clopper-Pearson [0.558806, 0.862097]. Of entries harvested from his own reply files, where the text certainly is his, **1 of 1158** does so — 0.000864, Wilson [0.000152, 0.004875]. Fisher exact p = 1.153757e-45, reproduced to a relative agreement of 4.045e-16 by an independent exact enumeration. The predicate is a proxy and the note says so: an entry quoting him about a third party would fire too, and the 10 that do not fire are not thereby shown to be his. What the pair does establish is that the label is unreliable as attribution, which matters because provenance is among the properties this project exists to document. No repair is made: the stored field has no public setter and the ticket identities do not depend on it, so whether to add a setter is a decision. Producer: `scripts/whose_words_does_the_register_say_they_are_2026-11-07.py`.

**Nothing a commit consults can refuse a new script. 0 of the 5 guards that refused this session's new scripts are on the commit board**, so each refusal was learned from a complete board of about 2 hours 17 minutes, 1 board at a time. That claim rests on 5 observed refusals rather than on a population estimate, which is the narrow form that survives: a first, wider predicate was abandoned because it missed 2 of those same 5 refusals, the 2 whose guards delegate their enumeration to a script and assert on its output. A later version matches the delegated form, and a third form would be missed in turn. The finding bears on 2 open entries that price the commit gate in seconds only, neither of which carries this figure. Producer: `scripts/what_does_a_new_script_owe_2026-11-07.py`.

## The decisions awaiting the founder

All 29 were re-measured on 2026-11-08 rather than cited from the earlier run. **29 of 29 had already been put to him in a dated file, and 0 of 29 carry a ruling of his that still settles them** — 0.000000, Wilson 95% [0.000000, 0.116970], Clopper-Pearson [0.000000, 0.119445]. 3 carry a ruling on a different question and are live again; 26 carry no ruling at all. Producer: `scripts/are_the_twenty_nine_new_or_repeats_2026-11-07.py`. The generated file carrying them renders 29 decisions, each with a heading, at least 1 option and a named project standard, verified at 0 omissions on each count.

## What the record should carry forward

The useful asymmetry is between the 2 halves of each prediction. The hard clause — naming in advance exactly which failures would survive a board and why — held on both boards of 2026-11-07. The easy clause, that the predicting session had introduced no new failures, was refuted on both, by 10 and then by 2, the second time having cited the first refutation as its reason for confidence. **A prediction about a test board is reliable about the code and unreliable about the predictor.** The scope of that statement is these 2 predictions and predictions of the same shape.

Written under CDSFL note standard v1.9 (1 November 2026).
