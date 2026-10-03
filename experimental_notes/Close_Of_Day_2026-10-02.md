# Close of day report, CDSFL

**2 October 2026, 23:08 BST (Europe/London)**



## Purpose

This report lists what changed today, what was measured, and the 9 decisions that now sit with the founder. It is written so the decisions can be taken without reading code.

## Summary

The day's work split into 3 strands. A set of integrity fixes from a 2 seat panel were merged and verified. A standing question about falsifier supply was investigated and the investigation overturned several of the assistant's own claims. A second panel round is running as this is written, because 2 of the project's 3 formal standards were found to be absent from every panel dispatch.

## The board

The full test suite was run twice on a settled tree. The second run finished at 9,762 passed, 7 failed, 9 skipped, in 3,137 seconds. Of those 7 failures, 4 have since been repaired and 3 remain open pending a ruling described below. An earlier run reported 18 failures, of which 10 were an artefact of the assistant editing files while the suite was running. That was an error of method, not of code, and the lesson is recorded: a suite measures a tree that is not moving.

## What was merged

Two panel seats produced complementary fixes for the same defect, and merging them surfaced 3 things the panel record did not contain.

First, both seats' working copies were taken before a fix that closed a hole in the key access scanner. Applying either copy wholesale would have reopened that hole. The merge asserts the fix is present before and after.

Second, the naive merge was silently broken. One seat excluded findings from the convergence machinery on one field, the other reported them on a different field, so a finding excluded by the first route would never appear in the report. That is a silent exclusion, and silence is the one outcome the founder's ruling forbids. Both now share a single decision, and the property is asserted over all 48 field combinations and 400 randomised registries.

Third, the assistant's own extension was too broad. A finding in the most recent run carries a stale integrity label beside a verdict showing it was later tested and confirmed. Reading the stale label without that qualification would have reported a tested finding as excused from the gate.

## The advisory channel

The 2 seats proposed incompatible designs for the same false positive. One excluded every carried source file from the advisory by file type, which leaves open the bypass that seat itself named: write a key reader into a detector file and let the harvester carry it in. The other suppressed the hit entirely, which removes evidence. The merged form uses the second seat's verbatim comparison to decide which channel a hit lands on rather than whether it survives. Measured: on the real run, 0 advisory hits and 7 audit hits, advisory silent. With an exploit planted in the same file, the advisory fires on 2 hits and nothing is dropped. Both seats' forms fail one of those 2 cases.

## The falsifier supply question

The founder asked why falsifier supply is a persistent problem, and whether falsifiers are too specific rather than general. An independent investigation with 6 agents was run, and it refuted several of the assistant's claims.

The headline figure the assistant produced, that 60.58 percent of critical findings had no falsifier, is retired. It pooled runs from April and May 2026 that predate the falsifier machinery entirely. 751 of those 793 findings come from before the feature existed.

A defect was found in the assistant's own measuring script. It decided a finding had no falsifier before reading the verdict, so 42 findings that were assessed and explicitly declined were reported as never written. That is 5.2963 percent of the bucket the conclusion rested on. It is fixed and guarded.

A figure the assistant quoted to the founder earlier today is withdrawn. The claim that routing multiplies falsifier supply rested on a comparison whose null arm returns an empty string by construction. It measures that an empty string is not a falsifier. The arithmetic is correct and the evidence is vacuous.

## What survived, and it is the founder's own intuition

Of 3 competing causes, only 1 reproduced. A falsifier that names a concrete file fails to run at 4.3 times the rate of one that does not, with a Fisher odds ratio of 4.3063 and a p value of 0.000243. The claim being tested was 4.3049, so it reproduced closely. Over specificity is therefore a real contributor, though a minority one, accounting for roughly 1 failure in 7.

The second cause, that findings raised against control runs cannot have falsifiers, did not reproduce. It measures 0 of 46 here rather than the 19 of 46 claimed, most likely because it used the same faulty definition the assistant corrected hours earlier.

The third cause, that prose targets starve more than code targets, cannot be measured at all. The target file is recorded on only 52 of 624 findings, all of them code. That is an open panel dispute, and it is now preventing a measurement rather than merely being untidy.

