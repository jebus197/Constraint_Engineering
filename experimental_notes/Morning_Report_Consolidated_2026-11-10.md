# Consolidated morning report, 10 November 2026

Companion to the spoken file of the same name. The detailed technical record of the panel audit is a separate note, *Panel checked my fixes, 10 November 2026*; this document is the decision-facing summary and is deliberately shorter.

## The short version

A free panel of 2 seats audited the night's work, first blind and then jointly with each seat having read the other in full. It refuted 4 claims. 3 reproduced on independent checking and 1 did not.

The one that matters: a fix made and committed during the night had **destroyed a working capability**, while the measurement justifying it reported a win. Corrected, and the corrected rule is now derived from the measurement rather than written out by hand.

**1 decision is added to the queue**, B136 on the dimensional check, carrying a single recommendation. Nothing else from the night needs a ruling.

## What was wrong, and what replaced it

The harness may accept a repair when a verification tool confirms the claim. Which tools may do that alone is decided by a control: give a tool a claim and then a false variant sharing its vocabulary. Identical verdicts mean the verdict carries no information about the claim.

| configuration | truth-blind paths barred | discriminating paths retained |
|---|---|---|
| the first seat's tool-level exclusion | 4 of 5 | 3 of 7 |
| what was first committed | 5 of 5 | 5 of 7 |
| adopted: gate at the branch by anatomy | **5 of 5** | **7 of 7** |

Scored over 12 fully enumerated admitting paths rather than the 5 the first pass saw. The adopted rule: a tool is gated at the branch where it has both a truth-blind and a comparing favourable branch, at the whole tool where every favourable branch is truth-blind, and not at all where none is. Nothing is held out by name, so a tool cannot be misplaced because its author did not think of it.

Producer: `scripts/which_admissions_are_truth_blind_2026-11-10.py`. Guard: `bench/tests/test_a_confirming_tool_must_discriminate_to_admit_2026-11-10.py`, 17 tests, 3 of 3 mutations red in both the guard and the producer.

## Why it can't recur

The same 1-branch-of-N error occurred 3 times in 1 night from 3 different authors, so the fix is structural rather than a corrected number:

1. The producer enumerates each verifier's favourable branches by bounding the function with the syntax tree, and **exits 1** if its probe set covers fewer branches than exist.
2. It derives both configuration tables from its own measured rows, not from a typed list.
3. It imports the live tables and **exits 1 on any drift** between what ships and what the measurement justifies. Nothing compared those 2 things until a seat did.

## Also fixed

- A completeness check read the keys its own pattern had captured, so a third consequence level was invisible to the one instrument built to detect it. Widened after checking the widening captures identical sets on the live appendix.
- A stray byte-copy of a producer at the repository root, removed on a 3-of-3 dominance measurement. The seat's stated harm was wrong — it exits 1, not 0 — and that is recorded.
- The spoken-report generator was marking 17 decision headings, 12 sub-headings and the note-standard foot-line with an asterisk, guessing headings from their shape. Headings are now recorded where they are emitted.
- Count pins that had drifted 6 times in 4 days, never once from a defect, converted to bounds plus the invariant that catches the actual regression. Mutation-verified in both directions.

## A refutation that was itself refuted

A seat argued that my vacuity-predicate measurement could not have come from this tree, on 2 grounds: that the file does not load, and that both predicates open with an identical clause. Both are false here. The file loads, and the clauses differ — the committed version tests for an assertion **or** a raise, the discarded copy for an assertion alone, which is exactly why the 2 raise cases separate them. The other seat agreed with me in the same round. Taking the refutation at face value would have withdrawn a correct correction.

## The 9 retired explanation requests

Discharged. Measured against the 11 tickets concerned, 9 are closed or deprecated — 0.818182, Wilson 95% [0.523019, 0.948632]. The 2 that read as remaining are not explanations: 1 is a question deferred by the founder himself with an instruction to re-ask on completion, and 1 is the bounded-orchestrator feature request, carried at B20 as the orchestrator bound inside the harness. **Outstanding count 0, not 2**; the 11 was the wrong denominator.

## The runway

Nothing of substance now stands between the current state and the orchestrator work and the zero-plant control. The remaining queue is work carrying rulings already given, plus the single decision above.

Written under CDSFL note standard v1.9 (1 November 2026).
