# Experiment 40 — What Happened, What it Means

2026-05-14 06:29 BST

## What this note is

The plain-English companion to the technical record of Experiment 40, the first experiment in the project's current fifteen-experiment arc. The technical record carries all the file paths, commit hashes, per-round numbers, and reproducibility detail. This note carries the story.

## What the experiment was for

Experiment 40 was a live exercise of a specific instruction the project gives to language models — the project's "feedback channel" — running against the very piece of code that implements that instruction. The experiment ran five large language models from four different vendors as a co-equal review panel, with each model independently analysing the target code and producing findings about possible issues. The experiment's purpose was to confirm that this instruction works under real conditions and to surface anything about the panel's behaviour worth noting before the rest of the arc proceeds.

## Three small bugs caught at the very start

Before the experiment proper could even begin, the launcher script crashed three times in quick succession. Each crash exposed a small piece of integration code that had never been exercised end-to-end before. None of the three bugs were caught by the substantial pre-launch panel review (three rounds of expert review, six regression tests around the launcher's preflight check) because no reviewer had been asked to actually execute the launcher against the runner's real entry path. Each bug fixed in under five minutes; the fourth launch attempt ran cleanly.

The lesson is worth recording: panel review correctly identifies what to look for in the running code, but it does not catch integration glue that nobody has actually executed. The fix is operational rather than methodological — future experiments should be exercised end-to-end at least once during pre-launch verification.

## The experiment ran for about two hours total

The experiment ran in two segments. The first attempted to run with a one-hour wall-clock limit, which produced three full rounds of data before the limit fired. The wall-clock limit is a review checkpoint rather than a hard ceiling — its purpose is to give the founder a chance to see how things are going and decide whether to continue or adjust. At that checkpoint the project's primary measurement (called "gamma") had climbed close to its convergence threshold, suggesting one more round might cross it. Under the founder's prior authorisation to extend the wall-clock if convergence appeared close, the experiment was resumed with the limit raised to two hours.

The resumed segment ran another seven rounds (rounds three through nine) before terminating at the maximum-rounds boundary. The full experiment thus ran ten rounds: the maximum the project's runner is configured to permit.

## What the panel found, in numbers

Across the ten rounds, the five models together produced 207 raw findings. The project's reconciliation pipeline — the part of the system that compares each new finding against everything previously logged to detect duplicates — reduced those 207 to 146 distinct canonical findings, with the other 61 being repeats. That's a 29% duplicate rate across the whole run, which is reasonable for a panel-style experiment where multiple models can independently surface the same issue.

The 146 canonical findings sit in the experiment's data directory in machine-readable form. Interpreting which of them describe real issues in the target code, and which are false positives or methodology artefacts, is the next analytical step.

## The convergence story — gamma versus reconciliation

The single most important finding from the run is methodological, not about the target code. The project has two ways of measuring whether the panel has run out of new things to find. The two ways disagree.

The first measure is gamma, the project's primary metric for convergence. Gamma rose from zero in round zero to a peak of 0.297 in round three, then declined for six straight rounds to a low of 0.143 in round nine. The convergence threshold is 0.30. Gamma never crossed it and ended the experiment moving in the wrong direction.

The second measure is the reconciliation pipeline's own behaviour. From round six onwards, that pipeline progressively rejected larger and larger fractions of each model's findings as duplicates of canonical entries already in the registry. By round eight, four of the five models had 100% of their findings rejected as duplicates. By round nine, all five models did. The pipeline's view was unambiguous: the panel has nothing new to contribute, the experiment is fully saturated.

Two measures, opposite conclusions. The reason they disagree is that they compute novelty against different signals. Gamma uses the runner's pre-reconciliation novelty count, which can stay high even when reconciliation is rejecting everything because the runner's novelty check is shallower. Reconciliation uses canonical-entry uniqueness, which is the deeper check. The two metrics ought to converge but don't.

This is the highest-leverage fix for the rest of the arc. If gamma keeps being computed against pre-reconciliation novelty, every subsequent experiment will burn through its full round budget when the panel has effectively saturated several rounds earlier. The fix is to compute gamma against post-reconciliation novelty so that the headline metric agrees with what the pipeline is actually observing.

## The system found a bug in itself

A particularly elegant outcome: the panel, while running, produced findings about a defect in the project's own analysis runner. Four of the five models — Claude, ChatGPT, Codex, and DeepSeek — independently generated findings about a parser bug in how the runner reads finding identifiers from model output. The bug causes the parser to capture long runs of descriptive text into the identifier slot when the model's output contains certain formatting characters. Each model's finding was rich enough that the reconciliation pipeline correctly merged all four into a single canonical entry. Two of the models even proposed the same fix (add a missing token to the parser's regex alternation).

This is exactly the reflexive behaviour the project's design intends: a system that's analysing itself can surface its own infrastructure issues, and a multi-vendor panel can converge on the same root cause without prompting. The fix is small (one regex change) and the post-mortem includes it as an action item.

## Twelve requests for human review