## The intelligence-first contract

The founder restated that a hand rolled falsifier is acceptable as a reasoning scratchpad provided the reasoning is invariably confirmed or refuted by tools, and provided the runner's per round corrective instruction keeps the models trying until a tool confirms. The project's own tool constraint box supports this in its own words: reasoning selects and interprets tool output and never substitutes for it.

This reframes the measurement. The figure that 86.3727 percent of falsifiers are hand rolled is correct, but it measures the wrong property for that design. The property that matters is whether the reasoning was subsequently adjudicated by a tool. That has not been measured. The record does contain instances where it was not: 118 of 864 findings with tool only status carry no falsifier code, and of 4 escalations examined, 0 carried falsifier code and their confirmation came from model votes, which the project forbids.

## The panel, and why it is running twice

The founder asked whether the project's 3 formal standards are mechanically written into every panel dispatch. They were not. Measured on the dispatcher: the additive standard appeared 7 times, the simplest sufficient standard 0 times, and composability 0 times. So 1 of 3 reached the seats and 2 did not, for every panel round ever run.

All 3 are now carried by the dispatcher's seat prompt, which every seat receives, in the founder's own words, including his specific warning that composability does not mean composing 2 solutions merely because they can be composed. A guard holds all 3, and restating composability as mere coexistence breaks 3 of its checks.

The first panel round completed before this was found. Both seats responded on the free route with 88 and 58 tool calls and edits to 21 files in isolated copies. Nothing was wasted. A second round on the same brief, now carrying all 3 standards, was dispatched at 23:06 and its output will be compared against the first.

## The 9 decisions awaiting the founder

1. The archived figure problem. An archived brief from 11 September declares a rejection rate of 2 in 640. The narrowed gate makes it 1 in 640, so a figure in the historical record stopped reproducing, not because the corpus grew but because a rule changed beneath it. The project already handles corpus growth by pinning the denominator to the brief's date. It has no answer for a rule change. Editing the record is not on the table. 3 tests are red on this. Options are to pin the rule set as well as the corpus, keeping superseded rules alive so historical figures reproduce forever, or to register rule changes in a committed amendments file the validator consults.

2. The A19 flag. The prose scoring flag is built, tested and off by default. The last step is the founder's. 2 further findings from the earlier review remain recorded and unfixed because fixing them changes what reaches a verdict on every target.

3. Task V9, which checks that a completed item's evidence actually fails when its fix is reverted. Approved in September and scheduled after the mathematical model revision. Confirmation that it stays scheduled, or a decision to bring it forward.

4. Whether to build the general falsifier template. Over specificity is now a measured minority cause, so a template is justified on quality and reuse grounds rather than as a cure for starvation. The hazard is named: a general falsifier that cannot fail is worse than none, and the project has shipped exactly that twice.

5. Whether to run the repointing experiment. Two reviewers independently named it as the only thing that settles the over specificity question, because nothing in 7,656 archived files was ever repointed at a different target. It is cheap and read only.

6. Whether to formally retire the routing supply measurement described above, given its null arm is vacuous.

7. Whether to record the target file at dispatch, which is an open panel dispute and is now blocking the prose versus code measurement.

8. Whether to implement the founder's own recommendation that the false positive sweep be able to see refused falsifiers. It is still owed. Measured at the correct location, 23 of 221 routed falsifier bodies are invisible to that sweep and 183 exist only as 600 character truncations.

9. Whether today's work should be committed to the simulation branch. It is currently uncommitted.

## Also recorded

The term witness is used in 33 tracked files but appears 0 times in the glossary. In this project it means the concrete evidence certifying a claim, with the attached safety rule that absence of a witness means not counted, never proven absent. It will be added to the glossary so it can be looked up.

Notification settings were checked. All 3 relevant settings are on: dock attention, task completion banners, and system sound. The cause of the missing dock bounce is therefore outside the application, in the operating system's notification permissions for Claude or an active focus mode.

Written under CDSFL note standard v1.7 (26 August 2026).