The runner has an internal mechanism called the Intelligent Task Controller that watches for repeated failures from individual panel models — silent responses, malformed output, unexpectedly low yield — and raises a flag asking for human attention when failures cluster. Across the ten rounds, the controller raised twelve such flags: four for Gemini, four for ChatGPT, two for Codex, and two for DeepSeek. Claude (running through the project's Max subscription) was the only model not flagged.

The Codex flags are classified as "capability mismatch", which is a distinct category from the "degradation" classification applied to the others — worth investigating what specifically the runner detected.

Two of the Gemini flags correspond to rounds where Gemini returned zero characters of synthesis after running for five to six minutes. That's a 20% empty-response rate across the ten rounds, which is not random and is the most concerning per-model finding from the run. The most recent project decision had been to route Gemini through OpenRouter rather than the Google direct API, partly to draw on existing prepaid credits. It is worth investigating whether reverting Gemini to the Google direct API resolves the intermittent empty-response pattern.

## A separate Gemini pattern — boilerplate self-assessment

A second Gemini-specific finding worth noting: in three of the ten rounds (rounds two, six, and eight), Gemini produced multiple findings (six or seven at a time) that all had identical residual-risk numbers down to three decimal places. Each round's findings differed by exactly the same amount from what the runner's validation said the numbers should be — strongly suggesting Gemini is producing template-uniform residual-risk values rather than per-finding self-assessments. This is a real model-behaviour finding and exactly the kind of signal the project's self-assessment validation is designed to detect. The pattern repeated three times, so it is not random.

## Merge conflicts arrived earlier than predicted

The project's pre-launch panel review had specified that a particular class of issue — the runner's auto-merge pipeline deadlocking when specialist subsystems disagree about which canonical finding a new finding should merge into — was unlikely to surface before experiment 49 (the cross-domain synthesis experiment). Experiment 40 produced this class of issue abundantly. At least eight merge-deadlock events occurred across the rounds, including one event with twenty-one separate target disagreements on a single finding. Three specific canonical entries (one of them being the parser-bug canonical entry mentioned above) recurred as deadlock anchors across multiple rounds.

This is rich evidence that the project can use to design the deferred arbitration rule. The pre-launch decision to wait for evidence before designing the rule has paid off — the evidence is now in hand, earlier than expected.

## A non-fatal calibrator bug

During round six post-processing, the shadow-mode Stage-6 calibrator (the part of the runner that scores novelty across the panel) raised a warning and skipped its calculation: it tried to call a text method on what turned out to be a number. The calibrator is in observation-only mode so its silent skip did not affect the run. It is a real bug to fix.

## What this means for the rest of the arc

The headline takeaways for the founder:

The launcher works end-to-end now, with three small bugs fixed during launch. The pre-launch process didn't catch them because nobody actually ran the launcher; this is fixable as an operational practice for future experiments.

The experiment produced a substantial finding corpus (146 canonical findings on the target module). The interpretive question — whether those findings reflect real issues in the target code, methodology artefacts, or some mix — is the next analytical step. That work proceeds against the per-finding data in the experiment's log directory.

The most consequential single fix to make before Experiment 41 is the gamma metric — moving it from pre-reconciliation novelty to post-reconciliation novelty. Without that, every subsequent experiment will run too long.

Three smaller code fixes are queued: the parser regex, the calibrator bug, and either lowering the gamma threshold or recalibrating the open-critical-high count limit for the wider scope this arc covers.

Two model-route questions need investigating before the rest of the arc proceeds: should Gemini be routed back through Google's direct API (the recent change to OpenRouter routing correlates with the intermittent empty-response pattern), and what specifically did the runner's controller detect about Codex's "capability mismatch" early in the run.

The G7 deferred-design item (the merge-deadlock arbitration rule) can begin design work now, three experiments earlier than the pre-launch plan anticipated.

## Total session arc

The session that began on 13 May at midnight closed Round 3 of the pre-launch focused panel review, then advanced into note-standard version 1.2 work and the comprehensive documentation sweep, and then dispatched and completed Experiment 40 across two segments. Cumulative agent time: roughly four hours of pre-launch closure plus three hours of experiment monitoring and intervention. Eight commits to the project's main branch. The experiment produced its first data and exposed its first real architectural finding (the gamma-versus-reconciliation gap) — exactly what a first experiment in an arc is supposed to do.

## What to read alongside this

The technical record at `experimental_notes/Exp40_PostMortem_2026-05-14.md` carries all per-round numbers, file paths, commit hashes, HIL flag enumerations, and reproducibility detail. The machine-readable report at `bench/logs/exp40_gate_20260514T020550Z/exp40_gate_report.json` carries the raw data the runner produced. The per-round per-model JSON files in the same directory carry the original model responses for any deeper analysis.

## Next review trigger

When the founder wakes and reviews this note, the decision to make is priority order for the nine action items in the technical record. Two of them (the gamma fix and the parser regex) are the highest-leverage. Once they are settled, the autonomous queue can resume toward Experiment 41.

Written under CDSFL note standard v1.2 (14 May 2026).
